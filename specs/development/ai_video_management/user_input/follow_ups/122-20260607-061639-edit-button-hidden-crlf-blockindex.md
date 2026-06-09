---
target_stage: 6
target_artifacts:
  - projects/ai_video_management/apps/ui/src/markdown/renderer.tsx
  - ai_videos/nvdi_tuihun_houhuile/
severity: high
---

# Follow-up draft 122 — 2026-06-07
md page 上看不到 prompt 的 ✏ Edit 按钮 (跟 121 的默认 raw 模式无关 —— 按钮本身没出现)。

## 根因
`CopyableCode` 的 `canEdit = editEnabled && blockIndex>=0 && mtimeHttp!==undefined`。`blockIndex = bodyToIndex.get(trimmedBody)`。`bodyToIndex` 的 key 由**源文件**块体构造, 含 `\r\n` (CRLF); 但 ReactMarkdown 渲染出的代码块被规范化成 `\n` (LF), `trimmedBody` 是 LF → key 对不上 → `blockIndex = −1` → 按钮静默隐藏。nvdi 全部 `.md` 是 CRLF (本会话早先用 Python `open(...,"w")` 写文件时把 LF 转成了 CRLF; 仓库标准是 LF, feng_shou_lu 即 LF)。

## What landed
- **数据修复**: nvdi 全部 35 个 `.md` 由 CRLF 转回 LF (二进制替换 `\r\n`→`\n`) → 块匹配立即对上, 按钮出现 (无需重新构建, 刷新页面即可)。
- **代码防呆**: `renderer.tsx` 的 `bodyToIndex` key 与 `trimmedBody` 都先 `.replace(/\r\n/g,"\n")` 再 trim → 即使源文件是 CRLF 也能匹配, 按钮不再被行尾隐藏 (需重新构建生效)。

## 注 (过程教训)
后续用 Python 脚本批量改 ai_videos/ 下 `.md` 时, 须**保留 LF**: 用 `open(f,"wb")` 二进制写, 或 `open(f,"w",newline="\n")`, 不要默认 text 模式 (Windows 会把 `\n`→`\r\n`)。mozun_chongsheng 也是 CRLF (非本会话所致), 其 edit 按钮同样会被隐藏 —— 代码防呆修复对它也生效 (待重新构建); 数据层 LF 转换本轮**仅做了 nvdi**。

## 验证
nvdi `.md` 残留 CRLF = 0; `tsc --noEmit` 通过 (regex 归一化, 类型安全)。
