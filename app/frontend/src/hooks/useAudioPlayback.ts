"use client";

import { useState, useRef, useCallback } from "react";

interface UseAudioPlaybackReturn {
  isPlaying: boolean;
  enqueueAudio: (base64Data: string) => void;
  stopPlayback: () => void;
}

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
 * Gapless TTS audio playback using an AudioWorklet ring buffer.
 *
 * Instead of creating individual AudioBufferSourceNode instances per
 * chunk (which causes micro-gap clicks at boundaries), this approach
 * pushes decoded Float32 samples into an AudioWorklet that maintains
 * a continuous ring buffer and pulls samples at the audio-thread rate.
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
      // Resume context if it was suspended (e.g. after user gesture policy)
      if (audioContextRef.current.state === "suspended") {
        await audioContextRef.current.resume();
      }
      return workletNodeRef.current;
    }

    // Create a new AudioContext at 24 kHz (matching TTS output)
    const ctx = new AudioContext({ sampleRate: 24000 });
    audioContextRef.current = ctx;

    // Load the playback worklet processor
    await ctx.audioWorklet.addModule("/audio-playback-processor.js");

    const node = new AudioWorkletNode(ctx, "pcm16-playback-processor", {
      outputChannelCount: [1],
    });
    node.connect(ctx.destination);

    // Listen for "ended" messages (buffer drained, no more data)
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

      // Fire-and-forget: ensure worklet is ready then push samples
      ensureWorklet().then((node) => {
        // Transfer the float32 buffer to the worklet thread for zero-copy
        node.port.postMessage(float32, [float32.buffer]);

        if (!isPlayingRef.current) {
          isPlayingRef.current = true;
          setIsPlaying(true);
          // In case the worklet was previously stopped, resume it
          node.port.postMessage("resume");
        }
      });
    },
    [ensureWorklet]
  );

  const stopPlayback = useCallback(() => {
    // Tell the worklet to flush its ring buffer and go silent
    if (workletNodeRef.current) {
      workletNodeRef.current.port.postMessage("stop");
    }

    isPlayingRef.current = false;
    setIsPlaying(false);
  }, []);

  return { isPlaying, enqueueAudio, stopPlayback };
}
