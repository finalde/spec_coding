---
name: agent_team
description: Spec-driven workflow orchestrator. Walks a task through six stages — intake (Claude revises the user's raw prompt), interview (Claude asks multi-choice questions), research (Claude spawns researcher workers in parallel and synthesizes findings), spec compilation (Claude writes the spec), validation strategy (Claude spawns level-specialist workers in parallel and consolidates a multi-level plan), and execution with streaming validation (Claude implements; per-unit validators run in parallel against the strategy). Persists every artifact under specs/{task_type}/{task_name}/ so any stage is resumable. Invoke when the user wants to start, resume, or run a spec-driven task.
---

# agent_team — spec-driven workflow

You are driving a task through six stages. Persist every artifact so the user can resume at any stage. Each stage where coordination is needed (2, 3, 5, 6) follows a **parent-direct** model: you (Claude in this skill) read the relevant playbook + agent_refs, decide team composition, spawn workers in parallel via `Agent` (not via a manager subagent), and synthesize the outputs yourself. There is no separate manager subagent layer — that indirection has been removed for parallelism, lower latency, and lower communication cost.

## Inputs (collect from the user if not given)

- `task_type` — required, enum: `development | ai_video`. ASK if unclear; never invent.
- `task_name` — slug, no spaces (e.g., `spec_driven`).
- `raw_prompt` — what they want to build.

Build `task_id = "{task_name}-{YYYYMMDD-HHmmss}"` once at the start of the run. Use it for `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/` paths.

## The four playbooks

Stages 2, 3, 5, and 6 are governed by procedural playbooks that live alongside this skill:

- `.claude/skills/agent_team/playbooks/interview.md` — stage 2 procedure.
- `.claude/skills/agent_team/playbooks/research.md` — stage 3 procedure.
- `.claude/skills/agent_team/playbooks/validation.md` — stages 5 and 6 procedure (strategy + runtime modes).

For each of those stages you MUST read the corresponding playbook AND the matching files under `.claude/agent_refs/{interview|research|validation}/` (always `general.md`; also `<task_type>.md` if it exists for this run's `task_type`) BEFORE you act on that stage. Record the absolute paths you read in a `pre_reading_consulted` array on the stage's first event in `events.jsonl`.

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

## Stage 1 — Intake (parent-direct, no workers)

1. Save the raw prompt verbatim to `specs/{task_type}/{task_name}/user_input/raw_prompt.md`.
2. Revise it: clean grammar, expand abbreviations, surface implicit constraints, structure into goal / context / desired outcome. **Do not invent requirements.** Save to `specs/{task_type}/{task_name}/user_input/revised_prompt.md`.
3. Show the revised prompt to the user. If they object, edit and re-save.

## Stage 2 — Interview (parent-direct + optional category workers)

1. Read `.claude/skills/agent_team/playbooks/interview.md`.
2. Read `.claude/agent_refs/interview/general.md` and `.claude/agent_refs/interview/{task_type}.md` (the second only if it exists). Record `pre_reading_consulted`.
3. Run the procedure in the playbook: identify probe categories, generate the multi-choice question pool (shape A direct, or shape B with parallel category workers via `Agent`), call `AskUserQuestion` (max 4 questions per call, batched by category), iterate up to 3 rounds, write `specs/{task_type}/{task_name}/interview/qa.md`.
4. Show `qa.md` to the user and confirm before moving on.

## Stage 3 — Research (parent-direct + parallel angle workers)

1. Read `.claude/skills/agent_team/playbooks/research.md`.
2. Read `.claude/agent_refs/research/general.md` and `.claude/agent_refs/research/{task_type}.md` (the second only if it exists). Record `pre_reading_consulted`.
3. Run the procedure: identify 3–6 angles, spawn one researcher worker per angle in parallel via `Agent` (single message, multiple tool calls), wait for all to finish, synthesize `specs/{task_type}/{task_name}/findings/dossier.md`. Each researcher writes its own `angle-{slug}.md` and audit pair under `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/spawns/researcher-NN-{slug}/`.

## Stage 4 — Spec compilation (parent-direct, no workers)

Read revised_prompt + qa.md + dossier.md. Produce `specs/{task_type}/{task_name}/final_specs/spec.md`. The spec must include:

- **Goal** — one paragraph
- **Out of scope** — explicit list
- **User roles & primary flows**
- **Functional requirements** — numbered, each testable
- **Non-functional requirements** — performance, security, deployment as relevant
- **Acceptance criteria summary** (full criteria belong in validation)
- **Open questions** that survived (if any)

Show the spec to the user. They can request changes; iterate until they approve.

## Stage 5 — Validation strategy (parent-direct + parallel level workers)

1. Read `.claude/skills/agent_team/playbooks/validation.md` (strategy mode section).
2. Read `.claude/agent_refs/validation/general.md` and `.claude/agent_refs/validation/{task_type}.md` (the second only if it exists). Record `pre_reading_consulted`.
3. Run the procedure: decide which validation levels apply, spawn one level-specialist worker per level in parallel via `Agent` (single message, multiple tool calls), wait for all to finish, synthesize `specs/{task_type}/{task_name}/validation/strategy.md`. Each worker writes its own per-level file (`acceptance_criteria.md`, `bdd_scenarios.md`, `unit_tests.md`, `system_tests.md`, optionally `performance.md`/`security.md`/`accessibility.md`) and audit pair under `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/spawns/level-specialist-NN-{level}/`.

## Stage 6 — Execution + streaming validation (parent-direct + parallel validators per unit)

1. Decompose the spec into work units. A work unit is a coherent piece of buildable output — e.g., "backend API for X", "frontend component Y", "DB schema migration Z". Aim for 3–8 units.
2. Initialize `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/events.jsonl`.
3. For each work unit (sequentially unless explicitly independent):
   - Append `exec.unit.started` event.
   - Implement the unit (write code/files into `projects/{task_name}/` or `ai_videos/{task_name}/`).
   - Append `exec.unit.completed`.
   - Run runtime validation per `.claude/skills/agent_team/playbooks/validation.md` (runtime mode section): decide which levels apply to this `work_unit_kind`, append `validation.started` (with `pre_reading_consulted`), spawn one validator worker per applicable level in parallel via `Agent`, collect results, emit `validation.pass` or `validation.issue.raised` per result, apply severity policy.
   - If issues: revise the unit, append `exec.revision.applied`, re-validate. Cap at 3 revision rounds.
   - If still failing after 3 rounds: append `pipeline.halted`, stop, escalate to the user.
4. After all units pass, run a whole-project validation pass (still per the validation playbook's runtime mode) for end-to-end checks. For development tasks, emit `validation.requires_manual_walkthrough` after all automated levels pass and surface it to the user before declaring done.

For `task_type=development`, code lands in `projects/{task_name}/`. For `task_type=ai_video`, artifacts land in `ai_videos/{task_name}/`.

## Halt conditions

Emit `pipeline.halted` and escalate if:
- Validation can't pass after 3 revisions on any work unit.
- Same issue repeats across two iterations.
- Wall-clock exceeds 30 minutes on a single unit.

## Audit and post-mortem

Each worker spawn writes runtime logs under `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/spawns/{worker_id}/{prompt.md, output.md}`. After the run completes (whether successful or halted), summarize for the user: which stages ran, how many workers were spawned per stage, durations, surprises, recommendations.
