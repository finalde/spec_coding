# Performance validation — `spec_driven`

Run: `spec_driven-20260503-145859` · Level specialist: `level-specialist-06-performance`

Hard performance budgets in the spec are NFR-1 (`GET /api/tree` p95 < 250 ms at canonical scale), NFR-2 (`GET /api/file` p95 < 100 ms for files <500 KB), and NFR-3 (initial app load p95 < 2 s on localhost). This level extends those budgets with a small set of derived budgets covering the other latency-sensitive surfaces (regen-prompt assembly, write round-trip, tree-walk degradation, sidebar mount) so the gate is end-to-end and not just a partial coverage of the three NFRs.

Per `agent_refs/validation/general.md` § Standard severity policy, any "hard performance budget missed" is a `blocker` (3-revision-round cap). Per `agent_refs/validation/development.md`, every backend-side latency check should be implementable with plain `pip` + `.venv` (no `uv`) and Windows-friendly fixtures.

## Scope and out-of-scope

**In scope:**

- Single-client p50 / p95 latency on a developer-class workstation against the `make run-prod` single-process backend bound to `127.0.0.1:8765`.
- Backend latency for the four read endpoints (`/api/tree`, `/api/file`, `/api/stages`, `/api/regen-prompt`), the write endpoint (`PUT /api/file`), and the two promote endpoints (where derived from regen-prompt budget).
- Frontend cold-load time (HTML + JS + first `/api/tree` + first `/api/file`) under `make run-prod` (covers NFR-3).
- Frontend sidebar mount cost on a 10 000-leaf tree.
- Performance regression check when the artifact tree grows (canonical-scale + 100-file delta).

**Out of scope (per spec § Out of scope (v1) + agent-refs guidance):**

- Concurrency / multi-client load. Spec is explicitly single-user localhost; concurrent benchmarks would test a non-existent contract. **Judgment call: not measured** — flag as a v2 follow-up if multi-author / shared-host modes are ever introduced.
- LAN bind (`0.0.0.0`) latency. Out-of-scope per FR-39 / OQ-9; SEC-20 forbids the bind in the first place.
- IPv6 (`[::1]`) latency. Uvicorn IPv4-only in v1 (OQ-8).
- Cold-disk first-touch FS latency. Measurements run after one warm-up iteration so the OS page cache is primed; this matches the actual user experience of a long-lived dev session.
- Production-grade percentile tail (p99, p99.9). Single-user localhost workload doesn't justify the cost; p50 + p95 captures the budget.
- Frontend bundle-size budget. Touched indirectly by NFR-3 (initial load p95 < 2 s) but not enumerated here as a separate PERF-NN.

## Methodology — backend

- **Driver:** synchronous `httpx.Client(base_url="http://127.0.0.1:8765")` with `verify=False` not needed (loopback HTTP, no TLS). Re-used `Client` instance across iterations so the TCP socket is kept warm — tests measure the server-side handler cost, not connection setup.
- **Iteration count:** ≥ 30 timed iterations per workload after one warm-up iteration that is discarded. The warm-up primes the FS page cache and the tree-walker's internal state. Below 30 iterations the p95 sample is too noisy to assert against (binomial 95 % CI on the 95th-percentile rank with n = 30 covers ranks 27–30, tight enough).
- **Timer:** `time.perf_counter_ns()` deltas around the request. Includes JSON deserialization on the client side (the SPA pays this cost too, so the budget should include it).
- **Statistics reported:** p50, p95, max. Budget is on p95.
- **Pass criterion:** p95 ≤ stated budget. Fail emits `validation.issue.raised` with severity `blocker`.
- **Fixture scale:** the canonical "50 projects × 200 files = 10 000 leaves" tree is materialized once into a tmp directory pointed at by `EXPOSED_TREE`, and reused for every PERF-NN that needs it. Files are 1 KB plain markdown unless a specific PERF-NN says otherwise.
- **Isolation:** runs serialized; no other PERF-NN executes concurrently. Hardware variance is tolerated up to ± 15 % between repeat runs of the same PERF-NN; > 15 % between back-to-back runs flags the host as unsuitable (`validation.requires_manual_walkthrough`).
- **Skip rule:** PERF-NN that depends on Playwright skips with a clear reason on hosts without browser binaries (per `agent_refs/general.md` § Skipping is a feature) — not silently passing.

