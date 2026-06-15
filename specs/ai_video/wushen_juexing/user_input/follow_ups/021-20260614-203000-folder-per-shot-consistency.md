---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/episodes/ep01/shots/
  - .claude/agent_refs/project/ai_video.md
  - .claude/agent_refs/validation/ai_video.md
  - validation/structure_schema.md
severity: medium
---

# Follow-up draft 021 — 2026-06-14

用户指出不一致：`nvdi_tuihun_houhuile`（女帝退婚后悔了）每个 shot 是一个**文件夹** `shots/shotNN/`（内含 `shotNN.md` + `renders/` 渲染媒体），而 `wushen_juexing`（武神觉醒）的 shot 是扁平的 `shots/shotNN.md` 文件。要求把 wushen_juexing 修正为文件夹结构，并保证两剧 behaviour 一致。

## 根因
- 规范本身就要求 folder-per-shot：`agent_refs/project/ai_video.md` rule #12.9 明确 `episodes/ep{NN}/shots/shot{NN}/shot{NN}.md`；webapp 显示契约 / 渲染导入路由 `shots/shotNN/renders/` / 台词烧录 `subtitles.md` 全部依赖该文件夹。
- 但 ref 的 layout 示意图（authoring order + 目录树）漂移成了扁平 `shotNN.md`，且 wushen_juexing 的 `structure_schema.md` S-LAYOUT-4 把「扁平 shotNN.md 才是 prompt 源」写成了规则——本会话早先还把 worker 生成的 `shotNN/shotNN.md` 当成「nested-dir bug」误「修复」成扁平，方向正好反了。

## 抽象后的指令（common-level + project）
1. wushen_juexing 22 个扁平 `shotNN.md` → `shotNN/shotNN.md` 文件夹。
2. 修正 ref layout 示意图（目录树 + authoring order 第 5 步）为 folder-per-shot，引用 rule #12.9。
3. 新增机检规则：validation/ai_video.md move #10 + 严重度行；wushen_juexing structure_schema S-LAYOUT-4 改写为 folder-per-shot blocker。
4. 全仓库一致：两剧都 folder-per-shot，无扁平 shot md。
