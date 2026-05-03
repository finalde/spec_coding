# Validation strategy — spec_driven

Run: spec_driven-20260503-145859 (autonomous full-pipeline regen, parent-direct synthesis from 7 parallel level-specialist subagent outputs)

## Levels chosen

All seven canonical levels apply. Spec is UI-heavy with HTTP API + filesystem sandbox + CSRF gate + copy-paste prompt assembly + accessibility surface.

| Level | File | Why |
|---|---|---|
| Acceptance criteria | `acceptance_criteria.md` | 29 ACs in Gherkin Given/When/Then per primary flow. |
| BDD scenarios | `bdd_scenarios.md` | Feature-level user-perceived behaviors broader than ACs (15 Features, ~620 lines). |
| Unit tests | `unit_tests.md` | 131 cases across 12 module groups (backend libs + frontend components). |
| System tests | `system_tests.md` | 27 SYS-NN end-to-end scenarios (Playwright + httpx). |
| Security | `security.md` | 22 SEC-NN probes with CWE/CVE citations; CSRF, traversal, sandbox, XSS, single-404 enumeration policy. |
| Performance | `performance.md` | 7 PERF-NN budgets anchored to NFR-1, NFR-2, NFR-3 + 4 derived budgets. |
| Accessibility | `accessibility.md` | 25 A11Y-NN checks WCAG 2.1 AA; manual walkthrough trigger. |

## Per-level summary

### Acceptance criteria (29 ACs)

- 11 Feature clusters: file reader, tree consumer-walk, extension+size cap, Origin/Host validation, file writer, stale-write 409, per-Q/A inline edit, regen prompt assembly, regen size policy, build-prompt UI, promotions, parse-fallback Error Boundary, sidebar+breadcrumb, boot smoke, localhost-only bind.
- AC-11 split into six sub-scenarios — proves every Origin/Host gate path including the dev-server proxy contract.
- AC-13..15 cover the FR-7b 409 stale-write conflict path with the exact `{detail: {kind: "stale_write", current_mtime}}` shape.
- AC-25 includes a static-grep ban on `try { return <Foo/> } catch` per `agent_refs/validation/development.md` move 9.

### BDD scenarios (15 Features, ~620 lines)

- Browse, Render-mode dispatch (Scenario Outline per mode), File-edit, Per-Q/A inline edit, Pin/unpin, Per-stage Build prompt, Project-level Build prompt, CSRF Origin/Host gate (12-row Outline), Path sandbox traversal, Autonomous regen resume with read-zero, Stage-6 multi-mode dev workflow, Light-theme chrome with dark carve-outs, Audit-log discipline, Severity-by-blast-radius, Manual walkthrough.
- Build-prompt feature exercises BOTH the proxied dev-server flow AND the load-bearing pre-rewrite shape sent direct to backend → 403 (move 11). Dropping the Vite `configure` hook fails a test — no silent re-introduction of the run `spec_driven-006` bug.

### Unit tests (131 cases, 12 groups)

1. safe_resolve / path sandbox (traversal, ADS, Windows reserved, 8.3, Vite CVE-2025-62522)
2. file_reader (extension allowlist, size cap, security headers)
3. file_writer (atomic write, body validation, 409 stale-write)
4. tree_walker (uniform `children` field — consumer-walk regression — move 2)
5. api_security (Origin/Host allow-list; pre-rewrite `localhost:5173` direct → 403, post-rewrite → 200 — move 11)
6. regen_prompt (header verbatim, autonomous imperative, follow-ups inlined, promoted.md inlined, read-zero contract verbatim, size policy)
7. promotions (parse_promoted_text, idempotent post/delete, stage_folder allowlist)
8. api routes (PUT/POST/DELETE 405 surface, 415, 413, 404 single status)
9. frontend qaParser (interactive + autonomous-mode `*(judgment call ...)*` — move 10 fixture rotation)
10. frontend linkResolver (relative resolution, broken-link detection)
11. frontend QaErrorBoundary (real React class, `componentDidCatch` actually fires — move 9)
12. frontend autonomousMode + localStorage cross-tab `storage` event

### System tests (27 SYS-NN, 869 lines)

- SYS-1 boot smoke; SYS-2..6 every render mode via Playwright deep-link (move 8); SYS-7..8 editor + per-Q inline edit; SYS-9..11 regen-prompt small/warn/413; SYS-12 autonomous toggle persistence + cross-tab `storage`; SYS-13 QaView Error Boundary against malformed real-shape; SYS-14..15 safe_resolve probes; SYS-16 Origin/Host + DNS rebind; **SYS-16b** dev-server proxy parity (boots Vite + backend; tests pre-rewrite-403 and proxied-200 — move 11); SYS-17 `make run` localhost-only bind; SYS-18..27 verb whitelist, extension/size caps, sidebar structural sanity, project-page master Regenerate, broken-link spans NOT `<a>`, save-error banner persistence, pin verbatim survival, NFR-3 latency budget, 409 stale-write, manual-walkthrough handoff.
- SYS-16b notes: wiring the second Playwright `webServer` is itself a stage-6 implementation task; SYS-16b stands as the contract.

### Security (22 SEC-NN, ~285 lines)

