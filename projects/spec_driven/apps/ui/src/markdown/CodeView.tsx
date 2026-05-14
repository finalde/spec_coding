import { useMemo } from "react";

export interface CodeViewProps {
  content: string;
  filename: string;
}

export function CodeView({ content, filename }: CodeViewProps): JSX.Element {
  const ext = useMemo(() => {
    const dot = filename.lastIndexOf(".");
    return dot >= 0 ? filename.slice(dot + 1).toLowerCase() : "";
  }, [filename]);

  const formatted = useMemo(() => {
    if (ext === "json") {
      try {
        return JSON.stringify(JSON.parse(content), null, 2);
      } catch {
        return content;
      }
    }
    return content;
  }, [ext, content]);

  return (
    <div className="code-view">
      <pre>
        <code className={`language-${ext}`}>{formatted}</code>
      </pre>
    </div>
  );
}
