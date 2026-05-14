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
import { archiveMedia, extractFrames, mediaUrl, unarchiveMedia } from "../api";
import { ApiError } from "../types";

const VIDEO_EXTS = new Set([".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"]);
const IMAGE_EXTS = new Set([".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"]);
const MEDIA_EXTS = new Set([...VIDEO_EXTS, ...IMAGE_EXTS]);
const ARCHIVE_DIR_NAME = "archive";

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

function announce(message: string): void {
  const region = document.getElementById("aria-live-toast");
  if (region) {
    region.textContent = "";
    window.setTimeout(() => {
      region.textContent = message;
    }, 30);
  }
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
  selected: boolean;
  selectionBusy: boolean;
  onToggleSelect: (path: string) => void;
  onArchive: (path: string) => void;
  onUnarchive: (path: string) => void;
  onExtractFrames: (path: string) => void;
}

function MediaTile({
  path,
  archived,
  busy,
  extracting,
  selected,
  selectionBusy,
  onToggleSelect,
  onArchive,
  onUnarchive,
  onExtractFrames,
}: MediaTileProps): JSX.Element {
  const ext = extOf(path);
  const isVideo = VIDEO_EXTS.has(ext);
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
  const archived = useMemo(() => findArchivedMedia(currentPath, knownPaths), [currentPath, knownPaths]);
  const [busyPath, setBusyPath] = useState<string | null>(null);
  const [busy, setBusy] = useState<boolean>(false);
  const [extractingPath, setExtractingPath] = useState<string | null>(null);
  const [selectedActive, setSelectedActive] = useState<Set<string>>(() => new Set());
  const [selectedArchived, setSelectedArchived] = useState<Set<string>>(() => new Set());

  // Drop selected paths that no longer exist in the lists after a tree refresh
  // (e.g., archive op moved them across sections — old paths become stale).
  useEffect(() => {
    setSelectedActive((prev) => prune(prev, siblings));
  }, [siblings]);
  useEffect(() => {
    setSelectedArchived((prev) => prune(prev, archived));
  }, [archived]);

  if (siblings.length === 0 && archived.length === 0) return null;

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

  const toggleActive = (path: string): void => {
    setSelectedActive((prev) => toggle(prev, path));
  };
  const toggleArchivedSel = (path: string): void => {
    setSelectedArchived((prev) => toggle(prev, path));
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
                selected={selectedActive.has(p)}
                selectionBusy={busy}
                onToggleSelect={toggleActive}
                onArchive={handleArchive}
                onUnarchive={handleUnarchive}
                onExtractFrames={handleExtractFrames}
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
                selected={selectedArchived.has(p)}
                selectionBusy={busy}
                onToggleSelect={toggleArchivedSel}
                onArchive={handleArchive}
                onUnarchive={handleUnarchive}
                onExtractFrames={handleExtractFrames}
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
