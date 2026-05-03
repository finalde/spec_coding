import { Link } from "react-router-dom";
import type { TreeNode } from "../types";

export interface HomeProps {
  tree: TreeNode | null;
}

interface ProjectRef {
  type: string;
  name: string;
}

export function Home({ tree }: HomeProps): JSX.Element {
  const projects = tree ? discoverProjects(tree) : [];
  return (
    <div className="home-view">
      <h1>spec_driven</h1>
      <p>
        Browse and edit the artifacts produced by the spec-driven workflow. Use the sidebar
        to open any file under the curated tree.
      </p>
      {tree === null ? (
        <p className="muted">Loading tree…</p>
      ) : projects.length === 0 ? (
        <p className="muted">
          {(tree.children ?? []).length} top-level section
          {(tree.children ?? []).length === 1 ? "" : "s"} loaded.
        </p>
      ) : (
        <section className="home-projects" aria-labelledby="home-projects-heading">
          <h2 id="home-projects-heading">Projects</h2>
          <p className="muted">
            Build a regen prompt that walks any subset of the six pipeline stages.
          </p>
          <ul className="home-project-list">
            {projects.map((p) => (
              <li key={`${p.type}/${p.name}`} className="home-project-item">
                <Link to={`/project/${encodeURIComponent(p.type)}/${encodeURIComponent(p.name)}`}>
                  {p.type}/{p.name}
                </Link>
                <span className="muted"> — Build regen prompt for the whole project</span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

function discoverProjects(tree: TreeNode): ProjectRef[] {
  const specsSection = (tree.children ?? []).find(
    (c) => c.type === "section" && c.name === "Specs",
  );
  if (!specsSection) return [];
  const out: ProjectRef[] = [];
  for (const typeNode of specsSection.children ?? []) {
    if (typeNode.type !== "directory") continue;
    for (const nameNode of typeNode.children ?? []) {
      if (nameNode.type !== "directory") continue;
      out.push({ type: typeNode.name, name: nameNode.name });
    }
  }
  return out;
}
