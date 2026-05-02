export type LinkClass =
  | { kind: "external"; href: string }
  | { kind: "anchor"; fragment: string }
  | { kind: "internal"; targetPath: string }
  | { kind: "broken"; cause: BrokenCause; original: string; targetPath?: string };

export type BrokenCause =
  | "outside exposed tree"
  | "file not found"
  | "anchor not found"
  | "case mismatch — fix the link"
  | "not yet generated";

const SCHEME_RE = /^[a-z][a-z0-9+.-]*:/i;

export interface ClassifierContext {
  sourcePath: string;
  exposedPaths: ReadonlySet<string>;
}

export function classifyLink(href: string, ctx: ClassifierContext): LinkClass {
  if (SCHEME_RE.test(href) || href.startsWith("//")) {
    return { kind: "external", href };
  }
  if (href.startsWith("#")) {
    return { kind: "anchor", fragment: href.slice(1) };
  }
  const decoded = safeDecode(href);
  const sourceDir = ctx.sourcePath.split("/").slice(0, -1);
  const targetParts = decoded.split(/[/\\]/);
  const stack: string[] = [...sourceDir];
  for (const part of targetParts) {
    if (part === "" || part === ".") continue;
    if (part === "..") {
      if (stack.length === 0) {
        return { kind: "broken", cause: "outside exposed tree", original: href };
      }
      stack.pop();
      continue;
    }
    stack.push(part);
  }
  const resolved = stack.join("/");
  if (!ctx.exposedPaths.has(resolved)) {
    return { kind: "broken", cause: "file not found", original: href, targetPath: resolved };
  }
  return { kind: "internal", targetPath: resolved };
}

function safeDecode(input: string): string {
  try {
    return decodeURIComponent(input);
  } catch {
    return input;
  }
}
