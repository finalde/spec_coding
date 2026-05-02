# Validation playbook (stages 5 & 6)

This file is the procedural runbook the parent (Claude in the `agent_team` skill) reads to drive stage 5 (validation strategy) and the runtime-validation half of stage 6 (execution + streaming validation). There is **no separate manager subagent**. The parent is the manager.

The playbook has two modes — **strategy** (run once at stage 5) and **runtime** (run per work unit during stage 6).

## Required pre-reading (BEFORE doing anything else, in either mode)

Before defining validation levels OR validating a work unit, the parent MUST read:

1. `.claude/agent_refs/validation/general.md` — task-type-agnostic principles, the standard severity policy, and the audit-event contract. **Always required.**
2. `.claude/agent_refs/validation/{task_type}.md` — task-type-specific lessons and required validation moves (e.g., `development.md` for `task_type=development`). **Required if the file exists for this task's type.**

These accumulate institutional memory across past runs (e.g., the `development.md` captures contract-drift lessons that mandate Playwright e2e + consumer-walk API tests). Treat them as required pre-work, not optional context.

The parent records the absolute paths it actually read in a `pre_reading_consulted` array inside the run's `events.jsonl` event for the stage start (or per-work-unit `validation.started` event).

If a rule from the per-task-type playbook would override a default in this file, the per-task-type file wins — those files exist precisely to encode lessons the original playbook didn't anticipate.

## Inputs (both modes)

- `task_type`, `task_name`, `task_id`

---

## Mode: `strategy` (stage 5)

Additional input:
- `spec_path` — `specs/{task_type}/{task_name}/final_specs/spec.md`

### 1. Decide which validation levels apply

Always include:
- **Acceptance criteria** (Gherkin-style Given/When/Then).
- **BDD scenarios** (feature-level behaviors).

Add as relevant to the spec:
- **Unit tests** — when the spec has discrete logic to verify.
- **System / integration tests** — when components must work together.
- **Performance checks** — when the spec calls out latency/throughput.
- **Security checks** — when the spec touches auth, secrets, or external input.
- **Accessibility checks** — when the spec is UI-heavy.

Don't add levels that don't apply.

### 2. Spawn level-specialist workers in parallel

The parent spawns ONE general-purpose worker subagent per chosen level, **all in parallel** in a single message with multiple `Agent` tool calls. Each level-specialist:
- Reads the spec.
- Produces the artifact for its level.
- Writes to `specs/{task_type}/{task_name}/validation/{level_filename}.md`:
  - `acceptance_criteria.md` — Gherkin scenarios, one per primary flow.
  - `bdd_scenarios.md` — feature-level behaviors with examples.
  - `unit_tests.md` — described unit test cases (test name, inputs, expected output, edge cases) — descriptions only, no code.
  - `system_tests.md` — end-to-end scenarios with setup, action, assertions.
  - `performance.md`, `security.md`, `accessibility.md` — only if applicable.

Capture each worker spawn under `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/spawns/level-specialist-NN-{level}/{prompt.md, output.md}`.

### 3. Consolidate the strategy

After all workers finish, the parent reads every level file and writes `specs/{task_type}/{task_name}/validation/strategy.md`:

```markdown
# Validation strategy — {task_name}

Run: {task_id}

## Levels chosen
- {level} — {why}
- ...

## Per-level summary
### Acceptance criteria
- {3 bullets summarizing the most important scenarios}
### BDD scenarios
- ...
### {Other levels}
- ...

## Cross-cutting concerns
- {flaky areas, integration boundaries, state to reset between tests}

## How runtime validation will use this
- {which levels run on which kinds of work units, how pass/fail is decided}

## Promotion-preservation check
- For each spec-pipeline stage with a non-empty `<stage>/promoted.md`, every pin MUST appear verbatim in the regenerated artifact for that stage. Severity: missing pin = `critical`. Implemented by parsing `promoted.md` and asserting each pin's body appears as a substring of the regenerated artifact, modulo whitespace normalization. Stage 6 (project code) is excluded from this check in v1.
```

### 4. Promotion preservation (this stage)

