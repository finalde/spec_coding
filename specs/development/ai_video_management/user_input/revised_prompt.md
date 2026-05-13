# Revised prompt — ai_video_management

**task_type:** development
**task_name:** ai_video_management
**Composed from:** `raw_prompt.md` + `follow_ups/001-20260505-121536-ai-videos-only-scope.md` + `follow_ups/002-20260505-130548-zero-claude-coupling.md` + `follow_ups/003-20260509-152135-research-folder-and-viewer.md` + `follow_ups/004-20260509-194837-allow-chinese-filenames.md` + `follow_ups/005-20260510-161839-media-display-playback.md` + `follow_ups/006-20260510-164054-stale-runtime-instructions.md` + `follow_ups/007-20260510-170438-rename-media-to-parent-folder.md` + `follow_ups/008-20260510-201826-archive-unarchive-media.md` + `follow_ups/009-20260511-195638-import-from-downloads-classifier.md` + `follow_ups/010-20260511-120454-scene-ref-video-3.9s-all-angles.md` + `follow_ups/011-20260511-202546-batch-archive-media-multi-select.md` + `follow_ups/012-20260511-122833-backend-autoreload-stale-routes.md` + `follow_ups/013-20260511-125029-batch-trim-character-mp4-to-2.9s.md` + `follow_ups/014-20260512-201500-actor-face-pool-casting-ref-video.md` + `follow_ups/015-20260512-210500-actors-bootstrap-folder.md` + `follow_ups/016-20260512-213000-jpg-preview-uses-api-media.md` + `follow_ups/017-20260512-220000-actor-generation-progress-visibility.md` + `follow_ups/018-20260512-223000-pollinations-rate-limit-retry.md` + `follow_ups/019-20260512-214345-archive-ui-for-direct-media-views.md` + `follow_ups/020-20260512-215751-mp4-page-single-archive-button.md` + `follow_ups/021-20260512-230000-multi-provider-face-generation.md` + `follow_ups/022-20260512-220724-sidebar-collapse-all-icon.md` + `follow_ups/023-20260512-221539-delete-media-to-deleted-folder.md` + `follow_ups/024-20260512-233000-kling-text-to-image-provider.md` + `follow_ups/025-20260512-225147-kling-only-provider-and-env-file.md` + `follow_ups/026-20260512-231014-actor-folder-delete.md` + `follow_ups/027-20260512-232656-concurrency-and-variance.md` + `follow_ups/028-20260512-234309-actor-grid-view.md` + `follow_ups/029-20260513-000012-richer-variance-and-resolution-picker.md` + `follow_ups/030-20260513-001116-grid-bulk-delete-and-assign.md` + `follow_ups/031-20260513-001600-photorealism-no-wax-face.md` + `follow_ups/032-20260513-001936-grid-page-size-and-prompt-preview.md` + `follow_ups/033-20260513-002547-filename-convention-and-filters.md`

**Last regenerated:** 2026-05-13 00:25:47 — header bump for follow-up 033（用户："lets introduce some convention for the actor file names, it should be always {民族}__{性别}__{年龄段}.jpg, and then in the main 演员池page, lets add filters, like filter by race, filter by gendor, filter by age etc. and make your best guess to update existing actors to follow this new rule"）。**三个相关改动**: (1) **新 jpg 文件名约定** `{ethnicity}__{gender}__{age_range}.jpg` 在 `actor_NNNN/` folder 内；folder 名仍 `actor_NNNN/` 保持稳定 ID (casting.md / sidebar / API 引用)；sidecar 文件名仍 `actor_NNNN.md` 不变。(2) **ActorGrid 加 filter UI**: 民族 / 性别 / 年龄段 三个 dropdown，"全部" 默认；client-side filter；header 显示 `filtered / total`；filter 变化时 page reset 0。(3) **Migration**: `ActorPool.__init__` 末尾自动调 `migrate_filenames()` idempotent 扫 `_actors/`，把 legacy `actor_NNNN.jpg` 重命名到新格式（从 sidecar 读 attrs）；per-folder try/except，OSError 不阻塞启动；skips `_deleted/_actors/`。`list_actors` / `actor_exists` / `_reap_incomplete_folders` 全部改走新 helper `_find_actor_jpg` 兼容 legacy + 新格式。**Spec walk**: FR-9f 加新文件名 + auto-migrate；FR-91 加 filter UI；acceptance_criteria U3.15/U3.18 加文件名 + filter + migration 断言。**Prior 032/031/...** 保持有效。

