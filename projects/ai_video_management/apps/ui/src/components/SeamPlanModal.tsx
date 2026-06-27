import { useCallback, useEffect, useMemo, useState } from "react";
import {
  analyzeEpisodeSeams,
  concatEpisode,
  type EpisodeLang,
  type SeamInfo,
  type SeamPlanEntry,
} from "../api";

const LANG_LABEL: Record<EpisodeLang, string> = {
  original: "原片",
  zh: "中文",
  en: "EN",
  both: "中英",
};

// 补帧密度 = 桥接处插入多少帧。depth d → 2^d − 1 帧。越密过渡越平滑、渲染越慢，
// 且当两帧差异较大时越容易出现拖影；自动 = 按裁切时长估算（通常 3~7 帧）。
const DEPTH_OPTIONS: { value: string; label: string }[] = [
  { value: "", label: "自动" },
  { value: "1", label: "1 · 最疏(插1帧)" },
  { value: "2", label: "2 · 插3帧" },
  { value: "3", label: "3 · 插7帧" },
  { value: "4", label: "4 · 最密(插15帧)" },
];

const TRIM_HELP =
  "裁切：从接缝两侧各裁掉多少秒的「减速/加速」尾巴，再用补帧把这段运动接回。" +
  "越大(如 0.16)裁得越狠、去顿挫更彻底但丢的原片更多；越小(如 0.10)更保守。默认 0.10。" +
  "0 = 不裁切，仅在接缝处插补帧平滑、不丢任何原片。";
const DEPTH_HELP =
  "补帧密度：桥接处插入的帧数。最疏(1)=插1帧，最密(4)=插15帧。" +
  "越密过渡越平滑、渲染越慢；两帧差异大时过密反而易糊。自动=按裁切量估算。";
const RIFE_HELP =
  "RIFE 补帧：在裁切后的接缝处用光流插出中间帧，把运动接回。" +
  "勾选=裁切+补帧（两帧差异较大时用）；不勾=只裁切平接、不补帧（承接缝已基本连续时最平滑）。" +
  "裁切秒=0 则不裁切、仅补帧。";

interface SeamChoice {
  method: "butt" | "trim" | "rife";
  trim: number;
  depth: number | null;
}

interface Props {
  path: string;
  lang: EpisodeLang;
  onClose: () => void;
  onDone: (summary: string) => void;
}

/** Per-seam stitch planner: lists every shot→shot junction with thumbnails + a
 * frame-diff suggestion. 硬切 junctions are locked to 硬拼; 承接 junctions let the
 * user pick 硬拼 / RIFE (+ trim + 补帧密度). 生成 builds with the chosen plan, which
 * the backend persists to seam_plan.json for reproducible regen. */
