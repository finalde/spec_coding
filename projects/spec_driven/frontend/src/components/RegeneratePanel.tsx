import { useEffect, useMemo, useState } from "react";
import { buildRegenPrompt, fetchStages, type StageDef } from "../api";
import { loadAutonomous, saveAutonomous, subscribeAutonomous } from "../autonomousMode";

export interface RegeneratePanelProps {
  projectType: string;
  projectName: string;
  stageHint?: string;
}

const STAGE_FOLDER_TO_ID: Record<string, string> = {
  user_input: "intake",
  interview: "interview",
  findings: "research",
  final_specs: "spec",
  validation: "validation_strategy",
};

export function RegeneratePanel({
  projectType,
  projectName,
  stageHint,
}: RegeneratePanelProps): JSX.Element {
  const [open, setOpen] = useState<boolean>(false);
  const [stages, setStages] = useState<StageDef[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setStages(null);
    setLoadError(null);
    fetchStages(projectType, projectName)
      .then((r) => {
        if (!cancelled) setStages(r.stages);
      })
      .catch((e) => {
        if (!cancelled) setLoadError(String(e));
      });
    return () => {
      cancelled = true;
    };
  }, [projectType, projectName]);

  const stageId = stageHint ? STAGE_FOLDER_TO_ID[stageHint] : undefined;
  const stage = useMemo(
    () => (stages ? stages.find((s) => s.id === stageId) ?? null : null),
    [stages, stageId],
  );

  if (!stage) {
    return (
      <details className="regen-panel" open={open} onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)}>
        <summary className="regen-summary">
          <span className="regen-summary-title">Regenerate</span>
          <span className="regen-summary-hint">
            {loadError ? `(${loadError})` : "view the project page for whole-project regeneration"}
          </span>
        </summary>
      </details>
    );
  }

  return (
    <details className="regen-panel" open={open} onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)}>
      <summary className="regen-summary">
        <span className="regen-summary-title">Regenerate {stage.label}</span>
        <span className="regen-summary-hint">— pick modules and copy-paste prompt</span>
      </summary>
      <RegenForm
        projectType={projectType}
        projectName={projectName}
        stages={[stage]}
        defaultSelected={Object.fromEntries([[stage.id, stage.modules.map((m) => m.id)]])}
      />
    </details>
  );
}

export interface RegenFormProps {
  projectType: string;
  projectName: string;
  stages: StageDef[];
  defaultSelected: Record<string, string[]>;
}

export function RegenForm({
  projectType,
  projectName,
  stages,
  defaultSelected,
}: RegenFormProps): JSX.Element {
  const [selected, setSelected] = useState<Record<string, string[]>>(defaultSelected);
  const [autonomous, setAutonomous] = useState<boolean>(() => loadAutonomous());
  const [prompt, setPrompt] = useState<string | null>(null);
  const [busy, setBusy] = useState<boolean>(false);
  const [copyState, setCopyState] = useState<"idle" | "copied" | "error">("idle");

  useEffect(() => {
    return subscribeAutonomous((v) => setAutonomous(v));
  }, []);

  useEffect(() => {
    setSelected(defaultSelected);
    setPrompt(null);
    setCopyState("idle");
  }, [JSON.stringify(defaultSelected)]);

  const toggleModule = (stageId: string, moduleId: string): void => {
    setSelected((prev) => {
      const cur = new Set(prev[stageId] ?? []);
      if (cur.has(moduleId)) cur.delete(moduleId);
      else cur.add(moduleId);
      return { ...prev, [stageId]: Array.from(cur) };
    });
  };

  const toggleStage = (stageId: string): void => {
    setSelected((prev) => {
      const has = (prev[stageId] ?? []).length > 0;
      const stage = stages.find((s) => s.id === stageId);
      return {
        ...prev,
        [stageId]: has ? [] : (stage ? stage.modules.map((m) => m.id) : []),
      };
    });
  };

  const onAutonomousToggle = (v: boolean): void => {
    setAutonomous(v);
    saveAutonomous(v);
  };

  const onBuild = async (): Promise<void> => {
    setBusy(true);
    setCopyState("idle");
    try {
      const stageIds = stages
        .map((s) => s.id)
        .filter((id) => (selected[id] ?? []).length > 0);
      const text = await buildRegenPrompt({
        project_type: projectType,
        project_name: projectName,
        stages: stageIds,
        modules: selected,
        autonomous,
      });
      setPrompt(text);
    } catch (e) {
      setPrompt(`(error: ${String(e)})`);
    } finally {
      setBusy(false);
    }
  };

  const onCopy = async (): Promise<void> => {
    if (!prompt) return;
    try {
      await navigator.clipboard.writeText(prompt);
      setCopyState("copied");
      window.setTimeout(() => setCopyState("idle"), 1500);
    } catch {
      setCopyState("error");
    }
  };

  return (
    <div className="regen-form">
      {stages.map((s) => (
        <fieldset key={s.id} className="regen-stage">
          <legend className="regen-stage-legend">
            <label className="regen-stage-toggle">
              <input
                type="checkbox"
                checked={(selected[s.id] ?? []).length > 0}
                onChange={() => toggleStage(s.id)}
              />
              <strong>{s.label}</strong>
            </label>
          </legend>
          <p className="regen-stage-invocation">{s.invocation}</p>
          <ul className="regen-module-list">
            {s.modules.map((m) => {
              const checked = (selected[s.id] ?? []).includes(m.id);
              return (
                <li key={m.id} className="regen-module">
                  <label>
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggleModule(s.id, m.id)}
                    />
                    <code>{m.label}</code> — {m.description}
                  </label>
                </li>
              );
            })}
          </ul>
        </fieldset>
      ))}
      <div className="regen-controls">
        <label className="regen-autonomous">
          <input
            type="checkbox"
            checked={autonomous}
            onChange={(e) => onAutonomousToggle(e.target.checked)}
          />
          <strong>Autonomous mode</strong>
          <span className="regen-autonomous-hint">
            (Claude won't ask questions — uses best judgment for unclear cases.)
          </span>
        </label>
        <button
          type="button"
          className="editor-button editor-save"
          onClick={() => void onBuild()}
          disabled={busy}
        >
          {busy ? "Building…" : "Build prompt"}
        </button>
      </div>
      {prompt !== null && (
        <details className="regen-prompt-details" open>
          <summary>
            Copy-paste prompt ({prompt.length.toLocaleString()} chars)
            <button
              type="button"
              className="editor-button regen-copy"
              onClick={(e) => {
                e.preventDefault();
                void onCopy();
              }}
            >
              {copyState === "copied" ? "Copied!" : copyState === "error" ? "Copy failed" : "Copy"}
            </button>
          </summary>
          <pre className="regen-prompt-pre">{prompt}</pre>
        </details>
      )}
    </div>
  );
}
