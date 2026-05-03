# Validation strategy — spec_driven

Run: spec_driven-20260503-030434 (autonomous full-pipeline clean regen)

Inputs: `final_specs/spec.md` (44 FRs / 16 NFRs / 29 ACs / 7 OQs in this regen). Pre-reading: `.claude/skills/agent_team/playbooks/validation.md`, `.claude/agent_refs/validation/general.md`, `.claude/agent_refs/validation/development.md`. No `validation/promoted.md` exists.

## Levels chosen

| Level | Why this applies | Spec hooks | File |
|---|---|---|---|
| Acceptance criteria | Always — Gherkin-style runnable proofs of every AC-NN. | AC-1..AC-29 | `acceptance_criteria.md` (29 scenarios + pin-preservation) |
| BDD scenarios | Always — feature-level behaviors covering primary journeys + edge cases. | §2 user journeys, FR-1..FR-39 | `bdd_scenarios.md` (10 Features) |
| Unit tests | Spec has discrete logic (parsers, regex, walk-vs-shape contracts). | FR-4 / FR-11 / FR-19 / FR-21, regression coverage from prior run | `unit_tests.md` (12 groups) |
| System tests | Multi-component (FastAPI + React + browser); per `agent_refs/validation/development.md` move #1 e2e is mandatory. | FR-1..FR-39, NFR-1..NFR-13 | `system_tests.md` (27 SYS-NN) |
| Security | Spec touches FS sandboxing, CSRF/DNS-rebinding, content-sniffing, XSS. | FR-3..FR-9, NFR-4..NFR-9 | `security.md` (23 SEC-NN) |
| Performance | Spec defines hard latency budgets and a size policy with discrete tiers. | NFR-1..NFR-3, FR-12 | `performance.md` (8 PERF-NN) |
| Accessibility | UI-heavy spec with explicit ARIA / keyboard / contrast claims. | NFR-14..NFR-16, FR-24..FR-36 | `accessibility.md` (17 A11Y-NN) |

303 testable items total: 29 AC + 70 BDD scenarios + 129 unit cases + 27 SYS-NN + 23 SEC-NN + 8 PERF-NN + 17 A11Y-NN. (Counts cross-checked against the level files.)

## Per-level summary

### Acceptance criteria — 29 scenarios

- One Gherkin scenario per AC-NN with concrete URLs (`http://127.0.0.1:8765/api/...`), exact status codes (200/403/404/405/413/415), real file paths, and exact `data-testid` selectors (`sidebar`, `tree-leaf`, `project-link`, `qa-view`, `qa-q-block`, `qa-a-block`, `regen-prompt-block`, `link-broken`).
- Final `## Feature: Pin preservation` Scenario asserts pin-001 (Round 1 / functional-scope / "All discovered (Recommended)") from `interview/promoted.md` appears verbatim in regenerated `interview/qa.md`. No `## Pinned items (orphaned)` section emitted.
- Each scenario carries a `Spec refs:` line traceable back to FR-N / NFR-N / AC-N.

### BDD scenarios — 10 Features

- Sidebar tree + render dispatch (5 paths via Scenario Outline → MarkdownView/QaView/JsonlView/CodeView/ImagePlaceholder).
- File reader + safe_resolve sandbox (Scenario Outline for 404 cases: `..`, `CON.md`, `::$DATA`, junctions, etc.).
- File editor (toolbar, dirty-dot, persistent error banner, Ctrl+S; Save never disabled during error).
- Structured Q/A view + per-block edit, mutually exclusive with file-level edit.
- Per-stage Regenerate panel (with the FR-33(f) inline `regen-prompt-block` + header bar Copy + Wrap toggle).
- Project-page master Regenerate.
- Autonomous-mode toggle persistence + cross-tab `storage` event sync.
- QaView Error-Boundary fallback.
- Promotion (pin/unpin) with `stage_folder` allowlist + Stage-6 exclusion.
- Boot smoke.

### Unit tests — 12 groups, 129 cases

