/** ShotPairView: renders Kling + Seedance shot prompts side-by-side
 * using react-resizable-panels. Pair detection via shotPairing helper.
 *
 * Per follow-up 2026-05-25: each pane has an inline "✏ Edit" toggle that
 * swaps just the prompt code block into a textarea + Save / Cancel.
 * The "复制" button copies just the code-block body (not the whole .md).
 */
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { fetchFile, putFile } from "../api";
import { extractFirstFencedCode, replaceFirstFencedCode } from "../lib/promptEdit";
import { PromptStructuredEditor } from "./PromptStructuredEditor";
import { ApiError, type FileResult } from "../types";
import { detectShotPair, type ShotPairInfo } from "../lib/shotPairing";
import { Renderer } from "../markdown/renderer";
import { ParseFallback } from "./ParseFallback";

export interface ShotPairViewProps {
  primaryFile: FileResult;
  primaryPath: string;
  knownPaths: string[];
  onSaved?: () => void;
}

export function ShotPairView({ primaryFile, primaryPath, knownPaths, onSaved }: ShotPairViewProps): JSX.Element {
  const pair = useMemo<ShotPairInfo | null>(() => detectShotPair(primaryPath), [primaryPath]);
  const [partner, setPartner] = useState<FileResult | null>(null);
  const [partnerError, setPartnerError] = useState<ApiError | null>(null);

  useEffect(() => {
    if (!pair) return;
    setPartner(null);
    setPartnerError(null);
    fetchFile(pair.partnerPath)
      .then((f) => setPartner(f))
      .catch((err) => {
        if (err instanceof ApiError) setPartnerError(err);
        else setPartnerError(new ApiError(0, String(err), null));
      });
  }, [pair]);

  if (!pair) {
    return (
      <div className="muted">
        Path does not match shot-pair pattern. Required: <code>prompts/shot&#123;NN&#125;_&#123;kling|seedance&#125;.md</code>
      </div>
    );
  }

  const left = pair.primaryKind === "kling" ? primaryFile : partner;
  const leftLabel = "Kling (image-to-video)";
  const right = pair.primaryKind === "kling" ? partner : primaryFile;
  const rightLabel = "Seedance (text-to-video)";
  const leftPath = pair.primaryKind === "kling" ? primaryPath : pair.partnerPath;
  const rightPath = pair.primaryKind === "seedance" ? primaryPath : pair.partnerPath;
  const partnerMissing = partnerError !== null && partnerError.status === 404;

  return (
    <div className="shot-pair-view" data-shot={pair.shotSlug}>
      <header className="shot-pair-header">
        <h2>Shot {pair.shotNumber} — pair view</h2>
        {partnerMissing ? (
          <div className="shot-pair-missing-banner" role="alert">
            缺少配对文件: <code>{pair.partnerPath}</code> —{" "}
            <Link to={`/file/${encodeURIComponent(pair.partnerPath)}`}>open expected path</Link>
          </div>
        ) : null}
      </header>
      <PanelGroup direction="horizontal" autoSaveId="shot-pair-split">
        <Panel defaultSize={50} minSize={20}>
          <ShotPane file={left} label={leftLabel} path={leftPath} knownPaths={knownPaths} onSaved={onSaved} />
        </Panel>
        <PanelResizeHandle className="resize-handle" />
        <Panel defaultSize={50} minSize={20}>
          <ShotPane file={right} label={rightLabel} path={rightPath} knownPaths={knownPaths}
            partnerMissing={!right && partnerMissing} onSaved={onSaved} />
        </Panel>
      </PanelGroup>
    </div>
  );
}

interface ShotPaneProps {
  file: FileResult | null;
  label: string;
  path: string;
  knownPaths: string[];
  partnerMissing?: boolean;
  onSaved?: () => void;
}

