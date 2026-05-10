# Follow-up draft 008 — 2026-05-10
Summary: 在 ai_video_management webapp 加 per-file archive / unarchive 功能 — 用户在 SiblingMedia tile 上点 "📦 Archive" 把 media 文件移动到同 folder 下的 `archive/` 子目录（不存在则自动创建）；archive/ 内的 media tile 上点 "↺ Unarchive" 把它移回原 folder。两步皆可逆。

## 背景 / 用户场景
- 用户从 Seedance / Kling 渲染出大量 reference / shot mp4 + png 后，会有"暂时不要的 / 待筛选 / 旧版本"产物 — 既不想删（怕回头要用），也不想留在主 folder 里干扰 SiblingMedia 预览的视觉节奏。
- 现有 follow-up 007 已经把"按 parent folder 命名"自动化了，但没有一个 "soft delete" 或 "归档" 通道。
- 用户原话："lets add a new feature for all the images and videos archive and revert archive, basically, if I archive a video or picture, it will simply create a archive folder under current one parent folder and move the video file, I can also reverse that."

## 决策 (interactive 收集，2026-05-10 20:18)

| 问 | 用户答 |
|---|---|
| 按钮位置 | Per-tile in SiblingMedia — 每个 media tile 一个 inline button；archive subfolder 内的 tile 显示 Unarchive。 |
| archive/ 在 tree sidebar 可见性 | Show archive/ as normal folder in tree — 不加进 `_EXCLUDED_DIRS`，作为常规 subfolder 显示，用户可像浏览其他 folder 一样进入。 |
| `POST /api/rename-media` 是否跳过 archive/ 内文件 | Rename inside archive/ too — 保持 batch rename uniform，archive/ 内文件也按 parent folder name (即 `archive`) rename。⚠️注意：这意味着 `shot01/archive/foo.mp4` → `shot01/archive/archive.mp4`（单文件态）或 `shot01/archive/archive1.mp4`、`archive2.mp4`（多文件态）。如果用户后续觉得这规则不合适，单独 follow-up 调。 |

## 功能要求 (UI 层)
1. **Archive button**: SiblingMedia 中每个非 archive/ 内的 media tile 右下角浮一个轻量 "📦 Archive" 按钮（仅 hover 显示 OK，但 v1 默认始终显示以避免触屏隐藏）。Tooltip "Move to archive/ subfolder"。
2. **Unarchive button**: SiblingMedia 中每个 archive/ 子目录内的 media tile（同样以 grid 显示）右下角浮 "↺ Unarchive" 按钮。Tooltip "Move back to parent folder"。
3. **SiblingMedia 渲染范围扩展**: 当 currentPath 是 `<folder>/<file>.md` 时，除了显示 `<folder>/` 直系 media，还要显示 `<folder>/archive/` 内 media（带视觉区分：例如灰阶 figure border + figcaption 前缀 "📦"）。Archive subfolder 媒体作为单独子区域 "Archived · 已归档" 渲染在主 grid 下方。
4. **In-flight 防重复**: button 在 in-flight 期间 disabled。错误时通过 `aria-live` toast 公告（已有的 `#aria-live-toast`）。成功后调用 `onSaved` 触发 tree refresh + 重新 mount Reader → SiblingMedia 自动刷新。

## 后端 endpoints
- `POST /api/archive-media`，body `{ "path": "ai_videos/{drama}/.../<file>.<ext>" }`
  - 校验 path 在 sandbox 内 + ext 是 media + 文件存在 + 不是 symlink。
  - 计算目标 = `<file 所在 folder>/archive/<basename>`。
  - 若 archive/ 不存在则 `mkdir`；若目标已存在则返回 409 `target_exists`。
  - 若 source 自身已经在 immediate parent 名为 `archive` 的 folder 下，返回 400 `already_archived`。
  - 用 `Path.rename()` atomic 移动；任何 OSError 返回 500 `move_failed`。
  - 200 返回 `{ "from": old_rel, "to": new_rel }`。
  - 405 for 非 POST。
- `POST /api/unarchive-media`，body `{ "path": "ai_videos/{drama}/.../archive/<file>.<ext>" }`
  - 校验 path 在 sandbox 内 + ext 是 media + 文件存在 + immediate parent 名为 `archive`。
  - 计算目标 = `<archive folder 的 parent>/<basename>`。
  - 若目标已存在则 409 `target_exists`。
  - 若 source 不在 archive/ 下，400 `not_in_archive`。
  - rename atomic；OSError → 500 `move_failed`。
  - 200 返回 `{ "from": old_rel, "to": new_rel }`。
  - rename 后，若 archive/ folder 空（无任何文件 / 子目录），自动 `rmdir` 清理空壳。
  - 405 for 非 POST。

## 安全 / 边界
- 入参 `path` 必须 `safe_resolve` 后落在 EXPOSED_TREE 内（首段 `ai_videos` 或 `research`）— 与现有 `is_inside` 一致。
- Origin/Host gate 与现有 state-changing endpoint (`PUT /api/file`, `POST /api/rename-media`) 一致。
- 拒绝 symlink。
- 不需要 If-Unmodified-Since（rename 是 atomic per-file，不存在并发编辑 race；并发 archive 同一文件第二次会 fail with 404 not_found，因为第一次已移走）。
- archive/ folder 创建权限：与 file_writer 现有写权限一致（mode 0o755 默认）。

## 前端最小改动
- `api.ts`: 新增 `archiveMedia(path)` + `unarchiveMedia(path)` helpers，签名 `Promise<{from: string, to: string}>`。
- `SiblingMedia.tsx`: 接受新 prop `onChange?: () => void`；渲染 archive/ 子目录 media + per-tile 按钮；按钮 onClick 触发对应 helper + onChange。
- `Reader.tsx`: 把 `onSaved` 透传给 SiblingMedia 作 `onChange`（命名复用：archive/unarchive 也是 "tree mutation" → 触发 refreshKey bump）。
- `styles.css`: 新增 archive button + archived figure 灰阶样式；与已有 light theme 调性一致；不引入新色板。

## 不在本 follow-up 范围
- 不引入"全局 Archive 视图"（用户已选择"archive/ 在 tree 内可见"，无需单独面板）。
- 不批量归档（v1 per-file；批量归档单独 follow-up）。
- 不限制 archive/ 嵌套深度（理论上 `archive/archive/` 可能出现，但 v1 不阻止；只用 `parent.name === "archive"` 判定）。
- 不写 backend pytest（保持与 005 / 006 / 007 一致地推迟到批量补测）。
- 不改 `_EXCLUDED_DIRS`（archive/ 作为常规 folder 显示）。
- 不改 `MediaRenamer`（rename 内部不跳 archive/，与用户决策一致）。
