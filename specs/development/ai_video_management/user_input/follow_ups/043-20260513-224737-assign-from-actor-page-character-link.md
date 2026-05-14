# Follow-up draft 043 — 2026-05-13

**Summary:** ActorView 增加"角色分配"区块：用户在 actor 页用两层级联 dropdown（drama → 角色 folder）把当前 actor 挂到一个 ai_video 项目里的某个 c{N}_* 角色；assign 时在该角色 folder 内写 `_cast.md` 让 char folder 也能看到所选 actor（含 face 图）；一个 actor 可在不同 ai_video 项目里挂多个角色，但一个 ai_video 项目里同一角色只能挂 1 个 actor（由 casting.md upsert 已保证）；**actor 一旦有任何分配，禁止 delete / archive**。

## Source

> lets add a new feature for the actor page, I could assign the actor to a specific role under a specific ai_video project. It is like multi dropdown. Once assigned the role, you need to maintain a link of the actor under the charactor folder, you could aslo see the picture of the actor. Note one actor could play many roles in differnet ai videos, but one ai vidoe charactor could only be one actor. When an actor has a role assigned, it cannot be deleted or archived.

## Abstracted instruction

1. **ActorView 顶部新增"角色分配"区块**（在元数据块上方或下方均可，建议下方与 prompt card 同列）：
   - 区块顶 header："🎬 角色分配 (N)" — N 是当前 assignments 数量。
   - **N==0 时**渲染："尚未分配到任何角色" 文案 + "+ 添加分配"按钮。
   - **N>0 时**渲染每行：`{drama} / {role}`（drama folder name + role folder name 两段，加 `/` 分隔）、可选 notes（如有）、行尾"取消分配"按钮。下方仍有 "+ 添加分配" 按钮。
2. **"+ 添加分配" 表单**（inline，不必 modal）：
   - **第 1 个 dropdown：短剧（drama）**。选项 = 来自当前 tree 的 `ai_videos/` 直接子目录中**非 `_` 前缀**的 `type === "directory"` 节点。复用 `ActorGrid.extractDramas` 抽取逻辑（移到 `lib/dramas.ts` 共享）。
   - **第 2 个 dropdown：角色 (role)**。选项 = 选中 drama 的 `characters/` 子目录中匹配 `^c\d+(_.*)?$` 的子目录名（同 ActorGrid 规则）。drama 变化时角色列表重算并 reset 到首项。
   - **可选 notes textarea**（≤ 500 字符），默认空。
   - 确认按钮 → `POST /api/casting/assign` body `{path: "ai_videos/{drama}", role, actor_id, notes}` → 成功 toast + 刷新 assignments 列表。
   - 失败 → 表单内 alert 显示 `detail?.kind ?? status`。
3. **后端 character link file (`_cast.md`)：**
   - 路径：`ai_videos/{drama}/characters/{role}/_cast.md`
   - `Casting.assign()` 在 `casting.md` upsert 之后，**同步**调一个 helper `_write_character_link(drama_dir, role, actor_id, notes)`：
     - 若 `{drama_dir}/characters/{role}/` 不是 directory（角色 folder 不存在），**静默跳过**（casting.md 仍写入；这条 assignment 只在 casting.md 内可见）。
     - 否则原子写 `_cast.md`（temp + os.replace），内容含 Chinese metadata table + `![face](../../../_actors/{actor_id}/{face_filename})` 内嵌图 + `[查看演员档案](../../../_actors/{actor_id}/{actor_id}.md)` 链接 + 维护注释。
     - face 文件名通过 `actor_pool.face_filename(actor_id)` 解析（新公开 helper，复用既有 `_find_actor_jpg`）；找不到时 `_cast.md` 仅含 metadata + link，**不渲染 broken `![face]`**。
   - `Casting.unassign()` 在删 row 后，同步删 `_cast.md`（best-effort，FileNotFoundError 静默）。
   - `Casting.unassign_actor_everywhere()` 在 sweep 删 row 时，同步删每条对应的 `_cast.md`（保留方法但 endpoint 不再调）。
4. **新后端 endpoint `GET /api/actors/assignments?actor_id={id}`：**
   - Body: query string `actor_id`，shape `^actor_\d{4,}$`。
   - 返回：`{actor_id, assignments: [{drama: str, role: str, notes: str, character_folder: str, character_folder_exists: bool}]}`，按 (drama, role) 字典序。
   - 实现：`Casting.find_assignments_for_actor(actor_id) -> list[dict]`，扫 `ai_videos/` 下所有非 `_` 前缀的 drama folder，解析每个 `casting.md`，取 `actor_id` 匹配的行。
   - Status: `200`, `400 invalid_actor_id`, `405 method_not_allowed`。
