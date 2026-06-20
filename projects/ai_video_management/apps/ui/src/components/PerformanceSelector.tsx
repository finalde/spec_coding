/** PerformanceSelector: on a shot page, recommend演技库候选 (top-N scored against
 * the shot's emotion/intensity/duration), let the user multi-select, write the
 * selection back as the shot's `表演库参考:` line, and (separately) assemble a
 * copy-paste regen prompt from the selected entries. The regen prompt is shown
 * read-only with a 📋 复制 button — it never triggers a render directly.
 *
 * Filter UX mirrors CastingView (filter state + useMemo + toast). The regen
 * display + copy mirrors ShotRegenButton. mp4 previews reuse `mediaUrl`. */
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  type PerformanceCandidate,
  mediaUrl,
  performanceCandidates,
  regenShotPrompt,
  setShotPerformanceRefs,
} from "../api";
import { ApiError } from "../types";

export interface PerformanceSelectorProps {
  shotPath: string;
  mtime: string;
  /** Optional shot markdown content — used to pre-check已标注的 `表演库参考: perf_NNNN`. */
  content?: string;
}

const ALL = "(全部)";

/** Emotion 大类下拉 — the broad categories the library is tagged by. The
 * candidate endpoint accepts any of these or none (无 → 用 shot 猜测). */
const EMOTION_OPTIONS = [
  "愤怒",
  "悲伤",
  "喜悦",
  "恐惧",
  "惊讶",
  "厌恶",
  "平静",
  "紧张",
  "得意",
  "痛苦",
] as const;

/** Intensity 1–5; ALL means "don't filter by intensity". */
const INTENSITY_OPTIONS = ["1", "2", "3", "4", "5"] as const;

function parseExistingRefs(content: string | undefined): string[] {
  if (!content) return [];
  const out: string[] = [];
  const re = /表演库参考[:：]\s*(perf_\d{4})/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(content)) !== null) out.push(m[1]);
  return out;
}

