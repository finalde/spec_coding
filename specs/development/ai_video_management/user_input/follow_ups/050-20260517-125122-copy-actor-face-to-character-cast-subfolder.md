# Follow-up draft 050 — 2026-05-17

Summary: 给 actor 分配角色时，除了写 `_cast.md` 与 `casting.md` row（follow-up 043 既有行为），后端再把 actor face jpg 复制到 character folder 的 `cast/` 子目录，命名 `{actor_id}_face.{ext}`（保留源扩展名）。Unassign 时清空 `cast/` 子目录；reassign 时 sweep-then-copy 自动替换。`_cast.md` 内嵌图片 markdown 链接同步改用 local 相对路径 `cast/{actor_id}_face.{ext}`，去掉 `../../../_actors/` 跨级 traversal — 让 character folder 在 Seedance/Kling 等模型 prompt 时**自包含**，不依赖 `_actors/` 仍在 sandbox 内。

## 用户原话

> when assign an actor to a charactor, could you also copy the actors artifacts like image to the charactor folder

## 交互问答记录（启动前）

| 问 | 用户选 |
|---|---|
| 复制范围 | **Just the face jpg** — 仅一个 jpg；不复制 sidecar md / 不 mirror 整个 folder |
| Layout | **`cast/` 子目录 + `{actor_id}_face.{ext}` prefix** — 让 character root 干净，文件名带 actor_id 防 reassign 历史冲突（虽然本方案 unassign/reassign 都 sweep clean，prefix 仍保留以备万一 cast 内出现外部加文件） |
| 清理策略 | **Delete on unassign; replace on reassign** — character folder 永远 mirror 当前 assignment；无 stale orphan |

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| 复制工具 | `shutil.copyfile(src, dst)` | stdlib；保留文件内容，不复制 metadata（mtime / perms）— 后续 webapp `mediaUrl` 走 mtime cache-bust 用新 file 的 mtime 即可 |
| 目标 filename | `{actor_id}_face{ext}`（`ext` 取自 source `Path(face_filename).suffix`；默认 `.jpg`） | 保留源扩展名以兼容未来 png/webp face；prefix `{actor_id}_face` 唯一，未来若加 actor 多媒体（ref 视频）可同 prefix 扩 `{actor_id}_ref.mp4` |
| Sweep 策略 | 写入前 sweep `cast/` 中 `^actor_\d{4,}_face\.[a-z0-9]+$` 文件后再 mkdir + copy | 单 role 仅一个 actor → 任一时刻 cast/ 内至多一个 face；reassign 自动顶替；用户手工放进 cast/ 的其它文件（非 actor face 模式）不被 sweep |
| Sweep 后 rmdir 空 `cast/` | 是（best-effort）| 不留空 folder；与 follow-up 008 archive/ rmdir 风格一致 |
| copy 失败 | swallow OSError → `_cast.md` 不嵌入图片（face_md 段为空，与 face_filename=None 等价分支共用）| `casting.md` 是 truth source，face 仅 UI 嵌图；不让磁盘 issue 阻塞分配 |
| `_cast.md` 内 link | 改为 `cast/{actor_id}_face.{ext}` 相对路径（同 character folder 内） | 自包含 — 把 character folder 整段复制到任何地方仍能加载图片；以前 `../../../_actors/...` 三级跳出 sandbox 反 |
| "查看演员档案"链接 | **保留** `../../../_actors/{actor_id}/{actor_id}.md` | sidecar 是 authoritative，不复制；用户点链接仍能跳到 actor 档案查看 attrs |
| Sidebar 显示 `cast/` | **正常显示**（不 hide / 不 system-folder 化）| `cast/` 不以 `_` 起首；用户应当看见复制了什么；与 follow-up 023 `_deleted/` (隐藏行为已撤回为 sidebar 置底) 设计哲学相同 — visibility 强于 invisibility |
| `cast/` 文件夹名 | `cast`（不 `_cast`） | 已有 `_cast.md` 文件 — 同 folder 内文件夹也叫 `_cast/` 会 ambiguous（虽然 OS 允许同名不同类型；但视觉冲突重）；`cast/` 区分清晰 |
| 失败回滚 | copy 写入 cast/face.jpg 失败 → 已写完 casting.md row 不撤回；下次 assign 会 retry copy | casting.md row 是 truth；copy 是 secondary artifact。与 follow-up 043 `_cast.md` 写入 swallow OSError 同语义 |
| `unassign_actor_everywhere`（follow-up 026 cascade，code 仍在但 post-043 无 caller） | 同步加 sweep 调用 | 一致性 — 即便目前 dead code，未来 revive 时不发现 cast/ 残留 |