**Prior follow-up 032:** 2026-05-13 00:19:36 — Grid PAGE_SIZE 50 + preview-then-confirm prompt 流程（保持有效；033 不动 preview / seeds 流；preview 显示的 sidecar prompt 仍正确）。
**Prior follow-up 031:** 2026-05-13 00:16:00 — Anti-wax / no-AI-face prompt 改写 + 第 18 池 PHOTOREALISM camera cue（保持有效；033 不动 prompt 文本，仅改文件名约定 + 加 filter UI）。
**Prior follow-up 030:** 2026-05-13 00:11:16 — ActorGrid select mode + bulk delete + assign-character modal（保持有效；032 PAGE_SIZE 50 不影响 select 模式逻辑；选中跨页保留行为不变）。
**Prior follow-up 029:** 2026-05-13 00:00:12 — Rich variance (17 池 ≥1000 字符) + resolution selector (普通/2K/4K) + Pillow Lanczos resize（保持有效；032 预览的就是这些 17 池 + 031 加的第 18 池组装出的 prompt；seeds 流让 Kling 收到的与 preview 完全一致）。
**Prior follow-up 028:** 2026-05-12 23:43:09 — ActorGrid 视图 + 分页（保持有效；030 在其上加 select mode + bulk delete + assign 模态；分页 + 单 tile click → detail 行为不变）。
**Prior follow-up 027:** 2026-05-12 23:26:56 — 9-way 并发 + per-image variance + race-safe ID 分配 + cap 50（保持有效；029 在其 variance pool 基础上扩展到 17 池 ≥1000 字符，race-safe + 并发不动）。
**Prior follow-up 026:** 2026-05-12 23:10:14 — actor folder delete + cascade unassign（保持有效；与 028 正交 — 026 改写 delete 路径，028 加新 read view）。
**Prior follow-up 025:** 2026-05-12 22:51:47 — Kling-only provider + `backend/.env` + `libs/env_loader.py` failfast（保持有效；027 仍用同一 KlingProvider，仅前端并发数 + prompt variance + race-safe 分配改动）。
**Prior follow-up 024:** 2026-05-12 23:30:00 — Kling text-to-image 作为第 3 个 provider 加入 chain（已被 025 部分覆盖：KlingProvider + JWT + aspect ratio mapper + SSRF-vet 保留并升为唯一 provider；chain 抽象本身被 025 删除）。
**Prior follow-up 023:** 2026-05-12 22:15:39 — mp4 / image reader Delete 按钮 + `_deleted/` 目录 + `POST /api/delete-media`（保持有效；与 025 正交）。
**Prior follow-up 022:** 2026-05-12 22:07:24 — sidebar 顶部 collapse-all 图标按钮（保持有效；与 023/024 正交）。
**Prior follow-up 021:** 2026-05-12 23:00:00 — multi-provider face generation 架构（保持有效；backend `actor_pool.py` provider chain，与 023 不相干 surface）。
**Prior follow-up 020:** 2026-05-12 21:57:51 — 收窄 follow-up 019：mp4/image reader 单按钮 archive（保持有效；follow-up 023 在 archive button 旁加 delete button + 在 `_deleted/` 内隐藏两按钮 — archive 可见性规则的小幅扩展）。
**Prior follow-up 019:** 2026-05-12 21:43:45 — Reader 渲染 dispatch 在 video / image / ImageRefView / ShotPairView 分支挂 SiblingMedia 修归档 UI 不可见（保持有效但 follow-up 020 把 video + image 分支收窄到单按钮；imageRef + shotPair 分支仍走 SiblingMedia）。
**Prior follow-up 018:** 2026-05-12 22:30:00 — pollinations.ai 429 rate-limit cascade 修复 + incomplete actor folder reclaim（保持有效；与本 follow-up 不相干 surface）。
**Prior follow-up 017:** 2026-05-12 22:00:00 — frontend loop count=1 + progress bar 修 batch generate UX（保持有效；follow-up 018 在此 progress UX 基础上加 throttle phase + backend retry）。
**Prior follow-up 016:** 2026-05-12 21:30:00 — jpg/png preview 走 /api/media，修 base64 fall-through（保持有效）。
**Prior follow-up 015:** 2026-05-12 21:05:00 — eager-mkdir `_actors/` on startup 修 follow-up 014 的 chicken-and-egg bootstrap bug（保持有效）。
**Prior follow-up 014:** 2026-05-12 20:15:00 — actor face pool + casting workflow（保持有效；follow-up 015 + 016 + 017 + 018 修其 UX / 稳定性 bug，行为契约不变）。
**Prior follow-up 013:** 2026-05-11 12:50:29 — 一次性 data-op 把 19 个 character mp4 trim 到 ≤ 2.9s（保持有效；ref-video 生成仍遵守此约束）。
**Prior follow-up 012:** 2026-05-11 12:28:33 — backend `--reload` default（保持有效）。
**Prior follow-up 011:** 2026-05-11 20:25:46 — SiblingMedia multi-select + 批量 archive/unarchive（保持有效）。
**Prior follow-up 010:** 2026-05-11 12:04:54 — scene reference video 3.9s all-angle 序列（cross-project rule，webapp 不受影响，保持有效）。
**Prior follow-up 009:** 2026-05-11 19:56:38 — 导入 + 重命名一键流程（保持有效）。
**Prior follow-up 008:** 2026-05-10 20:18:26 — per-file archive / unarchive media（保持有效；011 在其基础上加批量层）。
**Prior follow-up 007:** 2026-05-10 17:04:38 — drama-level rename-media 按钮 + `POST /api/rename-media`（保持有效）。