## Methodology — frontend

- **Driver for cold-load:** Playwright Chromium, `page.goto('http://127.0.0.1:8765/')` with `waitUntil: 'networkidle'`. Performance timeline read via `performance.getEntriesByType('navigation')[0].domContentLoadedEventEnd - navigationStart` and `performance.now()` after the first `/api/file` settles. The two are summed for the "user-perceived ready" metric.
- **Driver for sidebar mount:** Playwright Chromium with the same canonical 10 000-leaf tree mounted into `EXPOSED_TREE`. Measured as `performance.mark('mount-start')` immediately before the `Sidebar` component's first render and `performance.measure('mount', 'mount-start', 'mount-end')` after the tree's `useEffect` settles. Because v1 has no virtualization (PERF-7 below), this is the worst-case render budget.
- **Iteration count:** 10 timed cold loads after one warm-up. Browser-driven measurement is more expensive than backend-only; 10 is a pragmatic floor that still gives a stable p95.

---

## PERF-1 — `GET /api/tree` at canonical scale (NFR-1)

**Workload.** `EXPOSED_TREE` materialized at the canonical scale: 50 project folders, each with 200 leaf files at varying nesting depths (1–4 levels). Total leaves = 10 000. Tree includes the full `.claude/` and `CLAUDE.md` surface so the response shape is realistic.

**Method.** `httpx.Client.get('/api/tree')`, 30 timed iterations after 1 warm-up. Re-used client. Each call serializes the full recursive `{type, name, path, children: []}` structure (per FR-3 — uniform `children` field).

**Budget.** p95 ≤ 250 ms (NFR-1 — direct).

**Pass criterion.** p95 ≤ 250 ms AND max ≤ 400 ms (max headroom guards against a single bad outlier that would surface to the user as a "the sidebar feels stuck" complaint). On fail: `blocker`.

**Notes.** This is the only PERF-NN that asserts against an explicit NFR's exact numeric. Tree response is also roughly the largest JSON payload the read path produces — so this benchmark indirectly covers JSON-serialization throughput.

---

## PERF-2 — `GET /api/file` for files < 500 KB (NFR-2)

**Workload.** Three representative file profiles inside `EXPOSED_TREE`:

| Profile | Size | Path |
|---|---|---|
| Small markdown | ~4 KB | `specs/.../interview/qa.md` (representative) |
| Medium markdown | ~80 KB | A regen-prompt-sized file fixture |
| Near-budget | ~480 KB | A synthetic markdown file just under the 500 KB NFR-2 boundary |

**Method.** Per profile, `httpx.Client.get('/api/file?path=<rel>')`, 30 timed iterations after 1 warm-up. Three profiles → three separate p95 readings.

**Budget.** p95 ≤ 100 ms across **all three profiles** (NFR-2 — direct).

**Pass criterion.** Every profile's p95 ≤ 100 ms AND max ≤ 200 ms. On fail: `blocker`.

**Notes.** Includes the response-header overhead from FR-5 (`X-Content-Type-Options: nosniff`, `Content-Disposition: attachment`). Any future header that materially adds CPU cost (e.g., HMAC signing) shows up here.

---

## PERF-3 — Initial app load on localhost (NFR-3)

**Workload.** Cold Playwright Chromium → `http://127.0.0.1:8765/` under `make run-prod` (single-process: backend serves SPA bundle from `backend/static/`). Tree is the canonical 10 000-leaf scale (PERF-1 fixture). The app loads, the sidebar walks `/api/tree`, the user-saved last-viewed file (or `CLAUDE.md` as the deterministic default) is fetched via `/api/file`, and the main pane renders it.

