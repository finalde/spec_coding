import { useParams } from "react-router-dom";
import { RegeneratePanel } from "./RegeneratePanel";

export function ProjectPage(): JSX.Element {
  const params = useParams<{ projectType: string; projectName: string }>();
  const projectType = params.projectType ?? "";
  const projectName = params.projectName ?? "";
  if (!projectType || !projectName) {
    return <div className="muted">Missing project type or name.</div>;
  }
  return (
    <div className="project-page">
      <header>
        <h1>
          {projectType} / {projectName}
        </h1>
      </header>
      <p className="muted">
        Build a regen prompt that walks any subset of the six pipeline stages.
      </p>
      <RegeneratePanel
        projectType={projectType}
        projectName={projectName}
        stageId={null}
        initiallyOpen={true}
      />
    </div>
  );
}
