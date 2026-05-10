# Findings dossier — mozun_chongsheng

Run: mozun_chongsheng-20260509-164205
Stage: 3 (research, AUTONOMOUS)
Coordination: parent-direct + 5 parallel agent workers
Date: 2026-05-09

## Angles researched

1. **story-and-pacing** — 60 集 × 90s 仙侠重生短剧的节奏模板；六卷大事件分布；"三钩"单集模型
2. **character-and-naming** — 9 个核心角色中文姓名候选 + 锁定描述符样板 + 7 阶魔功招式命名 + Seedream 立绘 prompt
3. **visual-style** — 黑金沉郁 × 传统仙侠美学；调色锁定表 / 镜头语言关键词 / 光影状态词典 / 转场词典 / 9:16 构图
4. **prompt-pipeline** — Kling 2.1 / Seedance 1.0 / Seedream 5.0 中文 prompt schema；image-to-video vs text-to-video；15s 切分；seam-frame 工作流；1 个 worked example
5. **platform-conventions** — 抖音 + YouTube Shorts 仙侠短剧发布元数据规范；标题 / hashtag / 封面 / 60 集发布节奏

## Cross-cutting insights

### CC-1 · "黑金沉郁 × 黄金 3 秒"复合留存模型 *(visual-style + story-and-pacing)*

`angle-visual-style` 锁定的"黑金沉郁主调 + 白衣伪君子反讽"美学，与 `angle-story-and-pacing` 的"单集 0-3s 冷开场决定 70% 留存"硬约束**自然耦合**：每集 ep N 的第一帧应当直接呈现"白衣 vs 黑袍"的视觉反差或"赤红瞳孔"的高对比镜头——视觉冲击与叙事钩同步落点。这意味着 ep01 shot01 不能是片头 logo / 上集回顾占用，必须是 climax 性质的一帧（行业惯例 + 美学约束的双重收敛）。

### CC-2 · "9 角色锁定 + 双修机缘"驱动 stage 6 prompt 复用率 *(character-and-naming + prompt-pipeline + story-and-pacing)*

`angle-character-and-naming` 给出 9 个角色 byte-identical 锁定描述符，`angle-prompt-pipeline` 警告"Kling image-to-video prompt 不要重新描述图中已有内容，只描述运动"——两者结合的 stage 6 模板：每镜的 Kling prompt 只写"动作 / 镜头 / 光线"，**角色描述靠 ref-image 锁定 + 一句话锁定句子嵌入**，可以让单镜 prompt 字数压缩 50% 以上。同时 `angle-story-and-pacing` 的 Midpoint Reversal A（ep13 血池真相）/ Midpoint Reversal B（ep50-55 男主前世瑕疵）等大节点，必然涉及 9 角色之间的多人同框——9 锁定描述符的字节一致性是这些镜头不"漂"的硬保证。

### CC-3 · 60 集压缩密度需要"系统提示弹窗"作为高频钩 *(story-and-pacing + prompt-pipeline + visual-style)*

`angle-story-and-pacing` 把行业 100 集模板压缩到 60 集（密度 ×1.7），导致每 25-30 秒就要出一个钩子。`angle-character-and-naming` 把"系统流"明确为本剧主驱动机制；`angle-visual-style` 提供"系统提示"光影状态词作为一个独立视觉状态。三者结合：**"系统弹窗" UI 元素在 stage 6 应当被实例化为一组可复用的 Kling/Seedance prompt 片段**（金色文字 + 黑底半透明面板 + 字幕动画），让"叮——任务发布 / 修为 +1 阶"作为标准化的中钩 H2 模式（参见 angle-story-and-pacing § 3.3 模式库）。

### CC-4 · 抖音封面安全区与 9:16 角色立绘构图的冲突点 *(platform-conventions + visual-style + character-and-naming)*

