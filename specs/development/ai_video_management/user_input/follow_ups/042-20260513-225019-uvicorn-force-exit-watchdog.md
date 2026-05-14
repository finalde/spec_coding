# Follow-up draft 042 — 2026-05-13

Summary: 修 follow-up 037 没修干净的 dev-reload 卡死。`timeout_graceful_shutdown=2` 让 uvicorn 在 2s 后 cancel 正在运行的 asyncio task，但 FastAPI 所有 sync `def` endpoint 都在 anyio threadpool 里跑（25+ 路由全 sync），cancel asyncio wrapper 不会 kill 底层线程；Kling 30–120s / `/api/media` range stream / pollinations / frame_extractor 等线程继续占住进程，Python 解释器在最外层 `sys.exit` 时等非-daemon 线程导致 `Waiting for connections to close. (CTRL+C to force quit)` 卡死。修法：注入 force-exit watchdog — patch `uvicorn.Server.handle_exit` 在 signal handler 跑完后启动一个 daemon `threading.Timer`，N 秒后调 `os._exit(0)` 硬退。uvicorn 自己的 graceful 路径仍优先跑，watchdog 仅作为兜底确保进程在 (timeout_graceful_shutdown + 余量) 内死掉。

## 用户原话

> I got some error again, the appliation just stucked: 2Fframes%2Fframes5.png HTTP/1.1" 200 OK
> WARNING:  WatchFiles detected changes in 'libs\tree_walker.py'. Reloading...
>  INFO:     Shutting down
> INFO:     Waiting for connections to close. (CTRL+C to force quit)

## 根因分析

1. **uvicorn 0.34（已安装）正确解析 `timeout_graceful_shutdown=2`** — `Server.shutdown()` 在 `_wait_tasks_to_complete()` 外裹了 `asyncio.wait_for(..., timeout=2)`，2s 后 `TimeoutError` cancel 所有 in-flight task。
2. **cancel asyncio task ≠ kill 底层 OS 线程** — FastAPI 把每个 sync `def get_/post_` endpoint 通过 `anyio.to_thread.run_sync` 派到 threadpool。cancel wrapper coroutine 只是 raise `CancelledError` 给 awaiter，**线程本身继续跑**直到 sync 函数自然返回。
3. **本项目所有 endpoint 都是 sync** — `actors_generate` 内调 Kling JWT POST + 30–120s polling；`get_media` 是 `FileResponse` 同步流；`extract_frames` 是阻塞 ffmpeg 子进程；`import_from_downloads` 同步 `shutil.move`；等等。任一在飞 → 1 个 threadpool 线程占住。
4. **Python `sys.exit()` 等非-daemon 线程** — uvicorn `Server.run()` 返回后回到 `main.py`，Python 标准退出路径需要 join 所有非-daemon 线程。anyio threadpool 工人默认是非-daemon → 卡住。
5. **`force_exit=True` 不杀线程** — `force_exit` 只跳过 graceful drain 但不调 `os._exit`，因此同卡。

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| 修复手段 | **monkey-patch `uvicorn.Server.handle_exit` 添加 watchdog timer** | 不改 uvicorn 内部、不动 endpoint signature、零 endpoint 重写、可在两条启动路径（reload 子进程 + `--no-reload` 直接路径）共享 |
| Watchdog 超时 | `timeout_graceful_shutdown + 2` = **4s** (常量 `FORCE_EXIT_GRACE = 2.0`) | 给 uvicorn 自己的 2s graceful 一个完整窗口 + 2s 给 lifespan shutdown + atexit hooks 跑完；> 4s 仍卡的话 watchdog 兜底 |
| Watchdog 终止方式 | `os._exit(0)` | 跳过 atexit / __del__ / 线程 join；OS 层 immediate exit；与 SIGKILL 等价但在 Python 内可控触发 |
| 触发点 | uvicorn 的 `handle_exit(sig, frame)` 已被 patch | 该方法是 uvicorn 唯一的信号入口（SIGTERM / SIGINT / SIGBREAK）；patch 后 watchdog timer 与 uvicorn 自己的 `should_exit=True` 设置在同一 callstack |
| 多次信号 | watchdog timer 只 schedule 一次 + daemon=True | 多次 SIGINT（用户按 CTRL+C）不重复 schedule；进程退出 timer 自动跟着死 |
| 安装位置 | 新建 `libs/uvicorn_force_exit.py::install()`，`main.py` + `libs/asgi.py` 顶部各调一次 | reload 模式下子进程通过 `uvicorn.run("libs.asgi:app", reload=True)` 启动，子进程 import `libs.asgi` 时 patch 生效；`--no-reload` 模式 `main.py` 直接 `uvicorn.run(app, ...)`，`main.py` import 时 patch 生效 |
| 跨平台 | Windows/Linux/macOS 同代码 | `os._exit` POSIX + Windows 都支持；`threading.Timer` 跨平台；signal patching 不依赖具体 signum |
| 不修 endpoint 为 async | 是 | 25+ endpoint 全改 async 是 100 行级重构 + 引入 httpx async client 等，远超本 follow-up 范围；watchdog 是 minimal-blast-radius 兜底 |
| 不动 `timeout_graceful_shutdown=2` | 是 | 037 决策保持有效；watchdog 是 037 之后的二级保险 |
| 不引入新依赖 | 是 | 纯 stdlib `os` / `signal` / `threading` |

## 功能要求

### Backend

