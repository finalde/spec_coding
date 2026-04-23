---
name: video_generation__seedance-packager
description: Turn a locked storyboard (from `storyboard-master`) plus the four series bibles into per-clip Seedance 2.0 生成包——每段一份 `.txt` video prompt、每段之间一份快照 prompt、整集一份 `generation_manifest.md`。本 skill 是**无状态的 prompt 组装器**：不研究、不发明、不改写人物/场景措辞，只把 `复用片段` 原样粘回去、挂参考图、套用 topic-scout 的固定 boilerplate、按第 4 段强制锚点重置。Use this between `storyboard-master` and `continuity-director`.
---

# 分镜打包 · Seedance Packager — 逐段 Prompt 组装

吃 `storyboard.md` + 四本圣经 + `anchor_registry.md` 当输入，逐段拼出可一键贴进 Seedance 2.0 的 prompt 文件。本 skill **不**做创作——所有人物、场景、风格文字都从圣经里逐字搬。

## Workflow

### Step 1 — 读入并校验

必读：
- `series/{name}/prompts/ep_{NNN:03d}/storyboard.md`
- `series/{name}/bibles/character_bible.md`
- `series/{name}/bibles/scene_bible.md`
- `series/{name}/bibles/style_bible.md`
- `series/{name}/bibles/voice_bible.md`
- `series/{name}/bibles/anchor_registry.md`
- `series/{name}/status.md`

前置校验（任一不满足 → 中止）：
- `status.md.bibles == LOCKED`
- `status.md.ep_{NNN} == storyboarded`
- `storyboard.md` 的 `## 锚点解析摘要` 全部命中
- beat 数 6–8、每段 ≤15s、总时长 90–120s

### Step 2 — 抽取 `复用片段` 到内存清单

对本集 `anchors_used` 里出现的每个锚点，从对应圣经拉出 20–40 字 `复用片段` 原文，存为：

```
anchor_map = {
  "character:角色A.近景": "……20-40字原文……",
  "scene:场景X.近景":    "……20-40字原文……",
  "style:风格锚点":       "……≈20字原文……",
  ...
}
```

后续所有 prompt 逐字粘贴，禁止改写。缺任一条 → HARD FAIL。

### Step 3 — 逐段生成视频 Prompt

对每段 `beat_index = M` 生成 `prompts/ep_{NNN:03d}/clip_{M:02d}_video_prompt.txt`，严格按以下模板（全部中文，每行原样）：

```
【分镜视频 Prompt — 第 {EP} 集 第 {M} 段（共 {TOTAL} 段）】

一、开头声明
{OPENER}
参考图挂载：
- 人物参考图：@人物参考图_{角色ID}（三视图：正/侧/背）
{若第二角色} - 人物参考图：@人物参考图_{角色B_ID}（三视图：正/侧/背）
- 背景参考图：@背景参考图_{场景ID}（三视图：远/近/特）
{若为续接段} - 快照参考图：@快照参考图_ep{EP}_clip{M-1}_末帧
{若 M % 4 == 0} 本段需以三视图参考图为首要身份锚点，快照仅作构图参考。

二、主体（逐字复用，禁止改写）
角色 {角色ID}：{复用片段_角色ID}
{若第二角色} 角色 {角色B_ID}：{复用片段_角色B_ID}
场景 {场景ID}：{复用片段_场景ID}
风格锚点：{复用片段_风格锚点}

三、本段叙事
景别：{storyboard.景别}
镜头运动：{storyboard.运镜}（运动幅度：{storyboard.运动幅度}）
动作流程：{storyboard.画面}
情绪弧线：{情绪起} → {情绪止}
光线/色温：{storyboard.光线色温}
时长：{storyboard.duration_s}s

四、角色阻挡（仅多角色时）
{storyboard.blocking_note_multi_char}

五、画质标注
4K 超高清，镜头运动流畅，皮肤与场景真实质感，电影级光影，短视频风格

六、负向约束
避免人物脸型/五官漂移，避免服装类别与主色变化，避免背景元素增减，避免光线色温跳变，避免出现未指定角色。
{若景别属 大特写/特写/近景 或 画面含头部转动} 附加：面部运动幅度 ≤2，避免面部形变。

七、收尾声明
{CLOSER}
```

替换规则：
- `{OPENER}` 首段（M=1）：`将根据附带的人物参考图、背景参考图，生成本段分镜视频`
- `{OPENER}` 续接段（M≥2）：`将根据附带的人物参考图、背景参考图、以及前一段快照参考图，继续生成本段分镜视频`
- `{CLOSER}` 首段：`以人物参考图、背景参考图为全部参考生成视频`
- `{CLOSER}` 续接段：`以人物参考图、背景参考图、快照参考图为全部参考生成视频`
- 这 4 条 boilerplate 逐字来自 `topic-scout`，一个字都不能改。

