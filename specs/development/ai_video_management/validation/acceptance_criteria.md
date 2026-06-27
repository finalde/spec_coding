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

#### Scenario U2.5 — dev reload 强制退出兜底（follow-up 042）
# 来源 FR: FR-2
[manual]

```gherkin
Given backend 启动于 reload 模式（`python main.py`，未传 --no-reload）
And libs/uvicorn_force_exit.py 存在，`install()` 在 libs/asgi.py 与 main.py 各调用一次
And uvicorn.Server._force_exit_installed === True（patch 已生效，可在 reload 子进程 REPL 验证）

When 触发一个长时阻塞 sync endpoint（e.g. POST /api/extract-frames 对一段 mp4 启动 ffmpeg，~5s）
And 在该请求未返回之前，编辑 libs/tree_walker.py 任一字节
Then WatchFiles 打印 "WatchFiles detected changes in 'libs\\tree_walker.py'. Reloading..."
And uvicorn 打印 "Shutting down" + "Waiting for connections to close. (CTRL+C to force quit)"
And 在 ≤ 4 秒内子进程 PID 消失（os._exit(0) 触发，跳过 ffmpeg 等待）
And WatchFiles 自动启动新子进程（uvicorn 的 reload 监督逻辑不被 patch 改变）
And 新 PID 在 ≤ 6 秒内开始响应 /api/tree
And 终端不再卡 "Waiting for connections to close (CTRL+C to force quit)" 行

When 用户连按 2 次 CTRL+C 终止 reload 模式
Then uvicorn 的 handle_exit 第二次调用复用同一 watchdog（idempotent — 不重复 schedule timer 也不崩）
And 进程在 (timeout_graceful_shutdown + 2) 秒内死掉

When backend 启动于 --no-reload 模式
And user 发 SIGTERM（或 CTRL+C）
Then 同样 ≤ 4 秒进程死掉；逻辑与 reload 子进程对称
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
And response.unmatched 含 1 项：random_unrelated.mp4 (kind=unmatched，仅含 from、无 to——未匹配文件不导入)
And response.errors[] 不含 old_stuff.mp4 / trailer_doc.pdf / a_symlink.mp4（这些被 window/ext/symlink 静默跳过，不计入 errors）
And response.rename = {renamed:[...重命名前 3 个...], skipped:[], errors:[]}
And 磁盘上 random_unrelated.mp4 仍原地留在 Downloads（未被导入、未创建 ai_videos/{tmp_drama}/not_matched/）
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

#### Scenario U3.15 — `POST /api/actors/generate` 批量生成 + Kling 出站 HTTP（follow-up 014 + 025 Kling-only + 027 concurrency + variance + 029 rich variance + resolution）
# 来源 FR: FR-9f, FR-86
[automated]

```gherkin
Given 空目录 ai_videos/_actors/ 不存在
And `KLING_ACCESS_KEY` + `KLING_SECRET_KEY` env 已设（fixture 注入，模拟 backend/.env 已加载）
And ActorPool 的 httpx 客户端被 monkey-patch 为返回固定 12-byte JPEG payload（模拟 Kling submit→poll→download 成功）
When POST /api/actors/generate with body {count: 3, ethnicity: "asian", gender: "male", age_range: "18-25", look: "handsome", style: "modern-casual", notes: "test"}
Then 响应 200
And response.generated 长度 = 3
And response.generated[0].id = "actor_0001"，[1].id = "actor_0002"，[2].id = "actor_0003"
And 磁盘上 ai_videos/_actors/actor_0001/actor_0001.jpg 存在 + actor_0001.md 存在
And actor_0001.md 含属性表（ethnicity / gender / age_range / look / style / notes）+ 组装的英文 prompt + seed
And 三张 sidecar 中记录的 prompt 互不相同（per-image variance phrase 注入；follow-up 027）
And 每张 sidecar 的 prompt 至少含一个 _VARIANCE_FACE_FEATURES / _VARIANCE_SKIN_TONES / _VARIANCE_FACE_SHAPES / _VARIANCE_EYE_DESCRIPTORS / _VARIANCE_HAIR_DESCRIPTORS 元素
When 第二次 POST /api/actors/generate 同一参数 count=2
Then 响应 200 + generated[0].id = "actor_0004"，[1].id = "actor_0005"（ID 单调自增，不复用）
When POST body 中 ethnicity = "klingon"（不在 enum） → 400 invalid_attribute
When POST body 中 count = 0 或 count = 51 → 400 invalid_attribute（cap follow-up 027 升到 50；51 越界）
When ActorPool 客户端 monkey-patch 为模拟 timeout → 那 1 张归 errors[]，其它 (count - 1) 张正常生成；状态 200
When 非 POST → 405
And 9 并发 POST /api/actors/generate count=1 在同一空 `_actors/` 上 → 全部 200 + 9 个 distinct `actor_NNNN` id（race-safe allocator，follow-up 027；`mkdir(exist_ok=False)` 原子）
And 每张 sidecar 中的 prompt 长度 ≥ 1000 字符（follow-up 029 expanded variance）
And sidecar prompt 不含 "photorealistic" / "sharp focus" / "8k" 单独 token（follow-up 031 移除）
And sidecar prompt 含 "candid" / "natural skin texture" / "no waxy smoothness" / "RAW unedited" 等 anti-wax keywords（follow-up 031 永久注入）
And sidecar prompt 含至少一项 `_VARIANCE_PHOTOREALISM` camera/film cue（follow-up 031 第 18 池）
When POST body resolution = "2k"
Then 保存的 jpg 文件解码后 size = (2048, 2048)（Pillow LANCZOS upscale；follow-up 029）
And response.generated[i].resolution = "2k"
When POST body resolution = "4k" → size = (4096, 4096)
When POST body resolution = "normal"（default）→ jpg 尺寸为 Kling 原始输出（kling-v1 1:1 通常 1024×1024）
When POST body resolution = "8k"（不在 enum）→ 400 invalid_attribute
When POST /api/actors/preview-prompts with body {count: 3, attrs}（follow-up 032）→ 200 + response.prompts 长度 = 3，每项含 {seed, prompt}
And response.prompts[i].prompt 即将发给 Kling 的 final prompt（含 variance + anti-wax + camera cue）
When POST /api/actors/generate with body {count: 3, attrs, seeds: [s0, s1, s2]}（用 preview 返的 seeds）
Then 生成的 sidecar prompts 与 preview.prompts[i].prompt 一一字节相等
When POST /api/actors/generate body seeds 长度 != count → 400 invalid_attribute
When POST /api/actors/generate body seeds 含非 int → 400 invalid_attribute
When 非 POST 到 /api/actors/preview-prompts → 405
And ActorGrid PAGE_SIZE = 50（follow-up 032）；25 actors 时不分页（25 ≤ 50）；51 actors 时分 2 页
And 生成的 jpg 文件名匹配 `{ethnicity}__{gender}__{age_range}.jpg`（follow-up 033）
And sidecar 文件名仍为 `actor_NNNN.md`（不变）
When 启动时存在 legacy `actor_NNNN.jpg` 文件 + sidecar → `ActorPool.__init__` 自动调 `migrate_filenames` 重命名到新格式；二次启动 noop（idempotent）
And ActorGrid 加民族/性别/年龄段三个 filter dropdown，默认 "全部"；filter 变化时 page 重置 0；header 显示 `filtered / total`
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

