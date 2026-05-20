# Follow-up draft 086 — 2026-05-17

Summary: ActorGrid (`/actors` 路由) 加一个新 filter dropdown "分配状态" — 用户可选 "全部 / 已分配 / 未分配" 来过滤已经分配到 character role 的 actor。Backend `GET /api/actors` listing payload 新增 `is_assigned: bool` 字段，每个 actor 标记是否在任一 drama 的 `casting.md` 内出现。同时 tile 右上角加一个 🎬 小 badge — "全部" 视图下也能一眼看到哪些 actor 已用、哪些空闲。

## 用户原话

> 在看 actor 的页面，帮我加个新功能，filter in or filter out those charactors already assigned to a role

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| `is_assigned` 计算位置 | application/queries 层（`ActorQuery.list`），调 `CastingRepository.assigned_actor_ids()` 一次拿全 union | 不污染 infra `ActorPool.list_actors`；join 属于 application 层职责 |
| Bulk scan vs N × per-actor | **bulk** — 新 `assigned_actor_ids() -> set[str]` 单次扫所有 drama casting.md | N actor × M drama 调用次数从 N × M 降到 1 × M；50 actor × 5 drama 从 250 次 parse 降到 5 次 |
| DTO 字段 | `ActorListRowQdto.is_assigned: bool = False` (default False 保留向后兼容) | 既有 caller 不传 set 也能用 (legacy fallback `is_assigned=False`) |
| Mapper 签名 | `list_to_qdto(infos, assigned_ids=None)` + `info_to_qdto(info, is_assigned=False)` | 可选 kwarg；旧测试不破 |
| API endpoint | 复用 `GET /api/actors`，payload 加 `is_assigned` 字段 | 不开新 endpoint；前端 list 调用一次拿齐 |
| Frontend filter UI | 第 4 个 filter dropdown "分配状态"：全部 / 🎬 已分配 / ⚪ 未分配 | 与既有 民族/性别/年龄段 dropdown 平行 pattern |
| Tile 视觉 | 加 🎬 小 badge 在 actor.id 行末（已分配才显示）| 即使在 "全部" 模式下也能一眼区分；filter 切 "已分配" 时是冗余但 OK |
| `is_assigned` 是否含 `_deleted/` 内 actor | **否** — `assigned_actor_ids()` 只扫 `ai_videos/` 顶层非-`_` drama；`_deleted/_actors/` 内的 deleted actor 不出现在 listing 也无 assignment | follow-up 026/043 deleted actor 已从 listing 过滤；新字段语义一致 |
| Stale data | listing per click `/actors` route 重新 fetch；assign/unassign 触发 `onChange()` → tree refresh → 也 reload actors → is_assigned 跟新 | 与既有 follow-up 043 onSaved chain 一致 |

## 功能要求

### Backend

1. **`libs/infrastructure/writers/casting__writer.py`** `Casting` 类加方法：
   ```python
   def assigned_actor_ids(self) -> set[str]:
       """单次扫所有 drama casting.md，返回 union of actor_ids。"""
   ```
   实现：iterate `ai_videos/{drama}/casting.md`（跳过 `_`-prefix 系统 folder），parse 每个 row，把 `actor_id` 加入 set。

2. **`libs/domain/repositories/casting__repository.py`** Protocol 加 `assigned_actor_ids() -> set[str]` declaration。

3. **`libs/application/dtos/actor__dto.py`** `ActorListRowQdto`:
   - 加 `is_assigned: bool = False` field（default False 向后兼容）。
   - `to_dict()` 输出加 `"is_assigned": self.is_assigned`。

4. **`libs/application/mappers/actor__mapper.py`**:
   - `info_to_qdto(info, is_assigned=False)` — kwarg。
   - `list_to_qdto(infos, assigned_ids=None)` — 可选 set；提供则 per-row `is_assigned = info.id in assigned_ids`。

5. **`libs/application/queries/actor__query.py`** `ActorQuery.list()`:
   ```python
   def list(self) -> ActorListQdto:
       assigned_ids = self._casting.assigned_actor_ids()
       return ActorMapper.list_to_qdto(self._pool.list_actors(), assigned_ids=assigned_ids)
   ```

6. 不动 `apps/api/routes.py` — `actors_list` handler 已经 dispatch to `ActorQuery.list()`，payload 自动多 `is_assigned` 字段。

### Frontend

1. **`apps/ui/src/api.ts`** `ActorInfo` interface 加 optional `is_assigned?: boolean`。

2. **`apps/ui/src/components/ActorGrid.tsx`**:
   - 新 state `filterAssigned: "all" | "assigned" | "unassigned"` (default "all")。
   - `filteredActors` 加判断：`if (filterAssigned === "assigned" && !a.is_assigned) return false; if (filterAssigned === "unassigned" && a.is_assigned) return false`。
   - filter row 加第 4 个 `<label>分配状态<select>` — 全部 / 🎬 已分配 / ⚪ 未分配。
   - page reset effect dep 加 `filterAssigned`。
   - 每个 tile 的 `actor-tile-id` 行末加 🎬 badge（`actor.is_assigned` 时）。

3. **`apps/ui/src/styles.css`**:
   - `.actor-tile-id` 改 `display: flex; align-items: center; gap: 6px`（让 badge 自然贴在 id 右侧）。
   - 新 `.actor-tile-assigned-badge { font-size: 11px; opacity: 0.85; line-height: 1; }`。

### 不动

- spec.md / acceptance_criteria.md — listing field 增加是向后兼容，无 FR 行为变化。
- Container.py / route 层 — ActorQuery 已有 casting 注入（follow-up 043 起）。
- 其它 components（ActorView / CastingView / DeletedView）— 不需要 `is_assigned`。

## 安全 / 边界

- **`_deleted/` actor 不出现在 `assigned_actor_ids()`** — 因为 `assigned_actor_ids` 扫的是非-`_` drama 的 casting.md；已 unassign 的 deleted actor 不会标记 assigned。
- **空 casting.md 文件不会 crash**：`_parse` 返回空 list；`assigned_actor_ids` 跳过。
- **未来 actor count >> 50 时性能**：每次 `/actors` listing 触发 1 × drama_count 次 casting.md parse。M drama × N rows 单次 listing < 100ms 即便 drama=20 / row=50。如果未来项目变巨，可以 cache `assigned_actor_ids()` 结果直到下次 assign/unassign 修改。
- **跨 race**：用户 assign 一个 actor 的瞬间正好别人 list — listing 看到的是 fresh casting.md state（每次 parse fresh）。
- **`is_assigned` 字段缺失向后兼容**：前端 `?: boolean` optional；旧 list payload 无字段时所有 actor 视为 unassigned，filter 工作正常（只是 "已分配" 永空）。

## 不在本 follow-up 范围

- 不显示 assignment 数量（"这个 actor 分配到 3 个角色"）— 用户问题只要 binary filter；count 留给 ActorView 详情页 (FR-95 已有 `assignments[].length`)。
- 不在 listing 上 expand 每个 actor 的 assignment 列表 — 数据量过大，留 ActorView。
- 不动 ActorView 内 assign/unassign 流（FR-95 已支持）。
- 不写 vitest / pytest。
