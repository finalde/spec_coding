# Revised prompt — spec_driven

Stage 1 output. Produced by Claude from `raw_prompt.md` on 2026-05-02. Cleans grammar, structures into sections, surfaces implicit constraints. Does not invent requirements — anything not stated in the raw prompt is left as an open question for the interview stage.

---

## Goal

Build `spec_driven`, the **first project** of the spec_coding monorepo. It is a **readonly viewer** for the artifacts produced by the spec-driven workflow, plus the conventions and infrastructure that make the workflow itself executable end-to-end.

## Context

The spec_coding repo hosts a spec-driven workflow. Every non-trivial task moves through six stages, and each stage's artifacts live as plain files under `specs/{task_type}/{task_name}/`. `task_type` is an enum (`development`, `ai_video`, …); `task_name` is the project slug.

The six stages:

1. **Intake** — `user_input/{raw_prompt.md, revised_prompt.md}`. Claude revises the raw prompt directly, no agent.
2. **Interview** — `interview/qa.md`. `agent_team__interview_manager` analyzes the use case, identifies probe categories, dynamically builds an interviewer team (one specialized sub-interviewer per category), runs multi-choice question rounds with the user (via `AskUserQuestion`), and iterates until the team agrees the requirement is crystal clear. The manager does **not** ask questions itself.
3. **Research** — `findings/{angle-*.md, dossier.md}`. `agent_team__research_manager` identifies research angles focused on **business and use case** (not technology trivia), dynamically builds a research team, runs them in parallel, and consolidates a dossier. The manager does **not** do research itself.
4. **Spec compilation** — `final_specs/spec.md`. Claude takes revised prompt + Q&A + dossier and writes the spec directly, no agent.
5. **Validation strategy** — `validation/`. `agent_team__validation_manager` (strategy mode) builds a validation team and produces a multi-level plan: high-level acceptance criteria, BDD scenarios, system tests, unit tests, plus any non-functional checks the spec calls for. The team has an opinion on the best strategy and ensures the levels are right for the spec.
6. **Execution + streaming validation** — `projects/{name}/` (or `ai_videos/{name}/`). Claude implements work units; for each unit, `agent_team__validation_manager` (runtime mode) validates against the strategy. Issues stream back as feedback in real time and revisions loop until the unit passes (capped at 3 rounds per unit).

## What `spec_driven` is

`spec_driven` is the first concrete project that exercises this workflow. Its deliverable is a **readonly viewer** for the workflow's artifacts.

### Stack

- **Backend:** FastAPI.
- **Frontend:** React.
- **Layout:** single project at `projects/spec_driven/` with `backend/` and `frontend/` subfolders sharing one `README.md`.

### What the viewer shows

A web app with a **left navigation sidebar** containing two top-level sections:

1. **Claude Settings & Shared Context** — readonly views of `CLAUDE.md`, `.claude/agents/*.md`, `.claude/skills/**/SKILL.md`. This is the shared context surfaced for any spec_driven project.
2. **Projects** — a tree under `Projects/{task_type}/{task_name}/` showing the per-stage subfolders: `user_input/`, `interview/`, `findings/`, `final_specs/`, `validation/`. The very first project shown is `Projects/development/spec_driven/`.

The main pane renders the selected file (Markdown rendered as HTML; YAML/JSON shown as syntax-highlighted text).

### Scope: strictly readonly

- View files only. No write actions.
- No run controls (no "start a pipeline" button, no streaming run feed in v1).
- No editing, no deletes, no uploads.

## Cross-cutting constraints surfaced from the prompt

- **Q&A UX must be multi-choice.** The interview team must use `AskUserQuestion` (single-choice and multi-select), modeled on Claude Code's planning-mode UX. Free-text only as the implicit "Other" option.
- **Manager agents do not do the work themselves.** All three managers (interview, research, validation) build dynamic teams and coordinate them. Sub-agents are general-purpose, ephemeral, and captured in the audit log — not permanent agent files.
- **Three permanent agents only.** No prompt-revision agent, no spec-compilation agent, no executor agent — Claude does those directly.
- **Streaming validation during execution.** Validation runs per work unit, results stream back as the build progresses, revisions loop until pass.

## Out of scope (implicit from the prompt — confirm during interview)

- Authentication / multi-user access.
- Deployment beyond running locally.
- Editing or creating spec artifacts from the UI.
- A live event feed of pipeline runs.
- Watching for file changes (auto-refresh).
- Search across artifacts.

These are not stated as required, so we will treat them as out of scope and confirm during the interview stage.

## Open questions for the interview stage

These are gaps the raw prompt did not pin down; the interview manager should pick them up:

- What does "Claude Settings & Shared Context" include exactly — only the three file types listed, or more (e.g., `CLAUDE.md` of subprojects, `pyproject.toml`)?
- How should the viewer handle non-markdown files (YAML execution plans if any, JSON event logs)?
- How does the viewer discover projects — scan `specs/` and `projects/` on each request, or build an index?
- Should the viewer run on a fixed local port? Single-binary or two-process (FastAPI + Vite dev server)?
- How are markdown links between artifacts resolved (e.g., spec.md linking to dossier.md) — clickable cross-links inside the viewer?
- What's the visual hierarchy when a project has many task_types — flat or grouped?
- Performance: any expectation on artifact sizes (single 100KB markdown vs. directory with 1000 files)?
- What does success look like — the user can browse the spec_driven project's own artifacts end-to-end without leaving the UI?

## Desired outcome

A working FastAPI + React app at `projects/spec_driven/` that, when run locally, lets the user browse:
- `CLAUDE.md`, all agent definitions, all skill definitions.
- The full artifact tree for `Projects/development/spec_driven/` itself (since this project's own pipeline run produces the artifacts the viewer displays — the viewer is its own first dogfood).

…validated against acceptance criteria + BDD scenarios + system tests as defined in stage 5.
