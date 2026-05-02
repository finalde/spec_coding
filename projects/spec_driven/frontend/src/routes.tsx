import { useEffect, useMemo, useState } from "react";
import { Navigate, Route, Routes, useNavigate, useParams } from "react-router-dom";
import { fetchTree } from "./api";
import { Reader } from "./components/Reader";
import { Sidebar } from "./components/Sidebar";
import type { TreeNode, TreeResponse } from "./types";

const DEFAULT_FILE = "specs/development/spec_driven/final_specs/spec.md";
const FALLBACK_FILE = "specs/development/spec_driven/user_input/revised_prompt.md";

export function AppRoutes(): JSX.Element {
  const [tree, setTree] = useState<TreeResponse | null>(null);
  const [refreshTick, setRefreshTick] = useState<number>(0);

  useEffect(() => {
    let cancelled = false;
    fetchTree()
      .then((t) => {
        if (!cancelled) setTree(t);
      })
      .catch(() => {
        if (!cancelled) setTree(null);
      });
    return () => {
      cancelled = true;
    };
  }, [refreshTick]);

  const exposedPaths = useMemo(() => buildExposedPaths(tree), [tree]);

  const onRefresh = (): void => setRefreshTick((t) => t + 1);

  return (
    <Routes>
      <Route path="/" element={<DefaultRedirect tree={tree} />} />
      <Route
        path="/file/*"
        element={
          <Layout
            tree={tree}
            exposedPaths={exposedPaths}
            onRefresh={onRefresh}
          />
        }
      />
      <Route path="*" element={<DefaultRedirect tree={tree} />} />
    </Routes>
  );
}

function Layout({
  tree,
  exposedPaths,
  onRefresh,
}: {
  tree: TreeResponse | null;
  exposedPaths: ReadonlySet<string>;
  onRefresh: () => void;
}): JSX.Element {
  const params = useParams();
  const splat = params["*"] ?? "";
  const filePath = decodeURI(splat);
  return (
    <div className="layout">
      <Sidebar tree={tree} onRefresh={onRefresh} selectedPath={filePath} />
      <Reader filePath={filePath} exposedPaths={exposedPaths} onRequestRefresh={onRefresh} />
    </div>
  );
}

function DefaultRedirect({ tree }: { tree: TreeResponse | null }): JSX.Element {
  const navigate = useNavigate();
  useEffect(() => {
    if (!tree) return;
    const paths = collectFilePaths(tree);
    const target = paths.has(DEFAULT_FILE) ? DEFAULT_FILE : FALLBACK_FILE;
    navigate(`/file/${encodeURI(target)}`, { replace: true });
  }, [tree, navigate]);
  if (!tree) {
    return <div className="boot-loading">Loading…</div>;
  }
  return <Navigate to={`/file/${encodeURI(FALLBACK_FILE)}`} replace />;
}

function collectFilePaths(tree: TreeResponse): Set<string> {
  const out = new Set<string>();
  const visit = (node: TreeNode): void => {
    if (node.kind === "file") out.add(node.path);
    if (node.children) node.children.forEach(visit);
  };
  tree.settings.claude_md.forEach(visit);
  tree.settings.agents.forEach(visit);
  tree.settings.skills.forEach(visit);
  tree.projects.forEach(visit);
  return out;
}

function buildExposedPaths(tree: TreeResponse | null): ReadonlySet<string> {
  if (!tree) return new Set();
  return collectFilePaths(tree);
}