#### Scenario U3.17 — `POST /api/actors/delete` 软删除 + cascade unassign（follow-up 026）
# 来源 FR: FR-9i, FR-87
[automated]

```gherkin
Given pool 内已生成 actor_0001 + actor_0002（fixture）
And ai_videos/dramaA/casting.md 含 (c1_主角, actor_0001) + (c2_配角, actor_0002)
And ai_videos/dramaB/casting.md 含 (c1_师傅, actor_0001)
And ai_videos/_deleted/ 不存在
When POST /api/actors/delete with body {actor_id: "actor_0001"}
Then 响应 200 + from = "ai_videos/_actors/actor_0001" + to = "ai_videos/_deleted/_actors/actor_0001"
And response.unassigned 含 2 项 [{drama: "dramaA", role: "c1_主角"}, {drama: "dramaB", role: "c1_师傅"}]
And 磁盘上 ai_videos/_actors/actor_0001/ 不再存在
And ai_videos/_deleted/_actors/actor_0001/actor_0001.jpg + .md 存在（folder 整体被搬迁）
And dramaA/casting.md 仅剩 (c2_配角, actor_0002) — actor_0001 引用已清除
And dramaB/casting.md 剩 empty table（仅 header） — 唯一 row 已清除
When 再次 POST /api/actors/delete with body {actor_id: "actor_0001"} → 响应 404 actor_not_found（folder 已搬走）
When POST body 中 actor_id = "actor_xx" → 响应 400 invalid_actor_id（shape mismatch）
When POST body 中 actor_id = "actor_9999"（不存在）→ 响应 404 actor_not_found
When 非 POST 到 /api/actors/delete → 405
When 下一次 POST /api/actors/generate count=1 → 新 actor 分配 ID "actor_0001"（_deleted/_actors/ 不参与 _next_actor_id_num 扫描，slot 可复用）
```

