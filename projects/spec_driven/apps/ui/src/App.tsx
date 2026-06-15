import { useCallback, useEffect, useMemo, useState } from "react";
import { Routes, Route, Navigate, useLocation, useNavigate } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";
import { Reader } from "./components/Reader";
import { Home } from "./components/Home";
import { ProjectPage } from "./components/ProjectPage";
import { StagePage } from "./components/StagePage";
import { PromptLabPage } from "./components/PromptLabPage";
import { fetchTree } from "./api";
import { collectFilePaths } from "./lib/linkResolver";
import {
  type ActiveProject,
  readActiveProject,
  writeActiveProject,
} from "./lib/activeProject";
import type { TreeNode } from "./types";

function deriveActiveProjectFromPath(pathname: string): ActiveProject | null {
  const projectMatch = pathname.match(/^\/project\/([^/]+)\/([^/]+)\/?$/);
  if (projectMatch) {
    return {
      type: decodeURIComponent(projectMatch[1]),
      name: decodeURIComponent(projectMatch[2]),
    };
  }
  const stageMatch = pathname.match(/^\/stage\/([^/]+)\/([^/]+)\/([^/]+)\/?$/);
  if (stageMatch) {
    return {
      type: decodeURIComponent(stageMatch[1]),
      name: decodeURIComponent(stageMatch[2]),
    };
  }
  if (pathname.startsWith("/file/")) {
    const encoded = pathname.slice("/file/".length);
    let decoded = "";
    try {
      decoded = decodeURIComponent(encoded);
    } catch {
      return null;
    }
    const parts = decoded.split("/");
    if (parts[0] === "specs" && parts.length >= 3 && parts[1] && parts[2]) {
      return { type: parts[1], name: parts[2] };
    }
  }
  return null;
}

function sameProject(a: ActiveProject | null, b: ActiveProject | null): boolean {
  if (a === null || b === null) return a === b;
  return a.type === b.type && a.name === b.name;
}

export default function App(): JSX.Element {
  const [tree, setTree] = useState<TreeNode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState<number>(0);
  const [activeProject, setActiveProject] = useState<ActiveProject | null>(() =>
    readActiveProject(),
  );
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

  useEffect(() => {
    const fromUrl = deriveActiveProjectFromPath(location.pathname);
    if (fromUrl && !sameProject(fromUrl, activeProject)) {
      setActiveProject(fromUrl);
      writeActiveProject(fromUrl);
    }
  }, [location.pathname, activeProject]);

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

  const onPickProject = useCallback(
    (project: ActiveProject) => {
      setActiveProject(project);
      writeActiveProject(project);
      navigate(
        `/project/${encodeURIComponent(project.type)}/${encodeURIComponent(project.name)}`,
      );
    },
    [navigate],
  );

  const onBackToProjects = useCallback(() => {
    setActiveProject(null);
    writeActiveProject(null);
    navigate("/");
  }, [navigate]);

  const onSkipToMain = (e: React.MouseEvent<HTMLAnchorElement>): void => {
    e.preventDefault();
    const main = document.getElementById("main");
    if (main) {
      main.setAttribute("tabindex", "-1");
      main.focus();
    }
  };

  const isLanding = location.pathname === "/";
  const isPromptLab = location.pathname === "/prompt-lab";

  if (isLanding) {
    return (
      <div className="app-root app-root-landing">
        <a className="skip-link" href="#main" onClick={onSkipToMain}>
          Skip to main content
        </a>
        <main id="main" className="picker-pane" aria-label="Main content">
          <Home
            tree={tree}
            loadError={error}
            onPick={onPickProject}
            onOpenPromptLab={() => navigate("/prompt-lab")}
          />
        </main>
      </div>
    );
  }

  if (isPromptLab) {
    return <PromptLabPage />;
  }

  return (
    <div className="app-root">
      <a className="skip-link" href="#main" onClick={onSkipToMain}>
        Skip to main content
      </a>
      <Sidebar
        tree={tree}
        currentPath={currentPath}
        onSelect={onSelect}
        loadError={error}
        activeProject={activeProject}
        onBackToProjects={onBackToProjects}
      />
      <main id="main" className="main-pane" aria-label="Main content">
        <Routes>
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
