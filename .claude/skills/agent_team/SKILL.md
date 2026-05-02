---
name: agent_team
description: Drive the spec-coding pipeline end-to-end for any task. Stage 1 (planning) — multi-turn interview, spec compile, research fan-out, optional adjustments, execution-plan YAML compile. Stage 2 (execution) — parallel execution + validation with event-stream feedback, iteration loop, final validation. Persists artifacts under specs/ and traces adhoc subagents under .audit/adhoc_agents/{date}/{task_id}/. Invoke with /agent_team followed by your task description.
---

# agent_team — spec-coding pipeline

You are now driving the **spec-coding pipeline**. You spawn the six manager agents directly. Managers in turn spawn adhoc subagents (researchers, executors, validators) — all adhoc spawns are captured under `.audit/adhoc_agents/{date}/{task_id}/spawns/{agent_id}/`.

This file is **hand-edited**. Subagents may paraphrase its instructions but must never rewrite it.

## Inputs

- `$ARGUMENTS` — the user's initial task prompt.
- `root_folder` — `projects` or `ai_videos`. **Ask the user** if not obvious from the prompt; do not guess.
- `CLAUDE.md` — repo conventions, always read.

## Bootstrap

1. Derive `task_id` — short snake_case slug from the prompt (e.g. `hello_cli`, `affiliate_dashboard`).
2. Create artifact roots if missing:
   - `specs/interviews/{task_id}/`
   - `specs/specs/{task_id}/`
   - `specs/findings/{task_id}/`
   - `specs/execution_plans/{task_id}/`
   - `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/spawns/`
3. Append a stub entry to `specs/index.json` under `tasks[]`: `{id, name, root_folder, status: "interviewing", created_at, current_phase: "interview"}`.
4. Initialize the event stream: `touch .audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/events.jsonl`.

## Stage 1 — Planning

### Phase 1: Interview
Spawn `agent_team__interview_manager`. It runs a multi-turn adaptive Q&A and writes `specs/interviews/{task_id}/qa.md`. Update `index.json` `current_phase = "spec"`.

### Phase 2: Spec compile
Spawn `agent_team__spec_compiler`. Reads `qa.md` + `CLAUDE.md` + any user-supplied ref docs. Writes `specs/specs/{task_id}/spec.md`. Update `current_phase = "research"`.

### Phase 3: Research fan-out
Spawn `agent_team__research_manager`. It identifies angles, spawns adhoc researchers in parallel, and consolidates `specs/findings/{task_id}/dossier.md` plus per-angle files. Update `current_phase = "adjustments"`.

### Phase 4: User adjustments (optional)
Ask the user if they want to add adjustments or rules. If yes, capture them at `specs/specs/{task_id}/adjustments.md`. Skipping is allowed. Update `current_phase = "plan"`.

### Phase 5: Execution-plan compile
Spawn `agent_team__execution_plan_compiler`. Inputs: `spec.md`, `dossier.md`, optional `adjustments.md`. Writes `specs/execution_plans/{task_id}/plan.yaml`. Update `current_phase = "execute"`.

## Stage 2 — Execution

### Phase 6: Execute & validate (parallel, event-stream coordinated)
Spawn `agent_team__execution_manager` and `agent_team__validation_manager` **in parallel**. They communicate exclusively through the append-only `events.jsonl`. Execution publishes `exec.unit.started`/`exec.unit.completed`; validation tails the file, runs checks per work-unit, and publishes `validation.issue.raised` events with severity. Execution tails for issues, applies revisions, and publishes `exec.revision.applied`. Loop continues until all work-units settle or a `pipeline.halted` is emitted.

**Iteration bound:** 3 per work-unit. Circuit-break + halt if (a) the same issue id repeats across two iterations, (b) more than five issues stay open after iteration 2, or (c) wall-clock exceeds 30 minutes on a single unit. On halt, escalate to the user — never silently retry.

### Phase 7: Final validation
After settle, validation_manager runs one more holistic pass (cross-cutting checks: integration, security, requirements compliance against the spec). Emits `validation.pass` if clean, `validation.issue.raised` (CRITICAL/MAJOR) otherwise. If issues remain, return to Phase 6 with one more bounded iteration.

Update `current_phase = "done"` and `status = "passed"` (or `"halted"`).

## Findings report — mandatory

After every run (success OR halt), write `.audit/adhoc_agents/{date}/{task_id}/findings_report.md` covering:
- Pipeline summary table: phase, agents spawned, duration, status.
- Adhoc subagents spawned per phase (count + types).
- Surprises / blockers / patterns.
- Recommendations for next run.

Do not skip this step.

## Anti-patterns

1. **No nested manager spawning.** Managers spawn adhoc workers (research/executor/validator), but they do NOT spawn other managers.
2. **No context dumps.** Pass file paths in spawn prompts; agents read files themselves.
3. **No conversation-history reads.** Every phase reads its inputs from disk only.
4. **No silent retries.** Bound every loop; emit `pipeline.halted` and escalate.
5. **No SKILL or agent file rewrites.** Subagents paraphrase; only humans (or this skill) edit `agent_team__*.md` and `SKILL.md`.

## Audit trail

Every adhoc subagent the managers spawn must drop three files under `.audit/adhoc_agents/{date}/{task_id}/spawns/{agent_id}/`:
- `prompt.md` — the exact prompt the manager passed.
- `tools.json` — the allowed-tools list (from the manager).
- `output.md` — the subagent's final output (or its target path if it wrote elsewhere).

This makes every dynamic spawn replayable and inspectable.
