# Follow-up draft 104 — 2026-05-20

Three bundled changes (reverts 103's round-robin design + adds visibility filter):
1. **Revert `download_all` to strict serial**: complete novel N fully (every chapter `done=True`) before starting novel N+1. The 103 round-robin pattern is replaced.
2. **Sidebar filter — show only complete novels**: `TreeReader._novels_section` filters out any novel whose `_meta.json.complete != True`. Incomplete novels stay on disk (resume checkpoint preserved) but are invisible in the webapp.
3. **Delete round-robin artifacts**: novels with `chapters_done <= 5` on disk (the 1-3-chapter stubs that follow-up 103's round-robin produced) get their folders removed. Preserve `xianxia/fanren_xiuxian_zhuan/`'s 348-chapter checkpoint (user explicitly opted to continue it).

## Why

User: "每一部小説為社麽只有第一章，我要完整的小説所有章節，如果只有一張，那就直接刪掉，我只要有完整章節的小説".

Translation: each novel only has the first chapter [in the sidebar]; I want the complete novel with all chapters; if a novel only has 1 chapter, just delete it; I only want novels with complete chapters.

Direct correction of 103's round-robin design. The user wants:
- The downloader to focus on one novel at a time until 100% complete.
- The sidebar to show only finished novels — partial stubs are visual noise.
- Round-robin's 1-chapter-per-novel artifacts removed from disk.

Clarification question asked + answered: keep `xianxia/fanren_xiuxian_zhuan/`'s 348-chapter checkpoint and continue it serially (option 1 of 3). Don't redo from zero.

## Design

### Revert to serial in `download_all`

The 103 two-phase shape (Phase 1 index pass for all, then Phase 2 round-robin across all) is replaced by:

```python
for spec in CANONICAL_NOVELS:
    download(spec.slug)        # synchronous, complete → next
```

`download(slug)` is unchanged from 103 — it already loops `_ensure_index` + `_download_one_chapter` until done. The two helpers stay; `_NovelState` dataclass stays. The change is one method body. **Net effect**: 凡人修仙傳 will be fully downloaded (~30 min remaining for 2164 chapters at 0.8 s/req) before 光阴之外 starts.

### Tree filter: complete-only

`libs/infrastructure/readers/tree__reader.py::_novels_section` reads each novel folder's `_meta.json` and skips folders where `complete != True`. Reasoning:
- The user's directive "我只要有完整章節的小説" maps to a visibility filter, not a disk-deletion policy. Incomplete folders stay on disk so the downloader's resume contract keeps working.
- Filter is read at tree-walk time (cheap — at most 39 small JSON reads per `GET /api/tree`).
- Category folders with zero complete children are also hidden, so the user sees an empty `Novels` section initially, then categories + novels pop in as they finish.

### Cleanup: delete round-robin stubs

Walk `novels/{category}/{slug}/_meta.json` and delete the folder iff `chapters_done <= 5 AND complete != True`. The threshold catches everything the round-robin produced (most novels finished cycle 1 with 1 chapter each before the user redirected) but preserves any novel with meaningful progress. Per the user's clarification, `fanren_xiuxian_zhuan` (348 chapters) is explicitly preserved.

After cleanup, the disk state is: `novels/xianxia/fanren_xiuxian_zhuan/` only. The downloader's next launch will resume `fanren_xiuxian_zhuan` from chapter 349, then naturally proceed to the next CANONICAL_NOVELS entry (光阴之外) once `fanren_xiuxian_zhuan.complete = True` is flipped.

### What the user sees

- **Right now (after this turn)**: webapp sidebar `Novels` section is empty. `fanren_xiuxian_zhuan` is downloading in the background but `complete != True` so it's filtered out.
- **In ~30 minutes**: `fanren_xiuxian_zhuan` finishes (348 → 2512 chapters done), `complete: True` flips in `_meta.json`, `仙侠 → 凡人修仙传` appears in the sidebar.
- **Over the next several hours**: each subsequent novel completes and appears one-by-one in the sidebar.

### Trade-offs acknowledged

- The user trades **broad visibility** (39 partial novels, 1 chapter each, hard to read) for **deep visibility** (1 fully readable novel at a time as it finishes).
- The sidebar is empty for ~30 minutes — the user accepted this when they said "我只要有完整章節的小説".
- If the user later wants in-progress visibility back, the fix is to relax the tree filter (e.g. show novels where `complete == True OR chapters_done > 100`). The state surface for that change is `tree__reader.py::_novels_section` (one predicate).

### Out of scope

- Progress indicator in the sidebar header (e.g. "currently downloading: 凡人修仙传 348/2512"). Could be added if the user finds the empty-sidebar UX unsettling.
- Parallel/concurrent download — explicitly rejected here; the user wants serial.
- Auto-trim incomplete novel folders on a schedule — only the one-time cleanup runs this turn.

## Touch list

- **Modified Python files**:
  - `libs/infrastructure/writers/novel__writer.py` — `download_all` body reverted to serial loop; helpers + dataclass unchanged.
  - `libs/infrastructure/readers/tree__reader.py::_novels_section` — complete-only filter.
- **Filesystem cleanup**: rm -rf every `novels/{cat}/{slug}/` where `_meta.json.chapters_done <= 5 AND complete != True`. Preserve `xianxia/fanren_xiuxian_zhuan/` per user clarification.
- **Background job**: relaunch `python -m apps.cli.novel_download`; resume `fanren_xiuxian_zhuan` from chapter 349.
- **Audit**: changelog entry 104.
