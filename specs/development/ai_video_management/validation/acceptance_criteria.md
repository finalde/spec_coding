# 验收标准 — ai_video_management

阶段 5 · 级别 1 · acceptance_criteria
来源 spec：`final_specs/spec.md`（85 FR + 7 NFR + 8 primary flows + U1–U7）

## 总览

本文件以 Gherkin（Given/When/Then）形式定义 `ai_video_management` 的可验收行为，覆盖：

- **8 个主流程**（spec § Primary flows）— 每条主流程至少 1 个端到端场景。
- **7 个工作单元**（U1–U7）— 每个工作单元的内部产物以独立 group 列出。
- **load-bearing FR**：FR-1..FR-85（共 85 项）— 全部映射到至少一个场景；映射见末尾覆盖矩阵。

约定：

- `[automated]` = 由 pytest / Vitest / Playwright 在 CI 触发，断言失败即 `blocker` 或更高（按 `agent_refs/validation/development.md` 严重度表）。
- `[manual_walkthrough_only]` = 视觉、对比度、感知延迟类，必须由 `make run-prod` + `make run-frontend` 各一次走查；触发 `validation.requires_manual_walkthrough`（参见 `validation/general.md` 原则 4）。
- 每个 `Scenario` 顶部以 `# 来源 FR: FR-X[, FR-Y...]` 注明溯源。
- 共 30 个场景（24 自动化 + 6 手动），位于 25–35 上限内。

并发与隔离：自动化场景假定 `make run-backend`（端口 8766）+ Vite dev server（端口 5174），且 `spec_driven` webapp 不在 8765 上跑（否则 8765 跨端口拒绝场景需用打桩 Origin 头模拟）。

---

## 自动化场景

### U1 — backend libs core

#### Scenario U1.1 — 后端核心 lib 文件就位
# 来源 FR: FR-1
[automated]

```gherkin
Given 工作树位于 projects/ai_video_management/
When 列出 backend/libs/ 目录
Then 必须存在以下文件且单文件大小 > 0:
  | repo_root.py | file_reader.py | file_writer.py | promotions.py |
  | safe_resolve.py | exposed_tree.py | tree_walker.py | regen_prompt.py |
  | stages.py | api_security.py | api.py | sub_type_lookup.py | main.py |
And 不得存在 backend/libs/render_views.py
```

#### Scenario U1.2 — EXPOSED_TREE 仅放行 4 个根
# 来源 FR: FR-7, FR-8
[automated]

```gherkin
Given exposed_tree.is_inside(repo_root, candidate)
When 候选路径为 ai_videos/x/y.md → 应返回 True
And 候选路径为 specs/ai_video/x/y.md → 应返回 True
And 候选路径为 CLAUDE.md → 应返回 True
And 候选路径为 .claude/skills/agent_team/SKILL.md → 应返回 True
And 候选路径为 projects/spec_driven/backend/libs/api.py → 应返回 False
And 候选路径为 specs/development/anything.md → 应返回 False
```

#### Scenario U1.3 — sub_type_lookup 解析 qa.md 的规范行
# 来源 FR: FR-22, FR-23, FR-24
[automated]

```gherkin
Given specs/ai_video/wukong_juexing/interview/qa.md 含一行 "| `sub_type` | `novel` |"
When 调用 sub_type_lookup.lookup("wukong_juexing")
Then 返回 "novel"

Given qa.md 缺失 / 没有 sub_type 行 / 值是 "longform" / 多个 sub_type 行
When 调用 sub_type_lookup.lookup(...)
Then 返回 None 而非崩溃，且不得返回第三种字面量
```

#### Scenario U1.4 — promotions._parse / _serialize 与 spec_driven 字节相同
# 来源 FR: FR-33
[automated]

```gherkin
Given 取 spec_driven/backend/libs/promotions.py 的 _parse_promoted_text 与 _serialize_promoted_block 字节
When 与 ai_video_management/backend/libs/promotions.py 同名函数比较
Then 函数体字节相同（去除模块路径常量后，AST 等价；并提供至少 3 条样例输入做 round-trip 等价测试）
```

### U2 — backend tree + regen

#### Scenario U2.1 — `GET /api/tree` 三段式 + 消费者递归走法
# 来源 FR: FR-18, FR-19, FR-20, FR-43
[automated]

```gherkin
Given 后端运行于 127.0.0.1:8766
When GET /api/tree
Then 返回 200，body 是数组，长度恰为 3，name 依次为 "AI Videos" / "Specs" / "Context"
And 对返回值调用 walker(node) → node.children → 递归，所有非叶子节点必须有 children 字段（来源 development.md 移动 #2）
And 同一层内目录排在文件之前，组内字母序（FR-20）
And 每个 ai_videos/{name}/ 目录节点带 project_meta，project_meta.sub_type ∈ {"novel","short", null}
```

#### Scenario U2.2 — TreeNode 含 image 类型与 mtime
# 来源 FR: FR-19
[automated]

```gherkin
Given ai_videos/wukong_juexing/characters/ref_images/main_seedream.png 存在
When GET /api/tree
Then 在路径下能找到 type == "image" 的叶子，mtime 为 epoch 浮点数
And 同目录下 main_seedream.md 的叶子 type == "file"
```

#### Scenario U2.3 — regen_prompt 阶段 1–5 与 spec_driven 字节同一
# 来源 FR: FR-37
[automated]

