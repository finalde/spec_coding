# Final spec — mozun_chongsheng

Run: mozun_chongsheng-20260509-164205
Stage: 4 (spec compilation)
Inputs consumed: `user_input/{raw,revised}_prompt.md`, `interview/qa.md`, `findings/dossier.md` + 5 angle-*.md
Mode: AUTONOMOUS

## Goal

制作一部 AI 驱动的中文 **仙侠 × 重生复仇 × 系统流 × 多女主** 短剧《魔尊归来》（task_name: `mozun_chongsheng`）。**60 集 × ~90 秒 / 集**（总片长 ~ 90 分钟），9:16 竖屏，发布于 **抖音 + YouTube Shorts**。每集 ~10 镜头，每镜 8-10 秒；每镜双管线产出（Kling image-to-video + Seedance text-to-video）+ 每镜 Seedream 末帧立绘 + 每集首镜 Seedream 首帧立绘 + 9 个核心角色 + 男主乞丐形态共 10 份 Seedream 角色立绘。

故事核心一句话："**渡劫后顶层修为的魔尊沧冥被五大宗主『正道盟』联手镇压，魂魄重生于乞丐少年叶无尘体内（满记忆 / 零修为），靠系统任务 + 三女主双修 + 药王谷丹药三轨缓慢恢复，最终杀回正派大本营揭穿伪君子并归位。**"

## Out of scope (v1)

- **音频 prompt**（v1 仅产出视觉 prompt；音频 / 配音 / BGM 后期人工接入）
- **真实渲染 / 剪辑 / 后期**（pipeline 仅产出 prompt 文本与 Seedream 立绘 prompt；用户自行去 Kling / Seedance / Seedream 平台渲染）
- **多语言版本**（v1 仅中文 + YouTube Shorts 双语标题；其他语种 v2 follow-up）
- **付费分成 / 备案号 / 上架审核流程**
- **真人配音脚本 / 音乐版权**
- **跨镜头 LUT 一致性 / AE 复合特效**（划归后期）
- **v2 二季制作**（仅在 ep60 final shot 留两个版本：单季 ending vs 二季钩 open ending；具体二季内容 v2 follow-up）
- **抖音封面投流投放策略**（pipeline 给出封面 prompt 模板，但实际 A/B 测试与投放由用户运营）
- **超过 ep05 的详细 episode/shotlist/prompts**（按 ai_video.md 规则 2，detail_batch_size=5；ep06-ep60 在 arc_outline.md 留单行大纲，由后续 stage-4 regen 按 5 集为一批扩展）

## User roles & primary flows

**唯一角色**：项目创作者（用户本人，本地运行 pipeline，产出 prompt 文本，去外部平台渲染）。

**主要工作流**：

1. **Pipeline 端到端运行** → 产出 `ai_videos/mozun_chongsheng/` 完整目录树（项目级 + ep01-ep05 详细）。
2. **创作者复制单镜 prompt** → 粘贴到 Kling / Seedance / Seedream 平台 → 渲染。
3. **创作者按 seam-frame 工作流拼接** → 用 `shotNN_lastframe.png` 作为 Kling shot{N+1} 的 `input_image_urls[0]`。
4. **创作者收集渲染结果** → 用 ffmpeg / CapCut / DaVinci 拼接 → 双语字幕 → 抖音 + YouTube Shorts 发布（按 publish.md 模板）。
5. **创作者按 5 集为一批触发 stage-4 regen** → ep06-ep60 渐进生成。
6. **首发期留存数据回流** → 决定 ep60 用 single-season ending 还是二季钩。

## Functional requirements

### 项目级文件（`ai_videos/mozun_chongsheng/`）

