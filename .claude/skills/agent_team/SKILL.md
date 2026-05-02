---
name: agent_team
description: Spec-driven workflow orchestrator. Walks a task through six stages — intake (Claude revises the user's raw prompt), interview (interview_manager builds a team and asks multi-choice questions), research (research_manager builds a team and gathers findings), spec compilation (Claude writes the spec), validation strategy (validation_manager builds a multi-level validation plan), and execution with streaming validation (Claude implements; validation_manager validates each work unit). Persists every artifact under specs/{task_type}/{task_name}/ so any stage is resumable. Invoke when the user wants to start, resume, or run a spec-driven task.
---

# agent_team — spec-driven workflow

You are driving a task through six stages. Persist every artifact so the user can resume at any stage.

## Inputs (collect from the user if not given)

- `task_type` — required, enum: `development | ai_video`. ASK if unclear; never invent.
- `task_name` — slug, no spaces (e.g., `spec_driven`).
- `raw_prompt` — what they want to build.

Build `task_id = "{task_name}-{YYYYMMDD-HHmmss}"` once at the start of the run. Use it for `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/` paths.

## Follow-up prompts (between full runs)

This skill is the entry point for full pipeline runs. **Follow-up chat prompts that arrive between runs are handled by the ambient triage rule in `CLAUDE.md` § "Follow-up prompt handling"** — they persist to `user_input/follow_ups/`, auto-regenerate `revised_prompt.md`, surgically auto-update conflicting downstream artifacts, and log to `specs/{type}/{name}/changelog.md`. Those follow-up edits do NOT invoke this skill.

When this skill IS invoked to resume or rerun a stage, read `changelog.md` first (if present) so you know which sections were already auto-patched from follow-ups; that context informs whether the user wants a true full regen or just to fill remaining gaps.

## Resuming

If `specs/{task_type}/{task_name}/` already exists, ASK which stage to start from. Default to the first stage with missing artifacts. Each stage's "missing" check:

| Stage | Missing if … |
|-------|--------------|
| 1 Intake | `user_input/revised_prompt.md` doesn't exist |
| 2 Interview | `interview/qa.md` doesn't exist |
| 3 Research | `findings/dossier.md` doesn't exist |
| 4 Spec | `final_specs/spec.md` doesn't exist |
| 5 Validation strategy | `validation/strategy.md` doesn't exist |
| 6 Execution | project output folder is empty or validation hasn't run end-to-end |

## Stage 1 — Intake (Claude does this directly, no agent)

1. Save the raw prompt verbatim to `specs/{task_type}/{task_name}/user_input/raw_prompt.md`.
2. Revise it: clean grammar, expand abbreviations, surface implicit constraints, structure into goal / context / desired outcome. **Do not invent requirements.** Save to `specs/{task_type}/{task_name}/user_input/revised_prompt.md`.
3. Show the revised prompt to the user. If they object, edit and re-save.

## Stage 2 — Interview

Invoke `agent_team__interview_manager` via the Agent tool. Pass:
- `task_type`, `task_name`, `task_id`
- `revised_prompt_path`

The manager runs its team and writes `specs/{task_type}/{task_name}/interview/qa.md`. Wait for completion. Skim the qa.md and confirm with the user before moving on.

## Stage 3 — Research

Invoke `agent_team__research_manager` via the Agent tool. Pass:
- `task_type`, `task_name`, `task_id`
- `revised_prompt_path`, `qa_path`

The manager writes `specs/{task_type}/{task_name}/findings/{angle-*.md, dossier.md}`. Wait for completion.

## Stage 4 — Spec compilation (Claude does this directly, no agent)

Read revised_prompt + qa.md + dossier.md. Produce `specs/{task_type}/{task_name}/final_specs/spec.md`. The spec must include:

- **Goal** — one paragraph
- **Out of scope** — explicit list
- **User roles & primary flows**
- **Functional requirements** — numbered, each testable
- **Non-functional requirements** — performance, security, deployment as relevant
- **Acceptance criteria summary** (full criteria belong in validation)
- **Open questions** that survived (if any)

Show the spec to the user. They can request changes; iterate until they approve.

## Stage 5 — Validation strategy

Invoke `agent_team__validation_manager` in **strategy mode**. Pass:
- `task_type`, `task_name`, `task_id`
- `mode: "strategy"`
- `spec_path`

The manager writes `specs/{task_type}/{task_name}/validation/strategy.md` plus per-level files (e.g., `acceptance_criteria.md`, `bdd_scenarios.md`, `unit_tests.md`, `system_tests.md`).

## Stage 6 — Execution + streaming validation

1. Decompose the spec into work units. A work unit is a coherent piece of buildable output — e.g., "backend API for X", "frontend component Y", "DB schema migration Z". Aim for 3–8 units.
2. Initialize `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/events.jsonl`.
3. For each work unit (sequentially unless explicitly independent):
   - Append `exec.unit.started` event.
   - Implement the unit (Claude writes code/files into `projects/{task_name}/` or `ai_videos/{task_name}/`).
   - Append `exec.unit.completed`.
   - Invoke `agent_team__validation_manager` in **runtime mode** with `work_unit_id` and the list of files this unit produced. The manager appends `validation.started`, then either `validation.pass` or one or more `validation.issue.raised` events.
   - If issues: revise the unit, append `exec.revision.applied`, re-validate. Cap at 3 revision rounds.
   - If still failing after 3 rounds: append `pipeline.halted`, stop, escalate to the user.
4. After all units pass, run `agent_team__validation_manager` in runtime mode against the whole project for end-to-end checks.

For `task_type=development`, code lands in `projects/{task_name}/`. For `task_type=ai_video`, artifacts land in `ai_videos/{task_name}/`.

## Halt conditions

Emit `pipeline.halted` and escalate if:
- Validation can't pass after 3 revisions on any work unit.
- Same issue repeats across two iterations.
- Wall-clock exceeds 30 minutes on a single unit.

## Audit and post-mortem

Each manager invocation writes runtime logs under `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/`. After the run completes (whether successful or halted), summarize for the user: which stages ran, how many sub-agents were spawned, durations, surprises, recommendations.