```gherkin
Given 同一 (stage, modules, mode) 输入，stage ∈ {intake, interview, research, spec, validation_strategy}
When 调用 ai_video_management.regen_prompt.build(...) 并去除 project_type=ai_video / sub_type 行
Then 与 spec_driven.regen_prompt.build(...) 的产物字节相同（行序、缩进、空行均一致）
```

#### Scenario U2.4 — regen_prompt 阶段 6 四种 short/novel × project/episode/episodes 形态
# 来源 FR: FR-38, FR-39
[automated]

```gherkin
Given project_type=ai_video, stage=execution

When (sub_type=short, scope=project)
Then 产物含 short 布局的删除契约 + 写入契约（agent_refs/project/ai_video.md 规则 10）

When (sub_type=novel, scope=project)
Then 产物含 novel 布局的删除契约 + 写入契约

When (sub_type=novel, scope=episode, scope_episode=3)
Then 产物的删除范围限定为 ai_videos/{name}/episodes/ep03/
And 产物含 "preserves characters/, world.md, style_guide.md, arc_outline.md, sibling episodes" 文本
And 产物禁止编辑上述 preserved 路径

When (sub_type=novel, scope=episodes, scope_episode_range={start:5,end:7})
Then 产物展开为字面 ep05 / ep06 / ep07 三个目录，不含 "M..N" 简写

In all four cases:
And 产物 inline 了 revised_prompt.md 全文 + 所有 user_input/follow_ups/*.md 全文
And 产物 inline 了 read-zero contract 与 audit-event 标签 (regen.delete.planned, regen.delete.completed, regen.write.completed)
And 产物以 "# EXECUTION MODE: AUTONOMOUS" 或 "# EXECUTION MODE: INTERACTIVE" 起首
```

### U3 — backend api + main + security

#### Scenario U3.1 — main.py ≤ 15 行且仅调用 api.create_app + uvicorn.run
# 来源 FR: FR-2, FR-3, FR-4
[automated]

```gherkin
Given backend/libs/main.py
When 解析为 AST 并统计非空非注释行
Then 行数 ≤ 15
And uvicorn.run 调用的 host 字面量 == "127.0.0.1"，port 字面量 == 8766
And 文件中不出现 "0.0.0.0" 或 "[::1]" 字面量
```

#### Scenario U3.2 — Origin/Host gate 拒绝 8765 与外域
# 来源 FR: FR-11, FR-28
[automated]

```gherkin
Given 后端运行于 127.0.0.1:8766
When PUT /api/file 头 Origin=http://127.0.0.1:8765 → 返回 403
And PUT /api/file 头 Origin=http://example.com → 返回 403
And PUT /api/file 缺失 Origin 头 → 返回 403
And PUT /api/file 头 Origin=http://localhost:8766 → 返回 200/409（视 mtime 而定，不为 403）
And PUT /api/file 头 Origin=http://127.0.0.1:8766 → 返回 200/409（视 mtime 而定）
```

#### Scenario U3.3 — Origin gate 双形态测试（pre-rewrite + post-rewrite + 真实代理）
# 来源 FR: FR-6, FR-11；development.md 移动 #11
[automated]

```gherkin
Given Vite dev server 在 5174 上把 Origin 改写为 8766 后转发到后端
When 直发后端 + Origin=http://127.0.0.1:5174 → 返回 403 (pre-rewrite shape)
When 直发后端 + Origin=http://127.0.0.1:8766 → 返回 200/409 (post-rewrite shape)
When 经 5174 代理 + 浏览器侧 Origin=http://127.0.0.1:5174 → 返回 200/409（真实链路）
```
*缺失 pre-rewrite 用例 = `blocker`（development.md 严重度表）。*

#### Scenario U3.4 — 路径遍历探针全部塌缩为 404
# 来源 FR: FR-12
[automated]

```gherkin
Given 后端运行
When GET /api/file?path=../CLAUDE.md
And GET /api/file?path=ai_videos/..%2Fsecrets.txt
And GET /api/file?path=ai_videos\xx\NUL
And GET /api/file?path=ai_videos/foo.md\
And GET /api/file?path=PROGRA~1/x.md   # 8.3 短名
Then 全部返回 404，body 不得透露 "exists" / "outside tree" 等区分性文案
And 指向 symlink / Windows junction 的路径 → 返回 404（不读取目标）
```

#### Scenario U3.5 — 扩展名白名单 + 图片不可写
# 来源 FR: FR-13, FR-28
[automated]

```gherkin
When GET /api/file?path=ai_videos/x.svg → 返回 404
And GET /api/file?path=ai_videos/x.exe → 返回 404
And GET /api/file?path=ai_videos/x.png → 返回 200 + Content-Type: image/png
And PUT /api/file body.path=ai_videos/x.png → 返回 400
And PUT /api/file body.path=ai_videos/x.md (合法 mtime) → 返回 200
```

#### Scenario U3.6 — 1 MiB 上限 + If-Unmodified-Since 并发
# 来源 FR: FR-14, FR-15, FR-27, FR-29
[automated]

```gherkin
When PUT /api/file body 大小 = 600 KiB → 返回 200，并在 stdout 含 "soft warning: >50KiB"
When PUT /api/file body 大小 = 1.5 MiB → 返回 413
When PUT /api/file 缺失 If-Unmodified-Since → 返回 400 或 412 (规范要求该头必填)
When PUT /api/file 提供过期 mtime → 返回 409
When PUT /api/file 成功 → 响应 body 含 mtime 浮点；磁盘上写入是 "tmp + rename" 原子（验证：写入期间无半文件）
```

#### Scenario U3.7 — CSP 头 + markdown sanitization
# 来源 FR: FR-16, FR-17
[automated]

