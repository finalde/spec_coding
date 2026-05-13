# Follow-up draft 020 — 2026-05-12

Summary: 收窄 follow-up 019 在 single-file media reader 页面上加的 SiblingMedia grid — 用户反馈"mp4 page 只要一个 archive 按钮归档当前文件"。视频 / 图片 单文件页面 grid + checkbox + toolbar 信息量过大，用户实际只想 "看完这个 mp4 觉得不要 → 一键归档 → 继续看下一个"。回归到 per-file inline button UX。

## 用户原话

> change the format a little bit, on the mp4 page, just give me a archive button to archieve current mp4 file

## 决策（无 interactive 问题，按用户原文直推）

| 问 | 决策 |
|---|---|
| 哪些 reader 分支收窄到单按钮？ | `isVideo` + `isMediaImage`（"mp4 page" + 同性质的单图片页对称）。 |
| `isImageRef` / `isShotPair` / `isMarkdown` 怎样？ | **保留 SiblingMedia 不变** — 那些是 markdown view，sibling grid 在它们底下有意义（一个 ref_images folder 通常有多张 _seedream.md 互为 sibling）。用户没要求改这几处。 |
| 按钮做什么？ | 当前文件在 archive/ 内 → `unarchiveMedia(path)`；否则 → `archiveMedia(path)`。即 archive / unarchive 互逆，由 path 自动判定。 |
| 成功后导航？ | `react-router-dom` `useNavigate` 跳转到响应里的 `to` 路径 — 用户能立刻看到同一 mp4 从新位置加载，按钮变成 "↺ Unarchive"（misclick recovery）；不直接跳父 folder（避免 sidebar 与 main 之间空窗）。 |
| 错误处理？ | 走已有 `#aria-live-toast` 公告；按钮 disabled in-flight。 |
| 视觉？ | 按钮挂 `.media-view` 内 video / img 之下，单行右对齐；轻量灰底 + light-theme，与 `.sibling-media-archive-btn` 调性一致但 reader 级 class 名独立。 |

## 功能要求

1. **Reader.tsx 在 `isVideo` 分支**：移除 follow-up 019 加的 `<SiblingMedia>`；在 `<video>` 之下加 `<button className="reader-media-archive-btn">` 触发 archive / unarchive；fragment 包裹不再需要 → 回到 `<div className="media-view">…</div>` 单容器。

2. **Reader.tsx 在 `isMediaImage` 分支**：同上，移除 SiblingMedia，加 button。

3. **`isImageRef` / `isShotPair` 分支**：**保持 follow-up 019 的 SiblingMedia 不变** — markdown 类视图，folder-level archive 仍有 batch 用例。

4. **archive 路径判定**（path-based，前端 only）：
   - `split('/')` 后看 `parts[parts.length - 2] === 'archive'` → `isArchivedFile = true`。
   - true → `unarchiveMedia(path)` + 按钮显示 "↺ Unarchive"。
   - false → `archiveMedia(path)` + 按钮显示 "📦 Archive"。

5. **成功后导航**：`navigate(\`/file/${encodeURIComponent(result.to)}\`)` + `onSaved()` 同时触发 tree refresh；URL 更新后 Reader 重新 fetch 媒体，UI 顺滑切换。

6. **错误时**：保留当前 URL，公告 `aria-live-toast`（"Archive failed: target_exists" 等），按钮重新 enabled。

7. **busy 状态**：local `archiving: boolean` state；button `disabled={archiving}`；label 切到 "Archiving…" / "Unarchiving…"。

8. **样式**：新增 `.reader-media-archive-btn` 样式 — float / margin-top 6px、light-theme bg、disabled cursor: progress；不污染已有 `.sibling-media-archive-btn`。

## 后端 / 安全 / 边界

- **零后端改动** — 复用 008 / 011 已有的 `POST /api/archive-media` + `POST /api/unarchive-media`，安全契约（Origin/Host gate、sandbox、symlink reject、原子 rename、archive/ folder 自动清理空壳）原样生效。
- **archive 文件再 archive**：后端已校验"immediate parent is archive → 400 `already_archived`"，所以按钮永远显示其中一个 state，不会 double-archive。
- **不跨 folder**：依然是 per-file，与 008 一致；用户视角只多了"已在 reader 里"这一个入口。

## 不在本 follow-up 范围

- 不为 `isImageRef` / `isShotPair` / `isMarkdown` 引入单按钮 — 那些 markdown view 旁的 SiblingMedia 仍是最佳 UX；用户没要求收窄。
- 不为 `isCasting` / `isShotlistTable` / `isJsonl` / `isCode` / `isTxt` 加 archive — drama-root 级文件，无 ref-video / ref-image 用例。
- 不引入"archive 后跳父 folder" / "archive 后自动加载下一个 sibling" — 跳新路径是最不 surprising 的行为；后续若用户想要 "next mp4 in folder" 是另一个 navigation feature，单独 follow-up。
- 不引入 confirm dialog — archive 可逆，按钮变成 Unarchive 即 misclick recovery。
- 不写 frontend Vitest / e2e Playwright（与 005 ~ 019 一致推迟）。
