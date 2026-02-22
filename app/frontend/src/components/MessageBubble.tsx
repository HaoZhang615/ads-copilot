"use client";

import type { Message } from "@/hooks/useVoiceSession";

interface MessageBubbleProps {
  message: Message;
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-3`}
    >
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white rounded-br-md"
            : "bg-[var(--surface)] text-[var(--foreground)] rounded-bl-md border border-[var(--border)]"
        }`}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
          {message.content}
          {message.isStreaming && (
            <span className="inline-block w-2 h-4 ml-1 bg-current rounded-sm animate-blink align-middle" />
          )}
        </p>
        <p
          className={`text-xs mt-1.5 ${
            isUser ? "text-blue-200" : "text-[var(--muted)]"
          }`}
        >
          {formatTime(message.timestamp)}
        </p>
      </div>
    </div>
  );
}
