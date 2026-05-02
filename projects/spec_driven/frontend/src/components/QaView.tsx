import { useEffect, useMemo, useState } from "react";
import { saveFile } from "../api";

export interface QaViewProps {
  source: string;
  filePath: string;
}

interface QaBlock {
  questionLineStart: number;
  questionLineEnd: number;
  answerLineStart: number;
  answerLineEnd: number;
  questionText: string;
  answerText: string;
}

interface QaCategory {
  name: string;
  lineStart: number;
  blocks: QaBlock[];
}

interface QaRound {
  number: string;
  lineStart: number;
  categories: QaCategory[];
}

interface ParsedQa {
  preamble: string[];
  rounds: QaRound[];
  raw: string[];
}

export function QaView({ source, filePath }: QaViewProps): JSX.Element {
  const [text, setText] = useState<string>(source);
  useEffect(() => setText(source), [source, filePath]);

  const parsed = useMemo<ParsedQa | null>(() => parseQa(text), [text]);

  if (!parsed || parsed.rounds.length === 0) {
    return (
      <div className="qa-fallback">
        <p className="qa-fallback-note">
          This file does not match the structured Q/A pattern (Round / category / Q / A).
          Falling back to raw view.
        </p>
        <pre className="qa-fallback-pre">{text}</pre>
      </div>
    );
  }

  const onBlockSaved = async (
    block: QaBlock,
    role: "question" | "answer",
    newBody: string,
  ): Promise<{ ok: true } | { ok: false; message: string }> => {
    const lines = text.split("\n");
    const range =
      role === "question"
        ? { start: block.questionLineStart, end: block.questionLineEnd }
        : { start: block.answerLineStart, end: block.answerLineEnd };
    const replacement = role === "question"
      ? renderQuestionLines(newBody)
      : renderAnswerLines(newBody);
    const next = [
      ...lines.slice(0, range.start),
      ...replacement,
      ...lines.slice(range.end + 1),
    ].join("\n");
    const result = await saveFile(filePath, next);
    if (result.ok) {
      setText(next);
      return { ok: true };
    }
    return { ok: false, message: `${result.error.error}${result.error.kind ? ` (${result.error.kind})` : ""}` };
  };

  return (
    <div className="qa-view">
      {parsed.preamble.length > 0 && (
        <pre className="qa-preamble">{parsed.preamble.join("\n").trim()}</pre>
      )}
      {parsed.rounds.map((round) => (
        <section key={round.number} className="qa-round">
          <h2 className="qa-round-title">Round {round.number}</h2>
          {round.categories.map((cat) => (
            <div key={`${round.number}-${cat.name}`} className="qa-category">
              <span className="qa-category-badge">{cat.name}</span>
              <ol className="qa-block-list">
                {cat.blocks.map((blk, idx) => (
                  <li key={`${round.number}-${cat.name}-${idx}`} className="qa-block">
                    <QaPair block={blk} onSave={onBlockSaved} />
                  </li>
                ))}
              </ol>
            </div>
          ))}
        </section>
      ))}
    </div>
  );
}

function QaPair({
  block,
  onSave,
}: {
  block: QaBlock;
  onSave: (
    blk: QaBlock,
    role: "question" | "answer",
    newBody: string,
  ) => Promise<{ ok: true } | { ok: false; message: string }>;
}): JSX.Element {
  return (
    <>
      <EditableBlock
        role="question"
        body={block.questionText}
        onSave={(body) => onSave(block, "question", body)}
      />
      <EditableBlock
        role="answer"
        body={block.answerText}
        onSave={(body) => onSave(block, "answer", body)}
      />
    </>
  );
}

