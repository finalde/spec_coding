import { useEffect, useState } from "react";

interface CodeViewProps {
  source: string;
  extension: string;
}

const EXT_TO_LANG: Record<string, string> = {
  ".json": "json",
  ".jsonl": "json",
  ".yaml": "yaml",
  ".yml": "yaml",
  ".md": "markdown",
  ".ts": "typescript",
  ".tsx": "tsx",
  ".js": "javascript",
  ".jsx": "jsx",
  ".py": "python",
};

export function CodeView({ source, extension }: CodeViewProps): JSX.Element {
  const [html, setHtml] = useState<string | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const shiki = await import("shiki");
        const lang = EXT_TO_LANG[extension] ?? "text";
        const highlighter = await shiki.createHighlighter({
          themes: ["github-light"],
          langs: [lang === "text" ? "markdown" : lang],
        });
        const out = highlighter.codeToHtml(source, {
          lang: lang === "text" ? "markdown" : lang,
          theme: "github-light",
        });
        if (!cancelled) setHtml(out);
      } catch {
        if (!cancelled) setError(true);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [source, extension]);

  if (error || html === null) {
    return (
      <pre tabIndex={0} className="code-fallback">
        {source}
      </pre>
    );
  }
  return (
    <div
      className="shiki-block"
      tabIndex={0}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
