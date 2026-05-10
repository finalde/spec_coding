# Angle — prompt-pipeline

Run: mozun_chongsheng-20260509-164205
Stage: 3 (research)
Researcher: researcher-04-prompt-pipeline
Date: 2026-05-09

## 1. 本角度覆盖范围

针对《魔尊归来》60 集 × 1.5 min × 9:16 双管线 prompt 项目，回答下列实操问题，使 stage 4 spec 与 stage 6 execution 可以直接复用模板：

- Kling 2.1 Pro（image-to-video，含立绘 ref + start/end 双帧）的 prompt 字段、负向 prompt、时长、画幅约束。
- Seedance 1.0 Pro（text-to-video）的 prompt 公式、字段、时长、画幅、相机词汇、负向支持情况。
- Seedream（v4.0 / v4.5 / v5.0，文生图）的中文 prompt 结构，用于 9 份角色立绘 + 每镜 seam-frame 静帧。
- image-to-video vs text-to-video 在 prompt 写法上的关键差异（"只描述运动" vs "全场景描述"）。
- 1 个仙侠完整 worked example：开场雷劫坠落 → 重生乞丐镜头组的 Kling + Seedance + Seedream 三套 prompt。

不覆盖：渲染成本估算、平台 API 调用代码、stitching / ffmpeg concat 流程（属 angle-postprod）。

## 2. 关键发现

### 2.1 Kling 2.1 Pro — image-to-video（含 start/end frame）

