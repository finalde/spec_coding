# Follow-up draft 012 — 2026-05-11

修复 stale-backend 导致 dev workflow 偶发 `405 Method Not Allowed` 的根因。让 `make run-backend` 默认开 uvicorn `--reload`，新加 endpoint 不再要求用户手动重启 Python 进程。

## 用户报告

> when I click the button on ai_video_management, I got error: 导入失败: Method Not Allowed

用户点 drama-row 的 "📥 导入 + 重命名" 按钮（per follow-up 009），前端 `POST /api/import-from-downloads`，UI toast 显示 `导入失败: Method Not Allowed`。该 toast 串内容由 `frontend/src/api.ts → readJson` 的 ApiError detail.kind 渲染；当 detail 是字符串（FastAPI 默认 405 体 `{"detail": "Method Not Allowed"}`）时，detail.kind 直接吃了那串 string，所以 toast 串带空格、Title Case。

## 根因诊断（先复现确认）

1. **代码层**：`backend/libs/api.py` 已注册 `@app.post("/api/import-from-downloads")`（follow-up 009 落地），fastapi TestClient 直接打该路由 → **200**；catch-all `methods=["GET","PUT","PATCH","DELETE"]` 注册正确 → `GET` → **405**（带结构化 `{detail:{kind:"method_not_allowed"}}`）。
2. **路由表层**：进程内 `app.routes` 列出 `/api/import-from-downloads {'POST'}` + `/api/import-from-downloads {'PATCH','DELETE','PUT','GET'}` 两条，**POST 槽 100% 占住**。
3. **唯一能解释「带空格 / Title Case 405 体」**：用户浏览器击中的 backend Python 进程 **是 follow-up 009 之前启动的旧进程**，里面只有 catch-all 的更早形态 / 或干脆没有 import-from-downloads 路由 — fastapi 在那个版本只 register 了 `/api/rename-media` POST，POST 到 `/api/import-from-downloads` 撞 fastapi 内置 405 fallback（`{"detail":"Method Not Allowed"}` — 注意不是我们自己 catch-all 的结构化体）。
4. **根因**：`backend/main.py` 直接 `uvicorn.run(app, host=..., port=...)`，**不开 `--reload`**。Makefile `run-backend` 跟着不开。每次 follow-up 加新 endpoint，老用户必须自己手动 Ctrl+C → 重启进程，否则 backend 是旧版。

## 修复方案

**最小代码改动 + 默认安全。**

1. **`backend/main.py`** 加一个 `--reload`/`--no-reload` flag，default `--reload=True`（dev workflow 占主导，prod 由 `make run-prod` build-static 后单独走，不在乎 reload）。当 `reload=True` 时，传 `"libs.api:_create_default_app"` 这种 import-string 形式给 `uvicorn.run`（reload 模式必须 import-string，不能传 app 实例 — uvicorn 的硬约束）。
2. **新加一个 `_create_default_app` factory function** 在 `libs/api.py`（或单独 `libs/asgi_factory.py`）— 闭包封装 `RepoRoot.find()` + `BoundOrigin(HOST, PORT)` + `serve_static=True`，给 `uvicorn` reload-mode 用。`serve_static=True` 默认值 OK：dev 模式下 `backend/static/` 为空（只有 `.gitkeep`），mount 不报错，spa 由 Vite 5174 提供。
3. **`Makefile`** 不动 — `run-backend` 仍是 `python main.py`，新 default `--reload` 自动启用。如果用户想跑无 reload 的 prod-like 模式（e.g. `make run-prod` 之后想 long-run backend），就 `python main.py --no-reload`。
4. **`backend/tests/test_boot_smoke.py`** 加一条 smoke：枚举所有 `app.routes` 的 `(path, method)` pair，断言 `("/api/import-from-downloads", "POST")` 在里面。下次有人意外把 endpoint 注释掉/typo 路径，boot-smoke 立刻红。同时把现有四个 POST endpoint (`rename-media` / `archive-media` / `unarchive-media` / `import-from-downloads`) 都列入断言。

不动：
- `frontend/src/api.ts` `readJson` 解析路径不变 — Title Case `Method Not Allowed` 是 fastapi 体本身的格式，前端不需要 normalize；解决 stale-backend 后这种 string 体不会再出现，只会出现自定义的结构化 `{detail:{kind:"method_not_allowed"}}`，toast 串变 `导入失败: method_not_allowed`（lowercase snake_case）— 这是设计内的标识。
- `OriginHostMiddleware` `GUARDED_ROUTES` — 与本 bug 无关；不在本 follow-up 范围扩。后续如果想把所有 POST endpoint 加 Origin/Host gate（目前只 PUT /api/file 有），另起 follow-up。

## 如何向用户解释 / immediate workaround

restart backend process — `Ctrl+C` 当前 `make run-backend` → `make run-backend` 重启 → 浏览器重试按钮即 OK。本 follow-up 落地后 dev workflow 不再需要这一步。

## 影响清单

- `projects/ai_video_management/backend/main.py` — 加 `--reload`/`--no-reload` flag + reload 分支用 import-string
- `projects/ai_video_management/backend/libs/api.py`（或新加 `libs/asgi_factory.py`） — 加 `_create_default_app` factory
- `projects/ai_video_management/backend/tests/test_boot_smoke.py` — 加 POST endpoint 注册矩阵 smoke
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bump
- `specs/development/ai_video_management/changelog.md` — append follow-up 012 条目

不受影响：
- `Makefile`（默认行为已正确）
- 任何前端 / `agent_refs/` / 其它项目
