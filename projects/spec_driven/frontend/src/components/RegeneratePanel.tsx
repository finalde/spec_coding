import { useEffect, useMemo, useState } from "react";
import { fetchStages, postRegenPrompt } from "../api";
import { useAutonomousMode } from "../autonomousMode";
import type { RegenResult, Stage } from "../types";

interface Props {
  projectType: string;
  projectName: string;
  initialStageId?: string;
  master?: boolean;
}

function formatBytes(bytes: number): string {
  return `${(bytes / 1024).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} KB`;
}

export function RegeneratePanel({ projectType, projectName, initialStageId, master }: Props) {
  const [stages, setStages] = useState<Stage[] | null>(null);
  const [selectedStageIds, setSelectedStageIds] = useState<Set<string>>(new Set());
  const [selectedModules, setSelectedModules] = useState<Record<string, Set<string>>>({});
  const [autonomous, setAutonomous] = useAutonomousMode();
  const [result, setResult] = useState<RegenResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [building, setBuilding] = useState<boolean>(false);
  const [wrap, setWrap] = useState<boolean>(true);
  const [copied, setCopied] = useState<boolean>(false);

  useEffect(() => {
    fetchStages(projectType, projectName)
      .then((s) => {
        setStages(s);
        if (master) {
          setSelectedStageIds(new Set(s.map((x) => x.id)));
          const all: Record<string, Set<string>> = {};
          for (const stage of s) all[stage.id] = new Set(stage.modules.map((m) => m.id));
          setSelectedModules(all);
        } else if (initialStageId) {
          setSelectedStageIds(new Set([initialStageId]));
          const stage = s.find((x) => x.id === initialStageId);
          if (stage) {
            setSelectedModules({ [initialStageId]: new Set(stage.modules.map((m) => m.id)) });
          }
        }
      })
      .catch((e) => setError(String(e)));
  }, [projectType, projectName, initialStageId, master]);

  const toggleStage = (stageId: string, checked: boolean) => {
    const next = new Set(selectedStageIds);
    if (checked) next.add(stageId);
    else next.delete(stageId);
    setSelectedStageIds(next);
    if (checked && stages) {
      const stage = stages.find((s) => s.id === stageId);
      if (stage)
        setSelectedModules((m) => ({ ...m, [stageId]: new Set(stage.modules.map((mm) => mm.id)) }));
    }
  };

  const toggleModule = (stageId: string, moduleId: string, checked: boolean) => {
    setSelectedModules((m) => {
      const cur = new Set(m[stageId] || []);
      if (checked) cur.add(moduleId);
      else cur.delete(moduleId);
      return { ...m, [stageId]: cur };
    });
  };

  const buildPrompt = async () => {
    setBuilding(true);
    setError(null);
    setResult(null);
    try {
      const stageIdArr = Array.from(selectedStageIds);
      const modulesObj: Record<string, string[]> = {};
      for (const sid of stageIdArr) modulesObj[sid] = Array.from(selectedModules[sid] || []);
      const r = await postRegenPrompt({
        project_type: projectType,
        project_name: projectName,
        stages: stageIdArr,
        modules: modulesObj,
        autonomous,
      });
      setResult(r);
    } catch (e: any) {
      const detail = e?.detail?.detail;
      if (detail && typeof detail === "object" && detail.kind === "too_large") {
        setError(`Could not build prompt: too large (${formatBytes(detail.bytes)})`);
      } else {
        setError(`Could not build prompt: ${typeof detail === "string" ? detail : JSON.stringify(detail || e)}`);
      }
    } finally {
      setBuilding(false);
    }
  };

  const copyPrompt = async () => {
    if (!result) return;
    try {
      await navigator.clipboard.writeText(result.prompt);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      setError("clipboard write failed");
    }
  };

  const breakdown = useMemo(() => {
    if (!result) return null;
    return `${result.selected_stages_count} stages selected, ${result.follow_ups_count} follow-ups inlined, autonomous=${result.autonomous}, ${formatBytes(result.bytes)}`;
  }, [result]);

  if (!stages) return null;

  const visibleStages = master ? stages : stages.filter((s) => s.id === initialStageId);

  const panel = (
    <div className="regen-body">
      {visibleStages.map((stage) => (
        <fieldset key={stage.id} className="regen-stage">
          <legend>
            {master && (
              <label>
                <input
                  type="checkbox"
                  checked={selectedStageIds.has(stage.id)}
                  onChange={(e) => toggleStage(stage.id, e.target.checked)}
                />{" "}
                <strong>{stage.label}</strong>
              </label>
            )}
            {!master && <strong>{stage.label}</strong>}
          </legend>
          <ul className="modules">
            {stage.modules.map((m) => (
              <li key={m.id}>
                <label>
                  <input
                    type="checkbox"
                    checked={selectedModules[stage.id]?.has(m.id) ?? false}
                    onChange={(e) => toggleModule(stage.id, m.id, e.target.checked)}
                  />{" "}
                  <span>{m.label}</span>
                </label>
              </li>
            ))}
          </ul>
        </fieldset>
      ))}
      <label className="autonomous-label">
        <input
          type="checkbox"
          checked={autonomous}
          onChange={(e) => setAutonomous(e.target.checked)}
          data-testid="autonomous-toggle"
        />{" "}
        Autonomous mode
      </label>
      <div className="regen-actions">
        <button
          type="button"
          data-testid="regen-build-button"
          onClick={buildPrompt}
          disabled={building || selectedStageIds.size === 0}
        >
          {building ? "Building…" : "Build prompt"}
        </button>
        {breakdown && (
          <span className="regen-breakdown" data-testid="regen-breakdown">
            {breakdown}
          </span>
        )}
      </div>
      {error && (
        <div role="alert" className="regen-error">
          {error}
        </div>
      )}
      {result?.warning && (
        <div className="regen-warning" data-testid="regen-warning-banner">
          warning: {result.warning} — verify your selection before pasting
        </div>
      )}
      {result && !error && (
        <div className="regen-prompt-block" data-testid="regen-prompt-block">
          <div className="regen-prompt-header">
            <span className="regen-prompt-title">Assembled prompt</span>
            <label className="wrap-toggle">
              <input
                type="checkbox"
                checked={wrap}
                onChange={(e) => setWrap(e.target.checked)}
                data-testid="regen-wrap-toggle"
              />{" "}
              Wrap
            </label>
            <button
              type="button"
              className="btn-primary"
              data-testid="regen-copy-button"
              aria-live="polite"
              style={{ minWidth: 90 }}
              onClick={copyPrompt}
            >
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>
          <pre
            style={
              wrap
                ? { whiteSpace: "pre-wrap", wordBreak: "break-word" }
                : { whiteSpace: "pre", overflowX: "auto" }
            }
          >
            {result.prompt}
          </pre>
        </div>
      )}
    </div>
  );

  if (master) {
    return (
      <section className="regen-panel master" data-testid="master-regen">
        <h2>Regenerate (whole project)</h2>
        {panel}
      </section>
    );
  }

  return (
    <details className="regen-panel" title="Regenerate" data-testid="regen-panel">
      <summary>Regenerate</summary>
      {panel}
    </details>
  );
}
