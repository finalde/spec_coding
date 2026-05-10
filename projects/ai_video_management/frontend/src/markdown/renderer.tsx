import { useMemo, useState, useRef, useCallback } from "react";
import type { ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import rehypeSanitize from "rehype-sanitize";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";
import { useNavigate } from "react-router-dom";
import { resolveLink } from "../lib/linkResolver";
import { BrokenLink } from "../components/BrokenLink";

export interface RendererProps {
  content: string;
  currentPath: string;
  knownPaths: string[];
}

/** Pre-render regex pass wrapping locked-descriptor blocks in <span class="locked-block">.
 * Pattern is GENERAL across characters: `【.+ · .+ · 锁定描述符 v\d+】 ... 禁用 ...。`
 */
const LOCKED_BLOCK_RE = /(【.+? · .+? · 锁定描述符 v\d+】[\s\S]*?禁用 [^\n]*?。)/g;

/** Pre-render regex pass wrapping `{ref_xxx}` placeholders in <span class="ref-placeholder">.
 * Match Chinese / ASCII identifier inside {ref_...}. Skip any inside fenced code blocks
 * by leveraging a state-machine pass.
 */
const REF_PLACEHOLDER_RE = /\{ref_([一-鿿\w-]+)\}/g;

function applyLockedBlockPill(source: string): string {
  return source.replace(LOCKED_BLOCK_RE, (m) => {
    return `<span class="locked-block" title="byte-equality contract — see characters/main.md" aria-describedby="locked-block-desc">${m}</span>`;
  });
}

/** Apply ref-placeholder pill only OUTSIDE fenced code blocks.
 * Inside code fences (the prompt body), placeholders MUST stay raw `{ref_xxx}` so the copy
 * button copies verbatim text. The reference table above each code fence (rendered as markdown
 * outside fences) gets the visual pill for review.
 */
function applyRefPlaceholderPill(source: string): string {
  const segments = source.split(/(```[\s\S]*?```)/g);
  return segments
    .map((seg, i) => {
      if (i % 2 === 1) return seg; // odd index = fenced code block, skip
      return seg.replace(REF_PLACEHOLDER_RE, (_, name) => {
        return `<span class="ref-placeholder" title="reference placeholder — replace with actual reference path when pasting to model">{ref_${name}}</span>`;
      });
    })
    .join("");
}

interface CopyableCodeProps {
  children: ReactNode;
}

/** Field labels in prompt body that get highlighted as markdown-style key headers.
 * Per rule #12.4 v4 / follow-up 013 visual contract.
 */
const FIELD_LABEL_RE = /^(角色|场景|镜头|动作|台词 ?\/ ?字幕|节奏|光线 ?\/ ?色调|渲染样式|比例|时长|负向|主体定义|姿态(（[^）]*）)?|参考|画幅)([:：])(\s*)/;

/** Walk a React node tree to extract its plain text content (used to render highlighted spans
 * while preserving the original text shape for `innerText` clipboard reads).
 */
function extractText(node: ReactNode): string {
  if (node === null || node === undefined || typeof node === "boolean") return "";
  if (typeof node === "string" || typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(extractText).join("");
  if (typeof node === "object" && "props" in node) {
    return extractText((node as { props: { children?: ReactNode } }).props.children);
  }
  return "";
}

/** Render plain code-block text with per-line field-label highlighting.
 * The output is a sequence of React nodes whose innerText equals the original plain text,
 * so the copy button still reads cleanly via `preRef.current.innerText`.
 */
function renderHighlightedLines(text: string): ReactNode {
  const lines = text.split("\n");
  return lines.map((line, idx) => {
    const m = line.match(FIELD_LABEL_RE);
    let content: ReactNode;
    if (m) {
      const label = m[1];
      const colon = m[m.length - 2];
      const spaces = m[m.length - 1] ?? "";
      const rest = line.slice(m[0].length);
      content = (
        <>
          <span className="field-label">{label}</span>
          {colon}
          {spaces}
          {rest}
        </>
      );
    } else {
      content = line;
    }
    return (
      <span key={idx}>
        {content}
        {idx < lines.length - 1 ? "\n" : null}
      </span>
    );
  });
}

function CopyableCode({ children }: CopyableCodeProps): JSX.Element {
  const [copied, setCopied] = useState(false);
  const preRef = useRef<HTMLPreElement>(null);

  const handleCopy = useCallback(async () => {
    const text = preRef.current?.innerText ?? "";
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      // clipboard API unavailable — graceful fallback: nothing to do
    }
  }, []);

  // Extract the plain text of children, then re-render with field-label highlighting
  // (per rule #12.4 v4 / follow-up 013). innerText still reads clean for copy.
  const plain = useMemo(() => extractText(children), [children]);
  const highlighted = useMemo(() => renderHighlightedLines(plain), [plain]);

  return (
    <div className="code-block-wrapper">
      <button
        type="button"
        className={`copy-btn${copied ? " copied" : ""}`}
        onClick={handleCopy}
        aria-label={copied ? "已复制" : "复制 prompt"}
      >
        {copied ? "已复制 ✓" : "复制 Copy"}
      </button>
      <pre ref={preRef}><code>{highlighted}</code></pre>
    </div>
  );
}

export function Renderer({ content, currentPath, knownPaths }: RendererProps): JSX.Element {
  const navigate = useNavigate();
  const known = useMemo(() => new Set(knownPaths), [knownPaths]);
  const isKnown = (p: string): boolean => known.has(p);
  const processed = useMemo(() => applyRefPlaceholderPill(applyLockedBlockPill(content)), [content]);

  return (
    <div className="markdown-view" lang="zh-Hans">
      <span id="locked-block-desc" className="visually-hidden">
        锁定描述符块 — byte-equality contract; do not edit
      </span>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeSanitize, rehypeHighlight]}
        components={{
          a: ({ href, children, ...rest }) => {
            if (typeof href !== "string") return <span>{children}</span>;
            const resolved = resolveLink({ currentFile: currentPath, href, isKnown });
            if (resolved.kind === "external") return <a href={resolved.href} target="_blank" rel="noopener noreferrer" {...rest}>{children}</a>;
            if (resolved.kind === "anchor") return <a href={resolved.hash} {...rest}>{children}</a>;
            if (resolved.kind === "internal") {
              const target = `/file/${encodeURIComponent(resolved.path)}${resolved.hash ?? ""}`;
              return <a href={target} onClick={(e) => { e.preventDefault(); navigate(target); }}>{children}</a>;
            }
            return <BrokenLink href={resolved.href} title={resolved.title}>{children}</BrokenLink>;
          },
          pre: ({ children }) => <CopyableCode>{children}</CopyableCode>,
        }}
      >
        {processed}
      </ReactMarkdown>
    </div>
  );
}
