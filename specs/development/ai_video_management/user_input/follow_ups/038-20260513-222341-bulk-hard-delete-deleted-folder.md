# Follow-up draft 038 — 2026-05-13

Summary: 在 sidebar `ai_videos/_deleted/` 行上加入"管理"入口（"🧹 永久清理"按钮，导航 `/deleted` route），打开新的 `DeletedView` 多选页面。页面递归列出 `ai_videos/_deleted/**` 下所有 media 文件（mp4 / 图片）作为 tile grid，支持 select-mode 多选 + 跨页保留 + 全选/全清；底部 sticky bar 提供 "🗑 永久删除 (N)" 按钮。点击触发"打字 `DELETE` 才能解锁确认按钮"的模态（含文件数 + "此操作不可撤销"红色警示），确认后前端 loop 新增 `POST /api/hard-delete-media` 端点逐文件 `Path.unlink()` 真删除。Soft-delete 仓库（`_deleted/`）变成可清空的"回收站"。

## 用户原话

> under ai_video_management, for _delete foler, give me an option to bulk hard delete those files

## 交互问答记录（启动前）

| 问 | 选项 | 用户选 |
|---|---|---|
| Scope | 全清 vs 多选 vs 兼有 | **多选 tiles in _deleted/ view** |
| Surface | sidebar row vs reader page vs both | **Sidebar row for ai_videos/_deleted** |
| Confirmation | type DELETE vs window.confirm vs two-step | **Type 'DELETE' to confirm + show file count** |

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| 后端 endpoint | 新增 `POST /api/hard-delete-media` body `{path}` | 与 `delete-media` (FR-9k follow-up 023) 镜像；per-file unlink；前端 loop 走批量 |
| 后端路径校验 | 必须以 `ai_videos/_deleted/` 开头 | 防御性：即使前端被改也无法从该 endpoint 真删 `_deleted/` 之外的文件。镜像 `delete()` 的 `NotInAiVideos` 校验 |
| 后端复用 `_validate_media_source` | 是 | 扩展名 / sandbox / symlink-reject / file-exists 校验全部复用 |
| 后端是否 rmdir 空 parent | **否** | 与 `delete()` 决策对称（follow-up 023 `_deleted/` 内文件 unlink 后留空 parent；用户手工或后续 follow-up 清理）|
| 后端不写删 audit log | 是 | webapp 不是 spec_driven agent_team；`events.jsonl` 是 agent_team 状态机的；webapp 操作进 server log 即可 |
| 前端 entry point | Sidebar `_deleted/` 行加 "🧹 永久清理" 按钮（镜像 `_actors/` 行的 "🔲 网格"） | 用户明确选择 sidebar surface；与 follow-up 028 现有 "🔲 网格" 按钮 pattern 一致；点击 `e.stopPropagation()` + `navigate("/deleted")` |
| 前端 view 选择 | 新 `DeletedView` route `/deleted` | 与 `/actors` 平行；不在现有 Reader 内嵌入（folder reader 不是 Reader 现有的 dispatch 模式） |
| 前端 grid 数据源 | client-side 递归 walk `tree` 收集 `path.startsWith("ai_videos/_deleted/")` 的 `type === "image" \|\| type === "video"` 节点 | 复用现有 `/api/tree`；无新 list endpoint；与 ActorGrid 用 `extractDramas(tree)` 同 pattern |
| Tile 内容 | image/video 缩略图（`mediaUrl(path)`，video 用 `<video preload="metadata">` 取首帧）+ filename + 相对路径子串（`_deleted/...` 后段） | 缩略图主导让用户快速辨认要不要保留 |
| Select-mode 入口 | grid header "✅ 选择" 按钮（与 ActorGrid follow-up 030 一致） | UX 一致；select-mode 期间 tile click 切 toggle 不再打开 Reader |
| 跨页保留 selection | 同 ActorGrid follow-up 030：`selectedIds: Set<string>` (keyed by full path) 不绑 page | 大 `_deleted/` 下多选效率 |
| 分页 | 复用 ActorGrid 的 `PAGE_SIZE=50` 与首/上/页码/下/末 5 控件 | 一致性 |
| 全选/全清 | 加 footer "全选" / "全清" 按钮 | 大量待清理常见用例 |
| 确认 UX | 模态：标题 + "此操作不可撤销"红色 warning + 文件计数 + "Type DELETE to confirm" input + 主按钮 disable until exact match | 用户明选 typed-DELETE；比 native confirm 高摩擦但与"不可逆"语义匹配 |
| 大小写敏感 | 必须 `===  "DELETE"` 全大写 | 摩擦本身是目的；自动 trim 也不做（typo 不该意外通过） |
| 主按钮文案 | "永久删除 N 个文件" + disabled 时变灰 | 中文 + 计数让用户在最后一刻仍能 reconsider |
| 失败处理 | per-file 独立 try/catch + 累计 ok/fail；toast `已永久删除 X / 失败 Y（详见 console）`；不 abort batch | 镜像 follow-up 011 / 030 batch pattern；单 file race（已被外部 rm）不该阻塞其余 |
| 关闭模态后行为 | 成功 → 关模态 + 退出 select mode + `onChange()` 重新 fetchTree | grid 数据源是 tree，刷新后已删 tile 消失 |
| `_deleted/` 已空时 | grid 显示 empty state "回收站为空 — 软删除的文件会出现在此处" + sidebar 按钮仍可点（导航后看到 empty state） | sidebar 不预判 emptiness（避免每次刷新打开 modal 时再做 tree count 判断） |
| 已 hard-delete 的文件 reader 行为 | 不动 Reader.tsx —用户在 hard-delete 后会回到 grid，不会停留在 `/file/...` 上看 404 | 范围收窄；不引入"Reader 检测 404 自动 navigate('/')" 这种额外行为 |
| `_deleted/` 外路径误传 | 后端 400 `not_in_deleted` | 防御性返回码；前端理论上只发 `_deleted/` 内路径 |