export function PerformanceSelector({ shotPath, mtime, content }: PerformanceSelectorProps): JSX.Element {
  const [emotion, setEmotion] = useState<string>(ALL);
  const [intensity, setIntensity] = useState<string>(ALL);

  const [candidates, setCandidates] = useState<PerformanceCandidate[]>([]);
  const [emotionGuess, setEmotionGuess] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [selected, setSelected] = useState<Set<string>>(() => new Set(parseExistingRefs(content)));
  const [currentMtime, setCurrentMtime] = useState<string>(mtime);

  const [busy, setBusy] = useState<boolean>(false);
  const [toast, setToast] = useState<{ kind: "ok" | "err"; text: string } | null>(null);

  const [regenPrompt, setRegenPrompt] = useState<string | null>(null);

  // Re-pre-check selection when the underlying shot content changes (e.g. after
  // a save elsewhere reloads the file). Keep it cheap — only on content change.
  useEffect(() => {
    setSelected(new Set(parseExistingRefs(content)));
  }, [content]);

  const reload = useCallback(async () => {
    setLoading(true);
    try {
      const opts: Parameters<typeof performanceCandidates>[1] = { topN: 12 };
      if (emotion !== ALL) opts.emotion = emotion;
      if (intensity !== ALL) opts.intensity = Number(intensity);
      const res = await performanceCandidates(shotPath, opts);
      setCandidates(res.candidates);
      setEmotionGuess(res.shot_emotion_guess);
      setError(null);
    } catch (err) {
      const msg = err instanceof ApiError ? `${err.status} ${err.detail?.kind ?? ""}` : String(err);
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [shotPath, emotion, intensity]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const selectedIds = useMemo(() => Array.from(selected), [selected]);

  const toggle = useCallback((perfId: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(perfId)) next.delete(perfId);
      else next.add(perfId);
      return next;
    });
  }, []);

  const onSaveSelection = useCallback(async () => {
    setBusy(true);
    setToast(null);
    try {
      const res = await setShotPerformanceRefs(shotPath, selectedIds, currentMtime);
      setCurrentMtime(res.mtime);
      setToast({ kind: "ok", text: `已写回 表演库参考 标注（${selectedIds.length} 个）` });
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setToast({ kind: "err", text: "文件已被外部修改，请刷新后重试" });
      } else {
        const msg = err instanceof ApiError ? `保存失败: ${err.detail?.kind ?? err.status}` : String(err);
        setToast({ kind: "err", text: msg });
      }
    } finally {
      setBusy(false);
    }
  }, [shotPath, selectedIds, currentMtime]);

  const onRegen = useCallback(async () => {
    if (busy) return;
    setBusy(true);
    setToast(null);
    setRegenPrompt(null);
    try {
      const res = await regenShotPrompt(shotPath, selectedIds);
      if (!res.prompt) {
        setToast({ kind: "err", text: res.message || "无可重生成内容" });
      } else {
        setRegenPrompt(res.prompt);
        setToast({ kind: "ok", text: `已组装（引用 ${res.refs.join(", ")}）— 复制到 Claude session 跑，不直接触发` });
      }
    } catch (err) {
      const msg = err instanceof ApiError ? `失败: ${err.detail?.kind ?? err.status}` : String(err);
      setToast({ kind: "err", text: msg });
    } finally {
      setBusy(false);
    }
  }, [shotPath, selectedIds, busy]);

  const onCopyRegen = useCallback(async () => {
    if (!regenPrompt) return;
    try {
      await navigator.clipboard.writeText(regenPrompt);
      setToast({ kind: "ok", text: "已复制到剪贴板" });
    } catch {
      setToast({ kind: "err", text: "复制失败 — 请手动选中" });
    }
  }, [regenPrompt]);

  return (
    <section
      style={{
        border: "1px solid var(--border)",
        borderRadius: 8,
        padding: 12,
        margin: "12px 0",
        background: "var(--bg-panel)",
        color: "var(--text)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", marginBottom: 8 }}>
        <strong>🎭 演技库候选推荐</strong>
        {emotionGuess ? (
          <span style={{ fontSize: 12, color: "var(--text-muted)" }}>shot 情绪猜测：{emotionGuess}</span>
        ) : null}
        <select value={emotion} onChange={(e) => setEmotion(e.target.value)} disabled={busy} aria-label="筛选 情绪">
          <option value={ALL}>情绪: {ALL}</option>
          {EMOTION_OPTIONS.map((o) => (
            <option key={o} value={o}>情绪: {o}</option>
          ))}
        </select>
        <select value={intensity} onChange={(e) => setIntensity(e.target.value)} disabled={busy} aria-label="筛选 强度">
          <option value={ALL}>强度: {ALL}</option>
          {INTENSITY_OPTIONS.map((o) => (
            <option key={o} value={o}>强度: {o}</option>
          ))}
        </select>
        <button type="button" className="drama-rename-btn" disabled={busy || loading} onClick={() => void reload()}>
          {loading ? "拉取中…" : "↻ 刷新候选"}
        </button>
        <span style={{ fontSize: 12, color: "var(--text-muted)" }}>已选 {selectedIds.length}</span>
      </div>

      {toast ? (
        <div
          role="status"
          aria-live="polite"
          style={{ fontSize: 12, marginBottom: 8, color: toast.kind === "err" ? "#e06c6c" : "#6cc26c" }}
        >
          {toast.text}
        </div>
      ) : null}

      {error ? (
        <div role="alert" className="save-error-banner">{error}</div>
      ) : loading ? (
        <div className="muted">加载候选…</div>
      ) : candidates.length === 0 ? (
        <p className="muted">没有匹配的演技库候选 — 调整情绪/强度筛选。</p>
      ) : (
        <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: 8 }}>
          {candidates.map((c) => {
            const checked = selected.has(c.perf_id);
            return (
              <li
                key={c.perf_id}
                style={{
                  border: `1px solid ${checked ? "#6cc26c" : "var(--border)"}`,
                  borderRadius: 6,
                  padding: 8,
                  background: "var(--bg)",
                  display: "flex",
                  gap: 10,
                  alignItems: "flex-start",
                }}
              >
                <input
                  type="checkbox"
                  checked={checked}
                  disabled={busy}
                  onChange={() => toggle(c.perf_id)}
                  aria-label={`选择 ${c.title || c.perf_id}`}
                  style={{ marginTop: 4 }}
                />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "baseline" }}>
                    <strong style={{ fontSize: 13 }}>{c.title || c.perf_id}</strong>
                    <span style={{ fontSize: 11, color: "var(--text-muted)" }}>
                      {c.emotion} · 强度{c.intensity} · {c.style} · {c.carrier} · {c.duration_s}s · 分{c.score.toFixed(2)}
                    </span>
                  </div>
                  {c.preview ? (
                    <pre
                      style={{
                        fontSize: 11,
                        fontFamily: "monospace",
                        whiteSpace: "pre-wrap",
                        margin: "6px 0 0",
                        color: "var(--text-muted)",
                        maxHeight: 120,
                        overflow: "auto",
                      }}
                    >
                      {c.preview}
                    </pre>
                  ) : null}
                </div>
                {c.mp4_rel_path ? (
                  <video
                    controls
                    preload="metadata"
                    src={mediaUrl(c.mp4_rel_path)}
                    style={{ width: 120, borderRadius: 4, flexShrink: 0 }}
                  />
                ) : null}
              </li>
            );
          })}
        </ul>
      )}

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 10, alignItems: "center" }}>
        <button type="button" className="drama-rename-btn" disabled={busy} onClick={() => void onSaveSelection()}>
          {busy ? "保存中…" : "💾 保存选择"}
        </button>
        <button
          type="button"
          className="drama-rename-btn"
          disabled={busy || selectedIds.length === 0}
          onClick={() => void onRegen()}
          title="按选中的演技库条目组装重生成 prompt — 复制到 Claude session 跑，不直接触发渲染"
        >
          🎬 按选择重生成
        </button>
        {regenPrompt ? (
          <button type="button" className="drama-rename-btn" onClick={() => void onCopyRegen()}>
            📋 复制
          </button>
        ) : null}
      </div>

      {regenPrompt ? (
        <>
          <p style={{ fontSize: 12, color: "var(--text-muted)", margin: "8px 0 4px" }}>
            复制到 Claude session 跑，不直接触发渲染。
          </p>
          <textarea
            readOnly
            value={regenPrompt}
            rows={14}
            style={{
              width: "100%",
              boxSizing: "border-box",
              fontFamily: "monospace",
              fontSize: 12,
              background: "var(--bg)",
              color: "var(--text)",
              border: "1px solid var(--border)",
              borderRadius: 6,
              padding: 8,
            }}
          />
        </>
      ) : null}
    </section>
  );
}
