# Changelog — ai_video_management

Append-only follow-up audit log. Each entry records what the follow-up changed and which downstream artifacts were patched in the same turn.

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
