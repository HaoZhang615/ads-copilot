"use client";

import { memo } from "react";
import type { Message } from "@/hooks/useVoiceSession";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { MermaidDiagram } from "./MermaidDiagram";

interface MessageBubbleProps {
  message: Message;
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

/* ── Stable remark plugins array (allocated once, never re-created) ── */
const remarkPlugins = [remarkGfm];

/* ── Module-level Markdown component overrides (stable references) ── */

function MdP({ children }: { children?: React.ReactNode }) {
  return <p className="mb-2 last:mb-0">{children}</p>;
}
function MdStrong({ children }: { children?: React.ReactNode }) {
  return <strong className="font-semibold">{children}</strong>;
}
function MdUl({ children }: { children?: React.ReactNode }) {
  return <ul className="list-disc pl-4 mb-2">{children}</ul>;
}
function MdOl({ children }: { children?: React.ReactNode }) {
  return <ol className="list-decimal pl-4 mb-2">{children}</ol>;
}
function MdLi({ children }: { children?: React.ReactNode }) {
  return <li className="mb-0.5">{children}</li>;
}
function MdH1({ children }: { children?: React.ReactNode }) {
  return (
    <h1 className="text-base font-bold mb-2 mt-3 first:mt-0">{children}</h1>
  );
}
function MdH2({ children }: { children?: React.ReactNode }) {
  return (
    <h2 className="text-sm font-bold mb-1.5 mt-2.5 first:mt-0">{children}</h2>
  );
}
function MdH3({ children }: { children?: React.ReactNode }) {
  return (
    <h3 className="text-sm font-semibold mb-1 mt-2 first:mt-0">{children}</h3>
  );
}
function MdTable({ children }: { children?: React.ReactNode }) {
  return (
    <div className="overflow-x-auto mb-2">
      <table className="text-xs border-collapse border border-[var(--border)] w-full">
        {children}
      </table>
    </div>
  );
}
function MdTh({ children }: { children?: React.ReactNode }) {
  return (
    <th className="border border-[var(--border)] px-2 py-1 text-left font-semibold bg-[var(--surface)]">
      {children}
    </th>
  );
}
function MdTd({ children }: { children?: React.ReactNode }) {
  return (
    <td className="border border-[var(--border)] px-2 py-1">{children}</td>
  );
}
function MdPre({ children }: { children?: React.ReactNode }) {
  return <>{children}</>;
}
function MdA({
  href,
  children,
}: {
  href?: string;
  children?: React.ReactNode;
}) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-[var(--accent-light)] underline hover:text-[var(--accent)]"
    >
      {children}
    </a>
  );
}
function MdHr() {
  return <hr className="border-[var(--border)] my-2" />;
}
function MdBlockquote({ children }: { children?: React.ReactNode }) {
  return (
    <blockquote className="border-l-2 border-[var(--accent)] pl-3 italic opacity-80 mb-2">
      {children}
    </blockquote>
  );
}

/**
 * Build the ReactMarkdown `components` map.
 *
 * All component functions except `code` are module-level constants, so React
 * sees the exact same reference every render. The `code` renderer needs
 * `message.isStreaming` which varies per-message, so it's a closure — but
 * because the entire MessageBubble is wrapped in `React.memo`, this function
 * only runs when the message prop actually changes.
 */
function markdownComponents(message: Message) {
  return {
    p: MdP,
    strong: MdStrong,
    ul: MdUl,
    ol: MdOl,
    li: MdLi,
    h1: MdH1,
    h2: MdH2,
    h3: MdH3,
    table: MdTable,
    th: MdTh,
    td: MdTd,
    pre: MdPre,
    a: MdA,
    hr: MdHr,
    blockquote: MdBlockquote,
    code: ({
      className,
      children,
    }: {
      className?: string;
      children?: React.ReactNode;
    }) => {
      const isMermaid = className === "language-mermaid";
      const isBlock = className?.startsWith("language-");
      if (isMermaid) {
        /* While streaming, every text delta re-mounts MermaidDiagram,
           resetting its async render state back to the spinner.
           Defer diagram rendering until the message is finalised. */
        if (message.isStreaming) {
          return (
            <div className="my-2 flex items-center gap-2 text-xs text-[var(--muted)]">
              <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
              Diagram will render when response completes…
            </div>
          );
        }
        /* Extract raw text from React children */
        const raw = String(children).replace(/\n$/, "");
        return <MermaidDiagram code={raw} />;
      }
      if (isBlock) {
        return (
          <pre className="bg-black/30 rounded-lg p-3 overflow-x-auto mb-2 text-xs">
            <code>{children}</code>
          </pre>
        );
      }
      return (
        <code className="bg-black/20 rounded px-1 py-0.5 text-xs">
          {children}
        </code>
      );
    },
  };
}

function MessageBubbleInner({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-3`}
    >
      <div
        className={`${isUser ? "max-w-[75%]" : "max-w-[90%]"} rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-[var(--accent)] text-white rounded-br-md"
            : "bg-[var(--surface)] text-[var(--foreground)] rounded-bl-md border border-[var(--border)]"
        }`}
      >
        {isUser ? (
          <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
            {message.content}
          </p>
        ) : (
          <div className="text-sm leading-relaxed break-words prose prose-sm prose-invert max-w-none">
            <ReactMarkdown
              remarkPlugins={remarkPlugins}
              components={markdownComponents(message)}
            >
              {message.content}
            </ReactMarkdown>
            {message.isStreaming && (
              <span className="inline-block w-2 h-4 ml-1 bg-[var(--accent)] rounded-sm animate-blink align-middle" />
            )}
          </div>
        )}
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

/**
 * Memoised message bubble — prevents re-renders caused by unrelated parent
 * state changes (e.g. `audioLevel` updating at ~60 fps while the mic is on).
 * Without this memo, every audioLevel tick re-creates the ReactMarkdown
 * `components` prop → React unmounts & remounts MermaidDiagram → the async
 * mermaid.render() call restarts from scratch → perpetual spinner.
 */
export const MessageBubble = memo(MessageBubbleInner);
