import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ATTR_OPTIONS,
  type ActorInfo,
  type CastEntry,
  castingAssign,
  castingUnassign,
  fetchCasting,
  listActors,
  mediaUrl,
} from "../api";
import { ApiError } from "../types";

export interface CastingViewProps {
  castingPath: string; // e.g. "ai_videos/mozun_chongsheng/casting.md"
  onChange: () => void;
}

type FilterKey = "ethnicity" | "gender" | "age_range" | "look" | "style";

interface FilterState {
  ethnicity: string;
  gender: string;
  age_range: string;
  look: string;
  style: string;
}

const ALL = "(全部)";

const REF_VIDEO_PROMPT_TEMPLATE = (faceRel: string, _role: string): string => `[参考图: ${faceRel}]
角色: {请填写角色锁定描述符，与 c{N}_*.md 的【XXX · YYY · 锁定描述符 v1】块 byte-identical}
场景: 纯色 ${"#1a1a1a"} 背景，无杂物
动作: 0-0.5s 正面定格；0.5-1.0s 缓慢右转 90°；1.0-1.5s 缓慢左转 180°；1.5-2.0s 回正；2.0-2.5s 微抬头；2.5-2.9s 回正定格
镜头: 中近景，固定机位，不变焦
光线/色调: 三点照明（主光柔光、副光弱、背光勾边），冷色调
比例: 9:16
时长: 2.9s
音频: 无（视频纯视觉 reference）
不要: 任何音频 / BGM / 音效 / 旁白 / 环境音；不要 超过 2.9s；不要 场景切换；不要 道具`;

