import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchFile } from "../api";
import { MarkdownView } from "../markdown/Renderer";
import { CodeView } from "../markdown/CodeView";
import { JsonlView } from "../markdown/JsonlView";
import { ImagePlaceholder } from "../markdown/ImagePlaceholder";
import { QaView } from "./QaView";
import { QaErrorBoundary } from "./QaErrorBoundary";
import { Editor } from "./Editor";
import { RegeneratePanel } from "./RegeneratePanel";
import { Breadcrumb } from "./Breadcrumb";
import type { FileResult } from "../types";

function dispatchKind(path: string): "qa" | "markdown" | "jsonl" | "code" | "image" | "text" {
  if (/\binterview\/qa\.md$/.test(path)) return "qa";
  const ext = (path.match(/\.([^.]+)$/)?.[1] || "").toLowerCase();
  if (ext === "md") return "markdown";
  if (ext === "jsonl") return "jsonl";
  if (ext === "json" || ext === "yaml" || ext === "yml") return "code";
  if (ext === "png" || ext === "jpg") return "image";
  return "text";
}

function projectContext(path: string): { type: string; name: string; stage: string | null } | null {
  const m = path.match(/^specs\/([^/]+)\/([^/]+)(?:\/([^/]+))?\//);
  if (!m) return null;
  return { type: m[1], name: m[2], stage: m[3] ?? null };
}

export function Reader() {
  const params = useParams();
  const filePath = (params["*"] || "") as string;

  const [file, setFile] = useState<FileResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState<boolean>(false);
  const [perBlockOpen, setPerBlockOpen] = useState<boolean>(false);

  useEffect(() => {
    setFile(null);
    setError(null);
    setEditing(false);
    fetchFile(filePath)
      .then(setFile)
      .catch((e) => {
        const msg =
          e?.status === 404
            ? "not found"
            : e?.status === 415
              ? "unsupported file type"
              : e?.status === 413
                ? "file too large"
                : "could not load file";
        setError(`${msg} (${filePath})`);
      });
  }, [filePath]);

  if (error) {
    return (
      <main id="main" tabIndex={-1}>
        <Breadcrumb path={filePath} />
        <div role="alert">{error}</div>
      </main>
    );
  }
  if (!file) {
    return (
      <main id="main" tabIndex={-1}>
        <Breadcrumb path={filePath} />
        <p>Loading…</p>
      </main>
    );
  }

  const kind = dispatchKind(file.path);
  const ctx = projectContext(file.path);
  const isStageFile = ctx && ctx.stage !== null;
  const stageId = mapFolderToStageId(ctx?.stage ?? null);

  const onSavedReplace = (newContent: string) => {
    setFile({ ...file, content: newContent });
  };

  return (
    <main id="main" tabIndex={-1}>
      <Breadcrumb path={file.path} />
      <div className="toolbar">
        <span className="filename">{file.path}</span>
        {!editing && kind !== "image" && (
          <button
            type="button"
            data-testid="editor-toggle"
            disabled={perBlockOpen}
            aria-disabled={perBlockOpen}
            onClick={() => setEditing(true)}
          >
            ✎ Edit
          </button>
        )}
      </div>
      {isStageFile && ctx && stageId && (
        <RegeneratePanel projectType={ctx.type} projectName={ctx.name} initialStageId={stageId} />
      )}
      {editing ? (
        <Editor
          filePath={file.path}
          initial={file.content}
          onClose={() => setEditing(false)}
          onSaved={onSavedReplace}
        />
      ) : kind === "qa" ? (
        <QaErrorBoundary
          fallback={(cause) => (
            <>
              <div role="alert" className="qa-fallback-banner">
                Could not parse structured Q/A view; rendering raw markdown. (cause: {cause})
              </div>
              <MarkdownView source={file.content} filePath={file.path} />
            </>
          )}
        >
          <QaView
            source={file.content}
            filePath={file.path}
            onWholeFileEdit={() => setEditing(true)}
            fileLevelDisabled={perBlockOpen}
            onAnyBlockOpen={setPerBlockOpen}
            onSaved={onSavedReplace}
          />
        </QaErrorBoundary>
      ) : kind === "markdown" ? (
        <MarkdownView source={file.content} filePath={file.path} />
      ) : kind === "jsonl" ? (
        <JsonlView source={file.content} />
      ) : kind === "code" ? (
        <CodeView source={file.content} language={langFromExt(file.path)} />
      ) : kind === "image" ? (
        <ImagePlaceholder path={file.path} base64={file.data_encoding === "base64" ? file.content : undefined} />
      ) : (
        <pre>{file.content}</pre>
      )}
    </main>
  );
}

function langFromExt(path: string): string {
  const ext = (path.match(/\.([^.]+)$/)?.[1] || "").toLowerCase();
  if (ext === "json" || ext === "jsonl") return "json";
  if (ext === "yaml" || ext === "yml") return "yaml";
  return "plaintext";
}

function mapFolderToStageId(folder: string | null): string | null {
  if (!folder) return null;
  switch (folder) {
    case "user_input":
      return "intake";
    case "interview":
      return "interview";
    case "findings":
      return "research";
    case "final_specs":
      return "spec";
    case "validation":
      return "validation";
    default:
      return null;
  }
}
