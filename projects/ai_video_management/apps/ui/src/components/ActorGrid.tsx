/** ActorGrid: paginated grid view of the actor pool.
 *
 * - follow-up 028: initial grid + pagination + tile click → detail.
 * - follow-up 030: select mode + bulk delete + assign-character modal.
 *
 * Multi-select state is cross-page (Set keyed by actor_id, not by visible
 * page slice). Bulk delete loops POST /api/actors/delete; assign loops
 * POST /api/casting/assign; both report per-actor errors without aborting.
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ATTR_OPTIONS, castingAssign, deleteActor, listActors, mediaUrl, type ActorInfo } from "../api";
import { extractDramas, type DramaChoice } from "../lib/dramas";
import { ApiError, type TreeNode } from "../types";

const PAGE_SIZE = 50;
const FILTER_ALL = "__all__";

export interface ActorGridProps {
  tree: TreeNode | null;
  onChange: () => void;
}

export function ActorGrid({ tree, onChange }: ActorGridProps): JSX.Element {
  const navigate = useNavigate();
  const [actors, setActors] = useState<ActorInfo[] | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [page, setPage] = useState<number>(0);
  const [reloadKey, setReloadKey] = useState<number>(0);
  const [selectMode, setSelectMode] = useState<boolean>(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [busyBulk, setBusyBulk] = useState<boolean>(false);
  const [assignOpen, setAssignOpen] = useState<boolean>(false);
  const [filterEthnicity, setFilterEthnicity] = useState<string>(FILTER_ALL);
  const [filterGender, setFilterGender] = useState<string>(FILTER_ALL);
  const [filterAgeRange, setFilterAgeRange] = useState<string>(FILTER_ALL);

  useEffect(() => {
    let cancelled = false;
    setActors(null);
    setError(null);
    void (async () => {
      try {
        const result = await listActors();
        if (!cancelled) setActors(result.actors);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err : new Error(String(err)));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [reloadKey]);

  const filteredActors = useMemo(() => {
    if (!actors) return [];
    return actors.filter((a) => {
      if (filterEthnicity !== FILTER_ALL && a.ethnicity !== filterEthnicity) return false;
      if (filterGender !== FILTER_ALL && a.gender !== filterGender) return false;
      if (filterAgeRange !== FILTER_ALL && a.age_range !== filterAgeRange) return false;
      return true;
    });
  }, [actors, filterEthnicity, filterGender, filterAgeRange]);

  const totalPages = useMemo(() => {
    if (filteredActors.length === 0) return 1;
    return Math.ceil(filteredActors.length / PAGE_SIZE);
  }, [filteredActors]);

  // Reset page when filters change so user starts from page 1 of filtered set.
  useEffect(() => {
    setPage(0);
  }, [filterEthnicity, filterGender, filterAgeRange]);

  useEffect(() => {
    if (page >= totalPages) setPage(Math.max(0, totalPages - 1));
  }, [page, totalPages]);

  const pageActors = useMemo(() => {
    const start = page * PAGE_SIZE;
    return filteredActors.slice(start, start + PAGE_SIZE);
  }, [filteredActors, page]);

  const dramas = useMemo<DramaChoice[]>(() => extractDramas(tree), [tree]);

  const toggleSelected = useCallback((id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  const onTileClick = useCallback(
    (actorId: string, imagePath: string) => {
      if (selectMode) {
        toggleSelected(actorId);
        return;
      }
      navigate(`/file/${encodeURIComponent(imagePath)}`);
    },
    [navigate, selectMode, toggleSelected],
  );

  const enterSelectMode = useCallback(() => {
    setSelectMode(true);
    setSelectedIds(new Set());
  }, []);

  const exitSelectMode = useCallback(() => {
    setSelectMode(false);
    setSelectedIds(new Set());
  }, []);

  const selectAll = useCallback(() => {
    if (!actors) return;
    setSelectedIds(new Set(actors.map((a) => a.id)));
  }, [actors]);

  const clearSelection = useCallback(() => {
    setSelectedIds(new Set());
  }, []);

  const onBulkDelete = useCallback(async () => {
    if (selectedIds.size === 0 || busyBulk) return;
    const ids = Array.from(selectedIds).sort();
    const ok = window.confirm(
      `Delete ${ids.length} actors? They will be moved to _deleted/_actors/ and unassigned from all casting.md.`,
    );
    if (!ok) return;
    setBusyBulk(true);
    let okCount = 0;
    let failCount = 0;
    let unassignCount = 0;
    for (const id of ids) {
      try {
        const r = await deleteActor(id);
        okCount += 1;
        unassignCount += r.unassigned.length;
      } catch (err) {
        failCount += 1;
        const kind = err instanceof ApiError ? err.detail?.kind ?? String(err.status) : String(err);
        console.warn(`bulk delete failed for ${id}: ${kind}`);
      }
    }
    announceToast(
      failCount === 0
        ? `批量删除完成：${okCount} 个 actor，清理 ${unassignCount} 个 casting 引用`
        : `批量删除：成功 ${okCount} / 失败 ${failCount}（详见 console）`,
    );
    setBusyBulk(false);
    exitSelectMode();
    setReloadKey((k) => k + 1);
    onChange();
  }, [busyBulk, exitSelectMode, onChange, selectedIds]);

  if (error) {
    return (
      <div className="actor-grid-page">
        <div role="alert" className="save-error-banner">
          加载失败: {error instanceof ApiError ? `${error.status} ${error.detail?.kind ?? error.message}` : error.message}
        </div>
        <button type="button" onClick={() => setReloadKey((k) => k + 1)}>重试</button>
      </div>
    );
  }

  if (actors === null) {
    return (
      <div className="actor-grid-page">
        <div className="muted">加载中…</div>
      </div>
    );
  }

  if (actors.length === 0) {
    return (
      <div className="actor-grid-page">
        <div className="actor-grid-header">
          <h2>🎭 演员池 (0)</h2>
        </div>
        <div className="actor-grid-empty">
          演员池为空 — 在 sidebar 的 <code>_actors/</code> 行点 "🎭 生成演员" 来生成第一批。
        </div>
      </div>
    );
  }

  return (
    <div className="actor-grid-page">
      <div className="actor-grid-header">
        <h2>🎭 演员池 ({filteredActors.length} / {actors.length})</h2>
        <div className="actor-grid-header-actions">
          {selectMode ? (
            <button type="button" onClick={exitSelectMode}>✕ 退出选择</button>
          ) : (
            <button type="button" onClick={enterSelectMode}>✅ 选择</button>
          )}
        </div>
        <div className="actor-grid-filters" role="group" aria-label="过滤演员">
          <label>
            民族
            <select value={filterEthnicity} onChange={(e) => setFilterEthnicity(e.target.value)}>
              <option value={FILTER_ALL}>全部</option>
              {ATTR_OPTIONS.ethnicity.map((o) => <option key={o} value={o}>{o}</option>)}
            </select>
          </label>
          <label>
            性别
            <select value={filterGender} onChange={(e) => setFilterGender(e.target.value)}>
              <option value={FILTER_ALL}>全部</option>
              {ATTR_OPTIONS.gender.map((o) => <option key={o} value={o}>{o}</option>)}
            </select>
          </label>
          <label>
            年龄段
            <select value={filterAgeRange} onChange={(e) => setFilterAgeRange(e.target.value)}>
              <option value={FILTER_ALL}>全部</option>
              {ATTR_OPTIONS.age_range.map((o) => <option key={o} value={o}>{o}</option>)}
            </select>
          </label>
        </div>
        {totalPages > 1 ? (
          <div className="actor-grid-pagination" role="navigation" aria-label="演员池分页">
            <button type="button" onClick={() => setPage(0)} disabled={page === 0} aria-label="首页" title="首页">⏮</button>
            <button type="button" onClick={() => setPage((p) => Math.max(0, p - 1))} disabled={page === 0} aria-label="上一页">◀ 上一页</button>
            <span className="actor-grid-page-indicator" aria-live="polite">第 {page + 1} / {totalPages} 页</span>
            <button type="button" onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))} disabled={page >= totalPages - 1} aria-label="下一页">下一页 ▶</button>
            <button type="button" onClick={() => setPage(totalPages - 1)} disabled={page >= totalPages - 1} aria-label="末页" title="末页">⏭</button>
          </div>
        ) : null}
      </div>
      <div className="actor-grid" role="list">
        {pageActors.map((actor) => {
          const selected = selectedIds.has(actor.id);
          return (
            <button
              key={actor.id}
              type="button"
              role="listitem"
              className={["actor-tile", selected ? "actor-tile-selected" : ""].filter(Boolean).join(" ")}
              onClick={() => onTileClick(actor.id, actor.image_path)}
              aria-label={selectMode ? `${selected ? "取消" : ""}选择 ${actor.id}` : `查看 ${actor.id} 详情`}
              aria-pressed={selectMode ? selected : undefined}
            >
              {selectMode ? (
                <span className="actor-grid-checkbox" aria-hidden="true">{selected ? "✓" : "○"}</span>
              ) : null}
              <img
                className="actor-tile-image"
                src={mediaUrl(actor.image_path, actor.mtime)}
                alt={actor.id}
                loading="lazy"
              />
              <div className="actor-tile-meta">
                <div className="actor-tile-id">{actor.id}</div>
                <div className="actor-tile-chips">
                  <span className="actor-tile-chip">{actor.ethnicity}</span>
                  <span className="actor-tile-chip">{actor.gender}</span>
                  <span className="actor-tile-chip">{actor.age_range}</span>
                  <span className="actor-tile-chip">{actor.look}</span>
                </div>
              </div>
            </button>
          );
        })}
      </div>
      {selectMode ? (
        <div className="actor-grid-select-bar" role="region" aria-label="批量操作">
          <span className="actor-grid-select-count">已选 {selectedIds.size} / 总 {actors.length}</span>
          <button type="button" onClick={selectAll} disabled={busyBulk}>全选</button>
          <button type="button" onClick={clearSelection} disabled={busyBulk || selectedIds.size === 0}>全清</button>
          <button
            type="button"
            className="actor-grid-bulk-delete"
            onClick={onBulkDelete}
            disabled={busyBulk || selectedIds.size === 0}
          >
            {busyBulk ? "删除中…" : `🗑 批量删除 (${selectedIds.size})`}
          </button>
          <button
            type="button"
            onClick={() => setAssignOpen(true)}
            disabled={busyBulk || selectedIds.size === 0}
          >
            🎬 分配角色 ({selectedIds.size})
          </button>
        </div>
      ) : null}
      {assignOpen ? (
        <AssignCharacterModal
          actorIds={Array.from(selectedIds).sort()}
          dramas={dramas}
          onClose={() => setAssignOpen(false)}
          onAssigned={() => { onChange(); }}
        />
      ) : null}
    </div>
  );
}

interface AssignModalProps {
  actorIds: string[];
  dramas: DramaChoice[];
  onClose: () => void;
  onAssigned: () => void;
}

function AssignCharacterModal({ actorIds, dramas, onClose, onAssigned }: AssignModalProps): JSX.Element {
  const [dramaPath, setDramaPath] = useState<string>(dramas[0]?.path ?? "");
  const currentDrama = useMemo(() => dramas.find((d) => d.path === dramaPath) ?? dramas[0] ?? null, [dramaPath, dramas]);
  const characters = currentDrama?.characters ?? [];
  const [role, setRole] = useState<string>(characters[0] ?? "");
  const [notes, setNotes] = useState<string>("");
  const [busy, setBusy] = useState<boolean>(false);

  useEffect(() => {
    setRole(characters[0] ?? "");
  }, [characters]);

  const onConfirm = useCallback(async () => {
    if (!currentDrama || !role || actorIds.length === 0 || busy) return;
    setBusy(true);
    let okCount = 0;
    let failCount = 0;
    for (const id of actorIds) {
      try {
        await castingAssign(currentDrama.path, role, id, notes);
        okCount += 1;
      } catch (err) {
        failCount += 1;
        const kind = err instanceof ApiError ? err.detail?.kind ?? String(err.status) : String(err);
        console.warn(`assign failed for ${id}: ${kind}`);
      }
    }
    announceToast(
      failCount === 0
        ? `已分配 ${okCount} 个 actor 到 ${currentDrama.name} / ${role}`
        : `分配：成功 ${okCount} / 失败 ${failCount}（详见 console）`,
    );
    setBusy(false);
    onAssigned();
    onClose();
  }, [actorIds, busy, currentDrama, notes, onAssigned, onClose, role]);

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label="分配角色" onClick={onClose}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🎬 分配角色 ({actorIds.length} 个 actor)</h2>
          <button type="button" className="modal-close" onClick={onClose} aria-label="关闭">×</button>
        </div>
        <div className="modal-body">
          {dramas.length === 0 ? (
            <p>当前 ai_videos/ 下没有 drama（系统 folder `_*` 不算）。</p>
          ) : (
            <>
              <label className="form-field">
                <span className="form-field-label">短剧</span>
                <select value={dramaPath} onChange={(e) => setDramaPath(e.target.value)} disabled={busy}>
                  {dramas.map((d) => (
                    <option key={d.path} value={d.path}>{d.name}</option>
                  ))}
                </select>
              </label>
              <label className="form-field">
                <span className="form-field-label">角色 (characters/c*/ 子目录)</span>
                <select value={role} onChange={(e) => setRole(e.target.value)} disabled={busy || characters.length === 0}>
                  {characters.length === 0 ? (
                    <option value="">（这个短剧下没有 c*/ 角色目录）</option>
                  ) : (
                    characters.map((c) => <option key={c} value={c}>{c}</option>)
                  )}
                </select>
              </label>
              <label className="form-field">
                <span className="form-field-label">备注 (可选)</span>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  disabled={busy}
                  maxLength={500}
                />
              </label>
            </>
          )}
        </div>
        <div className="modal-footer">
          <button type="button" onClick={onClose} disabled={busy}>取消</button>
          <button
            type="button"
            className="modal-primary"
            onClick={onConfirm}
            disabled={busy || !currentDrama || !role || actorIds.length === 0}
          >
            {busy ? "分配中…" : "确认"}
          </button>
        </div>
      </div>
    </div>
  );
}

function announceToast(message: string): void {
  const region = document.getElementById("aria-live-toast");
  if (!region) return;
  region.textContent = "";
  window.setTimeout(() => { region.textContent = message; }, 30);
}
