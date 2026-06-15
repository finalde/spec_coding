---
target_stage: 6
target_artifacts: [episodes/ep01/shots/, episodes/ep02/shots/, .claude/agent_refs/project/ai_video.md]
severity: medium
---
# Follow-up draft 034 — 2026-06-15
shot4 台词排版导致 Kling 混乱（多说话人挤一行 + "..." 内嵌 『』「」 引号 + 注释混在台词里）。改用更好的 structure。落地：所有 shot 视频块 `台词:` 改为——首行说明（画面不显示文字、仅供口型/配音；逐条↓），随后每个发声单元各占一行 `· {说话人}〔{类型·口型}〕：{纯文本台词}`；正文不加任何引号、不嵌套；系统名直写（去『』）。规则进 ai_video.md (#034) + recut 模板。
