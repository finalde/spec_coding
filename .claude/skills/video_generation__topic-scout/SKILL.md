---
name: video_generation__topic-scout
description: Search online for trending or evergreen topics suited for AI video generation, evaluate them for AI-friendliness, and produce a validated storyboard. Use this when the user wants to find a new video topic, brainstorm AI video ideas, scout viral trends for short-form video, or kickstart a new AI video project.
---

# Topic Scout — AI Video Topic Discovery & Storyboard

Find the best topic for an AI-generated video, validate it for AI-friendliness, and produce a foundation storyboard ready for downstream scene/character breakdown.

## Modes

### Short Video Mode (under 60 seconds)

**Strategy: Trending Topic Mining**

1. Search the web for current trending topics across platforms (Twitter/X, TikTok, YouTube Shorts, Reddit, Google Trends).
2. Filter for topics that are:
   - Peaking NOW or within the last 48 hours
   - Visual and dramatic (not text-heavy news)
   - Emotionally resonant (awe, humor, curiosity, surprise)
   - Simple enough to convey in under 60 seconds
3. Prioritize topics with high shareability and comment-bait potential.

### Long Video Mode (1–5 minutes)

**Strategy: Evergreen Curiosity**

1. Search for proven "what if" / "how does X work" / "things you didn't know" topics with steady search volume.
2. Look for topics that have worked well on YouTube (high view-to-sub ratio) but haven't been done as AI video.
3. Favor topics with:
   - Clear narrative arc (setup → escalation → payoff)
   - Multiple distinct visual scenes (not talking heads)
   - Universal appeal across cultures

## Workflow

### Step 1 — Research

Use `WebSearch` to find candidate topics. Gather at least 6–8 raw candidates.

For **short mode**: search for trending topics, viral moments, current events with visual potential.
For **long mode**: search for evergreen curiosity topics, popular explainers, "most amazing" lists.

### Step 2 — AI-Friendliness Evaluation

Score each candidate on the **AI Generation Feasibility Scorecard** (0–10 per criterion, out of 60 total):

| Criterion | What it measures |
|-----------|-----------------|
| **Visual Simplicity** | Can scenes be described in 1–2 sentences? Few complex interactions? |
| **Character Feasibility** | No real celebrities or public figures needed? Generic/fictional characters work? |
| **Scene Variety** | Multiple distinct environments/moments? Not just one static setting? |
| **Motion Friendliness** | Avoids fast action, crowds, sports, or complex physics? Slow/medium motion works? |
| **Emotional Hook** | Strong feeling in the first 3 seconds? Curiosity, shock, awe, humor? |
| **Narrative Clarity** | Can the story be understood without dialogue? Visual storytelling works? |

**Threshold**: Only topics scoring **40+/60** proceed.

### Step 3 — Present Candidates (Rich Detail)

每个候选主题必须包含足够细节，下游工作流可直接提取分镜 Prompt、人物参考 Prompt、背景参考 Prompt，无需额外调研。格式如下：

