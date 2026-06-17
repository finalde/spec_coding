# Follow-up draft 049 — 2026-06-16
确保 EP2 开场与 EP1 结尾连贯（消除"气场反转"重演的突兀），并把"改动剧本/台词后默认自检连贯性"写进标准流程。

---
target_stage: 6
target_artifacts:
  - episodes/ep02/shots/shot01/shot01.md
  - episodes/ep02/script.md
severity: medium
---

## 指令
- **跨集边界连贯**：EP1 末镜（S14）已让裴知秋"撑直佝偻脊背、气场由颓转锋、撂下'我也不稀罕'"。EP2 开场（shot01 / script 场景一）不得重演这一"撑身气场反转"beat——改为承接 EP1 已反转的状态：脊背已挺直、气场未散，直接续上"把话彻底说绝"。小说原文/Summary/情节/动作/script 场景一同步。
- 顺带把该镜标志断绝台词白话化并全局 byte-identical 同步（"用不着你赶。我裴知秋今天把话撂在这儿——从今往后，我跟镇北王府恩断义绝，这扇门，我自己走出去！"）。
- **流程通则（common-level，已写入 harness）**：每次改动剧本/台词（script.md / dialogue.md / shot `台词:` / 镜头剧情）后，**默认自动**自检叙事连贯性，无需用户提醒——查相邻镜衔接 + 跨集边界（首/末镜对照上一集结尾/下一集开场），前集已发生的关键转折不重演只承接。已落地 CLAUDE.md「General coding rules」+ ai_video.md「2026-06-16 amendment」。
