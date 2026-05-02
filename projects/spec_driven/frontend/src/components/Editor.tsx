import { useEffect, useRef, useState } from "react";
import { saveFile } from "../api";

export interface EditorProps {
  filePath: string;
  initialText: string;
  onSaved: (newText: string) => void;
  onCancel: () => void;
}

export function Editor({ filePath, initialText, onSaved, onCancel }: EditorProps): JSX.Element {
  const [text, setText] = useState<string>(initialText);
  const [status, setStatus] = useState<
    | { kind: "idle" }
    | { kind: "saving" }
    | { kind: "error"; message: string }
    | { kind: "saved" }
  >({ kind: "idle" });
  const taRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setText(initialText);
    setStatus({ kind: "idle" });
  }, [initialText, filePath]);

  useEffect(() => {
    if (taRef.current) taRef.current.focus();
  }, [filePath]);

  const dirty = text !== initialText;

  const onSave = async (): Promise<void> => {
    setStatus({ kind: "saving" });
    const result = await saveFile(filePath, text);
    if (result.ok) {
      setStatus({ kind: "saved" });
      onSaved(text);
    } else {
      setStatus({ kind: "error", message: `${result.error.error}${result.error.kind ? ` (${result.error.kind})` : ""}` });
    }
  };

  const onDiscard = (): void => {
    setText(initialText);
    setStatus({ kind: "idle" });
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "s") {
      e.preventDefault();
      void onSave();
    }
  };

  return (
    <div className="editor-pane">
      <div className="editor-toolbar" role="toolbar" aria-label="Editor actions">
        <button
          type="button"
          className="editor-button editor-save"
          onClick={() => void onSave()}
          disabled={!dirty || status.kind === "saving"}
        >
          {status.kind === "saving" ? "Saving…" : "Save (Ctrl+S)"}
        </button>
        <button
          type="button"
          className="editor-button"
          onClick={onDiscard}
          disabled={!dirty || status.kind === "saving"}
        >
          Discard changes
        </button>
        <button type="button" className="editor-button editor-cancel" onClick={onCancel}>
          Close editor
        </button>
        <span className="editor-status" aria-live="polite">
          {status.kind === "error" && <span className="editor-status-error">Error: {status.message}</span>}
          {status.kind === "saved" && !dirty && <span className="editor-status-ok">Saved.</span>}
          {dirty && status.kind !== "error" && <span className="editor-status-dirty">Unsaved changes</span>}
        </span>
      </div>
      <textarea
        ref={taRef}
        className="editor-textarea"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={onKeyDown}
        spellCheck={false}
        aria-label={`Edit ${filePath}`}
      />
    </div>
  );
}
