/** CharacterGrid: a per-drama character gallery.
 *
 * Per 2026-06-27 follow-ups. Data is derived from the `tree` prop (which folders
 * exist + portrait fallback), enriched with each character's NEWEST turntable
 * mp4 from `GET /api/character-videos` (the tree carries no mtime, so the
 * backend picks the latest by timestamp). Each tile defaults to an inline,
 * click-to-play `<video>` of that newest mp4 (portrait png fallback when none),
 * with an action-button row: 详情页 + per-character 重生三视图+前2s. The header
 * keeps the one-click 重生全部 over the whole drama.
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  extractAllCharacterViews,
  extractCharacterViews,
  listCharacterVideos,
  mediaUrl,
} from "../api";
import { extractDramas, findAssetDir, type DramaChoice } from "../lib/dramas";
import { announceToast } from "../lib/announce";
import { ApiError, type TreeNode } from "../types";

const IMAGE_EXTS = [".png", ".jpg", ".jpeg", ".webp"];
const CHAR_DIR_RE = /^c\d+(?:_.*)?$/;

interface CharacterTile {
  folder: string; // e.g. "c1_裴知秋"
  mdPath: string; // the character bible md
  dirPath: string; // the character folder
  thumbPath: string | null; // portrait image (fallback when no video)
}

function extOf(p: string): string {
  const dot = p.lastIndexOf(".");
  return dot < 0 ? "" : p.slice(dot).toLowerCase();
}

function isLeafFile(node: TreeNode): boolean {
  return node.type !== "directory" && node.type !== "section";
}

function findNodeByPath(tree: TreeNode | null, path: string): TreeNode | null {
  if (!tree) return null;
  const queue: TreeNode[] = [tree];
  while (queue.length > 0) {
    const node = queue.shift()!;
    if (node.path === path) return node;
    for (const c of node.children ?? []) queue.push(c);
  }
  return null;
}

function tilesForDrama(tree: TreeNode | null, drama: DramaChoice | null): CharacterTile[] {
  if (!tree || !drama) return [];
  const dramaNode = findNodeByPath(tree, drama.path);
  if (!dramaNode) return [];
  const charsDir = findAssetDir(dramaNode, "characters");
  if (!charsDir) return [];
  const tiles: CharacterTile[] = [];
  for (const folder of charsDir.children ?? []) {
    if (folder.type !== "directory" || !CHAR_DIR_RE.test(folder.name)) continue;
    const files = (folder.children ?? []).filter(isLeafFile);
    const images = files.filter((f) => IMAGE_EXTS.includes(extOf(f.path)));
    // Prefer the portrait named after the folder (cN_xxx.png); else first image.
    const portrait =
      images.find((f) => f.name.startsWith(folder.name)) ?? images[0] ?? null;
    tiles.push({
      folder: folder.name,
      mdPath: `${folder.path}/${folder.name}.md`,
      dirPath: folder.path,
      thumbPath: portrait ? portrait.path : null,
    });
  }
  return tiles;
}

export interface CharacterGridProps {
  tree: TreeNode | null;
  onChange: () => void;
}

export function CharacterGrid({ tree, onChange }: CharacterGridProps): JSX.Element {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const dramas = useMemo<DramaChoice[]>(() => extractDramas(tree), [tree]);
  const [dramaPath, setDramaPath] = useState<string>("");
  const [busy, setBusy] = useState<boolean>(false);
  // folder -> newest turntable mp4 rel path (null = none rendered yet). undefined
  // for the whole map = not loaded yet (degrade to portrait-only).
  const [videos, setVideos] = useState<Record<string, string | null>>({});
  const [regenFolder, setRegenFolder] = useState<string | null>(null);

  // Initial drama comes from the `?drama=` query (set by the sidebar 角色画廊
  // button) when the user hasn't picked one from the dropdown yet.
  const queryDrama = searchParams.get("drama") ?? "";
  const drama = useMemo<DramaChoice | null>(() => {
    if (dramas.length === 0) return null;
    const wanted = dramaPath || queryDrama;
    return dramas.find((d) => d.path === wanted) ?? dramas[0];
  }, [dramas, dramaPath, queryDrama]);

  const charsDirPath = useMemo<string | null>(() => {
    if (!tree || !drama) return null;
    const dramaNode = findNodeByPath(tree, drama.path);
    const charsDir = dramaNode ? findAssetDir(dramaNode, "characters") : null;
    return charsDir ? charsDir.path : null;
  }, [tree, drama]);

  const tiles = useMemo<CharacterTile[]>(() => tilesForDrama(tree, drama), [tree, drama]);

  // Fetch each character's newest turntable mp4 (the tree has no mtime, so the
  // backend picks the latest). Failure degrades silently to portrait-only.
  const [reloadKey, setReloadKey] = useState<number>(0);
  useEffect(() => {
    if (!charsDirPath) {
      setVideos({});
      return;
    }
    let cancelled = false;
    void (async () => {
      try {
        const result = await listCharacterVideos(charsDirPath);
        if (cancelled) return;
        const map: Record<string, string | null> = {};
        for (const item of result.items) map[item.folder] = item.latest_video;
        setVideos(map);
      } catch {
        if (!cancelled) setVideos({});
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [charsDirPath, reloadKey]);

  const onRegenAll = useCallback(async () => {
    if (!charsDirPath || busy) return;
    setBusy(true);
    try {
      const result = await extractAllCharacterViews(charsDirPath);
      const ok = result.items.filter((i) => i.status === "ok").length;
      const skipped = result.items.filter((i) => i.status === "skipped").length;
      const failed = result.items.filter((i) => i.status === "error").length;
      announceToast(`重生完成：${ok} 成功 / ${skipped} 跳过(无视频) / ${failed} 失败`);
      setReloadKey((k) => k + 1);
      onChange();
    } catch (err) {
      const kind = err instanceof ApiError ? (err.detail?.kind ?? `HTTP ${err.status}`) : String(err);
      announceToast(`一键重生失败：${kind}`);
    } finally {
      setBusy(false);
    }
  }, [charsDirPath, busy, onChange]);

  const onRegenOne = useCallback(
    async (folder: string, latestVideo: string | null) => {
      if (!latestVideo || regenFolder !== null) return;
      setRegenFolder(folder);
      try {
        const r = await extractCharacterViews(latestVideo);
        const ok = r.views.length + (r.audio ? 1 : 0) + (r.trim ? 1 : 0);
        announceToast(`${folder}：重生 ${ok} 个文件 → views/`);
        setReloadKey((k) => k + 1);
        onChange();
      } catch (err) {
        const kind = err instanceof ApiError ? (err.detail?.kind ?? `HTTP ${err.status}`) : String(err);
        announceToast(`${folder} 重生失败：${kind}`);
      } finally {
        setRegenFolder(null);
      }
    },
    [regenFolder, onChange],
  );

  if (dramas.length === 0) {
    return (
      <div className="actor-grid-page">
        <div className="actor-grid-header">
          <h1>角色画廊</h1>
        </div>
        <div className="actor-grid-empty">没有找到任何剧集。</div>
      </div>
    );
  }

  const withVideo = tiles.filter((t) => videos[t.folder]).length;

  return (
    <div className="actor-grid-page">
      <div className="actor-grid-header">
        <h1>角色画廊</h1>
        {dramas.length > 1 && (
          <select
            value={drama?.path ?? ""}
            onChange={(e) => setDramaPath(e.target.value)}
            aria-label="选择剧集"
          >
            {dramas.map((d) => (
              <option key={d.path} value={d.path}>
                {d.name}
              </option>
            ))}
          </select>
        )}
        <span className="actor-grid-count">
          {tiles.length} 个角色 · {withVideo} 个已有建立视频
        </span>
        <button
          type="button"
          onClick={onRegenAll}
          disabled={busy || charsDirPath === null}
          title="对本剧每个角色，取其最新的 turntable 原始视频，重新生成 三视图(front/side/back) + 音频 + 前2s trim 到各自 views/。无视频的角色自动跳过。"
        >
          {busy ? "⏳ 重生中…" : "🖼 一键重生全部三视图+前2s"}
        </button>
      </div>
      {tiles.length === 0 ? (
        <div className="actor-grid-empty">本剧 characters/ 下没有角色文件夹。</div>
      ) : (
        <div className="actor-grid">
          {tiles.map((t) => {
            const latestVideo = videos[t.folder] ?? null;
            const regenning = regenFolder === t.folder;
            return (
              <div key={t.folder} className="character-tile">
                <div className="character-tile-media">
                  {latestVideo ? (
                    <video
                      src={mediaUrl(latestVideo)}
                      controls
                      preload="metadata"
                      playsInline
                    />
                  ) : t.thumbPath ? (
                    <img src={mediaUrl(t.thumbPath)} alt={t.folder} loading="lazy" />
                  ) : (
                    <div className="actor-tile-noimg">无立绘</div>
                  )}
                </div>
                <div className="actor-tile-label">
                  {t.folder}
                  {!latestVideo && <span className="character-tile-novideo"> · 无视频</span>}
                </div>
                <div className="character-tile-actions">
                  <button
                    type="button"
                    onClick={() => navigate(`/file/${encodeURIComponent(t.mdPath)}`)}
                    title={`打开 ${t.folder} 人物卡`}
                  >
                    📄 详情页
                  </button>
                  <button
                    type="button"
                    onClick={() => onRegenOne(t.folder, latestVideo)}
                    disabled={!latestVideo || regenFolder !== null}
                    title={
                      latestVideo
                        ? "用该角色最新 turntable 视频重生 三视图+音频+前2s 到 views/"
                        : "该角色还没有 turntable 视频"
                    }
                  >
                    {regenning ? "⏳…" : "🖼 重生三视图+前2s"}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