```gherkin
When 任意 GET 响应
Then 响应头含 "Content-Security-Policy: default-src 'self'; img-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'"

Given GET /api/file 返回的 markdown 含 "<script>alert(1)</script>" 与 'href="javascript:alert(1)"'
When 前端 MarkdownView 渲染
Then DOM 中无 <script> 节点；href 被 rehype-sanitize 默认 schema 剥离
```

#### Scenario U3.8 — 4 个变更端点 + 2 个读端点，无更多
# 来源 FR: FR-9, FR-10
[automated]

```gherkin
Given FastAPI app.routes
When 收集所有非 OPTIONS / HEAD 路由
Then 仅有以下 6 条 (path, method) 对外（不含静态文件）:
  | GET    /api/tree         |
  | GET    /api/file         |
  | PUT    /api/file         |
  | POST   /api/regen-prompt |
  | POST   /api/promote      |
  | DELETE /api/promote      |
And 不存在任何 POST / PUT / DELETE 用于创建/上传/删除任意文件的路由
```

#### Scenario U3.9 — promote 拒绝 stage=execution 与 ai_videos/ 路径
# 来源 FR: FR-30, FR-31, FR-32
[automated]

```gherkin
When POST /api/promote body.stage="execution" → 返回 400
When POST /api/promote body.stage="findings", source_path="ai_videos/wukong/foo.md" → 返回 400
When POST /api/promote body.stage="findings", source_path="specs/ai_video/wukong/findings/dossier.md" → 返回 200，且 specs/ai_video/wukong/findings/promoted.md 追加了对应块
When DELETE /api/promote body.stage="findings", item_id="..." → 返回 200，promoted.md 中对应块消失
```

#### Scenario U3.10 — regen-prompt 错误码面
# 来源 FR: FR-34, FR-35, FR-36
[automated]

```gherkin
When POST /api/regen-prompt body.project_type="development" → 返回 400
When body.scope="episode" 但 sub_type=short → 返回 400
When body.scope="episode" 但缺 scope_episode → 返回 400
When body.scope="episodes" 但 start > end → 返回 400
When body.scope="episode", project sub_type 未知 (qa.md 缺失) → 返回 409
When 组装后 body > 1 MiB → 返回 413
When 成功 → 响应含 {prompt, scope, scope_resolved, byte_size}, byte_size == len(prompt.encode("utf-8"))
```

#### Scenario U3.11 — boot-smoke：进程起得来 + /api/tree 真实 200
# 来源 FR: FR-83；development.md 移动 #4
[automated]

```gherkin
Given `make boot-smoke`
When pytest fixture 启动 backend，等待端口
Then GET / 返回 200
And GET /api/tree 返回 200 且 body 是长度 3 的数组（结构性断言，不仅是 status code）
```
*失败 = `critical`（development.md 严重度表：boot-time exception）。*

#### Scenario U3.12 — `POST /api/rename-media` drama-scoped batch（follow-up 007）
# 来源 FR: FR-9b
[automated]

```gherkin
Given fixture drama at `ai_videos/{tmp_drama}/` with sample shot folder containing 2 mp4 + 1 png with arbitrary names
When POST /api/rename-media with body {path: "ai_videos/{tmp_drama}"}
Then 响应 200 + body 含 renamed[]: {from, to} 列表 + skipped[] + errors[]
And 同 ext 多文件 → {parent}{N}.{ext} 序号；单 ext 单文件 → {parent}.{ext} 无序号
And path = "ai_videos/" 单层 / "ai_videos/{tmp_drama}/sub/sub" 多层 → 400 invalid_drama_path
And path 指向不存在的 drama → 404 not_found
And 非 POST → 405
```

#### Scenario U3.14 — `POST /api/import-from-downloads` 分类导入 + chain rename（follow-up 009）
# 来源 FR: FR-9e
[automated]

```gherkin
Given fixture drama at `ai_videos/{tmp_drama}/` with characters/c1_aaa/ + scenes/s1_bbb/ + episodes/ep01/prompts/shot01/
And fixture Downloads dir (env AI_VIDEO_MGMT_DOWNLOADS_DIR) containing:
  * kling_c1_aaa_test.mp4 (mtime: now-1d)
  * scene_s1_bbb_v2.png (mtime: now-2d)
  * ep01_shot01_seedance.mp4 (mtime: now-3d)
  * random_unrelated.mp4 (mtime: now-1h)
  * old_stuff.mp4 (mtime: now-30d, BEYOND window)
  * trailer_doc.pdf (non-media, must skip)
  * a_symlink.mp4 (symlink, must skip)
When POST /api/import-from-downloads with body {path: "ai_videos/{tmp_drama}"}
Then 响应 200
And response.moved 含 3 项：kling_c1_aaa_test.mp4 → characters/c1_aaa (kind=character)，scene_s1_bbb_v2.png → scenes/s1_bbb (kind=scene)，ep01_shot01_seedance.mp4 → episodes/ep01/prompts/shot01 (kind=shot)
And response.unmatched 含 1 项：random_unrelated.mp4 → ai_videos/{tmp_drama}/not_matched/random_unrelated.mp4 (kind=unmatched)
And response.errors[] 不含 old_stuff.mp4 / trailer_doc.pdf / a_symlink.mp4（这些被 window/ext/symlink 静默跳过，不计入 errors）
And response.rename = {renamed:[...重命名前 3 个 + 不含 not_matched 内的文件...], skipped:[], errors:[]}
And 磁盘上 ai_videos/{tmp_drama}/not_matched/random_unrelated.mp4 保留原文件名（未被 rename 触及）
And 磁盘上 ai_videos/{tmp_drama}/characters/c1_aaa/c1_aaa.mp4 已被 rename
When 第二次 POST /api/import-from-downloads 对同一 drama（Downloads 已空）
Then 响应 200 + moved=[] + unmatched=[] + errors=[] + rename.renamed=[]
When path 非 drama-level（如 "ai_videos/" 或 "ai_videos/{drama}/sub"）→ 400 invalid_drama_path
When path 指向不存在 drama → 404 not_found
When AI_VIDEO_MGMT_DOWNLOADS_DIR 指向不存在路径 → 500 downloads_dir_missing
When 非 POST → 405
And 端点经过 Origin/Host gate（foreign Origin → 403）
```

