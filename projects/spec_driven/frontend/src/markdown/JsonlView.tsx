import { useState } from "react";

export interface JsonlViewProps {
  content: string;
}

interface Line {
  raw: string;
  parsed: unknown | null;
  error: string | null;
}

function parseLines(content: string): Line[] {
  const lines = content.split(/\r?\n/);
  const result: Line[] = [];
  for (const raw of lines) {
    if (raw.trim() === "") continue;
    try {
      result.push({ raw, parsed: JSON.parse(raw), error: null });
    } catch (err) {
      result.push({ raw, parsed: null, error: err instanceof Error ? err.message : String(err) });
    }
  }
  return result;
}

export function JsonlView({ content }: JsonlViewProps): JSX.Element {
  const lines = parseLines(content);
  return (
    <div className="jsonl-view">
      {lines.map((line, idx) => (
        <JsonlLine key={idx} line={line} />
      ))}
    </div>
  );
}

interface JsonlLineProps {
  line: Line;
}

function JsonlLine({ line }: JsonlLineProps): JSX.Element {
  const [expanded, setExpanded] = useState<boolean>(false);
  if (line.error) {
    return (
      <div className="jsonl-line parse-error">
        <span className="jsonl-badge" role="img" aria-label="parse error">
          parse error
        </span>
        <pre>{line.raw}</pre>
      </div>
    );
  }
  return (
    <div className={`jsonl-line parsed ${expanded ? "expanded" : "collapsed"}`}>
      <button
        type="button"
        className="jsonl-toggle"
        aria-expanded={expanded}
        onClick={() => setExpanded((e) => !e)}
      >
        {expanded ? "▾" : "▸"} {summarize(line.parsed)}
      </button>
      {expanded ? <pre>{JSON.stringify(line.parsed, null, 2)}</pre> : null}
    </div>
  );
}

function summarize(value: unknown): string {
  if (value === null) return "null";
  if (typeof value !== "object") return String(value);
  if (Array.isArray(value)) return `[Array(${value.length})]`;
  const keys = Object.keys(value as Record<string, unknown>);
  if (keys.length === 0) return "{}";
  return `{${keys.slice(0, 3).join(", ")}${keys.length > 3 ? ", …" : ""}}`;
}
