---
target_stage: 6
target_artifacts:
  - ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shots/
  - ai_videos/nvdi_tuihun_houhuile/scenes/s1_陈国公府正厅/
  - .claude/agent_refs/project/ai_video.md
severity: medium
---

# Follow-up draft 026 — 2026-06-07
把所有 prompt 的负向都去掉。

## 落地 (nvdi 全部 prompt)
移除 `负向` 字段:
- 28 个 ep01 shot 的 ```text``` 块 `负向:` 行。
- 6 个朝向背景 plate (bg1-bg6) 的 `负向:` 行。
- scene 主档 walk-through 视频 prompt 的 `负向:` 行。
- scene 主档 场景立绘 prompt 的 `[负向]` 段 (header + 内容行)。
- scene 主档 `## 负向` 文档段 (re-paste 参考, 已随之孤立, 一并移除)。

核查: nvdi 已无任何 `负向` / `[负向]` / `## 负向`; 所有 ```text``` 块闭合正常 (末行为 时长/构图/[参数] 等, 非空非负向)。

## 范围说明
本轮仅 nvdi (用户近期在弄的项目)。feng_shou_lu (46 文件) / mozun_chongsheng (166 文件) 也含负向, **未动** —— 待用户确认「所有」是否含其他两项目再处理。

## 规则 (ai_video.md)
`负向` 字段非必须, 可按项目从生成块移除 (反向约束改放平台「反向提示词」输入框); ref 里「负向应含 X」规则仍定义要抑制什么, 仅承载位置变化。
