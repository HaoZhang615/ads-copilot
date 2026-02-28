"use client";

import { useEffect, useCallback, useRef, useState } from "react";
import { createPortal } from "react-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { MermaidDiagram } from "./MermaidDiagram";

/** Lazy-loaded PDF dependencies (only imported when user clicks "Download PDF"). */
async function loadPdfDeps() {
  const [{ default: html2canvas }, { jsPDF }] = await Promise.all([
    import("html2canvas-pro"),
    import("jspdf"),
  ]);
  return { html2canvas, jsPDF };
}

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

/**
 * Shared PDF builder: captures the rendered summary as a multi-page JPEG-based PDF.
 * Uses html2canvas-pro to rasterize the DOM (including rendered Mermaid SVGs)
 * and jsPDF to assemble pages with per-page canvas slicing for small file size.
 */
async function buildPdf(element: HTMLDivElement) {
  const { html2canvas, jsPDF } = await loadPdfDeps();

  /* Temporarily expand the element so html2canvas captures full scrollable content */
  const origHeight = element.style.height;
  const origOverflow = element.style.overflow;
  const origMaxHeight = element.style.maxHeight;
  const origFlex = element.style.flex;
  element.style.height = "auto";
  element.style.overflow = "visible";
  element.style.maxHeight = "none";
  element.style.flex = "none";

  try {
    const canvas = await html2canvas(element, {
      scale: 1.5,
      useCORS: true,
      logging: false,
      backgroundColor: "#1a1a2e",
    });

    /* A4 dimensions in mm */
    const pageW = 210;
    const pageH = 297;
    const margin = 10;
    const contentW = pageW - margin * 2;
    const contentH = pageH - margin * 2;

    /* How many canvas pixels correspond to one PDF content-area page */
    const pxPerMm = canvas.width / contentW;
    const pxPageHeight = Math.floor(contentH * pxPerMm);
    const totalHeight = canvas.height;
    const nPages = Math.ceil(totalHeight / pxPageHeight);

    const pdf = new jsPDF({
      orientation: "portrait",
      unit: "mm",
      format: "a4",
      compress: true,
    });

    /* Per-page canvas slicing: extract one page-sized strip at a time and encode as JPEG */
    const pageCanvas = document.createElement("canvas");
    const pageCtx = pageCanvas.getContext("2d")!;
    pageCanvas.width = canvas.width;

    for (let page = 0; page < nPages; page++) {
      const sliceHeight = Math.min(
        pxPageHeight,
        totalHeight - page * pxPageHeight,
      );
      pageCanvas.height = sliceHeight;

      /* Fill with background colour to avoid white flash on the final (partial) page */
      pageCtx.fillStyle = "#1a1a2e";
      pageCtx.fillRect(0, 0, pageCanvas.width, sliceHeight);

      pageCtx.drawImage(
        canvas,
        0,
        page * pxPageHeight,
        canvas.width,
        sliceHeight,
        0,
        0,
        canvas.width,
        sliceHeight,
      );

      if (page > 0) pdf.addPage();

      const imgData = pageCanvas.toDataURL("image/jpeg", 0.8);
      const actualPageH = (sliceHeight / canvas.width) * contentW;
      pdf.addImage(imgData, "JPEG", margin, margin, contentW, actualPageH);
    }

    return pdf;
  } finally {
    /* Restore original styles */
    element.style.height = origHeight;
    element.style.overflow = origOverflow;
    element.style.maxHeight = origMaxHeight;
    element.style.flex = origFlex;
  }
}

/** Download the rendered summary as a multi-page PDF. */
async function downloadPdf(element: HTMLDivElement) {
  const pdf = await buildPdf(element);
  pdf.save(`ads-session-summary-${new Date().toISOString().slice(0, 10)}.pdf`);
}

/**
 * Generate PDF as base64 string (for email attachment).
 * Reuses the same buildPdf pipeline as downloadPdf.
 */
async function generatePdfBase64(element: HTMLDivElement): Promise<string> {
  const pdf = await buildPdf(element);
  /* pdf.output('datauristring') returns 'data:application/pdf;base64,...' */
  const dataUri = pdf.output("datauristring");
  return dataUri.split(",")[1];
}

