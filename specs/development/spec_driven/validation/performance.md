# Validation — Performance level

Stage: 5 (Validation strategy) — clean-state regeneration
Run: spec_driven-20260503-030434
Specialist: level-specialist-06-performance
Inputs read:
- `specs/development/spec_driven/final_specs/spec.md` (NFR-1, NFR-2, NFR-3, FR-12)
- `.claude/agent_refs/validation/general.md` (severity table; observe-only → `warning`)

## Scope

Performance validation covers four budgets defined in the spec:

- **NFR-1.** `GET /api/tree` < 200 ms p95 at locked scale (≤50 projects, ≤200 files/project).
- **NFR-2.** `GET /api/file` < 100 ms p95 for files <500 KB.
- **NFR-3.** Initial app load < 2 s p95 on localhost.
- **FR-12.** `POST /api/regen-prompt` size-policy thresholds (50 KB warning, 1 MB hard ceiling, warn-don't-truncate).

Plus three derived budgets surfaced by the consumer-contract review (editor save round-trip, regen-prompt latency at worst-case in-spec size, sidebar tree first-paint).

## Tooling

- **Backend latency / status:** `httpx.Client` (sync) for repeatable wall-clock measurements over loopback. Per-case loop runs ≥30 iterations to compute p50 / p95. Warm-cache runs are taken AFTER one untimed warm-up request; cold-cache runs spawn a fresh process.
- **Frontend timings:** Playwright with `page.evaluate(() => performance.getEntriesByType('navigation')[0])` for navigation timings (`domContentLoaded`, `loadEventEnd`), `performance.getEntriesByType('paint')` for `first-contentful-paint` / `first-paint`, and `performance.now()` deltas around explicit user actions (Save click → 200 → re-render).
- **Workload generation:** for tree / file scale tests, a fixture builder seeds `specs/_perf_fixture/{project_NN}/...` with synthetic stage subfolders sized to the locked scale. The fixture root is added to the EXPOSED_TREE only under `PYTEST_CURRENT_TEST` (or an explicit env flag); never in production runs.
- **Threshold sources:** budgets quote NFR-1/2/3 verbatim; derived budgets cite the user-experience floor surfaced under `findings/` (markdown-editor-ux angle: <250 ms save roundtrip is the perceptual "instant" threshold).

## Severity policy (specialization of `agent_refs/validation/general.md`)

| Class | Severity | Halt? |
|---|---|---|
| Hard NFR budget missed at p95 (NFR-1, NFR-2, NFR-3) | `blocker` | Standard 3-revision-round cap. |
| FR-12 size-policy contract violation (truncation, missing warning, wrong status) | `blocker` | Standard. The size-policy is functional, not observe-only. |
| Derived UX budget missed at p95 (PERF-4, PERF-5, PERF-8) | `warning` | Logged; never halts. UX budgets are perceptual floors, not contracts. |
| p50 within budget but p95 outside on observe-only metric (paint times in CI) | `warning` | Logged; never halts. |
| Non-deterministic CI variance pushing p95 over budget on a non-blocker case | `warning` | Logged; flagged for fixture / harness review. |

## Cases

Each case names: workload, budget, measurement window (cold vs. warm), failure semantics, and the `events.jsonl` event the runner emits on miss.

---

### PERF-1 — `GET /api/tree` p95 < 200 ms at locked scale

**Source.** NFR-1.
**Workload.** Tree fixture seeded to the locked scale (50 projects × 200 files/project = 10 000 leaf files plus their stage-folder ancestors). Single `httpx.Client` over loopback. 50 iterations after one warm-up.
**Budget.** p95 < 200 ms; p50 < 80 ms (sanity floor — if p50 is also pushing 200 ms, the implementation is doing work it shouldn't).
**Measurement window.** Warm — the server has already walked the tree once during warm-up. The cold-cache case is covered by PERF-3 (which subsumes the first `/api/tree` call into the initial load budget).
**Failure semantics.** p95 ≥ 200 ms → `blocker` per severity table. Emit `validation.issue.raised` with `case_id: PERF-1, observed_p95_ms: <n>, budget_ms: 200`.
**Test pseudocode.**

```python
import httpx, time
samples_ms: list[float] = []
client = httpx.Client(base_url="http://127.0.0.1:8765")
client.get("/api/tree")  # warm-up, untimed
for _ in range(50):
    t0 = time.perf_counter()
    r = client.get("/api/tree")
    samples_ms.append((time.perf_counter() - t0) * 1000)
    assert r.status_code == 200
assert percentile(samples_ms, 95) < 200, f"PERF-1: p95={percentile(samples_ms,95):.1f}ms"
```

---

### PERF-2 — `GET /api/file` p95 < 100 ms for files <500 KB

**Source.** NFR-2.
**Workload.** Parameterized over four representative artifacts (each <500 KB):
- `CLAUDE.md`
- `specs/development/spec_driven/interview/qa.md`
- `specs/development/spec_driven/final_specs/spec.md`
- `specs/development/spec_driven/findings/dossier.md`
30 iterations per file, after one warm-up per file.
**Budget.** p95 < 100 ms per file. p50 < 40 ms (floor).
**Measurement window.** Warm. (Cold-cache file reads are typically dominated by OS page cache misses, which are out of the application's control on Windows; observing them here would be observe-only.)
**Failure semantics.** p95 ≥ 100 ms on any of the four files → `blocker`. Emit `validation.issue.raised` per file.
**Note.** Run separately for each fixture file; a single per-file failure is enough to halt — the spec budget is "<100 ms for files <500 KB," singular.

---

### PERF-3 — Initial app load p95 < 2 s on localhost

**Source.** NFR-3.
**Workload.** Cold-start scenario: launch a fresh uvicorn process, then drive Playwright to `http://127.0.0.1:8765/` with `cache: 'no-cache'` (browser cache cleared between runs). Measure window: from `navigation.startTime` to the moment `[data-testid="sidebar"]` AND the first `<main>` content node have been painted (i.e., HTML + bundle + first `/api/tree` + first `/api/file` all completed). 10 iterations (cold start is expensive; sample size is the realistic cost).
**Budget.** p95 < 2 000 ms; p50 < 1 200 ms (floor).
**Measurement window.** Cold — explicitly. The point of NFR-3 is the first-load experience; warm cache is covered by PERF-1 + PERF-2.
**Failure semantics.** p95 ≥ 2 000 ms → `blocker`. Emit `validation.issue.raised` with breakdown attached: `domContentLoaded_ms`, `loadEventEnd_ms`, `first-contentful-paint_ms`, `tree_response_ms`, `first_file_response_ms`. The breakdown is what makes the regression actionable.
**Test pseudocode.**

```python
async def test_perf_3_initial_load(page):
    samples_ms: list[float] = []
    for _ in range(10):
        await restart_server()  # fresh uvicorn process
        t0 = time.perf_counter()
        await page.goto("http://127.0.0.1:8765/", wait_until="networkidle")
        await page.wait_for_selector('[data-testid="sidebar"] [data-testid="tree-leaf"]')
        await page.wait_for_selector("main :not(:empty)")
        samples_ms.append((time.perf_counter() - t0) * 1000)
    assert percentile(samples_ms, 95) < 2000
```

---

### PERF-4 — Editor save round-trip p95 < 250 ms (typical files)

**Source.** Derived. Markdown-editor-ux research angle: 250 ms is the perceptual floor where a save feels "instant."
**Workload.** Open a stage file (`interview/qa.md`, ~30–80 KB), enter edit mode, append one line, click **Save** (Ctrl+S). Measure: `performance.now()` at click → 200 response received → editor re-renders with new baseline (dirty dot cleared). 30 iterations; warm cache.
**Budget.** p95 < 250 ms.
**Measurement window.** Warm.
**Failure semantics.** p95 ≥ 250 ms → `warning` (perceptual floor, not a hard NFR). Logged; never halts.
**Why warning, not blocker.** The spec's hard NFRs are NFR-1/2/3; this is a UX floor surfaced by research. Per `agent_refs/validation/general.md` standard severity table, observe-only metrics outside expected range are `warning`.

---

### PERF-5 — `POST /api/regen-prompt` p95 < 300 ms at worst-case in-spec size

**Source.** Derived. The 50 KB threshold (FR-12) is the boundary where the response is still "in-spec" without a warning; the assembler must remain responsive at that size.
**Workload.** Build a regen request that produces a ~49–50 KB prompt (full pipeline regen, all six stages selected, all modules, all follow-ups inlined; project fixture sized to hit ~50 KB on disk). 30 iterations after one warm-up.
**Budget.** p95 < 300 ms; p50 < 150 ms (floor).
**Measurement window.** Warm.
**Failure semantics.** p95 ≥ 300 ms → `warning`. Logged; never halts. The latency budget is a UX target, not an NFR.
**Note.** This case is paired with PERF-6/7 which test the size-policy *contract* (those are blockers). PERF-5 is about latency at the worst in-spec size.

---

### PERF-6 — 50 KB warning threshold check (warn-don't-truncate)

**Source.** FR-12.
**Workload.** Four prompt sizes built deterministically by tuning the fixture's revised_prompt + follow-ups bulk:
- 49 KB → expect `200`, `warning is None`, `bytes == len(prompt.encode())`.
- 51 KB → expect `200`, `warning is not None and warning != ""`, full prompt body returned (no truncation: `len(response.json()["prompt"].encode("utf-8")) == bytes`).
- 100 KB → expect `200`, `warning is not None`, full body returned.
- 999 KB → expect `200`, `warning is not None`, full body returned.
**Budget.** Functional contract; no latency assertion (latency is PERF-5's job).
**Measurement window.** N/A — single shot per size.
**Failure semantics.** Any of the above expectations not met → `blocker`. Truncation in particular (`len(response.json()["prompt"].encode()) != bytes` for any 50 KB < size ≤ 1 MB case) is the most severe FR-12 violation: warn-don't-truncate is the load-bearing reliability guarantee per NFR-11.
**Test pseudocode.**

```python
import httpx
client = httpx.Client(base_url="http://127.0.0.1:8765",
                     headers={"Origin": "http://127.0.0.1:8765"})
for target_kb, expect_warning in [(49, False), (51, True), (100, True), (999, True)]:
    body = build_request_targeting_kb(target_kb)
    r = client.post("/api/regen-prompt", json=body)
    assert r.status_code == 200
    j = r.json()
    if expect_warning:
        assert j["warning"], f"PERF-6: missing warning at {target_kb} KB"
    else:
        assert j["warning"] is None, f"PERF-6: spurious warning at {target_kb} KB"
    assert len(j["prompt"].encode("utf-8")) == j["bytes"], "PERF-6: bytes/prompt mismatch — truncation?"
```

---

### PERF-7 — 1 MB hard ceiling

**Source.** FR-12.
**Workload.** Two prompt sizes:
- 1.0 MB (1 048 576 bytes after assembly) → expect `200` with `warning is not None` (still in the warn-don't-truncate band; the ceiling is *exclusive* of 1 MB per FR-12 language `body > 1 MB → 413`).
- 1.1 MB → expect `413` with `response.json()["detail"] == {"kind": "too_large", "bytes": <count>}`.
**Budget.** Functional contract; no latency assertion.
**Measurement window.** N/A.
**Failure semantics.** Either expectation not met → `blocker`. A `200` at 1.1 MB violates the hard ceiling; a `413` at 1.0 MB violates warn-don't-truncate.
**Note.** The boundary at exactly 1 MB matches AC-13's "above 1 MB returns 413" — interpreted as strict `>`. If the implementation chooses `>=`, that's a spec drift to flag, not a test bug.

---

### PERF-8 — Sidebar tree render perf < 100 ms after `/api/tree` resolves

**Source.** Derived. UX floor: once the tree JSON is on the wire, paint the sidebar quickly so the user sees navigation structure before any file content.
**Workload.** Locked-scale fixture (same as PERF-1). Playwright drives `page.goto("/")` with the tree fixture loaded. Measure: from the `/api/tree` response's `responseEnd` (via `PerformanceResourceTiming`) to the moment `[data-testid="sidebar"] [data-testid="tree-leaf"]:nth-of-type(50)` is painted. 20 iterations; warm cache (browser cache primed).
**Budget.** p95 < 100 ms; p50 < 50 ms (floor).
**Measurement window.** Warm. Cold tree-paint is folded into PERF-3's cold-load budget.
**Failure semantics.** p95 ≥ 100 ms → `warning`. Logged; never halts. Paint times in CI are observe-only per the standard severity table.
**Test pseudocode.**

```python
async def test_perf_8_sidebar_first_paint(page):
    samples_ms: list[float] = []
    for _ in range(20):
        await page.goto("http://127.0.0.1:8765/")
        timing = await page.evaluate("""() => {
            const r = performance.getEntriesByType('resource')
                .find(e => e.name.endsWith('/api/tree'));
            const tree_end = r.responseEnd;
            const leaf = document.querySelector('[data-testid="sidebar"] [data-testid="tree-leaf"]:nth-of-type(50)');
            return leaf ? performance.now() - tree_end : null;
        }""")
        assert timing is not None
        samples_ms.append(timing)
    assert percentile(samples_ms, 95) < 100  # warning on miss, not blocker
```

---

## Audit-event protocol

Per `agent_refs/validation/general.md` core principle 5, every PERF-NN run emits:

- `validation.started` with `level: "performance", case_ids: [...]` at the start of the level.
- `validation.pass` per case on success, with `observed_p50_ms`, `observed_p95_ms`, `budget_ms`, `samples_n`.
- `validation.issue.raised` per failing case, with the same fields plus `severity: "blocker" | "warning"` and `case_id`.
- `validation.requires_manual_walkthrough` is NOT used at this level — performance budgets are machine-measurable.

A level run with no audit events is treated as if it did not run.

## Out of scope (deferred)

- **Concurrency / load testing.** Single-user localhost only per spec scope; multi-client throughput is out of scope for v1.
- **Cross-origin / WAN latency.** The server binds to 127.0.0.1 (FR-38, NFR-7); LAN performance is undefined.
- **Browser-side bundle-size budgets.** Vite produces the bundle; bundle-size budgets are a build-time concern, not a runtime perf check. Out of scope for stage-5 strategy; can be added as a build-time linter.
- **Power-loss / I/O fault perf.** NFR-10 covers atomicity, not latency under fault. Skipped here.

## Promotion preservation

This run's `validation/promoted.md` is empty (clean-state regen, no pinned items). If pins land in a future run, every pin must appear verbatim in this regenerated artifact per the promotion-preservation contract.
