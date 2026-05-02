# Validation strategy — spec_driven

Run: spec_driven-20260502-141813
Stage: 5 (Validation strategy)
Compiled by: parent (agent_team skill, parent_direct synthesis), 2026-05-02
Inputs: spec at `specs/development/spec_driven/final_specs/spec.md` (39 FRs, 16 NFRs, 15 ACs)

## Architecture note

Per CLAUDE.md "Tool scoping and team coordination", the parent owns spawning. For Stage 5 strategy:
- `agent_team__validation_manager` was invoked (mode=strategy) to define the team and produce per-level worker prompt templates. It returned the JSON team definition and recommended `parent_direct` synthesis.
- The parent spawned 7 level-specialist subagents in parallel using the manager's worker prompt templates. Each wrote its level file plus prompt+output audit pairs under `.audit/.../spawns/level-specialist-NN-{level}/`.
- This file (strategy.md) was authored by the parent from the seven returned summaries — no synthesis subagent was invoked.

## Levels chosen

7 of 7 standard levels apply to this spec. None deferred.

| Level | Output file | Items | Why this spec needs it |
|-------|-------------|-------|------------------------|
| **acceptance_criteria** | `acceptance_criteria.md` (16 KB) | 23 Gherkin scenarios | Mandatory per contract. Spec defines AC-1..AC-15 mapped 1:1 to primary flows; the file adds AC-16..AC-23 for FR/NFR items not enumerated in the summary. |
| **bdd_scenarios** | `bdd_scenarios.md` (28 KB) | 12 Features (9 per-flow + 3 cross-cutting) | Mandatory per contract. Captures end-to-end behaviors that span multiple FRs (e.g., follow-an-internal-cross-link is FR-15+FR-17+FR-33). Distinct from per-FR Gherkin in AC file. |
| **unit_tests** | `unit_tests.md` (41 KB) | 98 test descriptions across 10 groups | Spec has substantial discrete logic — `safe_resolve`, `EXPOSED_TREE` glob membership, GFM slug generation with collision suffixes, link classifier 3-case chain, JSONL per-line parser, file-read error mapping, localStorage state restore, long-name truncation. All pure functions, framework-independent. |
| **system_tests** | `system_tests.md` (30 KB) | 20 scenarios (SYS-01..SYS-20) | Spec is fundamentally backend+frontend+filesystem+browser integration. `make run` build+serve, path traversal end-to-end, dogfood self-render, refresh-after-external-write, browser back-button, concurrent writes — all need cross-component scenarios. |
| **performance** | `performance.md` (16 KB) | 7 checks (PERF-01..PERF-07) | Spec calls out concrete latency budgets — NFR-1 (`/api/tree` <200ms), NFR-2 (`/api/file` <100ms), NFR-3 (initial load <2s). Each is a measurable threshold needing a workload+method+pass criterion. |
| **security** | `security.md` (39 KB) | 18 checks (SEC-01..SEC-18) + threat model | Security is load-bearing in v1: path-traversal sandbox, symlink refusal, GET-only API, localhost-bind, no-CORS-wildcard, binary-content rejection, size cap. CVE-2023-29159 lessons baked in. |
| **accessibility** | `accessibility.md` (35 KB) | 18 checks (A11Y-01..A11Y-18) | Spec is UI-heavy with explicit ARIA tree pattern (FR-18..FR-20, FR-24..FR-26), WCAG 2.1 AA contrast (NFR-10), keyboard nav per W3C APG (FR-19). Tooling-specific (axe-core, NVDA, Colour Contrast Analyzer) — distinct level. |

**Total: 196 testable items across 7 levels.**

## Per-level summary

### Acceptance criteria

