import { useCallback, useEffect, useMemo, useState } from "react";
import { useAutonomousMode } from "../lib/autonomousMode";
import { fetchStages, postRegenPrompt } from "../api";
import { ApiError, type RegenResult, type Stage } from "../types";

export interface RegeneratePanelProps {
  projectType: string;
  projectName: string;
  /** when set, panel only shows the named stage (per-stage mode); when null shows all stages (project-page) */
  stageId: string | null;
  initiallyOpen?: boolean;
}

const DEFAULT_STAGES: Stage[] = [
  {
    id: "user_input",
    label: "Intake",
    folder: "user_input",
    invocation: "Stage 1 — Intake",
    modules: [
      {
        id: "revised_prompt",
        label: "Revised prompt",
        relative_path: "user_input/revised_prompt.md",
        description: "Auto-regenerated raw + every follow-up",
      },
    ],
  },
  {
    id: "interview",
    label: "Interview",
    folder: "interview",
    invocation: "Stage 2 — Interview",
    modules: [
      {
        id: "qa",
        label: "qa.md",
        relative_path: "interview/qa.md",
        description: "Multi-choice question pool + answers",
      },
    ],
  },
  {
    id: "findings",
    label: "Research",
    folder: "findings",
    invocation: "Stage 3 — Research",
    modules: [
      {
        id: "dossier",
        label: "dossier.md",
        relative_path: "findings/dossier.md",
        description: "Synthesized cross-angle findings",
      },
      {
        id: "angles",
        label: "angle-*.md",
        relative_path: "findings/angle-*.md",
        description: "Per-angle research worker output",
      },
    ],
  },
  {
    id: "final_specs",
    label: "Spec compilation",
    folder: "final_specs",
    invocation: "Stage 4 — Spec compilation",
    modules: [
      {
        id: "spec",
        label: "spec.md",
        relative_path: "final_specs/spec.md",
        description: "Compiled specification",
      },
    ],
  },
  {
    id: "validation",
    label: "Validation strategy",
    folder: "validation",
    invocation: "Stage 5 — Validation strategy",
    modules: [
      {
        id: "strategy",
        label: "strategy.md",
        relative_path: "validation/strategy.md",
        description: "Master strategy",
      },
      {
        id: "acceptance_criteria",
        label: "acceptance_criteria.md",
        relative_path: "validation/acceptance_criteria.md",
        description: "ACs",
      },
      {
        id: "bdd_scenarios",
        label: "bdd_scenarios.md",
        relative_path: "validation/bdd_scenarios.md",
        description: "BDD scenarios",
      },
      {
        id: "unit_tests",
        label: "unit_tests.md",
        relative_path: "validation/unit_tests.md",
        description: "Unit-level plan",
      },
      {
        id: "system_tests",
        label: "system_tests.md",
        relative_path: "validation/system_tests.md",
        description: "System-level plan",
      },
      {
        id: "security",
        label: "security.md",
        relative_path: "validation/security.md",
        description: "Security plan",
      },
      {
        id: "performance",
        label: "performance.md",
        relative_path: "validation/performance.md",
        description: "Performance plan",
      },
      {
        id: "accessibility",
        label: "accessibility.md",
        relative_path: "validation/accessibility.md",
        description: "Accessibility plan",
      },
    ],
  },
  {
    id: "execution",
    label: "Execution",
    folder: "projects",
    invocation: "Stage 6 — Execution + streaming validation",
    modules: [
      {
        id: "code",
        label: "project code",
        relative_path: "projects/{name}/",
        description: "Output project under projects/",
      },
    ],
  },
];

