/** WorkflowPage — interactive end-to-end view of the AI 短剧 production pipeline.
 *
 * Two views over the same data (workflowData.ts):
 *   - 卡片视图: rich, readable per-stage cards (读 / 内建提问 / 避坑) + QC gates.
 *   - 流程图谱: one Mermaid overview of the whole pipeline; stage nodes are clickable.
 * Clicking any stage (a card's drill button OR a graph node) opens StageDrawer —
 * a right-side window showing that stage's internal-flow diagram + fields. That
 * drawer is the extension point for future per-stage detail/features.
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  GLOBAL_DEFAULTS,
  MECHANISMS,
  PIPELINE_DIAGRAM,
  REVIEW_SUITE,
  STAGES,
  type Layer,
  type Stage,
} from "../lib/workflowData";
import { Mermaid } from "./Mermaid";
import { StageDrawer } from "./StageDrawer";

type View = "cards" | "graph";

const LAYER_CLASS: Record<Layer, string> = {
  横切: "wf-layer-cut",
  单镜: "wf-layer-shot",
  整集: "wf-layer-ep",
  全剧: "wf-layer-drama",
  "整集+全剧": "wf-layer-drama",
};

function StageCard({ stage, onOpen }: { stage: Stage; onOpen: (s: Stage) => void }): JSX.Element {
  const [open, setOpen] = useState<boolean>(false);
  return (
    <div className="wf-stage" style={{ ["--wf-accent" as string]: stage.accent }}>
      <div className="wf-stage-head">
        <button type="button" className="wf-stage-headmain" aria-expanded={open} onClick={() => setOpen((o) => !o)}>
          <span className="wf-stage-num">{stage.n}</span>
          <span className="wf-stage-title">{stage.title}</span>
          <code className="wf-stage-out">{stage.output}</code>
          <span className="wf-stage-toggle" aria-hidden="true">{open ? "▾" : "▸"}</span>
        </button>
        <button
          type="button"
          className="wf-stage-drill"
          title="打开内部细节流程图"
          aria-label={`打开阶段 ${stage.n} 内部细节流程图`}
          onClick={() => onOpen(stage)}
        >
          🔍 内部流程
        </button>
      </div>
      {open ? (
        <div className="wf-stage-body">
          <div className="wf-col">
            <h4>读（pre-reading）</h4>
            <ul>{stage.reads.map((r) => <li key={r}><code>{r}</code></li>)}</ul>
          </div>
          <div className="wf-col">
            <h4>内建提问清单（interactive）</h4>
            <ul>{stage.asks.map((a) => <li key={a}>{a}</li>)}</ul>
          </div>
          <div className="wf-col">
            <h4>避坑</h4>
            <ul>{stage.pitfalls.map((p) => <li key={p}>{p}</li>)}</ul>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function QcGate({ stage }: { stage: Stage }): JSX.Element {
  const human = stage.qc.includes("人工确认");
  return (
    <div className="wf-gate">
      <span className="wf-gate-icon" aria-hidden="true">⛬</span>
      <div className="wf-gate-main">
        <div className="wf-gate-skills">
          {stage.qc.map((s) =>
            s === "人工确认" ? (
              <span key={s} className="wf-skill-chip wf-skill-human">👤 人工确认</span>
            ) : (
              <span key={s} className="wf-skill-chip">{s}</span>
            ),
          )}
        </div>
        <p className="wf-gate-label">{stage.qcLabel}</p>
        <p className="wf-gate-pass">{human ? "确认齐全 → 进下一步" : "blocker = 0（严格度 = 严）→ 进下一步，否则回修"}</p>
      </div>
    </div>
  );
}

export function WorkflowPage(): JSX.Element {
  const [view, setView] = useState<View>("cards");
  const [active, setActive] = useState<Stage | null>(null);
  const [suiteOpen, setSuiteOpen] = useState<boolean>(false);

  const stageByN = useMemo(() => new Map(STAGES.map((s) => [s.n, s])), []);

  const openStage = useCallback((s: Stage) => setActive(s), []);

  // The overview Mermaid binds `click sN call wfStageClick("N")`; register it.
  useEffect(() => {
    const w = window as unknown as { wfStageClick?: (n: string) => void };
    w.wfStageClick = (n: string) => {
      const s = stageByN.get(Number(n));
      if (s) setActive(s);
    };
    return () => {
      delete w.wfStageClick;
    };
  }, [stageByN]);

  return (
    <div className="wf-view">
      <header className="wf-header">
        <div className="wf-titlerow">
          <h1>AI 短剧 · 端到端工作流</h1>
          <div className="wf-viewtoggle" role="tablist" aria-label="视图切换">
            <button type="button" role="tab" aria-selected={view === "cards"} className={view === "cards" ? "active" : ""} onClick={() => setView("cards")}>
              📋 卡片视图
            </button>
            <button type="button" role="tab" aria-selected={view === "graph"} className={view === "graph" ? "active" : ""} onClick={() => setView("graph")}>
              🗺 流程图谱
            </button>
          </div>
        </div>
        <p className="muted">
          <code>ai_videos__全流程编排</code> — 脑洞 → 立项 → 世界观人设 → 分集大纲 → 文学剧本 → 分镜运镜 →
          标准化分镜 Prompt。六阶段，每阶段先问你、再生成、再过 QC 关卡。点任一阶段看其<strong>内部细节流程图</strong>。本期到出 prompt 即止（阶段 7 渲染剪辑暂不做）。
        </p>
        <div className="wf-defaults">
          <strong>锁定全局默认：</strong>
          <span className="muted">{GLOBAL_DEFAULTS}</span>
        </div>
      </header>

      {view === "cards" ? (
        <section aria-label="六阶段主线（卡片）" className="wf-pipeline">
          {STAGES.map((stage, i) => (
            <div key={stage.n} className="wf-stage-wrap">
              <StageCard stage={stage} onOpen={openStage} />
              <QcGate stage={stage} />
              {i < STAGES.length - 1 ? <div className="wf-arrow" aria-hidden="true">↓</div> : null}
            </div>
          ))}
          <div className="wf-done">✓ 本期产出：标准化 AI 分镜 Prompt（阶段 7 渲染剪辑暂不做）</div>
        </section>
      ) : (
        <section aria-label="六阶段主线（图谱）" className="wf-graph">
          <p className="muted wf-graph-hint">点击任一阶段方块 → 打开内部细节流程图。</p>
          <Mermaid chart={PIPELINE_DIAGRAM} className="wf-graph-host" />
        </section>
      )}

      <section className="wf-mechanisms" aria-label="三大贯穿机制">
        <h2>三大贯穿机制</h2>
        <div className="wf-mech-grid">
          {MECHANISMS.map((m) => (
            <div key={m.title} className="wf-mech-card">
              <h3>{m.title}</h3>
              <p>{m.body}</p>
            </div>
          ))}
        </div>
        <div className="wf-agile">
          <strong>敏捷原则：</strong>大方向先定、每集剧情边拍边改 — 阶段 1–3 只定骨架 + 前几集细纲，后续各集留松、推进到该集再细化、随 feedback 临时调整、不绑死。
        </div>
      </section>

      <section className="wf-suite" aria-label="审查总编排调用顺序">
        <button type="button" className="wf-suite-head" aria-expanded={suiteOpen} onClick={() => setSuiteOpen((o) => !o)}>
          <span className="wf-stage-toggle" aria-hidden="true">{suiteOpen ? "▾" : "▸"}</span>
          <h2>审查总编排（review suite）调用顺序 · 0 → 9</h2>
          <span className="muted">机械先行 → 单镜审美 → 整集 → 全剧</span>
        </button>
        {suiteOpen ? (
          <ol className="wf-suite-list">
            {REVIEW_SUITE.map((s) => (
              <li key={s.ord} className="wf-suite-step">
                <span className="wf-suite-ord">{s.ord}</span>
                <span className={`wf-layer-chip ${LAYER_CLASS[s.layer]}`}>{s.layer}</span>
                <code className="wf-suite-skill">{s.skill}</code>
                {s.conditional ? <span className="wf-suite-cond">{s.conditional}</span> : null}
                <span className="wf-suite-duty">{s.duty}</span>
              </li>
            ))}
          </ol>
        ) : (
          <p className="muted wf-suite-hint">阶段 6 出片前对每个 shot / ep 跑这整套；点击展开看 13 步调用链与作用层。</p>
        )}
      </section>

      <StageDrawer stage={active} onClose={() => setActive(null)} />
    </div>
  );
}
