# 中文 vs 英文锁定文本块校准渲染 — `_performances/` 库级前置实验

> **状态：待渲染（pending_render）。** 这是 stage 6 的第一个渲染工作单元，先于任何 `perf_NNNN` 的批量验证。结论决定整库 entry body 是否需要「中文措辞规约」。

## 为什么需要这条校准

所有公开的 AI 视频表演服从性实测（Segmind / Curious Refuge 等）都用**英文 prompt**。本库全部内容中文（FR-3），「中文肌肉描述（如『眉内角上提、嘴角下拉抿紧』）是否与英文同样 land」是 v1 的根基性未验证假设。若中文系统性弱于英文，整库 body 撰写规则需调整——这是低成本早期去风险，必须在批量撰写前跑。

## 实验设计（控制变量 = 只变语言）

- **对象**：压抑隐忍·强度3·内敛·眼神（中段最可控，校准信噪比最高）——取 `perf_0003` 的锁定文本块。
- **两版**：写语义等价的「中文版」与「英文版」锁定文本块（同一组 FACS 底表动作，仅语言不同）。
- **测试台**：完全沿用 `_testrig.md`，唯一变量 = 语言。双模型各渲中 / 英两版 = **4 次渲染**。
- **打分**：按三轴（表演达意 / 情绪可识别 / 是否过火，各 1–5）盲看打分。

### 中文版（取自 perf_0003 锁定文本块）

```
眼眶下缘极淡泛红、泪膜在睑缘成形但不滑落；上睑微抬强压、眨眼频率刻意放慢以锁住泪膜；视线先垂向斜下方一瞬、随即强行抬回平视；眉内角极轻上提（忧的痕迹）而眉峰不动；喉头一次不易察觉的吞咽。全程嘴部保持平静、不参与（上下脸冲突即「强忍」的读法）。
```

### 英文版（语义等价）

```
Lower eyelid rims faintly redden; a film of tears forms along the lash line but does not fall. Upper lids lift slightly to hold it back; blink rate deliberately slows to lock the tear film in place. Gaze drops to the lower diagonal for an instant, then is forced back to level. Inner brow corners raise very slightly (a trace of grief) while the brow peaks stay still. One barely perceptible swallow at the throat. The mouth stays composed and uninvolved throughout — the upper/lower-face conflict is the read of "holding it in."
```

## 渲染记录（待回填）

| 语言 | 模型 | 版本/日期 | 表演达意 | 情绪可识别 | 是否过火 | 笔记 |
|------|------|-----------|----------|-----------|----------|------|
| 中文 | kling | _ | _ | _ | _ | _ |
| 中文 | seedance | _ | _ | _ | _ | _ |
| 英文 | kling | _ | _ | _ | _ | _ |
| 英文 | seedance | _ | _ | _ | _ | _ |

## 判读规则（渲染后填写结论）

- **中文分 ≈ 英文分（任一轴差 ≤1）** ⇒ 中文假设成立，照计划批量撰写中文 body。
- **中文系统性低于英文（达意 / 可识别差 ≥2）** ⇒ 触发 spec 级警报：需在 entry body 增「中文措辞规约」（如调整为更口语的画面词、或在 metadata 混排 AU 号辅助），或回 stage-4 调整 body 撰写规则。

## 结论

> _（待 4 次渲染 + 打分后填写。在此之前，下方所有 `perf_NNNN` 的中文 body 均为「假设中文 land」的待验证产物。）_
