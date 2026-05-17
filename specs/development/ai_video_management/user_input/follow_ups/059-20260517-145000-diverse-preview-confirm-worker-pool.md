# Follow-up draft 059 — 2026-05-17

Summary: 把多样化随机模式（follow-up 053）的生成路径从"单 HTTP 调用阻塞 N 个 actor"重做为"preview-then-confirm + 9-worker concurrent pool 单 slot 单调用"，对齐标准模式（follow-up 032 + 027）。单次请求生成 10 个 actor × face+body 双图 ≈ 10 × 2 × 30-120s = 10-40 分钟的同步 HTTP，浏览器看到 UI 卡死，uvicorn `timeout_graceful_shutdown=2` 也可能截断。修法：(1) 新 `POST /api/actors/preview-diverse` 返回 N 个 slot 的 `{seed, archetype, archetype_label, attrs, prompt, body_prompt}` 计划；(2) `ActorPoolGenerator` 多样化模式从直 generate 改为 preview→confirm pattern，确认后用既有 9-worker pool 按 slot iterate 调 `generateActors({count: 1, ...slot.attrs, seeds: [slot.seed], archetype: slot.archetype})`；(3) `generateActors` 后端 body 扩 optional `archetype` 字段，按 slot 写入 sidecar archetype slug；(4) ProgressPanel 原生支持 done/failed/in-flight 进度报告。同时满足用户两条诉求：preview-first + UI 响应式 progress。

## 用户原话

> when I choose多样化随机模式, still show me the prompt and let me review first, before you submit to kling api to generate the actors

> when I click generate 10 random actors, it just stuck there forever, plesae fix the issue also the UI should be responsive and show me the progress

## 根因 (responsiveness)

`ActorPoolGenerator.onDiverseGenerate` 调 `generateDiverseActors({count, gender, ethnicity, resolution})` → 单 HTTP 调用。后端 `ActorPool.generate_diverse_batch` 在该单次 sync FastAPI request 内 sequential 跑 N 个 slot，每 slot 两次 Kling：face (10-120s) + body (10-120s)。N=10 时上限 ~40 分钟。浏览器看到无响应（无中间反馈、无进度），用户感觉"卡死"。同时 follow-up 037 + 042 的 `timeout_graceful_shutdown=2` + `os._exit` watchdog 在 dev reload 时可能截断该长 request。

修法：把"单 batch 调用"改为"N 个 count=1 调用 + 9-worker concurrent pool"。每 slot 一个 HTTP request；front-end 边收边更新 `Progress { done, failed, in_flight }` → ProgressPanel 实时显示。已经是标准模式 (follow-up 027) 的成熟 pattern；只需把多样化模式接入。

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| Preview-then-confirm 强制 | 是 — 多样化模式仅经 preview→confirm 路径；direct-generate 路径下线 | 用户原话；同时解决"卡死"问题 |
| Preview 后端 | 新 `ActorPool.preview_diverse_prompts(gender, ethnicity, count, resolution)` — 复用 `_distribute_archetypes` + per-slot RNG 滚 (age, look, style)，build face_prompt + body_prompt | 不 call Kling；纯计算；返回 plan |
| Preview return shape | `{prompts: [{seed, archetype, archetype_label, attrs:{eth,gen,age,look,style,notes}, prompt, body_prompt}], resolution}` | 兼容标准 preview shape（`{prompts: [{seed, prompt, body_prompt}]}`），额外字段 archetype/attrs 由 diverse-mode preview consumer 渲染 |
| Notes 字段在 diverse 模式 | 自动设为 `spec.name_zh`（中文档案 ID）| 与 follow-up 053 generate_diverse_batch 一致；用户在 ActorGrid tile 上能看到角色类型 |
| Preview seed 计算 | `base_seed = int(time.time() * 1000)` + `seed = base_seed + i`；per-slot RNG `random.Random(seed ^ 0x5A5A5A)` 与 generate_diverse_batch 一致的逻辑 | 同确定性；preview 与 confirm-then-generate 之间通过 explicit seeds list 传递，无需相同 base_seed |
| 新 endpoint | `POST /api/actors/preview-diverse` body `GenerateDiverseActorsBody` (既有 - count/gender/ethnicity/resolution) | 与 preview-prompts 平行 |
| Confirm 端 (worker pool) | 复用既有 9-worker concurrent pool；遍历 `preview.prompts` 调 `generateActors({count: 1, ethnicity, gender, age_range, look, style, notes, resolution, seeds: [slot.seed], archetype: slot.archetype})` | 复用标准模式 follow-up 027/032 成熟代码；每 slot 一 HTTP + 实时 progress |
| `GenerateActorsBody` 扩 | 加 optional `archetype: str \| None = None` | 让 worker pool per-slot 调用写入 archetype slug 到 sidecar；标准模式继续 None（无 archetype 行） |
| `ActorPool.generate_batch` 扩 | 加 optional `archetype: str \| None = None` 参数；plumb 到 `_build_sidecar` | 单 slot 调用支持 archetype；不影响标准模式 |
| `GenerateActorsCommand.execute` 扩 | 接收 + 传 `input_cdto.archetype` 到 `pool.generate_batch` | DDD 通道 |
| `GenerateActorsInputCdto` 扩 | 加 optional `archetype: str \| None = None` | DTO 一致 |
| 旧 `generate-diverse` endpoint | **保留**（不动）— 后端向后兼容，UI 不再使用 | 不破契约；其它 client 仍可调（虽然没有） |
| 旧 `onDiverseGenerate` 函数 | **删除** — 多样化模式直生成路径下线；走 preview→confirm | 单一路径 |
| 多样化模式 footer button | 改为 "预览 prompt" — 与标准模式一致 | 用户一致体验 |
| Preview modal 渲染 diverse 元数据 | `PromptPreviewModal` 加可选 archetype/attrs 显示在每个 prompt card header（present 即显示） | 用户审阅时能看到角色类型分布 + 滚出的 attrs |
| ProgressPanel | 不动 — 既有标准模式 progress UI 已支持 done/failed/in_flight + per-slot phase 报告 | 多样化模式自动得益 |

