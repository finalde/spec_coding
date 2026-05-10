# Revised prompt — spec_driven

Stage 1 output. Auto-regenerated from `raw_prompt.md` + every `user_input/follow_ups/*.md` in numerical order.

Last regenerated: 2026-05-09 12:01:57 — header bump for follow-up 013 (sidebar's top-level sections **Claude Settings & Shared Context** and **Specs** are now collapsible — disclosure caret + Enter/Space + ArrowLeft/ArrowRight all toggle them; default state on first render is expanded; collapse state is per-tab React state, not persisted to `localStorage`; FR-15 amended; backend `tree_walker.py` unchanged — frontend `nodeKey()` helper disambiguates the empty-path sections locally). Prior follow-up 012 (landing-page project picker + scoped sidebar: `/` now renders a project picker WITHOUT the sidebar; clicking a project sets `activeProject` in localStorage and navigates to `/project/{type}/{name}`; on any non-landing route the sidebar's Specs section is filtered to only the active `{type}/{name}` subtree while Claude Settings & Shared Context stays unchanged; deep-link / bookmark URLs that carry `{type, name}` re-derive activeProject from URL; new "← Back to projects" link in the sidebar header clears activeProject; FR-15 amended; new FR-42; no backend changes — filtering is purely client-side, wire shape from `/api/tree` unchanged). Prior follow-up 011 (two coupled fixes for 010: [1] prod-mode 405 bug + validation-gap closure — `serve_static=True` static-mount can shadow unregistered routes returning 405 to all non-GET methods; new regression test asserts `DELETE /api/project` reaches the FastAPI handler with static mount active; `agent_refs/validation/development.md` move #1 amended with a "every state-changing endpoint needs at least one `serve_static=True` integration test" sub-clause; [2] generic delete — `ALLOWED_TASK_TYPES_FOR_DELETE` extended to `{"ai_video", "development"}` with task-type→output-dir map `{"ai_video": "ai_videos", "development": "projects"}`; new `SelfDeleteRefused` exception protects `development/spec_driven` from UI-driven self-immolation; frontend `ProjectPage.tsx` removes the `ai_video`-only gate and disables the button on the running-webapp page). Follow-up 010 (parent-level project delete for `task_type=ai_video` only: new `DELETE /api/project` endpoint that recursively removes both `specs/ai_video/{name}/` and `ai_videos/{name}/`; new `backend/libs/project_deleter.py` module with strict slug validation and dual-path `rm -rf`-equivalent; new "Delete project" button on `ProjectPage.tsx` with two-step confirmation; `events.jsonl` audit event `project.deleted`). Prior follow-ups 009 (four coupled UX gaps: Specs subtree, project/stage routes, pin-loader regex, Renderer pin context), 008 (Specs subtree mirrors `specs/{type}/{name}/`; Home project list), 007 (Makefile `--host`/`--port` flag mismatch), 006 (Vite proxy `Origin` rewrite + class-of-failure into `agent_refs/validation/`), 005 (light-theme relocation), 004 (loopback-alias backend fix), 003 (run-backend / run-frontend split), 002 (friendly regen UI), 001 (editable webapp) preserved.

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
- **Layout:** single project at `projects/spec_driven/` with `backend/` and `frontend/` subfolders sharing one `README.md`.
- **Dev workflow (added by follow-up 003):** the `Makefile` exposes `run-backend` (FastAPI on `127.0.0.1:8765`) and `run-frontend` (Vite dev server on `127.0.0.1:5173`) as separate targets; `run` is preserved as a backend-only alias and `run-prod` still builds + serves single-process from `backend/static/`.

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
