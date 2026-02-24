"use client";

export type SessionState = "idle" | "listening" | "thinking" | "speaking";

export type OutgoingAudioMessage = {
  type: "audio";
  data: string;
};

export type OutgoingControlMessage = {
  type: "control";
  action: "start_listening" | "stop_listening" | "start_session" | "end_session" | "tts_stop";
};

export type OutgoingTextMessage = {
  type: "text";
  content: string;
};

export type OutgoingAvatarOfferMessage = {
  type: "avatar_offer";
  sdp: string;
};

export type OutgoingAvatarIceRequestMessage = {
  type: "avatar_ice_request";
};

export type OutgoingMessage =
  | OutgoingAudioMessage
  | OutgoingControlMessage
  | OutgoingTextMessage
  | OutgoingAvatarOfferMessage
  | OutgoingAvatarIceRequestMessage;

export type IncomingTranscriptMessage = {
  type: "transcript";
  text: string;
  is_final: boolean;
};

export type IncomingAgentTextMessage = {
  type: "agent_text";
  text: string;
  is_final: boolean;
};

export type IncomingTtsAudioMessage = {
  type: "tts_audio";
  data: string;
};


export type IncomingTtsStopMessage = {
  type: "tts_stop";
};

export type IncomingStateMessage = {
  type: "state";
  state: SessionState;
};

export type IncomingErrorMessage = {
  type: "error";
  message: string;
};

export type IncomingAvatarAnswerMessage = {
  type: "avatar_answer";
  sdp: string;
  ice_servers: Array<{ urls: string[]; username: string; credential: string }>;
};

export type IncomingAvatarIceMessage = {
  type: "avatar_ice";
  ice_servers: Array<{ urls: string[]; username: string; credential: string }>;
};

export type IncomingAvatarStateMessage = {
  type: "avatar_state";
  state: AvatarState;
};

export type AvatarState = "idle" | "connecting" | "speaking" | "disconnected";

export type IncomingMessage =
  | IncomingTranscriptMessage
  | IncomingAgentTextMessage
  | IncomingTtsAudioMessage
  | IncomingTtsStopMessage
  | IncomingStateMessage
  | IncomingErrorMessage
  | IncomingAvatarAnswerMessage
  | IncomingAvatarIceMessage
  | IncomingAvatarStateMessage;

type MessageHandler = (msg: IncomingMessage) => void;

export class WebSocketManager {
  private ws: WebSocket | null = null;
  private url: string;
  private handlers: Set<MessageHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectDelay = 30000;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private intentionalClose = false;

  constructor(url: string) {
    this.url = url;
  }

  get readyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN || this.ws?.readyState === WebSocket.CONNECTING) {
      return;
    }

    this.intentionalClose = false;

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event: MessageEvent) => {
        try {
          const msg = JSON.parse(event.data as string) as IncomingMessage;
          this.handlers.forEach((handler) => handler(msg));
        } catch {
          // malformed message, ignore
        }
      };

      this.ws.onclose = () => {
        this.ws = null;
        if (!this.intentionalClose) {
          this.scheduleReconnect();
        }
      };

      this.ws.onerror = () => {
        this.ws?.close();
      };
    } catch {
      this.scheduleReconnect();
    }
  }

  disconnect(): void {
    this.intentionalClose = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close(1000, "Client disconnect");
      this.ws = null;
    }
  }

  send(message: OutgoingMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  onMessage(handler: MessageHandler): () => void {
    this.handlers.add(handler);
    return () => {
      this.handlers.delete(handler);
    };
  }

  private scheduleReconnect(): void {
    if (this.intentionalClose) return;

    const delay = Math.min(
      1000 * Math.pow(2, this.reconnectAttempts),
      this.maxReconnectDelay
    );
    this.reconnectAttempts++;

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }
}