- Backend: `safe_resolve` (10 cases including all OWASP / Vite-CVE-2025-62522 traversal classes), `file_reader` (extension whitelist, size cap, single-404, header-set check), `file_writer` (atomic temp+rename, body cap, UTF-8 first-16 check), `regen_prompt` (header verbatim, autonomous imperative line, follow-up ordering, promoted.md inline, 50KB-warn / 1MB-413 size policy, read-zero in constraints), `promotions` (POST/DELETE roundtrip, idempotence), `tree_walker` (uniform `children` field, `test_tree_consumer_walk` walking the way the frontend Sidebar does), `api` (verb whitelist, Origin/Host validation, 413/415/404 mapping).
- Frontend: `Sidebar` (recursive `node.children`), `Editor` (dirty-dot / error-banner / Save-never-disabled), `QaView` parser (accepts BOTH `- A:` and `- A *(judgment call — chose X because Y)*:`; fixture rotation against a real on-disk autonomous-mode qa.md), `RegeneratePanel` (breakdown line shape, soft-wrap toggle, Copy label flip, no-render on 413), `autonomousMode` (key, default, storage-event subscription).
- All three `spec_driven-20260502-clean` regressions are encoded with `[regression-2026-05-02-clean]` tags + a regression-coverage table at the file's bottom.

### System tests — 27 SYS-NN

- SYS-1 boot smoke (`make run-prod` → `/api/tree` 200 → SPA loads → ≥1 leaf under each top-level section).
- SYS-2..6: every render mode via Playwright deep-link (one file per mode, asserts on rendered DOM, `consoleErrors == []`).
- SYS-7..8: editor save round-trip + per-Q inline edit; mutual-exclusion with file-level edit; reload preserves disk state.
- SYS-9..11: regen-prompt small / medium-warning / large-413 (the >1 MB case proves `regen-prompt-block` is NOT rendered).
- SYS-12: autonomous toggle persistence + native `storage` event cross-tab.
- SYS-13: QaView Error Boundary fallback against a deliberately-malformed real-shape qa.md.
- SYS-14..15: safe_resolve probes (traversal / junctions / ADS / Windows-reserved / 8.3-short — all return single 404).
- SYS-16: Origin/Host validation including DNS-rebind probe.
- SYS-17: `make run` binds 127.0.0.1 only (LAN unreachable + `netstat`/`ss` socket inspection + `0.0.0.0` source-grep).
- SYS-18..27: verb whitelist, extension/size caps, sidebar structural sanity, project-parent master Regenerate Copy + Wrap, broken-link span (NOT `<a>`), editor save-error banner persistence, pin survival in regen prompts, autonomous header verbatim, promotion roundtrip, NFR-3 latency budget.
- A `validation.requires_manual_walkthrough` trigger covers visual-only checks.

### Security — 23 SEC-NN