**Prior follow-up 006:** 2026-05-10 16:40:54 — runtime reload procedure documentation（保持有效 — 仅 documentation）。

**Prior follow-up 005:** 2026-05-10 16:18:39 — media display + playback (backend `/api/media` route + frontend Reader video/image rendering + SiblingMedia gallery)（保持有效）。

**Prior follow-up 004:** 2026-05-09 19:48:37 — 中文 filename opt-in（保持有效）。
**Prior follow-up 003:** 2026-05-09 15:21:35 — research/ folder + viewer（保持有效）。

## Goal

Build a focused viewer / editor SPA + FastAPI backend at `projects/ai_video_management/` for the artifacts under `ai_videos/{name}/` — character bibles, Seedream立绘 prompts, style guides, scripts, shotlists, dual Kling+Seedance shot prompts, publish metadata, README. The webapp ships three custom view modes that make the ai_video output structure navigable: **ShotPairView** (Kling + Seedance side-by-side), **ShotlistTableView** (clickable shot-row navigation), and **ImageRefView** (Seedream prompt + companion `.png` preview). It reuses spec_driven's security posture (Origin/Host gate, EXPOSED_TREE sandbox, RFC 7232 mtime concurrency, IPv4 loopback, light theme, CSP) but targets a single tree root: `ai_videos/`. Bound port: **8766** (parallels spec_driven's 8765 for simultaneous run).

**Per follow-up 001 + 002:** the webapp does not load, read, reference, or anchor on `specs/`, the workspace `CLAUDE.md`, or `.claude/` — at any layer. Source files contain zero references to those paths. Regen-prompt and pinning features are out of scope; users who need to drive an ai_video pipeline run regen prompts through a separate webapp dedicated to that purpose. `RepoRoot.find()` anchors on `ai_videos/` directory presence, the only path this webapp cares about.

## Context