`angle-platform-conventions` 指出抖音封面文字安全带 y∈[160,1050]、主体置上 1/3 线；`angle-visual-style` 与 `angle-character-and-naming` 的 9:16 立绘默认构图是"半身正面 + 三庭五眼东方面孔 + 目视镜头"——**默认构图的脸部正好落在 y≈480 区域，与抖音 8-12 字大字标题（按行业惯例放在 y≈700-900）安全错位**。这是个无意中的好兆头：默认 9:16 立绘 prompt 不需要为了让封面字不挡脸做特殊适配。但若 stage 6 决定生成 cover-frame 专用 Seedream（一个角色 + 一个字幕预留区），仍需独立 prompt——已记入 angle-platform-conventions § 4 开放问题。

### CC-5 · Seedance 无 negative_prompt 字段，影响视觉规范执行 *(prompt-pipeline + visual-style)*

`angle-prompt-pipeline` 发现 **Seedance 1.0 Pro 没有公开的负向 prompt 字段**——这与 `angle-visual-style` 的"不要现代服饰 / 不要赛博朋克元素 / 不要暖橙红主调"等规避约束直接冲突。**唯一可行的工作方法：把负向词嵌入主 prompt 末尾的"避免"段**（如"避免: 现代服饰、暖橙红主调、赛博朋克元素"）。Stage 4 spec 必须明确这个约束并在 stage 6 模板里强制每镜 Seedance prompt 都带"避免"段，否则会出现风格漂移。

### CC-6 · 60 集发布节奏与"二季钩"决策耦合 *(platform-conventions + story-and-pacing)*

`angle-platform-conventions` 推荐"day1-12 每日 1 集 + day13-30 每日 2 集 + day31-60 每日 1 集"约 40 天首发；`angle-story-and-pacing` 在 ep60 末预留 5 秒"二季钩"开关。两者结合形成**"40 天首发期内观察留存数据 → 决定是否激活二季钩 → 第 41 天起开始二季制作"**这种自然续作链路，避免一次性提交 60 集后再决定二季的窒息点。Stage 4 spec 应把"二季钩开关"做成 ep60 的可选 final shot，而非硬编码。

## Per-angle highlights

### story-and-pacing
- 单集"三钩"模型：0-3s 冷开场 + 25-30s 第一反转 + 75-88s cliffhanger
- 60 集压缩 7 处大钩：ep05 / ep12 / ep22 / ep30 / ep43 / ep55 / ep60
- 男频仙侠重生爆款 *《我真没想重生啊》* (2025) 验证 147 集体量；本剧需密度 ×2.5
- 重生复仇配方："半集卖惨 → 一集手刃 → 三集洗刷污名" 已被光明网 / 澎湃新闻多次验证
- 6 卷主线大事件分布表已锚定到 60 个具体集号（详见 § 3.1）

### character-and-naming
- 9 个核心角色 × 5 个候选名 × 1 个推荐 → 已交付。男主前世推荐"**沧冥 · 魔尊**"，乞丐转生推荐"**叶无尘**"
- 五大宗主推荐组合：白月清 / 赵焚天 / 方鼎元 / 韩夺心 / 司空玄——名字本身埋"伪正派"反讽
- 三女主推荐：**苏璃月**（圣女） / **柳红袖**（酒楼老板娘） / **苓夭夭**（药王谷医师）
- 男主 9 阶标志魔功命名（练气黑息引 → 渡劫后顶层"星辰魔阵·沧冥归位"），每招带视觉关键词
- 锁定描述符 10 字段格式（性别/年龄/面貌/瞳色/发型/服装/道具/标志动作/气质/一句话锁定）已定型
- Seedream 立绘 prompt 通用模板四段式（主体+细节+风格+参数）+ 男主魔尊态完整实例

### visual-style
- 调色锁定表（7 命名 hex）已交付，主调 #0a0a0a / #a8842c / #1a3038 / #f5f5f0
- 13 类景别 / 运动 / 速度关键词字典 + 10 个光影状态词典 + 8 个转场词典
- 黑金沉郁锚定到《长月烬明》"五彩斑斓的黑"模板；白衣伪君子反向利用《琉璃》《沉香》"白衣帝君"视觉记忆做反讽
- "prompt 可写"vs"后期才有"分桌严格——服化、单点光源、简单粒子、6 类运镜可由 Kling/Seedance 一镜出；跨镜头 LUT、AE 复合特效、字幕同步明确划归后期

