/** Reader: render-mode dispatch by file extension + path pattern. */
import { useCallback, useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";
import { Breadcrumb } from "./Breadcrumb";
import { ParseFallback } from "./ParseFallback";
import { Editor } from "./Editor";
import { ShotPairView } from "./ShotPairView";
import { ShotlistTableView } from "./ShotlistTableView";
import { ImageRefView } from "./ImageRefView";
import { Renderer } from "../markdown/renderer";
import { CodeView } from "../markdown/CodeView";
import { JsonlView } from "../markdown/JsonlView";
import { detectShotPair } from "../lib/shotPairing";
import { fetchFile, putFile } from "../api";
import { ApiError, type FileResult } from "../types";

export interface ReaderProps {
  knownPaths: string[];
  onSaved: () => void;
}

export function Reader({ knownPaths, onSaved }: ReaderProps): JSX.Element {
  const location = useLocation();
  const path = useMemo<string | null>(() => {
    if (!location.pathname.startsWith("/file/")) return null;
    const encoded = location.pathname.slice("/file/".length);
    try { return decodeURIComponent(encoded); } catch { return null; }
  }, [location.pathname]);

  const [file, setFile] = useState<FileResult | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [editing, setEditing] = useState<boolean>(false);
  const [saveError, setSaveError] = useState<Error | null>(null);
  const [conflict, setConflict] = useState<{ current_mtime: string } | null>(null);

  const load = useCallback(async () => {
    if (!path) return;
    try {
      const f = await fetchFile(path);
      setFile(f);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    }
  }, [path]);

  useEffect(() => {
    setFile(null); setError(null); setEditing(false); setSaveError(null); setConflict(null);
    void load();
  }, [load]);

  const onSave = useCallback(async (newContent: string): Promise<void> => {
    if (!file || !path) return;
    try {
      const result = await putFile(path, newContent, { ifUnmodifiedSince: file.mtime_http });
      setFile({ ...file, content: newContent, ...result });
      setSaveError(null); setConflict(null);
      onSaved();
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 409 && err.detail?.kind === "stale_write") {
          const cm = (err.detail as { current_mtime?: string }).current_mtime;
          setConflict({ current_mtime: cm ?? "" });
        } else { setSaveError(err); }
      } else if (err instanceof Error) { setSaveError(err); }
      throw err;
    }
  }, [file, onSaved, path]);

  const setDocumentTitle = useCallback((dirty: boolean) => {
    if (!path) return;
    const base = path.split("/").pop() ?? path;
    document.title = dirty ? `* ${base} — ai_video_management` : `${base} — ai_video_management`;
  }, [path]);

  if (!path) return <div className="muted">No file selected.</div>;
  if (error) {
    return (
      <div className="reader">
        <div role="alert" className="save-error-banner">
          {error instanceof ApiError ? `${error.status} ${apiErrorLabel(error)}` : error.message}
        </div>
      </div>
    );
  }
  if (!file) return <div className="muted">Loading…</div>;

  const ext = extOf(path);
  const isImage = ext === ".png" || ext === ".jpg" || ext === ".jpeg";
  const isMarkdown = ext === ".md";
  const isJsonl = ext === ".jsonl";
  const isCode = ext === ".json" || ext === ".yaml" || ext === ".yml";
  const isTxt = ext === ".txt";

  const shotPair = isMarkdown ? detectShotPair(path) : null;
  const isShotPair = shotPair !== null;
  const isShotlistTable = path.startsWith("ai_videos/") && path.endsWith("/shotlist.md");
  const isImageRef = (isMarkdown && /\/ref_images\/[^/]+_seedream\.md$/.test(path)) || isImage;

  const filename = path.split("/").pop() ?? path;

  return (
    <div className="reader">
      <div className="reader-toolbar" role="toolbar" aria-label="File toolbar">
        <Breadcrumb path={path} />
        {!isImage ? (
          <button type="button" className="reader-edit-toggle"
            onClick={() => setEditing((e) => !e)}
            aria-label={editing ? "Stop editing" : "Edit file"} aria-pressed={editing}>
            ✎ {editing ? "Editing" : "Edit"}
          </button>
        ) : null}
      </div>
      {editing && !isImage && !isShotPair && !isImageRef ? (
        <Editor
          initialContent={file.content} filename={filename}
          onSave={onSave} onClose={() => setEditing(false)}
          onReload={async () => { await load(); }}
          saveError={saveError} conflict={conflict}
          onClearConflict={() => setConflict(null)}
          onDirtyChange={setDocumentTitle}
        />
      ) : (
        <div className="reader-body">
          {isImageRef ? (
            <ImageRefView primaryFile={file} primaryPath={path} knownPaths={knownPaths} />
          ) : isShotPair ? (
            <ShotPairView primaryFile={file} primaryPath={path} knownPaths={knownPaths} />
          ) : isShotlistTable ? (
            <ParseFallback rawText={file.content} componentName="ShotlistTableView">
              <ShotlistTableView content={file.content} shotlistPath={path} />
            </ParseFallback>
          ) : isJsonl ? (
            <ParseFallback rawText={file.content} componentName="JsonlView">
              <JsonlView content={file.content} />
            </ParseFallback>
          ) : isCode ? (
            <ParseFallback rawText={file.content} componentName="CodeView">
              <CodeView content={file.content} filename={filename} />
            </ParseFallback>
          ) : isMarkdown ? (
            <ParseFallback rawText={file.content} componentName="MarkdownView">
              <Renderer content={file.content} currentPath={path} knownPaths={knownPaths} />
            </ParseFallback>
          ) : isTxt ? (
            <pre className="text-view">{file.content}</pre>
          ) : (
            <pre className="text-view">{file.content}</pre>
          )}
        </div>
      )}
    </div>
  );
}

function apiErrorLabel(err: ApiError): string {
  if (err.status === 404) return "not found";
  if (err.status === 400) return err.detail?.kind ?? "bad request";
  if (err.status === 413) return "file too large";
  if (err.status === 403) return "forbidden";
  if (err.status === 409) return "stale write";
  return err.detail?.kind ?? err.message;
}

function extOf(path: string): string {
  const dot = path.lastIndexOf(".");
  if (dot < 0) return "";
  return path.slice(dot).toLowerCase();
}
