/** StageDrawer — the per-stage drill-down "window".
 *
 * Slides in from the right when a stage box is clicked (from either the card view
 * or the overview graph). Renders that stage's internal-flow Mermaid diagram plus
 * its structured fields (产物 / 读 / 内建提问 / QC / 避坑). This is the surface to
 * grow: add tabs, live project status, per-shot drill-down, etc. — all keyed off
 * the Stage object from workflowData.
 */
import { useEffect } from "react";
import type { Stage } from "../lib/workflowData";
import { Mermaid } from "./Mermaid";

export interface StageDrawerProps {
  stage: Stage | null;
  onClose: () => void;
}

export function StageDrawer({ stage, onClose }: StageDrawerProps): JSX.Element | null {
  useEffect(() => {
    if (!stage) return;
    const onKey = (e: KeyboardEvent): void => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [stage, onClose]);

  if (!stage) return null;
  return (
    <div className="drawer-overlay" onClick={onClose}>
      <aside
        className="stage-drawer"
        role="dialog"
        aria-modal="true"
        aria-label={`阶段 ${stage.n} 内部细节`}
        style={{ ["--wf-accent" as string]: stage.accent }}
        onClick={(e) => e.stopPropagation()}
      >
        <header className="stage-drawer-head">
          <span className="wf-stage-num">{stage.n}</span>
          <h2>{stage.title}</h2>
          <button type="button" className="stage-drawer-close" aria-label="关闭" onClick={onClose}>
            ×
          </button>
        </header>
        <div className="stage-drawer-body">
          <p className="stage-drawer-out">
            产物落点：<code>{stage.output}</code>
          </p>

          <h3>内部细节流程</h3>
          <div className="stage-drawer-diagram">
            <Mermaid chart={stage.detailDiagram} />
          </div>

          <div className="stage-drawer-grid">
            <section>
              <h4>读（pre-reading）</h4>
              <ul>{stage.reads.map((r) => <li key={r}><code>{r}</code></li>)}</ul>
            </section>
            <section>
              <h4>内建提问清单</h4>
              <ul>{stage.asks.map((a) => <li key={a}>{a}</li>)}</ul>
            </section>
            <section>
              <h4>QC 关卡</h4>
              <div className="wf-gate-skills">
                {stage.qc.map((s) =>
                  s === "人工确认" ? (
                    <span key={s} className="wf-skill-chip wf-skill-human">👤 人工确认</span>
                  ) : (
                    <span key={s} className="wf-skill-chip">{s}</span>
                  ),
                )}
              </div>
              <p className="stage-drawer-qclabel">{stage.qcLabel}</p>
            </section>
            <section>
              <h4>避坑</h4>
              <ul>{stage.pitfalls.map((p) => <li key={p}>{p}</li>)}</ul>
            </section>
          </div>
        </div>
      </aside>
    </div>
  );
}
