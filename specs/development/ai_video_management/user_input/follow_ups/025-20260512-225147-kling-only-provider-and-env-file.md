# Follow-up draft 025 — 2026-05-12

把 face generation provider 收窄为 **仅 Kling**。删除 Pollinations + AI Horde + `ProviderChain` + 旧 retry/backoff 机制 + `AI_VIDEO_MGMT_FACE_PROVIDERS` env var。Kling 凭借 ~1-3s/img + 商业级稳定性 + JWT auth + prompt-attribute 可控，已经压倒 fallback chain 的价值；保留多 provider 抽象只会让安全表面 (3 个出站 host + 公开 anonymous apikey + r2.dev SSRF surface) 更大而无收益。

## 用户原话

> Lets remove the rest options to generate pictures, only use kling api key, here is the key you can put it in some local env file that is not tracked by git.
>   Access Key: A4PbbYLeTaaF3GBaBBmm3JgKFkNQPCHy
>   Secret Key: hyKnTGphpHEFbp4mpbhPNkQMR93Gpa3d

## 决策

| 项 | 之前 (follow-up 024) | 现在 (follow-up 025) |
|---|---|---|
| Default chain | `kling,pollinations,aihorde`（factory None→fallback） | **Kling-only，无 chain** |
| Kling env vars | optional（缺 → 静默 skip） | **required**（缺 → 启动 `RuntimeError`，failfast）|
| `AI_VIDEO_MGMT_FACE_PROVIDERS` | env-controlled | **删除**（无配置必要）|
| `ProviderChain` 类 | 存在 | **删除**（单 provider 不需要 round-robin）|
| `_FetcherShimProvider` | 存在（legacy 测试入口） | **删除**（无 tests 使用 fetcher kwarg，clean cut）|
| Pollinations retry/backoff (`_RETRY_BACKOFFS_SECONDS`, `_parse_retry_after`, `_default_fetcher`) | 存在 | **删除**（Kling 自己 poll，retry 不复用）|
| `AIHordeProvider` + `AIHORDE_*` 常量 | 存在 | **删除** |
| `PollinationsProvider` + `POLLINATIONS_BASE` + `_build_pollinations_url` | 存在 | **删除** |
| 出站 host 数 | 3 (`image.pollinations.ai`, `aihorde.net`, `*.r2.dev`, `api.klingai.com`) | **2** (`api.klingai.com` + Kling 返回的 r2-class CDN URL — 仍走 SSRF-vet) |
| Frontend "pollinations.ai 限速" hint | 存在 | **删除** |
| Frontend 2s inter-request throttle | 存在 (`INTER_REQUEST_THROTTLE_MS`) | **删除**（Kling 不限速）|
| 凭证存储 | env 直接 export（无文档） | **`projects/ai_video_management/backend/.env`** + 启动时 stdlib 加载（不入 git，根 `.gitignore` 已含 `.env`）|

## 实现

### 1. `backend/.env`（新文件，不入 git）

```
KLING_ACCESS_KEY=A4PbbYLeTaaF3GBaBBmm3JgKFkNQPCHy
KLING_SECRET_KEY=hyKnTGphpHEFbp4mpbhPNkQMR93Gpa3d
```

- 路径：`projects/ai_video_management/backend/.env`（main.py 旁，启动 cwd）
- 根 `.gitignore` 第 "# Environments" section 已含 `.env` → 自动 ignored，无需修改 .gitignore
- 文件本身不通过 EXPOSED_TREE 暴露（EXPOSED_TREE 限于 `ai_videos/`, `research/`, `specs/ai_video/`, `CLAUDE.md`, `.claude/**`；`projects/` 不在内）

### 2. `libs/env_loader.py`（新模块，≤30 行 stdlib）

- `load_env_file(path: Path) -> int` —— 读 `KEY=VALUE` 行；跳过空行 + `#` 注释行；只在 key 不在 `os.environ` 时 setdefault（已存在的 env 优先，便于 CI override）；返回加载的 key 数
- 不引入 `python-dotenv` 依赖；纯 stdlib (`pathlib` + `os`)
- 文件不存在 → return 0（dev 友好；缺凭证的错误会在 `KlingProvider.from_env()` 阶段以 `RuntimeError` 浮现）

### 3. wire into `main.py` + `libs/asgi.py`

两个启动入口都在最早期 import 完 stdlib 后 `load_env_file(Path(__file__).parent / ".env")`：

- `main.py`：在 `from libs.api import create_app` **之前**调用（否则 ActorPool 的 `_build_default_chain` 已经构造 KlingProvider）
- `libs/asgi.py`：在 `from libs.api import create_app` **之前**调用（reload mode 路径）

### 4. `actor_pool.py` 重构

