---
target_stage: 6
target_artifacts:
  - projects/ai_video_management/apps/ui/src/lib/promptEdit.ts
  - projects/ai_video_management/apps/ui/src/markdown/renderer.tsx
  - projects/ai_video_management/apps/ui/src/components/Reader.tsx
  - projects/ai_video_management/apps/ui/src/components/ShotPairView.tsx
  - projects/ai_video_management/apps/ui/src/components/ImageRefView.tsx
  - projects/ai_video_management/apps/ui/src/components/ActorView.tsx
  - projects/ai_video_management/apps/ui/src/styles.css
severity: medium
---

# Follow-up draft 116 — 2026-05-25

webapp 的 inline "edit prompt" 模式只覆盖 **第一个** fenced code block。但 ai_video.md rule 12.6-B (per follow-up xianxia_new/011) + rule 12.3 + rule 12.5 让 scene 档 / character 档 / actor 档可包含 N 个 prompt code block (scenes: 立绘 + 15s walk-through; characters: turntable + Seedream立绘 + state-A/B 变体; actors: face shot + body shot)。结果: 用户只能编辑第一个 prompt，其余 prompt 只能开"整个 md 文件"编辑器，违背"edit just the prompt"原则。

## 抽象指令

在 `ai_videos/` 下的所有 markdown 文件中，**每一个** fenced code block 都加一个 inline ✏ Edit 按钮，行为契约: (a) 仅替换该 code block 的 body, (b) 保留 frontmatter / 标题 / 锁定描述符 / 负向段 / cross-doc 路径 等其他段落 byte-identical, (c) 走现有 PUT /api/file + If-Unmodified-Since concurrency, (d) 409 stale_write 时保留 textarea buffer 不丢失。

落地三件套:

1. **promptEdit.ts 拓展为索引化 API**: 新增 `findAllFencedCode(content) → FencedCodeMatch[]`, `findNthFencedCode(content, n)`, `extractNthFencedCode(content, n)`, `replaceFencedCodeAt(content, n, newBody)`. 保留 `findFirst/extractFirst/replaceFirst*` 老 API 不动以保持后向兼容 (VoiceView 仍使用)。

2. **markdown Renderer 加每块 inline edit**: 新增 RendererProps `editEnabled?: boolean` + `mtimeHttp?: string` + `onSaved?: () => void`。Renderer 内 `findAllFencedCode(content)` 一次, 用 React Context 把 `{ bodyToIndex map, fileContent, currentPath, mtimeHttp, onSaved, editEnabled }` 下发给每个 `CopyableCode`。CopyableCode 通过 `extractText(children) → trimmedBody` lookup `bodyToIndex` 拿到自己的 block-index, 然后渲染 ✏ Edit 按钮 (并排于 📋 复制按钮)。点击 ✏ 切换 inline textarea + ✓ Save + ✕ Cancel; Save 调用 `replaceFencedCodeAt(fileContent, blockIndex, buffer)` + PUT。

3. **Reader.tsx 路由层**: isMarkdown fallthrough 给 Renderer 新增 prop `editEnabled = path.startsWith("ai_videos/")` + `mtimeHttp` + `onSaved = async () => { await load(); onSaved(); }`。其他路径 (my_novel/, 等) 不传 editEnabled, Renderer 回退到只显示 📋 复制按钮 (现状)。

4. **4 个 specialized view 同步升级 (用户选项 "都换成 每块一按钮")**:
   - **ShotPairView** / **ImageRefView**: 已通过 Renderer 渲染文件正文, 仅需透传新 props (mtimeHttp, onSaved, editEnabled). 顶部 "✏ Edit" 快捷按钮保留 (是第一块的 power-user 快捷入口)。
   - **ActorView**: actor md 含 2 个 prompt (face shot + body shot). 抽出 `ActorPromptCard` 子组件持有 per-card edit 状态; main view 改为 `parsed.prompts.map(...)` 循环渲染 N 个 card; parser `parsePrompts(content)` 用 `findAllFencedCode` + `nearestHeadingBefore` 提取每块的前置标题作为 section title。
   - **VoiceView**: voice md 当前单 prompt (per follow-up 115). 保持 `replaceFirstFencedCode` 单块编辑 (功能正确, 与 voice 单 prompt 域一致); 若未来 voice md schema 演化到多 prompt, 再按 ActorView 模式上升。

5. **CSS** (styles.css): 新增 `.code-block-actions` (flex 容器, 替代旧的单按钮绝对定位), `.code-block-edit-btn` (蓝色 variant), `.code-block-save-btn` (绿色 variant), `.code-block-wrapper-editing` (蓝边框 + padding), `.code-block-textarea` (类比 shot-pane-textarea, 等宽字体), `.code-block-edit-error` (红色 banner)。

## 不动的契约

- `prompts/` 路径全部已废止 → `shots/` (per follow-up xianxia_new/011)。Reader.tsx `SHOT_MD_RE` 仍使用旧路径 regex `prompts/shot\d+/shot\d+.md` —— 本 follow-up 不修复 (单独 follow-up 应跟进, 否则 shotNN.md 不再走 ShotPairView 而落到 isShotMd-only path)。
- VoiceView 单 prompt 编辑模式保持 byte-identical (functional currently)。
- 全文件编辑入口 ("✎ Edit" toolbar button) 保留, 用于编辑 frontmatter / 标题 / 锁定描述符 / 负向段等非 prompt 段。
- promptEdit.ts 老 API (`findFirst*` / `replaceFirst*`) 保留, 不破坏现有调用方。

## 触发原因

用户原话: "在ai videos裏，每個prompt都給我一個edit mode，而且只是edit prompt自己，不是當前md 文件". 用户通过多选锁定: 范围 = 仅 `ai_videos/` 下的 .md / 4 个 specialized view 同步升级。
