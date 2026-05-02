# studio_nav

## Goal

Replace the current per-task tab UI in `projects/spec_studio/frontend/src/pages/TaskDetail.tsx` with a left-nav of **five modules** — `Input`, `Interview Questions`, `Specs`, `Findings`, `Execution Plan` — and back the redesign with PUT endpoints so each module's content is **editable in place**. The new shell uses an opinionated component library (chosen during research) instead of bespoke Tailwind primitives, so the result looks polished without per-component design effort.

## Context

- Current per-task UI is `projects/spec_studio/frontend/src/pages/TaskDetail.tsx` with six tabs (`Interview / Spec / Research / Adjustments / Plan / Execute & Validate`). All six are dropped (interview Q1=f, "redo from scratch").
- The pipeline definitions in `.claude/skills/agent_team/SKILL.md` and `.claude/agents/agent_team__*.md` are unchanged by this task — only the UI and the parts of the backend that surface them.
- The repo's read/write conventions for projects under `projects/` are in `CLAUDE.md` § "Project rules" — strong typing, OOP for stateful concepts, thin entry point + logic in `libs/`, README kept in sync.
- The interview Q&A (`specs/interviews/studio_nav/qa.md`) is the primary input. The user's full directive is in `specs/interviews/studio_nav/initial_prompt.md`.

## Scope

### Frontend (`projects/spec_studio/frontend`)

- Replace `TaskDetail.tsx` with a two-pane layout: vertical module nav on the left, content pane on the right.
- The module nav is **always-expanded** and **flat** — five entries, no nested tasks (interview Q5=d, Q7=a).
- Five module components, each as its own file under `src/components/modules/`:
  - `InputModule.tsx` — sub-tabs/sections for `CLAUDE.md`, `SKILL.md`, current phase manager `.md`, and this task's `initial_prompt.md`. All four editable in place.
  - `InterviewModule.tsx` — renders `qa.md` in a "beautified" form (collapsible question cards with selected options highlighted) and supports inline editing of selections + notes.
  - `SpecsModule.tsx` — renders `spec.md` with a markdown viewer + edit toggle.
  - `FindingsModule.tsx` — renders `dossier.md` plus a per-angle accordion of `findings/{task_id}/*.md`.
  - `ExecutionPlanModule.tsx` — Monaco YAML viewer/editor for `plan.yaml`.
- Adopt an opinionated component library (Mantine v8 / Ant Design v5 / shadcn-with-blocks — final pick from research). It must provide AppShell-style layout, NavLink, Tabs, Card, Notification/Toast, and ideally a CodeEditor/Markdown viewer.
- Routing changes to `src/App.tsx` and `src/main.tsx`: `/tasks/:taskId/:module` deep-linkable URLs (interview Q8 default). Default route `/tasks/:taskId` redirects to `/tasks/:taskId/input`.
- `Dashboard` page (`/`) is **kept as-is** — task list table; clicking a task lands on `/tasks/:id/input`.
- Each module's right pane includes a **Save** action that PUTs the edited content; saving never triggers downstream regeneration (interview Q4=a).

### Backend (`projects/spec_studio/backend`)