#### Scenario U3.13 — `POST /api/archive-media` + `POST /api/unarchive-media`（follow-up 008）
# 来源 FR: FR-9c, FR-9d
[automated]

```gherkin
Given fixture media file at `ai_videos/{tmp_drama}/x/foo.mp4`（archive/ 不存在）
When POST /api/archive-media with body {path: "ai_videos/{tmp_drama}/x/foo.mp4"}
Then 响应 200 + body = {from: "ai_videos/{tmp_drama}/x/foo.mp4", to: "ai_videos/{tmp_drama}/x/archive/foo.mp4"}
And 磁盘上 archive/ 已被 mkdir + 文件已 rename 进去
When 二次 POST /api/archive-media 对已 archive 的同一 path → 404 not_found（源已不存在）
When POST /api/archive-media 对 path 已在 archive/ 内 → 400 already_archived
When POST /api/archive-media 对 .md 文件 → 400 extension_not_allowed
When POST /api/archive-media 对 archive/foo.mp4 已存在的 target → 409 target_exists
When POST /api/unarchive-media with body {path: "ai_videos/{tmp_drama}/x/archive/foo.mp4"}
Then 响应 200 + body = {from: "...archive/foo.mp4", to: ".../foo.mp4"}
And 磁盘上 archive/ 已被 rmdir（空了）+ foo.mp4 已 rename 回 parent
When POST /api/unarchive-media 对非 archive/ 内文件 → 400 not_in_archive
When 非 POST → 405
And 两个端点均经过 Origin/Host gate（foreign Origin → 403，与 PUT /api/file 一致）
```

#### Scenario U3.15 — `POST /api/actors/generate` 批量生成 + pollinations.ai 出站 HTTP（follow-up 014）
# 来源 FR: FR-9f, FR-86
[automated]

```gherkin
Given 空目录 ai_videos/_actors/ 不存在
And ActorPool 的 httpx 客户端被 monkey-patch 为返回固定 12-byte JPEG payload（模拟 pollinations.ai 成功响应）
When POST /api/actors/generate with body {count: 3, ethnicity: "asian", gender: "male", age_range: "18-25", look: "handsome", style: "modern-casual", notes: "test"}
Then 响应 200
And response.generated 长度 = 3
And response.generated[0].id = "actor_0001"，[1].id = "actor_0002"，[2].id = "actor_0003"
And 磁盘上 ai_videos/_actors/actor_0001/actor_0001.jpg 存在 + actor_0001.md 存在
And actor_0001.md 含属性表（ethnicity / gender / age_range / look / style / notes）+ 组装的英文 prompt + seed
When 第二次 POST /api/actors/generate 同一参数 count=2
Then 响应 200 + generated[0].id = "actor_0004"，[1].id = "actor_0005"（ID 单调自增，不复用）
When POST body 中 ethnicity = "klingon"（不在 enum） → 400 invalid_attribute
When POST body 中 count = 0 或 count = 21 → 400 invalid_attribute（同 kind，code 复用）
When ActorPool 客户端 monkey-patch 为模拟 timeout → 那 1 张归 errors[]，其它 (count - 1) 张正常生成；状态 200
When 非 POST → 405
```

#### Scenario U3.16 — casting.md upsert / delete + GET /api/casting + GET /api/actors（follow-up 014）
# 来源 FR: FR-9g, FR-9h, FR-10b, FR-10c
[automated]

```gherkin
Given fixture drama at ai_videos/{tmp_drama}/ + pool 内 actor_0001 / actor_0002 已存在（fixture 创建）
And ai_videos/{tmp_drama}/casting.md 不存在
When POST /api/casting/assign with body {path: "ai_videos/{tmp_drama}", role: "c1_主角", actor_id: "actor_0001", notes: "魔尊"}
Then 响应 200 + path = "ai_videos/{tmp_drama}/casting.md" + entries 长度 = 1
And 磁盘上 casting.md 被创建，含 header + markdown 表，含 1 行 c1_主角 → actor_0001 → 魔尊
When POST 同一 role 但 actor_id = "actor_0002"（修改 cast）
Then 响应 200 + entries 长度 = 1（覆盖，不重复）+ row 现在指向 actor_0002
When POST 新 role "c2_配角" actor_id = "actor_0001"
Then 响应 200 + entries 长度 = 2
When GET /api/casting?path=ai_videos/{tmp_drama}
Then 响应 200 + entries = [{role: "c1_主角", actor_id: "actor_0002", notes: ""}, {role: "c2_配角", actor_id: "actor_0001", notes: ""}]
When DELETE /api/casting/assign with body {path, role: "c1_主角"}
Then 响应 200 + entries 长度 = 1 + c1_主角 row 已删
When POST /api/casting/assign with body {path, role: "c3", actor_id: "actor_9999"}（不存在）
Then 响应 400 invalid_actor_id
When POST body 中 path = "ai_videos/" 或 "ai_videos/{drama}/sub" → 400 invalid_drama_path
When path 指向不存在 drama → 404 not_found
When GET /api/actors
Then 响应 200 + actors 数组按 id 升序，每条含 ethnicity / gender / age_range / look / style / notes / image_path / mtime
And 缺 sidecar md 或 jpg 的 actor folder 静默跳过（warning logged 但不进 response）
When 非 POST/DELETE 到 /api/casting/assign → 405
```