#### Scenario U3.18 — `/actors` grid view + pagination（follow-up 028）
# 来源 FR: FR-91, FR-87, FR-10b
[automated]

```gherkin
Given pool 为空（ai_videos/_actors/ 无 actor_NNNN folders）
When 用户在 sidebar `_actors/` 行点击 "🔲 网格" 按钮
Then 浏览器跳到 `/actors`
And ActorGrid 渲染 empty state 文案 "演员池为空 — ..."
And 无分页控件
When pool 有 5 个 actor（fixture 注入 actor_0001..actor_0005）
And 用户进入 `/actors`
Then header 显示 "🎭 演员池 (5)"
And grid 渲染 5 个 tile，按 id 升序 actor_0001 在最前
And 每个 tile 含 img (src 含 `/api/media?path=...&mtime=...`) + actor id + 4 个 chip (ethnicity / gender / age_range / look)
And 无分页控件（5 ≤ PAGE_SIZE=12）
When 用户点击 tile actor_0003
Then 浏览器跳到 `/file/{image_path}`（encodeURIComponent），Reader 渲染单图详情
When pool 有 13 个 actor
Then header "🎭 演员池 (13)"
And 第 1 页渲染 12 个 tile (actor_0001..actor_0012)
And 分页控件显示 "第 1 / 2 页"，"上一页" / "首页" 按钮 disabled，"下一页" / "末页" enabled
When 用户点 "下一页"
Then 第 2 页渲染 1 个 tile (actor_0013)
And "下一页" / "末页" 按钮 disabled，"上一页" / "首页" enabled
When 用户点 "首页"
Then 回到第 1 页
When pool 有 25 个 actor → 总页数 ceil(25/12) = 3
When `/api/actors` 返 500 / network error → 页面渲染 error banner + 重试按钮；点重试触发再次 fetch
And 进入 select mode（点 "✅ 选择" 按钮）
Then tile click 不再 navigate，而是 toggle selectedIds 成员资格；tile 显示 checkmark overlay + 蓝边
And footer bar sticky 出现，显示 "已选 N / 总 M" + 全选 / 全清 / 🗑 批量删除 (N) / 🎬 分配角色 (N) 按钮
When 用户跨页选择（page 1 选 2 个，去 page 2 再选 1 个，回 page 1）
Then page 1 tile 仍保留 selected 状态（selection 跨页）
When 用户点 "🗑 批量删除 (3)" → window.confirm 后，前端 loop POST /api/actors/delete × 3
Then 每张 cascade unassign + 移到 _deleted/_actors/；toast 显示 "批量删除完成：3 个 actor，清理 N 个 casting 引用"；grid 重新加载，已选 actor 消失
When 用户在 select mode 点 "🎬 分配角色 (N)"
Then 模态打开，drama dropdown 列 `ai_videos/` 下所有 non-`_` 子目录（fixture：dramaA / dramaB）
And character dropdown 列 selected drama 的 `characters/c*/` 子目录名（fixture：dramaA 有 c1_主角 / c2_配角）
When 用户选 dramaA → c1_主角 → 确认
Then loop POST /api/casting/assign × N（每个 actor 一次），写入 ai_videos/dramaA/casting.md；toast "已分配 N 个 actor 到 dramaA / c1_主角"
When 同一 actor 被分到 dramaA/c1 后再分到 dramaB/c2 → 两个 casting.md 都含该 actor_id（多剧参演原生支持，无新 data store）
```

#### Scenario U3.19 — actor sidecar md 走 `ActorView`（follow-up 034）
# 来源 FR: FR-92
[automated]

