---
target_stage: 6
target_artifacts:
  - ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shots/shot07/shot07.md
severity: medium
---

# Follow-up draft 033 — 2026-06-08
撤销 FU032 的 shot07 `@element` 试验, 把 shot07 改回 `_place_holder` 状态; 28 shot 重新统一约定。**本条取代/修正 FU032。**

## 修正诊断 (FU032 诊断有误)
FU032 把根因写成「用户用旧的多图参考/软绑定」——**错**。用户澄清: 本就在 Kling 3.0 Omni 用 `placeholder=@element` 做硬绑定, 且大部分镜头 work。
正确根因 (为什么 @element 硬绑定大部分 work、偏偏 shot07 双背影翻车):
- @element 绑的是**身份**, 身份主要靠**脸**落实; 双背影把最强判别通道(脸)抽走。
- 加之**两人贴一起、同跪姿同景别** → 模型 subject 分区模糊, 可能只绑一个区。
- 加之 **@chenfan 被反复提及/是台词焦点** → 注意力失衡, 暧昧区域偏向 @chenfan。
- 最可能的具体原因: **元素是用正脸图建的、缺互不相同的「背面图」** → 正面镜全对、纯背面镜抓瞎 (与"大部分 work、只背影镜翻车"吻合)。
→ 所以问题**不是 token 格式 (placeholder vs @)**, 切换 token 格式无意义; 真正的修复在**给元素补互不相同的背面图** + 拉开两背影 + 削弱单人注意力。FU031 的衣色/发型文字区分是有效兜底, 保留。

## 落地
- shot07: `@拼音` → `{拼音}_place_holder` 全部还原 (@taijian/@chenguogong/@chenfan/@bg1 → *_place_holder); Reference uploads 行还原原文。残留 @=0, token 计数与 FU032 改动前一致, LF 保持。
- 其余 27 shot 本就未动。
- ai_video.md 未改 (FU032 本就没改; 不引入 token 格式规则)。

## 结论 (沉淀方向, 非 token 改动)
真正要写进规范的不是"placeholder vs @", 而是: **当人物只露背影/远景(无脸)时, 其 Kling 元素必须含「背面视角图」, 且同框多个无脸主体的元素背面要互不相同**; prompt 侧配 FU031 的背影文字区分 + 主体拉开 + 注意力均衡。待用户用"含背面图的元素"验证有效后再正式入 ai_video.md。

## 核查
shot07 残留 @=0; *_place_holder 还原 (taijian11/chenguogong7/chenfan10/bg1 2); 台词自然名完好; CRLF=0; 反引号包裹不变; 与 27 shot 约定重新一致。
