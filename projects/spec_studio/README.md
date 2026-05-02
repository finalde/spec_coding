# spec_studio

FastAPI + React platform for the **spec-coding workflow**. The backend exposes the planning + execution pipeline as REST/SSE; the frontend renders a task dashboard plus a per-task **5-module navigation** (Input · Interview Questions · Specs · Findings · Execution Plan) where every artifact is **editable in place**.

`spec_studio` lives under `projects/` like every other project, but it has a special role: it is the platform that drives the spec-coding pipeline for *all other* user tasks (whose outputs land in sibling `projects/<name>/` or `ai_videos/<name>/` folders).

UI library: **Mantine v9** (CSS-modules, no runtime CSS-in-JS). Free-form markdown via **`@uiw/react-md-editor`**. The Execution Plan module's YAML editor is **`@monaco-editor/react`** + **`monaco-yaml`** with a JSON Schema for `plan.yaml`, lazy-loaded on the Plan route only.

## Layout

```
projects/spec_studio/
├── README.md
├── requirements.txt          # -r backend/requirements.txt
├── main.py                   # backend entry — `python projects/spec_studio/main.py`
├── backend/
│   ├── requirements.txt
│   └── libs/
│       ├── app.py            # FastAPI factory + router wiring (incl. inputs/edits/interview)
│       ├── config.py         # @dataclass(frozen=True) Settings (repo_root, specs_root, audit_root, ...)
│       ├── models/           # Pydantic schemas (Task, Phase, Artifact, InputBundle, InterviewQA, ...)
│       ├── storage/          # FileStore + AtomicWriter + BackupWriter (.bak snapshots)
│       ├── edits/            # RepoInputResolver (allowlist + traversal protection)
│       ├── parsers/          # qa_parser — bidirectional qa.md ⇄ typed InterviewQA
│       ├── agents/           # ClaudeRunner wrapping claude-agent-sdk
│       ├── runs/             # RunRegistry (asyncio task pool, Semaphore-bounded)
│       └── routes/           # tasks, phases, events (SSE), artifacts, inputs, edits, interview
└── frontend/
    ├── package.json          # vite, react, ts, mantine v9, monaco-yaml, @uiw/react-md-editor
    └── src/
        ├── pages/{Dashboard,TaskDetail}.tsx
        ├── components/modules/         # InputModule, InterviewModule + InterviewQuestionCard,
        │                                #   SpecsModule, FindingsModule, ExecutionPlanModule
        ├── editor/                     # monaco_setup.ts + yaml.worker.ts (Vite worker config)
        ├── schemas/plan.schema.json    # JSON Schema for monaco-yaml validation
        ├── api/client.ts               # GET/PUT against the REST surface
        ├── hooks/useEventStream.ts
        └── types/                      # mirrors of backend Pydantic schemas
```

## Persistence

File-based, single-user, local. The `specs/` folder at the repo root **is** the database; `specs/index.json` is the task registry. Live event streaming reads from `.audit/adhoc_agents/{date}/{task_id}/events.jsonl` (gitignored — local only).

## Run model

Each phase invocation creates an in-process `asyncio.Task` owned by `RunRegistry`. Runs are bounded by an `asyncio.Semaphore` (default cap: 3). Events stream from the SDK into the per-run JSONL file *and* an in-memory queue; SSE handlers subscribe to the queue and replay missed lines from the JSONL on reconnect (via `Last-Event-ID`).

## Running locally

Two terminals — start backend and frontend separately.

```bash
# one-time install (from repo root)
uv sync                                                       # python deps
( cd projects/spec_studio/frontend && npm install --legacy-peer-deps )

# terminal 1 — backend (FastAPI on :8000)
python projects/spec_studio/main.py

# terminal 2 — frontend (Vite dev on :5173)
cd projects/spec_studio/frontend && npm run ui
```

Open the UI at `http://127.0.0.1:5173`. Vite proxies `/api` → `http://127.0.0.1:8000`.

Backend binds `127.0.0.1` by default. CORS regex permits any port on `127.0.0.1` / `localhost` — single-user local only, no auth.

To override ports: `BACKEND_PORT=9000 python projects/spec_studio/main.py` and `npm run ui -- --port 3000`.

### Configurable env vars