```gherkin
Given pool 内存在 actor_0013，folder 内含 actor_0013.md + asian__male__18-25.jpg
When 用户导航到 `/file/ai_videos/_actors/actor_0013/actor_0013.md`
Then Reader dispatch 命中 isActor 分支，渲染 <ActorView/>
And 不渲染 <SiblingMedia/>（页面底部 NO "Select all" / "Clear" / "Archive Selected" toolbar、NO 每 tile checkbox）
And ActorView header 显示 "actor_0013"
And ActorView 显示大幅 face 图，src 含 `/api/media?path=ai_videos/_actors/actor_0013/asian__male__18-25.jpg`
And ActorView 元数据块以 <dl> 形式列出 ethnicity / gender / age_range / look / style / notes / seed 七行
And "生成 prompt" 卡片渲染 sidecar 第一段 fenced code block 的纯文本（<pre> 样式 + monospace 字体）
And 卡片右上有 "📋 Copy" 按钮
When 用户点击 "📋 Copy"
Then 浏览器 clipboard 写入 prompt 字符串，按钮文字 1.5s 内显示 "✓ Copied"
When 用户在 Reader 顶部 toolbar 点 "✎ Edit"
Then ActorView 收起，Editor 渲染 actor_0013.md 原始 markdown（power-user 编辑路径仍存在）
When sidecar md 不含 fenced code block（无 prompt 段）
Then ActorView 不渲染 "生成 prompt" 卡片，仅显示 image + 元数据
When actor folder 无 jpg / png / webp 图片
Then ActorView image pane 显示 fallback 文案 "尚未生成 face 图片"，其他面板正常渲染
```

#### Scenario U3.21 — actor folder 在 sidebar 折叠成单 leaf + ActorView 内 delete（follow-up 036）
# 来源 FR: FR-93
[automated]

```gherkin
Given pool 内存在 actor_0013，folder 内含 actor_0013.md + asian__male__18-25.jpg
When 调用 GET /api/tree
Then ai_videos/_actors/ 节点的 children 中存在 type="actor", name="actor_0013", path="ai_videos/_actors/actor_0013/actor_0013.md" 的节点
And 该节点的 children 为空 / 不存在
And 该节点的 face_path 等于 "ai_videos/_actors/actor_0013/asian__male__18-25.jpg"（或 actor 内部首个匹配 _IMAGE_EXTENSIONS 的相对路径；actor 无图片时 face_path 为 null）
And /api/tree 返回中不含 path="ai_videos/_actors/actor_0013/actor_0013.md" 之外的任何 actor_0013 子文件节点（即 jpg / md 不再作为独立 tree row）
And linkResolver.collectFilePaths(tree) 的输出同时包含 actor_0013 的 md path 与 face_path（face_path 非 null 时）

Given Sidebar 已渲染 actor_0013 leaf 行
Then 行内显示 🎭 图标 + "actor_0013" label + 右侧 "🗑" 按钮
And 行不渲染展开三角（disclosure triangle）
When 用户点击行 body（非 🗑 按钮区域）
Then URL 变为 /file/ai_videos/_actors/actor_0013/actor_0013.md
And Reader 命中 isActor 分支，渲染 <ActorView/>

Given ActorView 已渲染
Then header 同时显示 "actor_0013" title 与 "🗑 删除" 按钮
When 用户点击 "🗑 删除"
Then window.confirm 弹窗（文案含 actor_0013 + "_deleted/_actors/" + casting unassign 提示）
When 用户确认
Then 前端发起 POST /api/actors/delete body {actor_id: "actor_0013"}
And 200 成功后导航到 "/"（或 sidebar 重新渲染且 actor_0013 leaf 行消失）
And onSaved 回调被触发以触发 tree refresh

Given /api/actors/delete 返回 4xx / 5xx
Then ActorView 内显示红色 inline alert 包含 detail.kind 或 error.message
And 不发生导航

Given pool 内含 _deleted/_actors/actor_0099/ （已软删除）
When 调用 GET /api/tree
Then _deleted/_actors/actor_0099/ 仍按递归 directory 渲染（含 jpg + md 子节点）— 折叠规则不适用于 _deleted 子树
```

#### Scenario U3.22 — DeletedView bulk hard-delete with typed-DELETE confirm（follow-up 038）
# 来源 FR: FR-94
[automated]

