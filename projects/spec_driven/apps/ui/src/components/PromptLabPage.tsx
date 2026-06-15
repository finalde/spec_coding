import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  createPromptLabFile,
  deletePromptLabFile,
  executePromptLab,
  fetchFile,
  fetchPromptLab,
  getPromptLabRun,
  putFile,
  stopPromptLab,
} from "../api";
import { Editor } from "./Editor";
import { Renderer } from "../markdown/renderer";
import {
  ApiError,
  type FileResult,
  type PromptLabEntry,
  type PromptLabOverview,
  type PromptLabRun,
} from "../types";

function fileTemplate(title: string): string {
  return `# ${title}

**Stack:** _stack_ · **Est:** _time_ · **Output:** _what you get_

## ✨ 1. Expectation — what you'll get

_After you run the prompt, what concretely happens and the impressive result you can see/share._

**Why it's cool:** _the wow / innovation angle._

**Use cases:** _2–4 concrete applicable use cases — who'd use this and for what._

## ▶️ 2. How to run

_Copy-paste-and-walk-away: paste the prompt below into Claude Code in an empty folder, answer the short setup questions, then it runs autonomously. Prerequisites: none / \`pip install ...\` / a tiny server._

## 🔗 3. Reference & prior art

_This prompt is original — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:_

**Source:** [owner/repo](https://github.com/owner/repo) · **Expected result:** [reference examples](https://example.com)

---

## 📋 COPY-PASTE PROMPT

\`\`\`
You are building _X_.

PHASE 1 — SETUP (ask me these questions, then STOP and wait):
1. ...

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, self-review against the checklist, fix, repeat.

ACCEPTANCE CHECKLIST (finish line):
- [ ] ...

STOP CONDITIONS: stop when every item passes, OR after 6 self-review rounds. Then open/run the result.
\`\`\`

---

## Remix ideas

_Follow-up prompts to push it further._
`;
}

