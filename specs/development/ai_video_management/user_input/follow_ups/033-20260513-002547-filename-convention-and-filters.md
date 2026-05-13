# Follow-up draft 033 — 2026-05-13

三个相关改动:

1. **新 jpg 文件命名约定**: 从 `actor_NNNN/actor_NNNN.jpg` 改为 `actor_NNNN/{race}__{gender}__{age_range}.jpg`。`__` (double-underscore) 作为分隔避免与 css class 命名歧义；folder 名仍是 `actor_NNNN/` 保留稳定 ID（casting.md 等已引用），仅 jpg 文件名描述化方便文件系统浏览
2. **Filters on ActorGrid**: 加 race / gender / age_range 三个过滤 dropdown，"全部" 默认；过滤后 actors 列表再走分页
3. **Migrate existing actors**: app 启动时 idempotent 扫描 `_actors/`，把 `actor_NNNN.jpg` 重命名到新格式（从 sidecar 读 attrs）

## 用户原话

> lets introduce some convention for the actor file names, it should be always {民族}__{性别}__{年龄段}.jpg, and then in the main 演员池page, lets add filters, like filter by race, filter by gendor, filter by age etc. and make your best guess to update existing actors to follow this new rule

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| 文件名格式 | `{race}__{gender}__{age_range}.jpg` 在 `actor_NNNN/` folder 内 | 用户原话；`__` 双下划线避免与 css 命名歧义 |
| Folder 名 | **不变** 仍 `actor_NNNN/` | folder 名作为 actor_id 已被 casting.md / sidebar / API 引用 |
| 同 attrs 多 actor 冲突 | 不会 — 每个 actor 一个独立 folder，folder 内仅一个 jpg | 同 attrs 的 jpg 在不同 folder 不冲突 |
| Sidecar `.md` | **保持** `actor_NNNN.md` (跟 folder 名) | 便于命令行 / 文件浏览器看 sidecar 与 folder 同名；不随 attrs 改变 |
| Migration 触发点 | **app 启动时**（`create_app`/`actor_pool` 构造后），idempotent，单次扫描 | 一次性 op；下次启动是 no-op |
| Migration 范围 | 仅 `ai_videos/_actors/actor_NNNN/`；**跳过** `_deleted/_actors/` | 软删除文件保持原状不动 |
| Migration 失败处理 | per-folder try/except；OSError → 跳过该 folder 记 warning；不影响其他 | 不能让一个坏文件挡所有启动 |
| `list_actors` 兼容 | 优先找新格式 `*__*__*.jpg`，找不到再 fallback 找 `{actor_id}.jpg` | 启动 migration 跑过后老格式应该不存在，但多一层兜底 |
| `actor_exists` 同上 | 同 `list_actors`：检查 folder 存在 + 任意 `.jpg` 文件 | 不绑死 filename |
| `_next_actor_id_num` 中"complete" 检查 | 改为"folder 含任意 `.jpg`" 而非 `{actor_id}.jpg` | 与新命名一致 |
| Filter UI | 三 dropdowns（race / gender / age_range），"全部" 默认 | 用户原话；与现有 ATTR_OPTIONS 复用 |
| 过滤行为 | client-side filter on already-fetched actors list | 数据已 in-memory，无需新 API |
| 过滤 + 分页 | 先 filter → 再 page；filter 变化时 page 重置到 0 | 标准模式 |
| 过滤状态持久 | in-memory；URL / localStorage 不持久 | v1 简单 |

## 功能要求

### Backend

**`projects/ai_video_management/backend/libs/actor_pool.py`**:

1. 新增 helper `_attrs_to_filename(attrs: ActorAttrs) -> str`:
   - 返回 `f"{attrs.ethnicity}__{attrs.gender}__{attrs.age_range}.jpg"`
2. 修改 `generate_batch` 的 jpg 路径:
   - `jpg_path = actor_folder / _attrs_to_filename(attrs)` 替代 `actor_folder / f"{actor_id}.jpg"`
3. 修改 `list_actors`:
   - 优先 glob `*__*__*.jpg`；没找到则 fallback `{actor_id}.jpg`；都没有则 skip
4. 修改 `actor_exists`:
   - 不再检查具体 filename，改为 `any(folder.glob("*.jpg"))`
5. 修改 `_next_actor_id_num` (历史 in-progress reap 逻辑 follow-up 027 已分到 `_reap_incomplete_folders`):
   - `_reap_incomplete_folders`: "有 jpg" 检查改为 `any(entry.glob("*.jpg"))` 而非具体 filename
6. 新方法 `migrate_filenames() -> dict[str, int]`:
   - 扫 `_actors/actor_NNNN/`
   - 对每个 folder：若已含 `*__*__*.jpg` → skip；否则若含 `{actor_id}.jpg` → 读 sidecar `_parse_sidecar` 拿 attrs → rename → 记 ok
   - per-folder try/except；失败记 warning
   - 返回 `{"migrated": N, "skipped": M, "errors": K}`
7. `ActorPool.__init__` 末尾自动调 `migrate_filenames()` 一次（idempotent；缺 `_actors/` dir 时静默 skip）

### Frontend

**`projects/ai_video_management/frontend/src/components/ActorGrid.tsx`**:

- 新增 3 个 filter state: `filterEthnicity`, `filterGender`, `filterAgeRange`；default `"all"`
- Filter UI: 在 header 加三个 `<select>` + "全部" option
- 派生 `filteredActors = actors.filter(...)` (filter `"all"` skips)
- 改 `pageActors` 用 `filteredActors`
- 改 `totalPages` 用 `filteredActors.length`
- Filter 变化时 setPage(0)

**`projects/ai_video_management/frontend/src/styles.css`**:

- 加 `.actor-grid-filters` (flex row of dropdowns)

### Spec / validation

- `final_specs/spec.md` FR-9f: 描述 new jpg filename + sidecar 不变 + auto-migrate
- `final_specs/spec.md` FR-91: 加 filter UI 描述
- `validation/security.md` 无新 carve-out
- `validation/acceptance_criteria.md` U3.15: 加 jpg 文件名匹配 `{race}__{gender}__{age_range}.jpg`；U3.18: 加 filter 多组合断言

## 安全 / 边界

- **No new HTTP surface** — migration 是 backend 内部；filter 纯前端
- **No new write surface** — migration 是 rename within `_actors/`，仍在 EXPOSED_TREE 内
- **Migration 失败兜底** — per-folder try/except；坏文件不阻塞 app 启动
- **Sidecar 不动** — 仅 jpg 重命名

## 不在本 follow-up 范围

- 不引入 filter "look" / "style"（v1 只 race/gender/age 三轴；用户原话）
- 不引入 search 框
- 不引入 filter 状态 URL / localStorage 持久化
- 不动 folder 名 `actor_NNNN/`
- 不动 sidecar 名 `actor_NNNN.md`
- 不动 `_deleted/_actors/` 内文件
- 不动 casting.md 引用（actor_id 仍是 folder 名）
- 不写 pytest / Vitest
