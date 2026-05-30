# Revised prompt — xianxia_new (working slug)

**task_type:** ai_video
**sub_type:** novel
**Working task_id:** `xianxia_new-20260524-101931`
**Composed from:** `raw_prompt.md` + follow-ups 001 (MVP ep01) + 002 (阮瑶 rename) + 003 (scenes single-file + seam-frame abolished) + 004 (characters folder pattern) + 005 (mirror characters → ai_videos) + 006 (chapter.md canonical, chapter-first authoring order) + 007 (chapter excerpts in shot prompts) + 008 (c{N}_pinyin hybrid folder pattern, webapp-compatible) + 009 (split fenshoulu: my_novel=reader, ai_videos=production) + 010 (scene prompts novel-prose-grade + 15s walk-through video reference per rule 12.4-E / 12.10) + 011 (per-episode dialogue.md derived from chapter per rule 12.6-B + folder rename `prompts/` → `shots/` global)
**Last regenerated:** 2026-05-24 (post follow-up 011)

## Goal

撰写一部原创仙侠（xianxia）长篇小说手稿，作为后续 AI 短剧（AI 短剧 / vertical short drama）拍摄的源文本。手稿正文落在 `my_novel/{slug}/`；AI 短剧产物（角色 ref-image、分镜、Kling / Seedance prompt、字幕、合成镜头视频）落在 `ai_videos/{slug}/`，由后续独立任务承接。本任务只到「小说手稿 + AI 短剧第一季可拍摄分镜本」为止。

## Context

用户已通过 follow-up 113 重构了顶层目录：

- `downloaded_novels/xianxia/` — 14 本既有仙侠基线小说（爬自 sudugu/ttkan）。
- `my_novel/` — 用户原创手稿目录，本任务的 stage 6 输出目的地。
- `ai_videos/` — AI 短剧项目目录。

用户的核心诉求是：把这 14 本作为「题材教材」，提取通用要素（修炼境界、宗门 / 散修 / 魔门三方格局、主角原型、爆款节拍），抽象出去版权化的新作。要保持仙侠类型读者期待的 **競猜性**（伏笔密度 + 反转 + 悬念 + 身份揭示节奏），同时融入 2025–2026 的短剧 / 网文 / 抖音 / 小红书最新趋势，并且产出必须是 AI 短剧可拍摄的（角色少、prop 简单、画面可由 image / video gen 稳定生成）。

## Desired outcome (MVP scope — post follow-up 001)

**MVP delivery target = ep01 only**, iteratively. Ship ep01 → review with user → learn → regen ep02 in a subsequent run. The 60-ep design and full character/world/style bibles still stand (ep01 references them all visually); only the detailed shot-level production is restricted to ep01.

到 stage 6 结束，仓库里应该有：

