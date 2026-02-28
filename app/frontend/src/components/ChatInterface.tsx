"use client";

import { useEffect, useRef } from "react";
import { useVoiceSession } from "@/hooks/useVoiceSession";
import { MessageBubble } from "@/components/MessageBubble";
import { VoiceButton } from "@/components/VoiceButton";
import { TextInput } from "@/components/TextInput";
import { AvatarPanel } from "@/components/AvatarPanel";
import { SessionSummaryModal } from "@/components/SessionSummaryModal";
import type { SessionState } from "@/lib/ws-protocol";

type TopicId = "databricks" | "fabric";

const STATE_LABELS: Record<SessionState, string> = {
  idle: "Ready",
  listening: "Listening...",
  thinking: "Thinking...",
  speaking: "Speaking...",
};

const STATE_COLORS: Record<SessionState, string> = {
  idle: "bg-gray-500",
  listening: "bg-[var(--topic-accent)]",
  thinking: "bg-amber-500",
  speaking: "bg-[#0078D4]",
};

const TOPIC_CONFIG: Record<TopicId, {
  label: string;
  subtitle: string;
  liteDescription: string;
  fullDescription: string;
}> = {
  databricks: {
    label: "Azure Databricks",
    subtitle: "Azure Databricks",
    liteDescription: "Text-based AI assistant for designing your Databricks solution architecture. Type your message below to begin.",
    fullDescription: "Voice-enabled AI assistant for designing your Databricks solution architecture. Start by speaking or typing below.",
  },
  fabric: {
    label: "Microsoft Fabric",
    subtitle: "Microsoft Fabric",
    liteDescription: "Text-based AI assistant for designing your Microsoft Fabric solution architecture. Type your message below to begin.",
    fullDescription: "Voice-enabled AI assistant for designing your Microsoft Fabric solution architecture. Start by speaking or typing below.",
  },
};



function DatabricksLogo({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 250 250" xmlns="http://www.w3.org/2000/svg" fill="none" className={className} aria-label="Databricks" role="img">
      <path fill="#FF3621" d="M215 170.861V136.65l-3.77-2.092-85.739 48.513-81.412-46.057.017-19.838 81.395 45.538L215 112.575V78.883l-3.77-2.092-85.739 48.513-78.06-44.172 78.06-43.896 63.032 35.438 4.725-2.646v-3.943L125.491 28 36 78.313v4.963l89.491 50.279 81.413-45.765v20.063l-81.413 46.058-85.72-48.496L36 107.507V141.7l89.491 50.14 81.413-45.608v19.942l-81.413 46.058-85.72-48.514L36 165.811v5.05L125.491 221 215 170.861Z"/>
    </svg>
  );
}

