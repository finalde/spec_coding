import { useEffect, useState } from "react";
import {
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
} from "react-router-dom";
import { fetchTree } from "./api";
import type { TreeNode, TreeResponse } from "./types";
import { Sidebar } from "./components/Sidebar";
import { Reader } from "./components/Reader";
import { ProjectPage } from "./components/ProjectPage";

const FALLBACK_SPEC = "specs/development/spec_driven/final_specs/spec.md";
const FALLBACK_REVISED = "specs/development/spec_driven/user_input/revised_prompt.md";

function _walk(nodes: ReadonlyArray<TreeNode>, out: string[]): void {
  for (const n of nodes) {
    if (n.kind === "file") out.push(n.path);
    if (n.children) _walk(n.children, out);
  }
}

function flattenAllFiles(tree: TreeResponse): string[] {
  const out: string[] = [];
  _walk(tree.settings.claude_md, out);
  _walk(tree.settings.agents, out);
  _walk(tree.settings.skills, out);
  _walk(tree.projects, out);
  return out;
}

function DefaultRedirect(): JSX.Element {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchTree()
      .then((tree) => {
        if (cancelled) return;
        const all = flattenAllFiles(tree);
        let target: string | null = null;
        if (all.includes(FALLBACK_SPEC)) {
          target = FALLBACK_SPEC;
        } else if (all.includes(FALLBACK_REVISED)) {
          target = FALLBACK_REVISED;
        } else if (all.length > 0) {
          target = all[0]!;
        }
        if (target) {
          navigate(`/file/${encodeURI(target)}`, { replace: true });
        } else {
          setError("no files yet");
        }
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : "tree fetch failed");
      });
    return () => {
      cancelled = true;
    };
  }, [navigate]);

  if (error) {
    return (
      <div className="empty-state" role="status">
        no files yet
      </div>
    );
  }
  return <div className="loading">Loading…</div>;
}

function Layout(): JSX.Element {
  const location = useLocation();
  const splat = location.pathname.replace(/^\/file\//, "");
  const filePath = decodeURI(splat);
  const [tree, setTree] = useState<TreeResponse | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

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
  }, [refreshKey]);

  const onRefresh = (): void => setRefreshKey((k) => k + 1);

  return (
    <div className="app-layout">
      <Sidebar
        tree={tree}
        selectedPath={filePath}
        onRefresh={onRefresh}
      />
      <main className="reader-pane">
        <Reader
          filePath={filePath}
          tree={tree}
          onRefresh={onRefresh}
        />
      </main>
    </div>
  );
}

function ProjectLayout(): JSX.Element {
  const params = useParams<{ projectType: string; projectName: string }>();
  const [tree, setTree] = useState<TreeResponse | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

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
  }, [refreshKey]);

  const onRefresh = (): void => setRefreshKey((k) => k + 1);

  return (
    <div className="app-layout">
      <Sidebar tree={tree} selectedPath={null} onRefresh={onRefresh} />
      <main className="reader-pane">
        <ProjectPage
          projectType={params.projectType ?? ""}
          projectName={params.projectName ?? ""}
        />
      </main>
    </div>
  );
}

// Folder-only redirect: /file/.../stage/  (trailing slash) -> first file
function FolderRedirect(): JSX.Element {
  const location = useLocation();
  const navigate = useNavigate();
  const [empty, setEmpty] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const splat = location.pathname.replace(/^\/file\//, "");
    const decoded = decodeURI(splat);
    const folderPath = decoded.replace(/\/$/, "");
    fetchTree()
      .then((tree) => {
        if (cancelled) return;
        const all = flattenAllFiles(tree);
        const first = all.find((p) =>
          p.startsWith(folderPath + "/") &&
          p.slice(folderPath.length + 1).indexOf("/") === -1,
        );
        if (first) {
          navigate(`/file/${encodeURI(first)}`, { replace: true });
        } else {
          setEmpty(true);
        }
      })
      .catch(() => {
        if (!cancelled) setEmpty(true);
      });
    return () => {
      cancelled = true;
    };
  }, [location.pathname, navigate]);

  if (empty) {
    return (
      <div className="empty-state" role="status">
        no files yet
      </div>
    );
  }
  return <div className="loading">Loading…</div>;
}

export function AppRoutes(): JSX.Element {
  return (
    <Routes>
      <Route path="/" element={<DefaultRedirect />} />
      <Route path="/file/*" element={<FileRouter />} />
      <Route
        path="/project/:projectType/:projectName"
        element={<ProjectLayout />}
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

// Disambiguates folder-only URLs (trailing slash) from file URLs.
function FileRouter(): JSX.Element {
  const location = useLocation();
  if (location.pathname.endsWith("/")) {
    return <FolderRedirect />;
  }
  // Also detect: path has no recognizable file extension -> treat as folder.
  const splat = location.pathname.replace(/^\/file\//, "");
  const decoded = decodeURI(splat);
  const last = decoded.split("/").pop() ?? "";
  if (last && !last.includes(".")) {
    return <FolderRedirect />;
  }
  return <Layout />;
}
