---
name: agent_team
description: Spec-driven workflow orchestrator. Walks a task through six stages — intake (Claude revises the user's raw prompt), interview (Claude asks multi-choice questions), research (Claude spawns researcher workers in parallel and synthesizes findings), spec compilation (Claude writes the spec), validation strategy (Claude spawns level-specialist workers in parallel and consolidates a multi-level plan), and execution with streaming validation (Claude implements; per-unit validators run in parallel against the strategy). Persists every artifact under specs/{task_type}/{task_name}/ so any stage is resumable. Invoke when the user wants to start, resume, or run a spec-driven task.
---

# agent_team — spec-driven workflow

You drive a task through six stages, persisting every artifact so the user can resume at any stage. Coordinated stages (2, 3, 5, 6) use the parent-direct model — see `CLAUDE.md` § Tool scoping and team coordination for the rationale; this skill only covers the entry-point flow.

## Inputs (collect from the user if not given)

- `task_type` — required, enum: `development | ai_video`. Ask if unclear; never invent.
- `task_name` — slug, no spaces (e.g., `spec_driven`).
- `raw_prompt` — what the user wants to build.

Build `task_id = "{task_name}-{YYYYMMDD-HHmmss}"` once at run start (see `CLAUDE.md` § Task ID convention).

## Resuming

If `specs/{task_type}/{task_name}/` already exists, ASK which stage to start from. Default to the first stage with missing artifacts:

| Stage | Missing if … |
|---|---|
| 1 Intake | `user_input/revised_prompt.md` doesn't exist |
| 2 Interview | `interview/qa.md` doesn't exist |
| 3 Research | `findings/dossier.md` doesn't exist |
| 4 Spec | `final_specs/spec.md` doesn't exist |
| 5 Validation strategy | `validation/strategy.md` doesn't exist |
| 6 Execution | output project folder is empty or validation hasn't run end-to-end |

When resuming, read `changelog.md` first (if present) so you know which sections were already auto-patched from follow-ups.

## Follow-up prompts (between full runs)

Follow-up chat that arrives between runs is handled by `CLAUDE.md` § Follow-up prompt handling — those edits do NOT invoke this skill.

## Stage flow

For each coordinated stage, read its playbook AND its agent_refs files (per `CLAUDE.md` § Stage playbooks and reference docs — pre-reading contract). Record `pre_reading_consulted` on the stage's first `events.jsonl` event.

### Stage 1 — Intake

1. Save raw prompt to `specs/{task_type}/{task_name}/user_input/raw_prompt.md`.
2. Revise it: clean grammar, expand abbreviations, surface implicit constraints, structure into goal / context / desired outcome. **Don't invent requirements.** Save to `user_input/revised_prompt.md`.
3. Show to the user; iterate if they object.

### Stage 2 — Interview

Run `.claude/skills/agent_team/playbooks/interview.md`. Output: `interview/qa.md`. Confirm with the user before moving on.

### Stage 3 — Research

Run `.claude/skills/agent_team/playbooks/research.md`. Output: `findings/dossier.md` + per-angle files.

### Stage 4 — Spec compilation

Read `revised_prompt.md` + `qa.md` + `dossier.md`. Produce `final_specs/spec.md` with these sections:

- **Goal** (one paragraph)
- **Out of scope** (explicit list)
- **User roles & primary flows**
- **Functional requirements** (numbered, each testable)
- **Non-functional requirements** (performance, security, deployment as relevant)
- **Acceptance criteria summary** (full criteria belong in stage 5)
- **Open questions** (if any survived)

Show to the user; iterate until they approve.

### Stage 5 — Validation strategy

Run `.claude/skills/agent_team/playbooks/validation.md` (strategy mode). Output: `validation/strategy.md` + per-level files.

### Stage 6 — Execution + streaming validation

1. Decompose the spec into 3–8 work units (e.g., `backend_api`, `frontend_component`, `db_schema`).
2. Initialize `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/events.jsonl`.
3. For each unit (sequentially unless explicitly independent):
   - Append `exec.unit.started`.
   - Implement into `projects/{task_name}/` or `ai_videos/{task_name}/`.
   - Append `exec.unit.completed`.
   - Run `playbooks/validation.md` (runtime mode) against the unit.
   - On issues: revise, append `exec.revision.applied`, re-validate. Cap per `CLAUDE.md` § Iteration bounds.
4. After all units pass, run a whole-project validation pass for end-to-end checks. For development tasks, emit `validation.requires_manual_walkthrough` after all automated levels pass and surface to the user before declaring done.

## Audit and post-mortem

After the run (successful or halted), summarize for the user: stages run, workers spawned per stage, durations, surprises, recommendations.
