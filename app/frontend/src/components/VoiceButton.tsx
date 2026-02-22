"use client";

import { WaveformVisualizer } from "@/components/WaveformVisualizer";

interface VoiceButtonProps {
  isListening: boolean;
  audioLevel: number;
  disabled: boolean;
  onClick: () => void;
}

export function VoiceButton({
  isListening,
  audioLevel,
  disabled,
  onClick,
}: VoiceButtonProps) {
  return (
    <div className="flex flex-col items-center gap-2">
      <button
        type="button"
        onClick={onClick}
        disabled={disabled}
        aria-label={isListening ? "Stop recording" : "Start recording"}
        className={`relative flex items-center justify-center w-14 h-14 rounded-full transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[var(--accent)] focus:ring-offset-2 focus:ring-offset-[var(--background)] ${
          disabled
            ? "bg-gray-700 text-gray-500 cursor-not-allowed"
            : isListening
              ? "bg-[var(--danger)] text-white hover:bg-[#e02e1a]"
              : "bg-[var(--surface)] text-[var(--foreground)] hover:bg-[var(--accent)]/10 border border-[var(--border)]"
        }`}
      >
        {isListening && (
          <span className="absolute inset-0 rounded-full bg-[var(--danger)] animate-pulse-ring" />
        )}
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
          className="relative z-10 w-6 h-6"
        >
          <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
          <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
          <line x1="12" x2="12" y1="19" y2="22" />
        </svg>
      </button>
      <WaveformVisualizer audioLevel={audioLevel} isActive={isListening} />
    </div>
  );
}
