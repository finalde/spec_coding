---
name: video_generation__storyboard-master
description: Expand one 短剧 episode's 4-column beat sheet into a production storyboard: 6–8 beats × ≤15 s, 15 s snapshot stubs between beats, locked 景别 / 运镜 vocabulary, full anchor resolution. Each beat is self-contained so `seedance-packager` can turn it into a Seedance prompt without rereading prose. Runs between `serial-novelist` and `seedance-packager`.
---

# 分镜大师 · Storyboard Master — 单集 4 栏分镜 + 15 秒快照

吃一集 `episodes/ep_{N}.md` 的 4 栏 beat sheet 当输入，把它扩成一份 **生产级分镜稿** + **段与段之间的快照提示**。本步骤不再写新内容 —— 只整理、校验、补运镜细节、补快照。

## Workflow

### Step 1 — 读入上下文

- `series/{name}/episodes/ep_{NNN:03d}.md`
- `series/{name}/bibles/character_bible.md` / `scene_bible.md` / `style_bible.md`
- `series/{name}/bibles/anchor_registry.md`
- `series/{name}/status.md`

校验 `status.md.bibles == LOCKED`；否则中止并指回 `preproduction`。

### Step 2 — Beat 数量 + 总时长校验

- Beat 数 **6–8**（硬边界）。<6 → 要求 `serial-novelist` 加段；>8 → 要求合并。
- 总时长 **90–120 s**（即 6 × 14.4 s ≈ 86 s 起，8 × 14.4 s ≈ 115 s 止；含 Seedance 首末 0.3 s 修边容差）。超 120 s → 要求 `serial-novelist` 压缩；< 90 s → 要求加 BGM 尾奏或多一段。

### Step 3 — 四栏展开

逐 beat 扩写。每行必填：

| 字段 | 说明 |
|---|---|
| `beat_index` | 1 起算 |
| `duration_s` | ≤15（Seedance 硬限）；首推 13–14 s（留 Seedance 末帧渐隐容差） |
| `画面` | `景别` + `运镜` + `{{scene:id.view}}` + `{{character:id.view}}` + 一句动作描写（30–60 字） |
| `对白` | `【角色ID】"≤10 字"` 一条或 `（无对白）` |
| `旁白` | ≤2 短句或 `（无旁白）` |
| `情绪节拍` | 从 `踩 / 亮 / 碾 / 钩 / 垫 / 升 / 收` 七字里选 1–2 |
| `景别` | 独立字段便于 packager 抽取：`大特写 / 特写 / 近景 / 中近景 / 全景 / 远景` |
| `运镜` | 独立字段：`推近 / 拉远 / 跟拍 / 平移 / 环绕 / 固定` |
| `运动幅度` | 1–5；面部特写 / 近景 → ≤2；全景 / 动作段 → 3–4；禁用 5（易漂移） |
| `光线色温` | 直接引用 `scene_bible` 复用片段里的光源描写；允许本段扩写（例：加「侧逆光 5600K」） |
| `道具清单` | 本段画面内必须出现的道具逐项列出 |
| `TTS 音素提示` | 本段 VO 中的 多音字 / 生僻字 pinyin 修正 |
| `字幕安全文本` | 单行 ≤15 汉字，`|` 分行；对白与旁白分别写一条 |
| `anchors_used` | 本段用到的全部 `{{...}}` 锚点，逗号分隔，用于 packager 快速解析 |

### Step 4 — 锚点解析校验

对每行 `anchors_used` 里的每个 `{{...}}`：

- 在 `anchor_registry.md` 里查 → 必须全部命中，否则中止并报缺失。
- 从 `character_bible.md` / `scene_bible.md` / `style_bible.md` 拉 **复用片段** 原文，附在本段下方的 `## 复用片段引用` 子块（为 packager 提供逐字源）。
- 风格锚点 `{{style:anchor}}` 必须出现在第 1、5 段（默认锚定位置）；若剧本该集较短（≤6 段）则仅第 1 段。

