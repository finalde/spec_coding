/** Reader: render-mode dispatch by file extension + path pattern. */
import { useCallback, useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Breadcrumb } from "./Breadcrumb";
import { ParseFallback } from "./ParseFallback";
import { Editor } from "./Editor";
import { ShotPairView } from "./ShotPairView";
import { ShotlistTableView } from "./ShotlistTableView";
import { ImageRefView } from "./ImageRefView";
import { CastingView } from "./CastingView";
import { ActorView } from "./ActorView";
import { Renderer } from "../markdown/renderer";
import { CodeView } from "../markdown/CodeView";
import { JsonlView } from "../markdown/JsonlView";
import { SiblingMedia, isCharacterVideoPath } from "./SiblingMedia";
import { detectShotPair } from "../lib/shotPairing";
import { announceToast } from "../lib/announce";
import {
  archiveMedia,
  concatShotCharacters,
  deleteMedia,
  extractCharacterViews,
  extractFrames,
  fetchFile,
  mediaUrl,
  putFile,
  unarchiveMedia,
} from "../api";
import { ApiError, type FileResult, type TreeNode } from "../types";

const IMAGE_EXTS = new Set([".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"]);
const VIDEO_EXTS = new Set([".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"]);
const AUDIO_EXTS = new Set([".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"]);
const SHOT_MD_RE = /^ai_videos\/[^_][^/]*\/(?:episodes\/ep\d+\/)?prompts\/shot\d+\/shot\d+\.md$/;

export interface ReaderProps {
  tree: TreeNode | null;
  knownPaths: string[];
  onSaved: () => void;
}

