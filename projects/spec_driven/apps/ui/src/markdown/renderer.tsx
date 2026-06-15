import React, { useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeSanitize from "rehype-sanitize";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";
import { useNavigate } from "react-router-dom";
import { resolveLink } from "../lib/linkResolver";
import { BrokenLink } from "../components/BrokenLink";

export interface PinContext {
  projectType: string;
  projectName: string;
  stageFolder: "interview" | "findings" | "final_specs" | "validation";
  pinnedIds: Set<string>;
  onPin: (itemId: string) => void;
  onUnpin: (itemId: string) => void;
}

export interface PromptMode {
  onEditPrompt: () => void;
}

export interface RendererProps {
  content: string;
  currentPath: string;
  knownPaths: string[];
  pinContext?: PinContext | null;
  promptMode?: PromptMode | null;
}

const PIN_MARKER = /^(FR|NFR|AC|SYS|OQ)-(\d+[a-z]?)\.?$/;

function extractPinId(children: React.ReactNode): string | null {
  const arr = React.Children.toArray(children);
  if (arr.length === 0) return null;
  const first = arr[0];
  if (!React.isValidElement(first)) return null;
  if (first.type !== "strong") return null;
  const inner = React.Children.toArray(
    (first.props as { children?: React.ReactNode }).children,
  )
    .filter((c) => typeof c === "string")
    .join("");
  const m = PIN_MARKER.exec(inner.trim());
  if (!m) return null;
  return `${m[1]}-${m[2]}`;
}

function PinButton({
  itemId,
  ctx,
}: {
  itemId: string;
  ctx: PinContext;
}): JSX.Element {
  const pinned = ctx.pinnedIds.has(itemId);
  return (
    <button
      type="button"
      role="switch"
      aria-checked={pinned}
      aria-label={`${pinned ? "Unpin" : "Pin"} ${itemId}`}
      className="pin-toggle pin-toggle-md"
      title={pinned ? "Pinned (click to unpin)" : `Pin ${itemId} to ${ctx.stageFolder}/promoted.md`}
      onClick={() => (pinned ? ctx.onUnpin(itemId) : ctx.onPin(itemId))}
    >
      <span aria-hidden="true">📌</span>
    </button>
  );
}

function PromptBlock({
  onEdit,
  preProps,
  children,
}: {
  onEdit: () => void;
  preProps: Record<string, unknown>;
  children: React.ReactNode;
}): JSX.Element {
  const preRef = useRef<HTMLPreElement>(null);
  const [copied, setCopied] = useState<boolean>(false);

  const copy = async (e: React.MouseEvent): Promise<void> => {
    e.stopPropagation();
    const text = preRef.current?.innerText ?? "";
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard unavailable */
    }
  };

  return (
    <div
      className="prompt-block"
      role="button"
      tabIndex={0}
      title="Click to edit this prompt"
      onClick={onEdit}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onEdit();
        }
      }}
    >
      <div className="prompt-block-hint">
        <span aria-hidden="true">📋 copy-paste prompt · ✎ click to edit</span>
        <button
          type="button"
          className="prompt-block-copy"
          onClick={(e) => void copy(e)}
          aria-label="Copy prompt to clipboard"
        >
          {copied ? "Copied ✓" : "Copy"}
        </button>
      </div>
      <pre {...(preProps as React.HTMLAttributes<HTMLPreElement>)} ref={preRef}>
        {children}
      </pre>
    </div>
  );
}

export function Renderer({
  content,
  currentPath,
  knownPaths,
  pinContext,
  promptMode,
}: RendererProps): JSX.Element {
  const navigate = useNavigate();
  const known = useMemo(() => new Set(knownPaths), [knownPaths]);
  const isKnown = (p: string): boolean => known.has(p);
  const ctx = pinContext ?? null;
  const prompt = promptMode ?? null;

  return (
    <div className="markdown-view">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeSanitize, rehypeHighlight]}
        components={{
          pre: ({ children, ...rest }) => {
            if (!prompt) return <pre {...rest}>{children}</pre>;
            return (
              <PromptBlock onEdit={prompt.onEditPrompt} preProps={rest}>
                {children}
              </PromptBlock>
            );
          },
          a: ({ href, children, ...rest }) => {
            if (typeof href !== "string") {
              return <span>{children}</span>;
            }
            const resolved = resolveLink({ currentFile: currentPath, href, isKnown });
            if (resolved.kind === "external") {
              return (
                <a href={resolved.href} target="_blank" rel="noopener noreferrer" {...rest}>
                  {children}
                </a>
              );
            }
            if (resolved.kind === "anchor") {
              return (
                <a href={resolved.hash} {...rest}>
                  {children}
                </a>
              );
            }
            if (resolved.kind === "internal") {
              const target = `/file/${encodeURIComponent(resolved.path)}${resolved.hash ?? ""}`;
              return (
                <a
                  href={target}
                  onClick={(e) => {
                    e.preventDefault();
                    navigate(target);
                  }}
                >
                  {children}
                </a>
              );
            }
            return (
              <BrokenLink href={resolved.href} title={resolved.title}>
                {children}
              </BrokenLink>
            );
          },
          p: ({ children, ...rest }) => {
            const id = ctx ? extractPinId(children) : null;
            if (!id || !ctx) return <p {...rest}>{children}</p>;
            return (
              <p {...rest} data-pin-id={id}>
                {children}
                <PinButton itemId={id} ctx={ctx} />
              </p>
            );
          },
          li: ({ children, ...rest }) => {
            if (!ctx) return <li {...rest}>{children}</li>;
            const arr = React.Children.toArray(children);
            const id = extractPinId(children);
            if (id) {
              return (
                <li {...rest} data-pin-id={id}>
                  {children}
                  <PinButton itemId={id} ctx={ctx} />
                </li>
              );
            }
            const firstEl = arr.find((c) => React.isValidElement(c));
            if (firstEl && React.isValidElement(firstEl) && firstEl.type === "p") {
              const innerId = extractPinId(
                (firstEl.props as { children?: React.ReactNode }).children,
              );
              if (innerId) {
                return (
                  <li {...rest} data-pin-id={innerId}>
                    {children}
                    <PinButton itemId={innerId} ctx={ctx} />
                  </li>
                );
              }
            }
            return <li {...rest}>{children}</li>;
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
