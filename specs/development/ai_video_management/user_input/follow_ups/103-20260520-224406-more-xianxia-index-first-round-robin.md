# Follow-up draft 103 — 2026-05-20

Two bundled changes (extends 101 + 102):
1. **Add 11 more xianxia novels** to the manifest (28 → 39 total; xianxia: 10 → 21).
2. **Refactor `NovelDownloader.download_all` to index-first + round-robin** so all novels appear in the sidebar within ~30 s of launch, and chapter counts grow across every novel in parallel instead of draining one novel to completion before starting the next.

## Why

User: "I can only see 1 凡人修仙傳，please help me download more novels, 仙俠題材爲主".

The user's blocker was UX: 凡人修仙传 has 2512 chapters. At 0.8 s/req that's ~33 minutes minimum before the second novel even starts under the old serial flow. The sidebar showed exactly one xianxia novel during that window, even though 27 more were queued. Two compounded asks:
- **More novels** — the request implies they want more variety than the current 10 xianxia entries. (102 added 18 across other genres but the xianxia-only count stayed at 10.)
- **仙俠題材爲主** — prioritize xianxia in the expansion.

## Design

### Architecture: two-phase `download_all`

```
Phase 1 — index pass (fast, ~1 request × 1-3 pages per novel):
  for spec in CANONICAL_NOVELS:
    _ensure_index(spec)  -> writes novels/{cat}/{slug}/_meta.json + body header

Phase 2 — round-robin chapter pass:
  active = [all states with incomplete chapters]
  while active:
    for state in active:
      next_undone = first chapter not yet done
      download(next_undone)
    active = [s for s in active if s.meta has more undone chapters]
```

Key benefits:
- Every novel folder exists on disk within ~1 min of launch (39 novels × ~1.5 s per index = ~1 min). Sidebar shows the full catalog immediately.
- Round-robin means each cycle adds 1 chapter to **every** in-progress novel. After 10 cycles the user sees 10 chapters in each of 39 novels — broad-shallow visible progress beats deep-narrow invisible progress.
- Resume contract preserved: `_meta.json[chapters][i].done` is the only checkpoint. Re-running picks up exactly where it left off in either phase.
- Rate-limit is global (single `httpx.Client`, single `_last_request_at` clock), so polite to the source across all 39 novels combined — not 39 × per-novel.

### Code shape

- `download_all` body completely replaced (no surgical edits). Splits into:
  - `_ensure_index(spec) -> _NovelState`: idempotent index fetch + meta/body initialization. New helper, replaces the leading 12 lines of the old `download(slug)` body.
  - `_download_one_chapter(state, chapter, on_progress) -> tuple[bool, str | None]`: single-chapter fetch + atomic meta write. Replaces the inner for-body of the old chapter loop.
  - `download(slug)` rewritten to loop over `_download_one_chapter` until no undone chapters remain (functional parity with the old per-novel synchronous flow).
- New `_NovelState` dataclass holds the in-flight `(spec, meta, meta_path, body_path)` tuple — keeps the round-robin loop one-line per iteration.

### Manifest expansion (11 new xianxia)

All probed against sudugu.org index pages, title + author + first-page chapter count verified:

| slug | title | author | source_id | page1_ch |
|---|---|---|---|---|
| gou_zai_yaowu_luanshi | 苟在妖武乱世修仙 | 文抄公 | 529 | 999 |
| cong_jianshu_xiuxing | 从箭术开始修行 | 豆浆油条热干面 | 534 | 573 |
| zhutian_daozu | 诸天道祖，从遮天开始 | 山海一闲鱼 | 2533 | 164 |
| gou_zai_xiuxianjie | 苟在修仙界吞噬成圣 | 喵郡王 | 2036 | 376 |
| changsheng_xiuxian_haomao | 长生修仙：从薅妖兽天赋开始 | 廿三声 | 2035 | 510 |
| changsheng_zhuji_chenggong | 长生：筑基成功后，外挂才开启 | 好的名字很难想 | 1820 | 450 |
| xiyou_baishi_taiyi | 西游：从拜师太乙救苦天尊开始 | 清风映明月 | 319 | 401 |
| po_dao_xing | 泼刀行 | 张老西 | 205 | 877 |
| xi_shen | 戏神！ | 独孤欢 | 1962 | 464 |
| qinghu_jianxian | 青葫剑仙 | 竹林剑隐 | 1649 | 999 |
| cong_songzi_liyu | 从送子鲤鱼到天庭仙官 | 锦绣灰 | 2528 | 813 |

These are sudugu.org's xianxia category page-1 entries not already in the manifest (page 2/3 of the category turned out to be cross-category trending, so the natural xianxia pool maxed out at this count).

### Backwards-compatibility

- `_meta.json` format unchanged from 102.
- `NovelDownloadResult` / `NovelStatusQdto` shapes unchanged from 102.
- `download(slug)` public method preserves its old signature + semantics (used by `NovelCommand.download(slug)` and unchanged routes).
- The in-flight `xianxia/fanren_xiuxian_zhuan/` (348 chapters done at the moment of restart) resumes from chapter 349 on the next launch — confirmed by manual checkpoint inspection.

### Out of scope

- ThreadPoolExecutor / parallel HTTP. Single-threaded round-robin already meets the visibility goal; concurrent requests would either violate the 0.8 s polite-rate contract or require per-source rate-limit bookkeeping.
- Cross-category round-robin priority (e.g. "prioritize xianxia"). The manifest order itself already puts all 21 xianxia first, so they naturally start indexing/downloading before the other 18 entries.
- Auto-discovery from sudugu.org rankings — manifest stays hand-curated.

## Touch list

- **Modified**:
  - `libs/domain/value_objects/novel__valueobject.py` — 11 new xianxia entries.
  - `libs/infrastructure/writers/novel__writer.py` — `download_all` two-phase rewrite; new `_ensure_index` / `_download_one_chapter` helpers; new `_NovelState` dataclass; `download(slug)` rebuilt on top of the new helpers.
- **Background job**: restart `python -m apps.cli.novel_download` after refactor; resume from existing `_meta.json` checkpoints.
- **Audit**: changelog entry 103.