**删除：**
- `POLLINATIONS_BASE`, `_build_pollinations_url`, `PollinationsProvider`
- `AIHORDE_*` 常量, `AIHordeProvider`
- `Provider` Protocol, `ProviderChain`, `_FetcherShimProvider`
- `HttpFetcher` type alias
- `_RETRY_BACKOFFS_SECONDS`, `_RETRY_AFTER_CAP_SECONDS`, `_parse_retry_after`, `_default_fetcher`
- `PROVIDERS_ENV_VAR`, `_DEFAULT_PROVIDER_NAMES`, `_PROVIDER_FACTORIES`, `_build_default_chain`

**保留 + 加强：**
- `KlingProvider` —— 仍 JWT HS256 stdlib + async POST→poll→download + SSRF-vet
- `_make_kling_jwt`, `_b64url`, `_kling_aspect_ratio`, `_is_safe_download_host`
- `ActorPool` —— constructor 改：移除 `fetcher` + `chain` kwargs，只接受可选 `provider: KlingProvider | None`（None → `KlingProvider.from_env()`，无 env → raise `RuntimeError` failfast）
- `KlingProvider.from_env()` —— 行为不变（缺 env → None），但 ActorPool 不再静默 fallback；构造时 None 直接 raise（启动期 failfast 优于运行期 silent 404）

**Sidecar 字符串：**「`AI-generated actor face (pollinations.ai, follow-up 014).`」→ 「`AI-generated actor face (Kling text-to-image, follow-up 025).`」

### 5. `frontend/ActorPoolGenerator.tsx`

- 删除 `INTER_REQUEST_THROTTLE_MS` 常量 + 主循环里的 `await new Promise(setTimeout, 2000)` 块
- 删除 `phase: "throttling"` 状态 + ProgressPanel 的 "⏸ 等待限速冷却…" 分支 + footer 按钮的 "等待 2s 防限速…" 文本
- 删除 `<p className="rate-limit-hint">ℹ️ pollinations.ai 免费 endpoint 有限速…</p>` banner
- `Progress` interface 收窄：`phase: "idle" | "generating"`

### 6. Spec 更新（surgical）

- `final_specs/spec.md` FR-9f：删除 (a) Pollinations + (b) AI Horde 段；保留 (c) Kling 段并去掉 "(c)" 前缀；把 "Default chain" 改为 "Provider"；删除 `AI_VIDEO_MGMT_FACE_PROVIDERS` 提及；Kling env vars 从 optional 升为 required（启动 failfast）
- `validation/security.md` carve-out #7：删除 Pollinations + AI Horde + chain 描述；保留 Kling secret hardening (g-bis)；删 (e), (f), (g)；新增 .env 文件不入 git 说明
- `validation/acceptance_criteria.md` U3.15 标题 "+ pollinations.ai 出站 HTTP" → "+ Kling 出站 HTTP"；Given 行 monkey-patch 注释 "模拟 pollinations.ai 成功响应" → "模拟 Kling 成功响应"（httpx monkey-patch 路径不变，provider-agnostic）
- `user_input/revised_prompt.md`：composed-from 加 025；header summary 替换为本 follow-up；follow-up 018 / 021 / 024 标记为 "已被 025 覆盖" 但 prior 行仍保留以保审计完整

## 安全 / 边界变化

- **缩小**：出站 host 数 3→2；anonymous AI Horde apikey 漏洞面消失；pollinations 公共 endpoint 无 auth 风险消失
- **不变**：Kling JWT HS256 stdlib（无 PyJWT dep）；secret 仅 env / 仅 `hmac.new` 输入；access_key 在 `iss` claim 是 identifier；30 分钟 JWT exp 现生；`code != 0` 显式检查；SSRF-vet download URL；30s timeout + 5MB cap
- **新增**：`.env` 文件存在；根 `.gitignore` `.env` 已覆盖；env_loader 不覆写已存在的 env（CI / shell 可 override）；文件 read errors 静默（filenotfound→return 0；其他 IOError 不影响启动，KlingProvider.from_env() 会 raise 给出明确错误）
- **failfast**：之前 follow-up 024 的 `KlingProvider.from_env() → None → chain fallback` 链路消失；现在 `ActorPool.__init__` 缺 env → `RuntimeError("kling env keys missing; set KLING_ACCESS_KEY + KLING_SECRET_KEY")`，启动期就报错而非首次 generate 时

## 不在本 follow-up 范围

- 不引入 `python-dotenv` 依赖（stdlib 30 行足够）
- 不改 `ActorPool.generate_batch` 公开签名（仍 `(attrs, count) -> GenerateResult`）
- 不改 `POST /api/actors/generate` HTTP 契约（响应 shape 不变）
- 不删 follow-up 018 / 021 / 024 follow-up 文件本身（审计历史保留）
- 不动 acceptance_criteria.md 其他 scenario
- 不删 sidecar 旧 actor_0001..0009 文件里 "pollinations.ai" 字样（历史 artifact，未来 regen 才会覆盖）
- 不引入 `KLING_MODEL` env override（继续 hardcode `kling-v1`）
- 不写 backend pytest（与 014-024 一致推迟；inline smoke 验证 import + env_loader + KlingProvider.from_env）
