# Follow-up draft 106 — 2026-05-20

Revert CLI default `--workers` from 5 → 1 after sudugu.org IP-blocked us in response to follow-up 105's parallel run. Parallel-mode code path stays in place for future opt-in; default behavior reverts to the polite single-stream pace.

## Why

Within ~10 s of launching 5 parallel workers in follow-up 105, every chapter request started returning HTTP 302 redirects to `https://www.google.com/`. Verified post-incident with three different User-Agents (Chrome / Firefox / curl) — all three returned 302 → google.com from the same Win11 client IP. Conclusion: sudugu.org's edge fired a per-IP anti-bot rule.

The IP block is currently active. Even single-threaded requests now redirect. The block likely expires on its own in minutes to hours (typical CDN edge rule TTL).

User signoff: parallel risk was accepted in 105 ("可能封 IP" was explicitly in the prompt). This follow-up captures the consequence + the mitigation.

## Design

### Revert the default, keep the code

`apps/cli/novel_download.py::main` parses `--workers N`. Previous default: 5. New default: 1. Three lines change (banner help string + comment + the `workers = N` initializer). The `download_all` ThreadPoolExecutor body and the `_download_in_isolated_worker` helper from follow-up 105 stay — `--workers 3` (or higher) still works once the block clears.

The single-stream default is the proven-polite shape: 0.8 s/req with httpx-level backoff on 429/5xx. The same pattern that downloaded `xianxia/fanren_xiuxian_zhuan/` to chapter 501 without incident.

### Why not also remove the parallel code?

Two reasons:
1. The user opted into parallel and may want to retry once the block lifts.
2. Removing it now would be churn — same surface area to maintain either way.

### Why not auto-detect the 302→google redirect?

A defensive improvement worth doing later: `_http_get` could treat "response URL host != source host" as a block signal and halt with a structured error instead of feeding google.com's HTML into the content parser (which is what generated the misleading `DownloadFailed: content block not found at <chapter URL>` messages). Deferred — small scope, separate concern from the immediate "revert default" fix.

### Resume contract still intact

Every chapter the parallel workers attempted got `done=False` with an `error` field set. On the next launch, those chapters automatically retry (the loop iterates over `chapters` and acts on any not-yet-`done` entry; the `error` field is informational, not load-bearing for resume logic). `xianxia/fanren_xiuxian_zhuan/` stays at its real 501-chapter checkpoint.

### What the user should do

- Wait some amount of time (likely 15-60 min, possibly longer) before relaunching. Or use a VPN to get a fresh IP.
- Once relaunched with the new default (`workers=1`), the download proceeds polite-rate.
- The fanren progress is preserved — it resumes from chapter 502.

### Out of scope

- 302-detection circuit-breaker in `_http_get` (deferred).
- Multi-source fallback so we can route around a blocked source (was already out of scope in 101 — still is).
- Proxy / VPN integration (user-side concern).
- Auto-back-off across CLI launches (e.g. detect the block, sleep 30 min, retry).

## Touch list

- **Modified**: `apps/cli/novel_download.py` — three-line change: docstring `Usage:` block, comment explaining the revert, `workers = 1`.
- **Audit**: changelog entry 106.
- **No code change**: `libs/infrastructure/writers/novel__writer.py` parallel-mode code path stays intact; opt-in via `--workers N` still works.