```markdown
## 候选主题 {N}：{中文标题}

### 概览

**模式**：短视频 / 长视频
**时长**：{目标时长}秒
**画幅**：9:16（默认）或用户指定
**来源/趋势**：{出处，为何正在流行或有长期吸引力}
**一句话概要**：{核心钩子，一句话}
**标签**：{8–12 个标签，中文为主}

### AI 可行性评分：{总分}/60

| 评估维度 | 得分 | 说明 |
|----------|------|------|
| 视觉简洁度 | {x}/10 | {评分理由} |
| 人物可行性 | {x}/10 | {评分理由} |
| 场景多样性 | {x}/10 | {评分理由} |
| 运动友好度 | {x}/10 | {评分理由} |
| 情绪钩子 | {x}/10 | {评分理由} |
| 叙事清晰度 | {x}/10 | {评分理由} |

**漂移风险**：{AI 生成中可能不一致的部分}
**缓解策略**：{如何降低每项漂移风险}

### 叙事

{3–5 段散文体，从第一帧到最后一帧完整讲述故事。
必须具体生动——描述观众"看到"什么，而非抽象概念。
包含感官细节：颜色、质感、运动方式、光线变化、情绪节拍。
这是下游工作流理解故事的核心来源。}

### 人物约束

**每条视频最多 1–2 个人物。** 单人物故事优先，仅在剧情必须互动时允许两个人物。严禁超过两个——群像、人群、多人合照均不在范围内。

### 人物（3D 模型三视图规范）

每个人物生成**正面、侧面、背面 3 张独立视角 Prompt**（纯中文），每张必须包含以下内容（缺一不可）：

- **名称/角色**：如"小女孩（主角）"
- **基础信息**：年龄、性别、国籍/民族、身高、体型
- **五官细节**：眉形、眼型、鼻型、唇形、脸型、肤色及肤质（细腻/粗糙/皱纹）、妆容（无妆/淡妆/浓妆 + 具体效果）
- **发型细节**：发色（hex）、长度、造型、发丝质感
- **穿搭细节**：上衣、下装、鞋子、配饰——材质、颜色（hex）、花纹、版型逐一标明
- **神态细节**：贴合剧情情绪，明确眼神与面部表情
- **肢体姿态**：站姿/坐姿/手持道具等自然姿态，适配各视角
- **随身道具**：角色携带或互动的物品
- **肢体语言**：移动方式、体态、精力状态
- **弧线**：从开头到结尾外貌/表情的变化
- **参考说明**：末尾统一标注 —— 以附带的 3 张人物三视图参考图为基准生成 3D 人物模型
- **画质要求**：末尾统一标注 —— 4K 超高清，电影级光影，真实质感，全身无裁切，纯白背景便于模型提取
- **复用片段**：{20–40 字可复制粘贴到所有生成 Prompt 中的人物描述}

### 环境/背景（3 张不同视角规范）

每个环境生成**远景 + 近景 + 特写**（或正面 + 侧面 + 俯视/仰视）共 3 张 Prompt。3 张必须描绘**同一场景**，细节统一。

每张必须包含以下内容（缺一不可）：

- **名称**：如"荒原""水下洞穴"
- **场景信息**：场景名称、在故事中的用途
- **环境设定**：地点类型、时间段、季节、天气
- **环境细节**：室内/室外、材质、颜色、状态
- **关键元素**：3–5 个定义此环境的必备视觉元素
- **道具细节**：场景内所有道具的位置、材质、颜色、纹理
- **色彩组合**：3–4 种主色调（附 hex 值）
- **光影细节**：光源类型、角度、效果（柔光/逆光/阴影等）、色温
- **氛围色调**：整体情绪 + 色调风格（暖/冷/高饱和/低饱和）
- **氛围效果**：雾气、微粒、体积光、灰尘、雨水等
- **空间感/纵深**：空间是宏大还是亲密
- **声音印象**：观众想象中会听到什么——即使无声也用来塑造情绪
- **参考说明**：末尾统一标注 —— 以附带的 3 张不同视角背景参考图为基准搭建 3D 场景
- **画质要求**：末尾统一标注 —— 4K 超高清，极致细节，真实质感，无人物仅场景道具，电影级氛围
- **复用片段**：{20–40 字可复制粘贴到所有生成 Prompt 中的场景描述}

### 分镜拆解（顺序视频 Prompt + 15 秒快照机制）

**固定 3 场分镜。** 结构：钩子（场景 1）→ 剧情推进（场景 2）→ 高潮+结尾（场景 3）。每场只讲一个核心动作/情绪。

**Seedance 15 秒上限规则**：Seedance 单次生成上限 15 秒。当某场超过 15 秒时，必须按 15 秒切分。在每个 15 秒边界处提供一张**快照图 Prompt**，描述该时刻的精确画面。用户据此生成静帧图，作为下一段视频的起始帧参考，确保视觉连贯。

```
场景 1 视频 Prompt（≤15s）
    ↓（若场景 > 15s）
  快照图 Prompt @ 15s 处 → 生成参考图
    ↓
场景 1 视频 Prompt 续（下一段 ≤15s，以快照为起始帧）
    ↓
场景 2 视频 Prompt（≤15s）
    ↓（若场景 > 15s）
  快照图 Prompt @ 15s 处 → 生成参考图
    ↓
场景 2 视频 Prompt 续 ...
    ↓
场景 3 视频 Prompt（≤15s）
    ...
```

| 序号 | 时长 | 景别 | 镜头运动 | 动作概要 |
|------|------|------|----------|----------|
| 1 | {x}秒 | {大特写/特写/近景/中近景/全景/远景} | {运镜方式} | {一句话动作} |
| 2 | {x}秒 | ... | ... | ... |
| 3 | {x}秒 | ... | ... | ... |

#### 分镜视频 Prompt

按时间顺序输出。每场根据时长生成一个或多个视频 Prompt。**每条分镜视频 Prompt 不超过 2000 字。**

**场景 {N} 分镜视频 Prompt**（第 {M} 段，若有拆分）
- 开头（场景首段）：将根据附带的人物参考图、背景参考图，生成本段分镜视频
- 开头（快照续接段）：将根据附带的人物参考图、背景参考图、以及前一段快照参考图，继续生成本段分镜视频
- 内容：完整描述本段动作流程、景别、镜头运动（推近/拉远/跟拍/平移）、情绪变化
- 参数：时长（≤15s）、运镜速度、色调、氛围音效
- 画质标注：4K 超高清，镜头运动流畅，皮肤与场景真实质感，电影级光影，短视频风格
- 结尾：以人物参考图、背景参考图为全部参考生成视频（续接段则为：以人物参考图、背景参考图、快照参考图为全部参考生成视频）

#### 快照图 Prompt（15 秒边界处）

当某场超过 15 秒时，在视频段之间插入快照图 Prompt。快照描述该时刻的精确视觉状态，用于生成静帧图锚定下一段。

**快照图 Prompt（场景 {N}，{时间戳}秒）**
- 开头：本次将根据附带的人物参考图与背景参考图，仅生成 1 张快照画面，用于后续视频续接的起始帧参考
- 内容：精确描述此刻的景别、人物姿态/表情/位置、光线状态、道具位置
- 必须与前一段视频末帧完全一致
- 结尾：以附带的人物参考图和背景参考图为基准生成

#### Prompt 序列示例

以场景 1（10秒）+ 场景 2（20秒）+ 场景 3（15秒）= 总计 45 秒为例：

```
1. 场景 1 视频 Prompt         （0s–10s，≤15s，无需拆分）
2. 场景 2 视频 Prompt 第 1 段 （10s–25s，场景 2 前 15s）
3. 快照图 Prompt @ 25s        （场景 2 第 15 秒处的画面快照）
4. 场景 2 视频 Prompt 第 2 段 （25s–30s，剩余 5s，以快照为起始帧）
5. 场景 3 视频 Prompt         （30s–45s，恰好 15s，无需拆分）
```

#### 单场附加信息

每场还需提供：
- **观众所见**：2–3 句详细视觉描写
- **情绪/氛围**：观众应感受到什么
- **本场光线**：此刻的具体光线情况
- **关键运动**：什么在动、速度多快、方向如何

### 视觉风格

- **整体风格**：如"电影写实""风格化插画""动漫风"
- **参考质感**：摄影机/胶片参考，如"Arri Alexa 质感，浅景深"
- **色彩策略**：色彩如何随故事弧线变化
- **风格锚点**：{适用于所有镜头的可复用 Prompt 前缀，约 20 字}

### 音乐/音效方向

- **整体情绪**：曲风、节奏、乐器
- **弧线**：音频从头到尾如何演变
- **关键时刻**：哪些镜头需要音效强调——重击、静默、渐强

### 为何适合 AI 视频

- **传播角度**：{1–2 句}
- **AI 生成优势**：{此主题对 AI 来说容易在哪里}
- **复看/互动钩子**：{什么让观众评论、分享或循环播放}
```

