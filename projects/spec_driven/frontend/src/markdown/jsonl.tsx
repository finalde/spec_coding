import { useEffect, useState } from "react";
import { codeToHtml } from "shiki";

interface JsonlBlock {
  raw: string;
  isJson: boolean;
}

function parseLines(text: string): JsonlBlock[] {
  const blocks: JsonlBlock[] = [];
  for (const line of text.split(/\r?\n/)) {
    if (line.trim() === "") continue;
    let isJson = false;
    try {
      JSON.parse(line);
      isJson = true;
    } catch {
      isJson = false;
    }
    blocks.push({ raw: line, isJson });
  }
  return blocks;
}

export function JsonlView({ source }: { source: string }): JSX.Element {
  const [rendered, setRendered] = useState<string[]>([]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const blocks = parseLines(source);
      const out: string[] = [];
      for (const block of blocks) {
        if (block.isJson) {
          try {
            const formatted = JSON.stringify(JSON.parse(block.raw), null, 2);
            const html = await codeToHtml(formatted, { lang: "json", theme: "github-dark" });
            out.push(html.replace("<pre", '<pre tabindex="0"'));
            continue;
          } catch {
            // fall through
          }
        }
        out.push(`<pre tabindex="0" class="jsonl-malformed"><code>${escapeHtml(block.raw)}</code></pre>`);
      }
      if (!cancelled) setRendered(out);
    })();
    return () => {
      cancelled = true;
    };
  }, [source]);

  return (
    <div className="jsonl-body">
      {rendered.map((html, i) => (
        <div key={i} className="jsonl-line" dangerouslySetInnerHTML={{ __html: html }} />
      ))}
    </div>
  );
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
