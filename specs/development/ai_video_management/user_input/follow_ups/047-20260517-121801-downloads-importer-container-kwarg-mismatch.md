# Follow-up draft 047 — 2026-05-17

**Summary:** Backend 500 on `POST /api/import-from-downloads`. **Same kwarg-mismatch bug** that follow-up 046 fixed for `Casting`, but on the `DownloadsImporter` provider — 046 修了 sibling provider 没扫面所有 provider，留下了相同形态的 wiring 不一致。`apps/api/container.py::downloads_importer` 写 `media_renamer=media_renamer`，但 `libs/infrastructure/downloads__importer.py::DownloadsImporter.__init__` 第 3 个形参叫 `renamer` —— DI singleton 在 first inject 时调 `DownloadsImporter(exposed=..., resolver=..., media_renamer=...)` → `TypeError: __init__() got an unexpected keyword argument 'media_renamer'` → FastAPI 默认 handler 返回 `{"detail": "Internal Server Error"}`（无 `detail.kind`） → 前端 `Sidebar.tsx` 落入 `err.detail?.kind ?? err.status` 分支 → toast 显示 `导入失败: 500`。

## Source

> got error when I try to import the downloaded video after click button: 导入失败: 500

## Root-cause diagnosis（与 046 同形态）

| 处 | container.py kwarg | constructor 形参 | 状态 |
|---|---|---|---|
| `casting` | `renamer=media_renamer` | `renamer` | ✅ follow-up 046 修复 |
| `downloads_importer` | `media_renamer=media_renamer` | `renamer` | ❌ 本 follow-up 047 修 |
| `media_renamer / media_archiver / frame_extractor / file_reader / file_writer / tree_reader / actor_pool / exposed_tree / safe_resolver` | `exposed=... / resolver=...` 等与 `__init__` 形参 byte-equal | (匹配) | ✅ 无 bug |

Pattern：039 迁移到 `dependency_injector` 时，container 字段名一般沿用变量名（`media_renamer`），但传给 sub-provider 的 kwarg 必须按目标 `__init__` 的**形参名**写。`Casting.__init__(renamer=...)` 与 `DownloadsImporter.__init__(renamer=...)` 是 sibling — 046 只修了前者；后者一直挂着。

## Fix

**最小、单行、纯 container.py。**

`apps/api/container.py`：

```python
downloads_importer: providers.Singleton[DownloadsImporter] = providers.Singleton(
    DownloadsImporter,
    exposed=exposed_tree,
    resolver=safe_resolver,
    media_renamer=media_renamer,   # ← BUG
)
```

改为：

```python
downloads_importer: providers.Singleton[DownloadsImporter] = providers.Singleton(
    DownloadsImporter,
    exposed=exposed_tree,
    resolver=safe_resolver,
    renamer=media_renamer,         # ← align with DownloadsImporter.__init__(renamer=...)
)
```

零 libs 改动；`DownloadsImporter.__init__` 签名保留 `renamer`（与 follow-up 009 + 041 时的代码字节一致）。Provider 内部变量名 `media_renamer` 不动 — 与 sibling providers 命名风格一致 (`media_renamer` / `media_archiver`)；只调整传给 `DownloadsImporter` 的关键字。

## 防御：扫一次所有 provider 的 kwarg 矩阵

为防 047 同型 bug 再潜伏（每加一个 infra 类就重蹈），本 follow-up 顺手 audit container.py 全部 11 个 provider 与其 `__init__` 签名（见上表）；目前仅 `downloads_importer` 一处。**不引入 lint / test** — 若再有同型 bug，应在 follow-up 042 的 boot-smoke matrix 内补一条「DI container resolve smoke」（先解析所有 provider，捕获 TypeError），但那是独立 follow-up 的工作量。本 follow-up 仅修当前 bug。

## Why now

User 之前使用 import-from-downloads 走的是 pre-039 路径 (`backend/libs/api.py::create_app` 手工 `DownloadsImporter(exposed, resolver, media_renamer)` 位置传参，因此 `media_renamer` 形参名差异不出错)。039 迁移到 DI singleton 用关键字传参后，第一次实际调用就 500 — 用户此刻才点 import 按钮触发。

## Acceptance

- `POST /api/import-from-downloads` body `{path: "ai_videos/{drama}"}` 返回 200 + `{moved, unmatched, errors, rename}`（FR-9e shape 不变）。
- Sidebar drama-row "📥 导入 + 重命名" 按钮：从 toast `导入失败: 500` 恢复到 `已导入 N / 未分类 M / 错误 X，重命名 Y` 正常摘要。
- `frames/` 仍被 rename 排除（follow-up 041 + 047 两层 — 041 行为不变）。
- 其它端点不动。

## 影响范围

- `projects/ai_video_management/apps/api/container.py` — 单行 kwarg 名修正。
- `specs/development/ai_video_management/user_input/revised_prompt.md` — 文件列表追加 047 + header bump。
- `specs/development/ai_video_management/changelog.md` — append follow-up 047 条目。

## 不影响

- `libs/infrastructure/downloads__importer.py` — 零改动；`DownloadsImporter.__init__(renamer=...)` 形参不变。
- 任何 FR / `final_specs/spec.md` — 这是纯 wiring bug，FR-9e endpoint 契约（请求 body / response shape / status codes）从未变化；spec walk 无需更新。
- 其它 `dependency_injector` provider — audit 后矩阵无第二处不一致。
- Frontend — 零改动；`Sidebar.tsx::handleImportFromDownloads` 与 `importFromDownloads` API 函数都不变；fix 后 toast 自然显示正常摘要。
- Tests — `apps/api/tests/test_boot_smoke.py` 已枚举 POST 路由矩阵，且本 follow-up 不动路由；no test 改动。
- Follow-up 046 的 `Casting` fix 仍然有效；本 047 是其在 sibling provider 上的镜像补丁。
