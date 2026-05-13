# Follow-up draft 017 — 2026-05-12

修 follow-up 014 引入的 batch generate UX 问题：用户报告点 "🎭 生成演员" 选 count=20，磁盘只出现 1 张图片，且不知道剩下 19 张的状态（仍在生成？失败？已结束？）。

## 用户原话

> I clicked the genreate button to generate 20 actors, right now only 1 picture gets genreated, I am not sure the progress of the rest 19, could you introduce some way for me to see the generation job's progress whether it is still running or failed or what happend.

附带管家请求：

> Btw, the current instructure [instruction] and previous one please make sure they are tracked as follow up prompts.

（先前 prompt 已登记为 follow-up 016；本 prompt 登记为本 draft 017。）

## 根因

follow-up 014 的 `POST /api/actors/generate` 是 **同步 + 串行** 实现：

```python
for i in range(count):
    image_bytes = self._fetcher(url, DEFAULT_TIMEOUT_SECONDS=30.0, MAX_RESPONSE_BYTES=5MB)
    ...
```

pollinations.ai 每次响应 5–30 秒不等。`count=20` worst case = 20 × 30s = **10 分钟** 阻塞 HTTP 请求。

后果：
1. 浏览器 fetch 默认 timeout 通常 ~5 分钟（实现差异大）→ 浏览器中途断开 → 前端 catch ApiError 显示 "生成失败" toast；但后端 **仍在继续 loop**，第 2..N 张图最终会写盘。
2. 用户刷新 sidebar 看到只 1 张图，**无任何 in-flight 状态指示**，无法分辨是后端还在跑、是 pollinations.ai 限速、还是 backend 已完成但失败。
3. 失败的具体原因（per-image timeout / response_too_large / mkdir_failed）藏在 backend `errors[]` 数组里，但因浏览器断开，前端永远拿不到这个数组。

## 修复策略：搬移循环到前端

最小侵入修复 —— 不动 backend，只把循环从 `generate_batch(attrs, count)` **搬到前端**：

- 前端 `ActorPoolGenerator` 把 `count=N` 拆成 N 次 `count=1` 串行调用；
- 每次响应在秒级返回（单张 ~5-30s）→ 浏览器不会 timeout；
- 每次响应后立即更新 UI 进度（`已生成 X / 总 N`），把累积 errors 显示在 modal 内；
- 每次成功后调 `onGenerated()` 触发 sidebar refresh → 新 actor 即时出现；
- 用户随时关闭 modal：当前 in-flight 请求继续完成，但后续迭代不再发起（cancellation via React ref，避免 React state-update-after-unmount 警告）。

**Why frontend loop and not backend SSE / job tracking**：

| 方案 | 代码量 | 取舍 |
|---|---|---|
| 前端 loop count=1 (本 follow-up) | 改 1 个组件 ~30 行 | 浏览器关闭 / refresh = 中断；网络抖动每张独立处理 |
| 后端 SSE streaming | 新 endpoint + 流式响应中间件 + 前端 EventSource | 浏览器关闭不中断 backend，但 SSE 调试 / 测试成本高 |
| 后端 job tracker | 状态 dict + job_id + poll endpoint + 后台 task | 完整但与现有"无 backend 状态"原则冲突 |

前端 loop 已能满足"可见进度 + 单张失败可分辨"的核心需求；SSE / job tracker 是 v2 升级路径。

## 行为契约

修复后：
- 单击 "生成" → modal 显示 progress bar `[████░░░░░░] 4 / 20 (20%)`；按钮文案 `生成中… (4 / 20)`；
- 每张完成后 sidebar 出现新 actor folder（自然刷新）；
- 每张失败的具体 reason 累加到 modal 内 errors 列表（不阻断后续迭代）；
- 全部完成 → toast `已生成 N / 失败 E`；errors 列表保持可见，便于用户拍照 / debug；
- 关闭 modal：当前 inflight 请求完成（无法 abort 中途），但 loop 停止。

## 后端改动：零

`actor_pool.py:generate_batch` 保持原 count 参数支持（与现有 endpoint 契约 / pytest scenarios / 测试 stub 一致）；仅前端调用方式从 `count=N` 改为 `N × count=1`。

## 不在本 follow-up 范围

- 不引入 backend job tracker / SSE（如未来需要可独立 follow-up）
- 不引入 retry-failed-only 按钮（v1 失败后用户重新点 "生成" 即可，跳过已生成的 ID 范围）
- 不引入并行 N 张同时跑（pollinations.ai 限速未知；保守 serial）
- 不写 pytest / e2e（与 005-016 一致推迟）
- 不动 backend / `POST /api/actors/generate` 错误码契约
