"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { createPortal } from "react-dom";

let mermaidInitialized = false;
type MermaidAPI = { default: { initialize: (config: Record<string, unknown>) => void; render: (id: string, code: string) => Promise<{ svg: string }> } };
let mermaidModule: MermaidAPI | null = null;

/** Monotonically increasing ID to avoid collisions between renders. */
let idCounter = 0;

interface MermaidDiagramProps {
  code: string;
}

/** Fullscreen overlay for viewing the diagram at maximum size. */
function DiagramModal({ svg, onClose }: { svg: string; onClose: () => void }) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="relative w-[95vw] h-[90vh] bg-white rounded-xl shadow-2xl flex flex-col">
        {/* Header bar */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--accent)]/20 shrink-0">
          <span className="text-sm font-medium text-gray-700">Architecture Diagram</span>
          <button
            type="button"
            onClick={onClose}
            className="flex items-center justify-center w-8 h-8 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-[var(--accent)] transition-colors"
            aria-label="Close"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
        {/* Scrollable SVG area */}
        <div
          className="flex-1 overflow-auto p-6 flex items-start justify-center"
          dangerouslySetInnerHTML={{ __html: svg }}
        />
      </div>
    </div>,
    document.body
  );
}

/** Download raw Mermaid source as a .mmd file. */
function downloadMmd(code: string) {
  const blob = new Blob([code], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `architecture-diagram-${Date.now()}.mmd`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function MermaidDiagram({ code }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showCode, setShowCode] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const renderDiagram = useCallback(async () => {
    try {
      if (!mermaidModule) {
        const mod = await import("mermaid");
        mermaidModule = mod as unknown as MermaidAPI;
      }
      if (!mermaidInitialized) {
        mermaidModule.default.initialize({
          startOnLoad: false,
          theme: "dark",
          securityLevel: "loose",
          fontFamily: "ui-monospace, monospace",
        });
        mermaidInitialized = true;
      }

      const id = `mermaid-${++idCounter}`;
      const { svg: rendered } = await mermaidModule.default.render(id, code.trim());
      setSvg(rendered);
      setError(null);
    } catch (err) {
      console.error("Mermaid render failed:", err);
      setError(err instanceof Error ? err.message : "Failed to render diagram");
      setSvg(null);
    }
  }, [code]);

  useEffect(() => {
    renderDiagram();
  }, [renderDiagram]);

  if (error) {
    return (
      <div className="my-2">
        <div className="text-xs text-yellow-400 mb-1">⚠ Diagram render failed — showing source</div>
        <pre className="bg-black/30 rounded-lg p-3 overflow-x-auto text-xs">
          <code>{code}</code>
        </pre>
      </div>
    );
  }

  if (!svg) {
    return (
      <div className="my-2 flex items-center gap-2 text-xs text-[var(--muted)]">
        <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
        Rendering diagram…
      </div>
    );
  }

  return (
    <div className="my-2">
      <div
        ref={containerRef}
        className="bg-white rounded-lg p-4 overflow-x-auto"
        dangerouslySetInnerHTML={{ __html: svg }}
      />
      {/* Toolbar */}
      <div className="flex items-center gap-3 mt-1.5">
        <button
          type="button"
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-1 text-xs text-[var(--muted)] hover:text-[var(--accent-light)] transition-colors"
          title="View full screen"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
            <polyline points="15 3 21 3 21 9" />
            <polyline points="9 21 3 21 3 15" />
            <line x1="21" y1="3" x2="14" y2="10" />
            <line x1="3" y1="21" x2="10" y2="14" />
          </svg>
          Maximize
        </button>
        <button
          type="button"
          onClick={() => downloadMmd(code)}
          className="inline-flex items-center gap-1 text-xs text-[var(--muted)] hover:text-[var(--accent-light)] transition-colors"
          title="Download .mmd file"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          Download .mmd
        </button>
        <button
          type="button"
          onClick={() => setShowCode((v) => !v)}
          className="inline-flex items-center gap-1 text-xs text-[var(--muted)] hover:text-[var(--accent-light)] transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
            <polyline points="16 18 22 12 16 6" />
            <polyline points="8 6 2 12 8 18" />
          </svg>
          {showCode ? "Hide" : "Show"} source
        </button>
      </div>
      {showCode && (
        <pre className="bg-black/30 rounded-lg p-3 overflow-x-auto mt-1 text-xs">
          <code>{code}</code>
        </pre>
      )}
      {showModal && <DiagramModal svg={svg} onClose={() => setShowModal(false)} />}
    </div>
  );
}