## 功能要求

### 1. Backend

**`projects/ai_video_management/backend/libs/media_archiver.py`**：
- 新增 `class NotInDeleted(Exception)`：标记 hard-delete 调用了非 `_deleted/` 路径。
- 新增 `MediaArchiver.hard_delete(self, rel: str) -> str`：
  - `src = self._validate_media_source(rel)` — 复用扩展名 / sandbox / symlink / 存在性校验。
  - `relative = src.relative_to(self._resolver.root)`；要求 `relative.parts[0] == "ai_videos"` 且 `relative.parts[1] == DELETED_DIR_NAME` — 否则 `raise NotInDeleted`。
  - `src.unlink()` → `OSError` → `raise MoveFailed`（复用既有失败语义）。
  - 返回 `self._rel(src)`（相对 root 的字符串）。

**`projects/ai_video_management/backend/libs/api.py`**：
- import 加 `NotInDeleted`。
- 顶部 docstring：endpoint count 17 → 18；endpoint 列表加 `POST /api/hard-delete-media`。
- 新 endpoint `POST /api/hard-delete-media`，body `ArchiveMediaBody`（复用同 shape `{path}`）；mapping：
  - `ArchiveInvalidPath` → 400 `invalid_path`
  - `NotMedia` → 400 `extension_not_allowed`
  - `NotInDeleted` → 400 `not_in_deleted`
  - `ArchiveNotFound` → 404 `not_found`
  - `MoveFailed` → 500 `delete_failed`（kind 与 archive/delete 的 `move_failed` 区分）
  - 405 method_not_allowed handler (GET/PUT/PATCH/DELETE)
  - 成功 `{deleted: "ai_videos/_deleted/.../foo.mp4"}`。

### 2. Frontend

**`projects/ai_video_management/frontend/src/api.ts`**：
- 加 `interface HardDeleteMediaResult { deleted: string; }`
- 加 `async function hardDeleteMedia(path: string): Promise<HardDeleteMediaResult>` — POST `/api/hard-delete-media`。

**`projects/ai_video_management/frontend/src/App.tsx`**：
- 新 route `/deleted` → `<DeletedView tree={tree} onChange={() => setRefreshKey((k) => k + 1)} />`。
- import 加 `DeletedView`。

**`projects/ai_video_management/frontend/src/components/DeletedView.tsx`** (新文件)：
- Props `{ tree: TreeNode | null; onChange: () => void }`。
- 递归 walk `tree`，收集所有 `path.startsWith("ai_videos/_deleted/")` 且 `type === "image" || type === "video"` 节点，按 path 升序。
- State：`selectMode`、`selectedPaths: Set<string>`、`page`、`busy`、`modalOpen`、`typedConfirm`。
- 渲染：
  - Header：title `🗑 回收站 (N 个文件)`，"✅ 选择" / "✕ 退出选择" 按钮，分页（N > PAGE_SIZE=50 时）。
  - Tile grid：`<img>` for image / `<video preload="metadata" muted>` for video，filename + 子路径作 label。Select mode 下点击 toggle，否则 navigate to `/file/{path}`。
  - Select mode footer (sticky)：`已选 N / 总 M` + 全选 + 全清 + "🗑 永久删除 (N)"（disabled if N=0 or busy）。
  - 模态：标题 `永久删除 N 个文件？`，红色 banner "⚠ 此操作不可撤销 — 文件将从磁盘真删除"，列出前 10 个 path（更多以 `+ X 个其他文件…` 折叠），input `<input placeholder="输入 DELETE 解锁">`，确认按钮 disabled until typed === "DELETE"。
  - 确认：`setBusy(true)`；`for (path of selected) await hardDeleteMedia(path)` 累计 ok/fail；toast `已永久删除 X / 失败 Y`；关模态 + 退出 select mode + `onChange()`。
