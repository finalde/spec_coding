# Interview — performance_library

Run: performance_library-20260613-014942

## Metadata

- `task_type`: ai_video
- `sub_type`: **N/A — 共享资产库 (shared asset library)**，非剧目。
  > Divergence note（对齐 `agent_refs/interview/ai_video.md` rule 1 的 sub_type 强制 fork）：本任务建设的是与 `_actors/` / `_voices/` 同级的下划线前缀共享资产库，不产出 `episodes/` 或单片短视频，故 `novel`/`short` fork 不适用。库内每条检验视频本身按 `short` 单镜约束（≤15s、9:16）生成，但库整体不是一部短剧。
- 库路径: `ai_videos/_performances/`

## Categories probed

- **首批情绪覆盖** — 决定 research 与 stage-6 的工作量与首版边界。
- **维度结构** — 决定 entry schema 的骨架，是整个库可检索性的核心。
- **条目数量** — 校准"几十种"的具体目标与节奏。
- **条目来源** — 决定 research 阶段的调研角度（方法论 vs 实战）。
- **库布局与命名** — 决定目录树与编号方案。
- **验证标准** — 决定一条 entry 何时算"验证通过"，是闭环的验收点。
- **引用机制** — 决定库完成后如何被 shot prompt 复用。
- **webapp 集成范围** — 决定本期是否触及 ai_video_management。

## Round 1

### 首批情绪覆盖
**Q:** 首批表演库覆盖哪些情绪类别?
- A: **短剧高频情绪集 (~10 种)** — 按国内短剧实战频率选：悲/喜/怒/惧 四基础 + 压抑隐忍、爽感反转、羞辱难堪、震惊错愕、狠戾、柔情等高频桥段情绪。分类边界在 research 阶段细化。

### 维度结构
**Q:** 条目的维度结构采用哪种?
- A: **四维：情绪 × 强度 × 风格 × 载体 (Recommended)** — 每条 entry 标注 情绪（悲伤…）、强度（1-微表情 → 5-失控爆发）、风格（内敛压抑 / 外放爆发）、载体（面部 / 眼神 / 肢体 / 呼吸 / 复合）。槽位明确、易发现空缺、易检索。

### 条目数量
**Q:** 每种情绪的条目数量目标?
- A: **20-40 条/情绪 (Recommended)** — 对齐用户原话"几十种"。按四维槽位自然展开。

### 条目来源
**Q:** 条目内容的来源策略?
- A: **方法论 + 实战双轨 (Recommended)** — research 阶段并行两路：表演方法体系（斯坦尼斯拉夫斯基/迈斯纳/FACS 微表情编码）提供系统性骨架；国内短剧高频表演桥段提供实战词汇。合流成条目。

## Round 2

### 库布局与命名
**Q:** 表演库的目录布局与命名?
- A: **`_performances/` 按情绪分子目录 (Recommended)** — `ai_videos/_performances/{emotion}/perf_NNNN/perf_NNNN.md` 三级布局，与 `_actors/actor_NNNN` 对齐（每 entry 一个文件夹，装检验视频 mp4）。情绪作为一级分类轴。

### 验证标准
**Q:** 一条表演 entry 什么时候算「验证通过」?
- A: **双模型 + 主观评分 (Recommended)** — Kling 和 Seedance 各渲染一版检验视频，用户按「表演是否达意 / 情绪是否识别得出 / 是否过火」打分（1-5），≥阈值且至少一个模型达标即通过；实测笔记记录哪个模型好 / 哪些词被忽略。

### 引用机制
**Q:** 表演 entry 被 shot prompt 引用的机制?
- A: **reference-handle 头 + 嵌字段 (Recommended)** — shot 代码块顶部加一行 reference 头（对齐现有 `<char>请参考:` 约定），同时把 entry 的锁定文本块逐字嵌入 `动作:` / `表情:` 字段。与 `_actors`/`_voices` 引用一致。

### webapp 集成范围
**Q:** 本期是否含 ai_video_management webapp 集成?
- A: **含最小集成** *(偏离我推荐的"本期不含"——用户选择顺带挂入 webapp)* — 本期顺带把 `_performances/` 挂进 webapp sidebar + 可浏览；不做结构化编辑器 / ✨推荐。这两项留作独立 follow-up。

## Team consensus

All 8 categories marked clear after 2 rounds. 进入 Stage 3（research）。
