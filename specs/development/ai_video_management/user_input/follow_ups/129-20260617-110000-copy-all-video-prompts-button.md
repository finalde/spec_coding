# Follow-up draft 129 — 2026-06-17
一键复制本集所有 shot 的视频 prompt（only 视频 prompt，不含台词配音）。

---
target_stage: 6
target_artifacts:
  - apps/ui/src/components/Reader.tsx
  - apps/ui/src/lib/videoPrompts.ts
severity: low
---

## 指令
在 webapp 加一个按钮：一键复制当前 EP 下**所有 shot 的视频 prompt**到剪贴板。**只含视频 prompt**（`## 视频 prompt` 代码块），不含 `台词配音` 块。

## 实现（纯前端、无新后端端点）
- 位置：episode 级 markdown（`episodes/ep{NN}/{shotlist,script,dialogue,publish,…}.md`）的 reader 工具栏，复用 `isEpisodeFile` 锚点（与「合成本集视频」四个 🎬 按钮并排）。按钮 **📋 复制全部视频 prompt**。
- 行为：从 `knownPaths` 过滤本集 `shots/shot{NN}/shot{NN}.md`（排序）→ 逐个 `GET /api/file` → 提取「视频 prompt」fenced block（按最近的前置 `##` 标题分类，同 inline 编辑器规则，`blockKindFromHeading==="video"`）→ 以空行拼接 → `navigator.clipboard.writeText` → toast 报告复制数 / 跳过数。
- 新文件 `apps/ui/src/lib/videoPrompts.ts`：`extractVideoPromptBody` / `episodeDirOf` / `shotMdPathsInEpisode`，含单测 `test/videoPrompts.test.ts`（7 例）。
- CSS `.reader-copy-prompts-btn`（镜像 `.reader-episode-concat-btn`）。
- 校验：tsc --noEmit 通过；vitest 全绿（30 旧 + 7 新）。