- **AC-1..AC-15** map 1:1 to the spec's `## Acceptance criteria summary` line items (first open / browse stages / browse settings / cross-link nav / broken link / external link / path traversal / extension whitelist / binary content / size limit / missing stage / refresh / state restoration / keyboard nav / concurrent write tolerance).
- **AC-16..AC-23** cover FR/NFR items not enumerated in AC summary: FR-37 broken-outside (CLAUDE.md → pyproject.toml), FR-33 case-2 silent anchor no-op, NFR-7 `127.0.0.1` bind, NFR-5 symlink-as-source rejection, FR-2 `REPO_ROOT` exit, FR-12 `SPEC_DRIVEN_PORT` override + unavailable-port exit, NFR-8 no CORS wildcard, NFR-6 405 on POST/PUT/PATCH/DELETE.
- Every scenario has concrete Windows absolute paths, exact HTTP status codes / error keys (`outside_sandbox`, `unsupported_extension`, `binary_content`, `too_large`, `kind: "file_removed"`), DOM attributes (`aria-selected="true"`, `target="_blank"`, `rel="noopener noreferrer"`), CSS classes (`link-broken`, `image-placeholder`), tooltip strings — and a `Spec refs:` traceability footer.

### BDD scenarios

- **9 per-flow Features**, one per primary flow (Flows 1–9 from the spec). Each has `Background:` (running app on 8765, REPO_ROOT, Stages 1–4 on disk), happy-path `Scenario:`, parametric `Scenario Outline:` with `Examples:` table where applicable, and edge cases (Flow 1 spec.md fallback, Flow 4 back-button + scroll restore, Flow 6 mailto/ftp/protocol-relative external classification, Flow 9 corrupted localStorage).
- **3 cross-cutting Features**: Markdown rendering (Shiki + GFM with language/file-type/image Examples including a malformed `.jsonl` line), Sidebar tree shape & ordering (FR-7/8/9/10 incl. validation/ priority order), Dogfood self-render (open app → final_specs/spec.md → click cross-link → findings/dossier.md → click cross-link → validation/strategy.md).
- All scenarios use real filenames, real URL paths, real localStorage key (`spec_driven.sidebar.v1`), real port (`8765`).

### Unit tests

- **10 unit groups, 98 cases total**. Groups: `safe_resolve` (12+ cases incl. URL-encoded, double-encoded, drive letters, mixed slashes, null bytes, symlinks, `~`); `EXPOSED_TREE` glob membership (positive + negative cases for each of the four sources); tree ordering (stage order + validation/ priority + alphabetical within); stage presence flag (FR-9 three states); GFM slug generator (table cases incl. collisions, non-ASCII, leading digit); markdown link classifier (each branch of FR-33); JSONL per-line renderer (well-formed + malformed + empty + trailing newline); file-read error mapping (FR-5 status code table); sidebar localStorage state (corrupted JSON fallback); long-name truncation classifier (file vs folder, middle vs end ellipsis).
- Each case has `Test name:`, `Inputs:`, `Expected output:`, `Edge cases handled:`, `Spec refs:` — no test-framework code.
- File opens with required-fixture inventory (`tests/fixtures/2mb_plus_1_byte.md`, `tests/fixtures/binary_with_null.md`, `tests/fixtures/jsonl_with_malformed_line.jsonl`, etc.).

### System tests

- **20 end-to-end scenarios** covering: `make run` build+serve (SYS-01), `make dev` two-process (SYS-02), port override + unavailable-port exit (SYS-03), `REPO_ROOT` walk-upward + failure (SYS-04), `/` redirect with spec.md fallback (SYS-05), path traversal end-to-end across encodings and slash directions (SYS-06), symlink rejection (SYS-07, with Windows skip-test condition), `127.0.0.1` bind (SYS-08), no CORS wildcard (SYS-09), GET-only API (SYS-10), dogfood self-render (SYS-11), cross-link + back-button (SYS-12), folder-only-URL replace-history redirect (SYS-13), refresh after external write (SYS-14), stale-tree click inline refresh (SYS-15), concurrent-write tolerance (SYS-16), session restore on reload (SYS-17), Section 1 navigation (SYS-18), image placeholder + non-image-bytes (SYS-19), JSONL render (SYS-20).
- Each has explicit `Setup / Action / Assertions / Spec refs / Components exercised` blocks. `Method: manual visual check` callouts mark the scroll-position / focus-ring / Shiki-color cases.

### Performance