- **Why a focused tool:** the existing `spec_driven` webapp already manages the spec pipeline (intake, interview, findings, final_specs, validation, regen prompts, pinning) for both `development` and `ai_video` task types. The user wants a complementary tool that opens directly into the *output* tree of ai_video projects, without forcing them through the spec-pipeline navigation chrome. Division of concern: spec_driven for the pipeline; ai_video_management for the artifacts.
- **Why a parallel of spec_driven structurally:** the security posture (Origin/Host gate, sandbox, traversal hardening, mtime concurrency, IPv4 loopback only, light-theme chrome, extension allowlist, CSP) is battle-tested. Reusing it verbatim is the right call. The render-mode dispatch + sidebar pattern also ports — it's just the EXPOSED_TREE membership and the stage-pipeline features that change.
- **What's specific to ai_video output:** the `prompts/shot{NN}_{kling|seedance}.md` paired-file pattern, the `shotlist.md` table that needs row-click navigation, the `characters/ref_images/{role}_seedream.md` + companion `.png` preview, and the locked-descriptor block sentinel that should render with a "锁定块" pill. These four cases drive the three new view modes plus the locked-block pill in MarkdownView.

## Desired outcome

A `projects/ai_video_management/` folder following the same structural conventions as `projects/spec_driven/`, but functionally narrowed to ai_videos/:

```
projects/ai_video_management/
├── README.md
├── Makefile                       # install / install-* / run-prod / run-backend / run-frontend / run / test-* / e2e / boot-smoke / clean
├── backend/
│   ├── main.py                    # ~15 lines — argparse + create_app + uvicorn
│   ├── requirements.txt
│   ├── libs/
│   │   ├── repo_root.py           # find CLAUDE.md + .claude/ to anchor (NOT exposed)
│   │   ├── safe_resolve.py        # path traversal hardening; allowed top-level = {"ai_videos"}
│   │   ├── exposed_tree.py        # is_inside admits ONLY ai_videos/**
│   │   ├── file_reader.py         # GET /api/file: text + image (.png/.jpg) routes
│   │   ├── file_writer.py         # PUT /api/file: text only, If-Unmodified-Since required
│   │   ├── tree_walker.py         # single-section "AI Videos" tree
│   │   ├── sub_type_lookup.py     # heuristic: episodes/ exists → novel, else → short
│   │   ├── api_security.py        # Origin/Host gate + CSP middleware
│   │   ├── api.py                 # 2 endpoints only: GET /api/tree, GET/PUT /api/file
│   │   └── __init__.py
│   ├── static/                    # bundled SPA for single-process mode
│   └── tests/                     # pytest unit + boot-smoke + Origin/Host shapes
└── frontend/
    ├── package.json               # react-resizable-panels for ShotPairView/ImageRefView
    ├── vite.config.ts             # Vite proxy /api/* → 127.0.0.1:8766 with Origin rewrite
    ├── tsconfig.json
    ├── index.html
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx                # Routes: / and /file/* only (no /project, no /stage)
    │   ├── api.ts                 # 3 calls: fetchTree, fetchFile, putFile (+ imageUrl helper)
    │   ├── localStorage.ts
    │   ├── types.ts               # TreeNode + ProjectMeta + FileResult — no Stage/Regen/Promote types
    │   ├── styles.css             # light-theme chrome + dark <pre> carve-outs
    │   ├── components/
    │   │   ├── Sidebar.tsx        # single section "AI Videos" with sub-type badges
    │   │   ├── Reader.tsx         # render-mode dispatch (no regen-panel, no cross-tree link)
    │   │   ├── Editor.tsx
    │   │   ├── BrokenLink.tsx
    │   │   ├── Breadcrumb.tsx
    │   │   ├── Home.tsx
    │   │   ├── ParseFallback.tsx
    │   │   ├── ShotPairView.tsx
    │   │   ├── ShotlistTableView.tsx
    │   │   └── ImageRefView.tsx
    │   ├── markdown/
    │   │   ├── renderer.tsx       # locked-block "锁定块" pill via pre-render regex
    │   │   ├── CodeView.tsx
    │   │   ├── JsonlView.tsx
    │   │   └── ImagePlaceholder.tsx
    │   └── lib/
    │       ├── linkResolver.ts
    │       ├── shotPairing.ts
    │       └── shotlistParser.ts
    ├── e2e/                       # Playwright (2 mode profiles)
    └── test/                      # Vitest
```