export function SessionSummaryModal({
  summary,
  isGenerating,
  onDismiss,
}: SessionSummaryModalProps) {
  const contentRef = useRef<HTMLDivElement>(null);
  const [isPdfGenerating, setIsPdfGenerating] = useState(false);
  const [showEmailForm, setShowEmailForm] = useState(false);
  const [emailAddress, setEmailAddress] = useState("");
  const [isEmailSending, setIsEmailSending] = useState(false);
  const [emailStatus, setEmailStatus] = useState<"idle" | "sent" | "error">("idle");

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

  const handleDownloadPdf = useCallback(async () => {
    if (!contentRef.current || isPdfGenerating) return;
    setIsPdfGenerating(true);
    try {
      await downloadPdf(contentRef.current);
    } finally {
      setIsPdfGenerating(false);
    }
  }, [isPdfGenerating]);

  const handleSendEmail = useCallback(async () => {
    if (!contentRef.current || !emailAddress.trim() || isEmailSending) return;
    setIsEmailSending(true);
    setEmailStatus("idle");
    try {
      const pdfBase64 = await generatePdfBase64(contentRef.current);
      const date = new Date().toISOString().slice(0, 10);
      const res = await fetch("/api/send-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          to: emailAddress.trim(),
          subject: `ADS Session Summary — ${date}`,
          body: "<p>Please find your ADS session summary attached as a PDF.</p>",
          pdf_base64: pdfBase64,
          pdf_filename: `ads-session-summary-${date}.pdf`,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      setEmailStatus("sent");
    } catch (err) {
      console.error("Failed to send email:", err);
      setEmailStatus("error");
    } finally {
      setIsEmailSending(false);
    }
  }, [emailAddress, isEmailSending]);

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
        <div ref={contentRef} className="flex-1 overflow-y-auto px-6 py-5 scrollbar-thin">
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
          <div className="px-6 py-3 border-t border-[var(--border)] shrink-0 space-y-3">
            {/* Email form */}
            {showEmailForm ? (
              <div className="flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4 text-[var(--muted)] shrink-0">
                  <rect x="2" y="4" width="20" height="16" rx="2" />
                  <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                </svg>
                <input
                  type="email"
                  placeholder="recipient@example.com"
                  value={emailAddress}
                  onChange={(e) => { setEmailAddress(e.target.value); setEmailStatus("idle"); }}
                  onKeyDown={(e) => { if (e.key === "Enter") handleSendEmail(); }}
                  disabled={isEmailSending}
                  className="flex-1 text-sm px-3 py-1.5 rounded-lg bg-[var(--surface)] text-[var(--foreground)] border border-[var(--border)] focus:outline-none focus:border-[var(--accent)] placeholder:text-[var(--muted)] disabled:opacity-50"
                  aria-label="Recipient email address"
                />
                <button
                  type="button"
                  onClick={handleSendEmail}
                  disabled={isEmailSending || !emailAddress.trim()}
                  className="inline-flex items-center gap-1.5 text-sm px-4 py-1.5 rounded-lg bg-[var(--accent)] text-white hover:bg-[var(--accent-hover)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isEmailSending ? (
                    <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
                      <line x1="22" y1="2" x2="11" y2="13" />
                      <polygon points="22 2 15 22 11 13 2 9 22 2" />
                    </svg>
                  )}
                  Send
                </button>
                <button
                  type="button"
                  onClick={() => { setShowEmailForm(false); setEmailStatus("idle"); }}
                  className="text-sm px-2 py-1.5 rounded-lg text-[var(--muted)] hover:text-[var(--foreground)] transition-colors"
                  aria-label="Cancel email"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </button>
              </div>
            ) : null}
            {/* Email status messages */}
            {emailStatus === "sent" && (
              <p className="text-xs text-green-400">✓ Email sent successfully to {emailAddress}</p>
            )}
            {emailStatus === "error" && (
              <p className="text-xs text-red-400">Failed to send email. Please check the address and try again.</p>
            )}
            {/* Action buttons */}
            <div className="flex items-center justify-end gap-3">
              {!showEmailForm && (
                <button
                  type="button"
                  onClick={() => setShowEmailForm(true)}
                  className="inline-flex items-center gap-1.5 text-sm px-4 py-2 rounded-lg bg-[var(--surface)] text-[var(--foreground)] hover:bg-[var(--surface-hover)] border border-[var(--border)] transition-colors"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
                    <rect x="2" y="4" width="20" height="16" rx="2" />
                    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                  </svg>
                  Email PDF
                </button>
              )}
              <button
                type="button"
                onClick={() => downloadMarkdown(content)}
                className="inline-flex items-center gap-1.5 text-sm px-4 py-2 rounded-lg bg-[var(--surface)] text-[var(--foreground)] hover:bg-[var(--surface-hover)] border border-[var(--border)] transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="7 10 12 15 17 10" />
                  <line x1="12" y1="15" x2="12" y2="3" />
                </svg>
                Download .md
              </button>
              <button
                type="button"
                onClick={handleDownloadPdf}
                disabled={isPdfGenerating}
                className="inline-flex items-center gap-1.5 text-sm px-4 py-2 rounded-lg bg-[var(--accent)] text-white hover:bg-[var(--accent-hover)] transition-colors disabled:opacity-50 disabled:cursor-wait"
              >
                {isPdfGenerating ? (
                  <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="7 10 12 15 17 10" />
                    <line x1="12" y1="15" x2="12" y2="3" />
                  </svg>
                )}
                Download .pdf
              </button>
              <button
                type="button"
                onClick={onDismiss}
                className="text-sm px-4 py-2 rounded-lg bg-[var(--surface)] text-[var(--foreground)] hover:bg-[var(--surface-hover)] border border-[var(--border)] transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>,
    document.body
  );
}
