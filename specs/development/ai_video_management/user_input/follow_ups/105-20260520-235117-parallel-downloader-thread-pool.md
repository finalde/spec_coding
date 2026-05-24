# Follow-up draft 105 — 2026-05-20

Switch `download_all` to a thread-pool parallel runner so multiple novels download simultaneously, while preserving every checkpoint (no re-downloads).

## Why

User: picked option 2 (parallel) + option 3 (keep current state) from the speedup menu. Translation: keep the existing `xianxia/fanren_xiuxian_zhuan/` 479-chapter checkpoint, but run multiple novels concurrently so total wall-clock drops from ~9h serial to ~2h parallel.

User explicitly accepted the trade-off of higher total request rate to sudugu.org (option 2 was annotated with "可能封 IP" risk).

## Design

### Thread pool of per-worker downloaders

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_all(self, on_progress=None, max_workers=5):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_to_spec = {pool.submit(self._download_in_isolated_worker, s, on_progress): s for s in CANONICAL_NOVELS}
        for f in as_completed(future_to_spec):
            try:
                results.append(f.result())
            except Exception as exc:
                spec = future_to_spec[f]
                results.append(NovelDownloadResult(slug=spec.slug, ..., errors=[str(exc)]))
    self._write_index_md(results)
    return results

def _download_in_isolated_worker(self, spec, on_progress):
    # Each worker owns its own httpx.Client + its own rate-limit clock,
    # so they don't serialize on a shared mutex.
    with NovelDownloader(novels_root=self._root, delay_seconds=self._delay,
                        max_retries=self._max_retries) as d:
        return d.download(spec.slug, on_progress=on_progress)
```

### Why per-worker `httpx.Client` (not shared)

The current `NovelDownloader` has a single `httpx.Client` + a single `_last_request_at` clock that gates every request. Sharing this across threads would force a 0.8 s serial gate even with N workers — defeating the point.

Per-worker clients mean each thread's rate limiter is independent: each thread does at most 1.25 req/s. With 5 workers that's a peak ~6.25 req/s aggregate to sudugu.org. Risk acknowledged: the user opted in.

### Why keep `max_workers=5` as default

- 1-2 workers: tiny speedup, not worth the complexity.
- 3-5 workers: ~3-5× wall-clock improvement, sudugu.org likely tolerates this for a few hours.
- 10+ workers: high block-IP risk + diminishing returns once per-worker delay dominates network latency.

5 is a reasonable middle. Can be tuned later via CLI flag if 429s show up.

### Resume contract preserved

`download(slug)` is unchanged — it uses `_ensure_index` + the chapter loop that reads/writes `_meta.json` atomically per chapter. Parallel workers each write only their own novel's meta file, so there's no shared-state contention (each `novels/{cat}/{slug}/` directory is owned by exactly one worker).

The current `xianxia/fanren_xiuxian_zhuan/` at chapter 479 will be picked up by whichever worker happens to claim it and resumed from chapter 480.

### `_write_index_md` runs once at the end

Previously called inside the serial loop after each novel finished. With parallel completions arriving on different threads, the safer path is to write `_index.md` once after `as_completed` drains. (The user reads the sidebar — which auto-builds from `_meta.json` files via `TreeReader` — not `_index.md`, so the lag is harmless.)

### `download` method unchanged

The public single-novel `NovelCommand.download(slug)` path stays as it was — synchronous, single client, single rate-limit clock. Parallel behavior only kicks in via `download_all`.

### Out of scope

- Per-source / per-IP global rate limit. The 0.8 s per-worker limit + httpx-level retry on 429 is the v1 throttling strategy. If sudugu.org rate-limits, the per-chapter retry+backoff in `_http_get` already handles it.
- Configurable `max_workers` via CLI flag. Default 5 hardcoded; can be parameterized if needed.
- Progress reporter changes. The existing `on_progress` callback prints lines like `[slug] idx/total`; with parallel workers these now interleave across slugs, which is acceptable (the line itself names the slug).

## Touch list

- **Modified**: `libs/infrastructure/writers/novel__writer.py` — `download_all` rewritten to use `ThreadPoolExecutor`; new `_download_in_isolated_worker(spec, on_progress)` helper that owns a fresh `NovelDownloader` per call.
- **Background job**: kill current downloader, restart; parallel mode resumes every novel from its existing checkpoint.
- **Audit**: changelog entry 105.
