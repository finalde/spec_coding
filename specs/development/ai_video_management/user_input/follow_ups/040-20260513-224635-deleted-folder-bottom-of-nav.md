# Follow-up draft 040 — 2026-05-13

Summary: 左侧 nav 的 "AI Videos" section 内，把 `ai_videos/_deleted/` directory 节点 sort 到列表底部（其它 drama folder 和 `_actors/` 保持现有字母顺序）。回收站是低频访问 + 视觉噪声大的系统目录，应该让位给真正的内容 — drama / `_actors`。

## 用户原话

> in ai_video_management left nav, lets move _deleted to the bottom of the left nav

## 当前行为

`backend/libs/tree_walker.py::_ai_videos_section` 用 `sorted(p for p in ai_videos_root.iterdir() if p.is_dir())` 对 ai_videos 顶层子目录按文件名字母序排序。ASCII 中 `_` (0x5F=95) < lowercase letters (97–122)，所以 `_actors`, `_deleted` 都排在所有 pinyin/英文 drama folder 之前。结果 sidebar 顶部是：

```
📁 _actors/ 🎭
📁 _deleted/ 🧹  ← 噪声
📁 mozun_chongsheng/
📁 ...其它 dramas
```

## 期望行为

```
📁 _actors/ 🎭
📁 mozun_chongsheng/
📁 ...其它 dramas
📁 _deleted/ 🧹  ← 底部
```

`_actors/` 不动（高频使用 — 整个 face pool + 角色分配工作流的入口）。只把 `_deleted/` 拉到末尾。

## 修复方案

**最小、纯 backend、零 frontend 改动。**

`tree_walker.py::_ai_videos_section`：分离出 `_deleted` 节点，按字母序处理其它子目录，循环结束后把 `_deleted` 节点 append 到 children 列表末尾。

```python
def _ai_videos_section(self) -> dict[str, Any]:
    ai_videos_root = self._root / "ai_videos"
    children: list[dict[str, Any]] = []
    deleted_child: dict[str, Any] | None = None
    if ai_videos_root.is_dir():
        for project_dir in sorted(p for p in ai_videos_root.iterdir() if p.is_dir()):
            if project_dir.name in self._exposed.excluded_dirs():
                continue
            project_node = self._walk_project(project_dir)
            if project_node is None:
                continue
            if project_dir.name == "_deleted":
                deleted_child = project_node
            else:
                children.append(project_node)
    if deleted_child is not None:
        children.append(deleted_child)
    return {"type": "section", "name": "AI Videos", "path": "", "children": children}
```

**为什么 backend 而非 frontend：** `tree_walker` 已经是排序权威；Sidebar.tsx 直接消费后端给的 children 顺序。在前端再做 reorder 是双重权威，违反单一权威原则。

**为什么硬编码 name 等于 `"_deleted"` 而非泛化 "所有 `_` 前缀都到末尾"：** `_actors/` 是高频入口（按当前 UX 应靠前）；未来若再加 `_orphans/` / `_archive/` 之类系统目录，规则可能继续分化（哪些靠前哪些靠后）。先实现用户实际要求的"`_deleted` 到底部"，不预设抽象。

**为什么 `_deleted` 不参与字母序对比：** 简化逻辑 — 无论项目里有多少 drama 文件夹，`_deleted` 永远是最后一项，零歧义。

## 影响范围

- `projects/ai_video_management/backend/libs/tree_walker.py` — `_ai_videos_section` 改写如上。
- `specs/development/ai_video_management/user_input/revised_prompt.md` — 文件列表追加 040 + header bump。
- `specs/development/ai_video_management/final_specs/spec.md` — FR-tree section 加一行 `_deleted` 排序契约（已找到 FR-39 / FR-40 附近的 tree-walking 描述区域）。
- `specs/development/ai_video_management/changelog.md` — append follow-up 040 条目。

## 不影响

- Frontend `Sidebar.tsx` — 直接消费 backend 给的顺序，零改动。
- `_actors/` 顶部位置 — 保持当前 alphabetical 顺序。
- `_deleted/` 内部内容 — 子树排序与渲染完全不变，仅其 parent slot 在 AI Videos section 的位置改动。
- 嵌套于 drama folder 内的任何同名 `_deleted/` 子目录（如果将来有）— `_ai_videos_section` 只对顶层做 hoist，drama 内的子树仍走 `_walk_filtered` 字母序。
- `/api/tree` 响应 shape — 与之前 100% 一致，仅 `ai_videos` section 的 children 数组顺序变化。
- Tests — `backend/tests/` 内无 `_deleted` 顺序断言（grep 已验证）；不新增测试。
- Follow-up 039 的 `apps/+libs/` layout 改造尚未应用到 code，本 follow-up 改的是当前 `backend/libs/tree_walker.py`；当 039 应用时该模块会迁到 `libs/infrastructure/` 或 `libs/application/`，本规则随之搬走，语义不变。