```gherkin
Given ai_videos/_deleted/ 下存在 mozun/shot01.mp4 + dramaA/c1/photo.jpg + _actors/actor_0099/asian__male__18-25.jpg（fixture）
And sidebar 渲染 ai_videos/_deleted/ 节点
Then 该节点行渲染 "🧹 永久清理" 按钮（className="drama-rename-btn"）
And button 点击 e.stopPropagation() 且不触发 tree row 展开
When 用户点击 "🧹 永久清理"
Then 浏览器路由 navigate 到 "/deleted"
And DeletedView 渲染 header "🗑 回收站 (3 个文件)"
And grid 渲染 3 个 tile，按 path 升序：_actors/actor_0099/asian__male__18-25.jpg → dramaA/c1/photo.jpg → mozun/shot01.mp4
And 每个 tile 渲染 <img> (image) 或 <video preload="metadata" muted> (video) + filename + 子路径（去 "ai_videos/_deleted/" 前缀）

When DeletedView 默认（非 select mode）下用户点 mozun/shot01.mp4 tile
Then navigate 到 `/file/ai_videos/_deleted/mozun/shot01.mp4`
When 用户点 header "✅ 选择" 按钮
Then DeletedView 进入 select mode，"✅ 选择" 文字替换为 "✕ 退出选择"
When select mode 下点 photo.jpg tile
Then tile 加 .deleted-tile-selected 蓝边、checkbox 显示 ✓；不再导航
When 跨页选择（pool 内 60+ tile 时 page 1 选 2 + page 2 选 1 + 回 page 1）
Then page 1 已选 tile 仍显示 selected（selectedPaths Set 跨页持久）

When 用户在 select mode 点 "🗑 永久删除 (1)"
Then 模态打开，标题 "永久删除 1 个文件？"
And red banner role="alert"：包含 "此操作不可撤销" 与 "没有 in-app restore"
And <ul> 列出第一条 path 全字符串（"ai_videos/_deleted/dramaA/c1/photo.jpg"）
And 超过 10 个时 ul 末尾追加 "+ N 个其他文件…" muted item
And input <input> 占位 "DELETE"，主按钮 "永久删除 1 个文件" disabled
When 用户输入 "del"
Then 主按钮仍 disabled（不 case-insensitive）
When 用户输入 "DELETE"
Then 主按钮 enabled
When 用户点主按钮
Then 前端 loop 调用 POST /api/hard-delete-media body {path: "ai_videos/_deleted/dramaA/c1/photo.jpg"}
And 后端 200 响应 {deleted: "ai_videos/_deleted/dramaA/c1/photo.jpg"}
And 磁盘上 photo.jpg 不再存在；其父 c1/ 文件夹仍存在（无 rmdir）
And toast 显示 "已永久删除 1 个文件"
And 模态关闭，select mode 退出，onChange 触发 tree 重新拉取
And DeletedView 重新渲染时 photo.jpg tile 消失

When POST /api/hard-delete-media body {path: "ai_videos/_actors/actor_0001/asian__male__18-25.jpg"}（路径不在 _deleted/ 下）
Then 后端 400 not_in_deleted
When POST body {path: "ai_videos/_deleted/dramaA/notes.md"}（非 media 扩展）
Then 后端 400 extension_not_allowed
When POST body {path: "ai_videos/_deleted/missing.mp4"}（文件不存在）
Then 后端 404 not_found
When POST body {path: "/etc/passwd"} 或 "../../etc/passwd"
Then 后端 400 invalid_path（_validate_media_source 内 sandbox 校验）
When 非 POST 方法到 /api/hard-delete-media → 405 method_not_allowed

When 用户批量选择 3 个文件，1 个被外部进程已删，确认 typed DELETE 主按钮
Then 前端 loop 3 次 hardDeleteMedia；2 个 200 + 1 个 404
And toast 显示 "永久删除：成功 2 / 失败 1（详见 console）"
And 不 abort batch；模态正常关闭

When ai_videos/_deleted/ 不存在 / 内无 media 文件
When 用户从 sidebar 点 "🧹 永久清理"
Then DeletedView empty state 渲染 "回收站为空 — 软删除的文件（来自 mp4 / 图片 Reader 的 🗑 Delete 按钮）会出现在此处"
```

#### Scenario U3.23 — ActorView assignments + assign / unassign + delete refusal（follow-up 043）
# 来源 FR: FR-9g, FR-9h, FR-9i, FR-9s, FR-95
[automated]

