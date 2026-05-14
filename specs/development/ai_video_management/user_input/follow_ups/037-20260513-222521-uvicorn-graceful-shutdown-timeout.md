# Follow-up draft 037 — 2026-05-13

Summary: dev backend (`make run-backend` / `python main.py`，默认 `--reload`）在 user 编辑 `libs/` 下任意 .py 文件触发 reload 时偶发"卡死"——uvicorn 打印 `Shutting down` + `Waiting for connections to close. (CTRL+C to force quit)` 后无限阻塞，user 不得不手动 Ctrl+C。根因是 uvicorn `graceful_shutdown` 默认 wait forever，而本项目的同步 endpoint（face generation 30s–2min / frame extraction 1–3s / import-from-downloads 文件移动）会持续占用线程；reload 期间任一未完成请求都把 shutdown 卡住。

修复：`backend/main.py` 给两个 `uvicorn.run` 调用加 `timeout_graceful_shutdown=2`（秒），让 reload / SIGINT 在 2 秒后强制 close 所有连接，dev 循环不再 hang。

## 用户原话

> for ai_video_management, once a while I will encouter errors and the system just stuck: WARNING:  WatchFiles detected changes in 'libs\frame_extractor.py'. Reloading...
>  INFO:     Shutting down
> INFO:     Waiting for connections to close. (CTRL+C to force quit)

## 根因诊断

1. **触发路径**：WatchFiles 检测到 `libs/frame_extractor.py` 变更 → uvicorn reload 进程发 SIGTERM 给老 worker → 老 worker 进入 graceful shutdown → 等所有 active connections close。
2. **uvicorn 默认行为**：`timeout_graceful_shutdown=None`（永久等待）— 这是 uvicorn 设计上对 prod-correctness 的偏好，但 dev workflow 完全相反。
3. **本项目的同步阻塞**：`backend/libs/api.py` 内 ~25 个 endpoint 全部 `def`（非 `async def`），每个请求占一个 ThreadPoolExecutor 线程；长时调用包括：
   - `POST /api/actors/generate`：Kling JWT → 提交任务 → 轮询直到出图（典型 30–120s）。
   - `POST /api/extract-frames`：ffmpeg subprocess 抽 5 帧（典型 1–3s，但黑屏 / 高码率素材偶尔 5s+）。
   - `POST /api/import-from-downloads`：大 mp4 跨盘 move（HDD 慢盘 5–20s）。
   - `POST /api/archive-media` / `POST /api/delete-media`：磁盘 IO，秒级但不绝对零。
4. **dev 表象**：user 在 generate / extract 期间改了 Python 文件 → reload 立刻发起 → 当前请求还没完 → graceful shutdown wait forever → terminal 卡 `Waiting for connections to close` 行。CTRL+C 后 user 还得 Ctrl+C 第二次才能彻底退出（uvicorn force-quit 路径）。

## 修复方案

**最小代码改动 + dev/prod 同改。** uvicorn `timeout_graceful_shutdown` 参数 since 0.29（本项目 `uvicorn[standard]>=0.29` 已满足）。两条 `uvicorn.run(...)` 调用各加 `timeout_graceful_shutdown=2`：

- `--no-reload` 分支 (`uvicorn.run(app, host=..., port=..., log_level="info")`)：用户 Ctrl+C 期望立即停；2s 等已足够冲刷正常 response，过期连接强 close。
- 默认 reload 分支 (`uvicorn.run("libs.asgi:app", host=..., port=..., log_level="info", reload=True, reload_dirs=["libs"])`)：reload 期间 2s 等是稳定的"重启窗口"，长任务（如正在轮询的 Kling 出图）会被 force-cancel，user 再发一次即可。

**为什么 2s 而非 0 / 0.5 / 5：**
- `0` / 极短：正常的 200 response 可能被截断（client 收不到完整 body）。
- `0.5–1s`：HDD move 类 IO 经常 ~1s，偶发被截。
- `5s+`：reload 体感慢，dev 反馈循环退化。
- `2s`：能完成绝大多数"快路径" response（tree/file/media/casting）的 flush，又把 Kling 出图 / 大文件 import 这种"慢路径"果断截掉——dev 时本来就准备重发的请求。

**不动其它：**
- 不把 endpoint 改成 `async def`。改异步要把内部所有 IO 包成 thread runner 或换 aiofiles / httpx async client，工作量数倍于本问题，且与项目当前 sync-first 设计冲突。
- 不动 reload_dirs / WatchFiles 行为。文件变更检测是对的，问题在 shutdown 阶段不该 wait forever。
- 不加 prod 部署文档警告。`--no-reload` 一样吃 2s timeout，prod 真要 hot deploy 用 nginx / systemd 滚动重启，不靠这 2s。
- 不加 frontend 提示 / toast。这是 dev workflow 内事故，user 看到的是 terminal 输出，前端无感知。

## 影响范围

- `projects/ai_video_management/backend/main.py` — 两条 `uvicorn.run(...)` 各加一个 kwarg `timeout_graceful_shutdown=2`。其余 argparse / load_env / import-string 不动。
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header 升级 + 文件列表追加 036。
- `specs/development/ai_video_management/final_specs/spec.md` — FR-2 docstring 同步（uvicorn.run 调用 shape 描述增加 `timeout_graceful_shutdown=2`）。
- `specs/development/ai_video_management/changelog.md` — append follow-up 036 条目。

## 不影响

- 任何 frontend 文件 / lib / endpoint 业务逻辑。
- 现有 `--reload` 默认行为（follow-up 012 确立）。
- Test suite — 不依赖 uvicorn boot；TestClient 直接挂 app。
- 其它项目（spec_driven 等）不动。
- agent_refs / playbook / harness — 这是本项目特定 dev 行为，不上升到 common-level rule（其它项目 sync endpoint 占比远低于本项目；本 fix 价值显著但非普适）。
