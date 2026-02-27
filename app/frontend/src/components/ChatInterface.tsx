"use client";

import { useEffect, useRef } from "react";
import { useVoiceSession } from "@/hooks/useVoiceSession";
import { MessageBubble } from "@/components/MessageBubble";
import { VoiceButton } from "@/components/VoiceButton";
import { TextInput } from "@/components/TextInput";
import { AvatarPanel } from "@/components/AvatarPanel";
import { SessionSummaryModal } from "@/components/SessionSummaryModal";
import type { SessionState } from "@/lib/ws-protocol";

const STATE_LABELS: Record<SessionState, string> = {
  idle: "Ready",
  listening: "Listening...",
  thinking: "Thinking...",
  speaking: "Speaking...",
};

const STATE_COLORS: Record<SessionState, string> = {
  idle: "bg-gray-500",
  listening: "bg-[#FF3621]",
  thinking: "bg-amber-500",
  speaking: "bg-[#0078D4]",
};

function AzureLogo({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 96 96"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <path
        d="M33.338 6.544h26.038l-27.03 80.455a4.46 4.46 0 0 1-4.223 3.01H4.834a4.46 4.46 0 0 1-4.221-5.912L29.114 9.556a4.46 4.46 0 0 1 4.224-3.012z"
        fill="#0078D4"
      />
      <path
        d="M71.175 60.261H31.528a2.07 2.07 0 0 0-1.404 3.587l25.554 23.88a4.46 4.46 0 0 0 3.046 1.2h24.258z"
        fill="#0078D4"
      />
      <path
        d="M33.338 6.544a4.45 4.45 0 0 0-4.248 3.09L.613 84.071a4.46 4.46 0 0 0 4.221 5.917h24.088a4.54 4.54 0 0 0 3.622-2.917l5.097-14.715 17.824 16.628a4.51 4.51 0 0 0 2.72 1.004h24.182l-10.596-28.727H37.788l21.264-49.277H33.338z"
        fill="#0078D4"
        opacity="0.8"
      />
    </svg>
  );
}

function DatabricksLogo({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 36 36"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <path
        d="M18 1.44L2.16 10.44v5.04l15.84 9 15.84-9v-5.04L18 1.44z"
        fill="#FF3621"
      />
      <path
        d="M18 17.28L2.16 8.28v5.04l15.84 9 15.84-9V8.28L18 17.28z"
        fill="#FF3621"
        opacity="0.7"
      />
      <path
        d="M2.16 20.52v5.04L18 34.56l15.84-9v-5.04L18 29.52l-15.84-9z"
        fill="#FF3621"
      />
      <path
        d="M2.16 15.48v5.04L18 29.52l15.84-9v-5.04L18 23.48l-15.84-8z"
        fill="#FF3621"
        opacity="0.85"
      />
    </svg>
  );
}