### U4 — frontend scaffolding

#### Scenario U4.1 — 前端骨架文件就位 + 依赖固定
# 来源 FR: FR-40, FR-41, FR-42
[automated]

```gherkin
Given projects/ai_video_management/frontend/
When 列出文件
Then 必须存在: package.json, vite.config.ts, tsconfig.json, index.html
And src/main.tsx, src/App.tsx, src/styles/app.css 存在
And package.json 的 dependencies 含: react ^18, react-dom ^18, react-markdown ^9, remark-gfm ^4, rehype-sanitize ^6, react-router-dom ^6, react-resizable-panels ^4
And devDependencies 含: vite ^5, typescript ^5, vitest, @playwright/test
And 不含未在 spec FR-42 列举的运行时依赖
```

#### Scenario U4.2 — Vite dev 端口 + 代理重写
# 来源 FR: FR-6
[automated]

```gherkin
Given vite.config.ts
When 解析 server.port 与 server.proxy
Then server.port == 5174
And server.proxy["/api"].target == "http://127.0.0.1:8766"
And server.proxy["/api"].configure 钩子改写 Origin 为 "http://127.0.0.1:8766"
```

### U5 — frontend ported components

#### Scenario U5.1 — Reader 派发表
# 来源 FR: FR-47, FR-48
[automated]

```gherkin
Given Reader 接收 ?file={path}&view={mode}
When path 匹配 /prompts/shotNN_(kling|seedance).md → 默认 view = "shot-pair"
When path 匹配 /ai_videos/.+/shotlist.md → 默认 view = "shotlist-table"
When path 匹配 /ref_images/.+_seedream.md 或以 .png/.jpg 结尾 → 默认 view = "image-ref"
When path 匹配 /interview/qa.md → 默认 view = "qa"
When path 以 .jsonl 结尾 → 默认 view = "jsonl"
When 其他 → 回落 view = "markdown"
And 若 URL 显式提供 view，则覆盖默认推断
```

#### Scenario U5.2 — Sidebar 三段式 + sub_type 徽章
# 来源 FR: FR-43, FR-44, FR-46
[automated]

```gherkin
Given /api/tree 返回三段
When Sidebar 渲染
Then 三段标题英文 "AI Videos" / "Specs" / "Context" 顺序固定
And ai_videos/wukong_juexing (sub_type="novel") 节点带文本 "剧" 徽章
And 另一 ai_videos/short_demo (sub_type="short") 节点带文本 "短" 徽章
And ai_videos/no_qa (sub_type=null) 节点不带徽章
And 工具栏含 "Refresh" 按钮，无 fs-watcher 周期性请求（用 network log 断言：除手动点击外 30 s 内无 GET /api/tree）
```

#### Scenario U5.3 — 跨树 "查看规格" 链接
# 来源 FR: FR-45, FR-78
[automated]

```gherkin
Given Reader 当前 ?file=ai_videos/wukong_juexing/characters/main.md
Then Reader 顶部工具栏出现 "查看规格" 链接
And 链接 href 含 "?file=specs/ai_video/wukong_juexing/"

Given Reader 当前 ?file=specs/ai_video/wukong_juexing/findings/dossier.md
Then 不出现反向 "查看产物" 链接（v1 暂未实现）
```

#### Scenario U5.4 — Editor 409 提示 + image 视图隐藏
# 来源 FR: FR-76, FR-77, FR-64
[automated]

```gherkin
Given Reader view=markdown，文件已被外部改动（mtime 跳动）
When 用户点 Edit → 修改 → Save
Then 后端返回 409，前端弹 toast "file changed externally — Reload?"
And 不覆盖磁盘内容

Given Reader view=image-ref，目标 path 以 .png 结尾
Then DOM 中不渲染 Edit 按钮
```

#### Scenario U5.5 — RegeneratePanel scope 闸门 + AUTONOMOUS 持久化
# 来源 FR: FR-70, FR-71, FR-72, FR-73, FR-74, FR-75
[automated]

```gherkin
Given RegeneratePanel 渲染于一个 sub_type="short" 的项目
When stage=execution
Then scope 选择器隐藏，提交 body.scope == "project"

Given 同一 panel 渲染于 sub_type="novel" 的项目
When stage=execution
Then scope 三选一可见: project / episode N / episodes M..N
And episode 输入要求 ≥ 1
And episodes 输入要求 1 ≤ M ≤ N (M>N → 表单不可提交)

Given mode toggle 拨到 AUTONOMOUS
When 刷新页面
Then localStorage["ai_video_management.autonomous_mode.v1"] == "true"
And 不污染 spec_driven 的同名 key

Given 点 "Generate"
Then 响应渲染于 dark <pre> (CSS class 包含 "dark-pre")，配 "Copy" 按钮
And 点 Copy 触发 navigator.clipboard.writeText(prompt) 且 aria-live 区域出现 "已复制"
```

### U6 — frontend new ai_video views

#### Scenario U6.1 — ShotPairView 双面板 + 配对算法
# 来源 FR: FR-50, FR-51, FR-53, FR-54
[automated]