- **FR-1** `README.md`（中文）— 项目概要、使用说明、9 角色清单、风格关键词、抖音 + YouTube Shorts 发布节奏总览。
- **FR-2** `world.md`（中文）— 世界观：修为体系（练气 → 渡劫后顶层共 10 阶）、五大宗派与"正道盟"统称（**默认"中州五道盟"** *(judgment call — chose 中州 because 仙侠通用地理感+5 道盟更朗朗上口，OQ-7)*）、男主前世魔殿名（**默认"沧冥魔域"**）、地理版图、关键道具（系统、丹药、双修机缘）、剧情核心反讽（伪君子 vs 反英雄魔尊）。
- **FR-3** `style_guide.md`（中文）— 视觉规范：调色锁定表（7 命名 hex）、镜头语言关键词字典（13 类景别 / 运动 / 速度）、光影状态词典（10 状态：魔气 / 仙气 / 雷劫 / 系统提示等）、转场词典（8 类：闪白 / 雷劫切等）、9:16 竖屏构图规范、传统仙侠 + 黑金沉郁双美学融合规则、**渲染样式锁定**（per follow-up 001：影视级真人写实 / cinematic / live-action / 8K HDR；负向锁定 anime / cartoon / illustration / 国漫 / 插画 / 工笔 / 水墨写意 / 二次元 / chibi / CGI 3D 渲染）。
- **FR-4** `arc_outline.md`（中文）— 60 集大纲：每集一行简介（卷 / 集号 / 主线大事件 / 修为段 / 三个 H 钩模式编号 / 关键角色出场）。包含六卷分布表（ep01-ep05 / ep06-ep13 / ep14-ep25 / ep26-ep43 / ep44-ep55 / ep56-ep60）。

### 角色级文件（`characters/`）

- **FR-5** 9 个核心角色 × 1 份 `characters/{中文名-身份}.md`（per follow-up 002，opt-in 中文文件名）。角色集合：
  1. `沧冥-魔尊本相.md` — 男主魔尊前世
  2. `叶无尘-乞丐转生.md` — 男主乞丐转生
  3. `苏璃月-紫霄圣女.md` — 主女主正派圣女
  4. `柳红袖-红袖招老板娘.md` — 副女主 1 酒楼老板娘
  5. `苓夭夭-药王谷医师.md` — 副女主 2 药王谷女医师
  6. `白月清-紫霄宫主.md` — 宗主 1（淫魔派）
  7. `赵焚天-玄炎宗主.md` — 宗主 2（炼器贩人派）
  8. `方鼎元-太清掌教.md` — 宗主 3（争位派）
  9. `韩夺心-万剑宗主.md` — 宗主 4（灭门夺宝派）
  10. `司空玄-影神殿主.md` — 宗主 5（暗通魔界派）

  **每个角色 .md 必含的 10 字段锁定描述符**：性别/年龄观感/体型 · 面貌 · 瞳色 · 发型/发色 · 服装/主色 · 标志道具 · 标志动作 · 气质 · 配色 hex · **一句话锁定**（byte-identical 跨集复制）。年龄观感锁定为 看似 18-35 岁青春帅气/貌美档（per follow-up 002 — 不要显得太老）。

- **FR-6** 每个角色 1 份 `characters/ref_images/{中文名-身份}-立绘.md`（中文 Seedream 立绘 prompt）— 共 **10 份**（男主双形态各 1）。每份遵循"主体+细节+风格+参数"四段式模板（见 angle-character-and-naming § 3.4），含黑金沉郁 hex / 9:16 / 4K / 负向词清单 / 影视级真人写实锁定（per follow-up 001）。柳红袖（老板娘）服饰必为"朱红绫上襦 + 浅黄锦缎围裙"，禁止肚兜 / 抹胸 / 露肩 / 露胸（per follow-up 002 — 妖娆但不暴露）。

### 单集级文件（`episodes/epNN/`，N=01..05 详细，N=06..60 仅在 arc_outline.md）

