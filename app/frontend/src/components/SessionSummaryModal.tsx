"use client";

import { useEffect, useCallback } from "react";
import { createPortal } from "react-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { MermaidDiagram } from "./MermaidDiagram";

interface SessionSummaryModalProps {
  summary: string | null;
  isGenerating: boolean;
  onDismiss: () => void;
}

/* ── Stable remark plugins array (allocated once) ── */
const remarkPlugins = [remarkGfm];

/* ── Module-level Markdown component overrides (matching MessageBubble style) ── */

function MdP({ children }: { children?: React.ReactNode }) {
  return <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>;
}
function MdStrong({ children }: { children?: React.ReactNode }) {
  return <strong className="font-semibold">{children}</strong>;
}
function MdUl({ children }: { children?: React.ReactNode }) {
  return <ul className="list-disc pl-5 mb-3">{children}</ul>;
}
function MdOl({ children }: { children?: React.ReactNode }) {
  return <ol className="list-decimal pl-5 mb-3">{children}</ol>;
}
function MdLi({ children }: { children?: React.ReactNode }) {
  return <li className="mb-1">{children}</li>;
}
function MdH1({ children }: { children?: React.ReactNode }) {
  return (
    <h1 className="text-xl font-bold mb-3 mt-6 first:mt-0 text-[var(--foreground)]">
      {children}
    </h1>
  );
}
function MdH2({ children }: { children?: React.ReactNode }) {
  return (
    <h2 className="text-lg font-bold mb-2 mt-5 first:mt-0 text-[var(--foreground)]">
      {children}
    </h2>
  );
}
function MdH3({ children }: { children?: React.ReactNode }) {
  return (
    <h3 className="text-base font-semibold mb-2 mt-4 first:mt-0 text-[var(--foreground)]">
      {children}
    </h3>
  );
}
function MdTable({ children }: { children?: React.ReactNode }) {
  return (
    <div className="overflow-x-auto mb-3">
      <table className="text-sm border-collapse border border-[var(--border)] w-full">
        {children}
      </table>
    </div>
  );
}
function MdTh({ children }: { children?: React.ReactNode }) {
  return (
    <th className="border border-[var(--border)] px-3 py-1.5 text-left font-semibold bg-[var(--surface)]">
      {children}
    </th>
  );
}
function MdTd({ children }: { children?: React.ReactNode }) {
  return (
    <td className="border border-[var(--border)] px-3 py-1.5">{children}</td>
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
  return <hr className="border-[var(--border)] my-4" />;
}
function MdBlockquote({ children }: { children?: React.ReactNode }) {
  return (
    <blockquote className="border-l-2 border-[var(--accent)] pl-4 italic opacity-80 mb-3">
      {children}
    </blockquote>
  );
}

/** Code renderer — renders mermaid fences via MermaidDiagram, others as code blocks. */
function MdCode({
  className,
  children,
}: {
  className?: string;
  children?: React.ReactNode;
}) {
  const isMermaid = className === "language-mermaid";
  const isBlock = className?.startsWith("language-");

  if (isMermaid) {
    const raw = String(children).replace(/\n$/, "");
    return <MermaidDiagram code={raw} />;
  }
  if (isBlock) {
    return (
      <pre className="bg-black/30 rounded-lg p-3 overflow-x-auto mb-3 text-xs">
        <code>{children}</code>
      </pre>
    );
  }
  return (
    <code className="bg-black/20 rounded px-1 py-0.5 text-xs">
      {children}
    </code>
  );
}

/* ── Stable components map (allocated once since no per-instance closure needed) ── */
const markdownComponents = {
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
  code: MdCode,
};

/** Download the summary as a .md file. */
function downloadMarkdown(content: string) {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `ads-session-summary-${new Date().toISOString().slice(0, 10)}.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function SessionSummaryModal({
  summary,
  isGenerating,
  onDismiss,
}: SessionSummaryModalProps) {
  /* Close on Escape key */
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape" && !isGenerating) onDismiss();
    },
    [isGenerating, onDismiss]
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  const content = summary || "";

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
      onClick={(e) => {
        if (e.target === e.currentTarget && !isGenerating) onDismiss();
      }}
    >
      <div className="relative w-[95vw] max-w-4xl h-[90vh] bg-[var(--background)] border border-[var(--border)] rounded-xl shadow-2xl flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border)] shrink-0">
          <div className="flex items-center gap-3">
            {/* Document icon */}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={1.5}
              strokeLinecap="round"
              strokeLinejoin="round"
              className="w-5 h-5 text-[var(--accent)]"
            >
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
            <h2 className="text-base font-semibold text-[var(--foreground)]">
              Session Summary
            </h2>
            {isGenerating && (
              <div className="flex items-center gap-2 text-xs text-[var(--muted)]">
                <span className="inline-block w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                Generating…
              </div>
            )}
          </div>
          <div className="flex items-center gap-2">
            {/* Download button — only when summary is available */}
            {content && !isGenerating && (
              <button
                type="button"
                onClick={() => downloadMarkdown(content)}
                className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-[var(--surface)] text-[var(--foreground)] hover:bg-[var(--surface-hover)] border border-[var(--border)] transition-colors"
                title="Download as Markdown"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="w-3.5 h-3.5"
                >
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="7 10 12 15 17 10" />
                  <line x1="12" y1="15" x2="12" y2="3" />
                </svg>
                Download .md
              </button>
            )}
            {/* Close button */}
            <button
              type="button"
              onClick={onDismiss}
              disabled={isGenerating}
              className="flex items-center justify-center w-8 h-8 rounded-lg hover:bg-[var(--surface-hover)] text-[var(--muted)] hover:text-[var(--foreground)] transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              aria-label="Close summary"
            >
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
            </button>
          </div>
        </div>

        {/* Scrollable content area */}
        <div className="flex-1 overflow-y-auto px-6 py-5 scrollbar-thin">
          {!content && isGenerating ? (
            /* Initial loading state before any text arrives */
            <div className="flex flex-col items-center justify-center h-full text-center">
              <span className="inline-block w-8 h-8 border-2 border-[var(--accent)] border-t-transparent rounded-full animate-spin mb-4" />
              <p className="text-sm text-[var(--muted)]">
                Generating session summary…
              </p>
              <p className="text-xs text-[var(--muted)] mt-1 opacity-70">
                This may take a moment
              </p>
            </div>
          ) : (
            <div className="text-sm leading-relaxed text-[var(--foreground)] prose prose-sm prose-invert max-w-none">
              <ReactMarkdown
                remarkPlugins={remarkPlugins}
                components={markdownComponents}
              >
                {content}
              </ReactMarkdown>
              {isGenerating && (
                <span className="inline-block w-2 h-4 ml-1 bg-[var(--accent)] rounded-sm animate-blink align-middle" />
              )}
            </div>
          )}
        </div>

        {/* Footer — only visible when summary is complete */}
        {content && !isGenerating && (
          <div className="flex items-center justify-end gap-3 px-6 py-3 border-t border-[var(--border)] shrink-0">
            <button
              type="button"
              onClick={() => downloadMarkdown(content)}
              className="inline-flex items-center gap-1.5 text-sm px-4 py-2 rounded-lg bg-[var(--accent)] text-white hover:bg-[var(--accent-hover)] transition-colors"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
                className="w-4 h-4"
              >
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              Download as Markdown
            </button>
            <button
              type="button"
              onClick={onDismiss}
              className="text-sm px-4 py-2 rounded-lg bg-[var(--surface)] text-[var(--foreground)] hover:bg-[var(--surface-hover)] border border-[var(--border)] transition-colors"
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>,
    document.body
  );
}
