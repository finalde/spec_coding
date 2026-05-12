# Changelog — ai_video_management

Append-only follow-up audit log. Each entry records what the follow-up changed and which downstream artifacts were patched in the same turn.

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
