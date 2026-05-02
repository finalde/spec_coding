import { useEffect, useMemo, useState } from "react";
import {
  buildRegenPrompt,
  fetchStages,
  RegenPromptError,
  RegenPromptResponse,
  StageDef,
  StagesResponse,
} from "../api";
import {
  loadAutonomous,
  saveAutonomous,
  subscribeAutonomous,
} from "../autonomousMode";

interface RegeneratePanelProps {
  projectType: string;
  projectName: string;
  stageHint?: string;
  // When true, shows ALL stages (project-level / master) regardless of stageHint.
  showAll?: boolean;
}

interface ModuleSelection {
  // stageId -> set of relative_path's that are checked
  [stageId: string]: Set<string>;
}

function formatBytes(n: number): string {
  const kb = n / 1024;
  return `${kb.toLocaleString(undefined, { maximumFractionDigits: 1 })} KB`;
}

export function RegeneratePanel({
  projectType,
  projectName,
  stageHint,
  showAll,
}: RegeneratePanelProps): JSX.Element {
  const [stages, setStages] = useState<StagesResponse | null>(null);
  const [stageError, setStageError] = useState<string | null>(null);
  const [autonomous, setAutonomous] = useState(loadAutonomous());
  const [selection, setSelection] = useState<ModuleSelection>({});
  const [stageChecked, setStageChecked] = useState<Record<string, boolean>>({});
  const [building, setBuilding] = useState(false);
  const [response, setResponse] = useState<RegenPromptResponse | null>(null);
  const [buildError, setBuildError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const unsub = subscribeAutonomous(setAutonomous);
    return unsub;
  }, []);

  useEffect(() => {
    let cancelled = false;
    fetchStages(projectType, projectName)
      .then((s) => {
        if (cancelled) return;
        setStages(s);
        // Default: all checked
        const sel: ModuleSelection = {};
        const stCheck: Record<string, boolean> = {};
        for (const st of s.stages) {
          sel[st.id] = new Set(st.modules.map((m) => m.relative_path));
          stCheck[st.id] = true;
        }
        setSelection(sel);
        setStageChecked(stCheck);
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        setStageError(e instanceof Error ? e.message : "stages fetch failed");
      });
    return () => {
      cancelled = true;
    };
  }, [projectType, projectName]);

  const visibleStages: StageDef[] = useMemo(() => {
    if (!stages) return [];
    if (showAll) return stages.stages;
    if (stageHint) {
      const match = stages.stages.find(
        (s) => s.folder === stageHint || s.id === stageHint,
      );
      return match ? [match] : stages.stages;
    }
    return stages.stages;
  }, [stages, showAll, stageHint]);

  const toggleModule = (stageId: string, relPath: string): void => {
    setSelection((prev) => {
      const cur = new Set(prev[stageId] ?? []);
      if (cur.has(relPath)) cur.delete(relPath);
      else cur.add(relPath);
      return { ...prev, [stageId]: cur };
    });
  };

  const toggleStage = (stageId: string): void => {
    setStageChecked((prev) => ({ ...prev, [stageId]: !prev[stageId] }));
  };

  const onAutonomousChange = (v: boolean): void => {
    setAutonomous(v);
    saveAutonomous(v);
  };

  const onBuild = async (): Promise<void> => {
    if (!stages) return;
    setBuilding(true);
    setBuildError(null);
    setResponse(null);
    try {
      const stageIds: string[] = [];
      const modules: Record<string, string[]> = {};
      for (const st of visibleStages) {
        if (!stageChecked[st.id]) continue;
        stageIds.push(st.id);
        modules[st.id] = Array.from(selection[st.id] ?? []);
      }
      const r = await buildRegenPrompt({
        project_type: projectType,
        project_name: projectName,
        stages: stageIds,
        modules,
        autonomous,
      });
      setResponse(r);
    } catch (e) {
      if (e instanceof RegenPromptError) {
        setBuildError(`${e.status} ${e.body.kind ?? e.body.error ?? "error"}`);
      } else {
        setBuildError(e instanceof Error ? e.message : "build failed");
      }
    } finally {
      setBuilding(false);
    }
  };

  const onCopy = async (): Promise<void> => {
    if (!response) return;
    try {
      await navigator.clipboard.writeText(response.prompt);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      // ignore
    }
  };

  if (stageError) {
    return (
      <div className="regen-panel regen-error" role="alert">
        regen panel error: {stageError}
      </div>
    );
  }
  if (!stages) {
    return <div className="regen-panel">Loading stages…</div>;
  }

  const summaryLine = response
    ? `${response.selected_stages_count} ${response.selected_stages_count === 1 ? "stage" : "stages"} selected, ${response.follow_ups_count} ${response.follow_ups_count === 1 ? "follow-up" : "follow-ups"} inlined, autonomous=${response.autonomous}, ${formatBytes(response.bytes)}`
    : "";

  return (
    <details className="regen-panel">
      <summary className="regen-panel-summary">Regenerate</summary>
      <div className="regen-panel-body">
        <label className="regen-autonomous">
          <input
            type="checkbox"
            checked={autonomous}
            onChange={(e) => onAutonomousChange(e.target.checked)}
          />
          Autonomous mode
        </label>
        {visibleStages.map((st) => (
          <fieldset key={st.id} className="regen-stage">
            <legend className="regen-stage-legend">
              <label>
                <input
                  type="checkbox"
                  checked={stageChecked[st.id] !== false}
                  onChange={() => toggleStage(st.id)}
                />{" "}
                {st.label}
              </label>
              <span className="regen-stage-folder">{st.folder}</span>
            </legend>
            <ul className="regen-modules">
              {st.modules.map((m) => {
                const checked = selection[st.id]?.has(m.relative_path) ?? false;
                return (
                  <li key={m.relative_path}>
                    <label>
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleModule(st.id, m.relative_path)}
                      />{" "}
                      <span className="regen-module-label">{m.label}</span>{" "}
                      <span className="regen-module-path">
                        {m.relative_path}
                      </span>
                    </label>
                  </li>
                );
              })}
            </ul>
          </fieldset>
        ))}
        <div className="regen-actions">
          <button
            type="button"
            className="regen-build-btn"
            onClick={() => void onBuild()}
            disabled={building}
          >
            {building ? "Building…" : "Build prompt"}
          </button>
          {response && (
            <>
              <button
                type="button"
                className="regen-copy-btn"
                onClick={() => void onCopy()}
              >
                {copied ? "Copied!" : "Copy to clipboard"}
              </button>
              <span className="regen-summary-line">{summaryLine}</span>
            </>
          )}
        </div>
        {buildError && (
          <div className="editor-error-banner" role="alert">
            {buildError}
          </div>
        )}
        {response?.warning && (
          <div className="regen-warning" role="status">
            warning: {response.warning} — verify your selection before pasting
          </div>
        )}
        {response && (
          <details className="regen-prompt-details">
            <summary>View assembled prompt</summary>
            <pre className="regen-prompt-pre" tabIndex={0}>
              {response.prompt}
            </pre>
          </details>
        )}
      </div>
    </details>
  );
}