### prompt-pipeline
- Kling 2.1 Pro: image-to-video; 支持 `input_image_urls[]` 至 4 张 → 完美适配 seam-frame `[shot{N-1}_lastframe, shot{N}_lastframe]` 契约
- Kling prompt 关键陷阱: image-to-video prompt 只描述运动，不要复述图中已有内容
- Seedance 1.0 Pro: text-to-video; **无负向字段** → 规避词必须嵌入主 prompt
- 时长锁定: Kling 8-10s（10s 默认）；Seedance 5-12s
- 比例锁定: 9:16 / 1080p
- 完整 worked example: ep01 shot01 "魔尊雷劫坠落"，含 byte-identical "沧冥 · 前世魔尊形态" 锁定句跨 4 个 prompt

### platform-conventions
- 抖音标题模板: `《魔尊归来》第NN集 ｜ {8-15 字钩子}` (≤ 25 字)；hashtag 5-10 个 3 层结构
- 抖音封面: 720×1280 / 主体上 1/3 线 / 文字带 y∈[160,1050]
- YouTube Shorts 双语标题: `《魔尊归来》EP NN | Demon Lord Returns | {English hook} | #shorts #cdrama #xianxia`
- 60 集发布节奏: 40 天首发，密集期 ep13-30 每日 2 集，前后稀释
- 海外字幕: 中文原声 + 英文 subtitle，修为术语保留汉字 + 英文同位语（练气 Qi Refining 等）
- 2025 爆款门槛: 热度峰值 ≥3 亿 + 主话题 ≥100 亿

## Recommendations for the spec

### R-1 · 直接采用研究产出的"推荐"命名集合作为 stage 4 的 canonical names

无需进一步候选筛选。9 角色的"推荐"列已经在 `angle-character-and-naming` § 3.1 给出，这一组在 (a) 黑金沉郁色调、(b) 伪君子反讽、(c) 网感记忆点 三个维度都已综合。stage 4 直接 lock 这一组到 spec。

### R-2 · 把"系统弹窗"作为一个独立 prompt 片段模板

CC-3 揭示 60 集压缩密度需要高频钩；"系统弹窗" UI 应当被 stage 4 spec 化为可复用的 prompt 片段（金色文字 + 黑底半透明面板）。建议 stage 4 spec 在 `style_guide.md` 加一个独立"系统 UI 视觉规范"章节，并在每集 shotlist 都标注哪些 shot 包含系统弹窗。

### R-3 · stage 6 工作单元划分按"卷"而非"集"做并行

研究产出的六卷边界（ep01-05 / ep06-13 / ep14-25 / ep26-43 / ep44-55 / ep56-60）天然有"风格段"特征——每卷的视觉关键词、男主修为段、女主出场都是独立的。stage 6 把每卷设为一个 work unit，可以让卷内多镜头并行生成时风格更稳。但 stage 4 第一次输出仍按 ai_video.md 规则只详细写 ep01-ep05 (detail_batch_size=5)，剩余在 arc_outline.md 留单行大纲。

### R-4 · 单集 10 镜头默认布局

每集 90 秒默认 10 镜（每镜 ~9 秒），落点：

| 镜头 # | 时长 | 段位 | 内容 |
|---|---|---|---|
| 1 | 8s | 黄金钩 | 冷开场 / 上集召回 |
| 2 | 8s | 情境 | 场景 / 任务 |
| 3 | 9s | 情境 | 冲突起点 / 角色互动 |
| 4 | 9s | 反转 | 局势翻转 |
| 5 | 9s | 反转 | 关键人物 / 系统提示 |
| 6 | 10s | 爽点 | 修为提升 / 打脸 |
| 7 | 10s | 爽点 | 女主互动 / 情绪峰值 |
| 8 | 9s | 爽点尾 | 转折预兆 |
| 9 | 9s | Cliff | 新威胁 / 真相 |
| 10 | 9s | Cliff + 预告 | 切动作 / 闪剪下集 |

总和 90 秒 ✓。这个布局直接 lock 到 stage 4 spec 作为单集 shotlist 默认骨架。

### R-5 · Seedance 负向 prompt 强制内嵌

