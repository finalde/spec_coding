/** SiblingMedia: render images + videos that live in the same folder as the
 * currently-viewed .md file. Per follow-up 005, character / scene / shot folders
 * may contain user-rendered turntable.mp4, ref.png, shot output mp4 etc.
 * This component shows them inline below the markdown so user doesn't have to
 * click each media file separately to preview.
 *
 * Per follow-up 008: each tile gets a per-file Archive / Unarchive button. The
 * archive/ subfolder of the current md folder is also surfaced as an "Archived"
 * subsection so users can unarchive without navigating into archive/.
 */
import { useMemo, useState } from "react";
import { archiveMedia, mediaUrl, unarchiveMedia } from "../api";
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

interface MediaTileProps {
  path: string;
  archived: boolean;
  busy: boolean;
  onArchive: (path: string) => void;
  onUnarchive: (path: string) => void;
}

function MediaTile({ path, archived, busy, onArchive, onUnarchive }: MediaTileProps): JSX.Element {
  const ext = extOf(path);
  const isVideo = VIDEO_EXTS.has(ext);
  const filename = path.split("/").pop() ?? path;
  const url = mediaUrl(path);
  const handleClick = (): void => {
    if (busy) return;
    if (archived) onUnarchive(path);
    else onArchive(path);
  };
  return (
    <figure className={archived ? "sibling-media-item is-archived" : "sibling-media-item"}>
      {isVideo ? (
        <video controls preload="metadata" src={url} />
      ) : (
        <img src={url} alt={filename} loading="lazy" />
      )}
      <figcaption>
        {archived ? "📦 " : ""}
        {filename}
      </figcaption>
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
    </figure>
  );
}

export function SiblingMedia({ currentPath, knownPaths, onChange }: SiblingMediaProps): JSX.Element | null {
  const siblings = useMemo(() => findSiblingMedia(currentPath, knownPaths), [currentPath, knownPaths]);
  const archived = useMemo(() => findArchivedMedia(currentPath, knownPaths), [currentPath, knownPaths]);
  const [busyPath, setBusyPath] = useState<string | null>(null);

  if (siblings.length === 0 && archived.length === 0) return null;

  const handleArchive = async (path: string): Promise<void> => {
    setBusyPath(path);
    try {
      await archiveMedia(path);
      announce(`Archived ${path.split("/").pop() ?? path}`);
      onChange?.();
    } catch (err) {
      announce(formatError("Archive failed", err));
    } finally {
      setBusyPath(null);
    }
  };

  const handleUnarchive = async (path: string): Promise<void> => {
    setBusyPath(path);
    try {
      await unarchiveMedia(path);
      announce(`Unarchived ${path.split("/").pop() ?? path}`);
      onChange?.();
    } catch (err) {
      announce(formatError("Unarchive failed", err));
    } finally {
      setBusyPath(null);
    }
  };

  return (
    <section className="sibling-media-grid" aria-label="Sibling media in folder">
      {siblings.length > 0 ? (
        <>
          <h3>📁 Folder media · 同 folder 媒体</h3>
          <div className="sibling-media-row">
            {siblings.map((p) => (
              <MediaTile
                key={p}
                path={p}
                archived={false}
                busy={busyPath === p}
                onArchive={handleArchive}
                onUnarchive={handleUnarchive}
              />
            ))}
          </div>
        </>
      ) : null}
      {archived.length > 0 ? (
        <>
          <h3>📦 Archived · 已归档</h3>
          <div className="sibling-media-row sibling-media-archived">
            {archived.map((p) => (
              <MediaTile
                key={p}
                path={p}
                archived
                busy={busyPath === p}
                onArchive={handleArchive}
                onUnarchive={handleUnarchive}
              />
            ))}
          </div>
        </>
      ) : null}
    </section>
  );
}

function formatError(prefix: string, err: unknown): string {
  if (err instanceof ApiError) {
    const kind = err.detail?.kind ?? `HTTP ${err.status}`;
    return `${prefix}: ${kind}`;
  }
  if (err instanceof Error) return `${prefix}: ${err.message}`;
  return `${prefix}: unknown error`;
}