- **FR-7** `episode.md`（中文）— 本集剧情简介 + 上集回顾（≤ 50 字）+ 本集主线（300-500 字）+ 下集预告（≤ 50 字）+ 情绪节奏（钩 #1 / #2 / #3 三个时间轴定位）+ 涉及角色 + 关键场景。
- **FR-8** `shotlist.md`（中文 GFM 表格）— 10 行 × 8 列：shot_id / 时长 / 景别 / 镜头运动 / 内容 / 角色 / 场景 / 配色。total ≤ 90s，每镜 ≤15s（默认 8-10s）。
- **FR-9** `prompts/shot{NN}_kling.md` × 10（中文，每镜一份 Kling image-to-video prompt，含 `input_image_urls[]` 注释指向 seam-frame）。
- **FR-10** `prompts/shot{NN}_seedance.md` × 10（中文，每镜一份 Seedance text-to-video prompt，**末尾必含"避免: ..." 段** 因 Seedance 无 `negative_prompt` 字段）。
- **FR-11** `prompts/shot{NN}_lastframe_seedream.md` × 10（中文，每镜一份末帧 Seedream still 立绘 prompt）。
- **FR-12** `prompts/shot01_startframe_seedream.md` × 1（中文，单集首镜首帧 Seedream still）。
- **FR-13** `publish.md`（中文）— 本集发布元数据：抖音标题模板 ≤ 25 字、抖音 hashtag 5-10 个 3 层结构、抖音封面建议（含字幕带 y 坐标）、YouTube Shorts 双语标题模板 ≤ 90 字符、YouTube Shorts hashtag 6-8 个、cover-frame shot id（哪个 shot 用作缩略图，默认 shot07 爽点峰值帧）。

### 修为体系（写入 `world.md`）

- **FR-14** 修为 10 阶：练气 → 筑基 → 金丹 → 元婴 → 化神 → 合体 → 大乘 → 渡劫 → 渡劫后顶层 1（**默认"真仙"**）→ 渡劫后顶层 2（**默认"圣人 / 沧冥归位"**，男主归位标杆）。
- **FR-15** 男主修为路径：练气（卷一·乞丐 ep06-ep10）→ 筑基（ep11-ep13）→ 金丹（ep14-ep20）→ 元婴（ep21-ep25 觉醒卷尾）→ 化神（ep26-ep30）→ 合体（ep31-ep36）→ 大乘（ep37-ep43）→ 渡劫（ep44-ep49）→ 真仙（ep50-ep55）→ 圣人 / 沧冥归位（ep59-ep60 终战）。
- **FR-16** 反派 5 大宗主前世修为：渡劫期巅峰（联手才能镇压渡劫后顶层男主）。
- **FR-17** 男主标志魔功 9 阶：黑息引（练气）→ 九幽指（筑基）→ 九幽噬魂掌（金丹）→ 魔气化龙（元婴）→ 血色雷（化神）→ 魔影分身（合体）→ 虚空蚀心（大乘）→ 血雨九重劫（渡劫）→ 星辰魔阵·沧冥归位（渡劫后顶层）。

### 系统机制（写入 `world.md`）

- **FR-18** 系统三轨混合（任务 / 双修 / 丹药）：
  - **任务模块**：系统派发"诛伪君子 / 救凡人 / 揭露阴谋"任务，奖励 = 修为提升 / 神识强化 / 魔功秘籍。系统 UI = 金色文字 + 黑底半透明面板 + 字幕动画（写入 `style_guide.md` "系统 UI 视觉规范"）。
  - **双修机缘**：与三女主之一关键节点双修，触发修为大关突破（金丹→元婴 = 主女主第一次双修；化神→合体 = 副 1；大乘→渡劫 = 副 2 *(judgment call — chose this distribution because 主女主线最厚故占主突破点；OQ-5 多女主结局分配)*）。
  - **丹药机缘**：药王谷女医师所炼丹药为另一关键阶级跃迁辅助（具体丹药 ep26-ep30 入药王谷起出现）。
- **FR-19** 系统强度 = 中等加成（系统给任务 / 提示 / 机缘，男主仍需自己阳反击）。

### 视觉规范（写入 `style_guide.md`）