- New aggregator endpoint: `GET /api/tasks/{task_id}/inputs` returns the four Input sources packed together — `{claude_md, skill_md, phase_manager_md, initial_prompt}` with `path`, `content`, and `editable` fields each.
- New PUT endpoints for editable artifacts: `PUT /api/tasks/{task_id}/artifacts/{kind}` for `kind ∈ {qa, spec, plan, initial_prompt}`. Body is `{content: string}`. Returns the saved `Artifact`.
- New PUT endpoints for repo-level inputs: `PUT /api/inputs/{name}` where `name ∈ {claude_md, skill_md}` and `PUT /api/agents/{agent_name}` for the manager `.md` files. Body is `{content: string}`. Each writes back to the corresponding repo file. **Each requires a `confirm: true` field in the body** because the change affects every task — not just the current one.
- Extend `ArtifactKind` in `backend/libs/models/schemas.py` to include `"initial_prompt"` (already exists on disk under `specs/interviews/{task_id}/initial_prompt.md` but isn't in the enum yet).
- Add `current_phase_manager_path()` helper to `FileStore` — given a task's `current_phase`, returns the path of the corresponding `.claude/agents/agent_team__*_manager.md` (or `agent_team__spec_compiler.md` / `agent_team__execution_plan_compiler.md` for non-manager phases).
- Single-version persistence: every PUT writes the new content, after first copying the previous content to a sibling `.bak` (`{path}.bak`). No multi-version history in v1.

### Repo conventions to honor

- New `libs/` modules under `backend/libs/` (no logic in route handlers beyond plumbing). Strong typing on every parameter and return.
- README updates: `projects/spec_studio/README.md` documents the new module nav, the new endpoints, and the chosen component library.
- All description fields in any new `.claude/` files stay under the 500-character ceiling (CLAUDE.md rule, also `feedback_yaml_description_500.md`).

## Out of Scope

- Multi-task left-nav tree (explicitly dropped in interview Q5=d).
- The existing Dashboard page — left untouched.
- The existing run-control buttons / live SSE event log inside the now-deleted Execute & Validate tab. **Their relocation is an Open Question; v1 default below.**
- Auto-trigger of downstream regeneration on edit (interview Q4=a).
- Multi-version artifact history beyond a single `.bak` snapshot.
- Authentication, multi-user editing, optimistic-locking, or conflict resolution between UI edits and CLI agent runs.
- New agent files or pipeline phases — this task changes the surface, not the pipeline.
- Edits to `.audit/` content from the UI.

## Constraints

- **Stack:** TypeScript + React 18 + Vite (existing); Python 3.11+ + FastAPI + Pydantic v2 (existing). Honor the conventions in `CLAUDE.md` § "Project rules".
- **Deployment:** Single-user local on `127.0.0.1`; ports configurable via env (existing — `BACKEND_PORT`, `FRONTEND_PORT`).
- **Component library:** must be **one** opinionated library — no mixing. Picked during research with a short rationale.
- **No new runtime dependencies** in the backend besides what FastAPI/Pydantic already provide. Frontend may add the chosen UI library + a Monaco wrapper if not already present.
- **Repo file edits via PUT must require an explicit `confirm: true`** in the request body. Returning 400 without confirm is the contract.
- **Style compliance** for every new Python file: type hints on all parameters/returns, OOP for stateful logic in `libs/`, classes for domain concepts (a `RepoInputResolver` class for the input aggregator, a `BackupWriter` class for `.bak` writes).

## Acceptance Criteria

1. `/tasks/:taskId` redirects to `/tasks/:taskId/input` and the `Input` module is selected in the left nav.
2. The left nav shows exactly five entries — `Input`, `Interview Questions`, `Specs`, `Findings`, `Execution Plan` — always expanded, with the active module visually highlighted.
3. Clicking any of the five entries updates both the right pane and the URL `:module` segment.
4. Browser back/forward/reload preserves the selected module via URL.
5. The **Input** module right pane shows four sub-sections — `CLAUDE.md`, `SKILL.md`, current phase's manager `.md`, this task's `initial_prompt.md` — each with editable content.
6. Saving an edit in any of the four Input sub-sections that is a repo-level file (`CLAUDE.md`, `SKILL.md`, manager `.md`) prompts a confirm dialog before PUTting; the PUT body must include `confirm: true`.
7. The **Interview Questions** module renders `qa.md` as a list of question cards (each card shows the question text, the option list with the picked option visually highlighted, and any user notes); editing a selection or note saves on confirm.
8. The **Specs** module renders `spec.md` (markdown) with a toggle between view and edit modes.
9. The **Findings** module shows the consolidated dossier on top and a collapsible per-angle list of findings files below.
10. The **Execution Plan** module shows `plan.yaml` in a Monaco editor with YAML syntax highlighting; a `Save` button PUTs the content.
11. `GET /api/tasks/{task_id}/inputs` returns the four Input sources keyed by name with `path`, `content`, `editable` fields.
12. `PUT /api/tasks/{task_id}/artifacts/{kind}` (kind ∈ qa/spec/plan/initial_prompt) writes the artifact, copies the prior content to `{path}.bak`, and returns the saved `Artifact`.
13. `PUT /api/inputs/{claude_md|skill_md}` and `PUT /api/agents/{name}` both require `confirm: true` in the request body — return 400 otherwise.
14. After save, no agent run is triggered — the response body confirms the write only.
15. `python -m compileall projects/spec_studio/backend` is clean.
16. `npm --prefix projects/spec_studio/frontend run build` is clean (TypeScript + Vite production build).
17. The Dashboard page (`/`) renders the current task list unchanged.
18. `projects/spec_studio/README.md` documents the new module set, the chosen component library, and the new endpoints.

## Open Questions

- **Where do agent run controls live in the new UI?** Three candidates: (i) inline at the top of each phase-related module's right pane (Interview, Specs, Plan); (ii) a top-bar action menu on the TaskDetail header; (iii) drop UI run controls in v1 — rely on `/agent_team` from Claude Code. **v1 default: option (i)** — each of `Interview`, `Specs`, `Findings`, `Execution Plan` has a "Run this phase" button + minimal run-status banner inline. The execution plan compiler should still emit work units to enable a one-click "Run Plan" — but no live event log. The user can override at adjustments phase.
- **Repo-file edit safety** — a confirm dialog gates `CLAUDE.md` / `SKILL.md` / manager edits. Is the confirm sufficient, or should we additionally require an env flag (e.g. `STUDIO_ALLOW_REPO_EDITS=true`) to enable those PUT routes at all? **v1 default: confirm-only**, no env gate.
- **"Beautified" interview style** — picked once the component library is locked. v1 default: question card with a left border colored by perspective (Goal / Scope / Tech / etc.), the picked option in a filled chip, unpicked options as outlined chips, notes in a soft-bg quote block.
- **Component library choice** — Mantine v8 vs Ant Design v5 vs shadcn-with-blocks. Final pick comes from research; rationale captured in the dossier.
- **Versioning beyond `.bak`** — a single `.bak` is the v1 default. If users want full history, v2 promotes `.bak` to a per-artifact directory of timestamped snapshots.
