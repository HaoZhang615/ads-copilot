"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import {
  WebSocketManager,
  type IncomingMessage,
  type SessionState,
  type AvatarState,
} from "@/lib/ws-protocol";
import { useAudioCapture } from "@/hooks/useAudioCapture";
import { useAudioPlayback } from "@/hooks/useAudioPlayback";
import { useWebRTC } from "@/hooks/useWebRTC";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

interface UseVoiceSessionReturn {
  messages: Message[];
  sessionState: SessionState;
  isConnected: boolean;
  audioLevel: number;
  isCapturing: boolean;
  isPlaying: boolean;
  startSession: () => void;
  endSession: () => void;
  toggleListening: () => void;
  sendTextMessage: (text: string) => void;
  stopAudio: () => void;
  avatarState: AvatarState;
  avatarVideoRef: React.RefObject<HTMLVideoElement | null>;
  avatarAudioRef: React.RefObject<HTMLAudioElement | null>;
  avatarHasActivated: boolean;

}

const DEFAULT_WS_URL = "ws://localhost:8000/ws";

let messageIdCounter = 0;
function generateId(): string {
  messageIdCounter++;
  return `msg-${Date.now()}-${messageIdCounter}`;
}

export function useVoiceSession(): UseVoiceSessionReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionState, setSessionState] = useState<SessionState>("idle");
  const [isConnected, setIsConnected] = useState(false);
  const [avatarState, setAvatarState] = useState<AvatarState>("disconnected");
  const [avatarHasActivated, setAvatarHasActivated] = useState(false);


  const {
    videoRef,
    audioRef,
    createOffer,
    setAnswer,
    disconnect: disconnectWebRTC,
  } = useWebRTC();

  const wsRef = useRef<WebSocketManager | null>(null);
  const currentAssistantIdRef = useRef<string | null>(null);
  const sessionStateRef = useRef<SessionState>("idle");
  const handleMessageRef = useRef<((msg: IncomingMessage) => void) | undefined>(undefined);

  const { isCapturing, audioLevel, startCapture, stopCapture } =
    useAudioCapture();
  const { isPlaying, enqueueAudio, stopPlayback } = useAudioPlayback();

  handleMessageRef.current = (msg: IncomingMessage) => {
    switch (msg.type) {
      case "transcript": {
        if (msg.is_final && msg.text.trim()) {
          const userMessage: Message = {
            id: generateId(),
            role: "user",
            content: msg.text,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, userMessage]);
        }
        break;
      }

      case "agent_text": {
        // Guard: skip empty text deltas (e.g. from tool-call events)
        if (!msg.text && !msg.is_final) {
          break;
        }
        if (!currentAssistantIdRef.current) {
          // Only create a new bubble if we have actual text content
          if (!msg.text) {
            break;
          }
          const id = generateId();
          currentAssistantIdRef.current = id;
          const assistantMessage: Message = {
            id,
            role: "assistant",
            content: msg.text,
            timestamp: new Date(),
            isStreaming: !msg.is_final,
          };
          setMessages((prev) => [...prev, assistantMessage]);
        } else {
          const currentId = currentAssistantIdRef.current;
          setMessages((prev) =>
            prev.map((m) =>
              m.id === currentId
                ? {
                    ...m,
                    content: msg.is_final ? msg.text : m.content + (msg.text || ""),
                    isStreaming: !msg.is_final,
                  }
                : m
            )
          );
        }
        if (msg.is_final) {
          currentAssistantIdRef.current = null;
        }
        break;
      }

      case "tts_audio": {
        enqueueAudio(msg.data);
        break;
      }

      case "tts_stop": {
        stopPlayback();
        break;
      }

      case "state": {
        setSessionState(msg.state);
        sessionStateRef.current = msg.state;
        // When agent starts thinking, request ICE servers to prepare avatar
        if (msg.state === "thinking") {
          console.log("[avatar] State=thinking, requesting ICE servers");
          wsRef.current?.send({ type: "avatar_ice_request" as const });
        }
        break;
      }

      case "error": {
        const errorMessage: Message = {
          id: generateId(),
          role: "assistant",
          content: `⚠ Error: ${msg.message}`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
        break;
      }

      case "avatar_ice": {
        // ICE servers received — create WebRTC offer with proper ICE config
        console.log("[avatar] ICE servers received, creating offer...");
        createOffer(msg.ice_servers)
          .then((sdp) => {
            console.log("[avatar] Offer created (SDP " + sdp.length + " chars), sending to backend");
            wsRef.current?.send({ type: "avatar_offer" as const, sdp });
          })
          .catch((err) => {
            console.error("[avatar] Failed to create offer:", err);
          });
        break;
      }
      case "avatar_answer": {
        console.log("[avatar] Answer received, setting remote description");
        setAnswer(msg.sdp);
        break;
      }

      case "avatar_state": {
        setAvatarState(msg.state);
        if (msg.state === "speaking" || msg.state === "idle") {
          setAvatarHasActivated(true);
        }
        if (msg.state === "disconnected") {
          disconnectWebRTC();
        }
        break;
      }
    }
  };

  useEffect(() => {
    let cancelled = false;
    let ws: WebSocketManager | null = null;
    let checkConnection: ReturnType<typeof setInterval> | null = null;
    let unsubscribe: (() => void) | null = null;

    async function init() {
      let wsUrl = DEFAULT_WS_URL;
      try {
        const res = await fetch("/api/config");
        if (res.ok) {
          const cfg = await res.json();
          if (cfg.wsUrl) wsUrl = cfg.wsUrl;
        }
      } catch {
        // fall back to default
      }

      if (cancelled) return;

      ws = new WebSocketManager(wsUrl);
      wsRef.current = ws;
      checkConnection = setInterval(() => {
        setIsConnected(ws!.isConnected);
      }, 500);
      unsubscribe = ws.onMessage((msg: IncomingMessage) => {
        handleMessageRef.current?.(msg);
      });
      ws.connect();
    }

    init();
    return () => {
      cancelled = true;
      if (checkConnection) clearInterval(checkConnection);
      unsubscribe?.();
      ws?.disconnect();
    };
  }, []);

  const startSession = useCallback(() => {
    wsRef.current?.send({ type: "control", action: "start_session" });
  }, []);

  const endSession = useCallback(() => {
    stopCapture();
    stopPlayback();
    disconnectWebRTC();
    setAvatarState("disconnected");
    setAvatarHasActivated(false);
    wsRef.current?.send({ type: "control", action: "end_session" });
    setSessionState("idle");
    sessionStateRef.current = "idle";
  }, [stopCapture, stopPlayback, disconnectWebRTC]);

  const onAudioChunk = useCallback((base64Data: string) => {
    wsRef.current?.send({ type: "audio", data: base64Data });
  }, []);

  const toggleListening = useCallback(async () => {
    if (isCapturing) {
      stopCapture();
      wsRef.current?.send({ type: "control", action: "stop_listening" });
    } else {
      if (sessionStateRef.current === "speaking") {
        stopPlayback();
      }
      try {
        await startCapture(onAudioChunk);
        wsRef.current?.send({ type: "control", action: "start_listening" });
      } catch (err) {
        console.error("Failed to start audio capture:", err);
        // Ensure we don't leave the UI in a broken half-capturing state
        stopCapture();
      }
    }
  }, [isCapturing, startCapture, stopCapture, stopPlayback, onAudioChunk]);

  const sendTextMessage = useCallback((text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    wsRef.current?.send({ type: "text", content: text });
  }, []);

  const stopAudio = useCallback(() => {
    stopPlayback();
    wsRef.current?.send({ type: "control", action: "tts_stop" });
  }, [stopPlayback]);

  return {
    messages,
    sessionState,
    isConnected,
    audioLevel,
    isCapturing,
    isPlaying,
    startSession,
    endSession,
    toggleListening,
    sendTextMessage,
    stopAudio,
    avatarState,
    avatarVideoRef: videoRef,
    avatarAudioRef: audioRef,
    avatarHasActivated,

  };
}
