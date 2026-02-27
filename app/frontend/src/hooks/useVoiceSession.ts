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
  liteMode: boolean;
  setLiteMode: (enabled: boolean) => void;
  sessionSummary: string | null;
  isGeneratingSummary: boolean;
  dismissSummary: () => void;
}

const DEFAULT_WS_URL = "ws://localhost:8000/ws";
const LITE_MODE_KEY = "ads-lite-mode";

function readLiteModeFromStorage(): boolean {
  if (typeof window === "undefined") return false;
  try {
    return localStorage.getItem(LITE_MODE_KEY) === "1";
  } catch {
    return false;
  }
}

let messageIdCounter = 0;
function generateId(): string {
  messageIdCounter++;
  return `msg-${Date.now()}-${messageIdCounter}`;
}

/** Build the final WS URL, appending ?lite=1 when lite mode is active. */
function buildWsUrl(base: string, lite: boolean): string {
  if (!lite) return base;
  const sep = base.includes("?") ? "&" : "?";
  return `${base}${sep}lite=1`;
}

export function useVoiceSession(): UseVoiceSessionReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionState, setSessionState] = useState<SessionState>("idle");
  const [isConnected, setIsConnected] = useState(false);
  const [avatarState, setAvatarState] = useState<AvatarState>("disconnected");
  const [avatarHasActivated, setAvatarHasActivated] = useState(false);
  const [liteMode, setLiteModeState] = useState<boolean>(readLiteModeFromStorage);
  const [sessionSummary, setSessionSummary] = useState<string | null>(null);
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);

  // Ref mirror so the message handler closure always reads the latest value.
  const liteModeRef = useRef(liteMode);
  liteModeRef.current = liteMode;

  // Stores the base WS URL (fetched from /api/config once) so reconnections
  // triggered by setLiteMode don't need to re-fetch.
  const wsBaseUrlRef = useRef<string>(DEFAULT_WS_URL);

  // Ref to the interval used for connection polling — needed for cleanup on reconnect.
  const checkConnectionRef = useRef<ReturnType<typeof setInterval> | null>(null);
  // Ref to the unsubscribe function for the current WS message listener.
  const unsubscribeRef = useRef<(() => void) | null>(null);

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
        // Guard: skip empty, non-final deltas (e.g. keep-alive from tool calls)
        if (!msg.text && !msg.is_final) {
          break;
        }

        // Always clear the tracking ref when is_final arrives — even if
        // the text is empty (e.g. agent turn with only tool calls).
        // This prevents the NEXT response from appending to a stale bubble.
        if (msg.is_final) {
          if (currentAssistantIdRef.current) {
            // Finalise the existing bubble with the full response text
            const currentId = currentAssistantIdRef.current;
            setMessages((prev) =>
              prev.map((m) =>
                m.id === currentId
                  ? { ...m, content: msg.text || m.content, isStreaming: false }
                  : m
              )
            );
          } else if (msg.text) {
            // No active bubble but we received a complete message in one
            // shot (no prior streaming deltas). Create the bubble now.
            const id = generateId();
            setMessages((prev) => [
              ...prev,
              {
                id,
                role: "assistant" as const,
                content: msg.text,
                timestamp: new Date(),
                isStreaming: false,
              },
            ]);
          }
          currentAssistantIdRef.current = null;
          break;
        }

        // Streaming delta (is_final === false, text is non-empty)
        if (!currentAssistantIdRef.current) {
          // First chunk of a new response — create the bubble
          if (!msg.text) break;
          const id = generateId();
          currentAssistantIdRef.current = id;
          setMessages((prev) => [
            ...prev,
            {
              id,
              role: "assistant" as const,
              content: msg.text,
              timestamp: new Date(),
              isStreaming: true,
            },
          ]);
        } else {
          // Append to existing streaming bubble
          const currentId = currentAssistantIdRef.current;
          setMessages((prev) =>
            prev.map((m) =>
              m.id === currentId
                ? { ...m, content: m.content + (msg.text || ""), isStreaming: true }
                : m
            )
          );
        }
        break;
      }

      case "tts_audio": {
        // In lite mode the backend won't send TTS audio, but guard here too.
        if (!liteModeRef.current) {
          enqueueAudio(msg.data);
        }
        break;
      }

      case "tts_stop": {
        if (!liteModeRef.current) {
          stopPlayback();
        }
        break;
      }

      case "state": {
        setSessionState(msg.state);
        sessionStateRef.current = msg.state;
        // When agent starts thinking, request ICE servers to prepare avatar.
        // Skip entirely in lite mode — no avatar.
        if (msg.state === "thinking" && !liteModeRef.current) {
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
        if (liteModeRef.current) break;
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
        if (liteModeRef.current) break;
        console.log("[avatar] Answer received, setting remote description");
        setAnswer(msg.sdp);
        break;
      }

      case "avatar_state": {
        if (liteModeRef.current) break;
        setAvatarState(msg.state);
        if (msg.state === "speaking" || msg.state === "idle") {
          setAvatarHasActivated(true);
        }
        if (msg.state === "disconnected") {
          disconnectWebRTC();
        }
        break;
      }

      case "session_summary_chunk": {
        if (msg.is_final) {
          // Final summary — replace any streaming content with the complete text
          setSessionSummary(msg.text);
          setIsGeneratingSummary(false);
        } else {
          // Streaming chunk — append to summary
          setSessionSummary((prev) => (prev || "") + msg.text);
        }
        break;
    }
    }
  };

  // ---------- WS connection helper (shared by init + reconnect) ----------

  /** Tear down current WS connection and its polling interval / listener. */
  const teardownWs = useCallback(() => {
    if (checkConnectionRef.current) {
      clearInterval(checkConnectionRef.current);
      checkConnectionRef.current = null;
    }
    unsubscribeRef.current?.();
    unsubscribeRef.current = null;
    wsRef.current?.disconnect();
    wsRef.current = null;
    setIsConnected(false);
  }, []);

  /** Create a new WS connection using wsBaseUrlRef + current lite mode. */
  const connectWs = useCallback((lite: boolean) => {
    const url = buildWsUrl(wsBaseUrlRef.current, lite);
    const ws = new WebSocketManager(url);
    wsRef.current = ws;

    checkConnectionRef.current = setInterval(() => {
      setIsConnected(ws.isConnected);
    }, 500);

    unsubscribeRef.current = ws.onMessage((msg: IncomingMessage) => {
      handleMessageRef.current?.(msg);
    });

    ws.connect();
  }, []);

  // ---------- Initial connection (runs once) ----------

  useEffect(() => {
    let cancelled = false;

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

      wsBaseUrlRef.current = wsUrl;
      connectWs(liteModeRef.current);
    }

    init();
    return () => {
      cancelled = true;
      teardownWs();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ---------- Lite mode toggle ----------

  const setLiteMode = useCallback(
    (enabled: boolean) => {
      if (enabled === liteModeRef.current) return;

      // Persist preference
      try {
        localStorage.setItem(LITE_MODE_KEY, enabled ? "1" : "0");
      } catch {
        // storage unavailable
      }

      // Update state + ref
      setLiteModeState(enabled);
      liteModeRef.current = enabled;

      // Stop any in-progress voice activity
      stopCapture();
      stopPlayback();
      disconnectWebRTC();
      setAvatarState("disconnected");
      setAvatarHasActivated(false);

      // Reset session UI state
      setSessionState("idle");
      sessionStateRef.current = "idle";
      currentAssistantIdRef.current = null;

      // NOTE: We preserve messages so the user doesn't lose conversation history.
      // The backend will create a NEW session on reconnect, but the frontend
      // conversation stays visible.

      // Reconnect with new ?lite= param → backend creates a new session
      teardownWs();
      connectWs(enabled);
    },
    [stopCapture, stopPlayback, disconnectWebRTC, teardownWs, connectWs]
  );

  // ---------- Session controls ----------

  const startSession = useCallback(() => {
    wsRef.current?.send({ type: "control", action: "start_session" });
  }, []);

  const endSession = useCallback(() => {
    stopCapture();
    stopPlayback();
    disconnectWebRTC();
    setAvatarState("disconnected");
    setAvatarHasActivated(false);
    setIsGeneratingSummary(true);
    setSessionSummary(null);
    wsRef.current?.send({ type: "control", action: "end_session" });
    // Don't set state to idle yet — wait for summary to complete.
    // The backend will send state updates as it generates the summary.
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

  const dismissSummary = useCallback(() => {
    setSessionSummary(null);
    setIsGeneratingSummary(false);
  }, []);

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
    liteMode,
    setLiteMode,
    sessionSummary,
    isGeneratingSummary,
    dismissSummary,
  };
}
