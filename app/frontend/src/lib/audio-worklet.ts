"use client";

export async function registerAudioWorklet(
  audioContext: AudioContext
): Promise<void> {
  await audioContext.audioWorklet.addModule("/audio-processor.js");
}
