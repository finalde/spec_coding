# Follow-up draft 024 — 2026-05-12

加 **Kling text-to-image** 作为第 3 个 face generation provider，放在 chain 首位作为 primary。Kling 是 ByteDance/快手 商业级 API（用户已经用它跑 Seedance 视频，故已有 access），text-to-image ~1-3s 出图（10×+ 快过 pollinations，30×+ 快过 AI Horde queue），属性可控（prompt 内传），稳定（无队列波动）。

## 用户原话

> please use the following see if it could speed things up, right now it took so long to generate the pictures:
>   - 方案 A：从 thispersondoesnotexist.com 自动下载 100 张 AI 生成的亚洲脸（需要筛选，因为它生成全人种）
>   - 方案 C：用 generated.photos 的筛选功能直接拉亚洲面孔
>
> if I give you kling text to image api, would that help?

## 评估

| 选项 | Verdict |
|---|---|
| A) TPDNE | ❌ StyleGAN/FFHQ documented bias — 亚洲脸命中率 10-30%；要 ML 分类器或人工 curation，新增复杂度高于收益 |
| C) Generated.Photos | ❌ ToS 明禁 "caching, stockpiling, or downloading photos as stand-alone files" —— 与 `_actors/` 持久化用例正面冲突 |
| **Kling text-to-image (用户提议)** | ✅ 商业级 + JWT auth + 用户已有 access + ~1-3s/img + prompt-based attribute control + 无队列等 |

## Kling API 摘要

- POST `https://api.klingai.com/v1/images/generations`
- Auth: JWT HS256，payload `{iss: access_key, exp: now+1800, nbf: now-5}`，signed with `secret_key`
- Body: `{model_name: "kling-v1", prompt: "...", aspect_ratio: "1:1", n: 1}`
- Response: `{code: 0, data: {task_id: "..."}}`
- Poll: GET `/v1/images/generations?pageSize=500` 列 tasks，找匹配 task_id，等 `task_status: "succeed"`
- 拿到 `task_result.images[0].url` → download (r2-like CDN URL)

## 实现

### 新增 `KlingProvider`（actor_pool.py）

跟随 `Provider` Protocol，集成现有 chain：

- **JWT 生成**：纯 stdlib (`hmac` + `hashlib` + `base64` + `json`)，**不引入新依赖**（避免 `PyJWT` dep）；header `{"alg":"HS256","typ":"JWT"}` + payload + url-safe base64 + HMAC-SHA256 signature
- **`from_env()` factory**：读 env `KLING_ACCESS_KEY` + `KLING_SECRET_KEY`，**两者都设才返回 instance，否则返回 None**（让 `_build_default_chain` skip 该 provider）
- **流程**：submit POST → 检 `code == 0` → poll GET（每 2s，max 120s）→ 找 task → 检 `task_status` (`succeed` / `failed` / 其他 = processing) → 拿 url → SSRF-vet → download (follow_redirects=True, 5MB cap, 30s timeout)
- **Aspect ratio**：从 (width, height) 推断：512×512 → `"1:1"`；其他 16:9 / 9:16 / 4:3 / 3:4 fallback。Kling 不接受任意分辨率，必须 enum ratio

### `_build_default_chain` 改动

- 默认 chain 改为 **`kling,pollinations,aihorde`**（kling 优先；用户未设 kling env 时 factory 返 None，chain 自动降级回 `pollinations,aihorde` —— 零 breaking change）
- factory 返 None 的支持：循环内 `instance = factory(); if instance is None: continue`

### env vars

新增两个 optional env（zero impact if unset）：
- `KLING_ACCESS_KEY` —— Kling access key (AK)
- `KLING_SECRET_KEY` —— Kling secret key (SK)

获取：`app.klingai.com/global/dev` 创建账号 → API keys page。

`AI_VIDEO_MGMT_FACE_PROVIDERS` 不动；默认值变为 `kling,pollinations,aihorde`。用户可手动 override 顺序（如 `pollinations,kling,aihorde` 让 pollinations 优先）或排除某个（`kling,pollinations` 跳过 AI Horde）。

## 安全 / 边界扩展

- **JWT secret 不进 source code / log / response body** —— 仅 env var 读，仅 HMAC 输入用
- **AK 进 JWT payload (`iss` claim)** —— 这是 Kling 协议标准，AK 本身不是 secret（identifier）
- **JWT 每次 generate() 调用现生**（30 分钟有效期，绰绰有余；不缓存在内存避免 stale），HMAC 实现无 timing attack 风险（用 `hmac.new` 常时计算）
- **Download URL SSRF-vet**：复用现有 `_is_safe_download_host` —— Kling 返回的 r2/CDN URL 必须 https + 非 loopback / RFC1918 / link-local / multicast / reserved
- **Response code check**：Kling 即使 HTTP 200 也可能在 body `code != 0` 报错；显式检查避免吞错
- **失败模式**：JWT 过期 → submit 401 → chain fall through；Kling rate limit → submit 429 → chain fall through；轮询超时 (120s) → raise TimeoutError → chain fall through

## 不在本 follow-up 范围

- 不引入 `PyJWT` 依赖（stdlib 足够）
- 不引入 Kling video-to-image / image-to-image / image-to-video endpoint（仅 text-to-image）
- 不引入 negative_prompt / cfg_scale / image_count > 1 等高级参数（v1 用 model 默认 `n: 1`）
- 不持久化 task_id 到磁盘 / 数据库（每次内存 poll；进程重启则失踪的 task 算丢失，重试新 batch 即可）
- 不写 backend pytest（与 005-022 一致推迟；inline smoke 验证 JWT 生成 + chain 集成）
- 不动前端（chain 透明）
- 不在 spec.md 改 FR-9f 的 endpoint 契约（仅在 provider 描述里加 kling）
