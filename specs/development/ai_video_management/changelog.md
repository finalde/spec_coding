# Changelog — ai_video_management

Append-only follow-up audit log. Each entry records what the follow-up changed and which downstream artifacts were patched in the same turn.

## Follow-up 112 — 2026-05-24 10:04:44
Source: user_input/follow_ups/112-20260524-100444-kling-actor-429-retry.md
Summary: 修 actor 生成时 Kling `/v1/images/generations` POST 返回 429 Too Many Requests 导致 batch 内整批 slot 阵亡的 bug。Root cause: follow-up 027 引入的 9-worker frontend pool × `generate_batch(count=1)` 内的 face+body 双 Kling submit = 瞬时 18 并发请求超过 Kling 商业端 per-account QPS cap；`KlingProvider._submit` 单次 `raise_for_status()` 抛 `httpx.HTTPStatusError` 冒泡到 `generate_batch except Exception` 写 `http_failed`。Fix 复用 follow-up 018 (pollinations rate-limit retry) 设计：3 retries + [3s, 6s, 12s] backoff + 429 时尊重 `Retry-After`（cap 60s）+ httpx 超时同 backoff 重试 + 其他 HTTP 错误立即 propagate。新增 `_KLING_RETRY_BACKOFFS` / `_KLING_RETRY_AFTER_CAP` 常量 + `_kling_retry_sleep_seconds` / `_kling_call_with_retry` helper，`_submit` 包 POST、`_poll` 包 GET。前端 9-worker 并发保留（018 同款判断：retry-on-server 优于牺牲吞吐）。

Auto-updated:
- `projects/ai_video_management/libs/infrastructure/writers/actor__writer.py` — imports 新增 `from collections.abc import Callable`；常量区新增 `_KLING_RETRY_BACKOFFS = (3.0, 6.0, 12.0)` + `_KLING_RETRY_AFTER_CAP = 60.0`；模块函数新增 `_kling_retry_sleep_seconds(attempt, retry_after_header)` + `_kling_call_with_retry(fn)`；`KlingProvider._submit` 把 `client.post(...) + raise_for_status()` 包成 `_do_post` 闭包并改走 `_kling_call_with_retry(_do_post)`；`KlingProvider._poll` 同款包成 `_do_get` 闭包 + `_kling_call_with_retry(_do_get)`。
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 2026-05-24 09:58:34 → 2026-05-24 10:04:44；header 摘要描述 429 cascade root cause + retry helper 设计 + smoke 5/5 PASS + 下游 no-change verified 三处 + open question (CONCURRENCY 调节 vs token-bucket)。

No conflicts found in: `libs/application/commands/actor__command.py` (接口契约不变), `apps/api/routes/actor__route.py` (route handler 透传 `GenerateResult.to_payload()`，无 Kling 知识), `apps/ui/src/components/ActorPoolGenerator.tsx` (9-worker pool 保留), `specs/development/ai_video_management/validation/security.md` ("no rate limit" carve-out 是 spec 侧 PUT/regen，本 follow-up 在 Kling 外部依赖边界加 retry 不冲突), `specs/development/ai_video_management/final_specs/spec.md` (Kling render-API 集成在 "Out of scope" 区域，不约束重试行为).

Smoke (ad-hoc local script, .venv/Scripts/python.exe):
- 三档 backoff 默认 `[3.0, 6.0, 12.0]` ✓
- `Retry-After` 数字 `4` → 4.0 ✓；低于 base 的 `1` 回退到 base ✓；非数字 `abc` 回退到 base ✓；负数 `-2` 回退到 base ✓；`120` 被 cap 到 60.0 ✓
- retry-on-429（2 次 429 + 1 次成功，3 attempt）✓
- exhaustion（连续 4 个 429，attempt #4 后 raise）✓
- 500 立即 propagate（1 attempt）✓
- timeout-retry（1 次 ReadTimeout + 1 次成功，2 attempt）✓

Severity: Medium — bug fix for user-facing batch-actor-gen failure mode; backward compatible (无 schema / 无 interface 变化；retry 透明吸收 transient 429 + timeout)。

## Follow-up 110 — 2026-05-23 12:37:01
Source: user_input/follow_ups/110-20260523-123701-add-five-popular-xianxia.md
Summary: 用户要求 (a) resume in-progress novel downloads (恢复 `guangyin_zhiwai` 240/1383 起继续) + workers=2; (b) Assistant 从 sudugu xianxia 排行榜挑 5 部 ongoing/complete 高人气作品补进 catalog。Background task `bxxhdmqun` 已用 `--workers 2` 启动，新增 5 个 entries 后下次启动会自动跑这 5 部。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated bumped to 2026-05-23 12:37:01；header 摘要描述 5 部新 entries + sudugu IDs + 不强行 restart 当前 background task 的理由。
- `projects/ai_video_management/libs/domain/value_objects/novel__valueobject.py` — 仙侠 section 末尾追加 5 个 `NovelSpec`（`jianlai` 287 / `xian_ni` 410 / `dafeng_dagengren` 405 / `chixin_xuntian` 56 / `dadao_zhengfeng` 435）。注释 `# 仙侠 — added in follow-up 110 (popular ongoing/complete picks from sudugu xianxia ranking)` 与 follow-up 103 的 expanded comment 风格一致。所有 entries 用单一 `_sudugu(...)` source（ttkan 备源 deferred）。
- (Zero changes to `apps/cli/novel_download.py` / `libs/infrastructure/writers/novel__writer.py` — `download_all` 已 iterates `CANONICAL_NOVELS`，新 entries 透传)。

Runtime state:
- Background task `bxxhdmqun` (workers=2) 在恢复 `guangyin_zhiwai` 后继续；新增 5 部不会在当前 task 内被发现（task 启动时已 capture 旧 tuple）。
- 用户下次手动跑 `python -m apps.cli.novel_download --workers 2` 即拉新 5 部下载（resumable 状态机 + 现有 done chapters skip）。
- No forced restart — 当前 task 正常跑完 `guangyin_zhiwai` + 其余 in-progress 仙侠 novels 是较优策略。

Deferred (not in this follow-up):
- ttkan 备源（参考 follow-up 107 multi-source pattern；若 sudugu 抓不下来时再补）。
- 玄幻 / 都市 / 历史 / 科幻 / 言情 catalog 扩充。
- workers 默认值调整（保持 follow-up 106 的 serial-by-default + opt-in `--workers N`）。

Severity: Low — additive catalog entries, no breaking changes, no schema changes.

## Follow-up 109 — 2026-05-21 20:31:17
Source: user_input/follow_ups/109-20260521-203117-cn-ttkan-jitter-end-of-chapter.md

Trigger: user asked whether `xueant-t/novel` (Java fork of `freeok/so-novel`) could help speed up novel downloads. Investigation cloned the upstream `freeok/so-novel` repo, read `bundle/rules/{main,rate-limit,no-search,proxy-required,cloudflare}.json` + `rule-template.json5` + the Java package layout under `src/main/java/com/pcdd/sonovel/`. Reported back with a 3-tier extract plan (quick wins / declarative rule-engine refactor / 3rd-4th fallback hosts). User picked path 1 only — three trivial wins, no architectural commitment. Architectural refactor and new hosts deferred until a 3rd source is actually needed.

### What was taken from so-novel

- **`cn.` subdomain for ttkan** — `bundle/rules/no-search.json` targets `cn.ttkan.co` which serves Simplified Chinese. Follow-up 107 added `ttkan.co` via the `www.` subdomain which serves Traditional Chinese (acknowledged in 107's "Caveats" as a deferred opencc problem). Switching the subdomain dissolves that caveat at the source.
- **`(本章完)` filter regex** — every site rule in `bundle/rules/*.json` lists `chapter.filterTxt: "\\(本章完\\)"`. It's a near-universal Chinese-web-novel end-of-chapter boilerplate marker; my `_extract_paragraphs` was preserving it in body files.
- **1.0–2.0 s random jitter delay** — so-novel's `crawl.minInterval`/`maxInterval` for both sudugu + ttkan converged on `1000`/`2000` ms with random uniform jitter per request. Anti-bot fingerprinting cares about request *cadence*, not just average rate — jitter at the same average is harder to fingerprint than a fixed 0.8 s.

### What was deliberately NOT taken

- **Declarative `SourceRule` dataclass + bs4/selectolax CSS-selector engine.** so-novel's `rule-template.json5` schema (CSS selectors, XPath, `crawl.concurrency`/`minInterval`/`maxInterval`, `chapter.filterTxt`/`filterTag`, `toc`/`chapter.pagination`/`nextPage`) is genuinely better than my hardcoded `_TTKAN_*_RE` + `_INDEX_LIST_RE` regex approach. Held until a 3rd source actually appears.
- **`xbiqugu.la` / `22biqu.com` / `shuhaige.net` as 3rd/4th fallback hosts.** Each would need either new `_fetch_index_via_*` + `_fetch_chapter_via_*` pairs (deepens the per-host pattern) or the refactor above. Bundled with the refactor.
- **`@js:` post-processing rules.** ~3 sites in `main.json` embed JavaScript snippets (base64 decode, paragraph reordering). Python equivalent is mini-racer / pyjsdom — heavy for narrow use.
- **Cloudflare and proxy-required tier hosts** (`69shuba.com`, `quanben5.com`, `xhytd.com`, etc.). Would need `curl_cffi` for TLS fingerprint spoofing or actual proxies. Not pursued.
- **The Legado scaffolding from follow-up 108** (`libs/infrastructure/readers/legado__reader.py` + `sources/ttkan_co.json`). Stays unwired and untouched — 109 is a different direction (surgical patches to existing helpers, not a rule-engine swap).
- **opencc 繁→简 conversion** of pre-migration Traditional Chinese body fragments. Still deferred per 107.

### Code changes

1. **`libs/domain/value_objects/novel__valueobject.py`** — `_ttkan(source_slug)` factory returns `NovelSource("cn.ttkan.co", source_slug)` (was `"ttkan.co"`). Single-line change. All 5 ttkan-bearing entries (`fanren_xiuxian_zhuan`, `guangyin_zhiwai`, `wanmei_shijie`, `ze_tian_ji`, `lingjing_xingzhe`) flip together.

2. **`libs/infrastructure/writers/novel__writer.py`**:
   - Module docstring rate-limit line `0.8 s` → `1.0–2.0 s random jitter (follow-up 109)`.
   - Added `import random`.
   - Constant `_INTER_REQUEST_DELAY = 0.8` replaced with `_INTER_REQUEST_DELAY_MIN = 1.0` + `_INTER_REQUEST_DELAY_MAX = 2.0`.
   - New module-level `_END_OF_CHAPTER_MARKER_RE = re.compile(r"\(本章完\)")`.
   - `NovelDownloader.__init__` signature: `delay_seconds: float` → `delay_min_seconds: float, delay_max_seconds: float`. Stored as `self._delay_min` / `self._delay_max`.
   - `_http_get` computes `required = random.uniform(self._delay_min, self._delay_max)` and sleeps for `required - elapsed` instead of the old fixed `self._delay - elapsed`.
   - `_download_in_isolated_worker` plumbs both new delays to per-worker `NovelDownloader` instances.
   - `_extract_paragraphs` strips the end-of-chapter marker after entity decode and before the empty-paragraph drop, so a paragraph that contained only the marker is removed entirely.
   - `_fetch_index_via_ttkan` URL templates drop the `www.` prefix: `https://www.{src.host}/...` → `https://{src.host}/...`. `src.host` now carries `cn.` already.
   - `_fetch_chapter_index_for_source` host comparison `if src.host == "ttkan.co"` → `if src.host == "cn.ttkan.co"`.
   - `_fetch_chapter_full` host comparison `if host == "ttkan.co"` → `if host == "cn.ttkan.co"`. `_host_of_url` regex `https?://(?:www\.)?([^/]+)` does NOT strip `cn.` (only `www.`), so chapter URLs of shape `https://cn.ttkan.co/...` parse to host `cn.ttkan.co` correctly.
   - `download_all` docstring updated to reflect the new per-worker rate (~3.3 req/s aggregate at 5 workers, was ~6 req/s).
   - `_download_in_isolated_worker` docstring expanded with the rate-justification line.

3. **CLI (`apps/cli/novel_download.py`)** — no change. Uses default delays.

4. **Application layer / frontend / API routes / container** — no change. `NovelSource` and `NovelSpec` schemas unchanged; compat properties `source_host`/`source_id` still return `sources[0].host`/`source_id` byte-identical to before from the caller's perspective.

### Migration semantics on next launch

For the 5 ttkan-bearing novels, existing `_meta.json` files carry `active_source_host="ttkan.co"`. New spec exposes `cn.ttkan.co` → `_ensure_index` evaluates `meta.active_source_host != active.host` to True → re-fetches ttkan index from the new `cn.` subdomain → builds new chapter list with `cn.ttkan.co` URLs → for each new chapter looks up the old chapter at the same `idx` and preserves `done` / `hash` / `error` (last only if `not prev.done`). Already-downloaded Traditional Chinese chapter content in the body `.md` files stays verbatim — only un-done chapters get the Simplified URL going forward, so the body file is mixed-script at the migration boundary. Sudugu-only novels (`active_source_host="sudugu.org"`) are unaffected since host is unchanged.

### Verification

- **Static / import smoke (5/5 PASS)**: 5 ttkan sources resolve to `cn.ttkan.co`; `_END_OF_CHAPTER_MARKER_RE.sub('', 'final.(本章完)').strip() == 'final.'`; constants `_INTER_REQUEST_DELAY_MIN=1.0` / `_MAX=2.0`; `NovelDownloader(delay_min_seconds=0.5, delay_max_seconds=1.5)` constructs and stores both; `find_novel('fanren_xiuxian_zhuan').sources` returns `[NovelSource('sudugu.org', '128'), NovelSource('cn.ttkan.co', 'fanrenxiuxianchuan-wangyu')]` in order.
- **Live HTTP probe** against `https://cn.ttkan.co/novel/chapters/fanrenxiuxianchuan-wangyu`: HTTP 200; final URL is `cn.ttkan.co` (no redirect to `www.`); first paragraph of chapter 1 reads "二愣子睁大着双眼，直直望着茅草和烂泥糊成的黑屋顶..." (fully Simplified — `着` not `著`, `烂` not `爛`, `仓` not `倉`, etc.); 0/8 Traditional char hits, 5/8 Simplified char hits on a sample of common 简↔繁 pairs (`这国时间个学发说` vs `這國時間個學發說`); 2453 chapter links parse with existing `_TTKAN_CHAPTER_LINK_RE` (same count as follow-up 107's `www.ttkan.co` index — index shape byte-identical). First chapter link `/novel/pagea/fanrenxiuxianchuan-wangyu_1.html` confirms the chapter URL pattern is unchanged.
- **No filesystem mutation this turn**: existing `_meta.json` files untouched. Migration triggers automatically on the next `python -m apps.cli.novel_download` invocation.

### Auto-updated

- `user_input/revised_prompt.md` — `**Last regenerated:**` header bumped from 108 to 109; the 108 entry demoted to `**Prior bump:**` chain.
- `changelog.md` — this entry.

### No conflicts found in

- `interview/qa.md`, `findings/*.md`, `final_specs/spec.md`, `validation/*.md` — none reference `ttkan.co`, `0.8 s` delay, or specific `(本章完)` boilerplate handling.

## Follow-up 107 — 2026-05-21 00:11:30
Source: user_input/follow_ups/107-20260521-001130-multi-source-fallback-ttkan-co.md

Trigger: user picked "1 + 3" from the recovery menu — wait for the sudugu.org IP block to expire AND add multi-source fallback. The block in follow-up 106 exposed a structural weakness (single source per novel); multi-source is the architectural fix.

### Probing summary

9 candidate alt-sites tried; one verified usable: **ttkan.co**. Others returned 403 / connection-reset / DNS-fail (69shuba, biquge.tw, ddyueshu, biquge88, biqugesf, biqu5200, biquge.info, biquge365, bqg5). ttkan.co confirmed:
- Has 5 of the popular novels via slug guessing (fanren_xiuxian_zhuan, guangyin_zhiwai, wanmei_shijie, ze_tian_ji, lingjing_xingzhe).
- Chapter index served on a single page (no pagination — simpler than sudugu).
- Chapter body in `<div class="content">` with `<p>` paragraphs — same shape as sudugu.
- Content is Traditional Chinese (sudugu was Simplified). Body files will end up mixed for novels that source-switch; user can run opencc later if uniform script is needed.

### Design

- New `NovelSource(host, source_id)` frozen dataclass in domain VO.
- `NovelSpec.sources: tuple[NovelSource, ...]` replaces single `source_host` + `source_id` fields. Compat properties (`spec.source_host`, `spec.source_id`) return `sources[0]` so all callers (queries, mappers, DTOs, frontend) stay byte-identical.
- `NovelMeta` gains `active_source_host` + `active_source_id` fields. Empty until first successful index fetch. JSON `from_json` falls back to `source_host` / `source_id` for legacy meta files (zero migration noise).
- 5 novels updated to multi-source: `fanren_xiuxian_zhuan` (sudugu→ttkan), `guangyin_zhiwai`, `wanmei_shijie`, `ze_tian_ji`, `lingjing_xingzhe`. The other 34 stay sudugu-only — extending the manifest requires manual ttkan-slug discovery per novel.

### Infrastructure dispatch

Writer rewritten with per-host scrapers:
- `_fetch_index_via_sudugu(src)` — paginated index (existing logic, factored out).
- `_fetch_index_via_ttkan(src)` — single-page index, anchor pattern `<a href="/novel/pagea/{slug}_{N}.html">第N章 标题</a>`.
- `_fetch_chapter_via_sudugu(chapter, host)` — chapter with `下一页` pagination (existing logic).
- `_fetch_chapter_via_ttkan(chapter)` — single chapter page, content in `<div class="content">`.
- `_fetch_chapter_index(spec)` iterates `spec.sources`, returns first success; dispatcher uses `src.host` to pick scraper.
- `_fetch_chapter_full(spec, chapter)` dispatches on the URL's host (parsed via static `_host_of_url`), so chapter URLs from different sources route to the right fetcher even if a meta carries mixed URLs (it shouldn't normally — `_ensure_index` rewrites all chapter URLs on source switch).

### Source switch — done flags preserved by idx

When `_ensure_index` detects `meta.active_source_host != active.host` (e.g. existing meta says sudugu but sudugu is now blocked, falling through to ttkan), it:
1. Indexes the *new* active source.
2. Builds a new chapter list with the new source's URLs.
3. For each new chapter, looks up the old chapter at the same `idx` and copies `done` / `hash` / `error` (the last only if `not prev.done`).
4. Replaces `meta.chapters` and writes meta.

Verified live on a copy of `xianxia/fanren_xiuxian_zhuan/_meta.json` (501 chapters done from sudugu): post-migration meta has 2453 chapters (ttkan count, vs sudugu's 2512), `done count == 501` preserved, all URLs rewritten to ttkan format, `active_source` populated. ✓

### Caveats acknowledged

- Chapter count differs between sources (sudugu 2512 vs ttkan 2453 for fanren). After source switch, the last ~59 sudugu-only chapters become unreachable. Acceptable: the bulk of the novel transfers cleanly. User can manually re-add them later if sudugu unblocks.
- Traditional vs Simplified Chinese: source-switched body files will have mixed scripts at the boundary. Out of scope for this turn (opencc conversion deferred).
- Auto-detect-and-switch mid-novel still not implemented — switch only happens at `_ensure_index` time (i.e. next launch). Acceptable: chapter-fetch failures already mark `error` in meta and stop further attempts for that chapter; next launch re-indexes and probably picks a working source.

### Changes

1. **Modified Python files (2)**:
   - `libs/domain/value_objects/novel__valueobject.py` — `NovelSource` dataclass; `NovelSpec.sources` schema + compat properties; manifest updated (5 novels gain ttkan as 2nd source).
   - `libs/infrastructure/writers/novel__writer.py` — `NovelMeta` gains `active_source_*` fields; new per-host fetcher methods (`_fetch_index_via_*`, `_fetch_chapter_via_*`); `_ensure_index` detects source change + migrates chapter URLs preserving `done`-by-idx; new patterns `_TTKAN_CHAPTER_LINK_RE` + `_TTKAN_CONTENT_BLOCK_RE`; new dispatcher `_host_of_url`.
2. **No code change**: application layer (queries / mappers / DTOs), frontend, API routes, container — all unchanged. The new fields exist behind the existing surface.
3. **No filesystem change** this turn: existing `xianxia/fanren_xiuxian_zhuan/_meta.json` is untouched; the source migration will trigger automatically the next time the downloader launches and finds sudugu still blocked.

### Verification

- `pytest tests/test_boot_smoke.py tests/test_tree_walker_consumer_walk.py::test_tree_sections_order tests/test_tree_walker_consumer_walk.py::test_novels_section_walks_repo_novels_dir tests/test_api_security_three_shapes.py::test_get_tree_unguarded` → 10/10 passing ✓
- `_fetch_chapter_index(spec)` on fanren_xiuxian_zhuan: sudugu fails (302→google→parse fail), falls through to ttkan, returns 2453 chapters, active=`ttkan.co/fanrenxiuxianchuan-wangyu` ✓
- `_fetch_chapter_full` on chapter 1 via ttkan: 350-char body extracted in Traditional Chinese ✓
- Source-switch migration on copy of real fanren meta: 501 done flags preserved, URLs rewritten to ttkan, total chapters 2512→2453, active_source populated ✓

### Scope deferred

- Mid-novel source switch (currently only at `_ensure_index` time).
- Search-driven ttkan slug discovery for the other 34 novels.
- Multi-site fallback beyond ttkan (other candidates currently hostile/down).
- opencc conversion for source-switched novels.
- 302→google.com circuit-breaker in `_http_get` (better error reporting, not a correctness fix).

## Follow-up 106 — 2026-05-20 23:57:18
Source: user_input/follow_ups/106-20260520-235718-sudugu-ip-block-revert-to-serial-default.md

Trigger: within ~10 s of launching the 5-worker parallel downloader from follow-up 105, every chapter request started returning **HTTP 302 → https://www.google.com/**. Verified the block with 3 different User-Agents (Chrome / Firefox / curl) from the same client IP — all 3 got the same 302. Sudugu.org's edge fired a per-IP anti-bot rule.

User had explicitly accepted this risk in 105 ("可能封 IP" was in the choice prompt); this follow-up captures the consequence + the immediate mitigation.

### Changes

1. **Modified Python file**:
   - `apps/cli/novel_download.py` — default `workers` reverted from 5 → 1. Three lines: `Usage:` docstring, the comment line above the default, the `workers = N` initializer. Parallel-mode code path (`download_all`'s ThreadPoolExecutor body + `_download_in_isolated_worker` from 105) stays intact; user can opt back into parallel via `--workers 3` once the block clears.
2. **No filesystem cleanup** — every chapter the parallel workers attempted is `done=False` with an `error` field set; the resume loop picks them up automatically on next launch. `xianxia/fanren_xiuxian_zhuan/` checkpoint preserved at 501.
3. **Background job**: parallel downloader killed; no relaunch this turn (waiting for the block to clear).

### Verification

- 3 separate UA probes (Chrome 120, Firefox 120, curl/8) to `sudugu.org/128/` and `sudugu.org/128/10643.html` — all 4 return 302 to google.com. Block is per-IP, not per-UA.
- `apps/cli/novel_download.py` `--workers` flag still parses; `--workers 3` (or higher) still wires into `download_all(max_workers=3)`. Parallel path is dormant, not deleted.

### What surfaced as a missing defense

The misleading error chain was: 302 → google.com → httpx followed redirect → 200 with google's HTML → `<div class="con">` regex missed → `DownloadFailed: content block not found at <chapter URL>`. The chapter URL in the error is the *original* requested URL, not the *final* response URL, which made the message confusing. Future improvement (deferred): `_http_get` should check `response.url.host == source_host` and raise a `SourceBlocked` error early instead of letting parsing fail downstream.

### User-facing trade-offs

- Sidebar `Novels` section will stay empty for longer than originally hoped — the 105 parallel-run wasted ~10 s of wall-clock and traded that for a multi-minute-to-multi-hour IP block.
- Once the block lifts (likely 15-60 min, possibly longer; CDN edge rules typically have short TTLs), `python -m apps.cli.novel_download` will resume `fanren_xiuxian_zhuan` from chapter 502, single-threaded, polite-rate.

### Scope deferred

- 302-detect-and-halt in `_http_get` (better error reporting for the next time we get blocked).
- Multi-source fallback (route around a blocked source).
- VPN/proxy integration.
- Auto-back-off across CLI launches (detect the block, sleep, retry).

## Follow-up 105 — 2026-05-20 23:51:17
Source: user_input/follow_ups/105-20260520-235117-parallel-downloader-thread-pool.md

Trigger: user picked "2 + 3" from a speedup menu: option 2 = parallel downloads (accepting higher request rate to sudugu.org), option 3 = keep existing fanren progress alive. After follow-up 104's strict-serial design, the wall-clock estimate for the 39-novel manifest was ~9 hours; the user wanted faster.

### Design

- `download_all` switched from serial loop to `ThreadPoolExecutor(max_workers=5)`. Each future runs `_download_in_isolated_worker(spec)` which creates a **fresh `NovelDownloader` per call** with its own `httpx.Client` + its own `_last_request_at` clock. This is critical: sharing the existing instance would have serialized workers on the shared rate-limit mutex, defeating the parallelism.
- Per-worker 0.8 s polite delay still applies, so each individual stream is polite; but with 5 workers the aggregate request rate to sudugu.org peaks around ~6 req/s. User explicitly accepted this risk.
- `download(slug)` (the single-novel path used by `NovelCommand.download(slug)`) is unchanged — still synchronous, still one client, still one rate clock. Parallel behavior only kicks in via `download_all`.
- Results are sorted back into canonical (`CANONICAL_NOVELS`) order before `_write_index_md` writes the markdown index, so `_index.md` reads predictably regardless of completion-order interleaving.
- Dead `_stub_results_for_remaining` helper from follow-up 104 removed (no longer needed — `_write_index_md` runs once at the end of `download_all`).
- CLI gains an optional `--workers N` flag (default 5) so the user can tune up/down without code edits.

### Resume contract preserved

Each `novels/{cat}/{slug}/` directory is owned by exactly one worker for the duration of that novel's download — no two threads touch the same `_meta.json`. The `_load_or_init_meta` → `_ensure_index` → per-chapter `_write_meta` chain stays unchanged. `xianxia/fanren_xiuxian_zhuan/` at checkpoint 501 was picked up by the parallel runner and resumed from chapter 502.

### Changes

1. **Modified Python files (2)**:
   - `libs/infrastructure/writers/novel__writer.py`:
     - Imports added: `ThreadPoolExecutor`, `as_completed` (from `concurrent.futures`), `Lock` (from `threading`).
     - `download_all` body replaced with thread-pool runner; new `_download_in_isolated_worker(spec, on_progress)` helper; new `_reorder_to_canonical(results)` helper.
     - `_stub_results_for_remaining` removed (dead code from follow-up 104).
   - `apps/cli/novel_download.py`:
     - `--workers N` / `--workers=N` flag parsing.
     - Banner now reads `downloading all canonical novels (parallel, workers={n})`.
2. **Background job**: serial downloader killed at fanren=501/2512; parallel downloader relaunched with 5 workers. Verified: 5 novels in flight (fanren_xiuxian_zhuan, guangyin_zhiwai, jie_jian, meiqian_xiu_shenme_xian, xuanjian_xianzu) — all xianxia, all resuming from `_meta.json` checkpoints.

### Verification

- `pytest tests/test_boot_smoke.py tests/test_tree_walker_consumer_walk.py::test_tree_sections_order tests/test_tree_walker_consumer_walk.py::test_novels_section_walks_repo_novels_dir tests/test_api_security_three_shapes.py::test_get_tree_unguarded` → 10/10 passing ✓
- `inspect.signature(NovelDownloader.download_all)` returns `(self, on_progress, max_workers)` ✓
- 5 worker folders observed on disk within ~8 s of launch — confirms concurrent activity.
- Fanren resume monitor armed; will fire when chapter 502 appears in log.

### Trade-offs (the user explicitly accepted)

- Aggregate request rate ~6 req/s → some risk that sudugu.org rate-limits or temp-blocks the IP. Mitigation: existing exponential backoff in `_http_get` (retries on 429 / 5xx, up to 3 attempts with 1.5^attempt backoff).
- CPU/memory: 5 simultaneous httpx clients = 5 TCP connections + 5 SSL contexts. Negligible on a desktop.
- Order of completion is non-deterministic; the sidebar's `complete-only` filter (from 104) hides this — novels just appear in arrival order as they finish.

### Scope deferred

- Cross-source / per-IP global rate limit (would force serial across workers).
- Adaptive worker count (e.g. drop to 2 if 429s arrive).
- async-IO refactor (would let us reach the polite-rate ceiling without OS threads, but ROI low at this scale).

## Follow-up 104 — 2026-05-20 23:34:36
Source: user_input/follow_ups/104-20260520-233436-novels-serial-mode-complete-only-sidebar.md

Trigger: user — "每一部小説為社麽只有第一章，我要完整的小説所有章節，如果只有一張，那就直接刪掉，我只要有完整章節的小説".

User correcting follow-up 103's round-robin design: they want each novel fully downloaded (every chapter `done=True`) before any other novel starts, and the sidebar should surface only completed novels. Round-robin's 1-chapter stubs are visual noise to be deleted.

Asked clarifying question about `xianxia/fanren_xiuxian_zhuan/`'s 348-chapter checkpoint; user opted to preserve + continue it.

### Three changes

1. **`download_all` reverted to strict serial**:
   - Phase 1 / Phase 2 two-phase shape from 103 removed.
   - New body: `for spec in CANONICAL_NOVELS: download(spec.slug)`. Each novel completes before the next starts.
   - `download(slug)`, `_ensure_index`, `_download_one_chapter`, `_NovelState` from 103 all kept — only `download_all`'s top-level loop changed.
   - Added `_stub_results_for_remaining(last_done)` helper so `_index.md` continues to list every canonical novel between iterations (with 0/0 placeholders for not-yet-touched ones).

2. **Tree filter — complete-only**:
   - `libs/infrastructure/readers/tree__reader.py::_novels_section` now reads each `novels/{cat}/{slug}/_meta.json` and skips folders where `complete != True`.
   - New helper `_novel_is_complete(novel_dir)` does the JSON read defensively (returns False on missing/corrupt).
   - Category folders with zero complete children are also hidden (handled by existing "if not novel_nodes: continue" guard).
   - Net effect: sidebar `Novels` section is empty until a novel actually finishes; in-progress novels stay on disk for resume but invisible.

3. **One-time cleanup — delete round-robin stubs**:
   - 38 novel folders deleted (all the 5-7 chapter stubs Phase 2 of 103 had produced before the user redirected).
   - Preserved per user clarification: `xianxia/fanren_xiuxian_zhuan/` at 355/2512 chapters.
   - Empty category folders (`dushi/`, `kehuan/`, `lishi/`, `xuanhuan/`, `yanqing/`) also removed; only `xianxia/` remains.

### Verification

- `pytest tests/test_boot_smoke.py tests/test_tree_walker_consumer_walk.py::test_tree_sections_order tests/test_tree_walker_consumer_walk.py::test_novels_section_walks_repo_novels_dir tests/test_api_security_three_shapes.py::test_get_tree_unguarded` → 10/10 passing ✓
- `GET /api/tree`: `Novels` children count = 0 (fanren incomplete, filter active) ✓.
- Downloader relaunched; `xianxia/fanren_xiuxian_zhuan/_meta.json` re-loaded at chapter 355, resumed serially from chapter 356.
- Background monitor armed to fire on first "fanren_xiuxian_zhuan] 356" log line; confirms serial resume.

### Changes

1. **Modified Python files (2)**:
   - `libs/infrastructure/writers/novel__writer.py` — `download_all` body replaced with serial loop + `_stub_results_for_remaining` helper.
   - `libs/infrastructure/readers/tree__reader.py` — `_novel_is_complete` predicate, filter applied inside `_novels_section`, `json` import added.
2. **Filesystem cleanup**:
   - Deleted 38 novel folders across 5 categories (all with `chapters_done <= 7 AND complete == False`).
   - Removed 5 now-empty category folders.
   - Preserved: `novels/xianxia/fanren_xiuxian_zhuan/` (355 chapters).
3. **Background job**: serial downloader running; will complete `fanren_xiuxian_zhuan` (~30 min for remaining 2157 chapters at 0.8 s/req), then proceed to `guangyin_zhiwai`, then through the rest of `CANONICAL_NOVELS` in order. Each novel pops into the sidebar at the moment its `complete: true` flips.

### Trade-offs the user accepted

- Empty `Novels` section in the sidebar until the first novel finishes (~30 minutes). Explicitly chosen via "我只要有完整章節的小説".
- Deep-narrow visibility (one fully-readable novel at a time) instead of broad-shallow (39 partial novels). Aligned with the user's reading-focused intent.
- The downloader sequence is now strict-fixed in `CANONICAL_NOVELS` order; no priority queue. Manifest already puts all 21 xianxia entries first, so 仙侠 will be fully completed before 玄幻 / 都市 / 历史 / 科幻 / 言情 start.

### Scope deferred

- Visible "currently downloading" indicator (e.g. progress badge above the empty Novels section). Could be added if the empty-sidebar UX feels disorienting.
- Tree filter relaxation (e.g. show novels where `complete OR chapters_done > 100`) — keeping the strict filter per literal user directive.
- Concurrent downloads — explicitly rejected; user wants serial.

## Follow-up 103 — 2026-05-20 22:44:06
Source: user_input/follow_ups/103-20260520-224406-more-xianxia-index-first-round-robin.md

Trigger: user — "I can only see 1 凡人修仙傳，please help me download more novels, 仙俠題材爲主".

The blocker was UX: 凡人修仙传's 2512 chapters at 0.8 s/req took ~33 min before the *second* novel even started under serial `download_all`. Only one xianxia novel appeared in the sidebar during that window despite 27 others being queued.

### Two changes

1. **Add 11 more xianxia novels** (manifest 28 → 39; xianxia 10 → 21). All probed against sudugu.org index pages; title + author + first-page chapter count verified before write. New entries: 苟在妖武乱世修仙 / 从箭术开始修行 / 诸天道祖，从遮天开始 / 苟在修仙界吞噬成圣 / 长生修仙：从薅妖兽天赋开始 / 长生：筑基成功后，外挂才开启 / 西游：从拜师太乙救苦天尊开始 / 泼刀行 / 戏神！ / 青葫剑仙 / 从送子鲤鱼到天庭仙官. These are sudugu.org's xianxia category page-1 entries not already in the manifest.

2. **`download_all` refactored to index-first + round-robin**:
   - Phase 1 (index pass): for every spec, fetch chapter index, write `_meta.json` + body header. All 39 novel folders appear within ~1 min of launch (single-threaded, 0.8 s polite rate).
   - Phase 2 (round-robin chapter pass): cycle through every novel that still has undone chapters, downloading one chapter per cycle. Broad-shallow visible progress beats deep-narrow invisible progress.
   - Rate-limit stays global (single `httpx.Client`, single `_last_request_at`), so the source sees the same 0.8 s/req pace it saw before — not 39× polite-rate.
   - Resume contract preserved: `_meta.json[chapters][i].done` is the only checkpoint. Re-running picks up exactly where it left off in either phase. xianxia/fanren_xiuxian_zhuan/'s 348-chapter checkpoint at restart time was honored; download resumed from chapter 349.

### Code shape

- New `_NovelState` dataclass for `(spec, meta, meta_path, body_path)` — keeps the round-robin loop one-line per iteration.
- New `_ensure_index(spec)` helper extracted from the head of the old `download(slug)`.
- New `_download_one_chapter(state, chapter, on_progress)` helper extracted from the body of the old chapter loop.
- `download(slug)` rewritten on top of the new helpers — public signature + semantics unchanged.
- `download_all` body completely replaced (no surgical edits) — clean two-phase shape.

### Changes

1. **Modified Python files (2)**:
   - `libs/domain/value_objects/novel__valueobject.py` — 11 new xianxia entries appended to `CANONICAL_NOVELS`.
   - `libs/infrastructure/writers/novel__writer.py` — `download_all` two-phase rewrite + helpers + `_NovelState` dataclass.
2. **Background job**: downloader killed at xianxia/fanren_xiuxian_zhuan 348/2512, refactor applied, downloader relaunched. Resume confirmed.

### Verification

- `pytest tests/test_boot_smoke.py tests/test_tree_walker_consumer_walk.py::test_tree_sections_order tests/test_tree_walker_consumer_walk.py::test_novels_section_walks_repo_novels_dir tests/test_api_security_three_shapes.py::test_get_tree_unguarded` → 10/10 passing ✓
- Index pass: 10 novels indexed within ~30 s of restart (background monitor confirmed); 39 expected once Phase 1 completes.
- Manifest count + categories: `len(CANONICAL_NOVELS) == 39`, xianxia count 21, all 6 categories represented.

### Scope deferred

- Parallel/concurrent HTTP — single-threaded round-robin meets the visibility goal; concurrent would need per-source rate-limit bookkeeping.
- Cross-category priority logic — manifest order already puts all 21 xianxia entries first, so they naturally enter Phase 2 ahead of other genres.
- Auto-discovery from sudugu.org rankings — manifest stays hand-curated.

## Follow-up 102 — 2026-05-20 21:56:38
Source: user_input/follow_ups/102-20260520-215638-novels-categorize-and-chinese-display.md

Trigger: user — "幫我下載更多的小説，在UI上名字要顯示中文，下載的小説要按題材分類， 比如仙俠類".

Three compounded asks: (1) expand the novel manifest, (2) display Chinese titles in the sidebar (not pinyin slugs), (3) group novels by genre under category folders.

### Design

- `NovelSpec` gains `category: str` (slug, ASCII) + `category_zh: str` (Chinese label). New helper `categories()` returns the unique (slug, zh) pairs in canonical order.
- `CANONICAL_NOVELS` expanded **10 → 28** entries spread across 6 categories:
  - **仙侠 (xianxia, 10)**: 凡人修仙传 / 光阴之外 / 玄鉴仙族 / 没钱修什么仙？ / 借剑 / 苟在两界修仙 / 我的模拟长生路 / 谁让他修仙的！ / 山河稷 / 阵问长生 (unchanged from 101).
  - **玄幻 (xuanhuan, 5)**: 诡秘之主 / 完美世界 / 择天记 / 普罗之主 / 青山.
  - **都市 (dushi, 4)**: 我不是戏神 / 深空彼岸 / 国民法医 / 捞尸人.
  - **历史 (lishi, 3)**: 状元郎 / 晋末长剑 / 明朝败家子.
  - **科幻 (kehuan, 4)**: 吞噬星空 / 黎明之剑 / 异度旅社 / 灵境行者.
  - **言情 (yanqing, 2)**: 我在惊悚游戏里封神 / 灯花笑.
  - All 18 new source_ids verified against sudugu.org index pages (title + author + first-page chapter count probed before the manifest was finalized).
- Filesystem layout migrated from flat `novels/{slug}/` to grouped `novels/{category}/{slug}/`. Existing in-flight `novels/fanren_xiuxian_zhuan/` (100 chapters done at time of migration) was moved to `novels/xianxia/fanren_xiuxian_zhuan/`; `_meta.json` got two new fields (`category`, `category_zh`) backfilled in place; download resumed from chapter 101 (confirmed in log) — zero re-downloads.
- `TreeReader._novels_section` rewritten as a category-aware two-level walker. Category folders + novel folders emit a `display_name` field carrying the Chinese label (仙侠 / 凡人修仙传); other intermediate folders + leaf files keep the existing shape.
- React Sidebar (`Sidebar.tsx`) renders `node.display_name || node.name` — one-token change in the label expression. Type added to `TreeNode` in `apps/ui/src/types.ts`.
- `NovelDownloader._write_index_md` rewritten to group rows by category — one `## {category_zh}` section per genre with a status table inside.
- `NovelQuery.list()` walks two levels (`novels/{cat}/{slug}/_meta.json`).
- DTOs (`NovelStatusQdto`, `NovelDownloadResultCdto`) + mapper + `NovelMeta` + `NovelDownloadResult` all gain `category` + `category_zh` fields. `NovelMeta.from_json` accepts legacy meta files without those fields (defaults to xianxia/仙侠).

### Changes

1. **Modified Python files (7)**:
   - `libs/domain/value_objects/novel__valueobject.py` — `NovelSpec` schema + manifest 10 → 28 + `categories()` helper.
   - `libs/infrastructure/writers/novel__writer.py` — `{category}/{slug}/` write path, category fields on `NovelMeta` + `NovelDownloadResult`, `_write_index_md` grouped by category.
   - `libs/application/dtos/novel__dto.py` — category fields on both Qdto + Cdto.
   - `libs/application/mappers/novel__mapper.py` — propagate category fields.
   - `libs/application/queries/novel__query.py` — two-level walk.
   - `libs/infrastructure/readers/tree__reader.py` — `_novels_section` rewritten with category awareness + `display_name` emission; imports `CANONICAL_NOVELS` + `categories()`.
2. **Modified frontend files (2)**:
   - `apps/ui/src/types.ts` — `display_name?: string` on `TreeNode`.
   - `apps/ui/src/components/Sidebar.tsx` — render `display_name || name`.
3. **Filesystem migration**: `novels/fanren_xiuxian_zhuan/` → `novels/xianxia/fanren_xiuxian_zhuan/`; `_meta.json` patched with `category` + `category_zh`.

### Verification

- `pytest tests/test_boot_smoke.py tests/test_tree_walker_consumer_walk.py::test_tree_sections_order tests/test_tree_walker_consumer_walk.py::test_novels_section_walks_repo_novels_dir tests/test_api_security_three_shapes.py::test_get_tree_unguarded` → 10/10 passing ✓
- `GET /api/tree` `children[name=="Novels"]` now returns `[{name: "xianxia", display_name: "仙侠", type: "directory", children: [{name: "fanren_xiuxian_zhuan", display_name: "凡人修仙传", ...}]}]` ✓ (verified via TestClient smoke).
- `GET /api/novels` returns 1 item: `xianxia/fanren_xiuxian_zhuan` with 106/2512 chapters done, category fields populated ✓.
- Background downloader restarted; resumed at chapter 101 from the 100-chapter checkpoint — no re-downloads.
- Manifest count verified: `len(CANONICAL_NOVELS) == 28`; `categories()` returns 6 entries in canonical order.

### Scope deferred

- Renaming `{slug}.md` files to use Chinese — file names stay pinyin per ASCII-paths convention.
- Sidebar grouping of `ai_videos/` by sub-type (orthogonal change; novels-only here).
- Auto-discover novels from sudugu.org rankings rather than the hand-curated manifest.
- Adding more entries to lightly-populated categories (历史: 3, 言情: 2). Architecture supports adding more without code changes.

## Follow-up 101 — 2026-05-20 20:53:02
Source: user_input/follow_ups/101-20260520-205302-novels-section-and-downloader.md

Trigger: user — "帮我把这几部小说完整dwonload下来，在ai_video_management里加一个新的栏目，用来让我看所有下载好的小说，并且把现在research里的内容全部删掉".

Three bundled changes:
1. **Delete `research/` top-level** — 9 curated xianxia-drama md files + `xianxia_storylines/` folder + `research/` root removed. Recoverable via `git checkout HEAD -- research/`.
2. **Replace Research section with Novels section** in the webapp tree. `_ALLOWED_TOP_LEVEL` admit-list dropped `"research"`, added `"novels"`; `TreeReader` renamed `_research_section` → `_novels_section`; section label "Research" → "Novels". Frontend Sidebar auto-renders new section name; no React change needed.
3. **Add novel-downloader pipeline** (DDD + CQRS per CLAUDE.md project rules):
   - Domain: `libs/domain/value_objects/novel__valueobject.py` (`NovelSpec` + `CANONICAL_NOVELS` tuple of 10) + `libs/domain/errors/novel__error.py` (4 named errors).
   - Infrastructure: `libs/infrastructure/errors/novel__error.py` + `libs/infrastructure/writers/novel__writer.py` (`NovelDownloader` with sudugu.org HTML scraper, paginated chapter follow, atomic `_meta.json`, resume-from-checkpoint, 0.8 s rate limit, exponential backoff on 5xx/429, max 3 retries).
   - Application: 4 files — `libs/application/dtos/novel__dto.py` (Qdto+Cdto), `mappers/novel__mapper.py`, `commands/novel__command.py` (`.download(slug)` + `.download_all()` re-raises infra errors as domain errors), `queries/novel__query.py` (reads `_meta.json` files into status payloads).
   - API: `apps/api/routes/novel__route.py` — read-only `GET /api/novels`; download deliberately CLI-only to prevent browser clients from spawning multi-hour scrapes. Route mounted in `routes/__init__.py`.
   - CLI: `apps/cli/__init__.py` + `apps/cli/novel_download.py` — runnable via `python -m apps.cli.novel_download` (all novels) or `python -m apps.cli.novel_download <slug>` (single).
   - Container: `novels_root` Singleton + `novel_downloader` Singleton + `novel_command`/`novel_query` Factories wired into `apps/api/container.py`.

Per-novel folder shape: `novels/{slug}/{slug}.md` (concatenated readable markdown, appended chapter-by-chapter) + `novels/{slug}/_meta.json` (chapter manifest with done/hash flags, `complete` invariant — true IFF every chapter is done) + `novels/_index.md` (auto-regenerated status table).

Canonical novel manifest (10 xianxia novels, sudugu.org as v1 source):
凡人修仙传 / 光阴之外 / 玄鉴仙族 / 没钱修什么仙？ / 借剑 / 苟在两界修仙 / 我的模拟长生路 / 谁让他修仙的！ / 山河稷 / 阵问长生.

Honest scale note: combined ~5000-10000 chapters at 0.8 s polite rate = 70-130 minutes of network I/O minimum (likely longer with retries). Download is launched in background at end of this turn; CLI is resumable — re-running picks up from the last gap. The "no partial downloads" constraint is enforced as a `_meta.json.complete` invariant (only flips true at 100% chapter coverage).

### Changes

1. **Deleted**: `research/` (full folder).
2. **NEW Python files (8 application/domain/infra)** + 1 route + 2 CLI files:
   - `libs/domain/value_objects/novel__valueobject.py`
   - `libs/domain/errors/novel__error.py`
   - `libs/infrastructure/errors/novel__error.py`
   - `libs/infrastructure/writers/novel__writer.py`
   - `libs/application/dtos/novel__dto.py`
   - `libs/application/mappers/novel__mapper.py`
   - `libs/application/commands/novel__command.py`
   - `libs/application/queries/novel__query.py`
   - `apps/api/routes/novel__route.py`
   - `apps/cli/__init__.py`
   - `apps/cli/novel_download.py`
3. **Modified Python files**:
   - `libs/common/exposed_tree.py` — admit-list, renamed `research_dirs()` → `novel_dirs()`.
   - `libs/common/safe_resolve.py` — admit-list.
   - `libs/infrastructure/readers/tree__reader.py` — renamed `_research_section` → `_novels_section`, label "Research" → "Novels".
   - `apps/api/routes/__init__.py` — include `_novel_router`.
   - `apps/api/container.py` — `novels_root`/`novel_downloader` Singletons + `novel_command`/`novel_query` Factories.
4. **Test updates (3 files)**:
   - `tests/test_boot_smoke.py` — section list `["AI Videos", "Research"]` → `["AI Videos", "Novels"]`.
   - `tests/test_tree_walker_consumer_walk.py` — section list assertion; renamed `test_research_section_walks_repo_research_dir` → `test_novels_section_walks_repo_novels_dir`.
   - `tests/test_api_security_three_shapes.py` — section list assertion.
5. **NEW empty dir**: `novels/.gitkeep`.

### Verification

- `python -m pytest tests/test_boot_smoke.py tests/test_tree_walker_consumer_walk.py::test_tree_sections_order tests/test_tree_walker_consumer_walk.py::test_novels_section_walks_repo_novels_dir tests/test_api_security_three_shapes.py::test_get_tree_unguarded` → 10/10 passing ✓
- Full suite: 5 pre-existing `wukong_juexing`-fixture failures unchanged (project not present in repo); zero regressions introduced by 101.
- `GET /api/tree` returns `children: [{name: "AI Videos"}, {name: "Novels"}]` ✓ (verified via TestClient smoke).
- `GET /api/novels` returns 200 with `{"items": []}` when no novels yet downloaded ✓.
- Sudugu.org index page probe (book 128 / 凡人修仙传): chapter index regex matches, content `<div class="con">` extraction works, paginated `下一页` link followed ✓.

### Scope deferred to follow-up

- Multi-source fallback per book (v1 = sudugu.org only).
- Pagination/raise of FileReader's 1 MiB `MAX_FILE_BYTES` cap for novel `.md` files (some will be 5-20 MB; user will hit this when reading; quick fix is to raise the cap for the novels/ tree or add `/api/novels/read`).
- POST `/api/novels/download` endpoint (CLI-only for now).
- Search/chapter-jump UI inside a novel (v1 = scroll the single .md).

### Number collision note

The previous turn filed this follow-up as 096-20260520-205302; existing follow-ups already had a `096-20260518-224047-...` (character-ref 7s locked-framing) so the new file was renumbered to **101** in the current turn. The earlier 096 file's changelog entry (line ~165) is unchanged; this 101 entry is the canonical record for the novels-section + downloader work.

## Follow-up 099 — 2026-05-19 20:22:33
Source: user_input/follow_ups/099-20260519-202233-character-ref-v11-simplified-prompt.md

Trigger: user, after rendering v10.2 character mp4s: "the camera did not move as you intended in the charactor prompt, I think kling got confused, you need to tell it in a more simple way and only once in the prompt. currently the it shart to turn around to side view at only about 5s. ... yes, the video does not have a backview in it, I think it start to move around 4~5s so the last frame in the video is still side view. Please update the prompt now".

Diagnosis: v10.2's prompt had the camera motion path described in 4 different fields with different vocabularies — 镜头 line (5-phase enumeration), 动作 5 timed beats (each repeating phase description), 节奏 line (repeating 5-phase + 3 statics + 2 motion bridges), 负向 line (14 items with qualifier paragraphs like `不要 motion 跨越目标角度 (1s motion bridge 必须精确终止在 90° (t=3s)...)`). Model averages across the redundant descriptions and under-commits to motion. Result: motion delayed to ~5s in rendered output.

Fix: rule #12.5 v10.2 → v11 — same 5-phase schedule, same `CANONICAL_VIEWS` timestamps, but motion described ONCE only (in 动作 timed beats field) using plain Chinese. **No code change** — value object constants unchanged.

### v11 prompt field consolidation

| Field | v10.2 | v11 |
|---|---|---|
| 镜头 | 5-phase enumeration with motion path + framing all mixed, "motion bridge"/"锁定机位"/"locked-framing" jargon | Framing + lens specs ONLY — no motion path |
| 动作 | 5 beats each repeating "锁定机位 X medium-full" / "motion bridge 缓慢顺时针 orbit X°→Y°" | 5 beats in plain Chinese — single source of truth for motion |
| 节奏 | "锁定 framing 5-phase 单 take, 3 static landings (0-2s / 3-4s / 5-7s) + 2 motion bridges (2-3s / 4-5s 各 1s)" — REPEATS motion path | "单 take 7s, 角色站立不动只说话, 镜头按 动作 timed beats 旋转 + 停顿" — minimal |
| 负向 | 14 items with qualifier paragraphs | 10 simple bans, no qualifier paragraphs |

Plain Chinese examples replacing jargon:
- "锁定机位 正面 medium-full" → "镜头正面拍角色 medium-full"
- "motion bridge 缓慢顺时针 orbit 0° → 90° (1s motion bridge, no dolly, no zoom, 终止在精确 90° = 左侧身)" → "镜头围绕角色顺时针绕 90° 到角色左侧身"
- "锁定机位 左侧身 90° medium-full (1s static lock — 镜头完全不动 ...)" → "镜头停在左侧身角度不动"
- 锁定机位 jargon removed entirely — model interprets "锁定" as "全程不要动" which conflicts with subsequent motion beats.

### Changes (3 source files + 12 audit/character files)

1. **`.claude/agent_refs/project/ai_video.md` rule #12.5 v10.2 → v11** — cross-cutting rule patch:
   - Active spec section rewritten: 「为什么 7s 5-phase single-take with simplified plain-Chinese prompt (rule #12.5 v11)」 replaces 「为什么 7s locked-framing 5-phase single-take with static landings (rule #12.5 v10.2)」 with diagnosis of v10.2's empirical failure (model averaging across 4-field redundancy) + v11's field-consolidation design.
   - v10.2 demoted to archive with explicit 「为什么 v10.2 verbose multi-field prompt 不再生效」 paragraph documenting the user's empirical observation (motion delayed to ~5s under v10.2 vs spec 2s).
   - File-note line, h1 heading, prompt-block title, 镜头 line, 动作 6-line block, 台词 enumeration, 光线 line, 节奏 line, 负向 line, table heading, table 3 用途 columns, 抽帧时间戳 callout, 设计原则 section, locked-fields section, 文件结构 sibling-file comment — all rewritten for v11 plain-Chinese simplified form.
   - Footer attribution: appended v11 rev paragraph with diagnosis + design rationale + retreat paths (v12 = shift schedule earlier breaking 0-2s truncate-compat, v13 = multi-clip).
2. **`projects/ai_video_management/libs/domain/value_objects/character_video__valueobject.py`** — **no change** (CANONICAL_VIEWS constants stay `(1.0, 3.5, 6.0)` — v11 keeps v10.2's static-landing schedule + timestamps).
3. **10 character md files** (`ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md`) patched via two-script sequence:
   - `C:/Users/light/AppData/Local/Temp/patch_chars_v11.py` — 12 substitutions per file (10 fixed-string + 2 regex). Covered: 文件说明 line / h1 / table heading / 3 table 用途 rows / 场景 line / 镜头 line / 节奏 line / 负向 v10.2-block → v11-block / 动作 6-line block (regex preserving character name + 标志台词 #1/#2 via 3 named capture groups) / 台词 5-line enumeration block (regex preserving same character-specific content).
   - `C:/Users/light/AppData/Local/Temp/patch_chars_v11_fix.py` — corrective patch for 2 patterns the first script missed: title line (used different wording in files vs the rule template, so regex didn't match) + 光线 line (no `**轮廓光 + key 在 orbit 全程保持稳定**` tail in files). Title applied to all 10; 光线 applied to 7 (3 characters without character-specific aura segment kept v10.2 wording — cosmetic, non-load-bearing).
   - All 10 confirmed at v11, zero v10.2 motion-jargon markers remaining (sanity-checked: `5-phase locked-framing single-take` / `motion bridge 缓慢顺时针` / `锁定机位 左侧身 90° medium-full` / `motion bridge 段速度 ≤ 90°/s` / `motion 跨越目标角度` / `(reference 上传上限 v10.2)` — all zero).
4. **`specs/development/ai_video_management/user_input/revised_prompt.md`** — header bump 099.
5. **`specs/development/ai_video_management/changelog.md`** — 本条目.

### Verification

- Python: `python -c "from libs.domain.value_objects.character_video__valueobject import CANONICAL_VIEWS; print(...)"` still returns `[(1.0, 'front'), (3.5, 'side'), (6.0, 'back')]` ✓ (no code change in 099).
- Spot-check c1_沧冥.md:
  - Title line at v11: `沧冥 · 魔尊本相 — 角色 reference 7s 单 take` ✓
  - 镜头 line: framing/lens only, no motion path ✓
  - 动作: 5 plain-Chinese beats, motion described ONCE ✓ (preserves character name "沧冥" in beat 2-3s, preserves 标志台词 #1 "当年你们怎么对我，今日我便十倍奉还" + #2 "本尊从不解释，只清算" in beat 5-7s)
  - 节奏: one short sentence ✓
  - 负向: 10 simple bans, no qualifier paragraphs ✓
  - Character bible (lines 1-78) untouched ✓
  - 渲染样式: character-specific style adders preserved (cinematic + 4K HDR + ... + 真实皮肤微瑕) ✓

### Risks acknowledged in the spec

1. **Model may still under-commit to motion despite simpler prompt.** If v11 also has motion delayed beyond ~3s, the issue is a fundamental model bias toward static front-facing content (not prompt redundancy). Retreat paths:
   - v12: shift schedule earlier — 0-1s static front + 1-3s motion + 3-4s static side + 4-5s motion + 5-7s static back. Breaks 0-2s truncate-compat byte-identical contract; `CANONICAL_VIEWS` side would change 3.5 → 3.5 (unchanged), front 1.0 → 0.5 (mid 0-1s static front instead of mid 0-2s), back 6.0 unchanged.
   - v13 multi-clip: render front / side / back as 3 separate 2-3s clips, concatenate at file-system level. Most expensive, most bulletproof — each clip is a static shot, no motion required.
2. **Bare-bones negatives may let unwanted defaults slip through.** v10.2 had explicit `不要 motion 跨越目标角度` preventing the model from rotating past 180°. v11 drops this. If the model over-rotates (e.g., 270° instead of 180°), retreat is to add back ONE qualifier (`不要 镜头超过 180°`) without re-inflating the entire negatives section.

### Sibling mozun_chongsheng follow-up 028

Pending in same turn (post this entry): `specs/ai_video/mozun_chongsheng/user_input/follow_ups/028-…` documenting the v10.2 → v11 ripple already applied to the 10 character md files via the patch scripts; mozun_chongsheng 027 (v10.2 patch) marked SUPERSEDED at top; mozun_chongsheng revised_prompt + changelog bumped.

No conflicts found in: `interview/qa.md` / `findings/dossier.md` / `final_specs/spec.md` / `validation/strategy.md` (none reference character ref prompt text), `apps/api/routes/character_video__route.py` (route unchanged), `apps/api/container.py` (DI graph unchanged), backend `CharacterViewExtractor` (writer unchanged), frontend Reader.tsx + SiblingMedia.tsx (UI unchanged from 097 state).

## Follow-up 098 — 2026-05-19 00:06:05
Source: user_input/follow_ups/098-20260519-000605-character-ref-v10.2-static-landings.md

Trigger: user, after rendering first v10 character mp4s + clicking 🖼 — "the side is still almost front, the back picture actually shows side ... the video does not have a backview in it, I think it start to move around 4~5s so the last frame in the video is still side view. Please update the prompt now".

Diagnosis: video model under-rotates v10's single 4s continuous orbit (~22°/s, ~half spec speed) with apparent motion-start delay to t≈4-5s. Spec math `(t-2)×45°/s = angle` is correct but the rendered video doesn't follow linearly. Root cause is structural: video models don't honor timed-beat *speed* instructions for "slow continuous motion".

Fix: rule #12.5 v10 → v10.2 — replace single 4s continuous orbit with **3 static landings + 2 short motion bridges**. Each angle pick now lands at a guaranteed-static moment. The angle contract changes from "time × speed" to "explicit landing angle hold".

### v10.2 5-phase camera path

| Phase | Time | Camera | Pick |
|---|---|---|---|
| Static front | 0-2s | locked, medium-full | front @ t=1.0s |
| Motion bridge | 2-3s | orbit 0° → 90° (1s) | — |
| Static side | 3-4s | locked at 90°, medium-full | **side @ t=3.5s** |
| Motion bridge | 4-5s | orbit 90° → 180° (1s) | — |
| Static back | 5-7s | locked at 180°, medium-full, settle | back @ t=6.0s |

### Changes (3 source files + 12 audit/character files)

1. **`.claude/agent_refs/project/ai_video.md` rule #12.5 v10 → v10.2** — cross-cutting rule patch:
   - Active spec section rewritten: 「为什么 7s locked-framing 5-phase single-take with static landings (rule #12.5 v10.2)」 replaces 「为什么 7s locked-framing single-take (rule #12.5 v10)」 with full diagnosis of v10's empirical under-rotation + design rationale for the 5-phase architecture.
   - v10 demoted to archive with explicit 「为什么 v10 的 4s 连续 orbit 不再生效」 paragraph.
   - File schema header line: `7s locked-framing single continuous take + 0-2s 一/二 lock + 180° orbit` → `7s locked-framing 5-phase single-take + 0-2s 一/二 lock + static landings at 0°/90°/180°`.
   - Prompt body code block rewritten: 3-phase → 5-phase schedule; timed beats split into 5 beats (0-1s/1-2s/2-3s/3-4s/4-5s/5-7s — slot 4 covers static-side hold + motion-to-back transition); negatives bumped from 13 items to 14 items (drop `不要 mid-shot freeze` which conflicts with v10.2's explicit mid-shot statics, add `不要 motion 跨越目标角度` + `不要 静态段内继续微调机位` + modify quals for motion speed/cut/blur).
   - 设计原则 section rewritten for v10.2 (5-phase + bookended motion + 3-static-landings architecture); footnote about why v10's "time × speed" contract failed empirically.
   - Locked-fields list updated: 节奏 = "锁定 framing 5-phase 单 take, 3 static landings + 2 motion bridges"; 镜头 = 5-phase template; negatives count 13 → 14.
   - Footer attribution: appended v10.2 rev paragraph with diagnosis, design pivot rationale, retreat paths (v10.3 / v10.4 / v11+ multi-clip), and reference to the value-object code change.
2. **`projects/ai_video_management/libs/domain/value_objects/character_video__valueobject.py`** — code change:
   - `CANONICAL_VIEWS` tuple: `(front 1.0, side 4.0, back 6.0)` → `(front 1.0, side 3.5, back 6.0)`. Front unchanged; side moves 4.0 → 3.5 (mid 3-4s static side; was in motion segment in v10); back unchanged (still 6.0s but now reliably lands in static 5-7s window).
   - Module docstring rewritten to reference v10.2's 5-phase camera path and derive each timestamp from a static-landing window (not from `(t-2)*45°/s` arithmetic).
3. **`projects/ai_video_management/apps/ui/` (no change)** — the 🖼 button + path-gate + Cdto / mapper / endpoint wiring all driven by `CANONICAL_VIEWS` and unchanged. v10.2 propagates purely through the value-object constant + the cross-cutting rule.
4. **10 character md files** under `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md` — patched via two one-shot Python scripts:
   - `C:/Users/light/AppData/Local/Temp/patch_chars_v10_2.py` — 13 fixed-string + 4 regex substitutions per file (17/file). Updated: 文件说明 line / h1 heading / 镜头 line / 动作 heading / 节奏 line / 负向 line / table heading / 3 table 用途 rows / 3 enumeration line tweaks / prompt-block title (regex preserving NAME · ROLE) / beat 2-3s wording (regex preserving character name).
   - `C:/Users/light/AppData/Local/Temp/patch_chars_v10_2_fix.py` — 1 multi-line regex per file. Split v10's combined 3-5s + 5-7s beat pair (which I had collapsed from v9's 3-line structure during v8 → v10 patching) into v10.2's 3-line structure (3-4s static side + 4-5s motion bridge + 5-7s static back), preserving 标志台词 #1 and #2 via two capture groups. The first script's regex assumed v10 had 3 motion-beat lines; reality was 2; corrective script fixed it.
   - All 10 confirmed at v10.2, zero v10 markers remaining (sanity-checked: no `single continuous take + 0-2s 一/二 lock + 180° orbit` / no `3 阶段连续运动` / no `(reference 上传上限 v10)` / no `side t=4.0s` / no `over orbit 0-90°` / no `3-5s: 镜头继续缓慢 orbit, 45° → 135°` / no `5-7s: 镜头继续缓慢 orbit 135° → 180°`).
5. **`specs/development/ai_video_management/user_input/revised_prompt.md`** — header bump 098.
6. **`specs/development/ai_video_management/changelog.md`** — 本条目.

### Verification

- TypeScript: no changes to .ts files in 098 (frontend unchanged).
- Python: `python -c "from libs.domain.value_objects.character_video__valueobject import CANONICAL_VIEWS; print(...)"` returns `[(1.0, 'front'), (3.5, 'side'), (6.0, 'back')]` ✓.
- Spot-check c1_沧冥.md: 5 distinct timed beats (0-1s / 1-2s / 2-3s / 3-4s / 4-5s / 5-7s) ✓; static side hold at 3-4s with 标志台词 #1 起声 ✓; motion bridge at 4-5s with 标志台词 #1 续声 + 落声 ✓; static back lock at 5-7s with 标志台词 #2 + 自然定格收尾 ✓; character bible (lines 1-78) untouched.

### Risks acknowledged in the spec

1. **Kling validator may flag v10.2's mid-shot static landings as "stop-and-go".** Hypothesis: bookended motion segments with 0 velocity at landing boundaries are categorically different from v6 whip-pans (720°/s continuous spin). If v10 passed validator, v10.2 should pass since motion total time is shorter (2s × 2 bridges vs v10's continuous 4s). Retreat paths:
   - v10.3: drop one motion bridge — 0-2s front + 2-3s motion + 3-7s side hold (4s). Loses back angle; extract degrades to front + side reliable.
   - v10.4: drop both bridges — 7s static front = v8 + v10.2 negatives. Loses side + back; extract degrades to front-only.
   - v11+ multi-clip: render 3 separate 2-3s clips and concatenate at file-system level. Most expensive, most bulletproof.

2. **Pre-v10.2 mp4s already rendered (the v10 batch just rendered this morning) are invalidated for the extract pipeline.** v10 sources extracted with new (1.0, 3.5, 6.0) timestamps would: front OK (same mid-static), side land at v10's motion-segment mid (improvement over t=4.0s but still in-motion), back land at v10's static back (= v10's settle = actually OK since v10's 6-7s segment was static). User re-renders character mp4s with v10.2 prompt to get clean 3-still extraction.

### Sibling mozun_chongsheng follow-up 027

Pending in same turn (post this entry): `specs/ai_video/mozun_chongsheng/user_input/follow_ups/027-…` documenting the v10 → v10.2 ripple already applied to the 10 character md files via the patch scripts; mozun_chongsheng 026 (v10 patch) marked SUPERSEDED at top; mozun_chongsheng revised_prompt + changelog bumped.

No conflicts found in: `interview/qa.md` / `findings/dossier.md` / `final_specs/spec.md` / `validation/strategy.md` (none reference character ref schedule timing), `apps/api/routes/character_video__route.py` (route unchanged), `apps/api/container.py` (DI graph unchanged), backend `CharacterViewExtractor` (writer unchanged — consumes `CANONICAL_VIEWS` as opaque tuple).

## Follow-up 097 — 2026-05-18 23:57:49
Source: user_input/follow_ups/097-20260518-235749-extract-views-button-on-direct-mp4-page.md

Trigger: user — "make the button appear on each mp4 page please". Discovered when the user navigated directly to a v10 character mp4 in the file tree and couldn't see the 🖼 "提取三视图+音频" button — the button existed only on per-tile thumbnails inside the SiblingMedia panel (which renders below md / shot-pair / image-ref files), so reaching it required first opening the character `.md` file and scrolling past the rendered markdown.

Fix: frontend-only dual-placement parity. The 🎞 "Extract Frames" button already had this dual placement from follow-up 062 (one copy in SiblingMedia tiles + one copy in the direct-video toolbar inside Reader). Follow-up 093 wired the new 🖼 button only to SiblingMedia tiles. 097 mirrors the 🎞 pattern so 🖼 also appears in the direct-video toolbar.

### Changes (2 source files + 2 audit files)

1. **`projects/ai_video_management/apps/ui/src/components/SiblingMedia.tsx`** — single-line change: `function isCharacterVideoPath` → `export function isCharacterVideoPath`. Promotes the path-shape gate from module-private to named export so Reader.tsx can import it without duplicating the regex. No behavior change in SiblingMedia itself.
2. **`projects/ai_video_management/apps/ui/src/components/Reader.tsx`** — additive changes:
   - Imports: `extractCharacterViews` added to the api import block; `isCharacterVideoPath` added to the SiblingMedia import.
   - State: `const [extractingViews, setExtractingViews] = useState<boolean>(false);` parallel to existing `extracting` state.
   - Handler: new `onExtractCharacterViewsClick` useCallback — parallels `onExtractFramesClick` line-for-line. Calls `extractCharacterViews(path)`, derives `okCount = result.views.length + (result.audio ? 1 : 0)` + `failCount = result.failures.length`, announces toast (`Extracted N views + audio from ${name} → views/` on full success, `Extracted N from ${name} (M failed)` on partial, `Extract views failed: ${kind}` on exception), triggers `onSaved()` to refresh tree so the new `views/` subfolder appears.
   - Derived values: `mediaActionsBusy` extended to `archiving || deleting || extracting || extractingViews` so all 4 mutually-blocking actions disable each other; new `viewsExtractLabel = extractingViews ? "⏳ 提取中…" : "🖼 提取三视图+音频"` (byte-identical Chinese wording to SiblingMedia's tile button); new `showViewsBtn = isVideo && !isArchivedFile && !isDeletedFile && isCharacterVideoPath(path)` combining all 4 gate conditions.
   - Render: new `{showViewsBtn ? <button … /> : null}` block placed between the existing 🎞 Extract Frames button and the 📦 Archive button inside the `<div className="reader-media-actions">` block (lines 265-285 in the direct-video-view branch). Same className convention as the SiblingMedia counterpart (`sibling-media-views-btn` → `reader-media-views-btn` — naming parallels the 🎞 button's `sibling-media-extract-btn` → `reader-media-extract-btn` split, even though no CSS rules exist for either reader-* class today — preserves the prefix scheme so future CSS work can target both contexts independently).
   - Tooltip text: `"提取三视图 (front / side / back) + 音频 (.mp3) 到 ./views/ — 适用于 v10 character turntable (7s locked-framing + 180° slow orbit)"`. References v10 since the rule was bumped v9 → v10 by the prior follow-up 096. **The SiblingMedia tile button's tooltip still says v9** (stale post-096); not bundled here to keep the 097 diff focused on the dual-placement parity. Separate cleanup follow-up if desired.
3. **`specs/development/ai_video_management/user_input/revised_prompt.md`** — header bump 097 with full code-change rationale + tooltip-staleness acknowledgment.
4. **`specs/development/ai_video_management/changelog.md`** — 本条目.

### Verification

- TypeScript check (`npx tsc --noEmit` from `apps/ui/`): no errors in touched files. Two pre-existing errors in `vite.config.ts` (`Cannot find module 'path'` + `Cannot find name '__dirname'`) — unrelated, present on the prior commit too.
- No runtime test executed — pure additive UI change with no behavioral risk to existing flows (the new button gate is strictly additive; SiblingMedia tile behavior unchanged; api.ts wire-up unchanged; backend untouched). Manual smoke deferred to user: open a character mp4 directly, confirm 🖼 button appears, click it, confirm toast + views/ subfolder appears alongside the existing extract behavior.

### Out of scope

- No backend changes (route shape / Cdto / mapper / value-object / writer / domain-error all byte-identical to post-096 state).
- No SiblingMedia tile changes beyond the single export promotion (button behavior identical, gate logic identical, no tooltip update).
- No new CSS for `.reader-media-views-btn` (deferred — current CSS for `.reader-media-extract-btn` etc. is also absent today; both rely on inherited button styling).
- No keyboard shortcut for the new button (deferred — 🎞 also lacks a shortcut).
- No batch-extract-all-character-mp4s feature at the character-folder level (deferred per 093 "out of scope").

No conflicts found in: `interview/qa.md` (no UI button content), `findings/dossier.md` (no UI button content), `final_specs/spec.md` (no per-button render rules), `validation/strategy.md` (no UI parity check), `apps/api/routes/character_video__route.py` (route unchanged), `apps/api/container.py` (DI graph unchanged), backend `CharacterViewExtractor` (writer unchanged).

## Follow-up 096 — 2026-05-18 22:40:47
Source: user_input/follow_ups/096-20260518-224047-character-ref-7s-locked-framing-3view-extract.md

Trigger: user — 「在生成 character 视频之后, 我需要能可靠抽出 4 样东西 — 全身正面（要能看清脸）/ 全身侧面 / 全身背面 + 一段音频。7s 的视频 prompt 你帮我设计成抽这 4 样东西最容易的形态」.

Re-designs character ref turntable as 7s locked-framing single-take, bottom-up around the extract-3-views + audio pipeline introduced by follow-up 093. Supersedes v9 (15s slow-push-in + slow-orbit + reverse-dolly, follow-up 092) which had a structural mismatch with the extract pipeline: v9's dolly-in and reverse-dolly vary head-size-in-frame across the take, so the 3 angle picks land at inconsistent framings (front pick at wide, side at head-1/3-frame mid-pull-back, back near-wide mid-pull-back), making them unusable as a coherent 3-view character sheet.

### Design decision — locked medium-full framing throughout

User picked (via clarifying question this turn): "locked medium-full framing throughout" over "mixed framing with dedicated face MCU". The trade-off:
- **Picked**: 3 extracted stills at IDENTICAL framing (head ~1/5 frame, full body, toe-safe), face still recognizable (~360-400px tall at 9:16 1080p), suitable as image-to-video reference.
- **Rejected**: dedicated face close-up window (v9's 2-5s dolly to MCU) — but at the cost of inconsistent 3-still framings that defeat the extract pipeline's purpose.

### Schedule (3-phase camera path)

| Phase | Time | Camera | Framing throughout |
|---|---|---|---|
| Static front lock | 0-2s | 锁定机位 正面, no motion | medium-full ~40mm, head ~1/5 frame, head-to-toe visible |
| Slow ccw 180° orbit | 2-6s | 顺时针 45°/s × 4s, locked distance, no dolly, no zoom | identical medium-full — only angle changes |
| Static back lock | 6-7s | 锁定机位 背面, no motion | identical medium-full, character's back to camera |

Extract-ready timestamps (algebraic image of the 3-phase schedule):
- `front` at t=1.0s (mid 0-2s static intro)
- `side` at t=4.0s ((4.0-2.0) × 45°/s = exactly 90° left-side)
- `back` at t=6.0s ((6.0-2.0) × 45°/s = exactly 180° back, coincides with orbit-end + back-lock-start)
- `audio` = full 7s mp3

### Dialogue retimed (5 slots, same structure as v8/v9)

| # | 台词 | 时段 | Camera state |
|---|---|---|---|
| 1 | 一 | 0-1s | static front lock |
| 2 | 二 | 1-2s | static front lock (must finish by 2.0s) |
| 3 | 三, 我是 {角色名} | 2-3s | orbit start, 0° → 45° |
| 4 | {标志台词 #1} | 3-5s | orbit 45° → 135° (through 90° at t=4.0s) |
| 5 | {标志台词 #2} | 5-7s | orbit 135° → 180° + back-lock settle |

### Changes (3 source files + 2 audit files)

1. **`.claude/agent_refs/project/ai_video.md` rule #12.5 v9 → v10** — cross-cutting rule patch:
   - Active spec section rewritten: 「为什么 7s locked-framing single-take (rule #12.5 v10)」 replaces 「为什么 15s slow-push-in + slow-orbit single-take (rule #12.5 v9)」 with full rationale for the reversal.
   - v9 demoted to archive with explicit 「为什么 v9 的 15s mixed-framing single-take 不再生效」 paragraph documenting the extract-pipeline mismatch.
   - 2s truncate-compat section updated: v8 / v9 / v10 共同契约 (content byte-identical: 静态 + 正面 + 全身 + 一/二; framing in v10 fractionally tighter wide ~35mm → medium-full ~40mm).
   - File schema header line: `15s slow-push-in + slow-orbit single continuous take + 0-2s 一/二 lock` → `7s locked-framing single continuous take + 0-2s 一/二 lock + 180° orbit`.
   - File 用法 line: `≤ 15s 硬上限 (reference 上传约束 per rule #12.5 v9)` → `≤ 7s (rule #12.5 v10 时长)` + explicit 抽帧契约 callout (front t=1.0s / side t=4.0s / back t=6.0s).
   - Prompt body code block rewritten: 5-phase → 3-phase schedule; timed beats retimed; framing field locked at medium-full throughout; negatives bumped from 11 items to 13 items (added no-dolly / no-zoom / no-framing-change bans, dropped v9's reverse-dolly-allowed carve-out).
   - 5-row dialogue table retimed: slot 3 (2-5s → 2-3s), slot 4 (5-10s → 3-5s), slot 5 (10-15s → 5-7s).
   - New 「抽帧时间戳契约」 callout under the dialogue table, citing the CANONICAL_VIEWS constants in the value object and the algebraic derivation from camera path.
   - 设计原则 section rewritten for v10: 3-phase template + locked-framing + 180° orbit; v9-specific bullets (dolly-in face MCU, reverse-dolly hidden in orbit, 360° orbit) all replaced with v10-specific bullets (no-dolly / no-zoom contract, 180° suffices via bilateral symmetry, framing locked for extract pipeline).
   - Locked-fields list updated: 时长 = 7s; 节奏 = 锁定 framing 单方向慢速 orbit 7s 单 take; negatives count 11 → 13; 镜头 = 3-阶段 locked-framing template.
   - Footer attribution: appended v10 rev paragraph with full design rationale, supersedes note for v9, retreat paths (v10.1 / v10.2), and reference to the value-object code change.
2. **`projects/ai_video_management/libs/domain/value_objects/character_video__valueobject.py`** — code change:
   - `CANONICAL_VIEWS` tuple: `(front 1.0, side 7.0, back 9.0)` → `(front 1.0, side 4.0, back 6.0)`.
   - Module docstring updated: references v10's 3-phase camera path instead of v9's 5-phase; explains the algebraic derivation of new timestamps; notes that all 3 picks share IDENTICAL medium-full framing because v10 forbids dolly / zoom.
   - No other code change. The extract route, the `CharacterViewExtractor` class, the Cdto / mapper / command wiring, and the frontend button all work unchanged — they consume `CANONICAL_VIEWS` as a tuple, so changing the timestamps is sufficient.
3. **`specs/development/ai_video_management/user_input/revised_prompt.md`** — header bump 096 with full v10 design rationale + risk acknowledgment + sibling-ripple deferral note.
4. **`specs/development/ai_video_management/changelog.md`** — 本条目.
5. **`specs/development/ai_video_management/user_input/follow_ups/096-…`** — follow-up draft itself.

### Risks acknowledged in the spec

1. **Kling validator may still reject v10 uploads.** Same hypothesis as v9: slow continuous single-direction motion passes; only fast / direction-reversing motion is judged as cut. v10's orbit is at the same 45°/s speed cap as v9 — if v9 passes, v10 should pass. Retreat paths if empirical data shows rejection:
   - v10.1: drop the orbit entirely, ship 7s of static front lock (= v8 + 2-7s per-character 标志台词). Extract pipeline degrades to front-only reliable; side/back fall back to "extract failed" partial-failure shape (which the 093 pipeline already handles).
   - v10.2: keep orbit but insert ~0.3s static holds at 90° (t=4.0s) and 180° (t=6.0s). Breaks v10's "no mid-shot stop-and-go" rule but each motion segment is < 2s so the validator may still pass. Worth trying only if v10.0 fails AND v10.1's reference loss is unacceptable.

2. **Medium-full framing may make face too small for casting decisions.** At 9:16 1080×1920, head ~1/5 frame height = ~384px tall. Borderline for eye-color / mouth-shape reads. If users find face details insufficient, retreat: introduce a separate FACE-only short clip (~3s static MCU) as a sibling file to the turntable, decoupling "body silhouette ref" from "face detail ref". v1 sticks with single-clip 3-view design per user pick this turn.

3. **Pre-v10 mp4s already rendered in `ai_videos/mozun_chongsheng/characters/c*` won't extract cleanly at the new timestamps.** v9 sources extracted with new (1.0, 4.0, 6.0) timestamps would land side at t=4.0s in the v9 dolly-in window (not at any clean angle) and back at t=6.0s also pre-orbit-arrival in v9's schedule. Mitigation: users re-render character refs to v10 before extracting. The webapp's extract endpoint returns the same shape regardless of source provenance; only the visual quality of the 3 stills differs.

### Deferred to user

- **Sibling mozun_chongsheng follow-up**: a `specs/ai_video/mozun_chongsheng/user_input/follow_ups/` entry would patch the 10 character `c{N}_*.md` files via a one-shot script (s/15s/7s/ + replace timed-beats table + replace 镜头 line + replace 负向 clauses). Same pattern as 092 / 091 / 088 / 078 — user runs the script after reviewing this draft. **NOT performed in this turn**, follow-up 096 explicitly scopes the ripple as user-side.
- **Character re-rendering**: not auto-triggered. Users re-render character refs to v10 at their discretion. Until they do, the extract button will produce inconsistent-framing stills from pre-v10 sources (still 200 OK shape, just visually mismatched).

No conflicts found in: `interview/qa.md` (no character ref schema content), `findings/dossier.md` (no character ref schema content), `final_specs/spec.md` (no embedded duration / schedule details — defers to agent_refs rule #12.5), `validation/strategy.md` (no v9-specific checks), `apps/api/routes/character_video__route.py` (route shape byte-identical), `apps/ui/src/components/SiblingMedia.tsx` (button behavior + path-gate unchanged).

## Follow-up 095 — 2026-05-18 22:30:27
Source: user_input/follow_ups/095-20260518-223027-gender-bleed-fix-and-actor-tile-redirect.md

Trigger: user — "there is bug in actor generation, when I ask to batch generate for men, half of them are women, also help me change 1 behaviour, when I click a specific actor in grid view, it should redirect me to the actor main page instead of just a jpg view".

Two fixes bundled because both improve actor UX.

### Fix 1 — gender bleed in Chinese structured prompts

Root cause: the 7 descriptor pools (`_EYES_ZH` / `_NOSE_ZH` / `_LIPS_ZH` / `_BROW_ZH` / `_CONTOUR_ZH` / `_SKIN_ZH` / `_BODY_ZH` in `libs/infrastructure/writers/actor__chinese_prompt.py`, ~22 entries each) mix neutral and gendered descriptors uniformly. `_pick_biased` and `_resolve_batch_picks` draw with no gender filter, so a male prompt has ~30-45% chance per pool of pulling a feminine descriptor; cumulated across 7 attribute lines it's >95% probability of at least one cross-gender leak, enough to push Kling toward female rendering even with `性别：男性` in the header.

修法:
- New module-level constants in `actor__chinese_prompt.py`:
  - `_FEMALE_ONLY_MARKERS` (18 unambiguous identity terms: 少女 / 女孩 / 美人 / 闺秀 / 佳人 / 妩媚 / 妖艳 / 妖媚 / 娇憨 / 楚楚动人 / 致命诱惑 / 贤淑 / 仕女 / 邻家姐姐 / 萌妹 / 娇媚柔弱 / 弱不禁风 / 婴儿肥).
  - `_MALE_ONLY_MARKERS` (10 unambiguous identity terms: 男性化 / 男性硬朗 / 邻家男孩 / 阳光男孩 / 健壮型男 / 长腿欧巴 / 偶像身材 / 腹肌分明 / 魁梧 / 强壮有力).
  - Marker selection rule: only unambiguous identity terms — borderline-feminine physical attributes (性感 / 丰满) and borderline-masculine physical attributes (肌肉 / 肩宽) are deliberately excluded because they can apply across genders.
- New helper `_filter_pool_by_gender(pool, bias_indices, gender_slug) -> (filtered_pool, translated_bias_indices)`: substring-matches markers against descriptors, drops matches, builds an `original_to_new` index map so `bias_indices` can be translated (entries whose source descriptor was stripped are dropped from the bias tuple).
- `build_face_prompt` + `build_body_prompt`: apply `_filter_pool_by_gender` to each of the 7 pools (eyes / nose / lips / brow / contour / skin / body) before calling `_pick_biased` / `_pick`.
- `_resolve_batch_picks`: signature gains `gender_slug: str`; each pool is filtered before passing to `_batch_sample_pool`.
- `actor__writer.py:2080` (sole caller of `_resolve_batch_picks`): pass `gender_slug=attrs.gender`.

Verification:
- Boot smoke 7/7 pass (no import / wiring regressions).
- Smoke against `build_face_prompt(gender=male, look=righteous, archetype=leading_hero)` × 10 seeds: 0 female markers found across all 10 prompts (was ~30-45% per pool / >95% cumulative before fix).
- Smoke against `build_face_prompt(gender=female, look=seductive, archetype=femme_fatale)` × 10 seeds: 0 male markers found.
- Smoke against `_resolve_batch_picks(gender_slug=male)` × 10 slots: 0 female markers in batch-coordinated picks.
- Smoke against `_resolve_batch_picks(gender_slug=female)` × 10 slots: 0 male markers in batch-coordinated picks.

Risk acknowledged in spec: substring-marker filter is the 80/20 fix. Some residual feminizing is possible from non-marker descriptors (e.g., "高颧骨, 立体感强, 模特脸" is gender-neutral on paper but Kling might still skew). If empirical Kling output remains skewed >10% post-fix, fallback options: (a) expand marker lists, (b) introduce gender-specific sub-pools per attribute, (c) repeat `性别:` line later in the prompt.

### Fix 2 — actor tile → main page redirect

UX change in `apps/ui/src/components/ActorGrid.tsx::onTileClick`: replace `navigate("/file/" + encodeURIComponent(imagePath))` with `const mdPath = "ai_videos/_actors/" + actorId + "/" + actorId + ".md"; navigate("/file/" + encodeURIComponent(mdPath));`. The `imagePath` parameter is preserved in the closure signature but renamed `_imagePath` to flag it as deliberately unused (avoids TS lint warnings without removing the second arg from the caller signature).

Reader's existing `^ai_videos/_actors/actor_[^/]+/actor_[^/]+\.md$` shape detector (Reader.tsx:216) routes the file to `ActorView`, which renders the actor's bible + attribute table + assignments + delete button — the actual "actor main page" the user expects on click-through. The jpg thumbnail is still shown on the tile itself; only the click target changes.

修法 (3 source files + 2 audit files):
1. `projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py`: + 2 marker tuples + `_filter_pool_by_gender` helper + 7-pool filtering in `build_face_prompt`/`build_body_prompt`/`_resolve_batch_picks`; signature change to `_resolve_batch_picks` adds `gender_slug` parameter.
2. `projects/ai_video_management/libs/infrastructure/writers/actor__writer.py`: 1-line change at the `_resolve_batch_picks` call site to pass `gender_slug=attrs.gender`.
3. `projects/ai_video_management/apps/ui/src/components/ActorGrid.tsx`: rewrite `onTileClick` navigate target to the actor md path.
4. `specs/development/ai_video_management/user_input/revised_prompt.md`: header bump 095.
5. `specs/development/ai_video_management/changelog.md`: 本条目.

No backend API changes (route shapes byte-identical). No new DTOs / errors. No `agent_refs` changes (project-scoped fix, not a cross-cutting rule).

## Follow-up 094 — 2026-05-18 22:24:55
Source: user_input/follow_ups/094-20260518-222455-actor-grid-look-filter.md

Trigger: user — 「在演员页面，外貌气质也应该是可以filter的选项」.

修法 (1 file, frontend-only):
- `projects/ai_video_management/apps/ui/src/components/ActorGrid.tsx`: add `filterLook` state (init `FILTER_ALL`); add 5th predicate `if (filterLook !== FILTER_ALL && a.look !== filterLook) return false;` inside `filteredActors` useMemo; add `filterLook` to the page-reset useEffect deps; add new `<select>` block populated from `ATTR_OPTIONS.look` (13 canonical values), matching the existing 民族 / 性别 / 年龄段 dropdown pattern (Chinese label, English-slug options).

No backend / API / type changes — `actor.look` was already exposed on `ActorInfo` and the 13 canonical values were already in `ATTR_OPTIONS.look`.

## Follow-up 093 — 2026-05-18 20:39:39
Source: user_input/follow_ups/093-20260518-203939-character-views-and-audio-extract.md

Trigger: user request — "turns the character video into 3 pictures from different angle, like front, side and back, and also extract the audio from it".

Design choices confirmed in this turn (AskUserQuestion):
- Output layout: new `views/` subfolder inside character folder.
- Audio: single full-length .mp3, libmp3lame VBR ~165kbps (`-q:a 4`).
- UI trigger: manual per-tile button "🖼 提取三视图+音频" gated by character-folder path.

Timestamps (anchored to rule #12.5 v9's 5-phase camera path; pinned in `CharacterViewSpec` constants):
- front = 1.0s (mid 0-2s static frontal intro)
- side = 7.0s (25% / 90° into 5-13s slow orbit)
- back = 9.0s (50% / 180° into orbit)

修法 (12 files, no breaking changes):

1. `libs/domain/value_objects/character_video__valueobject.py` (NEW): `CharacterViewSpec` frozen dataclass + `CANONICAL_VIEWS` tuple of 3 + `view_output_filename` / `audio_output_filename` helpers. Domain knowledge — timestamps are the algebraic image of rule #12.5 v9's camera path, must update if v10+ changes the schedule.
2. `libs/infrastructure/errors/character_video__error.py`: add `ViewExtractFailed`, `AudioExtractFailed` exceptions.
3. `libs/domain/errors/character_video__error.py`: add `ViewExtractFailedError`, `AudioExtractFailedError` named domain errors.
4. `libs/infrastructure/writers/character_video__writer.py`: append `CharacterViewExtractor` class (~200 lines, 3rd operation alongside Truncator + ShotConcatBuilder). Reuses `CharacterVideoTruncator._is_under_character_folder` for sandbox validation. Output folder mkdir + sweep `.png`/`.mp3` on each run for idempotency. 3 sequential ffmpeg view extracts (`-ss {t} -i {src} -frames:v 1 -q:v 1`) + 1 audio extract (`-vn -c:a libmp3lame -q:a 4`). Partial failures accumulate in tuple; raises only if all 4 outputs fail (parallels `FrameExtractor`'s "raise if no frames produced" semantics). New dataclasses `ViewResult` / `AudioResult` / `ViewExtractResult` with `to_payload()`.
5. `libs/application/dtos/character_video__dto.py`: add 4 new frozen Cdtos — `CharacterViewCdto`, `CharacterAudioCdto`, `CharacterViewFailureCdto`, `ExtractCharacterViewsResultCdto`.
6. `libs/application/mappers/character_video__mapper.py`: add `views_to_cdto(r: ViewExtractResult)` static method on `CharacterVideoMapper`.
7. `libs/application/commands/character_video__command.py`: add `extract_views(rel_path)` method on `CharacterVideoCommand`; `__init__` gains 3rd dep `extractor: CharacterViewExtractor`.
8. `apps/api/routes/character_video__route.py`: add `POST /api/extract-character-views` with `ExtractCharacterViewsBody{path: str}` Pydantic body. Maps 6 named domain errors to `detail.kind` strings (invalid_path / not_a_character_video / not_found / ffmpeg_missing / view_extract_failed / audio_extract_failed).
9. `apps/api/container.py`: add `character_view_extractor: Singleton[CharacterViewExtractor]`; update `character_video_command` Factory wiring to pass `extractor=character_view_extractor`.
10. `apps/ui/src/api.ts`: add 4 new TS interfaces (CharacterView / CharacterAudio / CharacterViewFailure / ExtractCharacterViewsResult) + `extractCharacterViews(path)` fetch wrapper.
11. `apps/ui/src/components/SiblingMedia.tsx`: import `extractCharacterViews`; new `CHARACTER_VIDEO_PATH_RE` + `isCharacterVideoPath` path-shape gate; new `extractingViewsPath` state; new `handleExtractCharacterViews` handler; `MediaTile` props gain `extractingViews` + `onExtractCharacterViews`; new 🖼 button rendered only when `isCharacterVideo && !archived`. Both `MediaTile` call sites (active + archived sections) wired with new props.

Verification:
- Boot smoke 7/7 pass.
- `app.routes` enumeration confirms `POST /api/extract-character-views` registered.
- E2E smoke against real character mp4 (`ai_videos/mozun_chongsheng/characters/c10_司空玄/c10_司空玄1.mp4`): 200 OK; `views = [front@1.0s, side@7.0s]`, `audio = views/c10_司空玄_audio.mp3` produced (77 KB), `failures = [('back', 'ffmpeg_failed')]`. Back failed because the source is a pre-v9 take shorter than 9s — exactly the partial-failure semantics the spec defines. Outputs landed in `ai_videos/mozun_chongsheng/characters/c10_司空玄/views/`.
- 4 unrelated test failures (`wukong_juexing` fixture missing) are pre-existing env issues, not introduced.

No spec rule changes (this is a downstream-of-v9 webapp tool, not a cross-cutting contract). No `.claude/agent_refs/` changes. No sibling mozun_chongsheng ripple needed (project-scoped feature).

## Follow-up 092 — 2026-05-18 19:49:56
Source: user_input/follow_ups/092-20260518-194956-character-ref-slow-push-in-slow-orbit.md

Trigger: user directive 「镜头由远到近，要能拍清楚脸部，而且缓慢旋转能看到侧身和背面」 — explicit reversal of 091's v8 static-camera lockdown. User rejects v8's trade-off: static frontal full-body means face never gets a close-up read (~1/6 frame is too small for casting-detail) and 侧身/背面 silhouette reference is entirely lost.

Hypothesis (the design's premise, not yet empirically validated): Kling validator's "cut/transition" rejection was triggered by **speed + direction reversal**, not motion itself. v5/v6 ran ~720°/s spin (0.5s whip-around) + 6-segment push/pull reversals; v9 caps motion at ≤ 45°/s slow orbit + monotone push-in + reverse-dolly hidden inside orbit arc.

修法 — v8 → v9 (reintroduces motion under speed + direction constraints):
- 时长 7s → 15s (room for slow push-in + slow 360° + settle)
- 镜头 line: "静态单镜头 locked camera · 零运动" → "单镜头连续运镜 single continuous take · 5 阶段连续运动 + 全程匀速 / 无方向反转 / 无定格中断"
- 5 timed beats retimed: 0-2s lock (unchanged from v8) → 2-5s slow dolly-in to medium close-up (face clear) → 5-13s slow CW 360° orbit + concurrent slow reverse-dolly to wide (侧身 + 背面 reveal) → 13-15s lock at wide (settle)
- dialogue table 5-row preserved, slot 3 (2-5s) / slot 4 (5-10s, over orbit front-half) / slot 5 (10-15s, over orbit back-half + settle) retimed
- 0-2s 一/二 byte-identical 跨角色 preserved exactly (downstream 2s truncate output identical to v8)
- 节奏: "静态" → "缓慢连续运镜 15s 内单 take, 镜头匀速运动, 全程单方向无反转"
- negatives swap (11 items): drop no-camera-motion / no-cut bans; add **slow-motion-only ≤45°/s** + **no-reversal** + **no-stop-and-go** + **no-spin-blur** Kling-validator-aware bans

Risk acknowledged in the spec: v9 is a hypothesis. If Kling still rejects uploads, retreat to v9.1 (drop 5-13s orbit, keep only 2-5s push-in, upload 5s clip) or back to v8 (7s static). 092 records both retreats as fallback paths.

修法 (3 surfaces, no ai_video_management 项目代码改动):
1. `.claude/agent_refs/project/ai_video.md` rule #12.5 v8 → v9:
   - 新「为什么 15s slow-push-in + slow-orbit single-take」rationale 段 + risk acknowledgment + v8 demoted to archive entry alongside v6/v5/v4.
   - 主 prompt 体重写: 镜头 段 "静态单镜头 locked camera · 零运动" → "单镜头连续运镜 single continuous take · 5 阶段". 动作 5 段 retimed (2-3s/3-5s/5-7s v8 → 2-5s/5-13s/13-15s v9 with motion phases). 节奏 段 "静态" → "缓慢连续运镜". 时长 7s → 15s.
   - 负向段 (11 items): drop v8 的 no-camera-motion 全禁 + no-cut 单 take 双重 ban; 加 v9 的 slow-motion-only ≤45°/s + no-reversal + no-stop-and-go + no-spin-blur + no-超过-15s 四组 Kling-validator-aware ban (含 v8 的 no-cut/no-transition + no-character-turn 保留).
   - Schema header 块 + 文件说明 line + 用法 line + 标题块 + locked-fields list 全部 v8 文案 → v9 文案 (静态 → 缓慢连续, 7s → 15s, 5-7s → 10-15s, no-camera-motion → ≤45°/s slow).
   - Dialogue table 5-row 时段 column retimed (slot 3 2-3s → 2-5s, slot 4 3-5s → 5-10s, slot 5 5-7s → 10-15s).
   - 设计原则段 "0-2s lock + 2-7s 静态单 shot" → "0-2s lock + 2-15s slow-motion single-take" with new bullets explaining slow-velocity smooth handoff between phases + face close-up read (2-5s) + multi-angle silhouette (5-13s) features that v8 lacked.
   - 0-2s 自包含 段补 v9 加入共同契约 list (v5/v6/v8/v9) + 明确 0-2s 在 v8 + v9 完全相同, 下游 webapp 2s 切片输出不变.
   - 末尾 attribution 段加 v9 rev (092 — 2026-05-18 晚段, supersedes v8).
2. `specs/development/ai_video_management/user_input/revised_prompt.md` — header bump 092 (v9 hypothesis + 5-phase design + risk acknowledgment).
3. `specs/development/ai_video_management/changelog.md` — 本条目.

Sibling cross-project ripple:
- `specs/ai_video/mozun_chongsheng/user_input/follow_ups/025-20260518-194956-character-ref-15s-slow-orbit.md` — sibling follow-up (supersedes 024's v8 patch; new v9 patch for the same 10 character md files).
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — header bump.
- `specs/ai_video/mozun_chongsheng/changelog.md` — entry.

**Out-of-band user steps** (not in this turn):
- Patch `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md` 10 files via one-shot script (parallel to 091's `/tmp/patch_chars_v8.py`): v8 5-segment static dynamics → v9 5-phase slow-motion dynamics, 时长 7s → 15s, 镜头 line static-declaration → continuous-motion-declaration, dialogue table slot times retimed, negatives swap. Each character's existing bible 标志台词 #1 + #2 (already plugged in by 088 → 091) stay in slots #4 + #5 with new time windows (now 5-10s / 10-15s).
- Re-render 10 turntable mp4 files at 15s with the new prompt + upload to Seedance / Kling reference channel for empirical validator validation. If accepted, v9 confirmed; if rejected, fall back to v9.1 (push-in only, 5s) or v8 (7s static).

Numbering note: v8 (091) → v9 (092), no skip. v8 is demoted to archive entry but the 091 follow-up file + mozun_chongsheng/024 sibling stay on file as audit trail of the static-camera retreat that 092 reverses.

修法 (no ai_video_management 项目代码改动): ai_video_management webapp 不变 — 2s trim path 仍 slices byte-identical first 2s (0-2s segment 在 v8 + v9 完全相同).

## Follow-up 091 — 2026-05-18 00:15:44
Source: user_input/follow_ups/091-20260518-001544-character-ref-7s-static-camera-kling-compat.md

Trigger: user reported Kling 拒收 v6 15s casting reel uploads with:
> the current video contains cuts or transitions, and no clear, complete character is detected, please upload a single shot clear character video

诊断: v5 4s / v6 15s / planned v7 7s 全部在 0-2s 段做 fast 360° orbit, validator 判 cut/transition + spin blurs character detector miss subject。v6/v7 在 tail 加 push-in/pull-out/pan, 同样判 transitions。Every prior version structurally violates Kling 的 single-shot constraint。

修法 — v6 → v8 (skip v7): **完全弃 multi-camera ambition, 走 7s 全程静态正面单镜头 single take**:
- 5 段 timed beats 全部以「同机位同构图」开头 (anti-cut 显式语义)
- 0-2s 段保 一/二 byte-identical 跨角色 truncate-compat, 但**弃 v5/v6/v7 的 0-2s 360° silhouette pass** (incompatible with single-shot rule) — 用户接受 truncate output 降级为 frontal voice baseline
- 2-7s 段 per-character: 三 + 自报姓名 / 标志台词 #1 baseline / 标志台词 #2 catch+peak+final-lock
- Negatives 加 no-camera-motion + no-cut/transition + no-turn-in-place 三组 Kling-validator-aware ban
- 8-row dialogue table → 5-row

Numbering note: 本 turn 原 spec'd v7 (follow-up 090, 7s 3-camera-move casting reel) 在 user 报 Kling 反馈后 superseded before implementation。090 + sibling mozun_chongsheng/023 文件标 SUPERSEDED 留作 audit trail; 实际改动走 091 + mozun_chongsheng/024。

修法 (3 surfaces, no ai_video_management 项目代码改动):
1. `.claude/agent_refs/project/ai_video.md` rule #12.5 v6 → v8 (跳 v7):
   - 新「为什么 7s static-camera single-shot」rationale 段 + v7-superseded explanation + v6 archive 段 + v5/v6/v8 共同 "前 2s 自包含" 契约段。
   - 主 prompt 体重写: 镜头 段从 6-camera-move enumeration → "静态单镜头 single take · 锁定机位 ..." declaration。
   - 动作 段从 7-segment 15s casting reel → 5-segment 7s static block (全部以「同机位同构图」开头)。
   - 台词 enumeration 从 8 行 → 5 行。
   - 节奏 段从 "分段 (15s 内 ...)" → "静态 (7s 内无任何镜头运动 + 无任何 cut / transition ...)".
   - 时长 15s → 7s。
   - 负向 段 drop v6's "不要 跳过任何 6 个 camera-move 段" + "不要 镜头回切倒退（要单向 360°）"; 加 v8's "不要 任何镜头运动" + "不要 任何 cut / transition" + "不要 角色转身 / 走动 / 大幅度肢体动作"; swap "不要 超过 15s" → "不要 超过 7s"。
   - 8-row 对照表 → 5-row。
   - 设计原则段 + locked-fields 段 + footer attribution 全部 v8 重写。
2. `specs/ai_video/mozun_chongsheng/user_input/follow_ups/024-{ts}-character-ref-7s-static-camera-kling-compat.md` sibling follow-up (supersedes 023)。
3. `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md` patch via `/tmp/patch_chars_v8.py`: 标题/文件说明/镜头/动作/台词/节奏/时长/负向 + 5-row 对照表 + 6-line stripper 清除 v5 360°-related negatives 残留。

Smoke:
- 10/10 character files: 镜头 line 已是 "静态单镜头 single take..." ✓
- 0/10 files 含 v6/v5 stale 标记 (`15s casting reel` / `6 段 camera-move` / `全身远景起手`) ✓
- 0/10 files 含 v5 360°-related negatives (`不要 镜头回切倒退` / `不要 全身在快速环绕中被裁切` / `不要 横向运镜大偏移`) ✓
- c1 沧冥 spot-check: slot 4 = "当年你们怎么对我，今日我便十倍奉还" / slot 5 = "本尊从不解释，只清算" ✓
- 5-row dialogue table 全部 10 个 ✓
- 时长: 7s 全部 10 个 ✓

Pre-v8 multi-camera ambition 完全弃。无 backward-compat — 历史 4s v5 / 15s v6 rendered mp4s 不动 (user 按需 re-render 到 7s static)。HTTP routes + JSON shapes + ai_video_management 项目代码 byte-identical (无 webapp 改动)。

Auto-updated:
- .claude/agent_refs/project/ai_video.md — rule #12.5 v6 → v8 全条 patched (含 footer 091 attribution + 090-v7-superseded 备注)。
- ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md — 10 个文件 v8 schema 应用。
- specs/ai_video/mozun_chongsheng/user_input/follow_ups/024-... — sibling follow-up。
- specs/ai_video/mozun_chongsheng/changelog.md — entry。
- specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md — header bump。
- specs/development/ai_video_management/user_input/follow_ups/090-... — marked SUPERSEDED at top (kept as audit trail)。
- specs/ai_video/mozun_chongsheng/user_input/follow_ups/023-... — marked SUPERSEDED at top。
- specs/development/ai_video_management/user_input/revised_prompt.md — header bump 091。

No conflicts found in:
- `projects/ai_video_management/libs/infrastructure/writers/character_video__writer.py` — 2s trim + concat path 不动; v8 源 mp4 静态 + 一/二 仍 satisfies 0-2s self-sufficient 契约 (just 不再有 360° silhouette pass)。
- ai_video_management webapp UI/code — 不动。
- 其他 ai_video 项目 (如未来 sibling project) — agent_refs 规则 v8 update 直接 inherit。
- final_specs/spec.md / interview/qa.md / findings/* / validation/* — 时长 / 镜头 实现细节非 spec-level。
- 历史 rendered 4s/15s mp4 — 不动; user 按需 re-render 到 7s static。

## Follow-up 089 — 2026-05-17 23:45:00
Source: user_input/follow_ups/089-20260517-234500-stale-backend-blocking-half-body-fixes.md
Summary: 用户："Kling 调出来一直 portrait / half-body, 不是全身". 诊断: 代码端 085 + 087 fix 已经全部在磁盘上, 但用户最近一次生成的 `ai_videos/_actors/actor_0141/actor_0141.md` (今天 22:12 生成) 的 sidecar prompt 是 PRE-085/PRE-087 的旧格式 — 第一行 `镜头【强制 MANDATORY · 全身从头到脚】...`, 含 `85mm f/1.4 人像镜头` 和 `严禁 portrait` baked-in positive prompt — 这些字符串在当前 source 里 `grep` 0 matches。`actor_0141.md` 是在生成那一刻写出的, 内容反映真正 ship 给 Kling 的 prompt — 证明 backend uvicorn 进程加载的是旧 module (Python module cache, 不会自动 reload), 080-087 期间所有 prompt 文件 edit 都没被 in-memory module pick up。"还是 half-body" 不是 085/087 的 structural fix 不够, 而是 fix 从来没被运行时加载。

Action: 用户重启 backend (`uvicorn` 或 docker container 或者无论用什么 launcher), 生成 ONE 测试 actor, 检查新生成的 `actor_NNNN.md` 第一行是否为 `镜头：full body shot · head to toe · 9:16 vertical · long shot · 全身照` (087 的 `_POSITIVE_COMPOSITION_TAG`)。如果是 → fix is live, 看 JPG 判断 Kling 实际 framing。如果仍是 chest-up, 才考虑升级 `KLING_DEFAULT_MODEL = "kling-v1"` 到 newer 模型 — 但这是 separate follow-up, 不在 089 范围。

代码改动: 0 (085 + 087 已经完整在 disk 上, 不需要再 edit prompt builder)。089 唯一的 deliverable 是诊断记录 + future-proof convention: "每次 prompt 文件 edit 后, 下一次生成的 sidecar md 是 ground truth — 如果 sidecar 不含新 string, backend 没 pick up, 重启后再下结论"。

Auto-updated:
- specs/development/ai_video_management/changelog.md — this entry.
- specs/development/ai_video_management/user_input/follow_ups/089-20260517-234500-stale-backend-blocking-half-body-fixes.md — created.

No conflicts found in: interview/qa.md, findings/dossier.md, final_specs/spec.md, validation/strategy.md, projects/ai_video_management/libs/* — 089 是 operational diagnosis, 不触发 surgical patch downstream。

## Follow-up 088 — 2026-05-17 23:13:50
Source: user_input/follow_ups/088-20260517-231350-character-ref-15s-proper-casting.md
Summary: 用户："lets change the charactor video prompt to from 4s to 15s, ... let the charactor speak a lot more than 1,2,3. but since I have a use case to also need to truncate the vidoe to 2s, so lets make sure we have a proper first 2s, and charactor speak 1,2 at least, and then you can use the result of time, to show more angle of the charactor in casting and let him talk more". 升级 character reference turntable 从 v5 4s → v6 **15s casting reel**，给每个角色更多时间做 proper casting (6 个 camera angles + 角色 bible 自己的 3 句标志台词 + 表情 range silent capture + 标志特征点 final-lock close-up)。**保留** v5 的 0-2s 自包含契约 byte-identical 跨角色 — `_CONCAT_SEGMENT_S = 2.0` 短角色合辑 + `✂ 截到 2s` 按钮 (`_TRUNCATE_DURATION_S = 2.0`) 切到的前 2s 仍含 "一 + 二 + 正面定场 + 360° 回正"，跨 10+ 角色 voice baseline 可对齐。

**No code change to webapp** — `character_video__writer.py` 的 2s trim path 已经 do what 088 needs (slices 0-2s)。新 15s 源 mp4 只是在 2s 标记之后有更多内容; truncator 不 care。

修法 — 此 follow-up 为 cross-cutting rule update + mozun_chongsheng 项目 ripple, 不动 ai_video_management 项目代码:
1. **`.claude/agent_refs/project/ai_video.md`** rule #12.5 v5 → v6:
   - "为什么 N 硬上限" 段重写: v6 = 15s casting reel, ref upload ceiling 2026-05 中旬放宽到 ≥ 15s 同 rule #12.10 v3 dim-comparable; v5 archive 段保留作历史交代。
   - "为什么前 2s 必须自包含" 段标注为 v5/v6 共同契约。
   - 文件位置约定 schema 注释从 "4s turntable + 一, 二, 三 数字计数台词" → "15s casting reel + 0-2s 一/二 lock + 2-15s per-character dialogue from 标志台词"。
   - 主 prompt 体重写: 7 段 timed-beats (was 4 段)，0-2s = 一/二 lock byte-identical, 2-3s = 三 + 自报姓名, 3-5s = 反向 90° + 标志台词 #1, 5-8s = 3/4 侧像 + 标志台词 #2, 8-11s = 横向 pan + 表情 range silent, 11-13s = medium close-up + 标志台词 #3, 13-15s = 推至特写 + catch-phrase close。
   - 镜头 段从 "全身远景起手 + 360° + 推近" 一句话扩成 6-camera-move 结构枚举 (① 全身远景 360°, ② 推近, ③ 反向 90°, ④ 拉远 3/4, ⑤ 横向 pan 360°, ⑥ 推至特写)。
   - 节奏 段重写: "分段（15s 内: 0-2s 极速定场 + 360° 锁定 truncate-compat / 2-15s 较慢 casting reel ...）"。
   - 时长: 4s → 15s。
   - 负向 段去掉 "不要 超过 4s（v5）", 加 5 条 v6 新增: "不要 超过 15s（v6）/ 不要 把 一/二 延后到 2s 之后 / 不要 在 0-2s 段加入额外台词 (保 truncate byte-identical) / 不要 跳过任何 6 个 camera-move 段 (结构性破坏 casting reel) / 不要 让任何台词 over-emote 至失真 (声线 baseline 优先)"。
   - 配音对照表 4 行 → 8 行 (0-2s lock byte-identical 跨角色 + 2-3s 三 + 自报姓名 + 3 个 character-specific 标志台词 slots + 8-11s silent 表情 range + 13-15s catch close)。
   - 设计原则段重写: "0-2s lock + 2-15s casting reel 设计原则"。
   - Locked-fields 段重写: 仍 9 字段 byte-identical, 但加 `台词 0-2s` byte-identical 跨角色 + `台词 2-15s` per-character (取自 bible) 的明确 carve-out。
   - Footer 加 `rev — ai_video_management follow-up 088 — 2026-05-17: rule #12.5 v6 ...` lineage line。
2. **`specs/ai_video/mozun_chongsheng/user_input/follow_ups/022-{ts}-character-ref-15s-casting-reel.md`** 新 sibling follow-up: 把 v6 schema 应用到 10 个 character md files, 每角色 bible 中的 3 句 `## 标志台词或口头禅` plug 入 3-5s / 5-8s / 11-13s slots, 最短一句 reuse 作 13-15s catch close。
3. **10 个 character md files** (`ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md`): 经一次性 Python 脚本 (`/tmp/patch_chars_15s.py`, 临时 not shipped) 应用 v5 4-segment dynamics block → v6 7-segment block + 4-row dialogue table → 8-row table + 标题/文件说明/节奏/时长/负向 line uniform header edits。每角色的 3 句台词从其 bible 自身 `## 标志台词或口头禅` 段提取 (剥离 trailing 中文 parenthetical context), 自动 plug 入。
4. **`specs/ai_video/mozun_chongsheng/changelog.md`** 追加 entry。
5. **`specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md`** header bump。

Smoke:
- 10/10 character files 应用了 v6 dynamics block ("动作（timed beats，15s ...) ✓
- 0 个文件残留 v5 dynamics 4s opener ✓
- c1 沧冥: slot 4 = "当年你们怎么对我，今日我便十倍奉还" / slot 5 = "本尊从不解释，只清算" / slot 7 = "无情无怒，才是最大威压" / slot 8 = "本尊从不解释，只清算" (shortest reused) ✓
- c10 司空玄: slot 4 = "你前世并非全清白" / slot 5 = "道在何处？道在阴影里" / slot 7 = "本座只是看着" / slot 8 = "本座只是看着" (shortest reused, after parenthetical strip) ✓
- 时长 line: 4s → 15s 全 10 个 ✓
- 负向 line: 加 5 条新 v6 negative ✓
- 8-row dialogue table 全 10 个 ✓

Auto-updated:
- .claude/agent_refs/project/ai_video.md — rule #12.5 v5 → v6 全条 patched。
- ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md — 10 个文件 dynamics + table + header edits。
- specs/ai_video/mozun_chongsheng/user_input/follow_ups/022-... — sibling follow-up。
- specs/ai_video/mozun_chongsheng/changelog.md — entry。
- specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md — header bump。
- specs/development/ai_video_management/user_input/revised_prompt.md — header bump 088 + Composed-from 段追加。

No conflicts found in:
- `projects/ai_video_management/libs/infrastructure/writers/character_video__writer.py` — 2s trim path (_CONCAT_SEGMENT_S = 2.0) 和 truncate path (_TRUNCATE_DURATION_S = 2.0) 不动; 新 15s 源 mp4 走相同 trim logic, 切到的 0-2s 仍 self-sufficient。
- ai_video_management webapp UI/code — 不动; 显示的 mp4 时长从 4s 变 15s 是 user-rendered media metadata 变化, 与 webapp 渲染无关。
- 其他 ai_video 项目 (如未来 sibling project) — agent_refs 规则 update 直接 inherit, 走相同 v6 schema。
- final_specs/spec.md / interview/qa.md / findings/* / validation/* — 时长 数字非 spec-level, 概念契约 ("character video reference") 不变。
- 历史 rendered 4s mp4 — 不动; user 按需 re-render 个别角色到 15s。

## Follow-up 087 — 2026-05-17 22:35:38
Source: user_input/follow_ups/087-20260517-223538-negative-prompt-split-shorten-positive.md
Summary: 用户："生成的图片还是只有上半身" (post-085 canvas fix). 085 fix 了 canvas → 9:16 + 把 `定妆照` swap 了 + 重写了 photography pool — 图像确实回来 9:16 了, 但 SUBJECT 在 9:16 frame 内仍是 chest-up composition。诊断: 我们 080-083 一直在 prompt 层 escalate ("更大声地告诉 Kling 全身"), 但实际上 prompt 越长越糟糕, 因为:

1. **Negative-tokens-in-positive-prompt 是 diffusion-model 反模式**。扩散模型解析每个 token 的 semantic 含义, 不解析否定 context。在 positive prompt 写 `严禁 portrait` / `不要 头肩` / `生成失败 = portrait crop` **把 `portrait` token 注入到模型的 attention pool**。模型在 1660 字 prompt 里反复看到 `portrait`, 逐步漂向它看到最多的概念。081/082/083 每轮 escalate 都让这个 antipattern 更严重。
2. **Kling 的 `negative_prompt` API field 没用上**。Submit body 一直只有 `{model_name, prompt, aspect_ratio, n}` 4 个字段。kling-v1 接受 `negative_prompt` 作为 dedicated field, 有独立 negative attention pass。所有 `严禁/不要/失败/portrait/half-body/close-up/crop` token 应该走 negative_prompt, 不应该污染 positive attention。
3. **Positive prompt 1660 字超 Kling effective attention budget** (~500-800 chars typical), 真正的 subject description 被 framing instruction 淹没。

Numbering: 本 turn 原 slot 086 撞上 parallel "actor-grid-assigned-filter" follow-up (`is_assigned` DTO field 已存在), renumber 到 087。slot 084 撞过 "delete-toast-never-disappears" frontend fix, slot 086 撞 "assigned filter chip" — 现在 actor pipeline 系列连续 077/078/079/080/081/082/083 → 085 → 087, 留 086 给已 ship 的 grid filter, 留 084 给 ship 的 toast fix。

修法 (3 文件):

1. **`libs/infrastructure/writers/actor__writer.py`**:
   - `KlingProvider.generate(prompt, seed, width, height, negative_prompt=None)`: 新增 optional `negative_prompt`。Docstring 说明 087 antipattern fix。
   - `KlingProvider._submit(... negative_prompt=None)`: 当 non-empty 时 `body["negative_prompt"] = negative_prompt`。Backward-compat — None 时 body shape byte-identical to pre-087。
   - `ActorPool._build_prompts_for_slot(...)` 现返回 3-tuple `(face_prompt, body_prompt, negative_prompt)` (was 2-tuple)。negative 在 face + body 之间共享 (composition / photorealism / wardrobe-fallback bans 对两个 shot 都适用)。
   - 新 module-level `_shared_negative_prompt() -> str` thin wrapper around `actor__chinese_prompt.build_negatives()` — lazy import 避免 chinese-prompt 模块在 actor__writer import time 加载。
   - `preview_prompts`: each slot payload 加 `negative_prompt` 字段 (visibility for the preview pane)。
   - `generate_batch` (standard mode): 把 `neg_prompt` 透传到 `self._provider.generate(...)` 的 face + body 两次调用。
   - `preview_diverse_prompts` (diverse mode): 每 slot payload 加 `negative_prompt: _shared_negative_prompt()`。
   - `generate_diverse_batch` (diverse mode): 同样把 `neg_prompt = _shared_negative_prompt()` 透传到 face + body 两次 Kling 调用。

2. **`libs/infrastructure/writers/actor__chinese_prompt.py`**:
   - **删除** `_NEGATIVES_ZH` (was 8-line 严禁/避免/媚态 内含 negative-in-positive antipattern)。
   - **删除** 3 个 framing-mandate 常量 `_LEADING_FRAMING_MANDATE` / `_RESTATE_FRAMING_MANDATE` / `_TAIL_FRAMING_MANDATE` (083 引入, 现 superseded — 它们 contain "严禁 portrait" / "生成失败" / "不合格" tokens, 都是 antipattern)。
   - **新增** `_NEGATIVE_PROMPT_ZH` 常量 (~390 chars): comma-separated EN + ZH token list, 内容覆盖 composition negatives (`portrait, half body, headshot, close-up, head and shoulders, head-shoulder crop, upper body only, chest up, waist up, cropped feet/legs/hands/head, head too large, body too small`) + photorealism / anti-AI-face (was old _NEGATIVES_ZH leading list: `塑料感皮肤, 蜡像感, 卡通比例...`) + wardrobe-fallback bans (was 080 addition: `宽松衣物, T 恤, 长裤, 长裙, 大衣, 厚外套`) + glamour drift (was 080 addition: `故意性感姿势, 媚态, 内衣广告, glamour pose`) + generic quality (`blurry, low quality, deformed, extra limbs`)。EN + ZH 都有 — Kling-v1 双语训练, 任一边都能 catch。Plain comma-separated tokens (无 `严禁/不要/不合格` 装饰)。
   - **新增** `build_negatives()` public helper returning `_NEGATIVE_PROMPT_ZH` (future-proof for per-archetype/per-attrs negative tuning)。
   - **新增** `_POSITIVE_COMPOSITION_TAG` 常量 (~80 chars): `镜头：full body shot · head to toe · 9:16 vertical · long shot · 全身照` — canonical diffusion-model composition keywords, positive-only。Replaces 3 framing-mandate 常量 (减 ~600 chars)。
   - **4 builder variants 重写** (`build_face_prompt`, `build_body_prompt`, `build_face_prompt_with_picks`, `build_body_prompt_with_picks`):
     - Line 0 = `_POSITIVE_COMPOSITION_TAG` (was 3 lines `_LEADING + _RESTATE` + descriptor wrap)。
     - Line 1 = 简化 descriptor `正面全身模特造型照 / fashion comp card full-body shot：{ethn} {gender}，{age}` (去掉 `**【强制全身】**` markdown-bold + `（远景 wide / long shot · 整图必须包含头顶到脚趾 zero-crop · ...）` 括号 enumeration)。
     - 姿态 line 去掉 `头部清晰可辨, 双手 + 双脚 完整入框不可被裁切` (now in negative_prompt)。
     - 画面 line 简化 `9:16 竖屏, 头顶到脚趾完整入画, 头部 1/5 + 身体 4/5, 中性纯灰背景` (去掉 `~5% 顶边 / 双脚下方留 ~5% 底边` 细节)。
     - **删除** trailing `_TAIL_FRAMING_MANDATE` + `_NEGATIVES_ZH`。
   - Positive prompt 长度 1660 → ~750 chars (-55%)。

3. **`libs/application/dtos/actor__dto.py`** — touch only `PreviewPromptQdto` to optionally carry `negative_prompt` (deferred to next turn if frontend needs preview-pane visibility; current `preview_prompts` payload already includes the field as a top-level dict key in `{seed, prompt, body_prompt, negative_prompt}`)。

Smoke (`preview_prompts` end-to-end with `batch_seed=7777, batch_size=10, slot_index=3`):
- Positive prompt 762 chars (was 1660) ✓
- Positive contains `严禁`: False ✓
- Positive contains `不要`: False ✓
- `negative_prompt` payload field present (392 chars) ✓
- Negative starts: `portrait, half body, headshot, close-up, head and shoulders, ...` ✓
- `_shared_negative_prompt()` returns same ✓
- DummyProvider asserts neg_prompt threaded through `.generate(...)` ✓
- pytest 15 pass / 3 pre-existing wukong fixture failures (= 085 baseline, 0 regressions)。

Pre-087 framing constants + `_NEGATIVES_ZH` block fully superseded — 无 backward-compat shim。Look bias (077) / minimal wardrobe (080) / batch coordination (082) / canvas 9:16 + photography pool (085) 全部 unchanged — 新 negative_prompt + slim positive 仅清理 prompt engineering antipattern, 不动 pool 抽样 / canvas / wardrobe / bias 路由。

Auto-updated:
- projects/ai_video_management/libs/infrastructure/writers/actor__writer.py — KlingProvider `generate/_submit` accept negative_prompt + `_build_prompts_for_slot` 3-tuple + `_shared_negative_prompt` module helper + 4 generate-path sites (standard preview/generate + diverse preview/generate) plumb neg_prompt。
- projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py — delete `_NEGATIVES_ZH` + 3 framing-mandate 常量 + 新 `_NEGATIVE_PROMPT_ZH` + `build_negatives()` + `_POSITIVE_COMPOSITION_TAG` + 4 builder rewrite。
- specs/development/ai_video_management/user_input/revised_prompt.md — header bump 087 + Composed-from 段追加。

No conflicts found in:
- `_kling_aspect_ratio` (085 fix — 720x1280 → "9:16") — unchanged。
- `_resize_jpeg` aspect-preserving (085) — unchanged。
- `_LOOK_FEATURE_BIAS_ZH` / `_LOOK_OVERLAY_ZH` / `_SYNTHESIS_BY_ARCHETYPE` / `_BODY_BIAS_BY_ARCHETYPE` / `_BIAS_WILD_PROB` / `_classify_actor_attrs` / `_casting_wardrobe` / 7 face-body pools / `_CASTING_REQUIREMENTS_ZH` / `_PHOTOGRAPHY_ZH` (085 wide-angle rewrite) — 全部 untouched。
- `_batch_sample_pool` / `_resolve_batch_picks` / `_build_with_picks_lines` — 全部 unchanged。
- HTTP routes / response shapes (additive `negative_prompt` field in preview slot — backward-compat for clients that ignore unknown fields)。
- Frontend ActorPoolGenerator / ActorGrid / ActorView / api.ts — 不动 (preview pane 现 receives `negative_prompt` field 但不渲染; future polish 加 negative-prompt section 渲染)。
- Parallel slots 084 (toast TTL fix) + 086 (assigned filter chip) — 不动。
- final_specs/spec.md / interview/qa.md / findings/* / validation/* — 概念契约 ("full-body comp-card reference") 不变, prompt-engineering 实现细节非 spec-level。

## Follow-up 086 — 2026-05-17 22:20:00
Source: user_input/follow_ups/086-20260517-222000-actor-grid-assigned-filter.md
Summary: ActorGrid (`/actors` 路由) 加 "分配状态" filter dropdown — 全部 / 🎬 已分配 / ⚪ 未分配。Backend `GET /api/actors` payload 加 `is_assigned: bool` 字段，每个 actor 标记是否在任一 drama 的 `casting.md` 出现。Tile 右上角加 🎬 小 badge "全部" 模式下也能一眼区分已用 vs 空闲 actor。

Backend:
- `libs/infrastructure/writers/casting__writer.py`: 新 `Casting.assigned_actor_ids() -> set[str]`，单次扫所有 drama casting.md (跳 `_`-prefix 系统 folder)，返回 actor_id union。
- `libs/domain/repositories/casting__repository.py`: Protocol 加 `assigned_actor_ids() -> set[str]` declaration。
- `libs/application/dtos/actor__dto.py` `ActorListRowQdto`: 加 `is_assigned: bool = False` field（default False 向后兼容）；`to_dict()` 输出加 `"is_assigned"`。
- `libs/application/mappers/actor__mapper.py`:
  - `info_to_qdto(info, is_assigned=False)` 加 kwarg。
  - `list_to_qdto(infos, assigned_ids=None)` 可选 set；提供则 per-row `is_assigned = info.id in assigned_ids`。
- `libs/application/queries/actor__query.py` `ActorQuery.list()`: 取 `assigned_ids = self._casting.assigned_actor_ids()` 一次，passed 给 mapper。

Smoke test:
- 临时 repo 含 2 drama × 各 1 casting.md (一共 3 actor 行 actor_0001 ×2 + actor_0002 ×1)；`Casting.assigned_actor_ids()` 返 `{actor_0001, actor_0002}` ✓
- AST + 模块 load 全 5 backend 文件无错 ✓

Frontend:
- `apps/ui/src/api.ts` `ActorInfo`: 加 optional `is_assigned?: boolean`。
- `apps/ui/src/components/ActorGrid.tsx`:
  - 新 state `filterAssigned: "all" | "assigned" | "unassigned"`。
  - `filteredActors` predicate 加 `if (filterAssigned === "assigned" && !a.is_assigned) return false; if (filterAssigned === "unassigned" && a.is_assigned) return false`。
  - filter row 加第 4 个 dropdown "分配状态"（与 民族/性别/年龄段 平行 pattern）。
  - page reset effect dep 加 `filterAssigned`。
  - 每个 tile 的 `actor-tile-id` 行末加 🎬 badge（`actor.is_assigned` 时显示）。
- `apps/ui/src/styles.css`:
  - `.actor-tile-id` 改 `display: flex + align-items: center + gap: 6px`。
  - 新 `.actor-tile-assigned-badge { font-size: 11px; opacity: 0.85; line-height: 1; }`。

No conflicts found in:
- follow-up 043 (`_cast.md` write contract + casting flow) — 沿用既有 `Casting._parse` 解析 casting.md row 的 actor_id 字段；新 `assigned_actor_ids` 复用同 parser。
- follow-up 053 (diverse mode archetype filter) — ActorGrid 既有 archetype filter 与新 assigned filter 平行无冲突。
- follow-up 067/064 (look enum + Chinese labels) — ActorListRowQdto 字段加是向后兼容；既有字段不动。
- follow-up 084 (delete-toast) + 085 (half-body root cause) — 与本 follow-up 正交；本 follow-up 不动 actor generation / sidecar / delete flow。

`is_assigned` 是 payload 字段新增，老前端忽略字段（typescript optional），新前端解析。Container.py 无改（`ActorQuery` 既有 `casting` 注入）。

User-input:
- `user_input/follow_ups/086-20260517-222000-actor-grid-assigned-filter.md` (NEW; originally numbered 084 — 与用户 parallel 084 + 085 撞号，本 follow-up renumber 至 086)。

## Follow-up 085 — 2026-05-17 22:18:15
Source: user_input/follow_ups/085-20260517-221815-fix-half-body-root-cause.md
Summary: 用户："为什么生成的actor照片还是半身照"。用户贴了 084 之后的实际 prompt — 4 个 framing anchor 完整 (lead + restate + descriptor + tail), 但生成结果仍是半身照。诊断: prompt 文本无法 override **3 个结构性 root cause** — 我们之前 080-084 一直在 prompt 层面 escalate (越来越大声地告诉 Kling "全身"), 但 Kling 收到的 API 请求几何上不允许全身:

1. **Face shot canvas = 1:1 (512x512)** — 人体头到脚解剖学上没法塞进方画幅, Kling 的 compositional sampler 解 "human subject + 1:1 canvas" 必然 → 头肩 / 胸上 / 半身 crop。`_kling_aspect_ratio(512,512)` → "1:1" 上传 Kling API → portrait 优先级 hard-locked at API layer。Body shot 用 576x1024 (9:16) — 那张大概率是全身, 用户只是在看 face JPEG。
2. **"定妆照" 是 Chinese beauty-headshot prior** — 中文摄影 taxonomy 里 「定妆照」压倒性指 face/headshot (TV/电影 production 拍演员妆容时用)。`全身` 修饰词压不住 noun-level prior。
3. **`_PHOTOGRAPHY_ZH` 10 entries 一半 actively bias portrait** — 85mm 人像镜头 / 哈苏中画幅人像 / Portra 400 (世上最有名的人像胶片) / 105mm / SX-70 (方画幅)。用户 paste 的 prompt picked Portra 400 → 模型当然生成 portrait, 我们在 prompt 体里 explicit 选择了人像胶片。

Numbering note: 本 turn 原 slot 084 撞上 parallel "is_assigned filter chip" follow-up (DTO + query + api.ts 已有 "Per follow-up 084" comments 但 follow-up 文件 yet-uncreated), renumber 到 085 避免主题 collision。

修法 (2 文件):
1. **`libs/infrastructure/writers/actor__writer.py`**:
   - `IMAGE_WIDTH/IMAGE_HEIGHT`: 512x512 → **720x1280** (face shot now 9:16 capable, 短视频原生 res)。
   - `IMAGE_WIDTH_BODY/IMAGE_HEIGHT_BODY`: 576x1024 → 720x1280 (统一两个 shot 同 res, 同 aspect)。
   - `_kling_aspect_ratio(720, 1280)` 自动 → "9:16" sent to Kling API — canvas geometry now agrees with prompt-body 9:16 line。
   - `_resize_jpeg(jpeg_bytes, target_px)` rewrite: 旧版 `img.resize((target_px, target_px))` forced square; 新版 scale 最长边到 `target_px`, 短边按 source aspect 推 — `720x1280 + "2k" → 1152x2048`, `720x1280 + "4k" → 2304x4096`。Docstring 重写, 注释 follow-up 084 (现 085)。
2. **`libs/infrastructure/writers/actor__chinese_prompt.py`**:
   - 4 个 builder variant 的 descriptor 行 `**【强制全身】**正面全身定妆照` → `**【强制全身】**正面全身模特造型照 / fashion comp card full-body shot` (replace_all)。「模特造型照」/「fashion comp card」 是 talent-agency body-evaluation 行业术语, 无 headshot prior。
   - `_CASTING_REQUIREMENTS_ZH` 开头 `全身定妆 comp-card 标准照` → `全身模特造型照 / fashion editorial full-body shot`。
   - `_PHOTOGRAPHY_ZH` 10 entries 全部重写: 35mm 全身广角 / 24mm 全身镜头 / 28mm 全身 / 50mm 全身大画幅 / Ektar 100 (landscape film) 35mm 全身 / Cinestill 50D 35mm 全身 / 28mm 全身抓拍 / iPhone 0.5x 超广角 全身 / 35mm 全身镜头 / 32mm 全身中画幅。每个 entry: 焦距 24-50mm (从无 85mm/105mm 人像镜) + 显式「全身」cue + 弃 Portra 400/SX-70 这种 portrait 胶片 prior + 保留 074/077/080 依赖的 真实质感 / 真实毛孔 / 化学色偏 anti-AI-face 锚点。

Smoke:
- Canvas: face 720x1280 (ratio 0.5625) + body 720x1280 (0.5625) == 9:16 target (0.5625) ✓
- _PHOTOGRAPHY_ZH portrait-bias hits: 0/10; 全 10 entries 含「全身」 ✓
- 4 builder variant 全部 `定妆照=False / 全身模特造型照=True` ✓
- `_resize_jpeg(720x1280 source, 2048)` → (1152, 2048) ✓; `(..., 4096)` → (2304, 4096) ✓
- pytest: 15 pass / 3 pre-existing wukong fixture failures (= 083 baseline, 0 regressions)

Pre-085 1:1 face canvas + 定妆照 prior + portrait photography pool 完全替换, 无 backward-compat shim。历史 1:1 generated JPEG 不动 (user 按需 regenerate); 新 generate 走 9:16 canvas + 模特造型照 descriptor + wide-angle 全身 photography cue, 三层全部 agree → Kling 不再有 portrait-favoring 信号。

HTTP routes + JSON shapes + endpoint behaviors byte-identical (canvas dims 仅 internal; preview pane JPEG src URL 路径不变; ActorGrid / ActorView 渲染任何 aspect 的 JPG, frontend 无 change)。Look bias (077) / minimal wardrobe (080) / batch coordination (082) / triple-anchor framing (083) 全部 unchanged — 新 canvas + 新 descriptor + 新 photography pool 只是 align 三层 signal, 不动 pool 抽样 / bias 路由 / batch 协调 / anchor 文本。

Auto-updated:
- projects/ai_video_management/libs/infrastructure/writers/actor__writer.py — canvas constants + `_resize_jpeg` aspect-preserving。
- projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py — descriptor swap (4 builders) + `_CASTING_REQUIREMENTS_ZH` + `_PHOTOGRAPHY_ZH` (10 entries rewrite)。
- specs/development/ai_video_management/user_input/revised_prompt.md — header bump 085 + Composed-from 段追加。

No conflicts found in:
- `_kling_aspect_ratio()` mapper — 自动 derive "9:16" from 720x1280 (existing mapping)。
- `ActorPool.preview_prompts` / `generate_batch` / `_build_prompts_for_slot` (082 dispatcher) — width/height 直接从 IMAGE_WIDTH/IMAGE_HEIGHT 常量读, 自动跟随。
- `_LOOK_FEATURE_BIAS_ZH` / `_LOOK_OVERLAY_ZH` / `_SYNTHESIS_BY_ARCHETYPE` / `_BODY_BIAS_BY_ARCHETYPE` / `_BIAS_WILD_PROB` / `_classify_actor_attrs` / `_casting_wardrobe` / 7 face-body pools — 全部 untouched。
- Frontend (`ActorPoolGenerator.tsx` / `ActorGrid` / `ActorView` / `api.ts`) — JPEG dimensions 变化 但 file format + filename convention + sidecar shape 不变, React 自动适配新 aspect ratio (no layout breakage; `<img>` 默认 preserve-aspect)。
- Parallel "follow-up 084" (is_assigned filter chip) 在 DTO + query + api.ts 留的 "Per follow-up 084" comments — 不动, 等其 own follow-up 文件 land 后会成 valid reference。
- final_specs/spec.md / interview/qa.md / findings/* / validation/* — canvas dims 不在 spec 硬编码, 概念契约 ("全身 reference") 不变。

## Follow-up 083 — 2026-05-17 22:03:13
Source: user_input/follow_ups/083-20260517-220313-mandatory-full-body-triple-anchor.md
Summary: 用户："请确保生成的actor照片是全身照从头到脚，请在所有prompt 提开始强调这点，而且是必须执行"。081 已经加了 leading `镜头:` line 在 prompt 最前面, 082 在 batch-coordinated builder 中保留了它 — 但 line 内 `严禁` token 落在 line 尾 attention 最弱位置, line 整体读作 enumeration of preferences 而非 hard contract。用户报告 Kling 仍偶尔 drop full-body intent。修法 — 把 full-body contract 从 single anchor 升到 **triple anchor**, 在 prompt 的 3 个不同位置 restate, attention 摊薄了 1 个也不会被 3 个 token 同时 ignore。

修法 (`libs/infrastructure/writers/actor__chinese_prompt.py`):
1. **3 个 module-level 常量 (新)** — 把 framing mandate 文本提到顶层避免 4 个 builder variant 漂移:
   - `_LEADING_FRAMING_MANDATE`: `镜头【强制 MANDATORY · 全身从头到脚】：full-body wide shot · long shot · 9:16 竖屏 · 头顶到脚趾完整入画 · MUST show entire body from top of head to toes · 严禁 portrait / half-body / close-up / head-shoulder crop · 任何裁切均视为生成失败。` — 前缀 `【强制 MANDATORY · 全身从头到脚】` 把 MUST contract 钉在最高 attention 位置 + 双语 (EN duplicate `MUST show entire body...`) 对 EN-trained 模型 backstop + `·` 分隔符 (less token-merge issues) + `任何裁切均视为生成失败` explicit failure semantics。
   - `_RESTATE_FRAMING_MANDATE`: `【再次强调 · 必须执行】整张图必须显示完整全身：从 ① 头顶（含发丝）→ ② 面部 → ③ 颈 → ④ 肩 → ⑤ 胸 → ⑥ 腰 → ⑦ 臀 → ⑧ 大腿 → ⑨ 小腿 → ⑩ 脚趾, 上下 zero crop。生成任何 portrait / 半身 / 特写 / 头肩 / 腰上 / 胸上 构图 = 生成失败。` — 10-waypoint anatomy checklist 强制模型 visualize 每个 body part, numbered enumeration 进一步降 drift。
   - `_TAIL_FRAMING_MANDATE`: `【强制构图 · 最后强调】整图必须 9:16 竖屏 + 头顶到脚趾 zero-crop + 头部仅占画面 1/5 + 身体占 4/5 + 头顶留 ~5% 顶边 + 脚趾下方留 ~5% 底边。如未满足任何一项均视为不合格。` — 放在 `_NEGATIVES_ZH` 上方作 prompt 倒数第二行, framing contract 是模型 apply 负向约束前最后读到的 token batch。
2. **4 个 builder variant** (`build_face_prompt`, `build_body_prompt`, `build_face_prompt_with_picks`, `build_body_prompt_with_picks`) 全部统一应用 triple-anchor 结构:
   - Line 0 = `_LEADING_FRAMING_MANDATE`
   - Line 1 = `_RESTATE_FRAMING_MANDATE`
   - Line 2 = 强化版 descriptor: `**【强制全身】**正面全身定妆照（远景 wide / long shot · 整图必须包含头顶到脚趾 zero-crop · {face: 头部清晰仅用于身份识别, 不主导构图 | body: 形体对焦}）：{ethn} {gender}，{age}` — markdown-bold `**【强制全身】**` 把 full-body contract 也钉在 descriptor 行 (4th anchor 实际上, 但仍在 high-attention prefix 段)。
   - Line -2 (between `_CASTING_REQUIREMENTS_ZH` and `_NEGATIVES_ZH`) = `_TAIL_FRAMING_MANDATE`。
3. 081 的 leading line 文本 (`镜头：full-body wide shot / long shot, ...`) + 082 的 picks-builder 同 line 完全被新 `_LEADING_FRAMING_MANDATE` 替换 — 无 backward-compat shim。

Smoke (4 builder variants all share triple-anchor + descriptor):
- `face_legacy / body_legacy / face_with_picks / body_with_picks` 全部 verified: `lead=True restate=True descriptor=True tail=True tail@-2=True` ✓
- 第一行 = `镜头【强制 MANDATORY · 全身从头到脚】：...` ✓
- 第二行 = `【再次强调 · 必须执行】... ① 头顶 → ② 面部 → ... → ⑩ 脚趾 ...` ✓
- 第三行 = `**【强制全身】**正面全身定妆照 ...` ✓
- 倒数第二行 = `【强制构图 · 最后强调】整图必须 9:16 竖屏 + 头顶到脚趾 zero-crop ...` ✓
- pytest: 15 pass / 3 pre-existing wukong fixture failures (= 082 baseline, 0 regressions)。

Pre-083 leading line (single anchor) + post-082 picks-builder 同 line 完全 superseded。HTTP routes + JSON shapes + endpoint behaviors byte-identical (只 prompt 文本变化, preview pane 显示更长 prompt — 069+070 已支持长 text wrap)。Batch coordination (082) / look bias (077) / minimal wardrobe (080) / look-led classifier (079) / 25% wild-card (074) 全部 unchanged — 新 anchors 仅在 prompt 体的固定位置 inject, 不动 pool 抽样或 dispatch 逻辑。

Auto-updated:
- projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py — 3 个 module constants + 4 个 builder variant rewrite。
- specs/development/ai_video_management/user_input/revised_prompt.md — header bump 083 + Composed-from 段追加。

No conflicts found in:
- `_LOOK_FEATURE_BIAS_ZH` / `_LOOK_OVERLAY_ZH` / `_BODY_BIAS_BY_ARCHETYPE` / `_BIAS_WILD_PROB` / `_classify_actor_attrs` / `_casting_wardrobe` / pool sampler / batch dispatch — 全部 unchanged。
- `_NEGATIVES_ZH` (081 imperative escalation) — 保留 verbatim, 现在 prompt 中 tail-mandate 与 negatives 双重 framing emphasis 互补。
- 6-dropdown random_dim diversity (deferred phase-2) — 与本 follow-up 正交。
- `actor__writer.py` / queries / commands / DTOs / repository protocol / Pydantic body / TS API / `ActorPoolGenerator.tsx` — 全部不动 (无 wire-shape change)。
- final_specs/spec.md / interview/qa.md / findings/* / validation/* — framing contract 仍是 implementation detail; spec 仅引用 "comp-card 全身 reference" 概念契约。

## Follow-up 082 — 2026-05-17 20:38:12
Source: user_input/follow_ups/082-20260517-203812-batch-pool-diversity.md
Summary: 用户："对一个batch里，除了我explictly选择的外，在同一个batch里不得有重复的，比如我选择的asian，25岁，美丽型的，那这个batch里的10张图都要符合这些，但是我没选择的部分，要强制他们不一样，比如一个嘴大，另一个就一定嘴小，一个眼睛大另一个就一定眼睛小，一个高，另一个就矮，一个丰满另一个就苗条等等"。用户的 4 个例子 (嘴/眼/高矮/丰满苗条) 全部 map 到 7 个 face/body pool；今前 N 个 parallel count=1 calls 各 seed 自己的 RNG, 独立 `_pick_biased` → pool draws 间 collision 是 birthday-problem 概率, 22-element pool × 10 slots 期望 ~4 distinct, 用户看到 "10 张脸都长一样"。

Scope (per user clarification this turn): **Pools-only** within-batch diversity (the 7 face/body pools). Dropdown random_dim diversity deferred. Bias exhaustion strategy: **exhaust bias first, then fall through to full pool** + 074's 25% wild-card retained at batch level.

修法 (4 文件 + 1 新 helper):
1. **`libs/infrastructure/writers/actor__chinese_prompt.py`** 加 2 个 helper + 2 个 new builder:
   - `_batch_sample_pool(batch_rng, pool_len, bias_indices, count, wild_prob=_BIAS_WILD_PROB) -> list[int]`: deterministic batch-coordinated sampler. 算法 — `wild_count = sum(rng.random() < wild_prob for _ in range(count))`; bias 先 shuffle + take `bias_count = count - wild_count`; 不足 fall through 到 full_pool 的未用 indices; wild_count 个 slot 从 full_pool 未用 indices 随机抽; 整体 final shuffle 防 slot_index 与 bias/wild 位置耦合; count > pool_len 时 cycle。Pure deterministic in `(batch_rng state, pool_len, bias_indices, count)` — 同 batch_seed 的 N 个并行 call 各自重算同 list, 各取 slot_index。
   - `_resolve_batch_picks(batch_seed, batch_size, slot_index, look, archetype) -> dict[str,str]`: 一次性 resolve 这个 slot 的 7 个 pool 描述符。skin 不进 bias (074 决策); body bias = look_bias.get('body') or archetype_bias 兜底。
   - `build_face_prompt_with_picks(attrs, seed, archetype, picks) -> str` + `build_body_prompt_with_picks(...)` — 接受 caller-supplied pool picks, 其余字段 (镜头 / 服装 / 画面 / 摄影 / 要求 / 避免) 与 pre-082 build_face_prompt / build_body_prompt 行对齐 (081 framing line 仍在最前)。photo cue 仍 per-slot via `random.Random(seed)`。
2. **`libs/infrastructure/writers/actor__writer.py`**: 加 `ActorPool._build_prompts_for_slot(attrs, seed, archetype, batch_seed, batch_size, slot_index) -> (face_prompt, body_prompt)` dispatcher — 当 3 个 batch 字段全 non-None, 走 `_resolve_batch_picks` + `*_with_picks`; 否则 fallback 到 legacy `_build_face_prompt + _build_body_prompt`。`preview_prompts` + `generate_batch` 签名各加 3 个 optional kwargs (`batch_seed/batch_size/slot_index`), call site 切到 new dispatcher。
3. **`libs/application/dtos/actor__dto.py`**: `GenerateActorsInputCdto` 加 3 个 optional 字段 + lineage comment。
4. **`libs/application/queries/actor__query.py::ActorQuery.preview_prompts`** + **`libs/application/commands/actor__command.py::ActorCommand.generate`**: 转发 3 个 cdto 字段到 pool layer。
5. **`libs/domain/repositories/actor__repository.py::ActorRepository` Protocol**: `preview_prompts` + `generate_batch` 签名加 3 个 optional kwargs (Protocol 必须 match concrete)。
6. **`apps/api/routes/actor__route.py::GenerateActorsBody`** Pydantic body 加 3 个 optional int 字段; `_generate_input` 把 body.archetype + body.batch_seed/batch_size/slot_index 全部映到 CDTO。
7. **`apps/ui/src/api.ts::GenerateActorsRequest`** 加 3 个 optional `batch_seed?/batch_size?/slot_index?` 字段。
8. **`apps/ui/src/components/ActorPoolGenerator.tsx`**: `onPreview` 中 `batchSeed = Date.now()` + `batchSize = count` + 每个 parallel `previewPrompts` call 加 `batch_seed/batch_size/slot_index: i`; 新 `previewBatchRef = useRef<{batchSeed, batchSize} | null>(null)` 把 preview 时的 batch 元数据 stash 起来; `onConfirmGenerate` 的 worker pool 在每次 `generateActors` 调用中 forward `previewBatchRef.current.batchSeed + .batchSize + slot_index: slot - 1`, 保证 Kling 实际渲染的 prompt 与 preview byte-equal。

Smoke (end-to-end via `ActorPool.preview_prompts`):
- batch-coordinated (count=10, look=sinister, batch_seed=7777): 眼/鼻/嘴/眉/轮廓/皮肤/体型 全部 **10/10 distinct** ✓
- legacy uncoordinated 同 setup: 眼睛 4/10, 体型 6/10 (birthday-problem collision) ✓
- bias exhaustion (look=cunning, 2-element lips bias subset, count=10): lips 仍 10/10 distinct (bias 取尽 → fall through to full pool 不重复) ✓
- determinism: `_resolve_batch_picks(12345, 10, 3, 'sinister', 'femme_fatale')` 两次调用 == ✓
- 081 framing line 仍在 prompt 最前 ✓
- pytest: 15 pass / 3 pre-existing wukong fixture failures (= 081 baseline, 0 regressions); legacy CDTO without batch fields 仍 OK (backward compat) ✓

HTTP route paths + response shapes byte-identical (只 request body 加 3 optional 字段)。Worker-pool concurrency / `_reap_incomplete_folders` mtime guard / Kling client / look bias overlay (077) / look-led classifier (079) / minimal wardrobe (080) / 081 full-body framing 全部 unchanged。

Auto-updated:
- projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py — 2 helpers + 2 builder variants.
- projects/ai_video_management/libs/infrastructure/writers/actor__writer.py — `_build_prompts_for_slot` dispatcher + `preview_prompts` / `generate_batch` kwargs.
- projects/ai_video_management/libs/application/dtos/actor__dto.py — `GenerateActorsInputCdto` 3 字段。
- projects/ai_video_management/libs/application/queries/actor__query.py — forward。
- projects/ai_video_management/libs/application/commands/actor__command.py — forward。
- projects/ai_video_management/libs/domain/repositories/actor__repository.py — Protocol align。
- projects/ai_video_management/apps/api/routes/actor__route.py — `GenerateActorsBody` + `_generate_input`。
- projects/ai_video_management/apps/ui/src/api.ts — `GenerateActorsRequest` 3 字段。
- projects/ai_video_management/apps/ui/src/components/ActorPoolGenerator.tsx — `onPreview` + `previewBatchRef` + worker pool forward。
- specs/development/ai_video_management/user_input/revised_prompt.md — header bump 082 + Composed-from 段追加。

No conflicts found in:
- `preview_diverse_prompts` / `generate_diverse_batch` (follow-up 059 cross-archetype path) — orthogonal, batch coordination 不应用; 留作 phase-2 follow-up 如果需要。
- 6-dropdown random_dim diversity — 用户 explicit chose "pools only", 留待 phase-2。低 cardinality dropdowns (gender ∈ {male, female} with count=10) 仍可能 collide, expected。
- `_classify_actor_attrs` (079) / `_casting_wardrobe` (080) / 081 framing line — 全部 stack 在 batch-coordinated pool draws 之上, 完整保留。
- final_specs/spec.md / interview/qa.md / findings/* / validation/* — batch coordination 是 implementation detail, 概念契约 ("comp-card per-slot prompts") 不变。
- 历史 generated jpg — 不触, user 按需 regenerate 个别 archetype。

## Follow-up 081 — 2026-05-17 20:26:25
Source: user_input/follow_ups/081-20260517-202625-actor-force-full-body-framing.md
Summary: 用户："生成actor是，请强制生成全身从头到脚的全身照"。即使 080 加了 minimal wardrobe + 11-metric body-readability + 头顶到脚趾 framing language, `build_face_prompt` 的开行 `正面全身定妆照（头部对焦）` 和 姿态行 `头部对焦清晰` 仍是 head-emphasis 信号 — Kling 会把它解读为 portrait crop。本 follow-up 把 framing 决策从模型手里拿走 ↓ 钉死在 prompt 高 attention prefix 段。

修法 (`libs/infrastructure/writers/actor__chinese_prompt.py`，5 处微改):
1. **新增首行** `镜头：full-body wide shot / long shot, 9:16 竖屏构图, 头顶到脚趾完整入框, 头部上方 ~5% 顶边, 双脚下方 ~5% 底边, 严禁任何 portrait crop / head-shoulder framing / 半身像 / close-up。` — 插在 `build_face_prompt` + `build_body_prompt` 两个 prompt 体的最前面。Kling 等 caption-style 模型把前导 token 当 compositional anchor；framing 锚在 prefix 比埋在中段（旧 画面: line）有效得多。
2. **`build_face_prompt` 开行重写**：`正面全身定妆照（头部对焦）：{ethn}...` → `正面**全身**定妆照（远景 wide / long shot; 头到脚完整入框; 头部清晰仅用于身份识别, 不主导构图）：{ethn}...`。删 head-emphasis 词 "头部对焦", 改为 explicit wide-shot wording + 主从关系说明。
3. **`build_body_prompt` 开行重写**：同上风格，保留 `形体对焦` (body variant 本就 body-emphasis)，但加 `远景 wide / long shot; 头到脚完整入框` prefix。
4. **姿态行**：两个 variant 都末尾加 `双手 + 双脚 完整入框不可被裁切`。face variant 同时把 `头部对焦清晰` → `头部清晰可辨` (退掉 "对焦" 词)。
5. **画面行重写**：`从头顶到脚趾全身可见（一帧定格不裁切）, 中性纯灰背景, 头部居画上 1/3` → `9:16 竖屏 / 从头顶到脚趾完整可见 / 头部上方留 ~5% 顶边 / 双脚下方留 ~5% 底边 / 头部占画面上 1/5 (留 4/5 给身体) / 中性纯灰背景`。数字 framing 比 1/3 比例更紧, 头部占比 1/5 强制 body 占 4/5。body variant 同样改 + 保留 `形体居画中`。
6. **`_NEGATIVES_ZH` 升级 imperative**：原 `裁切脚部 / 裁切大腿 / 半身构图 / 头肩特写` 段替换为 4 条 **严禁** 子句：(a) 头肩特写 / 半身像 / portrait crop / close-up / 任何裁切头部 / 双手 / 双脚 / 大腿 的构图；(b) 头部 > 整图 1/4 (头部占比过大暗示 portrait framing)；(c) 身体高度 < 整图 70% (身体占比不足暗示 framing 错误)；(d) 手部 / 脚部 越出画面边缘。其余 080 加的 modest-fallback wardrobe 段 + glamour-pose drift 段保留。

Smoke (`build_face_prompt(east-asian/female/26-35/modern-casual, seed=42, archetype=femme_fatale)`):
- 第一行 = `镜头：full-body wide shot / long shot, 9:16 竖屏构图, ...` ✓ (framing 在 prefix)
- 开行无 `头部对焦`, 改为 `（远景 wide / long shot; 头到脚完整入框; 头部清晰仅用于身份识别, 不主导构图）` ✓
- 姿态行末 `双手 + 双脚 完整入框不可被裁切` + 头部 `清晰可辨` (无 "对焦") ✓
- 画面行 9:16 + ~5% margins + 头部 1/5 + 4/5 给身体 ✓
- 避免行 4 个 **严禁** 子句 ✓
- module import + draw deterministic ✓

Pre-081 framing language (头部对焦 / 头部对焦清晰 / 头部居画上 1/3) 完全替换；无 backward-compat shim — Kling/Sora 等下游模型从此次 turn 起收 full-body wide-shot anchored prompt。Look bias (077) + minimal wardrobe (080) + body bias (074) + 25% wild-card (074) + look-led classifier (079) 全部仍正常 fire 在新 framing 之上。HTTP routes + JSON shapes byte-identical。

Auto-updated:
- projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py — 5 处微改 per 上面 spec。
- specs/development/ai_video_management/user_input/revised_prompt.md — header bump 081 + Composed-from 段追加。

No conflicts found in:
- `_LOOK_FEATURE_BIAS_ZH` / `_LOOK_OVERLAY_ZH` (077) — bias 在 五官 + 综合描述 + 气质 overlay 层, 与 framing 正交。
- `_BODY_BIAS_BY_ARCHETYPE` / `_BIAS_WILD_PROB` (074) — body type bias 仍 fire；framing 不影响 body-pool 抽样。
- `_classify_actor_attrs` (079) — look-led classifier 与 framing 完全 orthogonal。
- `_casting_wardrobe` (080) — wardrobe text 不被 081 触碰。
- `actor__writer.py` preview_prompts seeds 注入 / 9-way 并发 / Kling client / `_reap_incomplete_folders` mtime guard — 全部不动。
- final_specs/spec.md / interview/qa.md / findings/* / validation/* — framing contract 未硬编码在 spec, 概念契约 ("comp-card 全身 reference") 不变。

## Follow-up 080 — 2026-05-17 20:02:56
Source: user_input/follow_ups/080-20260517-200256-actor-minimal-wardrobe-full-body.md
Summary: 用户："生成actor时，请确保生成的actor是全身照，从头到脚，我要看到身材，要知道腿长还是腿短，退直的还是弯的，胸大还是胸小，所以穿越少越好"。把 actor comp-card 服装从 076 的紧身背心 + booty shorts 升到 industry swimwear-standard (运动比基尼 / 赤膊 + 高叉紧身短) — talent-agency fit-cast 标准，最大化 单帧 body-shape 读取。

Numbering note: 本 turn 计划用 slot 079 但发现已被另一个 follow-up "look-led-archetype-classification" 抢占 (11:39:48 timestamp 早于本 turn)，renumber 到 080。

修法 (`libs/infrastructure/writers/actor__chinese_prompt.py`，4 处微改):
1. `_casting_wardrobe('女性')` → "运动比基尼上装（窄肩带细带 + 紧贴胸型 + 完全露肩 / 露上胸 / 露背 / 露腹 / 露腰）+ 高叉紧身运动比基尼下装（高腰线露髋骨 + 高开叉露大腿全长 / 显腿型 / 腿长短 / 腿型直弯 / 大腿内外侧线条 / 臀型）+ 赤足"。`_casting_wardrobe('男性')` → "上身赤膊（露胸肌 / 腹肌 / 肋骨线 / 肩宽 / 腰线 / 腰臀比）+ 紧身贴身运动短裤（高开叉短款露大腿全长 / 显腿型 / 腿长短 / 腿型直弯 / 大腿内外侧线条 / 臀型）+ 赤足"。Docstring 标注 "Per follow-ups 076 + 080" 保 lineage。
2. `_CASTING_REQUIREMENTS_ZH` 形体可辨清单扩展：胖瘦 / 腿长短 / 腿型直弯 / **大腿内外侧线条 / 胸大胸小** / 胸型 / 肩宽 / **腰线** / 腰臀比 / **臀型 / 上身肌肉线条**（新增 5 个 metric 与用户原话 "胸大还是胸小" / 赤膊 male 配套）。"头顶到脚踝" → "头顶到脚趾, 一帧定格不裁切"（脚踝允许 crop 脚, 脚趾强制 toe inclusion）。
3. `build_face_prompt` + `build_body_prompt` 内 `画面:` line: "从头顶到脚踝" → "从头顶到脚趾...（一帧定格不裁切）" — 与 requirements line 对齐。
4. `_NEGATIVES_ZH` 追加 3 段：(a) "裁切脚部 / 裁切大腿 / 半身构图 / 头肩特写" 防 framing 退化；(b) "宽松遮形衣物 / T 恤 / 长裤 / 长裙 / 大衣 / 任何遮挡躯干或大腿轮廓的服装" 防模型回退到 modest fallback；(c) "故意性感化姿势 / 媚态 / 内衣广告感 (本图是 body-reference comp-card, 中性站姿即可)" — 关键：minimal wardrobe 是 body-shape 评估工具, 非 glamour, 姿态保持 follow-up 052 的 自然站立 + 双臂略外开 15° 中性站姿。

Smoke (`build_face_prompt(east-asian/female/26-35/modern-casual, seed=42, archetype=femme_fatale)`): 服装行渲染新比基尼 + 高叉短 verbatim ✓; 画面行渲染 "从头顶到脚趾...（一帧定格不裁切）" ✓; 要求行含新 11-metric body 清单 ✓; 避免行含新 3 段 ✓; module import clean。

Pre-080 wardrobe (076: "黑色紧身运动背心..." + "黑色紧身贴身运动背心...") 完全替换, 无 backward-compat shim。HTTP routes + JSON shapes + endpoint behaviors byte-identical (preview pane 仅显示新 prompt 文本)。历史 generated jpg 不动 (user 可按需重 generate 个别 archetype)。

Auto-updated:
- projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py — 4 处微改 per spec 上面。
- specs/development/ai_video_management/user_input/revised_prompt.md — header bump 080 + "Composed from" 段追加。

No conflicts found in:
- `_LOOK_FEATURE_BIAS_ZH` / `_LOOK_OVERLAY_ZH` (follow-up 077) — look bias 独立于 wardrobe, 在 五官 + 综合描述 + 气质 overlay 三层正常叠加在新 wardrobe 之上。
- `_BODY_BIAS_BY_ARCHETYPE` / `_BIAS_WILD_PROB` (follow-up 074) — body type bias 仍 fire；新 wardrobe 只换面料量, 不动 archetype 体型分布。
- `_classify_actor_attrs` look-led classification (follow-up 079) — look → archetype 映射逻辑不变；新 wardrobe 在 wardrobe layer 下游 of 该 classifier, 完全正交。
- pose line — unchanged, neutral standing 与 minimal wardrobe 联合保证 body-shape read。
- `actor__writer.py` preview_prompts seeds 注入 / 9-way 并发 / Kling client / `_reap_incomplete_folders` mtime guard — 全部不动。
- `ai_videos/{drama}/characters/cN_*/cN_*.md` (character bibles) — in-story costume reference, 与 casting comp-card 是两条独立 pipeline, 不受影响。
- final_specs/spec.md / interview/qa.md / findings/* / validation/* — 这些只引用 "comp-card body-shape reference" 概念契约, 具体 wardrobe 文本不在 spec 里硬编码, 无需 patch。

## Follow-up 079 — 2026-05-17 11:39:48
Source: user_input/follow_ups/079-20260517-113948-look-led-archetype-classification.md
Summary: 修复 actor preview 综合描述 与用户所选 look 矛盾的 regression。`look=sinister + gender=female` 之前 fall-through 到 `everyman`，synthesis 行变成"市井百姓 烟火气十足"——与"阴邪"完全相反。

Backend:
- `libs/infrastructure/writers/actor__writer.py::_classify_actor_attrs`: rewrote as look-led 4-priority classifier (strict 4-way → gender + look + age/style → gender + look → look-only → fallback).
- `libs/infrastructure/writers/actor__writer.py::_ARCHETYPES`: cross-gendered the follow-up 064 看法 (sinister/cunning → femme_fatale; seductive → leading_warm; righteous → ingenue_kind; innocent → youth_fresh) 让每个 look 在每个性别都有锚定 archetype。

Smoke-test passed on 10 edge cases including user's exact bug (sinister female → femme_fatale; was everyman) + legacy 4-way path intact (handsome male 18-25 ancient → leading_hero).

## Follow-up 078 — 2026-05-17 19:28:26
Source: user_input/follow_ups/078-20260517-192826-character-ref-4s-truncate-2s.md
Summary: 角色 reference turntable 时长 2.9s → 4s（下游 Seedance 等 reference 上传上限放宽，多 ~38% on-screen 时间做身份捕捉），同时锁定「前 2s 必须自包含」契约 — 中文 「一」/「二」必须在 2.0s 前完成发声 + 镜头回正到正面，以对齐 `ai_video_management` 已有 短角色合辑 `ShotConcatBuilder._ffmpeg_concat` 的 `_CONCAT_SEGMENT_S = 2.0` 切片边界 + ✂ 截到 2s 按钮 (`_TRUNCATE_DURATION_S = 2.0`) 的下游截取。Arabic 「1, 2, 3」→ 中文「一, 二, 三」；动作 beats 由三段 (0-1 / 1-2 / 2-2.9) 重排为四段 (0-1 / 1-2 / 2-3 / 3-4)，3-4s 新增 1s 面部特写定格作为 face viewer 的 final lock。

**No code change to `character_video__writer.py`.** Shot-char concat 已在 follow-up 054 引入的 `_CONCAT_SEGMENT_S = 2.0` + ffmpeg `-filter_complex trim=duration=...` 路径上自动 trim 每段到 2s。本 follow-up 仅 reaffirm 该行为为 canonical contract，并把 prompt 模板的 0-2s 信息密度配合该 2s 切片。

Numbering note: 此 slot 原排到 076 但发现 077 entry (look-dominates-feature-bias) 引用了 orphan 076（指 `actor__writer.py` 内 wardrobe 注释的待回填）—— 为避免主题冲突，新文件 renumber 至 078。slot 076 留待 future 回填 wardrobe / framing / `_classify_actor_attrs` 兜底。

Auto-updated:
- .claude/agent_refs/project/ai_video.md — rule #12.5 v4 → v5: 2.9s → 4s + 中文「一, 二, 三」+ 4-segment timed beats + 前 2s 自包含契约 + 负向 `不要 超过 2.9s` → `不要 超过 4s（v5）/ 不要 把 "一" / "二" 延后到 2s 之后`；schema 段、locked-fields 段、设计取舍段、bottom 配音对照表 (3 → 4 行)、attribution footer 全部同步。
- ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md — 全部 10 个角色文件按新 schema patched: 文件说明 line + section header + 内嵌 ```text``` fence 内 (动作 / 台词 / 节奏 / 时长 / 负向) + bottom 配音对照表。批处理脚本 `/tmp/patch_chars.py` (临时, 未 ship) idempotent 跑了一遍；c10 之前已部分手工 migrate，仅补 section header。
- specs/ai_video/mozun_chongsheng/user_input/follow_ups/019-20260517-192826-character-ref-4s.md — 跨项目 sibling follow-up，应用同一规则到 mozun_chongsheng 角色文件 + 自身 revised_prompt.md + changelog.md。
- specs/development/ai_video_management/user_input/revised_prompt.md — 追加 078 段（"Composed from" + "Last regenerated" header bump，描述 4s/2s 契约 + auto-truncate 既存代码路径 + cross-project 联动）。

No conflicts found in:
- projects/ai_video_management/libs/infrastructure/writers/character_video__writer.py — 已存在的 `_CONCAT_SEGMENT_S = 2.0` + `_TRUNCATE_DURATION_S = 2.0` 即用户要求的 "auto-truncate to 2s then concat"，无需改。
- projects/ai_video_management/apps/ui/* — 截到-2s 按钮 + 生成角色合辑 按钮 文案 / 行为不变（"2s" 文案与新契约一致）。
- specs/development/ai_video_management/final_specs/spec.md, interview/qa.md, findings/*, validation/* — 这些没有引用具体的 character ref 时长数字（仅引用 ai_video task_type 的 cross-cutting 规则，那条规则已在 agent_refs 中 patched）。
- specs/ai_video/mozun_chongsheng/{final_specs,findings,validation}/* — grep 确认 0 个 2.9s 引用，无需 patch。changelog.md 与历史 follow-ups (015 / 016 / 017) 中的 2.9s 引用是历史记录，保留不动。

## Follow-up 077 — 2026-05-17 19:22:20
Source: user_input/follow_ups/077-20260517-192220-look-dominates-feature-bias.md
Summary: 用户报"在角色生成是，预览显示的prompt跟我所要的有比较大的出入，我在选项中已经选择了要淫邪的，但是预览里的10个prompt都跟淫邪不太相关，你可以在眼睛大小，鼻子形状等等细节自由发挥，但整体需要按我的要求来"。根因：075 把 prompt 改成结构化中文后，仅 `体型` 一行按 archetype bias，其余 五官/轮廓/皮肤 全部 uniform 随机 — 即使 archetype 命中 `villain_cold`，`综合描述` 一行压不住 7 行 uniform 随机；池里有 阴邪向 descriptor (凌厉/狐眼/凤眼/挑眉冷峻/薄唇紧抿 等) 但 uniform 抽到概率低，10 个 prompt 跑下来大多是 大眼/桃花/樱桃小嘴 之类与 sinister 无关组合。

修法：在 `libs/infrastructure/writers/actor__chinese_prompt.py` 加 `_LOOK_FEATURE_BIAS_ZH` (5 个 character-archetype look slug × 6 个 pool 的 index 子集) + `_LOOK_OVERLAY_ZH` (5 条 ≥10 字中文气质句); `build_face_prompt` + `build_body_prompt` 把 5 个 五官+轮廓 行从 `_pick` 切到 `_pick_biased(look_bias.get(pool))`; body bias 优先用 look bias，兜底 archetype；选 5 个 character-look 时在 `综合描述` 之后追加 `气质：{overlay}` 行。25% wild-card 保留 — `0.75^6 ≈ 18%` 概率全 bias 命中，大多数 actor 仍有 1-2 个 wild-card feature 保 within-batch 多样性（"细节自由发挥"），但 整体气质 + 综合描述 + 气质 overlay 三层叠加，10 个 preview prompt 都能感受到所选 look。皮肤保留 uniform (074 决策 — 跨-archetype skin variety 最大化)。8 个物理 look (handsome/beautiful/cute/mature/rugged/soft/aristocratic/fierce) byte-identical to pre-077 — `look_bias = {}` 时 `_pick_biased` 退化 uniform，无 `气质：` 行。

Smoke (sinister look male, 30 seeds, archetype=None — 等效用户最常见 case 即 look 命中但 age/style 随机所以 `_classify_actor_attrs` 走 `everyman` 兜底): 描述行匹配 sinister 关键词 30/30 vs 同样 setup 的 handsome look 18/30；10 sinister seeds → 5 distinct 眼睛 descriptor (variety 保留)；handsome look prompt assert `'气质：' not in p` ✓。

Auto-updated:
- projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py — 新 `_LOOK_FEATURE_BIAS_ZH` + `_LOOK_OVERLAY_ZH` 字典；`_BIAS_WILD_PROB` docstring 注明 077 复用；`build_face_prompt` + `build_body_prompt` 切 5 个 五官+轮廓 行到 `_pick_biased(look_bias.get(...))` + 选 character-look 时追加 `气质：{overlay}` 行 + body bias 优先 look bias 兜底 archetype。
- specs/development/ai_video_management/final_specs/spec.md — FR-9j 末尾追加 077 段：5 character-archetype look 触发 per-pool bias + 气质 overlay；25% wild-card preserved；8 物理 look byte-identical to pre-077。
- specs/development/ai_video_management/user_input/revised_prompt.md — `Composed from` + `Last regenerated` 双 header bump 加 077 段，描述 look bias map + overlay map + smoke 结果 + Discovery note (in-code "follow-up 076" 引用但 follow-up 076 文件不存在 — 历史遗留，留待回填)。

No conflicts found in: interview/qa.md, findings/dossier.md, validation/* (validation 层不动；prompt 内容的 acceptance criterion 是 "prompt 上 wire" — 仍然成立), final_specs/promoted.md, validation/promoted.md, 既有 5 个 character-look 的下游 (archetype 反查 / migrate_archetypes / ActorView / ActorGrid filter 都不读 prompt 内容), 8 个物理 look 全部 (`_pick_biased` 退化 uniform，byte-identical to pre-077)，所有 053 + 064 + 071 + 074 + 075 之前的 actor-pool follow-up (无 wire 行为冲突)。

Out-of-band (not fixed in this follow-up): `actor__writer.py` line 332/354/356/390 + `actor__writer.py` line 1358/1471 都有 "Per follow-up 076" comment 引用但 `specs/development/ai_video_management/user_input/follow_ups/076-*.md` 文件不存在 — 历史遗留 orphan reference。一次回填可写一个 076 entry 描述 075 之后的 wardrobe (comp-card 紧身露肩 + 露大腿) + 全身 framing (头顶到脚踝) + `_classify_actor_attrs` 兜底 这三处实际改动。本 follow-up 不回填。

## Follow-up 075 — 2026-05-17 17:51:00
Source: user_input/follow_ups/075-20260517-175100-chinese-structured-prompt.md
Summary: 把发给 Kling 的所有 actor-generation prompt 全部改为 **结构化中文**，按用户指定格式：眼睛/鼻子/嘴巴/眉毛/轮廓/皮肤/体型 + 综合描述 (妖艳/正值/...) + 服装/摄影/避免。Kling 是快手中文模型，对中文 prompt 支持优于英文；follow-up 072 之前的 `(中文)` 失败仅因 English 主体内 parens-CJK 切换破 tokenizer，纯中文 prompt 无此问题。

New file (per SRP): `libs/infrastructure/writers/actor__chinese_prompt.py`:
- 7 个中文 variance pools (每池 ≥ 20 条覆盖大小/形状/颜色多维度):
  - `_EYES_ZH` (22): 含 桃花/丹凤/鹿/狐/卧蚕/凤/杏 全套 Chinese 眼型
  - `_NOSE_ZH` (22): 含 高挺/驼峰/蒜头/挺直/小巧/塌/鹰钩/K-beauty 标准
  - `_LIPS_ZH` (22): 樱桃小嘴/薄/厚/丰满嘟嘴/咬唇/古典樱唇 + 唇形 + 厚度
  - `_BROW_ZH` (22): 剑/柳叶/远山/卧蚕/上挑/平直/古典蛾眉 + 粗细 + 弧度
  - `_CONTOUR_ZH` (22): 方/V字/鹅蛋/圆/瓜子/国字/心形/婴儿肥/骨感/刀削 + 颧骨
  - `_SKIN_ZH` (22): 颜色 (白皙→乌黑) + 质地 (玻璃/水光/哑光/婴儿肌/雀斑/沧桑)
  - `_BODY_ZH` (22): **新增体型池** — 高矮 + 胖瘦 + 整体姿态 (用户要求 "形体的描述, 高矮胖瘦之类的")
- `_PHOTOGRAPHY_ZH` (10) 中文相机 cue (佳能 EOS R5 / 索尼 / 富士 / 哈苏 / 柯达 Portra / iPhone …)
- `_SYNTHESIS_BY_ARCHETYPE` 10 entries: archetype slug → 中文 综合描述 (e.g., `femme_fatale` → "一位妖媚妩媚的女配, 风情万种, 美艳动人, 致命诱惑")
- `_BODY_BIAS_BY_ARCHETYPE` 10 entries: 体型 bias per archetype (leading_hero → 高挑/魁梧/健硕; femme_fatale → 高挑/纤瘦/丰满/曲线/娇媚; etc.) + 25% wild-card fallthrough preserved from 074
- `build_face_prompt(attrs_dict, seed, archetype) -> str`: emits 13-line structured Chinese
- `build_body_prompt(attrs_dict, seed, archetype) -> str`: same structure + 灰色 T 恤 + 黑色运动短裤 industry comp-card uniform (preserved from 052) + 9:16 full-figure framing
- 中英文映射 dicts (`_AGE_ZH`/`_ETHNICITY_ZH`/`_GENDER_ZH`/`_STYLE_ZH`) for the 角色描述 + 服装 lines
- `_NEGATIVES_ZH`: 中文 negative 段 (避免 塑料感/蜡像感/卡通比例/过度磨皮/对称完美脸/AI 同质化/影楼美化/网红脸)

`actor__writer.py` changes:
- `_build_face_prompt(attrs, variance)` → `_build_face_prompt(attrs, seed, archetype)`; delegates `build_face_prompt(attrs.to_dict(), seed, archetype)`
- `_build_body_prompt(attrs, variance)` → `_build_body_prompt(attrs, seed, archetype)`; delegates `build_body_prompt(attrs.to_dict(), seed, archetype)`
- 4 call sites (preview_prompts / preview_diverse_prompts / generate_batch / generate_diverse_batch) 丢 `variance = _variance_for(...)` 直接 `self._build_face_prompt(attrs, seed, archetype)` (or `spec.slug` for diverse 路径) — Python 脚本一次性 replace 完成 (2+2 = 4 sites)
- English `Variance` machinery (`_VARIANCE_*` pools / `_variance_for` / `_ARCHETYPE_FEATURE_BIAS` / `_pick_biased` / `_LOOK_ENRICHED`) 现为 dead code 对 wire prompt 内容；留在 source 不删 (deferred cleanup — follow-up 075 out of scope)
- `_CJK_PARENS_RE` strip 留在 `_variance_for` 内但 no longer load-bearing — 071 的 English pool 已不上 wire

Smoke (sample face prompt for femme_fatale, seed=42):
```
角色描述：东亚 女性，30 岁左右
眼睛：端庄秀眼, 双眼皮, 杏眼, 温柔贤淑
鼻子：小巧鼻型, 精致玲珑, 鼻头微翘
嘴巴：樱桃小嘴, 薄唇, 唇形精致
眉毛：平直眉, 韩式眉, 温柔大气
轮廓：长脸型, 五官立体, 高级感
皮肤：深棕色, 巧克力质感, 性感浑厚
体型：高大魁梧, 健壮型男, 肌肉发达
综合描述：一位妖媚妩媚的女配, 风情万种, 美艳动人, 致命诱惑
服装：中国古装, 仙侠武侠风
摄影：尼康 Z9 105mm f/1.4, 超自然渲染, 不平滑皮肤
要求：人像写真, 自然光, 真实质感, 8K 高清, 抓拍随意感, 真实毛孔, 自然不对称
避免：塑料感皮肤, 蜡像感, 卡通比例, 过度磨皮, 对称完美脸, AI 生成同质化脸, 影楼美化, 千篇一律的网红脸
```

Pytest: 18 pass / 5 pre-existing wukong fixture failures (=074 baseline, 0 regressions); `import apps.api.main` + `import apps.api.asgi` boot clean.

Out of scope (deferred):
- Removing dead English variance machinery (`_VARIANCE_*` pools 27 个 + `_variance_for` + bias maps + helpers) — would shrink `actor__writer.py` 2300 → ~600 行；SRP/file-size flag 持续标记。
- Per-五官 archetype bias on the Chinese side (currently 5 of 7 sections uniform random; only 体型 has bias). 综合描述 carries archetype direction; tightening 五官 bias is future follow-up if 妖艳/英俊 不够 consistent.
- Frontend prompt-preview UI 自动更新 — `PromptPreviewModal` 会显示新的中文结构 prompt (069+070 已让 modal 支持 multi-line/wrap 显示 long text)。

Auto-updated:
- `projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py` (NEW, ~250 行)
- `projects/ai_video_management/libs/infrastructure/writers/actor__writer.py`:
  - `_build_face_prompt` 签名 + 函数体重写 (delegate to ZH builder)
  - `_build_body_prompt` 签名 + 函数体重写 (delegate to ZH builder)
  - 4 个 call sites 改 `_variance_for` + 旧 builder → 新 builder 直接 invocation
- `specs/development/ai_video_management/user_input/follow_ups/075-20260517-175100-chinese-structured-prompt.md` (NEW)
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bumped (next)
- `specs/development/ai_video_management/final_specs/spec.md` / `validation/*` — 不需 surgical patch；纯 wire-content 语言切换 + 内部结构化，HTTP shapes byte-identical (frontend 收到的 preview prompt 现是中文)。

No conflicts found in:
- follow-up 074 (within-archetype diversity)：本 follow-up 把 074 的 wild-card + skin 扩展从 English path 搬到了 Chinese path (_BODY_BIAS_BY_ARCHETYPE 中 25% wild-card 保留；skin 不在 bias 保 uniform random — 跨 archetype skin variety 最大化)。
- follow-up 073 (reap mtime threshold)：并发 race fix 与 prompt 内容正交。
- follow-up 072 (CJK strip)：strip 仍存活 (legacy guard) 但不再 load-bearing — 新 Chinese 直接上 wire 不经 strip。
- follow-up 052 (face+body dual generation)：face + body 共享 seed → 共享身份锚 (五官+体型) 仍 preserved；body comp-card 灰色 T 恤 + 黑色短裤 wardrobe lock 保留 (Chinese 表达)。
- follow-up 053 (10-archetype taxonomy)：`_SYNTHESIS_BY_ARCHETYPE` + `_BODY_BIAS_BY_ARCHETYPE` 用 archetype slug 与 053 完全一致；archetype 行为不变。
- follow-up 064/051 (unified mode + DDD)：command/route 层不动；wire format 改变对上层透明。
- follow-ups 001-068：HTTP routes + JSON shapes byte-identical。

## Follow-up 074 — 2026-05-17 17:28:56
Source: user_input/follow_ups/074-20260517-172856-within-archetype-diversity-skin-eyeshape.md
Summary: 用户反馈 within-archetype 演员差异性还是不够 (e.g. 妩媚 women 都长一样)。三步走解决：(1) 扩 skin_tone (10→22, 全色谱 alabaster→ebony) + skin_texture (8→21, 全 tactile spectrum)，覆盖用户提的 皮肤白/皮肤黑。(2) 加 5 个 Chinese 眼型 到 EYES pool (22→27): 桃花眼/杏眼/鹿眼/狐眼/卧蚕。(3) `_pick_biased` 加 `_BIAS_WILD_PROB = 0.25` wild-card fallthrough — 25% 概率 archetype bias 被忽略走全 pool uniform。6 个 biased 五官 全 archetype-biased 概率 = 0.75^6 ≈ 18% → 大多数演员有至少一个 wild 五官 break sameness。Skin pool 不进 bias map (保留 uniform random) → 跨 archetype skin variety 最大化，正是用户想要的。

Pool expansions:
- `_VARIANCE_SKIN_TONE`: 10 → 22 (+ alabaster, translucent moonlight, cream rice, peachy rose-flushed, golden-honey, caramel, chestnut, umber, cocoa, ebony, deep mahogany, neutral-medium)
- `_VARIANCE_SKIN_TEXTURE`: 8 → 21 (+ freckled constellation, glass K-beauty, porous realistic, chok-chok dewy, scarred lived-in, ruddy windburn, matte velvet, silken satin, doll-flawless, sun-aged crinkled, pearlescent moonlit, olive-velvet matte, vellum parchment)
- `_VARIANCE_EYES`: 22 → 27 (+ 桃花眼/杏眼/鹿眼/狐眼/卧蚕，中文标在 parens 内做 in-source docs；072 strip 在 wire 上去掉 parens)

Wild-card mechanic:
- 新 module-level `_BIAS_WILD_PROB: float = 0.25`
- `_pick_biased(rng, pool, biased)` 改为 `if biased and rng.random() >= _BIAS_WILD_PROB: ... else: return rng.choice(pool)` — 25% 概率全 pool uniform random，否则 archetype biased
- Pure deterministic — same seed reproduces same choice
- 6 biased facial picks → P(all archetype-biased) = 0.75^6 ≈ 18% → 82% 演员有至少一个 wild 五官

Archetype eye-shape bias 扩展 (5 archetype 加新眼型 indices):
- `leading_warm`: + 22 (桃花眼) / 23 (杏眼) / 24 (鹿眼) / 26 (卧蚕) — 温润如玉 scholar
- `ingenue_kind`: + 23 (杏眼) / 24 (鹿眼) / 26 (卧蚕) — kind doe-eyed
- `ingenue_lively`: + 22 (桃花眼) / 25 (狐眼) / 26 (卧蚕) — lively flirty
- `femme_fatale`: + 22 (桃花眼) / 23 (杏眼) / 25 (狐眼) — 妩媚 textbook eye vocabulary
- `youth_fresh`: + 23 (杏眼) / 24 (鹿眼) / 26 (卧蚕) — fresh innocent
- 其它 5 archetype (leading_hero / villain_cold / sage_elder / martial_drifter / everyman) 不显式加新眼型 — 通过 wild-card fallthrough 仍能命中 ~25%

Smoke (30 femme_fatale gens):
- unique skin-tones seen: 17/22 (palette 横扫 alabaster→ebony) ✓
- unique eye-shapes seen: 8 (含 桃花眼 9× / 狐眼 8× / 杏眼 11× / catlike 12× / phoenix 6× / dark intense 7×) ✓
- CJK leaks in wire: 0/30 (072 strip 保留) ✓
- 18 pass / 5 pre-existing wukong fixture failures (=073 baseline, 0 regressions) ✓
- main+asgi boot clean ✓

Pre-074 同样 30 gens 大约只会出现 ~4 unique skin tones (small pool) + ~4 unique eyes (narrow bias)。差异化 step-change 明显。

Auto-updated:
- `projects/ai_video_management/libs/infrastructure/writers/actor__writer.py`:
  - `_VARIANCE_SKIN_TONE` 加 12 新条目 (10→22)
  - `_VARIANCE_SKIN_TEXTURE` 加 13 新条目 (8→21)
  - `_VARIANCE_EYES` 加 5 新中文眼型条目 (22→27)
  - 新 `_BIAS_WILD_PROB: float = 0.25` 常量
  - `_pick_biased` 函数体重写 (加 wild-card fallthrough)
  - `_ARCHETYPE_FEATURE_BIAS` 5 archetype 的 "eyes" 子集扩展加新眼型 indices
- `specs/development/ai_video_management/user_input/follow_ups/074-20260517-172856-within-archetype-diversity-skin-eyeshape.md` (NEW)
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bumped (next)
- `specs/development/ai_video_management/final_specs/spec.md` / `validation/*` — 不需要 surgical patch；纯 prompt 内容多样性扩展，HTTP shapes byte-identical。

No conflicts found in:
- follow-up 073 (reap mtime threshold)：并发 race fix；与本 follow-up 的 prompt 多样性扩展正交。
- follow-up 072 (CJK strip)：本 follow-up 新加的中文眼型 (桃花眼 etc.) 仍依赖 072 的 strip — 已 smoke-tested 0 leak。
- follow-up 071 (feature pools + bias)：本 follow-up 在 071 的 bias 框架上加 wild-card + 加新眼型 + 扩 skin。
- follow-ups 052-053-064 (face+body / diverse mode / unified mode)：所有上层不变。
- follow-ups 001-068：HTTP routes + JSON shapes byte-identical。

## Follow-up 073 — 2026-05-17 17:21:07
Source: user_input/follow_ups/073-20260517-172107-reap-mtime-threshold-concurrent-race.md
Summary: 并发 race-condition bugfix。用户 6 张里 2 张失败 `[Errno 2] No such file or directory` 写 jpg 时。根因：前端 (per follow-up 064 + 059 worker-pool) 并行发 N 个 `count=1` 请求；每个请求进 `generate_batch` 顶部都 run `_reap_incomplete_folders`，该 reaper 无 mtime 判断 — 删除任何无 jpg 的 actor 文件夹，包括 sibling 并发请求刚 allocate 但还在等 Kling HTTP (30-120s) 的文件夹。修法：reaper 加 mtime threshold (5 分钟，安全覆盖 Kling face 120s + body 120s worst-case)。

Fix:
- 新加 `_REAP_MIN_AGE_SECONDS: float = 300.0` 模块常量
- `_reap_incomplete_folders` 每个 candidate 加 guard: `if entry.stat().st_mtime > cutoff: continue` 其中 `cutoff = time.time() - _REAP_MIN_AGE_SECONDS`；OSError on stat 也 skip
- 既有 keep-if-has-jpg 规则 (follow-ups 018/027/033) 完整保留

Smoke (临时目录三场景):
- 刚 mkdir 的 fresh folder → 不再被 reap ✓ (修复 race)
- mtime 回拨过 300s 的 stale folder → 仍被 reap ✓ (genuine orphan cleanup 保留)
- 含 jpg 的 folder 无论 age → 不被 reap ✓ (keep-if-has-jpg 保留)
- 18 pass / 5 pre-existing wukong fixture failures (=072 baseline, 0 regressions)

Auto-updated:
- `projects/ai_video_management/libs/infrastructure/writers/actor__writer.py`:
  - 新加 `_REAP_MIN_AGE_SECONDS: float = 300.0` 在 JPEG_QUALITY 后
  - `_reap_incomplete_folders` 加 mtime guard 与解释 docstring
- `specs/development/ai_video_management/user_input/follow_ups/073-20260517-172107-reap-mtime-threshold-concurrent-race.md` (NEW)
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bumped (next)
- `specs/development/ai_video_management/final_specs/spec.md` / `validation/*` — 不需要 surgical patch；纯并发 race 修复，HTTP shapes / endpoint contract / actor-folder schema 全部 byte-identical。

Class-of-bug note: 任何 "scan-then-act" pattern 跨并发调用都要么用 lock (这里 over-engineering) 要么靠 mtime/sentinel 防误删 sibling 工作。如果未来 reap 想做更强 (e.g., 检测整个 batch 失败后立即 cleanup 而非等 300s)，可加 explicit per-folder sentinel file (`.in_progress` marker) + 删除在 write_bytes 成功后 — 本 follow-up 选 mtime 简化方案。

No conflicts found in:
- follow-up 072 (CJK-in-prompt strip) / 071 (feature pools + bias)：纯 prompt 内容改动 / archetype 抽样改动，与 reaper/race 正交。
- follow-up 059 (diverse mode worker pool) / 064 (unified mode 并行 preview→confirm)：本 follow-up 修的就是这两 follow-up 引入的并发 pattern 暴露出的 reaper race；workflow / UX 不变。
- follow-up 052 (face+body dual gen 30-120s 各)：300s threshold 已覆盖最坏 worst-case (face 120 + body 120 + assembly buffer)。
- follow-up 027 (race-safe id 分配 via mkdir(exist_ok=False) + reap moved into generate_batch)：本 follow-up 是 027 reaper 设计的 follow-on bugfix — 027 假设 reap 仅 cleanup 已-orphaned；并发 worker pool 引入后该假设不成立。
- follow-ups 001-058：HTTP routes + JSON shapes byte-identical；行为变化仅是 reap 更保守 (从不立删，等 5 分钟)。

## Follow-up 072 — 2026-05-17 17:12:15
Source: user_input/follow_ups/072-20260517-171215-strip-cjk-annotations-from-kling-prompt.md
Summary: Bugfix to follow-up 071。UI 报 "失败 6 张 / #1: 500 HTTP 500 ..." — 全是 Kling API 拒绝 prompt (per-slot HTTP 500，surfaced through `result.errors` 的 `http_failed: …` 条目，不是 Python 异常)。根因：071 给新 pool 条目埋了 CJK-in-parens 注释作为 in-source docs (e.g. ` (高挺鼻梁)`, ` (小眼睛)`, ` (蒜头鼻)` 等 9 处)，但这些条目直接 join 进 `features_text` 上 wire 到 Kling，Kling-v1 silently 拒绝 → 500 per slot。修法：assembly 时一次性 strip。源 docs 保留。

Fix:
- 新加 module-level `_CJK_PARENS_RE = re.compile(r"\s*\([^)]*[一-鿿][^)]*\)")` (matches CJK Unified Ideograph U+4E00–U+9FFF in parens with optional leading space)
- `_variance_for` 末尾改 `features_text = _CJK_PARENS_RE.sub("", ", ".join(parts))`
- 源条目不动 — `(高挺鼻梁)` 等仍在 pool 定义里供 devs 看映射关系

Smoke:
- `_CJK_PARENS_RE.sub('', '...nose... (高挺鼻梁), ...eyes (小眼睛)')` → `'...nose..., ...eyes'` ✓
- 6 seeds × 4 archetype-branches (含 None) = 24 combos，每个 `features_text` CJK 字符数 = 0 ✓
- 18 pass / 5 pre-existing wukong fixture failures (=071 baseline, 0 regressions)
- main+asgi boot clean

Auto-updated:
- `projects/ai_video_management/libs/infrastructure/writers/actor__writer.py`:
  - 加 `_CJK_PARENS_RE` 模块常量 (放在 `_VARIANCE_NEGATIVE_ROTATION` 后)
  - `_variance_for` 中 `features_text = ", ".join(parts)` → `features_text = _CJK_PARENS_RE.sub("", ", ".join(parts))`
- `specs/development/ai_video_management/user_input/follow_ups/072-20260517-171215-strip-cjk-annotations-from-kling-prompt.md` (NEW)
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bumped (next)
- `specs/development/ai_video_management/final_specs/spec.md` / `validation/*` — 不需要 surgical patch；纯 wire-content sanitization fix，HTTP shape 不变。

Class-of-bug note: 任何 bake 非-ASCII 字符进 LLM/text-to-image prompt 都要 sanitize。Kling 静默拒绝 (无明确 error code 解释)；下次类似集成应该 (a) ASCII-only by convention 或 (b) sanitize at prompt-build (本 follow-up 选 b — 保留 in-source 多语言 docs)。如果未来 Kling-v2/3 支持 CJK，移除 strip 即可。

No conflicts found in:
- follow-up 071 (feature pools + archetype bias)：本 follow-up 是 071 的 bugfix；071 的 pool expansion + bias map 全部保留并正常工作 — 只是 wire content 现在干净 ASCII。
- follow-up 069 (prompt preview card polish) / 070 (markdown pre overflow)：纯前端，与 backend prompt sanitization 正交。
- follow-ups 052-053-064 (actor body / diverse mode / unified mode + 5 new look enriched)：`_LOOK_ENRICHED` 不含 CJK，不受 strip 影响。
- follow-ups 001-068：HTTP routes + JSON shapes byte-identical；fix 仅影响 prompt 字符串内容。

## Follow-up 071 — 2026-05-17 17:02:53
Source: user_input/follow_ups/071-20260517-170253-feature-pools-expand-archetype-bias.md
Summary: 演员生成 prompt 更深的多样性 + archetype 连贯性。两个 coupled changes 到 `libs/infrastructure/writers/actor__writer.py`:
(1) 6 个面部五官 variance pools 全部扩到 ≥20 条 — eyes 14→22 (含大眼/小眼/圆眼/泪眼); nose 10→21 (含蒜头鼻/驼峰鼻/高挺鼻梁); jawline 10→22; cheekbones 9→20; brow 10→21; lips 10→20。新条目用 inline parentheses 标中文 (e.g. `(蒜头鼻)`)。原有条目全保留。
(2) 新增 `_ARCHETYPE_FEATURE_BIAS: dict[str, dict[str, tuple[int, ...]]]` 10 archetype → pool_name → preferred indices map。`_variance_for(seed, gender, archetype=None)` 签名加 `archetype` 参数；给定时面部五官 picks 走 `_pick_biased(rng, pool, biased_indices)` helper (filter to subset then random.choice)；不给或 unknown 时回退到 uniform random。

Bias 设计示例：
- `leading_hero` (英俊男主气场冷峻): jawline 5 indices (square / chiseled / Roman / catlike / K-beauty), eyes (1, 2, 4, 10, 15 = 丹凤眼 + deep-set + piercing + dark intense + 小眼), nose (aquiline / Roman / 高挺鼻梁 / chiseled / K-beauty), lips thin/balanced/tight.
- `femme_fatale` (妖艳女配): jawline (V-shaped / heart / swan-neck / catlike), eyes heavy-lidded + 丹凤眼 + catlike, lips Bardot / bee-stung / pouty.
- `ingenue_kind` (清纯善良女主): jawline soft/oval/apple-cheek/fawn-curve, eyes 大眼 + 圆眼 + wide innocent + double-eyelid, nose petite/snub/button/ski-jump.
- 7 more archetypes (leading_warm, ingenue_lively, villain_cold, sage_elder, martial_drifter, everyman, youth_fresh) 同样 dict shape; 全 10 个都有 bias 条目。

Implementation: 一次性 Python script `_apply_069.py` (本 turn 后删除) 用 regex 替换 6 个 pool 定义 + insert bias map after `_ARCHETYPE_BY_SLUG` + 修改 `_variance_for` 签名和函数体。然后 4 处 `_variance_for(...)` 调用点 (`preview_prompts`, `preview_diverse_prompts`, `generate_batch`, `generate_diverse_batch`) 用 Edit 修改 forward `archetype`：preview/generate 路径用 `archetype=archetype` (from kwarg) — diverse 路径用 `archetype=spec.slug` (per-slot ArchetypeSpec)。`preview_prompts` 签名加 optional `archetype: str | None = None` kwarg。

Out-of-scope (deferred — SRP/file-size 已 flag):
- 把 variance pools 抽到独立文件 (`libs/infrastructure/writers/actor__variance_pools.py` 或 `libs/domain/value_objects/actor__variance.py` — 它们是 business knowledge 应在 domain): `actor__writer.py` 现 ~2200 行，未来 stage-5 抓。
- 非面部 pools (hair, skin, expression, lighting, mood) 的 archetype bias — 用户只问 五官，其它保持 uniform random。
- Frontend dropdown 不需改 — diverse mode 已通过 `_distribute_archetypes` 驱动 archetype。

Smoke test:
- 6 pool sizes verified: jawline 22, cheekbones 20, brow 21, nose 21, lips 20, eyes 22。
- `_ARCHETYPE_FEATURE_BIAS` 10 archetype keys ✓。
- `_variance_for(seed=42, gender='male')` (no archetype) → uniform output (soft oval jaw + porcelain cheeks 等)。
- `_variance_for(seed=42, gender='male', archetype='leading_hero')` → "powerful Roman-bust jawline" + "sharply angled cheekbones" (bias indices 7 + 3 命中) ✓。
- `_variance_for(seed=42, gender='female', archetype='femme_fatale')` → "elongated swan-neck jawline" + "sharply angled cheekbones" (bias indices 12 + 3 命中) ✓。
- `python -m pytest tests/` — 18 pass / 5 pre-existing wukong fixture failures (= 070 baseline, 0 regressions)。

Auto-updated:
- `projects/ai_video_management/libs/infrastructure/writers/actor__writer.py`:
  - 6 个 _VARIANCE_{JAWLINE,CHEEKBONES,BROW,NOSE,LIPS,EYES} pool definitions 扩展 (旧 entries 保留 + 新 entries 追加)。
  - 新 _ARCHETYPE_FEATURE_BIAS dict (10 archetype × 6 pool × ~5-8 indices each) 插在 _ARCHETYPE_BY_SLUG 后。
  - 新 _pick_biased helper function。
  - _variance_for 签名 + body 重写以 forward archetype + 用 bias。
  - 4 个 _variance_for(...) call sites + preview_prompts 签名 forward archetype。
- `specs/development/ai_video_management/user_input/follow_ups/071-20260517-170253-feature-pools-expand-archetype-bias.md` (NEW)。
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bumped (next)。
- `specs/development/ai_video_management/final_specs/spec.md` / `validation/*` — 不需要 surgical patch；纯 prompt 内容扩展 + 内部 archetype bias 实现，HTTP shapes byte-identical，0 endpoint 改动。

No conflicts found in:
- follow-up 070 (markdown pre no horizontal scroll) / 069 (prompt preview card polish)：纯前端，与 backend variance 扩展正交。
- follow-up 068 (SRP infra exceptions extracted)：本 follow-up 不动 exception classes，新增的 _pick_biased helper 是 pure function 不需要 errors 文件。
- follow-up 067 (look enum sync) + 064 (unified mode + 5 新 look 值)：bias map 用 archetype slug 而非 look slug — 与 look 扩展正交；新 look 值会通过 `_LOOK_ENRICHED` 在 prompt 中展开，与 facial-feature bias 互补。
- follow-up 053 (diverse mode + 10 archetype): 本 follow-up 在 053 已有的 10 archetype 基础上加深 bias 到 facial 层；`_ARCHETYPES` tuple 不动 — 只是为每个 slug 加额外的 `_ARCHETYPE_FEATURE_BIAS` entry。
- follow-up 052 (actor body image + diversity strategy)：variance dataclass + 17-pool 微特征不动 — 本 follow-up 给其中 6 pool 加深度 + 加 bias，其它 11 pool 保持 uniform。
- follow-ups 001-051：所有 HTTP routes + JSON shapes byte-identical；prompt 内容更丰富 (用户感知就是图更多样 + archetype 更连贯)。

## Follow-up 070 — 2026-05-17 17:00:51
Source: user_input/follow_ups/070-20260517-170051-markdown-pre-no-horizontal-scroll.md
Summary: Reader 内 markdown-rendered shotXX.md / 角色 ref / 等 fenced ``` ```text ``` ``` 代码块仍有横向滚动条 — follow-up 069 仅修了 `PromptPreviewModal` 内 prompt 卡片，没动 Reader 渲染 markdown 时的 `<pre>` 元素。三处 `<pre>` 容器 `.markdown-view pre` / `.code-view pre` / `.jsonl-line pre` 都改 `white-space: pre-wrap` + `overflow-wrap: anywhere` + `word-break: break-word` + `overflow-x: hidden`（替代旧的 `overflow-x: auto`）— 长 prompt 自然换行无横条；换行符仍由 pre-wrap 保留不破多行 prompt 结构。

Frontend only:
- `apps/ui/src/styles.css`:
  - `.markdown-view pre`: 删 `overflow-x: auto`；加 wrap 三件套 + `overflow-x: hidden`；line-height 1.6→1.65。
  - `.code-view pre`: 同上 wrap 策略。
  - `.jsonl-line pre`: `white-space: pre` → `pre-wrap`；删 `overflow-x: auto`；加 wrap 三件套。
- 零 JSX / 后端 / endpoint / spec FR 改动。

Safety:
- pre-wrap 保留 `\n`：multi-line YAML / JSON / shot prompt 结构（每个 `字段: 值` 一行）不被破坏。
- 复制粘贴行为不变 — wrap 仅视觉；剪贴板内容是 raw text。
- `overflow-wrap: anywhere` 在 long URL 中间也会 break；本场景 shot prompt 不放 URL，可接受。

## Follow-up 069 — 2026-05-17 16:49:15
Source: user_input/follow_ups/069-20260517-164915-prompt-preview-card-polish-no-overflow.md
Summary: `PromptPreviewModal` 每张 prompt card 视觉优化 + 强制无横向滚动条。三层 overflow 防御保证 2000+ 字 prompt 不出横条：(a) `.prompt-preview-card` outer `overflow: hidden`；(b) `.prompt-preview-body` `overflow-x: hidden + overflow-y: auto + max-height: 360px` 内滚；(c) `.prompt-preview-toggle` / `.prompt-preview-attrs` / `.prompt-preview-body` 三处都加 `overflow-wrap: anywhere + word-break: break-word`。同步美化：圆角 4→6、padding 8/10→12/14、background `bg-toolbar`→`bg-panel`、hover 加 `border-strong + 阴影`、`<ol decimal inside>` → `list-style: none`（与 meta 行 "第 N 张" 重复 marker 删）、seed pill (圆角 10 + 1px border)、attrs 加底色 + 边框 + padding 5/9、details 原生 marker 隐藏自定义 ▸/▾ 箭头、body line-height 1.5→1.7 + font-size 12→12.5、panel max-width 900→980 / width 90vw→92vw。

Frontend only:
- `apps/ui/src/styles.css` `.prompt-preview-*` 9 个 class block 重写（panel / hint / list / card / meta / seed / attrs / toggle / body）。
- 零 JSX / 后端 / endpoint / spec FR 改动。
- 跨浏览器: `::marker` + `::-webkit-details-marker` 双写覆盖 Safari + Chromium + Firefox。

User-input:
- `user_input/revised_prompt.md`: composed-from + Last regenerated narrative for 069。
- `user_input/follow_ups/069-20260517-164915-prompt-preview-card-polish-no-overflow.md` (NEW; originally 068 — 与用户 parallel 068 (SRP-extract-infra-exceptions) 撞号，本 follow-up renumber 到 069)。

## Follow-up 068 — 2026-05-17 16:44:19
Source: user_input/follow_ups/068-20260517-164419-srp-extract-infra-exceptions.md
Summary: 应用 SRP 到 infrastructure：exception class 不再混在 writer/reader 文件里，全部抽到 `libs/infrastructure/errors/{aggregate}__error.py`（与 `libs/domain/errors/` 镜像）。43 个 exception class 从 8 个 writer/reader 文件抽出到 7 个 errors 文件。Writer/reader 用 `from libs.infrastructure.errors.X import (...)` 重新 import 以保持向后兼容（commands 仍可 `from libs.infrastructure.writers.X import SomeException`）。

Common-level rule 加 (`agent_refs/project/development.md` §1 + `CLAUDE.md` § Project rules):
- **Single Responsibility Principle — one concern per file**：exception 不在 writer；DAO dataclass 不在 writer (`libs/infrastructure/daos/`)；DTO 不在 command/query (`libs/application/dtos/`)；Pydantic request body 不在 command/query (route handler)。

Exception extractions (43 总数):
- `writers/actor__writer.py`: 6 (InvalidAttribute, GenerationDirMissing, ActorNotFound, ActorAlreadyDeleted, ActorDeleteTargetExists, ActorDeleteFailed) → `errors/actor__error.py`
- `writers/casting__writer.py`: 2 (InvalidActorId, InvalidRole) → `errors/casting__error.py`
- `writers/character_video__writer.py`: 8 (InvalidPath, NotFound, FfmpegMissing 共享 + NotCharacterVideo, TruncateFailed, NotShotMd, NoCharacterTable, ConcatFailed) → `errors/character_video__error.py`
- `writers/downloads__writer.py`: 1 (DownloadsDirMissing) → `errors/downloads__error.py`
- `writers/file__writer.py` + `readers/file__reader.py`: 9 (UnsupportedExtension, FileTooLarge, InvalidBodyEncoding, OutsideSandbox, MissingIfUnmodifiedSince, StaleWrite from writer; FileTooLarge, OutsideSandbox, UnsupportedExtension from reader — dedup) → `errors/file__error.py`
- `writers/frame__writer.py`: 5 (InvalidPath, NotFound, NotVideo, FfmpegMissing, ExtractFailed) → `errors/frame__error.py`
- `writers/media__writer.py`: 12 (InvalidPath, NotFound, NotMedia, AlreadyArchived, NotInArchive, AlreadyDeleted, NotInAiVideos, NotInDeleted, TargetExists, MoveFailed, InvalidDramaPath, DramaNotFound) → `errors/media__error.py`

Implementation: one-shot Python script `_extract_errors.py` (deleted after this turn) scanned each writer/reader, regex-extracted `^class Xxx(Exception):` blocks (including multi-line bodies like `StaleWrite.__init__`), built per-aggregate errors files with proper docstrings, and inserted `from libs.infrastructure.errors.X__error import (...)` at top of each rewritten writer. `# noqa: F401` on re-imports because external callers (commands) still resolve `from libs.infrastructure.writers.X import SomeException` via the writer's re-export.

Domain side unchanged: `libs/domain/errors/{aggregate}__error.py` already exists per follow-up 056. Naming distinction preserved — domain errors are `*Error` (semantic, raised by commands for app-layer concerns), infra exceptions are bare names (raised by infra primitives for filesystem/HTTP/subprocess failures); commands catch infra → re-raise as domain.

Out of scope (deferred):
- DAO dataclass extractions to `libs/infrastructure/daos/{aggregate}__dao.py` (e.g., TruncateResult, ConcatResult, MoveResult, RenameResult, GenerateResult, ActorInfo, …). Rule is in place to flag at next stage-5 review.
- Command rewrites to import from errors files directly (currently they import from writer; that still works via re-export). Mechanical cleanup, orthogonal.

Smoke test:
- `python -c "import every libs/* module"` — 0 errors
- `python -c "import apps.api.main; import apps.api.asgi"` — boot clean (still relevant after follow-up 066 fix)
- `python -m pytest tests/` — 18 pass / 5 pre-existing wukong fixture failures (=066/067 baseline, 0 regressions)
- `grep -E "^class \w+\(Exception\):" libs/infrastructure/writers/*.py libs/infrastructure/readers/*.py` — 0 matches (acceptance gate passes)
- `find libs/infrastructure/errors -name "*.py" -not -name "__init__.py" | wc -l` = 7

Auto-updated:
- `.claude/agent_refs/project/development.md` §1 — 新增 SRP paragraph (4 concrete extractions listed) 放在 dependency-arrow 段后、file-size guideline 前。
- `CLAUDE.md` § Project rules — 新增 SRP bullet 引用 development.md §1。
- `projects/ai_video_management/libs/infrastructure/errors/{actor,casting,character_video,downloads,file,frame,media}__error.py` (7 NEW files, 43 class definitions).
- `projects/ai_video_management/libs/infrastructure/writers/*.py` 7 files + `readers/file__reader.py` — 各加 `from libs.infrastructure.errors.X__error import (...)` re-export，原 inline exception class definitions 删除。

No conflicts found in:
- follow-up 067 (look enum domain/infra sync)：纯 enum extension，与 SRP exception extraction 正交。
- follow-up 066 (main/asgi create_app import fix)：纯 import path bugfix，本 follow-up 不动 main/asgi。
- follow-up 065 (routes split + file-size rule)：本 follow-up 是 65/66 系列的姊妹 — SRP 是 "one concern per file" 的更深刻表达，file-size 是其表象之一。
- follow-ups 052/053/054 (actor body image / diverse mode / character_video)：新 exception class（如果有）会自动落入正确的 errors 文件，无 conflict。
- follow-ups 001-064：所有 commands 仍按旧路径 import exceptions from writers (re-export 保留 back-compat)，HTTP routes + JSON shapes byte-identical。

## Follow-up 067 — 2026-05-17 16:35:05
Source: user_input/follow_ups/067-20260517-163505-look-enum-domain-infra-sync.md
Summary: 修 follow-up 064 漏的第二份 `LOOK_OPTIONS`。064 把 5 个新 look 值（righteous / sinister / seductive / cunning / innocent）只加到 infrastructure 层 `actor__writer.py::LOOK_OPTIONS`，但 domain 层 `actor__valueobject.py::LOOK_OPTIONS` 仍是原 8 项；application layer 的 `ActorQuery.preview_prompts` / `ActorCommand.generate` 先调 `ActorAttrs.validate()`（domain）→ `InvalidActorAttributeError` → routes 映射 400 invalid_attribute → 用户看到 "预览失败: 400 invalid_attribute"。

Fix:
- `libs/domain/value_objects/actor__valueobject.py::LOOK_OPTIONS` frozenset 加 5 个 slug `righteous` / `sinister` / `seductive` / `cunning` / `innocent`；inline 注释提醒 MUST stay in sync with infrastructure 层 LOOK_OPTIONS。

Smoke test:
- `ActorAttrs(look="righteous"|...).validate()` 5 个新值全部 pass ✓
- `ActorAttrs(look="unknown_xyz").validate()` 仍正确 raise InvalidActorAttributeError ✓

Class-of-bug note: DDD enum-duplication anti-pattern — 6 个 closed enums (ETHNICITY / GENDER / AGE_RANGE / LOOK / STYLE / RESOLUTION) 每个都在 domain + infra 各定义一份；任何扩展 must touch both。Long-term cleanup: infra 应 `from libs.domain.value_objects.actor__valueobject import LOOK_OPTIONS` 而非自定义。本 follow-up 不做结构 refactor，仅修 064 漏的具体 mismatch。

No frontend / spec FR / endpoint changes.

## Follow-up 066 — 2026-05-17 16:29:55
Source: user_input/follow_ups/066-20260517-162955-fix-main-asgi-create-app-import.md
Summary: Bugfix to follow-up 065. `apps/api/main.py:13` + `apps/api/asgi.py:16` 还在 `from apps.api.routes import create_app` 旧位置 — 但 `apps/api/routes` 现在是 per-aggregate routes 包，`create_app` 实际在 `apps/api/app_factory.py` (since follow-up 051)。一行修：两处 import 改 `from apps.api.app_factory import create_app`。Pytest 漏抓因为 `tests/conftest.py:make_app` 已在 065 中修过；`make run-backend` (走 main.py) 才触发 ImportError。

Auto-updated:
- `projects/ai_video_management/apps/api/main.py` — line 13 import path fix。
- `projects/ai_video_management/apps/api/asgi.py` — line 16 import path fix。
- `projects/ai_video_management/specs/development/ai_video_management/user_input/follow_ups/066-...md` (NEW)
- `projects/ai_video_management/specs/development/ai_video_management/user_input/revised_prompt.md` — header bumped (next).
- `specs/development/ai_video_management/final_specs/spec.md` / `validation/*` — 不需要 surgical patch；纯 import-path fix，行为零变化。

Smoke test:
- `python -c "import apps.api.main"` — 0 errors。
- `python -c "import apps.api.asgi"` — app constructs OK, title='ai_video_management'。
- `python -m pytest tests/` — 18 pass / 5 pre-existing wukong fixture failures (与 065 baseline 完全一致，0 regressions)。

Class-of-bug note: 这是 follow-up 065 的回滚-recovery 步骤里未跑遍的 import site。065 用 Python regex sweep 改了 `from libs.infrastructure.X` 路径但 `from apps.api.routes import create_app` 是 `apps.*` 不在那个 sweep 范围；conftest.py 后来手动修了，main.py + asgi.py 漏。未来可加 stage-5 smoke: `python -m apps.api.main --no-reload` 跑 1 秒收 SIGINT — 现在的 boot_smoke 测试用 `make_app()` 路径，跳过了 main.py / asgi.py 入口。

No conflicts found in:
- follow-up 065 (routes split + file-size rule)：本 follow-up 是 065 routes-split 工作的 import-site-完整性 bugfix；065 的所有 contracts/layout 全部保留。
- follow-ups 062/063/064 (前端 UI changes / unified mode / shot concat tweaks)：纯前端 / 内容契约，与 backend boot fix 正交。
- follow-up 051 (create_app moved to app_factory)：本 follow-up 终于把 main.py + asgi.py 也对齐到 app_factory 位置（051 时移过 routes.py 但忘了同步 main/asgi import — 该 import 一直 broken 但未被 pytest 抓到，因为 conftest 单独 import path）。

## Follow-up 065 — 2026-05-17 16:22:02
Source: user_input/follow_ups/065-20260517-162202-split-routes-by-aggregate-file-size-rule.md
Summary: 双重改动：(1) 加文件大小规则 (`< 100 行 preferable, split by sub-concern when bigger`) 到 `agent_refs/project/development.md` §1。(2) 拆分 `apps/api/routes.py` (847 行) 到 `apps/api/routes/{aggregate}__route.py` 8 个 per-aggregate 文件 + `_helpers.py` + `__init__.py` (combined router)。同时清理本 turn 开局发现的 OLD/NEW 路径混乱状态 (5 flat infra 文件 / 11 OLD-path imports / container.py + agent_refs §1 + CLAUDE.md 都被回滚到 pre-051 状态)。

Routes split (apps/api/routes/):
- tree__route.py: 18 行 (GET /api/tree)
- file__route.py: 81 行 (GET/PUT /api/file)
- media__route.py: 204 行 (serve / archive / unarchive / delete / hard_delete / rename + 6 method_not_allowed)
- frame__route.py: 54 行 (POST /api/extract-frames)
- downloads__route.py: 44 行 (POST /api/import-from-downloads)
- actor__route.py: 238 行 (generate / generate-diverse / preview-prompts / preview-diverse / list / delete / assignments + 7 method_not_allowed + helpers)
- casting__route.py: 105 行 (read / assign / unassign)
- character_video__route.py: 84 行 (truncate / concat-shot)
- _helpers.py: 55 行 (file_security_headers, method_not_allowed, actor_assigned_409, map_move_failure)
- __init__.py: 30 行 (combines 8 sub-routers)

File-size rule (common-level, in `agent_refs/project/development.md` §1):
- Guideline: `< 100 行 preferable`, split direction matches layer's existing role taxonomy
- Hard cap `~1000 行` 无清晰 sub-concern boundary = stage-5 `warning` (not blocker)
- Aggregates with legitimately complex business logic (variance pools / prompt assembly) may exceed
- Examples: routes.py → routes/{aggregate}__route.py; bulky *__writer.py 按 operation 切分 if no shared state

Pre-turn recovery work (codebase was in inconsistent OLD/NEW state):
- Detected: `apps/api/{container,asgi,main,routes}.py`, `apps/api/routes.py`, `libs/infrastructure/{actor_pool,casting,downloads__importer,...}.py`, `agent_refs/project/development.md` §1, `CLAUDE.md` § Project rules — 全被回滚到 pre-051 状态
- BUT `libs/{application,domain,infrastructure}/` 子目录 + apps/api/app_factory.py + 我这 turn 写的 apps/api/routes/ 都还在 (NEW layout exists alongside OLD)
- Forward-fix per user 选择：
  - Moved 5 flat infra files into sub-folders (casting__writer, file__writer, file__reader, tree__reader, origin_host__middleware)
  - Deleted 5 superseded flat infra files (actor_pool, downloads__importer, frame__extractor, media__archiver, media__renamer) — writers/ 子目录已有 newer versions (含 follow-up 052/053/054 work)
  - Deleted apps/api/routes.py (新 routes/ folder takes over)
  - Bulk import rewrite: 17 subs across 7 files (apps/api/asgi.py + main.py + container.py + tests + libs/infrastructure/writers/casting__writer.py)
  - Rewrote apps/api/container.py: 12 Factory providers (post-061 aggregate Q/C wiring with `wiring_config = packages=["apps.api.routes"]` per 062)
  - Restored agent_refs/project/development.md §1 sub-bucketing tree + file-per-aggregate + one-class-per-Q/C + routes-mirror rules
  - Restored CLAUDE.md § Project rules bullets (solution-layout mandate + commands-via-domain + file-size guideline)

Note on NOT restored: follow-ups 051/056/060/061 had broader common-ref work (§6b empty-application-layer blocker, §11b validation grep checks, §3 application-layer rewrite, §4 file-pattern table) — those were ALSO rolled back this turn but NOT re-restored. The codebase enforces the rules; the documentation just doesn't currently cite them. Future cleanup can re-add if desired.

Smoke test:
- `python -c "import every module under libs/"` — 0 errors
- App constructs OK (41 routes via 12 Q/C aggregate classes wired via Container)
- `python -m pytest tests/` — 18 pass / 5 pre-existing wukong fixture failures (identical to baseline; 0 regressions)
- `wc -l apps/api/routes/*.py` — every per-aggregate file ≤ 238 lines (vs old 847-line single file)
- `wiring_config = packages=["apps.api.routes"]` — all per-aggregate route modules auto-wired

Common refs:
- `.claude/agent_refs/project/development.md` §1 — restored sub-bucketing tree (4 layers × role sub-folders) + file-per-aggregate / one-class-per-Q/C / routes-mirror rules + NEW file-size guideline.
- `CLAUDE.md` § Project rules — restored solution-layout / commands-via-domain bullets + NEW file-size guideline bullet.

Project-scoped (specs/development/ai_video_management/):
- `user_input/follow_ups/065-20260517-162202-split-routes-by-aggregate-file-size-rule.md` (NEW)
- `user_input/revised_prompt.md` — header bumped (after this commit)
- `final_specs/spec.md` / `validation/*` — 不需要 surgical patch；routes/ 拆分是内部结构，HTTP 行为零变化。

Auto-updated:
- `.claude/agent_refs/project/development.md` — §1 sub-bucketing 恢复 + file-size 规则。
- `CLAUDE.md` — § Project rules bullets 恢复 + file-size guideline。
- `projects/ai_video_management/apps/api/routes/` (NEW dir + 10 files)
- `projects/ai_video_management/apps/api/routes.py` (DELETED)
- `projects/ai_video_management/apps/api/container.py` (rewritten — 12 aggregate Q/C Factory providers + `packages=` wiring)
- `projects/ai_video_management/apps/api/{asgi,main}.py` (import path fix + `packages=` wiring)
- `projects/ai_video_management/libs/infrastructure/{actor_pool,downloads__importer,frame__extractor,media__archiver,media__renamer}.py` (DELETED — superseded by sub-folder versions)
- `projects/ai_video_management/libs/infrastructure/{casting__writer,file__writer,file__reader,tree__reader,origin_host__middleware}.py` → moved to sub-folders
- `projects/ai_video_management/libs/infrastructure/writers/casting__writer.py` — internal imports fixed (actor_pool / media_renamer → writers/ paths)
- `projects/ai_video_management/tests/{conftest,test_*}.py` — import path updates (create_app from app_factory, BoundOrigin from common.origin, infra paths to sub-folders)

No conflicts found in:
- follow-up 062 (confirm-send modal) / 063 (dropdown labels) / 064 (shot concat + unified mode)：纯前端 / 内容契约，与 routes split 正交。
- follow-up 061 (one-class-per-Q/C)：本 follow-up 在 061 的 aggregate Q/C 单类基础上对 routes 做同样的 per-aggregate 拆分 — pattern 一致。
- follow-up 060 (libs file-per-aggregate)：routes/ 现在 mirror application/{queries,commands}/ 的 per-aggregate file 命名。
- follow-up 056 (sub-bucketing)：routes/ 是同样的 per-role sub-folder 模式，apps/api/ 内的应用。
- follow-up 051 (DDD layering)：routes/ 内每 handler 仍 inject aggregate Q/C 并 call method (per 061 convention)；零 infra import。
- follow-ups 001-050 + 052-058：所有 HTTP routes + JSON shapes byte-identical；routes 拆分 + file-size 规则仅文档/结构变化。

## Follow-up 064 — 2026-05-17 15:34:14
Source: user_input/follow_ups/064-20260517-153414-unified-mode-random-defaults-look-extension.md
Summary: 合并 standard / diverse mode 为一；每个属性下拉加 🎲 随机 sentinel 作 default；扩 look 枚举加 5 个角色性格值（正义 / 阴邪 / 妩媚 / 狡诈 / 天真）；删除 mode toggle radio。Backend `preview_prompts` 加 optional `seeds` 参数（previously N 并行 count=1 调用因毫秒精度 `time.time()` 撞同 base_seed → 同 prompt → 同图）。前端 onPreview 给每个 slot 滚 random（仅对 `__random__` 字段） + 显式 `seeds: [Date.now()+i]` + `Promise.all` 并行 N 个 `previewPrompts({count: 1, ...})`，聚合成 `PromptPreviewResult`。Confirm 路径从 preview entries 取 per-slot resolved attrs。

Backend:
- `libs/infrastructure/writers/actor__writer.py`:
  - `LOOK_OPTIONS` 加 5 slug: righteous / sinister / seductive / cunning / innocent。
  - 新 `_LOOK_ENRICHED: dict[str, str]` 映射 5 新 slug 到 enriched English prompt fragment（旧 8 slug 保留 bare adjective behavior 经 `.get(slug, slug)` fallback）。
  - `_build_face_prompt` + `_build_body_prompt` 用 `_LOOK_ENRICHED.get(attrs.look, attrs.look)` 替代 raw `attrs.look`。
  - `preview_prompts` 签名加 `seeds: list[int] | None = None`，validate `len(seeds) == count` + 全 int；providing → per-slot seed = seeds[i]；omitted → fallback base_seed + i.
- `libs/domain/repositories/actor__repository.py`: `preview_prompts` Protocol 同步 seeds 参数。
- `libs/application/queries/actor__query.py` `ActorQuery.preview_prompts`: plumb `input_cdto.seeds` 到 `pool.preview_prompts`。

Frontend:
- `apps/ui/src/api.ts`:
  - `ATTR_OPTIONS.look` append 5 new slug。
  - 新 `ATTR_LABELS_ZH: { [K in keyof typeof ATTR_OPTIONS]: Record<string, string> }` 6 字段全中文映射（含 5 新 look slug：正义 / 阴邪 / 妩媚 / 狡诈 / 天真）。
  - 新 export `RANDOM_SENTINEL = "__random__"` + `rollRandomAttr<K>(field)` helper。
  - 新 interface `PromptPreviewSlot { seed, prompt, body_prompt?, attrs? }`；`PromptPreviewResult.prompts` 类型从 `{seed, prompt}[]` → `PromptPreviewSlot[]`。
  - `GenerateActorsRequest` 加 optional `archetype?: string | null` (forward-compat with future archetype-tagging via per-slot generate)。
- `apps/ui/src/components/ActorPoolGenerator.tsx`:
  - 删除 mode state + radio toggle (`mode === "standard"` / `mode === "diverse"`)。
  - 5 个 attr state 默认值 `useState<string>(RANDOM_SENTINEL)`（resolution 仍默认 normal — 混合 1024/2K/4K 输出 rarely 是用户想要的）。
  - 每个 `<select>` 第一个 `<option value={RANDOM_SENTINEL}>🎲 随机</option>` + 后续具体 options 用 `ATTR_LABELS_ZH[field][o]` 显示中文。
  - `onPreview` 重写：roll random per-slot per-field，N parallel `previewPrompts(count=1, seeds=[base+i])`，聚合 `PromptPreviewResult` 含每 slot 的 resolved attrs。
  - `onConfirmGenerate` worker：从 `previewSnapshot.prompts[slot-1].attrs` 取 per-slot resolved attrs 传给 `generateActors`。
  - `setPreview(null)` 在 onConfirmGenerate 启动 worker pool 前（follow-up 062 carry-over）。
  - 移除 backdrop `onClick={onCloseRequest}` + footer "关闭" button（follow-up 058 carry-over）。
  - Count input switch to `type="text" inputMode="numeric"` + countText string state + derived count + 三重 event guard（follow-up 055 + 057 carry-over）。
- `apps/ui/src/styles.css`: 加 `.prompt-preview-attrs` (monospace muted)。

Spec / validation: deferred batch.

User-input:
- `user_input/revised_prompt.md`: composed-from + Last regenerated 重写为 064。
- `user_input/follow_ups/064-20260517-153414-unified-mode-random-defaults-look-extension.md` (NEW)。

## Follow-up 063 — 2026-05-17 15:31:00
Source: user_input/follow_ups/063-20260517-153100-generator-dropdown-chinese-labels.md
Summary: ActorPoolGenerator 6 个下拉菜单 option 文本汉化（民族 / 性别 / 年龄段 / 外貌气质 / 风格 / 画质）。`<option value>` 保留 slug；仅显示中文。已 bundled 入 follow-up 064 落地。

## Follow-up 062 — 2026-05-17 15:22:34
Source: user_input/follow_ups/062-20260517-152234-confirm-send-close-preview-show-progress.md
Summary: 修 "点击确认发送后 UI 没反应" 的 bug。`onConfirmGenerate` 启动 9-worker pool 但从不调 `setPreview(null)`，预览模态遮住 ProgressPanel。`apps/ui/src/components/ActorPoolGenerator.tsx::onConfirmGenerate`：在 busy guard 之后立刻 `setPreview(null)` —— 关闭预览模态让 ProgressPanel 浮上来。已 bundled 入 follow-up 064 落地（previewSnapshot 局部变量保留 plan，setPreview(null) 触发 unmount）。

## Follow-up 045 — 2026-05-14
Source: user_input/follow_ups/045-20260513-231500-env-file-location-and-asgi-mismatch.md
Summary: Backend boot 失败 `RuntimeError: kling env keys missing` 的两层修复：(1) `apps/api/asgi.py` 的 env-path bug — 残留 `Path(__file__).resolve().parent.parent / ".env"` 来自原 `backend/libs/asgi.py`，在新路径 `apps/api/asgi.py` 下解析到 `apps/.env`（高了一层），与 `main.py` 的 `apps/api/.env` 不一致；改为 `parent / ".env"` 对齐。(2) 创建 `apps/api/.env` 包含 `KLING_ACCESS_KEY` + `KLING_SECRET_KEY`（用户私下提供，已通过 `git check-ignore` 确认被 repo root `.gitignore` line 138 catches；密钥值本身**不**写入任何 spec / changelog / 提交文件）。

Auto-updated:
- projects/ai_video_management/apps/api/asgi.py — `Path(__file__).resolve().parent.parent / ".env"` → `Path(__file__).resolve().parent / ".env"`，与 `main.py` 一致。
- projects/ai_video_management/apps/api/.env — 新建（**untracked**, gitignored），包含 KLING_ACCESS_KEY + KLING_SECRET_KEY 用户私下提供的值。
- specs/development/ai_video_management/user_input/revised_prompt.md — `Last regenerated` header bumped；`Composed from` 列表更新到 001–044 + 045。

Smoke verification: `python -c "from apps.api.asgi import app; ..."` 报告 `asgi build OK, routes: 36`，`KLING_ACCESS_KEY loaded: True`，`KLING_SECRET_KEY loaded: True`，并且 `git ls-files apps/api/.env` 返回空（未追踪）。

No conflicts found in: final_specs/spec.md, validation/*, libs/common/env_loader.py（已正确容忍 FileNotFoundError）, apps/api/main.py（路径表达式已正确）. Spec acceptance unchanged — 045 is an implementation gap fix, not a behavior change.

## Follow-up 044 — 2026-05-13 23:05:00
Source: user_input/follow_ups/044-20260513-230500-missing-lib-dramas-ts.md
Summary: 修 Vite import-analysis 错误 `Failed to resolve import "../lib/dramas" from "src/components/ActorView.tsx"`. follow-up 043 item #9 把 `extractDramas` / `findChild` / `DramaChoice` 从 `ActorGrid.tsx` 抽取到 `apps/ui/src/lib/dramas.ts`，但抽取目标文件从未被写入；ActorGrid.tsx + ActorView.tsx 的 `../lib/dramas` import 因此解析失败。新建 `apps/ui/src/lib/dramas.ts` 含 043 之前 commit (5abfd1a) 的原始 inline 实现——byte-for-byte 等价，零行为变化。

Auto-updated:
- projects/ai_video_management/apps/ui/src/lib/dramas.ts — 新建，包含 `DramaChoice` interface + `extractDramas(tree)` + `findChild(node, name)`。
- specs/development/ai_video_management/user_input/revised_prompt.md — `Last regenerated` header bumped to 2026-05-13 23:05:00；`Composed from` 列表归并到 001–043 + 044。

No conflicts found in: final_specs/spec.md, validation/*, projects/ai_video_management/apps/ui/src/components/{ActorView,ActorGrid}.tsx（imports 已是 `../lib/dramas`，无需修改）. Spec/AC unchanged — 044 fixes an implementation gap, not a behavior change; 043's spec walk and acceptance still apply.

## Follow-up 043 — 2026-05-13 22:47:37
Source: user_input/follow_ups/043-20260513-224737-assign-from-actor-page-character-link.md
Summary: ActorView 新增"🎬 角色分配 (N)"区块 + 级联 drama→role dropdown + assign/unassign 行内按钮；后端 `Casting.assign` / `unassign` 同步维护 `ai_videos/{drama}/characters/{role}/_cast.md`（含 face 图 markdown 链接 + 演员档案链接）；`POST /api/actors/delete` 从 cascade-unassign 改为 refuse-if-assigned；`POST /api/archive-media` / `POST /api/delete-media` 对 `_actors/{id}/` 下路径同样 409 if assigned；新 endpoint `GET /api/actors/assignments`。一个 actor 可分配到多个 drama+role，同一 (drama, role) 上仅一个 actor（casting.md upsert 已保证）。

Backend:
- `libs/casting.py`:
  - 新常量 `CAST_LINK_FILE_NAME = "_cast.md"`、`_ACTOR_ID_SHAPE_RE`。
  - `Casting.assign()` 末尾追加 `_write_character_link(drama_dir, role, actor_id, notes)` — character folder 不存在则静默跳过，否则原子写 `_cast.md`（temp+os.replace），内容 Chinese metadata 表 + 内嵌 `![face]` + 演员档案链接 + 维护注释。
  - `Casting.unassign()` 末尾追加 `_remove_character_link(drama_dir, role)` — best-effort `unlink(missing_ok=True)`。
  - `Casting.unassign_actor_everywhere()` 内循环增加 `_remove_character_link` 调用（保留方法供 admin 工具用，endpoint 不再调）。
  - 新方法 `find_assignments_for_actor(actor_id)`：扫所有 drama 的 casting.md，返回 `[{drama, role, notes, character_folder, character_folder_exists}, ...]` 按 (drama, role) 排序；shape-validation 失败抛 `InvalidActorId`。
  - 新静态方法 `_build_character_link_body(drama, role, actor_id, notes, face_filename)`：返回完整 markdown body。
  - `__all__` 加 `CAST_LINK_FILE_NAME`。
- `libs/actor_pool.py`:
  - 新公开方法 `actor_face_filename(actor_id) -> str | None`：wraps `_find_actor_jpg`，返回 jpg 的 bare filename；用于 `_cast.md` 内嵌图相对路径计算。
- `libs/api.py`:
  - `POST /api/actors/delete` 重写：先调 `casting.find_assignments_for_actor`；非空 → 409 `{kind:"actor_is_assigned", assignments:[...]}` 不动文件夹；空 → 原 `actor_pool.delete_actor` 路径，响应 `unassigned: []`（保留字段空数组兼容 v1 client）。`casting.unassign_actor_everywhere` 不再调用。
  - 新 endpoint `GET /api/actors/assignments?actor_id=...`：调 `find_assignments_for_actor` → 200 / 400 invalid_actor_id / 405 method_not_allowed。
  - 新 inner helper `_refuse_if_actor_assigned(path)`：若 path 形如 `ai_videos/_actors/actor_NNNN/...`，extract actor_id 并查 `find_assignments_for_actor`；非空返 `JSONResponse(409, ...)` 否则 None。
  - `POST /api/archive-media` 与 `POST /api/delete-media` 在入口处调 `_refuse_if_actor_assigned(body.path)`；非 None 直接返回。

Frontend:
- `src/lib/dramas.ts` (NEW)：抽出 `extractDramas` + `findChild` + `DramaChoice` 类型；ActorGrid + ActorView 共享。
- `src/components/ActorGrid.tsx`：移除本地 `extractDramas` / `findChild` 与 `DramaChoice` interface；import 共享版本；行为完全相同。
- `src/api.ts`：新增 `ActorAssignment` / `ActorAssignmentsResult` interface + `fetchActorAssignments(actorId)` 函数。
- `src/App.tsx`：`<Reader>` 调用追加 `tree={tree}` prop。
- `src/components/Reader.tsx`：`ReaderProps` 加 `tree: TreeNode | null`；`<ActorView>` 调用追加 `tree={tree}`。
- `src/components/ActorView.tsx`:
  - 新 import `useCallback`/`useEffect` + `castingAssign`/`castingUnassign`/`fetchActorAssignments`/`ActorAssignment` + `extractDramas`/`DramaChoice` + `TreeNode`。
  - Props 加 `tree: TreeNode | null`。
  - 新 state：`assignments` / `assignLoading` / `assignError` / `unassigning` / `formOpen`。
  - 新 `loadAssignments` callback；`useEffect` mount 时拉。
  - 新 `onUnassign(a)` handler：调 `castingUnassign` + 刷新；失败 inline alert。
  - 新 `onAssigned()` callback：关表单 + `onSaved()` + 重拉。
  - delete 按钮 `disabled` 增 `deleteDisabledReason !== null` 条件 + tooltip 文案 "actor 当前已分配到 N 个角色，无法删除"。
  - 新 JSX 区块 `actor-view-assignments`：header + 错误 alert + assignment 列表 + "＋ 添加分配" 按钮 / 行内 `<AssignForm>`。
  - 新内部组件 `AssignForm`：drama / role 级联 `<select>` + notes textarea + 已分配预警 + 确认按钮；调 `castingAssign(path=ai_videos/{drama}, role, actorId, notes)`。
  - 新 helper `formatError(err)`：识别 `actor_is_assigned` kind 并把 assignments 摘要拼进文案。
- `src/styles.css`：新增 `.actor-view-assignments` 容器 + `.actor-view-assignment-list` / `-row` / `-drama` / `-sep` / `-role` / `-warn` / `-notes` / `-unassign-btn` + `.actor-view-assign-btn` + `.actor-view-cancel-btn` + `.actor-view-assign-form` + form-row + form-actions 规则。复用既有 token `--bg-panel` / `--border` / `--text-muted` / `--error-border` / `--error-text` / `--bg-hover`。

Spec / validation:
- `final_specs/spec.md` FR-9g：追加 follow-up 043 amendment 段描述 `_cast.md` 同步写入（路径、内容、character folder 不存在时静默跳过）。
- `final_specs/spec.md` FR-9h：追加 follow-up 043 amendment 段描述 `_cast.md` 同步删除（unlink missing_ok）。
- `final_specs/spec.md` FR-9i：完整改写 — 从 cascade-unassign 改为 refuse-on-assignment，加 `actor_is_assigned` 409 状态码；保留 `unassigned: []` 字段向后兼容；`Casting.unassign_actor_everywhere` 保留但 endpoint 不再调用。
- `final_specs/spec.md` FR-9s 新增：`GET /api/actors/assignments` 端点契约。
- `final_specs/spec.md` FR-9c / FR-9k extension 新增：archive-media / delete-media 对 `_actors/{id}/` 下路径的 409 enforcement。
- `final_specs/spec.md` FR-95 新增：ActorView assignments section 完整契约（区块、级联 dropdown、`_cast.md` 副作用链、delete 按钮 gating、`lib/dramas.ts` 共享）。
- `validation/acceptance_criteria.md` U3.23 新增：8 段 Gherkin 覆盖加载 / 表单提交 / `_cast.md` 写入 / delete 按钮 disabled / 三种 409 拒绝路径 / 取消分配 / `_cast.md` 删除 / character folder 不存在时静默跳过。
- 覆盖矩阵：FR-9s + FR-95 两行 → U3.23。

User-input:
- `user_input/revised_prompt.md`：composed-from 加 043；Last regenerated narrative 重写为 043 内容；原 042 narrative 降为 "Prior regen 4"。
- `user_input/follow_ups/043-20260513-224737-assign-from-actor-page-character-link.md` (NEW；最初以 038→041 命名，因 user 在同 turn 抢占 041 号被重命名为 043)。

Auto-updated:
- `projects/ai_video_management/backend/libs/casting.py` — assign/unassign/sweep 同步维护 `_cast.md` + 新 `find_assignments_for_actor` + `_build_character_link_body`。
- `projects/ai_video_management/backend/libs/actor_pool.py` — `actor_face_filename` 公开方法。
- `projects/ai_video_management/backend/libs/api.py` — `actors_delete` 改 refuse-on-assigned；新 `GET /api/actors/assignments`；`_refuse_if_actor_assigned` 内置 helper 接入 archive-media + delete-media。
- `projects/ai_video_management/frontend/src/lib/dramas.ts` (NEW) — 共享 drama/character 抽取。
- `projects/ai_video_management/frontend/src/components/ActorGrid.tsx` — import 改共享 `dramas.ts`；本地复制删除。
- `projects/ai_video_management/frontend/src/api.ts` — `fetchActorAssignments` + interfaces。
- `projects/ai_video_management/frontend/src/App.tsx` — `<Reader tree={tree} ...>` 透传。
- `projects/ai_video_management/frontend/src/components/Reader.tsx` — `tree` prop + `<ActorView>` 透传。
- `projects/ai_video_management/frontend/src/components/ActorView.tsx` — 主要扩展：assignments state / handlers / AssignForm 内部组件 / delete 按钮 gating。
- `projects/ai_video_management/frontend/src/styles.css` — `.actor-view-assignments` 区块与级联 form 样式。
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9g / FR-9h / FR-9i / FR-9s / FR-9c-9k extension / FR-95 改写或新增。
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.23 + 覆盖矩阵补 FR-9s / FR-95。

No conflicts found in:
- follow-up 014 (CastingView)：CastingView 仍走同一 `castingAssign`/`castingUnassign` API，因此 `_cast.md` 也会随 CastingView 操作同步写/删；零代码改动。
- follow-up 030 (ActorGrid bulk assign)：`AssignCharacterModal` 走相同 `castingAssign` → `_cast.md` 自动同步；本 follow-up 把 `extractDramas` 抽到共享 module，AssignCharacterModal 仍直接 import 它，行为零变化。
- follow-up 034 (ActorView read view)：ActorView dispatch / 三面板 / SiblingMedia skip 不变；assignments section 是第四个区块。
- follow-up 036 (actor folder 折叠)：sidebar 行 🗑 按钮仍调 `deleteActor` (FR-9i)；新增 server-side 409 通过 toast `archiveErrorKind` 显示 — Sidebar 已有 ApiError detail.kind 解析，无前端改动需要。
- follow-up 041 (frame extraction v2)：frame_extractor.py / MediaRenamer / FR-9r 全部不动；本 follow-up 仅改 casting + actor 相关路径。
- follow-up 042 (uvicorn force-exit)：纯进程退出兜底，不动任何 endpoint 实现。

Verification:
- `curl GET /api/actors/assignments?actor_id=actor_0013` → 200 `{actor_id, assignments: []}` ✓
- `curl POST /api/casting/assign actor_0013 → c1_沧冥` → 200 + 磁盘上 `ai_videos/mozun_chongsheng/characters/c1_沧冥/_cast.md` 出现，内容含 `actor_0013` + face filename + 中文 metadata + `![face]` + `[查看演员档案]` ✓
- `curl POST /api/actors/delete {actor_id:"actor_0013"}` while assigned → 409 `{kind:"actor_is_assigned", assignments:[{drama:"mozun_chongsheng", role:"c1_沧冥", notes:"test 041", character_folder, character_folder_exists:true}]}` ✓
- `curl POST /api/archive-media path="ai_videos/_actors/actor_0013/<jpg>"` while assigned → 409 `actor_is_assigned` ✓
- `curl DELETE /api/casting/assign role="c1_沧冥"` → 200 + `_cast.md` 文件消失 ✓
- 测试 fixture 清理：casting.md 恢复 header-only 状态，文件树未污染 ✓

## Follow-up 042 — 2026-05-13 22:50:19
Source: user_input/follow_ups/042-20260513-225019-uvicorn-force-exit-watchdog.md
Summary: 修 follow-up 037 没修干净的 dev-reload 卡死。`timeout_graceful_shutdown=2` 让 uvicorn asyncio task 在 2s 后 cancel，但 FastAPI sync `def` endpoint 在 anyio threadpool 里跑，cancel asyncio wrapper 不 kill 底层 OS 线程；Kling 30-120s HTTP / `/api/media` range stream / ffmpeg / pollinations 这些 blocking sync 调用让非-daemon 线程占住 Python 进程使 `sys.exit` 永久 join。新 `libs/uvicorn_force_exit.py::install()` monkey-patch `uvicorn.Server.handle_exit` 在 signal handler 后启动 daemon `threading.Timer((config.timeout_graceful_shutdown or 0) + 2.0, lambda: os._exit(0))`，~4s 内进程必死。`main.py` 与 `libs/asgi.py` 顶部各调一次（覆盖 reload 子进程 + --no-reload 两条启动路径）。

Backend:
- `libs/uvicorn_force_exit.py` (NEW):
  - 常量 `FORCE_EXIT_GRACE = 2.0`。
  - `install()`：检测 `uvicorn.Server._force_exit_installed` 幂等；wrap `Server.handle_exit(sig, frame)` — 先调原方法（保持 uvicorn 自己的 `should_exit` / `force_exit` 流程）再起 daemon `threading.Timer` deadline=`(config.timeout_graceful_shutdown or 0) + FORCE_EXIT_GRACE` → `os._exit(0)`。
  - 设 `Server._force_exit_installed = True` 防重复 wrap。
- `main.py`：import `from libs.uvicorn_force_exit import install as _install_force_exit_watchdog`；`args = parser.parse_args()` 之后立即调 `_install_force_exit_watchdog()`，覆盖 `--reload` / `--no-reload` 两分支。
- `libs/asgi.py`：顶部 import `_install_force_exit_watchdog` 并立即调用（reload 模式子进程通过 `uvicorn.run("libs.asgi:app", reload=True)` 启动时 import asgi → patch 生效）。

Spec / validation:
- `final_specs/spec.md` FR-2：追加 follow-up 042 amendment 段，描述 `install()` 调用点、wrap 行为、deadline 公式、~4s 总窗口、不动 `Server.config` / `Server.run` / endpoints 的边界。
- `validation/acceptance_criteria.md`：新增 manual **U2.5** scenario — reload 模式 + 长任务 in-flight 时改 libs/ 文件 → 进程 ≤ 4s 死 + 新 PID ≤ 6s 响应；2× CTRL+C 幂等；`--no-reload` SIGTERM 对称。
- `validation/acceptance_criteria.md`：覆盖矩阵 FR-2 行补 `, U2.5 (follow-up 042 force-exit watchdog)`。

User-input:
- `user_input/revised_prompt.md`：composed-from 加 042；Last regenerated narrative 重写为 042 内容；原 041 narrative 降为 "Prior regen 3"；原 040 / 039 narrative 各下移一格。
- `user_input/follow_ups/042-20260513-225019-uvicorn-force-exit-watchdog.md` (NEW)。

Auto-updated:
- `projects/ai_video_management/backend/libs/uvicorn_force_exit.py` (NEW) — `install()` patch.
- `projects/ai_video_management/backend/main.py` — import + 调用点。
- `projects/ai_video_management/backend/libs/asgi.py` — import + 调用点。
- `specs/development/ai_video_management/final_specs/spec.md` — FR-2 amendment。
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U2.5 manual scenario + 覆盖矩阵 FR-2 行扩展。

No conflicts found in:
- follow-up 037 (`timeout_graceful_shutdown=2`)：watchdog 的 deadline 公式直接读 `config.timeout_graceful_shutdown`；037 配置是本 follow-up 的前置依赖，不动其值。
- follow-up 040 (`_deleted/` 置底)：纯 `tree_walker._ai_videos_section` 改动，与 uvicorn lifecycle 正交。
- follow-up 041 (frame extraction v2)：`/api/extract-frames` 是 sync def + 调 ffmpeg 子进程；ffmpeg 进程在 watchdog 触发时不会被 cleanup（属于"interpreter dies → OS reaps subprocess" 范畴），与 follow-up 041 的 idempotent sweep 设计无冲突 — 下次启动 `frames/*.png` 重新清扫。
- follow-up 039 (`apps/+libs/` DDD+CQRS layout)：未应用到代码；当迁移时 `libs/uvicorn_force_exit.py` 搬到 `libs/infrastructure/` 或 `libs/common/`，patch 语义不变。
- follow-up 038 (hard-delete media)：`Path.unlink` 是单 syscall，watchdog 触发不会留半完成的 hard-delete。
- follow-up 026 (actor folder delete) / 023 (soft delete)：rename 是单 syscall atomic，同样无 watchdog 触发风险。
- Kling generation (follow-up 014/025/027/029)：actor jpg + sidecar md 是两个独立 atomic write；若 watchdog 在两者之间触发，下次启动 `_reap_incomplete_folders()` (follow-up 027) 扫掉残缺 folder。

## Follow-up 041 — 2026-05-13 22:58:00
Source: user_input/follow_ups/041-20260513-225800-frame-naming-v2-8-frames-priority-rank.md
Summary: 重做 scene 视频抽帧约定 — 5 帧 → 8 帧（5 dwell + 3 战略 transition），命名从 `_f{N}_{role}.png` → `_r{rank}_{role}_{shot_size}.png`（rank 1-8 = 上传优先级，字典序 = 优先级序）；`MediaRenamer` 两条 caller 加 `"frames"` 排除避免命名丢失实测 bug；extract 起点新增 `frames/*.png` sweep idempotent 清理。

Auto-updated:
- projects/ai_video_management/backend/libs/frame_extractor.py — `CANONICAL_FRAMES` 改 4 元组 shape `(timestamp, role, shot_size, rank)` 8 条；`FrameResult` 加 `rank: int` + `shot_size: str` 字段及 `to_payload`；`extract()` 头部新增 `_sweep_pngs(frames_dir)` 步骤；filename 模板 `{prefix}_r{rank}_{role}_{shot_size}.png`；module docstring 全面重写（8 帧 + rank + shot_size + sweep + idempotent 覆盖语义）。
- projects/ai_video_management/backend/libs/api.py — `POST /api/rename-media` handler 的 `media_renamer.rename_drama(body.path)` 调用增 `excluded_folder_names=frozenset({"frames"})` kwarg。
- projects/ai_video_management/backend/libs/downloads_importer.py — `self._renamer.rename_drama(rel_drama_path, ...)` 的 `excluded_folder_names` 从 `frozenset({NOT_MATCHED_DIR_NAME})` 扩到 `frozenset({NOT_MATCHED_DIR_NAME, "frames"})`。
- projects/ai_video_management/frontend/src/api.ts — `ExtractedFrame` interface 新增 `shot_size: string` 与 `rank: number` 字段。
- specs/development/ai_video_management/user_input/revised_prompt.md — 文件列表追加 041 + Last regenerated header bump（含 8 帧 schema 摘要 + renamer bug 修复说明 + FR-9r 新增说明）；040 历史段下移为 "Prior regen 2"。
- specs/development/ai_video_management/final_specs/spec.md — 在 FR-9j 与 FR-9i 之间插入新 FR-9r（`POST /api/extract-frames` 端点契约 v2：8 帧 CANONICAL_FRAMES 表 + rank rationale + sweep 语义 + `MediaRenamer` companion contract）。

No conflicts found in: interview/qa.md, findings/dossier.md, findings/angle-*.md, validation/strategy.md, validation/acceptance_criteria.md, validation/backend_tests.md, validation/security.md, validation/bdd_scenarios.md, frontend/components/SiblingMedia.tsx（仅消费 frames 数组，不解析 path 形状）, frontend/components/Reader.tsx（同上）, frontend/components/ActorView.tsx, backend/libs/media_archiver.py, backend/libs/actor_pool.py, backend/tests/test_boot_smoke.py（POST 路由矩阵已含 `/api/extract-frames`）, README, Makefile, `.claude/agent_refs/project/ai_video.md` rule #12.10-C（保留作为手动覆盖退路，不动）。

Severity: 中。Backend `FrameExtractor` 改动 + 数据模型变更（5→8 fields，frame dataclass +2 字段），但 HTTP route shape / request body / status code 全部保留。Frontend ExtractedFrame interface 新增字段是非破坏性扩展（SiblingMedia 与 Reader 仅消费 frames 数组本身，不读 role/rank/shot_size，未来若要展示这些字段是 follow-up 工作）。实测验证待 user 在 webapp 内点 "🎞 Extract Frames" 按钮触发并核对 frames/ 输出。

## Follow-up 040 — 2026-05-13 22:46:35
Source: user_input/follow_ups/040-20260513-224635-deleted-folder-bottom-of-nav.md
Summary: sidebar `AI Videos` section 内把 `_deleted/` directory 节点 sort 到列表底部；其它顶层目录（含 `_actors/`）保持 alphabetical。

Auto-updated:
- projects/ai_video_management/backend/libs/tree_walker.py — `_ai_videos_section` 分离 `_deleted` 节点 + 循环末尾 append（其余 sort 与 walk 逻辑不变）。
- specs/development/ai_video_management/user_input/revised_prompt.md — 顶部文件列表追加 040 + header bump，037/039 历史段下移为 Prior regen。
- specs/development/ai_video_management/final_specs/spec.md — FR-20 增加 follow-up 040 amendment 行说明 `_deleted` hoist 规则与仅限顶层 slot 的范围。

No conflicts found in: interview/qa.md, findings/*, validation/strategy.md, validation/acceptance_criteria.md, validation/backend_tests.md, validation/security.md, validation/bdd_scenarios.md, frontend/Sidebar.tsx（消费 backend 顺序，零改动）, frontend/* 其它组件, backend/libs/* 其它模块, backend/tests/*, README, Makefile。

## Follow-up 038 — 2026-05-13 22:23:41
Source: user_input/follow_ups/038-20260513-222341-bulk-hard-delete-deleted-folder.md
Summary: `ai_videos/_deleted/` 内 bulk hard-delete — 新 `POST /api/hard-delete-media` (第 18 个 endpoint，`Path.unlink()` 仅接受 `_deleted/` 前缀)；sidebar `_deleted/` 行加 "🧹 永久清理" 按钮 → 新 `/deleted` route 渲染 `DeletedView`（递归 tree walk + media tile grid + select mode 跨页多选 + PAGE_SIZE=50 分页 + typed-DELETE 模态确认 + per-file loop 删除 + tree refresh）。

Backend:
- `libs/media_archiver.py`:
  - 加 `class NotInDeleted(Exception)`。
  - 加 `MediaArchiver.hard_delete(rel) -> str`：`_validate_media_source` 复用 + 强校验 `parts[0]=="ai_videos" && parts[1]=="_deleted"`（否则 `NotInDeleted`）+ `src.unlink()`（`OSError` → `MoveFailed`）+ 返回相对 root 字符串。
  - 模块 docstring 顶部加 follow-up 038 段落。
- `libs/api.py`:
  - import 加 `NotInDeleted`。
  - 顶部 docstring：endpoint count 17 → 18 + endpoint 列表加 `POST /api/hard-delete-media`。
  - 新 endpoint `POST /api/hard-delete-media`（body `ArchiveMediaBody` 复用）：错误映射 `InvalidPath→400 invalid_path` / `NotMedia→400 extension_not_allowed` / `NotInDeleted→400 not_in_deleted` / `NotFound→404 not_found` / `MoveFailed→500 delete_failed`；成功 200 `{deleted: <rel>}`。405 handler 覆盖 GET/PUT/PATCH/DELETE。

Frontend:
- `src/api.ts`：加 `interface HardDeleteMediaResult { deleted: string }` + `hardDeleteMedia(path)` POST 到 `/api/hard-delete-media`。
- `src/App.tsx`：import `DeletedView`；新 route `/deleted` → `<DeletedView tree={tree} onChange={...}/>`。
- `src/components/Sidebar.tsx`：加 `isDeletedRoot` 派生 (`dramaPathParts[1] === "_deleted"`)；在该行渲染 "🧹 永久清理" 按钮（`className="drama-rename-btn"` 复用样式），点击 `e.stopPropagation()` + `navigate("/deleted")`。
- `src/components/DeletedView.tsx` (NEW)：
  - Props `{tree, onChange}`。
  - `collectDeletedMedia(tree)` 递归 walk + path-prefix filter + image/video 类型 + 按 path 升序。
  - State：`selectMode` / `selectedPaths: Set<string>` (跨页) / `page` / `modalOpen` / `typedConfirm` / `busy`。
  - Tile：image `<img>` / video `<video preload="metadata" muted playsInline>` via `mediaUrl(path)` + filename + 去前缀 subPath；select mode 加蓝边 + checkmark；非 select 点击 navigate `/file/{path}`。
  - Header 按钮：✅ 选择 / ✕ 退出选择 + （>50 时）分页 5 控件。
  - 底部 sticky bar (select mode)：已选 N / 总 M + 全选 + 全清 + 红色 "🗑 永久删除 (N)" 主按钮。
  - 确认模态：红 banner role=alert "此操作不可撤销 — ..." + 前 10 path 列 + 超额 "+ X 个其他文件…" + typed-DELETE input（严格 `=== "DELETE"`）+ disabled 主按钮 → enable 后 loop `hardDeleteMedia` per file + 累计 toast + `onChange()` refresh tree。
  - Empty state：`回收站为空 — 软删除的文件（来自 mp4 / 图片 Reader 的 🗑 Delete 按钮）会出现在此处`。
- `src/styles.css`：新增 `.deleted-view-page` / `.deleted-view-header` / `.deleted-view-header-actions` / `.deleted-view-empty` / `.deleted-view-grid` / `.deleted-tile` / `.deleted-tile-selected` (蓝边) / `.deleted-tile-thumb` (16:9 black bg cover) / `.deleted-tile-meta` / `.deleted-tile-name` / `.deleted-tile-path` / `.deleted-view-confirm-warning` (red banner) / `.deleted-view-confirm-list` (scroll 220px) / `.deleted-view-confirm-input` (monospace) / `.deleted-bulk-purge` (red primary)；复用现有 `.actor-grid-pagination` / `.actor-grid-page-indicator` / `.actor-grid-select-bar` / `.actor-grid-checkbox` / `.modal-backdrop` / `.modal-panel` / `.form-field` / `.modal-primary` 不重定义。

Spec / validation:
- `final_specs/spec.md` 新增 **FR-94** (五段)：endpoint 契约 + DeletedView grid 行为 + typed-DELETE 模态 + sidebar 入口 + 与 FR-9i (actor soft-delete 的 `_deleted/_actors/` sidecar `.md` 无法 hard-delete) 的 coverage 关系。
- `validation/acceptance_criteria.md` 新增 **U3.22** Gherkin：sidebar 按钮 → DeletedView grid → tile click 默认 navigate / select mode toggle → 跨页 selection → typed-DELETE 模态严格大小写 → per-file loop 含失败 continue → empty state → 后端 4 个错误码（`not_in_deleted` / `extension_not_allowed` / `not_found` / `invalid_path`）+ 405。
- `validation/acceptance_criteria.md` 覆盖矩阵补 `FR-94 → U3.22`。

User-input:
- `user_input/revised_prompt.md`：插入 "Prior follow-up 038" 段（不动用户为 039 写的 `Last regenerated` 头）。Composed-from 经用户重写为 "every follow_ups/*.md in numerical order" 形式，无需再列举。
- `user_input/follow_ups/038-20260513-222341-bulk-hard-delete-deleted-folder.md` (NEW)。

Auto-updated:
- `projects/ai_video_management/backend/libs/media_archiver.py` — `NotInDeleted` exception + `hard_delete()` method + docstring 段落。
- `projects/ai_video_management/backend/libs/api.py` — `NotInDeleted` import + endpoint count 17→18 + `POST /api/hard-delete-media` handler + 405 handler。
- `projects/ai_video_management/frontend/src/api.ts` — `HardDeleteMediaResult` 类型 + `hardDeleteMedia()` function。
- `projects/ai_video_management/frontend/src/App.tsx` — `DeletedView` import + `/deleted` route。
- `projects/ai_video_management/frontend/src/components/Sidebar.tsx` — `isDeletedRoot` 派生 + "🧹 永久清理" 按钮。
- `projects/ai_video_management/frontend/src/components/DeletedView.tsx` (NEW) — recycle bin 多选页面 + typed-DELETE 模态。
- `projects/ai_video_management/frontend/src/styles.css` — `.deleted-*` 一组 CSS 类。
- `specs/development/ai_video_management/final_specs/spec.md` — 新 FR-94 五段。
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — 新 U3.22 + 覆盖矩阵 FR-94 行。

No conflicts found in:
- follow-up 023 (`/api/delete-media` 软删除)：hard-delete 是其镜像 + 真删；soft-delete 流不动；`_deleted/` 内文件 reader 隐藏 archive / delete 按钮的规则保持有效（follow-up 023 决策）。
- follow-up 026 (`/api/actors/delete` cascade unassign)：actor folder 整体被 rename 进 `_deleted/_actors/actor_NNNN/`，其内 jpg 可被 hard-delete 但 `.md` 受 `MEDIA_EXTENSIONS` 限制无法 — v1 接受（FR-94 末尾段说明）。
- follow-up 030 (ActorGrid bulk delete + assign)：`DeletedView` 复刻 `selectMode` / `selectedPaths` / 跨页 / 分页 / sticky footer / per-file loop pattern；CSS class 部分复用（`.actor-grid-pagination` / `.actor-grid-checkbox` / `.actor-grid-select-bar`），主按钮换为红色 `.deleted-bulk-purge`。
- follow-up 036 (actor folder 折叠成单 leaf)：`_deleted/_actors/` 子树仍按递归 directory 渲染（folded 规则不适用），所以 hard-delete `_deleted/_actors/actor_NNNN/<>.jpg` 走的是普通 image leaf 路径，与 DeletedView walker 兼容。
- follow-up 037 (uvicorn `timeout_graceful_shutdown=2`)：hard-delete 是 single `unlink` syscall ~ms 级，不会延长 graceful shutdown 窗口；shutdown 行为不变。
- follow-up 039 (apps/+libs/ DDD+CQRS 布局)：FR-94 的内部实现位置在 039 执行后将从 `backend/libs/media_archiver.py` 迁移到 `apps/api/libs/infrastructure/...`（具体目标位置由 039 spec 决定），HTTP route `POST /api/hard-delete-media` shape 不变，DeletedView 组件路径从 `frontend/src/components/` → `apps/ui/src/components/`。039 应在迁移时保留 `hard_delete` method + `NotInDeleted` exception + `_deleted/` 前缀校验。

## Follow-up 039 — 2026-05-13 12:00:00
Source: user_input/follow_ups/039-20260513-120000-apps-libs-ddd-cqrs-layout.md
Summary: 项目采纳 `.claude/agent_refs/project/development.md` §1–6 的 `apps/+libs/` 解决方案布局：`backend/` → `apps/api/`，`frontend/` → `apps/ui/`，`backend/libs/*.py` 拆分到 `libs/{infrastructure,domain,application,common}/`，文件名/类名采用 `__` 后缀约定，加 `dependency_injector`。HTTP 路由 + JSON 形状不变，仅内部组织调整。

Auto-updated:
- specs/development/ai_video_management/user_input/revised_prompt.md — `Last regenerated` header bumped; "Composed from" 列表归并；layout 改述。
- specs/development/ai_video_management/final_specs/spec.md — header amendment block 加入，统一映射 `backend/`/`frontend/`/`backend/libs/`/`backend/static/` 到新路径。
- specs/development/ai_video_management/validation/strategy.md — header amendment 同款 remap + 新 blocker（跨层导入违反 §1 依赖方向）。

No conflicts found in: interview/qa.md, findings/{dossier,angle-*}.md, validation/{acceptance_criteria,bdd_scenarios,backend_tests,e2e,security,accessibility_and_manual}.md（被 strategy.md umbrella amendment 覆盖）, 历史 follow-ups 001–038 (immutable history; preserved).

## Follow-up 036 — 2026-05-13 22:23:53
Source: user_input/follow_ups/036-20260513-222353-actor-folder-collapsed-single-leaf.md
Summary: 把 `ai_videos/_actors/actor_NNNN/` 在 sidebar 树里折叠成单 leaf（`type: "actor"`），点击进入 ActorView；ActorView header 新增 🗑 delete 按钮复用 `POST /api/actors/delete` (FR-9i)。

Backend:
- `libs/tree_walker.py`:
  - 加 `_ACTOR_FOLDER_RE = re.compile(r"^actor_\d{4,}$")`
  - `_walk_filtered`：在递归进 directory 前，先调 `_collapsed_actor_leaf(entry)`，命中则发射单 leaf 跳过递归。
  - 新方法 `_collapsed_actor_leaf(entry)`：要求 (1) 名匹配 `_ACTOR_FOLDER_RE`，(2) 相对 root 恰好是 `ai_videos/_actors/<actor_id>` 三段（`_deleted/_actors/*` 因 `rel_parts[1] != "_actors"` 自动排除），(3) 内部存在 `<actor_id>.md` sidecar；满足时返回 `{type:"actor", name, path:<md>, face_path:<first jpg/png/webp>, children:[]}`，否则 None 走原递归路径。
  - 新方法 `_first_face_image(folder)`：扫 folder 内文件，返回首个匹配 `_IMAGE_EXTENSIONS` 的相对路径；None 表示 actor folder 尚未生成 face 图。
- 零 API 改动 — `POST /api/actors/delete` (FR-9i) 复用既有 endpoint。

Frontend:
- `src/types.ts`：`TreeNodeType` 新增 `"actor"`；`TreeNode` 加可选 `face_path?: string | null`。
- `src/lib/linkResolver.ts` `collectFilePaths`：遇到 `type==="actor"` 时把 `node.path`（md）+ `node.face_path`（jpg/png/webp，若有）都 push 到 `knownPaths`，确保 `ActorView.findFaceImage` 在折叠后仍能定位 face 图。
- `src/components/Sidebar.tsx`:
  - `isLeaf` 把 `"actor"` 纳入 leaf 集合。
  - 自动展开 effect 跳过 `"actor"` 节点（不再写入 `expanded` 字典）。
  - `isActorEntry` 改判 `item.node.type === "actor"` + path 4 段（含 md 文件名）+ 排除 `_deleted` 路径。
  - 行 icon：`type==="actor"` 渲染 🎭。
  - 点击 leaf 行调 `onSelect(path)` → 触发 Reader 加载 md → 命中 `isActor` → 渲染 ActorView。
- `src/components/ActorView.tsx`:
  - 新 import：`useNavigate` / `deleteActor` / `ApiError`。
  - Props 加可选 `onSaved?: () => void`。
  - 新 state：`deleting` / `deleteError`。
  - 新 `onDelete()` handler：`window.confirm` → `POST /api/actors/delete` (FR-9i) → 成功 `onSaved()` + `navigate("/")`；失败设 `deleteError`。
  - Header 改成 flex 容器，title 旁追加 "🗑 删除" 按钮；error 时下方 inline `role="alert"` 红色 banner。
- `src/components/Reader.tsx`：`<ActorView>` 调用新增传 `onSaved={onSaved}`。
- `src/styles.css`：`.actor-view-header` 改 flex；新增 `.actor-view-delete-btn` / `.actor-view-delete-btn:hover` / `:disabled` + `.actor-view-delete-error` 规则；色彩复用已有 token + 与 `.actor-delete-btn` (follow-up 026) 同 palette。

Spec / validation:
- `final_specs/spec.md` FR-87：actor sub-row 描述改为"单 leaf"（不再 directory），追加 click → ActorView 导航路径 + `_deleted/_actors/` 不适用规则。
- `final_specs/spec.md` FR-93 新增：完整契约（tree shape + frontend type + sidebar 行为 + ActorView delete 按钮 + 失败 alert）。
- `validation/acceptance_criteria.md` U3.21 新增：tree shape / leaf 渲染 / ActorView delete / 失败路径 / `_deleted/` 豁免 5 段 Gherkin。
- 覆盖矩阵加 `FR-93 → U3.21`。

User-input:
- `user_input/revised_prompt.md`：composed-from 加 036；header summary 重写为 036 内容；Last regenerated 2026-05-13 22:23:53。
- `user_input/follow_ups/036-20260513-222353-actor-folder-collapsed-single-leaf.md` (NEW)。

Auto-updated:
- `projects/ai_video_management/backend/libs/tree_walker.py` — `_ACTOR_FOLDER_RE` + `_walk_filtered` 加折叠分支 + `_collapsed_actor_leaf` + `_first_face_image` 两个新方法。
- `projects/ai_video_management/frontend/src/types.ts` — `TreeNodeType` 加 `"actor"` + `TreeNode.face_path?`。
- `projects/ai_video_management/frontend/src/lib/linkResolver.ts` — `collectFilePaths` 处理 `type==="actor"` 时把 path + face_path 都收进 knownPaths。
- `projects/ai_video_management/frontend/src/components/Sidebar.tsx` — `isLeaf` / 自动展开 / `isActorEntry` / 行 icon 4 处更新。
- `projects/ai_video_management/frontend/src/components/ActorView.tsx` — delete 按钮 + handler + state + Props.onSaved + import 新增。
- `projects/ai_video_management/frontend/src/components/Reader.tsx` — `<ActorView ... onSaved={onSaved}/>` 传参。
- `projects/ai_video_management/frontend/src/styles.css` — `.actor-view-header` flex + `.actor-view-delete-btn*` + `.actor-view-delete-error` 规则。
- `specs/development/ai_video_management/final_specs/spec.md` — FR-87 更新 + FR-93 新增。
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.21 新增 + 覆盖矩阵补 FR-93。

No conflicts found in:
- follow-up 034 (ActorView read view)：`isActor` dispatch / SiblingMedia skip 全部保留；036 仅在 header 加按钮 + 在 props 加 `onSaved`；face image 通过 `face_path` 字段经 `knownPaths` 流回 `findFaceImage()`，渲染路径完全等价。
- follow-up 026 (actor folder delete)：sidebar 行内 🗑 按钮逻辑不变；036 把检测条件从 `type==="directory"` 改为 `type==="actor"`，但 `actorId` 提取规则等价。
- follow-up 033 (filename convention)：jpg 文件名 `{eth}__{g}__{age}.jpg` 仍由 backend 直接探测并填到 `face_path`，扩展名匹配 `_IMAGE_EXTENSIONS`；legacy `actor_NNNN.jpg` 也命中（按 lexicographic first），向后兼容。
- follow-up 030 (grid bulk delete)：`/actors` route 与 sidebar leaf 各自独立；grid 仍按 `/api/actors` 列表渲染，与 tree shape 无关。
- backend tests：boot-smoke 不查 _actors/ 内部 — `/api/tree` 仍返回 200 + section shape；tree_walker 单元测试若存在需手验（test_tree_walker_consumer_walk.py）。

Verification:
- `curl /api/tree` 返回 `_actors/` children 全为 `{type:"actor", name:"actor_NNNN", path:"ai_videos/_actors/actor_NNNN/actor_NNNN.md", face_path:"ai_videos/_actors/actor_NNNN/<jpg>", children:[]}` ✓
- 不再出现 `actor_NNNN.md` / `*.jpg` 独立 file/image 节点 ✓
- `_deleted/_actors/` 路径仍按原递归 directory 渲染（未触发折叠分支）— 由 `rel_parts[1] != "_actors"` 保证 ✓
- `face_path` 实测样本 `actor_0013` → `ai_videos/_actors/actor_0013/asian__male__18-25.jpg` ✓

## Follow-up 037 — 2026-05-13 22:25:21
Source: user_input/follow_ups/037-20260513-222521-uvicorn-graceful-shutdown-timeout.md
Summary: dev `--reload` backend reload 卡死修复——`uvicorn.run(...)` 加 `timeout_graceful_shutdown=2`，根因是同步 def endpoint 在 graceful-shutdown 默认 wait-forever 中持续占线程。

Auto-updated:
- projects/ai_video_management/backend/main.py — 两条 `uvicorn.run(...)` 各加 `timeout_graceful_shutdown=2` kwarg。
- specs/development/ai_video_management/user_input/revised_prompt.md — 文件列表追加 037 + header bump + Prior 036 行收纳。
- specs/development/ai_video_management/final_specs/spec.md — FR-2 行更新 `uvicorn.run` 调用 shape 描述（含 reload 分支 + timeout_graceful_shutdown=2 + 根因 sync def long-tail 说明）。

No conflicts found in: interview/qa.md, findings/dossier.md, findings/angle-*.md, validation/strategy.md, validation/acceptance_criteria.md, validation/backend_tests.md, validation/security.md, validation/bdd_scenarios.md, frontend/*, libs/*（除 main.py）, README, Makefile, tests/*.

## Follow-up 035 amendment — 2026-05-13 11:30:00
Source: 同 follow-up 035；用户在初次实现后追加细化要求："I need a button I can manually click to do it, and after generation it should put generated pictures in a local folder, regeneration of images under the same scene will always overwrite, so the prefix of the image is not the mp4 file name but instead the scene folder name"。

变更:
- **Backend `libs/frame_extractor.py`**：
  - 新增 `FRAMES_SUBDIR = "frames"` 常量。
  - `FrameExtractor.extract()` 改写：输出目录从 `src.parent` → `src.parent / "frames"`（在抽帧前 `mkdir(parents=True, exist_ok=True)`，失败则 `ExtractFailed`）；文件名前缀从 `src.stem`（mp4 文件名）→ `src.parent.name`（场景文件夹名）。所以 `s1_长阶顶/s1_长阶顶3.mp4` 与 `s1_长阶顶/s1_长阶顶1.mp4` 都会输出到 `s1_长阶顶/frames/s1_长阶顶_f{N}_{role}.png` 同一组 5 文件 — 任一 mp4 take 重抽帧都覆盖同一组 PNG，user 不会被多 take 多份 PNG 噪声困扰。
  - Docstring 顶部新增 "Output convention" 段说明 `{src.parent}/frames/{src.parent.name}_f{N}_{role}.png` 路径模板。
- **Frontend `src/components/Reader.tsx`**（NEW — 直接打开 mp4 时也能抽帧）：
  - import 新增 `extractFrames` 到既有 archive/delete imports 行。
  - 新增 `const [extracting, setExtracting] = useState<boolean>(false)`。
  - 新增 `onExtractFramesClick` async callback（mirror `onArchiveToggle` 结构）。
  - `mediaActionsBusy` 三项联动 `archiving || deleting || extracting`。
  - 新增 `extractLabel` 计算（`"⏳ Extracting…"` / `"🎞 Extract Frames"`）。
  - mp4 view 的 `.reader-media-actions` 内在 Archive / Delete 按钮前插入 `.reader-media-extract-btn`，仅在非 archived 时显示（archived 视频不抽帧）。
- **Frontend `src/components/SiblingMedia.tsx`**：
  - 按钮 tooltip 更新为 `"...into ./frames/ — overwrites previous extraction from this scene folder"`。
  - announce toast 更新为 `"Extracted N frames from {basename} → frames/"`，明确告知 user 输出目录。
- **Frontend `src/styles.css`**：
  - `.reader-media-archive-btn` 选择器扩展 `.reader-media-archive-btn, .reader-media-extract-btn`（共享 inline-block / padding 6px 14px / border-radius 4px / 13px 字号样式）。
  - `.reader-media-actions` flex-row 不变；子按钮 margin-top 12px 同时 apply 给 extract-btn。

实测（HTTP TestClient via `/api/extract-frames`）:
- 输入：`ai_videos/mozun_chongsheng/scenes/s1_长阶顶/s1_长阶顶3.mp4`（15.07s real mp4）
- 输出：
  - `ai_videos/mozun_chongsheng/scenes/s1_长阶顶/frames/s1_长阶顶_f1_hero.png`
  - `ai_videos/mozun_chongsheng/scenes/s1_长阶顶/frames/s1_长阶顶_f2_reverse.png`
  - `ai_videos/mozun_chongsheng/scenes/s1_长阶顶/frames/s1_长阶顶_f3_vert.png`
  - `ai_videos/mozun_chongsheng/scenes/s1_长阶顶/frames/s1_长阶顶_f4_mid.png`
  - `ai_videos/mozun_chongsheng/scenes/s1_长阶顶/frames/s1_长阶顶_f5_detail.png`
- HTTP 200，0 failures，`frames/` 子目录在第一次调用时自动创建。
- 验证幂等覆盖：再次 POST 相同 path → 5 PNG 被 ffmpeg `-y` 覆盖（mtime 更新，filename 不变）。

清理：
- 删除 v1 残留的 `s1_长阶顶3_f{1..5}_*.png`（旧 per-mp4-stem 命名）— 实查时已不存在（疑是 user 手动清理或 hook 清理），无 cruft 残留。

不影响:
- `final_specs/spec.md` FR-9r 已记，本 amendment 仅刷新 FR-9r 描述的"输出路径"项（`{src.parent}/frames/`）+"命名前缀"项（`{src.parent.name}`）+"幂等覆盖"语义；不增删 FR。
- `validation/strategy.md` 与 8 个 level files：现有 levels 全部适用；security level 已纳入 imageio-ffmpeg supply chain。
- 其它端点 / 组件行为不变。
- mozun_chongsheng 9 个 scene .md / 9 个 scene .mp4 不动。

Severity: 低 blast radius — 仅修改 frame_extractor 输出路径与命名 + 新增 Reader.tsx mp4 直视图的按钮 + 共享样式。后端 API 契约不变（请求 body 与响应 schema 不变；仅 `frames[*].path` 值的 path 形状从 `{folder}/{stem}_fN_role.png` 变为 `{folder}/frames/{parent_name}_fN_role.png`，frontend 不做 path 解析，仅原样显示，不破坏既有调用方）。

## Follow-up 035 — 2026-05-13 11:00:00
Source: user_input/follow_ups/035-20260513-110000-scene-frame-extract-button.md
Summary: 用户："now I can generate a 15s scene video we disucssed about about the scene, now lets add a new button for the scene, when click, you take pictures from those scene, where the pictures will be used as a reference about the scene to generate shot videos"。新增 SiblingMedia 每个 .mp4 tile 的 "🎞 Extract Frames" 按钮 + 后端 `POST /api/extract-frames` 端点，使用 `imageio-ffmpeg` 抽取 5 个 canonical 参考帧（对齐 `agent_refs/project/ai_video.md` rule #12.10 v3 抽帧建议 t=0.5/4.4/7.9/11.4/14.6s），命名 `{stem}_f{N}_{role}.png` 落同 folder。

Backend:
- `libs/frame_extractor.py` 新建（150 行）— 镜像 `media_archiver.py` 风格：`FrameExtractor` class + `CANONICAL_FRAMES` 常量 `((0.5,'hero'),(4.4,'reverse'),(7.9,'vert'),(11.4,'mid'),(14.6,'detail'))` + `VIDEO_EXTENSIONS` frozenset (.mp4/.mov/.webm/.mkv/.avi/.m4v) + `_FFMPEG_TIMEOUT_S=30` + 异常类 `InvalidPath` / `NotFound` / `NotVideo` / `FfmpegMissing` / `ExtractFailed` + frozen dataclass `FrameResult` / `ExtractResult` 带 `to_payload()` + `_validate_video_source` 复用 `ExposedTree.is_inside` + `SafeResolver.resolve` + 拒 symlink。每帧用 `subprocess.run([ffmpeg, '-y', '-ss', str(t), '-i', src, '-frames:v', '1', '-q:v', '1', '-loglevel', 'error', out])` 30s timeout。Partial-failure 容忍（部分帧失败 200 + failures 字段；全失败 500）。
- `libs/api.py`：(a) docstring 端点计数 16→17；(b) 新增 `ExtractFramesBody(BaseModel) { path: str }`；(c) import `frame_extractor` 各 symbol（`ExtractFailed` / `FfmpegMissing` / `FrameExtractor` / `InvalidPath as FrameInvalidPath` / `NotFound as FrameNotFound` / `NotVideo`）；(d) `create_app` 内 `frame_extractor = FrameExtractor(exposed, resolver)`；(e) `@app.post("/api/extract-frames")` handler — 异常映射：`FrameInvalidPath`→400 invalid_path / `NotVideo`→400 not_a_video / `FrameNotFound`→404 not_found / `FfmpegMissing`→500 ffmpeg_missing / `ExtractFailed`→500 extract_failed；(f) 405 method-not-allowed 兜底。
- `requirements.txt`：新增 `imageio-ffmpeg>=0.5`。

Frontend:
- `src/api.ts`：新增 `ExtractedFrame { timestamp: number; role: string; path: string }` + `ExtractFramesResult { src: string; frames: ExtractedFrame[]; failures: {timestamp,role,error}[] }` + `extractFrames(path): Promise<ExtractFramesResult>` 函数。
- `src/components/SiblingMedia.tsx`：(a) import `extractFrames`；(b) `MediaTileProps` 增加 `extracting: boolean` + `onExtractFrames: (path) => void`；(c) tile 内引入 `<div className="sibling-media-actions">` 容器包裹两个按钮（垂直 stack）；(d) `🎞 Extract Frames` 按钮仅在 `isVideo && !archived` 显示，busy 时显示 `⏳ Extracting…`，aria-label 含完整说明，title 述 5 个 canonical 角色；(e) `SiblingMedia` 增加 `extractingPath: string | null` state + `handleExtractFrames(path)` async handler（aria-live announce: "Extracted N frames from {basename} (M failed)"，成功后 `onChange?.()` 触发 tree refresh，新 PNG 立即作为新 tiles 出现）；(f) 两处 `<MediaTile>` 实例（active + archived sections）传入新 props。
- `src/styles.css`：`.sibling-media-archive-btn` 选择器扩展 `.sibling-media-archive-btn, .sibling-media-extract-btn` 共享样式；新增 `.sibling-media-actions { display: flex; flex-direction: column; gap: 4px; align-items: stretch; margin-top: 6px; }` + 子按钮 `align-self: stretch; margin-top: 0; text-align: center;`。

实测:
- `s1_长阶顶3.mp4` (15.07s) 抽 5 帧成功：`s1_长阶顶3_f1_hero.png` ~1.31 MB / `f2_reverse.png` ~1.29 MB / `f3_vert.png` ~1.21 MB / `f4_mid.png` ~1.22 MB / `f5_detail.png` ~1.30 MB，5 个 MD5 全异（非 duplicate）。失败 0 项。
- TypeScript 类型检查通过（仅 pre-existing `vite.config.ts` node 类型告警，与本 follow-up 无关）。
- 后端 import smoke test 通过。

No conflicts found in:
- `final_specs/spec.md` — FR 列表新增 FR-9r 端点契约即可（spec walk 待 user 触发 stage-4 regen）
- `validation/strategy.md` 与 8 个 level files — 现有 levels 8 维度全部适用（FR-9r 自然纳入 functional level；imageio-ffmpeg 是新增依赖纳入 security level 的 supply chain 审计；非破坏性 frontend-only 改动）
- 现有 endpoints / lib 模块行为不变（archive/unarchive/delete/rename/casting/actor_pool）
- mozun_chongsheng 9 个 scene .md 文件 / 9 个 scene .mp4 文件 — 内容不动，本 follow-up 仅在 webapp 层增加抽帧功能
- `agent_refs/project/ai_video.md` rule #12.10 v3 — 不动，抽帧时间点和 role 命名严格对齐既有规则

User next steps:
1. 用更新后的 9 份 scene .md 第三段 `场景 reference video prompt` 在 Kling / Seedance 重新渲染 15s walk-through mp4，替换或新增 `scenes/s{N}_*/s{N}_*.mp4`。
2. 在 webapp Sidebar 打开 scene .md（例如 `s1_长阶顶.md`）→ 在底部 SiblingMedia 视图里看到 mp4 tile → 点击 "🎞 Extract Frames" → 5 张 PNG 立即出现在同视图中 → 单击 PNG 即可下载 / 在 shot prompt 中作为 reference image 上传给 Kling / Seedance。

Severity: 中等 blast radius — 新增 1 个端点 + 1 个 frontend 按钮 + 1 个 pip 依赖。所有现有 endpoints / 组件不动。

## Follow-up 033 — 2026-05-13 00:25:47
Source: user_input/follow_ups/033-20260513-002547-filename-convention-and-filters.md
Summary: 用户："lets introduce some convention for the actor file names, it should be always {民族}__{性别}__{年龄段}.jpg, and then in the main 演员池page, lets add filters, like filter by race, filter by gendor, filter by age etc. and make your best guess to update existing actors to follow this new rule"。三个相关改动：jpg 文件名约定 + grid filter UI + 自动 migration。

Backend:
- `libs/actor_pool.py`:
  - 新增 `_NEW_FILENAME_RE = re.compile(r"^[^/\\]+__[^/\\]+__[^/\\]+\.jpg$")` + helper `_attrs_to_filename(attrs)` 返回 `{ethnicity}__{gender}__{age_range}.jpg`
  - 新增 helper `_find_actor_jpg(folder)`：先找匹配 `_NEW_FILENAME_RE` 的 jpg，没有则 fallback 找 `{folder.name}.jpg` (legacy)
  - 修改 `generate_batch`：jpg 路径 `actor_folder / _attrs_to_filename(attrs)` 替代 `actor_folder / f"{actor_id}.jpg"`
  - 修改 `list_actors`：先校验 sidecar 存在，然后 `_find_actor_jpg(child)` 找 jpg；image_path 反映实际 filename
  - 修改 `actor_exists`：`_find_actor_jpg(folder) is not None`
  - 修改 `_reap_incomplete_folders`："有 jpg" 检查改为 `_find_actor_jpg`，partial migration 中间状态不被误判为 incomplete
  - 新方法 `migrate_filenames() -> dict[str, int]`：idempotent 扫 `_actors/`，per-folder try/except；已含 `_NEW_FILENAME_RE` jpg → skip；含 legacy `actor_NNNN.jpg` + sidecar → parse attrs → rename；目标已存在 → skip；返回 `{migrated, skipped, errors}`；跳过 `_deleted/_actors/`（构造期不动）
  - `ActorPool.__init__` 末尾自动调 `migrate_filenames()`（try/except 兜底，best-effort，不阻塞启动）
- 零 API 改动 — 全部 frontend / sidecar 兼容自动 fall through

Frontend:
- `src/components/ActorGrid.tsx`:
  - 加常量 `FILTER_ALL = "__all__"`
  - 新增 3 个 state: `filterEthnicity` / `filterGender` / `filterAgeRange`，default `FILTER_ALL`
  - 派生 `filteredActors`：先 filter，再分页
  - filter 变化时 `setPage(0)`
  - header `<h2>` 显示 `filtered / total`
  - 新增 `<div className="actor-grid-filters">` 三个 `<select>` (民族/性别/年龄段) + "全部" default option，复用 `ATTR_OPTIONS`
- `src/styles.css`：加 `.actor-grid-filters` (flex + gap + flex-wrap) + label/select 样式
- 零 api.ts 改动

Spec / validation:
- `final_specs/spec.md` FR-9f: 描述新文件名 `{ethnicity}__{gender}__{age_range}.jpg`；sidecar 保持 `actor_NNNN.md` 不变；migration 在 `__init__` 自动跑
- `final_specs/spec.md` FR-91: 加 filter UI 描述 + filter→page reset 0 + header 显示 `filtered/total`
- `validation/security.md` 无新 carve-out — migration 仅 rename 在 EXPOSED_TREE 内；filter 纯前端
- `validation/acceptance_criteria.md`: U3.15 加 jpg 文件名格式 + sidecar 不变 + auto-migrate 断言；U3.18 加 filter UI 断言

User-input:
- `user_input/revised_prompt.md`：composed-from 加 033；Last regenerated 改 2026-05-13 00:25:47；header summary 重写为 033 内容；Prior 032/031 更新

Auto-updated:
- `projects/ai_video_management/backend/libs/actor_pool.py` — `_NEW_FILENAME_RE` + `_attrs_to_filename` + `_find_actor_jpg` + generate path + `list_actors` + `actor_exists` + `_reap_incomplete_folders` + `migrate_filenames` + 构造期自动调用
- `projects/ai_video_management/frontend/src/components/ActorGrid.tsx` — 3 filter state + filteredActors + 3 dropdown UI + header count
- `projects/ai_video_management/frontend/src/styles.css` — `.actor-grid-filters` rules
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9f / FR-91 改写
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.15 / U3.18 加断言
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 033 summary
- `specs/development/ai_video_management/user_input/follow_ups/033-20260513-002547-filename-convention-and-filters.md` (NEW)

No conflicts found in:
- follow-up 032 (preview-then-confirm)：preview 计算的 prompt 不依赖 jpg filename，033 不动 preview 流程
- follow-up 031 (anti-wax prompt)：prompt 内容不变，仅文件名约定改
- follow-up 030 (grid bulk/assign)：filter 与 select mode 互相独立；filter + select 同时使用：在 filtered set 上 select / delete / assign
- follow-up 028 (ActorGrid)：filter 是新 surface，分页 / tile click 行为保留
- follow-up 026 (actor delete) + 014 (casting)：actor_id (folder 名) 仍稳定，casting.md 不需要重写
- backend tests：boot-smoke 7/7 仍 pass；migration 在空 `_actors/` 上 no-op

Verification:
- `_attrs_to_filename(attrs)` → `'asian__male__18-25.jpg'` ✓
- `generate_batch` 写入 `actor_0001/asian__male__18-25.jpg` 而非 `actor_0001.jpg` ✓
- `list_actors` 返回新文件名路径 ✓
- `migrate_filenames` legacy → 新格式 + idempotent re-run noop ✓
- `pytest tests/test_boot_smoke.py`: 7/7 ✓

## Follow-up 032 — 2026-05-13 00:19:36
Source: user_input/follow_ups/032-20260513-001936-grid-page-size-and-prompt-preview.md
Summary: 用户："每页的演员展示上限可以多一点， 比如50个，当batch gen以前，加一个步骤，然我review 以下你准备发给kling api的prompt的final 版本，我确定之后点另一个button 在执行"。两个小改: PAGE_SIZE 12→50；新 `POST /api/actors/preview-prompts` endpoint + `generate_batch` 接 `seeds: list[int]` 实现字节级一致 preview-then-confirm。

Backend:
- `libs/actor_pool.py` 新增 `preview_prompts(attrs, count, resolution)` 方法：校验 attrs/count/resolution → 计算 N 个 `{seed: base_seed+i, prompt: _build_prompt(attrs, _variance_for(seed, gender))}` 返回 `{prompts: [...], resolution}`；不写磁盘 / 不调 Kling / 不分配 actor folder
- `generate_batch` 签名加 `seeds: list[int] | None = None`：当提供时校验 `len == count` + 全 int（否则 `InvalidAttribute`）；主循环改为 `seed = seeds[i] if seeds is not None else base_seed + i`
- `libs/api.py`: `GenerateActorsBody.seeds: list[int] | None = None`；新 endpoint `POST /api/actors/preview-prompts` 复用同 body（seeds 字段被 preview 忽略）→ 调 `actor_pool.preview_prompts` → 200 + JSON；新 method-not-allowed handler → 405；`actors_generate` 把 `body.seeds` 传给 `generate_batch`
- docstring endpoint count 15 → 16；endpoint 列表加 `POST /api/actors/preview-prompts`

Frontend:
- `src/api.ts` 加 `PromptPreviewResult` interface + `previewPrompts(req)` POST `/api/actors/preview-prompts`；`GenerateActorsRequest.seeds?: number[]`
- `src/components/ActorPoolGenerator.tsx` 大改:
  - 新 state: `previewBusy` / `preview: PromptPreviewResult | null` / `previewError`
  - 主按钮 onClick 从 `onSubmit` 改为 `onPreview`：调 `previewPrompts` → 设 preview state → 自动打开内嵌 `PromptPreviewModal`
  - `onSubmit` 重写为 `onConfirmGenerate`：从 preview 取 seeds，构造 worker pool，每 worker 调 `generateActors({..., seeds: [previewSeeds[slot-1]]})`
  - 新内嵌组件 `PromptPreviewModal`: 显示 N 张 `<details>` 卡片，summary 显示前 180 字符 + 展开；footer "取消" / "✓ 确认发送 (N)"
  - 主按钮 label：`"预览 prompt"` / `"计算预览中…"` / `"生成中… (X/N)"`
  - Modal close 重置 preview state
- `src/components/ActorGrid.tsx`: `PAGE_SIZE = 12` → `PAGE_SIZE = 50`
- `src/styles.css`: 加 `.prompt-preview-panel` / `.prompt-preview-hint` / `.prompt-preview-list` / `.prompt-preview-card` / `.prompt-preview-meta` / `.prompt-preview-seed` / `.prompt-preview-toggle` / `.prompt-preview-body` 8 条 rules

Spec / validation:
- `final_specs/spec.md` 新增 **FR-9j** `POST /api/actors/preview-prompts` 完整契约 (body / response shape / 无副作用 / preview→confirm 流程)
- `final_specs/spec.md` FR-9f body 加 `seeds?: list[int]`；详述 seeds 校验
- `final_specs/spec.md` FR-88: 主按钮改为 "预览 prompt"；描述内嵌 PromptPreviewModal + 确认发送 流程
- `final_specs/spec.md` FR-91: PAGE_SIZE 12 → 50（两处）
- `validation/security.md` 无新 carve-out — preview 是 read-only dry-run（无 Kling 调用 / 无文件 IO）；seeds 来自用户但走 InvalidAttribute 校验，仅作为 `_variance_for` RNG seed（无路径 / shell injection 面）；JSON response ~75KB / 50 prompts × 1500 chars 仍合理范围
- `validation/acceptance_criteria.md` U3.15 加 preview→confirm seeds 字节级一致 + seeds 长度校验 + seeds 类型校验 + 405 + PAGE_SIZE=50 断言

User-input:
- `user_input/revised_prompt.md`：composed-from 加 032；Last regenerated 改 2026-05-13 00:19:36；header summary 重写为 032 内容；Prior 031/030/029 与 032 的 surface 关系更新

Auto-updated:
- `projects/ai_video_management/backend/libs/actor_pool.py` — `preview_prompts` + `generate_batch` seeds 参数
- `projects/ai_video_management/backend/libs/api.py` — `GenerateActorsBody.seeds` + 新 endpoint + method-not-allowed + docstring
- `projects/ai_video_management/frontend/src/api.ts` — `PromptPreviewResult` + `previewPrompts` + `GenerateActorsRequest.seeds`
- `projects/ai_video_management/frontend/src/components/ActorPoolGenerator.tsx` — preview 流程改写 + `PromptPreviewModal`
- `projects/ai_video_management/frontend/src/components/ActorGrid.tsx` — PAGE_SIZE 50
- `projects/ai_video_management/frontend/src/styles.css` — 8 条 preview-modal rules
- `specs/development/ai_video_management/final_specs/spec.md` — 新 FR-9j + FR-9f/FR-88/FR-91 改
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.15 加 preview 断言
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 032 summary
- `specs/development/ai_video_management/user_input/follow_ups/032-20260513-001936-grid-page-size-and-prompt-preview.md` (NEW)

No conflicts found in:
- follow-up 031 (anti-wax prompt)：032 preview 显示的就是 031 改写后的 prompt，含 anti-wax + camera cue —— preview 真实反映 Kling 收到的内容
- follow-up 030 (grid bulk/assign)：PAGE_SIZE 50 不影响 select 模式 / 跨页 selection / bulk delete / assign 流程
- follow-up 029 (variance + resolution + Pillow)：preview 调 `_variance_for` 与 `_build_prompt`，与 generate 同代码路径
- follow-up 027 (concurrency)：seeds 流让每个 worker 用确定的 seed，9 路并发不变
- follow-up 026 (actor delete)：032 不动 delete 路径
- backend tests：boot-smoke 7/7 仍 pass

Verification:
- `preview_prompts(attrs, 3, 'normal')` 返 3 个 {seed, prompt}，每 prompt ≥1000 字符 + 含 anti-wax keywords ✓
- `generate_batch(attrs, 3, 'normal', seeds=preview.seeds)` 写入 sidecar，prompt 与 preview 字节级一致 ✓
- `generate_batch` seeds 长度 mismatch → `InvalidAttribute` ✓
- `generate_batch` seeds 含非 int → `InvalidAttribute` ✓
- `pytest tests/test_boot_smoke.py`: 7/7 ✓
- 全套 `pytest tests/`: 18 pass / 5 pre-existing fail（零回归）

## Follow-up 031 — 2026-05-13 00:16:00
Source: user_input/follow_ups/031-20260513-001600-photorealism-no-wax-face.md
Summary: 用户："请确保kling生成的人像是真人，目前生成的太假了，一看就是AI生成的，有的甚至像是蜡像脸"。Backend-only prompt 改写修 Kling 输出的蜡像脸 / 过度光滑 / 完美对称问题。

Backend:
- `libs/actor_pool.py`:
  - 改写 `_build_prompt(attrs, variance="")`:
    - 移除 `"photorealistic"` + `"sharp focus"` + `"8k"` 三个 AI/CG-correlated token（这些 token 在训练数据中常关联 render/CG aesthetic，把 Kling 推向蜡像脸）
    - 开头从 `"portrait headshot of ..."` → `"candid unposed portrait photograph of ..."`（candid + photograph 暗示真实照片）
    - 末尾追加固定段: `"natural ambient lighting, neutral uncluttered background, natural skin texture with visible pores and subtle imperfections, slight natural facial asymmetry, RAW unedited photograph aesthetic, no plastic skin, no waxy smoothness, no symmetrical perfection, no CG render look"` — positive 描述 + "no X" 形式的 anti-token（Kling text-to-image 不支持 negative_prompt 字段，但 prompt 内含 "no X" 仍有缓解效果）
  - 新增第 **18 个 variance pool `_VARIANCE_PHOTOREALISM`** (12 items): 真实相机 / 镜头 / 胶卷感 — Canon EOS R5 85mm f/1.4, Sony A7 IV 50mm f/1.8, Fujifilm X-T5 classic-chrome, Hasselblad medium-format, Kodak Portra 400 grain, Cinestill 800T halation, Leica M11, iPhone 15 Pro candid, Nikon Z9 105mm f/1.4, Pentax 67 medium-format, 35mm point-and-shoot, Polaroid SX-70。每 fragment 60-90 字符
  - `_variance_for(seed, gender)` 末尾加 `rng.sample(_VARIANCE_PHOTOREALISM, k=2)` — batch 中每张抽 2 个不同 camera/film cue，使一批生成像多个摄影师拍的而非同一 AI 出
- 长度 length-guard 不变（仍 ≥1000 chars）；signature 兼容

Frontend:
- 零改动 — 用户感知通过 backend prompt 改写自动生效，UX surface 不变

Spec / validation:
- `final_specs/spec.md` FR-9f: "17 池" → "18 池"；加 anti-wax 永久注入描述 (移除 photorealistic/sharp focus/8k + 追加 RAW/natural skin/no waxy 等)
- `validation/security.md`: 无新 carve-out — variance pool 仍 server-side hardcoded，prompt 改写不引入新输入面
- `validation/acceptance_criteria.md` U3.15: 加三项断言 — (a) sidecar 不含 "photorealistic"/"sharp focus"/"8k" 单独 token；(b) sidecar 含 "candid"/"natural skin texture"/"no waxy smoothness"/"RAW unedited"；(c) sidecar 至少含一项 `_VARIANCE_PHOTOREALISM` camera cue

User-input:
- `user_input/revised_prompt.md`：composed-from 加 031；Last regenerated 改 2026-05-13 00:16:00；header summary 重写为 031 内容；新增 "Prior follow-up 030" 行；Prior 029 描述更新（031 在其 17 池基础上加 PHOTOREALISM 第 18 池）

Auto-updated:
- `projects/ai_video_management/backend/libs/actor_pool.py` — `_build_prompt` 重写 + 新 pool + `_variance_for` 增 sample
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9f 文案
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.15 加三断言
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 031 summary + Prior 030/029 行
- `specs/development/ai_video_management/user_input/follow_ups/031-20260513-001600-photorealism-no-wax-face.md` (NEW)

No conflicts found in:
- follow-up 030 (grid bulk delete + assign)：030 仅改 frontend，031 仅改 backend prompt，正交
- follow-up 029 (rich variance + resolution)：031 在其 17 池基础上加第 18 池；`_build_prompt` 签名不变；resolution / Pillow / length-guard / sidecar 不动
- follow-up 027 (concurrency)：generate_batch 主循环不动；只是每张的 prompt 文本变化
- 已存在的 actor_0001..0009 sidecar：不重新生成（retro-fit 不在范围）；新生成立刻有 anti-wax + camera cue
- backend tests：boot-smoke 7/7 仍 pass

Verification:
- `_build_prompt(attrs)` 输出不含 "photorealistic" / "sharp focus" / "8k"，含 "candid"/"natural skin texture"/"RAW unedited"/"no waxy" ✓
- `_variance_for(seed=1, 'male')` 输出含至少一个 `_VARIANCE_PHOTOREALISM` 元素（Canon/Sony/Fujifilm/etc. 关键词出现）✓
- variance 长度仍 ≥1000 ✓
- `pytest tests/test_boot_smoke.py`: 7/7 ✓
- 全套 `pytest tests/`: 18 pass / 5 pre-existing fail（零回归）

## Follow-up 030 — 2026-05-13 00:11:16
Source: user_input/follow_ups/030-20260513-001116-grid-bulk-delete-and-assign.md
Summary: 用户："在演员池页面，加入以下功能，第一个是bulk delelte，第二个功能是assign charactor, 给我drop down的选项，先选择哪个短剧，在选择短剧里的人物，然后确定后，此演员会标记参演这部短剧的这个角色。一个演员可以同时出演多部剧.you may need a more powerful data store to store this kind of relationship..."。Interactive 决策: 复用 per-drama `casting.md`（many-to-many 原生支持）+ 单一 window.confirm + 客户端 loop 批量删除。**零 backend 改动** — 全部 frontend feature 走现有 endpoints。

Frontend:
- `src/components/ActorGrid.tsx` 大幅扩展：
  - 新增 props `tree: TreeNode | null`, `onChange: () => void`
  - 新 state: `selectMode` / `selectedIds: Set<string>` (跨页保留) / `busyBulk` / `assignOpen`
  - 派生 `DramaChoice[]` from tree (`extractDramas`)：filter `ai_videos/` 直接子目录 non-`_*`，对每个 drama 找 `characters/c*/` 子目录名
  - Tile click: select mode → `toggleSelected(id)`；否则 → navigate (现有行为)
  - Header 加 "✅ 选择" / "✕ 退出选择" 切换按钮
  - Tiles 加 `actor-tile-selected` class + checkmark overlay
  - Sticky footer bar (selectMode 时显示)：`已选 N / 总 M` + 全选 / 全清 / 🗑 批量删除 / 🎬 分配角色 按钮
  - `onBulkDelete`：window.confirm 单次 → loop `deleteActor(id)` for each id → 累计 ok/fail/unassign 计数 → toast + tree reload + onChange
  - 新内嵌组件 `AssignCharacterModal`：drama `<select>` + character `<select>` (filter regex `^c\d+(_.*)?$`) + notes textarea + 确认按钮 → loop `castingAssign(drama.path, role, actor_id, notes)` for each selected id → toast + onChange
- `src/App.tsx`：`<Route path="/actors" element={<ActorGrid tree={tree} onChange={() => setRefreshKey(...)} />} />`
- `src/styles.css`：加 `.actor-grid-header-actions` / `.actor-tile-selected` (蓝边 + box-shadow) / `.actor-grid-checkbox` (overlay 左上角圆形 checkbox) / `.actor-grid-select-bar` (sticky bottom + box-shadow) / `.actor-grid-select-count` (monospace) / 按钮 hover/disabled + `.actor-grid-bulk-delete` 危险红 hover

Backend:
- 零改动。所有逻辑走现有：
  - `POST /api/actors/delete` (FR-9i / follow-up 026) — 自带 cascade unassign
  - `POST /api/casting/assign` (FR-9g / follow-up 014)
  - `GET /api/tree` (FR-10) — 提取 dramas + characters

Spec / validation:
- `final_specs/spec.md` FR-91 大幅扩展：select mode + 跨页 Set selection + sticky footer + bulk delete 单 window.confirm + loop + per-actor 错误隔离 + assign modal (drama dropdown 从 tree 派生 + character dropdown regex `^c\d+(_.*)?$` + loop castingAssign + per-drama casting.md 原生支持多剧) 全部说明
- `validation/security.md` 无新 carve-out — 全部复用已有 endpoint surfaces
- `validation/acceptance_criteria.md` U3.18：加 select mode 切换 / 跨页 selection 保留 / 批量删除 toast + cascade / assign 模态 drama+character dropdown + 多剧分配同 actor 不冲突 断言

User-input:
- `user_input/revised_prompt.md`：composed-from 加 030；Last regenerated 改 2026-05-13 00:11:16；header summary 重写为 030 内容；Prior 029 / 028 与 030 的 surface 关系标注

Auto-updated:
- `projects/ai_video_management/frontend/src/components/ActorGrid.tsx` — select mode + bulk delete + AssignCharacterModal + 派生 dramas
- `projects/ai_video_management/frontend/src/App.tsx` — `<ActorGrid tree onChange />` props
- `projects/ai_video_management/frontend/src/styles.css` — 8 条新 rules + sticky footer
- `specs/development/ai_video_management/final_specs/spec.md` — FR-91 扩展
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.18 扩展
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 030 summary
- `specs/development/ai_video_management/user_input/follow_ups/030-20260513-001116-grid-bulk-delete-and-assign.md` (NEW)

No conflicts found in:
- follow-up 029 (rich variance + resolution)：030 不动 generate 路径
- follow-up 028 (ActorGrid)：030 在其基础上扩展，分页 + 单 tile click → detail 默认行为不变
- follow-up 026 (actor delete)：030 通过 client-side loop 复用相同 endpoint
- follow-up 014 (CastingView)：030 写入相同 `casting.md` markdown 表；CastingView 读视图自动反映新写入
- `backend/libs/casting.py.Casting.unassign_actor_everywhere`：bulk delete 时每张都自动 cascade unassign
- backend tests：boot-smoke 7/7 仍 pass（零 backend 改动）

Verification:
- `pytest tests/test_boot_smoke.py`: 7/7 ✓
- 全套 `pytest tests/`: 18 pass / 5 pre-existing fail (与 029 同基线，零回归)
- Frontend tsc：新 ActorGrid 类型零错误（vite.config.ts 2 个 pre-existing path-typing 错误与本 follow-up 无关）

## Follow-up 029 — 2026-05-13 00:00:12
Source: user_input/follow_ups/029-20260513-000012-richer-variance-and-resolution-picker.md
Summary: 用户："当生成一个batch的时候，你需要加一些random的形容词到prompt里，... 你至少要加1000字以上的random形容词，然后在发给kling api。 然后生成的时候应该让我选在像素，default可以不用2k，4k 普通画质就可以"。Interactive 决策：resolution 选项 = 普通 / 2K / 4K，default 普通。

Backend:
- `libs/actor_pool.py` 加 17 个 variance pool tuples（gender-aware look archetype + gender-aware face features + jawline + cheekbones + brow + nose + lips + eyes + hair length/style/color + skin tone/texture + expression + mood + lighting + photography）；每池 8-14 项，每项 30-60 字符
- 重写 `_variance_for(seed, gender)`：每池 1-3 picks，~30-40 fragments 总和；末尾 `while len(result) < 1000:` 兜底循环；同 seed 完全可复现
- 加 `_RESOLUTION_PRESETS = {"normal": None, "2k": 2048, "4k": 4096}` + `DEFAULT_RESOLUTION = "normal"` + `RESOLUTION_OPTIONS = frozenset(...)`；常量 `JPEG_QUALITY = 95`
- `generate_batch(attrs, count, resolution="normal")` 签名扩展；校验 `resolution in RESOLUTION_OPTIONS` 否则 raise `InvalidAttribute`；Kling 返回 bytes 后若 `target_px is not None` 调 `_resize_jpeg(bytes, target_px)`；失败归入 `errors[]: resize_failed`，batch 继续
- 新静态方法 `_resize_jpeg(jpeg_bytes, target_px)`：Pillow `Image.open(BytesIO)` → `.convert("RGB")` → `.resize((target_px, target_px), Image.LANCZOS)` → `save(buf, "JPEG", quality=95)`
- `_build_sidecar(actor_id, attrs, prompt, seed, resolution="normal")` 加 resolution 字段到属性表
- `result.generated[i]` 携带 `"resolution"` 字段
- `__all__` 加 `DEFAULT_RESOLUTION` + `RESOLUTION_OPTIONS`
- imports 加 `random` (follow-up 027 已加) + `io.BytesIO` + `from PIL import Image`
- `libs/api.py`：`GenerateActorsBody.resolution: str = "normal"`；`actors_generate` 把 `body.resolution` 传给 `generate_batch`
- `backend/requirements.txt` 加 `pillow>=10.0`

Frontend:
- `src/api.ts`：`GenerateActorsRequest.resolution?: string`；`ATTR_OPTIONS.resolution = ["normal", "2k", "4k"] as const`
- `src/components/ActorPoolGenerator.tsx`：`useState<string>("normal")` for resolution；onSubmit pass through；useCallback dep 加 resolution；form-grid 加第 7 个 dropdown "画质"，option label "普通 (~1024px, Kling 原始)" / "2K" / "4K"

Spec / validation:
- `final_specs/spec.md` FR-9f 重写：body 加 `resolution`；详述 17 池 + ≥1000 字符 length-guard + Pillow Lanczos resize + `resize_failed` 错误类
- `final_specs/spec.md` FR-86：加 `resolution` enum 行
- `final_specs/spec.md` FR-88：六 → 七 dropdown，注明 resolution UX
- `validation/security.md` carve-out #7：加 (d) Pillow image-decode + resize hardening（仅信任 Kling JPEG / 已 SSRF-vetted / 5MB cap 前置 / 失败兜底）+ (e) resolution enum closed schema；Pillow 新 dep 跟踪上游 advisories
- `validation/acceptance_criteria.md` U3.15：标题加 "+ 029 rich variance + resolution"；新增 ≥1000 字符断言 + resolution=2k → 2048×2048 / 4k → 4096×4096 / normal → Kling 原始 / 8k → 400 invalid_attribute 四个分支

User-input:
- `user_input/revised_prompt.md`：composed-from 加 029；Last regenerated 改 2026-05-13 00:00:12；header summary 重写为 029 内容；Prior 028 / 027 描述与 029 的 surface 关系

Auto-updated:
- `projects/ai_video_management/backend/libs/actor_pool.py` — 17 池 + `_variance_for` 重写 + `_RESOLUTION_PRESETS` + `_resize_jpeg` + `generate_batch` 签名 + `_build_sidecar` resolution 字段 + `__all__`
- `projects/ai_video_management/backend/libs/api.py` — `GenerateActorsBody.resolution` + 传参
- `projects/ai_video_management/backend/requirements.txt` — `pillow>=10.0`
- `projects/ai_video_management/frontend/src/api.ts` — `GenerateActorsRequest.resolution` + `ATTR_OPTIONS.resolution`
- `projects/ai_video_management/frontend/src/components/ActorPoolGenerator.tsx` — 第 7 dropdown + state + dep
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9f 重写 + FR-86 / FR-88 扩展
- `specs/development/ai_video_management/validation/security.md` — carve-out #7 加 (d) / (e)
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.15 扩
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 029 summary
- `specs/development/ai_video_management/user_input/follow_ups/029-20260513-000012-richer-variance-and-resolution-picker.md` (NEW)

No conflicts found in:
- follow-up 028 (ActorGrid)：029 不动 grid 路径；grid 仍用 `/api/actors` + lazy thumbnail，2K/4K 选项不影响 grid 行为
- follow-up 027 (concurrency + race-safe)：029 在 `_variance_for` 函数体扩展 pools，不动外层并发 / 分配 / cap
- follow-up 026 (actor delete)：029 不重叠 delete 路径
- follow-up 025 (Kling-only)：KlingProvider / JWT / SSRF-vet / cap 完全不动；resolution upscale 仅作用于 provider 返回的 bytes
- 已生成的 `_actors/actor_0001..0009` 老 sidecar：不重写（历史 artifact 保留；未来 regen 才有 `resolution` 字段 + 长 variance prompt）
- backend tests：boot-smoke 7/7 仍 pass

Verification (inline smoke):
- `_variance_for(seed=1, gender='male')` 输出长度 ≥ 1000；`_variance_for(seed=1, gender='male')` 二次调用 byte-equal（可复现）✓
- `_variance_for(seed=1, gender='male')` ≠ `_variance_for(seed=2, gender='male')` (不同 seed 不同 variance) ✓
- `_resize_jpeg(test_1024_jpeg, 2048)` 输出 Pillow 解码 size = (2048, 2048) ✓
- `_resize_jpeg(test_1024_jpeg, 4096)` 输出 size = (4096, 4096) ✓
- `generate_batch(attrs, count=1, resolution="invalid")` raise InvalidAttribute ✓
- `pytest tests/test_boot_smoke.py`: 7/7 ✓
- 全套 `pytest tests/`: 18 pass / 5 pre-existing fail (与 028 同基线，零回归)

## Follow-up 028 — 2026-05-12 23:43:09
Source: user_input/follow_ups/028-20260512-234309-actor-grid-view.md
Summary: 用户："current view of actors is only one at a time, need to first give me a grid like view to compare all pictures you could do paging if cannot fit all into one page, but one at a time is not efficient"。**新 `ActorGrid` 视图**: 一屏多图对比的演员池 grid，替代单张点击 workflow。**零 backend 改动** — 全部走 follow-up 014 已存的 `GET /api/actors` + follow-up 005 的 `GET /api/media`。

Frontend:
- `src/components/ActorGrid.tsx` (NEW)：React 组件，mount 时 `listActors()` → 内部 state；`PAGE_SIZE = 12`；响应式 CSS grid `repeat(auto-fill, minmax(180px, 1fr))`；每 tile 是 `<button>` 含 `<img loading="lazy">` + `actor_NNNN` + 4 个属性 chip (ethnicity / gender / age_range / look)；click 触发 `navigate('/file/' + encodeURIComponent(image_path))`；pagination 控件 (首页 / 上一页 / `第 N / M 页` / 下一页 / 末页) 仅 `actors.length > 12` 时渲染；empty / loading / error 三态 (error banner + reloadKey state-bump 重试)；`aria-live="polite"` 在页码指示
- `src/App.tsx`：import `ActorGrid`；加 `<Route path="/actors" element={<ActorGrid />} />`
- `src/components/Sidebar.tsx`：import `useNavigate` from `react-router-dom`；构造期拿 `navigate`；在 `isActorsRoot` 现有 🎭 生成演员 按钮后加 🔲 网格 按钮 sibling，onClick 跳 `/actors`
- `src/styles.css`：新增 14 条 `.actor-grid-page` / `.actor-grid-header` / `.actor-grid-pagination` / `.actor-grid-page-indicator` / `.actor-grid` / `.actor-tile` (hover + focus-visible) / `.actor-tile-image` / `.actor-tile-meta` / `.actor-tile-id` / `.actor-tile-chips` / `.actor-tile-chip` / `.actor-grid-empty` rules

Backend:
- 零改动（`GET /api/actors` from follow-up 014 已满足全部数据需求）

Spec / validation:
- `final_specs/spec.md` 新增 **FR-91** ActorGrid 完整契约 (route / fetch / tile / pagination / empty/loading/error 三态)
- `final_specs/spec.md` 扩 **FR-87** 提及网格按钮 + 路由 + 入口位置
- `validation/acceptance_criteria.md` 新增 **U3.18** scenario：空池 empty state / 5 actors 无分页 / 13 actors 跨页 2 / 25 actors 3 页 / tile click → `/file/{path}` / error retry
- `validation/acceptance_criteria.md` 覆盖矩阵加 `FR-91 | U3.18 (ActorGrid 分页，follow-up 028)`
- `validation/security.md` 无新 carve-out — grid 是纯 GET 读取面 (`/api/actors`)，follow-up 014 carve-out 已涵盖；本 follow-up 不引入新写入面或新出站 HTTP

User-input:
- `user_input/revised_prompt.md`：composed-from 加 028；Last regenerated 改 2026-05-12 23:43:09；header summary 重写为 028 内容；Prior 027 / 026 跟 028 的 surface 关系标注

Auto-updated:
- `projects/ai_video_management/frontend/src/components/ActorGrid.tsx` (NEW) — paginated grid
- `projects/ai_video_management/frontend/src/App.tsx` — 加 `/actors` route + import
- `projects/ai_video_management/frontend/src/components/Sidebar.tsx` — 加 🔲 按钮 + `useNavigate`
- `projects/ai_video_management/frontend/src/styles.css` — 14 条新 CSS rules
- `specs/development/ai_video_management/final_specs/spec.md` — FR-91 新增 + FR-87 扩展
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.18 scenario + matrix
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 028 summary
- `specs/development/ai_video_management/user_input/follow_ups/028-20260512-234309-actor-grid-view.md` (NEW)

No conflicts found in:
- follow-up 027 (concurrency + variance)：028 不动 generate 路径或 actor_pool，完全正交
- follow-up 026 (actor delete)：028 不重叠 delete 按钮，sidebar 🗑 仍是删除入口；grid 是 read-only
- follow-up 025 (Kling-only)：028 不动 provider
- follow-up 014 (CastingView)：CastingView 的 assign-mode grid 是 drama-scoped + filtered；ActorGrid 是 pool-level + 无 filter，surface 独立
- follow-up 022 (sidebar collapse-all)：028 加按钮但不动 collapse 逻辑
- `_actors/_deleted/` (follow-up 026)：grid 不显示已删除 actor（`GET /api/actors` 只 list `_actors/` 不含 `_deleted/`），一致行为

Verification:
- `pytest tests/test_boot_smoke.py`: **7/7 通过** ✓ (零 backend 改动)
- 全套 `pytest tests/`: 18 pass / 5 pre-existing fail (与 follow-up 027 完成时同样基线，零回归)
- TypeScript 编译：新 `ActorGrid.tsx` 导入 / 类型零错误（vite.config.ts 的 2 个 pre-existing path-typing 错误与本 follow-up 无关）
- 手工验证：route `/actors` 渲染、tile click 跳 `/file/...`、pagination 按钮 disabled/enabled 切换正确

## Follow-up 027 — 2026-05-12 23:26:56
Source: user_input/follow_ups/027-20260512-232656-concurrency-and-variance.md
Summary: 用户："current generation of actor picture is too slow, kling api allow 9 concurrent request, please remove any limitation on your side and leverage the 9 concurrency on kling api, also, when I let you do batch generation, you should introduce a lot of variance to the text on top of the basic info, ..."。**两个独立修复**: (1) **9-way 并发** — frontend `ActorPoolGenerator` 从串行 await 改用 9-worker pool (`CONCURRENCY=9` 对齐 Kling API)；20 张 batch 从 ~50s 降到 ~6-9s。Backend FastAPI sync endpoint 已经跑在 threadpool，9 个并发请求自然分配 9 个工作线程。(2) **Per-image variance** — `_variance_for(seed, gender)` 从 5 个 server-side 英文 tuple pool (gender-specific face features / skin tones / face shapes / eye descriptors / hair descriptors) 按 seed 抽 fragment 注入 prompt，避免同 base prompt 产生 near-duplicates。**Race-safe ID 分配**：之前的 "pre-compute `next_id + offset`" 在 9 并发下同 id 冲突；改用 `_allocate_actor_id` 循环 `mkdir(exist_ok=False)` 原子分配；`_reap_incomplete_folders` 独立提取，仅 batch 开始调一次（之前混在 `_next_actor_id_num` 内会跟 concurrent allocators 互相 reap）。**`MAX_BATCH_COUNT` 20→50**。

Backend:
- `libs/actor_pool.py`: import 加 `random`；新增 `_MAX_ID_ALLOC_SCAN = 1000` 常量
- 加 5 个 variance pool tuples (`_VARIANCE_FACE_FEATURES_MALE/FEMALE`, `_VARIANCE_SKIN_TONES`, `_VARIANCE_FACE_SHAPES`, `_VARIANCE_EYE_DESCRIPTORS`, `_VARIANCE_HAIR_DESCRIPTORS`)，每池 6-8 项 English fragments
- 新 module-level fn `_variance_for(seed, gender) -> str`：`random.Random(seed)` 每池 `choice` 一项 join 成单字串；同 seed 同 gender 完全可复现
- `ActorPool._build_prompt(attrs, variance: str = "") -> str`：在 base parts 中 `attrs.look` 之后 / `style` 之前插入 variance（不传时行为不变，向后兼容）
- 新方法 `ActorPool._allocate_actor_id(actors_dir) -> tuple[str, Path]`: `mkdir(exist_ok=False)` 循环往上找 free slot；OSError → `GenerationDirMissing`；1000 attempts 越界也 `GenerationDirMissing`
- `_reap_incomplete_folders(actors_dir)` 提取为独立 staticmethod（之前嵌在 `_next_actor_id_num` 里跟并发 race）；`_next_actor_id_num` 现在纯扫描无副作用
- `generate_batch` 主循环重写：开头 `_reap_incomplete_folders` 一次；每张图片 `_allocate_actor_id` 原子分配 → `_variance_for(seed, gender)` → `_build_prompt(attrs, variance=...)` → provider call → sidecar 用 varianced prompt
- `MAX_BATCH_COUNT = 50`

Frontend:
- `src/components/ActorPoolGenerator.tsx`:
  - 加常量 `CONCURRENCY = 9` + `MAX_BATCH_COUNT = 50`
  - `Progress.current: number` → `Progress.inFlight: number`
  - `onSubmit` 主循环重写为 worker pool：`claimSlot` 抽 slot；9 个 worker `await Promise.all([])` 并发；每 worker 循环到 slot 用完；`inFlight` 计数随 in-flight workers 起落；`cancelledRef` 检查放在 `claimSlot` 内 — 取消时新 slot 拿不到，已 in-flight 的 worker 完成后正常 tally
  - count 输入 `max={20}` → `max={MAX_BATCH_COUNT}`；clamp 同步
  - Button busy 文字 `生成中… (current / total)` → `生成中… (done+failed / total)` (current 已被 inFlight 替换，进度按"已完成数"展示更直观)
  - `ProgressPanel`：增 `⚡ 并发 N` chip 显示当前 in-flight workers
- `src/styles.css`：加 `.progress-inflight { color: #1e40af; font-weight: 600; }`

Spec / validation:
- `final_specs/spec.md` FR-9f 重写：详述 race-safe `_allocate_actor_id` (mkdir-exist_ok-False atomic) + variance pool 注入流程 + 9 并发 backend threadpool 路径；count cap 20→50
- `final_specs/spec.md` FR-88: 模态 count input 上限 20→50；描述 9-worker pool + `⚡ 并发 N` chip
- `validation/security.md` carve-out #7：增 3 项硬化 — (a) race-safe ID allocation 关闭 9 并发下的 ID 冲突 race；(b) variance pools server-side hardcoded，无新 prompt-injection 面；(c) count cap 50 仍 bound 总 outbound HTTP wave
- `validation/acceptance_criteria.md` U3.15：标题加 "+ 027 concurrency + variance"；新增断言 (sidecar prompt 互不相同 / 至少含一个 variance fragment / count cap 改 21→51 / 9 并发 distinct ids)

User-input:
- `user_input/revised_prompt.md`：composed-from 加 027；Last regenerated 改 2026-05-12 23:26:56；header summary 重写为 027 内容；Prior 026 与 Prior 025 重写描述跟 027 的 surface 关系

Auto-updated:
- `projects/ai_video_management/backend/libs/actor_pool.py` — variance pools + `_variance_for` + `_allocate_actor_id` + `_reap_incomplete_folders` + 重写 `generate_batch` + cap 50
- `projects/ai_video_management/frontend/src/components/ActorPoolGenerator.tsx` — worker pool + cap 50 + progress shape (current→inFlight) + 并发 chip
- `projects/ai_video_management/frontend/src/styles.css` — `.progress-inflight` rule
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9f 重写 + FR-88 改写
- `specs/development/ai_video_management/validation/security.md` — carve-out #7 第一段增 3 项硬化
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.15 扩
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 027 summary
- `specs/development/ai_video_management/user_input/follow_ups/027-20260512-232656-concurrency-and-variance.md` (NEW)

No conflicts found in:
- follow-up 026 (actor folder delete)：027 改 generate 路径，026 改 delete 路径，正交
- follow-up 025 (Kling-only)：027 仍用同一 KlingProvider，只是前端并发数 + variance + race-safe 分配；KlingProvider 的 JWT / SSRF-vet / 30s timeout / 5MB cap 全部不动
- follow-up 023 (mp4 delete)：完全独立 surface
- follow-up 018 (pollinations retry)：retry 代码 follow-up 025 已删；027 不依赖 retry
- `backend/libs/api.py` / `backend/libs/casting.py`: `ActorPool(exposed, resolver)` 构造签名不变；`generate_batch(attrs, count)` 公开签名不变
- `backend/tests/` 全部测试：boot-smoke 7/7 仍 pass；其他测试不依赖 actor_pool generate 路径
- 已生成的 `_actors/actor_0001..0009/actor_NNNN.md` 老 sidecar 中无 variance fragment 字样：那是 follow-up 027 之前生成的，retroactive 不重写；用户用新按钮重新生成才会有 variance

Verification (inline smoke):
- `_variance_for(seed=1, gender='male')` 与 `_variance_for(seed=2, gender='male')` 输出不同；同 seed 多次调用输出相同 ✓
- `_build_prompt(attrs, variance=v)` 含 v；`_build_prompt(attrs)` 不含 ✓
- 9 个线程并发调 `_allocate_actor_id(空 _actors/)` → 9 个 distinct actor_0001..0009 ✓
- `_reap_incomplete_folders` 仍正确回收 jpg-less folders；保留有 jpg 的 folder ✓
- `pytest tests/test_boot_smoke.py`: **7/7 通过** ✓
- 全套 `pytest tests/`: 18 pass / 5 pre-existing fail (与 follow-up 026 完成时同样 5 个 wukong_juexing-fixture failures，零回归)

## Follow-up 026 — 2026-05-12 23:10:14
Source: user_input/follow_ups/026-20260512-231014-actor-folder-delete.md
Summary: 用户："lets add a delete button at actor folder level, after delete, it will be moved to _delete folder similar to the mp4 delete feature"。**Sidebar 每个 `ai_videos/_actors/actor_NNNN/` 行加 🗑 软删除按钮**：移动整个 actor folder 到 `ai_videos/_deleted/_actors/actor_NNNN/`（镜像 follow-up 023 的 `_deleted/` 子路径 pattern，但作用于 folder 而非单文件）。Interactive 决策："Auto-unassign then delete" → cascade-unassign 模式：endpoint 先 sweep 所有 drama 的 `casting.md` 移除引用该 actor_id 的行，再原子 rename folder。响应携带 `unassigned: [{drama, role}]` 列表供 UI 报告。

Backend:
- `libs/actor_pool.py` 加 4 个 exceptions: `ActorNotFound` / `ActorAlreadyDeleted` / `ActorDeleteTargetExists` / `ActorDeleteFailed`；加方法 `ActorPool.delete_actor(actor_id: str) -> dict[str, str]`：校验 `_ACTOR_ID_RE` → `is_dir()` + `is_symlink()` reject → target = `resolver.root / "ai_videos" / "_deleted" / "_actors" / actor_id` → target.exists 拒 → mkdir parents → atomic `src.rename(target)` → 返回 `{from, to}`；`__all__` 扩展含 4 个新 exceptions
- `libs/casting.py` 加方法 `Casting.unassign_actor_everywhere(actor_id: str) -> list[dict[str, str]]`：walk `ai_videos/` 直接 children（跳 `_`-prefix system folders 与 non-dir / symlink），对每个 drama 的 `casting.md` parse → 过滤 actor_id 匹配的行 → 若有移除则 `_write()` 重写文件（复用 `assign()` 的 atomic temp+os.replace 路径）→ 累计 `{drama, role}` 返回；不动 unchanged casting.md 减少 mtime churn
- `libs/api.py` import 加 4 个新 actor_pool exceptions；新 Pydantic `DeleteActorBody { actor_id: str }`；新 endpoint `POST /api/actors/delete`：cascade 先 (OSError → 500 `cascade_failed`)，folder move 后；exception 映射 `InvalidAttribute` → 400 `invalid_actor_id`、`ActorNotFound` → 404 `actor_not_found`、`ActorDeleteTargetExists` → 409 `target_exists`、`ActorDeleteFailed` → 500 `move_failed`；method-not-allowed handler `GET/PUT/PATCH/DELETE` → 405；docstring endpoint count 14 → 15

Frontend:
- `src/api.ts` 加 `interface DeleteActorResult { from, to, unassigned: { drama, role }[] }` + `export async function deleteActor(actorId)` POST `/api/actors/delete`
- `src/components/Sidebar.tsx` 加 `ACTOR_ID_RE = /^actor_\d{4,}$/` 常量；`deletingActorId` state；`onActorDeleteClick` useCallback (window.confirm → deleteActor → 复用 `renameToast` surface 上 "已删除 actor_NNNN（解除 N 个 casting 引用）")；render loop 派生 `isActorEntry` flag (path parts.length===3 且 parts[0]==="ai_videos" 且 parts[1]==="_actors" 且 parts[2] 匹配 ACTOR_ID_RE) + 在该行 render 🗑 按钮（与 `_actors/` 的 🎭 生成演员 sibling pattern）；按钮 in-flight label "删除中…"
- `src/styles.css` 加 `.actor-delete-btn` rule（与 `.drama-rename-btn` 同基线尺寸；hover 时 border-color → `var(--error-border, #c53030)`；disabled opacity 0.55）

Spec / validation:
- `final_specs/spec.md` 新增 **FR-9i** `POST /api/actors/delete` 完整契约：body shape / cascade-first 顺序 / 状态码 / 符号链接 reject / `_next_actor_id_num` 不扫 `_deleted/` 故 ID 可复用 / EXPOSED_TREE 不变；扩 **FR-87** 加 row-level 🗑 按钮描述（hides under `_deleted/`）
- `validation/security.md` carve-out 加 **#7-bis**：4 项硬化 (actor_id shape strict、source/target 完全 derived 无 user-path、symlinks reject、atomic rename) + 3 项 residual risk (GUARDED_ROUTES gap 与 carve-out #7 同步、ID 复用是 intentional v1、cascade multi-file 非原子 race window) + coverage matrix 加 FR-9i 行 → `SEC-ACTORS-DELETE`
- `validation/acceptance_criteria.md` 加 **U3.17** scenario：fixture 2 个 actor + 2 个 drama casting.md → POST /api/actors/delete → 验证 unassigned 列表 + folder 移动 + casting.md 重写 + 重复删除返 404 + shape 400 + 不存在 actor 404 + ID slot 复用 + 405；coverage 矩阵加 `FR-9i | U3.17 (actors/delete，follow-up 026)`

User-input:
- `user_input/revised_prompt.md`：composed-from 加 026；Last regenerated 改 2026-05-12 23:10:14；header summary 重写为 026 范围；prior follow-up 025 标记为 "保持有效；026 在其上加新写入面 `POST /api/actors/delete`"

Auto-updated:
- `projects/ai_video_management/backend/libs/actor_pool.py` — 4 个新 exceptions + `delete_actor()` 方法 + `__all__` 扩展
- `projects/ai_video_management/backend/libs/casting.py` — `unassign_actor_everywhere()` 方法
- `projects/ai_video_management/backend/libs/api.py` — import 扩展 + `DeleteActorBody` + `POST /api/actors/delete` 实现 + method-not-allowed handler + docstring endpoint count 15
- `projects/ai_video_management/frontend/src/api.ts` — `DeleteActorResult` + `deleteActor()`
- `projects/ai_video_management/frontend/src/components/Sidebar.tsx` — 🗑 button + state + callback + 派生 flag
- `projects/ai_video_management/frontend/src/styles.css` — `.actor-delete-btn` rule
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9i 新增 + FR-87 扩展
- `specs/development/ai_video_management/validation/security.md` — carve-out #7-bis + coverage matrix FR-9i 行
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.17 scenario + coverage matrix FR-9i 行
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 026 summary
- `specs/development/ai_video_management/user_input/follow_ups/026-20260512-231014-actor-folder-delete.md` (NEW)

No conflicts found in:
- follow-up 023（mp4 delete）: 026 在 sub-path mirroring + soft-delete 语义上对齐；不抢同一文件路径（mp4 = file，026 = folder）
- follow-up 025（Kling-only provider）: 026 不动 actor_pool 的 Kling 调用面；新 `delete_actor` 与 Kling provider 独立
- follow-up 014（casting workflow）: 026 通过 cascade 主动保持 casting.md 一致；不破坏 FR-9g / FR-9h
- follow-up 022（sidebar collapse-all）: 026 加新按钮但不动 expand state 逻辑
- 已生成的 `_actors/actor_0001..0009/` 文件夹: 用户使用新按钮后会软删除，原 sidecar 内容（提到 "pollinations.ai" 的历史 artifact）随 folder 移到 `_deleted/_actors/`，不会被修改
- backend tests: 现有 7 boot-smoke 测试不依赖 actor_pool 写入面，未受影响

Verification (inline smoke):
- `python -c "from libs.actor_pool import ActorNotFound, ActorDeleteFailed, ActorDeleteTargetExists, ActorAlreadyDeleted; from libs.casting import Casting; from libs import api; print(hasattr(Casting,'unassign_actor_everywhere'), hasattr(api,'DeleteActorBody'))"` → `True True` ✓
- `pytest tests/test_boot_smoke.py`：**7/7 通过** ✓
- 全套 `pytest tests/`：18 pass / 5 pre-existing fail (与 follow-up 025 完成时同样的 5 个 wukong_juexing-fixture-missing failures，零回归)

## Follow-up 025 — 2026-05-12 22:51:47
Source: user_input/follow_ups/025-20260512-225147-kling-only-provider-and-env-file.md
Summary: 用户："Lets remove the rest options to generate pictures, only use kling api key, here is the key you can put it in some local env file that is not tracked by git" + 直接提供 Access/Secret Key。**把 face generation 收窄为 Kling-only**：删除 follow-up 021 引入的 multi-provider chain (Pollinations + AI Horde) + follow-up 024 的 chain-fallback 静默 skip 行为；Kling env vars 升为 **required**，缺失时启动期 failfast。**凭证存储**：新增 `projects/ai_video_management/backend/.env`（根 `.gitignore` `.env` pattern 已覆盖，不入 git）+ stdlib `libs/env_loader.py`（KEY=VALUE 解析，**不引入 python-dotenv**）+ `main.py` 与 `libs/asgi.py` 启动期 `load_env_file()`。

Backend:
- `libs/actor_pool.py` 重写：删除 `PollinationsProvider` + `AIHordeProvider` + `Provider` Protocol + `ProviderChain` + `_FetcherShimProvider` + `HttpFetcher` + `_default_fetcher` + `_parse_retry_after` + `_RETRY_BACKOFFS_SECONDS` + `_RETRY_AFTER_CAP_SECONDS` + `POLLINATIONS_BASE` + `_build_pollinations_url` + 全部 `AIHORDE_*` 常量 + `PROVIDERS_ENV_VAR` + `_DEFAULT_PROVIDER_NAMES` + `_PROVIDER_FACTORIES` + `_build_default_chain`
- `KlingProvider` 保留并升为唯一 provider；`from_env()` 行为不变；`ActorPool.__init__` 移除 `fetcher` + `chain` kwargs，新增 `provider: KlingProvider | None`；缺 env → 构造期 `RuntimeError("kling env keys missing; set KLING_ACCESS_KEY + KLING_SECRET_KEY ...")`
- `_build_sidecar` 字符串 "AI-generated actor face (pollinations.ai, follow-up 014)" → "(Kling text-to-image, follow-up 025)"
- `__all__` 收窄到 Kling-only + 通用常量
- `libs/env_loader.py` (NEW)：~30 行 stdlib `load_env_file(path: Path) -> int`；skip 空行 + `#` 注释；只 `os.environ.setdefault`（已存在 env 优先）；FileNotFoundError + OSError → return 0
- `main.py`：`load_env_file(Path(__file__).resolve().parent / ".env")` 在 import `libs.api` 前调用
- `libs/asgi.py`：同上，`Path(__file__).resolve().parent.parent / ".env"` (从 libs/ 上一级)

Frontend:
- `frontend/src/components/ActorPoolGenerator.tsx`：删除 `INTER_REQUEST_THROTTLE_MS = 2000` 常量 + 主循环 `await setTimeout(2000)` 块；删除 `phase: "throttling"` 状态 (`Progress.phase` 收窄到 `"idle" | "generating"`)；删除 ProgressPanel "⏸ 等待限速冷却…" 分支 + footer "等待 2s 防限速…" 按钮文本；删除 `<p className="rate-limit-hint">ℹ️ pollinations.ai 免费 endpoint 有限速 …</p>` banner
- `frontend/src/styles.css`：删除 `.rate-limit-hint { ... }` 整个 rule block（follow-up 018 引入的 CSS class 已无引用）

Spec / validation:
- `final_specs/spec.md` FR-9f 重写：删除 (a) Pollinations + (b) AI Horde 段；保留 Kling 段并提到 Kling env vars 升 required + .env 加载流程 + failfast；删除 `AI_VIDEO_MGMT_FACE_PROVIDERS` 提及；FR-9 master 注释 "outbound HTTP calls (pollinations.ai)" → "Kling text-to-image per follow-up 025"
- `validation/security.md` carve-out #7 重写：从 3-provider chain hardening 收窄为 Kling-only；新增 .env 加载流程 + .env 文件不在 EXPOSED_TREE (`projects/` 不在 FR-7 的 5 个 root 内) 的说明；residual risks 收窄为 (i) Kling 单点 + (ii) Kling CDN TOCTOU + (iii) 内容过滤 + (iv) 内网 egress
- `validation/security.md` 全文 `SEC-OUTBOUND-POLLINATIONS` → `SEC-OUTBOUND-KLING`（两处）
- `validation/acceptance_criteria.md` U3.15：标题 + Given 行的 monkey-patch 注释改为 Kling；新增 "KLING env 已设" precondition

User-input:
- `user_input/revised_prompt.md`：composed-from 加 025；Last regenerated 改 2026-05-12 22:51:47；header summary 替换为 025 内容（删除 024 长 summary 文本但保留 follow-up 024 reference）；Prior follow-up 024 标记为 "已被 025 部分覆盖：KlingProvider + JWT + aspect ratio mapper + SSRF-vet 保留，chain 抽象删除"

Auto-updated:
- `projects/ai_video_management/backend/.env` (NEW，untracked) — Kling access + secret key
- `projects/ai_video_management/backend/libs/env_loader.py` (NEW) — stdlib KEY=VALUE 加载器
- `projects/ai_video_management/backend/libs/actor_pool.py` — Kling-only 重写 (~340 行 net delete)
- `projects/ai_video_management/backend/main.py` — `load_env_file()` 调用
- `projects/ai_video_management/backend/libs/asgi.py` — `load_env_file()` 调用
- `projects/ai_video_management/frontend/src/components/ActorPoolGenerator.tsx` — throttle + hint UI 删除
- `projects/ai_video_management/frontend/src/styles.css` — `.rate-limit-hint` CSS 删除
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9f Kling-only 重写
- `specs/development/ai_video_management/validation/security.md` — carve-out #7 Kling-only 重写 + SEC-OUTBOUND-KLING rename
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.15 Kling
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 025 summary
- `specs/development/ai_video_management/user_input/follow_ups/025-20260512-225147-kling-only-provider-and-env-file.md` (NEW)

No conflicts found in:
- `frontend/src/api.ts` / `frontend/src/components/Sidebar.tsx` / `frontend/src/components/Reader.tsx` / `frontend/src/components/ImageRefView.tsx`：HTTP API shape (`POST /api/actors/generate`) 不变
- `backend/libs/api.py` / `backend/libs/casting.py` / `backend/libs/media_archiver.py`：`ActorPool(exposed, resolver)` 构造签名兼容（新增的 `provider` kwarg 是可选）
- `backend/tests/`：无 actor_pool 测试 (follow-up 014-024 推迟 pytest)，无 `fetcher=` / `chain=` 引用，零回归
- 已生成的 `ai_videos/_actors/actor_0001..0009/actor_NNNN.md` sidecar 中 "pollinations.ai, follow-up 014" 字样：保留为历史 artifact（未来 regen 才覆盖）
- follow-up 014-024 follow-up draft 文件本身：保留为审计历史，不删
- `.claude/skills/agent_team/` 与 `.claude/agent_refs/`：本 follow-up 是 project-scoped instruction，不动 common surface

Verification (inline smoke):
- `load_env_file(backend/.env)` 加载 2 个 keys ✓；二次调用 already-set env 不被覆写 ✓；missing file → 0 ✓
- `actor_pool.__all__` 收窄；`PollinationsProvider` / `AIHordeProvider` / `ProviderChain` / `_FetcherShimProvider` / `POLLINATIONS_BASE` / `AIHORDE_BASE_URL` / `PROVIDERS_ENV_VAR` / `_build_default_chain` / `HttpFetcher` / `Provider` 全部 `hasattr` 为 False ✓
- `KlingProvider.from_env()` 加载 env 后返 `KlingProvider` instance ✓
- `_make_kling_jwt('AKtest','SKtest', exp_seconds=60)` 仍生成 3-part JWT ✓
- `ActorPool(FakeExposed, FakeResolver)` 在缺 env 时 raise `RuntimeError("kling env keys missing ...")` ✓
- `pytest tests/test_boot_smoke.py`: **7/7 通过** ✓
- 全套 `pytest tests/`: 18 pass / 5 pre-existing fail (sub_type_lookup / tree_walker + 2 origin-host edge — 全部在 stashed pre-025 tree 上同样 5 fail，零回归)
- Frontend `tsc --noEmit`：仅 vite.config.ts 的 2 个 pre-existing `path` typing 错误，actor-pool / sidebar 编辑零 error

## Follow-up 024 — 2026-05-12 23:30:00
Source: user_input/follow_ups/024-20260512-233000-kling-text-to-image-provider.md
Summary: 用户提议 "if I give you kling text to image api, would that help?" 后，先 push back 之前用户提的方案 A (TPDNE — StyleGAN/FFHQ documented Asian bias，命中率仅 10-30%，需 ML classifier 或人工 curation) 与方案 C (Generated.Photos — ToS 明禁 "caching, stockpiling, or downloading photos as stand-alone files")，研究确认两者均不可行；Kling 是真正适配（商业级 + 用户已有 access + ~1-3s/img + prompt-based attribute control）。**加 Kling 作为第 3 个 face provider，放 chain 首位**。

实现:
- 新增 `KlingProvider` 类：JWT HS256 + async submit + poll + r2-CDN download；遵循 follow-up 021 引入的 Provider Protocol
- `_make_kling_jwt(ak, sk)`：纯 stdlib (`hmac` + `hashlib` + `json` + `base64`)，3-segment JWT (header.payload.signature)，claims `{iss: ak, exp: now+1800, nbf: now-5}`；**不引入 `PyJWT` 依赖**
- `_kling_aspect_ratio(width, height)`：从 (512, 512) 推断 "1:1" / "16:9" / "9:16" / "4:3" / "3:4"（Kling 不接受任意分辨率必须 enum）
- `KlingProvider.from_env()`：lazy 读 `KLING_ACCESS_KEY` + `KLING_SECRET_KEY` env vars，缺任一返 None 让 chain factory 静默跳过
- 流程: POST `https://api.klingai.com/v1/images/generations` `{model_name: "kling-v1", prompt, aspect_ratio, n: 1}` → 检 `code == 0` → 拿 `data.task_id` → poll GET `/v1/images/generations?pageSize=500` 每 2s（max 120s）→ 找匹配 task → 检 `task_status == "succeed"` (or `"failed"` → raise) → `task_result.images[0].url` → 复用现有 `_is_safe_download_host` SSRF-vet → download with `follow_redirects=True` + 30s timeout + 5MB cap
- `_PROVIDER_FACTORIES["kling"] = lambda: KlingProvider.from_env()` —— factory 可返 None
- `_build_default_chain` 加 `if instance is None: continue` 支持 None-returning factories
- `_DEFAULT_PROVIDER_NAMES = ("kling", "pollinations", "aihorde")` —— Kling 优先；factory None→skip 让无 env 用户自动降级回 follow-up 021 chain（零 breaking change）
- `__all__` 加 `KlingProvider` / `KLING_BASE_URL` / `KLING_ACCESS_KEY_ENV` / `KLING_SECRET_KEY_ENV` / `KLING_DEFAULT_MODEL`

Spec / validation:
- `final_specs/spec.md` FR-9f 加 provider (c) Kling 描述：JWT HS256 stdlib-only 实现 + claims + async POST+poll+download 流程
- `validation/security.md` carve-out #7 hardening (g-bis): KLING_SECRET_KEY 仅 env 读、仅 `hmac.new` 输入用、不 log / 不进 URL / 不进 response；KLING_ACCESS_KEY 在 JWT `iss` claim 是 identifier 非 secret；`code != 0` 显式检查；JWT 每次 generate() 现生（30 分钟有效期，无 stale 风险）

前端零改动 — chain 对调用方透明，HTTP API shape 不变。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-12 23:30:00；Composed-from 加 follow-up 024；header 摘要描述 push back 两方案 + Kling 选型 + 实现 + verification；prior follow-up 023 line 移到 prior 列表
- `projects/ai_video_management/backend/libs/actor_pool.py` — 新增 ~150 行 KlingProvider + JWT helpers + aspect ratio mapper + provider factory；`_PROVIDER_FACTORIES` 加 "kling" slot；`_build_default_chain` 支持 None-returning factory；`_DEFAULT_PROVIDER_NAMES` 加 "kling" 在最前；`__all__` 扩展
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9f provider 列表加 (c) Kling
- `specs/development/ai_video_management/validation/security.md` — carve-out #7 (g-bis) Kling secret 硬化
- `specs/development/ai_video_management/user_input/follow_ups/024-20260512-233000-kling-text-to-image-provider.md` (NEW) — full follow-up draft 含 评估 / Kling API 摘要 / 实现 / 安全 / 不在范围

Verification (inline smoke):
- `from libs.actor_pool import KlingProvider, _make_kling_jwt, _kling_aspect_ratio, _build_default_chain, _DEFAULT_PROVIDER_NAMES` 全部 import 成功
- JWT 生成 byte-equality verify：解码 header `{"alg":"HS256","typ":"JWT"}` ✓；payload `{iss, exp, nbf}` 正确；signature `hmac.new(sk, header.payload, sha256)` byte-byte 匹配 ✓
- aspect ratio: 512×512 → "1:1"，1920×1080 → "16:9"，1080×1920 → "9:16" ✓
- `KlingProvider.from_env()`：无 env → None ✓；有 env (ak+sk) → KlingProvider instance ✓
- `_DEFAULT_PROVIDER_NAMES == ('kling', 'pollinations', 'aihorde')` ✓
- `_build_default_chain()` 有 env → `('kling', 'pollinations', 'aihorde')` ✓；无 env → graceful fallback `('pollinations', 'aihorde')` ✓
- `make boot-smoke`: **7/7 通过** ✓

No conflicts found in:
- 与 follow-up 023 (delete-media + `_deleted/`) 完全正交 —— 一个改 frontend reader + media_archiver，一个改 backend actor_pool outbound HTTP
- 与 follow-up 022 (sidebar collapse-all) 正交
- 与 follow-up 021 (multi-provider chain) 增强：在其 Provider 抽象基础上加新 provider 类
- 与 follow-up 020 / 019 (archive UI for direct media views) 正交
- 与 follow-up 018 (pollinations retry) 兼容：PollinationsProvider 仍封装 follow-up 018 retry 逻辑；Kling 不复用同样 retry (Kling 商业 endpoint 限速远松，简单 raise + chain failover 已足够)
- `validation/acceptance_criteria.md` U3.15 / U3.16 — pytest fixture 仍用 `fetcher=lambda` 路径通过 `_FetcherShimProvider`；Kling 不参与，无 conflict
- 所有 frontend 组件 / 其他 backend libs / casting.md / media archiver / api.py — 零影响

User next step:
1. 在 `app.klingai.com/global/dev` 创建账号 → API keys page → 拿 Access Key + Secret Key
2. PowerShell: `$env:KLING_ACCESS_KEY = "<your_ak>"` + `$env:KLING_SECRET_KEY = "<your_sk>"`
3. `make run-backend` 重启 backend 让 env 生效（`--reload` 只追代码改动，不追 env）
4. 点 "🎭 生成演员" → chain 现在 `kling,pollinations,aihorde` → 第 1 张走 Kling (~1-3s)，第 2 张走 pollinations，第 3 张走 AI Horde，第 4 张 wrap 回 Kling…
5. 若不设 env：chain 自动降级回 `pollinations,aihorde`，**完全没变化**，零风险
6. 单 Kling-only：`$env:AI_VIDEO_MGMT_FACE_PROVIDERS = "kling"` (跳过 pollinations + AI Horde fallback；要求 Kling 100% 可用)

Severity: Medium. Performance / user-blocking 真长效解（kling 商业级速度 10-30× 快过现有 free providers）；按用户 explicit 提议实现；零 breaking change（无 env 自动降级回 follow-up 021 chain）；secret handling hardening 已落地（hmac 计算 + 不 log + 不 leak）。改动范围：1 backend lib 加新类（~150 行）；前端零变动；API endpoint shape 零变动；安全 carve-out 扩展但所有新硬化点已落地。

## Follow-up 023 — 2026-05-12 22:15:39
Source: user_input/follow_ups/023-20260512-221539-delete-media-to-deleted-folder.md
Summary: mp4 / image reader 加 Delete 按钮 — soft-move 当前文件到 `ai_videos/_deleted/{保留 ai_videos 之下的子路径}`。新 backend endpoint `POST /api/delete-media` + 前端 Reader.tsx 双按钮 row（Archive + Delete）+ `_deleted/` 内文件两按钮全部隐藏。

Auto-updated:

**user_input:**
- `revised_prompt.md` — header bump：composed-from 末尾加 follow-up 023；Last regenerated 时间戳更新；follow-up 022 / 021 / 020 demote to "Prior"；新写 follow-up 023 summary（详述端点 mapping、target path 保留子结构、`_deleted/` 内按钮隐藏规则、警示红色 hover、不引入 in-app restore）。

**Generated outputs:**
- `backend/libs/media_archiver.py` —
  - 模块 docstring 加一段说明 follow-up 023 delete 行为。
  - 新增常量 `DELETED_DIR_NAME = "_deleted"`、`AI_VIDEOS_ROOT_NAME = "ai_videos"`。
  - 新增 exceptions `AlreadyDeleted`、`NotInAiVideos`。
  - `MediaArchiver` 新增 method `delete(self, rel: str) -> MoveResult`：复用 `_validate_media_source` 做 ext/sandbox/symlink 校验；relative parts[0] != "ai_videos" → `NotInAiVideos`；parts[1] == "_deleted" → `AlreadyDeleted`；target = `resolver.root / "ai_videos" / "_deleted" / Path(*parts[1:])`；`target.parent.mkdir(parents=True, exist_ok=True)`；target 存在 → `TargetExists`；`src.rename(target)` atomic；不删 src 原 parent。
- `backend/libs/api.py` —
  - 模块顶部 docstring：13 endpoints → 14 endpoints，列表加 `POST /api/delete-media`。
  - import from `media_archiver` 加 `AlreadyDeleted`、`NotInAiVideos`。
  - 新 endpoint `POST /api/delete-media` 复用 `ArchiveMediaBody` schema；mapping：InvalidPath→400 `invalid_path` / NotMedia→400 `extension_not_allowed` / NotInAiVideos→400 `not_in_ai_videos` / AlreadyDeleted→400 `already_deleted` / NotFound→404 `not_found` / TargetExists→409 `target_exists` / MoveFailed→500 `move_failed`。
  - 对应 method_not_allowed handler GET/PUT/PATCH/DELETE → 405 + Allow: POST。
- `frontend/src/api.ts` — 加 `export async function deleteMedia(path: string): Promise<ArchiveMediaResult>` POST `/api/delete-media`，复用 `ArchiveMediaResult` 类型。
- `frontend/src/components/Reader.tsx` —
  - import 加 `deleteMedia` from `../api`。
  - 加 `deleting: boolean` state。
  - 加 `onDeleteClick` useCallback (依赖 `[path, onSaved, navigate]`)：`window.confirm` 拦一次，确认后 `deleteMedia(path)` → 成功 announce + `onSaved()` + `navigate(/file/encoded)` → 失败 announce 错误 + button re-enable。
  - 派生 `isDeletedFile = path.startsWith("ai_videos/_deleted/")`、`mediaActionsBusy = archiving || deleting`、`deleteLabel`（`🗑 Delete` / `Deleting…`）。
  - `isVideo` / `isMediaImage` 分支：原 single archive button 包入新 `<div className="reader-media-actions">` flex row + Delete button；整个 actions 块在 `!isDeletedFile` 下渲染（`_deleted/` 内文件两按钮都隐藏，视频/图片仍正常播放）。
  - 两按钮共享 busy guard `disabled={mediaActionsBusy}` 防止并发 archive + delete。
- `frontend/src/styles.css` — 加 `.reader-media-actions`（flex row + justify-content center + gap 10px）+ `.reader-media-delete-btn`（基线尺寸同 archive；hover → color `--error-text` / bg `--error-bg` / border-color `--error-border` 警示红，全部复用既有 light-theme error 色板不引入新色）。

No conflicts found in: `SiblingMedia.tsx`（未触碰；批量 archive grid 仍服务 markdown / imageRef / shotPair 分支）; `Sidebar.tsx`（`_deleted/` 默认 walk 进 tree，无需 EXCLUDED_DIRS 改动；follow-up 022 的 collapse-all 让噪声可控）; `App.tsx`（onSaved 仍触发 tree refresh）; `exposed_tree.py`（`_deleted/` 不在 `_EXCLUDED_DIRS`，默认可见，与 `_actors/` 一致）; `_validate_media_source`（沿用 archive 路径校验链）; `interview/qa.md`, `findings/dossier.md`, `final_specs/spec.md`, `validation/*`（均未 prescribe 唯一目录布局 / 唯一移动语义 — follow-up 008 + 011 + 019 + 020 + 023 是 UX 渐进迭代）。

Verification (静态 reasoning + manual smoke 路径)：
- 后端：`media_archiver.delete("ai_videos/mozun/characters/c1/c1_1.mp4")` 预期返回 `{from: "ai_videos/mozun/characters/c1/c1_1.mp4", to: "ai_videos/_deleted/mozun/characters/c1/c1_1.mp4"}`；新建链上每级目录；原 c1/ folder 不删。
- 后端边界：non-media ext → `extension_not_allowed`；non-`ai_videos/` 路径 → `not_in_ai_videos`；已在 `_deleted/` 下 → `already_deleted`；target 已存在（罕见：先 delete 再撤销再 delete）→ `target_exists`。
- 前端：mp4 reader 显示 `<video>` + 两按钮 row；点 Delete → confirm 弹窗 "Move {filename} to _deleted/?"；OK → 请求 + navigate；Cancel → 不发请求。点 Archive 与 Delete 期间双向 disabled。点进已在 `_deleted/` 下的视频 → 视频正常播放，两按钮都不渲染。
- 安全：Origin/Host gate + sandbox + symlink reject + atomic rename 沿用既有契约，无新 carve-out。

## Follow-up 022 — 2026-05-12 22:07:24
Source: user_input/follow_ups/022-20260512-220724-sidebar-collapse-all-icon.md
Summary: Sidebar 顶部加 collapse-all 图标按钮 — 点击 `⊟` 折叠左 nav 全部 folder 节点。Toolbar 行紧贴 sidebar 顶部、`renameToast` 之上；状态利用现有 `expanded: Record<string,boolean>`，与 line-50 tree-init effect 的合并顺序天然兼容（collapse 跨 tree refresh 持久，新 folder 仍默认展开）。

Auto-updated:

**user_input:**
- `revised_prompt.md` — header bump：composed-from 末尾加 follow-up 022；Last regenerated 时间戳更新；follow-up 021 从 latest 降为 "Prior follow-up 021"；新写 follow-up 022 summary。

**Generated outputs:**
- `frontend/src/components/Sidebar.tsx` —
  - 加 `onCollapseAll` useCallback（依赖 `[tree]`）：walk tree → 把所有 `type` 非 file/image/video 的节点 path 收集进 `accum: Record<string, boolean>` 都设为 `false` → `setExpanded(accum)` 直接覆盖 prev。
  - 在 `<nav className="sidebar">` 内、`renameToast` 渲染之前，插入 `<div className="sidebar-toolbar">` 内置单按钮 `<button className="sidebar-collapse-all" aria-label="折叠全部" title="折叠全部 · Collapse all folders" onClick={onCollapseAll}>⊟</button>`。
  - 不动 line-50 / line-62 useEffect（tree-init 默认 expand-all 行为对新 folder 仍正确；`prev` 覆盖让 collapse 状态跨 tree refresh 持久）。
  - 不动 keyboard navigation / ActorPoolGenerator / renameToast 等既有 sidebar 功能。
- `frontend/src/styles.css` — 紧贴 `.sidebar-loading` 之后新增 `.sidebar-toolbar`（flex row + justify-content flex-end + border-bottom var(--border) + bg var(--bg-sidebar) + padding 4px 10px 6px）与 `.sidebar-collapse-all`（transparent bg / muted color / 16px / padding 2px 8px / border-radius 3px / hover → text + bg-toolbar + border / focus-visible → 2px solid var(--border-strong) outline）。

No conflicts found in: backend（纯前端 client-side state，零调用后端）; `App.tsx`（sidebar 仍接 `tree / currentPath / onSelect / onTreeReload` 旧 props，零 prop 签名变化）; `ActorPoolGenerator.tsx`（modal 触发逻辑不变）; `interview/qa.md`, `findings/dossier.md`, `final_specs/spec.md`, `validation/*`（均未 prescribe sidebar 必须无 toolbar / 默认全展开为契约 — 本 follow-up 是 UX 增量不是契约破坏）。

Verification (静态 reasoning)：点击按钮 → `setExpanded(allFalseMap)` → flat memo 重算 → 任何 `depth > 0` 的节点 `isOpen = expanded[path] === true` 为 `false` → 子节点不被 walk 进 flat array → 视觉上只剩 top-level；`depth === 0` 由 line 97 强制 `isOpen=true` 不受影响。用户实测路径 `ai_videos/mozun_chongsheng/characters/c1_沧冥/c1_沧冥1.mp4`：点 collapse-all 后 sidebar 应只看到 `ai_videos/`（或其下两个 top-level drama 名），其余隐藏；breadcrumb + reader 仍显示当前文件路径，用户可手动重新展开。键盘 Tab 到 button 后 Enter / Space 都触发 onCollapseAll。Focus-visible outline 走 `--border-strong` (#afb8c1) 已定义。

## Follow-up 021 — 2026-05-12 23:00:00
Source: user_input/follow_ups/021-20260512-230000-multi-provider-face-generation.md
Summary: 应用户提议"is pollination.ai the only site you could download free ai generated pictures? is there any other free alternative?"引入 **multi-provider face generation 架构**。Research 9 个候选（pollinations / AI Horde / Cloudflare Workers AI / Together AI / HuggingFace Inference / Puter.js / DeepAI / ZSky / Generated.Photos）；否决 Generated.Photos (ToS 禁 download)、Puter.js (browser-only 无 server-side path)、其他需要 signup / token / cold start 的。用户答**保留 pollinations + AI Horde fallback**（不引入 Cloudflare 因要 signup），策略 **round-robin per image with failover**。

Backend 重构：
- 新增 `Provider` Protocol：`name: str` + `generate(prompt, seed, width, height) -> bytes`
- 新增 `PollinationsProvider`：封装 follow-up 018 的 `_default_fetcher` 重试逻辑 + URL 构建。行为契约不变（3 retries on 429 + timeout，Retry-After honored capped 60s）
- 新增 `AIHordeProvider`：async POST→poll→download；base URL `https://aihorde.net/api/v2` + anonymous apikey `"0000000000"` 写死；流程 POST `/generate/async` → poll `/generate/check/{id}` 每 5s 直到 `done:true` 或 `faulted:true` (max 180s) → GET `/generate/status/{id}` 拿 `generations[0].img` (r2.dev URL) → SSRF-vet hostname (`_is_safe_download_host`: https only + 拒 loopback/RFC1918/link-local/multicast/reserved IPs via `socket.getaddrinfo`) → GET 该 URL with `follow_redirects=True` + 30s timeout + 5MB cap
- 新增 `ProviderChain` 类：`__init__(providers)` 拒空 list；`generate(...)` 每次前进 index 1 (round-robin)，失败时 fall through 同 chain 余下 provider 直到一个成功或全失败；全失败抛 `RuntimeError` 含 `last_exc` chain + 所有 provider 失败原因汇总
- 新增 `_FetcherShimProvider`：把 legacy callable `(url, timeout, max_bytes) -> bytes` 包成 Provider，让现有测试 `fetcher=lambda` 参数继续 work 无需重写
- 新增 `_build_default_chain()`：读 env var `AI_VIDEO_MGMT_FACE_PROVIDERS` (默认 `"pollinations,aihorde"`)，map 到工厂 dict；garbage 输入降级为单 pollinations chain
- `ActorPool.__init__` 签名扩展 `fetcher | chain | (env default)` 三路：fetcher 路径走 shim，chain 路径直接用，默认路径 `_build_default_chain()`
- `generate_batch` 把 `self._fetcher(url, ...)` 改为 `self._chain.generate(prompt, seed, IMAGE_WIDTH, IMAGE_HEIGHT)`；URL 构建从 ActorPool 移到 PollinationsProvider 内部
- 删除 `ActorPool._build_url` 静态方法（已下沉到 provider）

Spec / validation 改动：
- `final_specs/spec.md` FR-9f 重写：扩展为"通过 ProviderChain 调度，round-robin per image with failover"，列两 provider 完整流程契约
- `validation/security.md` Open carve-out #7 扩展：双 provider 各自的硬化（pollinations no-redirect / AI Horde SSRF-vet + follow-redirect 安全），加 4 类残余风险（双 provider 可用性依赖 / SSRF TOCTOU 子毫秒窗 / 无内容过滤 / localhost 触发外部 IO）

前端零改动 — chain 对调用方透明，`POST /api/actors/generate` body / response shape 不变。follow-up 017 frontend loop + follow-up 018 throttle 全部继续 work。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-12 23:00:00；Composed-from 加 follow-up 021；header 摘要描述 research 否决理由 + 两 provider 流程 + chain 行为 + verification；prior follow-up 020 line 保留
- `projects/ai_video_management/backend/libs/actor_pool.py` — 完全重构 outbound HTTP 层：新增 ~200 行 Provider 抽象 + AIHordeProvider 实现 + ProviderChain 实现 + env-driven 默认工厂；删除 `ActorPool._build_url`；调整 `ActorPool.__init__` 接受 `chain` 参数 + 内部用 `self._chain.generate(...)`；imports 加 `socket` / `ipaddress` / `os` / `urlparse` / `Protocol`；模块 docstring + `__all__` 更新
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9f 改写
- `specs/development/ai_video_management/validation/security.md` — Open carve-out #7 改写
- `specs/development/ai_video_management/user_input/follow_ups/021-20260512-230000-multi-provider-face-generation.md` (NEW) — full follow-up draft 含 research summary + 用户决策 + 架构设计 + 安全 / 边界扩展 + 不在范围

Verification (inline smoke checks):
- imports: 所有新 symbol (Provider / ProviderChain / PollinationsProvider / AIHordeProvider / `_build_default_chain` / PROVIDERS_ENV_VAR / `_is_safe_download_host`) 全部 import 成功
- `_build_default_chain()` 默认 → `('pollinations', 'aihorde')`
- `_is_safe_download_host`: sandbox 环境 DNS 受限故全 False（safe default）；reject `http://` (无 https) / `https://127.0.0.1` / `https://localhost` 均确认；生产 user 机器能 resolve `cdn.aihorde.net` → admit
- ProviderChain round-robin: A + B chain 调 3 次，A 始终 fail → A.calls=2 (起步位 0,_,0) + B.calls=3 (always 接管或起步) → 与设计一致
- ProviderChain failover: A fail + B ok → A.calls=1 + B.calls=1 + 返回 B bytes
- ProviderChain all-fail: 全 fail → RuntimeError 含 "all providers failed: A: ...; B: ..."
- ProviderChain([]) → ValueError
- ActorPool 集成: poll-always-fail + horde-ok chain → generate_batch(count=3) → 3 actor 全成功通过 horde 落盘
- Back-compat fetcher: `ActorPool(..., fetcher=lambda u,t,m: bytes)` → 仍能 generate 2 actor 通过 shim
- env var: `pollinations` → `('pollinations',)`；`aihorde,pollinations` → 逆序；`unknown,garbage` → 降级为 `('pollinations',)`
- `make boot-smoke`: **7/7 通过**（含 follow-up 014 加的 5 endpoint registration 断言）

No conflicts found in:
- `backend/libs/casting.py` / `media_renamer.py` / `media_archiver.py` / `downloads_importer.py` / `api.py` — 零影响；`api.py` 只用公共接口 `ActorPool` / `ActorAttrs` / `InvalidAttribute` / `GenerationDirMissing`，签名不变
- 所有前端组件 — chain 对前端透明，HTTP API shape 不变
- `validation/acceptance_criteria.md` Scenario U3.15 / U3.16 — 仍 valid；测试 fixture 用 `fetcher=lambda` 路径，通过 `_FetcherShimProvider` 走通
- 与 follow-up 020 (mp4 page single archive button) 完全正交

User next step:
1. Backend `--reload` (follow-up 012 默认) 自动检测 `libs/actor_pool.py` 改动 + reload。无需手动重启。
2. 可选设置 env var：PowerShell `$env:AI_VIDEO_MGMT_FACE_PROVIDERS = "pollinations,aihorde"` (默认值)；或 `"aihorde,pollinations"` 让 AI Horde 优先；或 `"aihorde"` 单 provider 跳过 pollinations。env 改动需 `make run-backend` 重启才生效（`--reload` 只追代码改动）。
3. 重试 count=20：第 1 张走 pollinations，第 2 张自动走 AI Horde；失败时另一 provider 接管。pollinations 限速但快，AI Horde 慢但无限速；混合后整体 throughput + 成功率应显著提升。
4. AI Horde 首次匿名调用 wait 可能 60-120s（kudos 0 → 队列末位）；后续 wait 通常 20-60s。如希望更快，独立 follow-up 加 Cloudflare Workers AI provider（需用户提供 free tier token）。

Severity: Medium. 用户报告的限速 blocker 的长效解。改动范围：1 backend lib 重构（新增 ~200 行 Provider 抽象 + AIHorde implementation），前端零变动；API 契约 / spec FR-9f 文字扩展但 endpoint shape 不变；安全 carve-out 扩展但所有新硬化点已落地。

## Follow-up 020 — 2026-05-12 21:57:51
Source: user_input/follow_ups/020-20260512-215751-mp4-page-single-archive-button.md
Summary: 收窄 follow-up 019：用户反馈 mp4 / image single-file reader 页面只要一个 archive 按钮，不需要 SiblingMedia grid + checkbox + toolbar。`isVideo` / `isMediaImage` 分支替换为内联 archive/unarchive 按钮，path-based 自动判定方向，成功后导航到新路径。`isImageRef` / `isShotPair` 分支的 SiblingMedia 保留不变。

Auto-updated:

**user_input:**
- `revised_prompt.md` — header bump：composed-from 末尾加 follow-up 020；Last regenerated 时间戳更新；follow-up 019 从 latest 降为 "Prior follow-up 019" 并注明 video + image 分支收窄、imageRef + shotPair 保留；新写 follow-up 020 summary。

**Generated outputs:**
- `frontend/src/components/Reader.tsx` —
  - import 加 `useNavigate` from react-router-dom、`archiveMedia` + `unarchiveMedia` from api。
  - 加 `archiving: boolean` state。
  - 加 `onArchiveToggle` useCallback：path 分段，`parts[length-2] === 'archive'` 判定 inArchive；调用 unarchive 或 archive；成功 `announceToast` + `onSaved()` + `navigate(/file/encoded)` 到新路径；失败公告。
  - 派生 `isArchivedFile` + `archiveLabel`（`📦 Archive` / `↺ Unarchive` / `Archiving…` / `Unarchiving…`）。
  - `isVideo` 分支：移除 follow-up 019 加的 `<SiblingMedia>`，回到单 `<div className="media-view">`，里面 `<video>` 之下加 `<button className="reader-media-archive-btn">`。
  - `isMediaImage` 分支：同上。
  - `isImageRef` / `isShotPair` 分支：**保留 follow-up 019 加的 SiblingMedia 不变**。
  - 文件底部加 module-level `announceToast` + `archiveErrorKind` helpers（与 SiblingMedia.tsx 内同名 helper 行为一致；不抽 util 文件以保持单文件修改）。
- `frontend/src/styles.css` — 新增 `.reader-media-archive-btn` 样式：inline-block、margin-top 12px、padding 6px 14px、light-theme bg-panel + text-muted、hover 时切到 bg-toolbar + text；disabled 时 cursor: progress + opacity 0.55。挂在 `.media-view video { width: 100%; }` 之后。

No conflicts found in: backend (`backend/libs/media_archiver.py` + `POST /api/archive-media` / `POST /api/unarchive-media` 已支持单 path 原子调用); `SiblingMedia.tsx`（未触碰；仍服务 markdown / imageRef / shotPair 分支）; `interview/qa.md`, `findings/dossier.md`, `final_specs/spec.md`, `validation/*`（均未 prescribe 单文件 archive UI 形态 — follow-up 008 + 011 + 019 的描述均为渐进迭代，本 follow-up 是 UX 收窄不是契约破坏）。

Verification: 用户实测路径 `ai_videos/mozun_chongsheng/characters/c1_沧冥/c1_沧冥1.mp4`。预期：reader 上半 `<video>`，正下方一个 "📦 Archive" 按钮；点击后请求 archive endpoint → 文件移到 `c1_沧冥/archive/c1_沧冥1.mp4` → URL 自动跳新路径 → reader 重新加载同一 mp4 但按钮变成 "↺ Unarchive"（用户可立刻 misclick recovery）。Sidebar 同时 refresh 显示新位置。Aria-live toast 公告 "Archived c1_沧冥1.mp4"。点 ImageRefView 或 ShotPairView 路径行为不变（仍显示 SiblingMedia 批量 grid）。

## Follow-up 019 — 2026-05-12 21:43:45
Source: user_input/follow_ups/019-20260512-214345-archive-ui-for-direct-media-views.md
Summary: archive feature 在 character / scene / shot folder 内**只对 markdown reader 可见**的回归 — follow-up 008 (per-tile archive) + 011 (批量 multi-select archive) 完全实现，但 `Reader.tsx` render-mode dispatch 只在 `isMarkdown` 分支挂 `<SiblingMedia>`。用户最自然的工作流是点 sidebar 里的 `.mp4` 直接看，走 `isVideo` 分支 → 没归档 UI。

Auto-updated:

**user_input:**
- `revised_prompt.md` — header bump：composed-from 末尾加 follow-up 019；Last regenerated 时间戳更新；follow-up 018 从 latest 降为 "Prior follow-up 018"；新写 follow-up 019 summary。

**Generated outputs:**
- `frontend/src/components/Reader.tsx` — `reader-body` JSX 内，`isVideo` / `isMediaImage` / `isImageRef` / `isShotPair` 四个分支各挂一份 `<SiblingMedia currentPath={path} knownPaths={knownPaths} onChange={onSaved} />`（props 与既有 markdown 分支完全一致），用 React fragment `<>...</>` 包住。零后端改动、零 CSS 新增、零新 endpoint。`isCasting` / `isShotlistTable` / `isJsonl` / `isCode` / `isTxt` 不挂（drama-root 级文件，无 ref-video 用例）。

No conflicts found in: backend (`backend/libs/media_archiver.py` + `POST /api/archive-media` / `POST /api/unarchive-media` 已支持 011 的批量循环用例); `SiblingMedia.tsx` (返回 `null` 当 `siblings.length === 0 && archived.length === 0` — 单文件文件夹无视觉回归); `styles.css` (复用 008 + 011 已有 grid / toolbar / checkbox 样式); `interview/qa.md`, `findings/dossier.md`, `final_specs/spec.md`, `validation/*` (均未 prescribe SiblingMedia 仅在 markdown 下渲染的 invariant — follow-up 005 的"在 markdown 渲染下方"是描述当时实现而非约束，本 follow-up 是 render-scope 扩展不是契约破坏).

Verification: 用户实测路径 `ai_videos/mozun_chongsheng/characters/c1_沧冥/` 含 1 个 `.md` + 8 个 `.mp4`。预期：点 sidebar 任一 mp4 → Reader 上半显示 `<video>`，下半显示 SiblingMedia grid（剩余 7 个 mp4 + 任何同 folder png/jpg），始终可见左上角 checkbox + section toolbar "📁 Folder media · 同 folder 媒体" + "Select all" / "Clear" / "📦 Archive Selected (N)"。Scene `s1_长阶顶/` (4 mp4)、shot folder 同 grid 行为。`isImageRef` (`_seedream.md`) + `isShotPair` 同样受惠 — 比如 character ref_images folder 内多张 _seedream.md 互为 sibling 时可批量归档实验稿。

## Follow-up 018 — 2026-05-12 22:30:00
Source: user_input/follow_ups/018-20260512-223000-pollinations-rate-limit-retry.md
Summary: 修用户实测中暴露的 **pollinations.ai 429 rate limit cascade**。用户 count=20 第 1 张成功后所有后续 429，所有 error 报相同 `actor_0003`。**两个独立 bug 合流**：(A) **限速无重试** — follow-up 014 `_default_fetcher` 单次 GET，pollinations.ai 免费 endpoint 限速激进，一连发 ≥2 请求即 429，无 backoff 直接冒泡。(B) **incomplete folder 占 ID** — follow-up 014 `_next_actor_id_num` 用 `_ACTOR_DIR_RE` regex 数 max+1，旧批失败时若 mkdir 成功但 jpg 没写盘（429 / timeout 在 stream 期间），cleanup 路径有时 swallow OSError 失败，残留空 folder 被下批算进 max → 死循环每次 `actor_0003`。

**三处修复**：

1. **Backend retry-with-backoff** (`actor_pool.py:_default_fetcher` 重写)：
   - 最多 3 次重试，backoff `[3s, 6s, 12s]` 累计 21s + httpx timeout
   - 单图 worst case wall-clock ~81s（仍远低于浏览器 fetch timeout，且前端 follow-up 017 已搬循环出 backend）
   - 429: honor `Retry-After` header（delta-seconds form per RFC 7231 §7.1.3）capped 60s；缺则用 backoff 默认
   - 读 / 连接 / 写 timeout: 同 backoff 重试
   - 其他 4xx/5xx（404/500/...）不重试直接 raise（避免浪费 wall-clock）
   - 新 helper `_parse_retry_after(header_value, default)` —— 解析 header_value or fallback to default, capped at 60s, 处理 garbage 输入
2. **Incomplete folder reap** (`actor_pool.py:_next_actor_id_num` 重写)：
   - 命中 `_ACTOR_DIR_RE` 但缺 `<id>.jpg` 的 folder：**不计 max**、立即 cleanup（删 folder 内任何 partial 文件 → rmdir）
   - cleanup 失败 silently swallow（与 `_cleanup_empty_folder` 一致，磁盘 dirty 不阻塞批次）
   - 副作用：用户**手动**创建的空占位 folder 会被删；不在 v1 contract 内，可接受
3. **Frontend inter-iteration throttle** (`ActorPoolGenerator.tsx`)：
   - 新增 `INTER_REQUEST_THROTTLE_MS = 2000` 常量
   - 每次 `await generateActors()` 完成后、下一轮开始前 sleep 2s（最后一轮不 sleep；cancelled 状态下也不 sleep）
   - `Progress.phase` 新 enum 字段 `"idle" | "generating" | "throttling"` —— UI 在 throttle 期间显示 `⏸ 等待限速冷却…` + 按钮文案 `等待 2s 防限速… (i / N)`
   - modal 内加 `.rate-limit-hint` 文字行告知用户机制："pollinations.ai 免费 endpoint 有限速 — 每张间隔 2 秒；遇到 429 后端自动重试 3 次（最长等 60s）"

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-12 22:30:00；Composed-from 加 follow-up 018；header 摘要描述两根因合流 + 三处修复 + verification；prior follow-up 017 line 移到 prior 列表。
- `projects/ai_video_management/backend/libs/actor_pool.py`：
  - 新增 module-level 常量 `_RETRY_BACKOFFS_SECONDS=(3.0, 6.0, 12.0)` + `_RETRY_AFTER_CAP_SECONDS=60.0` + helper `_parse_retry_after`
  - `_default_fetcher` 重写：retry loop 4 attempts (1 initial + 3 retries) over 429 / timeouts；honor Retry-After；non-retriable HTTP 错误 raise_for_status 冒泡；max_bytes cap 检查保留
  - `_next_actor_id_num` 重写：跳过 + cleanup incomplete folders；保留 OSError swallow 模式
- `projects/ai_video_management/frontend/src/components/ActorPoolGenerator.tsx`：
  - `Progress` interface 加 `phase: "idle" | "generating" | "throttling"` 字段；每个 `setProgress` 调用同步更新 phase
  - `onSubmit` for-loop 末尾加 inter-iteration sleep 块（带 cancellation check）
  - `ProgressPanel` 子组件根据 phase 渲染不同 emoji + 文字（throttle → ⏸ / generating → 🔄）
  - footer "生成中…" 按钮 label 根据 phase 拆两种文案
  - modal-body 新加 `<p className="rate-limit-hint">` 行告知用户机制
- `projects/ai_video_management/frontend/src/styles.css` — 新增 `.rate-limit-hint` 样式（small info bar，复用 `--text-muted` / `--bg-toolbar` / `--border` CSS vars）

Behavior changes:
- **Before**: count=20 → 第 1 张成功 → 第 2 张 timeout / 429 → cleanup → 第 3 张 mkdir 成功 → 429 → cleanup 失败遗留空 folder → 第 4-20 张都 mkdir 新 folder（next_id_num 把残留 folder 算进 max 不前进）→ 全部 429。最终用户得到 1 张图 + 19 个失败 error 都报 `actor_0003`。
- **After**: count=20 → 第 1 张成功 → sleep 2s → 第 2 张请求（若 429 → backend 自动等 Retry-After / 3s → retry → 大概率成功；最坏 4 attempts 后才彻底失败）→ 若成功 sidebar 立即多 1 个 folder + UI 显示 `🔄 生成中… 2 / 20` → 完成后 `⏸ 等待限速冷却…` 显示 2s → 第 3 张……持续。worst case 单图 81s + 2s throttle = 83s；count=20 worst case = ~27 min（远超用户期望但不会卡死）；nominal case 单图 < 30s + 2s throttle ≈ 8 min for 20 张。
- 残留 incomplete folder（包括用户先前批次失败留下的）在下次 generate_batch 调用时被 reap → ID 单调推进，不再卡 `actor_0003`。

Verification (smoke checks):
- Python imports: `from libs.actor_pool import ActorPool, _parse_retry_after, _default_fetcher` 成功。
- `_parse_retry_after` 单元: `None / "5" / "999" / "garbage"` → `3.0 / 5.0 / 60.0 / 3.0`（默认 / 解析 / cap / fallback）✓
- `_default_fetcher` 重试 unit-test（patch `httpx.Client` with FakeClient）:
  - Test 1: 429 + Retry-After=1 → 第 2 attempt 200 → 返回 bytes；elapsed ≥ 1s；calls=2 ✓
  - Test 2: 持续 429 + Retry-After=0 → 4 次尝试后 raise HTTPStatusError ✓
- `_next_actor_id_num` cleanup unit-test（tmpdir 模拟先前批次残留）:
  - pre-state: `actor_0001` (jpg+md ✓) + `actor_0002` (空 incomplete) + `actor_0003` (md only, 缺 jpg)
  - `generate_batch(count=1)` → 落 `actor_0002` (reclaim 该 slot) + cleanup `actor_0003` (incomplete)
  - 第二批 `generate_batch(count=1)` → 落 `actor_0003`（单调推进）✓
- `make boot-smoke`: **7/7 通过**，含 follow-up 014 加的 5 个 endpoint registration 断言。
- Frontend `npx tsc --noEmit`: 无新错误（仅两个 pre-existing `vite.config.ts` 错误）。

No conflicts found in:
- `final_specs/spec.md` FR-9f — `POST /api/actors/generate` 契约不变（仍 `count: 1..20` + invalid_attribute + actors_dir_unwritable 错误码面）；retry 在单次 HTTP 调用内部完成，对调用方透明。
- `validation/acceptance_criteria.md` U3.15 — fake fetcher 仅返回 stub bytes，不触发 retry 路径；测试断言仍 valid。如需覆盖 retry path，独立 follow-up 加 `_default_fetcher` 单元测试（本 follow-up 已在 inline smoke 验证）。
- `validation/security.md` carve-out #7 — 出站 HTTP 边界**不弱化**：retry 仍 single base URL hardcoded、URL-encoded prompts、follow_redirects=False、30s/请求 timeout、5MB cap；仅在 429 / timeout 时多 ≤3 次相同硬化的请求 + Retry-After 受信但 capped 60s（避免恶意 / buggy header 触发长 sleep DoS）。
- `agent_refs/project/ai_video.md` — 与本 follow-up 正交。
- 其他 backend libs (`casting.py` / `media_renamer.py` / `media_archiver.py` / `downloads_importer.py` / `api.py` 等) — 零影响。
- 其他前端组件 (`Sidebar.tsx` / `CastingView.tsx` / `Reader.tsx` / `ImageRefView.tsx` 等) — 零影响。

User next step:
1. Backend `--reload` (follow-up 012 默认开) 自动检测 `actor_pool.py` 改动 + reload；Vite HMR 自动重载 `ActorPoolGenerator.tsx` + `styles.css`。浏览器刷新即可。
2. **重要**：用户先前批次留下的 `_actors/actor_0002/` 等 incomplete folder 会在下次点 "🎭 生成演员" 时**自动被 reap**（看到 sidebar 内残留 folder 突然消失属正常）。
3. 重试 count=20 验证：每张间隔 2s + 429 自动重试；预期成功率显著高于上次（pollinations.ai 实际限速强度未知，nominal case 应该 ≥80% 通过；若仍大量失败，独立 follow-up 加 per-image inter-iteration 间隔到 5s+）。
4. 若仍频繁 429：考虑改用其他 AI face source（独立 research follow-up），或人工降低 batch size 到 ≤5。

Severity: Medium. 用户报告的实际可用性 blocker；后端 retry 是首次出站 HTTP 路径上的稳定性 hardening；folder reap 修 follow-up 014 的隐性 bug。改动范围：1 backend lib 重写 2 函数 + 1 frontend 组件加 phase state + 1 CSS 行。后端 / API 契约 / spec FR / 安全 carve-out 零变动。

## Follow-up 017 — 2026-05-12 22:00:00
Source: user_input/follow_ups/017-20260512-220000-actor-generation-progress-visibility.md
Summary: 修 follow-up 014 引入的 batch generate UX 问题 — 用户报告点 "🎭 生成演员" 选 count=20，磁盘只出现 1 张图片，剩 19 张状态不明（仍在跑？失败？已结束？）。**根因**：`POST /api/actors/generate` 同步串行循环 count 次 pollinations.ai 请求（每次 5–30s），count=20 worst case = 10 分钟，浏览器 fetch 默认 timeout ~5 min 中途断开 → 后端 silently 继续 loop、前端 catch ApiError 显示 "失败" toast、用户无任何 in-flight 状态指示。后端 errors[] 数组也因连接断开永远到不了前端。**Fix**：搬移循环到前端，**不动后端**。`ActorPoolGenerator` 重写：把 count=N 拆 N 次 count=1 串行调用，每次秒级返回；实时显示 progress bar + 累积 errors 列表 + 已生成 ID 列表；每次成功 / 失败立即调 `onGenerated()` 触发 sidebar refresh；"停止" 按钮设 cancellation flag (React `useRef`，避免 stale closure)，loop 跳出但当前 inflight 请求继续完成；modal 关闭时若 busy 触发 cancel 而不立即 unmount，等 inflight 结束再关。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-12 22:00:00；Composed-from 加 follow-up 017；header 摘要描述同步循环 + 浏览器 timeout + 前端循环 fix；prior follow-up 016 line 移到 prior 列表。
- `projects/ai_video_management/frontend/src/components/ActorPoolGenerator.tsx` — 完全重写 `onSubmit`：从 1 次 `generateActors({count: N, ...})` 改为 N 次 `generateActors({count: 1, ...})` 串行循环；新增 `Progress` state interface (`done` / `failed` / `total` / `current` / `errors` / `generatedIds`)；`useRef<boolean>` 持有 cancellation flag（不用 state 因为 stale closure 会让 loop 看不见更新）；新加 `ProgressPanel` 子组件渲染进度条 + 摘要 (`✓ N · ✗ E · pct%`) + collapsible details（已生成 ID 列表 + 失败原因列表 with `#i: message`）；modal footer 在 busy 状态把 "取消" 按钮改 "停止"，busy 状态下 "关闭" 按钮 = "中断后关闭"；按钮文案 `生成中…` 改 `生成中… (i / total)` 实时刷新。
- `projects/ai_video_management/frontend/src/styles.css` — 新增 `.progress-panel` 容器 + `.progress-summary` + `.progress-ok` / `.progress-err` 颜色 + `.progress-bar` / `.progress-bar-fill` (CSS transition width 0.3s 让进度变化平滑) + `.progress-details` (collapsible summary / code block / ul) + `.progress-details-err` 错误列表色板。复用既有 `--accent` / `--border` / `--bg(-toolbar)` / `--error-text` / `--text(-muted)` CSS vars，无新增色板。

Behavior changes:
- **Before**: 点 "生成" count=20 → 浏览器发 1 个 POST → 等待 10 分钟 → 浏览器 timeout → 前端 toast `生成失败: 504` 或 `生成失败: Failed to fetch`；后端继续静默处理 19 张；用户不知所措。
- **After**: 点 "生成" count=20 → 前端发 20 个独立 POST 顺序 →
  - 进度条 0 → 100% 实时增长；
  - 数字 `0 / 20 → 1 / 20 → ... → 20 / 20`；
  - 每张完成后 sidebar 立即多 1 个 `actor_NNNN/` folder（onGenerated triggers tree reload）；
  - 任何一张失败：accumulator 加 error `#i: <reason>`，进度条仍前进 (failed 计入 done+failed)，loop 不中断；
  - 中途 "停止" → 当前 inflight 完成 → loop 跳出 → toast `已中断 — 已生成 X / 失败 Y / 跳过 Z`；
  - 关闭后再打开 modal：progress / toast / cancellation flag 全部重置（`useEffect [open]` 清理）。
- 单张请求 wall-clock ~5–30s，远小于浏览器 fetch timeout，故连接稳定不再 mid-batch 断开。
- 后端零改动 — pytest scenarios U3.15 仍 valid（仍用 count=3 单次调用），actor_pool.py 行为契约不变。

Verification (smoke checks):
- Frontend `npx tsc --noEmit`: 无新错误（仅两个 pre-existing `vite.config.ts` 错误与本 follow-up 无关）。
- 渲染流验证（手动 trace）：modal open → state 全部 default → 用户调参 → 点 "生成" → busy=true, cancelledRef=false, progress 初始 0/N → for-loop i=1..N → 每轮 setProgress current=i → await generateActors(count=1) → 解构 generated[0].id + errors[] → push 到 accumulator → setProgress 更新 → onGenerated 触发 tree refresh → 下一轮；loop 结束 → setProgress current=0 → setToast 总结 → setBusy=false。
- "停止" 按钮路径：busy 时点击 → cancelledRef.current=true → 当前 await 完成后 for-loop 头部检测 cancelledRef → break → 进入 toast 总结。Modal 仍打开，progress 显示部分结果，用户可看 errors 然后关闭。
- 关闭 modal 路径：点击 backdrop / 关闭按钮 → onCloseRequest → if busy: cancelledRef.current=true (modal 不 unmount，等 inflight 完成)；if !busy: onClose() 直接 unmount。useEffect[open] 在下次 open=true 时重置 state（toast/progress 清空, cancelledRef=false）。
- Race conditions: `setProgress` 在 await 前后各调一次，确保 UI 在 in-flight 期间也显示 `(i / N)`；errors / generatedIds 用浅拷贝 `[...errors]` 保证 React 检测变化触发 re-render。

No conflicts found in:
- `backend/libs/actor_pool.py` — `generate_batch(attrs, count)` 实现完全不动；`count=1` 走同一路径，`MIN_BATCH_COUNT=1` 已存在所以 count=1 一直 valid。
- `backend/libs/api.py` `POST /api/actors/generate` 契约不动；前端循环对后端透明。
- `final_specs/spec.md` FR-9f / FR-88 — spec 文字说 "count: 1..20"，前端拆 count=20 为 20 次 count=1 仍满足契约（每次都是合法 count）。如要在 FR-88 加 "frontend 串行循环显示进度" 行为约束，可独立 follow-up；本 fix 不弱化任何 FR。
- `validation/acceptance_criteria.md` Scenario U3.15 — 测试 `POST /api/actors/generate count=3` 一次成功 + invalid attr / count 边界。前端循环不改 backend 测试。
- `validation/security.md` carve-out #7 — 出站 HTTP 限制不变（每次 count=1 仍 30s timeout + 5MB cap + base URL hardcoded）；前端连发 20 次的总流量仍由 backend 单次限制控制，且每次串行（无并发放大）。
- `Sidebar.tsx` / `CastingView.tsx` / `Reader.tsx` 等其他前端组件 — 零影响。
- `casting.py` / `media_renamer.py` / 其他 backend libs — 零影响。

User next step:
1. Vite HMR 自动重载 `ActorPoolGenerator.tsx` + `styles.css` → 浏览器刷新 modal 立即可见新 UI。
2. 旧批未完成的 19 张：可能磁盘上没出现（pollinations.ai 限速 / 后端进程已不再运行 / mid-batch 失败），可直接再次点 "🎭 生成演员" 跑新 batch；ID 单调自增不会冲突（已生成的 actor_0001 保留，新批从 actor_0002 起）。
3. 跑 count=20 验证：观察 modal 进度条 + 数字一张张跳；每张完成 sidebar 同步出现新 actor folder。

Severity: Medium-Low UX bug (后端无数据丢失风险 / 无 security 影响). 改动范围：1 个前端组件重写 + CSS 进度条样式。Backend / API 契约 / spec FR 零变动。

## Follow-up 016 — 2026-05-12 21:30:00
Source: user_input/follow_ups/016-20260512-213000-jpg-preview-uses-api-media.md
Summary: 修用户报告的 `.jpg` preview bug — 点击 `ai_videos/_actors/actor_NNNN/actor_NNNN.jpg`，Reader 显示一大段 base64 文本而非图片。**根因**（两件事的交叉）：① `backend/libs/file_reader.py:72-74` 对 `.png`/`.jpg` 走 `base64.b64encode` 返回 JSON `{content: "<base64>", encoding: "base64"}` —— 浏览器把它当 JSON 收，不是图片字节；② `frontend/src/components/Reader.tsx:43` 的 `isMediaOnly = isMediaVideo || (isMediaImage && ext !== ".png" && ext !== ".jpg")` 显式把 png/jpg 排除在 media-only 之外，加上 render 分支 `isMediaImage && ext !== ".png" && ext !== ".jpg" ? <img src={mediaUrl(path)}>` 也排除，导致 png/jpg fall through 所有 isVideo/isCasting/isImageRef/isShotPair/.../isMarkdown/isTxt 条件，最终落到 `<pre className="text-view">{file.content}</pre>` 兜底，渲染 base64 文本。其他 image 扩展（webp/gif/bmp）和 video 扩展走 `/api/media` raw bytes 正常 —— 这个差异性 bug 潜在了 5+ follow-up（005 引入 /api/media 后留下的不一致），follow-up 014 引入大量 `.jpg` 资产后首次暴露。**Fix**：让 `.png`/`.jpg` 也走 `/api/media`：① `Reader.tsx:43` `isMediaOnly = isMediaVideo || isMediaImage`；② `Reader.tsx` render 分支去掉 `ext !== ".png" && ext !== ".jpg"` 双重否定，统一为 `isMediaImage`；③ `ImageRefView.tsx` 两处 `imageUrl()` 换 `mediaUrl()` + import 同步换名（修同根因的二次 bug —— 仓库目前无 `_seedream.png` 加载过，本 follow-up 顺手治 root cause）。`/api/media` 端点 sandbox 限制（`exposed.is_inside` + `resolver.resolve`）与 `/api/file` 等价，不弱化安全。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-12 21:30:00；Composed-from 加 follow-up 016；header 摘要描述 base64 fall-through + 三处 fix；prior follow-up 015 line 移到 prior 列表。
- `projects/ai_video_management/frontend/src/components/Reader.tsx` — line 43 `isMediaOnly` 去掉 png/jpg 排除；render 分支 `isMediaImage && ext !== ".png" && ext !== ".jpg"` → `isMediaImage`。两处共 2 行改动。
- `projects/ai_video_management/frontend/src/components/ImageRefView.tsx` — import `imageUrl` → `mediaUrl`；line 55 (image-only layout) `imageUrl(...)` → `mediaUrl(...)`；line 86-87 (companion 立绘) `imageUrl(...)` → `mediaUrl(...)`。三处共 3 行改动 + 1 行 import。

Behavior changes:
- 点击 `.jpg` / `.png` 在 Reader 中：之前显示 base64 字符串墙（看上去像随机字符），现在显示 inline 图片（80vh max-height + center 对齐，与 `.webp`/`.gif`/`.mp4` 等同一 `.media-view` 容器）。
- ImageRefView companion 立绘右窗格：之前 `<img src="/api/file?path=...">` 加载 JSON 响应而失败渲染（HTTP 200 但 content-type=json），现在 `<img src="/api/media?path=...">` 加载 raw bytes 正常显示。注：仓库目前无 `_seedream.png` 资产被加载过，所以此分支的破损此前从未暴露。
- 之前 Reader load 对 png/jpg 也跑 `fetchFile()` 拿 base64 JSON（白白消耗 1MB cap 内的带宽 + memory）；现在跳过 `fetchFile()` 走 `/api/media` 流式响应，与其他 media 一致。

Verification (smoke checks):
- Frontend `npx tsc --noEmit`: 无新错误（仅两个 pre-existing `vite.config.ts` 错误与本 follow-up 无关）。
- 路径检查：点击 `ai_videos/_actors/actor_0001/actor_0001.jpg` → Reader 状态 `isMediaImage=true, isMediaOnly=true, ext=".jpg"` → load() skip fetchFile → setFile() 放 placeholder → render 分支命中 `isMediaImage` → `<img src={mediaUrl(path)}>` → 浏览器 GET `/api/media?path=ai_videos/_actors/actor_0001/actor_0001.jpg` → backend FileResponse 返回 image/jpeg bytes → 图片渲染。✓
- Existing `.png` paths in `characters/ref_images/` (e.g. 未来的 `_seedream.png`) 同理：之前 broken（不显示），现在正常渲染。✓
- `.webp/.gif/.bmp/.mp4` 等扩展：之前已通过 mediaUrl 正常工作，本 follow-up 零影响。✓

No conflicts found in:
- `backend/libs/file_reader.py` — base64 编码逻辑保留（其他调用方 e.g. potential 测试 / curl 直接 GET /api/file 可能仍依赖；本 follow-up 只改前端 render 路由，不改 `/api/file` 契约）。
- `backend/libs/api.py` `/api/media` endpoint — 不动；本身已有正确的 sandbox + MIME map + FileResponse + range support。
- `frontend/src/api.ts` `imageUrl` helper — 保留（公共 API，可能被 type-check / 测试 / 外部代码引用）；ImageRefView 已不再调用，可后续 follow-up 清理。
- `frontend/src/components/Sidebar.tsx` / `App.tsx` / `Editor.tsx` / `ShotPairView.tsx` / `ShotlistTableView.tsx` / `SiblingMedia.tsx` / `CastingView.tsx` 等 — 零影响。
- `final_specs/spec.md` FR-61 — spec 文字仍写 `<img src="/api/file?path={enc}&mtime={mtime}">`，但实际实现现在用 `/api/media`。这是 specs 的历史陈述 drift，**不阻碍 fix**；如需对齐，独立 follow-up 改 FR-61 + FR-19 image leaf 描述。
- `validation/*` — 无 acceptance scenario 显式断言 `.jpg` 渲染走 `/api/file` 还是 `/api/media`；行为契约「图片应当 inline 显示」继续满足。

User next step:
1. **若 backend + Vite dev server 都跑着**（follow-up 012 默认 `--reload` + Vite HMR）：浏览器刷新 `http://127.0.0.1:8766/` 即可。点 `_actors/actor_0001/actor_0001.jpg`（先用 "🎭 生成演员" 按钮生成至少 1 张）→ Reader 显示图片预览。
2. **若用 production build**（`make run-prod`）：需 `cd frontend && npm run build` 重建 + 拷贝到 `backend/static/`，然后重启 backend。

Severity: Low (UI render-only bug，no data corruption, no security impact). Surgical 5 行修改（Reader.tsx 2 行 + ImageRefView.tsx 3 行 + 1 import 换名）。`/api/file` 后端契约保留。

## Follow-up 015 — 2026-05-12 21:05:00
Source: user_input/follow_ups/015-20260512-210500-actors-bootstrap-folder.md
Summary: 修 follow-up 014 留下的 **chicken-and-egg UX bug** — 用户报告打开 webapp 后看不到 "🎭 生成演员" 按钮。**根因**：follow-up 014 的 `Sidebar.tsx` 把按钮 conditional 在 `dramaPathParts[1] === "_actors"` 行上，但 `ai_videos/_actors/` 目录只在 `ActorPool.generate_batch()` 第一行 `mkdir(parents=True, exist_ok=True)` 时 lazy 创建 —— 新用户从未触发过 endpoint，所以 TreeWalker `iterdir()` 看不到 `_actors/`，sidebar 不渲染该行，按钮永远不出现。**修复**：在 `api.py:create_app()` 实例化 `ActorPool` 后立即 eager `actor_pool.actors_dir().mkdir(parents=True, exist_ok=True)`。`exist_ok=True` 让已有 `_actors/` 安装零影响；`OSError` swallowed（与现有 `serve_static` 静默 mount-fail 模式一致 —— mkdir 失败不应阻止整个 webapp 起动）。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-12 21:05:00；Composed-from list 加 follow-up 015；header 摘要描述 chicken-and-egg 根因 + fix 一行；prior follow-up 014 line 移到 prior 列表。
- `projects/ai_video_management/backend/libs/api.py` — `create_app()` 内 `actor_pool = ActorPool(...)` 后插入 3 行：`try: actor_pool.actors_dir().mkdir(parents=True, exist_ok=True) except OSError: pass`，带 3 行 inline comment 标注 follow-up 015 + 解释 chicken-and-egg。无其他 api.py 改动。
- `ai_videos/_actors/` — 当前仓库新建空目录（boot-smoke 运行 `create_app()` 时自动创建；前端 sidebar 重启后即可看到该行 + "🎭 生成演员" 按钮）。

Verification (smoke checks):
- `make boot-smoke` (pytest test_boot_smoke.py): **7/7 通过**，含 follow-up 014 加的 5 个 endpoint registration 断言。
- `ls ai_videos/`: 输出含 `_actors`（新建）+ `mozun_chongsheng`（既有），与预期一致。
- TreeWalker 行为：空 `_actors/` directory 通过 `_walk_project` 走，生成 `{type:"directory", children:[], project_meta: null}` 节点 —— sub_type_lookup 对空 folder 自然返回 None (无 episodes/ 无 script.md/shotlist.md)。前端 `Sidebar.tsx` `isAiVideoChild && dramaPathParts[1] === "_actors"` 触发 `isActorsRoot=true` → 渲染 🎭 emoji icon + "🎭 生成演员" 按钮（开 ActorPoolGenerator modal）。

No conflicts found in:
- 所有 frontend 代码 (`Sidebar.tsx` / `Reader.tsx` / `ActorPoolGenerator.tsx` / `CastingView.tsx` / `api.ts` / `styles.css` 等) — 行为契约不变；唯一改动是后端启动时 eager mkdir，前端 fetch tree 时新增一个 directory node。
- `actor_pool.py` lazy mkdir 仍在 `generate_batch` 第一行 — 双重保险（启动时已 mkdir，但若 follow-up 014 行为被独立调用也 safe）。
- `casting.py` / `media_renamer.py` / `downloads_importer.py` / 其他 backend libs — 零影响。
- `final_specs/spec.md` FR-87 (`_actors` 非 drama 约定) — 行为不变；FR-87 只规定 `_actors` 在 sidebar 中的展示规则，不规定 何时创建。新加的 eager mkdir 是 implementation detail，与 FR 契约 orthogonal。
- `validation/*` — 测试场景 U3.15 / U3.16 用 tmpdir fixture 显式创建 actor folder，与生产 eager mkdir 行为正交，不需改动。

User next step:
1. **若 backend 还在跑（follow-up 012 默认 `--reload`）**：uvicorn 自动 detect `libs/api.py` 改动 + reload，下次浏览器刷新 `http://127.0.0.1:8766/` 即可看到 sidebar AI Videos 下出现 `_actors/` 行（🎭 emoji）+ "🎭 生成演员" 按钮。
2. **若 backend 没跑或用了 `--no-reload`**：`make run-backend` 重启即可。

Severity: Low. UI bootstrap bug in follow-up 014；3-line fix；零业务逻辑改动；不影响已生成的 actor / cast 数据；不影响已有 webapp 行为。

## Follow-up 014 — 2026-05-12 20:15:00
Source: user_input/follow_ups/014-20260512-201500-actor-face-pool-casting-ref-video.md
Summary: 新增 **actor face pool + casting workflow** 大功能。① 在 `ai_videos/_actors/` 维护 AI 生成的演员人脸池，每张 face 一个 `actor_NNNN/{actor_NNNN.jpg, actor_NNNN.md}` folder；sidecar md 记录六字段属性表（ethnicity / gender / age_range / look / style / notes）+ 生成 prompt + seed。② backend 调用 **pollinations.ai 免费 API**（`https://image.pollinations.ai/prompt/{prompt}?model=flux&seed=...`，无 API key，无 signup，MIT 协议）完全自动批量生成 + 落盘 —— 这是 backend **首次** 出站 HTTP，硬化：base URL 写死、prompt URL-encoded as path、30s/请求超时、5MB 响应 cap、批量上限 20、`follow_redirects=False` 防 SSRF。③ `ai_videos/{drama}/casting.md` 维护 role → actor_id 映射，新 `CastingView` 渲染表格 + 缩略图 + filter chips + 一键复制 ref-video prompt（即 rule #12.5 的 2.9s Seedance turntable schema + 演员图路径 inline）。④ ref-video 生成本身不进 webapp —— 用户拿 prompt + 演员图 在 Seedance 外部跑，下载后走已有 follow-up 009 import 流程落到 `characters/c{N}_*/c{N}_*.mp4`。`_actors/` 通过下划线前缀标记非-drama（sub_type 检测 None，sidebar 不渲染 drama-only rename 按钮，改渲染 "🎭 生成演员" 按钮打开 ActorPoolGenerator 模态）。

Research (决策依据):
- thispersondoesnotexist.com — 仅随机脸无属性控制 → 否决
- Generated.Photos API — ToS 禁 caching / downloading / standalone files → 否决（与本功能直接冲突）
- HuggingFace Inference (SDXL/FLUX) — 要 token + 1000/day 上限 + cold start → 否决
- pollinations.ai — 0 auth + MIT 协议 + 属性 in-prompt 自然 label + 100% free → 选中

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-12 20:15:00；Composed-from list 加 follow-up 014；header 摘要描述三段功能（pool / casting / ref-video）+ pollinations.ai 选型 + sandbox 出站 HTTP 边界 + `_actors/` 前缀约定；prior follow-up 013 line 移到 prior 列表。
- `specs/development/ai_video_management/user_input/follow_ups/014-*.md` — 追加 `## 决策 (interactive 收集)` 段：四问答案（pool 位置 / face 生成姿势 / casting 持久化 / ref-video 姿势）+ 六字段属性 schema + 文件 layout + 5 个新 endpoint 契约 + 3 个前端组件 + 安全 / 边界扩展 + 不在范围列表。
- `specs/development/ai_video_management/final_specs/spec.md` — FR-1 backend libs 列表加 `actor_pool.py` + `casting.py` (follow-up 014)；FR-9 注释扩展提及 follow-up 014 的 3 个 state-changing endpoint + 出站 HTTP；新增段 `### Actor pool + casting (follow-up 014)` 含 **FR-9f/g/h** (POST /api/actors/generate, POST/DELETE /api/casting/assign 完整契约)、**FR-10b/c** (GET /api/actors, GET /api/casting)、**FR-86** (六字段闭合 enum schema)、**FR-87** (`_actors` 非 drama 约定 + 下划线前缀 system folder)、**FR-88** (ActorPoolGenerator 模态)、**FR-89** (CastingView 两 mode + ref-video prompt 复制按钮)、**FR-90** (sidebar `_actors/` 🎭 图标)。
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — 新增 Scenario U3.15 (actor/generate 批量 + pollinations.ai 出站 + ID 自增 + invalid_attribute + count 边界 + per-image error 不 fail batch) + Scenario U3.16 (casting upsert / delete / GET /api/casting / GET /api/actors + 完整错误码面)；FR→Scenario 矩阵加 FR-9f→U3.15, FR-9g/h→U3.16, FR-10b/c→U3.16, FR-86→U3.15。
- `specs/development/ai_video_management/validation/security.md` — coverage matrix 加 FR-9f (`partial` 因首次出站 HTTP)、FR-9g/h (`partial` 因 Origin/Host gate 沿用现有 pattern，未扩展 GUARDED_ROUTES)、FR-86 (`covered`，闭合 schema 限制 prompt injection 面)；Open carve-outs #7 新增详述 `/api/actors/generate` 的 7 条出站硬化 + 3 类残余风险（外部依赖 / 无内容过滤 / localhost 触发外部 IO）+ casting 写也走相同 Origin gap。
- `projects/ai_video_management/backend/libs/actor_pool.py` (NEW) — `ActorPool` 类 + `ActorAttrs/ActorInfo/GenerateResult` dataclasses + 闭合 enum 常量 (ETHNICITY/GENDER/AGE_RANGE/LOOK/STYLE_OPTIONS) + `POLLINATIONS_BASE`/`MAX_BATCH_COUNT=20`/`MAX_RESPONSE_BYTES=5MB`/`DEFAULT_TIMEOUT_SECONDS=30`；`generate_batch(attrs, count)` 顺序循环：validate → mkdir `ai_videos/_actors/actor_NNNN/` → httpx GET pollinations.ai (stream, follow_redirects=False, max_bytes cap, timeout) → 写 jpg + 写 sidecar md（属性表 + prompt + seed）；per-image error → errors[] 不中断 batch + cleanup 空 folder；ID 通过扫描 max actor_NNNN+1 单调自增防覆盖；`_build_prompt` deterministic 英文 Seedream-style 拼接；`list_actors` 扫 _actors/ + 解析 sidecar md attrs；`actor_exists(id)` 给 casting 校验用；`fetcher` 参数允许测试注入 fake。
- `projects/ai_video_management/backend/libs/casting.py` (NEW) — `Casting` 类 + `CastEntry/CastingResult` dataclasses + `InvalidActorId/InvalidRole` 异常；`read(drama)` / `assign(drama, role, actor, notes)` / `unassign(drama, role)` 三入口；drama path validation 复用 `MediaRenamer.validate_drama`（同 invalid_drama_path / not_found 边界）；actor_id 校验通过 `ActorPool.actor_exists` 跨模块；assign 用 upsert 语义（同名 role 覆盖）；整文件 atomic temp-then-replace 重写，避免 markdown table line-level surgery 边界 case；表头固定为 `| role | actor_id | notes |`，empty notes 渲染为 `—`。
- `projects/ai_video_management/backend/libs/api.py` — module docstring "8 endpoints" → "13 endpoints"；imports 加 `ActorPool/ActorAttrs/InvalidAttribute/GenerationDirMissing` + `Casting/InvalidActorId/InvalidRole`；新 Pydantic models `GenerateActorsBody` / `CastingAssignBody` / `CastingUnassignBody`；instantiate `actor_pool = ActorPool(exposed, resolver)` + `casting = Casting(exposed, resolver, media_renamer, actor_pool)`；路由：`POST /api/actors/generate` (200 / 400 invalid_attribute / 500 actors_dir_unwritable / 405) + `GET /api/actors` (200 / 405) + `GET /api/casting` (200 / 400 invalid_drama_path / 404 not_found / 405) + `POST /api/casting/assign` (200 / 400 invalid_drama_path / 400 invalid_role / 400 invalid_actor_id / 404 not_found / 405) + `DELETE /api/casting/assign` (同 POST 错误码 + 404 role 不在 casting.md)。
- `projects/ai_video_management/backend/tests/test_boot_smoke.py` — `test_all_post_endpoints_registered` expected set 加 5 项：`("POST", "/api/actors/generate")` / `("GET", "/api/actors")` / `("POST", "/api/casting/assign")` / `("DELETE", "/api/casting/assign")` / `("GET", "/api/casting")`。`make boot-smoke` 7/7 通过。
- `projects/ai_video_management/frontend/src/api.ts` — 新增 types `ActorAttrs` / `ActorInfo` / `GenerateActorsRequest` / `GenerateActorsResult` / `CastEntry` / `CastingResult` + helpers `generateActors` / `listActors` / `fetchCasting` / `castingAssign` / `castingUnassign` + 闭合 enum 常量 export `ATTR_OPTIONS` 给前端下拉 + filter chips 使用。
- `projects/ai_video_management/frontend/src/components/ActorPoolGenerator.tsx` (NEW) — 模态对话框组件：六字段 select + count number input (1–20) + notes textarea + 提交按钮；in-flight disable + 进度文本；toast 显示 `已生成 N / 失败 E`；成功后 `onGenerated()` 触发 tree refresh。
- `projects/ai_video_management/frontend/src/components/CastingView.tsx` (NEW) — Reader 在 path 命中 `^ai_videos/[^/]+/casting\.md$` 时 dispatch 的渲染组件。两 mode：**read** = 渲染当前 casting 表（role / actor 缩略图 / 属性 / notes / row actions），row actions 含 `▶ 复制 ref-video prompt`（拼 rule #12.5 schema + actor.image_path）+ `🗑 取消`；**assign** = 角色名 input + filter chips（按 5 个属性筛 actor）+ actor 缩略图网格 → 点击 tile 调 `POST /api/casting/assign`。Toast announce 操作结果；onChange 回调让 Reader 刷新 sibling tree。
- `projects/ai_video_management/frontend/src/components/Reader.tsx` — import `CastingView`；新增 `isCasting` 检测（`/^ai_videos\/[^/]+\/casting\.md$/`）；render dispatch 在 `isImageRef` 之前优先匹配 `isCasting` → `<CastingView castingPath={path} onChange={onSaved} />`；Editor 按钮在 `isCasting` 时也隐藏（与 isShotPair / isImageRef 一致，casting 走自己的 mutation 路径）。
- `projects/ai_video_management/frontend/src/components/Sidebar.tsx` — import `ActorPoolGenerator`；新增 `generatorOpen` state；in render loop 新增 `isAiVideoChild` / `isSystemFolder` (name 起 `_`) / `isDrama` (重定义 = isAiVideoChild && !isSystemFolder) / `isActorsRoot` (`_actors`) 四个布尔；drama-row "📥 导入 + 重命名" 按钮现在排除 system folder（`_actors` 等不显示）；`_actors/` row 显示 🎭 emoji icon + "🎭 生成演员" 按钮（开 modal）；底部挂 `<ActorPoolGenerator>` 组件，关闭后若有生成则触发 `onTreeReload`。
- `projects/ai_video_management/frontend/src/styles.css` — 新增 modal 样式（`.modal-backdrop` / `.modal-panel` / `.modal-header` / `.modal-body` / `.modal-footer` / `.modal-toast(-ok/-err)` / `.form-grid` / `.form-field`）+ casting 样式（`.casting-view` / `.casting-header(-actions)` / `.casting-add-btn` / `.casting-toast(-ok/-err/-dismiss)` / `.casting-table` + 表头/行/缩略图/role/actor-cell/actor-id/missing/attrs/row-actions / `.casting-assign-pane(-form)` / `.casting-filter-chips` / `.casting-actor-grid` + tile/id/attrs）。全部 light-theme compliant，复用既有 CSS var `--accent` / `--border` / `--tint-a(-border)` / `--error-bg/text/border` / `--text(-muted)` / `--bg(-toolbar)`，无新增色板。

Verification (smoke checks):
- Python imports compile clean: `from libs.actor_pool import ActorPool, ActorAttrs` + `from libs.casting import Casting` + `from libs.api import create_app` 无异常。
- ActorPool smoke test（fake fetcher 返回 stub JPEG，tmpdir 模拟仓库）：3-batch 生成 ID 升序 actor_0001..0003，磁盘 jpg + md 都落盘；二次 batch 接 actor_0004..0005 单调自增；invalid `ethnicity="klingon"` → `InvalidAttribute`；count=21 → `InvalidAttribute`；`list_actors()` 解析回六字段属性表 + 跳过缺图/缺 md 的 folder。
- Casting smoke test（同 tmpdir + ActorPool 先生成 2 个 actor）：assign 创建 casting.md + 1 row；同 role 第二次 assign 覆盖；不同 role 第二次 assign 共 2 row；read 回正确顺序；unassign 减 1；invalid actor_0009 → `InvalidActorId`；path "ai_videos/" → `InvalidDramaPath`；role 含 `|` → `InvalidRole`。
- `make boot-smoke` (pytest test_boot_smoke.py): **7/7 通过**，含新加的 5 个 endpoint registration 断言。
- Frontend `npx tsc --noEmit`: 无新错误（仅 vite.config.ts 两个 pre-existing 错误，与本 follow-up 无关；与 follow-up 008-013 verification log 一致）。

Deferred (not in this follow-up):
- backend pytest for `actor_pool.py` + `casting.py` + 5 个新 endpoint 路由（与 follow-ups 005-013 一致推迟到批量补测；test_boot_smoke 已含 endpoint registration 断言作 baseline）。fixture 需要 monkey-patch `ActorPool._fetcher` 注入 fake JPEG bytes，以及 tmp_path drama scaffold。
- e2e Playwright 验证 ActorPoolGenerator 模态 + CastingView read/assign 两 mode + sidebar "🎭 生成演员" 按钮（同上推迟）。
- pool 内 actor 删除 endpoint (v1 用文件系统手工 rm；后续可加 `DELETE /api/actors/{id}`)。
- regenerate-same-attrs 功能（v1 不复用同 prompt + seed，每次 batch 都是新 seed）。
- 跨 drama casting clone / template（每 drama 独立 casting.md）。
- Origin/Host gate 扩展到新 POST/DELETE 端点（与现有 rename / archive / import 一致沿用现有 pattern；已知 security gap，留给独立 follow-up）。
- Actor attribute auto-classification (v1 attrs 来自用户填的表单 → 100% 准确，无 ML 推断需要)。
- ActorGalleryView 专用浏览模式（v1 简化：sidebar 展开 _actors/ 看 actor folders，每个 actor_NNNN.md 用现有 markdown view + SiblingMedia 渲染图）。

Severity: Medium-Low. Additive feature, no breaking changes to existing endpoints. 新 sandbox 边界（首次出站 HTTP）已通过 7 层硬化 + 残余风险记录在 security.md carve-out #7；用户决策"pollinations.ai 无 auth"避免引入 secret-handling；用户决策"ref-video 生成本身不进 webapp"保持 webapp 不直接调 Kling/Seedance API 的既有 invariant 不变。

No conflicts found in:
- `agent_refs/project/ai_video.md` rule #12.5 (character turntable 2.9s) — 本 follow-up 把 actor face + 这条规则的 prompt schema **组合** 后 expose 给用户，规则本身不动。
- `agent_refs/project/ai_video.md` rule #12.10 (scene reference 3.9s) — 与本 follow-up 正交。
- `projects/spec_driven/` — 完全不受影响。
- 其他 backend libs (`media_renamer.py` / `media_archiver.py` / `downloads_importer.py` / `file_reader.py` / `file_writer.py` / `api_security.py` / `exposed_tree.py` / `tree_walker.py` / `sub_type_lookup.py`) — 不动；`sub_type_lookup` 对 `_actors/` 自然返回 `None` (无 episodes/ 无 script.md/shotlist.md)；`exposed_tree.is_inside` 已 admit `ai_videos/**` 故 `_actors/` 自然 in sandbox。
- 其他前端组件 (`App.tsx` / `Editor.tsx` / `ShotPairView.tsx` / `ShotlistTableView.tsx` / `ImageRefView.tsx` / `SiblingMedia.tsx` / `Breadcrumb.tsx` / `BrokenLink.tsx` / `Home.tsx` / `ParseFallback.tsx`) — 保持不动。

## Follow-up 013 — 2026-05-12
Source: user_input/follow_ups/013-20260511-125029-batch-trim-character-mp4-to-2.9s.md
Summary: **一次性 data-op，webapp 代码零改动**。批量把 `ai_videos/mozun_chongsheng/characters/c*/c*.mp4` 19 个 character turntable mp4 in-place re-encode trim 到 ≤ 2.9s，对齐 rule #12.5 v4 的 Seedance reference ≤2.9s 上传约束 — 用户手工渲染的实际时长 3.04s–15.07s 不等，现已统一。ffmpeg 通过 `pip install --user imageio-ffmpeg` 拉的 v7.1 bundled binary（不污染系统 PATH）；每文件 `-t 2.9 -c:v libx264 -preset fast -crf 18 -c:a aac -movflags +faststart` 写 `<src>.trim.mp4` 临时文件 → atomic `os.replace` 覆盖原文件。结果：11 个文件 = 精确 2.9s，8 个文件 = 2.92s（mp4 packet-boundary 不可消的 ~20ms 过冲；远低于 3s 实际 Seedance 上限）。19/19 成功，无遗留 `.trim.mp4` 临时文件，无 stderr 错误。Hook 标 ai_video_management 项目，artifact 实际改动登记于 `specs/ai_video/mozun_chongsheng/changelog.md` cross-ref 条目。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-12；Composed-from list 加 follow-up 013；header 摘要描述 19 文件 in-place re-encode 2.9s + 11+8 分布 + ffmpeg 来源；prior follow-up 012 line 移到 prior 列表。
- `ai_videos/mozun_chongsheng/characters/c*/c*.mp4` (19 文件) — in-place re-encoded H.264 / AAC 2.9s（详见下表）；mtime 全部跳到 2026-05-12 19:51；文件 size 大幅下降（原 3-15s 的源 vs 现统一 2.9s 后 size 比例缩放）。
- `.audit/trim_chars_2.9s.py` (NEW) — 复用脚本，imageio-ffmpeg locate ffmpeg binary + ffmpeg metadata 解析时长 + atomic temp-rename + JSON summary 输出。下次想再 trim character mp4（或其他 drama 的 character）直接改 `ROOT` 路径运行即可。
- `.audit/trim_chars_2.9s_result.json` (NEW) — 19 文件 before/after duration + encode 时长 JSON summary。
- `specs/ai_video/mozun_chongsheng/changelog.md` — 追加 cross-ref 条目记录 19 mp4 的 byte-level patch + 时长 before/after 表。

Before / after 时长（all 19）:

| 文件 | before | after |
|---|---|---|
| c10_司空玄/c10_司空玄1.mp4 | 2.9s | 2.9s |
| c10_司空玄/c10_司空玄2.mp4 | 3.04s | 2.92s |
| c1_沧冥/c1_沧冥1.mp4 | 12.04s | 2.92s |
| c1_沧冥/c1_沧冥2.mp4 | 15.07s | 2.9s |
| c1_沧冥/c1_沧冥3.mp4 | 3.04s | 2.92s |
| c1_沧冥/c1_沧冥4.mp4 | 4.06s | 2.9s |
| c1_沧冥/c1_沧冥5.mp4 | 4.04s | 2.92s |
| c3_苏璃月/c3_苏璃月1.mp4 | 15.07s | 2.9s |
| c3_苏璃月/c3_苏璃月2.mp4 | 15.07s | 2.9s |
| c3_苏璃月/c3_苏璃月3.mp4 | 12.04s | 2.92s |
| c3_苏璃月/c3_苏璃月4.mp4 | 15.07s | 2.9s |
| c4_柳红袖/c4_柳红袖.mp4 | 15.07s | 2.9s |
| c5_苓夭夭/c5_苓夭夭.mp4 | 12.04s | 2.92s |
| c6_白月清/c6_白月清.mp4 | 12.04s | 2.92s |
| c7_赵焚天/c7_赵焚天1.mp4 | 4.06s | 2.9s |
| c7_赵焚天/c7_赵焚天2.mp4 | 4.06s | 2.9s |
| c7_赵焚天/c7_赵焚天3.mp4 | 3.04s | 2.92s |
| c8_方鼎元/c8_方鼎元.mp4 | 4.06s | 2.9s |
| c9_韩夺心/c9_韩夺心.mp4 | 4.06s | 2.9s |

No conflicts found in:
- `projects/ai_video_management/` (webapp 代码 — 不 parse 时长字段；trimmed mp4 仍是合法 H.264/AAC，前端 `<video>` tag 照常播放)
- `agent_refs/project/ai_video.md` rule #12.5（character turntable 锁 2.9s — 本 op 是把 artifact 主动对齐到现有规则，无规则改动）
- rule #12.10 v2 (scene reference 3.9s) — 不在范围（scene mp4 不动）
- `ai_videos/mozun_chongsheng/scenes/` 任何 mp4（明确排除；rule 不同）
- `episodes/ep*/prompts/shot*/shot*.md` shot prompt — `{ref_c{N}_*}` placeholder 引用按文件名不按时长，path 不变；仅 mtime + 时长变了，shot prompt 文件本身不需要 patch
- `characters/c*/c*_seedream.md` Seedream 立绘 prompt — 不动
- `interview/qa.md` / `findings/` / `final_specs/spec.md` / `validation/*` — webapp scope / 数据-op 都不冲突

Operational notes:
- 之前用户报告的 `导入失败: Method Not Allowed`（follow-up 012）必须先 restart backend（`make run-backend` 现 default `--reload`，新 session 起就生效）— 否则点 `📥 导入 + 重命名` 按钮仍走旧进程。本 follow-up 与 012 是同一会话内独立 op，互不影响。
- `imageio-ffmpeg` 安装位置 `%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.13_*\LocalCache\local-packages\Python313\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe`；调用方式 `python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"` 给出绝对路径。后续如果要支持「webapp 内一键 trim」，backend 加 `imageio-ffmpeg` 依赖 + 新 endpoint，但本 follow-up 不引入这层（用户原 prompt 是 one-shot ask，没要功能化）。

## Follow-up 012 — 2026-05-11 12:28:33
Source: user_input/follow_ups/012-20260511-122833-backend-autoreload-stale-routes.md
Summary: 修复用户报告的 `导入失败: Method Not Allowed` bug — 根因诊断为 stale-backend：`backend/main.py` 用 `uvicorn.run(app, ...)` app-instance 启动，**不开 `--reload`**；follow-up 009 加的 `POST /api/import-from-downloads` 在代码层 register 正确（TestClient 命中 → 200），但用户的 Python 进程是 follow-up 009 之前启动的旧实例，浏览器 POST 撞 fastapi 默认 405 fallback（体 `{"detail":"Method Not Allowed"}`，被前端 `readJson` 当作 string detail 塞进 toast，渲染为带空格 Title Case 错误串）。修复：让 `make run-backend` 默认开 uvicorn `--reload`，新 endpoint 即时生效，dev workflow 不再要求手动重启。Immediate workaround：Ctrl+C → `make run-backend` 重启即可点按钮成功。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-11 12:28:33；Composed-from list 加 follow-up 012；header 摘要描述根因 + 修复 + workaround；prior follow-up 011 line 移到 prior 列表。
- `projects/ai_video_management/backend/main.py` — 加 `--no-reload` argparse flag（default 不传 = reload 开）；reload 分支调 `uvicorn.run("libs.asgi:app", host=..., port=..., reload=True, reload_dirs=["libs"])` —— uvicorn reload 模式硬约束必须传 import-string 而非 app instance；no-reload 分支保持原 `create_app(...)` + `uvicorn.run(app, ...)` 行为不变，给 `make run-prod` 之后想跑长任务用。
- `projects/ai_video_management/backend/libs/asgi.py` (NEW) — `libs.asgi:app` 入口 module；闭包 `create_app(RepoRoot.find(), BoundOrigin(HOST=127.0.0.1, PORT=8766), serve_static=True)`；dev 模式下 `backend/static/` 为空（只有 .gitkeep），mount 不报错，SPA 由 Vite 5174 提供。
- `projects/ai_video_management/backend/tests/test_boot_smoke.py` — 新加 `test_all_post_endpoints_registered`：枚举 `app.routes` 的 `(method, path)` pair，断言 `{("POST","/api/rename-media"), ("POST","/api/archive-media"), ("POST","/api/unarchive-media"), ("POST","/api/import-from-downloads")}` 全部在内；下次有人 rename / typo / 漏 register 这四个 endpoint 之一，boot-smoke 立刻红，避免相同 stale-routes UX 退化。已 verify `make boot-smoke` 7/7 通过。

No conflicts found in:
- `Makefile` — `run-backend` target 不动（仍是 `python main.py`，新 default `--reload` 自动启用）
- `frontend/src/api.ts` `readJson` — string vs object detail 解析路径不变；stale-backend 不再发生后，405 体只会来自我们自己结构化 catch-all (`{detail:{kind:"method_not_allowed"}}`)，toast 串变 lowercase snake_case
- `OriginHostMiddleware.GUARDED_ROUTES` — 与本 bug 无关；POST endpoint 加 Origin/Host gate 留给后续 follow-up
- `final_specs/spec.md` / `validation/*` / `interview/qa.md` / `findings/` — 行为契约不变，只是部署 / 进程管理姿势改了
- 其它 backend libs / frontend 组件

## Follow-up 011 — 2026-05-11 20:25:46
Source: user_input/follow_ups/011-20260511-202546-batch-archive-media-multi-select.md
Summary: 在 SiblingMedia grid 加 multi-select + 批量 Archive / Unarchive — 每个 media tile 左上角 always-visible checkbox；per-section toolbar (`Select all` / `Clear` / `Archive Selected (N)` 或 `Unarchive Selected (N)`)；批量串行调用已存在的 `POST /api/archive-media` / `POST /api/unarchive-media`（无新 backend endpoint）；continue-on-error 聚合成功/失败 announce 到 `#aria-live-toast`；per-tile 单文件按钮保留兼容，批量 in-flight 期间整段 disabled。Selection state 在 active / archived 两 section 独立。范围 = SiblingMedia 已经覆盖的所有 folder（character / scene / shot / episode / 任何含 media 的 `.md` 同 folder）— 无需 per-folder 分别加。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated bumped to 2026-05-11 20:25:46；Composed-from list 加 follow-up 011；header 摘要描述 multi-select + 批量按钮 + 无新 backend endpoint + continue-on-error；prior follow-up 010 line 移到 prior 列表。
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9 注释扩展提及 follow-up 011 的批量层是 PURELY FRONTEND，循环已存在的 FR-9c / FR-9d endpoint，无新 endpoint。
- `projects/ai_video_management/frontend/src/components/SiblingMedia.tsx` — `MediaTile` 加 `selected` / `onToggleSelect` / `selectionBusy` props + 左上角 corner checkbox；`SiblingMedia` 新增两组独立 selection state (`selectedActive`, `selectedArchived`)、整段 `busy` 锁、批量 `handleBatchArchive` / `handleBatchUnarchive` 串行循环 + continue-on-error 聚合 announce；per-section `Toolbar` 子组件含 `Select all` / `Clear` / `Archive Selected (N)` (active) 或 `Unarchive Selected (N)` (archived)；per-tile 单文件按钮保留 + 共享 busy disable。
- `projects/ai_video_management/frontend/src/styles.css` — 新增 `.sibling-media-toolbar` (flex row, padding, light-theme bg) + `.sibling-media-toolbar button` 颜色 / disabled 灰阶 + `.sibling-media-item input.tile-checkbox` 左上角 absolute + 半透明白底 + scale 1.3。

No conflicts found in:
- backend `media_archiver.py` / `api.py`（批量纯前端循环已存在 endpoint，无 backend 改动）
- `interview/qa.md` / `findings/` / `validation/*`（webapp scope 未变；批量只是 UI 层增强已有的 FR-9c / FR-9d 功能）
- 其它 frontend 组件 (`Reader.tsx`, `api.ts` 等保持不动 — `onChange` 回调链已支撑 tree refresh)

## Follow-up 010 — 2026-05-11 12:04:54
Source: user_input/follow_ups/010-20260511-120454-scene-ref-video-3.9s-all-angles.md
Summary: **Cross-project rule change — ai_video_management webapp 本身不受影响**。把 ai_video pipeline 的 scene reference video prompt 时长上限 2.9s → **3.9s**；schema 从原"全景定场 + 中景横移 + 长焦推近"三段重写为"**正面建场 + 水平 360° 环绕 + 垂直三视角 + 中景横移 + 长焦特写**"**五段 all-angle 序列**（起手必须 front view）；prompt body 显式加 `音频: 无（视频纯视觉 reference）` 字段并把 byte-identical 字段集合 7→8。目标：给 Seedance 等下游 video 模型最大密度场景 reference，让它据此生成真正 shot 视频。Character turntable rule #12.5 保持 2.9s 不动。Hook 把本 prompt 归属到 ai_video_management 项目；用户在三选题中再次确认 follow-up 持久化位置 — 故登记于此。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-11 12:04:54；Composed-from 加 follow-up 010；header 摘要描述 3.9s + 五段 all-angle + visuals-only + 跨项目改动范围；prior follow-up 009 line 移到 prior 列表。
- `.claude/agent_refs/project/ai_video.md` — rule #12.10 全段重写（"为什么 2.9s 硬上限" → "为什么 3.9s 硬上限"；schema header / 用法 / body header / timed beats / 节奏 / 时长 / 负向 全部由 2.9s 改 3.9s；schema body 从三段改五段；新增 `音频: 无` 行；byte-identical 字段集 7→8；origin 行追加 follow-up 010 来源）。
- `ai_videos/mozun_chongsheng/scenes/s1_长阶顶/s1_长阶顶.md` 至 `s9_识海/s9_识海.md`（9 文件） — 「场景 reference video prompt — Seedance / Sora / Veo / Runway Gen-3 / Kling」段全段重写：header `2.9s` → `3.9s`；用法说明 `≤ 2.9s 硬上限` → `≤ 3.9s 硬上限`；body header 描述更新为 `正面建场 + 水平 360° 环绕 + 垂直三视角 + 中景横移 + 长焦特写`；动作 timed beats 五段（0-0.8s 正面建场 / 0.8-1.7s 水平 360° 环绕 / 1.7-2.5s 垂直三视角 / 2.5-3.3s 中景横移 / 3.3-3.9s 长焦特写定格）；节奏行 `极快（2.9s 内...）` → `极快（3.9s 内...全角度覆盖）`；时长行 `2.9s` → `3.9s`；新增 `音频: 无（视频纯视觉 reference，不要 BGM / 音效 / 旁白 / 环境音）` 行；负向 `不要 超过 2.9s` → `不要 超过 3.9s`，并加 `不要 任何音频 / BGM / 音效 / 旁白 / 环境音`。
- `specs/ai_video/mozun_chongsheng/changelog.md` — 追加 cross-ref 条目指向本 follow-up，记录 9 个 scene .md 被 patch。

No conflicts found in:
- `projects/ai_video_management/` (webapp 代码 — 不解析 .md 时长字段，schema 改动只是字节差)
- `specs/development/ai_video_management/interview/qa.md` / `findings/` / `final_specs/spec.md` / `validation/*` (webapp scope 未变)
- `.claude/agent_refs/project/ai_video.md` rule #12.5 (character turntable，按用户确认保持 2.9s)
- 其它 `ai_videos/` 项目（目前仅 mozun_chongsheng 一个）

## Follow-up 009 — 2026-05-11 19:56:38
Source: user_input/follow_ups/009-20260511-195638-import-from-downloads-classifier.md
Summary: 把 drama-row "🏷 重命名" 按钮升级为 "📥 导入 + 重命名" 一键流程 — 后端扫描用户 OS 的 Downloads folder（过去 7 天 by mtime 的 image/video 文件，只 immediate children），按文件名 substring-match drama 下 `characters/c*/` + `scenes/s*/` + `episodes/ep*/prompts/shot*/` folder 名（含下划线-split tokens + shot 额外的 epNN_shotNN / epNN tokens），longest-match 胜（tie shot > scene > character）；无匹配 → `ai_videos/{drama}/not_matched/`；移完后调 `MediaRenamer.rename_drama()` 并 exclude `not_matched/`，保留原始文件名供用户人肉 triage。新增 `POST /api/import-from-downloads` endpoint。**首次允许后端读取 EXPOSED_TREE 外路径** — 源端硬化：只读 Downloads immediate children + 扩展名白名单 + mtime 窗 + 拒 symlink + basename 正则 + 长度上限。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated bumped to 2026-05-11 19:56:38；Composed-from list 加 follow-up 009；header 摘要描述 import+rename 一键流程 + sandbox 外读取的硬化要点；prior follow-up 008 line 移到 prior 列表。
- `specs/development/ai_video_management/final_specs/spec.md` — FR-1 backend libs 列表加 `downloads_importer.py` (follow-up 009)；FR-9 注释扩展提及 follow-up 009 的 import endpoint + sandbox 外读取；新增 FR-9e 描述 `POST /api/import-from-downloads` 完整契约（drama-scope body / Downloads 源端硬化 / 分类器算法 / target_exists 处理 / chain 调 MediaRenamer.rename_drama exclude not_matched / 返回 schema / 错误码表）。
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — FR→Scenario 矩阵加 FR-9e → U3.14 行；新增 Scenario U3.14 覆盖 7-fixture 文件分类正确性（character/scene/shot/unmatched）+ window 静默跳过 + 非 media 跳过 + symlink 跳过 + 二次空运行 + 错误码面 (400/404/405/500) + Origin/Host gate。
- `specs/development/ai_video_management/validation/security.md` — coverage matrix 加 FR-9b / FR-9c / FR-9d / FR-9e 行（FR-9e 标记 `partial` 因为新引入 sandbox 边界）；Open carve-outs 加 #6 详述 `/api/import-from-downloads` 是首个外读端点，列出 6 条硬化 + 2 类残余风险（destination collision 由 target_exists 兜底；任意名匹配靠 not_matched 兜底），明确若需更严格则后续 follow-up 加 per-file 用户确认。
- `projects/ai_video_management/backend/libs/downloads_importer.py` (NEW) — `DownloadsImporter` 类 + `ImportResult` dataclass + `_Candidate` 内部 dataclass + `DownloadsDirMissing` 异常；`import_drama(rel)` 入口 validate drama 路径（复用 `MediaRenamer.validate_drama`）→ 验证 Downloads 目录存在 → `_collect_candidates(drama)` 拉取 characters/scenes/shots 三类 candidate folder 及其 lowercase tokens → `_iter_downloads(cutoff)` 扫 Downloads immediate children 过滤 ext/mtime/symlink → 每文件 basename 形状校验 + `_classify` 选目标 → `dst.mkdir(parents=True, exist_ok=True)` + `shutil.move` → 目标已存在 / mkdir 失败 / move 失败均加入 errors[] 不中断 batch → 最后调 `MediaRenamer.rename_drama(rel, excluded_folder_names=frozenset({"not_matched"}))` 把 rename_result 塞入 ImportResult；`_classify` 用 tuple key 排序选最佳 (score, kind_priority, lex-tiebreak)；`_tokens(folder_name)` 抽 primary + 下划线-split tokens (length ≥ 2)，去重保序；`_is_safe_basename` regex + 长度检查；`_display_src` 把 Downloads 路径渲染为 `~/<rel>` 避免泄露 home；环境变量 `AI_VIDEO_MGMT_DOWNLOADS_DIR` 可覆盖 Downloads 默认路径以便测试；`NOT_MATCHED_DIR_NAME = "not_matched"` constant 公开导出。
- `projects/ai_video_management/backend/libs/media_renamer.py` — `rename_drama()` 签名加 optional kwarg `excluded_folder_names: frozenset[str] | None = None`（None / 空集时行为完全不变 — 现有 /api/rename-media 调用方零影响）；非空时 merge 进 `self._exposed.excluded_dirs()` 形成更大的 excluded set 传入 `_iter_folders`；新增 public method `validate_drama(rel)` 作 `_validate_drama` 的 thin wrapper，给 DownloadsImporter 用避免跨模块调私有。
- `projects/ai_video_management/backend/libs/api.py` — module docstring "7 endpoints" → "8 endpoints"；imports 加 `DownloadsImporter` + `DownloadsDirMissing`；`ImportFromDownloadsBody` Pydantic model；`downloads_importer = DownloadsImporter(exposed, resolver, media_renamer)` 实例化；`POST /api/import-from-downloads` 路由 (200 / 400 invalid_drama_path / 404 not_found / 500 downloads_dir_missing) + 405 method-not-allowed guard。
- `projects/ai_video_management/frontend/src/api.ts` — 新增 `ImportFromDownloadsResult` type (含 nested `rename: RenameMediaResult`) + `importFromDownloads(path)` POST helper。`renameMedia` helper 保留（不再被 Sidebar 调，但保留以兼容、便测试）。
- `projects/ai_video_management/frontend/src/components/Sidebar.tsx` — import 把 `renameMedia` 替换为 `importFromDownloads`；`onRenameClick` 改调 `importFromDownloads` + toast text 改 `已导入 N / 未分类 M / 已重命名 K / 失败 E`；button label "🏷 重命名" → "📥 导入 + 重命名"，aria-label / title 同步更新描述新行为（"从 Downloads 按文件名分类导入近 7 天的图片/视频，并按 parent folder 重命名"）。

Verification (smoke checks):
- Python imports compile clean: `from libs.downloads_importer import DownloadsImporter, NOT_MATCHED_DIR_NAME, DownloadsDirMissing` + `from libs.api import create_app` 无异常。
- 分类器 smoke test（ASCII fixture，7 sample filenames）：`kling_c1_aaa_test.mp4` → c1_aaa (character) ✓；`jimeng-yewuchen-pic.png` → c2_yewuchen (character) ✓；`ep01_shot01_kling.mp4` → shot01 (shot) ✓（通过 ep01_shot01 长 token 命中）；`random_file.mp4` → not_matched ✓；`shot03_v2.mp4` → shot03 (shot) ✓；`shandao_seedance.mp4` → s7_shandao (scene) ✓；`just_c1.mp4` → c1_aaa (character) ✓（短 token 命中也算）。
- Frontend `npx tsc --noEmit` 无新错误（仅 vite.config.ts 两个 pre-existing 错误，与本 follow-up 无关）。

Deferred (not in this follow-up):
- backend pytest under `backend/tests/` for `downloads_importer.py` + `api.py /api/import-from-downloads` 路由（与 follow-ups 005-008 一致推迟到批量补测）。fixture 需要 `AI_VIDEO_MGMT_DOWNLOADS_DIR` env override + tmp_path drama scaffold。
- e2e Playwright 验证按钮 + toast 行为（同上推迟）。
- dry-run 预览模式 (`?dry_run=true`) 允许用户在 move 前看到将分到何处。
- 单文件 import / 多选 import（v1 batch only）。
- 跨 drama 比对（v1 只匹配点击的 drama；如果文件名包含其他 drama 的 character/scene 名，会被分到 not_matched 而非其他 drama）。
- 防 collision 自动重命名（v1 target_exists 直接报 error；后续可加 `<basename>_1.mp4` 自动 suffix）。

Severity: Medium-Low. Additive endpoint, no breaking changes. Security 边界扩展（首次读 sandbox 外）已通过 6 层硬化 + 残余风险记录在 security.md carve-out #6；用户决策"`excluded_folder_names={"not_matched"}`"保证未分类文件的原始 Downloads 文件名留存。其他 endpoint 零影响。

## Follow-up 008 — 2026-05-10 20:18:26
Source: user_input/follow_ups/008-20260510-201826-archive-unarchive-media.md
Summary: 在 SiblingMedia 每个 media tile 上加一个 inline "📦 Archive" / "↺ Unarchive" 按钮，点击把单个 image/video 文件移动到（或移出）同 folder 下的 `archive/` 子目录。新增两个后端 endpoint `POST /api/archive-media` + `POST /api/unarchive-media`；archive/ 在 tree sidebar 作为常规 folder 显示（不加进 `_EXCLUDED_DIRS`）；unarchive 后若 archive/ 已空自动 rmdir；rename-media batch 不跳 archive/（archive/ 内文件按 parent name "archive" 也参与 rename — 用户决策）。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated bumped to 2026-05-10 20:18:26；Composed-from list 加 follow-up 008；header 摘要描述新功能；prior follow-up 007 line 移到 prior 列表。
- `specs/development/ai_video_management/final_specs/spec.md` — FR-1 backend libs 列表加 `media_archiver.py` (follow-up 008)；FR-9 注释扩展提及 follow-up 008 的 archive endpoints；新增 FR-9c (`POST /api/archive-media`) 与 FR-9d (`POST /api/unarchive-media`) 描述 body / response / error surface (`400 invalid_path/extension_not_allowed/already_archived/not_in_archive`、`404 not_found`、`409 target_exists`、`500 move_failed`)；FR-9b 注释提示 archive/ 不被 rename-media 排除。
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — FR→Scenario 矩阵加 FR-9b (U3.12) / FR-9c (U3.13) / FR-9d (U3.13) 行；新增 Scenario U3.12 (rename-media，补 follow-up 007 缺漏) + U3.13 (archive/unarchive-media 完整错误码面 + Origin/Host gate)。
- `projects/ai_video_management/backend/libs/media_archiver.py` (NEW) — `MediaArchiver` 类 + `MoveResult` dataclass + 异常 `InvalidPath/NotFound/NotMedia/AlreadyArchived/NotInArchive/TargetExists/MoveFailed`；`archive(rel)` 入口 validate path（在 sandbox 内 + ext ∈ MEDIA_EXTENSIONS + 文件存在 + 不是 symlink + parent 不是 archive）→ mkdir archive/（exist_ok=True）→ 检查目标不存在 → atomic `Path.rename()`；`unarchive(rel)` 入口 validate path + 要求 parent.name == "archive" → 检查目标 parent dir 不存在同名 → atomic rename → 若 archive/ 空则 rmdir（best-effort）；`ARCHIVE_DIR_NAME = "archive"` constant 公开导出。
- `projects/ai_video_management/backend/libs/api.py` — module docstring "5 endpoints" → "7 endpoints"；imports 加 `media_archiver` 全部异常 + `MediaArchiver`（用 `as ArchiveInvalidPath/ArchiveNotFound` 别名避免与 media_renamer 同名异常冲突）；`ArchiveMediaBody` Pydantic model；`media_archiver = MediaArchiver(exposed, resolver)` 实例化；`POST /api/archive-media` 路由 (200 / 400 invalid_path/extension_not_allowed/already_archived / 404 not_found / 409 target_exists / 500 move_failed) + `POST /api/unarchive-media` 路由 (同 400 套 + `not_in_archive` / 404 / 409 / 500)；两个端点各自的 GET/PUT/PATCH/DELETE 405 method-not-allowed guard。
- `projects/ai_video_management/frontend/src/api.ts` — 新增 `ArchiveMediaResult` type + `archiveMedia(path)` + `unarchiveMedia(path)` POST helpers，签名 `Promise<{from: string, to: string}>`。
- `projects/ai_video_management/frontend/src/components/SiblingMedia.tsx` — Props 加 `onChange?: () => void`；新 helper `findArchivedMedia` 扫 `<currentParent>/archive/` 内 media；新 `MediaTile` 子组件渲染 figure + per-tile "📦 Archive" / "↺ Unarchive" button（in-flight disabled、`aria-label`、tooltip）；section 内拆 "📁 Folder media" + "📦 Archived · 已归档" 两个 grid；archive / unarchive 成功后 `announce()` 写 `#aria-live-toast` 并调 `onChange`；错误时 announce 错误 kind。
- `projects/ai_video_management/frontend/src/components/Reader.tsx` — `<SiblingMedia>` 透传 `onChange={onSaved}`（命名复用：archive/unarchive 也是 tree mutation → 触发 refreshKey bump）。
- `projects/ai_video_management/frontend/src/styles.css` — 新增 `.sibling-media-archive-btn` (右下角浮动 inline button，11px pill 风格 + hover/disabled 状态) + `.sibling-media-item.is-archived` (opacity 0.7 + 灰阶 filter 0.5) 视觉降权区分已归档 tile。

Verification (smoke checks):
- Python imports compile clean: `from libs.media_archiver import MediaArchiver, ARCHIVE_DIR_NAME` + `from libs.api import create_app` 无异常。
- Frontend `npx tsc --noEmit` 无新错误（仅 vite.config.ts 两个 pre-existing 错误，与本 follow-up 无关）。
- 两个 endpoints 405 guard 与已有 `/api/rename-media` 形状一致。

Deferred (not in this follow-up):
- backend pytest under `backend/tests/` for `media_archiver.py` + `api.py /api/{archive,unarchive}-media` 路由（与 follow-up 005/006/007 一致推迟到批量补测）。
- e2e Playwright 验证 per-tile button 行为（同上推迟）。
- 批量归档 / 多选归档（v1 per-file，单独 follow-up 触发批量）。
- archive/ 嵌套层级限制（v1 不阻止 `archive/archive/`，只用 immediate parent.name 判定）。

Severity: Low — additive feature, no breaking changes, no schema changes to existing endpoints. archive/ 与 rename-media 的交互（archive/ 内文件也参与 rename）是用户主动选择的 design tradeoff，不属 bug。

## Follow-up 007 — 2026-05-10 17:04:38
Source: user_input/follow_ups/007-20260510-170438-rename-media-to-parent-folder.md
Summary: 在每个短剧（drama）level 加一个 "🏷 重命名" 按钮，点击触发后端递归扫描该短剧 folder 树下所有 image/video 文件，按 immediate parent folder name 重命名（同扩展名 1 个 → `{folder}.ext`，多个 → `{folder}1.ext`、`{folder}2.ext`、…，按 lexicographic 顺序）。新增 `POST /api/rename-media` endpoint；只 touch media 文件；非法路径 / 非 drama-level 拒绝；两阶段 temp-rename 处理 intra-folder collision；refresh tree on完成。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated bumped to 2026-05-10 17:04:38；Composed-from list 加 follow-up 007；header 摘要描述新功能。
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9 加注释指向 follow-up 007；新增 FR-9b 描述 `POST /api/rename-media` body / response / behavior；FR-10 提及 `/api/media` (follow-up 005) 的存在 (旧文未补齐) 并保持 read endpoints 列表完整。
- `projects/ai_video_management/backend/libs/media_renamer.py` (NEW) — `MediaRenamer` 类 + `RenameOp/RenameError/RenameResult` dataclasses + `InvalidDramaPath/DramaNotFound` 异常；`rename_drama(rel)` 入口验证 path 形状（必须 `ai_videos/{drama}`，immediate child of `ai_videos/`）+ 在 sandbox 内 + dir 存在；`_iter_folders` 递归（跳过 `_EXCLUDED_DIRS` + symlink）；`_plan_folder` 按扩展名分组生成 RenameOp 列表（已是 target name → skip）；`_apply_ops` 两阶段 temp-rename 避免 collision，OSError 单独记录到 errors 不中断 batch。
- `projects/ai_video_management/backend/libs/api.py` — module docstring 改 "4 endpoints" → "5 endpoints"；imports 加 `MediaRenamer/InvalidDramaPath/DramaNotFound`；`RenameMediaBody` Pydantic model；`media_renamer = MediaRenamer(exposed, resolver)` 实例化；`POST /api/rename-media` 路由 (200 / 400 invalid_drama_path / 404 not_found)；`/api/rename-media` GET/PUT/PATCH/DELETE 405 method-not-allowed guard。
- `projects/ai_video_management/frontend/src/api.ts` — 新增 `RenameMediaResult` type + `renameMedia(path)` POST helper。
- `projects/ai_video_management/frontend/src/App.tsx` — Sidebar prop 加 `onTreeReload={() => setRefreshKey((k) => k + 1)}` 让 sidebar 在 rename 完成后能 trigger 整树 refresh。
- `projects/ai_video_management/frontend/src/components/Sidebar.tsx` — props 加 `onTreeReload?`；新增 `renamingPath/renameToast` state + `onRenameClick` callback；导入 `renameMedia` + `ApiError`；drama 节点（path 形如 `ai_videos/{name}` 且 type==directory）row 上紧邻 subtype-badge 渲染 "🏷 重命名" button (in-flight disabled)；sidebar 顶部 conditional toast 显示结果摘要 (renamed/skipped/errors counts) 或错误信息，带 dismiss 按钮 + `aria-live="polite"` 公告。Button click `e.stopPropagation()` 避免触发 row 的 expand-collapse。
- `projects/ai_video_management/frontend/src/styles.css` — 新增 `.drama-rename-btn` (轻量 11px pill style，hover/disabled 状态) + `.sidebar-toast/.sidebar-toast-ok/.sidebar-toast-err/.sidebar-toast-dismiss` (顶置 inline notification using existing `--tint-a` / `--error-bg` 色板)。

Verification (smoke tests run in tempdir):
- 多文件 + 单文件 + 已正确命名 + 跨扩展名混合 → 正确分组、正确编号、正确 skip。
- swap-collision (`aaa.mp4` 抢 `foo1.mp4`，原 `foo1.mp4` push 到 `foo2.mp4`) → 两阶段 temp-rename 无数据丢失。
- 入参形状错误 (`research/foo`、`ai_videos/X/sub`) → `InvalidDramaPath`。
- 不存在的 drama → `DramaNotFound`。

Deferred (not in this follow-up):
- backend pytest under `backend/tests/` for `media_renamer.py` + `api.py /api/rename-media` 路由（与 follow-up 005/006 一致地批量补测）。
- e2e Playwright 验证按钮行为（同上推迟）。
- dry-run 预览模式 (`?dry_run=true`)。

Severity: Low — additive feature, no breaking changes, no schema changes to existing endpoints.

## Follow-up 006 — 2026-05-10 16:40:54
Source: user_input/follow_ups/006-20260510-164054-stale-runtime-instructions.md
Summary: 用户报告 follow-up 005 后 mp4 仍不在 webapp 左侧 nav 显示（user 已 drop `c3_苏璃月{1,2,3}.mp4` 共 3 个 video 文件 + 1 个 md 到 `ai_videos/mozun_chongsheng/characters/c3_苏璃月/`）。**根因：用户运行中的 webapp 进程没 reload 新代码**，不是代码 bug。验证：直接调用 `TreeWalker.build()` 已 emit `type: "video"` 节点；`MEDIA_EXTENSIONS` 包含 `.mp4`；`exposed.is_inside('ai_videos/mozun_chongsheng/characters/c3_苏璃月/c3_苏璃月1.mp4')` 返回 `True`。Zero code changes 本 follow-up — 仅记录 reload 操作步骤 + 标记 deferred quality-of-life improvements。

Diagnosis (verified):
- Files exist: 3 mp4 + 1 md in `c3_苏璃月/` folder (sizes 11.9MB / 12.0MB / 21.6MB / 10K).
- Backend code verified at runtime: `TREE_VISIBLE_EXTENSIONS` ⊃ `.mp4` ✓; `MEDIA_EXTENSIONS` ⊃ `.mp4` ✓; tree walker emits `video` type for mp4 leaves ✓.
- `backend/static/` is empty (just `.gitkeep`). `frontend/dist/` doesn't exist. → user is running vite dev server for frontend (auto-reloads) + `python main.py` for backend (NO auto-reload).
- `python main.py` is plain spawn (no `uvicorn --reload`), so backend stays on stale code until manually restarted.

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated bumped to 2026-05-10 16:40:54 + follow-up 006 摘要.
- (Zero code changes — follow-up 005 backend / frontend code is correct as written.)

User next steps (resolve immediately):

1. **Restart backend**: kill the running `python main.py` process (Ctrl+C in its terminal, or kill via Task Manager — the one bound to port 8766) → re-run `make run-backend` (or `cd backend && PYTHONPATH=. python main.py`).
2. **If using vite dev server (`make run-frontend`)**: should auto-reload; if stale, hard-refresh browser (Ctrl+F5).
3. **If using production build**: rebuild frontend (`cd frontend && npm run build`) and ensure backend's `static/` dir contains the built dist (currently empty — separate Makefile gap deferred).
4. **Verify** by selecting `c3_苏璃月/` folder in left nav → expect 4 children: `c3_苏璃月.md` (📄) + 3× `c3_苏璃月N.mp4` (🎬) → click any mp4 → inline HTML5 `<video controls>` plays in right Reader pane (HTTP range supported for seeking).

Deferred surgical follow-ups (independent):
- (a) Add `--reload` argv to `backend/main.py` for `uvicorn.run(... reload=True)` dev-mode hot-reload (would require switching `app` from instance to import-string — minor refactor).
- (b) Makefile `run-prod` should `cp -r frontend/dist/* backend/static/` after `build-frontend` so backend serves the bundle (currently `backend/static/` stays empty even after build).
- (c) Backend tests: `test_api_media_route.py` + `test_tree_walker_includes_video.py` (already deferred per follow-up 005).

Severity: Zero (no behavior change, no code change). This entry exists to document a runtime-state issue and to write the reload procedure into the project's follow-up log so future regressions on similar "code change not visible" reports have an immediate playbook.

## Follow-up 005 — 2026-05-10 16:18:39
Source: user_input/follow_ups/005-20260510-161839-media-display-playback.md
Summary: 用户把生成好的 video / image 放进 `ai_videos/{project}/{characters,scenes,shots}/{folder}/` 文件夹（per mozun_chongsheng follow-up 014 的 folder-per-asset schema），但 webapp 左侧 nav 不显示这些 media 文件 + 不能在 Reader 内 inline 显示 / 播放。修复：(A) 后端 `MEDIA_EXTENSIONS` 引入 (mp4/mov/webm/mkv/avi/m4v + jpeg/webp/gif/bmp 共 12 项)；`TREE_VISIBLE_EXTENSIONS = ALLOWED ∪ MEDIA` 让 sidebar 显示 media；视频 tagged 为 `"video"` (新 TreeNodeType)；新增 `/api/media` route by FastAPI FileResponse with proper MIME (bypass 1MB MAX_FILE_BYTES; HTTP range for video seeking)；(B) 前端 Reader 检测 video / image 扩展 → 直接渲染 `<video controls>` / `<img>`；新增 `SiblingMedia` 组件让用户查看 .md 时下方 grid display 同 folder 媒体；新增 `mediaUrl()` helper；Sidebar / linkResolver 加 "video" 类型识别 + 🎬 icon；CSS 加 `.media-view` + `.sibling-media-grid` styling.

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated bumped to 2026-05-10 16:18:39 + follow-up 005 摘要.
- `projects/ai_video_management/backend/libs/exposed_tree.py` — 新增 `MEDIA_EXTENSIONS` (12 项 image+video) + `TREE_VISIBLE_EXTENSIONS = ALLOWED ∪ MEDIA`. `ALLOWED_EXTENSIONS` / `MAX_FILE_BYTES` 不变（`/api/file` 行为对 .md/.json 等 unchanged；只添加新的 media surface).
- `projects/ai_video_management/backend/libs/tree_walker.py` — `_is_allowed_leaf` 改用 `TREE_VISIBLE_EXTENSIONS`；`_leaf_for` 扩展 type tagging：`.mp4/.mov/.webm/.mkv/.avi/.m4v` → `type: "video"`；`.png/.jpg/.jpeg/.webp/.gif/.bmp` → `type: "image"`. `_IMAGE_EXTENSIONS` / `_VIDEO_EXTENSIONS` 各自定义.
- `projects/ai_video_management/backend/libs/api.py` — 新增 `_MEDIA_MIME_MAP` (12 ext → MIME) + `GET /api/media` 路由 (查询 `path` → exposed.is_inside sandbox check → resolver.resolve → FastAPI FileResponse with media_type)；新增 `/api/media` PUT/PATCH/DELETE/POST 405 method-not-allowed guard (镜像 `/api/file` 的 method 限制风格)；module docstring 改 "3 endpoints" → "4 endpoints".
- `projects/ai_video_management/frontend/src/types.ts` — `TreeNodeType` 加 `"video"`.
- `projects/ai_video_management/frontend/src/api.ts` — 新增 `mediaUrl(path, mtime?)` helper return `/api/media?path=...&mtime=...`.
- `projects/ai_video_management/frontend/src/components/SiblingMedia.tsx` (NEW) — `<SiblingMedia currentPath knownPaths>` scans knownPaths for sibling media in same folder, renders `<img>` for images / `<video controls>` for videos via `mediaUrl()`. `findSiblingMedia` helper filters by parent prefix + media regex.
- `projects/ai_video_management/frontend/src/components/Reader.tsx` — extended `extOf` is now reused at component top; added `IMAGE_EXTS` / `VIDEO_EXTS` / `isMediaImage` / `isMediaVideo` / `isMediaOnly` flags. `load()` skips `fetchFile` for media-only paths (videos can exceed 1MB) — sets minimal placeholder file. Render branch adds: video → `<video controls src={mediaUrl(path)}>`; non-png-jpg image → `<img src={mediaUrl(path)}>`; markdown branch now appends `<SiblingMedia />` below `<Renderer />`. Edit toggle hidden for both image + video.
- `projects/ai_video_management/frontend/src/components/Sidebar.tsx` — `node.type` checks updated in 4 places to include `"video"` (auto-collapse / leaf detection / Enter-key select / leaf rendering branch). Added `🎬` icon for video tree leaves.
- `projects/ai_video_management/frontend/src/lib/linkResolver.ts` — `collectFilePaths` 添加 `"video"` type to leaf collection.
- `projects/ai_video_management/frontend/src/styles.css` — 新增 `.media-view` (full-bleed image/video with shadow + 80vh max) + `.sibling-media-grid` (folder-context gallery card with grid row of figure items, max 320×240 thumbnails).

总计 patch 范围: **1 backend libs amend (exposed_tree + tree_walker + api) + 1 frontend types amend + 1 frontend api amend + 1 NEW SiblingMedia.tsx + 1 frontend Reader amend + 1 frontend Sidebar amend + 1 frontend linkResolver amend + 1 styles.css amend + 1 revised_prompt header bump = 9 file changes (8 modified + 1 new)**.

Behavior changes:
- `GET /api/tree` now includes `.mp4/.mov/.webm/.mkv/.avi/.m4v/.jpeg/.webp/.gif/.bmp` files under `ai_videos/**` and `research/**` (was previously only `.md/.json/.yaml/.yml/.jsonl/.txt/.png/.jpg`).
- New endpoint `GET /api/media?path=<rel>` returns raw bytes with proper Content-Type (no base64, no JSON wrapper, no 1MB limit). Same EXPOSED_TREE sandbox + same security headers as `/api/file`.
- Sidebar shows new media files with 🎬 icon for video / 🖼 icon for images (existing). User clicks → Reader displays inline.
- Markdown viewer (e.g., `c1_沧冥.md`) now shows a `📁 Folder media` gallery section below the markdown body, listing all media files in the same folder with inline previews.

No conflicts found in:
- `projects/ai_video_management/backend/libs/file_reader.py` / `file_writer.py` — unchanged (still allows only ALLOWED_EXTENSIONS for /api/file; /api/media is separate route bypassing the size limit).
- `projects/ai_video_management/backend/libs/api_security.py` — unchanged (`/api/media` is GET-only; only PUT routes are in GUARDED_ROUTES; SecurityHeadersMiddleware still applies via global middleware).
- `projects/ai_video_management/backend/libs/safe_resolve.py` / `repo_root.py` — unchanged (sandbox + path resolution reused as-is).
- `projects/ai_video_management/backend/tests/` — TBD: new `test_api_media_route.py` + `test_tree_walker_includes_video.py` deferred to independent surgical follow-up. Existing tests still pass (extension allowlist unchanged for /api/file).
- `projects/spec_driven/` — unchanged.

Severity: Low blast radius (additive only — new MEDIA_EXTENSIONS set, new /api/media route, new SiblingMedia component, new TreeNodeType variant). Existing /api/file + /api/tree contracts preserved (same ALLOWED_EXTENSIONS for /api/file; tree includes new media file types but field names unchanged). Webapp boots and renders existing markdown / image / shot-pair content without regression.

User next steps:
1. Drop a turntable.mp4 into `ai_videos/mozun_chongsheng/characters/c1_沧冥/` → refresh webapp → see `turntable.mp4` appear in left nav under `c1_沧冥/` folder with 🎬 icon → click → video plays inline in Reader.
2. Drop a `ref.png` into `scenes/s1_长阶顶/` → see it in nav with 🖼 icon → click → image displays at 80vh max-height.
3. Open any character / scene / shot `.md` file → see markdown content + new `📁 Folder media · 同 folder 媒体` section at bottom listing all media in same folder with inline previews.

Out of scope (deferred to independent surgical follow-up):
- Backend tests for `/api/media` route + tree_walker video inclusion.
- Audio file support (.mp3 / .wav / .m4a / .ogg).
- Video thumbnail generation (HTML5 `<video preload="metadata">` already provides poster frame fallback).
- PUT /api/media for uploading media via webapp (current contract is read-only — user drops files via filesystem).
- frontend test for SiblingMedia + media route detection.

## Follow-up 004 — 2026-05-09 19:48:37
Source: user_input/follow_ups/004-20260509-194837-allow-chinese-filenames.md
Summary: ai_video_management 已支持 UTF-8 中文文件名（`is_inside` 仅拦截 backslash / NUL byte / 已知 excluded dirs；前端 React Sidebar 直接渲染 `node.name` 中文字符串），无需代码改动。本 follow-up 仅做规则与 spec 文档侧 amend，配合 mozun_chongsheng/002 让 `ai_videos/mozun_chongsheng/characters/` 等"内容性"目录可 opt-in 中文文件名。

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — 规则 1 amend：明确"内容性"文件可 opt-in 中文命名（结构性文件 shotlist.md / episode.md / shot{NN}_*.md 等仍 English/pinyin；task_name 仍硬性 pinyin/English 因 task_id 构造与跨平台 path stability）。
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Composed-from header 加入 follow_ups/004；Last regenerated bumped 到 2026-05-09 19:48:37。

No conflicts found in: 
- final_specs/spec.md（FR-7 EXPOSED_TREE / FR-8 is_inside / FR-12 path-traversal 与字符集无关；UTF-8 中文路径段已通过现有 sandbox）
- 所有 backend libs（exposed_tree.py / safe_resolve.py / file_reader.py / file_writer.py / api.py / api_security.py 与字符集解耦，仅校验 backslash/NUL/leading-slash/excluded-dirs）
- 所有 frontend src 代码（Sidebar.tsx / Reader.tsx 用 React 渲染 node.name 字符串，浏览器原生支持 UTF-8）
- validation/* 与 tests/*（path-traversal 测试覆盖 ASCII 与 percent-encoded UTF-8 已存在；中文 path segment 通过现有测试集）

不需 code 改动；现有 webapp 直接支持。

## Follow-up 003 — 2026-05-09 15:21:35
Source: user_input/follow_ups/003-20260509-152135-research-folder-and-viewer.md
Summary: Introduce a new repo-root `research/` folder for free-form reference dumps, and surface its contents through the ai_video_management webapp's sidebar viewer alongside the existing AI Videos section. First content drop: 8 仙侠剧 storyline mds (+ index README) under `research/xianxia_storylines/`, sourced from public material on Wikipedia / 百度百科 / 豆瓣 / mainstream press. Backend `EXPOSED_TREE` widened to admit `research/**`; tree walker emits a new `Research` section at the canonical position 2 (after AI Videos). No frontend code changes — Sidebar walks `tree.children` uniformly, so the new section surfaces with working disclosure carets / keyboard nav / file-open behavior automatically. Same Origin/Host gate, same path-traversal hardening, same extension allowlist apply to research files.

Auto-updated:
- specs/development/ai_video_management/final_specs/spec.md — FR-7 amended (5 EXPOSED_TREE roots, research/** added as #2); FR-8 amended (`is_inside` admits `ai_videos/` and `research/`); FR-18 amended (sections in fixed order: AI Videos, Research, Specs, Context — Specs/Context still not-yet-implemented; AI Videos and Research are live); FR-43 amended (sidebar fixed-order section list updated). No new FR/NFR/AC.
- specs/development/ai_video_management/user_input/revised_prompt.md — Composed-from header bumped to include follow-up 003; new "Last regenerated" line at 2026-05-09 15:21:35 documenting the EXPOSED_TREE extension and content drop.
- projects/ai_video_management/backend/libs/exposed_tree.py — new module-level `_ALLOWED_TOP_LEVEL` frozenset {`ai_videos`, `research`}; `is_inside` keys off the set instead of a hardcoded `if first == "ai_videos":`; new `research_dirs()` accessor symmetrical to `ai_video_dirs()`. Class docstring updated to call out the two roots and reference follow-up 003.
- projects/ai_video_management/backend/libs/tree_walker.py — new `_research_section()` method paralleling `_ai_videos_section()`. Walks `research/` recursively via the existing `_walk_filtered` helper using `_is_allowed_leaf`. NO `project_meta` payload (research dirs don't have a sub_type). `build()` updated to include `_research_section()` ordered after `_ai_videos_section()` (matches FR-18).
- projects/ai_video_management/backend/tests/test_tree_walker_consumer_walk.py — `test_tree_single_ai_videos_section` renamed/replaced by `test_tree_sections_order` (asserts `["AI Videos", "Research"]`); old `test_no_other_sections_in_tree` dropped (replaced by the order assertion); new `test_research_section_walks_repo_research_dir` asserts the Research section exists, has `type=section`, and contains at least one child when the repo's `research/` directory has content.
- projects/ai_video_management/backend/tests/test_boot_smoke.py — `test_get_tree_returns_single_ai_videos_section` renamed to `test_get_tree_returns_expected_sections`; assertion updated to `["AI Videos", "Research"]` per FR-18.
- projects/ai_video_management/backend/tests/test_api_security_three_shapes.py — `test_get_tree_unguarded` assertion updated to `["AI Videos", "Research"]` per FR-18.
- research/xianxia_storylines/ — NEW directory at repo root. 9 markdown files: `README.md` (index), `sansheng_sanshi_shili_taohua.md` (三生三世十里桃花 2017), `xiangmi_chenchen_jin_rushuang.md` (香蜜沉沉烬如霜 2018), `liu_li.md` (琉璃 2020), `chenxiang_ru_xie.md` (沉香如屑·沉香重华 2022), `cang_lan_jue.md` (苍兰诀 2022), `chang_yue_jin_ming.md` (长月烬明 2023), `lian_hua_lou.md` (莲花楼 2023, tagged 武侠 not strict 仙侠 — flagged in-file), `yu_feng_xing.md` (与凤行 2024). Each file captures basic info, one-line setting, multi-volume plot synopsis, character table, key虐点/名场面 list, genre tags, AI-video visual-element notes, source citations.

No conflicts found in: interview/qa.md, findings/* (research is not a pipeline output and does not participate in regen prompts; FR-30/FR-32 promotion gates already exclude `ai_videos/{name}/` and now implicitly exclude `research/` too since `stage` allowlist remains `{interview, findings, final_specs, validation}`), validation/* (no AC referenced the section count directly; AC-Level-2 schema assertions still hold — TreeNode shape unchanged), projects/ai_video_management/backend/libs/{api.py, file_reader.py, file_writer.py, safe_resolve.py, repo_root.py, sub_type_lookup.py, api_security.py} (untouched — they all key off `is_inside` for sandbox enforcement, so the EXPOSED_TREE extension flows through automatically), projects/ai_video_management/frontend/src/* (untouched — Sidebar walks `tree.children` uniformly, Reader's path-based render-mode dispatch already handles `.md`/`.png`/`.jpg` under any path; locked-block pill, breadcrumb, link resolver all path-agnostic).

Discovery (out of scope, not fixed): 5 pre-existing backend test failures stem from `ai_videos/wukong_juexing/` no longer existing in the repo (`ai_videos/` is currently empty): `test_put_file_loopback_alias_admit`, `test_put_file_extension_rejected_as_400`, `test_lookup_wukong_juexing_is_short`, `test_lookup_shot_count_for_wukong_juexing`, `test_ai_videos_section_has_project_meta_for_wukong`. These are independent of follow-up 003 and predate this turn — flagged for a future follow-up that either (a) re-creates a synthetic ai_video fixture at `tests/fixtures/`, or (b) marks these tests as `@pytest.mark.skipif(not (repo_root() / "ai_videos" / "wukong_juexing").is_dir(), reason="...")`.

## Follow-up 001 — 2026-05-05 12:15:36

Source: `user_input/follow_ups/001-20260505-121536-ai-videos-only-scope.md`
Summary: narrow ai_video_management scope to `ai_videos/` only — drop `specs/`, `CLAUDE.md`, `.claude/` from EXPOSED_TREE; drop the regen-prompt + pinning + stages features along with their endpoints and frontend surface.

Auto-updated:

**user_input:**
- `revised_prompt.md` — regenerated as raw + follow-up 001; goal section now states "focused viewer/editor"; out-of-scope list expanded to include spec-pipeline operations.

**Generated outputs (`projects/ai_video_management/`):**
- `backend/libs/safe_resolve.py` — `_ALLOWED_TOP_LEVEL` reduced to `{"ai_videos"}`; `.claude/` and `specs/` branches removed from `resolve()`.
- `backend/libs/exposed_tree.py` — entire module rewritten; `is_inside` admits only `ai_videos/`; `claude_root_files`, `claude_skill_files`, `claude_agent_refs`, `specs_ai_video_dirs`, `CANONICAL_STAGES`, `SCRATCH_DIRNAME` constants removed.
- `backend/libs/tree_walker.py` — `_specs_section()`, `_context_section()`, `_build_dotclaude_node()` removed; `build()` now returns a single "AI Videos" section.
- `backend/libs/sub_type_lookup.py` — heuristic switched from `qa.md` parse to `episodes/` directory existence + `script.md`/`shotlist.md` presence (specs/ no longer reachable).
- `backend/libs/api_security.py` — `GUARDED_ROUTES` reduced to `{("PUT", "/api/file")}`.
- `backend/libs/api.py` — entire module rewritten; `/api/regen-prompt`, `/api/promote` (POST + DELETE), `/api/stages` endpoints removed; `RegenPromptBody`, `PromotePostBody`, `PromoteDeleteBody`, `ScopeEpisodeRange` Pydantic models removed.
- `backend/libs/regen_prompt.py` — DELETED.
- `backend/libs/promotions.py` — DELETED.
- `backend/libs/stages.py` — DELETED.
- `backend/tests/test_boot_smoke.py` — assertions updated to expect single AI Videos section; added explicit `test_stages_endpoint_dropped`, `test_regen_prompt_endpoint_dropped`, `test_promote_endpoint_dropped`.
- `backend/tests/test_sub_type_lookup.py` — switched from qa.md-fixture tests to episodes/-directory + shotlist-presence heuristic tests; added synthetic novel + synthetic short + empty-project cases.
- `backend/tests/test_tree_walker_consumer_walk.py` — assertion updated to expect `["AI Videos"]` instead of three sections; added `test_no_specs_or_context_section_in_tree` guard.
- `backend/tests/test_api_security_three_shapes.py` — switched all guarded-route probes from `POST /api/regen-prompt` to `PUT /api/file`; added `test_put_file_extension_rejected_as_400` (image-write rejection at 400).
- `frontend/src/App.tsx` — `/project/:type/:name` and `/stage/:type/:name/:stage` routes removed; `Home` import simplified.
- `frontend/src/types.ts` — removed: `Stage`, `StageModule`, `RegenWarning`, `RegenResult`, `ScopeKind`, `ScopeEpisodeRange`, `PromoteRequest`, `UnpromoteRequest`, `PromoteResult`, `RegenRequest`, `StaleWriteDetail`. Kept: `TreeNode`, `ProjectMeta`, `FileResult`, `WriteResult`, `ApiError`.
- `frontend/src/api.ts` — removed: `fetchStages`, `postRegenPrompt`, `postPromote`, `deletePromote`. Kept: `fetchTree`, `fetchFile`, `putFile`, `imageUrl`.
- `frontend/src/components/Home.tsx` — dropped `Link` to project pages; project list now renders as plain entries with sub-type badges only; added explanatory paragraph pointing users to spec_driven for regen.
- `frontend/src/components/Sidebar.tsx` — `classifySpecPath` and `navigateForNode` removed; `useNavigate` import removed; double-click behavior now toggles directory only.
- `frontend/src/components/Reader.tsx` — entire module simplified; removed `RegeneratePanel`, `QaView`, `QaErrorBoundary` imports + dispatch arms; cross-tree "查看规格" link removed; pinning logic + `pinContext` + `extractMarkdownItemBody` + all `postPromote`/`deletePromote` calls removed.
- `frontend/src/markdown/renderer.tsx` — `PinContext`, `PinButton`, `extractPinId`, custom `p` and `li` overrides for pin buttons removed; locked-block pre-render preserved.
- `frontend/src/components/RegeneratePanel.tsx` — DELETED.
- `frontend/src/components/ProjectPage.tsx` — DELETED.
- `frontend/src/components/StagePage.tsx` — DELETED.
- `frontend/src/components/QaView.tsx` — DELETED.
- `frontend/src/components/QaErrorBoundary.tsx` — DELETED.
- `frontend/src/lib/autonomousMode.ts` — DELETED (no regen panel).
- `frontend/src/lib/qaParser.ts` — DELETED (no QaView).
- `frontend/e2e/golden_path.spec.ts` — Specs/Context section assertions removed; "POST /api/regen-prompt" foreign-Origin test replaced with "PUT /api/file" foreign-Origin test; new `Spec routes return 404` assertion added confirming `specs/...` and `CLAUDE.md` are unreachable.
- `README.md` — overview rewritten as "focused viewer/editor"; spec-pipeline language removed; coexistence note now says "spec-pipeline operations live in spec_driven on port 8765"; sub_type detection note clarified as heuristic.

**Spec-pipeline artifacts that retain stale references** (not auto-patched per "smallest change that resolves the conflict" — surfaced here so future regens know):
- `interview/qa.md` — Regen-scope-UI category and Sidebar-organisation category are now obsolete; cross-tree-link probe is moot. Future stage-2 regen would re-derive these from the revised prompt and naturally drop them.
- `findings/dossier.md` + per-angle files — extensive references to specs/, regen prompts, sub_type-from-qa.md. Historical record; future stage-3 regen would re-derive.
- `final_specs/spec.md` — many FRs (FR-7 EXPOSED_TREE, FR-9 mutation surface, FR-22..FR-24 sub_type, FR-30..FR-39 regen + promote, FR-43..FR-46 sidebar, FR-65..FR-66 locked block, FR-70..FR-78 RegeneratePanel + cross-tree, FR-82..FR-85 tests) need surgical patches OR full stage-4 regen. Recommended: full stage-4 regen via spec_driven once user confirms follow-up 001 is final.
- `validation/strategy.md` + per-level files — security.md, e2e.md, accessibility_and_manual.md all reference dropped features. Recommended: full stage-5 regen via spec_driven once stage 4 is updated.

No conflicts found in: `findings/angle-spec-driven-parallel-audit.md` (read-only inventory), `validation/divergences.md` (does not exist for this project).

Backend test verification: 22/22 pytest pass after follow-up 001 patches.

## Follow-up 002 — 2026-05-05 13:05:48

Source: `user_input/follow_ups/002-20260505-130548-zero-claude-coupling.md`
Summary: zero-coupling cleanup. Backend must not read or reference `CLAUDE.md`, `.claude/`, or `specs/` even at internal-anchor level. Source code grep for those literals across `projects/ai_video_management/` returns nothing after this follow-up.

Auto-updated:

**user_input:**
- `revised_prompt.md` — header amended to compose from raw + 001 + 002; preface line rewritten to drop spec_driven cross-reference and assert anchor-on-`ai_videos/`.

**Generated outputs:**
- `backend/libs/repo_root.py` — `RepoRoot.find()` now walks up looking for an `ai_videos/` child directory; the parent of that match becomes the workspace root. `CLAUDE.md` + `.claude/` no longer referenced. New `ANCHOR_DIR_NAME` constant.
- `backend/libs/safe_resolve.py` — comment cleanup (no behavioral change).
- `backend/libs/exposed_tree.py` — docstring rewritten without follow-up / spec_driven reference.
- `backend/libs/tree_walker.py` — docstring rewritten.
- `backend/libs/sub_type_lookup.py` — module docstring rewritten without specs/ / qa.md narrative.
- `backend/libs/api.py` — module docstring trimmed; comment in PUT handler rephrased without "FR-28" / "spec_driven" terms.
- `backend/libs/api_security.py` — comment cleanup.
- `backend/libs/file_writer.py` — `MissingIfUnmodifiedSince` docstring + inline comment rephrased without "FR-15" / "spec_driven" references.
- `backend/tests/conftest.py` — `repo_root()` helper switched to `ai_videos/`-based anchor (matching `RepoRoot.find()`).
- `backend/tests/test_boot_smoke.py` — docstrings cleaned of "follow-up 001" / "Per follow-up" narrative.
- `backend/tests/test_sub_type_lookup.py` — module docstring rewritten.
- `backend/tests/test_tree_walker_consumer_walk.py` — docstrings cleaned; `test_no_specs_or_context_section_in_tree` renamed to `test_no_other_sections_in_tree`.
- `backend/tests/test_api_security_three_shapes.py` — module + per-test docstrings rewritten; "Port 8765 (spec_driven)" → "Any port other than 8766".
- `frontend/src/components/Reader.tsx` — docstring trimmed.
- `frontend/src/components/Home.tsx` — explanatory paragraph pointing users to "spec_driven webapp on port 8765" removed.
- `frontend/src/components/ShotPairView.tsx` — docstring trimmed; "FR-50" mention removed from inline error message.
- `frontend/src/components/ShotlistTableView.tsx` — docstring trimmed.
- `frontend/src/components/ImageRefView.tsx` — docstring trimmed.
- `frontend/src/styles.css` — "(FR-44)" / "(FR-65, FR-66)" comment annotations removed.
- `frontend/e2e/playwright.config.ts` — "(catches the spec_driven-006 Origin-rewrite regression)" softened to "(catches Origin-rewrite regressions)".
- `frontend/e2e/golden_path.spec.ts` — "Per follow-up 001" comments removed; the "Spec routes return 404" test rewritten as "Out-of-sandbox paths return 404" with non-specs probe paths (`node_modules/anything.md`, `../escape.md`, `random_top_level/file.md`).
- `frontend/test/shotPairing.test.ts` — `specs/ai_video/...` test paths replaced with paths that don't reference specs/.
- `README.md` — entire file rewritten removing all references to `specs/`, `spec_driven`, `CLAUDE.md`, `.claude/`, follow-up numbers. Architecture section now describes the `ai_videos/`-anchor strategy.

Backend test verification: 22/22 pytest pass.

Verification grep for `spec_driven|specs/|CLAUDE|.claude|FR-\d+|follow-up` across `projects/ai_video_management/` (case-insensitive): **zero matches**.

Note: The `specs/development/ai_video_management/` directory itself (this audit trail) continues to use those terms — it's the agent_team workflow's persistence surface, not webapp source. The webapp reads none of it.

## Follow-up 034 — 2026-05-13 00:38:00
Source: user_input/follow_ups/034-20260513-003800-actor-md-styled-read-view.md
Summary: actor sidecar md (`ai_videos/_actors/actor_NNNN/actor_NNNN.md`) gets a dedicated `ActorView` — large face image + key/value attrs + read-mode prompt card with Copy button; Reader dispatch skips `SiblingMedia` so the bulk-selection toolbar disappears on actor pages.

Auto-updated:
- `user_input/revised_prompt.md` — header bumped; `Composed from` extended with follow-up 034; prior-033 note appended.
- `final_specs/spec.md` — added `FR-92` (ActorView read view + Reader dispatch + skip-SiblingMedia rule) above FR-91.
- `validation/acceptance_criteria.md` — added Scenario U3.19 (actor md → ActorView dispatch, no bulk toolbar, image + dl + prompt-card + Copy button + Edit-toggle escape hatch + empty-prompt + missing-image edge cases); FR↔scenario map row `FR-92 | U3.19` appended.
- `projects/ai_video_management/frontend/src/components/ActorView.tsx` — new component (image resolve, attribute-table parse, fenced-block prompt extract, copy-to-clipboard).
- `projects/ai_video_management/frontend/src/components/Reader.tsx` — `isActor` regex (`^ai_videos/_actors/actor_[^/]+/actor_[^/]+\.md$`) added to dispatch; ActorView branch inserted before generic markdown branch; SiblingMedia not mounted on actor branch; Edit toggle exempted for actor (matches imageRef / casting / shotPair exemption pattern).
- `projects/ai_video_management/frontend/src/styles.css` — new `/* ActorView */` block (responsive 2-col grid → 1-col under 820px; image pane on `#fafafa`; meta pane with section titles; prompt card on `--pre-bg/--pre-fg` tokens; copy button absolutely positioned).

No conflicts found in: backend libs (FR-9f / FR-9i / FR-9j unchanged), ActorPoolGenerator, ActorGrid, CastingView, ImageRefView, ShotPairView, ShotlistTableView, casting / archive / delete endpoints, env / Kling provider stack.

## Follow-up 084 — 2026-05-17 22:19:24
Source: user_input/follow_ups/084-20260517-221924-delete-toast-never-disappears.md
Summary: 修复 "删除成功提示在前端永远不消失" bug — `lib/announce.ts` 的 shared `announceToast(msg, ttlMs=4500)` 自带 TTL 自动清除 + `.is-visible` class 移除 (follow-up 060 引入), 但 4 个 component 各自复制了一份缺 TTL clear 的本地 helper, 导致 `#aria-live-toast` region 一旦写入永久驻留。补做 follow-up 060 utility 引入时漏掉的 caller migration。

根因: 4 个 component 的本地 `announceToast` / `announce` 函数只做了 `textContent = ""` + `setTimeout(... textContent = message, 30)`, 没有 `setTimeout(..., 4500)` 把 region 清空 + 移除 visible class — 删除提示永久驻留 DOM。

Auto-updated:
- specs/development/ai_video_management/user_input/follow_ups/084-20260517-221924-delete-toast-never-disappears.md — 新建 follow-up 084 (本 fix 抽象到 follow-up 060 utility migration 补做)。
- specs/development/ai_video_management/user_input/revised_prompt.md — `Last regenerated` 头 bumped 到 084; 083 bump 保留为 Prior bump。
- projects/ai_video_management/apps/ui/src/components/Reader.tsx — 删除本地 `announceToast` helper (line 361-366); 顶部 `import { announceToast } from "../lib/announce";` 加入; 7 处 call sites (Archive/Unarchive/Delete/Delete failed/concat 角色合辑/Extract frames + 各自 failure) 不动 — 函数签名一致。
- projects/ai_video_management/apps/ui/src/components/ActorGrid.tsx — 删除本地 `announceToast` helper (line 406-411); 顶部 import 加入; 2 处 call sites (批量删除完成 + assign 完成) 不动。
- projects/ai_video_management/apps/ui/src/components/DeletedView.tsx — 删除本地 `announceToast` helper (line 298-303); 顶部 import 加入; 1 处 call site (永久删除提示) 不动。
- projects/ai_video_management/apps/ui/src/components/SiblingMedia.tsx — 删除本地 `announce` helper (line 66-74); 顶部 `import { announceToast as announce } from "../lib/announce";` aliased 加入; 8 处 archive/unarchive/extract frames call sites 不动 (aliased import 保留 `announce(...)` 命名)。

总计 patch 范围: **4 component files 修改 (各 +1 import, -1 local helper) + 1 follow-up 文件新建 + 1 revised_prompt header bump = 6 文件改动**。

Verification:
- `grep -c "function announceToast" src/components/` → 0 (4 local 副本全部清除)。
- `grep "announceToast" src/lib/announce.ts` → 1 (唯一权威 export, line 19)。
- `npx tsc --noEmit` → 仅 2 个 pre-existing vite.config.ts 错误 (不在本 fix 范围); 4 个 component 文件 0 errors。
- `npx vitest run` → 10/10 passed (no regression)。

No conflicts found in: lib/announce.ts (utility 已正确, 不动), App.tsx (`#aria-live-toast` div mount 不动), styles.css (`.a11y-live-region` / `.is-visible` CSS 不动), apps/api/ (纯前端 UX bug 无后端 ripple), 其他 component (本 follow-up 只覆盖 4 个 buggy 副本; 如未来发现新 buggy 副本同样应迁移到 shared)。

User next steps (manual browser verification — Claude 不能在 session 内做):
1. `npm run dev` 起前端。
2. 触发 ① 删除一个 media (Reader.tsx flow), ② 批量删除 actor (ActorGrid flow), ③ 永久清理 _deleted (DeletedView flow), ④ archive/unarchive 单文件 + 批量 (SiblingMedia flow)。
3. 观察右上角 toast: 出现 → 4.5 s 后自动消失 + DOM 中 `#aria-live-toast` 失去 `.is-visible` class + textContent 空。
4. 多次连续触发: 每次都重置 TTL 计时器 (`lib/announce.ts:30 clearTimeout`)。

Severity: **UX blocker** — 删除/归档完成后的 4.5 s 后自动消失语义破坏, 影响所有删除/归档/帧提取/合辑路径; 本 follow-up 完成后 4 个 component 已统一接到 shared utility, 无新增 utility 或新增组件。

## Follow-up 100 — 2026-05-20 21:33:34
Source: user_input/follow_ups/100-20260520-213334-clickable-breadcrumb-navigation.md
Summary: Reader breadcrumb segments become clickable buttons that navigate up the path; prefer the self-named `<folder>/<folder>.md` index file when present in `knownPaths`, fall back to `/file/<accumulated-prefix>`.

Auto-updated:
- projects/ai_video_management/apps/ui/src/components/Breadcrumb.tsx — `BreadcrumbProps` gains optional `knownPaths: string[]` + `onNavigate: (target: string) => void`. Each non-last segment renders a `<button class="breadcrumb-link">`; `resolveTarget(prefix, segment)` returns `prefix/segment.md` if that path is in `knownPaths`, else `prefix`. Last segment unchanged.
- projects/ai_video_management/apps/ui/src/components/Reader.tsx — passes `knownPaths={knownPaths}` (already a prop) + `onNavigate={(t) => navigate("/file/" + encodeURIComponent(t))}` to `<Breadcrumb />`. No other changes.
- projects/ai_video_management/apps/ui/src/styles.css — adds `.breadcrumb-link` rules (transparent button styling, hover/focus underline, `:focus-visible` outline) and explicit `.breadcrumb-sep` padding. `.breadcrumb`, `.breadcrumb-list`, `.breadcrumb-current` unchanged.
- specs/development/ai_video_management/user_input/revised_prompt.md — header bump (Last regenerated 2026-05-20 21:33:34, follow-up 100 narrative + previous 099 demoted to Prior bump).

No conflicts found in: final_specs/spec.md (only structural mention of Breadcrumb.tsx as a ported component — no behavioral contract), findings/dossier.md (same), validation/* (no breadcrumb requirements), interview/qa.md, apps/api/* (pure frontend change), other UI components.

## Follow-up 101 — 2026-05-21 00:24:55
Source: user_input/follow_ups/101-20260521-002455-sidebar-default-collapsed.md
Summary: Sidebar tree defaults to every directory collapsed on initial load; deep-link auto-expand of currentPath ancestors and user toggle persistence across refreshes are preserved.

Auto-updated:
- projects/ai_video_management/apps/ui/src/components/Sidebar.tsx — line 91 `accum[node.path] = true` → `accum[node.path] = false` in the tree-load `useEffect`. The render-side `isOpen = depth === 0 ? true : expanded[node.path] === true` (line 133) is unchanged, so top-level sections stay always-open. The `{ ...accum, ...prev }` merge order keeps user-toggled state across `onTreeReload` refreshes. The currentPath ancestor-expansion effect (lines 98-108) is unchanged.
- specs/development/ai_video_management/user_input/revised_prompt.md — header bump (Last regenerated 2026-05-21 00:24:55, follow-up 101 narrative + previous 100 demoted to Prior bump).

No conflicts found in: final_specs/spec.md (FR-90 mentions `_actors/` icon "Standard expand/collapse + folder navigation behavior is unchanged" — refers to that one folder’s behavior, not the global default expansion contract; no FR pins the default-expanded state), findings/dossier.md, interview/qa.md, validation/* (no sidebar default-state requirements), apps/api/* (pure frontend change), apps/ui/e2e/* (no expand/toggle assertions), other UI components.

## Follow-up 108 — 2026-05-21 00:52:00
Source: user_input/follow_ups/108-20260521-005200-legado-rule-reader.md
Summary: Add a Legado-3.0-rule-driven HTML reader as opt-in scaffolding so future novel-source fallbacks can be added by dropping a JSON book-source under `libs/infrastructure/readers/sources/` instead of hand-coding per-host scrapers. No existing download path touched; Legado would not help with follow-up 106's speed/anti-bot problem (same HTTP signature would trip the same rate limit), so this targets follow-up 107's extension axis only.

Auto-updated:
- projects/ai_video_management/libs/infrastructure/daos/__init__.py — new role folder under infrastructure (first DAO entry for this solution).
- projects/ai_video_management/libs/infrastructure/daos/legado_source__dao.py — frozen-dataclass DAO mirroring the Legado book-source JSON (snake_case attrs); nested `LegadoTocRulesDao` / `LegadoContentRulesDao` / `LegadoBookInfoRulesDao` / `LegadoSearchRulesDao`; `from_legado_json(dict)` constructor that drops unknown fields.
- projects/ai_video_management/libs/infrastructure/errors/legado_source__error.py — `LegadoRuleError`, `LegadoUnsupportedSyntaxError`, `LegadoFetchError`.
- projects/ai_video_management/libs/infrastructure/readers/legado__reader.py — `_LegadoEngine` (stateless rule evaluator: XPath / CSS / default tag-class-id path / `&&` concat / trailing `##pat##rep##`; raises on `@js:` / JSONPath / AllInOne single-colon regex) and `LegadoReader` (HTTP client + `fetch_toc` / `fetch_chapter` / `fetch_book_info`; `from_json_file(path)` classmethod; context-manager protocol; owns its `httpx.Client` with the existing downloader's UA + zh-CN headers).
- projects/ai_video_management/libs/infrastructure/readers/sources/ttkan_co.json — vendored Legado 3.0 community source for `cn.ttkan.co` (from XIU2/Yuedu#85); first data point that exercises the rule grammar (XPath in ruleBookInfo, default-path syntax `class.content@tag.p@text` in ruleContent, `class.full_chapters@children[1]@tag.a` + bare `text`/`href` accessors in ruleToc).
- projects/ai_video_management/pyproject.toml — add `lxml>=5.0` and `cssselect>=1.2` (HTML parse + XPath + CSS). Both ship precompiled Windows wheels for Python 3.10+; no native build chain.
- projects/ai_video_management/requirements.txt — mirror the new deps.

No conflicts found in: novel__writer.py (Legado reader is additive; existing `_fetch_index_via_sudugu` / `_fetch_index_via_ttkan` helpers unchanged — switching them to Legado JSON form would be a future follow-up with parity tests), application layer (no new query/command since nothing consumes the reader yet), apps/api/* + apps/ui/* (no route or UI surface change), apps/cli/novel_download.py (no CLI change; `--workers 1` default from follow-up 106 stays), final_specs/spec.md (no FR pins the scraper architecture; spec describes downloader behavior, not internal extensibility), findings/dossier.md, interview/qa.md, validation/* (no requirements on rule-engine layering), root pyproject.toml + requirements.txt (scoped to spec_studio platform; ai_video_management is a separate solution).


## Follow-up 111 — 2026-05-24 09:58:34
Source: user_input/follow_ups/111-20260524-095834-novels-split-per-chapter.md
Summary: Split each downloaded novel's single `{slug}.md` (3–19 MB, exceeds `MAX_FILE_BYTES = 1 MiB`) into per-chapter `chapters/{NNNN}-{title}.md` files (5–80 KB each) so the webapp can finally open them. Closes follow-up 101's deferred "pagination / single-file > 1 MiB" item.

Auto-updated:
- projects/ai_video_management/libs/infrastructure/writers/novel__writer.py — `ChapterRecord` gains nullable `file: str | None`; module-level `_safe_filename_segment` + `_build_chapter_filename` helpers (Windows-reserved-char strip + 80-char cap, preserves CJK per follow-up 004); `_NovelState.body_path` replaced by `chapters_dir` + `readme_path`; `_ensure_index` now mkdir-p's `chapters/` and writes a per-novel `README.md` (title/作者/来源) instead of seeding `{slug}.md`; `_download_one_chapter` writes `chapters/{NNNN}-{safe_title}.md` with body `# {title}\n\n{body}\n` and fills `ChapterRecord.file`; `_write_index_md` link target changed from `{slug}/{slug}.md` to `{slug}/README.md`; `__all__` exports the new helpers for the splitter.
- projects/ai_video_management/apps/cli/novel_split.py — NEW one-shot splitter (`python -m apps.cli.novel_split [<slug>] [--dry-run] [--keep]`). Splits `^## ` headings into per-chapter files; reuses `_build_chapter_filename`; idx-aligned title match via dict (last-wins on duplicate-heading retries from resumable-download); UTF-8 stdout reconfigure for Windows cp1252 console. Re-run-safe via `_repair_meta_from_chapters_dir`: when chapter files exist but meta is out of sync (concurrent legacy-writer downloader corruption), filename→idx rebuild restores `file` + `done`. Graceful degradation: chapters present in meta but absent from body get `done=False` + `file=None` so `download_all` re-fetches them. After successful split, the concatenated `{slug}.md` is deleted (per user direction; pass `--keep` to preserve). Auto-resolves `downloaded_novels/` first, falls back to `novels/` (forward-compat with in-flight follow-up 112 folder rename).
- specs/development/ai_video_management/user_input/revised_prompt.md — header bump (Last regenerated 2026-05-24 09:58:34, follow-up 111 narrative + previous 110 demoted to Prior bump).

Runtime — splitter executed against `downloaded_novels/xianxia/`:
- 7 novels split cleanly (`guangyin_zhiwai` 1383, `xuanjian_xianzu` 1659, `meiqian_xiu_shenme_xian` 941, `jie_jian` 465, `gou_zai_liangjie_xiuxian` 463, `shei_rang_ta_xiuxian_de` 1431, `shan_he_ji` 858).
- 4 novels had `done=True` chapters whose bodies never landed in `{slug}.md` (truncation from a concurrent legacy-writer downloader run); split what was findable, marked the rest for re-download — `fanren_xiuxian_zhuan` 1939+573, `wode_moni_changsheng_lu` 615+1188, `zhen_wen_changsheng` 1018+460, `gou_zai_yaowu_luanshi` 500+602. User's next `python -m apps.cli.novel_download` pass will refill the missing slots into the per-chapter layout.
- 3 novels skipped: `cong_jianshu_xiuxing`, `zhutian_daozu`, `gou_zai_xiuxianjie` — empty folders, never downloaded.

Coordination note: user is concurrently landing follow-up 112 (rename `novels/` → `downloaded_novels/`, add sibling `my_novel/` for original manuscripts). The novel_writer docstring already mentions 112; the splitter is dual-path so it runs cleanly under either name. Follow-up 112 will still need to update `_resolve_novels_root` in `apps/cli/novel_download.py`, `_ALLOWED_TOP_LEVEL` in `libs/common/exposed_tree.py` + `libs/common/safe_resolve.py`, and the section-name + walker target in `libs/infrastructure/readers/tree__reader.py`. None of 111's changes block 112.

No conflicts found in: libs/infrastructure/readers/tree__reader.py (`_walk_filtered` recurses into `chapters/` automatically; default-collapsed sidebar from follow-up 101 keeps the chapter list hidden until the user expands the novel's folder), libs/common/exposed_tree.py (`MAX_FILE_BYTES = 1 MiB` is unchanged — per-chapter files stay well under it), apps/api/routes/novel__route.py (`GET /api/novels` still aggregates by `_meta.json.complete`; the four partially-missing novels will flip to `complete=false` until re-downloaded, which is correct), final_specs/spec.md (no FR pins novel storage layout — the spec describes the downloader pipeline, not on-disk file granularity), findings/dossier.md, interview/qa.md, validation/*, apps/cli/novel_download.py (writer signature unchanged; CLI imports stay byte-aligned).


## Follow-up 113 — 2026-05-24 10:14:28
Source: user_input/follow_ups/113-20260524-101428-split-novels-into-downloaded-and-my-novel.md
Summary: Rename top-level `novels/` → `downloaded_novels/` (scraped baseline corpus) and add new sibling `my_novel/` (original manuscripts authored for AI-short-drama production). Webapp `ExposedTree` now admits three roots; `tree_reader` renders three sections (`AI Videos`, `Downloaded Novels`, `My Novel`). Path-level updates to sandbox allowlist, container DI, CLI downloader, frontend type comment, and three test files. Application/domain layer is path-agnostic (Path injection via DI) and unchanged. The number 112 is occupied by `112-kling-actor-429-retry.md`; the prior splitter follow-up (111) misremembered the rename as "follow-up 112" — corrected to 113 here.

Auto-updated:
- novels/ → downloaded_novels/ (OS-level rename; git will surface as renames once staged). New sibling `my_novel/.gitkeep` placeholder so the empty folder commits.
- projects/ai_video_management/libs/common/safe_resolve.py — `_ALLOWED_TOP_LEVEL = {"ai_videos", "downloaded_novels", "my_novel"}` (was `{"ai_videos", "novels"}`).
- projects/ai_video_management/libs/common/exposed_tree.py — same allowlist update; `novel_dirs()` split into `downloaded_novel_dirs()` + `my_novel_dirs()`; class docstring rewritten to describe the three-root surface.
- projects/ai_video_management/libs/infrastructure/readers/tree__reader.py — `_novels_section()` renamed/refactored to `_downloaded_novels_section()` (pointing at `downloaded_novels/`, retaining the `_meta.json.complete == True` filter and CANONICAL_NOVELS sort); new `_my_novel_section()` walks `my_novel/` without the completeness filter, ordered by lowercase name, reusing `_project_zh_title()` for `README.md` H1 中文 display name. `build()` emits children in order: AI Videos, Downloaded Novels, My Novel.
- projects/ai_video_management/apps/api/container.py — `novels_root` provider renamed to `downloaded_novels_root`; new `my_novel_root` Singleton; `NovelDownloader` + `NovelQuery` rebound to `downloaded_novels_root` (their `novels_root=` param name is preserved — it refers to the abstract "novels root" concept).
- projects/ai_video_management/apps/cli/novel_download.py — `_resolve_novels_root()` walks for `downloaded_novels/`; `NOVELS_ROOT` env-var name kept (backwards-compat). Progress label `novels_root:` → `downloaded_novels_root:`.
- projects/ai_video_management/libs/infrastructure/writers/novel__writer.py — module docstring path strings updated `novels/{slug}/` → `downloaded_novels/{cat}/{slug}/`; references follow-ups 096 + 111 + 113. Behaviour unchanged (writer receives Path via DI).
- projects/ai_video_management/libs/application/queries/novel__query.py — module docstring rewritten to clarify the new wiring (constructor param `novels_root` stays; container now points it at `downloaded_novels/`).
- projects/ai_video_management/apps/ui/src/types.ts — `display_name` comment extended to mention both `downloaded_novels/{category}/{slug}/` and `my_novel/{name}/` usage sites. No code change (frontend reads section names verbatim from the API).
- projects/ai_video_management/tests/test_tree_walker_consumer_walk.py — `test_tree_sections_order` updated to assert the three-section ordering; `test_novels_section_walks_repo_novels_dir` split into `test_downloaded_novels_section_walks_repo_downloaded_novels_dir` + new `test_my_novel_section_walks_repo_my_novel_dir`.
- projects/ai_video_management/tests/test_boot_smoke.py — `test_get_tree_returns_expected_sections` updated to expect three sections; docstring rewritten to track the 003 → 096 → 113 progression.
- projects/ai_video_management/tests/test_api_security_three_shapes.py — `test_get_tree_unguarded` updated to expect three sections.
- specs/development/ai_video_management/user_input/revised_prompt.md — surgical edit to technical-contract item 12 ("EXPOSED_TREE membership"): replaced the stale "single root" wording with "three roots — `ai_videos/**`, `downloaded_novels/**`, `my_novel/**`", noting the 003 → 096 → 113 progression and per-section behaviour (completeness filter on/off; README H1 display name).

Test results: `pytest tests/test_boot_smoke.py tests/test_api_security_three_shapes.py tests/test_tree_walker_consumer_walk.py` — 15 pass, 3 fail. The 3 failures are pre-existing wukong_juexing fixture failures (project deleted from disk earlier; reproduced against pristine working tree pre-113); zero regressions from this follow-up.

No conflicts found in: agent_refs/project/ai_video.md (no path-level reference to `novels/`), agent_refs/project/development.md (project-output rules untouched), CLAUDE.md (only `novels` reference is to the AI-video novel sub_type, unrelated to the top-level folder), apps/api/routes/novel__route.py (`/api/novels` endpoint is concept-named — still serves "downloaded-novel status"), libs/application/dtos/novel__dto.py + libs/application/commands/novel__command.py + libs/application/mappers/novel__mapper.py + libs/domain/value_objects/novel__valueobject.py (path-agnostic), follow-ups 096/101/102/103/104/105/106/107/108/109/110/111/112 (historical record; not retroactively updated). The original `novels/` top-level reference inside follow-up 111's changelog narrative (`forward-compat with in-flight follow-up 112 folder rename`) is preserved verbatim — it was correct at the time even though the rename later slipped to 113.


## Follow-up 114 — 2026-05-24 05:55:07
Source: user_input/follow_ups/114-20260524-055507-phase1-simplicity-refactor.md
Summary: Phase 1 simplicity refactor. Collapsed every aggregate's parallel error hierarchy (deleted `libs/infrastructure/errors/{actor,casting,character_video,downloads,file,frame,media,novel}__error.py` — 8 files; infrastructure now raises domain errors directly). Centralized HTTP error mapping at the FastAPI boundary via `app.exception_handler` registrations in `apps/api/app_factory.py` (one handler per domain error class), removing the per-endpoint try/except gauntlets and the `*_method_not_allowed` shim routes. Moved input validation into `GenerateActorsInputCdto.__post_init__` and `ActorAttrs.__post_init__` so neither Command nor Query has to call `validate_*` explicitly. Deduplicated the `LOOK_OPTIONS` / `ETHNICITY_OPTIONS` / `GENDER_OPTIONS` / `AGE_RANGE_OPTIONS` frozensets between `actor__writer.py` and `actor__valueobject.py` — domain is the single source of truth, infrastructure imports. Deleted the 32-line `libs/domain/entities/actor__entity.py` (a holder with no methods); moved `validate_actor_id` into the valueobject. Replaced `ActorAttrs.to_dict` with `dataclasses.asdict` at 7 call sites in `actor__writer.py`. Dropped `@runtime_checkable` from `ActorRepository`. Fixed the swallowed `OSError` in `app_factory.create_app` (actor dir creation now fails loudly if the filesystem rejects it). Net deletion: ~700 lines across infra-error files + per-endpoint translation blocks + manual input-DTO builders + method-not-allowed shims.

Auto-updated:
- projects/ai_video_management/libs/domain/errors/actor__error.py — added `ActorAlreadyDeletedError`, `ActorDeleteTargetExistsError`, `ActorDeleteFailedError`, `ActorGenerationDirMissingError`, `AssignmentsScanFailedError` (previously infra-only, now domain so infrastructure can raise them directly).
- projects/ai_video_management/libs/domain/errors/media__error.py — added `MediaTargetExistsError`, `MediaMoveFailedError` (same reason).
- projects/ai_video_management/libs/domain/value_objects/actor__valueobject.py — rewritten: `ActorAttrs.__post_init__` calls `self.validate()`; `validate_actor_id` moved in from the deleted entity; `to_dict` removed in favor of `dataclasses.asdict` at call sites.
- projects/ai_video_management/libs/domain/repositories/actor__repository.py — dropped `@runtime_checkable`; corrected `list_actors() -> list[ActorInfo]` (was the lying `list[ActorEntity]`); guarded the `ActorInfo` import under `TYPE_CHECKING` (transitional — Phase 2 will move `ActorInfo` to the domain).
- projects/ai_video_management/libs/domain/entities/actor__entity.py — DELETED (32 lines, no methods).
- projects/ai_video_management/libs/infrastructure/errors/{actor,casting,character_video,downloads,file,frame,media,novel}__error.py — DELETED (8 files). Only `legado_source__error.py` remains: those are internal to the scraper and never reach the route boundary.
- projects/ai_video_management/libs/infrastructure/writers/actor__writer.py — imports domain error classes; raises domain errors directly (replaced `InvalidAttribute` / `ActorNotFound` / `GenerationDirMissing` / `ActorDeleteTargetExists` / `ActorDeleteFailed` with the domain `*Error` counterparts); imports `ETHNICITY_OPTIONS` / `GENDER_OPTIONS` / `AGE_RANGE_OPTIONS` / `LOOK_OPTIONS` from the valueobject instead of redefining; `attrs.to_dict()` → `asdict(attrs)` at 7 call sites; `__all__` trimmed.
- projects/ai_video_management/libs/infrastructure/writers/casting__writer.py — imports domain `InvalidActorIdError` / `InvalidRoleError` / `DramaNotFoundError`; `__all__` trimmed.
- projects/ai_video_management/libs/infrastructure/writers/character_video__writer.py — imports the 12 domain error classes the three sub-writers raise. `CharacterVideoTruncator._validate_character_video_source` and `CharacterViewExtractor._validate_character_video_source` raise `InvalidCharacterVideoPathError` / `CharacterVideoNotFoundError`; `ShotConcatBuilder._validate_shot_md` raises `InvalidShotMdPathError` / `ShotMdNotFoundError` (disambiguating the shared `InvalidPath` / `NotFound` infra classes that previously needed the Command layer to disambiguate by which method was called).
- projects/ai_video_management/libs/infrastructure/writers/downloads__writer.py — imports domain `DownloadsDirMissingError`; `__all__` trimmed.
- projects/ai_video_management/libs/infrastructure/writers/file__writer.py — imports domain `UnsupportedFileExtensionError` / `FileTooLargeError` / `InvalidBodyEncodingError` / `FileNotInSandboxError` / `MissingIfUnmodifiedSinceError` / `StaleWriteError`; raises them directly (the infra `StaleWrite(current_mtime=...)` had an identical `current_mtime` attribute on the domain side, so the global 409 handler reads `exc.current_mtime` unchanged).
- projects/ai_video_management/libs/infrastructure/readers/file__reader.py — same import migration for the read path's 3 error classes.
- projects/ai_video_management/libs/infrastructure/writers/frame__writer.py — imports domain `FfmpegMissingError` / `FrameExtractFailedError` / `InvalidVideoPathError` / `NotVideoError` / `VideoNotFoundError`; `_validate_video_source` raises them directly.
- projects/ai_video_management/libs/infrastructure/writers/media__writer.py — imports the 12 media + casting domain error classes (including the new `MediaTargetExistsError` and `MediaMoveFailedError`). 12 `raise OldName(...)` → `raise NewError(...)` replacements (`AlreadyArchived` → `AlreadyArchivedError`, `MoveFailed` → `MediaMoveFailedError`, `TargetExists` → `MediaTargetExistsError`, etc.).
- projects/ai_video_management/libs/infrastructure/writers/novel__writer.py — imports domain `NovelChapterIndexParseError` / `NovelDownloadFailedError` / `NovelSourceUnreachableError`; raises them directly. (Substring collision repair: the initial replace_all of `DownloadFailed` → `NovelDownloadFailedError` matched inside the import-line `NovelDownloadFailedError`, producing `NovelNovelDownloadFailedErrorError`; fixed back to the intended single name.)
- projects/ai_video_management/libs/application/commands/{actor,casting,character_video,downloads,file,frame,media,novel}__command.py — all rewritten. Removed the `try / except InfraErr / raise DomainErr` translation blocks (infra now raises domain errors directly). Removed the now-unused infra-error imports. Kept the small cross-aggregate / domain logic that was actually doing work: `MediaCommand._refuse_if_actor_assigned` (called from `archive` and `delete`), `ActorCommand.delete`'s `find_assignments_for_actor` (wraps `OSError` in `AssignmentsScanFailedError` — the only remaining boundary translation needed). Validation calls (`attrs.validate`, `validate_batch_count`, `validate_resolution`, `validate_seeds`) deleted from commands — they now run inside the input Cdto's `__post_init__`.
- projects/ai_video_management/libs/application/queries/{actor,casting,file}__query.py — same try/except stripping; validation calls removed; `validate_actor_id` import moved from the deleted entity to the valueobject.
- projects/ai_video_management/libs/application/dtos/actor__dto.py — `GenerateActorsInputCdto.__post_init__` constructs an `ActorAttrs` (which validates) and calls `validate_batch_count` / `validate_resolution` / `validate_seeds`. `GenerateDiverseActorsInputCdto.__post_init__` calls `validate_batch_count` / `validate_resolution`. No Command/Query has to repeat these calls; constructing the Cdto either yields a valid value or raises a domain error.
- projects/ai_video_management/apps/api/app_factory.py — added a `_register_exception_handlers(app)` function that wires `app.add_exception_handler(DomainError, _handler)` for every domain error class the API surfaces. Plain handlers come from a `_PLAIN` table (status code + kind slug + whether to include `message=str(exc)` in the body); special handlers are inline (`StaleWriteError` carries `current_mtime`, `ActorAlreadyAssignedError` carries `actor_id` + `assignments`, `MediaTargetExistsError` / `ActorDeleteTargetExistsError` carry `target`, `DownloadsDirMissingError` carries `path`). A single `StarletteHTTPException` handler catches `status_code == 405` and returns the existing `{"detail": {"kind": "method_not_allowed"}}` body shape (with `Allow` from FastAPI's default) — replacing the per-endpoint `*_method_not_allowed` shim routes. The swallowed `OSError` on `actor_pool().actors_dir().mkdir(...)` was removed; the mkdir now propagates failures.
- projects/ai_video_management/apps/api/routes/_helpers.py — collapsed from 56 lines to 13. `method_not_allowed`, `actor_assigned_409`, `map_move_failure` deleted (the global exception handlers cover the same shapes). Only `file_security_headers` remains (used by `media__route.get_media` and `file__route.get_file`).
- projects/ai_video_management/apps/api/routes/actor__route.py — rewritten. Removed 6 `*_method_not_allowed` shim routes. Removed every `try/except → JSONResponse` block (handlers cover them). Replaced `_generate_input(body)` / `_diverse_input(body)` boilerplate helpers with `GenerateActorsInputCdto(**body.model_dump())` / `GenerateDiverseActorsInputCdto(**body.model_dump())`. Endpoint count and HTTP shapes unchanged.
- projects/ai_video_management/apps/api/routes/casting__route.py — rewritten. Dropped 2 method-not-allowed shims and all try/except.
- projects/ai_video_management/apps/api/routes/character_video__route.py — rewritten. Three routes collapsed to one-liners; dropped all try/except.
- projects/ai_video_management/apps/api/routes/downloads__route.py — rewritten. Dropped method-not-allowed shim + try/except.
- projects/ai_video_management/apps/api/routes/file__route.py — rewritten. Dropped method-not-allowed shim + try/except. `WriteFileInputCdto(rel_path=body.path, ...)` is kept (field names diverge `path` vs `rel_path` — the explicit construction is clearer than introducing a Pydantic alias).
- projects/ai_video_management/apps/api/routes/frame__route.py — rewritten. Dropped method-not-allowed shim + try/except.
- projects/ai_video_management/apps/api/routes/media__route.py — rewritten. Dropped 6 method-not-allowed shims, all try/except, and the route-level pre-check `command._refuse_if_actor_assigned(MediaPath(...))` (moved into `MediaCommand.archive` so the command — not the route — owns the cross-aggregate refusal rule, matching how `MediaCommand.delete` already worked).
- projects/ai_video_management/apps/api/routes/novel__route.py — rewritten. Dropped method-not-allowed shim.
- projects/ai_video_management/libs/application/commands/media__command.py — `MediaCommand.archive` now calls `_refuse_if_actor_assigned` (matching the existing pattern in `delete`); previously the route did the pre-check. `_refuse_if_actor_assigned` catches `InvalidActorIdError` (domain) instead of `InvalidActorId` (infra).

Test results: `pytest tests/` — 19 pass, 5 fail. The 5 failures all reference `ai_videos/wukong_juexing/` which has been deleted from disk; verified pre-existing by stashing this follow-up's changes and re-running (same 5 failures, with 18 passing — 1 fewer than after this follow-up, suggesting an incidental improvement from the cleaner error mapping). Zero regressions from this follow-up.

Phase 2 deferred (explicitly out of scope for 114): splitting `libs/infrastructure/writers/actor__writer.py` (2,431 lines) into `clients/kling__client.py` + archetype valueobject + sidecar file + a slimmed `ActorPool`; retyping `ActorRepository.preview_prompts() -> dict[str, object]` to a real dataclass so the `preview_to_qdto` mapper can drop its isinstance gauntlet; collapsing the mapper layer's pure-boilerplate methods. The `from __future__ import annotations` line at the top of every Python file is also intentionally left untouched (cosmetic-only).

No conflicts found in: final_specs/spec.md (no FR references either error-translation patterns or method-not-allowed routes — the spec describes endpoints and JSON shapes, both unchanged), findings/dossier.md, interview/qa.md, validation/* (the response shapes that validation cared about are byte-identical), agent_refs/project/development.md (§§ 1–6 still apply; the layering rules now read as "domain owns the enum surface; infrastructure raises domain errors directly when no second adapter is planned" — left for a future surgical agent_refs update if/when needed), CLAUDE.md (no change). The 17 follow-up references in narrative comments inside writer/command files (e.g. `Per follow-up 014:`) were left intact; they're institutional history, not behaviour.

## Follow-up 115 — 2026-05-24 11:30:00
Source: user_input/follow_ups/115-20260524-113000-voices-folder-and-prompt-generation.md
Summary: Add a `_voices/` voice-profile asset pool parallel to `_actors/`. Each voice profile is a Chinese-language dubbing prompt the user pastes into an external AI voice model (ElevenLabs / MiniMax / CosyVoice / OpenAI TTS / etc.) — the webapp itself does NOT call any voice-generation API. Voice generation is local text composition; the webapp's contribution is the prompt + an organized library + optional storage of user-supplied .mp3/.wav/.m4a samples (with in-grid playback). Mirrors the actor pool's grid / generator / casting / preview-confirm / archetype-bias UX but explicitly carves out all outbound-HTTP machinery (no Kling / no JWT / no 429 retry / no provider env vars).

Auto-updated:
- specs/development/ai_video_management/user_input/revised_prompt.md — appended follow-up 115 body.
- specs/development/ai_video_management/final_specs/spec.md — Goal updated to mention the two cross-drama asset pools (_actors + _voices). Out of scope: added "AI voice synthesis API calls — explicitly never (follow-up 115)". FR-7 EXPOSED_TREE root 1 extended with .mp3/.wav/.m4a. FR-13 extension allowlist extended with audio + carve-out that audio writes flow ONLY through FR-9v5 (not PUT /api/file). FR-87 cross-references _voices/ as a sibling system folder. NEW section "Voice pool + casting (follow-up 115)" added between Actor pool and Locked-block pill: FR-9v / FR-9v2 / FR-9v3 / FR-9v4 / FR-9v5 / FR-9v6 / FR-9v7 / FR-9v8 endpoint rows, FR-86v closed attribute schema (10 archetypes including the user's three named examples + 7 xianxia/palace siblings), FR-87v / FR-88v / FR-91v / FR-92v UX rows (sidebar / generator modal / grid / detail view), explicit "No external HTTP / no provider machinery" subsection enumerating the actor-side follow-ups (018 / 021 / 024 / 025 / 027 / 073 / 112) that DON'T apply, and the DDD + CQRS layering subsection listing every new file under apps/api/routes/ + libs/{application,domain,infrastructure}/. Stage-6 work-unit table got new row U8 (voice pool) depending on U3 + U6, strictly additive.
- specs/development/ai_video_management/validation/strategy.md — Per-work-unit applicability matrix gained the U8 row (acceptance ✓, bdd ✓, backend_tests ✓ with explicit "NO outbound-HTTP tests", security ✓ for FR-9v5 multipart upload only, e2e ✓ for VoiceView + VoiceGrid + audio playback, a11y ✓ for audio keyboard accessibility). NEW cross-cutting concern #7 captures the load-bearing no-HTTP grep-fail rule.
- specs/development/ai_video_management/validation/security.md — FR-to-check matrix gained 6 voice rows (FR-9v / FR-9v2 / FR-9v3 / FR-9v4 / FR-9v5 / FR-9v6 / FR-86v). NEW carve-out #8 with three sub-sections: SEC-VOICE-LOCAL-COMPOSITION (grep-fail rule covering httpx / requests / urllib / literal https URLs / new clients/voice_*.py files), SEC-VOICE-AUDIO-UPLOAD (extension allowlist + 10 MiB cap + sandbox + symlink-reject + atomic temp+replace + sidecar audio_sample row atomic update + Origin/Host gate + python-multipart CVE tracking), SEC-VOICE-DELETE (refuse-on-assignment mirror of follow-up-043 actor amendment).
- specs/development/ai_video_management/validation/acceptance_criteria.md — Appended U8 section with 9 automated scenarios (U8.1–U8.9) + 1 manual walkthrough (U8.M1) covering FR-9v / FR-9v2 / FR-9v3 / FR-9v4 / FR-9v5 / FR-9v6 / FR-9v7 / FR-9v8 / FR-86v / FR-87v / FR-88v / FR-91v / FR-92v. U8.1 explicitly grep-asserts zero httpx/requests/literal-https in libs/infrastructure/writers/voice__*.py.
- specs/development/ai_video_management/validation/bdd_scenarios.md — Added "AI voice synthesis API calls" to the explicitly-not-scenarios deferred list. NEW Feature 10 (Voice pool) with 6 scenarios (10.1 local-only-composition with socket.socket patch / 10.2 archetype overlay distinct prompts / 10.3 refuse-on-assignment delete / 10.4 audio upload extension+size+symlink gates / 10.5 voice-aware casting upsert preserving actor_id cell / 10.6 voice grid playback affordance with single shared Audio instance + e.stopPropagation()).
- specs/development/ai_video_management/validation/backend_tests.md — Appended Voice pool section listing 7 new pytest modules: test_voice_writer.py / test_voice_chinese_prompt.py / test_voice_no_outbound_http.py (critical severity — the load-bearing grep test) / test_voice_audio_upload.py / test_voice_delete_refuse_on_assign.py / test_casting_voice_column.py / boot smoke extension covering 9 new routes.
- specs/development/ai_video_management/validation/e2e.md — Appended Voice pool section with 2 new Playwright spec files (voice_grid.spec.ts + voice_view.spec.ts) running under both prod-mode and dev-mode, plus 3 new test fixture prerequisites (voice_0001 no-sample / voice_0002 + voice_0002.mp3 / _test_drama assignment).

No conflicts found in: interview/qa.md (early-stage interview from 2026-05-05; not backfilled with voice questions per surgical-patch policy), findings/dossier.md + findings/angle-*.md (research artifacts from stage 3; voice pool is a stage-4+ addition, no upstream conflict), validation/accessibility_and_manual.md (existing A11Y-01..12 + M-01..12 still apply to the chrome surfaces; voice-specific a11y is captured in the U8 row of strategy.md and as U8.M1 in acceptance_criteria.md), projects/ai_video_management/ source code (untouched in this turn — code changes follow once the user requests stage-6 execution against the updated spec). The 9 stage-6 endpoints (FR-9v / FR-9v2 / FR-9v3 / FR-9v4 / FR-9v5 / FR-9v6 / FR-9v7 / FR-9v8) are net-new; no existing route is modified.


## Follow-up 116 — 2026-05-25 23:17:32
Source: user_input/follow_ups/116-20260525-231732-per-block-inline-edit-ai-videos.md
Summary: webapp 的 inline edit prompt 模式从只覆盖第一个 fenced code block 升级到覆盖文件下每一个 fenced code block, 范围限定 ai_videos/ 下的 markdown. 解决: scene 档 (2 prompts) / character 档 (2-6 prompts, 含 dual-state) / actor 档 (2 prompts, face+body) 的非首块 prompt 之前只能开整个文件编辑器, 不符合 just-the-prompt 原则.

Auto-updated:
- projects/ai_video_management/apps/ui/src/lib/promptEdit.ts — 新增 findAllFencedCode / findNthFencedCode / extractNthFencedCode / replaceFencedCodeAt 索引化 API; 保留 findFirst/extractFirst/replaceFirst 老 API 后向兼容 (VoiceView 仍用).
- projects/ai_video_management/apps/ui/src/markdown/renderer.tsx — Renderer 新增 editEnabled / mtimeHttp / onSaved props; 引入 EditPromptContext + bodyToIndex map; CopyableCode 内嵌 ✏ Edit 按钮 + inline textarea + Save/Cancel; 409 stale_write 保留 buffer banner.
- projects/ai_video_management/apps/ui/src/components/Reader.tsx — isMarkdown fallthrough 给 Renderer 透传 editEnabled = path.startsWith(ai_videos/) + mtimeHttp + onSaved (refetch + 通知).
- projects/ai_video_management/apps/ui/src/components/ShotPairView.tsx — ShotPane 内 Renderer 透传新 props (顶部 ✏ Edit 快捷按钮保留作 power-user 入口编辑第一块).
- projects/ai_video_management/apps/ui/src/components/ImageRefView.tsx — 同 ShotPairView 透传新 props.
- projects/ai_video_management/apps/ui/src/components/ActorView.tsx — 大改: parsed.prompt (string|null) → parsed.prompts (ParsedActorPrompt[]); 抽出 ActorPromptCard 子组件持有 per-card 状态; parser parsePrompts + nearestHeadingBefore 用 H1/H2/H3 提取 section title; main view 改为 prompts.map(...) 循环.
- projects/ai_video_management/apps/ui/src/styles.css — 新增 .code-block-actions flex 容器 / .code-block-edit-btn 蓝色 variant / .code-block-save-btn 绿色 variant / .code-block-wrapper-editing 蓝边 / .code-block-textarea 等宽 + 最小高度 240px / .code-block-edit-error 红色 banner.

No conflicts found in: VoiceView (voice md schema 当前单 prompt, replaceFirstFencedCode 仍正确; 多 prompt 演化时按 ActorView 模式上升) / ParseFallback / Editor (全文件 textarea 编辑器, 用于 frontmatter/标题/负向段非 prompt 编辑场景) / api.ts (复用现有 putFile + ApiError) / 后端 routes/file__route.py (PUT contract 未变) / casting / actor 分配 / 删除 / 媒体抽帧 等所有其他功能 (改动仅集中在 renderer + 4 个 view 的 prompt section).

Known follow-up: Reader.tsx 的 SHOT_MD_RE 仍引用  旧路径 (xianxia_new/011 后应为 shots/shot\d+/shot\d+.md), 需单独 follow-up 修复, 否则 shotNN.md 在 isShotMd 分支可能 mismatch.


## Follow-up 117 — 2026-05-31 17:33:58
Source: user_input/follow_ups/117-20260531-173358-prompt-skeleton-plus-ai-dimension-refine.md
Summary: shot 视频 prompt 改为两段式 —— stage-6 自动生成「基础骨架版」(rule #12.4 全字段在、描述性维度只留 stub)，再在 ai_video_management webapp 里逐栏目用 ✨ 推荐 (后端实时调 Anthropic) 细化、智能合并落盘。建议来源 = 后端实时 LLM；范围 = 仅 shot 视频 prompt；SDK = 官方 anthropic；合并 = 空填入/非空追加。

Auto-updated:
- .claude/agent_refs/project/ai_video.md — rule #12.4 加 2026-05-31 amendment：basic skeleton 生成契约 (substantive-at-generation 字段 vs refine-later stub 字段；据此放宽 stage-6 validator；仅 shot 视频 prompt body)。[common surface — 适用所有 ai_video 项目]
- specs/.../final_specs/spec.md — 新增 §「Per-dimension AI prompt refinement (follow-up 117)」FR-96..FR-100 (骨架生成契约 / POST /api/prompt/suggest / 错误映射 / PromptStructuredEditor ✨ 细化 + 智能合并 / 优雅降级)。注意：FR-86..FR-95 已被 actor/voice follow-up 占用，故从 FR-96 起编号。
- specs/.../validation/security.md — 覆盖矩阵加 FR-97/FR-98 → SEC-OUTBOUND-ANTHROPIC；新增 carve-out #9 (第二个 outbound-HTTP 端点 / 只读不写文件 / env key 不入 EXPOSED_TREE / 优雅降级 / 数据 egress 提示)。
- specs/.../validation/acceptance_criteria.md — 覆盖矩阵加 FR-96..FR-100 → U9.*；新增 U9 work unit (5 场景：骨架生成内容校验 / suggest 端点 / 错误路径 / ✨ 组件行为+智能合并 / 优雅降级)。
- projects/ai_video_management/ 源码 (stage-6 执行)：新增 read-only prompt aggregate (anthropic__client + prompt__error/dto/mapper/query + prompt__route + container/app_factory/routes 接线) + 前端 api.ts suggestRefinements + PromptStructuredEditor ✨ RefinePanel + renderer 透传 shotContext/currentPath + styles.css .prompt-refine-*；anthropic>=0.40 入 requirements/pyproject。

No conflicts found in: interview/qa.md (2026-05-05 早期访谈，按 surgical-patch policy 不回填) / findings/dossier.md + angle-*.md (stage-3 研究产物，本功能为 stage-4+ 增量，无上游冲突) / validation/{strategy.md, bdd_scenarios.md, e2e.md, backend_tests.md, accessibility_and_manual.md} (既有断言仍适用；U9 自动化场景已在 acceptance_criteria.md 落点，深化 BDD/e2e 待用户触发 stage-5 重生成) / 现有 routes/endpoints (prompt aggregate 为净新增，未修改任何既有路由) / root pyproject.toml (不镜像 ai_video_management 专属依赖，照现状不动)。


## Follow-up 118 — 2026-05-31 19:42:55
Source: user_input/follow_ups/118-20260531-194255-episode-concat-shots-into-one-mp4.md
Summary: 新增 episode 级「合成本集视频」按钮 — 扫描本集每个 shot 的 renders/ 子文件夹取最新 mp4，按镜头顺序 ffmpeg 拼接成整集 ep{NN}.mp4 放本集文件夹（覆盖既有），无 renders/ mp4 的镜头跳过。扫描范围经用户确认为「仅 renders/ 子文件夹」以避开 2 秒角色合辑 shot{NN}_chars.mp4。

Auto-updated:
- specs/.../user_input/revised_prompt.md — 追加 Follow-up draft 118 块 (User words + What landed)。
- specs/.../final_specs/spec.md — 新增 §「Episode concat (follow-up 118)」FR-101..FR-104 (按钮锚点 / POST /api/concat-episode 选片契约 / ffmpeg concat-filter 输出契约 / 7 个错误映射)。FR-96..FR-100 已被 follow-up 117 占用，故从 FR-101 起编号。
- projects/ai_video_management/ 源码 (stage-6 执行)：新增 write-side episode aggregate — domain/errors/episode__error.py + infrastructure/writers/episode__writer.py (EpisodeConcatBuilder) + application/{dtos,mappers,commands}/episode__* + apps/api/routes/episode__route.py；container (episode_concat_builder Singleton + episode_command Factory) + routes/__init__ + app_factory 错误映射接线。前端 api.ts concatEpisode + Reader.tsx 按钮/handler/isEpisodeShotlist + styles.css .reader-episode-concat-btn。README.md ai_video-specific UX 加一条。tests/test_episode_concat.py 新增 (4 用例, stub ffmpeg)。

No conflicts found in: interview/qa.md + findings/* (stage-2/3 早期产物，本功能为 stage-4+ 净增量) / validation/* (既有断言仍适用；episode aggregate 为净新增端点，未改既有路由；深化 BDD/e2e/security 覆盖待用户触发 stage-5 重生成) / 既有 character_video 角色合辑 (per-shot, trim 2s) 与 frame/media/actor/voice/prompt 等所有其他功能 (episode 拼接为独立 aggregate，未触碰) / root pyproject.toml (无新依赖；ffmpeg 经已有 imageio-ffmpeg 提供)。

## Follow-up 119 — 2026-06-01 14:40:18
Source: user_input/follow_ups/119-20260601-144018-import-route-scene-orientation-plates.md
Summary: DownloadsImporter 支持把场景背景图归位到「朝向 plate 子 folder」(`scenes/{scene}/bg{N}_{方位}_{描述}/`)，按下载文件名里的**方位词**路由。根因：jimeng/即梦下载命名取 prompt `主体:` 行正文 (含方位词、不含完整 plate_id)，旧导入只匹配到 scene 根，朝向图无法归位。

Auto-updated:
- projects/ai_video_management/libs/infrastructure/writers/downloads__writer.py — 新增 `_PLATE_PREFIX` / `_PLATE_NON_DEST` 常量 + `_plate_orientation_token` (取 `bg\d+_` 后第一段=方位) + `_match_scene_plate` (scene 命中后按方位段子串匹配下沉到 plate folder)；`import_drama` 在 `chosen.kind=="scene"` 时调用，kind 记 `scene_plate`；模块 docstring 补述 scene-plate 路由。**只匹配方位段、不匹配描述段** (描述词会作相机走位词散落别朝向文件名→串档)。纯增量，不改 character/shot/scene-根 既有语义；仅当 scene 下存在 `bg\d+_*` 子 folder 时触发。

验证: 实跑 `import_drama("ai_videos/nvdi_tuihun_houhuile")` — 6 张背景 PNG 全部归位 bg1–bg6 + 自动重命名 (复用既有 rename_drama)，moved 全为 `scene_plate`，0 unmatched / 0 error。

No conflicts found in: media__writer (rename 步骤无需改) / 既有 character/shot/scene-根 路由 / spec.md (FR 待用户触发 stage-4 重生成时补登；本条为 stage-6 净增量) / validation/* (既有断言仍适用)。

## Follow-up 120 — 2026-06-02 13:19:16
Source: user_input/follow_ups/120-20260602-131920-downloads-scene-plate-overwrite-on-reimport.md
Summary: re-import 场景朝向图不 work —— 已有 `{plate_id}.png` 的 plate folder 再导入会生成 `{plate}1/{plate}2.png` 编号重复而非覆盖。fix 为 scene-plate 覆盖语义。

根因: `import_drama` move-then-rename 两步; plate folder 已有 `{plate_id}.png` 时新文件 move 进来变 2 个 png → `MediaRenamer._plan_folder` 多文件分支编号 (`{plate}1/2.png`), 不覆盖 (Windows rename 到已存在目标亦失败) → 累积重复。

Auto-updated:
- projects/ai_video_management/libs/infrastructure/writers/downloads__writer.py — 新增 `_clear_folder_media(folder)` (删顶层 media, 保留子目录/.md/非media/symlink); `import_drama` 在 `kind=="scene_plate"` 时 move 前先清空 plate folder 旧图+编号 junk (覆盖语义) → 之后单文件 rename 产出干净 `{plate_id}.png`; 通用同名 `dst` 由「报 target_exists 跳过」改为「unlink 覆盖」; docstring 补述。仅对 scene_plate 清空, 不动 character/scene-根/shot-renders 多文件共存。
- projects/ai_video_management/tests/test_downloads_import_shots.py — 新增 `test_scene_plate_routes_by_orientation_token` (补 follow-up 015 方位段路由回归, 此前无测试) + `test_scene_plate_reimport_overwrites_and_clears_numbered` (覆盖+清编号+.md 存活); pytest 6 passed。

验证: 实跑 `import_drama("ai_videos/nvdi_tuihun_houhuile")` —— 6 张新图归位 bg1-bg6, 旧 `{plate}1/2.png` junk 清除, 每 folder 恰 1 张 `{plate_id}.png`=新图, 0 unmatched/0 error。

No conflicts found in: media__writer (renamer 未改, scene_plate 清空后只剩单文件故不触发其多文件编号); character/scene-根/shot-renders 路由 (clear 仅 scene_plate); spec.md/validation/* (stage-6 行为修正, 净增量); 导入路由方位段逻辑 (follow-up 015 未动)。

## Follow-up 121 — 2026-06-07 06:03:22
Source: user_input/follow_ups/121-20260607-060322-prompt-edit-default-raw-text.md
Summary: 每个 prompt 给一个可直接改文字的 edit mode。现状已有 per-block ✏ Edit + raw/结构化双模式, 但默认进结构化表单; 改为默认 raw 文本编辑。

根因/现状: `ai_videos/` 下每个 ```text``` prompt 块右上角已有 ✏ Edit (renderer.tsx CopyableCode, editEnabled=path.startsWith("ai_videos/")) → 打开 PromptStructuredEditor (已含 📝 原文 raw textarea + 🪜 结构化表单 + 切换)。但 shot prompt 有可解析字段时默认进结构化表单, 非「直接改文字」。

Auto-updated:
- projects/ai_video_management/apps/ui/src/components/PromptStructuredEditor.tsx — 默认 `mode` 由 `initialParsed.fields.length>0 ? "structured" : "raw"` 改为恒 `"raw"`: 点 ✏ Edit 立即显示该 prompt 的可编辑文本框, 直接改字即存; 🪜 结构化逐字段表单仍可一键切回。
- projects/ai_video_management/apps/ui/src/markdown/renderer.tsx — 编辑提示文案改为「点它直接编辑该 prompt 的文字 (默认原文文本框, 改完即存; 也可切结构化表单)」。

机制 (已存在未改): raw textarea 编辑整块 body → 保存走既有 `replaceFencedCodeAt` + `putFile(..., ifUnmodifiedSince=mtimeHttp)` 单块替换 + 409 并发守卫, 不影响文件其他段落。

验证: `tsc --noEmit` 通过 (改动为字面量+注释+文案); 无 UI 测试断言旧默认; editEnabled 对 ai_videos/ 全开 → nvdi 所有 shot/scene prompt 均有此 edit mode (点 Edit 即可直接改文字)。

No conflicts found in: 保存机制/并发守卫 (复用未改); 结构化表单 (保留为可切换模式); 全文 Editor (✎ Edit 全文编辑器, 与本 per-block 编辑并存未动)。

## Follow-up 122 — 2026-06-07 06:16:39
Source: user_input/follow_ups/122-20260607-061639-edit-button-hidden-crlf-blockindex.md
Summary: md page 上 prompt 的 ✏ Edit 按钮根本不显示 (非 121 默认模式问题, 是按钮被隐藏)。根因: CRLF 行尾致 blockIndex 匹配失败。

根因: `CopyableCode.canEdit = editEnabled && blockIndex>=0 && mtimeHttp!==undefined`; `bodyToIndex` key 由源文件块体 (含 `\r\n`) 构造, 但 ReactMarkdown 渲染块体被规范化为 `\n` (LF), `trimmedBody` 是 LF → key 不匹配 → blockIndex=−1 → 按钮静默隐藏。nvdi 全部 .md 是 CRLF (本会话早先 Python `open(...,"w")` 写文件把 LF→CRLF; 仓库标准 LF, feng_shou_lu 即 LF)。

Auto-updated:
- ai_videos/nvdi_tuihun_houhuile/**/*.md (35 文件) — CRLF→LF (二进制 `\r\n`→`\n`), 块匹配立即对上 → 按钮出现 (无需 rebuild, 刷新页面即可)。
- projects/ai_video_management/apps/ui/src/markdown/renderer.tsx — `bodyToIndex` key + `trimmedBody` 均先 `.replace(/\r\n/g,"\n")` 再 trim, 即使源是 CRLF 也匹配 (防呆, 需 rebuild 生效)。

过程教训: Python 批改 ai_videos/ 下 .md 须保留 LF (`open(f,"wb")` 二进制写 或 `newline="\n"`, 勿默认 text 模式)。mozun_chongsheng 亦 CRLF (非本会话所致), 代码防呆对其也生效 (待 rebuild); 数据层 LF 转换本轮仅 nvdi。

验证: nvdi .md 残留 CRLF=0; tsc --noEmit 通过。

No conflicts found in: 121 默认 raw 模式 (本轮是按钮可见性的不同 bug); 保存机制; 其他项目内容。

## Follow-up 123 — 2026-06-13 17:03:59
Source: user_input/follow_ups/123-20260613-170359-perf-check-downloaded-mp4-and-score.md
Summary: 表演评分面板新增「让 Claude 检查已下载 MP4 并打分」按钮——定位 perf 条目 renders/ 下的成片，0 个/多个报错，恰好 1 个时组装 copy-paste prompt 让 Claude 抽帧打分。

Auto-updated (stage-6 generated outputs under projects/ai_video_management/):
- libs/infrastructure/readers/perf_check__reader.py — 新增 PerfCheckPromptReader：扫描 `_performances/<情绪>/perf_NNNN/renders/` 直接 .mp4 子文件，0→no_mp4 / >1→multiple_mp4 / 1→组装 prompt（含 ffmpeg 抽帧 + curl POST /api/perf-score who=Claude）。
- libs/application/queries/perf_check__query.py — 新增 PerfCheckPromptQuery（读侧，跳过 domain 层，与 shot_regen 同构）。
- apps/api/routes/perf_check__route.py — 新增 POST /api/perf-check-prompt（body {path}）。
- apps/api/container.py — perf_check_reader Singleton + perf_check_query Factory + 两条 import。
- apps/api/routes/__init__.py — 注册 _perf_check_router。
- apps/ui/src/api.ts — perfCheckPrompt() + PerfCheckPromptResult 接口。
- apps/ui/src/components/PerfScorePanel.tsx — 「🎬 让 Claude 检查 MP4 并打分」按钮 + handler/状态 + 只读 prompt 框 + 📋 复制（浅色主题真实变量）。

验证: python 导入 routes ok（/api/perf-check-prompt 已挂载）; tsc --noEmit 通过; reader 四分支冒烟（0/1/多/非法路径）全部正确。

No conflicts found in (downstream walk): interview/qa.md, findings/, final_specs/spec.md, validation/* — 表演库 / perf-score / shot-regen 子系统本就未进入 spec.md 与 validation 覆盖（这些 UI 微特性历来直接落代码），故无既有章节可作外科补丁；不在本轮 retro-spec 整个表演库（属 wholesale 反模式）。仅持久化 follow-up 草案 + 本 changelog + 代码。

## Follow-up 124 — 2026-06-13 18:38:59
Source: user_input/follow_ups/124-20260613-183859-actor-prompt-only-mode-and-downloads-import.md
Summary: 演员生成新增「只生成 prompt（默认）」模式——不调用 Kling，落地 actor 文件夹+sidecar，prompt 以 idNNNN[f|b] tag 打头；新增「📥 导入演员」一键扫 Downloads 按 tag 归位 face/body 图。

Auto-updated (stage-6 generated outputs under projects/ai_video_management/):
- libs/infrastructure/writers/actor__writer.py — 新增 ActorPool.create_prompts_batch（只写 tagged-prompt sidecar，无 Kling）；_reap_incomplete_folders 跳过含 sidecar 的待导入文件夹；_build_sidecar 加 pending_import；新增 _ACTOR_IMPORT_TAG + _actor_import_tag()。
- libs/infrastructure/writers/downloads__writer.py — 新增 DownloadsImporter.import_actors（镜像 import_performances，按 idNNNN[f|b] tag 路由，下载图经 _reencode_to_jpeg 转 JPEG 归位 face/body；无 sidecar 回填——body jpg 凭文件名后缀被 _find_actor_body_jpg 发现）+ _collect_actor_folders/_reencode_to_jpeg 辅助。
- libs/application/commands/actor__command.py — 新增 ActorCommand.create_prompts。
- libs/application/commands/downloads__command.py — DownloadsCommand.import_drama 增加 drama_name=="_actors" → import_actors 分流（与 _performances 同构；未新增 command 方法/路由）。
- libs/domain/repositories/actor__repository.py — 协议补 create_prompts_batch。
- apps/api/routes/actor__route.py — 新增 POST /api/actors/create-prompts。
- apps/ui/src/api.ts — createActorPrompts() + ActorPromptSlot/CreateActorPromptsResult 类型（导入复用既有 importFromDownloads）。
- apps/ui/src/components/ActorPoolGenerator.tsx — 模式切换（prompt-only 默认）+ 创建后的 prompt 面板（每 actor id + face/body 复制按钮）。
- apps/ui/src/components/Sidebar.tsx — actors 根新增「📥 导入演员」常驻按钮（复用 onRenameClick → importFromDownloads("ai_videos/_actors")）。
- tests/test_actor_prompt_only_roundtrip.py — 新增 create_prompts_batch → import_actors 往返测试 + 未匹配归 _not_matched。

判断点: 导入 tag 用 idNNNN[f|b]（ASCII + 显式 f/b）而非裸 0009，避免与文件名时间戳冲突并区分 face/body（沿用 perf 库 演NNNN tag 的防冲突教训）。

No conflicts found in (downstream walk): interview/qa.md, findings/, final_specs/spec.md, validation/* — 演员池生成器/出图历来直接落代码，未进入 spec.md 与 validation 覆盖，故无既有章节可作外科补丁；不在本轮 retro-spec 整个演员子系统（wholesale 反模式）。仅持久化 follow-up 草案 + 本 changelog + 代码。

## Follow-up 125 — 2026-06-16 10:00:00
Source: user_input/follow_ups/125-20260616-100000-bilingual-subtitle-burn.md
Summary: 双语 subtitles.md（中文||英文）+ 烧字幕三语言模式（zh/en/both）。
Auto-updated:
- libs/domain/value_objects/subtitle__valueobject.py — SubtitleCue 加 zh/en；parse 按 || 切双语；cues_to_ass(cues, lang) 三模式（ZH/EN 双 style，both 中上英下）；`|` 移出时间分隔符
- libs/domain/errors/subtitle__error.py — 新增 InvalidSubtitleLangError
- libs/infrastructure/writers/subtitle__writer.py — burn(rel, lang) 输出 *_subtitled_{zh|en|zhen}.mp4、lang 校验、按 lang 空文本→EmptySubtitles；scaffold 双语模板 + 从 ## 台词配音 取词
- libs/application/{dtos,mappers,commands}/subtitle__* — 透传 lang
- apps/api/routes/subtitle__route.py — BurnSubtitlesBody{path, lang}
- apps/api/app_factory.py — 注册 invalid_subtitle_lang(400)
- apps/ui/src/api.ts — burnSubtitles(path, lang); SubtitleLang 类型
- apps/ui/src/components/SiblingMedia.tsx — 单按钮→「💬中文/💬EN/💬中英」三按钮
- tests/test_subtitle_burn.py — 双语解析 + 三模式烧录 + 非法 lang + en-only 空校验
- README.md — 双语字幕烧录 UX 段
Tests: test_subtitle_burn.py 14 passed。全量 5 个失败均为既有(wukong_juexing 缺数据 + PUT-file 安全)，与本改动无关（已 stash 验证 HEAD 同样失败）。

## Follow-up 126 — 2026-06-16 11:00:00
Source: user_input/follow_ups/126-20260616-110000-subtitle-margins-naming-episode-lang.md
Summary: 字幕边距上移+左右加宽；烧字幕输出改 shot{NN}_{zh|en|zhen}.mp4（shot 文件夹根）；按语言合成整集（original/zh/en/both，最多 4 版本 ep{NN}[_suffix].mp4）。
Auto-updated:
- libs/domain/value_objects/subtitle__valueobject.py — MarginV 80→170(solo)/250-170(both 中上英下)、MarginL/R 60→120
- libs/infrastructure/writers/subtitle__writer.py — burn 输出 shot{NN}_{suffix}.mp4 于 shot 文件夹根（原 {stem}_subtitled_*）
- libs/infrastructure/writers/episode__writer.py — build(rel, lang) 按语言选 clip（original=renders 最新 / zh|en|both=shot{NN}_{suffix}.mp4）、输出 ep{NN}[_suffix].mp4、缺源跳过；EpisodeConcatResult.lang
- libs/application/{dtos,mappers,commands}/episode__* — 透传 lang；apps/api/routes/episode__route.py — ConcatEpisodeBody.lang
- apps/ui/src/api.ts — concatEpisode(path, lang)+EpisodeLang；burn 输出名变更已兼容
- apps/ui/src/components/Reader.tsx — 合成本集 4 语言按钮（原片/中文/EN/中英）
- tests/test_subtitle_burn.py — 输出命名断言更新；tests/test_episode_concat.py — 新增按语言合成 + both 命名测试
- .claude/agent_refs/project/ai_video.md rule 11c + README.md — 命名/边距/按语言合成 文档
Tests: test_subtitle_burn + test_episode_concat 20 passed；e2e 真机验证 burn→shot01_zh.mp4 / concat zh→ep01_zh.mp4 通过（artifacts 已清）。

## Follow-up 127 — 2026-06-16 12:00:00
Source: user_input/follow_ups/127-20260616-120000-subtitle-wrap-margins-os.md
Summary: 字幕长行溢出根因=WrapStyle 不换行→改自动折行（中≤13/英≤32 均分多行）+ WrapStyle 0；字号 72/52→64/46；both 合成单块防重叠；确认内心独白进字幕。
Auto-updated:
- libs/domain/value_objects/subtitle__valueobject.py — _wrap() 均分折行（CJK 硬切/拉丁按空格）；cues_to_ass 渲染层折行；WrapStyle 2→0；ZH 64/EN 46；both=单底部锚定块(中上英下)；删除 stacked 双 MarginV 常量
- tests/test_subtitle_burn.py — 新增长行折行 + 短行不折 + both 单块测试；both 旧"两事件"断言更新
- .claude/agent_refs/project/ai_video.md rule 11c — 自动换行/字号/both 单块/内心独白进字幕 文档
Tests: test_subtitle_burn + test_episode_concat 22 passed；e2e 校验 shot05 长台词折行(中≤13、英按空格)、both 单块不重叠。wushen EP1 14 文件全部含内心独白行(已校验)。

## Follow-up 128 — 2026-06-16 13:00:00
Source: user_input/follow_ups/128-20260616-130000-rename-skip-episode-final-cuts.md
Summary: 导入/重命名 button 的 rename pass 会递归遍历 episodes/ 把剧集成片 ep{NN}_{lang}.mp4 误改名为 ep01{i}.mp4（ep1_zh.mp4→ep012.mp4）。修复：rename_drama 永久排除整个 episodes/ 子树（renders/ 本就已排除，成片名得以保留），只规范化 characters/、scenes/ 及其 bg* plate 文件夹。

Auto-updated:
- libs/infrastructure/writers/media__writer.py — 新增 EPISODES_DIR_NAME 常量；rename_drama 的 excluded 集合无条件并入 episodes/，两处调用方（导入 button + 独立 rename button）均受益
- tests/test_downloads_import_shots.py — 新增 test_rename_pass_preserves_episode_final_cuts 回归测试（ep01_zh/ep01_en.mp4 不被改名）

No conflicts found in: interview/qa.md, findings/, final_specs/spec.md, validation/*

## Follow-up 129 — 2026-06-17 11:00:00（一键复制本集所有视频 prompt）
Source: user_input/follow_ups/129-20260617-110000-copy-all-video-prompts-button.md
Summary: episode 工具栏新增「📋 复制全部视频 prompt」按钮——一键把本集每个 shot 的【视频 prompt】块（only 视频 prompt、不含台词配音）按 shot 顺序拼接复制到剪贴板。纯前端、无新后端端点。

Auto-updated:
- apps/ui/src/lib/videoPrompts.ts（新）：extractVideoPromptBody（按前置 ## 标题分类取 video 块）/ episodeDirOf / shotMdPathsInEpisode。
- apps/ui/src/components/Reader.tsx：isEpisodeFile 工具栏加按钮 + onCopyAllVideoPromptsClick（从 knownPaths 过滤本集 shots→逐个 GET /api/file→提取 video 块→空行拼接→clipboard→toast 复制/跳过数）+ copyingPrompts state。
- apps/ui/src/styles.css：.reader-copy-prompts-btn（镜像 .reader-episode-concat-btn）。
- test/videoPrompts.test.ts（新·7 例）。
- README.md：新增「📋 复制全部视频 prompt」feature 条目（ShotPairView/ShotlistTableView 章节区）。

校验：tsc --noEmit 通过；vitest 全绿（旧 30 + 新 7 = 37）。只取 视频 prompt、显式排除 台词配音（测试覆盖）。

## Follow-up 130 — 2026-06-18 09:30:00（Sidebar 中文 display_name：drama + scene）
Source: user_input/follow_ups/130-20260618-093000-sidebar-zh-display-name.md
Auto-updated:
- libs/infrastructure/readers/tree__reader.py：新增 `_h1_zh`（《…》/（…）/·后段/整段 H1 提取）；`_project_zh_title` 扩展为 README《》→`1_立项/concept.md` H1（drama→武神觉醒）；`_sidecar_zh_label` 加 scene 分支（`parent=='scenes'` 读 `{name}.md` 的 `（中文）`→镇北王府正厅），scope 限定避免误改 character。
- tests/test_tree_display_name_zh.py（新·5 例，全过）。
- README.md：加「中文 display_name in sidebar」feature 条目。
校验：功能验证 wushen_juexing→武神觉醒、zhenbei_wangfu_zhengting→镇北王府正厅；新 5 测全过；前端 Sidebar 已用 display_name 无需改。
注：tests/test_tree_walker_consumer_walk.py::…wukong 失败为**既有 stale fixture**（项目已由 wukong_juexing 改名 wushen_juexing），与本改动无关。

## Follow-up 131 — 2026-06-18 11:00:00（分阶段结构破坏 assign/导入——drama_layout 解析器修复）
Source: user_input/follow_ups/131-20260618-110000-drama-layout-staged-paths.md
根因：staged 结构把 casting.md/characters/scenes→2_世界观人设/、episodes→4_剧本/；多处硬编码旧根路径，assign 断在前端 isCasting 正则不配新位置（CastingView 不渲染）+ 后端 writer 写错位置。
Auto-updated:
- 新增 libs/common/drama_layout.py（casting_md/characters_dir/scenes_dir/episodes_dir，根/stage 双兼容）。
- 后端接入：casting__writer、downloads__writer、sub_type_lookup、bgm_reference__reader、character_video__writer。
- 前端：Reader isCasting/isEpisodeFile 正则放开 stage 段；dramas.ts +findAssetDir（characters/scenes 根或 2_世界观人设/ 下找）。
- tests/test_drama_layout.py（5 例全过）。
校验：wushen(staged)/nvdi(root) 解析正确；tsc 干净；casting/character_video/downloads/tree 测试过。既有 stale wukong fixture 失败与本修复无关。

## Follow-up 132 — 2026-06-21 18:00:50
Source: user_input/follow_ups/132-20260621-180050-extract-last-frame-button.md
Summary: webapp 加「⏮ 生成末帧」按钮——一键 ffmpeg 截 shot 成片末帧成 PNG，作下一承接镜首帧（配合 ai_video.md 2026-06-21 跨镜首帧承接）。

Auto-updated:
- libs/infrastructure/writers/frame__writer.py — 新增 LastFrameResult + FrameExtractor.extract_last_frame（-sseof -3 + -update 1 取末帧）+ _shot_folder（落最近 shotNN 根）。
- libs/application/dtos/frame__dto.py — 新增 ExtractLastFrameResultCdto（{src,out}）。
- libs/application/mappers/frame__mapper.py — 新增 last_frame_to_cdto。
- libs/application/commands/frame__command.py — 新增 FrameCommand.extract_last_frame。
- apps/api/routes/frame__route.py — 新增 POST /api/extract-last-frame（复用 ExtractFramesBody；container 无需改、frame_command 已 wired；复用既有 frame 错误 handler）。
- apps/ui/src/api.ts — 新增 extractLastFrame + ExtractLastFrameResult。
- apps/ui/src/components/SiblingMedia.tsx — 新增 ⏮ 生成末帧 按钮（gated isShotVideoPath）+ state/handler/prop 三处 MediaTile wiring。
- tests/test_frame_last_frame.py — 新增 5 例（_shot_folder 分支 + 真 ffmpeg 截帧落 shot 根 + 校验错误路径）。
- README — 加「生成末帧」按钮说明。

校验: pytest 26 绿（boot smoke + scene_plate + intro_card + 本测试）；apps/ui tsc -b 干净。
No conflicts found in: 既有 frame extract / intro_card burn / 其余路由。

## Follow-up 133 — 2026-06-21 19:02:00
Source: user_input/follow_ups/133-20260621-190200-concat-seam-destutter.md
Summary: 整集 concat 时自动抹平承接镜接缝的 ~0.2s 重复定格帧卡顿（freezedetect 检测 + 裁头部静止段），硬切镜不动。

Auto-updated:
- libs/infrastructure/writers/episode__writer.py — 新增 _is_continuity_shot（读 衔接: 行·先判硬切）+ _detect_head_freeze + _parse_head_freeze（freezedetect 头部静止检测）+ _ffmpeg_exe；build() 对每个承接镜(i>0)算 head_trims、_ffmpeg_concat 在 filter 里 trim/atrim 裁头；ShotClip 加 trimmed_s。
- libs/application/dtos/episode__dto.py — EpisodeShotUsedCdto 加 trimmed_s。
- libs/application/mappers/episode__mapper.py — 透传 trimmed_s。
- apps/ui/src/api.ts — EpisodeShotUsed 加 trimmed_s。
- apps/ui/src/components/Reader.tsx — concat toast 加「抹平 N 处承接接缝」。
- tests/test_episode_concat.py — fake_concat 签名更新；+8 例（_parse_head_freeze 4 确定性 + 真 ffmpeg static-head 检测 + 承接裁/硬切不裁 build + _is_continuity_shot 硬切优先）。
- README — 合成本集视频 bullet 加承接接缝抹平说明。

修复（本次发现的真 bug）: 硬切文案「硬切（独立首帧·无承接帧）」含子串「承接」，_is_continuity_shot 必须先判「硬切」再判「承接」，否则所有硬切镜被误判为承接 → 会误裁。已由 test_is_continuity_shot 覆盖。
校验: pytest 47 绿；apps/ui tsc -b 干净。
No conflicts found in: 既有 concat 选片/排序/跳过/输出命名（原有 7 例全过）、frame/intro/subtitle 路径。

## Follow-up 134 — 2026-06-21 19:20:00
Source: 用户「把上限调整到1s吧」（承接接缝抹平裁帧上限）。
Summary: 承接接缝 head-freeze 裁帧上限 `_SEAM_MAX_TRIM_S` 0.6s → 1.0s（个别承接镜首帧静止段较长、0.6s 裁不净）。
Auto-updated:
- libs/infrastructure/writers/episode__writer.py — _SEAM_MAX_TRIM_S 0.6→1.0。
- tests/test_episode_concat.py — test_parse_head_freeze_caps_long_freeze 改断言 cap=1.0。
- README + ai_video.md (F) — capped 0.6s → 1s。
校验: test_episode_concat.py 14 绿。

## Follow-up 134 — 2026-06-22 00:05:30
Source: user_input/follow_ups/134-20260622-000530-seam-min-trim-duplicate-frame.md
Summary: 承接接缝残留 ~1 帧 micro-stutter（结构性重复帧 freezedetect 漏检）→ concat 承接镜 head_trim 保底裁 0.08s。

Auto-updated:
- libs/infrastructure/writers/episode__writer.py — 新增 _SEAM_MIN_HEAD_TRIM_S=0.08；build() 承接镜 head_trim=max(detected_freeze, min)，保底去结构性重复帧；docstring 注根因。
- tests/test_episode_concat.py — +test_build_承接_min_trims_structural_duplicate_when_no_freeze（detector stub=0 → 承接 trimmed_s==min、硬切/首镜=0）。

校验: pytest 22 绿（episode 15 + boot smoke）。
说明: 纯 concat/button 端、零 prompt 改动。残留速度突变型 hitch 留待 escalation（承接 seam 短 crossfade ~0.12s，未做）。
No conflicts found in: 既有 freeze-trim / 选片 / 硬切不裁 逻辑。

## Follow-up 135 — 2026-06-22 00:15:00
Source: user_input/follow_ups/135-20260622-001500-seam-crossfade.md
Summary: 承接 seam 残留速度突变 hitch → concat 加短 crossfade(~0.12s)；硬切 seam 仍硬切。

Auto-updated:
- libs/infrastructure/writers/episode__writer.py — `_ffmpeg_concat` 重写为左折叠：xfade/acrossfade 在承接 seam、concat=n=2 在硬切 seam；新增 `_SEAM_XFADE_S=0.12`、`_probe_duration`、`_CLIP_DURATION_RE`；audio-less 镜各自 anullsrc 静音轨（修原 ≥2 无音轨镜潜在双消费 filtergraph bug）；build() 计算并传 continuity 列表；docstring 更新。
- tests/test_episode_concat.py — fake_concat 签名 +continuity；+test_real_concat_xfade_at_承接_and_cut_at_硬切（真 ffmpeg 跑 xfade+concat 混合 filtergraph、3 无音轨 clip、产物合法 + 时长缩短 + 承接裁/硬切不裁）。
- README — 合成本集视频 bullet 加 xfade 折叠/anullsrc 说明。

校验: pytest 31 绿（episode 16 + boot smoke + frame_last_frame）。零 prompt 改动。
说明: 与 follow-up 134 保底裁叠加——先裁重复帧/hold（去定格卡顿），再 xfade（抹速度差）。
No conflicts found in: 选片/排序/跳过/输出命名/lang 变体（原 7 例全过）。

## Follow-up 135b — 2026-06-22 · 修 xfade 真机失败（timebase 不匹配）
来源: 用户实测「合成本集视频失败」。
根因: xfade 输出微秒 timebase(1/1000000)，但 normalize 后的 clip 是 1/30；**连续承接 seam（xfade→xfade）** 时第 2 个 xfade 的累加器(AVTB) 与下一 clip(1/30) timebase 不匹配 → ffmpeg `timebase do not match` 报错。先前集成测试只有 xfade→concat（concat 对 tb 宽容），漏掉 xfade→xfade。
修法: 每个 clip 视频链尾加 `settb=AVTB`，把所有输入与 xfade 输出统一到同一 timebase。
校验: 真跑 EP1 实拍 renders concat（zh + original 都 OK，12 镜 60s、承接镜裁 0.08 + xfade）；新增 `test_real_concat_consecutive_承接_xfades`（两连续承接→xfade→xfade 跑通）。pytest 32 绿。

## Follow-up 135c — 2026-06-22 · 修「concat 少了很多内容」（xfade offset 用错时长）
来源: 用户「为什么这次 concat 起来的视频少了很多内容」（EP1 ~129s 实际只出 60s）。
根因: xfade 的 `offset` 用了 `_probe_duration` 的**容器 Duration**，而容器时长取的是**更长的音轨**长度（实拍 render 音>视）。视频时间线被高估 → 第 1 个承接 seam 的 xfade offset 落到累加视频的真实末尾**之后** → xfade 只输出第一路、丢弃其后全部 → 输出截到 ~60s（shot06–12 全丢）。合成里的硬切 concat 对此宽容、故只在 xfade 暴露。
修法: ① `_probe_duration` 改测**视频流时长**（`-map 0:v:0 -c copy -f null -` 取末尾 `time=`，demux 不解码、快），不再用容器 Duration；② xfade offset 减一帧 epsilon，确保转场严格落在累加流内。
校验: 真跑 EP1 实拍 → zh + original 均 **127.4s 全 12 镜**（不再 60s）；新增回归测试 `test_real_concat_preserves_length_when_audio_longer_than_video`（音>视的 clip + 双连续承接 xfade，断言不被截断）——旧合成测试用纯视频 testsrc（容器==视频）复现不出此 bug。pytest 全绿（episode 18 + boot/frame/intro）。

## Follow-up 136 — 2026-06-22 · 撤销承接 seam 交叉淡化，回到干净 butt-join
来源: user_input/follow_ups/136-20260622-003000-revert-seam-crossfade.md（用户「效果不行，两个shot中间有一瞬间图片的转换，明显不契合」）。
根因: follow-up 135 的 xfade 把承接 seam 两帧 dissolve，但保底裁帧后两帧已不再相同，溶解被肉眼读成"一瞬间图片切换"，比顿挫更出戏。交叉淡化是错的工具——承接要的是去重复帧后的干净连续切。

Auto-updated:
- libs/infrastructure/writers/episode__writer.py — `_ffmpeg_concat` 去掉 xfade 左折叠，改回单次 `concat=n=N:v=1:a=1`；删 `continuity` 形参与 `_SEAM_XFADE_S` 常量、改注释；build() 不再计算/传 continuity。保留 134 保底裁 + audio-less anullsrc + `_probe_duration` 测视频流时长（修「少了很多内容」）。
- tests/test_episode_concat.py — fake_concat 签名去掉 continuity；两个 xfade 命名的真 ffmpeg 集成测试改名/改 docstring 为 butt-join 语义（仍校验连续承接产物合法 + 音>视不截断）。

校验: 真跑 EP1（wushen_juexing）zh + original 均 129.4s 全 12 镜（撤前 bug 截到 60s）。pytest 25 绿（episode + boot smoke）。零 prompt 改动。
No conflicts found in: 选片/排序/跳过/输出命名/lang 变体/首尾帧承接裁帧（保留）。

## Follow-up 137 — 2026-06-22 · 承接接缝两侧裁速度坡道（消 0.2s 卡顿）
来源: user_input/follow_ups/137-20260622-010000-seam-trim-both-sides-velocity-ramp.md（用户「还是有一瞬间的卡顿估计0.2秒左右」）。
根因: butt-join 去掉重复帧后仍卡顿——卡顿是**两侧速度坡道**（i2v 出镜减速收束到末帧、入镜从该静止帧加速），帧在慢变非定格，-55dB freezedetect 漏检；且原先只裁入镜单侧。松阈值实测：入镜头慢帧 0.13–0.22s、出镜尾慢帧 0.12–0.20s。

Auto-updated:
- libs/infrastructure/writers/episode__writer.py — 承接接缝两侧裁：入镜头部 freezedetect(-45dB)+floor、出镜尾部固定 0.15 裁（尾部碎片化检测会过裁故确定性裁）。常量 noise -55→-45dB、`_SEAM_MIN_HEAD_TRIM_S(0.08)`→`_SEAM_MIN_EDGE_TRIM_S(0.15)`、`_HEAD_EPS`→`_EDGE_EPS`；删除短暂加过的 tail-freeze 检测助手（碎片化不可靠）。build() 计算 head_trims+tail_trims；`_ffmpeg_concat` +tail_trims，每 clip `trim=start=H:end=(dur-T)`、eff/anullsrc 同步。
- tests/test_episode_concat.py — fake_concat +tail_trims；承接 trim 断言改为"前驱尾部也裁 _SEAM_MIN_EDGE_TRIM_S"；import 常量改名。
- README — 承接接缝 bullet 改为"两侧裁速度坡道"，去 xfade 残留描述。

校验: 真跑 EP1（wushen_juexing）zh + original 均 127.6s 全 12 镜；承接镜 06/07/11/12 头部裁、前驱 05/10 拿 0.15 尾裁——两侧都裁实锤。pytest 25 绿。零 prompt 改动。是否真消感知卡顿待用户肉眼确认。
No conflicts found in: 选片/排序/跳过/输出命名/lang 变体/视频流时长探测（保留）。

## Follow-up 138 — 2026-06-22 · 合成帧率跟随源（消 24→30 pulldown judder）
来源: user_input/follow_ups/138-20260622-013000-concat-match-source-fps-no-pulldown-judder.md（用户「还是不顺」）。
根因: 前三轮只动接缝但始终不顺——真因是合成把 ~24fps（VFR）源硬转 30fps，4:5 pulldown 每 5 帧复制 1 帧，mpdecimate 实测 30fps 输出 ~30% 是复制帧＝全片 judder，与接缝无关。

Auto-updated:
- libs/infrastructure/writers/episode__writer.py — 输出帧率改为跟随源：新增 `_target_fps`(中位+snap+回落)/`_probe_fps`(解析 `ffmpeg -i` "NN fps")/`_snap_fps`(取最近标准帧率、容差 1.5 内才 snap)。常量 `_CONCAT_TARGET_FPS=30`→`_CONCAT_FALLBACK_FPS=30`+`_STANDARD_FPS=(24,25,30,50,60)`+`_FPS_SNAP_TOL=1.5`+`_FPS_RE`。`_ffmpeg_concat` 算 target_fps 并用于 fps 滤镜。
- tests/test_episode_concat.py — +3 测试（_snap_fps 边界含 24/25 重叠取最近、_target_fps 24源→24 不上变、不可探测回落 30）。

校验: 真跑 EP1（wushen_juexing）zh 输出 23.89fps（≈24 原生）、12 镜 127.6s；复制帧 ~30%→~3%（剩为真静止内容）。pytest 28 绿。零 prompt 改动。感知是否真顺待用户确认；若仍残留接缝感属 i2v 两段运动轨迹不连续（生成侧问题，裁帧/帧率不可消）。
No conflicts found in: 选片/排序/跳过/输出命名/lang 变体/承接两侧裁/视频流时长探测（均保留）。

## Follow-up 139 — 2026-06-22 · 合成时自动去死帧（mpdecimate 压掉镜头内卡死段）
来源: user_input/follow_ups/139-20260622-020000-concat-defreeze-mpdecimate.md（用户「还是有明显的一秒跳跃」→ 诊断为源 clip 内部长近静止段 → 用户选「合成时自动去死帧」）。
根因: 前四轮只动接缝/全局帧率治不了，因为卡顿是镜头**内部**的 1–3s 长近静止段（i2v 生成卡住），freezedetect 严阈值看不出（慢漂移非定格）。实测 shot06 源 ~3.6s、shot08 ~2.4s、shot09 ~1s 近静止，且都在镜头中部。

Auto-updated:
- libs/infrastructure/writers/episode__writer.py — 每 clip 视频链加去死帧：`{_DECIMATE},setpts=N/{target_fps}/TB`（替原 fps 滤镜），`_DECIMATE="mpdecimate=hi=64*24:lo=64*12:frac=0.2"`（自适应：卡死镜削~26%、运动镜~3%）。concat 转 video-only（a=0[outv]）+ 额外 lavfi anullsrc 输入映射为静音轨 + -shortest。删 per-clip 音频段构建与 `_probe_has_audio`（去死帧后 a/v 无法逐 clip 对齐；真台词/BGM 后期 mux，本音轨 throwaway）。保留 seam 两侧裁/视频流时长探测/帧率跟随源/butt-join。
- tests/test_episode_concat.py — `_silent_clip`/`_clip_audio_longer` 加 `noise=alls=40:allf=t+u` 逐帧运动（否则近静止 testsrc 被 decimate 收掉、时长断言失效）。

校验: 真跑 EP1（wushen_juexing）zh 127.6→113.3s、original→113.5s，均 24.01fps 12 镜；压掉 ~14s 死气；长 hold(≥0.35s) 从 ~10s+ 降到 zh 1.8s/original 3.6s。pytest 28 绿。零 prompt 改动。残留散点 hold 若仍卡可调 lo=64*16/frac=0.15。
No conflicts found in: 选片/排序/跳过/输出命名/lang 变体/承接两侧裁（保留）。

## Follow-up 140 — 2026-06-22 · 去死帧后恢复同步音轨（修「没声音」回归）
来源: user_input/follow_ups/140-20260622-024500-defreeze-keep-synced-audio.md（用户「有一个新的 bug 是出来的视频没声音了」）。
根因: follow-up 139 去死帧时为绕开音画错位，把 concat 改成 video-only + 单条静音轨。但 12 个源 render 全带 AAC 音轨（i2v 自带环境音/人声），用户预览要听 → 误判为 throwaway 导致没声音。

Auto-updated:
- libs/infrastructure/writers/episode__writer.py — 恢复每镜真音轨并保持同步：测每镜去死帧后时长 ldur，音轨 `atempo=window/ldur` 时间匹配（卡死镜音频略快但同步；无卡死 tempo≈1 no-op）。concat 恢复 v=1:a=1[outv][outa]，去掉单条 anullsrc 输入。抽出 `_video_chain`（去死帧链构建一次、供测时长与 seg 共用保证帧数一致）；+`_decimated_duration`（跑链到 null 读末尾 time=）；+`_atempo_chain`（单 atempo 仅 [0.5,2]，>2 拆 ≤2 乘积）；恢复 `_probe_has_audio`（无音轨镜走 anullsrc 定长 ldur）。_DECIMATE 注释更新（不再说 a/v 不可同步）。保留 139/138/137/135c/136。
- (无测试改动；28 测试仍绿，含合成 noise clip)

校验: 真跑 EP1（wushen_juexing）zh video=113.9s/audio=114.0s、original 114.0/114.0，has_audio=True、漂移 0.08s（同步）。pytest 28 绿。零 prompt 改动。
另记: shot11→12 仍有明显跳，查证为两段独立生成的"背身朝窗"近静止镜位姿对不齐（无运动遮掩→跳切感），属生成侧内容问题，裁帧/去死帧/帧率均不可消；建议重生成 shot12（真从 shot11 末帧承接）或改硬切或加运动。
No conflicts found in: 选片/排序/跳过/输出命名/lang 变体/去死帧阈值/帧率跟随源（均保留）。

## Follow-up 141 — 2026-06-22 · 撤销去死帧+变速，回到忠实拼接
来源: user_input/follow_ups/141-20260622-031500-revert-defreeze-faithful-concat.md（用户「为什么拼接好的视频有些地方语速明显比原视频快了很多」+「感觉整体秒数跟原来不一致」）。
根因: 去死帧(139)删镜头内长近静止段、变速(140)把整镜音频 atempo 到去死帧后时长。但卡死段**压着台词**（freezedetect 视频区间与 silencedetect 音频区间不重合，shot06 视频 3.1–5.9s 冻结时音频非静音）→ atempo 对整镜音频统一加速含说话部分=语速明显快；去死帧压短总时长(EP1 130→113s)=与原始不符。去死帧与"卡顿压台词"素材根本冲突，是错的工具。用户选回到忠实拼接。

Auto-updated:
- libs/infrastructure/writers/episode__writer.py — 撤销 139/140：删 `_DECIMATE` 常量 + `_video_chain`/`_decimated_duration`/`_atempo_chain` 方法。`_ffmpeg_concat` 回到忠实拼接：每镜视频 `trim→setpts→scale→pad→setsar→fps={target}`（去 mpdecimate/setpts=N/FR/TB），音频 `atrim(window)→asetpts→aresample→aformat`（无 atempo，自然语速原长），anullsrc 按 eff=end-h 定长，concat v=1:a=1。保留 seam 两侧裁(137)/帧率跟随源(138)/视频流时长探测(135c)/butt-join(136)/`_probe_has_audio`。
- tests/test_episode_concat.py — 还原 `_silent_clip`/`_clip_audio_longer` 的 `noise`（仅去死帧需要、已删）+ docstring。

校验: 真跑 EP1（wushen_juexing）：源 clip 合计 130.2s，输出 zh/original 均 129.6s（差 0.6s＝承接 seam 微裁），has_audio=True、自然语速。pytest 28 绿。零 prompt 改动。
遗留（生成侧，concat 不可修，需重生成对应镜头）: 镜头内「边说话边卡画」的停顿（shot06/08 等）；shot11→12 近静止背身镜位姿对不齐的跳切。
No conflicts found in: 选片/排序/跳过/输出命名/lang 变体/帧率跟随源/承接两侧裁（均保留）。

## Follow-up 142 — 2026-06-22 21:15:00
Source: user_input/follow_ups/142-20260622-211500-concat-crossdissolve-soften-cuts.md
Summary: 合成镜头交接「先跳一下才切」/硬切感强 → 每对相邻 clip 加交叉叠化(xfade+acrossfade)柔化并盖住尾部跳帧。

Auto-updated:
- libs/infrastructure/writers/episode__writer.py — _ffmpeg_concat 由 concat 改 xfade+acrossfade 链；新增 _XFADE_DUR=0.25 + xdur 钳制；map 改最终标签
- tests/test_episode_concat.py — preserves_length 阈值 2.0→1.4(叠化重叠)、consecutive_承接 docstring 更新
- README.md — 合成本集视频 段落更新为交叉叠化

No conflicts found in: final_specs/spec.md, validation/*, 其余 routes/commands/dtos

## Follow-up 143 — 2026-06-22 21:30:00
Source: user_input/follow_ups/143-20260622-213000-revert-crossdissolve-back-to-hardcut.md
Summary: 撤销 142 交叉叠化（用户：没变柔和、还不如硬切），退回忠实硬拼接(=141 状态)。

Auto-updated:
- libs/infrastructure/writers/episode__writer.py — _ffmpeg_concat 恢复 concat butt-join + map [outv]/[outa]；删 _XFADE_DUR；seam 注释记两次叠化均回退
- tests/test_episode_concat.py — preserves_length 阈值 1.4→2.0 回退、consecutive_承接 docstring 回退
- README.md — 合成本集视频 段落删交叉叠化、恢复忠实拼接描述

No conflicts found in: final_specs/spec.md, validation/*, routes/commands/dtos

## Follow-up 144 — 2026-06-22 22:00:00
Source: user_input/follow_ups/144-20260622-220000-seam-concat-tool-trim-dedup-rife.md
Summary: 新增 tools/seam_concat.py 处理 Seedance 首尾帧链式拼接的接缝顿挫(trim+去重复帧默认 / --rife 光流补帧 opt-in)。

Auto-updated:
- tools/seam_concat.py — 新建独立工具

No conflicts found in: episode__writer.py(webapp 保持忠实硬拼接不动), final_specs/spec.md, validation/*

## Follow-up 144b — 2026-06-22 22:30:00 (amend)
Source: 同 144（用户反馈 trim+dedup「还差一点」）
Summary: 残留为缓动速度落差，需补帧。给用户「先调大 --trim(0.18/0.25)」即时手段；把 seam_concat.py 的 RIFE 调用由 dir-mode -n 改为最稳的单帧对 -0/-1/-o 递归(3 中间帧)。

Auto-updated:
- tools/seam_concat.py — _rife_bridge 改单帧对递归 + 新增 _rife_mid 助手（本机无 RIFE 二进制，按文档接口编写、失败安全退化）

## Follow-up 145 — 2026-06-22 23:30:00
Source: user_input/follow_ups/145-20260622-233000-rife-audio-fix-and-wire-into-episode-concat-button.md
Summary: 装好 RIFE 并本机实测 EP1 承接缝补帧获认可；seam_concat 加回音轨 + 逐缝承接/硬切控制(--seams)；把 RIFE 补帧接进 webapp「合成本集视频」button(默认开复选框，承接缝走 RIFE、硬切不动)。

Auto-updated:
- tools/seam_concat.py — _render_body/桥段保留+静音补齐音轨、末段 concat v=1:a=1、新增 --seams 逐缝承接/硬切、seam_concat() 返回 bridge 数、main() stdout utf-8
- episode__writer.py — build(rel,lang,rife)、_is_continuity_shot 自动生成 seam 谱、rife 时按 sandbox root 路径复用 tools/seam_concat.py、exe 缺失明确报错、结果加 rife_used/rife_bridges
- episode__dto.py / episode__mapper.py / episode__command.py / episode__route.py — 透传 rife 入参 + rife_used/rife_bridges 出参
- apps/ui/src/api.ts — concatEpisode(path,lang,rife) + 结果类型加 rife 字段
- apps/ui/src/components/Reader.tsx — 「🪄 RIFE 补帧」复选框(localStorage 持久化默认开)、toast 显示补帧缝数
- apps/ui/src/styles.css — .reader-episode-rife-toggle 行内对齐样式

No conflicts found in: final_specs/spec.md, validation/*, tests/test_episode_concat.py(21 项全过，rife 默认 False)

## Follow-up 145b — 2026-06-23 (amend)
Source: 同 145（用户反馈：声音恢复后效果反不如无声版——seam1 出现明显停顿、seam2 出现乱码）。
Diagnose（抽帧实证）: seam1(shot10→11) 两端帧近乎重复(mean|Δ|≈11/255)→RIFE 补出近静止桥=停顿(且我塞的静音空洞放大为死寂)；seam2(shot11→12) 是景别/机位跳变(mean|Δ|≈73/255)→RIFE 把整个人缩放morф=乱码。结论：RIFE 只在「中段运动」可用，太像→停顿、太不像→乱码。
Fix:
- tools/seam_concat.py — _rife_bridge 加**运动门限**：用 ffmpeg blend=difference→signalstats YAVG 量两端帧 mean|Δ|，落在 [20,55] 才补帧，否则退回干净 trim+butt-join（seam2=74 跳变被挡）。桥段音频改为**真·被裁掉的接缝内容**(前镜尾[dur-trim,dur]+后镜头[0,trim]，取自原始 clip、apad/atrim 到桥长)——连续环境声、非死寂(去 seam1 停顿感)、非 body 音频回声、且长度=桥长不破同步。门限/桥音频对 webapp button 自动生效(builder 复用本工具)。
- 既有 21+49 项测试全过；EP1 实测：seam2 自动硬接、seam1 补 1 桥带连续环境声、含 aac 44100 stereo。

No conflicts found in: episode__writer.py(逻辑不变，仅复用更新后的 tool), dto/mapper/route/UI(rife_bridges 现因门限可能为更小值，语义不变)

## Follow-up 145c — 2026-06-23 (amend)
Source: 同 145（用户：ep4 shot6→7 用 RIFE 还是有点跳转）。
Diagnose（抽帧实证）: shot6→7 全局 mean|Δ|≈12，被 MIN=20 当「near-still」挡掉、实际走的是 butt-join（没用 RIFE）。但两帧是同机位、大段静止背景(寺庙)+两个主体小幅移动——RIFE 中点帧实测干净无 morф。根因：全局 diff 被静止背景稀释，MIN=20 过高，把「背景静、主体动」这类 RIFE 安全甜区误判为静止。
Fix:
- tools/seam_concat.py — _BRIDGE_MIN_DIFF 20→6（低端只挡「真冻结/重复帧」diff≈0 的无意义桥；桥已带真环境声后，小幅运动桥不再读作停顿）。高端 MAX=55 不变（morф 防护是承重项：ep4 的 56/57 跳变仍正确挡掉）。
- 复核：ep4 重建 → 桥 2→4（含 shot6→7），仅 56/57 两条跳变硬接；ep3 同步重建。webapp button 自动生效。

No conflicts found in: episode__writer.py/dto/mapper/route/UI（仅工具阈值变化）

## Follow-up 146 — 2026-06-23 20:29:10
Source: user_input/follow_ups/146-20260623-202910-actor-gendered-wardrobe-frontal-face.md
Summary: Actor 生成 prompt 两修——① 服装按性别区分（修"男角色穿女式吊带背心"）；② 所有 actor 锁正脸朝镜头（否则捕捉不到面部细节）。根因：`_WARDROBE_REVEALING_ZH` 男女通用一条写死"吊带背心"（女款名词→Kling 给男也套女背心）；三个 header 仅 `_HEADER_FACE` 带正脸约束，`_HEADER_BODY`/`_HEADER_COMBINED`（主用）缺，且 seductive 面部细节含"微微侧脸"与正脸冲突。

Auto-updated:
- `projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py` — 删 `_WARDROBE_REVEALING_ZH`，新增 `_WARDROBE_MALE_ZH`（无袖紧身运动背心【男款圆领·绝非女式吊带背心】+ 运动短裤·胸肌肩背轮廓）/ `_WARDROBE_FEMALE_ZH`（紧身吊带背心·胸型大小）+ `_wardrobe_for(gender_slug)`；`_structured_lines` 用 `_wardrobe_for(gender_slug)`、`_build_with_picks_lines` 用 `_wardrobe_for(attrs["gender"])`（覆盖 face/body/combined 全 builder）；三个 header（FACE/BODY/COMBINED）统一加"正脸正面平视镜头（绝不侧脸·不转头·不低头·不仰头·面部完整正对镜头便于捕捉五官细节）"；`_LOOK_FACE_DETAIL_ZH["seductive"]` 的"微微侧脸、颈线慵懒妩媚"→"下颌微收、眼神慵懒直视镜头、媚意自生"；`_NEGATIVE_PROMPT_ZH` 新增正脸约束组（侧脸/侧面/半侧脸/3-4侧脸/转头/扭头/回头/低头/仰头/脸朝向一侧/面部转开/背对镜头/后脑勺/不看镜头/profile view/side face）。

Verified: `tests/test_actor_prompt_only_roundtrip.py` 2 passed；实跑男/女 combined prompt 确认服装分化（男运动背心 vs 女吊带背心）+ 两 header 均含正脸约束。

No conflicts found in: actor__writer.py（仅消费 builder 输出·无需改）、actor__command.py、actor__route.py、ActorPoolGenerator.tsx（前端不含服装/朝向文案）。

## Follow-up 146 — 2026-06-23
Source: 用户提议——点击「合成本集视频」不要立即拼，而是弹窗逐个衔接处选 硬拼/RIFE(+参数)，确认后再生成，方案存文件可复现。
Why: 全局帧差门限无法在 40~50 区间可靠区分「大幅连续运动」与「换机位/构图」(ep4 shot9→10=46 morф，但 ep3 有 44~46 是好的)，没有单一阈值正确。把决策交给人 + 缩略图，是正解；门限降级为"建议默认"。
新增「拼接方案」面板(SeamPlanModal)：
- 点击 原片/中文/EN/中英 → 弹窗，POST /api/episode-seams 拉每个衔接的 承接/硬切 + 前镜末帧/后镜首帧缩略图 + 自动帧差 + 建议。
- 硬切缝锁定「硬拼」；承接缝可选 硬拼/RIFE，RIFE 下可调 trim(裁切) + 补帧密度(depth 1–4/自动)。
- 「生成」→ POST /api/concat-episode {plan}，按选择拼接(用户选择覆盖自动门限)，并把方案存 epNN/seam_plan.json；重开面板自动载入。

Auto-updated:
- tools/seam_concat.py — seam_concat() 加 plan 参数(每缝 {bridge,trim,depth} 覆盖 seams+门限)；_rife_bridge 加 gate/depth_override；门限 MAX 55→40(仅作建议默认)。
- libs/infrastructure/writers/episode__writer.py — analyze_seams()(承接判定+缩略图 base64+帧差建议+载入已存方案)、build(plan)、_plan_for_used/_save_plan/_load_plan/_seam_thumb；SeamInfo/SeamAnalysis。
- libs/application/{dtos/episode__dto.py(SeamInfoQdto/SeamAnalysisQdto),mappers/episode__mapper.py(analysis_to_qdto),commands/episode__command.py(plan),queries/episode__query.py(新建 analyze_seams)}。
- apps/api/{container.py(episode_query),routes/episode__route.py(POST /api/episode-seams + concat plan，SeamPlanEntry from 别名)}。
- apps/ui/src/{api.ts(analyzeEpisodeSeams+SeamInfo/SeamPlanEntry+concatEpisode plan),components/SeamPlanModal.tsx(新建),components/Reader.tsx(lang 按钮改开弹窗，移除旧 RIFE 复选框),styles.css(.seam-modal*)}。

No conflicts found in: test_episode_concat.py(21 过); 5 项预存无关失败(wukong_juexing 数据/put_file loopback，未触及本功能)。

## Follow-up 146b — 2026-06-23 (amend)
Source: 用户：点击生成 ep4 后文件打不开。
Diagnose: ep04_zh.mp4 为 0 字节、无进程在跑——长耗时同步 build 被中断(浏览器/连接断开 → Starlette 取消 handler → ffmpeg 中途被杀)，旧代码直接写 out_path，留下 0 字节坏文件。按保存的 plan 重建即成功(34.8MB、解码干净)，证明 plan 本身没问题。
Fix:
- tools/seam_concat.py — 最终 concat 改**原子写**：先写 `out_path.part` 再 `Path.replace` 到正式名，仅成功才替换；失败/中断只留 .part(已清理)，正式文件保留上一份好文件、绝不被 0 字节覆盖。`.part` 扩展名 ffmpeg 无法推断容器，故显式加 `-f mp4`。
- 验证：原子写合成解码干净、无 .part 残留；ep04_zh.mp4 已重建为有效 2:50 文件；21 项 episode 测试全过。

No conflicts found in: episode__writer.py/route/UI(写机制变化，产物内容不变)。

## Follow-up 147 — 2026-06-24 20:48:23
Source: user_input/follow_ups/147-20260624-204823-concat-first-whole-episode-subtitles.md
Summary: 出片流程改 concat-first——先拼干净成片(ep{NN}.mp4 + segments.json)，再对整集按真实时间轴烧一次字幕，根治字幕被拼接二次编码 + 承接裁帧错位的问题。三按钮：① 定版 ② 拼接成片 ③ 整集字幕(zh/en/both)。

Auto-updated:
- `projects/ai_video_management/libs/infrastructure/writers/episode_takes__writer.py`（新增 EpisodeTakesSelector：每镜 newest_render → shutil.copy2 → shot{NN}.mp4）
- `projects/ai_video_management/libs/infrastructure/writers/episode_subtitle__writer.py`（新增 EpisodeSubtitleBurner.burn_whole / assemble_cues：读 segments.json，每镜 cue re-time 到真实段时长 + 按 start_s 平移，对 ep{NN}.mp4 烧一次 → ep{NN}_{zh|en|zhen}.mp4）
- `projects/ai_video_management/libs/infrastructure/writers/episode__writer.py`（_select_clip 优先 shot{NN}.mp4；build 写 ep{NN}.segments.json；_write_segments / _approx_eff，承接/RIFE 路径标 approx:true）
- `projects/ai_video_management/libs/infrastructure/writers/subtitle__writer.py`（新增 segment_cues：本地 0..dur_s 按字数 re-time，源 subtitles.md 否则 台词:）
- `projects/ai_video_management/libs/application/commands/{episode_takes__command.py,episode_subtitle__command.py}`、`dtos/episode_takes__dto.py`、`mappers/{episode_takes__mapper.py,episode_subtitle__mapper.py}`、`queries/episode__query.py`（新增）
- `projects/ai_video_management/libs/domain/errors/subtitle__error.py`（EpisodeNotConcatenatedError / NoEpisodeVideoError 等）
- `projects/ai_video_management/apps/api/routes/{episode__route.py(/api/select-episode-takes),subtitle__route.py(/api/burn-episode-subtitles-whole)}`、`container.py`、`app_factory.py`（wiring）
- `projects/ai_video_management/apps/ui/src/api.ts`（selectEpisodeTakes / burnEpisodeSubtitlesWhole + 类型；ConcatEpisodeResult 加 segments；concatEpisode 文档更新）
- `projects/ai_video_management/apps/ui/src/components/Reader.tsx`（episode 工具栏改 ①定版 ②拼接成片 ③整集字幕 三按钮 + 两 handler；旧 per-language concat 群组替换）
- `projects/ai_video_management/README.md`（新增「出片三步：定版 → 拼接 → 整集字幕」段；旧 per-shot 烧字幕 / per-language concat 标注保留为 back-compat 非主流程）
- `projects/ai_video_management/tests/test_episode_concat.py`（segments.json 断言）、新增 `tests/test_episode_whole_subtitle_burn.py`（offset 累加正确）

Verified:
- pytest test_episode_concat.py + test_episode_whole_subtitle_burn.py：24 passed；subtitle/episode/takes 全量 61 passed。
- UI `tsc --noEmit` 0 错；`vite build` 成功（重建 backend/static 含新三按钮）；`vitest run` 37 passed。

No conflicts found in: interview/qa.md、findings/、final_specs/spec.md、validation/*（本次为出片工序 UI/后端实现细化，不改 spec 级契约；字幕默认关闭 rule 11c 不变——整集字幕仍是手动 opt-in 的最后一步）。

Note: revised_prompt.md 此前漂移到 144，本次补回 145/146(×2)/147 以恢复「raw + 全部 follow-up」不变式。

## Follow-up 146d — 2026-06-24 (amend)
Source: 用户：rife 补帧后接缝处声音受影响，通常怎么解决 → 要求加上音频处理。
原理: 链式拼接硬切音频→接点波形不连续=爆音(click/pop)；桥段「裁掉的接缝声」两半也是硬接+apad 留小静音尾。真·交叉淡化(overlap)会缩短音频、与硬切视频累积失同步(口型漂移)，故不能全局 crossfade。
Fix（纯音频侧，画面/补帧逻辑不动）:
- tools/seam_concat.py — 最终拼接：每段音频两端加 ~10ms `afade` 微淡入淡出(**不重叠→时长不变→不失同步**)再硬 concat，消除接点爆音；桥内「前镜尾+后镜头」两半改 `acrossfade` 平滑(去内部硬切)，仍 apad/atrim 到固定桥长(不影响同步)。新增 _SEAM_FADE_S=0.010 / _BRIDGE_XFADE_S=0.05。
- 验证: ep4(2 RIFE 桥)重建，新 afade/acrossfade 滤镜图无报错、解码干净、音轨 aac 44100 stereo、**时长 169.3s 与改前一致(微淡不丢同步)**；21 项 episode 测试全过。ep04_zh.mp4 已更新。

## 注（外部改动观察）
VALID_EPISODE_LANGS 被外部改为 ("original",)（疑随"字幕默认关/弃 _zh 集变体"方向）。影响：concat-episode / episode-seams 的 lang=zh|en|both 现会 400；SeamPlanModal 的中文/EN/中英按钮需相应改走 original，或前端隐藏这些 lang。本条仅记录，未改（属另一方向，待用户确认）。

## Follow-up 148 — 2026-06-27 16:33:30
Source: user_input/follow_ups/148-20260627-163330-export-production-folder-and-drama-dashboard.md
Summary: ① 一键导出 production——把一部剧所有带字幕 ep 成片拷到 ai_videos/{drama}/production/（中文/英文/中英 子文件夹·去后缀命名）。② 新增剧 level dashboard 主页（点 left nav 剧→右侧 main page 放剧级按钮+展示，解决 toolbar 放不下）。

Auto-updated:
- `libs/infrastructure/writers/production__writer.py`（新增 ProductionExporter：解析 drama root + 走 episodes/ep* 两 layout，把 ep{NN}_{zh|en|zhen}.mp4 → production/{中文|英文|中英}/ep{NN}.mp4，shutil.copy2 覆盖、去后缀、nothing-to-export 为空结果非错误）
- `libs/application/{dtos/production__dto.py, mappers/production__mapper.py, commands/production__command.py}`（薄 application seam）
- `apps/api/routes/production__route.py`（POST /api/export-production {path}）+ `routes/__init__.py` 注册 + `container.py`（production_exporter singleton + production_command factory）
- `apps/ui/src/api.ts`（exportProduction + ExportProductionResult/ExportedEpisode 类型）
- `apps/ui/src/components/DramaDashboard.tsx`（新增·剧级 main page「剧集制作台」：📦 导出 production + 💬 全剧烧字幕 zh/en/both）
- `apps/ui/src/components/Reader.tsx`（drama README 页 body 顶部渲染 DramaDashboard；移除 toolbar 的全剧烧字幕群组 + 迁走 onBurnDramaSubtitlesClick/burnDramaBusy/burnDramaSubtitles import 进 dashboard）
- `apps/ui/src/styles.css`（.drama-dashboard* 样式）
- `tests/test_production_export.py`（新增：按语言路由+去后缀、空结果、scope 拒绝）

Verified:
- 后端 pytest test_production_export.py 3 passed；全量 181 passed（5 项预存无关失败：wukong 数据 / put_file loopback）；container 构建 + /api/export-production 注册确认。
- 前端 tsc --noEmit 0 错；vite build 成功（重建 backend/static）；vitest 37 passed。

设计说明（采纳用户建议）：剧级按钮放不进 left-nav toolbar → 新增**剧级 main page（DramaDashboard）**，以 drama README 页为锚在右侧呈现，承载剧级动作（导出 production + 全剧烧字幕）；后续剧级功能都往这放。导出落点 `ai_videos/{drama}/production/{中文|英文|中英}/ep{NN}.mp4`（lang 由子文件夹表示、文件去后缀）。

No conflicts found in: interview/qa.md、findings/、final_specs/spec.md、validation/*（本次为新增 UI/后端功能，不改既有契约；导出复用既有带字幕成片 ep{NN}_{zh|en|zhen}.mp4）。

## Follow-up 149 — 2026-06-27 17:09:04
Source: user_input/follow_ups/149-20260627-170904-seam-trim-allow-zero-rife-without-trim.md
Summary: 拼接功能裁切秒允许从 0 开始（min 0.04→0），即可「只选 RIFE 但不裁切」（trim=0）。

Auto-updated:
- `apps/ui/src/components/SeamPlanModal.tsx` — 裁切 input `min={0.04}`→`min={0}`（step 0.02/max 0.4 不变）；TRIM_HELP 补「0=不裁切，仅在接缝处插补帧平滑、不丢原片」。
- `tools/seam_concat.py` — 新增 `_SEAM_TRIM_EPS=0.02`；`_rife_bridge` 音频复用加 `reuse_ambient = trim >= _SEAM_TRIM_EPS` 守卫：trim≈0 时两侧 atrim 切片为空会让 acrossfade 失败→静默回退 butt-join，故 trim<eps 不复用环境声、改走 anullsrc 静音桥，保证 trim=0 仍出 RIFE 桥（depth 默认 1 帧，用户可用「密度」控件加帧）。

Verified:
- seam_concat.py 语法 OK；UI tsc 0 错 + vite build 成功（重建 bundle）；pytest test_episode_concat.py 23 passed（plan 路径未 floor trim 已确认：trims[j]=float(e["trim"])）。

No conflicts found in: 后端 plan 路径本就接受任意 trim、episode__writer 不 floor plan trim；本次仅放开 UI 下限 + 修 trim≈0 的桥段音频回退。

## Follow-up 150 — 2026-06-27 17:26:40
Source: user_input/follow_ups/150-20260627-172640-seam-butt-shows-rife-stale-bundle-and-trimbutt.md
Summary: 拼接「硬拼仍出 rife」根因＝构建/服务路径错配：app 服务 apps/api/static（空·.gitkeep），vite.config outDir 却是 apps/backend/static（backend→api 重构遗留）。用户已把拼接升级成三态（硬拼/裁切平接/RIFE）逻辑正确，但前端改动从未进入被服务 bundle → prod 跑旧 UI、硬拼仍出 rife。

Auto-updated:
- `apps/ui/vite.config.ts` + `apps/ui/vite.config.js` — build.outDir `apps/backend/static` → `apps/api/static`（app_factory.py 实际服务目录、Makefile clean 与 README 亦指此）。
- 重建 `apps/api/static`（index.html + assets 落位）→ 用户已实现的三态拼接前端（SeamPlanModal/api.ts）现真正被服务。

Verified:
- npm run build 成功、apps/api/static 现含 index.html + index-*.js；episode__writer.py 语法 OK、pytest test_episode_concat.py 23 passed（三态 _plan_for_used/_stitch_with_plan 已由用户并行实现、本次未改其逻辑）。

Note: 三态拼接（butt/trim/rife）的后端(_plan_for_used emit {bridge,rife}/_stitch_with_plan 仅在真 bridge 时要 RIFE exe) 与前端(method "butt"|"trim"|"rife") 为用户并行实现、已完整；本 follow-up 仅修构建落点使其生效。旧 `apps/backend/static/` 产物作废可后续清理。

No conflicts found in: 后端三态逻辑（已正确）、tests。

## Follow-up — 2026-06-27 承接缝新增「裁切平滑(trim)」第三接法 + seam_tune 调参工具
Source: 用户——「重要的是 persist 调好的参数，让我在 UI 上也能看见最优参数；这套找最优参数+拼接流程做成可频繁调用的工具，跑后续所有 ep」。
背景：seam_tune 实测发现 locked-frame 重生后承接缝近连续时，「裁切两侧 ease/重复帧 + 硬拼、不补帧」(trim-butt) 比 RIFE 更平滑，但旧 seam 计划只有 rife / butt(硬切) 两态，无法持久化/显示"裁切但不 RIFE"——会被当硬切丢掉 trim。
common-level 工具（仓库级）：
- 新增 `tools/seam_tune.py`——按 ep 文件夹自动调参：读 seam_plan.json、对每个承接缝扫 trim×depth + 裁切硬拼基线、客观度量(接缝逐帧亮度差对参考速度的最大偏离·罚 freeze/spike)选最平滑、--apply 回写计划、--build 出片；承接帧差超可桥接带([3,40])即报"prompt 问题(承接帧不匹配·无参数可救)"。可频繁调用于后续所有 ep。
- `tools/seam_concat.py`：plan 条目新增 `rife` 键(默认 True)——令某缝可「裁切+硬拼、不补帧」(bridge True, rife False)，与 RIFE 缝/硬切缝在同一次 concat 混用。
webapp（端到端三态：硬拼 / 裁切平滑 / RIFE 补帧）：
- episode__writer：`_plan_for_used` 产 {bridge,rife,trim,depth}（method∈rife/trim→bridge；rife=method==rife；depth 仅 rife）；新增 `_stitch_with_plan`——仅当确有 RIFE 缝才要 rife exe，纯裁切/硬切计划无需 GPU 即可拼；analyze_seams 对带内承接缝 suggest 由 rife 改 trim(经验最优默认)；SeamInfo.method/suggest 注释三态。
- episode__route：SeamPlanEntry.method 注释三态（route 不枚举校验，trim 直通）。
- ui：api.ts SeamInfo/SeamPlanEntry method/suggest 加 "trim"；SeamPlanModal 承接缝三按钮(硬拼/裁切/RIFE)、裁切&RIFE 都显示「裁切秒」(可见并可改持久化参数)、密度仅 RIFE、图例/建议提示/头部计数加裁切。
验证：pytest seam/episode 48 passed（全量 5 个失败与本改无关·wukong_juexing 子类型/tree_walker/api_security）；UI tsc 0 错 + vite build 成功(重建 bundle 落 apps/api/static)；ep01 saved plan→tool_plan 映射实跑确认两承接缝=trim-butt 0.14、硬切=plain。

## Follow-up 151 — 2026-06-27 17:41:35
Source: user_input/follow_ups/151-20260627-174135-seam-ux-hardcut-vs-soft-with-trim-and-rife.md
Summary: ① 拼接 UI 改两级结构：硬拼 / 不硬拼；不硬拼下 裁切 与 RIFE 并存可调。② 诊断 ep4 shot11→12「硬拼不像硬拼」= stale render（非代码 bug）。

Auto-updated:
- `apps/ui/src/components/SeamPlanModal.tsx` — 承接缝控件由三互斥按钮(硬拼/裁切/RIFE)改为：硬拼/不硬拼 两按钮 + 不硬拼时展开 裁切秒 input(始终)+ RIFE 补帧 checkbox + 密度 select(勾 RIFE 时)；「不硬拼」active = method≠butt，点不硬拼默认置 trim，RIFE 勾选切 trim↔rife。新增 RIFE_HELP；legend + 建议 hint 文案同步两级模型。method 仍发 butt/trim/rife（后端三态不变）。
- `apps/ui/src/styles.css` — `.seam-rife-toggle`（checkbox 行内对齐）。

Verified:
- tsc 0 错；vite build 成功（已落 apps/api/static·含本次 UI）；vitest 37 passed。

ep4 shot11→12 诊断：seam_plan.json `shot11->shot12 method=butt`（保存正确）；shot11 硬切 / shot12 承接 shot11 → 承接缝；后端 butt→{bridge:False}=纯硬拼。看到的「rife/发软」是 vite 修复前旧 bundle/旧 render 的产物（前端改动此前从未被服务）→ 重启后端 + 硬刷新 + 重生 ep4 即正常；承接缝想干净接用「不硬拼+裁切」。无代码 bug。

No conflicts found in: 后端三态(butt/trim/rife)逻辑、tests。

## Follow-up 152 — 2026-06-27 18:00:00
Source: user_input/follow_ups/152-20260627-180000-unmatched-downloads-not-imported.md
Summary: 未匹配的下载文件不再导入到 not_matched/，而是原地留在 Downloads、仅作 unmatched 上报。

Auto-updated:
- libs/infrastructure/writers/downloads__writer.py — 四个导入入口(import_drama/performances/actors/bgms)统一改为未匹配即跳过(不移动、仅 result.unmatched 上报 from)；删除 ACTOR/PERF/BGM_NOT_MATCHED_DIR_NAME 常量与模块/方法 docstring 中的 not_matched 描述。
- apps/ui/src/api.ts — ImportFromDownloadsResult.unmatched 去掉 to 字段。
- apps/ui/src/components/{Sidebar,DramaPage}.tsx — 导入 toast「未分类」→「未导入」。
- tests/{test_downloads_import_shots,test_downloads_import_bgms,test_downloads_import_performances,test_actor_prompt_only_roundtrip}.py — 断言改为「文件留在 Downloads、不创建 not_matched/」。22 passed。
- ai_videos/wushen_juexing/not_matched/ — 删除整个文件夹(12 个文件)。

No conflicts found in: final_specs/spec.md, validation/*.

## Follow-up 153 — 2026-06-27 18:45:00
Source: user_input/follow_ups/153-20260627-184500-drama-mainpage-open-from-nav-buttons-off-nav.md
Summary: 点击 left nav 剧节点本身弹出剧级 main page（不只 dropdown）；剧级按钮从 nav 移到该页；148 的 dashboard 从 README 页迁到专属 DramaPage。

Auto-updated:
- apps/ui/src/components/DramaPage.tsx — 新增剧级主页组件（route /drama?drama=）：DramaDashboard（导出 production + 全剧烧字幕）+ 资源管理（导入+重命名、角色画廊）+ 📺 分集总览（从 tree 派生各集已烧字幕成片 zh/en/中英 badge）。
- apps/ui/src/App.tsx — 注册 /drama 路由 → DramaPage。
- apps/ui/src/components/Sidebar.tsx — 剧节点 onClick 改为 navigate(/drama?drama=) + 仍 toggle dropdown；移除 nav 内联的剧级按钮（📥 导入+重命名、🎭 角色画廊）。
- apps/ui/src/components/Reader.tsx — DramaDashboard 从 isDramaReadme 页移除（含 import 与 isDramaReadme 判定），集中到 DramaPage；更新工具栏注释指向 DramaPage。
- apps/ui/src/styles.css — 新增 .drama-page* 布局（header / section / 分集列表 + 语言 badge）。

Verified: tsc -b 0 错；vite build 成功（已落 apps/api/static·含本次 UI）。后端 export-production 路由/命令早已 wired（148），本次纯前端 UX 重定位、无后端改动。

No conflicts found in: 后端 production__*（148 已落）、final_specs/spec.md、validation/*。

## Follow-up 152 — 2026-06-27 18:10:01
Source: user_input/follow_ups/152-20260627-181001-concat-drops-audio-tail-last-word.md
Summary: 拼接后 shot11 末字「了」消失 = 默认音频处理把音频裁到视频流长度。根因+修复+验证。

Auto-updated:
- `tools/seam_concat.py` — 根因：`_render_body` 把音频 `atrim end=dur`（dur=`_probe` 的视频流长）；clip 音频比视频长（TTS 末字在画面结束后才念完）时末字被裁，纯 butt 硬拼也中招。修：新增 `_audio_dur()` 探音频流长 + `_AUDIO_TAIL_KEEP_S=1.0`；`_render_body` 在 butt 尾(tail≈0)保留完整音频(不裁到视频长)、超出视频部分用 `tpad=stop_mode=clone` 保持末帧补齐画面(a/v 同步)、超出量 cap 1.0s 防 135c 卡死音轨。**坑**：`tpad` 须在 `_norm`(末尾含 `fps=`)之后才生效，否则静默 no-op——故 tpad 移到 `_norm` 之后。

Verified:
- shot11 body：音频 9.93→10.10s(「了」保住)、画面 tpad 补到 10.08s(a/v Δ0.02s)；3-clip 合成(含 0.3s 音频超长 clip) 解码 OK + a/v 同步；pytest test_episode_concat.py 23 passed。

Note: 用户提议把音频处理选项暴露到 UI——默认修复后音频不再被裁、末字保住，无需手动选项即正确（如需显式控制可后续加 toggle）。与 `ai_videos__运镜` M8 新增「接缝两端 0.3s 留台词静默(ai_video.md (J))」互补：本修为出片端兜底、(J) 为设计端预防。用户需**重新生成 ep04** 取得修复后音频。

No conflicts found in: episode__writer / 三态拼接逻辑（未触及）、tests。

## Follow-up 153 — 2026-06-27 19:00:00
Source: user_input/follow_ups/153-20260627-190000-drama-console-global-takes-and-per-episode-concat.md
Summary: 主页剧集制作台新增「全局定版」按钮 + 每集「拼接成片」按钮列表。

Auto-updated:
- libs/infrastructure/writers/drama_takes__writer.py (新增) — DramaTakesSelector：遍历全剧 episodes/ep*，委托既有 EpisodeTakesSelector 逐集锁 take（不漂移），单集失败不致命。
- libs/infrastructure/readers/drama_episodes__reader.py (新增) — DramaEpisodesReader：列出全剧每集 {shots, locked, has_master, episode_rel}。
- libs/application/{dtos,mappers,commands}/drama_takes__*.py + queries/dtos/mappers drama_episodes__*.py (新增) — DDD 应用层包装。
- apps/api/routes/drama__route.py (新增) — POST /api/select-drama-takes + /api/list-drama-episodes；注册进 routes/__init__.py；container.py 注入 4 个 provider。
- apps/ui/src/api.ts — 新增 listDramaEpisodes / selectDramaTakes + 类型。
- apps/ui/src/components/DramaDashboard.tsx — 加「🔒 全局定版」按钮 + 剧集列表（每集一行状态 + 「🎬 拼接成片」按钮，复用 concatEpisode，locked=0 时禁用）。
- apps/ui/src/styles.css — 剧集列表样式。
- final_specs/spec.md — 新增 FR-105（select-drama-takes）/ FR-106（list-drama-episodes）。
- tests/test_drama_takes_and_episodes.py (新增, 5 passed) + tests/test_boot_smoke.py（两新端点加入 smoke 矩阵）。全部 38 passed；UI tsc 0 error。

Note: UI 改动需重新 build 前端静态包（apps/api/static）后才会在 static-served 模式生效；vite dev 模式即时可见。

No conflicts found in: validation/*, interview/qa.md.

## Follow-up — 2026-06-27 接缝质量评分仪表盘（量化 metrics + UI dashboard）
Source: 用户——「需要量化指标衡量是不是最好的 / 帮我对齐到最优并在 UI 给一个 dashboard 展示分数和细节 / 我要知道你设了哪些指标好一步步 improve」。
工具层：`tools/seam_metrics.py` 暴露 `compute_scorecard()` 返回结构化评分（含 `METRIC_DEFS` 机读指标定义——名称/权重/单位/好坏阈值/中文说明，作 UI 与 scorer 的单一真相源）+ 每缝标准方法面板排名。CLI `grade()` 改为调它。
四指标（各 0–100·加权均）：M1 运动速度连贯(cv2 光流·权40)·M2 无冻结(权15)·M3 无跳变/无拖影(权25)·M4 接缝结构连续(相邻 SSIM·权20)。
webapp：
- 后端 EpisodeConcatBuilder.`score_seams()`（载 tools/seam_metrics.py·调 compute_scorecard·传 rife exe·缺 RIFE 仅跳过对应面板行）；EpisodeQuery.`score_seams()` 透传 dict；route `POST /api/episode-seam-metrics`（body path/lang/compare）。
- 前端 `SeamScoreDashboard.tsx`：📊 接缝评分按钮(Reader 出片三步区)→ 弹窗仪表盘：当前 plan 总分/最优上限/最弱缝三卡 + 指标定义折叠区 + 每缝方法排名(分数条·M1–M4 细分·原始测量值·★最佳/当前plan 标签)。首屏只评当前 plan(~15s)，勾「对比多种接法」再跑硬拼/裁切/RIFE 面板(~1–2min)。api.ts 加 SeamMetricsResult 等类型 + scoreEpisodeSeams()；styles.css 加 .seam-score-* 样式。
验证：seam/episode pytest 53 passed；UI tsc 0 错 + vite build 成功；容器集成实跑 score_seams(ep01·compare=false)=15.4s·overall 94.2(A)·seam10→11 88.9 / seam11→12 99.4。

## Follow-up — 2026-06-27 接缝评分持久化 + 打开页面自动显示 + 标注秒数区间
Source: 用户——「结果直接记录下来，一打开页面不点 button 就能看到，是 ep01.mp4 最近一次生成的 dashboard；只针对首尾帧连接处，写明秒数范围」。
- 持久化：build 成功后 EpisodeConcatBuilder.`_write_seam_scores()` 自动算分(chosen-only·快)并写 sidecar `ep{NN}.seam_scores.json`(带 generated_at·best-effort 不阻断 build)。tools/seam_metrics.py 加 `save_scorecard()`/`scorecard_path()`/CLI `--save`。
- 即时读取：`read_seam_scores()`(infra)→ EpisodeQuery.`read_seam_scores()` → route `POST /api/episode-seam-scores`(读 sidecar·~170ms·无重算)。
- 秒数区间(只首尾帧承接)：compute_scorecard 加 `_seam_timeline()`——按各 shot 有效时长(dur−head−tail·仅承接缝裁切)累加算出每个承接缝在成片里的 at_s + 区间[start_s,end_s](含 trim/桥接)，挂到 seam.time。CLI 文本/JSON/dashboard 全显示。仅 method∈trim/rife 的首尾帧缝计分(硬切不计)。
- 前端自动显示：新增 `SeamScorePanel.tsx`——打开剧集 md 或 ep{NN}.mp4 成片页即自动拉 sidecar 并内联展示(总分+各承接缝分数/秒数区间/M1–M4)，无需点按钮；「详情/重新评分/对比接法」开完整 dashboard 弹窗。Reader 在 isEpisodeFile||isEpisodeReel 时渲染该 panel。api.ts 加 SeamTime/readEpisodeSeamScores + generated_at/persisted 字段；styles.css 加 .seam-panel-*。
验证：seam/episode pytest 53 passed；UI tsc 0 + build OK；容器实测 read_seam_scores 173ms·overall 94.2(A)·seam10→11 @112.2s(112.0–112.4) 88.9 / seam11→12 @121.93s(121.73–122.13) 99.4。ep01 sidecar 已生成。

## Follow-up — 2026-06-27 删除成片「资源忙」根治：删前释放预览流 + 后端重试穿透锁
Source: 用户——「delete ep01.mp4 failed，点 delete 务必强制删成功，不管什么方法」。
根因：浏览器 <video> 预览成片是经同一 webapp 服务器进程拉流(range 请求)，该进程因此持有文件读句柄；点删除时同进程去 rename 自己正开着的文件 → Windows「资源忙」，soft-delete(rename 到 _deleted/) 失败。(经 Restart Manager 定位锁持有者＝webapp python 进程。)
修复(双侧，让删除必成)：
- 前端 Reader.onDeleteClick：删前先卸载预览 <video>(videoRef pause + removeAttribute src + load + 250ms)，浏览器断流→服务器释放句柄。
- 后端 media__writer：新增 `_rename_through_lock()`——rename 失败按 0.2s×15(≈3s)重试穿透瞬时锁，最后兜底 copy2+unlink；delete() 改用之。错误信息中文化。
本次即时处置：ep01.mp4 被锁，已用 Restart Manager 定位并 kill 锁进程(webapp server PID 57564)后强制删除(用户授权杀 blocker)；用户需重启服务。
验证：media/delete pytest 5 passed；UI tsc 0 + build OK。

## Follow-up 154 — 2026-06-27 20:00:00
Source: user_input/follow_ups/154-20260627-200000-actors-bgm-library-pages-and-voices-removal.md
Summary: _actors→「演员库」、_bgm→「背景音乐库」各自成主页（grid 合并进主页 + 左栏按钮迁移）；删除 _voices 库。

Auto-updated:
- libs/infrastructure/readers/tree__reader.py — 新增 _SYSTEM_FOLDER_LABELS_ZH {_actors:演员库, _bgm:背景音乐库}，在 _walk_project 赋 display_name（优先于 README/concept H1）。
- apps/ui/src/components/Sidebar.tsx — _actors/_bgm 节点点击改为 navigate(/actors|/bgm)+toggle；删除 _actors/_voices/_bgm 三组 root 内联按钮、VoicePoolGenerator/ActorPoolGenerator/BgmPoolGenerator 渲染与状态、onVoiceDeleteClick/deleteVoice/VOICE_ID_RE/isVoice* 等 voices 残留。
- apps/ui/src/components/ActorGrid.tsx — 标题「演员池」→「演员库」；header 加 🎭 生成演员(ActorPoolGenerator 模态)+📥 导入演员(importFromDownloads ai_videos/_actors)；空态同样带工具栏。
- apps/ui/src/components/BgmGrid.tsx — 标题「BGM 音乐库」→「背景音乐库」；header 加 🎵 生成 BGM(BgmPoolGenerator)+📥 导入下载音乐；空态文案更新。
- apps/ui/src/styles.css — 新增 .voice-page-actions。
- apps/ui/src/App.tsx — 删除 /voices 路由 + VoiceGrid import。
- ai_videos/_voices/ — 整个文件夹删除（voice_0001/voice_0002；无 casting.md 引用 voice_id，安全）。
- final_specs/spec.md — FR-87 更新 _actors/_bgm 节点行为 + 演员库/背景音乐库主页；FR-87 内 _voices 备注改为 RETIRED。
- tests/test_tree_system_folder_labels.py (新增, 2 passed) — 校验 _actors→演员库 / _bgm→背景音乐库，且真实剧集 H1 标题不被系统标签覆盖。

Note: 后端 /api/voices/* 端点保留（不再从 nav 可达，无 casting voice_id 引用）；如需彻底移除可再开 follow-up。UI 已 npm run build 刷新 apps/api/static 静态包。

Verification: 全量后端 188 passed（仅 5 项既有 wukong_juexing/PUT-security 预存失败，与本次无关）；UI tsc 0 error + vite build 成功。

No conflicts found in: validation/*, interview/qa.md.

## Follow-up — 2026-06-27 修「拼接成片生成不出来」：评分移出关键路径(后台线程)
Source: 用户——「点拼接成片，ep01.mp4 生成不出来」。
根因：上一条把 seam 评分(_write_seam_scores·会重建隔离 seam pair + 跑光流·~30s)放进了 build() 同步关键路径，叠加既有 ~65s 出片(逐镜 freezedetect + 12 片重编码 + RIFE 桥接尝试)→ 单次请求 ~95s+，前端/代理看着像卡住没出片。(实测：纯 concat 20s；webapp build 无评分 ~66–70s；加同步评分 >2min。)
修复：`_write_seam_scores` 改为 **daemon 后台线程**——ep{NN}.mp4 一写完 build() 立即返回(~65s 同改前)，评分 sidecar 稍后(~30s)自动落地，dashboard 仍能展示上次生成结果。评分不再拖慢/卡住拼接。
验证：seam/episode/media pytest 55 passed；改动模块全 import OK；实测 build 返回 65.9s 且 ep01.mp4 生成成功。
旁注：当前 seam_plan 两承接缝被 UI 实验设成 rife(shot10→11 d4/0.06、shot11→12 d1/0.1)，RIFE 桥接对本片降级失败("bridge unusable"→butt-join)且慢；trim@0.10 已证更优更快(94.2/A)，建议改回 trim。
