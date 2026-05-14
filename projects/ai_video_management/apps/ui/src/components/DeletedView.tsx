/** DeletedView: recycle-bin grid + bulk hard-delete for ai_videos/_deleted/**.
 *
 * Follow-up 038: sidebar `_deleted/` row → "🧹 永久清理" button → `/deleted`
 * route → grid of media tiles → multi-select + typed-DELETE modal → loop
 * `POST /api/hard-delete-media`. Soft-deleted via follow-up 023 lands here.
 */
import { useCallback, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { hardDeleteMedia, mediaUrl } from "../api";
import { ApiError, type TreeNode } from "../types";

const PAGE_SIZE = 50;
const PREVIEW_LIMIT = 10;
const CONFIRM_TOKEN = "DELETE";

interface DeletedEntry {
  path: string;
  name: string;
  subPath: string;
  isVideo: boolean;
}

export interface DeletedViewProps {
  tree: TreeNode | null;
  onChange: () => void;
}

export function DeletedView({ tree, onChange }: DeletedViewProps): JSX.Element {
  const navigate = useNavigate();
  const [selectMode, setSelectMode] = useState<boolean>(false);
  const [selectedPaths, setSelectedPaths] = useState<Set<string>>(new Set());
  const [page, setPage] = useState<number>(0);
  const [modalOpen, setModalOpen] = useState<boolean>(false);
  const [typedConfirm, setTypedConfirm] = useState<string>("");
  const [busy, setBusy] = useState<boolean>(false);

  const entries = useMemo<DeletedEntry[]>(() => collectDeletedMedia(tree), [tree]);

  const totalPages = useMemo(() => {
    if (entries.length === 0) return 1;
    return Math.ceil(entries.length / PAGE_SIZE);
  }, [entries.length]);

  const pageEntries = useMemo(() => {
    const start = page * PAGE_SIZE;
    return entries.slice(start, start + PAGE_SIZE);
  }, [entries, page]);

  const toggleSelected = useCallback((path: string) => {
    setSelectedPaths((prev) => {
      const next = new Set(prev);
      if (next.has(path)) next.delete(path);
      else next.add(path);
      return next;
    });
  }, []);

  const onTileClick = useCallback((entry: DeletedEntry) => {
    if (selectMode) {
      toggleSelected(entry.path);
      return;
    }
    navigate(`/file/${encodeURIComponent(entry.path)}`);
  }, [navigate, selectMode, toggleSelected]);

  const enterSelectMode = useCallback(() => {
    setSelectMode(true);
    setSelectedPaths(new Set());
  }, []);

  const exitSelectMode = useCallback(() => {
    setSelectMode(false);
    setSelectedPaths(new Set());
  }, []);

  const selectAll = useCallback(() => {
    setSelectedPaths(new Set(entries.map((e) => e.path)));
  }, [entries]);

  const clearSelection = useCallback(() => {
    setSelectedPaths(new Set());
  }, []);

  const openModal = useCallback(() => {
    if (selectedPaths.size === 0) return;
    setTypedConfirm("");
    setModalOpen(true);
  }, [selectedPaths.size]);

  const closeModal = useCallback(() => {
    if (busy) return;
    setModalOpen(false);
    setTypedConfirm("");
  }, [busy]);

  const onConfirmPurge = useCallback(async () => {
    if (typedConfirm !== CONFIRM_TOKEN || selectedPaths.size === 0 || busy) return;
    setBusy(true);
    const paths = Array.from(selectedPaths).sort();
    let okCount = 0;
    let failCount = 0;
    for (const p of paths) {
      try {
        await hardDeleteMedia(p);
        okCount += 1;
      } catch (err) {
        failCount += 1;
        const kind = err instanceof ApiError ? err.detail?.kind ?? String(err.status) : String(err);
        console.warn(`hard delete failed for ${p}: ${kind}`);
      }
    }
    announceToast(
      failCount === 0
        ? `已永久删除 ${okCount} 个文件`
        : `永久删除：成功 ${okCount} / 失败 ${failCount}（详见 console）`,
    );
    setBusy(false);
    setModalOpen(false);
    setTypedConfirm("");
    exitSelectMode();
    onChange();
  }, [busy, exitSelectMode, onChange, selectedPaths, typedConfirm]);

  if (entries.length === 0) {
    return (
      <div className="deleted-view-page">
        <div className="deleted-view-header">
          <h2>🗑 回收站 (0)</h2>
        </div>
        <div className="deleted-view-empty">
          回收站为空 — 软删除的文件（来自 mp4 / 图片 Reader 的 🗑 Delete 按钮）会出现在此处。
        </div>
      </div>
    );
  }

  return (
    <div className="deleted-view-page">
      <div className="deleted-view-header">
        <h2>🗑 回收站 ({entries.length} 个文件)</h2>
        <div className="deleted-view-header-actions">
          {selectMode ? (
            <button type="button" onClick={exitSelectMode} disabled={busy}>✕ 退出选择</button>
          ) : (
            <button type="button" onClick={enterSelectMode}>✅ 选择</button>
          )}
        </div>
        {totalPages > 1 ? (
          <div className="actor-grid-pagination" role="navigation" aria-label="回收站分页">
            <button type="button" onClick={() => setPage(0)} disabled={page === 0} aria-label="首页" title="首页">⏮</button>
            <button type="button" onClick={() => setPage((p) => Math.max(0, p - 1))} disabled={page === 0} aria-label="上一页">◀ 上一页</button>
            <span className="actor-grid-page-indicator" aria-live="polite">第 {page + 1} / {totalPages} 页</span>
            <button type="button" onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))} disabled={page >= totalPages - 1} aria-label="下一页">下一页 ▶</button>
            <button type="button" onClick={() => setPage(totalPages - 1)} disabled={page >= totalPages - 1} aria-label="末页" title="末页">⏭</button>
          </div>
        ) : null}
      </div>
      <div className="deleted-view-grid" role="list">
        {pageEntries.map((entry) => {
          const selected = selectedPaths.has(entry.path);
          return (
            <button
              key={entry.path}
              type="button"
              role="listitem"
              className={["deleted-tile", selected ? "deleted-tile-selected" : ""].filter(Boolean).join(" ")}
              onClick={() => onTileClick(entry)}
              aria-label={selectMode ? `${selected ? "取消" : ""}选择 ${entry.name}` : `查看 ${entry.name}`}
              aria-pressed={selectMode ? selected : undefined}
            >
              {selectMode ? (
                <span className="actor-grid-checkbox" aria-hidden="true">{selected ? "✓" : "○"}</span>
              ) : null}
              <div className="deleted-tile-thumb">
                {entry.isVideo ? (
                  <video src={mediaUrl(entry.path)} preload="metadata" muted playsInline />
                ) : (
                  <img src={mediaUrl(entry.path)} alt={entry.name} loading="lazy" />
                )}
              </div>
              <div className="deleted-tile-meta">
                <div className="deleted-tile-name">{entry.name}</div>
                <div className="deleted-tile-path">{entry.subPath}</div>
              </div>
            </button>
          );
        })}
      </div>
      {selectMode ? (
        <div className="actor-grid-select-bar" role="region" aria-label="批量永久删除">
          <span className="actor-grid-select-count">已选 {selectedPaths.size} / 总 {entries.length}</span>
          <button type="button" onClick={selectAll} disabled={busy}>全选</button>
          <button type="button" onClick={clearSelection} disabled={busy || selectedPaths.size === 0}>全清</button>
          <button
            type="button"
            className="deleted-bulk-purge"
            onClick={openModal}
            disabled={busy || selectedPaths.size === 0}
          >
            🗑 永久删除 ({selectedPaths.size})
          </button>
        </div>
      ) : null}
      {modalOpen ? (
        <ConfirmPurgeModal
          paths={Array.from(selectedPaths).sort()}
          typedConfirm={typedConfirm}
          onTypedChange={setTypedConfirm}
          busy={busy}
          onCancel={closeModal}
          onConfirm={onConfirmPurge}
        />
      ) : null}
    </div>
  );
}

