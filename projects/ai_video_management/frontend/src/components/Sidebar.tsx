import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { TreeNode } from "../types";

export interface SidebarProps {
  tree: TreeNode | null;
  currentPath: string;
  onSelect: (path: string) => void;
  loadError?: string | null;
}

interface FlatNode { node: TreeNode; depth: number; parentPath: string | null; }

export function Sidebar({ tree, currentPath, onSelect, loadError }: SidebarProps): JSX.Element {
  const treeRef = useRef<HTMLDivElement>(null);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [focusedPath, setFocusedPath] = useState<string | null>(null);

  useEffect(() => {
    if (!tree) return;
    const accum: Record<string, boolean> = {};
    const walk = (node: TreeNode): void => {
      if (node.type === "file" || node.type === "image") return;
      if (node.path) accum[node.path] = true;
      for (const c of node.children ?? []) walk(c);
    };
    walk(tree);
    setExpanded((prev) => ({ ...accum, ...prev }));
  }, [tree]);

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
    if (!tree) return [];
    const out: FlatNode[] = [];
    const walk = (node: TreeNode, depth: number, parentPath: string | null): void => {
      out.push({ node, depth, parentPath });
      const isOpen = depth === 0 ? true : expanded[node.path] === true;
      if (isOpen && node.children && node.children.length) {
        for (const child of node.children) walk(child, depth + 1, node.path);
      }
    };
    if (tree.type === "section" && (tree.path === "" || !tree.path)) {
      for (const top of tree.children ?? []) walk(top, 0, null);
    } else {
      walk(tree, 0, null);
    }
    return out;
  }, [tree, expanded]);

  const toggle = useCallback((path: string) => {
    setExpanded((prev) => ({ ...prev, [path]: !prev[path] }));
  }, []);

  const onItemKeyDown = (event: React.KeyboardEvent<HTMLDivElement>, item: FlatNode): void => {
    const items = flat;
    const index = items.findIndex((i) => i.node.path === item.node.path);
    const isLeaf = item.node.type === "file" || item.node.type === "image" || (item.node.children ?? []).length === 0;
    const isOpen = expanded[item.node.path] === true;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      const next = items[index + 1];
      if (next) focusByPath(treeRef.current, next.node.path, setFocusedPath);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      const prev = items[index - 1];
      if (prev) focusByPath(treeRef.current, prev.node.path, setFocusedPath);
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      if (!isLeaf && !isOpen) toggle(item.node.path);
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      if (!isLeaf && isOpen) toggle(item.node.path);
      else if (item.parentPath) focusByPath(treeRef.current, item.parentPath, setFocusedPath);
    } else if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      if (item.node.type === "file" || item.node.type === "image") onSelect(item.node.path);
      else toggle(item.node.path);
    }
  };

  if (loadError) {
    return (
      <nav className="sidebar" aria-label="File tree">
        <div role="alert" className="sidebar-error">Failed to load tree: {loadError}</div>
      </nav>
    );
  }
  if (!tree) {
    return (
      <nav className="sidebar" aria-label="File tree">
        <div className="sidebar-loading">Loading…</div>
      </nav>
    );
  }

  return (
    <nav className="sidebar" aria-label="File tree">
      <div ref={treeRef} role="tree" aria-label="File tree" className="tree">
        {flat.map((item) => {
          const isLeaf = item.node.type === "file" || item.node.type === "image";
          const hasChildren = (item.node.children ?? []).length > 0;
          const isOpen = expanded[item.node.path] === true || item.depth === 0;
          const isActive = currentPath === item.node.path;
          const isFocused = focusedPath === item.node.path;
          const subType = item.node.project_meta?.sub_type;
          return (
            <div
              key={item.node.path || item.node.name}
              role="treeitem"
              tabIndex={isFocused || (focusedPath === null && item === flat[0]) ? 0 : -1}
              data-path={item.node.path}
              aria-level={item.depth + 1}
              aria-expanded={isLeaf ? undefined : isOpen}
              aria-selected={isActive}
              className={["tree-item", isLeaf ? "tree-leaf" : "tree-branch", isActive ? "tree-active" : ""].filter(Boolean).join(" ")}
              style={{ paddingLeft: `${8 + item.depth * 14}px` }}
              onFocus={() => setFocusedPath(item.node.path)}
              onKeyDown={(e) => onItemKeyDown(e, item)}
              onClick={(e) => {
                e.stopPropagation();
                if (isLeaf) { onSelect(item.node.path); return; }
                if (hasChildren) toggle(item.node.path);
              }}
            >
              {!isLeaf && hasChildren ? (
                <button type="button" className="tree-disclosure" aria-label={isOpen ? "Collapse" : "Expand"}
                  onClick={(e) => { e.stopPropagation(); toggle(item.node.path); }}>
                  {isOpen ? "▾" : "▸"}
                </button>
              ) : null}
              {item.node.type === "image" ? <span aria-hidden="true" className="tree-icon">🖼</span> : null}
              <span className="tree-label">{item.node.name}</span>
              {subType ? (
                <span className={`subtype-badge subtype-${subType}`}
                  aria-label={`项目类型: ${subType === "novel" ? "剧" : "短"}`}>
                  {subType === "novel" ? "剧" : "短"}
                </span>
              ) : null}
            </div>
          );
        })}
      </div>
    </nav>
  );
}

function focusByPath(root: HTMLDivElement | null, path: string, setFocused: (p: string) => void): void {
  if (!root) return;
  const el = root.querySelector<HTMLElement>(`[data-path="${cssEscape(path)}"]`);
  if (el) { el.focus(); setFocused(path); }
}

function cssEscape(value: string): string {
  if (typeof CSS !== "undefined" && typeof CSS.escape === "function") return CSS.escape(value);
  return value.replace(/["\\]/g, "\\$&");
}
