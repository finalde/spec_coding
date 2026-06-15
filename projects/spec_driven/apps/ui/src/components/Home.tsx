import type { TreeNode } from "../types";
import type { ActiveProject } from "../lib/activeProject";

export interface HomeProps {
  tree: TreeNode | null;
  loadError?: string | null;
  onPick: (project: ActiveProject) => void;
  onOpenPromptLab?: () => void;
}

export function Home({ tree, loadError, onPick, onOpenPromptLab }: HomeProps): JSX.Element {
  const projects = tree ? discoverProjects(tree) : [];
  return (
    <div className="picker-view">
      <header className="picker-header">
        <h1>spec_driven</h1>
        <p className="muted">Pick a project to open its workspace.</p>
      </header>
      {onOpenPromptLab ? (
        <button type="button" className="promptlab-entry" onClick={onOpenPromptLab}>
          <span className="promptlab-entry-icon" aria-hidden="true">🧪</span>
          <span className="promptlab-entry-text">
            <span className="promptlab-entry-title">Prompt Lab</span>
            <span className="muted">
              Browse, run, and manage the <code>prompt_lab/</code> library of copy-paste AI build prompts.
            </span>
          </span>
          <span className="promptlab-entry-arrow" aria-hidden="true">→</span>
        </button>
      ) : null}
      {loadError ? (
        <div role="alert" className="sidebar-error">
          Failed to load tree: {loadError}
        </div>
      ) : tree === null ? (
        <p className="muted">Loading projects…</p>
      ) : projects.length === 0 ? (
        <p className="muted">No projects found under <code>specs/</code>.</p>
      ) : (
        <ul className="picker-list">
          {projects.map((p) => (
            <li key={`${p.type}/${p.name}`} className="picker-item">
              <button
                type="button"
                className="picker-link"
                onClick={() => onPick(p)}
              >
                <span className="picker-type">{p.type}</span>
                <span className="picker-sep">/</span>
                <span className="picker-name">{p.name}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function discoverProjects(tree: TreeNode): ActiveProject[] {
  const specsSection = (tree.children ?? []).find(
    (c) => c.type === "section" && c.name === "Specs",
  );
  if (!specsSection) return [];
  const out: ActiveProject[] = [];
  for (const typeNode of specsSection.children ?? []) {
    if (typeNode.type !== "directory") continue;
    for (const nameNode of typeNode.children ?? []) {
      if (nameNode.type !== "directory") continue;
      out.push({ type: typeNode.name, name: nameNode.name });
    }
  }
  return out;
}