```gherkin
Given 用户点击 ai_videos/wukong/episodes/ep01/prompts/shot03_kling.md
When Reader 派发 view=shot-pair
Then 两个 react-resizable-panels 面板并排，autoSaveId="shot-pair-split"
And 左面板渲染 shot03_kling.md，右面板渲染 shot03_seedance.md（同 MarkdownView）
And 每个面板有按钮 "复制 Kling prompt" / "复制 Seedance prompt"
And 点击复制后 aria-live="polite" 区域出现 "已复制"

Given shotPairing.ts 输入 path="ai_videos/x/episodes/ep02/prompts/shot07_seedance.md"
Then partner = "ai_videos/x/episodes/ep02/prompts/shot07_kling.md"
```

#### Scenario U6.2 — ShotPairView 缺失 partner 退化
# 来源 FR: FR-52
[automated]

```gherkin
Given shot05_kling.md 存在但 shot05_seedance.md 缺失
When Reader 渲染 shot-pair
Then 左面板渲染 shot05_kling.md
And 黄色横幅显示 "缺少配对文件: ai_videos/.../shot05_seedance.md"
And 横幅含一个链接，点击进入 BrokenLink 视图（不再尝试在右面板渲染空白）
```

#### Scenario U6.3 — ShotlistTableView 行点击跳转
# 来源 FR: FR-55, FR-56, FR-57, FR-58
[automated]

```gherkin
Given ai_videos/wukong/episodes/ep01/shotlist.md 第一列含 "shot01" / "shot02" / ... 的 cell
When Reader 派发 view=shotlist-table
Then 第一列每个匹配 ^shot\d+$ 的 cell 渲染为 <button>
And 点击 shot03 触发 navigate("?file=ai_videos/wukong/episodes/ep01/prompts/shot03_kling.md&view=shot-pair")
And 其它列保持纯文本，标题/段落正常 markdown 渲染
```

#### Scenario U6.4 — ImageRefView 三态 (有图 / 无图 fallback / 直开图)
# 来源 FR: FR-59, FR-60, FR-61, FR-62, FR-63
[automated]

```gherkin
Given ref_images/main_seedream.md 与同目录 main_seedream.png 都存在
When Reader 渲染 image-ref
Then 左面板渲染 markdown，右面板 <img src="/api/file?path=...main_seedream.png&mtime=..." alt="main_seedream立绘" />
And autoSaveId="image-ref-split"

Given 仅 main_seedream.md 存在，main_seedream.png 缺失
Then 右面板显示 "尚未生成立绘 — 复制左侧 prompt 至 Seedream 后保存为 main_seedream.png 并刷新"
And 不渲染 "Refresh" 按钮

Given 用户直接点 main_seedream.png（树中 image 叶子）
Then Reader 派发 image-ref，左面板留空，右面板渲染图片

Given 同目录同时存在 main_seedream.png 与 main_seedream.jpg
Then 优先使用 .png
```

#### Scenario U6.5 — Locked-block 药丸渲染
# 来源 FR: FR-65, FR-66
[automated]

```gherkin
Given markdown 源含 "【主角 · 雪夜战场 · 锁定描述符 v3】身披黑色斗篷……禁用 红色与金色。"
When MarkdownView 渲染
Then 该块外层有 <span class="locked-block" data-version="v3">
And CSS ::before 在右上角呈 "锁定块" 药丸（背景 #f3f4f6，monospace，cursor:help）
And 药丸 tooltip 文本 "byte-equality contract — see characters/main.md"
```

#### Scenario U6.6 — Parser 真实素材 + Error Boundary
# 来源 FR: FR-49；development.md 移动 #9, #10
[automated]

```gherkin
Given shotlistParser 与 shotPairing 的 Vitest 用例
When 输入是 ai_videos/wukong_juexing/episodes/ep01/shotlist.md 的真实磁盘内容
Then 解析结果含至少 1 个 shot id（非空数组），且与正则 ^shot\d+$ 匹配的列号为 0

Given Reader 任何 parse-on-render 子组件 (ShotPairView, ShotlistTableView, ImageRefView, QaView, JsonlView)
When 强制使其 throw（注入畸形 markdown）
Then 顶层 ParseFallback 真实 React Error Boundary class 捕获并展示 fallback UI
And 代码库中不存在 "try { return <X /> } catch" 形态（grep 检查）
```

### U7 — Makefile + README + e2e

#### Scenario U7.1 — Makefile 全部 target 存在 + pip-only
# 来源 FR: FR-81; development.md 移动 #6
[automated]

```gherkin
Given projects/ai_video_management/Makefile
When 解析其 .PHONY 与 target 列表
Then 包含: install, install-backend, install-frontend, run-prod, run-backend, run-frontend, run, test-backend, test-frontend, e2e, boot-smoke, clean
And `run` 是 `run-backend` 的别名
And 文件中不出现 "uv run" / "uv sync" 字面量（若出现，必须紧跟 pip 回退）
```

#### Scenario U7.2 — Playwright e2e 至少覆盖 5 条 (a)–(e)
# 来源 FR: FR-85; development.md 移动 #1, #8
[automated]

