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

export function useAudioPlayback(): UseAudioPlaybackReturn {
  const [isPlaying, setIsPlaying] = useState(false);

  const audioContextRef = useRef<AudioContext | null>(null);
  const queueRef = useRef<AudioBuffer[]>([]);
  const currentSourceRef = useRef<AudioBufferSourceNode | null>(null);
  const isPlayingRef = useRef(false);

  const getAudioContext = useCallback((): AudioContext => {
    if (!audioContextRef.current || audioContextRef.current.state === "closed") {
      audioContextRef.current = new AudioContext({ sampleRate: 24000 });
    }
    return audioContextRef.current;
  }, []);

  const playNext = useCallback(() => {
    if (queueRef.current.length === 0) {
      isPlayingRef.current = false;
      setIsPlaying(false);
      return;
    }

    const ctx = getAudioContext();
    const buffer = queueRef.current.shift()!;
    const source = ctx.createBufferSource();
    source.buffer = buffer;
    source.connect(ctx.destination);

    currentSourceRef.current = source;

    source.onended = () => {
      currentSourceRef.current = null;
      playNext();
    };

    source.start();
  }, [getAudioContext]);

  const enqueueAudio = useCallback(
    (base64Data: string) => {
      const ctx = getAudioContext();
      const int16 = base64ToInt16Array(base64Data);
      const float32 = int16ToFloat32(int16);

      const audioBuffer = ctx.createBuffer(1, float32.length, 24000);
      audioBuffer.getChannelData(0).set(float32);

      queueRef.current.push(audioBuffer);

      if (!isPlayingRef.current) {
        isPlayingRef.current = true;
        setIsPlaying(true);
        playNext();
      }
    },
    [getAudioContext, playNext]
  );

  const stopPlayback = useCallback(() => {
    queueRef.current = [];

    if (currentSourceRef.current) {
      try {
        currentSourceRef.current.onended = null;
        currentSourceRef.current.stop();
      } catch {
        // source may already be stopped
      }
      currentSourceRef.current = null;
    }

    isPlayingRef.current = false;
    setIsPlaying(false);
  }, []);

  return { isPlaying, enqueueAudio, stopPlayback };
}
