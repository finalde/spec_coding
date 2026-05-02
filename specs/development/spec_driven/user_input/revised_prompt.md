# Revised prompt — spec_driven

Stage 1 output. Auto-regenerated from `raw_prompt.md` + every `user_input/follow_ups/*.md` in numerical order.

Last regenerated: 2026-05-03 (follow-up 002 auto-regen — friendly regen-prompt copy UI).

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

### What the viewer/editor surfaces

A web app with a **left navigation sidebar** containing two top-level sections:

1. **Claude Settings & Shared Context** — views of `CLAUDE.md`, `.claude/agents/*.md`, `.claude/skills/**/SKILL.md`. This is the shared context surfaced for any spec_driven project.
2. **Projects** — a tree under `Projects/{task_type}/{task_name}/` showing the per-stage subfolders: `user_input/`, `interview/`, `findings/`, `final_specs/`, `validation/`. The very first project shown is `Projects/development/spec_driven/`.

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
- **Localhost-only security model still holds.** Editing endpoints inherit the same sandbox (exposed tree, allowed extensions, symlink refusal, size cap) as the reader.

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
