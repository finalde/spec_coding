# Revised prompt — mozun_chongsheng

**task_type:** ai_video
**sub_type:** novel（多集，episodes/epNN/ 布局）
**task_name:** mozun_chongsheng
**Composed from:** `raw_prompt.md`
**First generated:** 2026-05-09 16:42:05
**Last regenerated:** 2026-05-09 19:48:37 — header bump for follow-up 002 (人物年龄观感全面下调到 18-35 看似青春 + 加 俊朗/貌美/英气 关键词；服饰升级锦缎绣纹；柳红袖肚兜 → 朱红绫上襦 + 锦缎围裙（妖娆但不暴露）；方鼎元 鹤发银白长须 → 乌发玉簪三缕短须；全部角色文件改用中文名命名 沧冥-魔尊本相.md 等；agent_refs/project/ai_video.md 规则 1 amend 允许中文 opt-in；277 lock 替换 + 31 filename 替换覆盖 173 文件；20 旧英文文件已 rm)。

**Prior follow-up:** 2026-05-09 19:26:14 — follow-up 001 渲染样式锁定 影视级真人写实 / cinematic / live-action（保持有效）。

## Goal — 想做什么

制作一部 AI 驱动的中文 **仙侠 × 重生复仇** 短剧 **《魔尊归来》**（中文剧名已由用户在 stage 1 收尾时确认），约 60 集，每集 1.5 分钟（≈ 90 秒），总时长 ~ 90 分钟。每集以双 prompt（Kling + Seedance）驱动 AI 视频生成，配核心角色 Seedream 立绘做形象一致性锚点。

故事核心是一句话："**魔尊被正道伪君子联手镇压、转生于乞丐之身，从绝境一步步恢复实力，最终杀回正派大本营。**"

## Context — 设定与价值观

### 类型定位

- **赛道**：竖屏短剧（短视频平台主流形态：每集 ≤ 2 分钟、强情绪驱动、靠"爽"+"虐"快速勾人）。
- **题材**：仙侠（不是武侠）——有法宝、灵力、宗门、修为境界、神识空间等元素；同时融入"重生 / 转生"+"复仇 / 打脸"两大类型 trope。
- **道德底色**：反讽——所谓"正道"全是伪君子；男主魔尊不是单纯反派，而是被构陷的"反英雄"。这是与传统仙侠（《琉璃》《长月烬明》）正邪明晰路径的最大区别，更接近网络爽文 + 虐心叙事的混合。

### 视觉与美学（待 interview 收敛具体方向）

- 仙侠基础视觉语言：山门、剑气、雷劫、丹炉、灵力流光、长袍、发冠。
- 反派"正派伪君子"的双面性需要视觉化——明面"白衣胜雪 + 仙气飘飘"，背面"血色残忍"。
- 主角双形态：魔尊原形（黑袍 + 红瞳 + 魔气缠身）+ 乞丐转生形态（衣衫褴褛 + 神识压抑 + 双眼藏锋）。

### 输出规范（继承 `agent_refs/project/ai_video.md` 项目规则）

- 项目根目录：`ai_videos/mozun_chongsheng/`（路径英文 / 拼音；文件内容中文）。
- 多集制布局：`ai_videos/mozun_chongsheng/episodes/ep01/`、`ep02/`...`ep60/`，每集一个独立子目录承载 shotlist + Kling/Seedance prompts + 单集 publish.md。
- 共享资源在项目根：`characters/`（含每个角色的 Seedream 立绘 prompt + 锁定描述符）、`world.md`（世界观）、`style_guide.md`（视觉语言与配色）、`arc_outline.md`（60 集大纲）。
- 每个镜头 ≤ 15 秒；每个镜头同时给出 Kling prompt 与 Seedance prompt（双管线兼容）。
- 默认画幅 9:16（竖屏短剧）。
- v1 仅出"画面"，不出音频 prompt（音频后期人工 / 第三方 TTS 接入）。

## Desired outcome — 完工时应有的产出

### 项目级（`ai_videos/mozun_chongsheng/`）

- `README.md`（中文）—— 项目简介、剧情大纲、主创团队（如果有）、播出 / 渲染 / 后期 流程。
- `world.md`（中文）—— 世界观设定（修为体系、宗门版图、魔界 vs 正道、关键法宝 / 神识空间）。
- `style_guide.md`（中文）—— 视觉语言、配色、镜头法、字体、字幕规范。
- `arc_outline.md`（中文）—— 60 集大纲（每集一段一句话情节 + 关键转折点 + 高潮 / 虐点 / 爽点节奏）。
- `characters/{role_name}.md` + `characters/ref_images/{role_name}_seedream.md`（每个核心角色一份 Seedream 立绘 prompt + 一份角色档）。
- `publish/`（项目级发布元数据：标题候选、封面方案、平台适配模板）。

### 单集级（`ai_videos/mozun_chongsheng/episodes/epNN/`，N = 01..60）

- `episode.md`（中文）—— 本集剧情简介 + 上集回顾 + 下集预告 + 情绪节奏（钩子 / 转折 / 收尾）。
- `shotlist.md`（中文 + Markdown 表格）—— 本集所有镜头列表（shot_id / 时长 / 描述 / 角色 / 场景 / 配色）。每集约 6-12 个镜头（90 秒 ÷ 镜头时长）。
- `prompts/shot{NN}_kling.md` 和 `prompts/shot{NN}_seedance.md` —— 每个镜头一对 prompt 文件（双管线）。
- `publish.md`（中文）—— 本集发布元数据（标题、字幕、平台 hashtag、封面提示）。

### Pipeline 级（`specs/ai_video/mozun_chongsheng/`）