function EditableBlock({
  role,
  body,
  onSave,
}: {
  role: "question" | "answer";
  body: string;
  onSave: (body: string) => Promise<{ ok: true } | { ok: false; message: string }>;
}): JSX.Element {
  const [editing, setEditing] = useState<boolean>(false);
  const [draft, setDraft] = useState<string>(body);
  const [status, setStatus] = useState<{ kind: "idle" } | { kind: "saving" } | { kind: "error"; message: string }>({ kind: "idle" });

  useEffect(() => setDraft(body), [body]);

  const onClickSave = async (): Promise<void> => {
    setStatus({ kind: "saving" });
    const r = await onSave(draft);
    if (r.ok) {
      setStatus({ kind: "idle" });
      setEditing(false);
    } else {
      setStatus({ kind: "error", message: r.message });
    }
  };

  return (
    <div className={`qa-block-${role}`}>
      <div className="qa-block-header">
        <span className="qa-block-role">{role === "question" ? "Q" : "A"}</span>
        {!editing && (
          <button
            type="button"
            className="qa-block-edit"
            onClick={() => {
              setDraft(body);
              setEditing(true);
              setStatus({ kind: "idle" });
            }}
            aria-label={`Edit ${role}`}
          >
            ✎
          </button>
        )}
      </div>
      {!editing && <div className="qa-block-body">{body}</div>}
      {editing && (
        <div className="qa-block-edit-area">
          <textarea
            className="qa-block-textarea"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            spellCheck={false}
          />
          <div className="qa-block-edit-actions">
            <button
              type="button"
              className="editor-button editor-save"
              onClick={() => void onClickSave()}
              disabled={status.kind === "saving" || draft === body}
            >
              {status.kind === "saving" ? "Saving…" : "Save"}
            </button>
            <button
              type="button"
              className="editor-button"
              onClick={() => {
                setDraft(body);
                setEditing(false);
                setStatus({ kind: "idle" });
              }}
              disabled={status.kind === "saving"}
            >
              Cancel
            </button>
            {status.kind === "error" && (
              <span className="editor-status-error">Error: {status.message}</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function renderQuestionLines(body: string): string[] {
  const trimmed = body.trim();
  return [`**Q:** ${trimmed}`];
}

function renderAnswerLines(body: string): string[] {
  const trimmed = body.trim();
  if (!trimmed) return ["- A:"];
  const [first, ...rest] = trimmed.split("\n");
  return [`- A: ${first}`, ...rest.map((l) => `  ${l}`)];
}

function parseQa(source: string): ParsedQa | null {
  const lines = source.split("\n");
  const preamble: string[] = [];
  const rounds: QaRound[] = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (line.startsWith("## Round ")) break;
    preamble.push(line);
    i++;
  }
  let currentRound: QaRound | null = null;
  let currentCategory: QaCategory | null = null;
  while (i < lines.length) {
    const line = lines[i];
    if (line.startsWith("## Round ")) {
      const number = line.replace(/^## Round\s+/, "").trim();
      currentRound = { number, lineStart: i, categories: [] };
      currentCategory = null;
      rounds.push(currentRound);
      i++;
      continue;
    }
    if (line.startsWith("### ") && currentRound) {
      const name = line.slice(4).trim();
      currentCategory = { name, lineStart: i, blocks: [] };
      currentRound.categories.push(currentCategory);
      i++;
      continue;
    }
    if (line.startsWith("**Q:**") && currentRound && currentCategory) {
      const qStart = i;
      const qBody: string[] = [line.replace(/^\*\*Q:\*\*\s?/, "")];
      i++;
      while (i < lines.length && !isBoundary(lines[i]) && !lines[i].startsWith("- A:")) {
        qBody.push(lines[i]);
        i++;
      }
      const qEnd = i - 1;
      let aStart = -1;
      let aEnd = -1;
      const aBody: string[] = [];
      if (i < lines.length && lines[i].startsWith("- A:")) {
        aStart = i;
        aBody.push(lines[i].replace(/^- A:\s?/, ""));
        i++;
        while (i < lines.length && lines[i].startsWith("  ") && !isBoundary(lines[i].trim())) {
          aBody.push(lines[i].slice(2));
          i++;
        }
        aEnd = i - 1;
      }
      currentCategory.blocks.push({
        questionLineStart: qStart,
        questionLineEnd: qEnd,
        answerLineStart: aStart === -1 ? qEnd : aStart,
        answerLineEnd: aEnd === -1 ? qEnd : aEnd,
        questionText: qBody.join("\n").trim(),
        answerText: aBody.join("\n").trim(),
      });
      continue;
    }
    i++;
  }
  return { preamble, rounds, raw: lines };
}

function isBoundary(line: string): boolean {
  return (
    line.startsWith("## ") ||
    line.startsWith("### ") ||
    line.startsWith("**Q:**")
  );
}
