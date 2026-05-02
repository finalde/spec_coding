# Validation strategy — spec_driven

Run: spec_driven-20260502-clean
Stage: 5 (Validation strategy)
Compiled by: parent (agent_team skill, parent_direct synthesis under EXECUTION MODE: AUTONOMOUS), 2026-05-02
Inputs read: `final_specs/spec.md` (44 FRs incl. 14a/14b/14c subletters and 40-44, 16 NFRs, 27 ACs).
Inputs explicitly NOT read: any prior `validation/*.md`. Per CLAUDE.md "Regeneration semantics: read-zero from prior outputs."

## Architecture note

Per CLAUDE.md "Tool scoping and team coordination", the parent owns spawning. For Stage 5 strategy:
- `agent_team__validation_manager` was invoked (mode=strategy) to identify levels and define worker prompts. It returned the JSON team definition and recommended `parent_direct` synthesis.
- The parent spawned 5 level-specialist subagents in parallel (acceptance_criteria, bdd_scenarios, unit_tests, system_tests, security+performance+accessibility-combined). Each wrote its level file plus a spawn audit pair under `.audit/adhoc_agents/2026-05-02/spec_driven-20260502-clean/spawns/`.
- This file (strategy.md) was authored by the parent from the five returned summaries — no synthesis subagent was invoked.

## Levels chosen

7 of 7 standard levels apply to this spec. None deferred.

| Level | Output file | Items | Why this spec needs it |
|-------|-------------|-------|------------------------|
| **acceptance_criteria** | `acceptance_criteria.md` | 27 Gherkin scenarios | Mandatory per contract. Spec defines AC-1..AC-27 mapped 1:1 to primary flows + spec-summary items. |
| **bdd_scenarios** | `bdd_scenarios.md` | 18 Features / 70 scenarios | Mandatory. Captures end-to-end behaviors that span multiple FRs (cross-link follow = FR-15+FR-17+FR-33; editor save = FR-40+FR-14a). 14 per-flow Features + 4 cross-cutting. |
| **unit_tests** | `unit_tests.md` | 12 groups / 129 cases | Spec has substantial discrete logic — `safe_resolve`, `EXPOSED_TREE` glob membership, GFM slug, link classifier 4-case chain, JSONL per-line parser, file-read error mapping, sidebar localStorage, long-name truncation, regen-prompt size policy, editor dirty state. All pure functions, framework-independent. |
| **system_tests** | `system_tests.md` | 24 scenarios (SYS-01..SYS-24) | Spec is fundamentally backend+frontend+filesystem+browser integration. `make run` build+serve, path traversal end-to-end, dogfood self-render, refresh-after-external-write, browser back-button, concurrent writes, editor round-trip, regen warn-don't-truncate, read-zero constraint surfacing — all cross-component. |
| **performance** | `performance.md` | 8 checks (PERF-01..PERF-08) | Spec calls out concrete latency budgets — NFR-1 (`/api/tree` <200ms), NFR-2 (`/api/file` <100ms), NFR-3 (initial load <2s). Plus regen-prompt assembly time and cold-load. |
| **security** | `security.md` | 20 probes (SEC-01..SEC-20) + threat model | Security is load-bearing in v1: path-traversal sandbox, symlink refusal, GET/PUT/POST verb whitelist, localhost-bind, no-CORS-wildcard, binary-content rejection, size cap, atomic-write race, regen-prompt hard-ceiling, read-zero contract surfacing. CVE-2023-29159 lessons baked in. |
| **accessibility** | `accessibility.md` | 25 checks (A11Y-01..A11Y-25) | Spec is UI-heavy with explicit ARIA APG TreeView pattern (FR-18..FR-20, FR-24..FR-26), WCAG 2.1 AA contrast (NFR-10), keyboard nav per W3C APG (FR-19), editor a11y (FR-40), regen-warning a11y. Tooling-specific (axe-core, NVDA, Colour Contrast Analyzer) — distinct level. |

**Total: 27 + 70 + 129 + 24 + 8 + 20 + 25 = 303 testable items across 7 levels.**

## Per-level summary

### Acceptance criteria

- **AC-1..AC-27** map 1:1 to the spec's `## Acceptance criteria summary`. Each scenario has concrete Windows absolute paths, exact HTTP status codes / error keys, DOM attributes, CSS classes, tooltip strings — and a `Spec refs:` traceability footer.
- Grouped under 8 Features: routing, sidebar, settings, reader/links, file API, editor, regeneration, deployment.
- 73 spec-id mentions total — every FR/NFR is touched somewhere.

