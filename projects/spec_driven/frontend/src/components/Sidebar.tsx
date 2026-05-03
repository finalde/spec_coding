import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchTree } from "../api";
import type { TreeNode as TN } from "../types";

interface NodeProps {
  node: TN;
  depth: number;
}

function isProject(n: TN): boolean {
  return n.type === "project";
}

function TreeNodeItem({ node, depth }: NodeProps) {
  const [open, setOpen] = useState<boolean>(depth < 2);

  if (!node.children || node.children.length === 0) {
    if (node.type === "file") {
      return (
        <li>
          <Link
            to={`/file/${node.path}`}
            data-testid="tree-leaf"
            data-file-path={node.path}
            style={{ paddingLeft: `${depth * 12}px` }}
          >
            {node.name}
          </Link>
        </li>
      );
    }
    return (
      <li>
        <span style={{ paddingLeft: `${depth * 12}px` }}>{node.name}</span>
      </li>
    );
  }

  return (
    <li
      data-section={
        node.path === "_claude" ? "claude" : node.path === "_projects" ? "projects" : undefined
      }
    >
      <details open={open} onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)}>
        <summary
          style={{ paddingLeft: `${depth * 12}px` }}
          aria-expanded={open}
        >
          <span className="tree-name">{node.name}</span>
          {isProject(node) && (
            <Link
              to={`/project/${node.path.replace(/^specs\//, "")}`}
              className="project-link"
              data-testid="project-link"
              aria-label={`Open project page for ${node.name}`}
              onClick={(e) => e.stopPropagation()}
            >
              ↗
            </Link>
          )}
        </summary>
        <ul className="tree-children">
          {node.children.map((c) => (
            <TreeNodeItem key={c.path} node={c} depth={depth + 1} />
          ))}
        </ul>
      </details>
    </li>
  );
}

export function Sidebar() {
  const [tree, setTree] = useState<TN | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTree()
      .then(setTree)
      .catch((e) => setError(String(e)));
  }, []);

  if (error) {
    return (
      <aside className="sidebar" data-testid="sidebar" aria-label="File navigation">
        <p role="alert">Could not load tree: {error}</p>
      </aside>
    );
  }
  if (!tree) {
    return (
      <aside className="sidebar" data-testid="sidebar" aria-label="File navigation">
        <p>Loading…</p>
      </aside>
    );
  }
  return (
    <aside className="sidebar" data-testid="sidebar" aria-label="File navigation">
      <ul className="tree-root" role="tree">
        {tree.children.map((c) => (
          <TreeNodeItem key={c.path} node={c} depth={0} />
        ))}
      </ul>
    </aside>
  );
}