function ShotPane({ file, label, path, knownPaths, partnerMissing, onSaved }: ShotPaneProps): JSX.Element {
  const promptBody = useMemo<string | null>(
    () => (file ? extractFirstFencedCode(file.content) : null),
    [file],
  );
  const [editMode, setEditMode] = useState<boolean>(false);
  const [editBuffer, setEditBuffer] = useState<string>("");
  const [editSaving, setEditSaving] = useState<boolean>(false);
  const [editError, setEditError] = useState<string | null>(null);

  const onCopy = async (): Promise<void> => {
    if (!file) return;
    const toCopy = promptBody ?? file.content;
    try {
      if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(toCopy);
      announceCopy(label);
    } catch {
      // clipboard may be unavailable in non-secure contexts
    }
  };

  const onEditStart = (): void => {
    if (!file || promptBody === null) return;
    setEditBuffer(promptBody);
    setEditError(null);
    setEditMode(true);
  };
  const onEditCancel = (): void => {
    setEditMode(false);
    setEditBuffer("");
    setEditError(null);
  };
  const onEditSave = async (newBody?: string): Promise<void> => {
    if (!file || editSaving) return;
    const bodyToWrite = newBody ?? editBuffer;
    setEditSaving(true);
    setEditError(null);
    try {
      const newContent = replaceFirstFencedCode(file.content, bodyToWrite);
      await putFile(path, newContent, { ifUnmodifiedSince: file.mtime_http });
      setEditMode(false);
      setEditBuffer("");
      if (onSaved) onSaved();
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setEditError("文件已被外部修改，请刷新后重试（你的编辑保留在编辑器中）");
      } else if (err instanceof ApiError) {
        setEditError(`保存失败: ${err.detail?.kind ?? err.status}`);
      } else {
        setEditError(`保存失败: ${err instanceof Error ? err.message : String(err)}`);
      }
    } finally {
      setEditSaving(false);
    }
  };

  if (partnerMissing) {
    return (
      <section className="shot-pane shot-pane-missing">
        <header className="shot-pane-header">
          <span className="shot-pane-label">{label}</span>
        </header>
        <div className="muted">
          File not present at <code>{path}</code>.
        </div>
      </section>
    );
  }

  if (!file) {
    return (
      <section className="shot-pane">
        <header className="shot-pane-header"><span className="shot-pane-label">{label}</span></header>
        <div className="muted">Loading…</div>
      </section>
    );
  }

  return (
    <section className={`shot-pane${editMode ? " shot-pane-editing" : ""}`}>
      <header className="shot-pane-header">
        <span className="shot-pane-label">{label}</span>
        <div className="shot-pane-actions">
          {!editMode ? (
            <>
              <button
                type="button"
                className="copy-button"
                onClick={() => void onCopy()}
                aria-label={`复制 ${label} prompt`}
                title={promptBody !== null ? "复制 code block 内的 prompt 内容" : "code block 不存在 — 复制整个文件"}
              >
                {promptBody !== null ? "📋 复制 prompt" : "📋 复制全文"}
              </button>
              {promptBody !== null ? (
                <button
                  type="button"
                  className="copy-button"
                  onClick={onEditStart}
                  title="直接编辑 prompt 代码块内容"
                >
                  ✏ Edit
                </button>
              ) : null}
            </>
          ) : null /* PromptStructuredEditor renders its own Save / Cancel */ }
        </div>
      </header>
      {!editMode ? (
        <ParseFallback rawText={file.content} componentName={`ShotPane:${label}`}>
          <Renderer
            content={file.content}
            currentPath={path}
            knownPaths={knownPaths}
            editEnabled={path.startsWith("ai_videos/")}
            mtimeHttp={file.mtime_http}
            onSaved={onSaved}
          />
        </ParseFallback>
      ) : (
        <div className="shot-pane-edit-wrapper">
          <p className="shot-pane-edit-hint">
            正在编辑 <code>{path.split("/").pop()}</code> 内的第一个 <code>```text</code> 代码块。
            其他段落（frontmatter / Shot context / 起始帧 / 结束帧 / 小说文本）保持不动。
          </p>
          <PromptStructuredEditor
            initialBody={editBuffer}
            onSave={(newBody) => onEditSave(newBody)}
            onCancel={onEditCancel}
            saving={editSaving}
            errorMessage={editError}
            blockLabel={`${label} prompt`}
          />
        </div>
      )}
    </section>
  );
}

function announceCopy(label: string): void {
  const region = document.getElementById("aria-live-toast");
  if (!region) return;
  region.textContent = `${label} prompt 已复制`;
  setTimeout(() => { if (region.textContent?.endsWith("已复制")) region.textContent = ""; }, 2000);
}