**`projects/ai_video_management/backend/libs/uvicorn_force_exit.py`** (新)：
- 常量 `FORCE_EXIT_GRACE = 2.0`。
- `install() -> None`：
  - 检测 `uvicorn.Server` 是否已被 patch（看 attribute `_force_exit_installed`），是 → 直接 return（幂等）。
  - 包装 `uvicorn.Server.handle_exit`：先调原方法，再启动 daemon `threading.Timer(timeout_graceful_shutdown + FORCE_EXIT_GRACE, lambda: os._exit(0))` 并 `.start()`。
  - 从 `self.config.timeout_graceful_shutdown` 取窗口；若 `None`（极端 misconfigure）落回 `FORCE_EXIT_GRACE` 单独值。
  - 设 `uvicorn.Server._force_exit_installed = True`。

**`projects/ai_video_management/backend/main.py`**：
- 顶部 import `from libs.uvicorn_force_exit import install as _install_force_exit`；在 `main()` 内 `args = parser.parse_args()` 之后、`uvicorn.run` 之前调 `_install_force_exit()`。两条分支共享。

**`projects/ai_video_management/backend/libs/asgi.py`**：
- 顶部（在 `load_env_file` 之后、`create_app` 之前的 import 块内）`from libs.uvicorn_force_exit import install as _install_force_exit; _install_force_exit()`。Reload 模式子进程 import 该模块时 patch 生效。

### Spec / validation

- `final_specs/spec.md` **FR-2** 行：原本 follow-up 037 写了 `uvicorn.run(...)` 调用包含 `timeout_graceful_shutdown=2`。追加 follow-up 042 amendment：`main.py` 与 `libs/asgi.py` 在 uvicorn 启动前调 `libs.uvicorn_force_exit.install()`；该函数 monkey-patch `uvicorn.Server.handle_exit` 加 daemon `threading.Timer((timeout_graceful_shutdown or 0) + 2s, lambda: os._exit(0))`，作为 sync threadpool 阻塞导致 Python 退出 hang 的兜底。
- `validation/acceptance_criteria.md` 加一条 manual scenario **U2.5**：dev reload 强制退出兜底（manual：在 `/api/extract-frames` 在飞时改 `libs/tree_walker.py`，期望 ≤ 4s 内子进程 PID 消失 + WatchFiles 启动新 PID）。`[manual]` 标记 — 此场景需要 OS 进程观察 + 时间断言，自动化 cost 高，v1 接受 manual checkbox。
- `validation/acceptance_criteria.md` 覆盖矩阵 FR-2 行附加 `, U2.5`。

### User input

- `user_input/revised_prompt.md`：header 加 Prior follow-up 042 段；不动 040/041 narrative。
- `user_input/follow_ups/042-20260513-225019-uvicorn-force-exit-watchdog.md` (本文件)。

## 安全 / 边界

- **`os._exit(0)` 跳过所有 atexit / finally / __del__ / 线程 join**。后果：写入中的文件可能残缺（Path.rename 是 atomic 但 multi-write sequence 不是）。本项目所有写都是单 syscall 级（atomic rename / 单 `unlink` / 单 `mkdir`），无 multi-step 文件操作横跨 watchdog 触发窗口的风险。Kling generation 写的是 actor folder 内 `actor_NNNN.md` + jpg — 两个独立 atomic write；若一个写完另一个没写，下次 `_reap_incomplete_folders()` 会扫掉（follow-up 027）。
- **`os._exit` 不通过 lifespan shutdown** → 但本项目 FastAPI 没注册 `@app.on_event("shutdown")` handler；`ActorPool.__init__` 的 `migrate_filenames()` 是启动时一次性，无 shutdown 对应；DownloadsImporter / FrameExtractor / Casting 都 stateless。所以跳 lifespan 无副作用。
- **Patch 幂等** — `_force_exit_installed` flag 防多次 wrap。
- **不影响生产** — 即使 `--no-reload` 部署模式（user 手工 SIGTERM），watchdog 触发逻辑相同：先给 graceful 2s + 2s 兜底 = 4s 内进程一定死。`os._exit` 不会丢未 flush 的请求 body，因为 graceful 阶段已经在 2s 内 cancel 完所有 task。
- **Signal handler 仍由 uvicorn 持有** — patch 是 wrapper（先调原方法），uvicorn 该走的 `should_exit=True` / `force_exit=True` 流程不变；watchdog 是平行轨道。
- **Daemon timer** — 不阻塞进程退出；若 Python 在 watchdog 触发前自然退出，timer 跟着死。
- **不破 `uvicorn` 升级** — 只依赖 `Server.handle_exit(sig, frame)` 签名 + `Server.config.timeout_graceful_shutdown` 属性，两个 API 至少从 uvicorn 0.20 起稳定到 0.34。
- **不破 pytest** — 测试不 import `main.py` / `asgi.py` 顶层；`uvicorn_force_exit.install()` 不被自动调；测试套件继续正常退出。

## 不在本 follow-up 范围

- 不把 25+ 个 sync `def` endpoint 改成 `async def` + httpx async client（巨大重构）。
- 不把 anyio threadpool 工人改成 daemon（这会让 Kling generation 在 reload 触发时丢中间结果 → 比 hang 还差）。
- 不引入 `psutil` 或其他外部进程管理。
- 不引入新 endpoint。
- 不修 frontend 任何东西。
- 不动 `requirements.txt`（uvicorn[standard]>=0.29 已涵盖）。
- 不写 pytest（manual U2.5 是 v1 接受方案）。
- 不动 audit log / events.jsonl（webapp 非 agent_team 状态机）。
- 不动 040/041 已落地的修改。
