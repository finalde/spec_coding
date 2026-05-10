# Follow-up draft 004 — 2026-05-09

Summary: 用户希望 ai_video_management 能识别中文命名的 artifact 文件。背景: `mozun_chongsheng` 项目 follow-up 002 把所有 character / ref_image 文件名改为中文（`沧冥-魔尊本相.md` 等）。本 follow-up 验证 ai_video_management webapp 已支持 UTF-8 中文文件名，无需代码改动；只在 spec / agent_refs 中明确 documenting that 中文文件名也是合法 path 选项。

## 用户原话（部分，与 mozun_chongsheng follow-up 002 同源）

> 还有再ai_video_management里面，产生的artfacts可以以中文名命名，我好知道哪个文件对应的是哪个人物

## 当前实现实状

webapp 的 EXPOSED_TREE 沙箱通过 `backend/libs/exposed_tree.py::is_inside`：

```python
def is_inside(self, rel: str) -> bool:
    if not rel or rel.startswith("/") or "\\" in rel or "\x00" in rel:
        return False
    candidate = (self._root / rel).resolve(strict=False)
    ...
    if first in _ALLOWED_TOP_LEVEL:  # {"ai_videos", "research"}
        for seg in parts:
            if seg in _EXCLUDED_DIRS:
                return False
        return True
    return False
```

只拦截 backslash / NUL byte / leading slash / 已知 excluded dirs。**Unicode（含中文）路径 segment 不被拦截** — 通过 `pathlib.Path` resolve 后是合法的 UTF-8 字符串。

前端 `Sidebar.tsx` 通过 `tree.children` 递归 render，对 `node.name` 用 `<span className="tree-label">{item.node.name}</span>` 直接 React 渲染 — 中文 字符串自然展示。

`/api/file?path=...` GET endpoint 接 `Query(...)` 参数 — FastAPI 自动 URL-decode，Python 在 ASGI 层处理 percent-encoded UTF-8 → str，无问题。

`PUT /api/file` 同理。

**结论：webapp 已经支持中文文件名，无需代码改动。**

## 文档侧改动

### agent_refs/project/ai_video.md 规则 1 amend

旧规则:
> Folder and file names inside `ai_videos/{name}/` are **English or pinyin**.
> File **contents** are **Chinese**.

新规则 (允许中文文件名作为 OPT-IN，pinyin/English 仍为 default):
> Folder and file names inside `ai_videos/{name}/` 默认为 **English or pinyin**（更易跨平台 / git diff 友好）。
> 项目可在 `specs/ai_video/{name}/final_specs/spec.md` 显式 opt-in 中文文件名（with a divergence note），用于角色 / 场景文件需要直观可识别的场合。
> File **contents** are **Chinese** (unchanged).
> task_name 仍**必须**为 pinyin or English（用于 task_id 构造与跨平台 path stability）。

### ai_video_management spec 添加 acknowledgement

`specs/development/ai_video_management/final_specs/spec.md` 在 FR-7 / FR-8 后加一条说明（or as a separate FR）：webapp 沙箱已支持 UTF-8 中文文件名（不需 widening 任何 allow-list）；前端 sidebar 使用 React 直接渲染 `node.name` 自然支持中文。

## Out of scope

- 不改 EXPOSED_TREE / is_inside / safe_resolve 代码 (already supports UTF-8)
- 不改 frontend Sidebar / Reader components (already render Chinese node names)
- 不改 路径合规 / 安全测试 (Origin/Host gate / path traversal hardening 与字符集无关)
- 不改 task_name 必须 pinyin/English 的硬规则（task_id 构造与跨平台 stability）
