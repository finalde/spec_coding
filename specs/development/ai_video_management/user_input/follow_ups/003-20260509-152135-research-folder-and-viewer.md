# Follow-up draft 003 — 2026-05-09

Summary: Introduce a new repo-root `research/` folder for free-form reference / research dumps, and surface its contents through the ai_video_management webapp's sidebar viewer (alongside the existing AI Videos section).

## Original wording

> are you able to search online for the story line for some most popular chinese 仙侠剧 剧本？and dump them into a few md files
> 1: yes, 6~8 is good enough. 2: yes lets introduce a special research folder under root, and also please add the nice viewer to view them on ai_video_management project

## Desired behavior

1. **New repo-root folder `research/`.** Plain markdown dumps of reference material — initially `research/xianxia_storylines/{slug}.md` (one md per drama) plus an index `research/xianxia_storylines/README.md`. Format intentionally loose: not a spec-driven pipeline output, just structured prose / data the user can browse and feed into video planning later.
2. **ai_video_management webapp surfaces it.** The sidebar (currently a single "AI Videos" section) gets a sibling "Research" section that recursively walks `research/`. Same `<Reader>` machinery (markdown / image / qa fallback), same Origin/Host gate, same EXPOSED_TREE sandbox semantics.
3. **Same security / write contract as `ai_videos/`.** Files under `research/` are admitted by the EXPOSED_TREE `is_inside` predicate, the path-traversal hardening, and the read/write/promote allowlists exactly the same way as files under `ai_videos/`. Image files (`.png`/`.jpg`) keep their read-only contract; markdown is editable in place.
4. **Folder content is bilingual / loose.** The `agent_refs/project/ai_video.md` "everything Chinese in `ai_videos/` content" rule does NOT extend to `research/` — research dumps may mix Chinese (drama plot) with English (citations / metadata) freely. Path/file names stay ASCII.

## Why a new top-level folder, not a subfolder of `ai_videos/`

`ai_videos/{name}/` is reserved for stage-6 video-project outputs (per `agent_refs/project/ai_video.md` and CLAUDE.md "AI video rules"). Putting research dumps inside it would conflate "spec-pipeline output" with "free-form reference," confuse the regen-prompt scope semantics (`scope=project | episode N`), and risk accidental deletion when a project-scoped regen `rm -rf`'s the project folder. A sibling folder is cleaner.

## Concrete deltas

### Spec — `final_specs/spec.md`

- **FR-7 amend.** Append `research/**/*.{md,json,jsonl,yaml,yml,txt,png,jpg}` as a 5th EXPOSED_TREE root.
- **FR-8 amend.** `is_inside` predicate admits `research/` as a 4th allowed top-level (alongside the existing `ai_videos/`, plus `specs/ai_video/` and `.claude/` / `CLAUDE.md` from FR-7). The same `_EXCLUDED_DIRS` filter (`node_modules`, `.git`, `.audit`, `__pycache__`, `.pytest_cache`, `dist`, `build`, `.vite`) applies to the new admission.
- **FR-18 amend.** `GET /api/tree` now returns FOUR sections in fixed order: **AI Videos / Research / Specs (ai_video) / Context** — Specs and Context remain not-yet-implemented (acknowledged drift; tracked separately), but Research goes live in this follow-up. Implementation drift note: the current `tree_walker.py` only emits the AI Videos section; this follow-up extends it to also emit the Research section. Specs / Context sections are still future work.
- **FR-43 amend.** Sidebar fixed-order section list updated to **AI Videos / Research / Specs / Context**.
- No new FR / NFR — the Research section reuses every existing render mode dispatch, security control, and pinning rule.

### Backend — `projects/ai_video_management/backend/libs/`

- **`exposed_tree.py`** — `is_inside`'s allowed-first-segment branch extended: previously `if first == "ai_videos":`; now `if first in {"ai_videos", "research"}:`. Same excluded-dirs loop applies. Public method (kept thin, no API change).
- **`tree_walker.py`** — new `_research_section(self) -> dict` method paralleling `_ai_videos_section`. Walks `research/` recursively via the existing `_walk_filtered` helper using `_is_allowed_leaf`. Returns `{"type": "section", "name": "Research", "path": "", "children": [...]}`. Leaves use the same `_leaf_for` (so `.png`/`.jpg` get `type: "image"`). NO `project_meta` payload — Research dirs don't have a sub_type. `build()` updated to include `_research_section()` in the children list, ordered after `_ai_videos_section()` (matches FR-18 ordering).
- No changes to `api.py`, `file_reader.py`, `file_writer.py` — they already key off `is_inside` for sandbox enforcement, so the EXPOSED_TREE extension flows through automatically.

### Backend — tests

- `backend/tests/unit/test_exposed_tree.py` (if present) — add a parametrized case asserting that `is_inside("research/foo.md")` returns `True` and `is_inside("research/.git/foo")` returns `False`. If the file already covers `ai_videos/` shape, mirror those cases for `research/`.
- `backend/tests/unit/test_tree_walker.py` — add a case asserting that when `research/{slug}/file.md` exists, `walker.build()["children"]` contains a section named `"Research"` with the expected nested `children`.

### Frontend — `projects/ai_video_management/frontend/src/components/Sidebar.tsx`

- No code changes required. The sidebar already iterates `tree.children` uniformly and renders each top-level section recursively. As long as the backend emits the Research section, the sidebar surfaces it automatically with working disclosure carets, keyboard nav, and click-to-open file behavior.

### Frontend — `Reader.tsx` / `Home.tsx`

- No changes. Markdown files under `research/` dispatch to the standard markdown render path via the existing extension-based path inference (FR-48 fallback: `markdown`).

### New content — `research/xianxia_storylines/`

- One md per drama (6–8 dramas, per the user's confirmed scope). File slug is pinyin / English (e.g. `sansheng_sanshi_shili_taohua.md`); content is bilingual (Chinese plot + English / citation metadata mixed).
- Per-file structure: 中文剧名 + 英文标题 + 年份/集数/主演 + 一句话设定 + 主线剧情 (3–6 段) + 主要角色 + 关键虐点/名场面 + 题材标签 + 评分/口碑 + 来源 (Wikipedia / 百度百科 / Douban URLs).
- Index file `research/xianxia_storylines/README.md` lists every drama as a markdown link to its file with a one-liner.

## Out of scope

- Renaming `Research` to a Chinese label — kept English to match the existing "AI Videos" / "Specs" / "Context" pattern (per FR-43 and NFR-6: app chrome English, file content Chinese).
- Adding a "Research" tab to the regen-prompt panel — research files are NOT pipeline artifacts and do NOT participate in regen prompts.
- Promoting / pinning items inside research files — `POST /api/promote` is gated on `stage ∈ {"interview","findings","final_specs","validation"}` (FR-30); research is none of those.
- Moving the existing spec_driven webapp's sidebar to also include a Research section — that's a separate project with its own EXPOSED_TREE; out of scope for this ai_video_management follow-up.
- A project-meta badge for `research/{slug}/` dirs — research dumps don't have a sub_type, so no badge is rendered (FR-44 returns nothing when `project_meta` is absent — same code path).
- Image rendering deviations — `research/**/*.png` and `.jpg` route through the same `ImageRefView` / `ImagePlaceholder` machinery as `ai_videos/`. No new view mode.