- Path traversal classes including the canonical Vite CVE-2025-62522 `\` deny-list bypass on both platforms.
- Windows reserved device names, ADS, 8.3 short names, junctions, symlinks (POSIX) — all → single 404.
- Disallowed extensions / oversized read / oversized write / binary write to `.md` / write to `.png` / verb whitelist.
- DNS rebinding (`Host: 127.0.0.1.evil.com` → 403) + Origin validation.
- Markdown XSS via raw `<script>` and via event-handler / `javascript:` URIs — both stripped.
- Single-404 enumeration policy.
- Header pair (`X-Content-Type-Options: nosniff` + `Content-Disposition: attachment`) on every `GET /api/file`.
- `0.0.0.0` source-grep audit.
- Read-zero contract sentence verbatim in every assembled regen prompt across the autonomous + interactive matrix.
- Severity floor: any traversal/sandbox-escape success = `critical`; missing security header = `blocker`. CWE ids attached (CWE-22, 59, 79, 83, 138, 203, 204, 350, 352, 434, 538, 693, 749, 770, 918, 1327).

### Performance — 8 PERF-NN

- NFR-1 `/api/tree` p95 < 200 ms at locked scale.
- NFR-2 `/api/file` p95 < 100 ms parameterized over CLAUDE.md / qa.md / spec.md / dossier.md.
- NFR-3 cold initial load p95 < 2 s.
- FR-12 size policy: 49 / 51 / 100 / 999 KB warning behavior + 1.0 / 1.1 MB hard ceiling (1.1 MB → 413 `kind: "too_large"`).
- Editor save round-trip < 250 ms; regen-prompt assemble at ~50 KB < 300 ms; sidebar first-paint < 100 ms.
- Severity: hard NFR misses + FR-12 contract violations = `blocker`; perceptual budgets / observe-only paint timings = `warning` (never halts).

### Accessibility — 17 A11Y-NN

- Each case cites a named WCAG criterion (2.1.1 Keyboard, 2.4.1 Bypass Blocks, 2.4.3 Focus Order, 2.4.7 Focus Visible, 1.3.1 Info & Relationships, 1.4.3 Contrast Min, 1.4.10 Reflow, 4.1.2 Name/Role/Value, 4.1.3 Status Messages, 2.3.3 Animation, 3.3.2 Labels).
- Anchored to NFR-14/15/16 plus FR-16, FR-17, FR-24, FR-25, FR-26, FR-27, FR-29, FR-30, FR-33, FR-36 and AC-21/22/24.
- A11Y-17 is a dedicated `validation.requires_manual_walkthrough` pass (visual hierarchy, keyboard focus visibility, NVDA sanity, forced-colors, 200% zoom, `prefers-reduced-motion`, tooltip-on-focus).
- A11Y-01..A11Y-16 are automatable via `@axe-core/playwright` + DOM snapshot assertions.
- Severity: structural ARIA / mandatory checks = `blocker`; recommended-tier gaps = `warning`.

## Cross-cutting concerns

1. **Frontend ↔ backend field-name mirroring (`agent_refs/validation/development.md` move #3).** Single canonical `node.children` field across `/api/tree`. Pure-shape unit tests are insufficient; `test_tree_consumer_walk` (in `unit_tests.md` group 6) walks the response the way the Sidebar does.
2. **Cross-platform fixture matrix.** Windows + Git Bash is the canonical dev host. POSIX symlinks (skipif `win32`), NTFS case-folding (skipif `!= "win32"`), `os.replace` atomicity (skipif `win32`), backslash conversion (win32-only) are all called out per case in `unit_tests.md` and `system_tests.md`.
3. **Consumer-walk e2e per render mode.** SYS-2..6 each open a real file that triggers exactly one render mode and assert on rendered DOM (`agent_refs/validation/development.md` move #8). The QaView fixture for SYS-13 is a malformed real-shape qa.md, not a synthetic one.
4. **Parse-on-render boundary discipline.** FR-19 + unit case 10.6 + SYS-13 jointly enforce a real React Error Boundary class, NOT `try { return <Foo/> } catch`.
5. **Regen prompt size policy is observable end-to-end.** PERF-6/PERF-7 + SYS-9..11 + AC-13 + SEC-23 jointly verify warn-don't-truncate / 413-no-block / read-zero-in-constraints.
6. **`make run` localhost binding.** SYS-17 + SEC-20 + AC-29 jointly assert `127.0.0.1` and forbid `0.0.0.0`.
7. **`agent_refs/validation/development.md` move #6 — no `uv` without pip fallback.** A static Makefile review during runtime validation flags any `uv run` without pip equivalent as `blocker`.

## How runtime validation will use this

| Stage 6 work_unit_kind | Levels run | Pass criterion |
|---|---|---|
| `boot_smoke` | system_tests SYS-1, SYS-17 | Process up, /api/tree 200, bound to 127.0.0.1, ≥1 leaf under each top-level section. Failure = `critical`, no revision rounds. |
| `backend_api` | acceptance_criteria + unit_tests + security + performance | All ACs in scope pass; consumer-walk tests pass; SEC traversal probes return single 404; PERF budgets within tolerance. |
| `frontend_component` | bdd_scenarios + unit_tests + accessibility | Render-mode-specific scenario passes (Playwright + DOM); axe-core scan green; Error Boundary fallback path reachable for parse-on-render components. |
| `e2e_walk` | system_tests SYS-2..27 | Every Playwright deep-link scenario passes; `consoleErrors == []`; manual walkthrough event emitted for visual checks. |

Iteration bounds: 3 revision rounds per unit (per CLAUDE.md). 30-min wall clock per unit. If the same `issue_id` repeats across two iterations, append `pipeline.halted` to `events.jsonl` and escalate.

## Promotion-preservation check

For each of the four spec-pipeline stages with a non-empty `<stage>/promoted.md`, every pin MUST appear verbatim in the regenerated artifact. Severity: missing pin = `critical`. Implemented by `parse_promoted_text` (in `libs/promotions.py`) parsing both `<stage>/promoted.md` and the regenerated artifact, then asserting each pin's body appears as a substring of the artifact, modulo whitespace normalization. Stage 6 (project code under `projects/{name}/`) is excluded from this check in v1.

For this run: `interview/promoted.md` contains pin-001 (Round 1 / functional-scope / "All discovered (Recommended)"). Validation under `acceptance_criteria.md` "Pin preservation" Feature confirms the pin appears verbatim in regenerated `interview/qa.md`.

## Audit log contract

Every level run MUST emit, to `.audit/adhoc_agents/{date}/{task_id}/events.jsonl`:
- `validation.started` (with `levels[]` + `pre_reading_consulted[]`)
- `validation.pass` OR one or more `validation.issue.raised` (with severity, level, location, description)
- `validation.requires_manual_walkthrough` for the visual-only A11Y-17 + system manual-walkthrough trigger.

A level that ran without audit events is treated as if it didn't run.
