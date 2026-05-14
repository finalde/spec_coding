# Follow-up draft 036 — 2026-05-13

**Summary:** 把 `ai_videos/_actors/actor_NNNN/` 文件夹在左侧导航树中折叠成**一个 leaf 节点**（不再展开成 folder + jpg + md 两层），点击 leaf → 进入 `ActorView`（已存在的 follow-up 034 视图）一页展示该 actor 的全部内容；该页同时承载所有相关操作（特别是 delete 按钮 — 与 sidebar 现有的 🗑 等价）。

## Source

> under ai_video_management actors, each actor has a folder, inside it we have md file as well as the jpg file combine the folder, jpg and md into 1 item on the left nav, so the 1 page will show everything about this actor and all the related operation like delete

## Abstracted instruction

1. **Tree shape — actor folder collapses to leaf.** `TreeWalker._walk_filtered` 在遍历到 `ai_videos/_actors/` 的直接子目录时，若该子目录名匹配 `^actor_\d{4,}$`，**不再递归展开**其内容；改为发射**单个 leaf 节点**：
   - `type: "actor"` (新 TreeNode 类型，介于 file/image/video 之间但语义上唯一)
   - `name: <actor_id>` (folder 名)
   - `path: ai_videos/_actors/<actor_id>/<actor_id>.md` (md 文件 — 点击导航的目标，触发 Reader → ActorView 渲染)
   - 不挂 `children`
2. **Frontend types.** `TreeNodeType` 添加 `"actor"`。
3. **Sidebar treats `type=actor` as a leaf row.**
   - 渲染图标 `🎭` (与 `_actors/` root icon 一致以建立视觉关联)
   - label 显示 actor_id (`actor_NNNN`)
   - 点击行 → `onSelect(node.path)` 即导航到该 md 文件，Reader 检测到 `isActor` → 渲染 `ActorView`
   - **保留** sidebar 现有的 🗑 delete 按钮（follow-up 026 的 `actor-delete-btn`），用同一 `isActorEntry` 检测但改为基于 `type==="actor"`
   - 不再展开/不再渲染 disclosure 三角
4. **ActorView 增加 delete 按钮（"all the related operation like delete"）。**
   - 在 `header` 右侧（title 同行）追加 "🗑 删除" 按钮。
   - 点击 → `window.confirm` 同 Sidebar 文案 → `POST /api/actors/delete` (FR-9i) → 成功后 `navigate("/")` 回主页并触发 tree refresh (`onSaved()` 回调链)
   - 失败 → 内嵌 alert 区域，红色背景，显示 `result.detail?.kind ?? error.message`
   - 加载中状态：按钮 disabled + 文案 "删除中…"
5. **Reader plumbing.** `Reader` 接收 `onSaved` (已有) 用于 tree 刷新；新增可选 prop 或复用 `onSaved` 给 ActorView 让 actor 被删除后 sidebar 立即少一行 — 选择复用 `onSaved` 不加新 prop。
6. **Backend 0 行为变动 except tree shape.** `/api/actors/delete` (FR-9i) 已经存在并支持 cascade-unassign + folder rename。该 endpoint 也已经被 sidebar 直接调用 (follow-up 026)。ActorView 内的 delete 按钮**复用同一 endpoint** — 没有新 API。
7. **Out of scope.**
   - 不动 `_deleted/_actors/` 的展示（保持递归展开，方便查看已软删除 actor 的内容）。
   - 不动 ActorGrid 的网格行为 (follow-up 028/030/032/033)。
   - 不动 CastingView 的 actor 选择器（仍按 `GET /api/actors` 返回的扁平列表呈现）。

## Why now

折叠前，每个 actor 在 sidebar 占 3 行（folder ▾ + jpg 🖼 + md 📄），200 个 actors 就是 600 行展开后的节点；几乎从不需要单独点 jpg 或 md（jpg 已经在 ActorView 顶部展示，md 已经被 ActorView 解析成结构化视图）。折叠成单 leaf 后，导航成本从 N×3 行降到 N 行，且语义上"actor"就是一个原子单位 — folder 名等于 actor_id 等于稳定的 casting reference key。把 delete 操作放进 ActorView 同时保留 sidebar 的 🗑 按钮，给出两条等价路径（左侧扫一眼批删 vs 进入 actor 详情核对后再删），与 follow-up 030 的 ActorGrid bulk delete 形成完整的 1/N/批量三级删除矩阵。

## Acceptance

- 加载 `/` 后展开 `ai_videos/_actors/`：每个 `actor_NNNN` 显示为**单行** `🎭 actor_NNNN` + 右侧 🗑 按钮，**不显示**展开三角，**不显示**任何 jpg/md 子节点。
- 点击 `actor_NNNN` 行 → URL 变为 `/file/ai_videos/_actors/actor_NNNN/actor_NNNN.md` → 主区渲染 `ActorView`（face 图 + 属性表 + prompt card + Copy + **新增**的 🗑 删除按钮 + 顶部 title）。
- ActorView 的 🗑 删除按钮触发 `window.confirm` → 确认后 `POST /api/actors/delete` → 200 后导航回 `/` 且 sidebar 不再显示该 actor 行。
- Sidebar 行中的 🗑 按钮仍按 follow-up 026 行为工作（无变化）。
- 其他左侧节点 (drama folder / `_deleted/_actors/` / research) 行为均不变。
