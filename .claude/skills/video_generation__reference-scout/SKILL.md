---
name: video_generation__reference-scout
description: Scout 短剧 趋势 + 差异化 material to seed a new Chinese 短剧 series before preproduction. Covers 红果 / 抖音 / 快手 / YT Shorts / TikTok via WebSearch, scores samples with the 6-dim AI-friendliness card (≥40/60), maps 套路密度 vs 空白区, and emits one `reference_pack.md`. Use when starting `series/{name}/` or refreshing visual references. Replaces `ai-shorts-scout` + `trend-gap-scout`.
---

# 参考侦察 · Reference Scout — 趋势 + 差异化侦察

先看市场在放什么，再决定你写什么。产出 **一份** 侦察报告，足够让 `preproduction` 锁圣经、让 `serial-novelist` 定语气。

## Modes

- **趋势挖掘模式 (trend sweep)** — 给出当前 7 天 / 30 天内在目标平台跑出的 AI 短剧 / 爽文样本。按题材聚类，排趋势热度表。
- **类型差异化模式 (gap)** — 在锁定题材（重生 / 穿越 / 系统 / 古风 / 仙侠 / 玄幻）内，映射已存在的套路密度并标出白空间。

两种模式可合并跑（大多数新系列需要两段都做一次）。

## Workflow

### Step 1 — 平台扫描

按优先级顺序执行（每个平台 2–4 条 WebSearch 查询，超出预算则停止）：

1. **红果短剧 / 河马剧场 / 九州短剧**（国内短剧 App 爆款，Q3ac 首选）—— 通过 WebSearch 拿榜单与爆款标题（禁止在 App 内做账号行为，只取公开页面信息）。
2. **抖音话题标签**（`#短剧` `#爽文` `#重生` `#大男主` `#古风` `#仙侠`）—— 按 CLAUDE.md YouTube-fallback 同一套策略（WebSearch 为主，不尝试反爬）。
3. **快手短剧榜**（`磁力新剧` / `短剧新榜`）。
4. **YouTube hashtag landing page**（`https://www.youtube.com/hashtag/aishortdrama/shorts` / `chineseshortdrama` 等）—— 遵守 CLAUDE.md 规则：Playwright MCP 在 `/watch?v=<ID>` 页面提取；WebFetch 在 YouTube 只能拿 footer，不用；`/shorts/<ID>` 先改 `/watch?v=<ID>`。
5. **TikTok**（英文海外市场，用于 IP 孵化判断 Q3c）—— 同样通过 WebSearch 拿主题线索，不做反爬。

每个平台至少收 **10–15 条** 候选标题与封面描述。所有平台 403 / 反爬 → 按 CLAUDE.md 「YouTube/trending 不超 1 次尝试」规则立刻降级到 WebSearch。

### Step 2 — 按题材聚类

把候选分入 Q1 题材桶：

- 现代都市爆款组（霸总 / 甜宠 / 职场逆袭）—— **本系列默认排除**（Q1bc 锁定为 重生 / 穿越 / 系统 + 古风 / 仙侠 / 玄幻）
- 重生 / 穿越 / 系统组 ✅
- 古风 / 仙侠 / 玄幻组 ✅
- 悬疑 / 末日 / 硬核组 —— 仅当用户明确扩展时收录

对每桶统计：样本数、近 30 天平均播放估算（Unknown 时标 Unknown）、常见钩子关键词前 10、常见身份反差模板（战神 / 赘婿 / 废柴 / 重生仙尊 / 系统宿主）。

### Step 3 — AI 可行性重评分

沿用 `video_generation__topic-scout` 的 **6 维度 / 每维 0–10 / 阈值 40** 打分卡（逐字复用维度名与说明）：

| 评估维度 | 含义 |
|---|---|
| 视觉简洁度 | 场景可 1–2 句描述，无复杂交互 |
| 人物可行性 | 不含真人艺人 / 公众人物；虚构角色可行 |
| 场景多样性 | 有多个不同环境 / 时刻 |
| 运动友好度 | 无快速动作 / 人群 / 体育 / 复杂物理 |
| 情绪钩子 | 前 3 秒有强情绪触点 |
| 叙事清晰度 | 可无对白理解故事 |

对每桶内样本逐条打分；**≥40 分进入候选池**，<40 踢掉并在报告里用一行说明原因。