### Step 4 — 逐段生成快照 Prompt

对 M = 1..TOTAL-1 生成 `prompts/ep_{NNN:03d}/clip_{M:02d}_snapshot_prompt.txt`。末段无快照。

模板（全部中文）：

```
【快照图 Prompt — 第 {EP} 集 第 {M} 段末帧 → 第 {M+1} 段起始帧】

一、开头声明
本次将根据附带的人物参考图与背景参考图，仅生成 1 张快照画面，用于后续视频续接的起始帧参考。
参考图挂载：
- 人物参考图：@人物参考图_{角色ID}
{若第二角色} - 人物参考图：@人物参考图_{角色B_ID}
- 背景参考图：@背景参考图_{场景ID}

二、主体（逐字复用）
角色 {角色ID}：{复用片段_角色ID}
{若第二角色} 角色 {角色B_ID}：{复用片段_角色B_ID}
场景 {场景ID}：{复用片段_场景ID}

三、末帧画面精确描写（必须与第 {M} 段末帧完全一致）
景别：{快照存根.景别}
角色姿态：{快照存根.角色姿态}
表情：{快照存根.表情}
道具状态：{快照存根.道具状态}
服装状态：{快照存根.服装状态}
背景元素位置：{快照存根.背景锚定元素 3–5 项}
光线：{快照存根.光线}

四、画质标注
4K 超高清，单帧静态图，真实质感，电影级光影，与前段视频末帧像素级对齐

五、负向约束
避免姿态/表情/服装/光线相对前段末帧发生任何变化；避免新增或移除背景元素。

六、收尾声明
以附带的人物参考图和背景参考图为基准生成。
```

所有字段从 `storyboard.md` 的 `### 快照存根 · beat M → beat M+1` 子块直接取。缺任一字段 → HARD FAIL。

### Step 5 — 锚点重置（每 4 段一次）

对 M ∈ {4, 8}（本集 ≤8 段，至多两次）：
- 视频 prompt 一、开头声明 末尾追加：`本段需以三视图参考图为首要身份锚点，快照仅作构图参考。`
- 在 `generation_manifest.md` 的「锚点重置」列打勾。
- 本段不允许以快照为**唯一**参考：若本段没有第二角色也没有额外场景锚点，额外再把风格锚点 `复用片段` 复述一次。

### Step 6 — 生成 `generation_manifest.md`

写到 `series/{name}/prompts/ep_{NNN:03d}/generation_manifest.md`：

```markdown
# 第 {EP} 集 Seedance 生成清单

## 基本信息
- 系列：{series_name}
- 本集：ep_{NNN}
- 片段数：{TOTAL}
- 预计总时长：{sum}s
- 视觉/连续性圣经版本：{style_bible 版本 hash/date}
- 语音圣经版本：{voice_bible 版本 hash/date}

## 参考图清单（生成前需全部就位）
- 角色 {角色ID} 三视图：{path/正面.txt} {path/侧面.txt} {path/背面.txt}
- {若第二角色} 角色 {角色B_ID} 三视图：{…}
- 场景 {场景ID} 三视图：{path/远景.txt} {path/近景.txt} {path/特写.txt}

## 运行顺序
| 序号 | 类型 | 文件 | 时长 | 角色 | 场景 | 景别 | 运动幅度 | 锚点重置 |
|------|------|------|------|------|------|------|----------|----------|
| 1 | 视频 | clip_01_video_prompt.txt | {d}s | … | … | … | … | — |
| 2 | 快照 | clip_01_snapshot_prompt.txt | — | … | … | … | — | — |
| ... |
| K | 视频 | clip_04_video_prompt.txt | {d}s | … | … | … | … | **是** |
| ... |

## 验收标准（每段生成后人工校验）
1. **身份一致性** — 角色面部、发型、服装与三视图参考对比无明显漂移
2. **场景一致性** — 背景锚定元素位置、色调、光线与场景参考一致
3. **末帧对齐** — 本段末帧与下一段快照图像素级一致
4. **负向约束命中** — 无脸型漂移 / 无服装类别变化 / 无背景元素增减 / 无光线跳变 / 无未指定角色

## 失败处理
- ≥6/8 段通过 → 接受本集；失败段重跑前先检查累积漂移（第 4+ 段且未重置锚点 → 先加重置再重跑）
- <6/8 段通过 → 停机，回 `serial-novelist` 查剧本或 `preproduction` 查圣经冲突
- 单段 3 次仍漂移 → 降运动幅度至 1；仍失败 → 拆为两段 7–8s 子段

## 警告清单（本次打包触发）
{逐条列 SOFT WARN 命中项；无则写「无」}
```

