/**
 * AudioWorklet processor for gapless TTS playback.
 *
 * Uses a dynamically growing queue of Float32 chunks instead of a
 * fixed-size ring buffer.  This avoids overflow when the main thread
 * pushes audio faster than real-time (e.g. a 30-second TTS response
 * arrives in < 1 second over WebSocket).
 *
 * The main thread is responsible for resampling from the TTS source
 * sample rate (24 kHz) to the AudioContext sample rate before posting
 * chunks here.
 */
class PCM16PlaybackProcessor extends AudioWorkletProcessor {
  constructor() {
    super();

    /** @type {Float32Array[]} */
    this._queue = [];
    /** Offset into the first chunk in _queue */
    this._offset = 0;
    this._stopped = false;
    this._finished = false;

    this.port.onmessage = (event) => {
      if (event.data === "stop") {
        this._stopped = true;
        this._queue = [];
        this._offset = 0;
        return;
      }
      if (event.data === "resume") {
        this._stopped = false;
        this._finished = false;
        return;
      }

      // Incoming Float32Array of PCM samples (already resampled)
      const samples = event.data;
      if (samples instanceof Float32Array && samples.length > 0) {
        this._queue.push(samples);
      }
    };
  }

  process(_inputs, outputs) {
    if (this._stopped) {
      return true;
    }

    const output = outputs[0];
    if (!output || output.length === 0) return true;

    const channel = output[0];
    let written = 0;

    while (written < channel.length && this._queue.length > 0) {
      const chunk = this._queue[0];
      const remaining = chunk.length - this._offset;
      const needed = channel.length - written;
      const toCopy = Math.min(remaining, needed);

      // Copy samples from current chunk into the output
      for (let i = 0; i < toCopy; i++) {
        channel[written + i] = chunk[this._offset + i];
      }
      written += toCopy;
      this._offset += toCopy;

      // Move to next chunk if current is exhausted
      if (this._offset >= chunk.length) {
        this._queue.shift();
        this._offset = 0;
      }
    }

    // Fill any remaining output with silence
    for (let i = written; i < channel.length; i++) {
      channel[i] = 0;
    }

    // Notify main thread when buffer drains completely
    if (written > 0) {
      this._finished = false;
    } else if (!this._finished) {
      this._finished = true;
      this.port.postMessage("ended");
    }

    return true;
  }
}

registerProcessor("pcm16-playback-processor", PCM16PlaybackProcessor);