If `specs/{task_type}/{task_name}/validation/promoted.md` exists and is non-empty, every pinned strategy bullet / level-summary / acceptance criterion in it MUST appear verbatim in the regenerated `strategy.md` (or the relevant level file). Orphaned pins go in a `## Pinned items (orphaned)` section.

### Output (strategy mode)

Return the absolute path to `strategy.md` plus a one-paragraph summary of the strategy.

---

## Mode: `runtime` (stage 6, per work unit)

Additional inputs:
- `work_unit_id` — caller-provided identifier.
- `work_unit_output_paths` — list of files this unit produced.
- `work_unit_kind` — short tag (e.g., `backend_api`, `frontend_component`, `db_schema`, `ai_video_scene`, `boot_smoke`) — informs which levels to run.

### 1. Decide which validation levels apply to this unit

Not every level runs on every unit. A `backend_api` unit needs acceptance + system + unit tests. A `frontend_component` needs BDD + accessibility. Use `work_unit_kind` and the strategy file to decide.

### 2. Append `validation.started` event

Append a JSON line to `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/events.jsonl`:

```json
{"ts": "<ISO 8601>", "type": "validation.started", "task_id": "...", "work_unit_id": "...", "levels": ["acceptance_criteria", "unit_tests"], "pre_reading_consulted": ["<absolute path>", ...]}
```

### 3. Spawn validators in parallel

The parent spawns ONE worker subagent per applicable level, **all in parallel** in a single message with multiple `Agent` tool calls. Each validator:
- Reads its level's artifact (`acceptance_criteria.md`, `unit_tests.md`, etc.).
- Reads the work unit's output files.
- Runs the appropriate check:
  - For test-style levels: write minimal test code if needed and run it (Bash).
  - For criteria-style levels: read code/output and reason about whether each criterion is satisfied.
- Returns either `pass`, or a list of issues with `{id, level, severity, location, description, suggested_fix}`.

Capture each spawn under `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/spawns/validator-NN-{level}/`.

### 4. Emit events for each result

For each issue, append:
```json
{"ts": "...", "type": "validation.issue.raised", "task_id": "...", "work_unit_id": "...", "issue_id": "...", "level": "...", "severity": "...", "description": "..."}
```

If all levels passed:
```json
{"ts": "...", "type": "validation.pass", "task_id": "...", "work_unit_id": "..."}
```

If a level requires a manual sign-off pass (visual contrast, focus visibility, motion, perceived latency), append `validation.requires_manual_walkthrough` so the skill can prompt the user before declaring the unit done.

### 5. Apply severity policy and decide status

Use the standard severity table (see `.claude/agent_refs/validation/general.md`) plus any task-type-specific escalations (e.g., `development.md`).

If the same `issue_id` repeats across two iterations on the same work unit, return `"halt"` and append:
```json
{"ts": "...", "type": "pipeline.halted", "task_id": "...", "work_unit_id": "...", "reason": "issue {id} unresolved across 2 iterations"}
```

### Output (runtime mode)

- `status`: `"pass" | "issues" | "halt"`
- `issues`: list of issues (if any)
- `summary`: 2-3 sentence rollup
- `requires_manual_walkthrough`: bool (development tasks: true after all automated levels pass and before final sign-off)

---

## Tools used by the parent

- `Read`, `Write`, `Bash` (mkdir, jsonl appends, ISO timestamps, running tests).
- `Agent` — workers in parallel (level-specialists in strategy mode, validators in runtime mode).
- `Grep`, `Glob` — finding work-unit outputs.

## Failure modes to refuse

- **Don't validate the implementation.** Validate the contract — what the next layer / the user actually consumes. Tests that mirror the implementation pass when both sides are wrong the same way.
- **Don't disable a test by deleting its assertions.** Skipping with a clear reason (e.g., `pytest.mark.skipif(sys.platform == "win32", reason="...")`) is fine; silent passing is not.
- **Don't fabricate "validator" outputs** as if a worker ran when the parent did the check directly. The audit folder records who actually did the work.
- **Don't run a level without emitting `validation.started` / `validation.pass` / `validation.issue.raised`.** A level that ran without audit events is treated as if it didn't run.
