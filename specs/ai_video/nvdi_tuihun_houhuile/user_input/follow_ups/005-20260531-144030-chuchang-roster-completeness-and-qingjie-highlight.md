---
target_stage: 6
target_artifacts:
  - episodes/ep01/shots/*/shot*.md
severity: medium
---

# Follow-up draft 005 — 2026-05-31
出场角色 checklist 必须列全画面内所有角色；shot 档顶部小说段的出场角色名以粗体高亮。

## 抽象指令

1. **出场角色完整性（全集扫一遍）**：每个 shot 的 `参考:` 行、`角色:` 块、Shot context `Characters:` 行必须按 ai_video.md「出场角色 checklist 派生规则」列出**该 shot 画面内出现的全部角色**，不只主要/聚焦角色。范例缺陷：ep01/shot02 是全景父子跪礼区（陈国公在画面内且有 c3 角色档），却只列了陈凡——陈国公（及画面内的太监）被漏列。多人同框镜头（全景 / 父子或太监同框中景）普遍存在此漏列，需全集核对补齐。补齐时各角色的 byte-identical 一句话锁定 + face-differentiator 取自其 character bible 第 10/11 行。

2. **小说段角色名高亮**：shot 档顶部的 `## 小说原文` / `## Chapter excerpt` 段内，出场角色名以 markdown 粗体标注（如 **陈凡** / **陈国公** / **太监**），便于与 `Characters:` 行交叉核对。粗体仅为显示层——去除 `**` 后与 chapter 正文 byte-identical。代码块内的 `情节:` 字段保持纯文本（不加粗，避免污染复制到模型的 prompt）。
