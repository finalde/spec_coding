import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import type { TreeNode, TreeResponse } from "../types";
import { loadSidebarState, saveSidebarState, type SidebarState } from "../localStorage";
import { RefreshButton } from "./RefreshButton";

export interface SidebarProps {
  tree: TreeResponse | null;
  onRefresh: () => void;
  selectedPath: string | null;
}

export function Sidebar({ tree, onRefresh, selectedPath }: SidebarProps): JSX.Element {
  const [state, setState] = useState<SidebarState>(() => loadSidebarState());

  useEffect(() => {
    saveSidebarState(state);
  }, [state]);

  useEffect(() => {
    if (selectedPath && state.lastSelectedPath !== selectedPath) {
      const ancestors = ancestorPaths(selectedPath);
      setState((prev) => ({
        expanded: { ...prev.expanded, ...Object.fromEntries(ancestors.map((p) => [p, true])) },
        lastSelectedPath: selectedPath,
      }));
    }
  }, [selectedPath]);

  const toggle = (path: string): void => {
    setState((prev) => ({ ...prev, expanded: { ...prev.expanded, [path]: !prev.expanded[path] } }));
  };

  return (
    <aside className="sidebar" aria-label="Artifact navigator">
      <div className="sidebar-header">
        <span className="sidebar-title">spec_driven</span>
        <RefreshButton onClick={onRefresh} />
      </div>
      {tree ? (
        <>
          <SettingsSectionView settings={tree.settings} selectedPath={selectedPath} />
          <ProjectsSectionView
            projects={tree.projects}
            expanded={state.expanded}
            onToggle={toggle}
            selectedPath={selectedPath}
          />
        </>
      ) : (
        <div className="sidebar-loading">Loading…</div>
      )}
    </aside>
  );
}

function ancestorPaths(filePath: string): string[] {
  const parts = filePath.split("/").filter((s) => s !== "");
  const out: string[] = [];
  for (let i = 1; i <= parts.length; i++) {
    out.push(parts.slice(0, i).join("/"));
  }
  return out;
}

function SettingsSectionView({
  settings,
  selectedPath,
}: {
  settings: TreeResponse["settings"];
  selectedPath: string | null;
}): JSX.Element {
  return (
    <section className="sidebar-section" aria-label="Claude Settings & Shared Context">
      <h2 className="sidebar-section-title">Claude Settings &amp; Shared Context</h2>
      <SubgroupView title="CLAUDE.md" nodes={settings.claude_md} selectedPath={selectedPath} />
      <SubgroupView title="Agents" nodes={settings.agents} selectedPath={selectedPath} />
      <SubgroupView title="Skills" nodes={settings.skills} selectedPath={selectedPath} />
    </section>
  );
}

function SubgroupView({
  title,
  nodes,
  selectedPath,
}: {
  title: string;
  nodes: TreeNode[];
  selectedPath: string | null;
}): JSX.Element {
  return (
    <div className="sidebar-subgroup">
      <h3 className="sidebar-subgroup-title">{title}</h3>
      <ul role="list" className="sidebar-list">
        {nodes.map((n) => (
          <li key={n.path}>
            <FileLink node={n} selectedPath={selectedPath} />
          </li>
        ))}
      </ul>
    </div>
  );
}

function ProjectsSectionView({
  projects,
  expanded,
  onToggle,
  selectedPath,
}: {
  projects: TreeNode[];
  expanded: Record<string, boolean>;
  onToggle: (path: string) => void;
  selectedPath: string | null;
}): JSX.Element {
  return (
    <section className="sidebar-section" aria-label="Projects">
      <h2 className="sidebar-section-title">Projects</h2>
      <ul role="tree" aria-multiselectable="false" className="sidebar-tree">
        {projects.map((tn) => (
          <TreeItem
            key={tn.path}
            node={tn}
            level={1}
            expanded={expanded}
            onToggle={onToggle}
            selectedPath={selectedPath}
          />
        ))}
      </ul>
    </section>
  );
}

function TreeItem({
  node,
  level,
  expanded,
  onToggle,
  selectedPath,
}: {
  node: TreeNode;
  level: number;
  expanded: Record<string, boolean>;
  onToggle: (path: string) => void;
  selectedPath: string | null;
}): JSX.Element {
  const isFolder = node.kind === "folder";
  const isMissing = node.kind === "missing-folder";
  const isOpen = expanded[node.path] ?? false;
  if (isMissing) {
    return (
      <li
        role="treeitem"
        aria-level={level}
        aria-disabled="true"
        className="tree-row tree-missing"
        title="not yet generated"
      >
        <span className="tree-label tree-label-missing">{node.name}</span>
      </li>
    );
  }
  if (isFolder) {
    const projectMatch = matchProjectPath(node.path);
    return (
      <li role="treeitem" aria-level={level} aria-expanded={isOpen} className="tree-row">
        <button
          type="button"
          className="tree-toggle"
          onClick={() => onToggle(node.path)}
          aria-label={`${isOpen ? "Collapse" : "Expand"} ${node.name}`}
        >
          <span aria-hidden="true">{isOpen ? "▾" : "▸"}</span>
          <span className="tree-label">{node.name}</span>
        </button>
        {projectMatch && (
          <Link
            to={`/project/${projectMatch.projectType}/${projectMatch.projectName}`}
            className="tree-project-link"
            title={`Open the project page (master regen panel) for ${projectMatch.projectName}`}
          >
            ↗ project page
          </Link>
        )}
        {isOpen && node.children && (
          <ul role="group" className="tree-group">
            {node.children.map((c) => (
              <TreeItem
                key={c.path}
                node={c}
                level={level + 1}
                expanded={expanded}
                onToggle={onToggle}
                selectedPath={selectedPath}
              />
            ))}
          </ul>
        )}
      </li>
    );
  }
  const isSelected = selectedPath === node.path;
  return (
    <li
      role="treeitem"
      aria-level={level}
      aria-selected={isSelected}
      className={`tree-row tree-leaf${isSelected ? " tree-selected" : ""}`}
    >
      <FileLink node={node} selectedPath={selectedPath} />
    </li>
  );
}

function FileLink({
  node,
  selectedPath,
}: {
  node: TreeNode;
  selectedPath: string | null;
}): JSX.Element {
  const navigate = useNavigate();
  const location = useLocation();
  const isSelected = selectedPath === node.path;
  const truncated = useMemo(() => truncateFileName(node.name), [node.name]);
  return (
    <Link
      to={`/file/${encodeURI(node.path)}`}
      title={node.name}
      className={`tree-leaf-link${isSelected ? " selected" : ""}`}
      state={{ from: location.pathname }}
      onClick={(e) => {
        if (e.metaKey || e.ctrlKey) return;
        e.preventDefault();
        navigate(`/file/${encodeURI(node.path)}`);
      }}
    >
      {truncated}
    </Link>
  );
}

function matchProjectPath(path: string): { projectType: string; projectName: string } | null {
  const parts = path.split("/");
  if (parts.length === 3 && parts[0] === "specs") {
    return { projectType: parts[1], projectName: parts[2] };
  }
  return null;
}

function truncateFileName(name: string, max = 40): string {
  if (name.length <= max) return name;
  const dotIdx = name.lastIndexOf(".");
  if (dotIdx <= 0 || dotIdx < name.length - 8) return name.slice(0, max - 1) + "…";
  const ext = name.slice(dotIdx);
  const stem = name.slice(0, dotIdx);
  const keepHead = Math.max(8, max - ext.length - 4);
  return stem.slice(0, keepHead) + "…" + ext;
}
