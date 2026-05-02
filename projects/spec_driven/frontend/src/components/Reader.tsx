import { useEffect, useMemo, useState } from "react";
import { fetchFile } from "../api";
import { CodeView } from "../markdown/code";
import { JsonlView } from "../markdown/jsonl";
import { MarkdownView } from "../markdown/renderer";
import type { FileResponse } from "../types";
import { Breadcrumb } from "./Breadcrumb";
import { Editor } from "./Editor";
import { QaView } from "./QaView";
import { RegeneratePanel } from "./RegeneratePanel";

export interface ReaderProps {
  filePath: string;
  exposedPaths: ReadonlySet<string>;
  onRequestRefresh: () => void;
}

export function Reader({ filePath, exposedPaths, onRequestRefresh }: ReaderProps): JSX.Element {
  const [state, setState] = useState<
    | { status: "loading" }
    | { status: "ok"; data: FileResponse }
    | { status: "error"; httpStatus: number; error: string; kind?: string }
  >({ status: "loading" });
  const [editing, setEditing] = useState<boolean>(false);

  useEffect(() => {
    let cancelled = false;
    setState({ status: "loading" });
    setEditing(false);
    (async () => {
      const result = await fetchFile(filePath);
      if (cancelled) return;
      if (result.ok) {
        setState({ status: "ok", data: result.data });
      } else {
        setState({
          status: "error",
          httpStatus: result.status,
          error: result.error.error,
          kind: result.error.kind,
        });
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [filePath]);

  const projectContext = useMemo(() => deriveProjectContext(filePath), [filePath]);

  const onSaved = (newText: string): void => {
    setState((prev) =>
      prev.status === "ok"
        ? { status: "ok", data: { ...prev.data, text: newText, bytes: new Blob([newText]).size } }
        : prev,
    );
  };

  return (
    <main className="reader">
      <Breadcrumb filePath={filePath} />
      {state.status === "ok" && (
        <div className="reader-actions">
          {!editing && (
            <button type="button" className="editor-button" onClick={() => setEditing(true)}>
              ✎ Edit
            </button>
          )}
        </div>
      )}
      {projectContext && state.status === "ok" && !editing && (
        <RegeneratePanel
          projectType={projectContext.projectType}
          projectName={projectContext.projectName}
          stageHint={projectContext.stageHint}
        />
      )}
      {state.status === "loading" && <div className="reader-loading">Loading…</div>}
      {state.status === "error" && (
        <ErrorView
          httpStatus={state.httpStatus}
          error={state.error}
          kind={state.kind}
          onRefresh={onRequestRefresh}
        />
      )}
      {state.status === "ok" && (
        <div className="reader-content">
          {editing ? (
            <Editor
              filePath={state.data.path}
              initialText={state.data.text}
              onSaved={onSaved}
              onCancel={() => setEditing(false)}
            />
          ) : (
            <RenderedFile data={state.data} exposedPaths={exposedPaths} />
          )}
        </div>
      )}
    </main>
  );
}

function RenderedFile({
  data,
  exposedPaths,
}: {
  data: FileResponse;
  exposedPaths: ReadonlySet<string>;
}): JSX.Element {
  if (data.extension === ".md" && isQaFile(data.path)) {
    return <QaView source={data.text} filePath={data.path} />;
  }
  if (data.extension === ".md") {
    return <MarkdownView source={data.text} sourcePath={data.path} exposedPaths={exposedPaths} />;
  }
  if (data.extension === ".jsonl") {
    return <JsonlView source={data.text} />;
  }
  return <CodeView source={data.text} extension={data.extension} />;
}

function isQaFile(path: string): boolean {
  return path.endsWith("/interview/qa.md") || path === "interview/qa.md";
}

interface ProjectContext {
  projectType: string;
  projectName: string;
  stageHint?: string;
}

function deriveProjectContext(filePath: string): ProjectContext | null {
  const parts = filePath.split("/").filter((s) => s !== "");
  if (parts[0] !== "specs" || parts.length < 3) return null;
  const projectType = parts[1];
  const projectName = parts[2];
  const stageHint = parts[3];
  return { projectType, projectName, stageHint };
}

function ErrorView({
  httpStatus,
  error,
  kind,
  onRefresh,
}: {
  httpStatus: number;
  error: string;
  kind?: string;
  onRefresh: () => void;
}): JSX.Element {
  const cause = errorMessage(httpStatus, error, kind);
  const showRefresh = kind === "file_removed" || error === "not_found";
  return (
    <div className="reader-error" role="alert">
      <span className="link-broken" aria-disabled="true" title={cause}>
        {cause}
      </span>
      {showRefresh && (
        <button type="button" className="refresh-button" onClick={onRefresh}>
          ↻ Refresh sidebar
        </button>
      )}
    </div>
  );
}

function errorMessage(status: number, error: string, kind?: string): string {
  if (status === 400 && error === "outside_sandbox") return "outside exposed tree";
  if (status === 404 && kind === "file_removed") return "this file no longer exists — refresh sidebar";
  if (status === 404 && kind === "outside_exposed_tree") return "outside exposed tree";
  if (status === 404) return "file not found";
  if (status === 403) return "permission denied";
  if (status === 413) return "file too large";
  if (status === 415 && error === "binary_content") return "file appears to be binary";
  if (status === 415) return "unsupported file type";
  return `error ${status}: ${error}`;
}
