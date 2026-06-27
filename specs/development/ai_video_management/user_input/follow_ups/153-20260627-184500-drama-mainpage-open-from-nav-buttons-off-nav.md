# Follow-up draft 153 — 2026-06-27

点击 left nav 的剧节点本身应弹出剧级 main page（不只是 dropdown），剧级按钮从 left nav 移到该 main page；导出 production 按钮亦在此页。（148 主页落点修正——原实现把 dashboard 锚在 README 页、点剧节点只展开 dropdown，未达 148 本意。）

---
target_stage: 6
target_artifacts:
  - projects/ai_video_management/apps/ui/src/components/Sidebar.tsx
  - projects/ai_video_management/apps/ui/src/components/DramaPage.tsx
  - projects/ai_video_management/apps/ui/src/App.tsx
severity: medium
---

## 指令
1. 点击 left nav 的剧（武神觉醒）节点：**不仅是 dropdown**——右侧同时弹出一个剧级 main page。
2. 这个剧级 main page 承载：导出 production 按钮（148 的新 button）+ 一系列剧 level 功能与展示，后续剧级功能都往这放。
3. **不要把这些剧级 button 加到 left nav 里**（从 nav 移除，集中到 main page）。

## 落地
- 新 `DramaPage` 组件 + 路由 `/drama?drama={path}`（App.tsx）。host：`DramaDashboard`（导出 production + 全剧烧字幕）+ 资源管理（导入+重命名、角色画廊，从 nav 迁入）+ 📺 分集总览（每集列出已烧字幕成片 zh/en/中英 = 导出会拷到 production/ 的内容）。
- `Sidebar`：剧节点 onClick → `navigate(/drama?drama=)` + 仍 toggle dropdown；移除 nav 内联的两个剧级按钮（导入+重命名、角色画廊）。
- `Reader`：`DramaDashboard` 从 isDramaReadme 页移除（连同 import 与 isDramaReadme 判定），集中到 DramaPage。
- styles.css：新增 `.drama-page*` 布局。
