import { useEffect, useState } from "react";
import { fetchFile } from "../api";
import { CodeView } from "../markdown/code";
import { JsonlView } from "../markdown/jsonl";
import { MarkdownView } from "../markdown/renderer";
import type { FileResponse } from "../types";
import { Breadcrumb } from "./Breadcrumb";

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

  useEffect(() => {
    let cancelled = false;
    setState({ status: "loading" });
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

  return (
    <main className="reader">
      <Breadcrumb filePath={filePath} />
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
          <RenderedFile data={state.data} exposedPaths={exposedPaths} />
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
  if (data.extension === ".md") {
    return <MarkdownView source={data.text} sourcePath={data.path} exposedPaths={exposedPaths} />;
  }
  if (data.extension === ".jsonl") {
    return <JsonlView source={data.text} />;
  }
  return <CodeView source={data.text} extension={data.extension} />;
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
