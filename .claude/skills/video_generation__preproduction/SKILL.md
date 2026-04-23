---
name: video_generation__preproduction
description: Lock the four series-level bibles (character / scene / style / voice) plus the anchor registry for a Chinese serialized 短剧 AI-video project. Use this when starting a new `series/{name}/` series, when adding a new recurring character or scene mid-series, or when any downstream skill reports a missing anchor. Outputs are the source-of-truth for every downstream Seedance prompt and every TTS synthesis call — they must be locked before storyboarding or packaging can begin.
---

# 预制作锁定 · Preproduction — 系列级四圣经 + 锚点注册表

把系列的视觉身份、环境身份、风格身份、声线身份一次性锁定到四份圣经里，并登记可在下游 Prompt 中原文替换的锚点清单。**所有下游 Seedance Prompt / 剪辑字幕 / TTS 合成都只从这里读取原文。**

## Modes

- **初始化模式 (bootstrap)** — 新系列首次锁定。读 `series/{name}/episodes/ep_001.md`（由 `serial-novelist` 先写）+ `series/{name}/research/reference_pack.md`（由 `reference-scout` 先写），生成全部 4 份圣经 + `anchor_registry.md`，把 `status.md` 置为 `bibles: LOCKED`。
- **增量锁定模式 (incremental)** — 已锁定系列新增一个常驻角色或场景。只追加该锚点；不允许修改既有锚点的 `复用片段` 原文（需 `status.md` 版本号递增 + 兼容影响说明）。

## Workflow

### Step 1 — 读入上游

必读：

- `series/{name}/episodes/ep_001.md`（bootstrap）或 `episodes/ep_{latest}.md`（incremental）
- `series/{name}/research/reference_pack.md`
- `series/{name}/status.md`

如缺任一项：中止并提示上游 skill 先运行。

### Step 2 — 身份清册

列出本系列会反复出现的：

- **核心角色**：上限 2–3 个（Q8a）。`大男主` 强制 1 个；女配 1 个；师父 / 反派 / 系统 三选一共 1 个。第 4 个角色请求 → 拒绝并解释。
- **常驻场景**：2–5 个（宗门大殿 / 荒原 / 酒楼 / 闺房 / 战场之类）。
- **风格锚点**：整套系列共 1 条 20 字左右的可复用 Prompt 前缀。
- **声线锚点**：每个核心角色 1 条 TTS 配置（引擎 + voice_id + 语速 + 音调 + 情感范围）。

### Step 3 — 写 `bibles/character_bible.md`

沿用 `video_generation__topic-scout` 的 **3D 三视图规范**（正面 / 侧面 / 背面）。每个角色必须完整写出以下全部字段：

- **名称 / 角色**：中文全名 + 角色定位（男主 / 女主 / 反派 / 师父 / 系统）
- **基础信息**：年龄 / 性别 / 民族 / 身高 / 体型
- **五官细节**：眉 / 眼 / 鼻 / 唇 / 脸型 / 肤色 / 肤质 / 妆容
- **发型细节**：发色（hex）/ 长度 / 造型 / 发丝质感
- **穿搭细节**：上衣 / 下装 / 鞋子 / 配饰，逐件写材质、颜色（hex）、花纹、版型
- **神态细节**：眼神 + 面部表情（贴合角色定位的默认情绪）
- **肢体姿态**：站姿 / 坐姿 / 手持道具
- **随身道具**：令牌 / 剑 / 折扇 / 系统面板 之类
- **肢体语言**：走路方式 / 精力状态
- **弧线**：从首集到大致 ep_20 的外貌 / 表情变化方向（纯爽文不允许低谷，仅允许气场递增）
- **参考说明**：末尾逐字复用 —— `以附带的 3 张人物三视图参考图为基准生成 3D 人物模型`
- **画质要求**：末尾逐字复用 —— `4K 超高清，电影级光影，真实质感，全身无裁切，纯白背景便于模型提取`
- **复用片段**：**20–40 字**，一条句子密度的身份锚。下游所有 Prompt 原文粘贴，禁止改写一个字符。

**复用片段示例（战神归来型）**：
> 男主叶无极，28 岁，身形挺拔颧骨分明，右眉有一道浅疤，身穿洗旧玄青长衫腰悬玄天剑令，眼神沉静压得住场。

### Step 4 — 写 `bibles/scene_bible.md`

每个常驻场景生成 **3 张视角**（远景 + 近景 + 特写，或 正 + 侧 + 俯），严格同场景细节统一。字段清单：

