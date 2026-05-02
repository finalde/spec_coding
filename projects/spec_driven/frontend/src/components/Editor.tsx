import { useCallback, useEffect, useRef, useState } from "react";
import { saveFile } from "../api";

interface EditorProps {
  filePath: string;
  initialText: string;
  onSaved: (text: string) => void;
  onCancel: () => void;
}

type Status = "idle" | "saving" | "error" | "saved";

export function Editor({
  filePath,
  initialText,
  onSaved,
  onCancel,
}: EditorProps): JSX.Element {
  const [text, setText] = useState(initialText);
  const [lastSavedText, setLastSavedText] = useState(initialText);
  const [status, setStatus] = useState<Status>("idle");
  const [errorBanner, setErrorBanner] = useState<string | null>(null);
  const taRef = useRef<HTMLTextAreaElement | null>(null);

  const dirty = text !== lastSavedText;

  const doSave = useCallback(async (): Promise<void> => {
    if (!dirty) return;
    setStatus("saving");
    const result = await saveFile(filePath, text);
    if (result.ok) {
      setLastSavedText(text);
      setStatus("saved");
      setErrorBanner(null);
      onSaved(text);
    } else {
      const errKind = result.error.kind ?? result.error.error ?? "save_failed";
      setStatus("error");
      setErrorBanner(`${result.status} ${errKind}`);
    }
  }, [dirty, filePath, text, onSaved]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent): void => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
        e.preventDefault();
        if (dirty) {
          void doSave();
        }
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [doSave, dirty]);

  return (
    <div className="editor">
      <div className="editor-toolbar">
        <span className="editor-file-label">
          {filePath}
          {dirty && (
            <span
              className="editor-dirty-dot"
              aria-label="Unsaved changes"
              title="Unsaved changes"
            />
          )}
        </span>
        <button
          type="button"
          className="editor-btn editor-save"
          onClick={() => void doSave()}
          disabled={!dirty || status === "saving"}
          aria-label="Save"
        >
          Save
        </button>
        <button
          type="button"
          className="editor-btn editor-discard"
          onClick={() => {
            setText(lastSavedText);
            setStatus("idle");
            setErrorBanner(null);
          }}
          disabled={!dirty}
          aria-label="Discard changes"
        >
          Discard
        </button>
        <button
          type="button"
          className="editor-btn editor-close"
          onClick={onCancel}
          aria-label="Close editor"
        >
          Close editor
        </button>
        <span className="editor-status" role="status" aria-live="polite">
          {dirty
            ? "Unsaved changes"
            : status === "saved"
              ? "Saved."
              : ""}
        </span>
      </div>
      {errorBanner && (
        <div className="editor-error-banner" role="alert">
          {errorBanner}
        </div>
      )}
      <textarea
        ref={taRef}
        className="editor-textarea"
        value={text}
        onChange={(e) => setText(e.target.value)}
        aria-label={`Edit ${filePath}`}
        spellCheck={false}
      />
    </div>
  );
}
