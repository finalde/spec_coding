import { useCallback, useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";
import { Breadcrumb } from "./Breadcrumb";
import { QaView } from "./QaView";
import { QaErrorBoundary } from "./QaErrorBoundary";
import { ParseFallback } from "./ParseFallback";
import { Editor } from "./Editor";
import { Renderer, type PinContext } from "../markdown/renderer";
import { CodeView } from "../markdown/CodeView";
import { JsonlView } from "../markdown/JsonlView";
import { ImagePlaceholder } from "../markdown/ImagePlaceholder";
import { RegeneratePanel } from "./RegeneratePanel";
import { fetchFile, putFile, postPromote, deletePromote } from "../api";
import { ApiError, type FileResult } from "../types";

export interface ReaderProps {
  knownPaths: string[];
  onSaved: () => void;
}

interface ProjectInfo {
  type: string;
  name: string;
  stage: string | null;
}

export function Reader({ knownPaths, onSaved }: ReaderProps): JSX.Element {
  const location = useLocation();
  const path = useMemo<string | null>(() => {
    if (!location.pathname.startsWith("/file/")) return null;
    const encoded = location.pathname.slice("/file/".length);
    try {
      return decodeURIComponent(encoded);
    } catch {
      return null;
    }
  }, [location.pathname]);

  const [file, setFile] = useState<FileResult | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [editing, setEditing] = useState<boolean>(false);
  const [activeBlockOpen, setActiveBlockOpen] = useState<boolean>(false);
  const [saveError, setSaveError] = useState<Error | null>(null);
  const [conflict, setConflict] = useState<{ current_mtime: string } | null>(null);
  const [pinnedIds, setPinnedIds] = useState<Set<string>>(new Set());

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
    setFile(null);
    setError(null);
    setEditing(false);
    setSaveError(null);
    setConflict(null);
    void load();
  }, [load]);

  // Load pinned items from any sibling promoted.md
  const projectInfo = useMemo<ProjectInfo | null>(() => parseProjectFromPath(path), [path]);
  const pinnableStage = useMemo<PinStage | null>(
    () => (projectInfo && isPinnableStage(projectInfo.stage) ? (projectInfo.stage as PinStage) : null),
    [projectInfo],
  );

  useEffect(() => {
    if (!projectInfo || !pinnableStage) return;
    const stagePath = `specs/${projectInfo.type}/${projectInfo.name}/${pinnableStage}/promoted.md`;
    fetchFile(stagePath)
      .then((f) => setPinnedIds(extractPinnedIds(f.content)))
      .catch(() => setPinnedIds(new Set()));
  }, [projectInfo, pinnableStage]);

  const onSave = useCallback(
    async (newContent: string): Promise<void> => {
      if (!file || !path) return;
      try {
        const result = await putFile(path, newContent, {
          ifUnmodifiedSince: file.mtime,
        });
        setFile({ ...file, content: newContent, ...result });
        setSaveError(null);
        setConflict(null);
        onSaved();
      } catch (err) {
        if (err instanceof ApiError) {
          if (err.status === 409 && err.detail?.kind === "stale_write") {
            const cm = (err.detail as { current_mtime?: string }).current_mtime;
            setConflict({ current_mtime: cm ?? "" });
          } else {
            setSaveError(err);
          }
        } else if (err instanceof Error) {
          setSaveError(err);
        }
        throw err;
      }
    },
    [file, onSaved, path],
  );

  const setDocumentTitle = useCallback(
    (dirty: boolean) => {
      if (!path) return;
      const base = path.split("/").pop() ?? path;
      document.title = dirty ? `* ${base} — spec_driven` : `${base} — spec_driven`;
    },
    [path],
  );

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
  const isImage = ext === ".png" || ext === ".jpg";
  const isMarkdown = ext === ".md";
  const isQa = path.endsWith("/interview/qa.md");
  const isJsonl = ext === ".jsonl";
  const isCode = ext === ".json" || ext === ".yaml" || ext === ".yml";
  const isTxt = ext === ".txt";

  const filename = path.split("/").pop() ?? path;
  const editDisabled = activeBlockOpen;

  const showRegenPanel =
    projectInfo !== null && projectInfo.stage !== null && !isImage;

  const onPin = async (pair: { itemId: string; rawQuestionLine: string; rawAnswerLine: string }): Promise<void> => {
    if (!projectInfo || !projectInfo.stage) return;
    if (projectInfo.stage !== "interview") return;
    const block = `${pair.rawQuestionLine}\n${pair.rawAnswerLine}`;
    await postPromote({
      project_type: projectInfo.type,
      project_name: projectInfo.name,
      stage_folder: "interview",
      source_file: filename,
      item_id: pair.itemId,
      item_text: block,
    });
    setPinnedIds((s) => new Set([...s, pair.itemId]));
  };

  const onUnpin = async (pair: { itemId: string }): Promise<void> => {
    if (!projectInfo || !projectInfo.stage) return;
    if (projectInfo.stage !== "interview") return;
    await deletePromote({
      project_type: projectInfo.type,
      project_name: projectInfo.name,
      stage_folder: "interview",
      item_id: pair.itemId,
    });
    setPinnedIds((s) => {
      const n = new Set(s);
      n.delete(pair.itemId);
      return n;
    });
  };

  const onPinMarkdown = async (itemId: string): Promise<void> => {
    if (!projectInfo || !pinnableStage || !file) return;
    const body = extractMarkdownItemBody(file.content, itemId);
    if (body === null) return;
    await postPromote({
      project_type: projectInfo.type,
      project_name: projectInfo.name,
      stage_folder: pinnableStage,
      source_file: filename,
      item_id: itemId,
      item_text: body,
    });
    setPinnedIds((s) => new Set([...s, itemId]));
  };

  const onUnpinMarkdown = async (itemId: string): Promise<void> => {
    if (!projectInfo || !pinnableStage) return;
    await deletePromote({
      project_type: projectInfo.type,
      project_name: projectInfo.name,
      stage_folder: pinnableStage,
      item_id: itemId,
    });
    setPinnedIds((s) => {
      const n = new Set(s);
      n.delete(itemId);
      return n;
    });
  };

  const pinContext: PinContext | null =
    projectInfo && pinnableStage && pinnableStage !== "interview"
      ? {
          projectType: projectInfo.type,
          projectName: projectInfo.name,
          stageFolder: pinnableStage,
          pinnedIds,
          onPin: (id) => void onPinMarkdown(id),
          onUnpin: (id) => void onUnpinMarkdown(id),
        }
      : null;

  return (
    <div className="reader">
      <div className="reader-toolbar" role="toolbar" aria-label="File toolbar">
        <Breadcrumb path={path} />
        {!isImage ? (
          <button
            type="button"
            className="reader-edit-toggle"
            onClick={() => setEditing((e) => !e)}
            disabled={editDisabled}
            aria-label={editing ? "Stop editing" : "Edit file"}
            aria-pressed={editing}
          >
            ✎ {editing ? "Editing" : "Edit"}
          </button>
        ) : null}
      </div>
      {showRegenPanel && projectInfo ? (
        <RegeneratePanel
          projectType={projectInfo.type}
          projectName={projectInfo.name}
          stageId={mapFolderToStageId(projectInfo.stage)}
        />
      ) : null}
      {editing && !isImage ? (
        <Editor
          initialContent={file.content}
          filename={filename}
          onSave={onSave}
          onClose={() => setEditing(false)}
          onReload={async () => {
            await load();
          }}
          saveError={saveError}
          conflict={conflict}
          onClearConflict={() => setConflict(null)}
          onDirtyChange={setDocumentTitle}
        />
      ) : (
        <div className="reader-body">
          {isImage ? (
            <ImagePlaceholder filename={filename} bytes={file.bytes} />
          ) : isQa ? (
            <QaErrorBoundary key={path} rawText={file.content}>
              <QaView
                content={file.content}
                filePath={path}
                onSave={onSave}
                saveError={saveError}
                onActiveBlockChange={setActiveBlockOpen}
                fileEditDisabled={editing}
                projectType={projectInfo?.type ?? null}
                projectName={projectInfo?.name ?? null}
                onPin={onPin}
                onUnpin={onUnpin}
                pinnedIds={pinnedIds}
              />
            </QaErrorBoundary>
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
              <Renderer
                content={file.content}
                currentPath={path}
                knownPaths={knownPaths}
                pinContext={pinContext}
              />
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
  if (err.status === 415) return "unsupported file type";
  if (err.status === 413) return "file too large";
  if (err.status === 403) return "forbidden";
  return err.detail?.kind ?? err.message;
}

function extOf(path: string): string {
  const dot = path.lastIndexOf(".");
  if (dot < 0) return "";
  return path.slice(dot).toLowerCase();
}

function parseProjectFromPath(path: string | null): ProjectInfo | null {
  if (!path) return null;
  // specs/{type}/{name}/{stage}/...
  const parts = path.split("/");
  if (parts[0] === "specs" && parts.length >= 4) {
    return {
      type: parts[1],
      name: parts[2],
      stage: parts.length >= 4 ? parts[3] : null,
    };
  }
  return null;
}

function mapFolderToStageId(folder: string | null): string | null {
  return folder;
}

function extractPinnedIds(content: string): Set<string> {
  const ids = new Set<string>();
  const matches = content.matchAll(/<!--\s*[Pp][Ii][Nn]\s+([^>]*?)-->/g);
  for (const m of matches) {
    const idMatch = /\bid=([^\s>]+)/.exec(m[1]);
    if (idMatch) ids.add(idMatch[1]);
  }
  return ids;
}

const PIN_STAGES = ["interview", "findings", "final_specs", "validation"] as const;
type PinStage = (typeof PIN_STAGES)[number];

function isPinnableStage(stage: string | null): stage is PinStage {
  return stage !== null && (PIN_STAGES as readonly string[]).includes(stage);
}

function extractMarkdownItemBody(content: string, itemId: string): string | null {
  // itemId looks like "FR-1", "NFR-12", "AC-29", "SYS-16b", "OQ-3".
  // Source lines look like:  **FR-1.** ...
  // We grab from the marker line through a blank line (paragraph) or next marker.
  const lines = content.split(/\r?\n/);
  const escaped = itemId.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const start = new RegExp(`^\\s*(?:[-*]\\s+)?\\*\\*${escaped}\\.?\\*\\*`);
  let startIdx = -1;
  for (let i = 0; i < lines.length; i++) {
    if (start.test(lines[i])) {
      startIdx = i;
      break;
    }
  }
  if (startIdx < 0) return null;
  let endIdx = lines.length;
  for (let i = startIdx + 1; i < lines.length; i++) {
    if (lines[i].trim() === "") {
      endIdx = i;
      break;
    }
  }
  return lines.slice(startIdx, endIdx).join("\n").trimEnd();
}