- **名称**：场景短标签（如 `青云宗大殿`）
- **场景信息**：在系列中的用途（开场亮身份 / 打脸舞台 / 感情戏转场）
- **环境设定**：地点类型 / 时间段 / 季节 / 天气
- **环境细节**：室内 / 室外 / 材质 / 颜色 / 状态
- **关键元素**：3–5 个定义该环境的必备视觉元素
- **道具细节**：每件道具位置 + 材质 + 颜色 + 纹理
- **色彩组合**：3–4 种主色调（hex）
- **光影细节**：光源类型 / 角度 / 效果（柔光 / 逆光 / 阴影）/ 色温
- **氛围色调**：情绪 + 暖 / 冷 / 高 / 低饱和
- **氛围效果**：雾气 / 微粒 / 体积光 / 灰尘 / 雨水
- **空间感 / 纵深**：宏大 vs 亲密
- **声音印象**：观众会听到什么（给 TTS + 音效留勾子）
- **参考说明**：逐字复用 —— `以附带的 3 张不同视角背景参考图为基准搭建 3D 场景`
- **画质要求**：逐字复用 —— `4K 超高清，极致细节，真实质感，无人物仅场景道具，电影级氛围`
- **复用片段**：20–40 字，原文粘贴使用

**复用片段示例（青云宗大殿）**：
> 青云宗大殿，青玉地砖映晨光，殿顶铜灯垂九盏，两侧列六十二张白玉座，香烟缭绕如薄雾。

### Step 5 — 写 `bibles/style_bible.md`

单文件单章，锁定全系列视觉语法：

- **整体风格**：如 `电影写实 · 古风厚重`
- **摄影机参考**：如 `Arri Alexa 浅景深，偏仿胶片颗粒`
- **色彩策略**：主调 hex 3–4 条 + 如何随剧情弧线变化（纯爽文建议：亮面稳定，反派出场加冷蓝压色）
- **灯光法则**：主光源 + 辅光 + 轮廓光 基调
- **镜头语言白名单**：`景别` 必须从 `大特写 / 特写 / 近景 / 中近景 / 全景 / 远景` 选；`运镜` 必须从 `推近 / 拉远 / 跟拍 / 平移 / 环绕` 选
- **负向禁忌**：`禁用空泛形容词：好看 / 唯美 / 漂亮 / 大气`
- **风格锚点**（≈20 字）：全系列所有 Prompt 顶部逐字拼接的前缀

**风格锚点示例**：
> 电影级古风写实，冷调偏青，浅景深仿胶片颗粒，稳定主光含逆光轮廓。

### Step 6 — 写 `bibles/voice_bible.md`

每个核心角色一段，字段清单：

- **角色ID**：与 `character_bible.md` 一致的短标签（如 `male_lead`）
- **中文全名**：`叶无极`
- **默认引擎**：`volcengine` / `minimax` / `iflytek` 三选一
- **voice_id**：
  - Volcengine：常用男主 `BV119_streaming`（通用赘婿）、`BV107_streaming`（霸气青叔）、`BV158_streaming`（智慧老者 · 师尊）
  - Volcengine 常用女配：`BV115_streaming`（古风少御）、`BV034_streaming`（知性姐姐）、`BV113_streaming`（甜宠少御）
  - Volcengine 旁白：`BV142_streaming`（沉稳解说男）
  - MiniMax（旁白优先，可克隆）：`Chinese (Mandarin)_Reliable_Executive` / `Chinese (Mandarin)_Male_Announcer` / 自有 `moss_audio_<uuid>`
  - iFlytek（古风生僻字兜底）：平台 `超拟人 x4` 系列 voice_id
- **语速**：`speed_ratio` `0.8–1.2`（古风偏慢 0.9 更稳）
- **音调**：`pitch_ratio` `0.9–1.1`
- **默认情感**：`neutral` / `happy` / `angry` / `sad` / `surprised` / `calm` 按角色定位锁定
- **情感范围**：列出允许的波动标签（纯爽文男主建议 `neutral → calm → angry`，不使用 `fearful` / `sad`）
- **音素提示**：列出该角色专属名字 / 招式 / 法器中的 多音字 pinyin 修正（例：`觉=jué`、`璟=jǐng`、`砚=yàn`、`曜=yào`）
- **SSML 模板**：一条可直接喂 TTS 的最小 SSML 骨架，含 `<prosody>` + `<break>` 典型用法

