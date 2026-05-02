import { useEffect, useState } from "react";

interface JsonlViewProps {
  source: string;
}

interface RenderedLine {
  index: number;
  raw: string;
  ok: boolean;
  html: string | null;
}

export function JsonlView({ source }: JsonlViewProps): JSX.Element {
  const [lines, setLines] = useState<RenderedLine[]>([]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const raw = source.split(/\r?\n/);
      const filtered: { idx: number; text: string }[] = [];
      raw.forEach((l, i) => {
        if (l.trim() !== "") filtered.push({ idx: i, text: l });
      });
      let highlighter: import("shiki").Highlighter | null = null;
      try {
        const shiki = await import("shiki");
        highlighter = await shiki.createHighlighter({
          themes: ["github-light"],
          langs: ["json"],
        });
      } catch {
        highlighter = null;
      }
      const rendered: RenderedLine[] = filtered.map(({ idx, text }) => {
        let parsed: unknown;
        try {
          parsed = JSON.parse(text);
        } catch {
          return { index: idx, raw: text, ok: false, html: null };
        }
        if (!highlighter) {
          return {
            index: idx,
            raw: JSON.stringify(parsed),
            ok: true,
            html: null,
          };
        }
        try {
          const pretty = JSON.stringify(parsed, null, 2);
          const html = highlighter.codeToHtml(pretty, {
            lang: "json",
            theme: "github-light",
          });
          return { index: idx, raw: text, ok: true, html };
        } catch {
          return { index: idx, raw: text, ok: true, html: null };
        }
      });
      if (!cancelled) setLines(rendered);
    })();
    return () => {
      cancelled = true;
    };
  }, [source]);

  return (
    <div className="jsonl-body">
      {lines.map((l) => (
        <div className="jsonl-line" key={l.index}>
          <span className="jsonl-gutter" aria-hidden="true">
            {l.index + 1}
          </span>
          {l.ok && l.html ? (
            <div
              className="shiki-block jsonl-content"
              tabIndex={0}
              dangerouslySetInnerHTML={{ __html: l.html }}
            />
          ) : (
            <pre tabIndex={0} className="jsonl-content jsonl-malformed">
              {l.raw}
            </pre>
          )}
        </div>
      ))}
    </div>
  );
}
