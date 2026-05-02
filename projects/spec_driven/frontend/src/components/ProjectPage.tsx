import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchStages, type StageDef } from "../api";
import { RegenForm } from "./RegeneratePanel";

export interface ProjectPageProps {
  projectType: string;
  projectName: string;
}

export function ProjectPage({ projectType, projectName }: ProjectPageProps): JSX.Element {
  const [stages, setStages] = useState<StageDef[] | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setStages(null);
    setErr(null);
    fetchStages(projectType, projectName)
      .then((r) => {
        if (!cancelled) setStages(r.stages);
      })
      .catch((e) => {
        if (!cancelled) setErr(String(e));
      });
    return () => {
      cancelled = true;
    };
  }, [projectType, projectName]);

  return (
    <main className="reader project-page">
      <h1 className="project-page-title">
        Project · {projectType} / {projectName}
      </h1>
      <p className="project-page-sub">
        Stage map and a master regeneration prompt builder. Open any artifact in the sidebar to edit it,
        or use the master panel below to build one prompt that walks several stages at once.
      </p>

      {err && <div className="reader-error" role="alert">Could not load stages: {err}</div>}

      {stages && (
        <>
          <section className="project-stage-map">
            <h2>Stages</h2>
            <ol className="project-stage-list">
              {stages.map((s) => (
                <li key={s.id} className="project-stage-row">
                  <h3>{s.label}</h3>
                  <p className="project-stage-invocation">{s.invocation}</p>
                  <ul className="project-stage-module-list">
                    {s.modules.map((m) => {
                      const url = m.relative_path
                        ? `/file/${encodeURI(`specs/${projectType}/${projectName}/${m.relative_path}`)}`
                        : null;
                      return (
                        <li key={m.id}>
                          {url ? (
                            <Link to={url}>
                              <code>{m.label}</code>
                            </Link>
                          ) : (
                            <code>{m.label}</code>
                          )}
                          {" — "}
                          {m.description}
                        </li>
                      );
                    })}
                  </ul>
                </li>
              ))}
            </ol>
          </section>

          <section className="project-regen-master">
            <h2>Regenerate (master)</h2>
            <p>
              Pick any subset of stages and modules. Default is "regenerate everything." Toggle
              autonomous mode if you're going to walk away — Claude will not stop to ask questions.
            </p>
            <RegenForm
              projectType={projectType}
              projectName={projectName}
              stages={stages}
              defaultSelected={Object.fromEntries(
                stages.map((s) => [s.id, s.modules.map((m) => m.id)]),
              )}
            />
          </section>
        </>
      )}

      {!stages && !err && <div className="reader-loading">Loading…</div>}
    </main>
  );
}
