# Follow-up draft 011 — 2026-05-11
Summary: 在 SiblingMedia grid 加 multi-select + 批量 Archive / Unarchive — 用户在 character / scene / shot / 任意含 media 的 folder 里勾选若干图片/视频，点 toolbar 上的 "Archive Selected (N)" 一键归档；archived 子区域同理勾选 + "Unarchive Selected (N)"。Per-tile 单文件按钮保留不变。

## 背景 / 用户场景
- Follow-up 008 实现了 per-tile archive / unarchive — 一次一文件。
- 实际工作流：用户从 Seedance/Kling 渲染出 10+ 候选 mp4 / png 后，只保留 1 个 final，其余全部归档。Per-tile 点 10 次太繁。
- 用户原话："I want an archive button so I can move selected pictures and videos and move them to a local archive folder, so I only leave that 1 video in the current charactor folder ... Apply the same features to other folder under left nav such as scene and shot etc"
- 范围 = SiblingMedia 当前已经覆盖的所有 folder（character / scene / shot / episode / 任何含 media 的 `.md` 同 folder）— 该组件已经 generic 跑在 Reader 下方，无需 per-folder 分别加。

## 决策 (interactive 收集，2026-05-11 20:25)

| 问 | 用户答 |
|---|---|
| Selection UX | Always-visible checkboxes on each tile — corner checkbox 始终可见，避免触屏隐藏 hover；勾选后 toolbar 出现 "Archive Selected (N)" / "Unarchive Selected (N)"。 |
| Per-tile button | Keep both — per-tile "📦 Archive" / "↺ Unarchive" 保留供单文件 quick action；批量 toolbar 仅在 ≥1 勾选时显示。无回归。 |
| Select all helper | Yes — toolbar 含 "Select all" + "Clear" + "Archive Selected (N)" 三按钮，分别作用于当前 section（Folder media 或 Archived）；selection state 两个 section 独立。 |
| Batch 错误处理 | Continue on error — 顺序发 N 个 archive/unarchive 请求，全部完成后聚合 announce："Archived 3, failed 2: foo.mp4 (target_exists), bar.png (move_failed)"。成功的不回滚，失败的留原地。 |

## 功能要求 (UI 层)

1. **Checkbox UI**:
   - 每个 `MediaTile` 左上角加一个 `<input type="checkbox">` (大小 ≥18px, hit area ≥24x24px for touch)。Background 半透明 white 圆角，避免被视频 thumbnail 吞没。
   - 勾选状态由 `SiblingMedia` 父组件维护两个独立 `Set<string>`：`selectedActive`（folder media）+ `selectedArchived`（archive/ media）。
   - Checkbox 阻止冒泡，不触发 tile 点击或 video 播放。

2. **Toolbar**:
   - Folder media section 上方（紧贴 `<h3>📁 Folder media · 同 folder 媒体</h3>` 之下）渲染一个 `<div class="sibling-media-toolbar">`，含三个按钮：
     - `Select all` — 选中当前 section 所有 tile。
     - `Clear` — 清空当前 section selection；仅在 N ≥ 1 时 enable。
     - `Archive Selected (N)` — 仅在 N ≥ 1 时 enable + 显示计数。点击触发批量归档。
   - Archived section 上方同样三按钮，但第三个是 `Unarchive Selected (N)`。
   - Toolbar 始终存在（即使 N = 0），保持布局稳定；按钮 disabled 状态走 light-theme 灰阶。

3. **批量执行（前端逻辑）**:
   - 点击 `Archive Selected (N)` 时：
     - 整个 toolbar + 所有 checkbox + 所有 per-tile 按钮 disabled（busy 整个 section）。
     - 顺序 `await archiveMedia(path)` 每个选中 path（**串行**而非并发，避免后端在同一 archive/ folder 上并发 mkdir / rename 竞争 — backend 已 atomic 但 UX 上顺序更易聚合错误）。
     - 累计 `successes: string[]` + `failures: {path: string, kind: string}[]`。
     - 完成后调用一次 `onChange?.()` 触发 tree refresh。
     - `aria-live` toast announce 聚合：成功多于 0 时 "Archived N file(s)"; 失败多于 0 时再 append "; failed M: name1 (kind), name2 (kind)"。
     - 清空 selection。
   - `Unarchive Selected (N)` 对称。