1. `my_novel/{slug}/README.md` — 中文标题 + 一段概要。
2. `my_novel/{slug}/world.md` — 世界观（境界体系、地理 / 势力、修炼系统物理规则）— **FULL**, 因为 ep01 + 后续都用得到。
3. `my_novel/{slug}/characters/{中文名}/{中文名}.md` — 每个 **ep01 出场角色** 一个 folder + 1 个主 bible 文件 (rule 12.5 v4 folder pattern per follow-up 004; sibling 文件按角色复杂度按需添加). 主 bible 含外貌锁定描述符 + 嵌入式 7s turntable 视频 reference prompt (rule 12.5 v11). 主角双形态 + 师父 + 主女主 + 童年邻家姐姐 (阮瑶, per follow-up 002) + 6 反派 + 1 前世档案 = **11 folder × 11 主 bible 文件**.
4. `my_novel/{slug}/style_guide.md` — 镜头语言 + 调色板 + 寄生升级 motif 等 — **FULL** verbatim from dossier R-3.
5. `my_novel/{slug}/arc_outline.md` — 60 集 one-liner 大纲 — **FULL**（包含 dossier R-6 的 reveal cadence 节点），保证 ep01 可以正确植入未来集数的钩子。
6. `my_novel/{slug}/scenes/{scene}.md` — **仅 ep01 出场场景**, 单文件 pattern (rule 12.3 v2 per follow-up 003): `s1_无寿崖.md` (前世坐化 / ep01 头 3s) + `s2_落雁渊.md` (ep01 系统觉醒地). 每文件含 bible 段 + 嵌入式 Seedream 立绘 段 (`---` 分隔). **`scenes/ref_images/` 子目录已废止**. 其他地点 inline 在 shot prompt 中.
7a. `my_novel/{slug}/episodes/ep01/chapter.md` — ep01 完整小说篇章 (用户可读的中文 novel prose, ≥ 5000 字, per follow-up 006). **canonical source-of-truth**; script / shotlist / prompts 全部从 chapter derive. 描写密度 + 内心 OS + cliffhanger 比下载基线小说更细致精彩.
7b. `my_novel/{slug}/episodes/ep01/script.md` — ep01 完整剧本 (screenplay form, derived from chapter)。
8. `my_novel/{slug}/episodes/ep01/shotlist.md` — ep01 分镜（≤ 15 s / shot，9:16 竖屏）。
9. `ai_videos/{slug}/episodes/ep01/shots/shotNN.md` — 每镜一份 self-contained prompt 文件 (rule 5 v3 三段式 per follow-up 007: ① Chapter excerpt + ② Shot context + ③ 视频 prompt 14-字段 schema). **seam-frame Seedream 嵌入块已 abolished** (per follow-up 003); 跨 shot 视觉连续性依描述层 byte-identical + 共享 turntable mp4 + 共享 scene mp4/PNG. (post follow-up 009 split: production-side under `ai_videos/`; post follow-up 011: 文件夹 `prompts/` → `shots/`)
9b. `ai_videos/{slug}/episodes/ep01/dialogue.md` — 纯对白 derived from chapter per rule 12.6-B (format: `角色名: "台词" (语气情感注释)` 每行 + 末尾发声清单表) post follow-up 011.
10. `my_novel/{slug}/episodes/ep01/publish.md` — 标题 / 简介 / 标签 / 封面建议。
11. `my_novel/{slug}/copyright_clearance.md` — 与 14 本基线小说 + sibling mozun_chongsheng 的差异度逐项核查（已基于 dossier 准备好黑名单）。

**Deferred (出本次 MVP)**：ep02–60 的 script / shotlist / shot prompts；ep02+ 才出场的角色立档；ep02+ 才用到的 scenes 立档；YouTube Shorts EN 字幕 pass。

**Iterative cadence**：完成 ep01 全部产出后停下来 review；用户决定 ep02 是否进入下一轮 spec-driven 流水线（可通过 stage-4 regen 扩到 ep02，或直接重新跑 agent_team）。

## Constraints — copyright safety

- 人名、地名、功法名、宗门名、灵兽名、神器名、独门体系命名（如「灵根」「金丹」这种通用术语可保留；具体功法 / 阵法 / 心法名必须独创）— 全部需要去版权化。
- 任何 plot beat 必须能溯源到至少 2 本基线小说才能用；只能溯源到 1 本的要素 → 必须重新设计或抛弃。
- 不抄某一本的卷结构 / 章节标题套路。
- 主角的开局设定（出身 / 起点 / 金手指）必须是 14 本之外的组合，且不与近 6 个月头部仙侠短剧 / 网文撞设定。
- 产出 `copyright_clearance.md`，逐项标注本作元素的「baseline 来源集合 + 与单本最近距离的描述 + 改写说明」。

## Constraints — genre fidelity (競猜性)

- 修炼境界体系：明确的阶梯式上升（≥ 5 个大境界，每境界有内在小阶段），瓶颈 / 突破时刻是固定的情绪爆点。
- 三方势力格局：正派 / 散修 / 魔门或类似三分。
- 伏笔密度：每章至少埋一个未来 5–20 章内回收的钩子；每 10 章至少一个「读者以为是 A，实际是 B」的反转。
- 身份揭示：主角身世 / 神器来历 / 师门秘辛至少有 3 条隐藏线，递进式揭示。
- 升级节奏：典型「升级 → 遇敌 → 险胜 / 蛰伏 → 再升级」的循环，符合仙侠读者肌肉记忆。
- 不可解构：本任务不是仙侠类型的颠覆 / 戏仿，而是 competent representative — 类型读者读完会说「这是我想看的仙侠」。

## Constraints — short-drama feasibility