### BDD scenarios

- **14 per-flow Features**, one per primary flow (Flows 1–14 from the spec). Each has `Background:` (running app, REPO_ROOT, prior stages on disk), happy-path `Scenario:`, parametric `Scenario Outline:` with `Examples:` table where applicable, and edge cases.
- **4 cross-cutting Features**: Markdown rendering (Shiki + GFM with language/file-type/image Examples + malformed `.jsonl` line), Sidebar tree shape & ordering (FR-7/8/9/10 incl. validation/ priority), Dogfood self-render, Read-zero regeneration contract.
- **Scenario Outlines with Examples tables** for: external-scheme classification (https/http/mailto/ftp/`//cdn`), save-error code matrix (400/403/404/413/415/500), Shiki language fallback, stage-folder URL redirect target, validation/ priority order, read-zero coverage across stage subsets.
- 70 scenarios total. All use real URLs, real localStorage keys, real ports.

### Unit tests

- **12 groups, 129 cases total**. Groups: `safe_resolve` (15), `EXPOSED_TREE` membership (32), tree ordering (8), stage presence (3), GFM slug (12), link classifier (16), JSONL renderer (8), file-read error mapping (8), sidebar localStorage (6), long-name truncation (5), regen-prompt size + breakdown (10), editor dirty + save (6).
- Each case has `Test name:`, `Inputs:`, `Expected output:`, `Edge cases handled:`, `Spec refs:` — no test-framework code.
- File opens with required-fixture inventory.

### System tests

- **24 end-to-end scenarios** covering: `make run` build+serve (SYS-01), `make dev` two-process (SYS-02), port override + unavailable-port exit (SYS-03), `REPO_ROOT` walk-upward + failure (SYS-04), `/` redirect with spec.md fallback (SYS-05), path traversal end-to-end across encodings (SYS-06), symlink rejection (SYS-07, with Windows skip), `127.0.0.1` bind (SYS-08), no CORS wildcard (SYS-09), GET/PUT/POST verb whitelist (SYS-10), dogfood self-render (SYS-11), cross-link + back-button (SYS-12), folder-only-URL replace-history redirect (SYS-13), refresh after external write (SYS-14), stale-tree click inline refresh (SYS-15), concurrent-write tolerance (SYS-16), session restore on reload (SYS-17), Section 1 navigation (SYS-18), image placeholder + non-image-bytes (SYS-19), JSONL render (SYS-20), editor round-trip (SYS-21), editor save failure persistent banner (SYS-22), regen-prompt warn-don't-truncate (SYS-23), read-zero constraint surfacing (SYS-24).
- Each has `Setup / Action / Assertions / Spec refs / Components exercised`.
- `STATUS=SKIPPED-...` policy noted on SYS-07 (Windows symlink privilege) and SYS-08 LAN-reachability subcase (no second host).

### Performance

- **8 checks** total. **3 hard-budget gates**: PERF-01, PERF-03, PERF-05 (mapped to NFR-1/2/3).
- **1 derived sanity gate**: PERF-02 (single-project tree baseline <50 ms).
- **1 regression guard**: PERF-06 (10 concurrent `/api/tree`, p95 <500 ms, no errors).
- **2 observe-only metrics**: PERF-04 (2 MB file boundary), PERF-07 (100-line `events.jsonl` Shiki freeze).
- **1 added by autonomous regen**: PERF-08 (`POST /api/regen-prompt` for full 6-stage prompt < 200 ms).
- Each check has fixture-generation pseudocode under `tests/fixtures/perf_*`. Regression cadence: "manually before release".

### Security

- **20 probes** organized by attack vector: path traversal in 4 forms (SEC-01..SEC-04), symlinks in 3 sub-cases (SEC-05), extension/binary/size limits (SEC-06/07/08), tree-walk DoS at 10K files (SEC-09), GET/PUT/POST verb whitelist (SEC-10), bind address (SEC-11), no CORS wildcard (SEC-12), no auth code paths greppable (SEC-13), markdown XSS `javascript:` URL sanitization (SEC-14), SSRF surface absence (SEC-15), error leakage (SEC-16), FR-37 outside-tree link rejection (SEC-17), PUT atomic-write race (SEC-18), regen-prompt 1 MB hard ceiling (SEC-19), read-zero constraint surfacing in assembled prompt (SEC-20).
- Each probe is curl-runnable with inline fixture descriptions.
- **Threat model section** distinguishes in-scope local attacker (malicious file content from upstream Claude, cross-origin local browser tabs) from out-of-scope remote attacker (mitigation = NFR-7 loopback bind).

