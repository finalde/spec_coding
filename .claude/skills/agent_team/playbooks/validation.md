# Validation playbook (stages 5 & 6)

Procedural runbook the parent reads to drive stage 5 (validation strategy) and the runtime-validation half of stage 6. Pre-reading contract, parent-direct model, audit-spawn paths, halt conditions, and pinned-items handling are in `CLAUDE.md` (§ Stage playbooks and reference docs, § Tool scoping, § Iteration bounds, § Pinned items survive regeneration).

Two modes — **strategy** (stage 5, run once) and **runtime** (stage 6, per work unit).

## Inputs (both modes)

`task_type`, `task_name`, `task_id`.

---

## Mode: `strategy` (stage 5)

Additional input: `spec_path` = `specs/{task_type}/{task_name}/final_specs/spec.md`.

### 1. Decide which validation levels apply

Always include:
- **Acceptance criteria** (Gherkin Given/When/Then).
- **BDD scenarios** (feature-level behaviors).

Add as relevant to the spec:
- **Unit tests** — discrete logic to verify.
- **System / integration tests** — components must work together.
- **Performance** — spec calls out latency / throughput.
- **Security** — spec touches auth, secrets, or external input.
- **Accessibility** — spec is UI-heavy.

Don't add levels that don't apply.

### 2. Spawn level-specialist workers in parallel

One general-purpose worker per chosen level, all in parallel via `Agent` (single message, multiple tool calls). Each writes its level file to `specs/{task_type}/{task_name}/validation/`:

- `acceptance_criteria.md` — Gherkin scenarios, one per primary flow.
- `bdd_scenarios.md` — feature-level behaviors with examples.
- `unit_tests.md` — described unit tests (name, inputs, expected, edge cases) — descriptions only, no code.
- `system_tests.md` — end-to-end scenarios with setup, action, assertions.
- `performance.md`, `security.md`, `accessibility.md` — only if applicable.

Capture spawn audit under `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/spawns/level-specialist-NN-{level}/`.

### 3. Consolidate into `strategy.md`

Read every level file; write `specs/{task_type}/{task_name}/validation/strategy.md`:

```markdown
# Validation strategy — {task_name}

Run: {task_id}

## Levels chosen
- {level} — {why}

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
- {which levels run on which work_unit_kind, how pass/fail is decided}

## Promotion-preservation check
- For each spec-pipeline stage with a non-empty `<stage>/promoted.md`, every pin MUST appear verbatim in the regenerated artifact for that stage. Severity: missing pin = `critical`. Stage 6 excluded in v1.
```

### Output

Return absolute path to `strategy.md` plus a one-paragraph summary.

---

## Mode: `runtime` (stage 6, per work unit)

Additional inputs:
- `work_unit_id` — caller-provided.
- `work_unit_output_paths` — files this unit produced.
- `work_unit_kind` — short tag (e.g., `backend_api`, `frontend_component`, `db_schema`, `ai_video_scene`, `boot_smoke`) — informs which levels to run.

### 1. Decide which levels apply to this unit

Not every level runs on every unit. `backend_api` → acceptance + system + unit. `frontend_component` → BDD + accessibility. Use `work_unit_kind` and `strategy.md` to decide.

### 2. Append `validation.started`

```json
{"ts": "<ISO 8601>", "type": "validation.started", "task_id": "...", "work_unit_id": "...", "levels": ["acceptance_criteria", "unit_tests"], "pre_reading_consulted": ["<absolute path>", ...]}
```

### 3. Spawn validators in parallel

One worker per applicable level, all in parallel via `Agent`. Each:
- Reads its level's artifact + the work unit's output files.
- Runs the appropriate check:
  - Test-style levels: write minimal test code if needed and run it (`Bash`).
  - Criteria-style levels: read code/output and reason about each criterion.
- Returns `pass`, OR a list of issues with `{id, level, severity, location, description, suggested_fix}`.

Capture spawn audit under `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/spawns/validator-NN-{level}/`.

### 4. Emit events

Per issue:
```json
{"ts": "...", "type": "validation.issue.raised", "task_id": "...", "work_unit_id": "...", "issue_id": "...", "level": "...", "severity": "...", "description": "..."}
```

If all levels pass:
```json
{"ts": "...", "type": "validation.pass", "task_id": "...", "work_unit_id": "..."}
```

If a level requires manual sign-off (visual contrast, focus visibility, motion, perceived latency), append `validation.requires_manual_walkthrough` so the skill prompts the user before declaring the unit done.

### 5. Apply severity policy

Use `agent_refs/validation/general.md` (standard table) plus any task-type-specific escalations (e.g., `development.md`).

If the same `issue_id` repeats across two iterations on the same unit, return `"halt"`:

```json
{"ts": "...", "type": "pipeline.halted", "task_id": "...", "work_unit_id": "...", "reason": "issue {id} unresolved across 2 iterations"}
```

### Output

- `status`: `"pass" | "issues" | "halt"`
- `issues`: list of issues (if any)
- `summary`: 2–3 sentence rollup
- `requires_manual_walkthrough`: bool (development tasks: true after all automated levels pass)

---

## Tools

- `Read`, `Write`, `Bash`, `Grep`, `Glob` — standard.
- `Agent` — workers in parallel (level-specialists in strategy mode, validators in runtime).

## Failure modes to refuse

- **Don't validate the implementation.** Validate the contract — what the next layer / the user actually consumes.
- **Don't disable a test by deleting its assertions.** Skipping with a clear reason (`pytest.mark.skipif(...)`) is fine; silent passing is not.
- **Don't fabricate validator outputs** when the parent did the check directly. Audit folder records who actually ran it.
- **Don't run a level without emitting `validation.started` / `validation.pass` / `validation.issue.raised`.** A level without audit events is treated as if it didn't run.