- 17 critical (immediate-halt): SEC-1..16 + SEC-20 (read-zero contract verbatim across the 14-prompt autonomous×interactive matrix).
- 5 blocker (3-round cap): SEC-17 (single-404 enumeration), SEC-18 (nosniff + Content-Disposition), SEC-19 (verb whitelist), SEC-21 (pre-proxy-rewrite shape → 403 — move 11), SEC-22 (vite.config.ts rewrite hook static check).
- Vite **CVE-2025-62522** explicitly cited; CWE-22, CWE-59, CWE-66, CWE-79, CWE-178, CWE-204, CWE-352, CWE-350, CWE-434, CWE-668, CWE-693, CWE-749, CWE-754, CWE-770, CWE-1188 covered.

### Performance (7 PERF-NN, ~230 lines)

- PERF-1 `/api/tree` p95 < 250 ms at canonical scale (NFR-1).
- PERF-2 `/api/file` p95 < 100 ms <500 KB (NFR-2).
- PERF-3 initial app load p95 < 2 s (NFR-3).
- PERF-4 `/api/regen-prompt` p95 < 500 ms.
- PERF-5 `PUT /api/file` 50 KB p95 < 150 ms.
- PERF-6 tree_walker +100-file degradation ≤ 1.15× ratio.
- PERF-7 sidebar mount on 10 000 leaves p95 < 250 ms (severity `warning` for v1 — no virtualization).
- Method: `httpx.Client` (sync) ≥30 iterations after warm-up; p50/p95/max; Playwright `performance.measure` for frontend.

### Accessibility (25 A11Y-NN, ~250 lines)

- 22 Mandatory blockers + 3 Recommended warnings.
- Tree pattern, breadcrumb + `aria-current`, keyboard parity, focus visibility, icon-only button names, editor labeling, dirty / save-error / 409 / Copy live regions, dark `<pre>` contrast vs light chrome contrast, QaView non-color cues, soft-wrap toggle, reduced-motion, forced-colors, heading hierarchy, landmarks, 200% zoom.
- A11Y-17 wires `validation.requires_manual_walkthrough` per general.md principles 4–5.

## Cross-cutting concerns

- **Promotion-preservation check (general.md principle 8 — mandatory):** for each spec-pipeline stage with non-empty `<stage>/promoted.md`, every pin MUST appear verbatim in the regenerated artifact. Severity: missing pin = `critical`. Implementation: parse `promoted.md` via `parse_promoted_text` in `libs/promotions.py`, assert pin body appears as substring of regenerated artifact modulo whitespace normalization. Stage 6 (project code) excluded in v1.
- **Out-of-scope carve-out scan (general.md principle 6):** stage-5 strategy MUST surface every "out of scope for v1" line in the spec to the user. v1 carve-outs in this spec: IPv6 `[::1]`, `0.0.0.0` LAN bind, multi-user auth, theme picker, server-side preference persistence, search, diff/version history, live event feed, run-Claude-inline, stage-6 promotion. Per principle 6: those that conflict with another spec section get `critical` flagged at sign-off — none conflict here. The dev-server proxy carve-out from follow-up 004 was already revoked by follow-up 006.
- **Multi-mode runtime feature parity (development.md move 1):** spec advertises `make run-prod` and `make run-frontend`. Both must have e2e profiles. Currently SYS-16b is the contract; the second Playwright `webServer` entry wiring is a known stage-6 implementation task.
- **Header-mutating-layer middleware tests (development.md move 11):** unit-test set covers pre-rewrite (raw `localhost:5173` direct → 403) AND post-rewrite (rewritten Origin → 200) shapes. SYS-16b covers the proxied flow end-to-end.
- **Audit-event contract (general.md principle 5):** every level run MUST emit `validation.started`, `validation.pass` or `validation.issue.raised`, and (for issues) `exec.revision.applied` or `pipeline.halted`. A level without audit events is treated as if it didn't run.
- **Cross-platform Windows skips (development.md move 5):** unit tests 1.8/1.9/3.7 and any POSIX-symlink check skip with `pytest.mark.skipif(sys.platform == "win32", reason="...")`. Skipping with reason is healthy; silent passing is not.

## How runtime validation will use this (stage 6)

`work_unit_kind` → applicable levels:

| Kind | Levels |
|---|---|
| `backend_api` | acceptance + unit + system + security |
| `backend_lib` | unit + security (sandbox-relevant only) |
| `frontend_component` | bdd + unit + accessibility |
| `frontend_route` | bdd + system + accessibility |
| `boot_smoke` | system (SYS-1) — `critical` severity, no revision rounds |
| `e2e_profile` | system + accessibility |
| `regen_assembly` | unit + system + security (SEC-20) |
| `makefile_target` | system (SYS-17 + SYS-1) + security (SEC-13) |

## Pinned items

`validation/promoted.md` was empty at run start — no pinned content to preserve verbatim in the regenerated validation suite. `interview/promoted.md` (pin-001) appears verbatim in the regenerated `qa.md`.

## Spec gaps surfaced by stage 5

Two minor gaps the level-specialists flagged that the next interactive run could clean up (none are blockers):

1. **FR-13 status code on out-of-allowlist `stage_folder`** — spec says "allowlist" but doesn't pin 400 vs 422. AC-NN settled on 422 (FastAPI validation default).
2. **FR-19 broken-link `title` tooltip** — spec body mentions it; FR-19 itself didn't mandate. AC-27 asserts both span + `title`.

(Both deferred to a future follow-up.)
