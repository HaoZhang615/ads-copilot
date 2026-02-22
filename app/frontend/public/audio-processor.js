class PCM16CaptureProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._buffer = new Int16Array(4096);
    this._bufferIndex = 0;
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || input.length === 0) return true;

    const channelData = input[0];
    if (!channelData) return true;

    for (let i = 0; i < channelData.length; i++) {
      const sample = Math.max(-1, Math.min(1, channelData[i]));
      this._buffer[this._bufferIndex++] = Math.round(sample * 32767);

      if (this._bufferIndex >= this._buffer.length) {
        const output = this._buffer.slice(0);
        this.port.postMessage(output.buffer, [output.buffer]);
        this._buffer = new Int16Array(4096);
        this._bufferIndex = 0;
      }
    }

    return true;
  }
}

registerProcessor("pcm16-capture-processor", PCM16CaptureProcessor);
