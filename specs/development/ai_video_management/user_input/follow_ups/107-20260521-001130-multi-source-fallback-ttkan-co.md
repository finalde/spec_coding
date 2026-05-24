# Follow-up draft 107 — 2026-05-21

Add multi-source fallback to the novel downloader so a single source going down (e.g. sudugu.org's IP block from follow-up 106) doesn't halt the pipeline. Second source: `ttkan.co` (verified reachable from this IP at the time of this follow-up).

## Why

User picked "1 + 3" from the recovery menu: wait for the sudugu.org IP block to expire AND add multi-source fallback as the long-term fix.

The IP block in 106 surfaced a structural weakness: the downloader had exactly one source per novel hardcoded into `NovelSpec`, so when sudugu.org started returning 302 → google.com, every novel halted. Multi-source is the architectural fix.

## Probing summary

Tried 9 candidate alt sites. Three return 200 cleanly; only one has the novels we need:

| Site | Status | Notes |
|---|---|---|
| ttkan.co | 200 ✓ | Has 5 of the popular novels confirmed (fanren, 光阴之外, 完美世界, 择天记, 灵境行者). Traditional Chinese. |
| bxwx9.org | 200 | No fanren found at probed ID; skipped. |
| 69shuba / biquge.tw / ddyueshu / biquge88 / biqugesf / biqu5200 / biquge.info / biquge365 / bqg5 | 403 / timeout / DNS fail / connection-reset | All hostile-to-bot or down. |

`ttkan.co` chosen because: (a) reachable, (b) has the popular novels, (c) HTML structure parseable with simple regex, (d) no chapter-page pagination (simpler than sudugu).

## Design

### Domain — `NovelSource` value object

```python
@dataclass(frozen=True)
class NovelSource:
    host: str         # 'sudugu.org' or 'ttkan.co'
    source_id: str    # site-specific identifier (numeric for sudugu, pinyin-slug for ttkan)
```

`NovelSpec` schema gains `sources: tuple[NovelSource, ...]`. Backward-compat properties `source_host` and `source_id` resolve to `sources[0]` so all callers (queries, mappers, DTOs) keep working.

Manifest update:
- Every existing entry's `(source_host='sudugu.org', source_id='X')` becomes `sources=(NovelSource('sudugu.org', 'X'),)`.
- The 5 verified ttkan entries get a second `NovelSource('ttkan.co', '<ttkan-slug>')` appended.

### Infrastructure — per-host dispatch

Two new private helpers in `NovelDownloader`:
- `_fetch_index_via_sudugu(source) -> list[ChapterRecord]` — the existing index-with-pagination logic, factored out.
- `_fetch_index_via_ttkan(source) -> list[ChapterRecord]` — single-page index; pattern `<a href="/novel/pagea/{slug}_{N}.html">第N章 标题</a>`.
- `_fetch_chapter_via_sudugu(url) -> str` — existing chapter logic with `下一页` pagination.
- `_fetch_chapter_via_ttkan(url) -> str` — single-page chapter; `<div class="content">` → `<p>` paragraph extraction.

`_fetch_chapter_index(spec)` is rewritten to iterate `spec.sources`, try each one, fail to the next on `ChapterIndexParseFailed`, return the first success.

`_fetch_chapter_full(spec, chapter)` looks at the URL's host and dispatches; the chapter URL already encodes which source it came from (because the URL string starts with `https://www.{host}/`).

### Active source tracked in `NovelMeta`

```python
@dataclass
class NovelMeta:
    ...
    active_source_host: str = ""
    active_source_id: str = ""
```

When `_ensure_index` picks a source successfully, it stores those two fields. On the next launch:
- If the active source still works (still in `spec.sources`, still reachable), reuse it. Chapter URLs stay aligned.
- If not, re-fetch the index from the next reachable source. Chapter URLs change. `done` flags are preserved by `chapter.idx` (98%+ correct; sources occasionally split chapters slightly differently — acceptable trade-off for v1).

### Re-fetch semantics on source switch

If a novel's existing meta has 501 chapters marked done with sudugu URLs, and we now switch to ttkan:
1. `_fetch_chapter_index_ttkan` returns 2453 chapter records (vs sudugu's 2512).
2. We replace each chapter's `url` field with the ttkan URL while preserving `done`, `hash`, `error` by index.
3. Net effect: chapters 1-501 keep `done=True`; chapter 502+ become the ttkan URLs and get downloaded.
4. The body `.md` file accumulated under sudugu content stays intact; new chapters appended under ttkan content (Traditional Chinese — small content style mismatch the user can accept or convert with opencc later).

### Out of scope

- Auto-recover MID-novel from source switch (i.e. detect 302 mid-chapter-download and switch immediately). v1 only switches at next launch.
- opencc 繁→简 conversion for ttkan content.
- Search-driven slug discovery on ttkan (manual hand-curation for the 5 verified novels; others fall back to sudugu-only).
- More source sites (biquge family, 69shuba) — all currently blocked or hostile; revisit if needed.

## Touch list

- **Modified Python files**:
  - `libs/domain/value_objects/novel__valueobject.py` — add `NovelSource` dataclass; refactor `NovelSpec` schema to `sources: tuple[NovelSource, ...]`; add compat `source_host` / `source_id` properties; update all 39 manifest entries; add ttkan source to 5 popular novels (fanren_xiuxian_zhuan, guangyin_zhiwai, wanmei_shijie, ze_tian_ji, lingjing_xingzhe).
  - `libs/infrastructure/writers/novel__writer.py` — multi-source dispatch in `_ensure_index` + `_fetch_chapter_index` + `_fetch_chapter_full`; per-host helper methods; `NovelMeta` gains `active_source_host` + `active_source_id` fields.
- **Audit**: changelog 107.
- **No code change** to application layer (queries / mappers / DTOs): existing `source_host` / `source_id` Qdto fields keep returning the active source via compat properties — frontend types + payloads stay byte-identical.
- **No code change** to CLI: `--workers 1` default from 106 stays.
- **No background-job restart this turn**: the IP block from 106 likely still active; user controls when to re-launch. Once unblocked (or via VPN), the new multi-source build will automatically prefer the working source.
