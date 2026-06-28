# Follow-up draft 080 — 2026-06-28

角色卡必须原子完整：每个（人形）角色都要有建立视频（turntable）prompt，建卡是 1-step 原子操作——要么不建此卡，要么立绘 ref prompt + 建立视频块一次齐全，绝不留「只有立绘、turntable 待出/待生成」的中间态。

---
target_stage: 2
target_artifacts:
  - 2_世界观人设/characters/c20_锦袍执事/c20_锦袍执事.md
  - 2_世界观人设/characters/c21_青袍长老/c21_青袍长老.md
  - 2_世界观人设/characters/c22_青衫少年/c22_青衫少年.md
  - .claude/skills/ai_videos__格式契约/SKILL.md
  - .claude/agent_refs/project/ai_video.md
severity: medium
---

## 背景
follow-up 079 新建的 c20/c21/c22 三个配角卡只写了 Seedream 立绘 ref prompt，turntable 建立视频块被留成 `> turntable 待出 ref 后生成` 占位行（changelog「待办: 三新卡 turntable 待渲染」）。用户判定该延后＝违规中间态。

## 规则（common-level）
- 命名人形角色卡 = 原子单元：立绘 ref prompt + 建立视频块（turntable）必须一次齐全。
- 禁止任何 turntable 延后占位行（`待出 ref 后生成` / `待生成` / TBD）。
- 轻量配角无选角脸也照样在建卡时直接以自身 `cN_名字.png` 立绘写全建立视频块、不延后。
- 仅非人形实体（系统/UI）豁免 turntable。
