/** SiblingMedia: render images + videos that live in the same folder as the
 * currently-viewed .md file. Per follow-up 005, character / scene / shot folders
 * may contain user-rendered turntable.mp4, ref.png, shot output mp4 etc.
 * This component shows them inline below the markdown so user doesn't have to
 * click each media file separately to preview.
 *
 * Per follow-up 008: each tile gets a per-file Archive / Unarchive button. The
 * archive/ subfolder of the current md folder is also surfaced as an "Archived"
 * subsection so users can unarchive without navigating into archive/.
 *
 * Per follow-up 011: multi-select via always-visible corner checkbox on each
 * tile + per-section toolbar (Select all / Clear / Archive Selected (N) or
 * Unarchive Selected (N)). Batch ops loop the existing per-file endpoints
 * serially with continue-on-error aggregation; per-tile single-file buttons
 * retained for quick single archives.
 */
import { useEffect, useMemo, useState } from "react";
import {
  archiveMedia,
  burnSubtitles,
  extractCharacterViews,
  extractFrames,
  extractScenePlates,
  mediaUrl,
  scaffoldSubtitles,
  unarchiveMedia,
} from "../api";
import { announceToast as announce } from "../lib/announce";
import { ApiError } from "../types";

const VIDEO_EXTS = new Set([".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"]);
const IMAGE_EXTS = new Set([".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"]);
const AUDIO_EXTS = new Set([".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"]);
const MEDIA_EXTS = new Set([...VIDEO_EXTS, ...IMAGE_EXTS, ...AUDIO_EXTS]);
const ARCHIVE_DIR_NAME = "archive";
const RENDERS_DIR_NAME = "renders";

/** Matches `ai_videos/{drama}/characters/c{N}[_{slug}]/{file}.{video_ext}`.
 * Used to gate the 🖼 three-view + audio extraction button so it only
 * appears for character turntable videos (rule #12.5 v9 sources).
 * Mirrors the backend `_CHARACTER_DIR_RE` shape in character_video__writer.py.
 */
const CHARACTER_VIDEO_PATH_RE =
  /^ai_videos\/[^/_][^/]*\/characters\/c\d+(?:_[^/]+)?\/[^/]+\.(?:mp4|mov|webm|mkv|avi|m4v)$/i;

export function isCharacterVideoPath(path: string): boolean {
  return CHARACTER_VIDEO_PATH_RE.test(path);
}

/** Matches a shot render video: `…/shots/shot{NN}/…/{file}.{video_ext}`
 * (the take sits in the shot folder or its `renders/` subfolder). Gates the
 * 📝 生成台词 / 💬 烧录台词 buttons so they only appear on shot videos, where a
 * sibling `subtitles.md` dialogue-timeline makes sense. */
const SHOT_VIDEO_PATH_RE = /\/shots\/shot\d+\//i;

export function isShotVideoPath(path: string): boolean {
  return SHOT_VIDEO_PATH_RE.test(path);
}

/** Matches a scene walk-through video: `…/scenes/{scene}/…`. Gates the
 * 🧭 截取方向背景图 button (extract per-direction bg plates) so it only appears
 * on scene videos, where sibling `bg{N}_{方位}_` direction folders exist. */
const SCENE_VIDEO_PATH_RE = /\/scenes\//i;

export function isSceneVideoPath(path: string): boolean {
  return SCENE_VIDEO_PATH_RE.test(path);
}

export interface SiblingMediaProps {
  currentPath: string;
  knownPaths: string[];
  onChange?: () => void;
}

function extOf(p: string): string {
  const dot = p.lastIndexOf(".");
  return dot < 0 ? "" : p.slice(dot).toLowerCase();
}

function findSiblingMedia(currentPath: string, all: string[]): string[] {
  const lastSlash = currentPath.lastIndexOf("/");
  if (lastSlash < 0) return [];
  const parent = currentPath.slice(0, lastSlash + 1);
  return all
    .filter((p) => {
      if (p === currentPath) return false;
      if (!p.startsWith(parent)) return false;
      const tail = p.slice(parent.length);
      if (tail.includes("/")) return false;
      return MEDIA_EXTS.has(extOf(p));
    })
    .sort();
}

/** Media inside the current folder's `renders/` subfolder — where the import
 * flow drops shot-generated images/videos (start-frame / end-frame / video),
 * keeping their original names. Immediate children only. */
