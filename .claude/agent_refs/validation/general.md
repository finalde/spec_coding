# Validation playbook — task-type-agnostic

This file is **required pre-reading** for stages 5 (validation strategy) and 6 (runtime validation) on every run, regardless of `task_type`. It captures cross-task-type lessons. The parent (Claude in the `agent_team` skill) reads this before defining validation levels or validating a work unit. See also `.claude/skills/agent_team/playbooks/validation.md` for the procedural runbook.

Per-task-type playbooks (`development.md`, `ai_video.md`, …) layer on top of this file with task-type-specific moves. When a rule appears in both a per-type file and this one, the per-type file wins.

## Core principles

### 1. Validate the contract, not the implementation

Tests that mirror the implementation pass when the implementation is wrong in a way the test was also wrong. Tests that mirror the **consumer's contract** catch contract drift. When defining a level, ask "what does the next stage / the next layer / the user actually consume from this artifact?" and write tests that walk it that way.

### 2. Severity flows from blast radius, not from how-recently-it-broke

A subtle XSS in a markdown renderer is `critical` even if it's never been exploited; a flaky test that breaks the cache cadence is `warning` even if it broke the build five times this week. The parent's job is to map issue → blast radius, not to weight by recency.

### 3. Skipping is a feature, not a failure

A test that skips with a clear reason on platforms it can't run is healthy. A test that silently passes because its assertions don't fire is a hidden bug. Prefer `pytest.mark.skipif(reason=...)` and the e2e-runner's equivalent; never disable a test by deleting its assertions.

### 4. Manual walkthrough is a level too

A sign-off pass that requires human eyes (visual contrast, focus visibility, motion, perceived latency) is a real level even when it can't be automated. Surface it as `validation.requires_manual_walkthrough` event so the parent can prompt the user.

### 5. The audit log is part of the validation artifact

Every level run MUST emit `validation.started`, `validation.pass` or `validation.issue.raised`, and (for issues) `exec.revision.applied` or `pipeline.halted` events to `.audit/adhoc_agents/{date}/{task_id}/events.jsonl`. A level that ran without audit events is treated as if it didn't run.

### 6. Pinned items survive regeneration

Every spec-pipeline stage (interview, findings, final_specs, validation) supports a `<stage>/promoted.md` sidecar containing user-pinned atomic items (Q/A pairs, FR-NN/AC-NN/SYS-NN blocks, recommendation bullets, etc.). Per `CLAUDE.md → ## Regeneration prompts & autonomous mode → ### Regeneration semantics → ### Pinned items survive regeneration`:

- The parent MUST add a "promotion preservation" check to every stage 5 strategy. The check verifies that **every pin in `<stage>/promoted.md` appears verbatim in the regenerated artifact**.
- Severity for a missing pin: `critical`. Halts the work unit; reverting silent loss of user-pinned content is the highest-priority class of regression.
- Severity for an out-of-place pin (in the artifact but at the wrong location, or under a `## Pinned items (orphaned)` section without justification): `blocker`. Standard 3-revision-round cap applies.
- The check is implemented by parsing both `<stage>/promoted.md` (via the `parse_promoted_text` helper in `libs/promotions.py`) and the regenerated artifact, then asserting that every pin's body appears as a substring of the artifact, modulo whitespace normalization.
- Stage 6 (project code under `projects/{name}/`) does NOT support promotion in v1; the parent should NOT generate a promotion-preservation check for stage 6 regenerations.

## Standard severity policy

| Class | Severity | Halt? |
|---|---|---|
| Security failure (any SEC-* check) | `critical` | Yes, immediately; no revision rounds without explicit user approval. |
| Path traversal / sandbox escape | `critical` | Yes. |
| Acceptance criterion failure | `blocker` | Standard 3-revision-round cap. |
| BDD scenario failure on golden path | `blocker` | Standard. |
| Hard performance budget missed | `blocker` | Standard. |
| ARIA / a11y mandatory check fail | `blocker` | Standard. |
| A11y "Recommended" gap | `warning` | Logged; never halts. |
| Observe-only metric outside expected range | `warning` | Logged; never halts. |

## When to add a new severity row

If a class of issue recurs across two or more runs, promote it to a permanent severity row in this file (or in the per-task-type playbook if it's task-type-specific). Cite the run ids that motivated the promotion.

## Update protocol

This file is updated at the end of any validation run that surfaces a cross-task-type lesson. Updates are surgical (one new bullet or one new severity row); avoid wholesale rewrites — the goal is to grow institutional memory, not to refactor it.
