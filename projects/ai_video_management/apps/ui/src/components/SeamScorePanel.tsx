import { useCallback, useEffect, useState } from "react";
import {
  readEpisodeSeamScores,
  type EpisodeLang,
  type SeamMethodScore,
  type SeamMetricsResult,
} from "../api";
import { SeamScoreDashboard } from "./SeamScoreDashboard";

function gradeClass(score: number | null | undefined): string {
  if (score == null) return "";
  if (score >= 90) return "grade-a";
  if (score >= 80) return "grade-b";
  if (score >= 70) return "grade-c";
  return "grade-d";
}

const METRIC_KEYS: { key: keyof SeamMethodScore; raw: string; id: string }[] = [
  { key: "M1_velocity", raw: "vel_break_pxf", id: "M1速度" },
  { key: "M2_no_freeze", raw: "min_ratio", id: "M2冻结" },
  { key: "M3_no_jump", raw: "peak_ratio", id: "M3跳变" },
  { key: "M4_junction_ssim", raw: "ssim", id: "M4结构" },
];

/** Always-on inline scorecard for an episode page: auto-loads the PERSISTED scorecard
 * (last build's score — instant, no recompute) and shows the overall grade + each
 * 首尾帧承接 seam's score, timeline position, and M1–M4 breakdown. The 详情/对比 button
 * opens the full dashboard for a live recompute + multi-method comparison. */
export function SeamScorePanel({ path, lang = "original" }: {
  path: string; lang?: EpisodeLang;
}) {
  const [data, setData] = useState<SeamMetricsResult | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const load = useCallback(() => {
    readEpisodeSeamScores(path, lang)
      .then((d) => setData(d.persisted === false ? null : d))
      .catch(() => setData(null))
      .finally(() => setLoaded(true));
  }, [path, lang]);

  useEffect(() => { load(); }, [load]);

  if (!loaded) return null;

  if (!data || !data.seams?.length) {
    return (
      <div className="seam-panel seam-panel--empty">
        <span>📊 接缝评分：尚未评分（生成成片后自动评分；或点</span>
        <button type="button" className="seam-panel-link" onClick={() => setShowModal(true)}>
          立即评分
        </button>
        <span>）</span>
        {showModal && (
          <SeamScoreDashboard path={path} lang={lang} onClose={() => setShowModal(false)} />
        )}
      </div>
    );
  }

  return (
    <div className="seam-panel">
      <div className="seam-panel-head">
        <span className="seam-panel-title">📊 接缝评分（首尾帧承接处）</span>
        <span className={`seam-panel-overall ${gradeClass(data.overall)}`}>
          {data.overall?.toFixed(1)} <small>{data.overall_grade}</small>
        </span>
        {data.generated_at && (
          <span className="seam-panel-time">最近生成 {data.generated_at.replace("T", " ").replace("+00:00", " UTC")}</span>
        )}
        <button type="button" className="seam-panel-link" onClick={() => setShowModal(true)}>
          详情 / 重新评分 / 对比接法 →
        </button>
      </div>
      <div className="seam-panel-seams">
        {data.seams.map((s) => {
          const c = s.chosen;
          if (c.error) {
            return <div key={s.seam} className="seam-panel-seam err">{s.seam}: {c.error}</div>;
          }
          return (
            <div key={s.seam} className="seam-panel-seam">
              <div className="seam-panel-seam-head">
                <span className="seam-panel-seam-name">{s.seam}</span>
                {s.time && (
                  <span className="seam-panel-seam-time">@{s.time.at_s}s（{s.time.start_s}–{s.time.end_s}s）</span>
                )}
                <span className="seam-panel-seam-method">{c.method} trim={c.trim}{c.depth != null ? ` d${c.depth}` : ""}</span>
                <span className={`seam-panel-floor ${c.floor_pass ? "ok" : "fail"}`}
                  title={c.floor_pass ? "四项指标全部 ≥80" : `有指标低于 80（最低 ${c.min_metric}）`}>
                  {c.floor_pass ? "✓全≥80" : `✗最低${c.min_metric ?? "?"}`}
                </span>
                <strong className={`seam-panel-seam-score ${gradeClass(c.score)}`}>{c.score?.toFixed(1)}</strong>
              </div>
              <div className="seam-panel-metrics">
                {METRIC_KEYS.map(({ key, raw, id }) => {
                  const m = c[key] as { score: number; [k: string]: number } | undefined;
                  if (!m) return null;
                  return (
                    <span key={String(key)} className="seam-panel-metric" title={`${id}: ${m.score} (raw ${m[raw]})`}>
                      <span className="seam-panel-metric-id">{id}</span>
                      <span className={`seam-panel-metric-val ${gradeClass(m.score)}`}>{m.score.toFixed(0)}</span>
                    </span>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
      {showModal && (
        <SeamScoreDashboard path={path} lang={lang} onClose={() => setShowModal(false)} />
      )}
    </div>
  );
}