interface ConfirmPurgeModalProps {
  paths: string[];
  typedConfirm: string;
  onTypedChange: (next: string) => void;
  busy: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

function ConfirmPurgeModal({ paths, typedConfirm, onTypedChange, busy, onCancel, onConfirm }: ConfirmPurgeModalProps): JSX.Element {
  const preview = paths.slice(0, PREVIEW_LIMIT);
  const overflow = paths.length - preview.length;
  const armed = typedConfirm === CONFIRM_TOKEN;
  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label="确认永久删除" onClick={onCancel}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>永久删除 {paths.length} 个文件？</h2>
          <button type="button" className="modal-close" onClick={onCancel} aria-label="关闭" disabled={busy}>×</button>
        </div>
        <div className="modal-body">
          <div className="deleted-view-confirm-warning" role="alert">
            ⚠ 此操作不可撤销 — 文件将从磁盘真删除，没有 in-app restore。
          </div>
          <ul className="deleted-view-confirm-list">
            {preview.map((p) => <li key={p}>{p}</li>)}
            {overflow > 0 ? <li className="muted">+ {overflow} 个其他文件…</li> : null}
          </ul>
          <label className="form-field">
            <span className="form-field-label">输入 <code>{CONFIRM_TOKEN}</code> 解锁确认按钮</span>
            <input
              className="deleted-view-confirm-input"
              type="text"
              value={typedConfirm}
              onChange={(e) => onTypedChange(e.target.value)}
              disabled={busy}
              autoFocus
              placeholder={CONFIRM_TOKEN}
              aria-label="输入 DELETE 解锁确认"
            />
          </label>
        </div>
        <div className="modal-footer">
          <button type="button" onClick={onCancel} disabled={busy}>取消</button>
          <button
            type="button"
            className="modal-primary deleted-bulk-purge"
            onClick={onConfirm}
            disabled={busy || !armed}
          >
            {busy ? "删除中…" : `永久删除 ${paths.length} 个文件`}
          </button>
        </div>
      </div>
    </div>
  );
}

function collectDeletedMedia(tree: TreeNode | null): DeletedEntry[] {
  if (!tree) return [];
  const out: DeletedEntry[] = [];
  const walk = (node: TreeNode): void => {
    if (node.type === "image" || node.type === "video") {
      if (node.path.startsWith("ai_videos/_deleted/")) {
        out.push({
          path: node.path,
          name: node.name,
          subPath: node.path.slice("ai_videos/_deleted/".length),
          isVideo: node.type === "video",
        });
      }
      return;
    }
    for (const c of node.children ?? []) walk(c);
  };
  walk(tree);
  out.sort((a, b) => (a.path < b.path ? -1 : a.path > b.path ? 1 : 0));
  return out;
}

function announceToast(message: string): void {
  const region = document.getElementById("aria-live-toast");
  if (!region) return;
  region.textContent = "";
  window.setTimeout(() => { region.textContent = message; }, 30);
}
