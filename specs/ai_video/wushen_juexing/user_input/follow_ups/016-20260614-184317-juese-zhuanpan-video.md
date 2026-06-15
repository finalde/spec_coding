---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/characters/
  - final_specs/spec.md
  - ai_videos/wushen_juexing/style_guide.md
severity: medium
---

# Follow-up draft 016 — 2026-06-14

新加角色（沈婉）prompt 太少、而且不是视频——角色应有转盘视频 prompt。

## 抽象后的指令

- 角色档现在只有一段 Seedream 立绘（静态图），**缺角色转盘 video prompt**。按 ai_video.md 规则 12.5：角色与场景同构，走两步——
  1. **立绘 seed 图**（已有）。
  2. **角色转盘 video prompt（turntable）**：上传立绘作 image-to-video reference，生成 ~7s 转盘视频（正面→侧面→背面 360° 缓转），渲染出 turntable.mp4，作为该角色在每个 shot 图生视频的人物锚点（锁定面孔/服装/体型跨镜一致）。
- 适用**全部 9 个角色**（不止沈婉），补齐两步流水线；prompt 细节加丰富。

## 落地

- 每个 `characters/cN_{名}/cN_{名}.md` 在 Seedream 立绘段之后追加「# 角色转盘 video prompt（turntable）」段：含用法说明 + 转盘 prompt（主体/角色锁定串/镜头360°缓转/动作正侧背/光线三点布光/渲染样式/时长7s；外貌服装发型道具 byte-identical 复用本档锁定描述符）。
- spec FR-5 + style_guide：角色=立绘 seed 图 + 转盘 video（两步），与场景两步流水线对齐。
- 比例不写（follow-up 010）。