```gherkin
Given pool 内存在 actor_0013，drama mozun_chongsheng 下 characters/c1_沧冥/ 是 directory
And casting.md 不存在 / 不含 actor_0013 的任何 row

When GET /api/actors/assignments?actor_id=actor_0013
Then 200 + {actor_id:"actor_0013", assignments: []}

Given ActorView 加载 actor_0013 页面
Then "🎬 角色分配 (0)" 区块渲染，文案 "尚未分配到任何角色" 与 "＋ 添加分配" 按钮
And header 的 "🗑 删除" 按钮 enabled

When 用户点击 "＋ 添加分配" → 表单展开
Then 第一个 dropdown 选项 = tree 内 ai_videos/ 直接非 `_` 前缀子目录（drama 列表）
And 第二个 dropdown 选项 = 当前 drama 的 characters/c*/ 子目录名（regex ^c\d+(_.*)?$）
When 用户选 drama=mozun_chongsheng, role=c1_沧冥, notes="主角 v1"
And 点击 "确认分配"
Then 前端 POST /api/casting/assign body {path:"ai_videos/mozun_chongsheng", role:"c1_沧冥", actor_id:"actor_0013", notes:"主角 v1"}
And 后端 200 + casting.md 含一行 c1_沧冥 | actor_0013 | 主角 v1
And 后端同步写 ai_videos/mozun_chongsheng/characters/c1_沧冥/_cast.md，内容含 actor_0013 + face filename + 中文 metadata table + `[查看演员档案]` 链接
And ActorView 重新拉 assignments → "🎬 角色分配 (1)" 区块渲染一行 `mozun_chongsheng / c1_沧冥` + notes "— 主角 v1" + "✕ 取消" 按钮

Given actor_0013 已分配到 c1_沧冥
When ActorView header "🗑 删除" 按钮状态
Then disabled = true
And tooltip = "actor 当前已分配到 1 个角色，无法删除（请先取消所有分配）"

When 用户在 sidebar 行点 🗑 / 或 ActorView 点 disabled-bypass POST /api/actors/delete body {actor_id:"actor_0013"}
Then 后端 409 + {detail:{kind:"actor_is_assigned", assignments:[{drama:"mozun_chongsheng", role:"c1_沧冥", notes:"主角 v1", character_folder:"ai_videos/mozun_chongsheng/characters/c1_沧冥", character_folder_exists: true}]}}
And ai_videos/_actors/actor_0013/ 文件夹未被移动到 _deleted/_actors/

When POST /api/archive-media body {path: "ai_videos/_actors/actor_0013/asian__male__18-25.jpg"}
Then 后端 409 + {detail:{kind:"actor_is_assigned", actor_id:"actor_0013", assignments:[...]}}
And jpg 未被移到 archive/

When POST /api/delete-media body {path: "ai_videos/_actors/actor_0013/asian__male__18-25.jpg"}
Then 后端 409 + 同上 kind
And jpg 未被移到 _deleted/

When 用户点 assignments 列表行的 "✕ 取消"
Then 前端 DELETE /api/casting/assign body {path:"ai_videos/mozun_chongsheng", role:"c1_沧冥"}
And 后端 200 + casting.md 该 row 移除（剩 header + 空 table）
And 后端同步删 ai_videos/mozun_chongsheng/characters/c1_沧冥/_cast.md（unlink(missing_ok=True)）
And ActorView 重新拉 assignments → 区块回到 "🎬 角色分配 (0)" 状态
And "🗑 删除" 按钮 enabled

When 用户随后点 "🗑 删除"，window.confirm 通过
Then POST /api/actors/delete body {actor_id:"actor_0013"} → 200 + {from:"ai_videos/_actors/actor_0013", to:"ai_videos/_deleted/_actors/actor_0013", unassigned: []}
And folder 已移到 _deleted/

Given character folder ai_videos/mozun_chongsheng/characters/c999_未存在/ 不存在
When POST /api/casting/assign role="c999_未存在"
Then 后端 200（casting.md 仍写入 row）
And `_cast.md` 不被创建（character folder 不存在 → 静默跳过）— 无文件出现在该路径
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
| FR-2 | U3.1, U2.5 (follow-up 042 force-exit watchdog) |
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
| FR-9i | U3.17 (actors/delete，follow-up 026) |
| FR-10 | U3.8 |
| FR-10b | U3.16 (GET /api/actors，follow-up 014) |
| FR-10c | U3.16 (GET /api/casting，follow-up 014) |
| FR-86 | U3.15 (attribute schema enums，follow-up 014) |
| FR-91 | U3.18 (ActorGrid 分页，follow-up 028) |
| FR-92 | U3.19 (ActorView 读视图，follow-up 034) |
| FR-93 | U3.21 (actor folder 折叠成单 leaf + ActorView delete，follow-up 036) |
| FR-94 | U3.22 (DeletedView bulk hard-delete + typed-DELETE 模态，follow-up 038) |
| FR-9s | U3.23 (GET /api/actors/assignments + ActorView assign / unassign / delete refusal，follow-up 043) |
| FR-95 | U3.23 (ActorView assignments section + cascading dropdown + delete gating，follow-up 043) |
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
| FR-96 | U9.1 (内容/生成契约 — skeleton 生成，stage-6 内容校验) |
| FR-97 | U9.2 |
| FR-98 | U9.3 |
| FR-99 | U9.4 |
| FR-100 | U9.5 |
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

---

## 追加：U8 配音池 (follow-up 115)

新增 work unit `U8 — 配音池`，承接 spec.md 的 FR-9v / FR-9v2 / FR-9v3 / FR-9v4 / FR-9v5 / FR-9v6 / FR-9v7 / FR-9v8 / FR-86v / FR-87v / FR-88v / FR-91v / FR-92v。验收场景沿用 actor 池 (U3 + U6) 的形态，但**全部禁止任何 outbound HTTP / provider credential 测试**。

| 场景 ID | 来源 FR | 标签 | 摘要 |
|---|---|---|---|
| U8.1 | FR-9v / FR-86v | [automated] | `POST /api/voices/generate` count=5 + 闭合枚举 archetype/gender/age_impression — 200 + 五个 `voice_NNNN/voice_NNNN.md` 写入 `ai_videos/_voices/`；每个 sidecar 含中文 metadata 表 + fenced "生成 prompt" 块；**断言 `httpx.AsyncClient` / `requests.` / 字面 `https://` URL 字符串在 `libs/infrastructure/writers/voice__*.py` grep 返回 0 命中**（local-only carve-out）。 |
| U8.2 | FR-9v2 | [automated] | `POST /api/voices/preview-prompts` 返回 `{prompts: [{seed, prompt}]}` 不写盘；后续以 `seeds=[previewed]` 调 FR-9v 产生 byte-equal prompt（与 FR-9j 的 actor 对照）。 |
| U8.3 | FR-9v3 | [automated] | `POST /api/voices/generate-diverse count=10` — 跨 10 个 archetype 均匀分布（每种 1 个）；同一 `notes` 文本通过；archetype-bias overlay 让 `effeminate_eunuch` vs `mighty_general` vs `gentle_palace_mistress` 在 prompt 文本上产生**可识别差异**（fixture: 用三个 archetype 各跑一次，断言生成的 prompt 字符串 hamming-distance > 阈值）。 |
| U8.4 | FR-9v4 | [automated] | `POST /api/voices/delete voice_id=voice_0003`，未分配 → 200 + soft-move 到 `_deleted/_voices/`；已分配（先 FR-9v6 assign）→ **409 voice_is_assigned** + 不动盘 + assignments 列表回传。 |
| U8.5 | FR-9v5 | [automated] | `POST /api/voices/voice_0001/audio` multipart 上传：(a) 合法 `.mp3` 1MB → 200 + 文件落在 `ai_videos/_voices/voice_0001/voice_0001.mp3` + sidecar `audio_sample` 行更新；(b) `.svg` → 400 `extension_not_allowed`；(c) 12 MiB 包体 → 413 `body_too_large`；(d) 缺失 `voice_id` 文件夹 → 404；(e) symlink 目标 → 400 + 不写盘。 |
| U8.6 | FR-9v6 | [automated] | `POST /api/casting/assign-voice` 给 `c1_zhuren` 角色绑定 `voice_0002` — `casting.md` 出现 `voice_id` 列 + `characters/c1_zhuren/_cast.md` 出现 "🎙 配音" 段 + 当样本存在时 embed `<audio>` markup；后续 `DELETE` 清除该行 + 删除 `_cast.md` 中的配音段（actor 段保留）。 |
| U8.7 | FR-9v7 / FR-9v8 | [automated] | `GET /api/voices` 返回完整列表（`audio_path` 为 null 当无样本）；`GET /api/voices/assignments?voice_id=voice_0002` 返回 `{voice_id, assignments: [...]}`；同样 actor_id-shape 校验 → 400 `invalid_voice_id`。 |
| U8.8 | FR-91v / FR-92v | [automated] | Playwright：访问 `/voices`，看到 archetype/gender/age/emotion 四个 filter dropdown + grid tiles；点击带 audio 样本的 tile 上的 ▶ 按钮触发播放（断言 `HTMLAudioElement.paused === false`，无导航）；点击 tile 本体导航到 `/file/...voice_NNNN.md` 并渲染 VoiceView 三栏布局（含 `<audio controls>` 当样本存在）。 |
| U8.9 | FR-87v / FR-93 类比 | [automated] | 后端 tree walk：`_voices/voice_NNNN/` 被 collapse 成单 leaf `{type: "voice", path, audio_path, children: []}`；sidebar 不渲染展开三角；`🗑` delete 按钮直接出现在 leaf row。 |
| U8.M1 | FR-92v / FR-9v5 | [manual_walkthrough_only] | 用户在 VoiceView drop-zone 拖入一个本地 `.mp3` 文件 → 上传成功 → 页面无刷新即出现 `<audio controls>` 并可播放；视觉确认 archetype 的中文 label（陰柔太監音 / 雄壯將軍音 / 柔美宮主音）正确显示。 |