```gherkin
Given frontend/e2e/
When 列出 .spec.ts 文件 + 解析 test() 名称
Then 至少覆盖以下五条命名场景:
  (a) browse-to-shot-pair flow
  (b) shotlist-table-row-click navigation
  (c) image-ref view: image present AND image absent (两条 it 子用例)
  (d) regen-prompt scope toggle for short AND novel (两条 it 子用例)
  (e) Origin/Host gate: 8765 直发被拒
And playwright.config.ts 含 ≥ 2 个 project（对应 spec 列出的运行模式 run-prod + run-backend+run-frontend）
And 每个 e2e 场景 assert: <main> 非空 AND mode-specific selector 解析 AND consoleErrors == []
```
*运行模式数量 < e2e profile 数量 = `blocker`（development.md 严重度表）。*

#### Scenario U7.3 — README 与 frontend/backend 配套
# 来源 FR: 项目规则 (CLAUDE.md `## Project rules`)
[automated]

```gherkin
Given projects/ai_video_management/README.md
Then 文件存在且非空
And 含安装 + 运行 + 端口（8766/5174）说明
And 与 spec_driven README 同结构（小节对齐）
```

#### Scenario U7.4 — pinned-item 保全（regen 后 promoted 项原样出现）
# 来源 validation/general.md 原则 8
[automated]

```gherkin
Given specs/ai_video/wukong_juexing/findings/promoted.md 含两条 pinned 块
When 用户运行 "regenerate stage 3" 端到端流程（自动化用 fixture 跑 regen_prompt → 模拟 Claude 写回新 dossier.md）
Then 新 dossier.md 在自然位置原样含两条 pinned 文本（用 _parse_promoted_text 比较，模白空格）
And 若新 dossier 已无对应插入点 → 末尾出现 "## Pinned items (orphaned)" 段落，且包含两条
And 任一条丢失 = critical
```
*Stage 6 regen 不生成此检查（spec FR-32 与 general.md 原则 8 第三条）。*

---

## 手动场景

#### Scenario M.1 — 视觉走查：浅色主题 + 深色 <pre> 飞地
# 来源 FR: FR-79, FR-80
[manual_walkthrough_only]

