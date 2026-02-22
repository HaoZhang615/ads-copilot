"use client";

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

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-3`}
    >
      <div
        className={`${isUser ? "max-w-[75%]" : "max-w-[90%]"} rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white rounded-br-md"
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
              remarkPlugins={[remarkGfm]}
              components={{
                /* Style overrides so markdown fits the chat bubble */
                p: ({ children }) => (
                  <p className="mb-2 last:mb-0">{children}</p>
                ),
                strong: ({ children }) => (
                  <strong className="font-semibold">{children}</strong>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc pl-4 mb-2">{children}</ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal pl-4 mb-2">{children}</ol>
                ),
                li: ({ children }) => <li className="mb-0.5">{children}</li>,
                h1: ({ children }) => (
                  <h1 className="text-base font-bold mb-2 mt-3 first:mt-0">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-sm font-bold mb-1.5 mt-2.5 first:mt-0">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-sm font-semibold mb-1 mt-2 first:mt-0">
                    {children}
                  </h3>
                ),
                table: ({ children }) => (
                  <div className="overflow-x-auto mb-2">
                    <table className="text-xs border-collapse border border-[var(--border)] w-full">
                      {children}
                    </table>
                  </div>
                ),
                th: ({ children }) => (
                  <th className="border border-[var(--border)] px-2 py-1 text-left font-semibold bg-[var(--surface)]">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="border border-[var(--border)] px-2 py-1">
                    {children}
                  </td>
                ),
                code: ({ className, children }) => {
                  const isMermaid = className === "language-mermaid";
                  const isBlock = className?.startsWith("language-");
                  if (isMermaid) {
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
                pre: ({ children }) => <>{children}</>,
                a: ({ href, children }) => (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 underline"
                  >
                    {children}
                  </a>
                ),
                hr: () => (
                  <hr className="border-[var(--border)] my-2" />
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-2 border-[var(--border)] pl-3 italic opacity-80 mb-2">
                    {children}
                  </blockquote>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
            {message.isStreaming && (
              <span className="inline-block w-2 h-4 ml-1 bg-current rounded-sm animate-blink align-middle" />
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
