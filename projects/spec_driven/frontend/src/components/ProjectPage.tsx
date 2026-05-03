import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchStages } from "../api";
import { RegeneratePanel } from "./RegeneratePanel";
import type { Stage } from "../types";

export function ProjectPage() {
  const { type = "", name = "" } = useParams<{ type: string; name: string }>();
  const [stages, setStages] = useState<Stage[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStages(type, name)
      .then(setStages)
      .catch((e) => setError(String(e)));
  }, [type, name]);

  return (
    <main id="main" tabIndex={-1} className="project-page">
      <h1>
        Project — <code>{type}</code> / <code>{name}</code>
      </h1>
      {error && <div role="alert">Could not load stages: {error}</div>}
      {stages && (
        <>
          <h2>Stages</h2>
          <ul className="stage-list">
            {stages.map((s) => (
              <li key={s.id} data-testid="project-stage">
                <strong>{s.label}</strong>
                <p className="stage-invocation">{s.invocation}</p>
                <ul>
                  {s.modules.map((m) => (
                    <li key={m.id}>
                      <code>{m.relative_path}</code> — {m.description}
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
          <RegeneratePanel projectType={type} projectName={name} master />
        </>
      )}
    </main>
  );
}
