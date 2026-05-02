import {
  KeyboardEvent,
  MouseEvent,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { Link, useNavigate } from "react-router-dom";
import type { TreeNode, TreeResponse } from "../types";
import {
  loadSidebarState,
  saveSidebarState,
  SidebarState,
} from "../localStorage";
import { RefreshButton } from "./RefreshButton";

interface SidebarProps {
  tree: TreeResponse | null;
  selectedPath: string | null;
  onRefresh: () => void;
}

function truncateFileName(name: string, max: number): string {
  if (name.length <= max) return name;
  if (max <= 3) return name.slice(0, max);
  const dotIdx = name.lastIndexOf(".");
  const ext = dotIdx >= 0 ? name.slice(dotIdx) : "";
  const base = dotIdx >= 0 ? name.slice(0, dotIdx) : name;
  const keep = max - ext.length - 1; // 1 for ellipsis
  if (keep < 4) {
    return name.slice(0, max - 1) + "…";
  }
  const headLen = Math.ceil(keep / 2);
  const tailLen = Math.floor(keep / 2);
  const head = base.slice(0, headLen);
  const tail = base.slice(base.length - tailLen);
  return `${head}…${tail}${ext}`;
}

interface VisibleNode {
  id: string; // unique focus id
  level: number;
  path: string | null; // null for synthetic groupings
  kind: "file" | "folder" | "missing-folder" | "settings-group" | "settings-section";
  name: string;
  expanded?: boolean;
  parentId: string | null;
  hasChildren: boolean;
  ariaSelected: boolean;
  isProjectFolder?: boolean;
  projectType?: string;
  projectName?: string;
}

interface BuildOpts {
  expanded: Record<string, boolean>;
  selectedPath: string | null;
}

function buildVisible(tree: TreeResponse, opts: BuildOpts): VisibleNode[] {
  const nodes: VisibleNode[] = [];

  // Section 1: Settings & Shared Context
  const sec1Id = "section:settings";
  nodes.push({
    id: sec1Id,
    level: 1,
    path: null,
    kind: "settings-section",
    name: "Claude Settings & Shared Context",
    parentId: null,
    hasChildren: true,
    ariaSelected: false,
  });

  const pushGroup = (id: string, label: string, items: ReadonlyArray<TreeNode>): void => {
    nodes.push({
      id,
      level: 2,
      path: null,
      kind: "settings-group",
      name: label,
      parentId: sec1Id,
      hasChildren: true,
      ariaSelected: false,
    });
    for (const f of items) {
      const isSelected =
        opts.selectedPath !== null && opts.selectedPath === f.path;
      nodes.push({
        id: `file:${f.path}`,
        level: 3,
        path: f.path,
        kind: "file",
        name: f.name,
        parentId: id,
        hasChildren: false,
        ariaSelected: isSelected,
      });
    }
  };

  pushGroup("group:claude_md", "CLAUDE.md", tree.settings.claude_md);
  pushGroup("group:agents", "Agents", tree.settings.agents);
  pushGroup("group:skills", "Skills", tree.settings.skills);

  // Section 2: Projects
  const sec2Id = "section:projects";
  const sec2Expanded = opts.expanded[sec2Id] !== false;
  nodes.push({
    id: sec2Id,
    level: 1,
    path: null,
    kind: "folder",
    name: "Projects",
    parentId: null,
    hasChildren: tree.projects.length > 0,
    expanded: sec2Expanded,
    ariaSelected: false,
  });

  if (sec2Expanded) {
    for (const taskType of tree.projects) {
      const ttId = `tt:${taskType.path}`;
      const ttExpanded = opts.expanded[ttId] === true;
      nodes.push({
        id: ttId,
        level: 2,
        path: taskType.path,
        kind: "folder",
        name: taskType.name,
        parentId: sec2Id,
        hasChildren: !!taskType.children?.length,
        expanded: ttExpanded,
        ariaSelected: false,
      });
      if (ttExpanded && taskType.children) {
        for (const proj of taskType.children) {
          const pjId = `pj:${proj.path}`;
          const pjExpanded = opts.expanded[pjId] === true;
          nodes.push({
            id: pjId,
            level: 3,
            path: proj.path,
            kind: "folder",
            name: proj.name,
            parentId: ttId,
            hasChildren: !!proj.children?.length,
            expanded: pjExpanded,
            ariaSelected: false,
            isProjectFolder: true,
            projectType: taskType.name,
            projectName: proj.name,
          });
          if (pjExpanded && proj.children) {
            for (const stage of proj.children) {
              const stId = `st:${stage.path}`;
              const stExpanded = opts.expanded[stId] === true;
              if (
                stage.kind === "missing-folder" ||
                stage.present === false
              ) {
                nodes.push({
                  id: stId,
                  level: 4,
                  path: stage.path,
                  kind: "missing-folder",
                  name: stage.name,
                  parentId: pjId,
                  hasChildren: false,
                  ariaSelected: false,
                });
                continue;
              }
              nodes.push({
                id: stId,
                level: 4,
                path: stage.path,
                kind: "folder",
                name: stage.name,
                parentId: pjId,
                hasChildren: !!stage.children?.length,
                expanded: stExpanded,
                ariaSelected: false,
              });
              if (stExpanded && stage.children) {
                for (const f of stage.children) {
                  const isSelected =
                    opts.selectedPath !== null && opts.selectedPath === f.path;
                  nodes.push({
                    id: `file:${f.path}`,
                    level: 5,
                    path: f.path,
                    kind: "file",
                    name: f.name,
                    parentId: stId,
                    hasChildren: false,
                    ariaSelected: isSelected,
                  });
                }
              }
            }
          }
        }
      }
    }
  }

  return nodes;
}

function isFocusable(n: VisibleNode): boolean {
  return n.kind === "file" || n.kind === "folder";
}

function ancestorChainFor(
  tree: TreeResponse,
  path: string,
): string[] {
  const chain: string[] = [];
  for (const tt of tree.projects) {
    for (const proj of tt.children ?? []) {
      for (const stage of proj.children ?? []) {
        for (const f of stage.children ?? []) {
          if (f.kind === "file" && f.path === path) {
            chain.push("section:projects");
            chain.push(`tt:${tt.path}`);
            chain.push(`pj:${proj.path}`);
            chain.push(`st:${stage.path}`);
            return chain;
          }
        }
      }
    }
  }
  return chain;
}

export function Sidebar({
  tree,
  selectedPath,
  onRefresh,
}: SidebarProps): JSX.Element {
  const [state, setState] = useState<SidebarState>(() => loadSidebarState());
  const [focusedId, setFocusedId] = useState<string | null>(null);
  const treeRef = useRef<HTMLDivElement | null>(null);
  const navigate = useNavigate();

  // Restore expand-ancestor-chain when tree loads or selectedPath changes
  useEffect(() => {
    if (!tree || !selectedPath) return;
    const ancestors = ancestorChainFor(tree, selectedPath);
    if (ancestors.length === 0) return;
    setState((prev) => {
      const next = { ...prev.expanded };
      let changed = false;
      for (const a of ancestors) {
        if (next[a] !== true) {
          next[a] = true;
          changed = true;
        }
      }
      if (!changed) return prev;
      return { ...prev, expanded: next };
    });
  }, [tree, selectedPath]);

  // Persist last-selected path
  useEffect(() => {
    if (selectedPath !== null && selectedPath !== state.lastSelectedPath) {
      const next: SidebarState = { ...state, lastSelectedPath: selectedPath };
      setState(next);
      saveSidebarState(next);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedPath]);

  // Persist expand state
  useEffect(() => {
    saveSidebarState(state);
  }, [state]);

  const visible = useMemo(() => {
    if (!tree) return [];
    return buildVisible(tree, {
      expanded: state.expanded,
      selectedPath,
    });
  }, [tree, state.expanded, selectedPath]);

  const focusableIds = useMemo(
    () => visible.filter(isFocusable).map((n) => n.id),
    [visible],
  );

  // Initialize roving tabindex once visible nodes appear.
  useEffect(() => {
    if (focusedId === null && focusableIds.length > 0) {
      // Prefer the selected node if it's focusable; else first focusable
      const selectedId =
        selectedPath !== null ? `file:${selectedPath}` : null;
      if (selectedId && focusableIds.includes(selectedId)) {
        setFocusedId(selectedId);
      } else {
        setFocusedId(focusableIds[0] ?? null);
      }
    }
    if (focusedId !== null && !focusableIds.includes(focusedId)) {
      setFocusedId(focusableIds[0] ?? null);
    }
  }, [focusableIds, focusedId, selectedPath]);

  const toggleExpanded = useCallback((id: string): void => {
    setState((prev) => {
      const cur = prev.expanded[id] === true;
      return { ...prev, expanded: { ...prev.expanded, [id]: !cur } };
    });
  }, []);

  const setExpanded = useCallback((id: string, value: boolean): void => {
    setState((prev) => ({
      ...prev,
      expanded: { ...prev.expanded, [id]: value },
    }));
  }, []);

  const handleClickFolder = useCallback(
    (id: string, e: MouseEvent): void => {
      e.preventDefault();
      toggleExpanded(id);
      setFocusedId(id);
    },
    [toggleExpanded],
  );

  const handleClickFile = useCallback(
    (path: string, id: string, e: MouseEvent): void => {
      e.preventDefault();
      navigate(`/file/${encodeURI(path)}`);
      setFocusedId(id);
    },
    [navigate],
  );

  const moveFocus = useCallback(
    (delta: number): void => {
      if (focusedId === null) return;
      const idx = focusableIds.indexOf(focusedId);
      if (idx < 0) return;
      const next = idx + delta;
      if (next < 0 || next >= focusableIds.length) return;
      setFocusedId(focusableIds[next] ?? null);
    },
    [focusableIds, focusedId],
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLDivElement>): void => {
      if (focusedId === null) return;
      const node = visible.find((n) => n.id === focusedId);
      if (!node) return;
      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          moveFocus(1);
          break;
        case "ArrowUp":
          e.preventDefault();
          moveFocus(-1);
          break;
        case "ArrowRight":
          e.preventDefault();
          if (node.kind === "folder") {
            if (!node.expanded) {
              setExpanded(node.id, true);
            } else {
              moveFocus(1);
            }
          }
          break;
        case "ArrowLeft":
          e.preventDefault();
          if (node.kind === "folder" && node.expanded) {
            setExpanded(node.id, false);
          } else if (node.parentId !== null) {
            const parentIdx = focusableIds.indexOf(node.parentId);
            if (parentIdx >= 0) {
              setFocusedId(node.parentId);
            }
          }
          break;
        case "Enter":
          e.preventDefault();
          if (node.kind === "file" && node.path) {
            navigate(`/file/${encodeURI(node.path)}`);
          }
          break;
        case "Home":
          e.preventDefault();
          setFocusedId(focusableIds[0] ?? null);
          break;
        case "End":
          e.preventDefault();
          setFocusedId(focusableIds[focusableIds.length - 1] ?? null);
          break;
        default:
          break;
      }
    },
    [focusedId, visible, moveFocus, setExpanded, focusableIds, navigate],
  );

  if (!tree) {
    return (
      <aside className="sidebar" aria-label="File tree">
        <header className="sidebar-header">
          <h1 className="sidebar-title">spec_driven</h1>
          <RefreshButton onClick={onRefresh} />
        </header>
        <div className="sidebar-loading">Loading…</div>
      </aside>
    );
  }

  // Render Section 1 separately (always-expanded subgroups) — NOT inside the tree.
  const section1 = (
    <section className="sidebar-section sidebar-section-settings" aria-labelledby="settings-header">
      <h2 className="sidebar-section-header" id="settings-header">
        Claude Settings &amp; Shared Context
      </h2>
      <div className="sidebar-subgroup">
        <h3 className="sidebar-subgroup-header">CLAUDE.md</h3>
        <ul className="sidebar-list">
          {tree.settings.claude_md.map((f) => (
            <li key={f.path}>
              <Link
                to={`/file/${encodeURI(f.path)}`}
                className={
                  selectedPath === f.path
                    ? "sidebar-leaf sidebar-leaf-selected"
                    : "sidebar-leaf"
                }
                title={f.name}
                aria-current={selectedPath === f.path ? "page" : undefined}
              >
                <span className="sidebar-leaf-text">
                  {truncateFileName(f.name, 36)}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
      <div className="sidebar-subgroup">
        <h3 className="sidebar-subgroup-header">Agents</h3>
        <ul className="sidebar-list">
          {tree.settings.agents.map((f) => (
            <li key={f.path}>
              <Link
                to={`/file/${encodeURI(f.path)}`}
                className={
                  selectedPath === f.path
                    ? "sidebar-leaf sidebar-leaf-selected"
                    : "sidebar-leaf"
                }
                title={f.name}
              >
                <span className="sidebar-leaf-text">
                  {truncateFileName(f.name, 36)}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
      <div className="sidebar-subgroup">
        <h3 className="sidebar-subgroup-header">Skills</h3>
        <ul className="sidebar-list">
          {tree.settings.skills.map((f) => (
            <li key={f.path}>
              <Link
                to={`/file/${encodeURI(f.path)}`}
                className={
                  selectedPath === f.path
                    ? "sidebar-leaf sidebar-leaf-selected"
                    : "sidebar-leaf"
                }
                title={f.name}
              >
                <span className="sidebar-leaf-text">
                  {truncateFileName(f.name, 36)}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );

  // Section 2 is the tree.
  // Skip the synthetic settings nodes (we render Section 1 above as plain lists).
  const treeNodes = visible.filter(
    (n) =>
      n.kind !== "settings-section" &&
      n.kind !== "settings-group" &&
      !n.id.startsWith("file:CLAUDE.md") &&
      !n.id.startsWith("file:.claude/"),
  );

  return (
    <aside className="sidebar" aria-label="File tree">
      <header className="sidebar-header">
        <h1 className="sidebar-title">spec_driven</h1>
        <RefreshButton onClick={onRefresh} />
      </header>
      {section1}
      <section className="sidebar-section sidebar-section-projects">
        <div
          className="sidebar-tree"
          role="tree"
          aria-multiselectable="false"
          aria-label="Projects"
          ref={treeRef}
          onKeyDown={handleKeyDown}
        >
          {treeNodes.map((n) => {
            const isFocused = n.id === focusedId;
            const tabIndex = isFocused ? 0 : -1;
            if (n.kind === "missing-folder") {
              return (
                <div
                  key={n.id}
                  role="treeitem"
                  aria-level={n.level}
                  aria-disabled="true"
                  className="sidebar-treeitem sidebar-missing"
                  title="not yet generated"
                  tabIndex={-1}
                  style={{ paddingLeft: `${(n.level - 1) * 14 + 8}px` }}
                >
                  <span className="sidebar-leaf-text">{n.name}</span>
                </div>
              );
            }
            if (n.kind === "folder") {
              const expanded = !!n.expanded;
              const isProject = n.isProjectFolder === true;
              return (
                <div
                  key={n.id}
                  role="treeitem"
                  aria-level={n.level}
                  aria-expanded={expanded}
                  aria-selected={n.ariaSelected}
                  className="sidebar-treeitem sidebar-folder"
                  tabIndex={tabIndex}
                  onClick={(e) => handleClickFolder(n.id, e)}
                  onFocus={() => setFocusedId(n.id)}
                  style={{ paddingLeft: `${(n.level - 1) * 14 + 8}px` }}
                  title={n.name}
                >
                  <span className="sidebar-twisty" aria-hidden="true">
                    {expanded ? "▾" : "▸"}
                  </span>
                  <span className="sidebar-leaf-text">{n.name}</span>
                  {isProject && n.projectType && n.projectName && (
                    <Link
                      to={`/project/${encodeURIComponent(n.projectType)}/${encodeURIComponent(n.projectName)}`}
                      className="sidebar-project-link"
                      onClick={(e) => e.stopPropagation()}
                      tabIndex={-1}
                      title="Open project page"
                    >
                      &#x2197; project page
                    </Link>
                  )}
                </div>
              );
            }
            // file
            return (
              <div
                key={n.id}
                role="treeitem"
                aria-level={n.level}
                aria-selected={n.ariaSelected}
                className={
                  n.ariaSelected
                    ? "sidebar-treeitem sidebar-file sidebar-file-selected"
                    : "sidebar-treeitem sidebar-file"
                }
                tabIndex={tabIndex}
                onClick={(e) =>
                  n.path ? handleClickFile(n.path, n.id, e) : undefined
                }
                onFocus={() => setFocusedId(n.id)}
                style={{ paddingLeft: `${(n.level - 1) * 14 + 22}px` }}
                title={n.name}
                data-path={n.path ?? undefined}
              >
                <span className="sidebar-leaf-text">
                  {truncateFileName(n.name, 36)}
                </span>
              </div>
            );
          })}
        </div>
      </section>
    </aside>
  );
}
