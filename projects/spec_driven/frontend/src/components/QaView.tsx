import { useState } from "react";
import { parseQa, type QaPair } from "../lib/qaParser";
import { putFile } from "../api";

interface Props {
  source: string;
  filePath: string;
  onWholeFileEdit: () => void;
  fileLevelDisabled?: boolean;
  onAnyBlockOpen?: (open: boolean) => void;
  onSaved?: (newSource: string) => void;
}

export function QaView({ source, filePath, onAnyBlockOpen, onSaved }: Props) {
  const doc = parseQa(source);
  const [editing, setEditing] = useState<{ id: string; field: "q" | "a" } | null>(null);
  const [draft, setDraft] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const startEdit = (pair: QaPair, field: "q" | "a") => {
    setEditing({ id: pair.id, field });
    setDraft(field === "q" ? pair.q : pair.a);
    setError(null);
    onAnyBlockOpen?.(true);
  };

  const cancel = () => {
    setEditing(null);
    onAnyBlockOpen?.(false);
  };

  const save = async (pair: QaPair, field: "q" | "a") => {
    const lineRe =
      field === "q"
        ? new RegExp(`(^[-*]\\s*\\*?\\*?Q\\*?\\*?:\\s*).+$`, "m")
        : pair.judgmentCall
          ? new RegExp(
              `(^[-*]\\s*\\*?\\*?A\\*?\\*?\\s*\\*\\(judgment call\\s*[—-]\\s*${escapeReg(pair.judgmentCall)}\\)\\*\\s*:\\s*).+$`,
              "m",
            )
          : new RegExp(`(^[-*]\\s*\\*?\\*?A\\*?\\*?:\\s*).+$`, "m");

    const oldText = field === "q" ? pair.q : pair.a;
    const lines = source.split(/\r?\n/);
    let replaced: string[] = [];
    let done = false;
    for (const line of lines) {
      if (!done && line.includes(oldText)) {
        replaced.push(line.replace(oldText, draft));
        done = true;
      } else {
        replaced.push(line);
      }
    }
    if (!done) {
      setError("could not locate the original text in the file");
      return;
    }
    const newSource = replaced.join("\n");
    try {
      await putFile(filePath, newSource);
      onSaved?.(newSource);
      cancel();
    } catch (e: any) {
      const detail = e?.detail?.detail?.kind || e?.detail?.detail || e?.detail || "save failed";
      setError(`Could not save: ${typeof detail === "string" ? detail : JSON.stringify(detail)}`);
    }
  };

  return (
    <div className="qa-view" data-testid="qa-view">
      {doc.rounds.map((round) => (
        <section key={round.number} className="qa-round">
          <h2>Round {round.number}</h2>
          {round.categories.map((category) => (
            <section key={category.name} className="qa-category" data-category-badge={category.name}>
              <h3>
                <span className="category-badge">{category.name}</span>
              </h3>
              {category.pairs.map((pair) => (
                <article key={pair.id} className="qa-pair" data-block-id={pair.id}>
                  <div
                    className="qa-block qa-tint-q"
                    data-block="q"
                    data-testid="qa-q-block"
                    aria-label="Question"
                  >
                    <strong>Q:</strong>{" "}
                    {editing?.id === pair.id && editing.field === "q" ? (
                      <BlockEditor
                        value={draft}
                        onChange={setDraft}
                        onSave={() => save(pair, "q")}
                        onCancel={cancel}
                        blockId={`qa-block-editor-${pair.id}-q`}
                      />
                    ) : (
                      <>
                        <span>{pair.q}</span>
                        <button
                          type="button"
                          className="pencil"
                          aria-label="Edit question"
                          data-testid={`qa-q-edit-${pair.id}`}
                          onClick={() => startEdit(pair, "q")}
                        >
                          ✎
                        </button>
                      </>
                    )}
                  </div>
                  <div
                    className="qa-block qa-tint-a"
                    data-block="a"
                    data-testid="qa-a-block"
                    aria-label="Answer"
                  >
                    <strong>A:</strong>{" "}
                    {editing?.id === pair.id && editing.field === "a" ? (
                      <BlockEditor
                        value={draft}
                        onChange={setDraft}
                        onSave={() => save(pair, "a")}
                        onCancel={cancel}
                        blockId={`qa-block-editor-${pair.id}-a`}
                      />
                    ) : (
                      <>
                        <span>{pair.a}</span>
                        {pair.judgmentCall && (
                          <em className="judgment-call" title="judgment call">
                            ({pair.judgmentCall})
                          </em>
                        )}
                        <button
                          type="button"
                          className="pencil"
                          aria-label="Edit answer"
                          data-testid={`qa-a-edit-${pair.id}`}
                          onClick={() => startEdit(pair, "a")}
                        >
                          ✎
                        </button>
                      </>
                    )}
                  </div>
                </article>
              ))}
            </section>
          ))}
        </section>
      ))}
      {error && (
        <div role="alert" className="qa-error">
          {error}
        </div>
      )}
    </div>
  );
}

interface BlockEditorProps {
  value: string;
  onChange: (v: string) => void;
  onSave: () => void;
  onCancel: () => void;
  blockId: string;
}

function BlockEditor({ value, onChange, onSave, onCancel, blockId }: BlockEditorProps) {
  return (
    <span className="block-editor">
      <textarea
        data-testid={blockId}
        aria-label="Edit Q/A block"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "s" && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            onSave();
          } else if (e.key === "Escape") {
            onCancel();
          }
        }}
      />
      <button type="button" onClick={onSave}>
        Save
      </button>
      <button type="button" onClick={onCancel}>
        Cancel
      </button>
    </span>
  );
}

function escapeReg(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
