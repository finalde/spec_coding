# Follow-up draft 021 — 2026-05-12

让 actor face 生成不再绑定单一 source，引入 **provider rotation with failover** 架构。Pollinations.ai 仍是默认 primary，新增 **AI Horde（aihorde.net）匿名 endpoint** 作为 fallback；每张图按 round-robin 选起点 provider，失败时 fall through 到 chain 内下一个。

## 用户原话

> is pollination.ai the only site you could download free ai generated pictures? is there any other free alternative? could you do a bit research to see if there is a better one, then we could avoid the rate limit of only 1 sites

## Research summary（详见 conversation log）

| Provider | Auth | Free limit | Latency | Server-side? | Verdict |
|---|---|---|---|---|---|
| Pollinations.ai (current) | None | 软限速；burst 触发 429 | 5–30 s sync GET | ✅ | 现役；限速痛 |
| **AI Horde** (aihorde.net) | 匿名 `apikey="0000000000"` | 无硬上限（kudos 优先级） | 10–90 s async (POST→poll→download) | ✅ | ✅ **选中** — 真免费 + 无 signup + FLUX/SDXL 可选 |
| Cloudflare Workers AI | 必须 signup + token | 10k neurons/d ≈ 100–200 img/d | 1–5 s sync | ✅ | 用户答选项中**不选**（要 signup） |
| Together AI | signup + 信用额 | 受限 | 1–2 s | ✅ | 同上理由排除 |
| HuggingFace Inference | token | ~1000/d | 慢 + cold start | ✅ | token + cold start |
| Puter.js | 无声称 | 未知 | – | ❌ browser-only | 不能从 Python backend 调 |
| DeepAI | 必须 key | 小 | fast | ✅ | 要 key |
| ZSky AI | signup + 50 lifetime credits | 50 lifetime | fast | ✅ | 太小 |
| Generated.Photos | 必须 key | 受限 | fast | ✅ | ⛔ ToS 禁 download/cache（同 follow-up 014 否决理由） |

## 用户决策（interactive 收集 2026-05-12）

| 问 | 用户答 |
|---|---|
| Provider mix | **pollinations + AI Horde fallback**（不引入 Cloudflare） |
| Failover 策略 | **Round-robin per image, with failover** — 每张从 chain 下一位起，失败则 fall through |

## 架构设计

### Provider 抽象

```python
class Provider(Protocol):
    name: str
    def generate(self, prompt: str, seed: int, width: int, height: int) -> bytes: ...
```

**PollinationsProvider**：把 follow-up 014/018 现有 `_default_fetcher` 逻辑（URL build + 3 次 retry + Retry-After + 30s timeout）原样封装到 class 内。

**AIHordeProvider**：
- Base URL: `https://aihorde.net/api/v2`
- Anonymous apikey: `"0000000000"`
- 流程：
  1. POST `/generate/async` with `{prompt, params:{seed, width, height, steps:30, n:1}, models:["stable_diffusion"], r2:true}` + header `apikey: 0000000000`
  2. 拿到 `id` (job UUID)
  3. Poll GET `/generate/check/{id}` 每 5s 一次，直到 `done: true` 或超时 (180s)
  4. GET `/generate/status/{id}` 拿 `generations[0].img` URL (通常 r2.dev)
  5. GET 那个 URL 下载 raw bytes (follow_redirects=True 因为 r2 可能 redirect)
- 异常：fault state、queue 满、polling 超时 → raise

**ProviderChain**：
```python
class ProviderChain:
    def __init__(self, providers): self._providers = providers; self._index = 0
    def generate(self, prompt, seed, width, height) -> bytes:
        n = len(self._providers)
        start = self._index
        self._index = (self._index + 1) % n  # advance regardless of success
        last_exc = None
        for offset in range(n):
            try: return self._providers[(start + offset) % n].generate(...)
            except Exception as exc: last_exc = exc; continue
        raise last_exc or RuntimeError("all providers failed")
```

Round-robin index 每次调用前进 1（无论成功失败），所以连续 N 次调用会依次以 provider[0], [1], ..., [N-1] 起手。失败时 fall through 同 chain 余下 provider。

### Configuration

环境变量 `AI_VIDEO_MGMT_FACE_PROVIDERS=pollinations,aihorde`（默认）控制 chain 组成 + 顺序。用户可设：
- `pollinations` → 单 provider，关闭 AI Horde
- `aihorde,pollinations` → 反序，AI Horde 优先
- 空 / 无效值 → 回退默认

### Test-fetcher 兼容

`ActorPool.__init__(exposed, resolver, fetcher=None, providers=None)`：
- 现有测试传 `fetcher=lambda u, t, m: bytes` 仍 work — `fetcher` 被包成 `FetcherShimProvider` 单成员 chain，绕过 env var
- 测试可显式传 `providers=[FakeProvider(...)]`
- 默认（生产）：读 env var 构建 chain

`generate_batch` 内部从 `self._fetcher` 改用 `self._chain.generate(prompt, seed, width, height)` —— URL build 移到 provider 内部，避免 chain 假设特定 URL 结构。

## 安全 / 边界扩展

- AI Horde 也是新出站 HTTP destination（第 2 个），与 pollinations 同样硬化：
  - Base URL 写死 `https://aihorde.net/api/v2`
  - apikey 写死 `"0000000000"` (公开 anonymous 标识符，非 secret)
  - r2.dev download URL 在 response body 内 —— 由 AI Horde 服务端控制 host，**这是新风险面**：恶意 / 被劫持的 AI Horde 服务端可返回任意 URL 让 backend GET
  - 缓解：download step 也限 30s timeout + 5MB response cap；只允许 https:// scheme；不允许内网 / localhost / RFC1918 IPs（用 `urllib.parse` 检查 hostname）
- 单图 worst case wall-clock：pollinations retry (~81s) + AI Horde async wait (180s) + AI Horde download (30s) = ~5 min。已远超浏览器 fetch timeout，但 follow-up 017 已搬循环到前端 → 每图独立请求，单图 5min 是上限。
- CSP `connect-src 'self'` 不变（前端不直接访问 AI Horde）

## 不在本 follow-up 范围

- 不引入 Cloudflare Workers AI（用户答选不要）
- 不引入更精细 per-provider retry config（pollinations 仍 retry 3 次；AI Horde 单次尝试不内部 retry，由 chain 层 fall through 到 pollinations）
- 不引入 AI Horde 模型 / params UI 选择（hardcode `stable_diffusion` model + 30 steps）
- 不引入 AI Horde kudos / API key registration（保持 anonymous）
- 不写新 backend pytest（与 005-019 一致推迟；inline smoke 验证 chain 行为）
- 不动 frontend（chain 对前端透明）