- **FR-20** 主调色锁定：黑 #0a0a0a / 护黄金 #a8842c / 深青 #1a3038 / 银白高光 #f5f5f0（+ 由 angle-visual-style 提供的 3 个辅助色，共 7 命名 hex）。
- **FR-21** 双美学融合规则：传统仙侠（白衣山门 / 剑气 / 青绿仙气）= 五大宗主 / 正道盟视觉；黑金沉郁（黑袍 / 魔气 / 雷劫）= 男主 / 魔殿场景；每集需有 ≥ 1 镜两套美学同框（白衣伪君子 vs 黑袍魔尊）。
- **FR-22** 9:16 竖屏构图规范：角色站位上 1/3 线 / 中心 / 下 1/3 线 三档；运镜以"推 / 拉 / 摇 / 升降 / 环绕"5 类基础为主；避免大幅横向运镜（9:16 不耐看）。
- **FR-23** 镜头时长锁定：默认 9 秒；范围 8-10 秒；硬上限 15 秒。任何 shot 时长 > 15s 须在 shotlist.md 拆分为两镜。

### Prompt 模板与 seam-frame 工作流

- **FR-24** Kling image-to-video prompt 模板（中文，每个 shot 强制字段）：
  ```
  [参考图: characters/ref_images/{role}_seedream.png + prompts/shot{N-1}_lastframe.png + prompts/shot{N}_lastframe.png]
  角色: {锁定句子, byte-identical 跨集}
  场景: {引用 world.md / style_guide.md 关键词}
  动作: {仅描述运动 — 0-9s 内可完成}
  镜头: {景别 + 运镜}
  光线/色调: {从 § 调色锁定 + 光影状态词典 取词}
  比例: 9:16
  时长: ≤10s
  ```
  **关键约束（CC-2）**：image-to-video prompt **不要复述图中已有内容**，只描述运动。
- **FR-25** Seedance text-to-video prompt 模板（中文，每个 shot 强制字段）：
  ```
  角色: {锁定句子, byte-identical}
  场景: {引用 world.md / style_guide.md}
  动作: {完整描述 — Seedance 无 ref-image, 必须文字给全}
  镜头: {景别 + 运镜}
  光线/色调: {从 § 调色锁定 + 光影状态词典}
  比例: 9:16
  时长: ≤10s
  避免: {规避词列表}  ← 强制，因 Seedance 无 negative_prompt 字段
  ```
- **FR-26** Seedream 立绘 prompt 模板（角色立绘，10 份）：见 angle-character-and-naming § 3.4 四段式。**渲染样式必须锁定为影视级真人写实** (per follow-up 001)：每份 prompt 的"风格"段使用 `电影级真人写实 + 4K HDR cinematic + 仙侠古装真人剧造型 + 8K 写实人像摄影 + 真实皮肤布料质感 + 实拍剧照风`；"负向"段必含 `anime / cartoon / illustration / chibi / 国漫 / 插画 / 工笔 / 水墨写意 / 二次元 / CGI 3D render / 塑料皮肤 / 卡通色`；类比剧目仍可引用《琉璃》《长月烬明》《苍兰诀》等（这些本就是 live-action 真人剧）。
- **FR-27** Seedream seam-frame 模板（每镜末帧 + 每集首镜首帧）。每份 seam-frame prompt 必含 `渲染样式: 影视级真人写实` 行，与 FR-26 立绘锁定一致：
  ```
  # {场景描述, 与对应 shot 的视频 prompt 同 token}
  # 角色 {锁定句子}
  # 姿态 (frozen instant): {精确 pose / 镜头角度 / 光线状态}
  # 比例: 9:16
  # 负向: {同视频 prompt 的避免词}
  ```
  与 video shot prompt 的 `场景:` / `光线/色调:` 字段 token 同步，确保静帧与视频段视觉连贯。
- **FR-28** seam-frame 工作流契约（per agent_refs/project/ai_video.md 规则 11）：
  - 渲染顺序：Seedream lastframe.png（每镜）+ shot01_startframe.png（每集首镜）→ Kling shot N 的 `input_image_urls[]` = [shot{N-1}_lastframe.png, shot{N}_lastframe.png]（shot01 用 [shot01_startframe.png, shot01_lastframe.png]）。
  - Seedance 不接 ref-image，但 token 描述必须与相邻镜头同步以减少视觉漂移。

### 单集 10 镜头默认布局

