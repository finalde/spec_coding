# Revised prompt — spec_driven

Stage 1 output. Auto-regenerated from `raw_prompt.md` + every `user_input/follow_ups/*.md` in numerical order.

Last regenerated: 2026-06-14 — Prompt Lab items become per-item **workspace folders** with an autonomous **Execute** button (follow-up 020: each item is now `prompt_lab/{cat}/{task}/prompt.md` + a `workspace/`; a ▶ Execute button spawns a headless `claude --print --permission-mode bypassPermissions` background session in that workspace, fed the item's prompt under a `# EXECUTION MODE: AUTONOMOUS` header + an autonomy contract — never wait for input, pick sensible defaults, log every decision as a JSON line to `decisions.jsonl`; the UI portal polls and shows run status + the autonomous decisions + live output + generated files, with a ⏹ Stop; endpoints `POST /api/prompt-lab/execute`, `GET /api/prompt-lab/run`, `POST /api/prompt-lab/stop`). Prior follow-up 019 — Prompt Lab opens/edits tasks **inline** within its own nav+main (follow-up 019: fixes the bug where clicking the prompt block / "Open / edit" navigated to the global `/file/{path}` route and swapped in the spec project's sidebar — now the selected task is fetched and rendered with `Renderer` in the Prompt Lab `.main-pane`, ✎ Edit swaps to the inline `Editor` (same `PUT /api/file` + `If-Unmodified-Since` 409 handling), and create opens the new file inline; no navigation away). Prior follow-up 018 — Prompt Lab gains a one-click **Copy** button on the highlighted prompt block + a fixed **3-section** task structure (follow-up 018: the copy-paste prompt block renders a Copy button that copies the prompt and `stopPropagation`s past the click-to-edit; every `prompt_lab/` task `.md` follows the order ✨ Expectation → ▶️ How to run → 🔗 Source & references before the prompt block, and the new-prompt template seeds that structure; overview parser unchanged). Prior follow-up 017 — Prompt Lab page adopts the standard **left-nav + main-section** layout (follow-up 017: the `/prompt-lab` overview renders as the app's two-column `app-root` — a `.sidebar` listing categories → task items with a "+ New" button and "← Home" link, and a `.main-pane` showing the selected task's detail (title, `Stack/Est/Output`, Source + Expected links, the highlighted click-to-edit prompt, and Copy / Open / Delete actions) — instead of the prior full-width tile grid; selection is page-local state, editing still routes to `/file/{path}`). Prior follow-up 016 — adds the **Prompt Lab** webapp section (follow-up 016: surface the repo-root `prompt_lab/` library — category subfolders of copy-paste, autonomous "Ralph-loop" task `.md` files — as a first-class section at `/prompt-lab` reachable from the landing page; overview lists every `prompt_lab/**/*.md` grouped by category as cards showing title + `Stack/Est/Output` + a `Source` link + an `Expected result` link/image + a prompt preview; simple CRUD via new `GET /api/prompt-lab` (overview), `POST /api/prompt-lab/file` (create, ensures category dir, refuses overwrite), `DELETE /api/prompt-lab/file` (delete one md, `prompt_lab/`-scoped), plus the generic `GET/PUT /api/file` extended to a new `prompt_lab/` sandbox root for read+update+create-in-existing-category; in read mode the copy-paste prompt code block renders **highlighted** and **click-to-edit**; each task `.md` and the UI carry a parseable `Source:` and `Expected result:` link/image; the generic `DELETE /api/file` stays 405 — deletion is `prompt_lab/`-scoped only). Prior follow-up 015 header bump (project adopts the **evolved** form of the `apps/+libs/` standard the workflow refs accumulated through ai_video_management follow-ups 056 / 060 / 061 / 065 / 068: per-role sub-bucketing within each layer — `infrastructure/{readers,writers,clients,daos,middleware,errors}/`, `domain/{entities,value_objects,errors,repositories}/`, `application/{queries,commands,dtos,mappers}/`; one file per aggregate per role with `{aggregate}__{role}.py`; ONE class per file in `commands/`+`queries/` with method-per-operation — e.g., `PromotionCommand.add(...)` + `.remove(...)`, not `AddPromotionCommand.execute()`; routes split per aggregate at `apps/api/routes/{aggregate}__route.py`, each with its own `APIRouter()`; SRP — infra exceptions extracted to `infrastructure/errors/{aggregate}__error.py`, DAO dataclasses to `daos/{aggregate}__dao.py`, Pydantic request bodies stay with the route handler; `< 100` lines file-size guideline; `~1000` lines `warning`. HTTP routes + JSON shapes byte-identical to v1 — only internal organization changes). Prior follow-up 014 (project adopts the `apps/+libs/` solution layout with DDD inside `libs/domain/`, CQRS inside `libs/infrastructure/` + `libs/application/`, `__suffix` filename/classname convention, and `dependency_injector` wiring — per `.claude/agent_refs/project/development.md` §1–6; HTTP routes + JSON shapes unchanged). Prior follow-up 013 (sidebar's top-level sections **Claude Settings & Shared Context** and **Specs** are now collapsible — disclosure caret + Enter/Space + ArrowLeft/ArrowRight all toggle them; default state on first render is expanded; collapse state is per-tab React state, not persisted to `localStorage`; FR-15 amended; backend `tree_walker.py` unchanged — frontend `nodeKey()` helper disambiguates the empty-path sections locally). Prior follow-up 012 (landing-page project picker + scoped sidebar: `/` now renders a project picker WITHOUT the sidebar; clicking a project sets `activeProject` in localStorage and navigates to `/project/{type}/{name}`; on any non-landing route the sidebar's Specs section is filtered to only the active `{type}/{name}` subtree while Claude Settings & Shared Context stays unchanged; deep-link / bookmark URLs that carry `{type, name}` re-derive activeProject from URL; new "← Back to projects" link in the sidebar header clears activeProject; FR-15 amended; new FR-42; no backend changes — filtering is purely client-side, wire shape from `/api/tree` unchanged). Prior follow-up 011 (two coupled fixes for 010: [1] prod-mode 405 bug + validation-gap closure — `serve_static=True` static-mount can shadow unregistered routes returning 405 to all non-GET methods; new regression test asserts `DELETE /api/project` reaches the FastAPI handler with static mount active; `agent_refs/validation/development.md` move #1 amended with a "every state-changing endpoint needs at least one `serve_static=True` integration test" sub-clause; [2] generic delete — `ALLOWED_TASK_TYPES_FOR_DELETE` extended to `{"ai_video", "development"}` with task-type→output-dir map `{"ai_video": "ai_videos", "development": "projects"}`; new `SelfDeleteRefused` exception protects `development/spec_driven` from UI-driven self-immolation; frontend `ProjectPage.tsx` removes the `ai_video`-only gate and disables the button on the running-webapp page). Follow-up 010 (parent-level project delete for `task_type=ai_video` only: new `DELETE /api/project` endpoint that recursively removes both `specs/ai_video/{name}/` and `ai_videos/{name}/`; new `backend/libs/project_deleter.py` module with strict slug validation and dual-path `rm -rf`-equivalent; new "Delete project" button on `ProjectPage.tsx` with two-step confirmation; `events.jsonl` audit event `project.deleted`). Prior follow-ups 009 (four coupled UX gaps: Specs subtree, project/stage routes, pin-loader regex, Renderer pin context), 008 (Specs subtree mirrors `specs/{type}/{name}/`; Home project list), 007 (Makefile `--host`/`--port` flag mismatch), 006 (Vite proxy `Origin` rewrite + class-of-failure into `agent_refs/validation/`), 005 (light-theme relocation), 004 (loopback-alias backend fix), 003 (run-backend / run-frontend split), 002 (friendly regen UI), 001 (editable webapp) preserved.

---

## Goal

Build `spec_driven`, the **first project** of the spec_coding monorepo. It is an **interactive viewer/editor** for the artifacts produced by the spec-driven workflow, plus the conventions and infrastructure that make the workflow itself executable end-to-end. Earlier scope (per the original raw prompt) called the viewer "readonly"; that constraint was lifted by follow-up 001.

## Context

The spec_coding repo hosts a spec-driven workflow. Every non-trivial task moves through six stages, and each stage's artifacts live as plain files under `specs/{task_type}/{task_name}/`. `task_type` is an enum (`development`, `ai_video`, …); `task_name` is the project slug.

The six stages:

1. **Intake** — `user_input/{raw_prompt.md, revised_prompt.md, follow_ups/*.md}`. Claude revises the raw prompt directly, no agent. Follow-ups append; `revised_prompt.md` is auto-regenerated whenever a follow-up lands.
2. **Interview** — `interview/qa.md`. `agent_team__interview_manager` analyzes the use case, identifies probe categories, dynamically builds an interviewer team (one specialized sub-interviewer per category), runs multi-choice question rounds with the user (via `AskUserQuestion`), and iterates until the team agrees the requirement is crystal clear. The manager does **not** ask questions itself.
3. **Research** — `findings/{angle-*.md, dossier.md}`. `agent_team__research_manager` identifies research angles focused on **business and use case** (not technology trivia), dynamically builds a research team, runs them in parallel, and consolidates a dossier. The manager does **not** do research itself.
4. **Spec compilation** — `final_specs/spec.md`. Claude takes revised prompt + Q&A + dossier and writes the spec directly, no agent.
5. **Validation strategy** — `validation/`. `agent_team__validation_manager` (strategy mode) builds a validation team and produces a multi-level plan: high-level acceptance criteria, BDD scenarios, system tests, unit tests, plus any non-functional checks the spec calls for.
6. **Execution + streaming validation** — `projects/{name}/` (or `ai_videos/{name}/`). Claude implements work units; for each unit, `agent_team__validation_manager` (runtime mode) validates against the strategy. Issues stream back as feedback in real time and revisions loop until the unit passes (capped at 3 rounds per unit).

## What `spec_driven` is

`spec_driven` is the first concrete project that exercises this workflow. Its deliverable is an **interactive viewer/editor** for the workflow's artifacts plus tooling that lets the user trigger regenerations.

### Stack

- **Backend:** FastAPI.
- **Frontend:** React.
- **Layout (amended by follow-up 014; sub-bucketing + one-file-per-aggregate added by follow-up 015):** single solution at `projects/spec_driven/` with `apps/api/` (FastAPI), `apps/ui/` (React), and a shared `libs/{infrastructure,domain,application,common}/`. Each non-`common/` layer is broken out by role: `infrastructure/{readers,writers,clients,daos,middleware,errors}/`, `domain/{entities,value_objects,errors,repositories}/`, `application/{queries,commands,dtos,mappers}/`. Within each role sub-folder, one file per aggregate: `{aggregate}__{role}.py` (e.g., `libs/application/commands/promotion__command.py` containing a single `PromotionCommand` class with methods `add(...)` + `remove(...)`). `apps/api/routes/` is itself a package split per aggregate: `apps/api/routes/{file,tree,stages,regen_prompt,promotion,project}__route.py`, each with its own `APIRouter()`; `apps/api/routes/__init__.py` exposes a combined `router` that `app_factory.py` mounts. One solution-root `README.md`, `Makefile`, `pyproject.toml`. The previous `backend/` + `frontend/` split is renamed to `apps/api/` + `apps/ui/`.
- **Dev workflow (added by follow-up 003, target names preserved by follow-up 014):** the `Makefile` exposes `run-backend` (FastAPI on `127.0.0.1:8765`, now `apps/api/main.py`) and `run-frontend` (Vite dev server on `127.0.0.1:5173`, now `apps/ui/`) as separate targets; `run` is the backend-only alias; `run-prod` builds the UI bundle and serves it single-process from `apps/api/static/`.

### What the viewer/editor surfaces

A web app with a **landing project picker** at `/` and a **left navigation sidebar** that mounts on every other route. Two layout modes:

- **Landing mode (`/`).** Full-width project picker — no sidebar. Lists every `{task_type}/{task_name}` discovered under `specs/`. Clicking a project sets the **active project** (persisted in `localStorage` under `spec_driven.active_project.v1`) and navigates to `/project/{type}/{name}`. (Added by follow-up 012.)
- **Workspace mode (any non-landing route).** Two-column layout: left navigation sidebar + main pane. Sidebar contains two top-level sections:
  1. **Claude Settings & Shared Context** — views of `CLAUDE.md`, `.claude/agent_refs/**/*.md`, `.claude/skills/**/SKILL.md`. Shared across all projects, never filtered.
  2. **Specs** — when an active project is set, this section is filtered to only the active `{type}/{name}` subtree showing the per-stage subfolders (`user_input/`, `interview/`, `findings/`, `final_specs/`, `validation/`). When no active project is set, the section is empty. (Filtering added by follow-up 012; was previously unfiltered.) A "← Back to projects" link sits above the tree and returns the user to the landing picker, clearing the active project.

The main pane renders the selected file (Markdown rendered as HTML; YAML/JSON shown as syntax-highlighted text). Every file is editable in place via an explicit ✎ Edit toggle.

### Editing scope (added by follow-up 001)

- Every file in the existing exposed tree is editable through the same path-sandbox the reader uses.
- File-level editing UX: ✎ Edit → textarea editor with Save (Ctrl+S) / Discard / Close-editor controls and a clear "unsaved changes" indicator.
- `interview/qa.md` gets a **structured Q/A view**: rounds, categories, questions and answers render as discrete color-differentiated blocks; each Q and each A is editable in place; whole-file editing remains available via the file-level toggle.

### Regeneration tooling (added by follow-up 001)

- **Per-stage Regenerate panel** on every stage file: collapsible widget with module checkboxes (default all checked), an autonomous-mode toggle, and a "Build prompt" button. After build the assembled prompt is rendered inline inside a bordered block with a header bar carrying the title, a soft-wrap toggle, and a prominent **Copy** button (per follow-up 002 — no inner `<details>` to expand). The prompt is assembled server-side from the current `revised_prompt.md` + every `follow_ups/*.md`.
- **Project parent page** at `/project/{type}/{name}` showing the stage map and a single master regen panel that builds one combined prompt across the chosen stages and modules.
- The autonomous-mode toggle is persisted in `localStorage`. Default: off.

### Autonomous-mode contract (added by follow-up 001)

Generated regen prompts open with one of two headers:

- `# EXECUTION MODE: AUTONOMOUS` — Claude must NOT call `AskUserQuestion`, must use best judgment for any ambiguity (recording the choice inline in the artifact), and must produce every requested artifact in a single uninterrupted run before stopping.
- `# EXECUTION MODE: INTERACTIVE` — default behavior, may use `AskUserQuestion`.

This contract is documented under a `## Regeneration prompts & autonomous mode` section of `CLAUDE.md`.

### Prompt Lab section (added by follow-up 016)

A second top-level surface, parallel to Specs, exposes the repo-root `prompt_lab/` library — category subfolders (`prompt_lab/{category}/{task}.md`) of copy-paste, autonomous "Ralph-loop" AI build prompts.

- **Entry + route.** A Prompt Lab entry on the landing page (`/`) navigates to `/prompt-lab`. The section does NOT require an active spec project; `prompt_lab/` is its own sandbox root.
- **Overview.** `/prompt-lab` lists every `prompt_lab/**/*.md`, grouped by category, as cards. Each card shows parsed metadata: title, the `Stack / Est / Output` line, a **Source** link (original inspiration), an **Expected result** link/image (representative reference output), and a preview of the copy-paste prompt. Cards open the file in the existing reader.
- **CRUD.** Create (new md under a chosen existing/new category), Read (reader), Update (existing editor), Delete (per-md, confirmed). Backed by `GET /api/prompt-lab`, `POST /api/prompt-lab/file`, `DELETE /api/prompt-lab/file`, plus generic `GET/PUT /api/file` extended to the `prompt_lab/` sandbox root. Generic `DELETE /api/file` stays 405; deletion is `prompt_lab/`-scoped only.
- **Prompt highlight + click-to-edit.** When viewing a `prompt_lab/` md, the copy-paste prompt code block renders highlighted (primary artifact) and is clickable — clicking switches the file into edit mode.
- **Source + expected-result everywhere.** Every task `.md` carries a parseable `**Source:**` link and an `**Expected result:**` link/image; both are surfaced in the UI cards and in the rendered file.

## Cross-cutting constraints surfaced from the prompt

- **Q&A UX must be multi-choice.** The interview team must use `AskUserQuestion` (single-choice and multi-select), modeled on Claude Code's planning-mode UX. Free-text only as the implicit "Other" option.
- **Manager agents do not do the work themselves.** All three managers (interview, research, validation) build dynamic teams and coordinate them. Sub-agents are general-purpose, ephemeral, and captured in the audit log — not permanent agent files.
- **Three permanent agents only.** No prompt-revision agent, no spec-compilation agent, no executor agent — Claude does those directly.
- **Streaming validation during execution.** Validation runs per work unit, results stream back as the build progresses, revisions loop until pass.
- **Localhost-only security model still holds.** Editing endpoints inherit the same sandbox (exposed tree, allowed extensions, symlink refusal, size cap) as the reader. The Origin/Host CSRF gate admits the `localhost` ↔ `127.0.0.1` loopback alias at the bound port (per follow-up 004); foreign domains and other hosts continue to return 403. Under `make run-frontend` (Vite at 5173), the dev-server proxy rewrites `Origin` to `http://127.0.0.1:8765` and `Host` to `127.0.0.1:8765` so the backend gate sees a same-shape request in both runtime modes (per follow-up 006); the backend allow-list is NOT widened to the dev-server port.
- **Light-theme app chrome.** Per the cross-cutting project-output rule in `.claude/agent_refs/project/development.md` (relocated from `CLAUDE.md → Project rules` by follow-up 005), the spec_driven webapp's body / sidebar / toolbar / panels / buttons stay light regardless of the OS `prefers-color-scheme`. Intentional dark surfaces on syntax-highlighted `<pre>` blocks and the assembled-prompt panel are preserved.

## Out of scope (still / clarified)

- Authentication / multi-user access.
- Deployment beyond running locally.
- A live event feed of pipeline runs.
- Watching for file changes (auto-refresh).
- Search across artifacts.
- "Run Claude inline" from the webapp — regen prompts are still copy-paste into the Claude Code CLI; the webapp does not invoke the model.
- Diff / version history beyond what git already provides.

## Open questions

(Original open questions were resolved during the first interview round and are recorded in `interview/qa.md`. New open questions surfaced by follow-up 001 are deferred to whenever the user explicitly chooses to re-invoke the interview manager.)

## Desired outcome

A working FastAPI + React app at `projects/spec_driven/` that, when run locally, lets the user:

- Browse `CLAUDE.md`, all agent definitions, all skill definitions, and the full artifact tree for `Projects/development/spec_driven/`.
- Edit any of those files in place — either as the whole file or, for `interview/qa.md`, as individual Q/A blocks.
- Generate copy-paste regeneration prompts at per-stage or whole-project granularity, with module selection and an autonomous-mode toggle.

…validated against acceptance criteria + BDD scenarios + system tests as defined in stage 5.
