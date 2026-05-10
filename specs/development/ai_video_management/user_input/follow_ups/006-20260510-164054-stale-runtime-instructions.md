# Follow-up draft 006 — 2026-05-10

Summary: 用户反馈 follow-up 005 之后 mp4 文件仍不在 webapp 左侧 nav 显示（user 已 drop 3 个 mp4 + 1 个 md 到 `ai_videos/mozun_chongsheng/characters/c3_苏璃月/`）。**根因诊断**：backend 代码已正确改写 (Python 测试 walker 已 emit `type: "video"` 节点)，但**用户运行中的 webapp 进程没有 reload 新代码**。本 follow-up: (A) 确认 backend 代码无 bug；(B) 写明 reload 步骤；(C) 加 backend `--reload` 选项 (optional) 让未来 backend 改动自动 hot-reload。

## 用户原话

> I still dont see any mp4 files on the left menu although I already put the files under the folders like C:\workspace\spec_coding\ai_videos\mozun_chongsheng\characters\c3_苏璃月

## 诊断

### 文件确实存在

```
C:\workspace\spec_coding\ai_videos\mozun_chongsheng\characters\c3_苏璃月\
├── c3_苏璃月.md       (10 492 bytes)
├── c3_苏璃月1.mp4     (11 923 233 bytes)
├── c3_苏璃月2.mp4     (11 993 845 bytes)
└── c3_苏璃月3.mp4     (21 643 452 bytes)
```

### Backend 代码已正确

通过 Python REPL 直接调用 `TreeWalker.build()` 后:
- `TREE_VISIBLE_EXTENSIONS` 包含 `.mp4` ✅
- `MEDIA_EXTENSIONS` 包含 `.mp4` ✅
- walker 输出树含 `type: "video"` 节点 ✅
- `exposed.is_inside('ai_videos/mozun_chongsheng/characters/c3_苏璃月/c3_苏璃月1.mp4')` returns `True` ✅

### 真正的问题: 进程未 reload 新代码

用户运行中的 webapp:
- `cd backend && PYTHONPATH=. python main.py` — 直接 spawn FastAPI/uvicorn 进程，**没有 auto-reload**。修改 `exposed_tree.py` / `tree_walker.py` / `api.py` 后必须 **手动重启** backend 进程。
- 前端 — 如果用 `make run-frontend` (vite dev) 运行，TypeScript 文件改动会 hot-reload；如果用 `backend/static/` 静态构建产物运行，须 rebuild (`npm run build`)。

`backend/static/` 当前是空 dir (仅 `.gitkeep`)，frontend/`dist/` 不存在 → 用户应当走 vite dev server 路径 → frontend 应已自动 reload。但 backend 必须重启。

## 修复 (代码层面 zero changes — backend 代码本身已正确)

### (A) 用户操作 (立即生效)

1. **重启 backend**:
   ```bash
   # 找到当前在跑的 main.py 进程并 kill
   #   Ctrl+C 在它的 terminal
   # OR
   #   任务管理器 → 结束 python.exe (port 8766)
   
   # 再启动:
   cd projects/ai_video_management
   make run-backend
   # OR 直接:
   cd projects/ai_video_management/backend && PYTHONPATH=. python main.py
   ```

2. **如果用 vite dev**: 通常已自动 hot-reload；如未生效，浏览器 `Ctrl+F5` 硬刷新清缓存。

3. **如果用 production build**: rebuild frontend
   ```bash
   cd projects/ai_video_management/frontend
   npm run build
   # build 后产物输出到 frontend/dist/，backend 启动时若有 `static/` dir 会 mount。需把 dist/ 内容 copy 到 backend/static/ (Makefile run-prod 自动做这一步).
   ```

4. **打开 webapp** → 选中 `ai_videos/mozun_chongsheng/characters/c3_苏璃月/` folder → 应看到 4 个 children:
   - `c3_苏璃月.md` (📄)
   - `c3_苏璃月1.mp4` (🎬)
   - `c3_苏璃月2.mp4` (🎬)
   - `c3_苏璃月3.mp4` (🎬)

### (B) 让未来 backend 改动自动 hot-reload (可选 quality-of-life)

`projects/ai_video_management/backend/main.py` 加 `--reload` arg 让 user 可启用 uvicorn auto-reload (dev 模式)：

```python
parser.add_argument("--reload", action="store_true", help="enable uvicorn auto-reload (dev mode)")
...
uvicorn.run(app, host=HOST, port=PORT, reload=args.reload, ...)
```

Trade-off: `reload=True` 时 uvicorn 不能直接接收 `app` instance，须传 import string `"main:app"`. 可保留两条 path：no-reload (production-style，传 instance) vs reload (dev-style，传 string). 本 follow-up 仅记录设计；具体实现 deferred 给独立 surgical follow-up。

### (C) 让 frontend `dist/` build 也 visible 给后端

当前 `make run-prod` 会 build frontend 并启 backend，但 `build-frontend` 输出到 `frontend/dist/` 而 backend 期待 `backend/static/`. Makefile 没有 copy step → 用户即使 build 了 frontend 也看不到产物。**也是已知 gap，independent surgical follow-up 处理**。

## 期望行为 (post-restart)

1. webapp 左侧 nav 在 `ai_videos/mozun_chongsheng/characters/c3_苏璃月/` 下展示 1 md + 3 mp4 = 4 children。
2. 点击任一 mp4 → 右侧 Reader 内嵌 HTML5 `<video controls>` 播放，支持 拖动 seek (HTTP range support 由 FastAPI FileResponse 提供)。
3. 点击 `c3_苏璃月.md` → Reader 渲染 markdown + 下方 `📁 Folder media · 同 folder 媒体` gallery 显示 3 个 video figure cards (含 inline `<video controls>`).

## Out of scope

- 不改 backend 代码 (验证已正确)。
- 不实现 backend `--reload` 选项 (deferred surgical follow-up)。
- 不实现 Makefile `run-prod` copy dist→static step (deferred surgical follow-up)。
- 不改 frontend 代码 (follow-up 005 frontend code 未触动用户运行进程；hot-reload 应自动接管)。
