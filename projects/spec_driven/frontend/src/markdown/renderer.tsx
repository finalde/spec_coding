import MarkdownIt from "markdown-it";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { codeToHtml } from "shiki";
import { classifyLink, type ClassifierContext } from "./classifier";
import { SlugRegistry } from "./slug";

const md = new MarkdownIt({ html: false, linkify: true, breaks: false });

const slugRegistry = new WeakMap<object, SlugRegistry>();

md.renderer.rules.heading_open = (tokens, idx, _options, env) => {
  const tag = tokens[idx].tag;
  let registry = slugRegistry.get(env);
  if (!registry) {
    registry = new SlugRegistry();
    slugRegistry.set(env, registry);
  }
  const inlineToken = tokens[idx + 1];
  const text = inlineToken && inlineToken.children
    ? inlineToken.children.filter((t) => t.type === "text" || t.type === "code_inline").map((t) => t.content).join("")
    : "";
  const slug = registry.generate(text);
  return `<${tag} id="${escapeAttr(slug)}">`;
};

function escapeAttr(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
}

export interface MarkdownViewProps {
  source: string;
  sourcePath: string;
  exposedPaths: ReadonlySet<string>;
}

export function MarkdownView({ source, sourcePath, exposedPaths }: MarkdownViewProps): JSX.Element {
  const html = md.render(source, {});
  const containerRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const [highlightedHtml, setHighlightedHtml] = useState<string>(html);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const transformed = await transformHtml(html, { sourcePath, exposedPaths });
      if (!cancelled) {
        setHighlightedHtml(transformed);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [html, sourcePath, exposedPaths]);

  useEffect(() => {
    const root = containerRef.current;
    if (!root) return;
    const handler = (event: Event): void => {
      const target = (event.target as HTMLElement).closest("a[data-internal-target]");
      if (!target) return;
      event.preventDefault();
      const path = target.getAttribute("data-internal-target");
      if (path) {
        navigate(`/file/${encodeURI(path)}`);
      }
    };
    root.addEventListener("click", handler);
    return () => root.removeEventListener("click", handler);
  }, [navigate, highlightedHtml]);

  return (
    <div
      ref={containerRef}
      className="markdown-body"
      dangerouslySetInnerHTML={{ __html: highlightedHtml }}
    />
  );
}

async function transformHtml(html: string, ctx: ClassifierContext): Promise<string> {
  const linksAndImages = html
    .replace(/<a\s+([^>]*?)href="([^"]*)"([^>]*)>(.*?)<\/a>/gi, (_m, before, href, after, body) => {
      const c = classifyLink(href, ctx);
      const inner = body;
      if (c.kind === "external") {
        return `<a ${before}href="${escapeAttr(c.href)}" target="_blank" rel="noopener noreferrer"${after}>${inner}<span class="sr-only"> (opens in new tab)</span></a>`;
      }
      if (c.kind === "anchor") {
        return `<a ${before}href="#${escapeAttr(c.fragment)}"${after}>${inner}</a>`;
      }
      if (c.kind === "internal") {
        return `<a ${before}href="#" data-internal-target="${escapeAttr(c.targetPath)}"${after}>${inner}</a>`;
      }
      return `<span class="link-broken" aria-disabled="true" title="${escapeAttr(c.cause)}">${inner}</span>`;
    })
    .replace(/<img\s+([^>]*?)src="([^"]*)"([^>]*)>/gi, (_m, before, src, after) => {
      const altMatch = /alt="([^"]*)"/i.exec(`${before} ${after}`);
      const alt = altMatch ? altMatch[1] : "";
      if (SCHEME_RE.test(src) || src.startsWith("//")) {
        return `<img ${before}src="${escapeAttr(src)}"${after}>`;
      }
      return `<span class="image-placeholder" title="v1: images not rendered">${escapeAttr(alt)}</span>`;
    });

  const codeBlockRe = /<pre><code(?:\s+class="language-(\w+)")?>([\s\S]*?)<\/code><\/pre>/g;
  const matches = Array.from(linksAndImages.matchAll(codeBlockRe));
  let result = linksAndImages;
  for (const match of matches) {
    const [whole, lang, code] = match;
    const decoded = decodeEntities(code);
    let highlighted: string;
    try {
      highlighted = await codeToHtml(decoded, {
        lang: lang || "text",
        theme: "github-light",
      });
      highlighted = highlighted.replace("<pre", '<pre tabindex="0"');
    } catch {
      highlighted = `<pre tabindex="0"><code>${escapeAttr(decoded)}</code></pre>`;
    }
    result = result.replace(whole, highlighted);
  }
  result = result.replace(/<pre(?![^>]*tabindex)/g, '<pre tabindex="0"');
  return result;
}

const SCHEME_RE = /^[a-z][a-z0-9+.-]*:/i;

function decodeEntities(input: string): string {
  return input
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}