**FR 覆盖增量**：FR-9v / FR-9v2 / FR-9v3 / FR-9v4 / FR-9v5 / FR-9v6 / FR-9v7 / FR-9v8 / FR-86v / FR-87v / FR-88v / FR-91v / FR-92v 全部映射至 U8.* 场景；任何遗漏视为文档缺陷按原则 6 在 U8 sign-off 标记 `critical`。

## 追加：U9 逐栏目 AI prompt 细化 (follow-up 117)

新增 work unit `U9 — prompt 细化建议`，承接 spec.md 的 FR-96 / FR-97 / FR-98 / FR-99 / FR-100。后端是第二个 outbound-HTTP 端点（Anthropic），验收沿用 actor 池的 outbound 形态但**只读、不写文件**（落盘仍走 FR-15 PUT）。

| 场景 | 来源 FR | 类型 | 验收 |
|---|---|---|---|
| U9.1 | FR-96 | [content/generation] | stage-6 生成或重生成一个 shot 视频 prompt：rule #12.4 全部必填字段在场；场景/镜头/动作(≥1 拍)/台词/比例/时长 非空且实质；描述性维度（运镜/光线·色调/节奏/渲染样式/多拍动作）允许只有一行 stub —— 校验器**不得**因 stub 判 warning/blocker。骨架字数远低于 2000 字 soft-limit。 |
| U9.2 | FR-97 | [automated] | `POST /api/prompt/suggest` body `{dimension:"镜头", shot_context:"…", prompt_body:"…"}`，mock AnthropicClient 返回固定 JSON 数组 → 200 + `{dimension, suggestions:[{value, rationale}]}`；断言 system 块带 `cache_control: ephemeral`；断言 mapper 解析能剥离 ```json 围栏 + 丢弃缺 value 的项。 |
| U9.3 | FR-98 | [automated] | 三个错误路径：无 `ANTHROPIC_API_KEY`（client=None）→ 503 `suggestion_unavailable`；`dimension:""` → 400 `invalid_suggestion_request`；client 抛 AnthropicRequestError / 解析失败 → 502 `suggestion_failed`。端点**不写任何文件**（断言无 PUT 副作用）。 |
| U9.4 | FR-99 | [automated/component] | PromptStructuredEditor blockKind=video + 传入 shotContext：可细化维度字段旁出现 `✨ 推荐`；点击 → 调 suggestRefinements → 渲染卡片 → 选中 + 确认 → 智能合并（空字段直接填入；非空字段换行追加，原内容保留）→ 调用方 onSave 收到合并后的 body。非 video block / 无 shotContext → 不渲染 ✨。 |
| U9.5 | FR-100 | [automated/component] + [manual_walkthrough] | 无 key 时 ✨ 面板显示「未配置 ANTHROPIC_API_KEY」且其余编辑/保存不受影响；起始帧/结束帧、actor/scene/character 结构化编辑不出现 ✨。手动走查：配好 key 后点 ✨ 实际拉到贴合本镜剧情的中文建议并成功落盘。 |

**FR 覆盖增量**：FR-96 / FR-97 / FR-98 / FR-99 / FR-100 全部映射至 U9.* 场景；任何遗漏视为文档缺陷按原则 6 在 U9 sign-off 标记 `critical`。
