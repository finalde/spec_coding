import { useCallback, useEffect, useState } from "react";
import {
  scoreEpisodeSeams,
  type EpisodeLang,
  type SeamMethodScore,
  type SeamMetricsResult,
} from "../api";

const LANG_LABEL: Record<EpisodeLang, string> = {
  original: "原片", zh: "中文", en: "EN", both: "中英",
};

interface Props {
  path: string;
  lang: EpisodeLang;
  onClose: () => void;
}

function gradeClass(score: number | null | undefined): string {
  if (score == null) return "";
  if (score >= 90) return "grade-a";
  if (score >= 80) return "grade-b";
  if (score >= 70) return "grade-c";
  return "grade-d";
}

/** Tiered rank: candidates clearing the 80-floor on every metric come first, then by
 * weighted score (mirrors seam_metrics.rank_key so UI order == tool's pick). */
function rankKey(m: SeamMethodScore): number {
  if (m.error || m.score == null) return -1;
  return (m.floor_pass ? 1e6 : 0) + m.score;
}

const METRIC_KEYS: { key: keyof SeamMethodScore; raw: string }[] = [
  { key: "M1_velocity", raw: "vel_break_pxf" },
  { key: "M2_no_freeze", raw: "min_ratio" },
  { key: "M3_no_jump", raw: "peak_ratio" },
  { key: "M4_junction_ssim", raw: "ssim" },
];

/** A horizontal 0–100 bar for one metric or the seam total. */
function ScoreBar({ value }: { value: number | undefined }) {
  const v = value ?? 0;
  return (
    <div className="seam-score-bar">
      <div className={`seam-score-bar-fill ${gradeClass(v)}`} style={{ width: `${v}%` }} />
      <span className="seam-score-bar-num">{v.toFixed(0)}</span>
    </div>
  );
}

