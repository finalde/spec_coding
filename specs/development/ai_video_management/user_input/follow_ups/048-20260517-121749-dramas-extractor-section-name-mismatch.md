# Follow-up draft 048 — 2026-05-17

Summary: 修 ActorView "＋ 添加分配" 按钮永远 disabled 的 bug。`apps/ui/src/lib/dramas.ts` 的 `extractDramas(tree)` 调用 `findChild(tree, "ai_videos")` 找小写 section name，但 backend `tree__reader.py::_ai_videos_section` 返回 `name: "AI Videos"`（display 字符串，原 follow-up 003 之后的 sidebar 三段式重命名所致）— `findChild` 永远返回 `null`，`dramas.length === 0`，ActorView line 240 与 AssignForm line 336 同时 disable。同 bug 也影响 `ActorGrid` 的 "🎬 分配角色 (N)" bulk-assign 模态。`Home.tsx:56` 已正确按 `c.name === "AI Videos"` 找 section — 证明 section 名确实是 "AI Videos"。

## 用户原话

> the button to assign actor is disabled on the front end

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| 修复手段 | **改 `extractDramas` 通过 path-prefix 找 ai_videos 段而不是 name** | path 是 backend 契约（`ai_videos/{drama}` 在 FR-1 / FR-43 已固定，跨重命名稳定），name 是 display string（"AI Videos" / "ai_videos" / 中文都可能）。bullet-proof 写法 |
| 实现 | 新增 helper `findAiVideosSection(tree)`：BFS 找第一个 `node` 满足 `node.children.some(c => c.path?.startsWith("ai_videos/"))` | top 是 `type="section" name="root"` 嵌套；两层下降即可。BFS 不假设深度 |
| 保留 path-prefix 二次过滤 | 是 — 在 children 遍历内再 `drama.path?.startsWith("ai_videos/")` 兜底 | 防止以后 backend tree shape 又变（e.g. 加包装层）漏到 dramas 里来 |
| 不动 `findChild` 签名 | 是 | 仍按 name 找 `characters` 子目录（"characters" 是磁盘真名，稳定）|
| 不动 Home.tsx | 是 | 它的 `name === "AI Videos"` 写法虽脆但目前正确；本 follow-up 不扩范围；与 dramas.ts 各自独立 |
| 不改 tree__reader.py 改回 lowercase | 是 | sidebar 三段式 display 用 "AI Videos" 中英对照（"AI Videos" / "Research"）是 follow-up 003 的 UX 决策；不能为修一个消费方而改契约 |
| 不重写 ActorView / ActorGrid | 是 | 它们 import `extractDramas`；改一处修两处 |
| 测试 | 暂不写自动化（沿用 005-045 推迟批量补测）| 用户手动验证：进 ActorView，"＋ 添加分配" 应可点击 |

## 功能要求

### Frontend

**`projects/ai_video_management/apps/ui/src/lib/dramas.ts`**：
- 改 `extractDramas(tree)`：
  - 用新 helper `findAiVideosSection(tree)` 找 section 节点。
  - 在 drama 遍历内追加 `drama.path?.startsWith("ai_videos/")` 二次过滤兜底。
- 新增 `findAiVideosSection(tree: TreeNode): TreeNode | null`：BFS，命中条件是"该节点的 children 中至少一个 `path.startsWith("ai_videos/")`"。
- 不动 `findChild`、`DramaChoice` 接口、export 列表。

### Spec / validation

- `final_specs/spec.md`：FR-91（ActorGrid bulk assign）+ FR-95（ActorView assignments，follow-up 043 引入）相关行追加 follow-up 046 amendment 一句：drama 列表通过 path-prefix 查找而非 section name lookup。
- `validation/acceptance_criteria.md`：U3.23（follow-up 043 ActorView assignments）追加一段 "given /api/tree 返回 section 名='AI Videos'" 的前置条件，确保未来回归。
- `validation/acceptance_criteria.md` 覆盖矩阵无新行（同 FR-95 + FR-91 覆盖，仅扩 Gherkin 文字）。
- `user_input/revised_prompt.md`：header bump for 046。
- `changelog.md` 加 follow-up 046 entry。

## 安全 / 边界

- **纯前端 lib 改动**，0 backend、0 HTTP route、0 endpoint shape 变化。
- **path-prefix 查找无歧义**：tree node 的 `path` 字段是 backend 用 `Path.relative_to(repo_root).as_posix()` 算出来的；`"ai_videos/{drama}"` 是磁盘 layout 的 ground truth，不会跨语言 / 本地化变。
- **BFS 不会进入"deleted" 子树**：第一个命中的 section 就返回，不递归到 dramas 内部。
- **空树 / null tree** 仍按原行为返回 `[]`。
- **`_actors/` / `_deleted/`** 系统 folder 仍被 `drama.name.startsWith("_")` 过滤掉，行为不变。
- **没字符 folder 的 drama** 仍以 `characters: []` 出现，由 AssignForm 第二级 select disabled + 提示文本处理（line 305–311 原逻辑）。

## 不在本 follow-up 范围

- 不重命名 backend section 名回 "ai_videos"（UI 三段式契约）。
- 不重写 Home.tsx 的 `c.name === "AI Videos"` 直接匹配（它独立工作；本次只修真正 broken 的路径）。
- 不动 `lib/linkResolver.ts` 或其他 tree walker。
- 不写 frontend Vitest（统一推迟）。
- 不动 backend `Casting` / `find_assignments_for_actor` / 任何 endpoint。
- 不动 ActorGrid / ActorView 组件本身（修一处 lib 改两处消费方）。
