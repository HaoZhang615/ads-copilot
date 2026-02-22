"use client";

import { useState, useRef, useCallback } from "react";
import { registerAudioWorklet } from "@/lib/audio-worklet";

interface UseAudioCaptureReturn {
  isCapturing: boolean;
  audioLevel: number;
  startCapture: (onAudioChunk: (base64Data: string) => void) => Promise<void>;
  stopCapture: () => void;
}

function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

export function useAudioCapture(): UseAudioCaptureReturn {
  const [isCapturing, setIsCapturing] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);

  const audioContextRef = useRef<AudioContext | null>(null);
  const workletNodeRef = useRef<AudioWorkletNode | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number>(0);

  const updateAudioLevel = useCallback(() => {
    if (!analyserRef.current) return;

    const dataArray = new Float32Array(analyserRef.current.fftSize);
    analyserRef.current.getFloatTimeDomainData(dataArray);

    let sumSquares = 0;
    for (let i = 0; i < dataArray.length; i++) {
      sumSquares += dataArray[i] * dataArray[i];
    }
    const rms = Math.sqrt(sumSquares / dataArray.length);
    const normalizedLevel = Math.min(1, rms * 5);
    setAudioLevel(normalizedLevel);

    animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
  }, []);

  const startCapture = useCallback(
    async (onAudioChunk: (base64Data: string) => void) => {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 24000,
        },
      });

      const audioContext = new AudioContext({ sampleRate: 24000 });
      await registerAudioWorklet(audioContext);

      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 2048;
      source.connect(analyser);

      const workletNode = new AudioWorkletNode(
        audioContext,
        "pcm16-capture-processor"
      );

      workletNode.port.onmessage = (event: MessageEvent<ArrayBuffer>) => {
        const base64 = arrayBufferToBase64(event.data);
        onAudioChunk(base64);
      };

      source.connect(workletNode);
      workletNode.connect(audioContext.destination);

      audioContextRef.current = audioContext;
      workletNodeRef.current = workletNode;
      mediaStreamRef.current = stream;
      sourceRef.current = source;
      analyserRef.current = analyser;

      setIsCapturing(true);
      animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
    },
    [updateAudioLevel]
  );

  const stopCapture = useCallback(() => {
    cancelAnimationFrame(animationFrameRef.current);

    if (workletNodeRef.current) {
      workletNodeRef.current.disconnect();
      workletNodeRef.current = null;
    }

    if (sourceRef.current) {
      sourceRef.current.disconnect();
      sourceRef.current = null;
    }

    if (analyserRef.current) {
      analyserRef.current.disconnect();
      analyserRef.current = null;
    }

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    setIsCapturing(false);
    setAudioLevel(0);
  }, []);

  return { isCapturing, audioLevel, startCapture, stopCapture };
}
