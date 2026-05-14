# Revised prompt — ai_video_management

**task_type:** development
**task_name:** ai_video_management
**Composed from:** `raw_prompt.md` + every `follow_ups/*.md` in numerical order (001–044 prior; 045 fixes the `.env` location post-039 migration — see `follow_ups/045-20260513-231500-env-file-location-and-asgi-mismatch.md`)

**Last regenerated:** 2026-05-14 — header bump for follow-up 045 (Backend boot failed with `RuntimeError: kling env keys missing; set KLING_ACCESS_KEY + KLING_SECRET_KEY`. Two reasons: [1] post-039 migration the project `.env` file was never recreated at the new canonical path `apps/api/.env` — follow-up 025's `backend/.env` is the same intent at the new location. [2] `apps/api/asgi.py` had a stale `Path(__file__).resolve().parent.parent / ".env"` left over from when it lived at `backend/libs/asgi.py` — at the new path that expression yields `apps/` (one level too high), disagreeing with `main.py`'s `parent / ".env"` = `apps/api/.env`. **Fix:** asgi.py now reads `parent / ".env"` (aligned with main.py); concrete Kling keys live in untracked `apps/api/.env` (gitignored line 138, verified by `git check-ignore`). **Spec walk:** any future text referring to `backend/.env` should read `apps/api/.env` going forward; no API / HTTP / behavior change. Prior 044 (lib/dramas.ts) + 043 (assignments) + 042/041/040/039 all remain in force.

**Prior regen 6:** 2026-05-13 23:05:00 — header bump for follow-up 044 (Vite `[plugin:vite:import-analysis] Failed to resolve import "../lib/dramas" from "src/components/ActorView.tsx"`. **Implementation gap from 043 item #9**: the `extractDramas` / `findChild` / `DramaChoice` extract from `ActorGrid.tsx` removed the inline definitions and updated both `ActorGrid.tsx` + `ActorView.tsx` to import from `../lib/dramas`, but the target file `apps/ui/src/lib/dramas.ts` itself was never written. **Fix**: write `apps/ui/src/lib/dramas.ts` containing exactly the logic captured from the last commit before 043 — `interface DramaChoice { path; name; characters[] }` + `extractDramas(tree)` walks `ai_videos` directory children (non-`_` prefix), pulls `characters/c\d+(_.*)?` subdirs into `characters` array + `findChild(node, name)` helper. **Zero behavior delta** vs. 043's intended state. Backend / HTTP routes / JSON shapes / `_cast.md` semantics / 409 refuse-if-assigned all unchanged. Prior 043 (assign-from-actor-page) remains in force.

**Prior regen 5:** 2026-05-13 22:47:37 — header bump for follow-up 043 (用户："lets add a new feature for the actor page, I could assign the actor to a specific role under a specific ai_video project. It is like multi dropdown. Once assigned the role, you need to maintain a link of the actor under the charactor folder, you could aslo see the picture of the actor. Note one actor could play many roles in differnet ai videos, but one ai vidoe charactor could only be one actor. When an actor has a role assigned, it cannot be deleted or archived."). **ActorView assignments + 角色 folder 链接 + delete 拒绝**：(1) 新 endpoint `GET /api/actors/assignments?actor_id=...` + `Casting.find_assignments_for_actor`; (2) `Casting.assign` / `unassign` 同步维护 `ai_videos/{drama}/characters/{role}/_cast.md`（actor face 图 + 链接），character folder 不存在则静默跳过；(3) `POST /api/actors/delete` 改为 **refuse-if-assigned**（不再 cascade-unassign），返 `409 actor_is_assigned`；(4) `POST /api/archive-media` & `POST /api/delete-media` 当 path 在 `_actors/actor_NNNN/` 下且 actor 有分配时同样 409；(5) `ActorView` 新增"🎬 角色分配 (N)"区块：列表 + 取消按钮 + 级联 drama→role dropdown + notes textarea + 确认；header `🗑 删除` 按钮在 assignments>0 时 disabled 并显 tooltip；(6) `App.tsx`/`Reader.tsx` 透传 `tree` 给 `ActorView`，`lib/dramas.ts` 共享给 `ActorGrid` + `ActorView`。**Spec walk**: FR-9g/FR-9h 描述 `_cast.md` 同步写/删；FR-9i 改写为 refuse-on-assigned；FR-9s 新增 `GET /api/actors/assignments`；FR-9c/FR-9k extension 块说明 archive/delete-media 在 `_actors/{id}/` 下的 409；FR-95 新 ActorView assignments section 契约。acceptance_criteria U3.23 全链路场景。**Prior 042 / 041 / 040 / 039** 全部保持有效；本 follow-up 不动 frame extraction / uvicorn / sidebar 置底 / DDD layout 任何路径。

**Prior regen 4:** 2026-05-13 22:50:19 — header bump for follow-up 042 (用户："I got some error again, the appliation just stucked: ...frames5.png HTTP/1.1 200 OK / WatchFiles detected changes in 'libs\\tree_walker.py'. Reloading... / Shutting down / Waiting for connections to close. (CTRL+C to force quit)"). **dev-reload 强制退出兜底**：follow-up 037 的 `timeout_graceful_shutdown=2` 让 uvicorn 在 2s 后 cancel asyncio task，但 FastAPI sync `def` endpoint 跑在 anyio threadpool 里，cancel asyncio wrapper 不会 kill 底层线程；Kling 30-120s HTTP / `/api/media` range stream / ffmpeg / pollinations 这些 blocking sync 调用让非-daemon 线程占住 Python 进程，导致 `sys.exit` join 线程时永久卡死。新 `libs/uvicorn_force_exit.py::install()` monkey-patch `uvicorn.Server.handle_exit`：signal 收到后除了走 uvicorn 自己的 graceful（仍是首选）外，再起一个 daemon `threading.Timer((timeout_graceful_shutdown or 0) + 2.0, lambda: os._exit(0))` 兜底；总时长 ≤ ~4s 进程必死。`main.py` 与 `libs/asgi.py` 顶部各调一次（reload 子进程经 asgi import，--no-reload 经 main）。**Spec walk**: FR-2 行追加 follow-up 042 amendment + 加 manual U2.5 acceptance + 覆盖矩阵 FR-2 行补 U2.5。041 / 040 / 039 narrative 保持不变；037 `timeout_graceful_shutdown=2` 是本 follow-up 的前置依赖（patch 读 `config.timeout_graceful_shutdown` 算 deadline）。

**Prior regen 3:** 2026-05-13 22:58:00 — header bump for follow-up 041 (用户："for the frames folder generated under a scene folder, I need better naming convention for the frame files, you should tell me things like if is hero wide or reverse wide, and there should be a fixed 8 pictures frames generated? ... please rank the pictures with order, in case I can only upload 3 as reference, I know which one to upload"). **Frame extraction v2**: 5 帧 → **8 帧**（5 个 canonical dwell + 3 个战略 transition：side / threequarter / mediumclose），命名约定从 `_f{N}_{role}.png` 改为 **`_r{rank}_{role}_{shot_size}.png`**（rank 1-8 = 上传优先级；字典序 = 优先级序），rank 1-3 覆盖三档不同焦段 medium / wide / telephoto 信息密度最高。**Renamer bug 同修**：`MediaRenamer.rename_drama` 在 `/api/rename-media` (api.py) + import-from-downloads 链式 rename (downloads_importer.py) 两条 caller 都新增/扩展 `excluded_folder_names` 排除 `"frames"`，避免之前的 `frames1.png ~ framesN.png` 命名丢失实测 bug。Extract 起点新增 `frames/*.png` sweep，自动 idempotent 清理 v1 残留 + 任何 rename 残留。`ExtractedFrame` API + TS interface 新增 `rank: int` 与 `shot_size: str` 字段。**Spec walk**: 新增 **FR-9r** 端点契约（8 帧 + rank + shot_size + sweep + rename 排除）。Prior 040 (`_deleted` 置底) 不变。

**Prior regen 2:** 2026-05-13 22:46:35 — header bump for follow-up 040 (用户："in ai_video_management left nav, lets move _deleted to the bottom of the left nav"). **Sidebar `_deleted/` 置底**：`tree_walker.py::_ai_videos_section` 分离 `_deleted` 节点，其它 ai_videos 顶层子目录（包括 `_actors/`）保持 alphabetical，循环结束把 `_deleted` append 到 children 末尾。纯 backend 改动，零 frontend，`/api/tree` shape 不变。**Spec walk**: FR-20 加 follow-up 040 amendment 行（`_deleted` hoist 规则）。Prior 039 `apps/+libs/` layout 改造仍未应用到代码；当迁移时该规则随 `tree_walker.py` 一起搬到 `libs/infrastructure/` 或 `libs/application/`，语义不变。

**Prior regen 1:** 2026-05-13 12:00:00 — header bump for follow-up 039 (项目采纳 `.claude/agent_refs/project/development.md` §1–6 的 `apps/+libs/` 解决方案布局：`backend/` → `apps/api/`，`frontend/` → `apps/ui/`，`backend/libs/*.py` 拆分到 `libs/{infrastructure,domain,application,common}/`，文件名/类名采用 `__` 后缀约定，加 `dependency_injector` 注入。HTTP 路由与 JSON 形状不变，只动内部组织。Prior 037 (uvicorn `timeout_graceful_shutdown=2`) 保持有效，调用位置改为 `apps/api/main.py`。)

**Prior follow-up 038:** 2026-05-13 22:23:41 — `_deleted/` 内 bulk hard-delete + 第 18 个 endpoint `POST /api/hard-delete-media` + `DeletedView` 多选页面 + typed-DELETE 模态 + sidebar `_deleted/` 行 "🧹 永久清理" 按钮（保持有效；039 把 `backend/libs/media_archiver.py` 移到 `apps/api/libs/infrastructure/...` 时需要保留 `hard_delete` 方法 + `NotInDeleted` exception + `_deleted/` 前缀校验；frontend `DeletedView.tsx` 移到 `apps/ui/src/components/`；HTTP route shape `POST /api/hard-delete-media` 不变）。

**Prior regen:** 2026-05-13 22:25:21 — header bump for follow-up 037（用户："once a while I will encounter errors and the system just stuck: WatchFiles detected changes... Shutting down... Waiting for connections to close. (CTRL+C to force quit)"）。**Dev reload 卡死修复**：`backend/main.py` 两条 `uvicorn.run(...)` 调用各加 `timeout_graceful_shutdown=2`（uvicorn ≥0.29 即支持，requirements 已固定）。根因：本项目 ~25 个 endpoint 全部同步 `def`，长任务（Kling face generation 30–120s / `/api/extract-frames` 1–5s / `/api/import-from-downloads` 5–20s）会持续占线程；uvicorn 默认 `timeout_graceful_shutdown=None` 让 reload 触发的 graceful shutdown wait-forever，user 看到 terminal 卡 `Waiting for connections to close` 行。加 2s 强制截断保证 dev 循环 reload 稳定。**Spec walk**: FR-2 行同步更新 `uvicorn.run` 调用 shape 描述。**Prior 036 (actor folder 折叠 + ActorView delete)** 保持有效。

**Prior follow-up 036:** 2026-05-13 22:23:53 — actor folder 折叠成单 leaf + ActorView 内置 delete（保持有效；037 不动 tree_walker / Sidebar / ActorView，仅修 uvicorn shutdown timing）。

**Prior follow-up 035:** 2026-05-13 11:00:00 — Extract Frames per-video button + `POST /api/extract-frames` 端点 + `frame_extractor.py`（保持有效；036 不动 SiblingMedia 与 frame extraction，仅折叠 actor folder 树节点）。

**Prior follow-up 034:** 2026-05-13 00:38:00 — actor md 读视图 + 无 bulk toolbar（保持有效；本 follow-up 035 不动 actor 视图，仅扩展 SiblingMedia 的按钮组）。
**Prior follow-up 033:** 2026-05-13 00:25:47 — actor jpg 文件名约定 `{ethnicity}__{gender}__{age_range}.jpg` + ActorGrid filter UI + idempotent migration（保持有效；034 不动文件名 / filter / migration，仅改 actor md 读视图）。

**Prior follow-up 032:** 2026-05-13 00:19:36 — Grid PAGE_SIZE 50 + preview-then-confirm prompt 流程（保持有效；033 不动 preview / seeds 流；preview 显示的 sidecar prompt 仍正确；034 新 ActorView 读视图复用同一 sidecar 的 prompt 字段，仅展示样式变化）。
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
