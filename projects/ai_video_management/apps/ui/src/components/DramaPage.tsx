/** DramaPage — the drama-level main page (production console).
 *
 * Opened by clicking a drama node in the left nav (→ `/drama?drama={path}`),
 * which now does double duty: it still toggles the nav dropdown AND surfaces
 * this main page on the right. It is the single home for every drama-wide
 * function + display that does not belong to one file:
 *  - 🎬 剧集制作台 (DramaDashboard): 📦 导出 production + 💬 全剧烧字幕.
 *  - 资源管理: 📥 导入 + 重命名, 🎭 角色画廊 (relocated off the left nav).
 *  - 📺 分集总览: every episode with the burned-subtitle masters it carries
 *    (zh / en / 中英) — i.e. exactly what 📦 导出 will copy into production/.
 * New drama-level features land here, not in the left nav. */
import { useCallback, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { importFromDownloads } from "../api";
import { ApiError, type TreeNode } from "../types";
import { announceToast } from "../lib/announce";
import { DramaDashboard } from "./DramaDashboard";

const EP_DIR_RE = /^ep\d+$/i;
const SUB_MASTER_RE = /^ep\d+_(zh|en|zhen)\.mp4$/i;
const LANG_LABEL: Record<string, string> = { zh: "中文", en: "英文", zhen: "中英" };

export interface DramaPageProps {
  tree: TreeNode | null;
  onChange: () => void;
}

interface EpisodeRow {
  name: string;       // ep01
  path: string;
  langs: string[];    // subset of zh | en | zhen present as burned masters
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

/** Collect every `episodes/ep{NN}` folder under the drama (legacy root layout
 *  AND the staged `…/5_6_…/episodes/` layout), with the burned-subtitle
 *  language masters each carries. Mirrors ProductionExporter's tree-walk. */
function collectEpisodes(dramaNode: TreeNode | null): EpisodeRow[] {
  if (!dramaNode) return [];
  const rows: EpisodeRow[] = [];
  const walk = (node: TreeNode): void => {
    if (node.type === "directory" && node.name === "episodes") {
      for (const ep of node.children ?? []) {
        if (ep.type !== "directory" || !EP_DIR_RE.test(ep.name)) continue;
        const langs: string[] = [];
        for (const child of ep.children ?? []) {
          const m = SUB_MASTER_RE.exec(child.name);
          if (m) langs.push(m[1].toLowerCase());
        }
        rows.push({ name: ep.name, path: ep.path, langs });
      }
    }
    for (const c of node.children ?? []) walk(c);
  };
  walk(dramaNode);
  rows.sort((a, b) => a.name.localeCompare(b.name));
  return rows;
}

export function DramaPage({ tree, onChange }: DramaPageProps): JSX.Element {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const dramaPath = searchParams.get("drama") ?? "";
  const [importBusy, setImportBusy] = useState<boolean>(false);

  const dramaNode = useMemo(() => findNodeByPath(tree, dramaPath), [tree, dramaPath]);
  const episodes = useMemo(() => collectEpisodes(dramaNode), [dramaNode]);
  const readmePath = `${dramaPath}/README.md`;

  const onImportClick = useCallback(async () => {
    if (importBusy) return;
    setImportBusy(true);
    try {
      const result = await importFromDownloads(dramaPath);
      const errorCount = result.errors.length + result.rename.errors.length;
      announceToast(
        `已导入 ${result.moved.length} / 未导入 ${result.unmatched.length} ` +
          `/ 已重命名 ${result.rename.renamed.length} / 失败 ${errorCount}`,
      );
      onChange();
    } catch (err) {
      const kind = err instanceof ApiError ? (err.detail?.kind ?? `HTTP ${err.status}`) : String(err);
      announceToast(`导入失败: ${kind}`);
    } finally {
      setImportBusy(false);
    }
  }, [dramaPath, importBusy, onChange]);

  if (!dramaPath || !dramaNode) {
    return (
      <div className="drama-page">
        <div className="drama-page-header">
          <h1>剧集主页</h1>
        </div>
        <div className="drama-page-empty">没有找到该剧集。请从左侧选择一部剧。</div>
      </div>
    );
  }

  const totalMasters = episodes.reduce((n, e) => n + e.langs.length, 0);

  return (
    <div className="drama-page">
      <div className="drama-page-header">
        <h1>{dramaNode.display_name || dramaNode.name}</h1>
        <button
          type="button"
          className="drama-page-link-btn"
          onClick={() => navigate(`/file/${encodeURIComponent(readmePath)}`)}
          title="打开本剧 README.md"
        >
          📖 打开 README
        </button>
      </div>

      <DramaDashboard path={dramaPath} onSaved={onChange} />

      <section className="drama-page-section" aria-label="资源管理">
        <h2 className="drama-page-section-title">资源管理</h2>
        <div className="drama-dashboard-group" role="group">
          <button
            type="button"
            className="drama-dashboard-btn"
            onClick={onImportClick}
            disabled={importBusy}
            title="从 Downloads 按文件名分类导入近 7 天的图片/视频，并按 parent folder 重命名"
          >
            {importBusy ? "⏳ 导入并重命名中…" : "📥 导入 + 重命名"}
          </button>
          <button
            type="button"
            className="drama-dashboard-btn"
            onClick={() => navigate(`/characters?drama=${encodeURIComponent(dramaPath)}`)}
            title="角色画廊：所有角色缩略图 + 一键重生全部三视图/前2s"
          >
            🎭 角色画廊
          </button>
        </div>
      </section>

      <section className="drama-page-section" aria-label="分集总览">
        <h2 className="drama-page-section-title">
          📺 分集总览
          <span className="drama-page-section-note">
            {episodes.length} 集 · {totalMasters} 个带字幕成片（📦 导出会拷到 production/）
          </span>
        </h2>
        {episodes.length === 0 ? (
          <div className="drama-page-empty">未找到 episodes/ep* 文件夹。</div>
        ) : (
          <ul className="drama-episode-list">
            {episodes.map((ep) => (
              <li key={ep.path} className="drama-episode-row">
                <span className="drama-episode-name">{ep.name}</span>
                {ep.langs.length === 0 ? (
                  <span className="drama-episode-badge drama-episode-badge-none">无字幕成片</span>
                ) : (
                  ["zh", "en", "zhen"]
                    .filter((l) => ep.langs.includes(l))
                    .map((l) => (
                      <span key={l} className="drama-episode-badge">
                        {LANG_LABEL[l]}
                      </span>
                    ))
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