CC-5 决定: stage 4 spec 必须把"避免"段做成每个 Seedance prompt 的强制字段，而非可选。stage 5 validation 应有一个独立 check: "每镜 Seedance prompt 必含'避免:'前缀的规避词列表"。

### R-6 · 9 锁定角色 + 双形态 = 实际 10 份 Seedream 立绘

男主双形态（魔尊 / 乞丐）需要 2 份独立立绘，因此实际 ref_images 数为 **10 份**（不是 9）。stage 4 spec / stage 5 validation 与 stage 6 execution 都按 10 份计算。

### R-7 · 抖音封面与默认 9:16 立绘构图无冲突，但 cover-frame 仍是独立 prompt

CC-4: 默认 9:16 立绘的脸部位置 y≈480，与抖音封面字幕带 y≈700-900 自然错位。但 stage 6 仍应为 ep01 / ep10 / ep30 / ep60 等"广告投流候选集"独立生成 cover-frame Seedream prompt（含字幕预留区），其余非候选集复用 ep 内 keyframe。

### R-8 · ep60 二季钩开关

stage 4 spec 把 ep60 的 final shot 实例化为两个版本：
- `shot10_finale_kling.md` (single-season ending) — 屠尽伪君子 + 三女主成婚 + 字幕"全剧终"
- `shot10_hook_kling.md` (二季钩 open ending) — 主女主立于雪中，腹部微凸光芒一闪 / 远方一道魔气未灭

实际渲染时由用户根据首发期留存数据二选一。

## Open questions surviving research

| # | 问题 | 来源 angle | 何时收敛 |
|---|---|---|---|
| OQ-1 | 抖音 + YouTube Shorts 全免费模式下，付费节点（ep05/12/22/30/43/55）是否仍保留为"投流转化点"？ | story-and-pacing | stage 4 spec |
| OQ-2 | 单集"上集召回 / 下集预告"用固定字幕模板还是蒙太奇画面？ | story-and-pacing | stage 4 + style_guide.md |
| OQ-3 | ep01 "满记忆零修为" 开局是否需要 30s 旁白教学集？ | story-and-pacing | stage 4 spec |
| OQ-4 | midpoint reversal B (ep50-55 男主前世瑕疵) 的"伤口程度"标尺 | story-and-pacing | stage 4 + stage 5 |
| OQ-5 | 多女主结局分配（副 1 / 副 2 是 happy / 留白 / 牺牲？） | story-and-pacing | stage 4 spec |
| OQ-6 | 男主"沧冥"vs"玄无极"——朗读测试 / 抖音搜索热度交叉验证 | character-and-naming | stage 4 spec |
| OQ-7 | "正道盟"统称 / 男主前世魔殿名 / 乞丐城酒楼名 | character-and-naming | stage 4 + worldbuilding |
| OQ-8 | 修为数值化（任务系统打分需要） | character-and-naming + 系统设计 | stage 4 + stage 5 |
| OQ-9 | 乞丐期 → 觉醒期 中间形态独立立绘？ | character-and-naming | stage 4 |
| OQ-10 | 跨镜头 LUT 一致性 / 抖音 vs YouTube 色域适配 | visual-style | stage 6 + 后期 |
| OQ-11 | Kling prompt 长度上限 / Seedance 负向字段是否未来开放 | prompt-pipeline | stage 5 + stage 6 |
| OQ-12 | 立绘 → 场景化首帧 是否需要 2-pass 生成 | prompt-pipeline | stage 6 |
| OQ-13 | Kling vs Seedance 评分表 (per-shot 用户 A/B 选谁) | prompt-pipeline | stage 5 validation |
| OQ-14 | YouTube Shorts 海外多语扩展（不止英文） | platform-conventions | v2 follow-up |
| OQ-15 | 抖音备案号获取时机 / 主话题词命名 | platform-conventions | 上架前 |

OQ 的处理：Stage 4 spec 中能给默认值的一律给默认 + `*(judgment call — chose X because Y)*`；不能默认的列入 spec 末尾"Open questions"由用户在播出前回填。

---

> Stage 3 完成。`dossier.md` 与 5 个 angle-*.md 已交付。下一步：stage 4 — spec compilation（parent-direct，无 workers，输出 `final_specs/spec.md`）。
