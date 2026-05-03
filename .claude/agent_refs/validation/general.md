# Validation refs — task-type-agnostic

Institutional memory for stage 5 (strategy) and stage 6 (runtime validation). The pre-reading contract, parent-direct model, audit paths, and pinned-items handling are in `CLAUDE.md` (§ Stage playbooks and reference docs, § Pinned items survive regeneration). Per-task-type files in this same folder override these defaults when they conflict.

## Principles

### 1. Validate the contract, not the implementation

Tests that mirror the implementation pass when the implementation is wrong in a way the test was also wrong. Tests that mirror the **consumer's contract** catch contract drift. Ask: "what does the next stage / the next layer / the user actually consume from this artifact?" — and walk the test that way.

### 2. Severity flows from blast radius, not recency

A subtle XSS in a markdown renderer is `critical` even if never exploited; a flaky test that breaks the cache cadence is `warning` even if it broke five builds this week. Map issue → blast radius, not by recency.

### 3. Skipping is a feature, not a failure

A test that skips with a clear reason on platforms it can't run is healthy. A test that silently passes because its assertions don't fire is a hidden bug. Prefer `pytest.mark.skipif(reason=...)` and the e2e equivalent; never disable a test by deleting assertions.

### 4. Manual walkthrough is a level too

Visual contrast, focus visibility, motion, perceived latency — surface as `validation.requires_manual_walkthrough` so the parent prompts the user.

### 5. The audit log is part of the validation artifact

Every level run MUST emit `validation.started`, `validation.pass` or `validation.issue.raised`, and (for issues) `exec.revision.applied` or `pipeline.halted` events. A level without audit events is treated as if it didn't run.

### 6. Question every "v1 out of scope" carve-out at stage 5

A spec carve-out is a decision *not* to test a behavior. Stage 5 MUST surface every such carve-out to the user: *"this is outside the validation gate; confirm that's intended."* When a carve-out conflicts with another part of the spec — a documented workflow relies on a behavior that another section disowns — that's contract drift, not scoping. Severity: `critical` at stage-5 sign-off.

*(Originated from run `spec_driven-006` — FR-9 carved out the dev-server flow that FR-39 advertised, and the bug shipped past validation.)*

### 7. Validate the post-mutation shape when a request crosses a header-mutating layer

When a request crosses a reverse proxy, a same-process router, a CDN, or any layer that mutates `Origin` / `Host` / auth headers, the unit-test set MUST cover BOTH the **pre-mutation** shape (what the browser sends) AND the **post-mutation** shape (what the gate sees). Mocking the proxy is fine; mocking it away is not. Severity: missing either case → `blocker` when a header-mutating proxy exists in the dev workflow.

*(Originated from run `spec_driven-006` — the Origin/Host middleware unit tests covered only the post-rewrite shape; the missing Vite proxy `configure` hook went undetected.)*

### 8. Pinned items survive regeneration

Per `CLAUDE.md` § Pinned items survive regeneration. The parent MUST add a "promotion preservation" check to every stage-5 strategy: every pin in `<stage>/promoted.md` appears verbatim in the regenerated artifact (parsed via `parse_promoted_text` in `libs/promotions.py`, asserted modulo whitespace). Severity:

- Missing pin = `critical` (halts the work unit; reverting silent loss of user-pinned content is the highest-priority regression).
- Out-of-place pin (in artifact at wrong location, or under `## Pinned items (orphaned)` without justification) = `blocker`.
- Stage 6 (project code) does NOT support promotion in v1 — strategy MUST NOT generate this check for stage-6 regen.

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

## Update protocol

Surgical: one new principle / severity row per lesson. If a class of issue recurs across two or more runs, promote to a permanent severity row (here or in the per-task-type playbook if task-type-specific). Cite the source run id.
