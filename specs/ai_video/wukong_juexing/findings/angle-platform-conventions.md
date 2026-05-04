# Angle — platform-conventions

Run: wukong_juexing-20260503-201831
Researcher: 04 (platform-conventions)

## 1. What this angle covers

Concrete publish-time conventions for the YouTube Shorts upload of 《悟空觉醒》, plus a low-effort cross-publish appendix for 抖音 / 微信视频号 (since the locked file-content language is Chinese and the same 中文 metadata is reusable). Output feeds directly into `final_specs/spec.md` (Stage 4) and `publish.md` (Stage 6). Specifically resolved here:

- Optimal-length window for a faceless cinematic Short, and whether ~40 s stands.
- First-2 s hook timing, loop-back ending requirement.
- Title 字数, 简介 字数, hashtag 数量 + 位置 + 必备 标签.
- 自定义封面 (1080×1920) — when it actually shows vs when YouTube pulls auto-frame.
- Best 发布时段 (China-content Chinese-language audience vs global English audience tradeoff).
- 抖音 / 视频号 reuse rules (where the same metadata can copy-paste, where it must mutate).

Practice vs spec is distinguished throughout: official platform docs (YouTube Help, 微信开放社区) give length caps; creator-economy 2026 articles give hashtag-count and posting-time conventions.

## 2. Key findings per platform

### YouTube Shorts (primary target)

