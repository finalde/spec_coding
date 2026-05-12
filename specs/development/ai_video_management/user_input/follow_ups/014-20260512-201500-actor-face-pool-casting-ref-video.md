# Follow-up draft 014 — 2026-05-12

新增三件事到 ai_video_management webapp，按 pipeline 顺序：

1. **Actor face pool** — 在仓库里维护一个用 AI 生成的"演员人脸"图片库，每张图带属性标签（民族 / 性别 / 年龄段 / 外貌气质 / 风格 等），webapp 可浏览 / 筛选 / 标签编辑 / 管理。
2. **Casting workflow** — 在 ai_video project 内，把 pool 中某个 actor 关联到该 project 的某个 role（character），形成 role → actor 映射。Casting 表可编辑可重置。
3. **Reference video generation** — 完成 casting 后，把 actor 的 face image 与现有 character turntable 2.9s Seedance prompt（agent_refs/project/ai_video.md rule #12.5）组合，产出 Seedance image-to-video ref-video 输入，最终的 mp4 落到 `ai_videos/{drama}/characters/c{N}_*/c{N}_*.mp4`（继续遵守 ≤ 2.9s 硬上限）。

## 用户原话

> lets add a new features to the ai_video_management, I will first need you to acurately genreate me a pool of actor faces using AI, like asian, men, 20~25 ages, handsome etc, all the pictures are well labled and managed, and then we need a workflow process to do casting, like pic actor A for the role B in this ai vidoe project C, and once we complete this casting, we will use the picture together with the 2.9s prompt you generated previously to generate a reference video for each charactor

(`charactor` = `character` 笔误；`pic` = `pick` 笔误)

## 上下文锚点

- "2.9s prompt you generated previously" 指 `agent_refs/project/ai_video.md` rule #12.5（character turntable Seedance reference 2.9s 硬上限）+ follow-up 013 已把 `ai_videos/mozun_chongsheng/characters/c*/c*.mp4` 全 19 个文件就地 trim 到 ≤ 2.9s，artifact 已对齐规则。
- 现有 import 流（follow-up 009 `POST /api/import-from-downloads`）已具备「从 Downloads 扫近 7 天 image/video → substring-match 分类 → move 到 drama 内」能力；新功能可在此基础上扩展，而不是另起炉灶。
- 现有 webapp 至 follow-up 013 都遵守"text-prompt viewing/editing only"原则（follow-up 001 hard-out-of-scope），从不直接调外部 AI API。本 follow-up **可能**会突破此原则（视 Q2/Q4 决策而定）。

## 决策 (interactive 收集，2026-05-12)

| 问 | 用户答 |
|---|---|
| Pool 位置 | `ai_videos/_actors/` — 特殊下划线前缀目录，在现有 `ai_videos/` 顶级根内；不当 drama 处理（sub_type 不检测、rename / import 按钮不出现）。Sandbox 自然 admit（`is_inside` 已 admit `ai_videos/**`）。 |
| Face 生成姿势 | **完全自动 + 用 pollinations.ai 免费 API**（endpoint `https://image.pollinations.ai/prompt/{url-encoded prompt}?model=flux&width=512&height=512&seed=N&nologo=true`；无 API key，无 signup，MIT 协议，许可 download/cache）。否决 Generated.Photos（ToS 禁 caching/downloading）、thispersondoesnotexist（无属性控制）、HuggingFace Inference（要 token + 1000/day 上限）。 |
| Casting 持久化 | `ai_videos/{drama}/casting.md` 单 markdown 表（role / actor_id / notes 三列；缩略图由前端 CastingView 通过 actor_id 查询 actor 池实时渲染，不在 md 内 inline 图）。 |
| Ref-video 生成 | **不进 webapp**。用户手工：在 webapp 内看到 actor face path + rule #12.5 的 2.9s prompt → 复制到 Seedance 外部跑 → 下载 → 走已有 follow-up 009 import-from-downloads 流程落到 `characters/c{N}_*/c{N}_*.mp4`。 |

## 属性 schema（六字段）

每张 face 用六个字段 label，前五个 enum，第六个自由文本：

| 字段 | 选项 |
|---|---|
| `ethnicity` | asian / east-asian / south-asian / caucasian / african / latino / middle-eastern / mixed |
| `gender` | male / female |
| `age_range` | 18-25 / 26-35 / 36-50 / 51-65 / 65+ |
| `look` | handsome / beautiful / cute / mature / rugged / soft / aristocratic / fierce |
| `style` | modern-casual / period-ancient-china / period-western / business / streetwear / sci-fi / fantasy |
| `notes` | 自由文本（可空） |

后端从六字段 deterministic 拼接一条英文 Seedream 风格 prompt，例如：
`portrait headshot of asian male, 22 years old, handsome, period ancient chinese cultivator outfit, professional studio lighting, neutral background, photorealistic, sharp focus, 8k`

## 文件 layout

```
ai_videos/
├── _actors/                          # 新：actor face pool（不是 drama）
│   ├── actor_0001/
│   │   ├── actor_0001.jpg            # pollinations.ai 输出的人脸
│   │   └── actor_0001.md             # sidecar：属性 + 生成 prompt + seed
│   ├── actor_0002/
│   │   └── ...
│   └── ...
└── {drama}/
    ├── casting.md                    # 新：role → actor_id 映射表
    ├── characters/
    │   └── c{N}_*/                   # 现有结构不动
    └── ...
```