5. **删除/归档拒绝（actor 有分配时）：**
   - `POST /api/actors/delete` (FR-9i)：**改写**为 cascade-unassign **不再执行**；改为 (a) 先调 `casting.find_assignments_for_actor(actor_id)`；(b) 若 `assignments` 非空 → 返回 `409 {kind:"actor_is_assigned", assignments:[...]}` 并**不**调 `actor_pool.delete_actor`；(c) 若空 → 走原 rename 路径。响应 shape：成功返回保留 `from / to`，去掉 `unassigned`（一致 200 contract）— 写测试时注意。
   - `POST /api/archive-media` & `POST /api/delete-media`：若 path 形如 `ai_videos/_actors/actor_NNNN/...`，先 extract `actor_NNNN` 并查 `find_assignments_for_actor`；非空 → 409 `{kind:"actor_is_assigned", actor_id, assignments}`。否则走原逻辑。`_deleted/_actors/` 下的路径不在 `_actors/` 直系下，自动豁免。
   - Sidebar 的 🗑 按钮以及 ActorView 的 🗑 按钮：成功执行后行为不变；当 backend 返 409 `actor_is_assigned`，UI 显示 alert 列出冲突 assignments（"无法删除 actor_NNNN — 已分配到 {drama}/{role}（共 N）"）。
6. **ActorView delete 按钮 disabled 状态：**当 assignments.length > 0，delete 按钮 disabled + tooltip "actor 当前分配到 N 个角色，无法删除"。Sidebar 行的 🗑 按钮**不要求**前端预先 disabled —— backend 已拒绝（用户也未要求两端同步），但 backend 错误 toast 文案要清晰。
7. **前端 api.ts 增加：** `fetchActorAssignments(actorId) -> ActorAssignmentsResult`；类型 `ActorAssignment` + `ActorAssignmentsResult`。
8. **App.tsx / Reader.tsx 把 `tree` 透传给 ActorView**（与 ActorGrid 的现有模式一致；ActorView 读 tree 派生 `dramas`）。
9. **共享 dramas 抽取逻辑**：把 `ActorGrid.tsx` 现有的 `extractDramas` + `findChild` + `DramaChoice` 类型迁到 `src/lib/dramas.ts`；`ActorGrid.tsx` 与新 `ActorView.tsx` 都 import 之。零行为变化。
10. **Out of scope**：
    - 角色 dropdown 不显示已被占用 vs. 空闲；用户假设知道目标 drama 当前哪些角色已有 actor（CastingView 是真相源）。再次 assign 同一 role → upsert 行为不变。
    - 不动 ActorGrid 的 bulk assign 流（FR-91 follow-up 030）；它仍走同样 `Casting.assign` → `_cast.md` 也会随之同步写入（隐式收益）。
    - 不为 `_cast.md` 加专门的 Reader render mode；它走通用 markdown 渲染分支，图片通过 ![face](...) 标准 markdown 语法 + 现有 renderer image src 解析。
    - 不在 _cast.md 内置编辑能力 / 不让 _cast.md 反向触发 casting.md（_cast.md 是衍生物，casting.md 是真相）。

## Why now

之前 actor → role 分配只能从 CastingView（drama 视角）或 ActorGrid 批量 modal（pool 视角）发起，actor detail 页是哑读视图。把分配能力放进 ActorView 让"我现在看着这张脸，想把它指派给某个角色"这条最常见的 mental motion 在同一页完成。`_cast.md` 这层把分配在 character folder 也"可见化"，让创作者在 drama tree 浏览角色 folder 时一眼看到当前 actor 的脸 + 跳回演员档案。Delete 拒绝把"actor 是 casting.md 引用源"从软约束（cascade-unassign 静默清理）改为硬约束，避免用户因为删错 actor 而丢失多个 drama 的精心分配。

## Acceptance

- ActorView 渲染时调 `GET /api/actors/assignments?actor_id=actor_0013` → 收到 `{assignments: [...]}` → 区块按上述规则 render。
- "+ 添加分配" 表单的两 dropdown 级联正确：drama 改变 → role 列表重算 → 第一项被选中。
- 确认分配 → `POST /api/casting/assign` 200 → 列表多一行；同步在 `ai_videos/{drama}/characters/{role}/_cast.md` 出现新文件，content 含 actor_id 链接 + face 图 markdown。
- 行内"取消分配" → `DELETE /api/casting/assign` 200 → 列表少一行；`_cast.md` 文件被删。
- 当 actor 有 ≥1 个 assignment：ActorView delete 按钮 disabled + tooltip 出现。
- 强行 `POST /api/actors/delete` actor_id="actor_NNNN" 在 assigned 状态：返回 409 `{kind:"actor_is_assigned", assignments:[...]}`，folder 不动。
- `POST /api/archive-media path="ai_videos/_actors/actor_NNNN/{jpg}"` 在 assigned 状态：返回 409 `{kind:"actor_is_assigned"}`，文件不动。
- character folder 不存在时 assign 仍然成功（casting.md 有 row，无 `_cast.md` 写入）—不算错误。
