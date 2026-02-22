/**
 * AudioWorklet processor for gapless TTS playback.
 *
 * Maintains a ring buffer of Float32 samples. The main thread pushes
 * decoded PCM data via port.postMessage; the processor pulls samples
 * at the audio-thread sample rate (24 kHz) and writes them into the
 * output buffer continuously — eliminating the micro-gap clicks that
 * occur when chaining individual AudioBufferSourceNode instances.
 */
class PCM16PlaybackProcessor extends AudioWorkletProcessor {
  constructor() {
    super();

    // Ring buffer: 2 seconds at 24 kHz = 48000 samples
    this._bufferSize = 48000;
    this._buffer = new Float32Array(this._bufferSize);
    this._writeIndex = 0;
    this._readIndex = 0;
    this._samplesAvailable = 0;
    this._stopped = false;
    this._finished = false;

    this.port.onmessage = (event) => {
      if (event.data === "stop") {
        this._stopped = true;
        this._samplesAvailable = 0;
        this._readIndex = 0;
        this._writeIndex = 0;
        return;
      }
      if (event.data === "resume") {
        this._stopped = false;
        this._finished = false;
        return;
      }

      // Incoming Float32Array of PCM samples
      const samples = event.data;
      if (!(samples instanceof Float32Array)) return;

      for (let i = 0; i < samples.length; i++) {
        if (this._samplesAvailable >= this._bufferSize) {
          // Buffer full — drop oldest sample (overwrite)
          this._readIndex = (this._readIndex + 1) % this._bufferSize;
          this._samplesAvailable--;
        }
        this._buffer[this._writeIndex] = samples[i];
        this._writeIndex = (this._writeIndex + 1) % this._bufferSize;
        this._samplesAvailable++;
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
    let hasData = false;

    for (let i = 0; i < channel.length; i++) {
      if (this._samplesAvailable > 0) {
        channel[i] = this._buffer[this._readIndex];
        this._readIndex = (this._readIndex + 1) % this._bufferSize;
        this._samplesAvailable--;
        hasData = true;
      } else {
        channel[i] = 0;
      }
    }

    // Notify main thread about buffer state for isPlaying tracking
    if (hasData) {
      this._finished = false;
    } else if (!this._finished) {
      this._finished = true;
      this.port.postMessage("ended");
    }

    return true;
  }
}

registerProcessor("pcm16-playback-processor", PCM16PlaybackProcessor);