## 功能要求

### Backend

**`libs/infrastructure/writers/actor__writer.py`**（post-056 reorg 路径）：

1. 新方法 `ActorPool.preview_diverse_prompts(gender, ethnicity, count, resolution) -> dict`:
   - validate gender / ethnicity / count / resolution (复用 `generate_diverse_batch` 校验逻辑)
   - `plan = self._distribute_archetypes(count, gender)`
   - `base_seed = int(time.time() * 1000)`
   - 对每 slot i:
     - `seed = base_seed + i`
     - `slot_rng = random.Random(seed ^ 0x5A5A5A)`
     - `spec = plan[i]`
     - `attrs = ActorAttrs(ethnicity, gender, age_range=slot_rng.choice(spec.age_ranges), look=slot_rng.choice(spec.looks), style=slot_rng.choice(spec.styles), notes=spec.name_zh)`
     - `variance = _variance_for(seed, gender)`
     - `face_prompt = _build_face_prompt(attrs, variance)`
     - `body_prompt = _build_body_prompt(attrs, variance)`
     - append `{seed, archetype: spec.slug, archetype_label: spec.name_zh, attrs: attrs.to_dict(), prompt: face_prompt, body_prompt}`
   - return `{prompts: [...], resolution}`

2. `ActorPool.generate_batch` 签名扩展：加 `archetype: str | None = None` 参数；调 `_build_sidecar(..., archetype=archetype)`。

**`libs/application/queries/actor__query.py`**：

新增 `PreviewDiverseActorPromptsQuery` 类，接收 `GenerateDiverseActorsInputCdto`，调 `pool.preview_diverse_prompts`，经 mapper 返回 Qdto。

**`libs/application/dtos/actor__dto.py`**：

- `GenerateActorsInputCdto` 加 optional `archetype: str | None = None`。
- `PreviewDiverseActorsResultQdto` 新增（结构 = `{prompts: [...], resolution}`）；如果偷懒可复用 `PreviewActorPromptsResultQdto` (假设它就是 `dict[str, object]`)。

**`libs/application/mappers/actor__mapper.py`**：

加 `preview_diverse_to_qdto(raw: dict) -> ...` (或直接复用 `preview_to_qdto`)。

**`libs/application/commands/actor__command.py`**：

`GenerateActorsCommand.execute` plumb `input_cdto.archetype` 到 `pool.generate_batch`。

**`apps/api/container.py`**：

加 `preview_diverse_actor_prompts_query` Factory provider。

**`apps/api/routes.py`**：

1. `GenerateActorsBody` Pydantic model 加 `archetype: str | None = None`。
2. 新 endpoint `POST /api/actors/preview-diverse`:
   - body `GenerateDiverseActorsBody` (已存在 - count/gender/ethnicity/resolution)
   - inject `PreviewDiverseActorPromptsQuery`
   - 错误映射同 `actors_preview_prompts` (InvalidActorAttributeError → 400)
   - 返回 `qdto.to_payload()`
