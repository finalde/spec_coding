export type LinkKind = "internal" | "external" | "broken" | "anchor";

export interface InternalLink {
  kind: "internal";
  path: string;
  hash: string | null;
}

export interface ExternalLink {
  kind: "external";
  href: string;
}

export interface BrokenLinkResult {
  kind: "broken";
  href: string;
  title: string;
}

export interface AnchorLink {
  kind: "anchor";
  hash: string;
}

export type ResolvedLink = InternalLink | ExternalLink | BrokenLinkResult | AnchorLink;

export interface ResolveLinkInput {
  currentFile: string;
  href: string;
  isKnown: (path: string) => boolean;
}

const MAX_SEGMENT_DEPTH = 1024;

export function resolveLink({ currentFile, href, isKnown }: ResolveLinkInput): ResolvedLink {
  if (typeof href !== "string" || href.length === 0) {
    return { kind: "broken", href: href ?? "", title: "Empty link" };
  }
  if (href.startsWith("#")) {
    return { kind: "anchor", hash: href };
  }
  if (/^https?:\/\//i.test(href)) {
    return { kind: "external", href };
  }
  if (/^(javascript|data|file|vbscript|mailto):/i.test(href)) {
    return { kind: "broken", href, title: `Unsupported scheme: ${href}` };
  }

  const normalized = href.replace(/\\/g, "/");
  const [pathPart, ...hashParts] = normalized.split("#");
  const hash = hashParts.length > 0 ? `#${hashParts.join("#")}` : null;
  const [target] = pathPart.split("?");

  let decoded: string;
  try {
    decoded = decodeURIComponent(target);
  } catch {
    decoded = target;
  }

  const baseDir = currentFile.includes("/")
    ? currentFile.substring(0, currentFile.lastIndexOf("/"))
    : "";

  const joined = joinSegments(baseDir, decoded);
  if (joined === null) {
    return {
      kind: "broken",
      href,
      title: `Link resolves outside the exposed tree: ${href}`,
    };
  }

  if (isKnown(joined)) {
    const result: InternalLink = { kind: "internal", path: joined, hash };
    return result;
  }

  return { kind: "broken", href, title: `Broken link: ${href} (target ${joined} not found)` };
}

function joinSegments(baseDir: string, rel: string): string | null {
  if (rel.startsWith("/")) {
    rel = rel.replace(/^\/+/, "");
  }
  const segments: string[] = baseDir ? baseDir.split("/").filter(Boolean) : [];
  const relSegments = rel.split("/");
  if (relSegments.length > MAX_SEGMENT_DEPTH) return null;
  let underflowed = false;
  for (const seg of relSegments) {
    if (seg === "" || seg === ".") continue;
    if (seg === "..") {
      if (segments.length === 0) return null;
      segments.pop();
      if (segments.length === 0) underflowed = true;
    } else {
      if (underflowed) return null;
      segments.push(seg);
    }
    if (segments.length > MAX_SEGMENT_DEPTH) return null;
  }
  return segments.join("/");
}

export function collectFilePaths(node: { path: string; type: string; children?: unknown[] }): string[] {
  const out: string[] = [];
  const walk = (n: { path: string; type: string; children?: unknown[] }): void => {
    if (n.type === "file") out.push(n.path);
    const kids = (n.children ?? []) as { path: string; type: string; children?: unknown[] }[];
    for (const k of kids) walk(k);
  };
  walk(node);
  return out;
}