**Length window — practice.** 2026 Shorts that consistently get algorithmic distribution sit in **15–35 s** for high-completion niches and **25–45 s** for narrative/cinematic niches. A 30-second Short with ~85 % watch duration consistently beats a 60-second one with ~50 % — completion rate dominates absolute view-time as a distribution signal. Shorts under 20 s see ~42 % completion at the median; 30–45 s Shorts that *earn* their length still need >60 % completion to escape low-distribution bucket. ([Miraflow 2026](https://miraflow.ai/blog/youtube-shorts-best-practices-2026-complete-guide), [OpusClip 2026](https://www.opus.pro/blog/ideal-youtube-shorts-length-format-retention), [Miraflow length 2026](https://miraflow.ai/blog/how-long-should-youtube-shorts-be-2026))

**Hook timing — practice.** Swipe-or-stay decision lands at **2–3 s**, not 5. Faceless / animated content benefits from on-screen visual claim within 1–2 s; pattern interrupt in the first 5 s lifts retention by ~23 %. Faceless shorts have a structural advantage for looping because there's no body-language continuity cue telling the viewer the video has ended. ([Virvid hooks 2026](https://virvid.ai/blog/first-3-seconds-hook-faceless-shorts-2026), [Virvid faceless algo 2026](https://virvid.ai/blog/faceless-youtube-algorithm-retention-2026))

**Loop ending — practice (high-impact).** Replays count as additional views since March 2025 and feed back into distribution. Visual-loop endings (final frame ≈ opening frame) are the strongest single retention trick in 2026 viral Shorts. The locked stage-2 decision (Shot 05 closes on the cracking-stone callback) is consistent with this. ([Virvid loops 2026](https://virvid.ai/blog/looping-structure-shorts-retention-2026), [Vidiq Shorts algo 2026](https://vidiq.com/blog/post/youtube-shorts-algorithm/))

**Title — spec + practice.** Hard cap is **100 字符** (YouTube technical limit). Mobile-display safe is **≤ 70 字符** (≈ 30–35 中文字 — Chinese characters are double-width so ≈ 60 字符 ≈ 30 中文字). Recommended structure: 1–2 关键词 早出现, 用悬念 / 数字 / 反差句开头, 不在标题里塞 hashtag (浪费字符 + 视觉脏). ([Hashtag Tools 2026](https://hashtagtools.io/blog/youtube-shorts-hashtags-title-vs-description-2026), [advancedcharactercounter 2026](https://advancedcharactercounter.com/youtube-description-character-limit-and-title-length-guide-2026/))

**Description — spec + practice.** Hard cap is **5000 字符** ([YouTube 官方帮助](https://support.google.com/youtube/answer/12948449?hl=en)). Practice for Shorts: **首句 = 钩子 / 一句话场景概述**, 因为 feed 默认只显示前 1–2 行就被 "Show more" 折叠. 总长 控制在 **150–250 中文字** for Shorts (longer is cargo-cult; doesn't help SEO). ([Miraflow 2026](https://miraflow.ai/blog/youtube-shorts-best-practices-2026-complete-guide))

**Hashtag — practice (load-bearing rule).** **3–5 hashtag, 全部放在描述区, 不放在标题**. 描述区前 3 个 hashtag 自动以可点击链接形式显示在标题上方 — same visibility, zero title-character cost. **超过 15 个 hashtag → YouTube 视为 0 个 hashtag** (硬罚则). 必备 `#Shorts` 以触发 Shorts shelf. ([Hashtag Tools 2026](https://hashtagtools.io/blog/youtube-shorts-hashtags-title-vs-description-2026), [Miraflow 2026](https://miraflow.ai/blog/youtube-shorts-best-practices-2026-complete-guide))

**封面 (cover frame) — spec + practice.** 自定义 thumbnail 尺寸 **1080 × 1920 px (9:16), ≤ 2 MB, JPG/PNG/GIF**. **关键:** Shorts 主 feed (上下滑) 显示的是 YouTube 自动抽帧, 不是自定义 thumbnail. 自定义 thumbnail 仅在 *频道页 / 搜索结果 / 主页推荐* 出现 — 但这些是非 feed 流量来源, 仍然可推 27–70 % CTR 提升. 设计原则: 主体放上 2/3, 字 ≤ 3–5 字, 字号比横屏放大 20–30 %. 对本项目而言, 重点应是 **保证 Shot 01 第 0–2 s 抽帧本身就是合格封面** (因为 feed 抽的就是它). ([Miraflow thumbnail 2026](https://miraflow.ai/blog/youtube-shorts-thumbnail-strategy-2026))

**发布时段 — practice.** 全球范围内 Wed–Fri 的 12:00–15:00 与 19:00–21:00 (本地时区) 是高峰; 中国大陆中文受众峰值 19:00–22:00 (晚饭后). 项目目标若是中文受众, 锁定 **周四 / 周五 19:00–21:00 北京时间**. 若兼顾北美华人, 早班 11:00–12:00 北京时间 = 北美前夜也可. ([posteverywhere 2026](https://posteverywhere.ai/blog/best-time-to-post-on-youtube), [flonnect 2026](https://flonnect.com/blog/best-time-to-upload-youtube-shorts/))

### 抖音 (cross-publish, optional)

**发布节奏:** Rule of 3 — 上午 ≤ 10:00, 下午 ≤ 14:00, 晚间 ≤ 18:00 三档; 单条本项目用晚间档. ([Taisly 2026](https://taisly.com/best-time-to-post/douyin))
**话题:** 3–5 个精准话题 + #抖音原创 (替代 #Shorts). 中文话题已天然适配, 直接复用 YouTube 描述里的 hashtag 词条即可. ([az-loc 2025](https://www.az-loc.com/chinese-video-platforms-2025-guide/))

### 微信视频号 (cross-publish, optional)

**文案上限:** 1 分钟以内的短视频文案 (含话题、@) **≤ 1000 字**; 标题 **15–20 字佳, ≤ 55 字硬上限**. 话题用 `#话题#` 闭合格式, 不是 YouTube 的 `#tag` 开放格式. ([视频号官方文案技巧](https://developers.weixin.qq.com/community/develop/article/doc/0008e8b3fb4f38e5fb6e4631856013), [zhihu 视频号标题](https://zhuanlan.zhihu.com/p/355033905))
**推荐机制:** 双引擎 — 好友推荐 + 平台算法; 完播率 + 点赞转发评论 是核心信号 (与 YouTube Shorts 算法同构). ([视频号官方推荐机制](https://developers.weixin.qq.com/community/minihome/article/doc/000006d43482b87fb6101d56261413))
**封面:** 视频号 强烈鼓励自定义封面 (与 YouTube Shorts 不同, 视频号 feed 也用自定义封面), 应额外为视频号准备一张 1080×1920 9:16 海报. ([Canva 视频号封面](https://www.canva.cn/learn/10-video-cover/))

## 3. Locked publish.md template skeleton (Chinese, paste-ready)

> Stage 6 will copy this into `ai_videos/wukong_juexing/publish.md`. Stage 4 should reference this section by name.

```markdown
# 发布元数据 — 《悟空觉醒》

## 标题 (YouTube Shorts)
- 硬规则: ≤ 60 英文字符 (约 30 中文字), 不放 hashtag.
- 软规则: 1–2 关键词早出现 ("悟空" / "觉醒" / "封神" / "黑神话" 等), 用悬念 / 反差 / 数字 开头.
- 示例 (4 选 1, 待用户挑): "石卵裂开的那一秒, 悟空醒了" / "40 秒看完悟空觉醒全过程" / "为什么石猴一睁眼整个三界都在抖" / "黑神话之外, 这才是真正的悟空诞生".

## 简介 (YouTube Shorts description)
- 硬规则: ≤ 5000 字符 (官方上限); 实操控制在 150–250 中文字.
- 结构 (强制):
  1. 第 1 句 = 钩子 / 一句话场景概述 (默认显示在 feed 折叠前).
  2. 第 2–3 句 = 简短背景 (西游记典故 / 黑神话美学锚点).
  3. 空行.
  4. hashtag 段 (3–5 个, 见下).
  5. 可选: 创作工具说明一行 ("由 Seedream + Kling + Seedance 制作") — 提升 AI-content 透明度.

## Hashtag 规则
- 数量: 3–5 个, 全部放在描述区前两行.
- 顺序 (前 3 个会自动作为可点击链接显示在标题上方, 选最强的三个排前面):
  1. `#Shorts` (强制, 触发 Shorts shelf).
  2. `#孙悟空` 或 `#悟空` (主 IP 词).
  3. `#中国神话` 或 `#黑神话悟空` (类目词, 看是否要蹭《黑神话》流量).
  4. (可选) `#AI视频` 或 `#AI动画` (透明度 + AI-content 池).
  5. (可选) `#西游记` (品类长尾).
- 红线: 标题 + 描述 hashtag 总数 ≤ 15 (超过 → YouTube 视为 0 hashtag).

## 封面建议
- YouTube Shorts feed 流量主要看 Shot 01 自动抽帧 → **Shot 01 的第 0–2 s 必须本身就是合格封面**: 主体居中偏上 2/3, 单一焦点 (裂开的石卵 + 金光), 高对比度.
- 自定义封面仅用于频道页 / 搜索 / 主页推荐 — 仍建议生成 1 张:
  - 尺寸 1080 × 1920 px (9:16), ≤ 2 MB, JPG.
  - 主视觉: 悟空特写 / 凤翅紫金冠 + 金箍棒 + 金色光晕.
  - 文字 ≤ 4 中文字 ("悟空觉醒" 即可), 字号占画面短边 1/8 以上, 高对比描边.
  - 不放小字 (移动端不可读).

## 发布时段建议
- 主受众中文 (中国大陆): 周四或周五 19:00–21:00 北京时间.
- 兼顾北美华人 / 东南亚: 周四 11:00–12:00 北京时间 (= 北美前夜 / 东南亚午休).
- 不要上午 9:00 前 / 凌晨 1:00–6:00 发 (低活跃 + 算法冷启动慢).

## 跨平台复用 (可选, 非 v1 必交付)
- 抖音: 标题 + 简介 直接复用; 替换 `#Shorts` → `#抖音原创`; 发布走 Rule-of-3 晚间档 (≤ 18:00 北京时间).
- 微信视频号: 标题 ≤ 55 字 (本项目标题已合规); 描述 ≤ 1000 字 (远超本项目); hashtag 转换 `#tag` → `#话题#` 闭合格式; 必须额外做一张 9:16 自定义封面 (视频号 feed 显示自定义封面而非自动抽帧).
```

## 4. Implications for the spec

**~40 s target — confirmed with a tightening.** The 35–55 s soft band stated in `revised_prompt.md` is too generous on the upper end for 2026 Shorts retention math. Recommend Stage 4 lock the runtime at **38 s ± 4 s** (effective 34–42 s band):

- 5 shots × 7.6 s = 38 s — well inside the ≤ 15 s/shot constraint and inside the 25–45 s "narrative cinematic" sweet spot.
- Caps the upper bound at 42 s so completion rate stays achievable for a no-dialogue, no-text-overlay piece (those are harder to retain in the 45 s+ band).
- Preserves the loop-back payoff already locked in stage 2 — visual loops are the single highest-impact retention trick in 2026.

**Hook contract for Shot 01.** The first 2 s must contain the literal cracking-stone + golden-light burst (not "lead up to" it). Stage 4 should encode this as an explicit FR on `shotlist.md` Shot 01: "frame 0–2 s = visible fracture + light burst, no slow lead-in".

**Cover-frame contract.** Stage 4 should add a derived requirement: Shot 01's first ≤ 2 s must double as the de-facto thumbnail (because YouTube Shorts feed pulls auto-frame). The Shot-01 Kling/Seedance prompts should explicitly call this out so the user re-generates if the opening abuse-test fails.

**`publish.md` schema is fully resolved** — Stage 6 worker can fill in titles + description body without further research.

**Cross-publish stays out of v1 scope** but the appendix above future-proofs a one-paragraph follow-up if the user later wants 抖音 / 视频号 variants.

## 5. Open questions surfaced

- **Title voice — should it explicitly invoke 《黑神话: 悟空》?** Two camps: (a) 蹭流量 = 更高 CTR + 更准受众; (b) 不蹭 = 视觉风格自证 + 不被算法分到二创/同人池. Stage 4 should default to **不蹭** (visual register already does the work; allows the piece to be its own IP), but call this out for user override.
- **Should we caption-overlay the title for the first 1.5 s?** 2026 data says on-screen text in the hook gives +18 % watch time, but `revised_prompt.md` out-of-scope explicitly forbids text overlays in v1. Recommend hold the line for v1; flag as a v2 lever.
- **English-language publish variant for non-Chinese YouTube Shorts audience?** Out of scope per stage-2 interview note. Defer to user follow-up.
- **Cover image generation tool.** If user wants a separate 1080×1920 still-poster (over and above relying on Shot 01 抽帧), they'll need a separate Seedream prompt — not currently in the deliverables list. Flag as small follow-up.
