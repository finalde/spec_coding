# Angle — Platform conventions（抖音 + YouTube Shorts 发布规范）

Run: mozun_chongsheng-20260509-164205
Stage: 3 (research) — angle 5 / 5
Worker: researcher-05-platform-conventions
Date: 2026-05-09
Inputs consulted: `user_input/revised_prompt.md`, `interview/qa.md`

---

## 1. 本角度覆盖范围

聚焦《魔尊归来》v1 上线主战场——**抖音（中文短剧主场）+ YouTube Shorts（海外华语 + 仙侠 cdrama 圈层）**——的元数据与分发规范，为 stage 4 spec 的 `episodes/epNN/publish.md` 模板和项目级 `publish/` 目录给出可直接落地的栏位与文案规则。

回答 6 个问题：(1) 标题模板与字数 / 钩子；(2) 描述与简介格式；(3) 封面 9:16 安全区与文字 overlay；(4) 抖音 / YouTube hashtag 选择策略；(5) 60 集的发布节奏（合并 / 每日 1-2 集 / 拆季）；(6) 海外双语字幕惯例。覆盖**平台共性**（9:16、强钩子、悬念结尾、前 3 秒留人）与**仙侠题材专属**（修为体系名词、魔尊 / 重生 trope 的话题词、白衣 vs 黑袍封面对比）。

不覆盖：投流 / 充值小程序变现链路（v1 不涉及）、备案号 / 版权中心提交流程（用户运营层、非创作 spec 层，但相关 URL 列在 §2.6）。

---

## 2. 关键发现

### 2.1 抖音短剧标题命名惯例

