# Follow-up draft 080 — 2026-06-28
角色卡原子性：要么完整建出来、要么不建，没有中间状态，turntable 建立视频 prompt is a must

---
target_stage: 2
target_artifacts:
  - .claude/skills/ai_videos__格式契约/SKILL.md
  - 2_世界观人设/characters/c20_锦袍执事 c21_青袍长老 c22_青衫少年
severity: medium
---

## 问题
新建的 c20/c21/c22 三张卡只有立绘 ref prompt(text→image)，缺 turntable「建立视频」prompt(```text 4s 角色 reference 视频块)。根因：我建卡时用了「turntable 待出 ref 后生成」占位、把视频块延后——这是被禁的中间状态。

## 规则（流程修复·已落地 K16b）
**角色卡原子性（no 中间态·video prompt is a must）**：建一张具名/配角人形角色卡，必须**一步建全**——锁定描述符 #识别标签 + voice_id + 立绘 ref prompt(image) + **turntable 建立视频 prompt(```text 4s 视频块)** + 统一声样台词表，缺 turntable 视频块＝不合格。**禁止「turntable 待出 ref 后生成 / 待生成 / TBD」任何延后占位**——要么不建此卡，要么一次齐全。仅非人形实体(系统/UI)豁免 turntable。格式契约 **K16b** 已含此校验(blocker)。

## 落地
c20/c21/c22 已补全 turntable 4s 建立视频 ```text 块(吃自身立绘供脸·念统一声样 voice_id JP-steward-01/QP-elder-01/QS-youth-01·各 ≤2000) + 声样表。三卡现原子完整。