### Accessibility

- **25 checks** total, each tagged `[Spec-mandated]` (22) or `[Recommended]` (3).
- Mandated coverage: tree container roles + multiselectable + tab stop, treeitem attributes incl. aria-level, aria-selected matches URL, full APG TreeView keyboard map (incl. Home/End), missing-state arrow-skip, focus + selection visuals simultaneously visible, WCAG 2.1 AA contrast on every interactive state, heading semantics observational, long-name truncation accessible name, folder-click toggle-only, breadcrumb landmark + nav element + `aria-current="page"`, broken-link span with `aria-disabled="true"`, external-link new-tab announcement, refresh button keyboard-activatable, reduced-motion preference, image placeholder accessible name, code-block AT compatibility, markdown link semantics, editor textarea aria-label + aria-live for dirty state, editor error banner role="alert", single tab stop with roving tabindex, regen-prompt warning banner role="status".
- Cited WCAG SC numbers and ARIA APG section names throughout. Tooling: axe-core, Chrome Lighthouse, NVDA + Chrome, Colour Contrast Analyzer, manual keyboard.

## Cross-cutting concerns

These concerns span multiple levels and require coordinated test design.

### 1. The "exposed tree" concept is referenced by every level

`EXPOSED_TREE` (FR-1) is named in unit tests (glob membership), system tests (SYS-06/07/14), security (SEC-04/17/18), and is the implicit basis for AC-7, AC-11, and the broken-link tooltip strings. **Inconsistency between the renderer's view and the file server's view is exactly the CVE-2023-29159 bug class.** Implementation MUST surface `EXPOSED_TREE` as a single named constant; tests at every level reference that constant.

### 2. The path-traversal sandbox spans security / system / unit

`safe_resolve` is unit-tested (15 cases), system-tested end-to-end (SYS-06 with curl), and security-probed across multiple attack vectors (SEC-01..SEC-05). All three must agree. A unit test that passes but a system test that fails means the helper is correct in isolation but the API endpoint isn't routing through it.

### 3. The ARIA APG TreeView pattern spans accessibility / system / BDD

A11Y-01..A11Y-06 verify DOM structure (axe-core + manual keyboard); SYS-11/SYS-17/SYS-18 verify rendering during navigation; BDD Flow 1, 2, 3, 14 cover user-facing keyboard sequences. The `aria-selected` / focus / URL triple must move atomically.

### 4. Concurrent-write / stale-tree handling

System-tested (SYS-15, SYS-16), BDD edge-cased (Flow 12, 13), unit-tested (FR-5 file-read error mapping). The implementation must NEVER produce a 500 from `/api/tree` or `/api/file` for any of the FR-5.7 enumerated cases.

### 5. Editor + write-endpoint independence

The editor (FR-40) and `PUT /api/file` (FR-14a) must NOT trust each other. Editor dirty state is unit-tested (Group 12); PUT atomic-write race is security-probed (SEC-18); save round-trip is system-tested (SYS-21); save failure is system-tested (SYS-22) and BDD-covered (Flow 8). Same path-sandbox and extension-whitelist rules MUST apply to both endpoints.

### 6. Regen-prompt size policy + read-zero contract

Three-level coverage: unit test for size thresholds + breakdown formatter (Group 11); system test for warn-don't-truncate (SYS-23) and read-zero constraint surfacing (SYS-24); security probe for hard-ceiling 413 (SEC-19) and constraint-string presence (SEC-20). All three levels share a 60 KB and 1.2 MB fixture for the size-policy boundary.

### 7. localStorage state restoration

System-tested (SYS-17), unit-tested (sidebar localStorage group), BDD edge-cased (Flow 14 corrupted localStorage). Single key `spec_driven.sidebar.v1`. Corrupted JSON falls back to defaults with NO console error.

### 8. State to reset between test runs

- **Backend**: process restart between SYS scenarios that mutate fixture filesystem; `localStorage.clear()` between BDD/system scenarios that exercise persistence.
- **Frontend**: full hard-reload between scenarios that test session restore (SYS-17, BDD Flow 14).
- **Fixtures**: tests under `tests/fixtures/` are checked-in, never auto-mutated by tests; perf fixtures are generated by setup scripts before run.