function findRendersMedia(currentPath: string, all: string[]): string[] {
  const lastSlash = currentPath.lastIndexOf("/");
  if (lastSlash < 0) return [];
  const rendersPrefix = `${currentPath.slice(0, lastSlash + 1)}${RENDERS_DIR_NAME}/`;
  return all
    .filter((p) => {
      if (!p.startsWith(rendersPrefix)) return false;
      const tail = p.slice(rendersPrefix.length);
      if (tail.includes("/")) return false;
      return MEDIA_EXTS.has(extOf(p));
    })
    .sort();
}

function findArchivedMedia(currentPath: string, all: string[]): string[] {
  const lastSlash = currentPath.lastIndexOf("/");
  if (lastSlash < 0) return [];
  const archivePrefix = `${currentPath.slice(0, lastSlash + 1)}${ARCHIVE_DIR_NAME}/`;
  return all
    .filter((p) => {
      if (!p.startsWith(archivePrefix)) return false;
      const tail = p.slice(archivePrefix.length);
      if (tail.includes("/")) return false;
      return MEDIA_EXTS.has(extOf(p));
    })
    .sort();
}

function basename(path: string): string {
  return path.split("/").pop() ?? path;
}

function errorKind(err: unknown): string {
  if (err instanceof ApiError) {
    return err.detail?.kind ?? `HTTP ${err.status}`;
  }
  if (err instanceof Error) return err.message;
  return "unknown_error";
}

interface MediaTileProps {
  path: string;
  archived: boolean;
  busy: boolean;
  extracting: boolean;
  extractingViews: boolean;
  extractingPlates: boolean;
  burning: boolean;
  scaffolding: boolean;
  selected: boolean;
  selectionBusy: boolean;
  onToggleSelect: (path: string) => void;
  onArchive: (path: string) => void;
  onUnarchive: (path: string) => void;
  onExtractFrames: (path: string) => void;
  onExtractScenePlates: (path: string) => void;
  onExtractCharacterViews: (path: string) => void;
  onBurnSubtitles: (path: string) => void;
  onScaffoldSubtitles: (path: string) => void;
}

