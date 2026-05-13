# Follow-up draft 022 — 2026-05-12

Summary: 在 sidebar 顶部加一个 collapse-all 图标按钮，单击 → 把当前 tree 内所有 folder 节点 `expanded` 状态置 `false`，整个 nav 树折叠到顶层。

## 用户原话

> on the ai_video_management left menu, lets add a collapse all icon, when click it will collapse the entire left nav tree

## 决策（无 interactive 问题，按用户原文直推）

| 问 | 决策 |
|---|---|
| 按钮位置 | Sidebar 顶部新增 `.sidebar-toolbar` 行，渲染在 `.sidebar-toast` 之上（toast 出现时不挤压 toolbar 位置）。 |
| 图标 | `⊟`（U+229F Box Minus）— 视觉上接近 VS Code Explorer "Collapse All" 图标；跨平台 fallback 良好；不引入 SVG / 第三方 icon 库。 |
| Label / Title | `aria-label="折叠全部"` + `title="折叠全部 · Collapse all folders"`（保持双语提示风格与 sidebar 内其他 button 一致：`📥 导入 + 重命名` / `🎭 生成演员` 都是中文 label + 中文 title）。 |
| 折叠范围 | 所有 folder（`type === "directory"` 或 `type === "section"` 等非 file/image/video 节点）。Top-level pseudo-root 不计（`depth === 0` 永远显示，由 Sidebar.tsx line 97 强制）。 |
| 与现有 effect 的交互 | line-50 effect（tree change 时初始化默认 expanded=true）merge 顺序是 `({ ...accum, ...prev })`，`prev` 覆盖 `accum`。collapse-all 把 `prev` 全置 `false` 后即使 tree 重新 fetch 也会保持折叠，新出现的 folder 仍默认 `true`（accum 提供）。无需改 effect。 |
| 与 currentPath ancestors 的交互 | line-62 effect 在 `currentPath` 变化时 expand 祖先链。collapse-all 不修改 `currentPath`，所以 effect 不会被触发抵消折叠。但若用户折叠后又点 sidebar 内别处文件，那次 navigation 会重新展开新路径的祖先链 — 符合 VS Code 行为。 |
| 当前文件被折叠后不可见 | 接受 — VS Code 同样行为。Breadcrumb + Reader 仍显示当前文件路径，用户可手动展开找回。不是缺陷。 |

## 功能要求

1. **Sidebar.tsx 修改范围**：
   - 加 `onCollapseAll: () => void` 局部 useCallback（依赖 `[tree]`）：walk tree → 把所有 `node.type` 非 file/image/video 的节点 path 都置 `false` → `setExpanded(allFalse)`（覆盖 prev 全部 known path）。
   - 在 `<nav className="sidebar">` 内、`renameToast` 渲染之前，插入 `<div className="sidebar-toolbar">` 含单个 `<button className="sidebar-collapse-all" aria-label="折叠全部" title="折叠全部 · Collapse all folders" onClick={onCollapseAll}>⊟</button>`。
   - tree 为 null / loadError 时 toolbar 不渲染（与 loading / error 视图保持简洁）。

2. **styles.css 新增**：
   - `.sidebar-toolbar` — flex row、padding 6px 12px、border-bottom var(--border)、background var(--bg-sidebar) 与 sidebar 一致；icon 右对齐 (justify-content: flex-end)。
   - `.sidebar-collapse-all` — 无 border、background transparent；color var(--text-muted)；font-size 16px；padding 2px 6px；border-radius 3px；hover 时 color var(--text) + background var(--bg-toolbar)；cursor pointer。

3. **零后端改动**、零新 endpoint、零新 dep。

## 安全 / 边界

- 不引入新的安全 surface — 纯 client-side state 操作。
- 不影响键盘导航 — 现有 ArrowLeft/Right/Up/Down/Enter/Space 行为不变；collapse-all button 通过 Tab 可达。
- 不影响 `ActorPoolGenerator` 模态 / `renameToast` / `subtype-badge` 等 sidebar 内既有功能。

## 不在本 follow-up 范围

- 不加 "Expand all" 反向按钮 — 用户没要求；line-50 effect 已经在 tree 刷新时默认全展开，需要时刷新页面即可。
- 不加键盘快捷键（Ctrl+Shift+Numpad-Minus 等） — 单按钮就够，键盘党用 Tab 到 button + Enter 即可。
- 不持久化 collapse 状态到 localStorage — line-50 effect 已经让 collapse-all 跨同 session tree refresh 持久；跨 session 重置（刷新页面 = 全展开默认）符合"一次性整理视图"语义。
- 不写 frontend Vitest / e2e Playwright（与 005 ~ 021 一致推迟）。