**请用户选择一个**（或要求更多候选）。生成批量列表（如"找 10 个主题"）时，每个条目使用相同的详细格式。

### 第四步 — 制作基础分镜文档

用户确认主题后，生成完整分镜文档，包含：

1. **标题** — 中文标题
2. **简介** — 2–3 句概要 + 标签
3. **视觉圣经** — 风格、画幅、色彩组合、光线、情绪、人物、环境、风格锚点
4. **完整叙事** — 散文体故事，具体生动
5. **分镜表** — 逐镜头拆解，每镜包含：
   - 时长（以 15 秒为单位，可更短）
   - 景别与镜头运动
   - 动作描述
   - 音效/情绪备注
   - 向下一镜头的过渡
   - 生成 Prompt（复用视觉圣经原文）
6. **制作备注** — 总时长、镜头数、音乐情绪、关键一致性注意事项

参照 `ai_videos/` 中已有分镜文档的格式。

### 第五步 — 保存输出

分镜文档保存至：

```
ai_videos/{date}/{story_id}/story/storyboard.md
```

其中：
- `{date}` = 当天日期，格式 `YYYY-MM-DD`
- `{story_id}` = 由标题生成的短蛇形命名（如 `tornado_cat`、`code_world`）

调研资料保存至：

```
ai_videos/{date}/{story_id}/story/research.md
```

调研文件应包含：
- 使用的搜索关键词
- 原始候选列表及评分
- 选定主题的链接/来源
- 选择理由

## 输出规范

- 写分镜前必须先征得用户确认
- 必须包含 AI 可行性评分卡——不可跳过评分
- 不得声称 AI 能完美渲染任何主题——必须明确标注漂移风险
- 所有 Prompt 中复用人物/环境描述原文，禁止改写
- 以 15 秒为场景单位，适配 Seedance
- 默认 9:16 竖屏（移动端优先），除非用户另行指定
- 分镜文档是最终交付物——必须完整到下游工作流可直接提取分镜、人物、Prompt，无需重新调研
- **每条视频最多 1–2 个人物**——单人物优先；仅在互动必不可少时允许两人
- **全部输出使用中文**——整个 MD 文件（标题、小标题、描述、评分、备注、Prompt）必须为中文。仅 hex 色值和无标准中文对应的技术术语（如 4K、golden hour、DoF）可保留英文
- **所有生成 Prompt 必须为纯中文**，精准无歧义
- **分镜 Prompt 字数限制**：每条分镜视频 Prompt 不超过 2000 字。超出时压缩语言、合并冗余描述，但不可删减必要细节
- **禁用空泛形容词**：禁止使用"好看""唯美""漂亮"——替换为具体细节（如：柔和 golden hour 阳光、皮肤细腻毛孔、布料哑光质感）
- **同一人物/同一场景 = 所有 Prompt 细节完全统一**——不矛盾、不突变
- **参考图标注必须一致**——不遗漏、不改写
- **所有 Prompt 必须适配 Seedance 2**——面向图生图、帧间生成、视频生成工作流设计

## 边界情况

- 若无候选主题评分超过 40/60，如实告知并建议用户提供细分方向或约束条件以缩小搜索范围。
- 若用户直接提供主题，跳过第一至三步，直接进入评估 + 分镜。
- 若用户希望同一主题出短视频和长视频两个版本，分别生成两套分镜。
- 默认模式为**短视频**，除非用户另行指定。