## 新增 endpoint（5 个）

- `POST /api/actors/generate` — body `{count: 1..20, ethnicity, gender, age_range, look, style, notes?}` → 循环调 pollinations.ai N 次（不同 seed）→ 每张图落到 `ai_videos/_actors/actor_NNNN/`；返回 `{generated: [{id, image_path, attrs}], errors}`
- `GET /api/actors` — 列出 pool 全部 actor + 属性（给 casting picker 用）
- `GET /api/casting?path=ai_videos/{drama}` — 读 `casting.md` 解析 entries
- `POST /api/casting/assign` — body `{path, role, actor_id, notes?}` → upsert row 到 `casting.md`
- `DELETE /api/casting/assign` — body `{path, role}` → 删 row

新 endpoint 仍走 SecurityHeadersMiddleware（CSP / X-Content-Type-Options / Referrer-Policy）。Origin/Host gate（`GUARDED_ROUTES`）暂沿用现有 pattern——只 PUT /api/file 在 gated set 内，新 POST/DELETE 与现有 rename / archive / import 一致地不加 gate（已知 security gap，留给后续 security pass）。

## 新增前端 view / 组件

- `ActorPoolGenerator.tsx` — 模态表单：六字段下拉 + count + 提交 → 调 `/api/actors/generate`。从 Sidebar 上 `_actors/` 行的 "🎭 Generate" 按钮触发。
- `ActorGalleryView.tsx`（可选 v1）— 浏览模式：filter chips + 缩略图网格。v1 简化：直接在 sidebar 展开 `_actors/` 看 actor folders；每个 `actor_NNNN.md` 用现有 markdown view + SiblingMedia 渲染。
- `CastingView.tsx` — Reader 在 path 命中 `ai_videos/{drama}/casting.md` 时 dispatch。两段：
  - **Read mode**：显示当前 casting 表 + 每行 actor 缩略图（通过 `/api/actors` 查询）+ rule #12.5 的 2.9s prompt 直接 inline 复制按钮（含 face path）。
  - **Assign mode**：filter chips（按属性筛 actor）+ 缩略图网格 + 每个 role 一个 dropdown（actor_id 选择）→ 调 `/api/casting/assign`。

## 新增后端 libs

- `actor_pool.py` — `ActorPool` 类：`generate_batch` / `list_actors`；prompt builder；ID 分配（`actor_{NNNN}` 自增）；httpx GET pollinations.ai；保存 jpg + 写 sidecar md；error per file 不 fail 整 batch。
- `casting.py` — `Casting` 类：`read_casting(drama)` / `assign(drama, role, actor, notes)` / `unassign(drama, role)`；管理 `casting.md` 表格的 parse + write（整文件重写避免 markdown table 编辑边界 case）。

## 安全 / 边界扩展

- **首次出站 HTTP**：backend 第一次访问外部 URL（pollinations.ai）。Server-side 硬化：
  - 写死 `POLLINATIONS_BASE = 'https://image.pollinations.ai/prompt/'`，不接受用户传 URL。
  - prompt 仅作 URL path segment + URL-encoded，无 redirect 跟随。
  - 每张图 30s 超时；批量上限 20 张；每张响应读取 cap 5MB；连接失败 → 单张 error，不 fail batch。
- **写路径**：仅在 EXPOSED_TREE 内（`ai_videos/_actors/actor_NNNN/`）；ID 单调自增防覆盖。
- **CSP `connect-src 'self'`** 不变 —— 前端从不直接访问 pollinations.ai；走 backend proxy。
- 新增 endpoint 仍受 SecurityHeadersMiddleware 覆盖。
- 不引入新 secret / API key（pollinations.ai 无 auth）。

## 不在本 follow-up 范围

- 不动 rule #12.5 的 2.9s 硬上限；ref-video 生成仍走"用户手工外部跑 + import"。
- 不动 rule #12.10 的 3.9s scene reference 规则。
- 不引入 backend pytest + e2e Playwright（与 005-013 一致推迟）。
- 不引入 actor face delete endpoint（v1 用文件系统手工删；后续可加）。
- 不引入 actor face edit / regenerate-with-same-attrs（v1 不重跑同 prompt+seed）。
- 不引入 cross-drama casting clone（每 drama 独立 `casting.md`）。
- 不引入 Origin/Host gate 扩展（与现有 pattern 一致；security gap 留给独立 follow-up）。
- 不引入 face attribute auto-classification（属性来自用户填的表单 → 100% 准确，无需 ML 推断）。

## 不在本 follow-up 范围（v1 红线）

- 不动 character turntable rule #12.5 的 2.9s 硬上限（follow-up 013 刚把 artifact 对齐到这条规则；ref-video 输出继续遵守）。
- 不影响 scene reference video rule #12.10 的 3.9s（follow-up 010 已定）。
- 不影响 spec_driven webapp / 现有 spec pipeline。
- 不在本 follow-up 内做 backend pytest + e2e Playwright（与 005-013 一致推迟）。
