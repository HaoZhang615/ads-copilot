"use client";

import { useEffect, useRef, useState, useCallback } from "react";

let mermaidInitialized = false;
type MermaidAPI = { default: { initialize: (config: Record<string, unknown>) => void; render: (id: string, code: string) => Promise<{ svg: string }> } };
let mermaidModule: MermaidAPI | null = null;

/** Monotonically increasing ID to avoid collisions between renders. */
let idCounter = 0;

interface MermaidDiagramProps {
  code: string;
}

export function MermaidDiagram({ code }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showCode, setShowCode] = useState(false);

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
      <button
        type="button"
        onClick={() => setShowCode((v) => !v)}
        className="mt-1 text-xs text-[var(--muted)] hover:text-[var(--foreground)] transition-colors"
      >
        {showCode ? "Hide" : "Show"} source
      </button>
      {showCode && (
        <pre className="bg-black/30 rounded-lg p-3 overflow-x-auto mt-1 text-xs">
          <code>{code}</code>
        </pre>
      )}
    </div>
  );
}