## How runtime validation will use this

Stage 6 (Execution + streaming validation) decomposes the spec into work units. Each work unit has a `work_unit_kind`, which determines which validation levels apply. Per the patched contract in CLAUDE.md, the parent does the actual `Agent` spawns; the manager defines the validator team and consolidates results.

### Mapping: work_unit_kind → applicable levels

| Work unit kind | Levels that run | Pass/fail rule |
|----------------|-----------------|----------------|
| `backend_api` (file endpoints, tree endpoint, regen endpoint, error mapping) | acceptance_criteria + system_tests + unit_tests + security + performance | All scenarios at all 5 levels must pass. Performance: PERF-01/03/05/08 budgets are gates; PERF-04/06/07 observe-only. |
| `backend_infra` (REPO_ROOT discovery, port binding, startup, Makefile) | system_tests + security | SYS-01/02/03/04/08 + SEC-11/13. Pass = all green. |
| `backend_writer` (PUT /api/file atomic write) | unit_tests + system_tests + security | Editor round-trip + SYS-21/22 + SEC-18. |
| `frontend_component_sidebar` (FR-18..FR-28) | acceptance_criteria + bdd_scenarios + accessibility + unit_tests | Sidebar AC group + BDD Flows 2/3/14 + A11Y-01..A11Y-10/A11Y-21 + unit (localStorage, truncation). |
| `frontend_component_reader` (FR-29..FR-39) | acceptance_criteria + bdd_scenarios + accessibility + unit_tests | Reader AC group + BDD Flows 4/5/6 + Markdown rendering Feature + A11Y-11..A11Y-18 + unit (slug generator, link classifier, JSONL renderer). |
| `frontend_component_editor` (FR-40, FR-41) | acceptance_criteria + bdd_scenarios + system_tests + accessibility + unit_tests | Editor AC group + BDD Flows 7/8/9 + SYS-21/22 + A11Y-19/20 + unit Group 12. |
| `frontend_component_regen_panel` (FR-42, FR-43, FR-44) | acceptance_criteria + bdd_scenarios + accessibility + unit_tests | Regen AC group + BDD Flows 10/11 + A11Y-22 + unit Group 11. |
| `frontend_routing` (FR-15, FR-16, FR-17) | bdd_scenarios + system_tests | BDD Flow 1 + SYS-05/12/13/17. |
| `markdown_renderer` (Shiki + link classifier + GFM slug + image placeholder) | unit_tests + acceptance_criteria + accessibility + security (XSS) | Unit (slug, link classifier branches) + AC (broken/external/internal flow) + A11Y-13/16 + SEC-14. |
| `build_deploy` (Makefile, packaging, README) | system_tests | SYS-01/02. |
| End-to-end / integration | bdd_scenarios + system_tests + performance + accessibility | Full BDD suite + all SYS-* + PERF-01/03/05 + A11Y full sweep. |

### Severity policy for runtime issues

- **`critical`** — security failures (any SEC-* failure), path-traversal escapes, exposed-tree consistency violations, 500-instead-of-structured-error in any FR-5 case, atomic-write race producing torn file. Halts the work unit immediately.
- **`blocker`** — acceptance-criteria failures, system-test failures, hard performance budgets (PERF-01/03/05/08) missed, ARIA tree pattern violations from A11Y-01..A11Y-06. Standard 3-revision-round cap applies.
- **`warning`** — accessibility "Recommended" gaps, observe-only performance metrics out-of-band. Logged but does not halt; tracked into v2 backlog.

### Halt conditions (per CLAUDE.md "Iteration bounds")

- 3 revision rounds per work unit before halting.
- Same `issue_id` repeating across two iterations on the same unit → halt.
- Wall-clock exceeds 30 minutes on a single unit → halt.
- After halt, emit `pipeline.halted` event with reason; escalate to user.

## Open questions surviving Stage 5

- **OQ-1..OQ-9 from spec.md** are unchanged. Validation strategy doesn't close these.
- **CI integration for performance and security checks** — spec is silent on whether PERF-01..PERF-08 and SEC-01..SEC-20 run in CI or only manually. Performance level recommends "manually before release" as default; security recommends the same, with a stronger suggestion that path-traversal probes (SEC-01..SEC-05) run in CI on every backend PR.
- **mtime-based 409-on-conflict for `PUT /api/file`** — flagged in OQ-4 of the spec; validation strategy defers to v2 implementation decision.

End of strategy.
