# Follow-up draft 023 — 2026-05-12

Summary: 在 mp4 / image reader 页面上 Archive 按钮旁加一个 Delete 按钮 — 把当前 media 文件 soft-move 到 `ai_videos/_deleted/{保留原 ai_videos 之下的子路径}`。Soft-delete 而非真删除 — 文件仍在 sandbox 内可见、可手工移回；后续若需要 in-app restore 走单独 follow-up。

## 用户原话

> please also add a delete button to the mp4 files which will move it to a top level _deleted folder

## 决策（无 interactive 问题，按用户原文直推 + 与 follow-up 008 / 020 一致性推断）

| 问 | 决策 |
|---|---|
| `_deleted/` 位置 | `ai_videos/_deleted/` — sandbox 内"top level"只能是 `ai_videos/` 或 `research/`，user 用 webapp 管 ai_videos 所以 `ai_videos/_deleted/`。与 `_actors/` 同为 `_`-prefix 系统 folder，pattern 一致。 |
| Target 内子结构 | 保留原 ai_videos 子路径。`ai_videos/mozun/characters/c1/c1_1.mp4` → `ai_videos/_deleted/mozun/characters/c1/c1_1.mp4`。优点：不撞名、心智可追溯（用户能看出"这是哪个 drama 哪个角色被删的"）、未来 restore 直接 reverse move。 |
| 范围 | mp4（视频）+ 标准图片（png/jpg/jpeg/webp/gif/bmp）— 与 follow-up 020 Archive 按钮一致。User 只说 "mp4 files" 但与 Archive 按钮 surface 一致更不易混淆。 |
| 按钮位置 | Reader.tsx `isVideo` / `isMediaImage` 分支内、`.media-view` 容器中 Archive 按钮旁边。 |
| 按钮 label | `🗑 Delete` — emoji + English 与 `📦 Archive` 风格一致；中文 title 跟 sidebar 既有按钮的双语 tooltip pattern 对齐。 |
| 确认对话框 | **加** `window.confirm("Move {filename} to _deleted/?")`。Archive 不 confirm（follow-up 008 决策），但 delete 是更"重"动作 — 用户语义里 "delete" 比 "archive" 危险，native confirm 是最低成本防误触。Cancel → 不发请求、不 announce。 |
| `_deleted/` 内文件的按钮显示 | **隐藏 Delete 按钮**（不允许"双 delete" → `_deleted/_deleted/...` 嵌套），**隐藏 Archive 按钮**（已 deleted 文件再 archive 语义错乱）。即 `_deleted/` 内的 mp4 / image reader 只显示视频/图片本身，没有 footer 按钮。此为 follow-up 020 Archive 可见性规则的小幅扩展。 |
| 删除已 archive 的文件 | 允许。文件原路径在 `archive/` 子目录内 → delete 把它移到 `_deleted/{drama}/.../archive/{name}` — 子结构保留包含 `archive/`，无歧义。 |
| 删除非 `ai_videos/` 路径 | 拒绝 400 `not_in_ai_videos`。`research/` 路径不在本 follow-up 范围（user 没要求；research/ 没有"top level deleted folder"语义指代）。 |
| 已在 `_deleted/` 再 delete | 后端拒绝 400 `already_deleted`（按钮已隐藏所以正常路径走不到这；防御性兜底）。 |
| `_deleted/` 在 tree 内可见？ | **可见** — 默认 directory walk，不加 `_EXCLUDED_DIRS`。让用户能看到删了啥，能手工 restore（用文件管理器或 sidebar 重命名 / 拖动）。与 `_actors/` 一致：`_`-prefix 但 tree 可见。Follow-up 022 的 collapse-all 让噪声可控。 |
| 后端何处实现 | `media_archiver.py` 内加 `MediaArchiver.delete()` 方法 + `DELETED_DIR_NAME = "_deleted"` 常量 + 新 exceptions `AlreadyDeleted` / `NotInAiVideos`；不抽新文件（`MediaArchiver` 已经语义是"per-file media mover"）。 |
| 成功后导航 | 与 Archive 一致：`useNavigate` 跳新路径让 reader 立刻显示同一 media 从 `_deleted/` 加载；但此时 button 区域因 `_deleted/` 隐藏 → 用户看到 video + 空 footer，明确反馈"已搬走"。 |
| 错误处理 | Aria-live toast 公告 + button re-enable。busy state 与 `archiving` 互斥（两按钮共享一个 busy guard 防 double-fire）。 |

## 功能要求

1. **`projects/ai_video_management/backend/libs/media_archiver.py`**：
   - 新增 `DELETED_DIR_NAME = "_deleted"` + `AI_VIDEOS_ROOT_NAME = "ai_videos"`。
   - 新增 `class AlreadyDeleted(Exception)` + `class NotInAiVideos(Exception)`。
   - `MediaArchiver` 加 method `delete(self, rel: str) -> MoveResult`：
     - 复用 `_validate_media_source` 做扩展名 / sandbox / symlink 校验。
     - `relative.parts[0] != "ai_videos"` → raise `NotInAiVideos`。
     - `relative.parts[1] == "_deleted"`（紧邻 `ai_videos` 之下）→ raise `AlreadyDeleted`。
     - target = `resolver.root / "ai_videos" / "_deleted" / Path(*parts[1:])`。
     - `target.parent.mkdir(parents=True, exist_ok=True)` → OSError → `MoveFailed`。
     - target 存在 → `TargetExists`。
     - `src.rename(target)` → 返回 `MoveResult`。
   - 不 rmdir empty parent — 与 Archive 不同（Archive unarchive 会清空 archive/）。删除不动原 folder 结构。

