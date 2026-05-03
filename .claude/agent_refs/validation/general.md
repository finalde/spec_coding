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

### 6.5. Question every "v1 out of scope" carve-out at stage 5

A spec-level "out of scope for v1" line is a decision *not* to test a behavior. Stage-5 strategy MUST surface every such carve-out back to the user as: *"this is outside the validation gate; confirm that's intended."* Carve-outs are usually legitimate (multi-user auth, IPv6, far-future features), but a meaningful fraction of them turn out to be contract-vs-user-feature gaps where the spec author scoped down something the user expects to work in their daily workflow.

**Concrete check at stage 5:** scan the spec's "Out of scope" section AND every inline "out of scope" / "v2 concern" / "deferred" mention. For each, check whether *another* part of the spec (FRs, NFRs, dev-workflow / Makefile-targets / ops sections) advertises a workflow that depends on the carved-out behavior. When the two conflict — a documented workflow relies on a behavior the spec explicitly carved out — that's a `critical` finding at stage 5, halting strategy sign-off until the user resolves the contract drift (either expand the spec to cover the workflow OR remove the workflow from the documented set; carve-outs that quietly break a documented workflow are not acceptable).

**Reason this exists:** in run `spec_driven` follow-up 004, the spec carved out the `make run-frontend` dev-server flow as "out of scope for v1" (cross-port `Origin: http://localhost:5173` 403s every mutation), while FR-39 simultaneously listed `make run-frontend` as a supported developer target. Stage 5 followed the spec literally and produced a validation strategy that asserted the same-port loopback case but not the dev-server case. The bug shipped, the user hit it on the documented workflow, and follow-up 006 had to re-open the contract. Catching the FR-9-vs-FR-39 conflict at stage 5 would have prevented the gap.

**Severity:** `critical` for stage-5 sign-off when an out-of-scope carve-out conflicts with another spec section. `warning` for a carve-out that's genuinely orthogonal (e.g., multi-user auth) but was not explicitly user-confirmed during the run.

### 7. Validate the post-mutation shape when a request crosses a header-mutating layer

When a request crosses a reverse proxy, a same-process router that rewrites headers, a CDN, or any other layer that can mutate `Origin` / `Host` / auth headers between the browser and the application gate, the unit-test set MUST include cases for BOTH:
- the **pre-mutation** shape (what the browser actually sends), AND
- the **post-mutation** shape (what the application gate actually sees after the proxy/router has done its work).

A test that only covers the post-mutation shape passes even when the pre-mutation request would 403 in reality (the proxy rewrite is broken). A test that only covers the pre-mutation shape passes when the proxy is bypassed (in production), missing the post-mutation invariants. Both are needed; mocking the proxy is fine, mocking it away is not.

**Reason this exists:** run `spec_driven` follow-up 006. The `Origin/Host` middleware unit tests covered only the post-rewrite shape (`Origin: http://localhost:8765` + `Host: localhost:8765` — same as what `make run-prod` produces). The Vite-proxy pre-rewrite shape (`Origin: http://localhost:5173` + `Host: localhost:5173`) was never tested, so the missing proxy `configure` hook went undetected.

**Severity:** missing pre-mutation case when a header-mutating proxy exists in the dev workflow → `blocker`. Missing post-mutation case → `blocker`.

### 9. Pinned items survive regeneration

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