- **FR-29** 单集默认 10 镜头骨架（90s 内）：
  | 镜 # | 时长 | 段位 | 内容契约 |
  |---|---|---|---|
  | 1 | 8s | 黄金钩 0-8s | 冷开场（直接给画面冲击）+ 后段一句旁白召回上集 cliffhanger |
  | 2 | 8s | 情境 8-16s | 本集核心场景 / 任务起点 |
  | 3 | 9s | 情境 16-25s | 冲突起点 / 角色互动 |
  | 4 | 9s | 反转 25-34s | 第一反转（钩 #2 落点）|
  | 5 | 9s | 反转 34-43s | 关键人物登场 / 系统提示 |
  | 6 | 10s | 爽点 43-53s | 修为提升 / 反派被打脸 |
  | 7 | 10s | 爽点 53-63s | 女主互动 / 情绪峰值 |
  | 8 | 9s | 爽点尾 63-72s | 转折预兆 |
  | 9 | 9s | Cliff 72-81s | 新威胁 / 真相 / 选择题（钩 #3 落点）|
  | 10 | 9s | Cliff + 预告 81-90s | 切动作 / 闪剪下集 |

  这是默认骨架；具体集可微调（±1 镜或±1s/镜，但单集总和保持 ≤ 90s 软上限）。

### 钩 / 模式库（写入 `style_guide.md`）

- **FR-30** 10 种 H 模式钩库（每集至少 2 个 H）：
  H1 = 冷开场极端虐 / H2 = 系统弹窗 / H3 = 身份反转 / H4 = 双修破境 / H5 = 丹药入腹 / H6 = 伪君子撕脸 / H7 = 主女主立场翻 / H8 = "我回来了" / H9 = 集尾选择题 / H10 = 二季钩（仅 ep60）。
  每集 episode.md 必填 `钩列表: [H#, H#, ...]` 字段。

### 发布元数据（写入每集 `publish.md`）

- **FR-31** 抖音标题模板（≤ 25 字）：`《魔尊归来》第NN集 ｜ {8-15 字钩子}`。钩子词前置：重生 / 反杀 / 当年 / 我倒要 / 你以为。
- **FR-32** 抖音 hashtag 5-10 个 3 层（P0-P3）：
  - P0（核心）：#短剧 #仙侠 #魔尊归来
  - P1（题材）：#重生 #爽剧 #打脸
  - P2（细分）：#修仙短剧 #国风 #古装
  - P3（长尾）：#男频短剧 #AI短剧
- **FR-33** 抖音封面规范：720×1280 / 主体置上 1/3 线 / 大字 8-12 字居中偏下 / 文字安全带 y∈[160, 1050]。cover-frame 默认取 shot07（爽点峰值帧）。
- **FR-34** YouTube Shorts 双语标题模板（≤ 90 字符）：`《魔尊归来》EP NN | Demon Lord Returns | {English hook} | #shorts #cdrama #xianxia`
- **FR-35** YouTube Shorts hashtag 6-8 个：#shorts #cdrama #xianxia #revenge #cultivation #xianxiadrama #aishort #demoncore
- **FR-36** YouTube Shorts 字幕：中文原声 + 英文 subtitle（修为术语保留汉字 + 英文同位语，例：练气 Qi Refining、金丹 Golden Core、渡劫 Tribulation）。
- **FR-37** 60 集发布节奏（建议）：day1-12 每日 1 集 → day13-30 每日 2 集 → day31-60 每日 1 集（约 40 天首发）。

### 卷间大事件分布（写入 `arc_outline.md`）

- **FR-38** 六卷大事件锁定：
  - **卷一·镇压（ep01-ep05）**：ep01 冷开场镇压 / ep02-04 倒叙因果 / ep05 转生乞丐 cliffhanger
  - **卷二·乞丐重生（ep06-ep13）**：ep10-12 系统觉醒 / ep13 Midpoint Reversal A（血池真相）
  - **卷三·觉醒（ep14-ep25）**：入正派 / 主女主 / 杀宗主 1 / 元婴觉醒 ep25
  - **卷四·恢复（ep26-ep43）**：药王谷 / 副女主 2 / 击杀宗主 2-3 / 大乘
  - **卷五·反击（ep44-ep55）**：击杀宗主 4-5 / 渡劫 / Midpoint Reversal B（ep50-55 男主前世瑕疵）
  - **卷六·终战（ep56-ep60）**：杀回大本营 / 真仙→圣人归位 / ep60 二季钩（可选 final shot）

