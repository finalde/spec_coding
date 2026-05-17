# Follow-up draft 046 — 2026-05-17

**Summary:** Backend 500 on every `POST /api/casting/assign` and `DELETE /api/casting/assign`. Root cause: `apps/api/container.py` 在 follow-up 039 DDD 迁移期间把 `Casting` provider 的 kwarg 写成 `media_renamer=media_renamer`，但 `libs/infrastructure/casting__writer.py::Casting.__init__` 的形参名是 `renamer`。`dependency_injector.providers.Singleton(Casting, ..., media_renamer=...)` 在首次解析时调 `Casting(exposed=..., resolver=..., media_renamer=..., actor_pool=...)` → `TypeError: __init__() got an unexpected keyword argument 'media_renamer'` → FastAPI 转 500。

## Source

> the feature seems not working, when trying to assign the actor to a charactor, it shows 请求失败: 500

## Abstracted instruction

1. **Fix the kwarg.** 在 `apps/api/container.py` 把 `Casting` provider 的 `media_renamer=media_renamer` 改成 `renamer=media_renamer`。命名约定上 provider 变量名仍叫 `media_renamer`（与其他 provider 一致），只是绑定到 `Casting.__init__` 的形参 `renamer` 时改用正确的关键字。
2. **No other changes.** `Casting.__init__` 签名保持 `renamer` —— 与 follow-up 014 时的旧 `backend/libs/casting.py` 字节一致；改 provider 的 kwarg 风险更小（影响面 = 一处）。`/api/casting/assign` (FR-9g) + `/api/casting/assign` DELETE (FR-9h) + ActorView assign 表单（FR-95 follow-up 043）从 500 恢复 200。
3. **Out of scope.** 不改 DDD 命名约定（infrastructure 类的 `__init__` 形参 vs container 字段名是否要一致是更大的设计讨论，留给后续）；不动 routes / endpoint shape / `_cast.md` 写入 / refuse-if-assigned 逻辑。

## Why now

Follow-up 043 在 pre-039 layout（`backend/libs/api.py` 手工构造 `Casting(exposed, resolver, media_renamer, actor_pool)` 位置参数）下 end-to-end 验证通过；039 迁移后 `container.py` 改用 `dependency_injector` 关键字参数，但 kwarg 名未与构造函数签名对齐，所有走 DI 的 casting 调用立刻 500。`fetchActorAssignments` 走 `find_assignments_for_actor` 不经过构造函数那条 unhealthy path 看起来 OK 是因为 ActorPool 单独构造成功（route 用 `_refuse_if_actor_assigned` helper 注入 casting 时同样 500，但用户先撞到 assign 表单提交路径）。Bug 是纯 wiring 不一致，零业务逻辑改动。

## Acceptance

- `POST /api/casting/assign` 用合法 `{path, role, actor_id, notes}` 返回 200 + `{path, entries}`，并写入 `ai_videos/{drama}/characters/{role}/_cast.md`（per FR-9g follow-up 043）。
- `DELETE /api/casting/assign` 用同 path/role 返回 200 并删除 `_cast.md`（per FR-9h follow-up 043）。
- ActorView "确认分配" 按钮：不再触发 `请求失败: 500` alert；assignment 出现在列表中。
- `GET /api/actors/assignments?actor_id=...` 仍返回 200（之前也 200，因为 casting singleton 在该路径解析时同样 throw，但 helper `_refuse_if_actor_assigned` 在该 endpoint 链路中也曾经 500 — 修复后两端都 200）。