- 完整六阶段 spec-pipeline trail（user_input、interview、findings、final_specs、validation、changelog），用于支撑后续按集 / 按场景的 regen prompts。

## 用户已明确的硬约束（不需 interview 再问）

1. 集数：约 60 集（前后 5 集弹性）。
2. 单集时长：1.5 分钟左右（前后 30 秒弹性）。
3. 总剧情主轴：镇压 → 转生乞丐 → 恢复实力 → 反杀正派大本营。
4. 男主立场：原魔尊（被构陷），后转生（双重身份）。
5. 反派定位："正道伪君子"——非单一反派，而是一群虚伪的正派宗师。
6. task_type = ai_video，sub_type = novel；走 episodes/epNN/ 布局。
7. 渲染管线：Kling + Seedance 双 prompt + Seedream 立绘（继承 ai_video 工作流约定）。
8. 主语言：中文（叙事 + 字幕 + 角色台词）。

## 待 stage 2 interview 收敛的开放问题

为避免 stage 1 越权，以下问题不在本 revised prompt 中预设答案——留给 interview manager 团队提问：

1. **剧名**：使用《魔尊重生》临时标题，还是另起更具记忆点的中文剧名？
2. **女主 / 感情线**：是否设女主？若设，立场为正派良心 / 魔界遗孤 / 乞丐时认识的凡间少女 / 多女主？
3. **复仇 vs 救赎**：男主最终目标——纯复仇杀光正派 / 复仇后立新秩序 / 复仇过程中被女主感化转向救赎？
4. **修为体系**：参照"练气—筑基—金丹—元婴—化神—合体—大乘—渡劫"传统九阶，还是自创？
5. **正派伪君子的群像**：人数（5 / 7 / 9）、组织结构（联盟 / 宗主会 / 长老会）、伪君子的具体表现（双面 / 表里不一 / 以正道之名行私利）。
6. **关键道具 / 法宝**：是否有标志性法宝（如《琉璃》的鸿蒙炉、《沉香》的四瓣莲）？
7. **每集叙事节奏**：番剧式（每集独立钩子）/ 三集一组（短剧节奏组）/ 整段连续切分？
8. **60 集分卷**：是否分 4-6 大卷（如：序卷 → 觉醒卷 → 恢复卷 → 反击卷 → 终战卷）？
9. **视觉风格**：传统仙侠 / 暗黑仙侠（血色重）/ 国潮赛博 / 水墨写意？决定 style_guide.md 的核心调性。
10. **角色一致性**：核心角色立绘锁定到何种粒度（仅主角 / 主角 + 主要正派 / 全员）？
11. **典型镜头时长**：默认 5 秒 / 8 秒 / 10 秒 / 15 秒？决定每集镜头数与节奏密度。
12. **publish 平台**：抖音 / 视频号 / 快手 / 小红书 / B站 / YouTube Shorts —— 决定封面 + 标题模板。
13. **是否分两季**（30 集 + 30 集），或一季完结？

## Out of scope（v1 默认排除，除非 interview 明确加入）

- 音频 prompt 生成（v1 视觉 only，音频后期人工接入）。
- 真实剪辑 / 渲染 / 后期 —— pipeline 仅产出 prompt 文本与 Seedream 立绘 prompt；用户自行去 Kling / Seedance / Seedream 平台渲染。
- 多语言版本（v1 仅中文；英文 / 海外发行版作为 v2 follow-up）。
- 真人配音脚本与音乐版权 —— 不在 spec-pipeline 范围内。
- 与 `research/xianxia_storylines/` 中任何一部已有作品的直接复刻 / 改编（仅做风格与节奏借鉴）。

## 主线参考节奏（pipeline 内部假设，stage 4 spec 阶段会被 interview / research 矫正）

> 仅作为 stage 1 → stage 2 的"心理图景"，非定稿。

- **第一卷 · 镇压（约 5 集）**：开场即决战。魔尊与正派联军的最终战，被诱入阵法、神识被剐、本体被封。最后一刻一缕魂魄飞遁——
- **第二卷 · 乞丐重生（约 8 集）**：转生于一名底层乞丐少年身上。神识封闭、修为尽散，靠记忆与一丝魔气在凡间苟活。建立日常 + 隐忍线。
- **第三卷 · 觉醒（约 12 集）**：偶然机遇（古宅 / 法宝碎片 / 旧部相认 / 仇人路过）唤回部分修为。识破"正派伪君子"在乞丐城的搜捕行动。
- **第四卷 · 恢复（约 18 集）**：远走江湖，逐一寻回散落的本命法宝 / 神识碎片 / 旧部魔将。并在沿途收割小反派，建立"我已不是当年那只待宰的魔"。
- **第五卷 · 反击（约 12 集）**：直捣正派各分舵，逐一击破伪君子的根基与名声，揭穿真相。
- **第六卷 · 终战（约 5 集）**：杀回正派大本营。终战、揭幕、一句"当年你们怎么对我，今日我便十倍奉还"。开放或闭合结局留给 stage 2 interview 决定。

---

## Stage 1 用户决策记录（2026-05-09 16:42:05 收尾）

- task_name = `mozun_chongsheng` ✓ 已锁定。
- 中文剧名 = **《魔尊归来》** ✓ 已锁定（替代原临时标题《魔尊重生》）。
- 主线参考节奏（六卷 / 5+8+12+18+12+5）✓ 用户认可，作为 stage 2 interview 的起点；卷间集数尚可由 stage 2 进一步精调。
- 13 个 interview 开放问题 ✓ 用户未提前消除任何一个 → 全部带入 stage 2 由 interview team 处理。

Stage 1 完成。下一步：stage 2（interview，parent-direct）。