### 二季钩开关

- **FR-39** ep60 final shot 双版本：
  - `shot10_finale_kling.md`（single-season ending）— 屠尽伪君子 + 三女主成婚 + "全剧终"字幕
  - `shot10_hook_kling.md`（二季钩 open ending）— 主女主立于雪中腹微凸光芒一闪 + 远方一道魔气未灭

### 多女主结局分配（OQ-5 默认）

- **FR-40** *(judgment call — chose this distribution because 主女主与男主主线深度绑定故 happy；副 1 留人间烟火味故 happy；副 2 中立医疗角色 + 三女主同侍一人略显套路化故留白：ep60 副 2 选择"留药王谷继承衣钵 / 不入魔域"开放结局，可与男主仍保持挚友关系；OQ-5)*：
  - 主女主（苏璃月）→ HE：与男主同归沧冥魔域共度长生
  - 副女主 1（柳红袖）→ HE：与男主仍在凡间酒楼有故人之谊（凡 / 仙互不打扰）
  - 副女主 2（苓夭夭）→ 留白 / 半 HE：留药王谷继承衣钵；男主每年来访一次

### Open questions 默认（来自 dossier OQ）

- **OQ-1** *(judgment call — 全免费下保留 ep05/12/22/30/43/55 大钩位置作为完播率/投流转化点，与付费节点同位)*
- **OQ-2** *(judgment call — 上集召回用蒙太奇 1-3 秒（节奏更紧）；下集预告用 1-2 秒闪剪（参见 FR-29 镜 #10）)*
- **OQ-3** *(judgment call — ep01 不做 30s 教学集；通过 ep02-04 倒叙交代因果，符合"重生流默认观众已熟悉"惯例)*
- **OQ-4** *(judgment call — midpoint reversal B 强度 = "前世男主曾误伤一名正派女弟子"，让"伪君子"的指控不完全成立但又不撼动男主主线复仇正当性；参考《长月烬明》"我已成魔"的中度伤口)*
- **OQ-9** *(judgment call — 乞丐 → 觉醒中间形态不独立立绘；用 lastframe Seedream 在关键 shot（ep11 / ep14 / ep21 / ep25）锚定形态过渡足够)*

### 其他默认

- **FR-41** 比例：所有 prompt 均为 9:16（不在每镜重复确认；style_guide.md 一处定义即可）。
- **FR-42** 语言：所有 prompt 文本与 publish.md 元数据中文（YouTube Shorts 标题中英双语）。
- **FR-43** 文件命名：英文 / 拼音；内容中文（per agent_refs/project/ai_video.md 规则 1）。

## Non-functional requirements

- **NFR-1** 文件命名：`mozun_chongsheng/episodes/epNN/` 数字两位补零（ep01 不是 ep1）；shot id 两位补零（shot01..shot10）。
- **NFR-2** 字符锁定：9 个角色（10 份立绘）的"一句话锁定"在所有 shot prompt 中 byte-identical 复制（modulo whitespace）。任何角色的描述符在同一集内出现两个版本即视为 blocker（per agent_refs/validation/ai_video.md 规则 3）。
- **NFR-3** 镜头原子性：每镜 ≤ 15 秒（硬上限），默认 8-10 秒。任何 shot 时长 > 15s 或缺失"时长"字段 = blocker。
- **NFR-4** 双管线 + seam-frame：每镜必含 `_kling.md` + `_seedance.md` + `_lastframe_seedream.md`；每集首镜必含 `_startframe_seedream.md`。
- **NFR-5** 比例字段：每镜 prompt 必含 `比例: 9:16`（缺失 = blocker）。
- **NFR-6** Seedance 规避词：每镜 Seedance prompt 必含"避免:"前缀的规避词列表（CC-5 决定，缺失 = blocker）。
- **NFR-7** Publish 完整性：每集 publish.md 必含抖音 + YouTube Shorts 双套元数据（缺任一 = blocker）。
- **NFR-8** 中文内容：所有 `ai_videos/mozun_chongsheng/*.md` 文件内容 ≥95% 汉字 + 全角标点（per agent_refs/validation/ai_video.md 规则 1，proper nouns 如 Kling/Seedance/Seedream/9:16 不计入）。
- **NFR-9** 角色未声明引用：任何 shot prompt 引用的角色必须在 characters/ 中已声明（缺失 = blocker，per agent_refs/validation/ai_video.md 严重表）。

## Acceptance criteria summary

完整 ACs 由 stage 5 strategy 给出。高级层次：

- **AC-1（语言合规）** 所有 `ai_videos/mozun_chongsheng/*.md` 中文内容 ≥95%。
- **AC-2（15s 原子）** 所有 shotlist.md 中每镜 `时长` ≤ 15s。
- **AC-3（角色一致性）** 每个角色的"一句话锁定"在同一集内所有引用其的 shot prompt 中 byte-identical。
- **AC-4（双管线 + seam-frame 完整性）** 每镜含 `_kling.md` + `_seedance.md` + `_lastframe_seedream.md`；每集首镜含 `_startframe_seedream.md`。
- **AC-5（比例 + 规避词）** 每镜 prompt 含 `比例: 9:16`；每镜 Seedance prompt 含"避免:"前缀。
- **AC-6（Publish 完整）** 每集 publish.md 含抖音 + YouTube Shorts 双套完整元数据。
- **AC-7（10 份立绘）** 9 角色 + 男主双形态 = 10 份 Seedream 立绘 prompt 在 characters/ref_images/ 下齐备。
- **AC-8（角色声明）** 任何 shot prompt 引用的角色名必须在 characters/ 已声明。
- **AC-9（卷边界）** arc_outline.md 包含 60 集每行一句概要 + 六卷分段标识。
- **AC-10（手动走查）** 所有自动 level 通过后，emit `validation.requires_manual_walkthrough`：用户随机抽查 ep01 + 任一 ep03/04/05 的 characters/ref_images/ + shotlist + 2-3 个 shot prompt，确认角色一致性 + 单集叙事连贯性。

## Open questions（明确不在 v1 处理）

| # | 问题 | 状态 |
|---|---|---|
| OQ-7 | "正道盟"统称（已默认"中州五道盟"）/ 男主前世魔殿名（已默认"沧冥魔域"）/ 乞丐城酒楼名 | stage 6 spec 阶段 final lock，可在 README 起始页修订 |
| OQ-8 | 修为数值化（任务系统打分）— 是否需要 0-100 数字标注 | 默认不数字化；仅用 9 阶名称定性，符合仙侠惯例 |
| OQ-10 | 跨镜头 LUT 一致性 / 抖音 vs YouTube 色域适配 | 后期问题；不在 prompt-pipeline v1 范围 |
| OQ-11 | Kling prompt 长度上限 / Seedance 负向字段未来开放 | 监控项；如 Seedance 加入 `negative_prompt` 字段，stage 6 模板可移除"避免:"前缀 |
| OQ-12 | 立绘 → 场景化首帧是否需要 2-pass 生成 | 默认 1-pass（Seedream 4 / 5 直出场景化首帧）；如发现漂移再 2-pass |
| OQ-13 | Kling vs Seedance 评分表 (per-shot 用户 A/B 选谁) | 由用户在 stage 6 后渲染时判断；非 spec 范围 |
| OQ-14 | YouTube Shorts 海外多语扩展 | v2 follow-up |
| OQ-15 | 抖音备案号获取时机 / 主话题词命名 | 上架前；非 pipeline 范围 |

---

> Stage 4 完成。`final_specs/spec.md` 已落盘，43 个 FR + 9 个 NFR + 10 个 AC 高级标识 + 8 个 deferred OQ。下一步：stage 5 — validation strategy（parent-direct + parallel level-specialist workers）。
