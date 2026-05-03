import { useEffect, useRef, useState } from "react";
import { putFile } from "../api";

interface Props {
  filePath: string;
  initial: string;
  onClose: () => void;
  onSaved: (newContent: string) => void;
}

export function Editor({ filePath, initial, onClose, onSaved }: Props) {
  const [content, setContent] = useState<string>(initial);
  const [baseline, setBaseline] = useState<string>(initial);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);
  const taRef = useRef<HTMLTextAreaElement | null>(null);

  const dirty = content !== baseline;

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        void doSave();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  const doSave = async () => {
    if (saving) return;
    setSaving(true);
    try {
      await putFile(filePath, content);
      setBaseline(content);
      onSaved(content);
      setError(null);
    } catch (e: any) {
      const detail = e?.detail?.detail;
      let msg: string;
      if (detail && typeof detail === "object" && "kind" in detail) {
        msg = String(detail.kind);
      } else if (typeof detail === "string") {
        msg = detail;
      } else {
        msg = `network error (status ${e?.status ?? "?"})`;
      }
      setError(`Could not save: ${msg}`);
    } finally {
      setSaving(false);
    }
  };

  const doDiscard = () => {
    setContent(baseline);
    setError(null);
  };

  return (
    <div className="editor">
      <div className="editor-toolbar">
        <span className="filename">
          {filePath}
          {dirty && (
            <span
              className="dirty-dot"
              data-testid="editor-dirty-dot"
              aria-label="unsaved changes"
              title="unsaved changes"
            >
              ●
            </span>
          )}
        </span>
        <button type="button" data-testid="editor-save" onClick={doSave}>
          Save
        </button>
        <button type="button" data-testid="editor-discard" onClick={doDiscard} disabled={!dirty}>
          Discard
        </button>
        <button type="button" data-testid="editor-close" onClick={onClose}>
          Close editor
        </button>
      </div>
      {error && (
        <div role="alert" className="editor-error" data-testid="editor-error-banner">
          {error}
        </div>
      )}
      <textarea
        ref={taRef}
        data-testid="editor-textarea"
        className="editor-textarea"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        aria-label={`Edit ${filePath}`}
        spellCheck={false}
      />
    </div>
  );
}
