/** SiblingMedia: render images + videos that live in the same folder as the
 * currently-viewed .md file. Per follow-up 005, character / scene / shot folders
 * may contain user-rendered turntable.mp4, ref.png, shot output mp4 etc.
 * This component shows them inline below the markdown so user doesn't have to
 * click each media file separately to preview.
 */
import { useMemo } from "react";
import { mediaUrl } from "../api";

const VIDEO_EXTS = new Set([".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"]);
const IMAGE_EXTS = new Set([".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"]);
const MEDIA_EXTS = new Set([...VIDEO_EXTS, ...IMAGE_EXTS]);

export interface SiblingMediaProps {
  currentPath: string;
  knownPaths: string[];
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

export function SiblingMedia({ currentPath, knownPaths }: SiblingMediaProps): JSX.Element | null {
  const siblings = useMemo(() => findSiblingMedia(currentPath, knownPaths), [currentPath, knownPaths]);
  if (siblings.length === 0) return null;
  return (
    <section className="sibling-media-grid" aria-label="Sibling media in folder">
      <h3>📁 Folder media · 同 folder 媒体</h3>
      <div className="sibling-media-row">
        {siblings.map((p) => {
          const ext = extOf(p);
          const isVideo = VIDEO_EXTS.has(ext);
          const filename = p.split("/").pop() ?? p;
          const url = mediaUrl(p);
          return (
            <figure key={p} className="sibling-media-item">
              {isVideo ? (
                <video controls preload="metadata" src={url} />
              ) : (
                <img src={url} alt={filename} loading="lazy" />
              )}
              <figcaption>{filename}</figcaption>
            </figure>
          );
        })}
      </div>
    </section>
  );
}
