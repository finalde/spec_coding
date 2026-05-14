import { useParams } from "react-router-dom";
import { RegeneratePanel } from "./RegeneratePanel";

const STAGE_LABELS: Record<string, string> = {
  user_input: "Intake",
  interview: "Interview",
  findings: "Research",
  final_specs: "Spec compilation",
  validation: "Validation strategy",
};

export function StagePage(): JSX.Element {
  const params = useParams<{
    projectType: string;
    projectName: string;
    stage: string;
  }>();
  const projectType = params.projectType ?? "";
  const projectName = params.projectName ?? "";
  const stage = params.stage ?? "";
  if (!projectType || !projectName || !stage) {
    return <div className="muted">Missing project type, name, or stage.</div>;
  }
  const stageLabel = STAGE_LABELS[stage] ?? stage;
  return (
    <div className="project-page" data-testid="stage-page">
      <header>
        <h1>
          {projectType} / {projectName} / {stage}
        </h1>
      </header>
      <p className="muted">
        Build a regen prompt scoped to the {stageLabel} stage.
      </p>
      <RegeneratePanel
        projectType={projectType}
        projectName={projectName}
        stageId={stage}
        initiallyOpen={true}
      />
    </div>
  );
}