- 每个 plot beat 必须能在 ≤ 15 s 单镜头内表达（多镜头连接也行，但每镜头独立 ≤ 15 s）。
- 每集（episode）≤ 8 分钟（短剧平台典型时长），即 ≤ 32 个 shot。
- 每集出场角色 ≤ 5 个有台词的角色（AI 角色一致性成本随角色数指数上升）。
- 主要场景 prop 复杂度：每个场景 ≤ 6 个 prop（剑、扇、丹炉、玉简、阵盘、灵石…），AI 图生成稳定。
- 选材偏好：山门、洞府、丹房、剑阁、坊市、密林、灵田、悬崖、瀑布、月夜、雪山 — AI 图 / 视频生成在这些 palette 上稳定；避开高密度群战、大规模法宝乱舞、复杂多人对白同框场景。
- 9:16 竖屏构图友好（人物中近景为主；广角全景每集 ≤ 2 个）。

## Constraints — trend awareness (2025–2026)

研究阶段必须查的方向（最终在 `trend_notes.md` 给出引用 + 应用决策）：

1. 当前短剧平台（抖音 / 红果 / 快手等）爆款仙侠选题清单 + 失败选题 / 读者疲劳点。
2. 网文 2025–2026 仙侠头部作品的开局钩子、主角设定、第一卷结构。
3. 小红书 / B 站仙侠剧讨论中重复出现的痛点（「主角太憋屈」「反派太蠢」「师父太工具人」之类）。
4. 当下短剧付费转化率高的情绪节点（打脸、复仇、揭穿、护短、收徒、传承…）。
5. AI 短剧赛道（区别于真人短剧）目前的视觉 / 叙事范式。

不必抄热点，但要知道热点存在并主动决策是「跟」还是「反」。

## Constraints — file & naming convention

- spec 流水线目录：`specs/ai_video/{task_name}/`（当前为 `xianxia_new`，最终 slug 由 interview 阶段决定）。
- 手稿目录：`my_novel/{slug}/`（slug = pinyin / English，README + 内容 = Chinese）。
- AI 短剧目录：`ai_videos/{slug}/`（同样 slug pinyin / English，所有内容 Chinese）。
- README.md 的 H1 必须是 `# 《<中文标题>》— AI 视频项目` 这一规范（与现有 mozun_chongsheng 一致）。
- 文件名 Chinese 允许，但 folder 名禁止 Chinese。
- 所有内容（剧本、对白、世界观、角色描述）= Chinese。

## Out of scope (this task)

- 实际渲染（不调用 Kling / Seedance API，只写 prompt）。
- 字幕音频合成（v1 visuals + on-frame 字幕；TTS / 配乐另起任务）。
- 第一季之后的所有剧集 shot 级展开（保持 outline 级即可）。
- 仓库已有的 mozun_chongsheng 项目（无关；本任务并行存在）。
- 顶层目录重构（已由 follow-up 113 落地，不再讨论）。

## Working slug clarification

`xianxia_new` 仅用于本 spec 流水线目录，便于在 stage 1 阶段先动起来。Stage 2 interview 的产出之一就是最终中文标题 + pinyin slug；如果与 `xianxia_new` 不同，会在 stage 2 通过的同一时刻 `mv specs/ai_video/xianxia_new/ specs/ai_video/{final_slug}/`，并在 stage 4 / 6 用新 slug 创建 `my_novel/{final_slug}/` 与 `ai_videos/{final_slug}/`。

## Open questions surfaced for stage 2 interview

1. 是否锁定「仙侠」？（用户原话「比如仙侠」— 比如是举例还是确定？）
2. 总集数预期（10 / 30 / 60 / 100+）？影响 outline 粒度与 stage 6 工作量。
3. 主角原型偏好（卷王 / 反套路懒人 / 重生 / 散修登仙 / 跨界 / 复仇）— 用户对哪一类有偏好？
4. 视角（第一人称 / 第三人称跟主角 / 全知）？
5. 男频 / 女频 / 全龄向？影响情感线设计与目标受众短剧平台。
6. 总篇幅目标（粗略字数 OR 季数）？
7. 第一集开场钩子的方向偏好（穿越 / 重生 / 灭门 / 拜师 / 拣到神器 / 系统觉醒…）？
8. 网络热点研究的优先级排序（短剧 vs 网文 vs 抖音 vs 小红书 — 用户最看重哪一块的趋势）？

这些都将在 stage 2 的 interview 多选题里逐一提问，确定后写入 `interview/qa.md`。
