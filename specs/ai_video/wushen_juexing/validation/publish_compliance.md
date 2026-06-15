---
worker_id: level-specialist-06-publish-compliance
stage: 5
role: level-specialist
level: publish_compliance
status: complete
blockers: []
confidence: high
---

# 验证层：publish_compliance（发布元数据 + 平台合规）

适用工件：`ai_videos/wushen_juexing/episodes/ep01/publish.md`，并兼查 EP1 钩子镜构图、体质/境界命名与羞辱桥段。
依据：spec FR-11、NFR-5、NFR-6；findings/angle-hongguo-fanqie.md §3；validation/ai_video.md 移动 #5、#6。

本层的「自动可阻断」规则只判断**字段在场与字面约束**（机检）；涉及主观审美/平台审核尺度的项一律降级为 `requires_manual_walkthrough`，绝不自动阻断。

---

## P-1 publish.md 文件存在且非空 — blocker

- 检查：`ai_videos/wushen_juexing/episodes/ep01/publish.md` 存在且去除空白后非空。
- 不存在或空 → `blocker`（移动 #6：缺失/部分=blocker）。

## P-2 标题字段存在且 ≤30 中文字 — blocker

- 检查：`publish.md` 含主标题字段（如 `标题:`）；标题中文字符数（含标点）≤ 30。
- 缺失，或中文字数 > 30 → `blocker`（FR-11 + 移动 #6）。
- 机检建议：取标题行值，统计中文块字符（含全角标点）计数 ≤ 30。

## P-3 口语化钩子副标题存在 — blocker

- 检查：含独立的「口语化钩子副标题」字段（与主标题分离的一行钩子句，如「全族跪求…」式）。
- 缺失 → `blocker`（FR-11；副标题与主标题是两个字段，不可合并替代）。

## P-4 简介字段存在且 ≤200 中文字 — blocker

- 检查：含 `简介:` 字段；简介正文中文字符数 ≤ 200。
- 缺失，或 > 200 字 → `blocker`（FR-11 + 移动 #6）。
- 内容应亮出「被废→觉醒→逆袭」弧（findings §2.5）；弧缺失但字段在场 → `warning`（提示补足身份反转预期）。

## P-5 Hashtags 数量 ∈ [5,10] — blocker

- 检查：含 hashtags 字段；解析出的标签条目数 ≥ 5 且 ≤ 10。
- 缺失，或条目数 < 5 或 > 10 → `blocker`（FR-11 + 移动 #6）。

## P-6 封面建议且指明具体镜号 — blocker

- 检查：含「封面建议」字段，且明确指向 EP1 某一镜（如「第NN镜」/「shotNN」），不得只写「选高光帧」泛指。
- 缺失，或未指明具体镜号 → `blocker`（FR-11 + 移动 #6）。
- 该镜号须落在 EP1 shotlist 实际镜号范围内 → 越界为 `blocker`。

## P-7 变现模式 = `IAA 免费+广告`，禁付费充值 — blocker

- 检查：含 `变现模式:` 字段，值含「IAA 免费+广告」（或等价「免费+广告分成」）。
- 缺失字段 → `blocker`。
- 出现「付费充值 / 付费墙 / 第N集解锁充值 / 充值卡点」等付费小程序剧字样 → `blocker`（红果是 IAA，无付费墙；findings §2.1、spec Out-of-scope）。

## P-8 题材标签齐全 — blocker

- 检查：题材标签字段须含全部五项：`男频` / `古风玄幻` / `系统流` / `逆袭` / `武神`（逐项命中，缺一即不合格）。
- 缺字段，或缺任一标签 → `blocker`（FR-11 + findings §3.7）。

## P-9 总集数=80、推广关键词预留 — blocker

- 检查：含 `总集数: 80`、`推广关键词:` 预留 4–5 字（用于抖音投流拉新）。
- 任一字段缺失 → `blocker`（FR-11）。
- 推广关键词在场但字数不在 4–5 字 → `warning`（findings §2.5 平台限制；可调）。

## P-10 前72小时高热运营提示存在 — blocker

- 检查：含运营提示，明确点到「前 72 小时高热窗口」（前 3 集钩子最密 / 每集结尾 cliffhanger 任一具体化均可，但 72h 窗口必须显式）。
- 缺失 → `blocker`（FR-11；findings §2.1 首月分账前 72h 占 60% 权重，经济杠杆）。

## P-11 [已废止 follow-up 010] prompt 不写比例 — 不再校验

- follow-up 010：所有 prompt 不写 `比例`，用户在平台自行设画幅；本检查废止。
- （不再校验比例字段）
- （follow-up 010 废止：prompt 不写比例，不再校验画幅）

---

## 需人工走查项（主观，不自动阻断）

## P-12 平台合规：神/帝/王字样 + 羞辱桥段审核尺度 — requires_manual_walkthrough

- 触发：world.md 体质/境界命名含「神/帝/王」字样（武神、武帝、武王、王体资质等），且 EP1 含「当众废丹/除族/退婚羞辱」桥段。
- 动作：发 `validation.requires_manual_walkthrough`，提示语：「出片前对照红果/番茄创作者规范与敏感词表，复核(a)『武神/武帝/武王/王体』等夸张称谓是否触发敏感词或夸大宣传红线；(b)EP1 废丹/除族/退婚羞辱是否控制在审核尺度内（不血腥过度、不低俗化）。」
- 理由：NFR-5 + findings §4 未取得官方敏感词/审核红线一手细则；尺度判断主观，**不自动阻断**。

## P-13 EP1 钩子镜构图主观性 — requires_manual_walkthrough（移动 #5 novel hook composition）

- 触发：EP1 shotlist 标注的 hook 镜（前 ≤3s「当众废丹/除族」）与 cliffhanger 镜（末镜宗门暗线）。
- 动作：发 `validation.requires_manual_walkthrough`，提示语：「人工复核 EP1 hook 镜与 cliffhanger 镜构图：主体是否在上三分之一、动作是否在 0.5s 内启动、是否无世界观旁白前置（前 10 秒铁律）。」
- 理由：移动 #5 — novel hook 构图主观，surface 为 requires_manual_walkthrough，非自动阻断。
