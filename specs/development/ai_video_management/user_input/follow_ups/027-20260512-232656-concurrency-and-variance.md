# Follow-up draft 027 — 2026-05-12

两个独立修复, 共同提升 batch generate UX:

1. **并发**: 当前 frontend 串行 await `generateActors({count: 1, ...})`，按 Kling ~2-3s/img 算 20 张就要 ~50s。Kling API 允许 9 路并发 → frontend 改用 9-worker pool, batch 总时间从 `N × 2-3s` 降到 `ceil(N/9) × 2-3s`（20 张约 6-9s）。
2. **变异 (variance)**: 当前 `_build_prompt(attrs)` 对一个 batch 输出**同一句** prompt，仅 seed 不同 → Kling 同语义 prompt + 不同 seed 产生的 face 仍偏趋同。用户原话 (translation): 同一批应当在六字段基础上**自动注入** per-image 描述差异 — 长相 (清秀/邪魅/俊朗/小鲜肉)、肤色 (白/麦色/古铜)、脸型 (尖/圆/方)、眼型、发型等，避免趋同。

## 用户原话

> current generation of actor picture is too slow, kling api allow 9 concurrent request, please remove any limitation on your side and leverage the 9 concurrency on kling api, also, when I let you do batch generation, you should introduce a lot of variance to the text on top of the basic info, for example the basic info is asian，18~25 years old，handsome man，然后在这个基础上，你应该对于每一张图片加入自己的信息，可能图片1是清秀长相，图片二是邪魅长相，图片三是俊朗长相，图片四是小鲜肉，然后有的是皮肤白，有的是尖脸有的是圆脸，总之不要让每张图片太趋同

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| 并发实现位置 | **Frontend worker pool** (9 并发)，backend 仍每请求 1 张 | 保留 per-image progress UX (用户能看 "已完成 X / 进行中 Y / 总共 N")，per-image 错误独立报告；backend FastAPI sync endpoint 自动跑 threadpool → 9 并发请求自然映射到 9 个线程 → 9 路并发 Kling submit |
| Concurrency 数 | **9**（用户指定）| 直接对应 Kling 限制 |
| ID 分配竞态 | **`mkdir(exist_ok=False)` 原子分配** — 替代当前 `next_id = _next_actor_id_num + i` 的预算-then-create 模式 | 9 路并发同时调用 count=1 → 都看到 same `next_id = K` → 都尝试 `mkdir actor_K`，第一个成功其他 `FileExistsError`。Fix: 每张图片在分配时循环 `mkdir actor_K, actor_K+1, ...` 直到成功，filesystem-level 原子保证无重号 |
| 分配上限 | 单 batch 内最多扫描 1000 个 ID 后放弃 | 防御性 bound — 正常路径下 9 路并发分配每张只 try 几次，1000 是极端 OS 错误 fallback |
| Batch count 上限 | **20 → 50** | 用户 "remove any limitation" 含意。50 是 UX 合理上限 (modal 数字输入 + 服务端校验)；更高 batch 用户自己分多次跑即可。`MAX_BATCH_COUNT = 50` |
| 变异语言 | **English** 与现有 prompt template 一致 | `_build_prompt` 已是 English；mixing CN/EN 容易让 Kling 重点散乱。用户的中文例子是 **意图描述**，落到 prompt 里用 English 等价词更可控 |
| 变异 pools | 5 类: 面部特征 (男/女各一池)、肤色、脸型、眼型、发型 | 覆盖用户列举的 "长相 / 皮肤 / 脸型" 三类，加眼型 + 发型增强差异 |
| 变异种子 | **复用 actor 的 seed** | seed 已经是 per-image 唯一；用 seed 做 `random.Random(seed)` → 同 seed 重现同 variance（可复现），不同 seed 自然变化 |
| 变异 + 基本 prompt 顺序 | 变异 phrase 紧跟 base parts 中的 `look`，在 `style` 之前 | 让 look-level 描述聚拢，Kling 更易理解 |
| Sidecar 记录 | **记录 full varianced prompt** (与当前 `_build_sidecar(prompt=...)` 一致路径) | 用户能在 `actor_NNNN.md` 看 "这张图实际用了什么 prompt"，复现 / 复盘可靠 |
| 关闭变异? | v1 无 opt-out — 用户明确想要差异 | 若未来用户需要 "纯净 base prompt" 模式可加 follow-up 加 toggle |

## 功能要求

### Backend

**`projects/ai_video_management/backend/libs/actor_pool.py`**

1. **常量**: 加 5 个 tuple pools (面部男/女、肤色、脸型、眼型、发型)，纯 English fragments，每池 6-8 项
2. **新方法 `_variance_for(seed: int, gender: str) -> str`**:
   - `rng = random.Random(seed)`
   - 从 (gender-appropriate face features, skin tones, face shapes, eye descriptors, hair descriptors) 各 pick 一项
   - 返回 ", ".join(...) 字符串