引用：fal.ai 官方页面 [Kling 2.1 Pro Image-to-Video](https://fal.ai/models/fal-ai/kling-video/v2.1/pro/image-to-video)、Leonardo.ai 文档 [Generate with Kling 2.1 Pro Using Start and End Frame](https://docs.leonardo.ai/docs/generate-with-kling-21-pro-using-start-and-end-frame)、Ambience AI [Kling Prompt Guide](https://www.ambienceai.com/tutorials/kling-prompting-guide)、官方 dev portal [Kling Image-to-Video API](https://app.klingai.com/global/dev/document-api/apiReference/model/imageToVideo)、ImagineArt [Kling 2.1 Prompt Guide](https://www.imagine.art/blogs/kling-2-1-prompting-guide)。

| 字段 | 类型 | 取值 | 备注 |
|---|---|---|---|
| `prompt` | string | 中文/英文均可 | image-to-video 模式只写"运动 + 镜头变化"，不要重复描述图中已有内容 |
| `image_url` | string | URL | 起始帧。**Kling 2.1 Pro 必须有 start frame**（Leonardo.ai 明确说明） |
| `input_image_urls` | array | up to 4 张 | 多帧约束，本项目用作 `[start_frame, end_frame]` 两帧锚定 |
| `negative_prompt` | string | 词组列表 | 默认建议词：`blur, distortion, watermark, text overlay, low quality, compression artifacts, flickering, inconsistent lighting, morphing faces, extra limbs, unnatural physics`（来自 Ambience AI） |
| `duration` | string | `"5"` 或 `"10"` | 仅两档；本项目按 Q4.x 共识取 8–10 秒，统一选 **10** |
| `aspect_ratio` | string | `"16:9"`/`"9:16"`/`"1:1"` | 本项目锁 `"9:16"`（1080×1920）|
| `cfg_scale` | number | 0–1，默认 0.5 | 越高越严格遵守 prompt，越低越有创意 |
| `mode` | string | `pro` | 1080p@30fps |

**关键差异（image-to-video 写法）：** 来自 fal.ai / Ambience AI 的反复强调——image-to-video 模式下 **prompt 只写运动指令**，不要再描述图里已有的脸/服饰/场景，否则模型会"漂移"。例如不写"黑袍魔尊站在云端，镜头推近"，而是只写"镜头缓慢推近，黑袍下摆被雷气吹动，背景闪电由远及近"。这是 stage 6 模板的**最大陷阱**，必须在 spec 中明确标注。

**start + end frame 双帧契约：** Kling 2.1 Pro 接受 `input_image_urls` 数组（最多 4 张）。本项目按 `agent_refs/project/ai_video.md` 规则 11 的 seam-frame 工作流，将每镜的 `[shot{N-1}_lastframe.png, shot{N}_lastframe.png]` 作为双帧输入 → 镜头首尾被钉死，stitch 不漂移。

### 2.2 Seedance 1.0 Pro — text-to-video

引用：ByteDance 官网 [Seedance 1.0](https://seed.bytedance.com/en/seedance)、ByteDance ModelArk 文档 [Seedance-1.0-lite Prompt Guide](https://docs.byteplus.com/en/docs/ModelArk/1587797)、Atlabs AI [Ultimate Seedance 1 Pro Prompting Guide](https://www.atlabs.ai/blog/ultimate-seedance-1-pro-prompting-guide)、AIML API [Seedance 1.0 pro Text-to-Video](https://docs.aimlapi.com/api-references/video-models/bytedance/seedance-1.0-pro-text-to-video)、Replicate [ByteDance Seedance 1 Pro](https://replicate.com/bytedance/seedance-1-pro)。

**官方 prompt 公式（Atlabs AI 整理）：** `[Subject] + [Action] + [Composition] + [Style]`，字段拆解：

1. **主体（Subject）** — 详尽人物 / 物体描述。本项目对每个角色复用 `qa.md` 锁定的"中文描述符" byte-identical（与 Kling 同一份）。
2. **动作（Action）** — 用具体电影化动词，避免 "walks/sits"，改用 "踉跄前行 / 凝立 / 衣袂翻飞"。
3. **构图（Composition）** — 景别 + 机位（远景 / 中景 / 特写 / POV / 牛仔镜头）。
4. **相机运动（Camera）** — Seedance 官方支持自然语言描述，关键词：**环绕（surround）/ 航拍（aerial）/ 推拉（zoom）/ 平移（pan）/ 跟随（follow）/ 手持（handheld）/ 切换（cut）**（来自 Atlabs AI + ByteDance ModelArk）。
5. **镜头与焦距（Lens & Focus）** — anamorphic / 浅景深 / 深景深 / rack focus / 广角。
6. **风格（Style）** — photorealistic / 概念画 / 仙侠水墨 / 黑金沉郁电影感 等（本项目固定写"传统仙侠 × 黑金沉郁电影感"）。
7. **光线（Lighting）** — volumetric / golden hour / 高对比 / chiaroscuro / 霓虹。

**技术参数：**
- `duration`: 3–12 秒（比 Kling 范围广，本项目仍统一 10 秒以匹配 Kling）
- `aspect_ratio`: 1:1, 3:4, 4:3, 16:9, **9:16**, 21:9, 9:21（本项目 9:16）
- `resolution`: 480p–1080p（本项目 1080p）
- prompt 语言：**中英文均支持**（ByteDance ModelArk 明确）

**负向 prompt：** Atlabs AI 教程未提及 Seedance 支持负向字段；Replicate API schema 也只暴露 `prompt` + 参数，**Seedance 1.0 Pro 当前公开 API 不支持独立 `negative_prompt` 字段**。规避词需要前置写进主 prompt 末尾，例如 `…画面无水印、无文字 overlay、无变形手指`。

**与 Kling 的关键差异：**

| 维度 | Kling 2.1 Pro (image-to-video) | Seedance 1.0 Pro (text-to-video) |
|---|---|---|
| 输入 | 起始帧 image + 文本 prompt | 仅文本 prompt |
| 文本 prompt 内容 | **只写运动**，不描述图中已有元素 | **全场景描述**（主体+动作+构图+风格+光线），无图可参 |
| 角色一致性 | 由参考图锁定（强） | 仅靠中文锁定描述符（弱，本项目以 byte-identical 文本兜底） |
| 时长 | 5 / 10（仅两档） | 3–12（连续） |
| 负向 prompt | 独立字段 | 无独立字段，需前置入主 prompt |
| 画幅 | 16:9 / 9:16 / 1:1 | 7 种（含 9:16）|

### 2.3 Seedream（4.0 / 4.5 / 5.0）— 文生图，立绘 + seam-frame

引用：[Seedream 5.0 上线分析](https://www.80aj.com/2026/02/10/seedream-ai-chinese-art/)、[Seedream 4.0 知乎技术解读](https://zhuanlan.zhihu.com/p/1948805126555932049)、[Seedream 4.0 智源社区](https://hub.baai.ac.cn/view/48845)、[Seedream 4.5](https://seed.bytedance.com/en/seedream4_5)、ByteDance [Seedream 3.0 技术报告](https://seed.bytedance.com/en/blog/seedream-3-0-text-to-image-model-technical-report-released)。

**关键能力（来自 Seedream 4.0 / 5.0 公开材料）：**

1. **中文原生**——Seedream 5.0 强调"对中文 prompt 友好，能精确理解自然语言"，本项目全程中文。
2. **角色一致性**——Seedream 4.0 可"提取参考图关键信息（身份、风格、结构特征）并在多次生成中保持"。这是 9 份立绘的核心能力支撑。
3. **多图融合 / 4K 直出**——Seedream 4.0 支持多图融合 + 4K，分辨率不再是瓶颈。
4. **2D → 3D 立绘**——Seedream 4.0 可将 2D 线稿转 3D 渲染立绘并自动补全背 / 侧视图。本项目 9 份立绘可以一次产出三视图。

**Seedream prompt 推荐字段（综合社区教程归纳，无单一官方模板）：** 主体 / 角色身份 / 服饰 / 发型 / 体型 / 表情 / 姿势 / 场景 / 光影 / 风格 / 比例。本项目固定使用下列 6 段式（与 ai_video.md 规则 4 + 规则 11 对齐）。

**负向 prompt：** Seedream 公开材料未明确支持独立负向字段，建议像 Seedance 一样前置入主 prompt 末尾。

## 3. 对 spec 的具体建议

### (a) Kling prompt 模板（每镜 `prompts/shot{NN}_kling.md` 骨架）

```markdown
# shot{NN} — Kling 2.1 Pro · image-to-video

## 输入参考帧（input_image_urls，按 agent_refs/project/ai_video.md 规则 11）

- start_frame: prompts/shot{N-1}_lastframe.png   # shot01 取 shot01_startframe.png
- end_frame:   prompts/shot{NN}_lastframe.png

## 角色锁定（byte-identical 复用 characters/{role}.md 中的"锁定中文描述符"）

{role_descriptor}

## prompt（只写运动 + 镜头变化，不重复描述图中已有元素）

镜头：{景别 + 运动，例如"中景缓慢推近 → 特写"}
动作：{0–10s 内可完成的连贯动作，例如"主角缓缓抬手，掌心黑气凝聚成漩涡"}
光线/色调：{匹配 style_guide.md，例如"主光由侧后打来，金边轮廓 + 黑金沉郁主调，高光仅落在掌心黑气"}
节奏：{慢推 / 快切 / 定格 / 360 环绕}

## negative_prompt

模糊, 形变, 水印, 文字, 低画质, 压缩失真, 闪烁, 多余手指, 多余四肢, 面部漂移, 不合理物理

## 参数

- model: KLING2_1, mode: pro
- duration: 10
- aspect_ratio: 9:16
- resolution: 1080p
- cfg_scale: 0.5
```

### (b) Seedance prompt 模板（每镜 `prompts/shot{NN}_seedance.md` 骨架）

```markdown
# shot{NN} — Seedance 1.0 Pro · text-to-video

## 角色锁定（byte-identical，与 Kling 同源 characters/{role}.md）

{role_descriptor}

## prompt（4 段式：主体 + 动作 + 构图 + 风格 ＋ 光线）

主体：{完整人物 + 服饰 + 表情；引用上方角色锁定}
动作：{电影化动词，例如"魔尊单膝跪地，黑袍下摆被九重雷劫卷至背后猎猎作响"}
构图：{景别 + 机位，例如"中景，机位略低，平视主角胸口"}
相机：{Seedance 官方词汇——环绕 / 航拍 / 推拉 / 平移 / 跟随 / 手持 / 切换}
镜头/焦距：{广角 / 浅景深 / anamorphic / rack focus}
风格：传统仙侠 × 黑金沉郁电影感（与 style_guide.md 一致）
光线：{volumetric / golden hour / 高对比侧光 / chiaroscuro 等}
规避：画面无水印、无文字 overlay、无变形手指、无多余四肢、无面部漂移

## 参数

- duration: 10
- aspect_ratio: 9:16
- resolution: 1080p
```

### (c) Seedream 立绘 prompt 模板（`characters/ref_images/{role}_seedream.md`，9 份）

```markdown
# {role} — Seedream 立绘 prompt（一次性，多镜头 ref 复用）

## 主体身份

{角色姓名} · {一句话定位，例如"前世魔尊，本卷为转生乞丐少年"}

## 外貌锁定（byte-identical 写入 characters/{role}.md "锁定中文描述符"，跨所有镜头复用）

- 年龄：{16–18 / 25–30 / ...}
- 发型：{长发披肩 / 半绾墨发 / 灰白乱发 / ...}
- 瞳色：{暗金 / 朱砂红 / 墨青 ...}
- 体型：{清瘦 / 颀长 / 魁梧 ...}
- 服饰：{黑金祥云暗纹长袍 / 灰白破布短褐 / 米白广袖法袍 ...}
- 配饰：{乌玉发冠 / 麻绳腰带 / 玄铁护腕 ...}
- 表情基调：{冷峻含威 / 隐忍不甘 / 慈眉伪善 ...}

## 姿势 / 视图

- 三视图（正面 / 侧面 / 背面），居中站立，全身入画
- 留白背景或纯黑黑金渐变背景，无道具干扰

## 风格

传统仙侠 × 黑金沉郁电影感；写实人像 + 微国风线条；4K 直出

## 比例 / 规避

- 比例：9:16（与视频一致，便于贴脸合成）；如需三视图横排可临时取 16:9 仅用于角色档
- 规避：水印、文字、多余手指、面部漂移、卡通化变形
```

### (d) Seedream seam-frame prompt 模板（`prompts/shot{NN}_lastframe_seedream.md`，每镜一份；shot01 多一份 startframe）

按 `agent_refs/project/ai_video.md` 规则 11，6 段式：

```markdown
# shot{NN} 末帧 — Seedream 静帧 prompt

## 1. 主体定义（冻结瞬间的全场景）

{该帧定格时刻的角色 + 环境 + 道具位置 + 光线状态，例如"魔尊单膝跪地于九重雷劫核心，左手撑地，右手紧握碎裂魔气，背后云海被金色雷光割裂"}

## 2. 角色（byte-identical 复用 characters/{role}.md 中的锁定描述符）

{role_descriptor}

## 3. 场景 / 镜头 / 光线（与对应视频镜头的 prompt 中"场景:"/"光线/色调:" 字段同 token）

场景：{world.md 中的命名地点，例如"九重雷劫云海中心"}
镜头：{景别 + 机位，与视频 prompt 同}
光线/色调：{黑金沉郁主调 + 金色雷光高光 + 深青云雾点缀；hex 引用 style_guide.md}

## 4. 姿态（冻结瞬间的精确姿势）

{角色精确姿态 + 镜头精确角度 + 光线精确状态，例如"主角右膝着地，左掌按地震出灰尘，仰角 15°，雷光从画面右上 45° 切入"}

## 5. 比例

9:16

## 6. 负向

水印、文字、多余手指、多余四肢、面部漂移、卡通变形、模糊、低画质
```

### (e) Worked example — ep01 shot01 "魔尊雷劫坠落 → 重生为乞丐"

下面给出**同一个镜头**的 Kling + Seedance + Seedream 三套完整 prompt，stage 4 / stage 6 可直接复用为模板 fixture。

#### 角色锁定描述符（先在 `characters/main_mozun.md` 写一次，下文复用 byte-identical）

```text
苍冥 · 前世魔尊形态：
年龄约 30，颀长清瘦，墨色长发半绾以乌玉发冠束起，余发散落胸前；
瞳色暗金内敛，眉峰极锐，唇色偏冷；
身着黑金祥云暗纹广袖长袍，玄铁护腕，腰悬未鞘魔剑（剑柄缠暗红丝绦）；
表情冷峻含威，举止凝然不动如临深渊。
```

#### `episodes/ep01/prompts/shot01_startframe_seedream.md`（绝对开篇帧）

```text
# 1. 主体定义
九重雷劫云海中心，魔尊苍冥独立于一道金色雷光投下的云海高台之上，黑袍立威，
背景万千金色雷弧由远及近交织如蛛网，深青云雾盘绕脚下。

# 2. 角色
{粘贴上方"苍冥 · 前世魔尊形态"全部 6 行 byte-identical}

# 3. 场景 / 镜头 / 光线
场景：九重雷劫云海中心（world.md §雷劫云海）
镜头：中远景，仰角 10°，主角占画面下三分之一，云海与雷光占上三分之二
光线/色调：黑金沉郁主调（黑 #0a0a0a 70%，护黄金 #a8842c 20%，深青 #1a3038 8%，米白 #f5f5f0 仅雷光高光 2%）

# 4. 姿态
主角双足并立、双手负后，长发与广袖被气流向后吹起约 15°，眼神平视画面右前方，下颌微抬。

# 5. 比例
9:16

# 6. 负向
水印、文字、多余手指、面部漂移、卡通化、模糊、低画质
```

#### `episodes/ep01/prompts/shot01_lastframe_seedream.md`（雷劫击中末帧）

```text
# 1. 主体定义
魔尊苍冥被九重雷劫合击命中，单膝跪地于龟裂的云海高台中心，
长袍焦黑、左袖断裂，魔剑横落身侧三尺，金色雷弧仍在皮肤表面流窜。

# 2. 角色
{byte-identical 重贴"苍冥 · 前世魔尊形态"}

# 3. 场景 / 镜头 / 光线
场景：九重雷劫云海中心（world.md §雷劫云海）
镜头：中景，机位与 startframe 完全一致（仰角 10°，9:16 对齐）
光线/色调：与 startframe 同色板，唯雷光高光占比由 2% 升到 6%（剧情高潮）

# 4. 姿态
左膝着地、右掌撑地，背部前倾约 30°，长发散落遮去半张脸，露出右眼一道暗金锐光；
镜头角度与 startframe 严格一致以保证 Kling 双帧对齐。

# 5. 比例
9:16

# 6. 负向
水印、文字、多余手指、面部漂移、卡通化、模糊、低画质
```

#### `episodes/ep01/prompts/shot01_kling.md`

```markdown
# ep01 / shot01 — Kling 2.1 Pro · image-to-video

## 输入
- input_image_urls: [shot01_startframe.png, shot01_lastframe.png]

## 角色锁定（byte-identical）
{粘贴"苍冥 · 前世魔尊形态" 6 行}

## prompt（只写运动）
镜头：从中远景缓慢推近至中景，仰角保持 10°，9:16 不变。
动作：九重金色雷弧由四面云海聚拢，于第 4 秒在主角头顶汇聚成蛛网状合击；
主角先抬手运魔剑迎击（第 0–4s），剑光与雷弧短暂胶着（第 4–6s），
之后主角被合力压垮，单膝跪地，长袍焦黑、剑横落身侧（第 6–10s 收末帧）。
光线/色调：黑金沉郁主调，雷光高光占比由 2% 渐至 6%。
节奏：前 4s 慢推蓄势，4–6s 短促胶着，6–10s 缓慢压低落定。

## negative_prompt
模糊, 形变, 水印, 文字, 低画质, 压缩失真, 闪烁, 多余手指, 多余四肢, 面部漂移, 不合理物理

## 参数
model: KLING2_1, mode: pro, duration: 10, aspect_ratio: 9:16, resolution: 1080p, cfg_scale: 0.5
```

#### `episodes/ep01/prompts/shot01_seedance.md`

```markdown
# ep01 / shot01 — Seedance 1.0 Pro · text-to-video

## 角色锁定（byte-identical）
{粘贴"苍冥 · 前世魔尊形态" 6 行}

## prompt（4 段式）
主体：魔尊苍冥（见上方角色锁定），独立于九重雷劫云海中心的龟裂高台之上。
动作：先抬腕拔魔剑迎击四方汇聚的金色雷弧，剑光与雷网短暂胶着，
最终被合力压垮单膝跪地，长袍焦黑、长发散落遮面，右眼露出一道暗金锐光。
构图：中远景缓推至中景，仰角 10°，主角占画面下三分之一，雷光与云海占上三分之二。
相机：缓慢跟随推近（dolly-in），第 6 秒后改为定机轻微手持。
镜头/焦距：浅景深，雷光位为景深落点。
风格：传统仙侠 × 黑金沉郁电影感（参 style_guide.md）。
光线：黑金沉郁主色板（黑 70% / 护黄金 20% / 深青 8% / 米白雷光 2→6%），高对比 chiaroscuro 侧光。
规避：画面无水印、无文字、无变形手指、无多余四肢、无面部漂移、无卡通化。

## 参数
duration: 10, aspect_ratio: 9:16, resolution: 1080p
```

## 4. 开放问题

1. **Kling 2.1 Pro 中文 prompt 长度上限** — 公开 API 文档未给出明确字符数；建议 stage 4 spec 把每镜 prompt 控制在 ~500 中文字以内（Atlabs AI 建议 Seedance 主 prompt < 800 token），并在 stage 6 第一集做实测后回填到 ai_video.md 规则 4。
2. **Seedance 1.0 Pro 是否能支持负向字段** — 当前公开 API 仅暴露主 prompt，本研究采用"前置入主 prompt"兜底；如未来版本开放 `negative_prompt`，需更新模板 (b) 与所有 stage 4 输出。
3. **Seedream 立绘 → Kling 双帧的对齐策略** — 立绘是 9:16 单人居中，开篇 shot01 startframe 是带场景的全景，两者并非同一构图，是否需要一道"立绘 → 场景化首帧"的中间 Seedream pass？建议 stage 4 验证后定型；当前 worked example 假定 Seedream 直接产场景化首帧，立绘只是 byte-identical 描述符的视觉锚（验证之后可能升级为"立绘 → 场景化首帧" 2-pass）。
4. **Kling vs Seedance 选择策略** — 双管线产出后，stage 6 用什么客观标准选 keep？建议 stage 5 validation 给一个评估表（角色一致性 / 动作流畅度 / 黑金色板还原 / 雷光物理感 4 项打分）。这超出本角度，移交 angle-validation。
5. **Seedream 版本选择（4.0 vs 4.5 vs 5.0）** — 5.0 中文友好度更高、5.0 Lite 支持单参考图直接套风格，但本项目 60 集 × 9 角色 × 多 seam-frame 量级巨大，5.0 是否在量级上经济需 stage 5 / stage 6 验证。当前模板对三版本都兼容（同一份中文 prompt 字段）。
