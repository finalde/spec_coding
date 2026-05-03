import { useMemo, useState } from "react";
import { parseQa, type QaPair } from "../lib/qaParser";
import type { ApiError } from "../types";

export interface QaViewProps {
  content: string;
  filePath: string;
  onSave: (newContent: string) => Promise<void>;
  saveError: ApiError | Error | null;
  onActiveBlockChange: (blockOpen: boolean) => void;
  fileEditDisabled: boolean;
  projectType: string | null;
  projectName: string | null;
  onPin: (pair: QaPair) => Promise<void>;
  onUnpin: (pair: QaPair) => Promise<void>;
  pinnedIds: Set<string>;
}

interface ActiveEdit {
  itemId: string;
  field: "Q" | "A";
  buffer: string;
}

export function QaView(props: QaViewProps): JSX.Element {
  const document = useMemo(() => parseQa(props.content), [props.content]);
  const [active, setActive] = useState<ActiveEdit | null>(null);
  const [saving, setSaving] = useState<boolean>(false);
  const [staleConflict, setStaleConflict] = useState<string | null>(null);

  const open = (itemId: string, field: "Q" | "A", initial: string): void => {
    setActive({ itemId, field, buffer: initial });
    props.onActiveBlockChange(true);
  };

  const close = (): void => {
    setActive(null);
    props.onActiveBlockChange(false);
  };

  const saveActive = async (): Promise<void> => {
    if (!active) return;
    const lines = props.content.split(/\r?\n/);
    let pair: QaPair | undefined;
    for (const round of document.rounds) {
      for (const cat of round.categories) {
        const found = cat.pairs.find((p) => p.itemId === active.itemId);
        if (found) {
          pair = found;
          break;
        }
      }
      if (pair) break;
    }
    if (!pair) {
      close();
      return;
    }
    if (active.field === "Q") {
      lines[pair.qLine] = `**Q:** ${active.buffer}`;
    } else {
      const annotation = pair.judgmentCall ? ` *(${pair.judgmentCall})*` : "";
      lines[pair.aLine] = `- A${annotation}: ${active.buffer}`;
    }
    const newContent = lines.join("\n");
    setSaving(true);
    try {
      await props.onSave(newContent);
      setStaleConflict(null);
      close();
    } catch (err) {
      const apiError = err as { status?: number; detail?: { kind?: string } };
      if (apiError && apiError.status === 409) {
        setStaleConflict("Q changed externally — Reload?");
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="qa-view">
      {document.rounds.length === 0 ? (
        <p className="muted">No Q/A pairs detected.</p>
      ) : null}
      {document.rounds.map((round) => (
        <section key={round.index} className="qa-round">
          <h2 className="qa-round-heading">
            Round {round.index}
            {round.title ? ` — ${round.title}` : ""}
          </h2>
          {round.categories.map((cat) => (
            <div key={`${round.index}-${cat.name}`} className="qa-category">
              <h3 className="qa-category-heading">{cat.name}</h3>
              {cat.pairs.map((pair) => (
                <article key={pair.itemId} className="qa-pair" data-qid={pair.itemId}>
                  <header className="qa-pair-header">
                    <span className="qa-category-badge" aria-label={`Category ${cat.name}`}>
                      {cat.name}
                    </span>
                    {props.projectType && props.projectName ? (
                      <button
                        type="button"
                        role="switch"
                        aria-checked={props.pinnedIds.has(pair.itemId)}
                        aria-label={`Pin ${pair.itemId}`}
                        className="pin-toggle"
                        title={
                          props.pinnedIds.has(pair.itemId)
                            ? "Pinned (click to unpin)"
                            : "Pin to interview/promoted.md"
                        }
                        onClick={() => {
                          if (props.pinnedIds.has(pair.itemId)) {
                            void props.onUnpin(pair);
                          } else {
                            void props.onPin(pair);
                          }
                        }}
                      >
                        <span aria-hidden="true">📌</span>
                      </button>
                    ) : null}
                  </header>
                  <div className="qa-q" aria-label="Question">
                    <span className="qa-prefix" aria-hidden="true">
                      Q:
                    </span>{" "}
                    {active && active.itemId === pair.itemId && active.field === "Q" ? (
                      <InlineEditor
                        value={active.buffer}
                        onChange={(v) => setActive({ ...active, buffer: v })}
                        onSave={saveActive}
                        onCancel={close}
                        saving={saving}
                      />
                    ) : (
                      <>
                        <span className="qa-text">{pair.q}</span>
                        <button
                          type="button"
                          aria-label={`Edit question ${pair.itemId}`}
                          className="qa-edit-pencil"
                          disabled={props.fileEditDisabled}
                          onClick={() => open(pair.itemId, "Q", pair.q)}
                        >
                          ✎
                        </button>
                      </>
                    )}
                  </div>
                  <div className="qa-a" aria-label="Answer">
                    <span className="qa-prefix" aria-hidden="true">
                      A:
                    </span>
                    {pair.judgmentCall ? (
                      <span className="qa-annotation"> ({pair.judgmentCall})</span>
                    ) : null}{" "}
                    {active && active.itemId === pair.itemId && active.field === "A" ? (
                      <InlineEditor
                        value={active.buffer}
                        onChange={(v) => setActive({ ...active, buffer: v })}
                        onSave={saveActive}
                        onCancel={close}
                        saving={saving}
                      />
                    ) : (
                      <>
                        <span className="qa-text">{pair.a}</span>
                        <button
                          type="button"
                          aria-label={`Edit answer ${pair.itemId}`}
                          className="qa-edit-pencil"
                          disabled={props.fileEditDisabled}
                          onClick={() => open(pair.itemId, "A", pair.a)}
                        >
                          ✎
                        </button>
                      </>
                    )}
                  </div>
                  {staleConflict && active && active.itemId === pair.itemId ? (
                    <div className="save-error-banner" role="alert">
                      {staleConflict}
                    </div>
                  ) : null}
                </article>
              ))}
            </div>
          ))}
        </section>
      ))}
      {props.saveError ? (
        <div className="save-error-banner" role="alert">
          Save failed: {props.saveError.message}
        </div>
      ) : null}
    </div>
  );
}

interface InlineEditorProps {
  value: string;
  onChange: (v: string) => void;
  onSave: () => void;
  onCancel: () => void;
  saving: boolean;
}

function InlineEditor({ value, onChange, onSave, onCancel, saving }: InlineEditorProps): JSX.Element {
  return (
    <span className="qa-inline-editor">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={Math.max(2, Math.min(8, value.split("\n").length))}
        aria-label="Inline edit"
      />
      <button type="button" onClick={onSave} disabled={saving} className="qa-inline-save">
        {saving ? "Saving…" : "Save"}
      </button>
      <button type="button" onClick={onCancel} className="qa-inline-cancel">
        Cancel
      </button>
    </span>
  );
}