export function SeamPlanModal({ path, lang, onClose, onDone }: Props) {
  const [seams, setSeams] = useState<SeamInfo[] | null>(null);
  const [choices, setChoices] = useState<Record<number, SeamChoice>>({});
  const [hadSavedPlan, setHadSavedPlan] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [building, setBuilding] = useState(false);

  useEffect(() => {
    let alive = true;
    setSeams(null);
    setError(null);
    analyzeEpisodeSeams(path, lang)
      .then((res) => {
        if (!alive) return;
        setSeams(res.seams);
        setHadSavedPlan(res.has_saved_plan);
        const init: Record<number, SeamChoice> = {};
        for (const s of res.seams) {
          init[s.index] = {
            method: s.link === "hardcut" ? "butt" : s.method,
            trim: s.trim,
            depth: s.depth,
          };
        }
        setChoices(init);
      })
      .catch((e) => alive && setError(String(e?.message ?? e)));
    return () => {
      alive = false;
    };
  }, [path, lang]);

  const handoffCount = useMemo(
    () => (seams ?? []).filter((s) => s.link === "handoff").length,
    [seams],
  );
  const rifeCount = useMemo(
    () => Object.values(choices).filter((c) => c.method === "rife").length,
    [choices],
  );
  const trimCount = useMemo(
    () => Object.values(choices).filter((c) => c.method === "trim").length,
    [choices],
  );

  const setChoice = useCallback((index: number, patch: Partial<SeamChoice>) => {
    setChoices((prev) => ({ ...prev, [index]: { ...prev[index], ...patch } }));
  }, []);

  const onGenerate = useCallback(async () => {
    if (!seams) return;
    setBuilding(true);
    setError(null);
    try {
      const plan: SeamPlanEntry[] = seams.map((s) => {
        const c = choices[s.index];
        return {
          from: s.from,
          to: s.to,
          method: c.method,
          // 裁切 & RIFE both carry a trim; only RIFE carries 补帧密度.
          trim: c.method === "butt" ? null : c.trim,
          depth: c.method === "rife" ? c.depth : null,
        };
      });
      const res = await concatEpisode(path, lang, false, plan);
      let summary = res.out
        ? `已合成 ${res.out.split("/").pop()} — 拼接 ${res.used.length} 个镜头 · RIFE 补帧 ${res.rife_bridges} 处`
        : "未生成 — 没有可用镜头";
      if (res.skipped.length > 0) summary += ` · 跳过 ${res.skipped.length}`;
      onDone(summary);
      onClose();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBuilding(false);
    }
  }, [seams, choices, path, lang, onDone, onClose]);

  return (
    <div className="seam-modal-backdrop" role="dialog" aria-modal="true"
      aria-label="拼接方案" onClick={onClose}>
      <div className="seam-modal" onClick={(e) => e.stopPropagation()}>
        <header className="seam-modal-head">
          <div>
            <strong>拼接方案 · {LANG_LABEL[lang]}</strong>
            {seams && (
              <span className="seam-modal-sub">
                {seams.length} 个衔接 · 承接 {handoffCount} · 本次 裁切 {trimCount} · RIFE {rifeCount}
                {hadSavedPlan ? " · 已载入保存的方案" : ""}
              </span>
            )}
          </div>
          <button type="button" className="seam-modal-x" onClick={onClose}
            aria-label="关闭">✕</button>
        </header>

        <div className="seam-modal-body">
          <div className="seam-legend">
            <p>
              <strong>硬拼</strong>：直接拼接、不裁不补（硬切缝只能硬拼）。
              <strong> 不硬拼</strong>：裁掉接缝两侧的减速/加速尾巴+重复帧（裁切秒），
              可再勾 <strong>RIFE 补帧</strong> 把运动接回 —— 仅<strong>承接缝</strong>（有首尾帧）可用。
            </p>
            <p>
              <strong>裁切(秒)</strong>：从两侧各裁掉多少「减速/加速」尾巴；
              <strong>0.10</strong> 保守、<strong>0.16</strong> 更狠（丢的原片更多）、
              <strong>0</strong>=不裁切仅补帧。承接缝已基本连续时不勾 RIFE 最平滑。
            </p>
            <p>
              <strong>RIFE / 密度</strong>：勾 RIFE 才补中间帧；密度=补几帧，
              <strong>最疏=1帧</strong>、<strong>最密=15帧</strong>（两帧差异大时过密易糊），
              <strong>自动</strong>按裁切量估算。
            </p>
          </div>
          {error && <div className="seam-modal-error">⚠ {error}</div>}
          {!seams && !error && <div className="seam-modal-loading">分析衔接中…</div>}
          {seams?.map((s) => {
            const c = choices[s.index];
            if (!c) return null;
            const isHandoff = s.link === "handoff";
            return (
              <div key={s.index}
                className={`seam-row${isHandoff ? "" : " seam-row--hardcut"}`}>
                <div className="seam-thumbs">
                  <img src={s.thumb_a} alt={`${s.from} 末帧`} />
                  <span className="seam-arrow">→</span>
                  <img src={s.thumb_b} alt={`${s.to} 首帧`} />
                </div>
                <div className="seam-meta">
                  <div className="seam-title">
                    {s.from} → {s.to}
                    <span className={`seam-badge seam-badge--${s.link}`}>
                      {isHandoff ? "承接" : "硬切"}
                    </span>
                  </div>
                  {isHandoff ? (
                    <div className="seam-hint">
                      帧差 {s.diff == null ? "?" : s.diff.toFixed(0)} · 建议
                      {s.suggest === "rife"
                        ? " 不硬拼 + RIFE 补帧"
                        : s.suggest === "trim"
                          ? " 不硬拼 · 裁切平滑"
                          : " 硬拼"}
                    </div>
                  ) : (
                    <div className="seam-hint">无首尾帧 · 仅硬拼</div>
                  )}
                </div>
                <div className="seam-controls">
                  {isHandoff ? (
                    <>
                      <div className="seam-method">
                        <button type="button"
                          className={c.method === "butt" ? "active" : ""}
                          onClick={() => setChoice(s.index, { method: "butt" })}>
                          硬拼
                        </button>
                        <button type="button"
                          className={c.method !== "butt" ? "active" : ""}
                          onClick={() => setChoice(s.index,
                            { method: c.method === "butt" ? "trim" : c.method })}>
                          不硬拼
                        </button>
                      </div>
                      {c.method !== "butt" && (
                        <div className="seam-params">
                          <label title={TRIM_HELP}>裁切秒 ⓘ
                            <input type="number" min={0} max={0.4} step={0.02}
                              value={c.trim} title={TRIM_HELP}
                              onChange={(e) =>
                                setChoice(s.index, { trim: Number(e.target.value) })} />
                          </label>
                          <label className="seam-rife-toggle" title={RIFE_HELP}>
                            <input type="checkbox" checked={c.method === "rife"}
                              onChange={(e) => setChoice(s.index,
                                { method: e.target.checked ? "rife" : "trim" })} />
                            RIFE 补帧 ⓘ
                          </label>
                          {c.method === "rife" && (
                            <label title={DEPTH_HELP}>密度 ⓘ
                              <select value={c.depth == null ? "" : String(c.depth)}
                                title={DEPTH_HELP}
                                onChange={(e) => setChoice(s.index, {
                                  depth: e.target.value === "" ? null : Number(e.target.value),
                                })}>
                                {DEPTH_OPTIONS.map((o) => (
                                  <option key={o.value} value={o.value}>{o.label}</option>
                                ))}
                              </select>
                            </label>
                          )}
                        </div>
                      )}
                    </>
                  ) : (
                    <span className="seam-locked">硬拼</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        <footer className="seam-modal-foot">
          <button type="button" className="seam-btn" onClick={onClose}
            disabled={building}>取消</button>
          <button type="button" className="seam-btn seam-btn--primary"
            onClick={onGenerate} disabled={!seams || building}>
            {building ? "⏳ 生成中…" : "🎬 生成"}
          </button>
        </footer>
      </div>
    </div>
  );
}