export function CastingView({ castingPath, onChange }: CastingViewProps): JSX.Element {
  const dramaPath = useMemo(() => {
    const parts = castingPath.split("/");
    return parts.slice(0, 2).join("/"); // "ai_videos/{drama}"
  }, [castingPath]);

  const [entries, setEntries] = useState<CastEntry[]>([]);
  const [actors, setActors] = useState<ActorInfo[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<"read" | "assign">("read");
  const [filters, setFilters] = useState<FilterState>({
    ethnicity: ALL,
    gender: ALL,
    age_range: ALL,
    look: ALL,
    style: ALL,
  });
  const [newRole, setNewRole] = useState<string>("");
  const [newNotes, setNewNotes] = useState<string>("");
  const [busy, setBusy] = useState<boolean>(false);
  const [toast, setToast] = useState<{ kind: "ok" | "err"; text: string } | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    try {
      const [castResult, actorResult] = await Promise.all([
        fetchCasting(dramaPath),
        listActors(),
      ]);
      setEntries(castResult.entries);
      setActors(actorResult.actors);
      setError(null);
    } catch (err) {
      const msg = err instanceof ApiError ? `${err.status} ${err.detail?.kind ?? ""}` : String(err);
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [dramaPath]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const filteredActors = useMemo(() => {
    return actors.filter((a) => {
      for (const k of Object.keys(filters) as FilterKey[]) {
        const v = filters[k];
        if (v !== ALL && (a as unknown as Record<string, unknown>)[k] !== v) return false;
      }
      return true;
    });
  }, [actors, filters]);

  const actorById = useMemo(() => {
    const m = new Map<string, ActorInfo>();
    for (const a of actors) m.set(a.id, a);
    return m;
  }, [actors]);

  const onAssign = useCallback(async (actorId: string) => {
    if (!newRole.trim()) {
      setToast({ kind: "err", text: "请先输入角色名" });
      return;
    }
    setBusy(true);
    setToast(null);
    try {
      const r = await castingAssign(dramaPath, newRole.trim(), actorId, newNotes);
      setEntries(r.entries);
      setToast({ kind: "ok", text: `已分配 ${newRole.trim()} → ${actorId}` });
      setNewRole("");
      setNewNotes("");
      setMode("read");
      onChange();
    } catch (err) {
      const msg = err instanceof ApiError ? `分配失败: ${err.detail?.kind ?? err.status}` : String(err);
      setToast({ kind: "err", text: msg });
    } finally {
      setBusy(false);
    }
  }, [dramaPath, newNotes, newRole, onChange]);

  const onUnassign = useCallback(async (role: string) => {
    setBusy(true);
    setToast(null);
    try {
      const r = await castingUnassign(dramaPath, role);
      setEntries(r.entries);
      setToast({ kind: "ok", text: `已取消 ${role}` });
      onChange();
    } catch (err) {
      const msg = err instanceof ApiError ? `取消失败: ${err.detail?.kind ?? err.status}` : String(err);
      setToast({ kind: "err", text: msg });
    } finally {
      setBusy(false);
    }
  }, [dramaPath, onChange]);

  const onCopyRefVideoPrompt = useCallback(async (entry: CastEntry) => {
    const actor = actorById.get(entry.actor_id);
    if (!actor) return;
    const prompt = REF_VIDEO_PROMPT_TEMPLATE(actor.image_path, entry.role);
    try {
      await navigator.clipboard.writeText(prompt);
      setToast({ kind: "ok", text: `已复制 ref-video prompt（${entry.role}）` });
    } catch {
      setToast({ kind: "err", text: "复制失败 — 请手动选中" });
    }
  }, [actorById]);

  if (loading) return <div className="muted">加载演员池…</div>;
  if (error) return <div role="alert" className="save-error-banner">{error}</div>;

  return (
    <div className="casting-view">
      <div className="casting-header">
        <h2>选角 — {dramaPath.split("/")[1]}</h2>
        <div className="casting-header-actions">
          {mode === "read" ? (
            <button type="button" className="casting-add-btn" onClick={() => setMode("assign")} disabled={busy}>
              + 添加角色
            </button>
          ) : (
            <button type="button" onClick={() => setMode("read")} disabled={busy}>
              ← 返回
            </button>
          )}
        </div>
      </div>
      {toast ? (
        <div role="status" aria-live="polite" className={`casting-toast casting-toast-${toast.kind}`}>
          {toast.text}
          <button type="button" onClick={() => setToast(null)} aria-label="关闭" className="casting-toast-dismiss">×</button>
        </div>
      ) : null}

      {mode === "read" ? (
        entries.length === 0 ? (
          <p className="muted">还没有 cast — 点 "+ 添加角色" 开始。</p>
        ) : (
          <table className="casting-table">
            <thead>
              <tr>
                <th>角色</th>
                <th>演员</th>
                <th>属性</th>
                <th>备注</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => {
                const actor = actorById.get(entry.actor_id);
                return (
                  <tr key={entry.role}>
                    <td className="casting-role">{entry.role}</td>
                    <td className="casting-actor-cell">
                      {actor ? (
                        <>
                          <img
                            src={mediaUrl(actor.image_path, actor.mtime)}
                            alt={entry.actor_id}
                            className="casting-thumbnail"
                          />
                          <span className="casting-actor-id">{entry.actor_id}</span>
                        </>
                      ) : (
                        <span className="casting-actor-missing">{entry.actor_id}（缺图）</span>
                      )}
                    </td>
                    <td className="casting-attrs">
                      {actor ? (
                        <span>
                          {actor.ethnicity} · {actor.gender} · {actor.age_range} ·{" "}
                          {actor.look} · {actor.style}
                        </span>
                      ) : null}
                    </td>
                    <td>{entry.notes || "—"}</td>
                    <td className="casting-row-actions">
                      <button
                        type="button"
                        onClick={() => onCopyRefVideoPrompt(entry)}
                        disabled={!actor || busy}
                        title="复制 2.9s Seedance ref-video prompt（rule #12.5）+ 演员图路径"
                      >
                        ▶ 复制 ref-video prompt
                      </button>
                      <button
                        type="button"
                        onClick={() => onUnassign(entry.role)}
                        disabled={busy}
                      >
                        🗑 取消
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )
      ) : (
        <div className="casting-assign-pane">
          <div className="casting-assign-form">
            <label className="form-field">
              <span className="form-field-label">角色名（例如 c1_主角）</span>
              <input
                type="text"
                value={newRole}
                onChange={(e) => setNewRole(e.target.value)}
                disabled={busy}
                placeholder="c1_主角"
              />
            </label>
            <label className="form-field">
              <span className="form-field-label">备注 (可选)</span>
              <input
                type="text"
                value={newNotes}
                onChange={(e) => setNewNotes(e.target.value)}
                disabled={busy}
                placeholder="可填例如：男主，魔尊"
              />
            </label>
          </div>
          <div className="casting-filter-chips">
            {(Object.keys(ATTR_OPTIONS) as FilterKey[]).map((k) => (
              <select
                key={k}
                value={filters[k]}
                onChange={(e) => setFilters((f) => ({ ...f, [k]: e.target.value }))}
                disabled={busy}
                aria-label={`筛选 ${k}`}
              >
                <option value={ALL}>{k}: {ALL}</option>
                {ATTR_OPTIONS[k].map((o) => (
                  <option key={o} value={o}>{k}: {o}</option>
                ))}
              </select>
            ))}
          </div>
          {filteredActors.length === 0 ? (
            <p className="muted">没有匹配的演员 — 调整筛选或先到 _actors/ 生成更多。</p>
          ) : (
            <div className="casting-actor-grid">
              {filteredActors.map((actor) => (
                <button
                  key={actor.id}
                  type="button"
                  className="casting-actor-tile"
                  onClick={() => onAssign(actor.id)}
                  disabled={busy || !newRole.trim()}
                  title={`分配 ${actor.id} → ${newRole.trim() || "（先输入角色名）"}`}
                >
                  <img src={mediaUrl(actor.image_path, actor.mtime)} alt={actor.id} />
                  <span className="casting-actor-tile-id">{actor.id}</span>
                  <span className="casting-actor-tile-attrs">
                    {actor.ethnicity} · {actor.gender} · {actor.age_range}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