### Step 4 — 视觉 / 音色参考包

从入池样本里抽：

- **色彩**：3–5 组主色 hex（可粗略取封面 / 截图主色）
- **景别 + 运镜高频组合**：如 `近景 + 推近` / `特写 + 环绕`
- **镜头语言白话清单**：避免空泛形容词的具体镜头动词
- **BGM 情绪走向**：压迫感 / 金戈铁马 / 清冷古韵 / 爽感升华
- **TTS 常见音色标签**：霸气青叔 / 通用赘婿 / 智慧老者 / 古风少御 / 沉稳解说男（可直接跨桶匹配 `BV107` / `BV119` / `BV158` / `BV115` / `BV142`）
- **字幕与 AI 披露标识样式**：样本里 AI 水印 / 披露文案的位置与字体风格

### Step 5 — 差异化 / 空白区

对锁定题材（重生 / 古风 / 仙侠），列一张 **「套路密度 vs 空白区」** 表：

| 套路标签 | 样本占比（%，估） | 创新空间（低 / 中 / 高） | 建议切入角度 |
|---|---|---|---|
| 战神归来 | ~ | | |
| 重生复仇 | ~ | | |
| 赘婿翻身 | ~ | | |
| 废柴觉醒 | ~ | | |
| 系统签到 | ~ | | |
| 宗门斗法 | ~ | | |

「创新空间高」行 = 本系列差异化候选；连同 2–3 条具体开局建议（开场主角身份 + 反差 + 首集钩）。

### Step 6 — 落盘

把全部结果写入：

```
series/{name}/research/reference_pack.md
```

报告节选结构（必须按顺序）：

1. **侦察摘要**（≤300 字，本系列应该怎么切入）
2. **平台趋势表**（按平台列 top 样本）
3. **样本评分表**（评分 ≥40 的条目，附原链接）
4. **视觉参考清单**（Step 4 拆出）
5. **套路密度 + 空白区表**（Step 5）
6. **差异化开局建议**（3 条，编号 A/B/C，每条一句钩 + 一句反差 + 一句首集钩）
7. **来源链接清册**（全部 URL，标注抓取时间）
8. **未知项 / 失败项**（`Unknown` 标注与复查建议）

最后把 `status.md` 的 `research` 字段置为 `reference_pack: v1 · {YYYY-MM-DD}`。

## Inputs

- 用户口头题材倾向（Q1bc 默认 重生/穿越/系统 + 古风/仙侠/玄幻）
- 可选：已有 `series/{name}/bibles/style_bible.md`（refresh 模式时读）

## Outputs

- `series/{name}/research/reference_pack.md`
- 更新 `status.md`

## 输出规范

- **全部中文**；仅 hex 色值 / 平台域名 / voice_id 保留英文。
- **只采公开数据**（CLAUDE.md）。任何需要登录 / 反爬破解的接口一律跳过。
- **来源不可造**。无法验证的主题标注 `Unknown` 并写明需要什么来验证。
- **AI 可行性评分 ≥40/60 才进报告**。低分样本仅保留一行否决说明。
- **不做价值判断**。样本是否「低俗」由合规侧审，本 skill 只描述。
- **引用 CLAUDE.md 的搜索预算限制**：单任务 ≤10 条 WebSearch；先宽后窄。
- **输出模板严格执行**，不自由发挥。

## 边界情况

- 所有桶内候选都 < 40/60 → 如实告知，建议用户补充细分方向（比如从「古风 + 医女」收窄而不是「古风」大词），不自动放宽阈值。
- 平台返回 403 / 要登录 → 按 CLAUDE.md 「不超过 1 次重试」立刻降级到 WebSearch；在「未知项」章节注明。
- 用户提了非中文市场（ReelShort / DramaBox 类海外 IP）→ 仍以中文原稿为准，附一节「海外迁移提示」但不自动双语化。
- refresh 模式且 `style_bible.md` 已锁定 → 只改 Step 4 的视觉参考清单，禁止改风格锚点本身。

## Invocation examples

- 「为 `series/战神归来/` 做一轮趋势侦察，重点是红果 + 抖音的大男主 + 重生。」
- 「帮 `series/剑尊重生/` 刷新视觉参考，只动 Step 4 这一节。」
- 「古风 + 仙侠 目前的套路密度哪几块是白空间？给 3 条差异化开局建议。」