## 功能要求

### Backend

**`projects/ai_video_management/libs/infrastructure/casting__writer.py`**：

1. 新增常量 + import：
   ```python
   import shutil
   _CAST_DIR_NAME = "cast"
   _CAST_FACE_RE = re.compile(r"^actor_\d{4,}_face\.[a-zA-Z0-9]+$")
   ```

2. 新增私有方法 `_sweep_cast_dir(self, cast_dir: Path) -> None`：
   - 若 `cast_dir` 不是 directory → return。
   - 遍历 `cast_dir.iterdir()`，对每个 file `entry.is_file() && _CAST_FACE_RE.match(entry.name)`：`entry.unlink(missing_ok=True)`，OSError swallow。
   - best-effort `cast_dir.rmdir()` 若空（OSError swallow）。

3. 新增私有方法 `_copy_actor_face(self, character_folder, actor_id) -> str | None`：
   - 用 `_actor_pool.actor_face_filename(actor_id)` 拿 source 文件名 `face_filename`；None → return None。
   - source = `_actor_pool.actors_dir() / actor_id / face_filename`；不存在 / 非 file / 是 symlink → return None。
   - ext = `Path(face_filename).suffix.lower()` (默认 `.jpg`)；dst_name = `f"{actor_id}_face{ext}"`。
   - cast_dir = `character_folder / _CAST_DIR_NAME`；`cast_dir.mkdir(exist_ok=True)`；OSError → return None。
   - `shutil.copyfile(str(source), str(cast_dir / dst_name))`；OSError → return None。
   - 返回 dst_name (e.g. `"actor_0013_face.jpg"`)。

4. 改 `_write_character_link(drama_dir, role, actor_id, notes)`：
   - 先 sweep：`self._sweep_cast_dir(character_folder / _CAST_DIR_NAME)`（处理 reassign 替换 + 新 cast/ 不存在的 no-op 分支）。
   - 调 `dst_name = self._copy_actor_face(character_folder, actor_id)`。
   - 将 `dst_name` 传给 `_build_character_link_body` 替代旧 `face_filename`。

5. 改 `_build_character_link_body` 签名：
   - 参数 `face_filename` 改为 `face_copy_filename: str | None`；语义从"_actors 内 face 文件名"变为"cast/ 内 copy 文件名"。
   - markdown image 链接：`![{actor_id} face](cast/{face_copy_filename})`（本地相对路径）。
   - "查看演员档案"链接仍指向 `../../../_actors/{actor_id}/{actor_id}.md`。

6. 改 `_remove_character_link(drama_dir, role)`：
   - 删 `_cast.md`（既有逻辑）。
   - 新增：`self._sweep_cast_dir(drama_dir / "characters" / role / _CAST_DIR_NAME)`。

7. 不改 `assign` / `unassign` 顶层签名 — caller 透明。

### 不动

- 路由层 `apps/api/routes.py` 不动 — `Casting.assign` / `unassign` 行为契约对调用方不变（仅副作用 surface 多出 cast/ 拷贝）。
- 前端 `apps/ui/src/components/ActorView.tsx` / `Reader.tsx` / `CastingView.tsx` 不动 — 不需要新 prop / 新 UI 元素。
- 前端 `lib/dramas.ts` 不动。
- `actor_pool__writer.py` 不动 — `actor_face_filename` / `actor_exists` 现有 API 已够。
- `agent_refs/project/ai_video.md` 不动 — `cast/` 是 webapp 副作用，不是 ai_video 任务 generation contract（rule #12.x 都是讲 prompt 内容，不讲 webapp 维护的辅助文件）。

### Spec / validation

