import { Link } from "react-router-dom";
import type { TreeNode } from "../types";

export interface HomeProps {
  tree: TreeNode | null;
}

interface ProjectRef {
  name: string;
  subType: "novel" | "short" | null;
  shotCount: number | null;
}

export function Home({ tree }: HomeProps): JSX.Element {
  const projects = tree ? discoverAiVideoProjects(tree) : [];
  return (
    <div className="home-view">
      <h1>ai_video_management</h1>
      <p>
        Browse and edit the artifacts under <code>ai_videos/</code>. Use the sidebar to open
        any character bible, style guide, script, shotlist, dual Kling/Seedance shot prompt,
        Seedream立绘 prompt, or publish metadata file.
      </p>
      <Link to="/workflow" className="home-workflow-link">
        🗺 查看 AI 短剧端到端工作流（六阶段 · QC 关卡 · skill / ref 调用）
      </Link>
      {tree === null ? (
        <p className="muted">Loading tree…</p>
      ) : projects.length === 0 ? (
        <p className="muted">
          No ai_video projects found under <code>ai_videos/</code>.
        </p>
      ) : (
        <section className="home-projects" aria-labelledby="home-projects-heading">
          <h2 id="home-projects-heading">Projects</h2>
          <ul className="home-project-list">
            {projects.map((p) => (
              <li key={p.name} className="home-project-item">
                <span className="home-project-name">{p.name}</span>
                {p.subType ? (
                  <span
                    className={`subtype-badge subtype-${p.subType}`}
                    aria-label={`项目类型: ${p.subType === "novel" ? "剧" : "短"}`}
                  >
                    {p.subType === "novel" ? "剧" : "短"}
                  </span>
                ) : null}
                {p.shotCount !== null ? <span className="muted"> · {p.shotCount} 镜</span> : null}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

function discoverAiVideoProjects(tree: TreeNode): ProjectRef[] {
  const aiVideosSection = (tree.children ?? []).find(
    (c) => c.type === "section" && c.name === "AI Videos",
  );
  if (!aiVideosSection) return [];
  const out: ProjectRef[] = [];
  for (const project of aiVideosSection.children ?? []) {
    if (project.type !== "directory") continue;
    out.push({
      name: project.name,
      subType: project.project_meta?.sub_type ?? null,
      shotCount: project.project_meta?.shot_count ?? null,
    });
  }
  return out;
}