### Step 7 — 写出 + 状态置位

- 所有 prompt 文件保存到 `series/{name}/prompts/ep_{NNN:03d}/`
- `status.md.ep_{NNN}` 置为 `packaged`
- 同时在 `status.md.last_packaged_at` 写入当前日期

## Inputs

- `series/{name}/prompts/ep_{NNN:03d}/storyboard.md`
- `series/{name}/bibles/*`
- `series/{name}/bibles/anchor_registry.md`

## Outputs

- `series/{name}/prompts/ep_{NNN:03d}/clip_{M:02d}_video_prompt.txt`（每段一份）
- `series/{name}/prompts/ep_{NNN:03d}/clip_{M:02d}_snapshot_prompt.txt`（末段外每段一份）
- `series/{name}/prompts/ep_{NNN:03d}/generation_manifest.md`
- 更新 `series/{name}/status.md`

## 输出规范

- **全部中文**；仅 hex / `4K` / `DoF` / voice_id / `@image1` 类 handle 保留英文。
- **每份 prompt ≤2000 字**（HARD FAIL）；**>1200 字触发 SOFT WARN**。
- **复用片段必须逐字**来自圣经；禁止改写、润色、顺序调换。
- **topic-scout 的 4 条 boilerplate 和画质标注、负向约束逐字复用**；一个字不动。
- **锚点重置**：M % 4 == 0 必须加三视图强调句；每集至多连续 3 段仅靠快照。
- **负向约束 ≤5 条**；特写/近景/头部转动段追加一条面部运动幅度限制，不超过 6 条。
- **禁用空泛形容词**（沿 `topic-scout`）。
- **不调用网络 / 不搜索**；本 skill 是纯本地组装。
- **2–3 个核心角色**（Q8a）：声明块里的 `角色 {ID}` 必须是 `character_bible.md` 登记的 2–3 个核心角色之一；本集不得引入第 4 个核心角色。

## HARD FAIL 触发条件（中止，不产出）

- 任一 `.txt` >2000 字
- `anchors_used` 里任一锚点的 `复用片段` 在圣经里找不到
- storyboard 里声明的角色不在 `character_bible.md` 登记的 2–3 个核心角色里
- 单段超过 3 个角色
- 本集整体出现 >3 个核心角色
- storyboard 的 光线/色温 与 `scene_bible.md` 对应场景条目不一致
- 快照存根缺姿态 / 表情 / 道具 / 服装 / 背景 / 光线 任一六维
- 多角色段缺 `blocking_note_multi_char`

## SOFT WARN 触发条件（照样产出，但在 manifest 的「警告清单」里列出）

- 任一 `.txt` >1200 字
- 连续 4 段及以上未触发锚点重置（自动在最近一段注入重置并 warn）
- 特写/近景段 `运动幅度` 未在 storyboard 给出（自动设为 2 并 warn）
- 同段两角色服装主色相同（身份互换风险）
- 快照存核里背景锚定元素 <3 项（续接对齐难度升高）

## 边界情况

- 本集只有 1 个角色 → 所有「若第二角色」块全部不输出；主体块只声明一个角色。
- 本集只有 1 个场景 → 场景条目只出现一次；快照若沿用同场景则快照主体块的 `场景` 逐字复用同一 `复用片段`。
- 本集为季首（ep_001）→ M=1 用首段 `{OPENER}` / `{CLOSER}`；无 `快照参考图` 挂载。
- 本集为季末（如 ep_060）→ 最末段视频 prompt 的 `收尾声明` 正常；无需生成末段快照 prompt（没有下段）。
- storyboard 中已有某段被明确标记「头部转动」或「面部表情大幅变化」→ 无论景别，强制在负向约束追加「面部运动幅度 ≤2」。
- 上游给了 `episode_wardrobe_note`（per-ep 变体）→ 仅在 `character_bible.md` 显式允许 wardrobe 变体时插入；否则忽略并 warn。

## Invocation examples

- 「把 `series/战神归来/ep_003` 的 storyboard 打包成 Seedance prompt。」
- 「`series/剑尊重生/ep_012` 第 5 段触发 HARD FAIL（复用片段缺失），逐项报出来。」
- 「只重生成 `ep_007` 的 manifest，不改已有的 clip prompt。」