function MediaTile({
  path,
  archived,
  busy,
  extracting,
  extractingViews,
  extractingPlates,
  burning,
  scaffolding,
  selected,
  selectionBusy,
  onToggleSelect,
  onArchive,
  onUnarchive,
  onExtractFrames,
  onExtractScenePlates,
  onExtractCharacterViews,
  onBurnSubtitles,
  onScaffoldSubtitles,
}: MediaTileProps): JSX.Element {
  const ext = extOf(path);
  const isVideo = VIDEO_EXTS.has(ext);
  const isAudio = AUDIO_EXTS.has(ext);
  const isCharacterVideo = isVideo && isCharacterVideoPath(path);
  const isShotVideo = isVideo && isShotVideoPath(path);
  const isSceneVideo = isVideo && isSceneVideoPath(path);
  const filename = basename(path);
  const url = mediaUrl(path);
  const handleClick = (): void => {
    if (busy) return;
    if (archived) onUnarchive(path);
    else onArchive(path);
  };
  const className = [
    "sibling-media-item",
    archived ? "is-archived" : "",
    selected ? "is-selected" : "",
  ]
    .filter(Boolean)
    .join(" ");
  return (
    <figure className={className}>
      <input
        type="checkbox"
        className="tile-checkbox"
        checked={selected}
        disabled={selectionBusy}
        onChange={() => onToggleSelect(path)}
        onClick={(e) => e.stopPropagation()}
        aria-label={`Select ${filename}`}
      />
      {isVideo ? (
        <video controls preload="metadata" src={url} />
      ) : isAudio ? (
        <audio controls preload="metadata" src={url} />
      ) : (
        <img src={url} alt={filename} loading="lazy" />
      )}
      <figcaption>
        {archived ? "📦 " : ""}
        {filename}
      </figcaption>
      <div className="sibling-media-actions">
        {isVideo && !archived ? (
          <button
            type="button"
            className="sibling-media-extract-btn"
            onClick={() => onExtractFrames(path)}
            disabled={busy || extracting}
            aria-label={`Extract 5 reference frames from ${filename}`}
            title="Extract 5 canonical reference frames (hero / reverse / vert / mid / detail) into ./frames/ — overwrites previous extraction from this scene folder"
          >
            {extracting ? "⏳ Extracting…" : "🎞 Extract Frames"}
          </button>
        ) : null}
        {isSceneVideo && !archived ? (
          <button
            type="button"
            className="sibling-media-extract-btn"
            onClick={() => onExtractScenePlates(path)}
            disabled={busy || extractingPlates}
            aria-label={`截取各方向场景背景图 from ${filename}`}
            title="按方位时间点(北1.5s/东4.5s/南7.5s/西10.5s/中13.5s)截帧，生成到各 bg{N}_{方位}_ 文件夹作 shot 背景板——视频朝向须与这些时间点一致"
          >
            {extractingPlates ? "⏳ 截取中…" : "🧭 截取方向背景图"}
          </button>
        ) : null}
        {isShotVideo && !archived ? (
          <button
            type="button"
            className="sibling-media-scaffold-btn"
            onClick={() => onScaffoldSubtitles(path)}
            disabled={busy || scaffolding}
            aria-label={`Scaffold subtitles.md for ${filename}`}
            title="在本 shot 文件夹生成 subtitles.md 台词时间轴 (从 shot.md 的台词+时长均分初值)，编辑后再点「烧录台词」"
          >
            {scaffolding ? "⏳ 生成中…" : "📝 生成台词"}
          </button>
        ) : null}
        {isShotVideo && !archived ? (
          <button
            type="button"
            className="sibling-media-burn-btn"
            onClick={() => onBurnSubtitles(path)}
            disabled={busy || burning}
            aria-label={`Burn subtitles into ${filename}`}
            title="把同 shot 文件夹 subtitles.md 的台词按时间烧进视频，生成 *_subtitled.mp4 (原视频保留)"
          >
            {burning ? "⏳ 烧录中…" : "💬 烧录台词"}
          </button>
        ) : null}
        {isCharacterVideo && !archived ? (
          <button
            type="button"
            className="sibling-media-views-btn"
            onClick={() => onExtractCharacterViews(path)}
            disabled={busy || extractingViews}
            aria-label={`Extract 3 views and audio from ${filename}`}
            title="提取三视图 (front / side / back) + 音频 (.mp3) 到 ./views/ — 适用于 v9 character turntable (15s slow-orbit)"
          >
            {extractingViews ? "⏳ 提取中…" : "🖼 提取三视图+音频"}
          </button>
        ) : null}
        <button
          type="button"
          className="sibling-media-archive-btn"
          onClick={handleClick}
          disabled={busy}
          aria-label={archived ? `Unarchive ${filename}` : `Archive ${filename}`}
          title={archived ? "Move back to parent folder" : "Move to archive/ subfolder"}
        >
          {archived ? "↺ Unarchive" : "📦 Archive"}
        </button>
      </div>
    </figure>
  );
}

interface ToolbarProps {
  total: number;
  selectedCount: number;
  busy: boolean;
  archived: boolean;
  onSelectAll: () => void;
  onClear: () => void;
  onBatch: () => void;
}

function Toolbar({
  total,
  selectedCount,
  busy,
  archived,
  onSelectAll,
  onClear,
  onBatch,
}: ToolbarProps): JSX.Element {
  const allSelected = selectedCount > 0 && selectedCount === total;
  const actionLabel = archived
    ? `↺ Unarchive Selected (${selectedCount})`
    : `📦 Archive Selected (${selectedCount})`;
  const actionAria = archived
    ? `Unarchive ${selectedCount} selected files`
    : `Archive ${selectedCount} selected files`;
  return (
    <div className="sibling-media-toolbar" role="toolbar">
      <button
        type="button"
        onClick={onSelectAll}
        disabled={busy || allSelected || total === 0}
        aria-label="Select all media in this section"
      >
        Select all
      </button>
      <button
        type="button"
        onClick={onClear}
        disabled={busy || selectedCount === 0}
        aria-label="Clear selection"
      >
        Clear
      </button>
      <button
        type="button"
        className="sibling-media-toolbar-primary"
        onClick={onBatch}
        disabled={busy || selectedCount === 0}
        aria-label={actionAria}
      >
        {actionLabel}
      </button>
    </div>
  );
}