export function PromptLabPage(): JSX.Element {
  const navigate = useNavigate();
  const [overview, setOverview] = useState<PromptLabOverview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<boolean>(false);
  const [showNew, setShowNew] = useState<boolean>(false);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);

  // Inline view/edit state (kept INSIDE this page so the category nav never changes).
  const [file, setFile] = useState<FileResult | null>(null);
  const [editing, setEditing] = useState<boolean>(false);
  const [saveError, setSaveError] = useState<Error | null>(null);
  const [conflict, setConflict] = useState<{ current_mtime: string } | null>(null);

  // Autonomous-run state for the selected item (FR-44).
  const [run, setRun] = useState<PromptLabRun | null>(null);
  const [runBusy, setRunBusy] = useState<boolean>(false);

  const load = useCallback(async () => {
    try {
      setOverview(await fetchPromptLab());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const categories = useMemo(() => overview?.categories ?? [], [overview]);
  const total = useMemo(
    () => categories.reduce((n, c) => n + c.entries.length, 0),
    [categories],
  );
  const existingCategories = useMemo(() => categories.map((c) => c.name), [categories]);

  const selected = useMemo<PromptLabEntry | null>(() => {
    for (const c of categories) {
      for (const e of c.entries) if (e.path === selectedPath) return e;
    }
    return null;
  }, [categories, selectedPath]);

  // Default to the first task once the library loads.
  useEffect(() => {
    if (!showNew && selectedPath === null && categories.length > 0) {
      const first = categories[0].entries[0];
      if (first) setSelectedPath(first.path);
    }
  }, [categories, selectedPath, showNew]);

  // Whenever the selected task changes, (re)load its full file content for the main pane.
  useEffect(() => {
    if (!selectedPath) {
      setFile(null);
      return;
    }
    let cancelled = false;
    setFile(null);
    setSaveError(null);
    setConflict(null);
    fetchFile(selectedPath)
      .then((f) => {
        if (!cancelled) setFile(f);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : String(err));
      });
    return () => {
      cancelled = true;
    };
  }, [selectedPath]);

  const selectTask = useCallback((path: string) => {
    setShowNew(false);
    setEditing(false);
    setSelectedPath(path);
  }, []);

  // Load the run status for the selected item (shows a prior run if any).
  useEffect(() => {
    if (!selectedPath) {
      setRun(null);
      return;
    }
    let cancelled = false;
    getPromptLabRun(selectedPath)
      .then((r) => {
        if (!cancelled) setRun(r);
      })
      .catch(() => {
        if (!cancelled) setRun(null);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedPath]);

  // Poll while a run is in progress.
  useEffect(() => {
    if (!selectedPath || run?.state !== "running") return;
    const id = window.setInterval(() => {
      getPromptLabRun(selectedPath)
        .then(setRun)
        .catch(() => {});
    }, 2000);
    return () => window.clearInterval(id);
  }, [selectedPath, run?.state]);

  const refreshRun = useCallback(async () => {
    if (!selectedPath) return;
    try {
      setRun(await getPromptLabRun(selectedPath));
    } catch {
      /* ignore */
    }
  }, [selectedPath]);

  const onExecute = useCallback(async () => {
    if (!selected) return;
    setRunBusy(true);
    setError(null);
    try {
      await executePromptLab(selected.path);
      await refreshRun();
    } catch (err) {
      if (err instanceof ApiError && err.status === 503) {
        setError("The `claude` CLI isn't available to the server, so autonomous execution can't start.");
      } else if (err instanceof ApiError && err.status === 409) {
        setError("A run is already in progress for this item.");
      } else {
        setError(err instanceof Error ? err.message : String(err));
      }
    } finally {
      setRunBusy(false);
    }
  }, [selected, refreshRun]);

  const onStop = useCallback(async () => {
    if (!selected) return;
    setRunBusy(true);
    try {
      await stopPromptLab(selected.path);
      await refreshRun();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setRunBusy(false);
    }
  }, [selected, refreshRun]);

  const onSave = useCallback(
    async (newContent: string): Promise<void> => {
      if (!file || !selectedPath) return;
      try {
        const result = await putFile(selectedPath, newContent, {
          ifUnmodifiedSince: file.mtime,
        });
        setFile({ ...file, content: newContent, ...result });
        setSaveError(null);
        setConflict(null);
        await load(); // refresh the parsed overview (title/prompt may have changed)
      } catch (err) {
        if (err instanceof ApiError) {
          if (err.status === 409 && err.detail?.kind === "stale_write") {
            const cm = (err.detail as { current_mtime?: string }).current_mtime;
            setConflict({ current_mtime: cm ?? "" });
          } else {
            setSaveError(err);
          }
        } else if (err instanceof Error) {
          setSaveError(err);
        }
        throw err;
      }
    },
    [file, selectedPath, load],
  );

  const onDelete = useCallback(
    async (entry: PromptLabEntry) => {
      if (!window.confirm(`Delete ${entry.path}? This cannot be undone.`)) return;
      setBusy(true);
      try {
        await deletePromptLabFile(entry.path);
        if (selectedPath === entry.path) {
          setSelectedPath(null);
          setEditing(false);
        }
        await load();
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setBusy(false);
      }
    },
    [load, selectedPath],
  );

  const onCreate = useCallback(
    async (category: string, filename: string, title: string) => {
      setBusy(true);
      try {
        const result = await createPromptLabFile({
          category,
          filename,
          content: fileTemplate(title || filename.replace(/\.md$/, "")),
        });
        setShowNew(false);
        await load();
        setSelectedPath(result.path);
        setEditing(true); // open the new file straight into the inline editor
      } catch (err) {
        if (err instanceof ApiError && err.status === 409) {
          setError("A prompt with that category + filename already exists.");
        } else {
          setError(err instanceof Error ? err.message : String(err));
        }
      } finally {
        setBusy(false);
      }
    },
    [load],
  );

  return (
    <div className="app-root">
      <a className="skip-link" href="#main">
        Skip to main content
      </a>
      <nav className="sidebar promptlab-nav" aria-label="Prompt Lab navigation">
        <div className="sidebar-header">
          <button
            type="button"
            className="sidebar-back"
            onClick={() => navigate("/")}
            aria-label="Back to home"
          >
            ← Home
          </button>
        </div>
        <div className="promptlab-nav-titlebar">
          <span className="promptlab-nav-title">Prompt Lab</span>
          <button
            type="button"
            className="promptlab-new-btn"
            onClick={() => {
              setShowNew(true);
              setEditing(false);
              setSelectedPath(null);
            }}
            disabled={busy}
          >
            + New
          </button>
        </div>
        <p className="promptlab-nav-sub muted">
          {total} prompts · {categories.length} categories
        </p>
        <div className="promptlab-nav-tree">
          {categories.map((cat) => (
            <div key={cat.name} className="promptlab-nav-cat">
              <div className="promptlab-nav-cat-title">
                {cat.name} <span className="muted">({cat.entries.length})</span>
              </div>
              {cat.entries.map((entry) => (
                <button
                  key={entry.path}
                  type="button"
                  className={[
                    "promptlab-nav-item",
                    !showNew && entry.path === selectedPath ? "active" : "",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                  aria-current={!showNew && entry.path === selectedPath ? "true" : undefined}
                  onClick={() => selectTask(entry.path)}
                  title={entry.title}
                >
                  {entry.title}
                </button>
              ))}
            </div>
          ))}
        </div>
      </nav>

      <main id="main" className="main-pane promptlab-main" aria-label="Main content">
        {error ? (
          <div role="alert" className="save-error-banner">
            {error}
          </div>
        ) : null}

        {showNew ? (
          <NewPromptForm
            existingCategories={existingCategories}
            busy={busy}
            onCancel={() => setShowNew(false)}
            onCreate={onCreate}
          />
        ) : overview === null ? (
          <p className="muted">Loading…</p>
        ) : !selected ? (
          <p className="muted">Select a prompt from the left, or create a new one.</p>
        ) : (
          <article className="promptlab-detail">
            <div className="promptlab-detail-toolbar">
              <span className="promptlab-detail-path">{selected.path}</span>
              <div className="promptlab-detail-actions">
                {run?.state === "running" ? (
                  <button
                    type="button"
                    className="promptlab-stop"
                    onClick={() => void onStop()}
                    disabled={runBusy}
                  >
                    ⏹ Stop run
                  </button>
                ) : (
                  <button
                    type="button"
                    className="promptlab-execute"
                    onClick={() => void onExecute()}
                    disabled={runBusy}
                    title="Spawn an autonomous Claude session in this item's workspace"
                  >
                    ▶ Execute
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => setEditing((e) => !e)}
                  aria-pressed={editing}
                >
                  ✎ {editing ? "Editing" : "Edit"}
                </button>
                <button
                  type="button"
                  className="promptlab-delete"
                  onClick={() => void onDelete(selected)}
                  disabled={busy}
                >
                  Delete
                </button>
              </div>
            </div>

            {file === null ? (
              <p className="muted">Loading…</p>
            ) : editing ? (
              <Editor
                initialContent={file.content}
                filename={selected.name}
                onSave={onSave}
                onClose={() => setEditing(false)}
                onReload={async () => {
                  const f = await fetchFile(selected.path);
                  setFile(f);
                }}
                saveError={saveError}
                conflict={conflict}
                onClearConflict={() => setConflict(null)}
                onDirtyChange={() => {}}
              />
            ) : (
              <Renderer
                content={file.content}
                currentPath={selected.path}
                knownPaths={[]}
                promptMode={{ onEditPrompt: () => setEditing(true) }}
              />
            )}
            {run && run.state !== "idle" ? <RunPanel run={run} /> : null}
          </article>
        )}
      </main>
    </div>
  );
}

function RunPanel({ run }: { run: PromptLabRun }): JSX.Element {
  const badge: Record<string, string> = {
    running: "● running",
    succeeded: "✓ succeeded",
    failed: "✗ failed",
    stopped: "■ stopped",
    idle: "idle",
  };
  return (
    <section className={`promptlab-run promptlab-run-${run.state}`} aria-label="Autonomous run">
      <div className="promptlab-run-head">
        <span className={`promptlab-run-badge promptlab-run-badge-${run.state}`}>
          {badge[run.state] ?? run.state}
        </span>
        {run.run_id ? <span className="muted">run {run.run_id}</span> : null}
        {run.exit_code !== null && run.exit_code !== undefined ? (
          <span className="muted">exit {run.exit_code}</span>
        ) : null}
      </div>

      <h3 className="promptlab-run-subhead">
        Autonomous decisions{run.decisions.length ? ` (${run.decisions.length})` : ""}
      </h3>
      {run.decisions.length === 0 ? (
        <p className="muted">
          No decisions logged yet — they appear here as the session makes autonomous choices.
        </p>
      ) : (
        <ul className="promptlab-decisions">
          {run.decisions.map((d, i) => (
            <li key={i} className="promptlab-decision">
              <div className="promptlab-decision-q">{d.question ?? "(decision)"}</div>
              <div className="promptlab-decision-d">→ {d.decision ?? ""}</div>
              {d.why ? <div className="promptlab-decision-why muted">{d.why}</div> : null}
            </li>
          ))}
        </ul>
      )}

      {run.files.length ? (
        <>
          <h3 className="promptlab-run-subhead">Generated files ({run.files.length})</h3>
          <ul className="promptlab-run-files">
            {run.files.map((f) => (
              <li key={f.name}>
                <code>{f.name}</code> <span className="muted">{f.bytes} B</span>
              </li>
            ))}
          </ul>
        </>
      ) : null}

      <h3 className="promptlab-run-subhead">Session output</h3>
      <pre className="promptlab-run-output">{run.output || "(no output yet)"}</pre>
    </section>
  );
}

function NewPromptForm({
  existingCategories,
  busy,
  onCancel,
  onCreate,
}: {
  existingCategories: string[];
  busy: boolean;
  onCancel: () => void;
  onCreate: (category: string, filename: string, title: string) => void;
}): JSX.Element {
  const [category, setCategory] = useState<string>(existingCategories[0] ?? "");
  const [title, setTitle] = useState<string>("");
  const [filename, setFilename] = useState<string>("");

  const slug = (s: string): string =>
    s.trim().toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");

  const submit = (e: React.FormEvent): void => {
    e.preventDefault();
    const cat = slug(category);
    const baseName = slug(filename || title);
    if (!cat || !baseName) return;
    onCreate(cat, `${baseName}.md`, title);
  };

  return (
    <form className="promptlab-newform" onSubmit={submit}>
      <h1 className="promptlab-detail-title">New prompt</h1>
      <div className="promptlab-newform-row">
        <label>
          Category
          <input
            list="promptlab-categories"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="games_interactive"
            required
          />
          <datalist id="promptlab-categories">
            {existingCategories.map((c) => (
              <option key={c} value={c} />
            ))}
          </datalist>
        </label>
        <label>
          Title
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="My Impressive Build"
            required
          />
        </label>
        <label>
          Filename
          <input
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
            placeholder="(defaults from title)"
          />
          <span className="promptlab-newform-ext">.md</span>
        </label>
      </div>
      <div className="promptlab-newform-actions">
        <button type="submit" disabled={busy}>
          Create
        </button>
        <button type="button" onClick={onCancel} disabled={busy}>
          Cancel
        </button>
      </div>
    </form>
  );
}
