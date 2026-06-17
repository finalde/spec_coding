# Follow-up draft 048 — 2026-06-16
为 EP1 全部 14 个 shot 生成双语字幕文件（中文+英文）。

---
target_stage: 6
target_artifacts: [episodes/ep01/shots/*/subtitles.md]
severity: low
---

## 指令
每个 `episodes/ep01/shots/shot{NN}/subtitles.md` 写入双语台词时间轴：每行 `起-止(秒) 中文 || English`，时间窗源自各句台词配音 `时长目标`。中文取自各 shot `## 台词配音` 块，英文为对应翻译（蛮荒城→Manhuang City、镇北王府→Zhenbei Manor）。配合 ai_video_management webapp 的「💬中文 / 💬EN / 💬中英」三按钮可分别烧出对应语言成片。规则见 ai_video.md rule 11c（双语格式）。
