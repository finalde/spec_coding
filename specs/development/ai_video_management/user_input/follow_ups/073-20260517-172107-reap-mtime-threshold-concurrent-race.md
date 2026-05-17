# Follow-up draft 073 — 2026-05-17

Race-condition bugfix in `_reap_incomplete_folders`. User reports two slots out of six failing with `[Errno 2] No such file or directory` when writing the actor jpg:

```
#2: actor_0096: write_failed: [Errno 2] No such file or directory: '...\\actor_0096\\east-asian__female__36-50.jpg'
#4: actor_0099: write_failed: [Errno 2] No such file or directory: '...\\actor_0099\\east-asian__female__36-50.jpg'
```

The folders `actor_0096` / `actor_0099` were successfully allocated by `_allocate_actor_id` (atomic `mkdir(exist_ok=False)`), but by the time their Kling HTTP returned (30–120s later) and the writer tried to `write_bytes` the jpg, the folder had been **deleted by a sibling concurrent request's reaper sweep**.

## Root cause

Per follow-up 064 (unified-mode generator) + follow-up 059 (diverse-mode preview→confirm worker pool), the frontend issues N parallel `count=1` requests to `POST /api/actors/generate` so the user gets progressive UI feedback instead of one long-blocking batch. Each request enters `ActorPool.generate_batch` which runs `self._reap_incomplete_folders(actors_dir)` at the top before allocating its own slot:

```
T=0   Request A: reap (nothing to reap); allocate actor_0096; Kling.generate(...)  ← 30-120s wait
T=2   Request B: reap → sees actor_0096 with no jpg → DELETES actor_0096   ← BUG
T=4   Request C: reap → sees actor_0099 (B's allocation) with no jpg → DELETES actor_0099
T=45  Request A: Kling returns; writer.write_bytes(actor_0096/...jpg) → [Errno 2]
T=47  Request B: Kling returns; writer.write_bytes(actor_0099/...jpg) → [Errno 2]
```

The reaper has no notion of "in-flight" — it deletes ANY actor folder without a jpg, treating sibling concurrent requests' fresh folders the same as orphaned folders left by killed batches.

## Fix

Add a mtime threshold to `_reap_incomplete_folders`. Folders younger than `_REAP_MIN_AGE_SECONDS = 300.0` (5 minutes) are skipped — that's safely past Kling's worst case (120s face wait + 120s body wait + assembly overhead), so a peer in-flight folder is never deleted. Genuinely orphaned folders from killed batches are still reaped on the next call after their mtime ages past the threshold.

Two changes to `libs/infrastructure/writers/actor__writer.py`:

1. New module-level constant `_REAP_MIN_AGE_SECONDS: float = 300.0` next to the other reaper / allocator constants.
2. Reaper loop guards each candidate with `if entry.stat().st_mtime > cutoff: continue` (where `cutoff = time.time() - _REAP_MIN_AGE_SECONDS`). OSError on `stat` also skips (defensive).

The keep-if-has-jpg check (from follow-ups 018 + 027 + 033) is preserved — folders with a jpg are kept regardless of age.

## Smoke proof

Three scenarios via a temp dir:
- Fresh folder (`mkdir` just now) → **NOT** reaped ✓ (was the bug)
- Stale folder (mtime back-dated past 300s) → reaped ✓ (genuine orphan cleanup still works)
- Fresh-or-stale folder with a jpg → NOT reaped ✓ (existing keep-if-has-jpg rule preserved)

Plus 18 tests pass / 5 pre-existing wukong fixture failures (zero regressions).

## Out of scope

- Adding a sentinel `in_progress` marker file (alternative architecture — a writer drops `.in_progress` after allocation, reaper skips folders with the marker, jpg-write removes the marker). The mtime-threshold approach is simpler and sufficient because the failure mode is timing-driven and the threshold is well above Kling's worst-case wait.
- Serializing concurrent generate calls (would defeat the worker-pool UX from follow-up 059).
- HTTP routes + JSON shapes (byte-identical).

## Acceptance trigger

- Re-running "generate 6 actors" through the worker-pool UI no longer produces `[Errno 2] No such file or directory` per-slot errors.
- Killed batches still get cleaned up on subsequent generate calls (after the mtime ages past 5 min).
- Pytest baseline preserved.
