"use client";

import { useEffect, useRef } from "react";
import { useVoiceSession } from "@/hooks/useVoiceSession";
import { MessageBubble } from "@/components/MessageBubble";
import { VoiceButton } from "@/components/VoiceButton";
import { TextInput } from "@/components/TextInput";
import type { SessionState } from "@/lib/ws-protocol";

const STATE_LABELS: Record<SessionState, string> = {
  idle: "Ready",
  listening: "Listening...",
  thinking: "Thinking...",
  speaking: "Speaking...",
};

const STATE_COLORS: Record<SessionState, string> = {
  idle: "bg-gray-500",
  listening: "bg-red-500",
  thinking: "bg-yellow-500",
  speaking: "bg-blue-500",
};

export function ChatInterface() {
  const {
    messages,
    sessionState,
    isConnected,
    audioLevel,
    isCapturing,
    startSession,
    endSession,
    toggleListening,
    sendTextMessage,
  } = useVoiceSession();

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasStartedRef = useRef(false);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (isConnected && !hasStartedRef.current) {
      hasStartedRef.current = true;
      startSession();
    }
  }, [isConnected, startSession]);

  const inputDisabled =
    sessionState === "thinking" || sessionState === "speaking";

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      <header className="flex items-center justify-between px-6 py-4 border-b border-[var(--border)]">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
              className="w-6 h-6 text-blue-400"
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            <h1 className="text-lg font-semibold text-[var(--foreground)]">
              Databricks ADS
            </h1>
          </div>
          <span className="text-xs text-[var(--muted)] hidden sm:inline">
            Architecture Design Session
          </span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${STATE_COLORS[sessionState]} bg-opacity-20 text-[var(--foreground)]`}
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${STATE_COLORS[sessionState]}`}
              />
              {STATE_LABELS[sessionState]}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-500" : "bg-red-500"}`}
              title={isConnected ? "Connected" : "Disconnected"}
            />
            <span className="text-xs text-[var(--muted)]">
              {isConnected ? "Connected" : "Disconnected"}
            </span>
          </div>
          {sessionState !== "idle" && (
            <button
              type="button"
              onClick={endSession}
              className="text-xs px-3 py-1.5 rounded-lg bg-[var(--surface)] text-[var(--muted)] hover:text-[var(--foreground)] hover:bg-[var(--surface-hover)] border border-[var(--border)] transition-colors"
            >
              End Session
            </button>
          )}
        </div>
      </header>

      <div className="flex-1 overflow-y-auto px-6 py-4 scrollbar-thin">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-2xl bg-[var(--surface)] flex items-center justify-center mb-4">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth={1.5}
                strokeLinecap="round"
                strokeLinejoin="round"
                className="w-8 h-8 text-blue-400"
              >
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                <line x1="12" x2="12" y1="19" y2="22" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-[var(--foreground)] mb-2">
              Azure Databricks ADS
            </h2>
            <p className="text-sm text-[var(--muted)] max-w-md">
              Start your Architecture Design Session by speaking or typing.
              The AI assistant will guide you through designing your Databricks
              solution.
            </p>
          </div>
        )}
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-[var(--border)] px-6 py-4">
        <div className="flex items-center gap-3">
          <TextInput onSend={sendTextMessage} disabled={inputDisabled} />
          <VoiceButton
            isListening={isCapturing}
            audioLevel={audioLevel}
            disabled={!isConnected}
            onClick={toggleListening}
          />
        </div>
      </div>
    </div>
  );
}