/** Stop audio playback button — shown when TTS is active. */
function StopAudioButton({
  onClick,
  visible,
}: {
  onClick: () => void;
  visible: boolean;
}) {
  if (!visible) return null;

  return (
    <button
      type="button"
      onClick={onClick}
      aria-label="Stop audio playback"
      title="Stop audio"
      className="relative flex items-center justify-center w-14 h-14 rounded-full transition-all duration-200 bg-[var(--danger)] text-white hover:bg-[#e02e1a] focus:outline-none focus:ring-2 focus:ring-[var(--danger)] focus:ring-offset-2 focus:ring-offset-[var(--background)]"
    >
      {/* Square stop icon */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="currentColor"
        className="w-5 h-5"
      >
        <rect x="6" y="6" width="12" height="12" rx="2" />
      </svg>
    </button>
  );
}

/** Toggle switch for lite (text-only) conversation mode. */
function LiteModeToggle({
  enabled,
  onChange,
}: {
  enabled: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <label className="flex items-center gap-1.5 cursor-pointer select-none" title={enabled ? "Voice & avatar disabled" : "Voice & avatar enabled"}>
      <span className="text-xs text-[var(--muted)] hidden sm:inline">
        {enabled ? "Lite" : "Full"}
      </span>
      <button
        type="button"
        role="switch"
        aria-checked={enabled}
        aria-label="Toggle lite conversation mode"
        onClick={() => onChange(!enabled)}
        className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-[var(--accent)] focus:ring-offset-1 focus:ring-offset-[var(--background)] ${
          enabled ? "bg-[var(--accent)]" : "bg-[var(--border)]"
        }`}
      >
        <span
          className={`inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform duration-200 ${
            enabled ? "translate-x-[18px]" : "translate-x-[3px]"
          }`}
        />
      </button>
    </label>
  );
}

export function ChatInterface() {
  const {
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
    avatarVideoRef,
    avatarAudioRef,
    avatarHasActivated,
    liteMode,
    setLiteMode,
    sessionSummary,
    isGeneratingSummary,
    dismissSummary,
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
  const showStopButton = !liteMode && (isPlaying || sessionState === "speaking");
  const showAvatar = !liteMode && (avatarState !== "disconnected" || avatarHasActivated);

  return (
    <div className="flex flex-col h-full max-w-6xl mx-auto">
      {/* Header with Azure + Databricks branding */}
      <header className="flex items-center justify-between px-6 py-3 border-b-2 border-[var(--accent)]" style={{ borderImage: "linear-gradient(to right, #0078D4, #FF3621) 1" }}>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2.5">
            <AzureLogo className="w-6 h-6" />
            <span className="text-[var(--muted)] text-sm select-none">×</span>
            <DatabricksLogo className="w-6 h-6" />
          </div>
          <div className="h-5 w-px bg-[var(--border)]" />
          <div>
            <h1 className="text-sm font-semibold text-[var(--foreground)] leading-tight">
              Architecture Design Session
            </h1>
            <span className="text-xs text-[var(--muted)] hidden sm:inline">
              Azure Databricks
            </span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${STATE_COLORS[sessionState]} bg-opacity-20 text-[var(--foreground)]`}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${STATE_COLORS[sessionState]}`}
            />
            {STATE_LABELS[sessionState]}
          </span>
          <div className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${isConnected ? "bg-[var(--success)]" : "bg-[var(--danger)]"}`}
              title={isConnected ? "Connected" : "Disconnected"}
            />
            <span className="text-xs text-[var(--muted)]">
              {isConnected ? "Connected" : "Disconnected"}
            </span>
          </div>
          <div className="h-4 w-px bg-[var(--border)]" />
          <LiteModeToggle enabled={liteMode} onChange={setLiteMode} />
        </div>
      </header>

      {/* Two-panel layout: avatar (left) + chat (right) */}
      <div className="flex flex-col lg:flex-row flex-1 min-h-0">
        {/* Avatar panel — visible once avatar has been used at least once (hidden in lite mode) */}
        {showAvatar && (
          <div className="p-4 lg:py-6 lg:pl-6 flex items-start justify-center lg:justify-start">
            <AvatarPanel
              avatarState={avatarState}
              videoRef={avatarVideoRef}
              audioRef={avatarAudioRef}
            />
          </div>
        )}

        {/* Chat column */}
        <div className="flex flex-col flex-1 min-w-0 min-h-0">
          {/* Messages area */}
          <div className="flex-1 overflow-y-auto px-6 py-4 scrollbar-thin">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="flex items-center gap-4 mb-6">
                  <AzureLogo className="w-12 h-12" />
                  <span className="text-2xl text-[var(--border)] font-light select-none">×</span>
                  <DatabricksLogo className="w-12 h-12" />
                </div>
                <h2 className="text-xl font-semibold text-[var(--foreground)] mb-2">
                  Azure Databricks
                </h2>
                <h3 className="text-lg text-[var(--accent-light)] mb-3">
                  Architecture Design Session
                </h3>
                {liteMode ? (
                  <>
                    <p className="text-sm text-[var(--muted)] max-w-md leading-relaxed">
                      Text-based AI assistant for designing your Databricks solution
                      architecture. Type your message below to begin.
                    </p>
                    <div className="mt-6 flex items-center gap-2 text-xs text-[var(--muted)]">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth={1.5}
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="w-4 h-4"
                      >
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                      </svg>
                      Lite mode — voice and avatar disabled
                    </div>
                  </>
                ) : (
                  <>
                    <p className="text-sm text-[var(--muted)] max-w-md leading-relaxed">
                      Voice-enabled AI assistant for designing your Databricks solution
                      architecture. Start by speaking or typing below.
                    </p>
                    <div className="mt-6 flex items-center gap-2 text-xs text-[var(--muted)]">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth={1.5}
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="w-4 h-4"
                      >
                        <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                        <line x1="12" x2="12" y1="19" y2="22" />
                      </svg>
                      Click the microphone to begin a voice session
                    </div>
                  </>
                )}
              </div>
            )}
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </div>
          {/* Input bar */}
          <div className="border-t border-[var(--border)] px-6 py-4">
            <div className="flex items-center gap-3">
              <TextInput onSend={sendTextMessage} disabled={inputDisabled} />
              {!liteMode && (
                <>
                  <StopAudioButton onClick={stopAudio} visible={showStopButton} />
                  <VoiceButton
                    isListening={isCapturing}
                    audioLevel={audioLevel}
                    disabled={!isConnected}
                    onClick={toggleListening}
                  />
                </>
              )}
              <button
                type="button"
                onClick={endSession}
                disabled={isGeneratingSummary}
                aria-label="End session"
                title={isGeneratingSummary ? "Summarizing…" : "End Session"}
                className={`relative flex items-center justify-center w-14 h-14 rounded-full transition-all duration-200 bg-[var(--surface)] text-[var(--muted)] hover:text-[var(--foreground)] hover:bg-[var(--surface-hover)] border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-[var(--danger)] focus:ring-offset-2 focus:ring-offset-[var(--background)] ${isGeneratingSummary ? "opacity-50 cursor-not-allowed" : ""}`}
              >
                {isGeneratingSummary ? (
                  <span className="inline-block w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                ) : (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="w-5 h-5"
                  >
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
      {/* Session summary modal */}
      {(sessionSummary !== null || isGeneratingSummary) && (
        <SessionSummaryModal
          summary={sessionSummary}
          isGenerating={isGeneratingSummary}
          onDismiss={dismissSummary}
        />
      )}
    </div>
  );
}
