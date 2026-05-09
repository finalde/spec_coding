import { useMemo } from "react";
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

function applyLockedBlockPill(source: string): string {
  return source.replace(LOCKED_BLOCK_RE, (m) => {
    return `<span class="locked-block" title="byte-equality contract — see characters/main.md" aria-describedby="locked-block-desc">${m}</span>`;
  });
}

export function Renderer({ content, currentPath, knownPaths }: RendererProps): JSX.Element {
  const navigate = useNavigate();
  const known = useMemo(() => new Set(knownPaths), [knownPaths]);
  const isKnown = (p: string): boolean => known.has(p);
  const processed = useMemo(() => applyLockedBlockPill(content), [content]);

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
        }}
      >
        {processed}
      </ReactMarkdown>
    </div>
  );
}
