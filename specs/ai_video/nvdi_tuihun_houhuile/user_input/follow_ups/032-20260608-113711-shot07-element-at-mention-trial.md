---
target_stage: 6
target_artifacts:
  - ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shots/shot07/shot07.md
severity: medium
---

# Follow-up draft 032 — 2026-06-08
> **⚠️ 已被 FU033 撤销并修正诊断。** shot07 已改回 `_place_holder`; 本文「软绑定 vs 硬绑定」的根因判断有误(用户本就在用 @element 硬绑定)。正确根因与结论见 `033-*.md`。下文保留作审计轨迹。

试验 Kling 3.0 Omni 的 Element + `@元素名` 方案,根治 shot07「两道背影都成陈凡」。仅 shot07 改动作验证;有效后再决定是否全量迁移其余 27 shot。

## 背景 (research 结论)
Kling 3.0 Omni 有 Element 库 + `@元素名` 硬绑定 + 多视角元素(正/左¾/右¾/**背面**)。
- `@` 是硬绑定(命名元素路由到该主体), 强于自由文本 `_place_holder` 软提示。
- 元素含**背面图** → 解决"背影没脸、参考(正脸)用不上"的根因。
- 用户旧用法是「多图参考」(框选+正脸视频, 软绑定无背面) → 才会两道背影塌成被强调的陈凡。

## 落地 (仅 shot07)
- shot07 prompt 内 `{拼音}_place_holder` → `@拼音`: @taijian / @chenguogong / @chenfan; 场景 `bg1_朝北_长案主位_place_holder` → `@bg1`。
- 台词及对白内自然名(陈凡/太监)不动(沿用 FU024/025, 台词不 token 化)。
- Reference uploads 行改注: 库内预建元素, 每个 4 视角图含**背面过肩**。

## 验证步骤 (用户侧)
1. Kling 3.0 Omni 元素库建 @taijian / @chenguogong / @chenfan, 各用 4 视角(正/左¾/右¾/背面)合成; @bg1 用 bg1 图。
2. 用改后 shot07 prompt 重生成, 看两道背影是否各按元素(深紫朝服银发 vs 玉白袍黑长发)正确区分。

## 待定
- 仅当 shot07 验证有效, 才: (a) 全量迁移 27 shot 的 token → @, (b) 把「元素优先 + 4视角含背面 + @硬绑定」写进 ai_video.md。当前 ai_video.md **未改**。
- 前提: 用户账号须为 Kling 3.0 Omni(支持 @ 语法); 旧版(1.6 Elements / 2.x 多图参考)无 @名, 需另案。

## 偏离说明
shot07 暂与其余 27 shot 的 `_place_holder` 约定(FU023/029)不一致——这是有意的 A/B 验证, 非约定变更。验证结论出来前不扩散。

## 核查
shot07 残留 _place_holder=0; @taijian/@chenguogong/@chenfan/@bg1 到位; 台词自然名完好; LF 保持; 反引号包裹不变。
