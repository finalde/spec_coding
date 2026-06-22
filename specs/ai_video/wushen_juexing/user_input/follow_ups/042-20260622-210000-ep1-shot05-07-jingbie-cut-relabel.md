# Follow-up draft 042 — 2026-06-22
EP1 shot05→06→07 由「承接」改判为「硬切」：实测接缝两帧 PSNR 仅 7–10dB（完全不同的两张图），且是景别跳切（面部特写→中近景含主观POV→面部特写），按 ai_video.md 跨镜首帧承接规则 景别跳切属硬切、不可链帧。原承接标注是错的，合成器据此对其做接缝微裁也是错的。改判后合成器对这三处按硬切处理（不裁、干净切）。

---
target_stage: 6
target_artifacts:
  - 5_6_分镜与prompt/episodes/ep01/shots/shot05/shot05.md
  - 5_6_分镜与prompt/episodes/ep01/shots/shot06/shot06.md
  - 5_6_分镜与prompt/episodes/ep01/shots/shot07/shot07.md
  - 5_6_分镜与prompt/episodes/ep01/all_shot_prompts.md
severity: medium
---

## 背景
用户要让 EP1 合成成片接缝更顺，提议「只在首尾帧做处理，确保 100% 对齐再各延长 0.1s」。查证否决该思路：
- 合成阶段无法「对齐」——接缝两边是两张独立生成的不同图，没有任何平移/裁切能把一张变成另一张；对齐只能发生在生成时（把上一镜末帧塞进模型「首帧」槽）。
- 「延长/定格首尾帧」只对两帧本就近乎相同（PSNR>40）的真承接缝有效；这里 PSNR 7–23，定格 0.1s 再硬切到另一张图＝在硬切前插一段卡顿，更糟。

## 根因
EP1 声明的「承接」缝里：
- shot05→06、shot06→07：PSNR 7、10dB＝完全不同的两张图，本质是景别跳切（特写↔中近景含主观POV），按 ai_video.md「跨镜首帧承接」规则的「景别跳切→硬切」条款，原承接标注错误；且 `shot06_firstframe.png`/`shot07_firstframe.png` 根本不存在，生成时压根没用上一镜末帧。
- shot10→11→12：背身走位真连续（PSNR 23），handoff PNG 齐备但现有渲染没从末帧续生，需重生成（见下条 regen 清单），不在本 follow-up 改标范围。

## 本 follow-up 改动（已落地）
shot05/06/07 三镜 + all_shot_prompts.md 聚合：
- shot06、shot07 的 `衔接` 由「承接 shotNN 末帧」改为「硬切（独立首帧·无承接帧）——景别跳切…非连续承接」。
- 连带清理首帧/末帧承接元数据：删 `本镜首帧=>`/`本镜末帧=>` 参考句柄、`首帧:`/`末帧:`/`首末帧:` 起止句、`参考分配` 里的首/尾帧锁定子句、Reference uploads 的「上一镜末帧」条目。
- shot05 因不再被 shot06 承接，删其 `尾帧锁定` 行与末帧参考。
- 剧情/台词/动作/光线一字未动（仅相机承接元数据）。

## 仍需用户侧重生成（生成缺陷，合成改不了）
- shot11、shot12：用已备 `shot11_firstframe.png`/`shot12_firstframe.png` 重出，真从上一镜末帧续生，修 11→12 背身位姿跳。
- 镜头内卡死（边说话边冻画，如 shot06/08）：重生让画面在说话段保持动作。
