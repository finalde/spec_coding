/** ImageRefView: renders Seedream立绘 prompt + companion .png preview.
 *
 * Triggered when path matches `/ref_images/.+_seedream\.md$` OR ends `.png|.jpg`.
 * - Left pane: prompt markdown (when triggered by `_seedream.md`) or empty
 * - Right pane: image preview (when companion exists) or fallback message
 *
 * Image extensions are read-only via /api/file.
 */
import { useEffect, useMemo, useState } from "react";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { fetchFile, mediaUrl, putFile } from "../api";
import { extractFirstFencedCode, replaceFirstFencedCode } from "../lib/promptEdit";
import { ApiError, type FileResult } from "../types";
import { Renderer } from "../markdown/renderer";
import { ParseFallback } from "./ParseFallback";

export interface ImageRefViewProps {
  primaryFile: FileResult;
  primaryPath: string;
  knownPaths: string[];
  onSaved?: () => void;
}

const SEEDREAM_RE = /^(.+\/ref_images\/)([^/]+)_seedream\.md$/;
const IMG_EXT_RE = /\.(png|jpg|jpeg)$/i;

export function ImageRefView({ primaryFile, primaryPath, knownPaths, onSaved }: ImageRefViewProps): JSX.Element {
  const layout = useMemo(() => resolveLayout(primaryPath), [primaryPath]);
  const [companionImage, setCompanionImage] = useState<FileResult | null>(null);
  const [companionMissing, setCompanionMissing] = useState<boolean>(false);
  const promptBody = useMemo<string | null>(
    () => extractFirstFencedCode(primaryFile.content),
    [primaryFile.content],
  );
  const [editMode, setEditMode] = useState<boolean>(false);
  const [editBuffer, setEditBuffer] = useState<string>("");
  const [editSaving, setEditSaving] = useState<boolean>(false);
  const [editError, setEditError] = useState<string | null>(null);

  const onEditStart = (): void => {
    if (promptBody === null) return;
    setEditBuffer(promptBody);
    setEditError(null);
    setEditMode(true);
  };
  const onEditCancel = (): void => {
    setEditMode(false);
    setEditBuffer("");
    setEditError(null);
  };
  const onEditSave = async (): Promise<void> => {
    if (editSaving) return;
    setEditSaving(true);
    setEditError(null);
    try {
      const newContent = replaceFirstFencedCode(primaryFile.content, editBuffer);
      await putFile(primaryPath, newContent, { ifUnmodifiedSince: primaryFile.mtime_http });
      setEditMode(false);
      setEditBuffer("");
      if (onSaved) onSaved();
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setEditError("文件已被外部修改，请刷新后重试（你的编辑保留在 textarea 中）");
      } else if (err instanceof ApiError) {
        setEditError(`保存失败: ${err.detail?.kind ?? err.status}`);
      } else {
        setEditError(`保存失败: ${err instanceof Error ? err.message : String(err)}`);
      }
    } finally {
      setEditSaving(false);
    }
  };

  useEffect(() => {
    if (layout.kind !== "prompt") return;
    setCompanionImage(null);
    setCompanionMissing(false);
    fetchFile(layout.expectedPngPath)
      .then((f) => setCompanionImage(f))
      .catch((err) => {
        if (err instanceof ApiError && err.status === 404) {
          // Try .jpg as fallback
          fetchFile(layout.expectedJpgPath)
            .then((f) => setCompanionImage(f))
            .catch(() => setCompanionMissing(true));
        } else {
          setCompanionMissing(true);
        }
      });
  }, [layout]);

  if (layout.kind === "image") {
    // Image clicked directly — no prompt left pane
    return (
      <div className="image-ref-view image-ref-view-img-only">
        <header><h2>{layout.filename}</h2></header>
        <div className="image-ref-img-wrapper">
          <img
            src={mediaUrl(primaryPath, primaryFile.mtime)}
            alt={`${layout.filename} 立绘`}
            className="image-ref-img"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="image-ref-view">
      <PanelGroup direction="horizontal" autoSaveId="image-ref-split">
        <Panel defaultSize={55} minSize={25}>
          <section className={`image-ref-prompt-pane${editMode ? " image-ref-prompt-pane-editing" : ""}`}>
            <header className="image-ref-pane-header">
              <span className="image-ref-pane-label">Seedream prompt</span>
              <div className="image-ref-pane-actions">
                {!editMode ? (
                  promptBody !== null ? (
                    <button
                      type="button"
                      className="copy-button"
                      onClick={onEditStart}
                      title="直接编辑 Seedream prompt 代码块"
                    >
                      ✏ Edit
                    </button>
                  ) : null
                ) : (
                  <>
                    <button
                      type="button"
                      className="copy-button shot-pane-save-btn"
                      onClick={() => void onEditSave()}
                      disabled={editSaving}
                    >
                      {editSaving ? "保存中…" : "✓ Save"}
                    </button>
                    <button
                      type="button"
                      className="copy-button"
                      onClick={onEditCancel}
                      disabled={editSaving}
                    >
                      ✕ Cancel
                    </button>
                  </>
                )}
              </div>
            </header>
            {!editMode ? (
              <ParseFallback rawText={primaryFile.content} componentName="ImageRefView:prompt">
                <Renderer
                  content={primaryFile.content}
                  currentPath={primaryPath}
                  knownPaths={knownPaths}
                  editEnabled={primaryPath.startsWith("ai_videos/")}
                  mtimeHttp={primaryFile.mtime_http}
                  onSaved={onSaved}
                />
              </ParseFallback>
            ) : (
              <div className="shot-pane-edit-wrapper">
                <p className="shot-pane-edit-hint">
                  正在编辑 <code>{primaryPath.split("/").pop()}</code> 内的第一个代码块。
                </p>
                <textarea
                  className="shot-pane-textarea"
                  value={editBuffer}
                  onChange={(e) => setEditBuffer(e.target.value)}
                  spellCheck={false}
                  rows={Math.min(50, Math.max(15, editBuffer.split("\n").length + 1))}
                  disabled={editSaving}
                />
                {editError ? <div role="alert" className="shot-pane-edit-error">{editError}</div> : null}
              </div>
            )}
          </section>
        </Panel>
        <PanelResizeHandle className="resize-handle" />
        <Panel defaultSize={45} minSize={20}>
          <section className="image-ref-img-pane">
            <header className="image-ref-pane-header">
              <span className="image-ref-pane-label">Generated 立绘</span>
            </header>
            {companionImage ? (
              <div className="image-ref-img-wrapper">
                <img
                  src={mediaUrl(layout.expectedPngPath.endsWith(".png") && !companionMissing
                    ? layout.expectedPngPath : layout.expectedJpgPath, companionImage.mtime)}
                  alt={`${layout.stem} 立绘`}
                  className="image-ref-img"
                />
              </div>
            ) : companionMissing ? (
              <div className="image-ref-fallback" role="status">
                尚未生成立绘 — 复制左侧 prompt 至 Seedream 后保存为{" "}
                <code>{layout.expectedPngPath.split("/").pop()}</code> 并刷新
              </div>
            ) : (
              <div className="muted">Loading…</div>
            )}
          </section>
        </Panel>
      </PanelGroup>
    </div>
  );
}

type Layout =
  | { kind: "prompt"; folder: string; stem: string; expectedPngPath: string; expectedJpgPath: string }
  | { kind: "image"; filename: string };

function resolveLayout(path: string): Layout {
  const m = SEEDREAM_RE.exec(path);
  if (m) {
    const [, folder, stem] = m;
    return {
      kind: "prompt",
      folder,
      stem,
      expectedPngPath: `${folder}${stem}_seedream.png`,
      expectedJpgPath: `${folder}${stem}_seedream.jpg`,
    };
  }
  if (IMG_EXT_RE.test(path)) {
    return { kind: "image", filename: path.split("/").pop() ?? path };
  }
  // Should not reach here if Reader's dispatch is correct
  return { kind: "image", filename: path.split("/").pop() ?? path };
}