```gherkin
Given 浏览器 prefers-color-scheme=dark 与 light 各一次
When 在 sidebar / Reader / Editor / RegeneratePanel 切换
Then 应用主体始终浅色（无暗色 chrome 翻转）
And 唯一深色区域为：regen-prompt <pre>、markdown 中 ``` 代码块、CodeView
And 所有深色 <pre> 文本对比度 ≥ WCAG AA (4.5:1)，使用 Lighthouse 取证
```

#### Scenario M.2 — CJK 渲染观感
# 来源 FR: FR-67, FR-68, FR-69
[manual_walkthrough_only]

```gherkin
Given Reader 渲染含中文与英文混排的 spec.md / qa.md / shot prompt
Then 容器 lang="zh-Hans"
And Windows 上中文走 "Microsoft YaHei"，macOS 走 "PingFang SC"（DevTools 检查 computed font-family）
And 中英文交界处不出现误折行 / 字符破损（手工目视）
```

#### Scenario M.3 — 8 个主流程一遍过
# 来源 spec § Primary flows 1–8
[manual_walkthrough_only]

```gherkin
Given `make run-prod` 单进程模式
When 依次执行：
  1. 打开 http://127.0.0.1:8766/，看到 sidebar 三段
  2. 点任一 prompts/shotNN_kling.md → ShotPairView
  3. 点 shotlist.md，再点行内 shot id → 跳到 ShotPairView
  4. 点 ref_images/*_seedream.md → ImageRefView (+复现"无图"和"有图"各一次)
  5. 在 markdown 视图点 Edit → 改 → Save → 刷新看到改动
  6. 在 qa.md 视图 pin 一条 → 检查 promoted.md 文件
  7. 在任一 stage 点 "Generate regen prompt" → 复制 → 粘贴到 Claude Code 验证可执行
  8. 在 ai_videos/{name}/ 文件视图点 "查看规格" → 跳到 specs/ai_video/{name}/
Then 全部 8 步均无 console error 与 a11y warning
And 在 `make run-backend` + `make run-frontend` 双进程模式下重复一遍，行为一致（development.md 移动 #1 多模式平价）
```

#### Scenario M.4 — 立绘 .png 出现后刷新即可见
# 来源 FR: FR-26, FR-62
[manual_walkthrough_only]

```gherkin
Given ImageRefView 显示 "尚未生成立绘 …" fallback
When 用户在 Seedream 生成图片，按提示文件名保存到 ref_images/
And 在 sidebar 点 Refresh
Then 重新点 ref_images/main_seedream.md，右面板渲染图片
And URL 含 ?mtime=... 与新 mtime 一致（DevTools Network 看到 Cache-Control: private, max-age=0）
```

#### Scenario M.5 — RegeneratePanel 模式语义可用性
# 来源 FR: FR-72, FR-73, FR-74
[manual_walkthrough_only]

```gherkin
Given 用户在 novel 项目尝试每种 scope 组合
Then 表单错误信息（episode<1, M>N, 缺 sub_type）的中文文案明确、可定位
And AUTONOMOUS 切换 toggle 视觉对比明显（不会与 INTERACTIVE 混淆）
And dark <pre> 中 prompt 全文可一键复制成功，剪贴板内容字节级与 byte_size 字段相等
```

#### Scenario M.6 — 跨平台：Windows + macOS/Linux 各跑一遍
# 来源 NFR-7；development.md 移动 #5
[manual_walkthrough_only]

```gherkin
Given 同一仓库
When 在 Windows 11 + Git Bash 与 macOS / Linux 上分别执行 `make boot-smoke && make e2e`
Then 全部测试通过（POSIX-only 用 pytest.mark.skipif 跳过而非失败）
And 路径处理在 Windows 上无 \ / 混合错位（ImageRefView 与 ShotPairView 路径 join 视觉验证）
```

---

## 覆盖矩阵

每条 FR / NFR → 至少一个场景。`*` 表示该 FR 由多个场景共同覆盖。

| FR | 场景 |
|---|---|
| FR-1 | U1.1 |
| FR-2 | U3.1 |
| FR-3 | U3.1 |
| FR-4 | U3.1 |
| FR-5 | M.3, U7.1 |
| FR-6 | U3.3, U4.2 |
| FR-7 | U1.2 |
| FR-8 | U1.2 |
| FR-9 | U3.8 |
| FR-9b | U3.12 (rename-media，follow-up 007) |
| FR-9c | U3.13 (archive-media，follow-up 008) |
| FR-9d | U3.13 (unarchive-media，follow-up 008) |
| FR-9e | U3.14 (import-from-downloads，follow-up 009) |
| FR-9f | U3.15 (actors/generate，follow-up 014) |
| FR-9g | U3.16 (casting/assign，follow-up 014) |
| FR-9h | U3.16 (casting/assign DELETE，follow-up 014) |
| FR-10 | U3.8 |
| FR-10b | U3.16 (GET /api/actors，follow-up 014) |
| FR-10c | U3.16 (GET /api/casting，follow-up 014) |
| FR-86 | U3.15 (attribute schema enums，follow-up 014) |
| FR-11 | U3.2, U3.3* |
| FR-12 | U3.4 |
| FR-13 | U3.5 |
| FR-14 | U3.6 |
| FR-15 | U3.6, U5.4 |
| FR-16 | U3.7 |
| FR-17 | U3.7 |
| FR-18 | U2.1 |
| FR-19 | U2.1, U2.2 |
| FR-20 | U2.1 |
| FR-21 | U5.2, M.4 |
| FR-22 | U1.3 |
| FR-23 | U1.3 |
| FR-24 | U1.3, U5.2, U5.5 |
| FR-25 | U2.2, U3.5, U3.7, U5.4 |
| FR-26 | M.4, U6.4 |
| FR-27 | U3.6 |
| FR-28 | U3.2, U3.5, U3.6 |
| FR-29 | U3.6 |
| FR-30 | U3.9 |
| FR-31 | U3.9 |
| FR-32 | U3.9, U7.4 |
| FR-33 | U1.4 |
| FR-34 | U3.10 |
| FR-35 | U3.10 |
| FR-36 | U3.10 |
| FR-37 | U2.3 |
| FR-38 | U2.4 |
| FR-39 | U2.4 |
| FR-40 | U4.1 |
| FR-41 | U4.1 |
| FR-42 | U4.1 |
| FR-43 | U2.1, U5.2 |
| FR-44 | U5.2 |
| FR-45 | U5.3 |
| FR-46 | U5.2 |
| FR-47 | U5.1 |
| FR-48 | U5.1 |
| FR-49 | U6.6 |
| FR-50 | U6.1 |
| FR-51 | U6.1 |
| FR-52 | U6.2 |
| FR-53 | U6.1 |
| FR-54 | U6.1 |
| FR-55 | U6.3 |
| FR-56 | U6.3 |
| FR-57 | U6.3 |
| FR-58 | U6.3 |
| FR-59 | U6.4 |
| FR-60 | U6.4 |
| FR-61 | U6.4 |
| FR-62 | U6.4, M.4 |
| FR-63 | U6.4 |
| FR-64 | U5.4 |
| FR-65 | U6.5 |
| FR-66 | U6.5 |
| FR-67 | M.2 |
| FR-68 | M.2 |
| FR-69 | M.2 |
| FR-70 | U5.5 |
| FR-71 | U5.5 |
| FR-72 | U5.5, M.5 |
| FR-73 | U5.5, M.5 |
| FR-74 | U5.5, M.1, M.5 |
| FR-75 | U5.5 |
| FR-76 | U5.4 |
| FR-77 | U5.4 |
| FR-78 | U5.3 |
| FR-79 | M.1 |
| FR-80 | M.1 |
| FR-81 | U7.1 |
| FR-82 | U1.1, U1.2, U1.3, U1.4, U2.1, U2.3, U2.4, U3.* |
| FR-83 | U3.11 |
| FR-84 | U6.6 |
| FR-85 | U7.2 |
| NFR-1 | U4.1, U7.1 |
| NFR-2 | U2.1 (含 200 ms 预算断言), U6.1 (300 ms 预算) |
| NFR-3 | U5.5 (localStorage namespace), U3.2 (8765 拒) |
| NFR-4 | U7.2 (≥2 Playwright project), M.3 |
| NFR-5 | U3.8 (无额外路由) |
| NFR-6 | U5.2 (英文 chrome), M.2 (中文内容) |
| NFR-7 | M.6 |

补遗：

- **promoted.md 保全**（general.md 原则 8）→ U7.4。
- **header-mutating-layer 双形态**（development.md 移动 #11）→ U3.3。
- **error boundary + 真实素材 parser**（development.md 移动 #9, #10）→ U6.6。
- **boot smoke**（development.md 移动 #4）→ U3.11。
- **多模式 e2e**（development.md 移动 #1, #8）→ U7.2 + M.3。
- **manual walkthrough**（general.md 原则 4 / development.md 移动 #7）→ M.1–M.6。
- **uv 禁用**（development.md 移动 #6）→ U7.1。

任何未在矩阵中出现的 FR 编号 = 文档缺陷，按 `validation/general.md` 原则 6 在 stage-5 sign-off 标记 `critical`。