**Method.** "User-perceived ready" = `domContentLoadedEventEnd - navigationStart` + the wall-clock delta from `domContentLoadedEventEnd` to the moment the main pane's render component mounts. 10 timed cold loads after 1 warm-up (browser cache cleared between iterations via `context.clearCookies()` + `route.fulfill` interception of `/api/*` to bypass SW cache; v1 has no SW so this is a no-op safeguard).

**Budget.** p95 ≤ 2000 ms (NFR-3 — direct).

**Pass criterion.** p95 ≤ 2000 ms AND max ≤ 3500 ms. On fail: `blocker`.

**Notes.** This is a multi-stage measurement: PERF-1 latency (tree fetch) and one PERF-2 latency (first file fetch) both feed into PERF-3, plus the static-asset transfer cost. If PERF-3 fails but PERF-1 and PERF-2 pass, the regression is in the bundle (size, parse, mount). Deferred subdivision (separate "TTI" vs "first contentful paint" budgets) — out of scope for v1.

---

## PERF-4 — `POST /api/regen-prompt` for default 6-stage all-modules

**Workload.** A typical `spec_driven` project: `revised_prompt.md` ~ 8 KB, four follow-up files totaling ~ 12 KB, every stage selected, every module checked, no autonomous toggle, no pinned items in `<stage>/promoted.md`. Body roughly 30–40 KB before assembly.

**Method.** `httpx.Client.post('/api/regen-prompt', json={...})`, 30 timed iterations after 1 warm-up. Each call exercises FR-10 / FR-11 fully — opens `revised_prompt.md`, walks `user_input/follow_ups/`, inlines every `<stage>/promoted.md` (empty in this fixture), assembles the constraints block, returns the prompt text.

**Budget.** p95 ≤ 500 ms.

**Pass criterion.** p95 ≤ 500 ms AND max ≤ 800 ms. On fail: `blocker`.

**Rationale.** No NFR pins this directly, but the SPA's "Build prompt" button is on a hot path — if assembly takes ≥ 1 s the user feels a hang. 500 ms is the standard "user perceives no lag" cutoff for a button click that triggers a meaningful computation. Judgment call: chose 500 ms over 250 ms because regen-prompt assembly is genuinely IO-heavy (reads ≥ 5 files per call) and the button has explicit feedback (loading state allowed).

---

## PERF-5 — `PUT /api/file` round-trip for a 50 KB body

**Workload.** A typical edited markdown file: 50 KB of UTF-8 text. Path inside `EXPOSED_TREE`. `If-Unmodified-Since` header set to the file's current `mtime` so the round-trip exercises the happy path (no 409 stale-write).

**Method.** Each iteration: read file's current mtime, `PUT /api/file` with new content (50 KB), assert 200, assert response `{bytes, mtime}` shape. 30 iterations after 1 warm-up. **The fixture file is restored to its original content between iterations** so the 30 writes don't accumulate (each PUT operates on the same starting state).

**Budget.** p95 ≤ 150 ms.

**Pass criterion.** p95 ≤ 150 ms AND max ≤ 300 ms. On fail: `blocker`.

**Rationale.** No NFR pins this directly. 150 ms is the standard "Save feels instant" floor — Ctrl+S in the editor should not introduce visible lag. The atomic write (temp file + `os.replace`) is the dominant cost on Windows / NTFS. Judgment call: 150 ms (vs the 100 ms budget on read in NFR-2) acknowledges that write is meaningfully heavier than read on any filesystem with journaling.

---

## PERF-6 — Tree-walker degradation under +100-file delta

**Workload.** Start from the PERF-1 canonical scale (10 000 leaves). Measure `GET /api/tree` p95 (call this `p95_baseline`). Add 100 new files into a representative subfolder (e.g., a fresh `specs/development/spec_driven/findings/synthetic-*` set). Re-measure (`p95_after`).

**Method.** Same `httpx.Client` driver as PERF-1. 30 timed iterations both before and after the file-add. The file-add is a pure FS operation outside the timed window.

