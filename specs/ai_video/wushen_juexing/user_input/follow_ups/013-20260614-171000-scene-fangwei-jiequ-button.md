---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/scenes/s1_裴王府正厅/
severity: medium
---

# Follow-up draft 013 — 2026-06-14

15s 场景视频要能一键按方位截帧到 bgX_(东/南/西/北/中) 文件夹（webapp video 上加按钮）；且视频逐秒朝向必须与截帧 function 的时间点严格一致（如前段正北、转正东…，截帧时点刚好镜头对准该方向）。

## 抽象后的指令
- webapp：scene 视频上加按钮，一点即按方位时间点截帧、生成到各 bg{N}_{方位}_ 文件夹（作 shot 背景板）。
- 一致性铁律：场景 video 的逐秒朝向 = 截帧 function 的时间点 = plate 方位。
- 方位集对齐为 北/东/南/西/中（bg5 高位俯瞰→中）。

## 落地（drama 侧）
- scene video 逐秒方位时间轴与截帧时点统一：北@1.5 / 东@4.5 / 南@7.5 / 西@10.5 / 中@13.5（5 dwell×3s，dwell 中点截帧）。
- bg5_高位俯瞰_中轴全景 → bg5_中_中轴俯瞰（folder+file+引用）；index 表方位列改「中（高位俯瞰）」。
- webapp 侧功能见 ai_video_management（新增 extract-scene-plates 端点 + SiblingMedia「🧭 截取方向背景图」按钮）。
