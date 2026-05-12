# Follow-up draft 015 — 2026-05-12

修 follow-up 014 留下的 chicken-and-egg UX bug: 用户启动 webapp 后看不到 "🎭 生成演员" 按钮，因为它绑在 sidebar 的 `_actors/` 行上，而 `_actors/` 目录只在第一次成功生成后才被 backend 创建。新用户无法首次触发生成 → 无法看到 UI 入口 → 无法用此功能。

## 用户原话

> I dont see it in ai_video_management's UI page

## 根因

follow-up 014 `Sidebar.tsx` 渲染逻辑：

```tsx
const isActorsRoot = isAiVideoChild && dramaPathParts[1] === "_actors";
// ...
{isActorsRoot ? (<button>🎭 生成演员</button>) : null}
```

这个按钮只在 sidebar 树包含 `ai_videos/_actors/` 节点时才渲染。TreeWalker 通过 `iterdir()` 读真实文件系统目录列表；目录不存在 → 不在 sibling 列表 → sidebar 不渲染行 → 按钮永远不出现。

follow-up 014 `actor_pool.py:generate_batch` 第一行 `actors_dir.mkdir(parents=True, exist_ok=True)` 是 lazy 创建 —— 必须先调用 endpoint 才创建文件夹。Endpoint 必须从 sidebar 按钮触发。死循环。

## 修复

后端启动时 eager 创建 `ai_videos/_actors/`，无需等待第一次生成调用：在 `api.py:create_app()` 实例化 ActorPool 之后立即调一次 `actor_pool.actors_dir().mkdir(parents=True, exist_ok=True)`。

- 文件夹永远存在 → sidebar 永远显示 `_actors/` 行 → "🎭 生成演员" 按钮永远可见
- 不引入新文件 / 新依赖 / 新 endpoint
- 文件夹为空时，TreeWalker.`_walk_project` 仍能正常生成 directory 节点（已 verified：`sub = []` 不阻塞 node 创建）
- 对已有 `_actors/` 的安装零影响（`exist_ok=True`）

## 用户 next step

若用户的 backend 进程是 follow-up 014 之前启动的，新代码（5 个 endpoint + 启动时 mkdir）不会生效。follow-up 012 已让 `make run-backend` 默认开 `uvicorn --reload`，新增 / 改动的 `libs/*.py` 文件会自动被检测并 reload。但若用户用 `make run-prod` 跑的（非 reload 模式）则需手动重启。

## 不在本 follow-up 范围

- 不动 actor pool / casting 任何业务逻辑
- 不动 backend libs 文件结构（只在 create_app 内加 1 行 mkdir）
- 不动前端代码
- 不写 backend pytest（与 005-014 一致推迟）