export function Reader({ tree, knownPaths, onSaved }: ReaderProps): JSX.Element {
  const location = useLocation();
  const navigate = useNavigate();
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
  const [archiving, setArchiving] = useState<boolean>(false);
  const [deleting, setDeleting] = useState<boolean>(false);
  const [extracting, setExtracting] = useState<boolean>(false);
  const [extractingViews, setExtractingViews] = useState<boolean>(false);
  const [concatBusy, setConcatBusy] = useState<boolean>(false);

  const ext = path ? extOf(path) : "";
  const isMediaImage = IMAGE_EXTS.has(ext);
  const isMediaVideo = VIDEO_EXTS.has(ext);
  const isMediaAudio = AUDIO_EXTS.has(ext);
  const isMediaOnly = isMediaVideo || isMediaImage || isMediaAudio;

  const load = useCallback(async () => {
    if (!path) return;
    if (isMediaOnly) {
      // Media files (video / non-png-jpg images) are streamed via /api/media —
      // skip /api/file fetch entirely (videos can exceed the 1 MB limit).
      setFile({ path, content: "", encoding: "media", bytes: 0, mtime: 0, mtime_http: "" });
      setError(null);
      return;
    }
    try {
      const f = await fetchFile(path);
      setFile(f);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    }
  }, [path, isMediaOnly]);

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

  const onArchiveToggle = useCallback(async () => {
    if (!path) return;
    const parts = path.split("/");
    const inArchive = parts.length >= 2 && parts[parts.length - 2] === "archive";
    setArchiving(true);
    try {
      const result = inArchive ? await unarchiveMedia(path) : await archiveMedia(path);
      announceToast(`${inArchive ? "Unarchived" : "Archived"} ${parts[parts.length - 1] ?? path}`);
      onSaved();
      navigate(`/file/${encodeURIComponent(result.to)}`);
    } catch (err) {
      announceToast(`${inArchive ? "Unarchive" : "Archive"} failed: ${archiveErrorKind(err)}`);
    } finally {
      setArchiving(false);
    }
  }, [path, onSaved, navigate]);

  const onDeleteClick = useCallback(async () => {
    if (!path) return;
    const name = path.split("/").pop() ?? path;
    if (!window.confirm(`Move ${name} to _deleted/?`)) return;
    setDeleting(true);
    try {
      const result = await deleteMedia(path);
      announceToast(`Deleted ${name}`);
      onSaved();
      navigate(`/file/${encodeURIComponent(result.to)}`);
    } catch (err) {
      announceToast(`Delete failed: ${archiveErrorKind(err)}`);
    } finally {
      setDeleting(false);
    }
  }, [path, onSaved, navigate]);

  const onConcatShotCharactersClick = useCallback(async () => {
    if (!path) return;
    setConcatBusy(true);
    try {
      const result = await concatShotCharacters(path);
      const usedNames = result.used.map((u) => u.role || u.character_folder).join(", ");
      const skippedNames = result.skipped.map((s) => `${s.role || s.character_folder} (${s.reason})`).join(", ");
      let summary: string;
      if (result.out) {
        summary = `已合成 ${result.out.split("/").pop()} — 使用 ${result.used.length} 个角色`;
        if (usedNames) summary += ` [${usedNames}]`;
        if (result.skipped.length > 0) summary += ` · 跳过 ${result.skipped.length}: ${skippedNames}`;
      } else {
        summary = `未生成 — 没有角色文件夹包含 mp4`;
        if (result.skipped.length > 0) summary += ` · 跳过 ${result.skipped.length}: ${skippedNames}`;
      }
      announceToast(summary);
      onSaved();
    } catch (err) {
      announceToast(`生成角色合辑失败: ${archiveErrorKind(err)}`);
    } finally {
      setConcatBusy(false);
    }
  }, [path, onSaved]);

  const onExtractFramesClick = useCallback(async () => {
    if (!path) return;
    const name = path.split("/").pop() ?? path;
    setExtracting(true);
    try {
      const result = await extractFrames(path);
      const okCount = result.frames.length;
      const failCount = result.failures.length;
      const noun = okCount === 1 ? "frame" : "frames";
      const summary =
        failCount === 0
          ? `Extracted ${okCount} ${noun} from ${name} → frames/`
          : `Extracted ${okCount} ${noun} from ${name} (${failCount} failed)`;
      announceToast(summary);
      onSaved();
    } catch (err) {
      announceToast(`Extract frames failed: ${archiveErrorKind(err)}`);
    } finally {
      setExtracting(false);
    }
  }, [path, onSaved]);

  const onExtractCharacterViewsClick = useCallback(async () => {
    if (!path) return;
    const name = path.split("/").pop() ?? path;
    setExtractingViews(true);
    try {
      const result = await extractCharacterViews(path);
      const okCount = result.views.length + (result.audio ? 1 : 0);
      const failCount = result.failures.length;
      const summary =
        failCount === 0
          ? `Extracted ${okCount} views + audio from ${name} → views/`
          : `Extracted ${okCount} from ${name} (${failCount} failed)`;
      announceToast(summary);
      onSaved();
    } catch (err) {
      announceToast(`Extract views failed: ${archiveErrorKind(err)}`);
    } finally {
      setExtractingViews(false);
    }
  }, [path, onSaved]);

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

  const isImage = isMediaImage;
  const isVideo = isMediaVideo;
  const isAudio = isMediaAudio;
  const isMarkdown = ext === ".md";
  const isJsonl = ext === ".jsonl";
  const isCode = ext === ".json" || ext === ".yaml" || ext === ".yml";
  const isTxt = ext === ".txt";

  const shotPair = isMarkdown ? detectShotPair(path) : null;
  const isShotPair = shotPair !== null;
  const isShotlistTable = path.startsWith("ai_videos/") && path.endsWith("/shotlist.md");
  const isImageRef = (isMarkdown && /\/ref_images\/[^/]+_seedream\.md$/.test(path));
  const isCasting = isMarkdown && /^ai_videos\/[^/]+\/casting\.md$/.test(path);
  const isActor = isMarkdown && /^ai_videos\/_actors\/actor_[^/]+\/actor_[^/]+\.md$/.test(path);
  const isShotMd = isMarkdown && SHOT_MD_RE.test(path);

  const filename = path.split("/").pop() ?? path;
  const pathParts = path.split("/");
  const isArchivedFile = pathParts.length >= 2 && pathParts[pathParts.length - 2] === "archive";
  const isDeletedFile = path.startsWith("ai_videos/_deleted/");
  const mediaActionsBusy = archiving || deleting || extracting || extractingViews;
  const archiveLabel = isArchivedFile
    ? (archiving ? "Unarchiving…" : "↺ Unarchive")
    : (archiving ? "Archiving…" : "📦 Archive");
  const deleteLabel = deleting ? "Deleting…" : "🗑 Delete";
  const extractLabel = extracting ? "⏳ Extracting…" : "🎞 Extract Frames";
  const viewsExtractLabel = extractingViews ? "⏳ 提取中…" : "🖼 提取三视图+音频";
  const showViewsBtn = isVideo && !isArchivedFile && !isDeletedFile && isCharacterVideoPath(path);

  return (
    <div className="reader">
      <div className="reader-toolbar" role="toolbar" aria-label="File toolbar">
        <Breadcrumb
          path={path}
          knownPaths={knownPaths}
          onNavigate={(target) => navigate(`/file/${encodeURIComponent(target)}`)}
        />
        {isShotMd ? (
          <button type="button" className="reader-shot-concat-btn"
            onClick={onConcatShotCharactersClick} disabled={concatBusy}
            aria-label="Build a character reel by concatenating the first mp4 found in each involved character's folder"
            title="Parse the 出场角色 table, take the alphabetically-first mp4 inside each character folder (skipping only folders that have no mp4), trim each to 2s, and ffmpeg-concat them into <shotNN>_chars.mp4 next to this shot md.">
            {concatBusy ? "⏳ 生成中…" : "🎬 生成角色合辑"}
          </button>
        ) : null}
        {!isImage && !isVideo && !isAudio ? (
          <button type="button" className="reader-edit-toggle"
            onClick={() => setEditing((e) => !e)}
            aria-label={editing ? "Stop editing" : "Edit file"} aria-pressed={editing}>
            ✎ {editing ? "Editing" : "Edit"}
          </button>
        ) : null}
      </div>
      {editing && !isImage && !isVideo && !isAudio && !isShotPair && !isImageRef && !isCasting && !isActor ? (
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
          {isVideo ? (
            <div className="media-view">
              <video controls preload="metadata" src={mediaUrl(path)} />
              {!isDeletedFile ? (
                <div className="reader-media-actions">
                  {!isArchivedFile ? (
                    <button type="button" className="reader-media-extract-btn"
                      onClick={onExtractFramesClick} disabled={mediaActionsBusy}
                      aria-label={`Extract 5 reference frames from ${filename}`}
                      title="Extract 5 canonical reference frames (hero / reverse / vert / mid / detail) into ./frames/ — overwrites previous extraction from this scene folder">
                      {extractLabel}
                    </button>
                  ) : null}
                  {showViewsBtn ? (
                    <button type="button" className="reader-media-views-btn"
                      onClick={onExtractCharacterViewsClick} disabled={mediaActionsBusy}
                      aria-label={`Extract 3 views and audio from ${filename}`}
                      title="提取三视图 (front / side / back) + 音频 (.mp3) 到 ./views/ — 适用于 v10 character turntable (7s locked-framing + 180° slow orbit)">
                      {viewsExtractLabel}
                    </button>
                  ) : null}
                  <button type="button" className="reader-media-archive-btn"
                    onClick={onArchiveToggle} disabled={mediaActionsBusy}
                    aria-label={isArchivedFile ? `Unarchive ${filename}` : `Archive ${filename}`}>
                    {archiveLabel}
                  </button>
                  <button type="button" className="reader-media-delete-btn"
                    onClick={onDeleteClick} disabled={mediaActionsBusy}
                    aria-label={`Delete ${filename}`}>
                    {deleteLabel}
                  </button>
                </div>
              ) : null}
            </div>
          ) : isMediaImage ? (
            <div className="media-view">
              <img src={mediaUrl(path)} alt={filename} />
              {!isDeletedFile ? (
                <div className="reader-media-actions">
                  <button type="button" className="reader-media-archive-btn"
                    onClick={onArchiveToggle} disabled={mediaActionsBusy}
                    aria-label={isArchivedFile ? `Unarchive ${filename}` : `Archive ${filename}`}>
                    {archiveLabel}
                  </button>
                  <button type="button" className="reader-media-delete-btn"
                    onClick={onDeleteClick} disabled={mediaActionsBusy}
                    aria-label={`Delete ${filename}`}>
                    {deleteLabel}
                  </button>
                </div>
              ) : null}
            </div>
          ) : isAudio ? (
            <div className="media-view">
              <audio controls preload="metadata" src={mediaUrl(path)} />
              {!isDeletedFile ? (
                <div className="reader-media-actions">
                  <button type="button" className="reader-media-archive-btn"
                    onClick={onArchiveToggle} disabled={mediaActionsBusy}
                    aria-label={isArchivedFile ? `Unarchive ${filename}` : `Archive ${filename}`}>
                    {archiveLabel}
                  </button>
                  <button type="button" className="reader-media-delete-btn"
                    onClick={onDeleteClick} disabled={mediaActionsBusy}
                    aria-label={`Delete ${filename}`}>
                    {deleteLabel}
                  </button>
                </div>
              ) : null}
            </div>
          ) : isCasting ? (
            <CastingView castingPath={path} onChange={onSaved} />
          ) : isActor ? (
            <ActorView primaryFile={file} primaryPath={path} knownPaths={knownPaths} tree={tree} onSaved={onSaved} />
          ) : isImageRef ? (
            <>
              <ImageRefView primaryFile={file} primaryPath={path} knownPaths={knownPaths} />
              <SiblingMedia currentPath={path} knownPaths={knownPaths} onChange={onSaved} />
            </>
          ) : isShotPair ? (
            <>
              <ShotPairView primaryFile={file} primaryPath={path} knownPaths={knownPaths} />
              <SiblingMedia currentPath={path} knownPaths={knownPaths} onChange={onSaved} />
            </>
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
              <SiblingMedia currentPath={path} knownPaths={knownPaths} onChange={onSaved} />
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

function archiveErrorKind(err: unknown): string {
  if (err instanceof ApiError) return err.detail?.kind ?? `HTTP ${err.status}`;
  if (err instanceof Error) return err.message;
  return "unknown_error";
}
