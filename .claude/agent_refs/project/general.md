# Project-level refs — task-type-agnostic

This file is **required pre-reading** at the start of every coordinated stage (2 interview, 3 research, 5 validation) AND at every stage-6 work unit, regardless of `task_type`. It captures cross-cutting rules that apply to the *outputs* of spec-driven projects (everything under `projects/{name}/` or `ai_videos/{name}/`), not to the parent's behavior at any particular stage.

The parent (Claude in the `agent_team` skill) reads this BEFORE deciding team composition or producing artifacts at each stage. Per-task-type files in this same folder (`development.md`, `ai_video.md`, ...) layer on top of this file with task-type-specific rules.

The parent records the absolute paths it actually read (this file PLUS `<task_type>.md` when the file exists for the current task's type) in the same `pre_reading_consulted` array on the run's first `events.jsonl` event for the stage (or per-work-unit `validation.started` event in stage 6). A missing or empty array is a critical failure.

## Why this folder exists

`agent_refs/{interview,research,validation}/` hold institutional memory for the **parent's behavior at a stage** ("how does the validation parent decide severity"). This folder — `agent_refs/project/` — holds institutional memory for the **shape of the project outputs themselves** ("what color is the app chrome on every webapp we ship"). The two are separate because they have different audiences (the parent reading at a stage vs the parent + downstream code reading at every stage), different update cadences, and different scopes (per-stage vs cross-stage).

When a user-provided rule applies to the **outputs** of every spec-driven project of a given task type (e.g., "all webapps in `projects/` ship light-theme app chrome"), it lands here, not in `CLAUDE.md`'s "Project rules" section and not in any individual project's `specs/` tree. Project-specific facts still belong in `specs/{type}/{name}/`.

## How task-type selection works

- `general.md` (this file) is loaded on every run.
- `<task_type>.md` is loaded when the current task's `task_type` field matches the filename stem AND the file exists. For `task_type=development` → load `development.md`. For `task_type=ai_video` → load `ai_video.md` if present.
- A missing `<task_type>.md` is NOT a failure — it just means no task-type-specific cross-cutting rules have accumulated yet.

When a rule appears in BOTH this file and a `<task_type>.md`, the per-task-type file wins. This file is the floor; per-task-type files are the override.

## Common principles

(intentionally empty in v1)

No rule yet applies to BOTH `development` AND `ai_video` project outputs in a way that isn't already covered by a workflow contract in `CLAUDE.md`. Add new principles here only when a rule genuinely spans task types — most rules will start in a `<task_type>.md` and only graduate here once a sibling task type adopts the same constraint.

## Update protocol

- Updates are **surgical** (one new principle, one new bullet, one new clarification). Wholesale rewrites are anti-patterns — the goal is to grow institutional memory.
- Cite the run id or follow-up id where the lesson surfaced (e.g., "originated from follow-up 005 of `spec_driven`").
- If a rule is task-type-specific, write it in the relevant `<task_type>.md` instead — this file is for principles that span task types.
- The first `events.jsonl` event for any coordinated stage MUST list the absolute path of this file (and any loaded `<task_type>.md`) in `pre_reading_consulted`. A run where this folder's relevant files were not read is a critical failure regardless of whether the rules in them happened to match the output by accident.

## Relationship to other state surfaces

- `CLAUDE.md` — workflow contracts (state surfaces, the six stages, regen semantics, follow-up handling, harness conventions). These do NOT go here.
- `.claude/agent_refs/{interview,research,validation}/` — institutional memory for the parent's behavior at a coordinated stage. Parallel to this folder but stage-scoped, not project-scoped.
- `.claude/skills/agent_team/playbooks/{interview,research,validation}.md` — procedural runbooks for what the parent DOES at a stage. Different lifecycle from refs (refs accumulate; playbooks change rarely).
- `specs/{type}/{name}/` — per-project intent and pipeline artifacts. Project-specific facts go here, NOT in this folder. This folder is for rules that apply to the union of projects of a task type, not to a single project.
- `.audit/adhoc_agents/{date}/{task_id}/` — runtime spawn logs and event streams. Does not interact with this folder except by recording `pre_reading_consulted` paths.