**Removed compared to v0** (per follow-up 001):
- Backend: `regen_prompt.py`, `promotions.py`, `stages.py`. `/api/regen-prompt`, `POST /api/promote`, `DELETE /api/promote`, `/api/stages` endpoints all dropped.
- Frontend: `RegeneratePanel.tsx`, `ProjectPage.tsx`, `StagePage.tsx`, `QaView.tsx`, `QaErrorBoundary.tsx`, `lib/autonomousMode.ts`, `lib/qaParser.ts`. Routes `/project/...` and `/stage/...` dropped.
- TreeNode sections: "Specs" and "Context" sections gone — sidebar emits ONLY the "AI Videos" section.

## Hard constraints (preserved from v0)

1. Localhost-only, IPv4 (`127.0.0.1`); IPv6 + `0.0.0.0` explicitly out of scope.
2. Origin/Host gate on every state-changing endpoint (now just `PUT /api/file`); foreign / wrong-port → 403; loopback aliases admit.
3. Path traversal hardening: every probe collapses to a single 404 (no existence oracle); symlinks/junctions refused.
4. Extension allowlist for reads: `.md`, `.json`, `.yaml`, `.yml`, `.jsonl`, `.txt`, `.png`, `.jpg`. SVG NOT allowed. Image extensions NOT writeable (PUT rejects with 400).
5. RFC 7232 `If-Unmodified-Since` required on PUT for existing files (divergence from spec_driven retained); stale → 409, missing → 400.
6. Markdown sanitization: `rehype-sanitize` default schema.
7. CSP header on responses: `default-src 'self'; img-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'`.
8. Light-theme chrome per `agent_refs/project/development.md` rule 1; dark `<pre>` carve-outs only.
9. FastAPI + Python 3.11+ + strong-typed `@dataclass(frozen=True)` containers; pip-only.
10. React + TypeScript + Vite + react-resizable-panels.
11. Bound port 8766 (Vite dev 5174); coexistence with spec_driven (8765/5173) intact.
12. EXPOSED_TREE membership: **single root — `ai_videos/**/*.{md,json,jsonl,yaml,yml,txt,png,jpg}`**.
13. localStorage namespace `ai_video_management.*` (still relevant for any future cross-tab state).

## Out of scope (v1, post-follow-up)

- Spec-pipeline navigation: `specs/`, `CLAUDE.md`, `.claude/` are not in EXPOSED_TREE.
- Regen-prompt assembly: not a feature of this webapp. Use `spec_driven` for that.
- Pinning (`<stage>/promoted.md`): not a feature.
- QaView render mode for spec interview pages: not applicable.
- Cross-tree link "查看规格": removed.
- Render-API integration with Kling / Seedance / Seedream (text-prompt viewing/editing only).
- Multi-tenant / multi-user; auth; WebSockets; mobile-responsive; storyboard horizontal-scroll view; cross-publish manager; English translation; project-diff view; file create/delete/upload through the webapp; dark-mode chrome toggle; file-system watcher.

## Success looks like

1. `make run-prod` → open `http://127.0.0.1:8766/` → recursive sidebar shows ONE section: AI Videos. The `wukong_juexing` entry has a `短` badge.
2. Click `ai_videos/wukong_juexing/prompts/shot02_kling.md` → ShotPairView with Kling on left + Seedance on right + per-pane copy buttons.
3. Click `ai_videos/wukong_juexing/shotlist.md` → ShotlistTableView; each `shotNN` cell is a button → opens that shot's pair view.
4. Click `ai_videos/wukong_juexing/characters/ref_images/main_seedream.md` → ImageRefView; left = prompt, right = companion `.png` if present, else fallback message.
5. Click `ai_videos/wukong_juexing/characters/main.md` → MarkdownView with the **锁定块** pill on the descriptor.
6. No "Specs" section. No "Context" section. No regen-prompt panel. No cross-tree link.
7. PUT `/api/file` succeeds for editable text files; rejects images with 400; missing `If-Unmodified-Since` returns 400; stale returns 409.
8. spec_driven on 8765 continues to handle regen + pinning for ai_video projects (unchanged).