- `final_specs/spec.md` FR-9g（`POST /api/casting/assign`）追加 amendment：除写 `casting.md` row + `_cast.md` 外，复制 actor face jpg 到 `characters/{role}/cast/{actor_id}_face.{ext}`；reassign 自动 sweep；OS 失败时 fall-through（仅 `_cast.md` image 段为空）。
- `final_specs/spec.md` FR-9h（`DELETE /api/casting/assign`）追加 amendment：除删除 `_cast.md` 外，sweep `characters/{role}/cast/actor_*_face.*` + 空 cast/ best-effort rmdir。
- `final_specs/spec.md` FR-95（ActorView assignments section）追加一句：assign 触发 backend 复制 face 到 character folder 的 `cast/` 子目录；ActorView UI 不变。
- `validation/acceptance_criteria.md` U3.23（follow-up 043 ActorView assignments）扩展 Gherkin：assign 后 `characters/{role}/cast/{actor_id}_face.jpg` 存在 + `_cast.md` 内 image link 指向 `cast/{actor_id}_face.jpg`；reassign 新 actor → 旧 actor 文件被删 + 新 actor 文件出现；unassign → cast/ 内 face 被删；空 cast/ rmdir。

### User input + audit

- `user_input/revised_prompt.md`：header bump for 050。
- `changelog.md`：append follow-up 050 entry。
- `specs/ai_video/mozun_chongsheng/changelog.md`：append 平行 entry（cross-task — 改了 mozun 下 character folder 的副作用 surface）— 但**不立刻 backfill 现有 assignments**（follow-up 050 是行为契约更新，未来 assign / 触发 reassign 时才生效；用户若要 backfill 已有 assignments 走 unassign-then-reassign）。

## 安全 / 边界

- **Sandbox**：source = `_actors/{actor_id}/{face_filename}`（在 `ai_videos/` 内）；dst = `characters/{role}/cast/{actor_id}_face.{ext}`（在 `ai_videos/` 内）。无 sandbox 逃逸。
- **Symlink**：source `is_symlink()` → return None 跳 copy（与 follow-up 008 / 014 一致）。dst 总是新文件，无 symlink。
- **覆盖语义**：`shutil.copyfile` 默认覆盖目标。但本方案先 sweep clean cast/，再 mkdir + copy；sweep 已删除旧 actor face，新 copy 进入空目录无覆盖冲突；同 actor reassign（idempotent）也 OK — sweep 删自己旧 copy → 重新写。
- **并发**：两条 `POST /api/casting/assign` 同 role race（极小概率）— sweep + copy 不原子；最坏情况 cast/ 内残留两个不同 actor 的 face，casting.md row 反映最后一次 write。**接受 v1** — 与 casting.md row race 严重程度一致（race 期窗口 < 100ms）。
- **磁盘空间**：每 assign 多一份 face jpg copy（typically 50-200 KB）；10 dramas × 10 characters × 1 face ≈ 5-20 MB；可接受。
- **Webapp tree refresh**：Reader / Sidebar 在 `onSaved()` 后 fetch `/api/tree`；新 `cast/` 子目录与内部 jpg 自动出现在 tree（`tree_walker._is_allowed_leaf` 已允许 jpg）。
- **未来扩展**：若加 actor ref video / 抽帧 frames，同 prefix `{actor_id}_*` 在 `cast/` 内扩展；当前 sweep regex 仅匹配 `actor_NNNN_face.*`，不误删未来其它 prefix 的文件。

## 不在本 follow-up 范围

- 不 backfill 现有 assignments — 行为契约变化只对未来 assign 生效；用户要应用到现存 assignments 手动 unassign-then-reassign 即可。
- 不复制 actor sidecar `.md` —用户选 just jpg。
- 不复制整个 actor folder — 同上。
- 不引入硬链接 / symlink（Windows 不可靠）。
- 不动 actor pool 数据结构 / 路由 / 前端 UI。
- 不写自动化 backfill 工具 / data-op script。
- 不写 pytest（统一推迟）。
- 不动 `_deleted/` / archive/ 逻辑。
- 不让 sidebar 隐藏 `cast/`（user 应能 inspect 复制了什么）。
