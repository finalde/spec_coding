# Follow-up draft 070 — 2026-05-17

Summary: Reader 内 markdown-rendered shotXX.md / 角色 ref / shot pair 等文件的 fenced ` ```text ` 代码块仍有横向滚动条 — follow-up 069 仅修了 `PromptPreviewModal` 内的 prompt 卡片，没动 Reader 渲染 markdown 时的 `<pre>` 元素。`.markdown-view pre` / `.code-view pre` / `.jsonl-line pre` 三处都用 `overflow-x: auto` + 默认 `white-space: pre`（不换行）。改为 `white-space: pre-wrap` + `overflow-wrap: anywhere` + `word-break: break-word` + `overflow-x: hidden` — 长 comma-separated prompt 自然换行，无横条；换行符仍被 `pre-wrap` 保留（不破多行 prompt 结构）。

## 用户原话

> I can still see horizontal bar in frontend page when comes to prompt like in shotXX.md

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| 范围 | Reader 内 `<pre>` 元素 3 处：`.markdown-view pre` (markdown-rendered .md), `.code-view pre` (JSON/YAML render), `.jsonl-line pre` (JSONL inline expand) | 用户原话指 shotXX.md，但 .json/.yaml/.jsonl 同 root cause；一并修保持一致 |
| Wrap 策略 | `white-space: pre-wrap` + `overflow-wrap: anywhere` + `word-break: break-word` | pre-wrap 保留 `\n` 不破多行结构；anywhere/break-word 在 token 内部强制换行（comma-separated 1000+ char variance 串里也有不少 ≥30 char 连续 token） |
| `overflow-x` | `auto` → `hidden` | 显式杀掉横条；如果 wrap 失败兜底也不出条 |
| 字体 / 颜色 / padding / 主题色 | 不动（沿 `--pre-bg` / `--pre-fg` / `--pre-border`，黑底 GitHub-dark 风） | 仅修 overflow 行为，不动 visual identity |
| `.markdown-view pre` line-height | 1.6 → 1.65（微调） | 换行后字距更舒展 |
| 其它 markdown 元素 | 不动 — `.markdown-view code` (inline) 已 `padding: 1px 4px`，自然 wrap | 仅 `<pre>` 块状元素有 horizontal-scroll 历史包袱 |

## 功能要求

`apps/ui/src/styles.css`:

1. `.markdown-view pre`: 删 `overflow-x: auto`；加 `white-space: pre-wrap; overflow-wrap: anywhere; word-break: break-word; overflow-x: hidden`；line-height 1.6→1.65。
2. `.code-view pre`: 同上策略（保留 padding / 字体 / size 不动）。
3. `.jsonl-line pre`: `white-space: pre` → `pre-wrap`；删 `overflow-x: auto`；加 `overflow-wrap: anywhere; word-break: break-word; overflow-x: hidden`。

无 JSX / 后端 / endpoint / spec FR 改动。

## 安全 / 边界

- **多行结构保留**：`pre-wrap` 保留 `\n` 换行符 — Multi-line YAML / JSON / shot prompt 的视觉结构（每个 `字段: 值` 一行）不被破坏。
- **Code highlighting**：项目当前无 syntax highlighter；`<pre><code>` 是 raw 文本；wrap 不破坏潜在 highlighter 的 token boundary（未来加 highlighter 也兼容，highlighter 输出 `<span>` 不改 white-space）。
- **JSON / JSONL "single line per record"**：`.jsonl-line pre` 是 JSONL inline-expand 后的 pretty-printed JSON 块，pre-wrap 不破 JSON parser；视觉上 N 行 JSON 仍 N 行渲染，只在 single line 过宽时 wrap。
- **Long URL / hash tokens**：`overflow-wrap: anywhere` 在 URL 中间也会 break — 罕见 cosmetic concern；本场景 shot prompt 不放 URL，可接受。
- **复制粘贴**：`<pre>` text content 在用户 select+copy 时仍是原始字符；wrap 是视觉行为，剪贴板内容不变。

## 不在本 follow-up 范围

- 不引入 syntax highlighting。
- 不动 `.code-block-wrapper > .copy-btn` 位置（既有 absolute top-right OK）。
- 不动 Reader / breadcrumb / toolbar / sidebar 样式。
- 不写 vitest。
