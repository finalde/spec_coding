import { useCallback, useEffect, useMemo, useState } from "react";
import { Routes, Route, Navigate, useLocation, useNavigate } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";
import { Reader } from "./components/Reader";
import { Home } from "./components/Home";
import { ProjectPage } from "./components/ProjectPage";
import { StagePage } from "./components/StagePage";
import { fetchTree } from "./api";
import { collectFilePaths } from "./lib/linkResolver";
import type { TreeNode } from "./types";

export default function App(): JSX.Element {
  const [tree, setTree] = useState<TreeNode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState<number>(0);
  const navigate = useNavigate();
  const location = useLocation();

  const loadTree = useCallback(async () => {
    try {
      const t = await fetchTree();
      setTree(t);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, []);

  useEffect(() => {
    void loadTree();
  }, [loadTree, refreshKey]);

  const knownPaths = useMemo(() => (tree ? collectFilePaths(tree) : []), [tree]);

  const currentPath = useMemo<string>(() => {
    if (!location.pathname.startsWith("/file/")) return "";
    const encoded = location.pathname.slice("/file/".length);
    try {
      return decodeURIComponent(encoded);
    } catch {
      return "";
    }
  }, [location.pathname]);

  const onSelect = useCallback(
    (path: string) => {
      navigate(`/file/${encodeURIComponent(path)}`);
    },
    [navigate],
  );

  const onSkipToMain = (e: React.MouseEvent<HTMLAnchorElement>): void => {
    e.preventDefault();
    const main = document.getElementById("main");
    if (main) {
      main.setAttribute("tabindex", "-1");
      main.focus();
    }
  };

  return (
    <div className="app-root">
      <a className="skip-link" href="#main" onClick={onSkipToMain}>
        Skip to main content
      </a>
      <Sidebar tree={tree} currentPath={currentPath} onSelect={onSelect} loadError={error} />
      <main id="main" className="main-pane" aria-label="Main content">
        <Routes>
          <Route path="/" element={<Home tree={tree} />} />
          <Route
            path="/file/*"
            element={
              <Reader
                knownPaths={knownPaths}
                onSaved={() => setRefreshKey((k) => k + 1)}
              />
            }
          />
          <Route
            path="/project/:projectType/:projectName"
            element={<ProjectPage />}
          />
          <Route
            path="/stage/:projectType/:projectName/:stage"
            element={<StagePage />}
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}