| Var               | Default                          | Used by      |
|-------------------|----------------------------------|--------------|
| `BACKEND_HOST`    | `127.0.0.1`                      | backend      |
| `BACKEND_PORT`    | `8000`                           | backend, vite proxy |
| `BACKEND_RELOAD`  | `false`                          | backend      |
| `BACKEND_URL`     | `http://$BACKEND_HOST:$BACKEND_PORT` | vite proxy |
| `FRONTEND_HOST`   | `127.0.0.1`                      | vite         |
| `FRONTEND_PORT`   | `5173`                           | vite         |

## Per-task UI — five modules

The `/tasks/:taskId/:module` page replaces the old per-phase tab UI. The left nav is a flat, always-expanded list of five entries; the right pane renders the selected module. The URL `:module` segment is deep-linkable and survives reload, browser back/forward.

| Module               | Right pane | Editable | Save behavior |
|----------------------|------------|----------|---------------|
| **Input**            | Mantine Tabs over four sub-tabs: `CLAUDE.md`, `SKILL.md`, current phase's manager `.md`, this task's `initial_prompt.md`. `@uiw/react-md-editor` for each. | ✅ All four | Saving repo-level files (CLAUDE.md / SKILL.md / agent .md) prompts a **confirm dialog** because the change affects every task. PUT body must include `confirm: true`. |
| **Interview Questions** | Typed cards via `InterviewQuestionCard`: perspective badge, picked-option chips, notes Textarea. Backend parses `qa.md` to `InterviewQA` and round-trips on save. | ✅ | `PUT /api/tasks/{id}/interview` re-renders qa.md via the parser, with a `.bak` snapshot. No downstream re-run. |
| **Specs**            | `@uiw/react-md-editor` over `spec.md`, with a Preview / Split / Edit toggle. | ✅ | `PUT /api/tasks/{id}/artifacts/spec` |
| **Findings**         | Markdown render of `dossier.md`. Per-angle accordion deferred to v2 — per-angle files live alongside the dossier. | Read-only | — |
| **Execution Plan**   | Lazy-loaded Monaco editor with YAML highlighting + `monaco-yaml` schema validation against `src/schemas/plan.schema.json`. | ✅ | `PUT /api/tasks/{id}/artifacts/plan` |

**Edit semantics:** every save persists only — it never auto-triggers downstream regeneration. The user re-runs the next phase manually from `/agent_team` in Claude Code.

**Conflict semantics:** v1 is **last-write-wins**. Saved-over content survives in `{path}.bak` (one slot per file). If a CLI agent run rewrites the file while you're editing, your save will simply overwrite — your old content sits in `.bak` and the agent's content is lost. v2 will promote `.bak` to a versioned history.

## API surface

See `backend/libs/routes/` for the canonical list. Highlights:

| Method | Path | Purpose |
|---|---|---|
| GET  | `/api/health`                                     | health check |
| GET  | `/api/enums/root-folders`                         | `["projects", "ai_videos"]` |
| GET  | `/api/tasks`                                      | list `TaskSummary` |
| POST | `/api/tasks`                                      | create task `{name, root_folder, initial_prompt}` |
| GET  | `/api/tasks/{id}`                                 | full task with phase statuses |
| POST | `/api/tasks/{id}/{phase}/start`                   | trigger a phase agent run |
| POST | `/api/tasks/{id}/interview/answers`               | submit a round of answers (multi-turn) |
| POST | `/api/tasks/{id}/adjustments`                     | save user adjustments (optional) |
| GET  | `/api/tasks/{id}/artifacts/{kind}`                | raw artifact content (qa, spec, adjustments, dossier, plan, findings_report, initial_prompt) |
| **PUT** | `/api/tasks/{id}/artifacts/{kind}`              | save editable artifacts (`qa`, `spec`, `plan`, `initial_prompt`). Body: `{content, if_match?}`. Writes a `.bak` of the prior content. |
| GET  | `/api/tasks/{id}/inputs`                          | aggregator: returns the four Input sources for the per-task UI |
| **PUT** | `/api/inputs/{name}`                            | edit `claude_md` or `skill_md` (repo-level). Body MUST include `confirm: true` or returns 400. |
| **PUT** | `/api/agents/{agent_name}`                      | edit a `.claude/agents/agent_team__*.md` file. Body MUST include `confirm: true` or returns 400. |
| GET  | `/api/tasks/{id}/interview`                       | parsed typed `InterviewQA` (rounds + questions + options) |
| **PUT** | `/api/tasks/{id}/interview`                     | save typed `InterviewQA`; backend re-renders to `qa.md` via the parser |
| GET  | `/api/tasks/{id}/runs/{run_id}/events`            | SSE stream |