**Budget.** `p95_after / p95_baseline ≤ 1.15` (no more than 15 % degradation for a 1 % growth in leaf count).

**Pass criterion.** Ratio ≤ 1.15. On fail: `blocker`.

**Rationale.** The tree-walker (`projects/spec_driven/backend/libs/tree_walker.py`) is the single piece of backend code most likely to have hidden N² behavior in `EXPOSED_TREE` enumeration. PERF-1 alone passes a fixed-size budget but won't catch an `O(n²)` walker that happens to fall under 250 ms at exactly 10 000 leaves. PERF-6 adds the differential signal. Judgment call: 15 % is more permissive than e.g. 5 % because filesystem caching introduces real noise; the goal here is catching algorithmic regressions, not micro-optimizations.

---

## PERF-7 — Sidebar mount on 10 000-leaf tree (no virtualization in v1)

**Workload.** Same canonical 10 000-leaf tree (PERF-1 fixture). Playwright opens `http://127.0.0.1:8765/`, waits for `/api/tree` to settle, marks `mount-start`, lets React mount the `Sidebar` component, marks `mount-end` after the recursive children render is committed (signaled by `useEffect` running on the root sidebar node).

**Method.** Playwright + `performance.measure`. 10 timed iterations after 1 warm-up. Browser context is fresh per iteration to defeat React DevTools / cache effects.

**Budget.** p95 ≤ 250 ms in Chromium.

**Pass criterion.** p95 ≤ 250 ms AND max ≤ 500 ms. On fail: `warning` for v1 + flag a v2 follow-up. **Judgment call: severity is `warning`, NOT `blocker`,** because v1 has no virtualization (FR-15 — full recursive sidebar) and the canonical scale is at the edge of what unvirtualized recursive React can handle without virtualization. If this PERF-NN fails, the right response is "introduce `react-virtuoso` or windowing in v2" not "block v1 release." Documented here so the user is not surprised when the budget is missed at extreme scale.

**Rationale.** No NFR pins this directly, but a 10 000-leaf sidebar is the workload that drives PERF-3 (initial app load). If sidebar mount is the bottleneck inside PERF-3, PERF-7 isolates it for diagnosis. The 250 ms budget is the same "user perceives no lag on first paint" floor as PERF-3.

---

## Audit & event protocol

Each PERF-NN run emits the standard validation events into the run's `events.jsonl`:

- `validation.started` with `{level: "performance", check: "PERF-NN"}` at the top of the iteration loop.
- `validation.pass` with `{level: "performance", check: "PERF-NN", p50_ms, p95_ms, max_ms, budget_ms}` on pass.
- `validation.issue.raised` with `{level: "performance", check: "PERF-NN", severity, p50_ms, p95_ms, max_ms, budget_ms, ratio (PERF-6 only)}` on fail.

Per `agent_refs/validation/general.md` § The audit log is part of the validation artifact, a PERF-NN with no audit event line is treated as if it didn't run.

## Failure escalation

- Any single `blocker` PERF-NN failure on a clean canonical-scale tree → standard 3-revision-round cap.
- Two consecutive runs of the same PERF-NN failing with the same metric (within 5 %) → `pipeline.halted` per § Iteration bounds.
- PERF-7 failing → `warning` only, surface as `validation.requires_manual_walkthrough` so the user confirms whether to defer to v2 (virtualization) or invest now.

## Non-goals reiterated

This file does NOT specify:

- Lighthouse / Core Web Vitals scores (no production CDN; localhost dev workflow only).
- Test framework choice for the Python side (covered by `validation/unit_tests.md` and `validation/system_tests.md`).
- The actual Pytest / Playwright fixture setup code (drafted in `system_tests.md` and unit_tests.md as appropriate).
- p99 / p99.9 — single-user localhost doesn't justify them.

The performance gate is a small, sharp set of seven measurements covering the three explicit NFRs plus four derived hot paths. If any of the seven fails on a representative canonical-scale fixture, stage-6 acceptance is blocked until either the implementation or the budget is amended through a follow-up.
