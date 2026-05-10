import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { TreeNode } from "../types";
import type { ActiveProject } from "../lib/activeProject";

export interface SidebarProps {
  tree: TreeNode | null;
  currentPath: string;
  onSelect: (path: string) => void;
  loadError?: string | null;
  activeProject: ActiveProject | null;
  onBackToProjects: () => void;
}

const STAGE_FOLDERS = new Set([
  "user_input",
  "interview",
  "findings",
  "final_specs",
  "validation",
]);

function nodeKey(node: TreeNode): string {
  return node.path || `section:${node.name}`;
}

function classifySpecPath(path: string): { kind: "project"; type: string; name: string }
  | { kind: "stage"; type: string; name: string; stage: string }
  | null {
  const parts = path.split("/");
  if (parts[0] !== "specs") return null;
  if (parts.length === 3) return { kind: "project", type: parts[1], name: parts[2] };
  if (parts.length === 4 && STAGE_FOLDERS.has(parts[3])) {
    return { kind: "stage", type: parts[1], name: parts[2], stage: parts[3] };
  }
  return null;
}

function filterSpecsForActiveProject(
  tree: TreeNode | null,
  active: ActiveProject | null,
): TreeNode | null {
  if (!tree) return tree;
  const children = (tree.children ?? []).map((section) => {
    if (section.type !== "section" || section.name !== "Specs") return section;
    if (!active) {
      return { ...section, children: [] };
    }
    const typeNode = (section.children ?? []).find(
      (c) => c.type === "directory" && c.name === active.type,
    );
    if (!typeNode) return { ...section, children: [] };
    const nameNode = (typeNode.children ?? []).find(
      (c) => c.type === "directory" && c.name === active.name,
    );
    if (!nameNode) return { ...section, children: [] };
    const filteredTypeNode: TreeNode = { ...typeNode, children: [nameNode] };
    return { ...section, children: [filteredTypeNode] };
  });
  return { ...tree, children };
}

interface FlatNode {
  node: TreeNode;
  depth: number;
  parentPath: string | null;
}