### Step 5 — 15 秒快照存根

在相邻两段之间插入 **快照存根**（`snapshot_{M}_to_{M+1}.md` 会由 packager 写；本 skill 只在 storyboard 里记字段）：

```markdown
### 快照存根 · beat {M} → beat {M+1}

- 景别：{从 beat M 末尾推出}
- 角色姿态：{头角 / 视线 / 四肢}
- 表情：{眉 / 眼 / 嘴}
- 道具状态：{每件可见道具位置与姿态}
- 服装状态：{褶皱 / 位移 / 开合}
- 背景锚定元素：{3–5 个定位于画面区}
- 光线：{光源方向 + 色温 + 阴影落点}
- anchors_carry_over: {需要在下段继续锁定的锚点}
```

**每相邻两段之间必写一条**。最末段无下段，故不写。

### Step 6 — 前后集连贯钩

在 storyboard 开头写 `## 跨集锚定`：

- `open_frame`：本集第 1 段起始帧 = 上一集末帧。照抄上一集 `前后集连贯钩` 的末段帧描写。
- `close_frame`：本集末段末帧 = 下一集起始帧；承接 `ep_{NNN}.md` 的 `前后集连贯钩` 条目。

### Step 7 — 写出

保存到 `series/{name}/prompts/ep_{NNN:03d}/storyboard.md`，顺序章节：

1. `## 元信息`（集号 / beat 数 / 总时长 / 字数 / 风格锚点引用位置）
2. `## 跨集锚定`（open_frame / close_frame）
3. `## 分镜 4 栏` 表格（所有字段）
4. `## 复用片段引用`（本集用到的全部复用片段原文）
5. `## 快照存根`（N-1 条）
6. `## 锚点解析摘要`（anchor → 文件路径 → 行号）
7. `## 验收前置`（把 `status.md.ep_{NNN}` 置为 `storyboarded`）

## Inputs

- `series/{name}/episodes/ep_{NNN}.md`
- `series/{name}/bibles/*`
- `series/{name}/bibles/anchor_registry.md`

## Outputs

- `series/{name}/prompts/ep_{NNN:03d}/storyboard.md`
- 更新 `series/{name}/status.md`

## 输出规范

- **全部中文**；仅 hex / `4K` / `DoF` / voice_id 保留英文。
- **6–8 beat 硬约束**；**每段 ≤15 s**；**总时长 90–120 s**。
- **运动幅度**：面部特写 / 近景段 ≤2，全景 / 动作段 3–4，禁 5。
- **景别 / 运镜词表白名单**严格执行（见 Step 3 表）；越界 → 中止。
- **锚点必须全解析**，缺一中止；**复用片段必须逐字粘贴**。
- **风格锚点** 第 1 段必挂；≥5 段时第 5 段再挂一次。
- **快照存根** 在相邻 beat 之间必写一条；描述细粒度到姿态 / 表情 / 道具 / 服装 / 背景 / 光线六维。
- **字幕单行 ≤15 汉字**；不得把对白与旁白写到同一行。
- **禁用空泛形容词**（沿用 `topic-scout`）。

## 边界情况

- beat 数 <6 或 >8 → 中止并把缺 / 超几条列清楚，要求 `serial-novelist` 改稿。
- 总时长 <90 s 或 >120 s → 中止并提供压缩 / 补段建议。
- 有锚点没登记 → 中止并列出缺失清单，指回 `preproduction`。
- 同 beat 出现 > 2 个对白角色 → 警告并要求拆段（多角色同台是 Seedance 身份漂移重灾区）。
- 上一集 `close_frame` 与本集 `open_frame` 显著不匹配 → 中止并要求 `serial-novelist` 重写本集开场。

## Invocation examples

- 「给 `series/战神归来/ep_003` 出分镜稿。」
- 「重出 `series/剑尊重生/ep_012` 的分镜，把第 4 段砍成两个 8 秒子段。」
- 「只刷新 `ep_005` 的快照存根，beat 表保留。」