4. **per-tile 单文件按钮兼容**:
   - 旧的 per-tile "📦 Archive" / "↺ Unarchive" 按钮保留行为不变 — 不消费 selection、不参与批量。
   - per-tile 按钮在批量 in-flight 期间 disabled（共享 `busy` 标志）。

5. **In-flight 防重复**:
   - `busy` 状态从单 `busyPath: string | null` 演化为 `busy: boolean`（true 时整个 section 锁定）+ 仍保留 `busyPath`（为 per-tile 单击高亮）。
   - 批量 in-flight 时 `busy=true`，per-tile 单击 in-flight 时仅 `busyPath` 被设置但 `busy=false`。
   - 双重 disable 条件：`disabled={busy || busyPath === path}`。

6. **a11y**:
   - 每个 checkbox 有 `aria-label="Select {filename}"`。
   - Toolbar 按钮 `aria-label` 含计数（"Archive 3 selected files"）。
   - Toast 走已有的 `#aria-live-toast` region。

## 后端
- **无新 endpoint**。`POST /api/archive-media` + `POST /api/unarchive-media` (follow-up 008, FR-9c / FR-9d) 已存在，per-file 原子操作，批量纯前端循环调用即可。
- 不引入 `POST /api/archive-media-batch` — N 通常 ≤20，串行 round-trip 在 localhost 上 < 50ms × N，不构成性能问题；引入批量 endpoint 反而需要复杂的部分失败回滚或半成功 response shape。

## 前端最小改动
- `SiblingMedia.tsx`:
  - 新增 `selectedActive: Set<string>` + `selectedArchived: Set<string>` state。
  - 新增 `busy: boolean` 整段锁；保留 `busyPath: string | null` 供单文件高亮。
  - `MediaTile` 新增 props: `selected: boolean`, `onToggleSelect: (path: string) => void`, `selectionBusy: boolean`（用于 disable checkbox）。
  - 新增 `<div class="sibling-media-toolbar">` 子组件，per-section 渲染。
  - 新增 `handleBatchArchive()` / `handleBatchUnarchive()` 异步循环。
- `styles.css` (或 `app.css` — 取项目实际命名):
  - `.sibling-media-toolbar` — flex row，padding 8px，gap 8px，light-theme 灰背景。
  - `.sibling-media-toolbar button:disabled` — 走 light-theme `#9ca3af` 灰。
  - `.sibling-media-item input[type="checkbox"]` — absolute 左上 8px / 8px，scale 1.3，半透明白底圆角 4px。

## 安全 / 边界
- 不引入新的安全 surface — 仅前端循环已存在的 endpoint。
- Origin/Host gate 仍然每次 archive 请求都走（per-call middleware，与 batch 无关）。
- 不需要 If-Unmodified-Since（批量 archive 复用 008 的"single atomic rename，无 edit race"假设）。

## 不在本 follow-up 范围
- 不引入 backend batch endpoint（理由见后端段）。
- 不引入"按 mtime 区间批量归档"、"按文件名 pattern 批量归档" 等高级筛选 — v1 纯 manual select。
- 不引入跨 folder 批量（每个 SiblingMedia 实例只看自己的 folder + archive/）。
- 不引入键盘多选（shift-click range, ctrl-click toggle）— v1 仅 checkbox click。
- 不引入 confirm dialog（archive 是可逆操作，无需 confirm；批量 unarchive 同理）。
- 不写 backend pytest（与 005 / 006 / 007 / 008 / 009 / 010 一致地推迟到批量补测）。
- 不写 frontend Vitest（与现有 SiblingMedia 一致 — e2e 走 Playwright 时再补）。