export function RegeneratePanel(props: RegeneratePanelProps): JSX.Element {
  const [stages, setStages] = useState<Stage[]>(DEFAULT_STAGES);
  const [open, setOpen] = useState<boolean>(props.initiallyOpen ?? false);
  const [autonomous, setAutonomous] = useAutonomousMode();
  const [selectedStageIds, setSelectedStageIds] = useState<Set<string>>(new Set());
  const [selectedModules, setSelectedModules] = useState<Record<string, Set<string>>>({});
  const [building, setBuilding] = useState<boolean>(false);
  const [result, setResult] = useState<RegenResult | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [softWrap, setSoftWrap] = useState<boolean>(true);
  const [copied, setCopied] = useState<boolean>(false);

  // Load stage definitions; default fallback already in place
  useEffect(() => {
    let alive = true;
    fetchStages(props.projectType, props.projectName)
      .then((s) => {
        if (alive && s.length > 0) setStages(s);
      })
      .catch(() => {
        // backend may not implement /api/stages — fall back to DEFAULT_STAGES
      });
    return () => {
      alive = false;
    };
  }, [props.projectType, props.projectName]);

  // Initialize selections when stages load
  useEffect(() => {
    const stagesToShow = props.stageId
      ? stages.filter((s) => s.id === props.stageId)
      : stages;
    const initialIds = new Set(stagesToShow.map((s) => s.id));
    const initialMods: Record<string, Set<string>> = {};
    for (const stage of stagesToShow) {
      initialMods[stage.id] = new Set(stage.modules.map((m) => m.id));
    }
    setSelectedStageIds(initialIds);
    setSelectedModules(initialMods);
  }, [stages, props.stageId]);

  const stagesShown = useMemo(
    () => (props.stageId ? stages.filter((s) => s.id === props.stageId) : stages),
    [stages, props.stageId],
  );

  const buildPrompt = useCallback(async () => {
    setBuilding(true);
    setError(null);
    setResult(null);
    setSoftWrap(true);
    setCopied(false);
    const stageIds = Array.from(selectedStageIds);
    const modules: Record<string, string[]> = {};
    for (const id of stageIds) {
      const set = selectedModules[id];
      modules[id] = set ? Array.from(set) : [];
    }
    try {
      const res = await postRegenPrompt({
        project_type: props.projectType,
        project_name: props.projectName,
        stages: stageIds,
        modules,
        autonomous,
      });
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setBuilding(false);
    }
  }, [autonomous, props.projectName, props.projectType, selectedModules, selectedStageIds]);

  const toggleStage = (stageId: string): void => {
    setSelectedStageIds((prev) => {
      const next = new Set(prev);
      if (next.has(stageId)) next.delete(stageId);
      else next.add(stageId);
      return next;
    });
  };

  const toggleModule = (stageId: string, moduleId: string): void => {
    setSelectedModules((prev) => {
      const set = new Set(prev[stageId] ?? []);
      if (set.has(moduleId)) set.delete(moduleId);
      else set.add(moduleId);
      return { ...prev, [stageId]: set };
    });
  };

  const copyPrompt = useCallback(async () => {
    if (!result) return;
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(result.prompt);
      }
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard may be unavailable
    }
  }, [result]);

  const breakdown = useMemo(() => {
    if (!result) return null;
    const kb = (result.bytes / 1024).toFixed(1);
    return `${result.selected_stages_count} stages selected, ${result.follow_ups_count} follow-ups inlined, autonomous=${result.autonomous}, ${kb} KB`;
  }, [result]);

  return (
    <details
      className="regen-panel"
      open={open}
      onToggle={(e) => setOpen((e.currentTarget as HTMLDetailsElement).open)}
    >
      <summary className="regen-panel-summary">
        Regenerate {props.stageId ? `(stage: ${props.stageId})` : "(project-wide)"}
      </summary>
      <div className="regen-panel-body">
        {stagesShown.map((stage) => (
          <fieldset key={stage.id} className="regen-stage">
            <legend>
              {props.stageId === null ? (
                <label>
                  <input
                    type="checkbox"
                    checked={selectedStageIds.has(stage.id)}
                    onChange={() => toggleStage(stage.id)}
                  />{" "}
                  {stage.label}
                </label>
              ) : (
                <span>{stage.label}</span>
              )}
            </legend>
            <div className="regen-modules">
              {stage.modules.map((m) => (
                <label key={m.id} className="regen-module">
                  <input
                    type="checkbox"
                    checked={(selectedModules[stage.id] ?? new Set()).has(m.id)}
                    onChange={() => toggleModule(stage.id, m.id)}
                  />{" "}
                  {m.label}
                </label>
              ))}
            </div>
          </fieldset>
        ))}
        <div className="regen-controls">
          <label className="regen-autonomous">
            <input
              type="checkbox"
              role="switch"
              checked={autonomous}
              aria-checked={autonomous}
              onChange={(e) => setAutonomous(e.target.checked)}
            />{" "}
            Autonomous mode
          </label>
          <button
            type="button"
            className="regen-build"
            onClick={() => void buildPrompt()}
            disabled={building || selectedStageIds.size === 0}
          >
            {building ? "Building…" : "Build prompt"}
          </button>
          {breakdown ? <span className="regen-breakdown">{breakdown}</span> : null}
        </div>
        {error ? (
          <div className="regen-error" role="alert">
            {formatRegenError(error)}
          </div>
        ) : null}
        {result?.warning ? (
          <div className="regen-warning" role="alert">
            Approaching ceiling: {result.warning.bytes.toLocaleString()} bytes (soft limit{" "}
            {result.warning.soft_limit.toLocaleString()})
          </div>
        ) : null}
        {result && !error ? (
          <div className="regen-prompt-block">
            <div className="regen-prompt-header">
              <span className="regen-prompt-title">Assembled prompt</span>
              <label className="regen-wrap-toggle">
                <input
                  type="checkbox"
                  role="switch"
                  checked={softWrap}
                  aria-checked={softWrap}
                  onChange={(e) => setSoftWrap(e.target.checked)}
                />{" "}
                Wrap
              </label>
              <button
                type="button"
                className="regen-copy"
                aria-live="polite"
                onClick={() => void copyPrompt()}
              >
                {copied ? "Copied!" : "Copy"}
              </button>
            </div>
            <pre
              className="regen-prompt-pre"
              style={{
                whiteSpace: softWrap ? "pre-wrap" : "pre",
                overflowX: softWrap ? "hidden" : "auto",
              }}
            >
              {result.prompt}
            </pre>
          </div>
        ) : null}
      </div>
    </details>
  );
}

function formatRegenError(error: Error): string {
  if (error instanceof ApiError) {
    if (error.status === 413) return "Prompt is too large to assemble (≥1 MB)";
    return `Build failed (${error.status})`;
  }
  return `Build failed: ${error.message}`;
}
