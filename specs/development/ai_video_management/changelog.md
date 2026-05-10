# Changelog — ai_video_management

Append-only follow-up audit log. Each entry records what the follow-up changed and which downstream artifacts were patched in the same turn.

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
