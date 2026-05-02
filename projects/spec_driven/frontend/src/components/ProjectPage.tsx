import { useEffect, useState } from "react";
import { fetchStages, StagesResponse } from "../api";
import { RegeneratePanel } from "./RegeneratePanel";

interface ProjectPageProps {
  projectType: string;
  projectName: string;
}

export function ProjectPage({
  projectType,
  projectName,
}: ProjectPageProps): JSX.Element {
  const [stages, setStages] = useState<StagesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchStages(projectType, projectName)
      .then((s) => {
        if (!cancelled) setStages(s);
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "stages fetch failed");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [projectType, projectName]);

  return (
    <div className="project-page">
      <header className="project-header">
        <h1 className="project-title">
          <span className="project-type-label">{projectType}</span>
          <span className="project-sep">/</span>
          <span className="project-name-label">{projectName}</span>
        </h1>
      </header>
      {error && (
        <div className="editor-error-banner" role="alert">
          {error}
        </div>
      )}
      <section className="project-stages">
        <h2>Stages</h2>
        {stages?.stages.map((st) => (
          <article key={st.id} className="project-stage">
            <h3 className="project-stage-header">
              <span className="project-stage-label">{st.label}</span>
              <span className="project-stage-folder">{st.folder}</span>
            </h3>
            <p className="project-stage-invocation">{st.invocation}</p>
            <ul className="project-stage-modules">
              {st.modules.map((m) => (
                <li key={m.relative_path}>
                  <span className="project-module-label">{m.label}</span>
                  <span className="project-module-path">{m.relative_path}</span>
                  {m.description && (
                    <span className="project-module-desc">{m.description}</span>
                  )}
                </li>
              ))}
            </ul>
          </article>
        ))}
      </section>
      <section className="project-master-regen">
        <h2>Regenerate prompt builder</h2>
        <RegeneratePanel
          projectType={projectType}
          projectName={projectName}
          showAll
        />
      </section>
    </div>
  );
}
