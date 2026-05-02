import { useEffect, useMemo, useState } from "react";
import { fetchFile } from "../api";
import type { FileResponse, TreeNode, TreeResponse } from "../types";
import { Breadcrumb } from "./Breadcrumb";
import { Editor } from "./Editor";
import { QaView, ParseError } from "./QaView";
import { MarkdownView } from "../markdown/renderer";
import { CodeView } from "../markdown/code";
import { JsonlView } from "../markdown/jsonl";
import { RegeneratePanel } from "./RegeneratePanel";
import { RefreshButton } from "./RefreshButton";

interface ReaderProps {
  filePath: string;
  tree: TreeResponse | null;
  onRefresh: () => void;
}

interface LoadState {
  status: "idle" | "loading" | "ok" | "error";
  data?: FileResponse;
  errorStatus?: number;
  errorKind?: string;
  errorMessage?: string;
}

function collectAllPaths(tree: TreeResponse): Set<string> {
  const out = new Set<string>();
  const walk = (nodes: ReadonlyArray<TreeNode>): void => {
    for (const n of nodes) {
      if (n.kind === "file") out.add(n.path);
      if (n.children) walk(n.children);
    }
  };
  walk(tree.settings.claude_md);
  walk(tree.settings.agents);
  walk(tree.settings.skills);
  walk(tree.projects);
  return out;
}

interface StageMatch {
  projectType: string;
  projectName: string;
  stageFolder: string;
}

function parseStageFromPath(path: string): StageMatch | null {
  // specs/{type}/{name}/{stage}/...
  const segs = path.split("/");
  if (segs[0] !== "specs" || segs.length < 5) return null;
  const knownStages = new Set([
    "user_input",
    "interview",
    "findings",
    "final_specs",
    "validation",
  ]);
  if (!knownStages.has(segs[3] ?? "")) return null;
  return {
    projectType: segs[1] ?? "",
    projectName: segs[2] ?? "",
    stageFolder: segs[3] ?? "",
  };
}

function isMarkdownExt(ext: string): boolean {
  return ext === ".md";
}

function isJsonlExt(ext: string): boolean {
  return ext === ".jsonl";
}

export function Reader({ filePath, tree, onRefresh }: ReaderProps): JSX.Element {
  const [load, setLoad] = useState<LoadState>({ status: "idle" });
  const [editing, setEditing] = useState(false);

  const exposedPaths = useMemo(() => {
    if (!tree) return new Set<string>();
    return collectAllPaths(tree);
  }, [tree]);

  useEffect(() => {
    let cancelled = false;
    setLoad({ status: "loading" });
    setEditing(false);
    fetchFile(filePath)
      .then((res) => {
        if (cancelled) return;
        if (res.ok) {
          setLoad({ status: "ok", data: res.data });
        } else {
          setLoad({
            status: "error",
            errorStatus: res.status,
            errorKind: res.error.kind ?? res.error.error,
            errorMessage: res.error.error,
          });
        }
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        setLoad({
          status: "error",
          errorMessage: e instanceof Error ? e.message : "fetch failed",
        });
      });
    return () => {
      cancelled = true;
    };
  }, [filePath]);

  const stage = parseStageFromPath(filePath);

  return (
    <div className="reader">
      <Breadcrumb filePath={filePath} />
      {stage && (
        <RegeneratePanel
          projectType={stage.projectType}
          projectName={stage.projectName}
          stageHint={stage.stageFolder}
        />
      )}
      {load.status === "loading" && (
        <div className="reader-loading">Loading…</div>
      )}
      {load.status === "error" && (
        <div className="reader-error">
          {load.errorStatus === 404 && load.errorKind === "file_removed" ? (
            <div className="stale-tree-banner" role="status">
              <span>this file no longer exists — refresh sidebar</span>
              <RefreshButton onClick={onRefresh} />
            </div>
          ) : (
            <div className="editor-error-banner" role="alert">
              {load.errorStatus ?? ""} {load.errorKind ?? load.errorMessage ?? "error"}
            </div>
          )}
        </div>
      )}
      {load.status === "ok" && load.data && (
        <ReaderBody
          file={load.data}
          editing={editing}
          onEdit={() => setEditing(true)}
          onCancelEdit={() => setEditing(false)}
          onSaved={(text) => {
            setLoad({
              status: "ok",
              data: { ...load.data!, text, bytes: new Blob([text]).size },
            });
          }}
          exposedPaths={exposedPaths}
        />
      )}
    </div>
  );
}

interface ReaderBodyProps {
  file: FileResponse;
  editing: boolean;
  onEdit: () => void;
  onCancelEdit: () => void;
  onSaved: (text: string) => void;
  exposedPaths: ReadonlySet<string>;
}

function ReaderBody({
  file,
  editing,
  onEdit,
  onCancelEdit,
  onSaved,
  exposedPaths,
}: ReaderBodyProps): JSX.Element {
  if (editing) {
    return (
      <Editor
        filePath={file.path}
        initialText={file.text}
        onSaved={onSaved}
        onCancel={onCancelEdit}
      />
    );
  }
  // Q/A path detection
  const isQa = file.path.endsWith("/interview/qa.md");
  return (
    <>
      <div className="reader-toolbar">
        <button
          type="button"
          className="reader-edit-btn"
          onClick={onEdit}
          aria-label="Edit file"
        >
          &#x270E; Edit
        </button>
      </div>
      {isQa ? (
        <QaViewSafe
          source={file.text}
          filePath={file.path}
          onSaved={onSaved}
          exposedPaths={exposedPaths}
        />
      ) : isMarkdownExt(file.extension) ? (
        <MarkdownView
          source={file.text}
          sourcePath={file.path}
          exposedPaths={exposedPaths}
        />
      ) : isJsonlExt(file.extension) ? (
        <JsonlView source={file.text} />
      ) : (
        <CodeView source={file.text} extension={file.extension} />
      )}
    </>
  );
}

interface QaViewSafeProps {
  source: string;
  filePath: string;
  onSaved: (text: string) => void;
  exposedPaths: ReadonlySet<string>;
}

function QaViewSafe({
  source,
  filePath,
  onSaved,
  exposedPaths,
}: QaViewSafeProps): JSX.Element {
  try {
    return <QaView source={source} filePath={filePath} onSaved={onSaved} />;
  } catch (e) {
    if (e instanceof ParseError) {
      return (
        <MarkdownView
          source={source}
          sourcePath={filePath}
          exposedPaths={exposedPaths}
        />
      );
    }
    return (
      <MarkdownView
        source={source}
        sourcePath={filePath}
        exposedPaths={exposedPaths}
      />
    );
  }
}
