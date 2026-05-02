import { useLayoutEffect, useMemo, useRef } from "react";
import { useNavigate } from "react-router-dom";
import MarkdownIt from "markdown-it";

interface MarkdownViewProps {
  source: string;
  sourcePath: string;
  exposedPaths: ReadonlySet<string>;
}

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: false,
  typographer: false,
});

function gfmSlug(text: string): string {
  // lowercase ASCII, drop non-ASCII and punctuation except hyphens, replace whitespace with hyphens
  let s = text.toLowerCase();
  s = s.replace(/[^\x00-\x7f]/g, ""); // drop non-ASCII
  s = s.replace(/[^a-z0-9\s-]/g, ""); // drop punctuation
  s = s.replace(/\s+/g, "-");
  s = s.replace(/-+/g, "-");
  s = s.replace(/^-+|-+$/g, "");
  if (s === "") s = "section";
  return s;
}

function isExternalHref(href: string): boolean {
  if (!href) return false;
  if (href.startsWith("//")) return true;
  return /^[a-z][a-z0-9+.\-]*:/i.test(href);
}

function resolveRelative(sourcePath: string, href: string): string {
  // sourcePath is a posix-like path with forward slashes
  // href may contain url-encoded segments; decode once
  let target = href;
  try {
    target = decodeURI(href);
  } catch {
    // pass through
  }
  // strip query / fragment
  const hashIdx = target.indexOf("#");
  const queryIdx = target.indexOf("?");
  let cut = -1;
  if (hashIdx >= 0) cut = hashIdx;
  if (queryIdx >= 0 && (cut < 0 || queryIdx < cut)) cut = queryIdx;
  const pathPart = cut >= 0 ? target.slice(0, cut) : target;
  if (pathPart === "") return "";
  const sourceParent = sourcePath.includes("/")
    ? sourcePath.slice(0, sourcePath.lastIndexOf("/"))
    : "";
  const joined = pathPart.startsWith("/")
    ? pathPart.slice(1)
    : sourceParent
      ? `${sourceParent}/${pathPart}`
      : pathPart;
  // normalize . and ..
  const out: string[] = [];
  for (const seg of joined.split("/")) {
    if (seg === "" || seg === ".") continue;
    if (seg === "..") {
      if (out.length === 0) continue;
      out.pop();
      continue;
    }
    out.push(seg);
  }
  return out.join("/");
}

function isImageExtension(path: string): boolean {
  const dot = path.lastIndexOf(".");
  if (dot < 0) return false;
  const ext = path.slice(dot).toLowerCase();
  return [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".ico"].includes(
    ext,
  );
}

export function MarkdownView({
  source,
  sourcePath,
  exposedPaths,
}: MarkdownViewProps): JSX.Element {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const navigate = useNavigate();

  const renderedHtml = useMemo(() => {
    // Pre-pass: collect heading ids with collision tracking.
    const slugCounts = new Map<string, number>();
    const tokens = md.parse(source, {});
    for (let i = 0; i < tokens.length; i++) {
      const t = tokens[i]!;
      if (t.type === "heading_open") {
        const inline = tokens[i + 1];
        const text = inline?.content ?? "";
        const base = gfmSlug(text);
        const seen = slugCounts.get(base) ?? 0;
        const id = seen === 0 ? base : `${base}-${seen}`;
        slugCounts.set(base, seen + 1);
        const existingAttrs = t.attrs ?? [];
        existingAttrs.push(["id", id]);
        t.attrs = existingAttrs;
      }
    }
    // Override link_open to add a sentinel data-rewriteme so we can post-process.
    const html = md.renderer.render(tokens, md.options, {});
    return html;
  }, [source]);

  useLayoutEffect(() => {
    const root = containerRef.current;
    if (!root) return;
    // Walk all <a> and <img>
    const anchors = Array.from(root.querySelectorAll("a"));
    for (const a of anchors) {
      const href = a.getAttribute("href") ?? "";
      if (!href) continue;
      if (isExternalHref(href)) {
        a.setAttribute("target", "_blank");
        a.setAttribute("rel", "noopener noreferrer");
        // Append sr-only sibling if not already present.
        const next = a.nextSibling;
        if (
          !(next instanceof HTMLElement) ||
          !next.classList.contains("sr-only-newtab")
        ) {
          const span = document.createElement("span");
          span.className = "sr-only sr-only-newtab";
          span.textContent = "(opens in new tab)";
          a.parentNode?.insertBefore(span, a.nextSibling);
        }
        continue;
      }
      if (href.startsWith("#")) {
        a.addEventListener("click", (e) => {
          e.preventDefault();
          const id = href.slice(1);
          const target = root.querySelector(`#${CSS.escape(id)}`);
          if (target instanceof HTMLElement) {
            target.scrollIntoView({ behavior: "auto", block: "start" });
          }
        });
        continue;
      }
      // Internal link: resolve relative path
      const hashIdx = href.indexOf("#");
      const fragment = hashIdx >= 0 ? href.slice(hashIdx) : "";
      const resolved = resolveRelative(sourcePath, href);
      if (resolved === "") {
        // Empty / pure fragment edge case already handled.
        continue;
      }
      const isExposed = exposedPaths.has(resolved);
      if (!isExposed) {
        // Replace with a span.link-broken
        const span = document.createElement("span");
        span.className = "link-broken";
        span.setAttribute("aria-disabled", "true");
        span.title = "file not found";
        span.textContent = a.textContent ?? "";
        a.replaceWith(span);
        continue;
      }
      // Internal exposed link: rewrite to /file/<encoded path><fragment>
      const newHref = `/file/${encodeURI(resolved)}${fragment}`;
      a.setAttribute("href", newHref);
      a.addEventListener("click", (e) => {
        if (
          e.defaultPrevented ||
          (e as MouseEvent).button !== 0 ||
          (e as MouseEvent).metaKey ||
          (e as MouseEvent).ctrlKey ||
          (e as MouseEvent).shiftKey ||
          (e as MouseEvent).altKey
        ) {
          return;
        }
        e.preventDefault();
        navigate(newHref);
      });
    }

    // Images: replace internal image references with placeholder spans.
    const imgs = Array.from(root.querySelectorAll("img"));
    for (const img of imgs) {
      const src = img.getAttribute("src") ?? "";
      const alt = img.getAttribute("alt") ?? "";
      if (isExternalHref(src)) continue;
      // internal image
      const resolved = resolveRelative(sourcePath, src);
      if (resolved && (exposedPaths.has(resolved) || isImageExtension(resolved))) {
        const span = document.createElement("span");
        span.className = "image-placeholder";
        span.title = "v1: images not rendered";
        span.textContent = alt;
        img.replaceWith(span);
      } else {
        const span = document.createElement("span");
        span.className = "image-placeholder";
        span.title = "v1: images not rendered";
        span.textContent = alt;
        img.replaceWith(span);
      }
    }

    // Pre blocks: tabindex 0
    const pres = Array.from(root.querySelectorAll("pre"));
    for (const pre of pres) {
      pre.setAttribute("tabindex", "0");
    }
  }, [renderedHtml, sourcePath, exposedPaths, navigate]);

  return (
    <div
      ref={containerRef}
      className="markdown-body"
      dangerouslySetInnerHTML={{ __html: renderedHtml }}
    />
  );
}