3. **修改 `_build_prompt(attrs, variance="") -> str`**:
   - 在现有 parts 列表中 `attrs.look` 之后、`style` 之前插入 variance
   - 不传 variance 时 (default) 行为不变 — 为测试与潜在未来 opt-out 留口
4. **新方法 `_allocate_actor_id(actors_dir: Path) -> tuple[str, Path]`**:
   - 从 `_next_actor_id_num` 拿起点
   - 循环 `mkdir(exist_ok=False)` 直到成功
   - 1000 次失败后 raise `GenerationDirMissing`
5. **重写 `generate_batch` 主循环**:
   - 去掉预算 `next_id_num = self._next_actor_id_num(actors_dir)` + offset 模式
   - 每张图片调 `_allocate_actor_id(actors_dir)` 拿 (actor_id, folder)
   - seed 仍 `base_seed + i`
   - `variance = self._variance_for(seed, attrs.gender)`
   - `prompt = self._build_prompt(attrs, variance=variance)` (per-image varianced prompt)
   - 传给 provider + sidecar
6. **`MAX_BATCH_COUNT`** 20 → **50**

### Frontend

**`projects/ai_video_management/frontend/src/components/ActorPoolGenerator.tsx`**

1. **常量** `CONCURRENCY = 9` (top-of-file)
2. **修改 `Progress` interface**: 把 `current: number` 替换为 `inFlight: number`
3. **重写 `onSubmit` 主循环**:
   - 不再 `for (let i = 1; i <= total; i++) await ...`
   - 改用 worker pool: 创建 `Math.min(CONCURRENCY, total)` 个 worker，每个 worker 在循环中从 shared `next` counter 拉下一张
   - 每张完成后 `onGenerated()` + setProgress 更新 done/failed/inFlight
   - 取消逻辑保留 (`cancelledRef`) — 取消时 worker 退出循环；已 in-flight 的请求完成时正常 tally
4. **修改 `<input type="number" max>` 1→**5**0** + onChange 的 clamp 上限同步
5. **修改 button 显示文字**:
   - busy 时: `生成中… (${done + failed} / ${total})` (去掉 current index 概念)
6. **修改 ProgressPanel**:
   - 显示新增 in-flight 计数: `<span>进行中: ${inFlight}</span>`

**`projects/ai_video_management/frontend/src/api.ts`** — 零改动 (HTTP API 形状不变)

### Spec / validation walk

- `final_specs/spec.md` FR-9f: 在 prompt 描述里加 "per-image variance phrase appended to the prompt (server-side variance pools seeded by the actor's seed, see `_variance_for`)"；提到 frontend 9-way worker pool；MAX_BATCH_COUNT 20→50
- `final_specs/spec.md` FR-88: count input 上限 20→50
- `validation/security.md` carve-out #7: 变异 fragments **来自硬编码的服务端 tuple**，不接受用户输入 → 无新 prompt-injection 面；race-safe ID 分配同时关闭 9-并发下的 ID 冲突 race；MAX_BATCH_COUNT 50 = 仍然 bound 整个 batch 的最大 outbound HTTP wave
- `validation/acceptance_criteria.md` U3.15: 加 "concurrent batch" 子断言 (Given 9 个并发请求各 count=1 → ID 不重号 + 全部成功); 提到 prompt 含 variance fragment

## 安全 / 边界

- **No new outbound surface** — 仍仅 Kling
- **No new user input** — variance pools 完全 server-side
- **No new race** — `mkdir(exist_ok=False)` 是 POSIX/Windows 都 atomic 的原子操作; 实际上 fix 了之前的潜在 race (虽然之前 frontend 串行所以从没触发)
- **No new failure mode** — variance 注入只是字符串拼接，不会让 prompt 失败
- **Sidecar 不变规格** — 仍含完整 prompt + seed; 用户可复现（同 seed → 同 variance → 同 prompt）

## 不在本 follow-up 范围

- 不引入 backend 内部并发（FastAPI sync threadpool 已足够；不加 `ThreadPoolExecutor` / async wrapper）
- 不引入 negative_prompt / cfg_scale 等 Kling 高级参数
- 不允许用户编辑 variance pools（v1 hard-coded）
- 不引入 "禁用 variance" toggle（用户明确要差异；未来若需要可加）
- 不写 backend pytest / frontend Vitest（与 005-026 一致推迟）
- 不动 follow-up 026 的 actor delete 按钮 / cascade 逻辑（正交）
- 不动 Kling JWT / SSRF-vet / 30s timeout / 5MB cap（与 follow-up 025 一致；并发只是同时跑多个相同的单请求）
- 不动 `_actors/_deleted/` 路径分配规则（follow-up 026 已定义）