function FabricLogo({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" className={className} aria-label="Microsoft Fabric" role="img">
      <path fill="url(#fc-a)" fillRule="evenodd" d="m5.64 31.6-.586 2.144c-.218.685-.524 1.693-.689 2.59a5.629 5.629 0 0 0 4.638 7.588c.792.114 1.688.108 2.692-.04l4.613-.636a2.924 2.924 0 0 0 2.421-2.127l3.175-11.662L5.64 31.599Z" clipRule="evenodd"/>
      <path fill="url(#fc-b)" d="M10.14 32.152c-4.863.753-5.861 4.423-5.861 4.423l4.656-17.11 24.333-3.292-3.318 12.052a1.706 1.706 0 0 1-1.388 1.244l-.136.022-18.423 2.684.137-.023Z"/>
      <path fill="url(#fc-c)" fillOpacity=".8" d="M10.14 32.152c-4.863.753-5.861 4.423-5.861 4.423l4.656-17.11 24.333-3.292-3.318 12.052a1.706 1.706 0 0 1-1.388 1.244l-.136.022-18.423 2.684.137-.023Z"/>
      <path fill="url(#fc-d)" d="m12.899 21.235 26.938-3.98a1.597 1.597 0 0 0 1.323-1.17l2.78-10.06a1.595 1.595 0 0 0-1.74-2.012L16.498 7.81a7.185 7.185 0 0 0-5.777 5.193L7.013 26.438c.744-2.717 1.202-4.355 5.886-5.203Z"/>
      <path fill="url(#fc-e)" d="m12.899 21.235 26.938-3.98a1.597 1.597 0 0 0 1.323-1.17l2.78-10.06a1.595 1.595 0 0 0-1.74-2.012L16.498 7.81a7.185 7.185 0 0 0-5.777 5.193L7.013 26.438c.744-2.717 1.202-4.355 5.886-5.203Z"/>
      <path fill="url(#fc-f)" fillOpacity=".4" d="m12.899 21.235 26.938-3.98a1.597 1.597 0 0 0 1.323-1.17l2.78-10.06a1.595 1.595 0 0 0-1.74-2.012L16.498 7.81a7.185 7.185 0 0 0-5.777 5.193L7.013 26.438c.744-2.717 1.202-4.355 5.886-5.203Z"/>
      <path fill="url(#fc-g)" d="M12.899 21.236c-3.901.706-4.87 1.962-5.514 3.932L4.279 36.577s.992-3.633 5.796-4.41l18.352-2.673.136-.022a1.707 1.707 0 0 0 1.388-1.244l2.73-9.915-19.782 2.923Z"/>
      <path fill="url(#fc-h)" fillOpacity=".2" d="M12.899 21.236c-3.901.706-4.87 1.962-5.514 3.932L4.279 36.577s.992-3.633 5.796-4.41l18.352-2.673.136-.022a1.707 1.707 0 0 0 1.388-1.244l2.73-9.915-19.782 2.923Z"/>
      <path fill="url(#fc-i)" fillRule="evenodd" d="M10.075 32.167c-4.06.657-5.392 3.345-5.71 4.164a5.629 5.629 0 0 0 4.638 7.59c.792.114 1.688.108 2.692-.039l4.613-.637a2.924 2.924 0 0 0 2.421-2.127l2.894-10.633-11.547 1.683-.001-.001Z" clipRule="evenodd"/>
      <defs>
        <linearGradient id="fc-a" x1="12.953" x2="12.953" y1="44.001" y2="29.457" gradientUnits="userSpaceOnUse"><stop offset=".056" stopColor="#2AAC94"/><stop offset=".155" stopColor="#239C87"/><stop offset=".372" stopColor="#177E71"/><stop offset=".588" stopColor="#0E6961"/><stop offset=".799" stopColor="#095D57"/><stop offset="1" stopColor="#085954"/></linearGradient>
        <linearGradient id="fc-b" x1="31.331" x2="17.286" y1="33.448" y2="18.173" gradientUnits="userSpaceOnUse"><stop offset=".042" stopColor="#ABE88E"/><stop offset=".549" stopColor="#2AAA92"/><stop offset=".906" stopColor="#117865"/></linearGradient>
        <linearGradient id="fc-c" x1="-3.182" x2="10.183" y1="32.706" y2="28.148" gradientUnits="userSpaceOnUse"><stop stopColor="#6AD6F9"/><stop offset="1" stopColor="#6AD6F9" stopOpacity="0"/></linearGradient>
        <linearGradient id="fc-d" x1="7.013" x2="42.589" y1="15.219" y2="15.219" gradientUnits="userSpaceOnUse"><stop offset=".043" stopColor="#25FFD4"/><stop offset=".874" stopColor="#55DDB9"/></linearGradient>
        <linearGradient id="fc-e" x1="7.013" x2="39.06" y1="10.247" y2="25.128" gradientUnits="userSpaceOnUse"><stop stopColor="#6AD6F9"/><stop offset=".23" stopColor="#60E9D0"/><stop offset=".651" stopColor="#6DE9BB"/><stop offset=".994" stopColor="#ABE88E"/></linearGradient>
        <linearGradient id="fc-f" x1="9.978" x2="27.404" y1="13.031" y2="16.885" gradientUnits="userSpaceOnUse"><stop stopColor="#fff" stopOpacity="0"/><stop offset=".459" stopColor="#fff"/><stop offset="1" stopColor="#fff" stopOpacity="0"/></linearGradient>
        <linearGradient id="fc-g" x1="15.756" x2="16.168" y1="27.96" y2="15.74" gradientUnits="userSpaceOnUse"><stop offset=".205" stopColor="#063D3B" stopOpacity="0"/><stop offset=".586" stopColor="#063D3B" stopOpacity=".237"/><stop offset=".872" stopColor="#063D3B" stopOpacity=".75"/></linearGradient>
        <linearGradient id="fc-h" x1="2.81" x2="17.701" y1="26.744" y2="29.545" gradientUnits="userSpaceOnUse"><stop stopColor="#fff" stopOpacity="0"/><stop offset=".459" stopColor="#fff"/><stop offset="1" stopColor="#fff" stopOpacity="0"/></linearGradient>
        <linearGradient id="fc-i" x1="13.567" x2="10.662" y1="39.97" y2="25.764" gradientUnits="userSpaceOnUse"><stop offset=".064" stopColor="#063D3B" stopOpacity="0"/><stop offset=".17" stopColor="#063D3B" stopOpacity=".135"/><stop offset=".562" stopColor="#063D3B" stopOpacity=".599"/><stop offset=".85" stopColor="#063D3B" stopOpacity=".9"/><stop offset="1" stopColor="#063D3B"/></linearGradient>
      </defs>
    </svg>
  );
}

/** Returns the topic-appropriate secondary logo component. */
function TopicLogo({ topic, className }: { topic: TopicId; className?: string }) {
  if (topic === "fabric") return <FabricLogo className={className} />;
  return <DatabricksLogo className={className} />;
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

export function ChatInterface({ topic = "databricks" }: { topic?: TopicId }) {
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
  } = useVoiceSession({ skill: topic });

  const config = TOPIC_CONFIG[topic];

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
      {/* Header with Azure + topic branding */}
      <header
        className="flex items-center justify-between px-6 py-3 border-b-2 border-[var(--accent)]"
        style={{ borderImage: `linear-gradient(to right, var(--topic-gradient-start), var(--topic-gradient-end)) 1` }}
      >
        <div className="flex items-center gap-3">
          <TopicLogo topic={topic} className="w-7 h-7" />
          <div className="h-5 w-px bg-[var(--border)]" />
          <div>
            <h1 className="text-sm font-semibold text-[var(--foreground)] leading-tight">
              Architecture Design Session
            </h1>
            <span className="text-xs text-[var(--muted)] hidden sm:inline">
              {config.subtitle}
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
                  <TopicLogo topic={topic} className="w-14 h-14" />
                </div>
                <h2 className="text-xl font-semibold text-[var(--foreground)] mb-2">
                  {config.label}
                </h2>
                <h3 className="text-lg text-[var(--accent-light)] mb-3">
                  Architecture Design Session
                </h3>
                {liteMode ? (
                  <>
                    <p className="text-sm text-[var(--muted)] max-w-md leading-relaxed">
                      {config.liteDescription}
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
                      {config.fullDescription}
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
