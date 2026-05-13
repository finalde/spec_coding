# Follow-up draft 030 — 2026-05-13

在 ActorGrid (follow-up 028) 上加两个 bulk operation 功能:

1. **Bulk delete**: 多选 + 一次确认 + 客户端 loop 现有 `POST /api/actors/delete` (follow-up 026)
2. **Assign character**: 多选后弹模态 → drama dropdown → character dropdown → confirm → 客户端 loop 现有 `POST /api/casting/assign` (follow-up 014 FR-9g) 给每个选中的 actor

用户问 "you may need a more powerful data store" — interactive 决策回答：**保持 per-drama `casting.md` 不变**。理由：actor-drama-character 关系本就是 many-to-many（同一 actor_id 出现在多个 drama 的 `casting.md` 即视为参演多剧），现有 markdown 表已经原生支持，引入 SQLite / JSON index 只会产生第二真值源 + sync 风险。

## 用户原话

> 在演员池页面，加入以下功能，第一个是bulk delelte，第二个功能是assign charactor, 给我drop down的选项，先选择哪个短剧，在选择短剧里的人物，然后确定后，此演员会标记参演这部短剧的这个角色。一个演员可以同时出演多部剧.you may need a more powerful data store to store this kind of relationship, it is up to you to pick the best fit

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| 数据存储 | **复用 per-drama `casting.md`** (interactive 选) | many-to-many 原生支持；同 actor_id 可在多个 `casting.md` 出现；FR-9g 已对接 |
| Bulk delete 确认 | **单一 `window.confirm` + 客户端 loop** (interactive 选) | 对齐 follow-up 011 的 batch-archive pattern；无新 endpoint |
| Bulk delete endpoint | 复用 `POST /api/actors/delete` (follow-up 026) | 已含 cascade unassign 逻辑，每张顺带清理对应 casting 引用 |
| Assign 模态触发 | grid 进入 select mode 后，footer bar 点 "🎬 分配角色" | 与 bulk delete 同 surface |
| Drama dropdown 数据源 | client-side parse `/api/tree` 的 `ai_videos/{drama}` 直接 children (过滤 `_*` system folders) | 复用现有 tree fetch；无新 endpoint |
| Character dropdown 数据源 | client-side: 在 selected drama 下找 `characters/c*/` 子目录名 | 复用现有 tree；role 直接用 folder name (per FR-9g "typically a c{N}_* folder name") |
| Assign 后端调用 | 复用 `POST /api/casting/assign` (FR-9g)，每个选中 actor 一次 | actor 可同时参演多剧 = 同 actor_id 写入多个 drama 的 casting.md |
| Assign 失败一处 vs 全部 | 单个失败 continue + 累计 errors[] (与 bulk delete 一致) | per-actor 独立 |
| Select mode 入口 | grid header 加 "选择" 按钮，点击进入；select mode 期间 tile click 切换选中 而非 navigate | 显式 mode 切换，避免误触 |
| 全选/全清 | select mode 加 "全选" / "全清" 按钮 | 大 pool 多选效率 |
| Selection 跨页保留 | **跨页保留 selection** (Set 不绑 page) | 用户能跨页累积多选；切回前页能看 selected 状态 |
| Footer bar 持久化 | 当 select mode 开启时 sticky 在 grid 底部 | UX 显眼 |

## 功能要求

### Backend

零改动。所有逻辑走现有 endpoints：
- `POST /api/actors/delete` (FR-9i, follow-up 026)
- `POST /api/casting/assign` (FR-9g, follow-up 014)
- `GET /api/tree` (FR-10, follow-up 003)

### Frontend

**`projects/ai_video_management/frontend/src/App.tsx`**:

- 把 `tree` + `setRefreshKey` 通过 prop 传给 `<ActorGrid />`

**`projects/ai_video_management/frontend/src/components/ActorGrid.tsx`** (扩):

- 新增 props: `tree: TreeNode | null`, `onChange: () => void`
- 新增 state:
  - `selectMode: boolean`
  - `selectedIds: Set<string>` (跨页保留)
  - `busyDelete: boolean`
  - `assignOpen: boolean`
- Tile click 分支：
  - `selectMode` → toggle id 在 `selectedIds`
  - 否则 → navigate to `/file/{image_path}` (现有)
- Grid header 加按钮:
  - "✅ 选择" (进入 selectMode)
  - selectMode 期间替换为 "✕ 退出选择"
- Select mode footer bar (sticky bottom 当 selectMode):
  - 显示 "已选 N / 总 M"
  - "全选" / "全清"
  - "🗑 批量删除 (N)" → window.confirm → loop `deleteActor(id)` → toast + onChange
  - "🎬 分配角色 (N)" → 打开 assign modal
- Tile 加 visual selected state (e.g. blue border + checkmark overlay)
- Assign modal (new sub-component or inline JSX):
  - drama `<select>` (populated from tree)
  - character `<select>` (populated from tree at selected drama's `characters/`)
  - confirm button → loop `assignCasting(drama, role=character_folder_name, actor_id, notes='')` for each selectedId
  - 累计 errors[] → toast

**`projects/ai_video_management/frontend/src/api.ts`**:

- 加 `assignCasting(path, role, actor_id, notes?)` (如果不存在；检查发现 `castingAssign` 可能已存在或不存在)

**`projects/ai_video_management/frontend/src/styles.css`**:

- `.actor-tile-selected` — 蓝边 + checkmark
- `.actor-grid-select-bar` — sticky bottom footer
- `.actor-grid-checkbox` — overlay 上左角 checkbox
- `.assign-modal` — backdrop + panel (复用现有 modal CSS)

### Spec / validation

- `final_specs/spec.md` FR-91 扩展: 加 select mode + bulk delete + assign workflow 描述
- `final_specs/spec.md` FR-89 (CastingView) 维持不变 — 这里的 assign 走相同 endpoint
- `validation/security.md` 无新 carve-out — 都走已有 endpoints
- `validation/acceptance_criteria.md` U3.18 扩展: select mode / 多选 / bulk delete / assign workflow

## 安全 / 边界

- **No new HTTP surface** — 全部复用 `POST /api/actors/delete` + `POST /api/casting/assign` + `GET /api/tree`
- **No new write surface** — 所有 writes 都已在前面 follow-up 校验
- **Selection state 跨页**：纯前端 in-memory，不持久化；刷新页面清空
- **Assign 失败不阻塞** — per-actor 独立，与现有 batch-archive (follow-up 011) 模式一致

## 不在本 follow-up 范围

- 不引入新 backend endpoint
- 不引入 SQLite / JSON index — 用户 interactive 选择保留 markdown 表
- 不引入 character 多选 (一次只 assign 到一个 character)
- 不引入 drama 多选 (一次只 assign 到一个 drama)
- 不引入 "取消所有 assignments for selected actors" 批量 unassign — 用户没要求
- 不动 CastingView (per-drama 视图，已有 read/edit/delete 单 actor)
- 不动 backend `Casting` 类 (`unassign_actor_everywhere` 来自 follow-up 026 已足)
- 不写 backend pytest / frontend Vitest (推迟)
- 不引入键盘 shortcut (Esc 退出 select mode 是 nice-to-have，v2)
- 不引入 selection 持久化 (URL / localStorage) — in-memory v1
