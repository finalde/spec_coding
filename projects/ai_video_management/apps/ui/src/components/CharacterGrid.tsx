/** CharacterGrid: a per-drama character gallery.
 *
 * Per 2026-06-27 follow-up「给我一个 character 的主页面，看到所有 character 的缩略图 +
 * 一键重新生成所有 character 的三视图和前2s」. Data is derived from the `tree`
 * prop (no backend list endpoint): walk the selected drama's
 * `2_世界观人设/characters/cN_*` folders, show each one's portrait png as a
 * thumbnail, and offer a single button that calls POST
 * /api/extract-all-character-views to regenerate every character's
 * 3 views + audio + 2s trim from its newest turntable mp4.
 */
import { useCallback, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { extractAllCharacterViews, mediaUrl } from "../api";
import { extractDramas, findAssetDir, type DramaChoice } from "../lib/dramas";
import { announceToast } from "../lib/announce";
import { ApiError, type TreeNode } from "../types";

const IMAGE_EXTS = [".png", ".jpg", ".jpeg", ".webp"];
const VIDEO_EXTS = [".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"];
const CHAR_DIR_RE = /^c\d+(?:_.*)?$/;

interface CharacterTile {
  folder: string; // e.g. "c1_裴知秋"
  mdPath: string; // the character bible md
  thumbPath: string | null; // portrait image to show
  hasVideo: boolean; // a turntable mp4 exists in the folder
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
    const hasVideo = files.some((f) => VIDEO_EXTS.includes(extOf(f.path)));
    tiles.push({
      folder: folder.name,
      mdPath: `${folder.path}/${folder.name}.md`,
      thumbPath: portrait ? portrait.path : null,
      hasVideo,
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

  const onRegenAll = useCallback(async () => {
    if (!charsDirPath || busy) return;
    setBusy(true);
    try {
      const result = await extractAllCharacterViews(charsDirPath);
      const ok = result.items.filter((i) => i.status === "ok").length;
      const skipped = result.items.filter((i) => i.status === "skipped").length;
      const failed = result.items.filter((i) => i.status === "error").length;
      announceToast(`重生完成：${ok} 成功 / ${skipped} 跳过(无视频) / ${failed} 失败`);
      onChange();
    } catch (err) {
      const kind = err instanceof ApiError ? (err.detail?.kind ?? `HTTP ${err.status}`) : String(err);
      announceToast(`一键重生失败：${kind}`);
    } finally {
      setBusy(false);
    }
  }, [charsDirPath, busy, onChange]);

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

  const withVideo = tiles.filter((t) => t.hasVideo).length;

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
          {tiles.map((t) => (
            <button
              key={t.folder}
              type="button"
              className="actor-tile"
              onClick={() => navigate(`/file/${encodeURIComponent(t.mdPath)}`)}
              title={`打开 ${t.folder} 人物卡`}
            >
              {t.thumbPath ? (
                <img src={mediaUrl(t.thumbPath)} alt={t.folder} loading="lazy" />
              ) : (
                <div className="actor-tile-noimg">无立绘</div>
              )}
              <div className="actor-tile-label">
                {t.folder}
                {!t.hasVideo && <span className="character-tile-novideo"> · 无视频</span>}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
