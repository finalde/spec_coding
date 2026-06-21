/** BgmEpisodePanel: episode-level BGM arrangement.
 *
 * Renders the sparse cue timeline (episodes/epNN/bgm/bgm.md): each cue shows
 * its time window + desired emotion + author note. Per cue, the user first
 * picks a TYPE (category, defaulting to the cue's emotion or 全部类型) then picks
 * a shared-library bgm_NNNN of that type — not locked to the cue's category. A
 * single "🎵 烧录 BGM" burns the assigned cues onto the subtitled episode master
 * ep{NN}_zh.mp4 → ep{NN}_zh_bgm.mp4 (re-burn overwrites).
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  assignBgmCue,
  burnEpisodeBgm,
  listBgms,
  mediaUrl,
  readEpisodeBgm,
  unassignBgmCue,
  BGM_CATEGORY_LABELS_ZH,
  BGM_CATEGORY_OPTIONS,
  type BgmCueInfo,
  type BgmInfo,
  type EpisodeBgmRead,
} from "../api";

const ALL_CATS = "__all__";
import { announceToast } from "../lib/announce";
import { ApiError } from "../types";

export interface BgmEpisodePanelProps {
  path: string;
  onSaved: () => void;
}

function fmt(n: number): string {
  return Number.isInteger(n) ? String(n) : n.toFixed(1);
}

function catLabel(cat: string): string {
  return BGM_CATEGORY_LABELS_ZH[cat] ?? (cat || "—");
}

export function BgmEpisodePanel({ path, onSaved }: BgmEpisodePanelProps): JSX.Element {
  const [data, setData] = useState<EpisodeBgmRead | null>(null);
  const [library, setLibrary] = useState<BgmInfo[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busyWindow, setBusyWindow] = useState<string | null>(null);
  const [burning, setBurning] = useState<boolean>(false);
  // Per-cue chosen category override (keyed by `${start}-${end}`). Defaults to
  // the assigned track's category, else the cue's emotion; user can switch to
  // any category or 全部类型 to pick a track outside the cue's emotion.
  const [pickCat, setPickCat] = useState<Record<string, string>>({});

  const load = useCallback(async () => {
    setError(null);
    try {
      const [read, libs] = await Promise.all([readEpisodeBgm(path), listBgms()]);
      setData(read);
      setLibrary(libs.bgms);
    } catch (e) {
      setError(e instanceof ApiError ? `${e.detail?.kind ?? e.message}` : String(e));
    }
  }, [path]);

  useEffect(() => { void load(); }, [load]);

  const byCategory = useMemo(() => {
    const map: Record<string, BgmInfo[]> = {};
    for (const b of library) {
      if (!b.audio_path) continue; // only assignable once it has audio
      (map[b.category] ??= []).push(b);
    }
    return map;
  }, [library]);

  const allAudible = useMemo(() => library.filter((b) => b.audio_path), [library]);

  const onAssign = async (cue: BgmCueInfo, bgmId: string) => {
    const key = `${cue.start}-${cue.end}`;
    setBusyWindow(key);
    setError(null);
    try {
      const next = bgmId
        ? await assignBgmCue(path, cue.start, cue.end, bgmId)
        : await unassignBgmCue(path, cue.start, cue.end);
      setData(next);
      onSaved();
    } catch (e) {
      setError(e instanceof ApiError ? `${e.detail?.kind ?? e.message}` : String(e));
    } finally {
      setBusyWindow(null);
    }
  };

  const onBurn = async () => {
    setBurning(true);
    setError(null);
    try {
      const res = await burnEpisodeBgm(path);
      const skipped = res.skipped.length ? `，跳过 ${res.skipped.length} 条未分配` : "";
      announceToast(`已烧录 ${res.used.length} 条 BGM → ${res.out}${skipped}`);
      await load();
      onSaved();
    } catch (e) {
      setError(e instanceof ApiError ? `烧录失败: ${e.detail?.kind ?? e.message}` : String(e));
    } finally {
      setBurning(false);
    }
  };

  if (error && !data) return <div className="bgm-ep-panel"><p className="bgm-ep-error">⚠ {error}</p></div>;
  if (!data) return <div className="bgm-ep-panel"><p>加载中…</p></div>;

  const assignedCount = data.cues.filter((c) => c.assigned).length;
  const canBurn = data.source_exists && assignedCount > 0 && !burning;

  return (
    <div className="bgm-ep-panel">
      <div className="bgm-ep-header">
        <h2>🎵 BGM 编排 — {data.episode.split("/").slice(-1)[0]}</h2>
        <div className="bgm-ep-actions">
          <button type="button" className="bgm-ep-burn-btn" onClick={onBurn} disabled={!canBurn}
            title={!data.source_exists
              ? "缺源：先合成本集中文字幕视频 ep{NN}_zh.mp4"
              : assignedCount === 0 ? "尚无已分配的 BGM cue"
              : "把已分配的 BGM 按 cue 烧进 ep{NN}_zh.mp4 → ep{NN}_zh_bgm.mp4（覆盖）"}>
            {burning ? "⏳ 烧录中…" : `🎵 烧录 BGM（${assignedCount}）`}
          </button>
        </div>
      </div>

      <p className="bgm-ep-status">
        源 <code>{data.source.split("/").slice(-1)[0]}</code>{" "}
        {data.source_exists ? "✅" : "❌（先合成中文字幕本集视频）"}
        {data.output_exists && <> · 成片 <code>{data.output.split("/").slice(-1)[0]}</code> ✅</>}
      </p>
      {error && <p className="bgm-ep-error">⚠ {error}</p>}

      {data.cues.length === 0 ? (
        <p className="bgm-ep-empty">尚无 cue。请在 <code>bgm/bgm.md</code> 里按剧情写稀疏配乐时间线。</p>
      ) : (
        <table className="bgm-ep-table">
          <thead>
            <tr><th>时间窗</th><th>情绪</th><th>分配 BGM</th><th>试听</th><th>参数</th><th>剧情</th></tr>
          </thead>
          <tbody>
            {data.cues.map((cue) => {
              const key = `${cue.start}-${cue.end}`;
              const assigned = library.find((b) => b.id === cue.bgm_id) ?? null;
              const effCat = pickCat[key] ?? assigned?.category ?? cue.category;
              let opts = effCat === ALL_CATS ? allAudible : (byCategory[effCat] ?? []);
              // Keep the currently-assigned track visible even if it sits in a
              // different category than the one being browsed.
              if (assigned?.audio_path && !opts.some((o) => o.id === assigned.id)) {
                opts = [assigned, ...opts];
              }
              return (
                <tr key={key} className={cue.assigned ? "bgm-ep-row-assigned" : "bgm-ep-row-open"}>
                  <td><code>{fmt(cue.start)}–{fmt(cue.end)}s</code></td>
                  <td>{catLabel(cue.category)}</td>
                  <td>
                    <select className="bgm-ep-cat-select" value={effCat} disabled={busyWindow === key}
                      onChange={(e) => setPickCat((p) => ({ ...p, [key]: e.target.value }))}
                      aria-label={`为 ${key} 选择 BGM 类型`}>
                      <option value={ALL_CATS}>全部类型</option>
                      {BGM_CATEGORY_OPTIONS.map((slug) => (
                        <option key={slug} value={slug}>{BGM_CATEGORY_LABELS_ZH[slug] ?? slug}</option>
                      ))}
                    </select>
                    <select value={cue.bgm_id ?? ""} disabled={busyWindow === key}
                      onChange={(e) => void onAssign(cue, e.target.value)}
                      aria-label={`为 ${key} 分配 BGM`}>
                      <option value="">— 未分配 —</option>
                      {opts.map((b) => (
                        <option key={b.id} value={b.id}>
                          {b.id} · {catLabel(b.category)}{b.mood ? ` · ${b.mood}` : ""} ({b.duration}s)
                        </option>
                      ))}
                    </select>
                    {opts.length === 0 && <span className="bgm-ep-hint"> 该类型下暂无已生成 BGM</span>}
                  </td>
                  <td>
                    {assigned?.audio_path
                      ? <audio controls preload="none" src={mediaUrl(assigned.audio_path)} />
                      : "—"}
                  </td>
                  <td className="bgm-ep-params">
                    音量 {fmt(cue.vol)}{cue.duck ? " · 闪避" : ""}
                    {cue.fade_in || cue.fade_out
                      ? ` · 淡化 ${cue.fade_in ? "淡入" : ""}${cue.fade_in && cue.fade_out ? "/" : ""}${cue.fade_out ? "淡出" : ""}`
                      : ""}
                  </td>
                  <td className="bgm-ep-comment">{cue.comment || "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
