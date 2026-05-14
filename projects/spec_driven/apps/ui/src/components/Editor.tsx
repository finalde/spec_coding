import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "../types";

export interface EditorProps {
  initialContent: string;
  filename: string;
  onSave: (content: string) => Promise<void>;
  onClose: () => void;
  onReload: () => Promise<void>;
  saveError: Error | null;
  conflict: { current_mtime: string } | null;
  onClearConflict: () => void;
  onDirtyChange: (dirty: boolean) => void;
}

export function Editor(props: EditorProps): JSX.Element {
  const [buffer, setBuffer] = useState<string>(props.initialContent);
  const [saving, setSaving] = useState<boolean>(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const dirty = buffer !== props.initialContent;

  useEffect(() => {
    props.onDirtyChange(dirty);
    return () => props.onDirtyChange(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dirty]);

  useEffect(() => {
    setBuffer(props.initialContent);
  }, [props.initialContent]);

  const save = useCallback(async () => {
    setSaving(true);
    try {
      await props.onSave(buffer);
    } finally {
      setSaving(false);
    }
  }, [buffer, props]);

  const discard = useCallback(() => {
    setBuffer(props.initialContent);
  }, [props.initialContent]);

  const close = useCallback(() => {
    if (dirty) {
      const ok = window.confirm("You have unsaved changes. Discard and close?");
      if (!ok) return;
    }
    props.onClose();
  }, [dirty, props]);

  // Save: Ctrl/Cmd+S
  useEffect(() => {
    const handler = (event: KeyboardEvent): void => {
      if ((event.ctrlKey || event.metaKey) && (event.key === "s" || event.key === "S")) {
        event.preventDefault();
        void save();
      }
    };
    const ta = textareaRef.current;
    if (ta) ta.addEventListener("keydown", handler);
    return () => {
      if (ta) ta.removeEventListener("keydown", handler);
    };
  }, [save]);

  // beforeunload guard
  useEffect(() => {
    if (!dirty) return;
    const handler = (event: BeforeUnloadEvent): void => {
      event.preventDefault();
      event.returnValue = "";
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [dirty]);

  return (
    <div className="editor">
      <div className="editor-toolbar" role="toolbar" aria-label="Editor toolbar">
        <button type="button" onClick={save} disabled={saving} aria-label="Save (Ctrl+S)">
          {saving ? "Saving…" : "Save"}
        </button>
        <button type="button" onClick={discard} disabled={!dirty} aria-label="Discard changes">
          Discard
        </button>
        <button type="button" onClick={close} aria-label="Close editor">
          Close editor
        </button>
        {dirty ? (
          <span
            className="dirty-indicator"
            role="status"
            aria-live="polite"
            aria-label="Unsaved changes"
          >
            <span aria-hidden="true">●</span>
          </span>
        ) : null}
      </div>
      {props.saveError ? <SaveErrorBanner error={props.saveError} /> : null}
      {props.conflict ? (
        <div className="conflict-banner" role="alert">
          file changed externally — Reload?
          <button
            type="button"
            onClick={() => {
              props.onClearConflict();
              void props.onReload();
            }}
            aria-label="Reload file"
          >
            Reload
          </button>
        </div>
      ) : null}
      <textarea
        ref={textareaRef}
        className="editor-textarea"
        value={buffer}
        onChange={(e) => setBuffer(e.target.value)}
        aria-label={`Editing ${props.filename}`}
        spellCheck={false}
      />
    </div>
  );
}

function SaveErrorBanner({ error }: { error: Error }): JSX.Element {
  let message = error.message;
  if (error instanceof ApiError) {
    if (error.status === 413) message = "file too large";
    else if (error.status === 400 && error.detail?.kind === "invalid_text") {
      message = "invalid text content (NUL byte or non-UTF-8)";
    } else if (error.status === 415) message = "unsupported file type";
    else if (error.status === 403) message = "request refused (origin/host)";
    else message = `Save failed (${error.status})`;
  }
  return (
    <div className="save-error-banner" role="alert">
      {message}
    </div>
  );
}