export function Sidebar({
  tree,
  currentPath,
  onSelect,
  loadError,
  activeProject,
  onBackToProjects,
}: SidebarProps): JSX.Element {
  const treeRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [focusedPath, setFocusedPath] = useState<string | null>(null);

  const filteredTree = useMemo(
    () => filterSpecsForActiveProject(tree, activeProject),
    [tree, activeProject],
  );

  const navigateForNode = useCallback(
    (path: string): boolean => {
      const cls = classifySpecPath(path);
      if (cls?.kind === "project") {
        navigate(`/project/${encodeURIComponent(cls.type)}/${encodeURIComponent(cls.name)}`);
        return true;
      }
      if (cls?.kind === "stage") {
        navigate(
          `/stage/${encodeURIComponent(cls.type)}/${encodeURIComponent(cls.name)}/${encodeURIComponent(cls.stage)}`,
        );
        return true;
      }
      return false;
    },
    [navigate],
  );

  // Default-expand every interior node when the tree (re)loads
  useEffect(() => {
    if (!filteredTree) return;
    const accum: Record<string, boolean> = {};
    const walk = (node: TreeNode): void => {
      if (node.type === "file") return;
      accum[nodeKey(node)] = true;
      for (const c of node.children ?? []) walk(c);
    };
    walk(filteredTree);
    setExpanded((prev) => ({ ...accum, ...prev }));
  }, [filteredTree]);

  // Auto-expand parents of the active path
  useEffect(() => {
    if (!currentPath) return;
    const parts = currentPath.split("/").slice(0, -1);
    const accum: Record<string, boolean> = {};
    let acc = "";
    for (const p of parts) {
      acc = acc ? `${acc}/${p}` : p;
      accum[acc] = true;
    }
    setExpanded((prev) => ({ ...prev, ...accum }));
  }, [currentPath]);

  // Keyboard shortcut: Ctrl/Cmd+Shift+E focuses the tree
  useEffect(() => {
    const handler = (event: KeyboardEvent): void => {
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && (event.key === "E" || event.key === "e")) {
        event.preventDefault();
        const root = treeRef.current;
        if (!root) return;
        const first = root.querySelector<HTMLElement>('[role="treeitem"]');
        if (first) {
          first.focus();
          const path = first.getAttribute("data-path");
          if (path) setFocusedPath(path);
        }
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  const flat = useMemo<FlatNode[]>(() => {
    if (!filteredTree) return [];
    const out: FlatNode[] = [];
    const walk = (node: TreeNode, depth: number, parentPath: string | null): void => {
      out.push({ node, depth, parentPath });
      const isOpen = expanded[nodeKey(node)] === true;
      if (isOpen && node.children && node.children.length) {
        for (const child of node.children) walk(child, depth + 1, nodeKey(node));
      }
    };
    if (filteredTree.type === "section" && (filteredTree.path === "" || !filteredTree.path)) {
      for (const top of filteredTree.children ?? []) walk(top, 0, null);
    } else {
      walk(filteredTree, 0, null);
    }
    return out;
  }, [filteredTree, expanded]);

  const toggle = useCallback((key: string) => {
    setExpanded((prev) => ({ ...prev, [key]: !prev[key] }));
  }, []);

  const onItemKeyDown = (event: React.KeyboardEvent<HTMLDivElement>, item: FlatNode): void => {
    const items = flat;
    const itemKey = nodeKey(item.node);
    const index = items.findIndex((i) => nodeKey(i.node) === itemKey);
    const isLeaf = item.node.type === "file" || (item.node.children ?? []).length === 0;
    const isOpen = expanded[itemKey] === true;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      const next = items[index + 1];
      if (next) focusByPath(treeRef.current, nodeKey(next.node), setFocusedPath);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      const prev = items[index - 1];
      if (prev) focusByPath(treeRef.current, nodeKey(prev.node), setFocusedPath);
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      if (!isLeaf && !isOpen) toggle(itemKey);
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      if (!isLeaf && isOpen) toggle(itemKey);
      else if (item.parentPath) focusByPath(treeRef.current, item.parentPath, setFocusedPath);
    } else if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      if (item.node.type === "file") onSelect(item.node.path);
      else if (!navigateForNode(item.node.path)) toggle(itemKey);
    }
  };

  const backLink = (
    <div className="sidebar-header">
      <button
        type="button"
        className="sidebar-back"
        onClick={onBackToProjects}
        aria-label="Back to projects"
      >
        ← Back to projects
      </button>
      {activeProject ? (
        <div className="sidebar-active-project" title={`${activeProject.type}/${activeProject.name}`}>
          {activeProject.type}/{activeProject.name}
        </div>
      ) : null}
    </div>
  );

  if (loadError) {
    return (
      <nav className="sidebar" aria-label="File tree">
        {backLink}
        <div role="alert" className="sidebar-error">
          Failed to load tree: {loadError}
        </div>
      </nav>
    );
  }

  if (!filteredTree) {
    return (
      <nav className="sidebar" aria-label="File tree">
        {backLink}
        <div className="sidebar-loading">Loading…</div>
      </nav>
    );
  }

  return (
    <nav className="sidebar" aria-label="File tree">
      {backLink}
      <div ref={treeRef} role="tree" aria-label="File tree" className="tree">
        {flat.map((item) => {
          const isLeaf = item.node.type === "file";
          const hasChildren = (item.node.children ?? []).length > 0;
          const itemKey = nodeKey(item.node);
          const isOpen = expanded[itemKey] === true;
          const isActive = currentPath === item.node.path;
          const isFocused = focusedPath === itemKey;
          return (
            <div
              key={itemKey}
              role="treeitem"
              tabIndex={isFocused || (focusedPath === null && item === flat[0]) ? 0 : -1}
              data-path={itemKey}
              aria-level={item.depth + 1}
              aria-expanded={isLeaf ? undefined : isOpen}
              aria-selected={isActive}
              className={[
                "tree-item",
                isLeaf ? "tree-leaf" : "tree-branch",
                item.node.type === "section" ? "tree-section" : "",
                isActive ? "tree-active" : "",
              ]
                .filter(Boolean)
                .join(" ")}
              style={{ paddingLeft: `${8 + item.depth * 14}px` }}
              onFocus={() => setFocusedPath(itemKey)}
              onKeyDown={(e) => onItemKeyDown(e, item)}
              onClick={(e) => {
                e.stopPropagation();
                if (isLeaf) {
                  onSelect(item.node.path);
                  return;
                }
                if (navigateForNode(item.node.path)) return;
                if (hasChildren) toggle(itemKey);
              }}
            >
              {!isLeaf && hasChildren ? (
                <button
                  type="button"
                  className="tree-disclosure"
                  aria-label={isOpen ? "Collapse" : "Expand"}
                  onClick={(e) => {
                    e.stopPropagation();
                    toggle(itemKey);
                  }}
                >
                  {isOpen ? "▾" : "▸"}
                </button>
              ) : null}
              <span className="tree-label">{item.node.name}</span>
            </div>
          );
        })}
      </div>
    </nav>
  );
}

function focusByPath(
  root: HTMLDivElement | null,
  path: string,
  setFocused: (p: string) => void,
): void {
  if (!root) return;
  const el = root.querySelector<HTMLElement>(`[data-path="${cssEscape(path)}"]`);
  if (el) {
    el.focus();
    setFocused(path);
  }
}

function cssEscape(value: string): string {
  if (typeof CSS !== "undefined" && typeof CSS.escape === "function") return CSS.escape(value);
  return value.replace(/["\\]/g, "\\$&");
}
