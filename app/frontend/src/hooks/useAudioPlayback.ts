"use client";

import { useState, useRef, useCallback } from "react";

interface UseAudioPlaybackReturn {
  isPlaying: boolean;
  enqueueAudio: (base64Data: string) => void;
  stopPlayback: () => void;
}

/** TTS audio comes in at this sample rate from the backend (24 kHz). */
const SOURCE_SAMPLE_RATE = 24000;

function base64ToInt16Array(base64: string): Int16Array {
  const binaryString = atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return new Int16Array(bytes.buffer);
}

function int16ToFloat32(int16: Int16Array): Float32Array {
  const float32 = new Float32Array(int16.length);
  for (let i = 0; i < int16.length; i++) {
    float32[i] = int16[i] / 32768;
  }
  return float32;
}

/**
 * Linear-interpolation resample from srcRate to dstRate.
 * Handles the common case where the browser's AudioContext runs at
 * 44100 or 48000 Hz but TTS audio is 24000 Hz.
 */
function resample(
  samples: Float32Array,
  srcRate: number,
  dstRate: number
): Float32Array {
  if (srcRate === dstRate) return samples;

  const ratio = srcRate / dstRate;
  const outLength = Math.ceil(samples.length / ratio);
  const out = new Float32Array(outLength);

  for (let i = 0; i < outLength; i++) {
    const srcIdx = i * ratio;
    const lo = Math.floor(srcIdx);
    const hi = Math.min(lo + 1, samples.length - 1);
    const frac = srcIdx - lo;
    out[i] = samples[lo] + frac * (samples[hi] - samples[lo]);
  }
  return out;
}

/**
 * Gapless TTS audio playback using an AudioWorklet queue.
 *
 * Instead of creating individual AudioBufferSourceNode instances per
 * chunk (which causes micro-gap clicks at boundaries), this approach
 * pushes decoded & resampled Float32 samples into an AudioWorklet that
 * maintains a dynamically growing queue and pulls samples at the
 * audio-thread rate — gapless and overflow-proof.
 */
export function useAudioPlayback(): UseAudioPlaybackReturn {
  const [isPlaying, setIsPlaying] = useState(false);

  const audioContextRef = useRef<AudioContext | null>(null);
  const workletNodeRef = useRef<AudioWorkletNode | null>(null);
  const isPlayingRef = useRef(false);
  const workletReadyRef = useRef(false);

  const ensureWorklet = useCallback(async (): Promise<AudioWorkletNode> => {
    // Re-use existing context and worklet node if still alive
    if (
      audioContextRef.current &&
      audioContextRef.current.state !== "closed" &&
      workletNodeRef.current &&
      workletReadyRef.current
    ) {
      if (audioContextRef.current.state === "suspended") {
        await audioContextRef.current.resume();
      }
      return workletNodeRef.current;
    }

    // Let the browser pick its preferred sample rate (usually 44100 or 48000).
    // We resample TTS audio (24 kHz) to match on the main thread before
    // posting to the worklet.
    const ctx = new AudioContext();
    audioContextRef.current = ctx;
    console.log(
      `[AudioPlayback] AudioContext created at ${ctx.sampleRate} Hz`
    );

    await ctx.audioWorklet.addModule("/audio-playback-processor.js");

    const node = new AudioWorkletNode(ctx, "pcm16-playback-processor", {
      outputChannelCount: [1],
    });
    node.connect(ctx.destination);

    node.port.onmessage = (event: MessageEvent) => {
      if (event.data === "ended") {
        isPlayingRef.current = false;
        setIsPlaying(false);
      }
    };

    workletNodeRef.current = node;
    workletReadyRef.current = true;
    return node;
  }, []);

  const enqueueAudio = useCallback(
    (base64Data: string) => {
      const int16 = base64ToInt16Array(base64Data);
      const float32 = int16ToFloat32(int16);

      ensureWorklet().then((node) => {
        const ctx = audioContextRef.current!;

        // Resample from 24 kHz source to the AudioContext's actual rate
        const resampled = resample(float32, SOURCE_SAMPLE_RATE, ctx.sampleRate);

        // Transfer the buffer to the worklet thread (zero-copy)
        node.port.postMessage(resampled, [resampled.buffer]);

        if (!isPlayingRef.current) {
          isPlayingRef.current = true;
          setIsPlaying(true);
          node.port.postMessage("resume");
        }
      });
    },
    [ensureWorklet]
  );

  const stopPlayback = useCallback(() => {
    if (workletNodeRef.current) {
      workletNodeRef.current.port.postMessage("stop");
    }
    isPlayingRef.current = false;
    setIsPlaying(false);
  }, []);

  return { isPlaying, enqueueAudio, stopPlayback };
}