export function SiblingMedia({ currentPath, knownPaths, onChange }: SiblingMediaProps): JSX.Element | null {
  const siblings = useMemo(() => findSiblingMedia(currentPath, knownPaths), [currentPath, knownPaths]);
  const renders = useMemo(() => findRendersMedia(currentPath, knownPaths), [currentPath, knownPaths]);
  const archived = useMemo(() => findArchivedMedia(currentPath, knownPaths), [currentPath, knownPaths]);
  const [busyPath, setBusyPath] = useState<string | null>(null);
  const [busy, setBusy] = useState<boolean>(false);
  const [extractingPath, setExtractingPath] = useState<string | null>(null);
  const [extractingViewsPath, setExtractingViewsPath] = useState<string | null>(null);
  const [extractingPlatesPath, setExtractingPlatesPath] = useState<string | null>(null);
  const [burningPath, setBurningPath] = useState<string | null>(null);
  const [scaffoldingPath, setScaffoldingPath] = useState<string | null>(null);
  const [selectedActive, setSelectedActive] = useState<Set<string>>(() => new Set());
  const [selectedRenders, setSelectedRenders] = useState<Set<string>>(() => new Set());
  const [selectedArchived, setSelectedArchived] = useState<Set<string>>(() => new Set());

  // Drop selected paths that no longer exist in the lists after a tree refresh
  // (e.g., archive op moved them across sections — old paths become stale).
  useEffect(() => {
    setSelectedActive((prev) => prune(prev, siblings));
  }, [siblings]);
  useEffect(() => {
    setSelectedRenders((prev) => prune(prev, renders));
  }, [renders]);
  useEffect(() => {
    setSelectedArchived((prev) => prune(prev, archived));
  }, [archived]);

  if (siblings.length === 0 && renders.length === 0 && archived.length === 0) return null;

  const handleArchive = async (path: string): Promise<void> => {
    setBusyPath(path);
    try {
      await archiveMedia(path);
      announce(`Archived ${basename(path)}`);
      onChange?.();
    } catch (err) {
      announce(`Archive failed: ${errorKind(err)}`);
    } finally {
      setBusyPath(null);
    }
  };

  const handleUnarchive = async (path: string): Promise<void> => {
    setBusyPath(path);
    try {
      await unarchiveMedia(path);
      announce(`Unarchived ${basename(path)}`);
      onChange?.();
    } catch (err) {
      announce(`Unarchive failed: ${errorKind(err)}`);
    } finally {
      setBusyPath(null);
    }
  };

  const handleExtractFrames = async (path: string): Promise<void> => {
    setExtractingPath(path);
    try {
      const result = await extractFrames(path);
      const okCount = result.frames.length;
      const failCount = result.failures.length;
      const noun = okCount === 1 ? "frame" : "frames";
      const summary =
        failCount === 0
          ? `Extracted ${okCount} ${noun} from ${basename(path)} → frames/`
          : `Extracted ${okCount} ${noun} from ${basename(path)} (${failCount} failed)`;
      announce(summary);
      onChange?.();
    } catch (err) {
      announce(`Extract frames failed: ${errorKind(err)}`);
    } finally {
      setExtractingPath(null);
    }
  };

  const handleExtractScenePlates = async (path: string): Promise<void> => {
    setExtractingPlatesPath(path);
    try {
      const result = await extractScenePlates(path);
      const okCount = result.plates.length;
      const dirs = result.plates.map((p) => p.direction).join("/");
      const failCount = result.failures.length;
      const summary =
        failCount === 0
          ? `已截取 ${okCount} 张方向背景图（${dirs}）→ 各 bg 文件夹`
          : `已截取 ${okCount} 张（${dirs}），${failCount} 张失败`;
      announce(summary);
      onChange?.();
    } catch (err) {
      announce(`截取方向背景图失败: ${errorKind(err)}`);
    } finally {
      setExtractingPlatesPath(null);
    }
  };

  const handleExtractCharacterViews = async (path: string): Promise<void> => {
    setExtractingViewsPath(path);
    try {
      const result = await extractCharacterViews(path);
      const viewCount = result.views.length;
      const hasAudio = result.audio !== null;
      const failCount = result.failures.length;
      const audioSuffix = hasAudio ? " + 音频" : "";
      const summary =
        failCount === 0
          ? `Extracted ${viewCount} 视图${audioSuffix} from ${basename(path)} → views/`
          : `Extracted ${viewCount} 视图${audioSuffix} from ${basename(path)} (${failCount} failed)`;
      announce(summary);
      onChange?.();
    } catch (err) {
      announce(`Extract views failed: ${errorKind(err)}`);
    } finally {
      setExtractingViewsPath(null);
    }
  };

  const handleScaffoldSubtitles = async (path: string): Promise<void> => {
    setScaffoldingPath(path);
    try {
      const result = await scaffoldSubtitles(path);
      announce(`已生成 ${basename(result.path)} (${result.cues} 句初值，请编辑时间轴)`);
      onChange?.();
    } catch (err) {
      const kind = errorKind(err);
      const hint =
        kind === "subtitles_already_exist"
          ? "subtitles.md 已存在，请直接编辑它"
          : kind;
      announce(`生成台词失败: ${hint}`);
    } finally {
      setScaffoldingPath(null);
    }
  };

  const handleBurnSubtitles = async (path: string): Promise<void> => {
    setBurningPath(path);
    try {
      const result = await burnSubtitles(path);
      announce(`已生成 ${basename(result.out)} (${result.cues} 句字幕)`);
      onChange?.();
    } catch (err) {
      const kind = errorKind(err);
      const hint =
        kind === "subtitle_file_missing"
          ? "未找到 subtitles.md — 请先点「📝 生成台词」或手写后再烧录"
          : kind === "empty_subtitles"
            ? "subtitles.md 无可解析台词行"
            : kind;
      announce(`烧录台词失败: ${hint}`);
    } finally {
      setBurningPath(null);
    }
  };

  const toggleActive = (path: string): void => {
    setSelectedActive((prev) => toggle(prev, path));
  };
  const toggleRendersSel = (path: string): void => {
    setSelectedRenders((prev) => toggle(prev, path));
  };
  const toggleArchivedSel = (path: string): void => {
    setSelectedArchived((prev) => toggle(prev, path));
  };

  const handleBatchArchiveRenders = async (): Promise<void> => {
    const paths = renders.filter((p) => selectedRenders.has(p));
    if (paths.length === 0) return;
    setBusy(true);
    const successes: string[] = [];
    const failures: { name: string; kind: string }[] = [];
    for (const p of paths) {
      try {
        await archiveMedia(p);
        successes.push(p);
      } catch (err) {
        failures.push({ name: basename(p), kind: errorKind(err) });
      }
    }
    setSelectedRenders(new Set());
    setBusy(false);
    onChange?.();
    announce(buildBatchAnnounce("Archived", successes.length, failures));
  };

  const handleBatchArchive = async (): Promise<void> => {
    const paths = siblings.filter((p) => selectedActive.has(p));
    if (paths.length === 0) return;
    setBusy(true);
    const successes: string[] = [];
    const failures: { name: string; kind: string }[] = [];
    for (const p of paths) {
      try {
        await archiveMedia(p);
        successes.push(p);
      } catch (err) {
        failures.push({ name: basename(p), kind: errorKind(err) });
      }
    }
    setSelectedActive(new Set());
    setBusy(false);
    onChange?.();
    announce(buildBatchAnnounce("Archived", successes.length, failures));
  };

  const handleBatchUnarchive = async (): Promise<void> => {
    const paths = archived.filter((p) => selectedArchived.has(p));
    if (paths.length === 0) return;
    setBusy(true);
    const successes: string[] = [];
    const failures: { name: string; kind: string }[] = [];
    for (const p of paths) {
      try {
        await unarchiveMedia(p);
        successes.push(p);
      } catch (err) {
        failures.push({ name: basename(p), kind: errorKind(err) });
      }
    }
    setSelectedArchived(new Set());
    setBusy(false);
    onChange?.();
    announce(buildBatchAnnounce("Unarchived", successes.length, failures));
  };

  return (
    <section className="sibling-media-grid" aria-label="Sibling media in folder">
      {renders.length > 0 ? (
        <>
          <h3>🎬 Renders · 生成产物 (renders/)</h3>
          <Toolbar
            total={renders.length}
            selectedCount={selectedRenders.size}
            busy={busy}
            archived={false}
            onSelectAll={() => setSelectedRenders(new Set(renders))}
            onClear={() => setSelectedRenders(new Set())}
            onBatch={handleBatchArchiveRenders}
          />
          <div className="sibling-media-row">
            {renders.map((p) => (
              <MediaTile
                key={p}
                path={p}
                archived={false}
                busy={busy || busyPath === p}
                extracting={extractingPath === p}
                extractingViews={extractingViewsPath === p}
                extractingPlates={extractingPlatesPath === p}
                burning={burningPath === p}
                scaffolding={scaffoldingPath === p}
                selected={selectedRenders.has(p)}
                selectionBusy={busy}
                onToggleSelect={toggleRendersSel}
                onArchive={handleArchive}
                onUnarchive={handleUnarchive}
                onExtractFrames={handleExtractFrames}
                onExtractScenePlates={handleExtractScenePlates}
                onExtractCharacterViews={handleExtractCharacterViews}
                onBurnSubtitles={handleBurnSubtitles}
                onScaffoldSubtitles={handleScaffoldSubtitles}
              />
            ))}
          </div>
        </>
      ) : null}
      {siblings.length > 0 ? (
        <>
          <h3>📁 Folder media · 同 folder 媒体</h3>
          <Toolbar
            total={siblings.length}
            selectedCount={selectedActive.size}
            busy={busy}
            archived={false}
            onSelectAll={() => setSelectedActive(new Set(siblings))}
            onClear={() => setSelectedActive(new Set())}
            onBatch={handleBatchArchive}
          />
          <div className="sibling-media-row">
            {siblings.map((p) => (
              <MediaTile
                key={p}
                path={p}
                archived={false}
                busy={busy || busyPath === p}
                extracting={extractingPath === p}
                extractingViews={extractingViewsPath === p}
                extractingPlates={extractingPlatesPath === p}
                burning={burningPath === p}
                scaffolding={scaffoldingPath === p}
                selected={selectedActive.has(p)}
                selectionBusy={busy}
                onToggleSelect={toggleActive}
                onArchive={handleArchive}
                onUnarchive={handleUnarchive}
                onExtractFrames={handleExtractFrames}
                onExtractScenePlates={handleExtractScenePlates}
                onExtractCharacterViews={handleExtractCharacterViews}
                onBurnSubtitles={handleBurnSubtitles}
                onScaffoldSubtitles={handleScaffoldSubtitles}
              />
            ))}
          </div>
        </>
      ) : null}
      {archived.length > 0 ? (
        <>
          <h3>📦 Archived · 已归档</h3>
          <Toolbar
            total={archived.length}
            selectedCount={selectedArchived.size}
            busy={busy}
            archived
            onSelectAll={() => setSelectedArchived(new Set(archived))}
            onClear={() => setSelectedArchived(new Set())}
            onBatch={handleBatchUnarchive}
          />
          <div className="sibling-media-row sibling-media-archived">
            {archived.map((p) => (
              <MediaTile
                key={p}
                path={p}
                archived
                busy={busy || busyPath === p}
                extracting={extractingPath === p}
                extractingViews={extractingViewsPath === p}
                extractingPlates={extractingPlatesPath === p}
                burning={burningPath === p}
                scaffolding={scaffoldingPath === p}
                selected={selectedArchived.has(p)}
                selectionBusy={busy}
                onToggleSelect={toggleArchivedSel}
                onArchive={handleArchive}
                onUnarchive={handleUnarchive}
                onExtractFrames={handleExtractFrames}
                onExtractScenePlates={handleExtractScenePlates}
                onExtractCharacterViews={handleExtractCharacterViews}
                onBurnSubtitles={handleBurnSubtitles}
                onScaffoldSubtitles={handleScaffoldSubtitles}
              />
            ))}
          </div>
        </>
      ) : null}
    </section>
  );
}

function toggle(prev: Set<string>, path: string): Set<string> {
  const next = new Set(prev);
  if (next.has(path)) next.delete(path);
  else next.add(path);
  return next;
}

function prune(prev: Set<string>, current: string[]): Set<string> {
  const valid = new Set(current);
  let dirty = false;
  const next = new Set<string>();
  for (const p of prev) {
    if (valid.has(p)) next.add(p);
    else dirty = true;
  }
  return dirty ? next : prev;
}

function buildBatchAnnounce(
  verb: string,
  okCount: number,
  failures: { name: string; kind: string }[],
): string {
  const parts: string[] = [];
  if (okCount > 0) parts.push(`${verb} ${okCount} file${okCount === 1 ? "" : "s"}`);
  if (failures.length > 0) {
    const detail = failures.map((f) => `${f.name} (${f.kind})`).join(", ");
    parts.push(`failed ${failures.length}: ${detail}`);
  }
  if (parts.length === 0) return `${verb}: no files selected`;
  return parts.join("; ");
}
