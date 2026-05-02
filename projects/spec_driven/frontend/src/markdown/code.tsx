import { useEffect, useState } from "react";
import { codeToHtml } from "shiki";

const EXT_LANG: Record<string, string> = {
  ".yaml": "yaml",
  ".yml": "yaml",
  ".json": "json",
};

export function CodeView({ source, extension }: { source: string; extension: string }): JSX.Element {
  const [html, setHtml] = useState<string>("");
  const lang = EXT_LANG[extension] ?? "text";
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const out = await codeToHtml(source, { lang, theme: "github-light" });
        if (!cancelled) setHtml(out.replace("<pre", '<pre tabindex="0"'));
      } catch {
        if (!cancelled) setHtml(`<pre tabindex="0"><code>${escape(source)}</code></pre>`);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [source, lang]);
  return <div className="code-body" dangerouslySetInnerHTML={{ __html: html }} />;
}

function escape(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
