import { useState } from "react";
import { saveFile } from "../api";
import { stagePathFor, usePromotions } from "../promotions";
import { PinToggle } from "./PinToggle";

interface QaViewProps {
  parsed: ParseResult;
  filePath: string;
  onSaved: (text: string) => void;
}

interface QaPair {
  // The text inside Q/A blocks (without the marker prefix).
  question: string;
  answer: string;
  // Source line indices for splice-back.
  qStart: number;
  qEnd: number; // exclusive
  aStart: number;
  aEnd: number;
}

interface CategoryGroup {
  category: string;
  pairs: QaPair[];
}

interface RoundGroup {
  roundLabel: string; // e.g., "Round 1"
  categories: CategoryGroup[];
}

class ParseError extends Error {}

interface ParseResult {
  rounds: RoundGroup[];
  lines: string[]; // for splice-back
}

function parseQa(source: string): ParseResult {
  const lines = source.split(/\r?\n/);
  const rounds: RoundGroup[] = [];
  let curRound: RoundGroup | null = null;
  let curCat: CategoryGroup | null = null;
  let curQStart = -1;
  let curQEnd = -1;
  let inQ = false;
  let questionText = "";

  const flushQuestion = (): void => {
    inQ = false;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i] ?? "";
    if (/^##\s+Round\s+/i.test(line)) {
      if (inQ) flushQuestion();
      const label = line.replace(/^##\s+/, "").trim();
      curRound = { roundLabel: label, categories: [] };
      rounds.push(curRound);
      curCat = null;
      continue;
    }
    if (/^###\s+/.test(line)) {
      if (!curRound) continue;
      const cat = line.replace(/^###\s+/, "").trim();
      curCat = { category: cat, pairs: [] };
      curRound.categories.push(curCat);
      continue;
    }
    // Question marker: paragraph that begins with "**Q:**"
    const qMatch = /^\*\*Q:\*\*\s*(.*)$/.exec(line);
    if (qMatch) {
      if (!curCat) continue;
      questionText = qMatch[1] ?? "";
      curQStart = i;
      curQEnd = i + 1;
      inQ = true;
      continue;
    }
    // Answer bullet: "- A:" or "- A *(judgment call ...)*:" (autonomous mode form)
    const aMatch = /^-\s*A\s*(?:\*[^*\n]*\*\s*)?:\s*(.*)$/.exec(line);
    if (aMatch) {
      if (!curCat) continue;
      const answerText = aMatch[1] ?? "";
      const aStart = i;
      const aEnd = i + 1;
      curCat.pairs.push({
        question: questionText,
        answer: answerText,
        qStart: curQStart,
        qEnd: curQEnd,
        aStart,
        aEnd,
      });
      inQ = false;
      questionText = "";
      curQStart = -1;
      curQEnd = -1;
      continue;
    }
  }

  if (rounds.length === 0) {
    throw new ParseError("no rounds parsed");
  }
  let totalPairs = 0;
  for (const r of rounds) {
    for (const c of r.categories) totalPairs += c.pairs.length;
  }
  if (totalPairs === 0) {
    throw new ParseError("no Q/A pairs parsed");
  }

  return { rounds, lines };
}

interface InlineEditState {
  // composite key: roundIdx + catIdx + pairIdx + which ("q" | "a")
  key: string;
  text: string;
}

interface BlockProps {
  text: string;
  className: string;
  pencilLabel: string;
  editing: boolean;
  draft: string;
  onStartEdit: () => void;
  onChangeDraft: (v: string) => void;
  onSaveEdit: () => void;
  onCancelEdit: () => void;
  prefix: string;
}

function QaBlock(props: BlockProps): JSX.Element {
  return (
    <div className={props.className}>
      <span className="qa-prefix" aria-hidden="true">
        {props.prefix}
      </span>
      {props.editing ? (
        <div className="qa-inline-editor">
          <textarea
            className="qa-inline-textarea"
            value={props.draft}
            onChange={(e) => props.onChangeDraft(e.target.value)}
            spellCheck={false}
            aria-label={props.pencilLabel}
          />
          <div className="qa-inline-actions">
            <button
              type="button"
              className="editor-btn"
              onClick={props.onSaveEdit}
            >
              Save
            </button>
            <button
              type="button"
              className="editor-btn"
              onClick={props.onCancelEdit}
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <>
          <span className="qa-text">{props.text}</span>
          <button
            type="button"
            className="qa-pencil"
            aria-label={props.pencilLabel}
            onClick={props.onStartEdit}
          >
            &#x270E;
          </button>
        </>
      )}
    </div>
  );
}

export function QaView({
  parsed,
  filePath,
  onSaved,
}: QaViewProps): JSX.Element {
  const [editing, setEditing] = useState<InlineEditState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const stagePath = stagePathFor(filePath);
  const { isPinned, pin, unpin, error: pinError } = usePromotions(stagePath);

  const splice = async (
    start: number,
    end: number,
    prefix: string,
    text: string,
  ): Promise<void> => {
    const newLines = parsed.lines.slice();
    const replacement = `${prefix}${text}`;
    newLines.splice(start, end - start, replacement);
    const newText = newLines.join("\n");
    const result = await saveFile(filePath, newText);
    if (!result.ok) {
      setError(
        result.error.kind ?? result.error.error ?? `save_failed_${result.status}`,
      );
      return;
    }
    setError(null);
    setEditing(null);
    onSaved(newText);
  };

  const composePinBody = (q: string, a: string): string =>
    `**Q:** ${q}\n- A: ${a}`;

  return (
    <div className="qa-view">
      {(error || pinError) && (
        <div className="editor-error-banner" role="alert">
          {error ?? pinError}
        </div>
      )}
      {parsed.rounds.map((round, rIdx) => (
        <section key={rIdx} className="qa-round">
          <h2 className="qa-round-header">{round.roundLabel}</h2>
          {round.categories.map((cat, cIdx) => (
            <div key={cIdx} className="qa-category">
              <span className="qa-category-badge">{cat.category}</span>
              {cat.pairs.map((p, pIdx) => {
                const qKey = `${rIdx}-${cIdx}-${pIdx}-q`;
                const aKey = `${rIdx}-${cIdx}-${pIdx}-a`;
                const qEditing = editing?.key === qKey;
                const aEditing = editing?.key === aKey;
                const body = composePinBody(p.question, p.answer);
                const matchedPin = stagePath ? isPinned(body) : null;
                const location = `interview/qa.md / ${round.roundLabel} / ${cat.category}`;
                return (
                  <div key={pIdx} className={`qa-pair${matchedPin ? " qa-pair-pinned" : ""}`}>
                    {stagePath && (
                      <div className="qa-pair-toolbar">
                        <PinToggle
                          pin={matchedPin}
                          onPin={() => pin(location, body)}
                          onUnpin={(id) => unpin(id)}
                          ariaLabel={
                            matchedPin
                              ? `Unpin Q/A ${rIdx + 1}.${cIdx + 1}.${pIdx + 1}`
                              : `Pin Q/A ${rIdx + 1}.${cIdx + 1}.${pIdx + 1}`
                          }
                        />
                        {matchedPin && (
                          <span className="qa-pair-pinned-label" title={matchedPin.location}>
                            📌 pinned ({matchedPin.pin_id}) — edits to fields
                            below modify the GENERATED file only; edit the
                            pinned version on the promoted.md page.
                          </span>
                        )}
                      </div>
                    )}
                    <QaBlock
                      text={p.question}
                      className="qa-question"
                      pencilLabel={`Edit question ${rIdx + 1}.${cIdx + 1}.${pIdx + 1}`}
                      prefix="**Q:** "
                      editing={qEditing}
                      draft={qEditing ? editing!.text : p.question}
                      onStartEdit={() =>
                        setEditing({ key: qKey, text: p.question })
                      }
                      onChangeDraft={(v) =>
                        setEditing({ key: qKey, text: v })
                      }
                      onSaveEdit={() =>
                        void splice(p.qStart, p.qEnd, "**Q:** ", editing!.text)
                      }
                      onCancelEdit={() => setEditing(null)}
                    />
                    <QaBlock
                      text={p.answer}
                      className="qa-answer"
                      pencilLabel={`Edit answer ${rIdx + 1}.${cIdx + 1}.${pIdx + 1}`}
                      prefix="- A: "
                      editing={aEditing}
                      draft={aEditing ? editing!.text : p.answer}
                      onStartEdit={() =>
                        setEditing({ key: aKey, text: p.answer })
                      }
                      onChangeDraft={(v) =>
                        setEditing({ key: aKey, text: v })
                      }
                      onSaveEdit={() =>
                        void splice(p.aStart, p.aEnd, "- A: ", editing!.text)
                      }
                      onCancelEdit={() => setEditing(null)}
                    />
                  </div>
                );
              })}
            </div>
          ))}
        </section>
      ))}
    </div>
  );
}

export { ParseError, parseQa };
export type { ParseResult };
