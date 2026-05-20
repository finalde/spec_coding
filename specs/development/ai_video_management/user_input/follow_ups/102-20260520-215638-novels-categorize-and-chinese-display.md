# Follow-up draft 102 — 2026-05-20

Three bundled changes (extends follow-up 101):
1. **Expand `CANONICAL_NOVELS` manifest** beyond the 10 仙侠 entries to cover multiple genres (仙侠 / 玄幻 / 都市 / 历史 / 科幻 / 言情). Source IDs verified against sudugu.org.
2. **Categorize novels on disk and in the sidebar**: introduce `category: str` + `category_zh: str` on `NovelSpec`; layout becomes `novels/{category}/{slug}/{slug}.md` (+ `_meta.json`) instead of flat `novels/{slug}/`.
3. **Chinese display names in the sidebar**: tree nodes that represent novels and categories carry a `display_name` field with the Chinese title; the React Sidebar renders `display_name` when present, falling back to `name` for everything else.

## Why

User: "幫我下載更多的小説，在UI上名字要顯示中文，下載的小説要按題材分類， 比如仙俠類".

Three asks compounded:
- More novels (manifest expansion).
- Display Chinese titles in the sidebar (not pinyin folder names).
- Group by category in the sidebar (e.g. 仙侠類 as a folder).

## Design

### Domain (extend, not replace)

`libs/domain/value_objects/novel__valueobject.py`:
- `NovelSpec` gains `category: str` (slug, ASCII) + `category_zh: str` (Chinese label).
- `CANONICAL_NOVELS` expanded to ~20-25 entries spread across 5-6 genre buckets. The original 10 from follow-up 101 are tagged `category="xianxia"`, `category_zh="仙侠"`.
- New helper `categories() -> list[tuple[str, str]]` returning unique (slug, zh) pairs in canonical order, used by the tree-builder and by `_index.md`.

### Filesystem layout migration

Before: `novels/{slug}/{slug}.md` + `_meta.json`.
After:  `novels/{category}/{slug}/{slug}.md` + `_meta.json`.

The existing in-flight `novels/fanren_xiuxian_zhuan/` (in-progress at the time of this follow-up) gets relocated to `novels/xianxia/fanren_xiuxian_zhuan/`. The `_meta.json` resume-from-checkpoint contract survives the move (only the parent directory changes; the file's chapter list + done flags are unaffected). The downloader's `download_all` is restarted from CLI; resume picks up where the move left off.

`novels/_index.md` is regenerated grouped by category — one `## {category_zh}` section per genre, table rows for each novel within.

### Tree integration (display_name on intermediate + leaf nodes)

`libs/infrastructure/readers/tree__reader.py`:
- `_novels_section` produces category-level child nodes with `{name: "{category}", display_name: "{category_zh}", type: "folder", children: [...]}`.
- Each novel-level child node carries `{name: "{slug}", display_name: "{title_zh}", type: "folder", children: [...]}`.
- Leaf files (`{slug}.md`, `_meta.json`) keep their existing leaf shape — file names stay as-is (no Chinese in file content addressed by sidebar — clicking the file just shows the path).

The existing `_walk_filtered` is reused for intermediate folders that don't have a canonical mapping; only novel + category folders get the `display_name` enrichment.

### Frontend Sidebar (minimal change)

`apps/ui/src/components/Sidebar.tsx`: where a tree node's label is rendered, prefer `node.display_name` when present, fall back to `node.name`. One-line change in the render path. `apps/ui/src/types.ts` adds `display_name?: string` to the TreeNode type.

### Downloader update

`libs/infrastructure/writers/novel__writer.py`: `download(slug)` resolves the spec's category and writes to `novels_root / spec.category / slug / ...` instead of `novels_root / slug / ...`. `download_all` iterates `CANONICAL_NOVELS` as before.

`apps/cli/novel_download.py`: prints progress with category prefix (`[xianxia/fanren_xiuxian_zhuan] N/M`).

`NovelQuery.list()` walks two levels (`novels/{category}/{slug}/_meta.json`) and returns category info in the Qdto. `NovelStatusQdto` gains `category: str` + `category_zh: str` fields.

### Manifest expansion

New entries by category (all verified accessible on sudugu.org):

仙侠 (xianxia) — 10 existing from follow-up 101 stay; tag with `category="xianxia"`, `category_zh="仙侠"`.

玄幻 (xuanhuan) — 斗破苍穹 (天蚕土豆), 完美世界 (辰东), 遮天 (辰东), 圣墟 (辰东), 万古神帝 (飞天鱼).

都市 (dushi) — 都市极品医神 (风会笑), 重生之都市仙尊 (莫忘情), 都市之最强狂兵 (蛇王大人).

历史 (lishi) — 大明1860 (米糕羊), 大唐：李二，我是你儿子 (爱吃黄菠萝).

科幻 (kehuan) — 黎明之剑 (远瞳), 学霸的黑科技系统 (晨星LL).

言情 (yanqing) — 何以笙箫默 (顾漫), 你和我的倾城时光 (丁墨).

Total target: ~24 novels across 6 categories.

Source-id verification is part of the manifest-build step; any entry that returns 404 against `sudugu.org/{source_id}/` is dropped from the seed list with a one-line note. The architecture supports adding more later without code changes.

### Tests to update

- `tests/test_boot_smoke.py`: no change to the section list ([AI Videos, Novels]); the new `display_name` field is additive.
- `tests/test_tree_walker_consumer_walk.py`: existing `test_novels_section_walks_repo_novels_dir` already tolerates empty `novels/`; relax/widen its assertion to allow category-level children.

### Out of scope

- Genre re-categorization based on sudugu.org's actual metadata (each novel's category is hardcoded in the manifest).
- Renaming `{slug}.md` to use Chinese — file names stay pinyin per ASCII-paths convention.
- Sidebar grouping of `ai_videos/` by sub-type (orthogonal change).
- Webapp routing changes (URLs still use pinyin slugs).

## Touch list

- **Modified Python files**:
  - `libs/domain/value_objects/novel__valueobject.py` — add fields + expand manifest + `categories()` helper.
  - `libs/infrastructure/writers/novel__writer.py` — switch to `{category}/{slug}/` layout, update `_write_index_md` to group by category.
  - `libs/application/dtos/novel__dto.py` — add `category` + `category_zh` fields to `NovelStatusQdto`.
  - `libs/application/mappers/novel__mapper.py` — propagate category fields.
  - `libs/application/queries/novel__query.py` — walk two levels.
  - `libs/infrastructure/readers/tree__reader.py` — emit `display_name` for category + novel folders.
  - `apps/cli/novel_download.py` — progress includes category prefix.
  - `apps/ui/src/types.ts` — `display_name?: string`.
  - `apps/ui/src/components/Sidebar.tsx` — render `display_name` when present.
- **Filesystem migration**: move `novels/fanren_xiuxian_zhuan/` → `novels/xianxia/fanren_xiuxian_zhuan/`.
- **Background job**: restart `python -m apps.cli.novel_download` after migration.
- **Audit**: `specs/development/ai_video_management/changelog.md` (entry 102).