- **字数**：抖音视频标题官方支持 ≤ 55 个汉字，但短剧爆款标题集中在 **15–25 字**——一行手机屏可读完不被截断。封面文字另算，标题正文还要留位置给 hashtag。([青瓜传媒《33 个开头模板》总结的爆款短文案规律](https://www.opp2.com/348214.html))
- **钩子词前置**：第一句话必须出现"虐 / 爽 / 重生 / 反杀 / 我的 / 当年 / 终于"等情绪词。猎奇、情绪张力大的句子放最前，"不要让观众有思考时间"（出处见 [TaoKeShow《短剧爆款剪辑创作技巧》](https://www.taokeshow.com/55553.html)）。男频爆点元素清单含"战神 / 重生 / 出狱 / 暴富 / 太子 / 女帝 / 美女总裁"等。
- **集数标识**：标题或描述中**必须明确集号**。短剧惯例两种写法并存：
  - `《剧名》第N集 ｜ 钩子句`（前置集号）
  - `钩子句｜《剧名》EP NN`（后置集号）
- **数据门槛**（影响标题/封面投入度）：2025 年抖音"爆款剧"门槛 = 实时热度峰值 ≥ 3 亿 + 主话题播放量 ≥ 100 亿；"热播剧" = 1.5 亿 / 50 亿（[36 氪《2025 短剧年终总结》](https://36kr.com/p/3611356355375875)）。爆款本身就要求强标题强封面。

### 2.2 抖音描述 / 简介 hashtag 与 hashtag 数量

- **描述总长度**：业内实测 80–150 字甜区。前 30 字最重要——刷信息流时只展示前一行。
- **hashtag 数量**：抖音短剧主流账号每集挂 **5–10 个**，超过 10 后权重边际下降。结构 = 1 个主剧名话题 + 1 个剧种话题 + 2-3 个 trope / 类型话题 + 1-2 个广义热门话题。
- **仙侠 / 重生赛道头部话题**（量级来自 36 氪 / DataEye 报告与抖音平台话题页）：
  - `#短剧` 全平台主标签（短剧推广通用）
  - `#仙侠` / `#玄幻仙侠`：玄幻仙侠题材关联剧 155 部，2025 年榜首单剧《斩仙台下》播放量增量破 10 亿（[36 氪《头部 IP 连出短剧爆款》](https://36kr.com/p/3602183676772870)）
  - `#修仙短剧` / `#沙雕修仙动画` 211.6 亿累计播放量
  - `#重生` / `#爽剧` / `#打脸` / `#复仇`
  - `#男频短剧`（魔尊归来定位偏男频）
  - `#国风` / `#古风` / `#仙气飘飘`
- 用户文档要求：发布前必须备案（2024-06-01 起），抖音版权中心 2025 年升级（[腾讯新闻《抖音短剧版权中心上线漫剧操作指南》](https://news.qq.com/rain/a/20251127A04G5900)；[南都《抖音集团成立短剧版权中心》](https://m.mp.oeeee.com/a/BAAFRD0000202505291090859.html)）。备案号写入描述末或 publish.md 的元数据栏。

### 2.3 抖音封面 9:16 安全区 + 文字 overlay

- 视频与封面尺寸 **720×1280 / 9:16**（[知乎《抖音短视频封面制作技巧》](https://zhuanlan.zhihu.com/p/150261928)）。
- **文字数量**：封面文字 ≤ 15 字最优，绝对上限 30 字。短剧封面常见规格：**主标题 1 行 8-12 字 + 集数小字**。
- **文字位置**：居中或居中偏下使画面稳定，最高位置不能超过画面上 1/8（被顶部状态栏 / 头像挡住）；底部安全区约下 18%（被进度条 / 点赞按钮遮）。换算到 720×1280：**安全文字带 = y ∈ [160, 1050]**。
- **主体（人物 / 关键道具）位置**：人物胸像置于上 1/3 线（rule of thirds），脸部居中，背景留出对比色块给文字（[数英《三种常见的抖音封面》](https://www.digitaling.com/articles/461383.html)；[Canva《抖音一夜涨粉上万的视频封面》](https://www.canva.cn/learn/douyin-video-cover/)）。
- **短剧封面专属**：影视公司常用三联屏 / 双联屏 + 大字标题模式（[脉脉《影视公司怎么做抖音短剧｜封面》](https://maimai.cn/article/detail?fid=1757145253&efid=LR5XZmcU7GvqCsogtIe9Vw)）。仙侠题材封面常见构图：左半边白衣伪君子 + 右半边黑袍魔尊 / 红瞳特写 + 顶部血色大字钩子。

### 2.4 YouTube Shorts 标题 / 描述 / hashtag

- **标题**：YouTube Shorts 标题硬上限 100 字符。爆款短剧海外频道（DramaBox、ReelShort）实测甜区 **40–70 字符**——移动端两行内可读完。仙侠 cdrama 频道惯例 = `Cnen 双语 + EP NN + 钩子`。
- **3 层 hashtag 公式**（[Fliki《Best YouTube Shorts Hashtags in 2026》](https://fliki.ai/blog/youtube-shorts-hashtags)；[Stack Influence《100 Most Popular YouTube Hashtags 2025》](https://stackinfluence.com/100-most-popular-youtube-hashtags-in-2025/)；[Minvo《From Zero to Viral》](https://minvo.pro/blog/from-zero-to-viral-the-hashtag-formula-for-youtube-shorts)）：
  - **第 1 层 平台基础**：`#shorts`（14 亿+ 视频量）+ `#youtubeshorts`
  - **第 2 层 题材**：`#cdrama` / `#xianxia` / `#xianxiadrama` / `#chinesedrama` / `#wuxia` / `#shortdrama` / `#duanju` / `#modernxianxia`
  - **第 3 层 长尾 / 剧情**：`#revenge` / `#reincarnation` / `#cultivation` / `#demonlord` / `#chinesefantasy`
  - 单条 Short **5-8 个 hashtag** 最优（haulpack、minvo 共识）；超过 15 个被 YouTube 视为 spam 风险。
- **描述**：前 100 字符是搜索摘要主区域。海外双语账号惯例 = 中文剧情 1-2 句 + 英文 logline 1 句 + hashtag 块 + 频道全集播放列表链接。
- **YouTube #xianxiadrama 已是平台官方 hashtag 页**，参见 [YouTube #xianxiadrama 标签页](https://www.youtube.com/hashtag/xianxiadrama)，并且 [#抖音短剧](https://www.youtube.com/hashtag/%E6%8A%96%E9%9F%B3%E7%9F%AD%E5%89%A7) 在海外华语圈层亦有专属页（中文搜流量入口）。
- **海外仙侠话题词清单**（出处 [best-hashtags.com #xianxia](https://best-hashtags.com/hashtag/xianxia/)）：`#chinesedrama #cdrama #wuxia #immortality #ashesoflove #cultivation #danmei`——可见**英文圈"xianxia"已成自有词条**，不需翻译为"Chinese fantasy"。

### 2.5 60 集发布节奏

- **核心结论**：60 集**不一次性合并发布**，**不分两季拆季**，**采用每日 1-2 集的连发节奏**。
- **依据 1**：抖音短剧推广实操经验——"每天剪辑 3-6 集，每集 5 分钟以内，每 2 小时发布一集"（[知乎《零粉丝如何去做短剧推广？》](https://zhuanlan.zhihu.com/p/13913971725)）。这是付费短剧的高速度版；自有原创短剧节奏可放慢到**每天 1-2 集**。
- **依据 2**：YouTube Shorts 出海运营——"按集维度 + 较高发布频率，建议每天 1 条或每两天 1 条"（[知乎《油管短剧运营从 0 到 1》](https://zhuanlan.zhihu.com/p/32696489759)、[CSDN《YouTube Shorts 优化指南》](https://blog.csdn.net/snowsnowip/article/details/146100660)）。
- **依据 3**：免费看剧引流模式——前 8-12 集免费、后续付费 / 解锁（[同上 知乎实操贴](https://zhuanlan.zhihu.com/p/13913971725)）。这意味着**前 12 集必须每日连发以维持留存**；之后 13-60 集节奏可按周维度规划（每周 5-7 集）。
- **推荐节奏**（写入 spec 默认）：**day 1-12 每日 1 集（强冲量 + 留存）→ day 13-30 每日 2 集（钩子卷恢复期密集）→ day 31-60 每日 1 集（终战卷收尾）**。总周期约 ~40 天完成首发上线。
- 不分两季理由：interview 阶段已锁定"60 集一气呵成、不分两季"；分季会让付费转化下降（用户流失风险）。海外 YouTube 频道可考虑**完结后再做合集长视频版（compilation）**，作为 v2 follow-up。

### 2.6 海外双语字幕惯例

- **主流方案**：中文原声 + 硬字幕双语（中文上 + 英文下）—— ReelShort / DramaBox 类海外大厂统一做法（[bridgingnews《Viral Micro-Drama Drives $1B Global Surge》](https://app.ichongqing.info/mixmedia/a/202508/08/WS68956519e4b08bd53e2b4bfc.html)；[mediaio《How to Translate Chinese Short Dramas》](https://www.mediaio.net/translate/translate-chinese-short-dramas-step/)）。
- **仙侠专属翻译规则**：classical Chinese 与修为术语必须**人工校对**——"练气 / 筑基 / 金丹 / 元婴 / 化神 / 渡劫"建议保留汉字 + 英文同位语（如 `元婴 Yuanying / Nascent Soul`）以保留题材辨识度。AI 翻译先跑、母语 reviewer 终审是公认 best practice（[mediaio 同上](https://www.mediaio.net/translate/translate-chinese-short-dramas-step/)）。
- **字幕样式**：上中文 28-32px、下英文 22-26px、白底黑边或黑底白字、底部居中、占画面下 1/6；不要遮 9:16 安全区底部 18% 的进度条 + 点赞按钮区。
- **YouTube auto-translate**：YouTube Studio 支持开启自动翻译生成多语 CC，但 xianxia 术语 auto-translate 错误率高，建议**自有 .srt 双语字幕硬上**而非靠 YouTube auto-CC。

---

## 3. 对 spec 的具体建议

以下规则建议直接写进项目级 `publish/templates.md` 与每集 `episodes/epNN/publish.md`。

### (a) 抖音标题模板

```
《魔尊归来》第{NN}集 ｜ {一句钩子词，8-15 字，含情绪 / 反转关键词}
```

钩子句必须含**至少 1 个**：`重生 / 反杀 / 当年 / 三千年 / 我倒要 / 这就 / 终于 / 看我 / 谁敢 / 你们`

示例：
- `《魔尊归来》第01集 ｜ 三千年前他们镇压我，今日我重生归来`
- `《魔尊归来》第07集 ｜ 五大宗主，当年的债今日我来收`
- `《魔尊归来》第25集 ｜ 元婴大成，正派的伪面具该撕了`

字数严控：剧名 + 集数 + 钩子总长 ≤ 25 字（不含 hashtag）。

### (b) 抖音 hashtag 列表（5-10 个，含热度估）

每集 publish.md 强制带前 5 个；6-10 按本集主题挑：

| 优先级 | hashtag | 量级 / 类型 | 说明 |
|---|---|---|---|
| P0 | #短剧 | 千亿级，平台主标签 | 必带 |
| P0 | #仙侠 | 百亿级，玄幻仙侠头部话题 | 必带 |
| P0 | #魔尊归来 | 自建专属话题 | 必带（项目主话题，对标"主话题播放量"指标） |
| P1 | #重生 | 高热度 trope 词 | 必带 |
| P1 | #爽剧 | 男频通用爆点词 | 必带 |
| P2 | #修仙短剧 | 题材长尾 | 5-7 集后视情况上 |
| P2 | #国风 / #古风 | 视觉调性词 | 高潮集 / 视觉强集挂 |
| P2 | #打脸 / #复仇 | 情节 trope | 反杀集 / 揭真相集挂 |
| P3 | #男频短剧 | 受众定向 | 项目前 5 集打受众用 |
| P3 | #AI短剧 / #AI动画 | 制作方式 | 视宣发策略选；AI 标签近 1 年涨势猛（[知乎《AI 漫剧爆火》](https://zhuanlan.zhihu.com/p/1999596272106116037)） |

### (c) 抖音封面建议

写入 `publish/cover_spec.md`：

- **画幅**：720×1280 (9:16)，导出 PNG / JPG。
- **主体**（人物 / 道具）：置于**上 1/3 线**（y ≈ 320-560），脸部 / 关键道具放黄金分割点。仙侠惯例构图 = 左白衣伪君子 + 右黑袍魔尊红瞳。
- **大字标题**：8-12 字，居中或居中偏下（y ≈ 700-950 安全带），字号 ≥ 80pt，描黑边 + 主辅色金（#a8842c）填充。例：`重生归来 灭尽伪君子` / `当年镇我 今日血债血偿`
- **集数小字**：右上或右下角，`EP 01` / `第01集`，字号 30-40pt，深青底色块 #1a3038。
- **安全区**：所有文字 y ∈ [160, 1050]；不放任何关键文字在顶部 1/8 与底部 18%（被状态栏 / 操作栏遮）。
- **配色**：必含项目主色 #0a0a0a 背景 + 护黄金 #a8842c 标题描金 + 米白 #f5f5f0 高光（继承 stage 4 `style_guide.md`）。

### (d) YouTube Shorts 双语标题模板

```
《魔尊归来》EP{NN} | Demon Lord Returns | {English hook, 4-8 words} | #shorts #cdrama #xianxia
```

字符总长 ≤ 90 字符（移动端 2 行内）。

示例：
- `《魔尊归来》EP01 | Demon Lord Returns | Reborn as a Beggar | #shorts #cdrama #xianxia`
- `《魔尊归来》EP25 | Demon Lord Returns | Nascent Soul Awakens | #shorts #xianxia #revenge`
- `《魔尊归来》EP60 | Demon Lord Returns | Final Reckoning | #shorts #cdrama #cultivation`

英文钩子词建议：`Reborn / Awakens / Revenge / Reckoning / Betrayed / Hidden Truth / Bloodline / Final Strike`。

### (e) YouTube Shorts hashtag 列表

每集挂 6-8 个，分 3 层：

| 层 | hashtag | 量级 / 备注 |
|---|---|---|
| 1 平台基础 | #shorts | 14 亿+ 视频量，必带 |
| 1 平台基础 | #youtubeshorts | 必带 |
| 2 题材 | #cdrama | 海外华语剧主话题 |
| 2 题材 | #xianxia / #xianxiadrama | YouTube 已建官方 hashtag 页 |
| 2 题材 | #chinesedrama | 长尾流量 |
| 3 长尾 | #revenge / #reincarnation | trope 词 |
| 3 长尾 | #cultivation / #demonlord | 题材长尾 |
| 3 长尾 | #shortdrama / #duanju | 短剧专属词 |

### (f) 60 集发布节奏建议

写入 `publish/release_schedule.md`：

- **Day 1-12（首卷镇压 + 乞丐重生 ep01-12）**：每日 1 集，固定 19:00-21:00 黄金档发抖音 + YouTube Shorts 同步上线。前 12 集是抖音免费引流主战场，必须连续。
- **Day 13-30（觉醒 + 恢复前段 ep13-30）**：每日 2 集，分 12:00 + 20:00 两档，密集留存高潮节奏 + 配合付费转化（如开启）。
- **Day 31-60（恢复后段 + 反击 + 终战 ep31-60）**：每日 1 集 19:00-21:00，匀速到完结。
- **YouTube Shorts 补充**：终战完结后第 7-14 天发布 1-2 条 **3 分钟合集长视频**（compilation），作为引流到完整频道的钩子（compilation 不算入 60 集计数；标记 v2）。
- **不分两季**（已在 interview Q5.4 锁定）；不一次性合并。
- **抖音备案号**：必须先获得备案号才可上线（[流媒体网《须获得备案号后方可播出》](https://www.tvoao.com/a/218181.aspx)）；备案号写入 publish.md 元数据栏。

---

## 4. 开放问题

留给 stage 4 spec 阶段决定 / 留给用户在 stage 4 收尾时确认：

1. **是否接入抖音付费小程序**（前 12 集免费 + 后续付费解锁）vs **全集免费走广告分成**？决定标题与描述的"解锁观看"提示句要不要加。本 spec 默认为**全集免费**（v1 不接付费链路）。
2. **YouTube Shorts 是否做 5 语种 metadata**（中、英、日、韩、西、印尼）—— ReelShort 已是 5 语种标准（搜索结果中提及）。本 spec 默认 v1 仅出 **中文 + 英文双语**；其余 4 语作为 v2 follow-up。
3. **抖音主话题词最终命名**——`#魔尊归来` 是默认；是否考虑更具记忆点的主话题词（如 `#魔尊乞丐归来` / `#我是魔尊不是乞丐`）？建议 stage 4 由用户在 publish/templates.md 上线前最终敲定。
4. **封面是否做"双联屏 / 三联屏"**模式（多人物拼贴）vs 单主体特写——影响 stage 4 `publish/cover_spec.md` 模板生成。本 spec 默认推荐**单主体上 1/3 线 + 大字标题**。
5. **修为体系英文术语对照表**（练气→Qi Refining、筑基→Foundation Building 等）—— stage 4 spec 阶段需在 `world.md` 增设 `cultivation_terms_zh_en.md`，配合 YouTube Shorts 字幕翻译使用。
6. **抖音备案号**何时获取——影响首集上线日期；是否需要在 stage 4 spec 增加 `publish/filing_checklist.md`？

---

## 引用来源

- [36 氪《2025 短剧年终总结：谁在破圈，谁稳坐头部？》](https://36kr.com/p/3611356355375875)
- [36 氪《头部 IP 连出短剧爆款，2025 年网文平台掘到金了吗？》](https://36kr.com/p/3602183676772870)
- [青瓜传媒《短视频爆款文案 33 个开头模板！》](https://www.opp2.com/348214.html)
- [TaoKeShow《快速 get 短剧爆款剪辑创作技巧》](https://www.taokeshow.com/55553.html)
- [腾讯新闻《抖音短剧版权中心上线漫剧操作指南》](https://news.qq.com/rain/a/20251127A04G5900)
- [南都《抖音集团成立短剧版权中心》](https://m.mp.oeeee.com/a/BAAFRD0000202505291090859.html)
- [流媒体网《须获得备案号后方可播出！多平台公布微短剧备案细则》](https://www.tvoao.com/a/218181.aspx)
- [知乎《抖音短视频封面制作技巧》](https://zhuanlan.zhihu.com/p/150261928)
- [数英《从三种常见的抖音封面中分析封面如何做》](https://www.digitaling.com/articles/461383.html)
- [Canva《抖音一夜涨粉上万的视频封面，都长什么样？》](https://www.canva.cn/learn/douyin-video-cover/)
- [脉脉《影视公司怎么做抖音短剧｜封面》](https://maimai.cn/article/detail?fid=1757145253&efid=LR5XZmcU7GvqCsogtIe9Vw)
- [知乎《零粉丝如何去做短剧推广？一级授权怎么拿？》](https://zhuanlan.zhihu.com/p/13913971725)
- [知乎《油管短剧运营从 0 到 1：全流程工具清单 + 避坑指南》](https://zhuanlan.zhihu.com/p/32696489759)
- [CSDN《YouTube Shorts 优化指南：4 步提升转化率》](https://blog.csdn.net/snowsnowip/article/details/146100660)
- [Fliki《Best YouTube Shorts Hashtags in 2026》](https://fliki.ai/blog/youtube-shorts-hashtags)
- [Stack Influence《100 Most Popular YouTube Hashtags in 2025》](https://stackinfluence.com/100-most-popular-youtube-hashtags-in-2025/)
- [Minvo《From Zero to Viral: The Hashtag Formula for YouTube Shorts》](https://minvo.pro/blog/from-zero-to-viral-the-hashtag-formula-for-youtube-shorts)
- [haulpack《Top 150 Trending YouTube Shorts Hashtags 2026》](https://www.haulpack.com/blog/top-40-hashtags-for-youtube-shorts/)
- [best-hashtags.com《Best #xianxia Hashtags》](https://best-hashtags.com/hashtag/xianxia/)
- [YouTube hashtag #xianxiadrama 官方页](https://www.youtube.com/hashtag/xianxiadrama)
- [YouTube hashtag #抖音短剧 官方页](https://www.youtube.com/hashtag/%E6%8A%96%E9%9F%B3%E7%9F%AD%E5%89%A7)
- [mediaio《How to Translate Chinese Short Dramas: Tips, Tools & Best Practices》](https://www.mediaio.net/translate/translate-chinese-short-dramas-step/)
- [bridgingnews《Viral Micro-Drama Drives $1 Billion Global Surge》](https://app.ichongqing.info/mixmedia/a/202508/08/WS68956519e4b08bd53e2b4bfc.html)
- [Wikipedia《Duanju》](https://en.wikipedia.org/wiki/Duanju)
- [知乎《AI 真人短剧爆火背后：谁在重构短剧创作生态？》](https://zhuanlan.zhihu.com/p/1999596272106116037)
- [DataEye 研究院《2025 年 H1 微短剧行业数据报告》](https://pdf.dfcfw.com/pdf/H3_AP202507111706795697_1.pdf?1752227449000.pdf=)
