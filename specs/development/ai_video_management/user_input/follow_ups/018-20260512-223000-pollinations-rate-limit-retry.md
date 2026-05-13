# Follow-up draft 018 — 2026-05-12

修 follow-up 014 / 017 batch generate 在用户实测中遇到的 **pollinations.ai 429 rate limit cascade**。用户跑 count=20，第 1 张成功后所有后续请求拿到 429 Too Many Requests，且每个 error 都报 `actor_0003` —— 两个独立 bug 的合流。

## 用户原话

> I asked to generate 20 in a batch, but after generate the first picture, I got error:
> #2: actor_0003: http_failed: The read operation timed out
> #3: actor_0003: http_failed: Client error '429 Too Many Requests' for url '...'
> #4: actor_0003: http_failed: Client error '429 Too Many Requests' ...
> ...

## 两个独立根因

### 根因 A：pollinations.ai 免费 endpoint 有限速

实测响应：连发 2+ 请求即触发 HTTP 429。Research 阶段（follow-up 014）调查的资料没明确说免费 endpoint 限速；现在用户实测 = 有，且很激进。

- 第 1 张成功，第 2 张就 timeout（pollinations.ai 服务过载或排队）
- 第 3-N 张 429
- follow-up 014 `_default_fetcher` 实现：单次 GET，无重试，无 backoff —— 一拿 429 / timeout 立即冒泡到 `generate_batch` 的 `except Exception` 分支，写 errors[]，跳过。

### 根因 B：incomplete folder 占着 ID 不放

每个失败请求都报 `actor_0003`，因为：

1. follow-up 014 `_next_actor_id_num(actors_dir)` 用 `_ACTOR_DIR_RE` regex 数 actor 文件夹算 max+1。
2. follow-up 014 的失败分支调 `_cleanup_empty_folder(actor_folder)`，**但**只删完全空的 folder（`if folder.is_dir() and not any(folder.iterdir()): folder.rmdir()`）。
3. 旧批失败时（用户先前那次 1/20）某个 folder 可能在 jpg 没写盘前 partial 残留 —— 或者 Windows 上偶发 rmdir 失败被 swallow。
4. 残留的 `actor_0002/` 空 folder 被 `_next_actor_id_num` 算进 max → 下一批永远从 `actor_0003` 开始。每次新 iteration mkdir(actor_0003) 成功（folder 被新批每次 cleanup 后又被新批 mkdir），收到 429，cleanup actor_0003 folder。下一 iteration 又是 actor_0003。死循环。

## 三处修复

### 修复 1 — backend retry-with-backoff on 429 / timeout

`actor_pool.py:_default_fetcher` 重写：

- 最多 3 次重试，backoff `[3s, 6s, 12s]` 累计 21s。
- 收到 429：honor `Retry-After` header（capped 60s），缺则用默认 backoff。
- 收到 `httpx.{ReadTimeout, ConnectTimeout, WriteTimeout}`：同 backoff 重试。
- 其他 HTTP 错误码（500/404/...）直接冒泡（不重试，避免浪费 wall-clock）。
- 单张图片总 wall-clock worst case ~81s（30s base × 1 + 3s + 30s × 1 + 6s + 30s × 1 + 12s + 30s × 1）。仍远低于浏览器 fetch 默认超时。

### 修复 2 — `_next_actor_id_num` 跳过 + 清理 incomplete folders

把 `_ACTOR_DIR_RE` 命中但缺 `<id>.jpg` 的 folder 视为 incomplete：

- 不计入 max_num（防 ID skip-ahead）
- 立即 cleanup：删 folder 内任何残留文件 → rmdir
- 失败静默（与现有 `_cleanup_empty_folder` 模式一致；磁盘脏不阻塞批次）

副作用：如果用户**手动**在 `_actors/` 里创建了空 `actor_NNNN/` folder 想"占位"，本 fix 会删掉它。这种 hack 不在 v1 contract 内，不视为破坏行为。

### 修复 3 — frontend 加 inter-iteration throttle

`ActorPoolGenerator.tsx` 在每次 await `generateActors()` 完成后、下一轮开始前 sleep **2 秒**（最后一轮不 sleep）：

- 主动避免 pollinations.ai 限速触发
- UI 显示 `等待 2s 防限速…` 子状态，区别于 `生成中… (i / N)`
- 2s 比 backend 重试 backoff 短 → 默认情况下绕过限速，触发限速才用 backend retry

加 hint 文字到 modal："pollinations.ai 免费 endpoint 有限速 — 默认每张间隔 2 秒；遇到 429 自动重试 3 次（最长等 60s）。"

## 不在本 follow-up 范围

- 不引入 backend job tracker（仍 stateless；retry 在单次 HTTP call 内完成，不跨 endpoint 调用持久化）
- 不并行 N 张（避免触发限速）
- 不引入 user-configurable retry / backoff 参数（v1 hardcoded）
- 不改 `MAX_BATCH_COUNT=20`（用户可继续要 20；只是更慢、有 throttle）
- 不写 backend pytest / e2e（与 005-017 一致推迟；retry path 在 fake fetcher 下不触发，需独立测试 fixture）