/** One method row inside a seam (chosen plan or a ranked panel candidate). */
function MethodRow({ m, rank, isChosen, isBest }: {
  m: SeamMethodScore; rank: number; isChosen: boolean; isBest: boolean;
}) {
  if (m.error) {
    return <div className="seam-score-method err">{m.label ?? m.method}: {m.error}</div>;
  }
  return (
    <div className={`seam-score-method${isChosen ? " chosen" : ""}${isBest ? " best" : ""}`}>
      <div className="seam-score-method-head">
        <span className="seam-score-rank">{rank}</span>
        <span className="seam-score-label">{m.label ?? m.method}</span>
        <span className={`seam-score-tag floor ${m.floor_pass ? "ok" : "fail"}`}
          title={m.floor_pass ? "四项指标全部 ≥80" : `有指标低于 80（最低 ${m.min_metric}）`}>
          {m.floor_pass ? "✓全≥80" : `✗最低${m.min_metric ?? "?"}`}
        </span>
        {isBest && <span className="seam-score-tag best">★最佳</span>}
        {isChosen && <span className="seam-score-tag chosen">当前plan</span>}
        <strong className={`seam-score-total ${gradeClass(m.score)}`}>
          {m.score?.toFixed(1)}
        </strong>
      </div>
      <div className="seam-score-metrics">
        {METRIC_KEYS.map(({ key, raw }) => {
          const metric = m[key] as { score: number; [k: string]: number } | undefined;
          if (!metric) return null;
          return (
            <div key={String(key)} className="seam-score-metric">
              <span className="seam-score-metric-id">{String(key).slice(0, 2)}</span>
              <ScoreBar value={metric.score} />
              <span className="seam-score-metric-raw">{metric[raw]}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/** Seam-quality dashboard: runs the objective optical-flow + SSIM scorer over the
 * episode's 承接 seams and shows per-metric scores, a ranked method panel, the metric
 * definitions, and the current-plan grade vs the achievable ceiling. */
export function SeamScoreDashboard({ path, lang, onClose }: Props) {
  const [data, setData] = useState<SeamMetricsResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  // Comparison (硬拼/裁切/RIFE panel) is several× slower — opt-in. First load scores
  // only the current plan so the dashboard appears quickly.
  const [compare, setCompare] = useState(false);

  const run = useCallback((withCompare: boolean) => {
    setLoading(true);
    setError(null);
    setData(null);
    scoreEpisodeSeams(path, lang, withCompare)
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false));
  }, [path, lang]);

  useEffect(() => { run(compare); }, [run, compare]);

  return (
    <div className="seam-modal-backdrop" role="dialog" aria-modal="true"
      aria-label="接缝评分" onClick={onClose}>
      <div className="seam-modal seam-score-modal" onClick={(e) => e.stopPropagation()}>
        <header className="seam-modal-head">
          <div>
            <strong>📊 接缝质量评分 · {LANG_LABEL[lang]}</strong>
            {data && (
              <span className="seam-modal-sub">
                {data.n_seams} 个承接缝 · 光流 + SSIM 客观度量
              </span>
            )}
          </div>
          <div className="seam-score-head-actions">
            <label className="seam-score-compare" title="对每个缝额外跑 硬拼/裁切/RIFE 多种接法并排名（较慢，多耗时数倍）">
              <input type="checkbox" checked={compare} disabled={loading}
                onChange={(e) => setCompare(e.target.checked)} />
              对比多种接法
            </label>
            <button type="button" className="seam-btn" onClick={() => run(compare)} disabled={loading}>
              {loading ? "⏳ 评分中…" : "↻ 重新评分"}
            </button>
            <button type="button" className="seam-modal-x" onClick={onClose}
              aria-label="关闭">✕</button>
          </div>
        </header>

        <div className="seam-modal-body">
          {error && <div className="seam-modal-error">⚠ {error}</div>}
          {loading && !error && (
            <div className="seam-modal-loading">
              正在解码 + 计算光流/SSIM（每缝建临时拼接并打分）…
              {compare ? "对比多种接法，约需一两分钟" : "仅评当前 plan，约需数十秒"}
            </div>
          )}

          {data && (
            <>
              <div className="seam-score-summary">
                <div className={`seam-score-big ${gradeClass(data.overall)}`}>
                  <span className="seam-score-big-num">{data.overall?.toFixed(1) ?? "—"}</span>
                  <span className="seam-score-big-grade">{data.overall_grade ?? ""}</span>
                  <span className="seam-score-big-cap">当前 seam_plan</span>
                </div>
                <div className="seam-score-big ceiling">
                  <span className="seam-score-big-num">{data.ceiling?.toFixed(1) ?? "—"}</span>
                  <span className="seam-score-big-grade">{data.ceiling_grade ?? ""}</span>
                  <span className="seam-score-big-cap">各缝最优上限</span>
                </div>
                <div className="seam-score-big">
                  <span className="seam-score-big-num">{data.weakest?.toFixed(1) ?? "—"}</span>
                  <span className="seam-score-big-grade">最弱缝</span>
                  <span className="seam-score-big-cap">短板</span>
                </div>
              </div>

              <details className="seam-score-defs" open>
                <summary>指标定义（权重 {data.metric_defs.map((d) => `${d.id} ${d.weight}`).join(" · ")}）</summary>
                <ul>
                  {data.metric_defs.map((d) => (
                    <li key={d.id}>
                      <strong>{d.id} {d.name}</strong>（权重 {d.weight}）— {d.desc}
                      <span className="seam-score-def-thr"> 好：{d.good} ｜ 差：{d.bad}</span>
                    </li>
                  ))}
                </ul>
              </details>

              {data.seams.map((s) => {
                const cands = [s.chosen, ...s.panel].filter((x) => !x.error);
                cands.sort((a, b) => rankKey(b) - rankKey(a));  // floor-tier, then score
                return (
                  <div key={s.seam} className="seam-score-seam">
                    <div className="seam-score-seam-head">
                      {s.seam}
                      {s.time && (
                        <span className="seam-score-seam-time">
                          首尾帧接合处 @{s.time.at_s}s（{s.time.start_s}–{s.time.end_s}s）
                        </span>
                      )}
                    </div>
                    {cands.map((m, i) => (
                      <MethodRow key={(m.label ?? "") + i} m={m} rank={i + 1}
                        isChosen={(m.label ?? "").includes("CHOSEN")}
                        isBest={i === 0} />
                    ))}
                  </div>
                );
              })}
            </>
          )}
        </div>

        <footer className="seam-modal-foot">
          <span className="seam-score-foot-note">
            排名规则：先看四项指标是否全 ≥80（✓/✗），全过的优先；同档再按加权分。都过不了 80 时按加权分取最好。★=该缝数据最优。
          </span>
          <button type="button" className="seam-btn seam-btn--primary" onClick={onClose}>
            关闭
          </button>
        </footer>
      </div>
    </div>
  );
}