3. 新 405 handler `actors_preview_diverse_method_not_allowed`。
4. `actors_generate` route 内 `_generate_input(body)` 函数 + 路由调用更新以传递 `body.archetype`（透传到 CDTO）。

### Frontend

**`apps/ui/src/api.ts`**：

1. `GenerateActorsRequest` interface 加 optional `archetype?: string | null`。
2. 新 `previewDiverseActors(req: GenerateDiverseActorsRequest)` POST `/api/actors/preview-diverse` 返回 PromptPreviewResult-compatible shape (含 archetype/attrs 可选字段).
3. 扩展 `PromptPreviewResult` interface 让 prompt entries 可选含 `archetype?: string`, `archetype_label?: string`, `attrs?: ActorAttrs`, `body_prompt?: string`.
4. 旧 `generateDiverseActors` 函数 **保留** — backward compat (CLI / 测试 / 未来直生成入口可能用到)；UI 不再调。
5. 旧 `GenerateDiverseActorsRequest` 接口 **保留** — 同理。

**`apps/ui/src/components/ActorPoolGenerator.tsx`**：

1. **删除** `onDiverseGenerate` 函数（不再走 direct-generate 路径）。
2. `onPreview` 函数内加 mode 分支：
   - `mode === "standard"` → 调 `previewPrompts` (现行行为)
   - `mode === "diverse"` → 调 `previewDiverseActors`
3. `onConfirmGenerate` 函数（既有 9-worker pool）改为：
   - 既有 `seedsList = preview.prompts.map((p) => p.seed)` 保留。
   - 每 worker 在 `claimSlot` → 调 `generateActors` 时，根据 slot 取的 prompt entry：
     - standard mode (无 archetype/attrs 字段) → 用 form attrs（既有行为）
     - diverse mode (有 archetype + attrs) → 用 slot.attrs + slot.archetype
4. Footer button label：mode === "diverse" 也显示 "预览 prompt"（取消区别）。
5. ProgressPanel 自动得益（既有）。

**`apps/ui/src/components/ActorPoolGenerator.tsx` 内 PromptPreviewModal**：

每张 prompt card header 加可选 archetype label 显示（条件 `entry.archetype`）。例如：
```
Seed 1234567890 | 角色类型: 男主气场冷峻 (leading_hero)
Attrs: asian / male / 18-25 / handsome / period-ancient-china
{prompt}
```

### Spec / validation

- `final_specs/spec.md` 加 FR-9t (`POST /api/actors/preview-diverse`) + FR-9f extension 提及 archetype 可选写入 sidecar via generate-actors 单 slot 调用。
- `validation/acceptance_criteria.md` 暂不更新（deferred batch）。

### User input + audit

- `revised_prompt.md` header bump for 059。
- `changelog.md` append 059 entry。

## 安全 / 边界

- **Preview 不调 Kling** — 零成本；用户自由 preview 后取消。
- **Cost x2 per slot** (face + body) — 同 follow-up 052；preview→confirm 之间用户能 cancel 减少未生成 slot。
- **Worker pool concurrency=9** — 同 follow-up 027；9-way 并行 → 10 个 slot 一轮全部并行；20 个 slot ~ 两轮。
- **Per-slot HTTP request** — 9 个并发 connection 进 backend；FastAPI threadpool 处理；既有架构验证。
- **`archetype` 写入 sidecar via generate_batch** — 不影响 list_actors / migrate_archetypes（已支持 archetype 字段 parse）。
- **Sandbox / origin gate / Kling SSRF vet** — 全部继承既有 `generate_batch` 路径。
- **失败隔离** — 单 slot 失败不阻塞其它（既有 worker pool 已支持）；diverse 模式同理。
- **Backward compat** — 旧 `generate-diverse` endpoint 保留；`generateDiverseActors` API 函数保留；只是 UI 不再用。

## 不在本 follow-up 范围

- 不删除旧 `generate-diverse` 后端 endpoint / 应用层 Command。
- 不为 standard 模式加 archetype（standard 不挑 archetype；用户若想标 archetype 走 diverse）。
- 不动 PromptPreviewModal 的整体布局（仅在 card header 加 archetype label 行）。
- 不写 vitest / pytest。
- 不动 ProgressPanel 实现。
- 不引入新 progress 字段（既有 done/failed/in_flight/phase 已够）。
- 不动 follow-up 052 的双图 + Variance + cast/ copy 路径。
- 不动 follow-up 053 的 generate_diverse_batch 方法（向后兼容保留）。
