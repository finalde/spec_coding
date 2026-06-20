# Follow-up draft 012 — 2026-06-18
场景方位背景图导出按钮加回 + 截帧秒数与 scene prompt 对齐 + 修正「mp4→图片」流程误解。

## 指令（抽象后）

1. **scene mp4 的「截取各 bg 朝向背景图」按钮没了 → 加回**（之前只在 SiblingMedia 兄弟列表里有，直接打开 scene mp4 的主播放器工具栏没有）。
2. **确保 scene prompt（步骤二 walk-through 逐秒方位）与导出功能的截帧秒数一致**——实测旧导出用固定罗盘序（北1.5/东4.5/南7.5/西10.5/中13.5），与本场景 walk-through 实际朝向序（北→西→俯瞰→中景→东）不符，抽出的图朝向错位。
3. **平台能力铁律**：AI 平台**不支持上传 mp4 生成图片**，只能 mp4→视频 或 图片→图片。故各朝向静帧只能**从 walk-through mp4 抽帧**（或 image→image 精修），不能「image prompt + 上传 mp4 → 出图」。
4. 新增 `bg6_座前_虚化背景` 如何生成 → 从 #5 长焦 detail dwell（13.5s，景深最虚）抽帧；要更虚走 image→image。

## 落点

- webapp（projects/ai_video_management）：Reader 主工具栏加「🧭 截取方向背景图」按钮（gate=isSceneVideoPath）；ScenePlateExtractor 截帧秒数改为读 scene md「背景图系统 index」表（per-scene 真源），罗盘 map 仅兜底；bg6 等表内非罗盘朝向也纳入抽帧。
- scene 档：`zhenbei_wangfu_zhengting.md` 生成流程/index 注释改为「抽帧为主 + image→image 精修」，删除「image prompt + 上传 mp4 出图」。
- institutional memory：`.claude/agent_refs/project/ai_video.md` 场景生成流程加「video-first→抽帧」+「mp4→图片 不支持」铁律。