2. **`projects/ai_video_management/backend/libs/api.py`**：
   - import 加 `AlreadyDeleted`, `NotInAiVideos` from `media_archiver`。
   - 新 endpoint `POST /api/delete-media`，body `ArchiveMediaBody`（复用，结构相同 `{path}`）；mapping：
     - InvalidPath → 400 `invalid_path`
     - NotMedia → 400 `extension_not_allowed`
     - NotInAiVideos → 400 `not_in_ai_videos`
     - AlreadyDeleted → 400 `already_deleted`
     - NotFound → 404 `not_found`
     - TargetExists → 409 `target_exists`
     - MoveFailed → 500 `move_failed`
   - 对应 method_not_allowed handler GET/PUT/PATCH/DELETE → 405。
   - 模块 docstring 顶部 endpoint count 由 13 改为 14；endpoint 列表加 `POST /api/delete-media`。

3. **`projects/ai_video_management/frontend/src/api.ts`**：
   - 加 `export async function deleteMedia(path: string): Promise<ArchiveMediaResult>` — 复用 `ArchiveMediaResult` 类型；POST `/api/delete-media`，body `{path}`。

4. **`projects/ai_video_management/frontend/src/components/Reader.tsx`**：
   - import 加 `deleteMedia` from `../api`。
   - 派生 `isDeletedFile = path.startsWith("ai_videos/_deleted/")`。
   - 加 `deleting: boolean` state；Archive 与 Delete 按钮 disabled 互斥（`archiving || deleting`）。
   - 加 `onDeleteClick` useCallback：
     - `window.confirm(\`Move ${filename} to _deleted/?\`)` 失败 → 直接 return。
     - `setDeleting(true)` → `deleteMedia(path)` → 成功 `announceToast` + `onSaved()` + `navigate(/file/encoded)` → 失败 announce 错误。
   - JSX：`isVideo` / `isMediaImage` 分支内、Archive button 之后加 Delete button。两按钮都包在 **`!isDeletedFile`** 条件下 — 已 deleted 的文件视频/图片仍正常播放但不显示 archive / delete footer。

5. **`projects/ai_video_management/frontend/src/styles.css`**：
   - 加 `.reader-media-delete-btn` — 与 `.reader-media-archive-btn` 同基线尺寸；hover 时 color → 警示红（用 var(--text)，不引入新色板；通过 border-color 切到 `#c53030` 或类似 light-theme 红 — 检查 styles 已有调色后选用 `--error-border` 之类已定义变量）。disabled 走相同 opacity 0.55 + cursor: progress。
   - 与 Archive button 间距：margin-left 8px 即可。

## 安全 / 边界

- **Origin/Host gate**（per follow-up 002 / api_security middleware）原样生效，新 endpoint 无 carve-out。
- **Sandbox**: `_validate_media_source` 已校验 path 在 EXPOSED_TREE 内。Target path `ai_videos/_deleted/...` 仍在 sandbox 首段 `ai_videos`，无逃逸。
- **Symlink reject**：复用现有 `_validate_media_source`。
- **Atomic rename**：单文件 `Path.rename()`，与 archive / unarchive 一致。
- **`_deleted/` 创建权限**：与 `archive/` 创建同 `mkdir` 默认 0o755。
- **DOS via deep path**：path 长度 / depth 没硬上限；但 sandbox 内文件本来就受 OS path-max 限制，与现状一致，无新风险。
- **不验 `If-Unmodified-Since`**：单 atomic rename，无 edit race，与 archive 决策一致。

## 不在本 follow-up 范围

- 不引入 in-app restore / undelete 按钮 — user 没要求；用户可用文件管理器或后续 follow-up。
- 不引入"clear _deleted/"批量真删除按钮 — 同理。
- 不为 `isImageRef` / `isShotPair` / `isMarkdown` 分支加 Delete — Archive 在这些分支走 SiblingMedia grid，那里加 delete 是更大改动；user 只要求 mp4 / 单图片。后续可对称扩展。
- 不引入键盘快捷键（Delete 键触发） — 单按钮 + confirm 即可。
- 不 emit `pipeline.halted` / 不写 `events.jsonl`（webapp 不是 spec_driven agent_team 的状态机；audit log 不属本 surface）。
- 不写 backend pytest / frontend Vitest（与 005 ~ 022 一致推迟到批量补测）。
- 不 rmdir 原文件被删后的空 parent folder — 与 Archive 设计不对称（Archive unarchive 会清空 archive/ 但 archive 创建不删 parent；Delete 同理，只创建 target chain 不删 src parent）。
- 不 prescribe `_deleted/` 大小 / 数量上限 — 用户责任。