**旁白另立一节**（`narrator:` ID），为全系列通用解说音。

### Step 7 — 写 `bibles/anchor_registry.md`

单张三列表，下游 skill 只读它做锚点解析：

| 锚点 | 类型 | 指向 |
|---|---|---|
| `{{character:male_lead}}` | character | `bibles/character_bible.md#男主-叶无极` 的 **复用片段** |
| `{{character:male_lead.front}}` | character_view | 同上 + 限定 `正面` 视角段 |
| `{{character:male_lead.side}}` | character_view | `侧面` |
| `{{character:male_lead.back}}` | character_view | `背面` |
| `{{scene:qingyun_hall}}` | scene | `bibles/scene_bible.md#青云宗大殿` 的 **复用片段** |
| `{{scene:qingyun_hall.far}}` / `.near` / `.closeup` | scene_view | 对应视角段 |
| `{{style:anchor}}` | style | `bibles/style_bible.md` 的 风格锚点 整段（≈20 字） |
| `{{voice:male_lead}}` | voice | `bibles/voice_bible.md#男主-叶无极` 的 voice_id + 参数 |
| `{{voice:narrator}}` | voice | 旁白条 |

所有锚点必须 **全部可解析**；新增 / 删除锚点必须同一次 commit 同步更新本文件。

### Step 8 — 锁定 + 登记

- 把 `status.md` 的 `bibles` 字段置为 `LOCKED`，记 `locked_at: YYYY-MM-DD` + `locked_by: preproduction` + `version: v1`。
- 增量模式：版本号 +1，追加 `CHANGELOG` 条目说明新增的锚点名 + 原因。
- 打印本次锁定摘要给用户：角色数、场景数、风格锚点长度、声线引擎分布。

## Inputs

- `series/{name}/episodes/ep_001.md`（bootstrap）或最新 `ep_{N}.md`（incremental）
- `series/{name}/research/reference_pack.md`
- `series/{name}/status.md`

## Outputs

- `series/{name}/bibles/character_bible.md`
- `series/{name}/bibles/scene_bible.md`
- `series/{name}/bibles/style_bible.md`
- `series/{name}/bibles/voice_bible.md`
- `series/{name}/bibles/anchor_registry.md`
- 更新后的 `series/{name}/status.md`

## 输出规范

- **全部中文**；仅 hex 色值 / `4K` / `golden hour` / `DoF` / `voice_id` 型号保留英文。
- **逐字复用原则**：`复用片段` / `风格锚点` / TTS 参数一旦写入，下游必须按字节原文粘贴；禁止同义改写。
- **身份上限 2–3 个核心角色**（Q8a）。超过直接拒绝。
- **角色弧线不允许低谷**（Q6d 纯爽文）。弧线只允许气场 / 身份 / 实力递增。
- **风格锚点 ≈20 字**（≥15 ≤25）。过短则锚定力不足，过长挤占 Prompt 预算。
- **禁用空泛形容词**：`好看 / 唯美 / 漂亮 / 大气 / 震撼 / 炸裂` 触发强制重写。
- **锚点命名**：`{{<type>:<snake_case_id>}}` 或 `{{<type>:<id>.<view>}}` 两种形态，与本 skill Step 7 表格一一对应，不得发明新语法。
- **声线与视觉解耦**：`voice_bible.md` 是独立文件，禁止把声线写进 `character_bible.md`。

## 边界情况

- 用户请求第 4 个核心角色 → 拒绝并回提 Q8a 规则；建议合并或轮换。
- 用户要求改已锁定角色的 `复用片段` → 拒绝；提示走 `增量锁定` 并版本号 +1 + 追加 CHANGELOG。
- 引用了 `bibles/` 里还不存在的锚点 → 中止并列出缺失锚点清单。
- 风格锚点与 `reference_pack.md` 的视觉基调冲突 → 给出并列对比表让用户裁决，不自动二选一。
- `ep_001.md` 尚未存在 → 直接指回 `video_generation__serial-novelist` 的 `新系列启动模式`。

## Invocation examples

- 「给 `series/战神归来/` 做 bootstrap 预制作，男主是叶无极，女配是苏婉。」
- 「往 `series/剑尊重生/` 增量锁定一个常驻反派 `血煞老祖` + 一个新场景 `万骨冢`。」
- 「只刷新 `voice_bible.md` —— 我换用 MiniMax 克隆的旁白。」