- 空 state：`grid` 为空时显示 `回收站为空 — 软删除的文件（来自 mp4 / 图片 Reader 的 🗑 Delete 按钮）会出现在此处`。

**`projects/ai_video_management/frontend/src/components/Sidebar.tsx`**：
- 派生 `isDeletedRoot = item.node.type === "directory" && dramaPathParts.length === 2 && dramaPathParts[0] === "ai_videos" && dramaPathParts[1] === DELETED_DIR_NAME` (常量 `"_deleted"` 内联即可)。
- 在该行渲染（独立 `<button>`）：`🧹 永久清理`，点击 `e.stopPropagation()` + `navigate("/deleted")`；与 `_actors/` 的 "🔲 网格" 按钮同 className（`drama-rename-btn`）以复用样式。

**`projects/ai_video_management/frontend/src/styles.css`**：
- 加 `.deleted-view-page`（页面包装）、`.deleted-view-grid`（CSS grid auto-fill 180px tiles，复用 `.actor-grid`）、`.deleted-tile`（按钮 tile）、`.deleted-tile-selected`（蓝边）、`.deleted-tile-thumb`（img/video 容器，`object-fit: cover`）、`.deleted-tile-name`、`.deleted-tile-path`（muted 小字）、`.deleted-view-empty`、`.deleted-view-confirm-input`、`.deleted-view-confirm-warning`（红色 banner）、`.deleted-bulk-purge`（footer 红主按钮）。

### 3. Spec / validation

- `final_specs/spec.md`：
  - 新增 **FR-94** (follow-up 038)：`POST /api/hard-delete-media` 端点契约 + `DeletedView` + sidebar `_deleted/` 行 "🧹 永久清理" 按钮 + typed-DELETE 模态契约。
  - **FR-9k** 段落（follow-up 023 `delete-media` 描述）末尾追加 `_deleted/` 通过 FR-94 提供 in-app 真删除路径的回链。
- `validation/acceptance_criteria.md`：
  - 新增 **U3.22** Gherkin：sidebar 行按钮 → DeletedView grid → multi-select → typed-DELETE 模态 → loop 删除 → tree refresh empty。
  - 覆盖矩阵补 `FR-94 → U3.22`。
- `user_input/revised_prompt.md`：composed-from 加 038；header summary 重写为 038 内容；Last regenerated 时间更新。

## 安全 / 边界

- **Origin/Host gate**（follow-up 002 / `api_security` middleware）原样生效 — 新 endpoint 无 carve-out。
- **Sandbox**：`_validate_media_source` 已校验 path 在 EXPOSED_TREE 内 + 扩展名 + symlink-reject。**额外**：`hard_delete` 强制 `parts[0]=="ai_videos" && parts[1]=="_deleted"`，所以即使前端被注入也无法 unlink `_deleted/` 之外的文件。
- **Atomic per-file**：单 `Path.unlink()`，无中间状态。
- **不验 `If-Unmodified-Since`**：unlink 不读 mtime，与 archive / delete 一致。
- **空 parent**：unlink 留空文件夹，由用户手工或将来 follow-up 清理（与 follow-up 023 设计对称：删除时不动 src parent）。
- **`_deleted/_actors/`**：actor folder（follow-up 026）整个 folder 被 rename 进 `_deleted/_actors/actor_NNNN/`，其内 jpg + md 是 media 与非-media 混合。**本 follow-up 仅删 media（mp4 + 图片）**，actor sidecar `.md` 不在 `MEDIA_EXTENSIONS` 内 → `_validate_media_source` 直接 raise `NotMedia` 400。这意味着 hard-delete 只能逐张清掉 actor folder 的 jpg，`.md` 残留 — v1 接受（与 hard-delete-media 只针对 media 的语义一致；clear actor sidecar 走 follow-up 035 之后的 v2 follow-up）。

## 不在本 follow-up 范围

- 不引入"清空整个 `_deleted/` 一键按钮"（用户选 multi-select 而非全清；全选 + typed-DELETE 已能实现等价 UX）。
- 不引入 hard-delete `.md` / `.json` / 非-media 文件。
- 不引入 rmdir 空 parent / `_deleted/` 整体折叠清空。
- 不引入 in-app restore / undelete（与 follow-up 023 决策一致）。
- 不写 backend pytest / frontend Vitest（与 005~037 一致推迟到批量补测）。
- 不动 Reader.tsx（已 hard-delete 文件留在 `/file/...` URL 上的 404 处理交给现有 Reader 错误分支；用户在 modal 后会回到 grid，不会去单文件 URL）。
- 不引入 audit log events（webapp 非 agent_team 状态机）。
- 不引入键盘 shortcut（Delete 键、Ctrl+A 等）。
- 不引入 sidebar 二级菜单 / 右键菜单（一个明显按钮足够）。
