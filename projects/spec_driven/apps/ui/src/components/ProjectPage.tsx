import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { RegeneratePanel } from "./RegeneratePanel";
import { deleteProject } from "../api";
import { ApiError, type ProjectDeleteResult } from "../types";

const ALLOWED_TASK_TYPES = ["ai_video", "development"] as const;
const TASK_TYPE_TO_OUTPUT_DIR: Record<string, string> = {
  ai_video: "ai_videos",
  development: "projects",
};
const SELF_PROJECT_TYPE = "development";
const SELF_PROJECT_NAME = "spec_driven";

export function ProjectPage(): JSX.Element {
  const params = useParams<{ projectType: string; projectName: string }>();
  const projectType = params.projectType ?? "";
  const projectName = params.projectName ?? "";
  const navigate = useNavigate();

  const [confirming, setConfirming] = useState<boolean>(false);
  const [confirmInput, setConfirmInput] = useState<string>("");
  const [deleting, setDeleting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ProjectDeleteResult | null>(null);

  if (!projectType || !projectName) {
    return <div className="muted">Missing project type or name.</div>;
  }

  const isAllowedType = (ALLOWED_TASK_TYPES as readonly string[]).includes(projectType);
  const isSelfProject =
    projectType === SELF_PROJECT_TYPE && projectName === SELF_PROJECT_NAME;
  const outputDirName = TASK_TYPE_TO_OUTPUT_DIR[projectType] ?? "(unknown)";
  const confirmReady = confirmInput.trim() === projectName;

  const onDelete = async (): Promise<void> => {
    if (!confirmReady) return;
    setDeleting(true);
    setError(null);
    try {
      const res = await deleteProject({
        project_type: projectType as "ai_video" | "development",
        project_name: projectName,
      });
      setResult(res);
      window.setTimeout(() => {
        navigate("/", { replace: true });
        window.location.reload();
      }, 1200);
    } catch (err) {
      if (err instanceof ApiError) {
        const kind = err.detail?.kind ?? `HTTP ${err.status}`;
        setError(`Delete failed (${err.status}): ${kind}`);
      } else if (err instanceof Error) {
        setError(`Delete failed: ${err.message}`);
      } else {
        setError("Delete failed: unknown error");
      }
    } finally {
      setDeleting(false);
    }
  };

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

      {isAllowedType ? (
        <section className="danger-zone" aria-labelledby="danger-zone-heading">
          <h2 id="danger-zone-heading">Danger zone</h2>
          {isSelfProject ? (
            <p className="muted">
              <strong>Refused.</strong> This is the running spec_driven webapp's own
              source. UI-driven deletion would kill the process mid-response and leave
              a half-deleted tree. To actually decommission spec_driven, stop the
              backend first and remove the directories from a shell.
            </p>
          ) : result ? (
            <div role="status" className="danger-zone-result">
              <div>
                <strong>Project deleted.</strong> Removed:
              </div>
              <ul>
                {result.deleted_paths.map((p) => (
                  <li key={p}>
                    <code>{p}</code>
                  </li>
                ))}
              </ul>
              {result.not_found_paths.length > 0 ? (
                <div className="muted">
                  Not present (skipped):{" "}
                  {result.not_found_paths.map((p) => (
                    <code key={p} style={{ marginRight: 6 }}>
                      {p}
                    </code>
                  ))}
                </div>
              ) : null}
              <p className="muted">Returning to home…</p>
            </div>
          ) : !confirming ? (
            <>
              <p className="muted">
                Permanently delete this project. Both the spec-pipeline trail (
                <code>
                  specs/{projectType}/{projectName}/
                </code>
                ) and the generated output (
                <code>
                  {outputDirName}/{projectName}/
                </code>
                ) will be removed recursively. This cannot be undone.
              </p>
              <button
                type="button"
                className="danger-zone-trigger"
                onClick={() => {
                  setConfirming(true);
                  setError(null);
                }}
              >
                Delete project
              </button>
            </>
          ) : (
            <div className="danger-zone-confirm">
              <p>
                <strong>This is permanent.</strong> The following paths will be{" "}
                <code>rm -rf</code>'ed:
              </p>
              <ul>
                <li>
                  <code>
                    specs/{projectType}/{projectName}/
                  </code>
                </li>
                <li>
                  <code>
                    {outputDirName}/{projectName}/
                  </code>
                </li>
              </ul>
              <label className="danger-zone-label">
                Type the project name (<code>{projectName}</code>) to confirm:
                <input
                  type="text"
                  value={confirmInput}
                  onChange={(e) => setConfirmInput(e.target.value)}
                  placeholder={projectName}
                  className="danger-zone-input"
                  aria-label="Type project name to confirm deletion"
                  autoFocus
                />
              </label>
              <div className="danger-zone-buttons">
                <button
                  type="button"
                  className="danger-zone-confirm-btn"
                  onClick={() => void onDelete()}
                  disabled={!confirmReady || deleting}
                >
                  {deleting ? "Deleting…" : "Permanently delete"}
                </button>
                <button
                  type="button"
                  className="danger-zone-cancel"
                  onClick={() => {
                    setConfirming(false);
                    setConfirmInput("");
                    setError(null);
                  }}
                  disabled={deleting}
                >
                  Cancel
                </button>
              </div>
              {error ? (
                <div role="alert" className="danger-zone-error">
                  {error}
                </div>
              ) : null}
            </div>
          )}
        </section>
      ) : null}
    </div>
  );
}
