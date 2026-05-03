import { useMemo } from "react";
import hljs from "highlight.js";
import "highlight.js/styles/github-dark.css";

interface Props {
  source: string;
  language: string;
}

export function CodeView({ source, language }: Props) {
  const html = useMemo(() => {
    try {
      const lang = hljs.getLanguage(language) ? language : "plaintext";
      return hljs.highlight(source, { language: lang }).value;
    } catch {
      return source.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]!));
    }
  }, [source, language]);

  return (
    <div className="code-view" data-testid="code-view">
      <pre>
        <code className={`hljs language-${language}`} dangerouslySetInnerHTML={{ __html: html }} />
      </pre>
    </div>
  );
}
