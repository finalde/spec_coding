# Follow-up draft 056 — 2026-06-17
按用户《EP2 全镜优化方案》改 EP2 全 14 镜 prompt（台词去机器化/情节衔接/运镜影视化/节奏/表演拟人化），并把这些原则融入 skill。两处异议经用户裁定。

---
target_stage: 6
target_artifacts: [episodes/ep02/**, characters/c1_裴知秋, arc_outline.md, style_guide.md]
severity: medium
---

## 用户裁定的两处异议
1. **签名台词**：用户的新 S03 宣言替换全剧锁定签名句。裁定=**全剧换新宣言**。新签名（白话·byte-identical 锁定）：「总有一天，我会站上武神之位，让你们所有人都仰起头来看我」。已全量替换：ep02(script/dialogue/shotlist/shot03/source_novel/publish/all_shot_prompts) + characters/c1 标志台词&弧光 + arc_outline(EP71-80/EP2/EP75) + style_guide 改写示例。
2. **白话 vs 文言**：用户部分新台词偏文言。裁定=**全部白话化**。今日之辱→今天的屈辱；他日/登临武神之位/皆要仰视→站上武神之位/仰起头来看我；莫测道韵→说不清的气机；经脉尽损→丹田碎了(canon)。

## EP2 全 14 镜优化（14 worker 并行·parent 锁 spine+OPT_CONTEXT 后 fan-out）
- 台词去机器化+白话（S01 区区废物大放厥词 / S02 系统"绑定成功体魄重塑中"+裴知秋"百倍讨回" / S03 新白话宣言 / S04 凌虚子白话生疑 / S08 系统"僻静处稳固修为"+裴知秋"我说了算" / S10 玉佩白话）。
- 运镜影视化：S01 侧方动态分层(裴昭朝向统一)、S02 侧后跟移微推锁侧脸、S03 跟拍门前微滞推门外天光、S04 远景极速推脸、S07 低位跟拍拉长光影、S11 低位仰拍随孤影极缓抬升压迫、S13 上下分镜双区、S14 纵深极速推进黑屏卡点。
- 表演拟人化：微表情层次(S05 回望先怅然转决绝、S06 步伐虚浮渐沉稳、S09 自然突发诧异)。
- 藏锋：能量入体只内在感+眼底锋芒、无金光入眉心/裂纹/光柱(全集校验零真实泄露)；描述符 byte-identical(1 distinct)；台词 v2 零字幕 token；时长合计 95s(S03 10s)。
- 重生 all_shot_prompts.md 快照。

## 融入 skill（下次一次性过关）
- ai_video__camera_master：单镜审查加「影视化动态运镜铁律」（杜绝死板固定机位/呆板对称、微推拉/虚实/情绪特写/动态机位、远景极缓抬升/跟移贴步伐/双区分镜）。
- ai_video__action_master：加 A7「表演拟人化·情绪层次」（去机械完美走位、关键情绪给层次/转折）。
- ai_video__dialogue_master：D1 加「真人脱口而出·禁规整书面长句/念稿」。