- **7 checks** total. **3 hard-budget gates**: PERF-01 (`/api/tree` p95 < 200ms at locked 50 × 200 × 5 scale, NFR-1), PERF-03 (`/api/file` p95 < 100ms for 500 KB markdown, NFR-2), PERF-05 (cold initial app load p95 < 2000ms, NFR-3).
- **1 derived sanity gate**: PERF-02 (dogfood-only `/api/tree` p95 < 50ms — single-project baseline).
- **1 regression guard**: PERF-06 (10 concurrent `/api/tree` requests, p95 < 500ms, no errors — verifies no-cache design doesn't blow up under load).
- **2 observe-only metrics**: PERF-04 (2 MB file boundary — measure but no hard budget per spec), PERF-07 (100-line `events.jsonl` main-thread freeze — Shiki per-line could hurt; observe).
- Each check has fixture-generation pseudocode under `tests/fixtures/perf_tree/`, `perf_file/`, `perf_file_large/`, `perf_jsonl/`. Regression cadence: "manually before release" — no CI infra required.

### Security

- **18 checks** organized by attack vector: path traversal in 4 forms (SEC-01 dot-dot, SEC-02 absolute paths incl. UNC, SEC-03 null injection, SEC-04 OS-specific bypass — Windows ADS, short names, case-insensitive matching); symlinks in 3 sub-cases (SEC-05); extension/binary/size limits (SEC-06/07/08); tree-walk DoS at 10K files (SEC-09); GET-only verb confusion (SEC-10); bind address verification (SEC-11); no CORS wildcard (SEC-12); no auth code paths greppable (SEC-13); markdown XSS (`javascript:` URL sanitization) (SEC-14); SSRF surface absence (SEC-15); error leakage — no stack traces, no Python class names, no local paths in 4xx bodies (SEC-16); FR-37 outside-tree link rejection (SEC-17); tree-metadata leakage of skipped entries (SEC-18).
- Each check is curl-runnable with inline fixture descriptions. No exploit code beyond probe payloads.
- **Threat model section** distinguishes in-scope local attacker (malicious file content from upstream Claude, cross-origin local browser tabs) from explicitly-out-of-scope remote attacker (mitigation = NFR-7 loopback bind).

### Accessibility

- **18 checks** total, each tagged `[Spec-mandated]` or `[Recommended]`. Mandated coverage: tree container roles + multiselectable + tab stop (A11Y-01), treeitem attributes incl. aria-level (A11Y-02), aria-selected matches URL (A11Y-03), full W3C APG TreeView keyboard map (A11Y-04), missing-state items skipped by arrow nav (A11Y-05), focus + selection visuals simultaneously visible (A11Y-06), WCAG 2.1 AA contrast on every interactive state (A11Y-07), heading semantics observational (A11Y-08), long-name truncation accessible name (A11Y-09), folder-click toggle-only semantics (A11Y-10), breadcrumb landmark + nav element (A11Y-11), broken-link span as `<span>` not `<a>` (A11Y-12), external-link new-tab announcement (A11Y-13), refresh button as real `<button>` keyboard-activatable (A11Y-14), reduced-motion preference (A11Y-15), image placeholder accessible name (A11Y-16), code-block AT compatibility (A11Y-17), markdown link semantics (A11Y-18).
- Cited WCAG SC numbers and ARIA APG section names throughout. Tooling: axe-core, Chrome Lighthouse, NVDA + Chrome, Colour Contrast Analyzer, manual keyboard.

## Cross-cutting concerns

These concerns span multiple levels and require coordinated test design / state reset between runs. Implementation work units must respect them.

### 1. The "exposed tree" concept is referenced by every level

`EXPOSED_TREE` (FR-1) is named explicitly in unit tests (glob membership), system tests (SYS-06/07/14), security (SEC-04/17/18), and is the implicit basis for AC-7, AC-11, and the broken-link tooltip strings. **Inconsistency between the renderer's view and the file server's view is exactly the CVE-2023-29159 bug class.** Implementation MUST surface `EXPOSED_TREE` as a single named constant; tests at every level reference that constant.

### 2. The path-traversal sandbox spans security / system / unit

`safe_resolve` is unit-tested (12+ cases in unit_tests.md), system-tested end-to-end (SYS-06 with curl from outside the process), and security-probed across multiple attack vectors (SEC-01..SEC-05). All three must agree. A unit test that passes but a system test that fails means the helper is correct in isolation but the API endpoint isn't routing through it.

### 3. The ARIA tree pattern spans accessibility / system / BDD

A11Y-01..A11Y-06 verify DOM structure (axe-core + manual keyboard); SYS-11/SYS-17/SYS-18 verify rendering during navigation; BDD Flow 1, 2, 3, 9 cover user-facing keyboard sequences. The `aria-selected` / focus / URL triple must move atomically — a known UX-bug class (Storybook tracks it as a long-standing issue).

### 4. Concurrent-write / stale-tree handling

System-tested (SYS-15 stale click, SYS-16 mid-write tolerance), BDD edge-cased (Flow 7 deletion, Flow 8 inline refresh component), unit-tested (FR-5 file-read error mapping). The implementation must NEVER produce a 500 from `/api/tree` or `/api/file` for any of the FR-5.7 enumerated cases. Tests at all three levels share fixtures simulating the race window.

### 5. `localStorage` state restoration

System-tested (SYS-17), unit-tested (sidebar localStorage group), BDD edge-cased (Flow 9 corrupted localStorage). Single key `spec_driven.sidebar.v1`. Corrupted JSON must fall back to defaults with NO console error and NO unhandled exception.

### 6. State to reset between test runs

Every level's tests must start from a clean state:
- **Backend**: process restart between SYS scenarios that mutate fixture filesystem; `localStorage.clear()` between BDD/system scenarios that exercise persistence.
- **Frontend**: full hard-reload between scenarios that test session restore (SYS-17, BDD Flow 9).
- **Fixtures**: tests under `tests/fixtures/` are checked-in, never auto-mutated by tests; perf fixtures (`perf_tree/`) are generated by setup scripts before run.

### 7. Spec gaps the validation team surfaced

Worker subagents flagged behaviors the spec is silent on. **These should be resolved before Stage 6 implementation begins** — either by amending the spec or by accepting the workers' suggested defaults explicitly. Each gap is currently flagged in the relevant level file.

| Gap | Surfaced by | Suggested resolution |
|-----|-------------|----------------------|
| Non-ASCII heading slug behavior (e.g., `Café` → `cafe` vs `caf` vs `caf-` vs error) | unit_tests | Accept GFM behavior (drop non-ASCII letters, leave `-` separators); add to FR-30. |
| URL-decode layering for incoming `/api/file?path=...` (decode-once at FastAPI vs in `safe_resolve`) | unit_tests, security | Decode once at FastAPI's query-param layer; `safe_resolve` receives already-decoded input; document explicitly. |
| Blank `.jsonl` lines | unit_tests | Skip (don't render an empty Shiki block); add to FR-32. |
| Alpha-sort case sensitivity (`A.md` vs `a.md`) | unit_tests | Case-insensitive sort with stable tie-break by raw filename; add to FR-8. |
| Windows path case sensitivity (links like `./Foo.md` matching `foo.md`) | unit_tests, security | Case-sensitive match; emit `case mismatch — fix the link` tooltip on Windows. Add to FR-33. |
| `aria-disabled="true"` on `<span class="link-broken">` | accessibility | Add. Costs nothing, helps assistive tech announce non-interactive. |
| `aria-current="page"` on final breadcrumb segment | accessibility | Add per WCAG best practice. |
| `prefers-reduced-motion: reduce` honoring on FR-39 animation | accessibility | Add CSS media query gating the transition; trivial. |
| Screen-reader hint for `target="_blank"` external links | accessibility | Add visually-hidden text "(opens in new tab)" to external link pattern. |
| Keyboard-scrollable `<pre>` for overflowing code blocks | accessibility | Add `tabindex="0"` to overflowing `<pre>`; trivial. |

## How runtime validation will use this

Stage 6 (Execution + streaming validation) decomposes the spec into work units. Each work unit has a `work_unit_kind`, which determines which validation levels apply. The validation_manager (runtime mode) is invoked per work unit; it spawns one validator subagent per applicable level — but per the patched contract in CLAUDE.md, the parent does the actual `Agent` spawns, the manager defines the validator team and consolidates results.

### Mapping: work_unit_kind → applicable levels

| Work unit kind | Levels that run | Pass/fail rule |
|----------------|-----------------|----------------|
| `backend_api` (file endpoint, tree endpoint, error mapping) | acceptance_criteria + system_tests + unit_tests + security + performance | All scenarios at all 5 levels must pass. Performance: PERF-01/03 budgets are gates; PERF-04/06/07 are observe-only. |
| `backend_infra` (REPO_ROOT discovery, port binding, startup, Makefile) | system_tests + security | SYS-01/02/03/04/08 + SEC-11/13. Pass = all green. |
| `frontend_component_sidebar` (FR-18..FR-28) | acceptance_criteria + bdd_scenarios + accessibility + unit_tests | Sidebar AC group + BDD Flows 2/3/9 + A11Y-01..A11Y-10 + unit (localStorage, truncation). |
| `frontend_component_reader` (FR-29..FR-39) | acceptance_criteria + bdd_scenarios + accessibility + unit_tests | Reader AC group + BDD Flows 4/5/6 + Markdown rendering Feature + A11Y-11..A11Y-18 + unit (slug generator, link classifier, JSONL renderer). |
| `frontend_routing` (FR-15, FR-16, FR-17) | bdd_scenarios + system_tests | BDD Flow 1 + SYS-05/12/13/17. |
| `markdown_renderer` (Shiki + link classifier + GFM slug + image placeholder) | unit_tests + acceptance_criteria + accessibility + security (XSS) | Unit (slug, link classifier branches) + AC (broken/external/internal flow) + A11Y-13/16 + SEC-14. |
| `build_deploy` (Makefile, packaging, README) | system_tests | SYS-01/02. |
| End-to-end / integration (across all of the above, post-implementation) | bdd_scenarios + system_tests + performance + accessibility | Full BDD suite + all SYS-* + PERF-01/03/05 + A11Y full sweep. |

### Severity policy for runtime issues

When a validator returns issues, the validation_manager (runtime mode) emits `validation.issue.raised` events with severity:

- **`critical`** — security failures (any SEC-* failure), path-traversal escapes, exposed-tree consistency violations, 500-instead-of-structured-error in any FR-5 case. Halts the work unit immediately; cannot revise past 1 round without explicit user approval.
- **`blocker`** — acceptance-criteria failures, system-test failures, hard performance budgets (PERF-01/03/05) missed, ARIA tree pattern violations from A11Y-01..A11Y-06. Standard 3-revision-round cap applies.
- **`warning`** — accessibility "Recommended" gaps (the items in §"Cross-cutting concerns 7"), observe-only performance metrics out-of-band. Logged but does not halt; tracked into v2 backlog.

### Halt conditions (per CLAUDE.md "Iteration bounds")

- 3 revision rounds per work unit before halting.
- Same `issue_id` repeating across two iterations on the same unit → halt.
- Wall-clock exceeds 30 minutes on a single unit → halt.
- After halt, emit `pipeline.halted` event with reason; escalate to user.

## Open questions surviving Stage 5

These items were either (a) explicitly left open in the spec's `## Open questions` section and not closed by validation work, or (b) surfaced during validation strategy but left for the implementation phase to take a position on.

- **OQ-1, OQ-3..OQ-7 from spec.md** are unchanged. Validation strategy doesn't close these.
- **Spec gaps in §"Cross-cutting concerns 7"** (10 items) — recommended to resolve before Stage 6 begins, either by amending the spec with the suggested defaults or by accepting them via decision log.
- **CI integration for performance and security checks** — spec is silent on whether PERF-01..PERF-07 and SEC-01..SEC-18 run in CI or only manually. Performance level recommends "manually before release" as default; security recommends the same, with a stronger suggestion that path-traversal probes run in CI on every backend PR.

End of strategy.
