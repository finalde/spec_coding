---
target_stage: 6
target_artifacts:
  - projects/ai_video_management/apps/ui/src/components/PromptStructuredEditor.tsx
  - projects/ai_video_management/apps/ui/src/markdown/renderer.tsx
severity: low
---

# Follow-up draft 121 — 2026-06-07
每个 prompt 都给一个 edit mode, 可以直接修改里面的文字。

## 现状
`ai_videos/` 下每个 ```text``` prompt 代码块右上角已有 `✏ Edit` 按钮 (renderer.tsx CopyableCode, editEnabled = path.startsWith("ai_videos/"))。点它打开 `PromptStructuredEditor`, 该编辑器已含「📝 原文」(raw textarea, 直接改文字) 与「🪜 结构化」(逐字段表单) 两模式 + 切换。但**默认进结构化表单** (shot prompt 有可解析字段时), 不是「直接改文字」。

## What landed (stage-6, 2 行级改动)
- `PromptStructuredEditor.tsx` — 默认模式由 `initialParsed.fields.length>0 ? "structured" : "raw"` 改为恒 `"raw"`: 点 ✏ Edit 立即显示该 prompt 的可编辑文本框, 直接改字即存; 「🪜 结构化」逐字段表单仍可一键切换。
- `renderer.tsx` — 编辑提示文案由「点它进入结构化表单编辑」改为「点它直接编辑该 prompt 的文字 (默认原文文本框, 改完即存; 也可切结构化表单)」。

## 机制 (已存在, 未改)
raw 模式 textarea 编辑整块 body → 保存走既有 `replaceFencedCodeAt(fileContent, blockIndex, newBody)` + `putFile(path, ..., {ifUnmodifiedSince: mtimeHttp})` 单块替换 + 409 并发守卫; 不影响文件其他段落。

## 验证
`tsc --noEmit` 通过 (改动为字面量+注释+文案, 类型安全); 无 UI 测试断言旧默认; editEnabled 对 ai_videos/ 全开 → nvdi 所有 shot/scene prompt 均有此 edit mode。
