# Follow-up draft 032 — 2026-05-13

两个独立小改:

1. **ActorGrid PAGE_SIZE 12 → 50**: 用户嫌每页 12 太少，希望一页看更多对比。50 是 follow-up 029 的 batch 上限 (MAX_BATCH_COUNT)，对齐。
2. **Pre-batch prompt review step**: 当前点 "生成" 直接 fire 9-worker pool；用户希望先 review **将要发给 Kling 的 final prompt**（含 variance + anti-wax + camera cue 全部展开），点 "确认发送" 才真正调 Kling。

第 2 项需要：preview 返回 N 个 (seed, prompt)，gen 接受 `seeds: list[int]` 复用同样种子 → 同样 variance → 同样 prompt → 字节级一致 review。

## 用户原话

> 每页的演员展示上限可以多一点， 比如50个，当batch gen以前，加一个步骤，然我review 以下你准备发给kling api的prompt的final 版本，我确定之后点另一个button 在执行

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| Grid PAGE_SIZE | **12 → 50** | 用户指定；对齐 MAX_BATCH_COUNT=50 |
| Preview surface | **新 endpoint `POST /api/actors/preview-prompts`** | preview 与 gen 解耦；preview 不消耗 Kling API quota / 不写文件 |
| Preview body | 与 `GenerateActorsBody` 同结构（attrs + count + resolution + notes） | 复用现有 schema |
| Preview response | `{prompts: [{seed, prompt}], resolution}` | seeds 保证 gen 可复用；resolution 透传 |
| Gen 接受 seeds | `GenerateActorsBody.seeds: list[int] \| None = None`；提供时 `generate_batch` 用这些 seeds，否则原 `int(time.time()*1000)+i` | 字节级一致 review |
| Seeds 校验 | 长度必须 == count；否则 400 invalid_attribute | 与现有 attribute 校验对齐 |
| Preview 模态 UI | 显示 N 张 expandable card：actor slot # / seed / prompt（默认 collapsed 显示前 200 chars + "展开"） | 50 张完整 prompt 一屏铺开难看，progressive disclosure |
| Confirm 按钮 | 模态 footer "✓ 确认发送 (N)" + "取消" | 用户原话 "我确定之后点另一个button 在执行" |
| 取消行为 | 关闭模态，丢弃 seeds，不调 gen API | 用户 explicit |
| Preview 失败 | 显示 error；不进 modal | preview API 失败不应静默 fall through |
| 并发不变 | 确认后仍 9-worker pool 跑 count=1 调用，每个调用带其 seed | gen API 已可接 seeds 数组分发 |
| seeds 传递机制 | frontend worker 池里每个 worker 拉的 slot 对应 seeds[slot-1]；POST /api/actors/generate body 带 `{seeds: [single_seed]}` count=1 | 单 seed 数组保证 backend 收到的 seeds 就是 frontend 期望的 |

## 功能要求

### Backend

**`projects/ai_video_management/backend/libs/actor_pool.py`**:

- `generate_batch(attrs, count, resolution="normal", seeds=None)` 加 `seeds: list[int] | None = None` 参数
- 校验：`seeds is None or (isinstance(seeds, list) and len(seeds) == count and all isinstance(s, int))`；否则 `InvalidAttribute`
- 主循环 seed 来源：`seed = seeds[i] if seeds is not None else base_seed + i`
- 加 new method `preview_prompts(attrs, count, resolution) -> dict[str, object]`:
  - 校验 attrs / count / resolution（复用现有）
  - 计算 `base_seed = int(time.time() * 1000)`
  - 对每个 i：`seed = base_seed + i; variance = _variance_for(seed, attrs.gender); prompt = self._build_prompt(attrs, variance=variance)`
  - 返回 `{"prompts": [{"seed": ..., "prompt": ...}], "resolution": resolution}`

**`projects/ai_video_management/backend/libs/api.py`**:

- `GenerateActorsBody.seeds: list[int] | None = None`
- 新 endpoint `POST /api/actors/preview-prompts` body `GenerateActorsBody`（seeds 字段忽略）→ 调 `actor_pool.preview_prompts(...)` → 返回 JSON；同 method-not-allowed handler 405
- `actors_generate` 把 `body.seeds` 传给 `generate_batch`

### Frontend

**`projects/ai_video_management/frontend/src/api.ts`**:

- 加 `interface PromptPreviewResult { prompts: { seed: number; prompt: string }[]; resolution: string }`
- 加 `previewPrompts(req: GenerateActorsRequest): Promise<PromptPreviewResult>` POST `/api/actors/preview-prompts`
- `GenerateActorsRequest.seeds?: number[]`

**`projects/ai_video_management/frontend/src/components/ActorPoolGenerator.tsx`**:

- 新 state: `preview: { prompts: [{seed, prompt}], resolution } | null`, `previewBusy: boolean`, `previewError: string | null`
- "生成" 按钮 onClick 改为 `onPreview`: 调 `previewPrompts(req)` → 设 `preview` state → 自动打开 preview modal
- 新 `PromptPreviewModal` 子组件: 列每个 slot card（slot # / seed / 默认 200 chars + "展开"），footer "取消" + "✓ 确认发送 (N)"
- 确认 → 关 preview modal → 进入现有 9-worker pool loop，但每个 worker 调 `generateActors({..., seeds: [previewSeeds[slot-1]]})`
- 已有 `onSubmit` 重命名为 `onConfirmGenerate(seeds)` 接收 preview seeds

**`projects/ai_video_management/frontend/src/components/ActorGrid.tsx`**:

- `PAGE_SIZE = 12` → `PAGE_SIZE = 50`

**`projects/ai_video_management/frontend/src/styles.css`**:

- 新 rules: `.prompt-preview-list` / `.prompt-preview-card` / `.prompt-preview-seed` / `.prompt-preview-body` / `.prompt-preview-toggle` 等

### Spec / validation

- `final_specs/spec.md` FR-9f: body 加 `seeds: list[int] | None` + 描述 preview-then-confirm 流程
- `final_specs/spec.md` 新 **FR-9j** `POST /api/actors/preview-prompts` (dry-run prompt 计算，无 Kling 调用，无文件 IO)
- `final_specs/spec.md` FR-88 + FR-91: 提及 preview modal step + PAGE_SIZE 50
- `validation/security.md` carve-out #7: 加 `/api/actors/preview-prompts` 是 read-only dry-run，无新 outbound HTTP；seeds 来自用户但走 InvalidAttribute 校验（必须 list[int] + len==count）
- `validation/acceptance_criteria.md` U3.15: 加 preview → seeds-roundtrip → gen 用同样 prompts 断言；新 U3.19 grid PAGE_SIZE 50 + 在 13 actors 时不分页（13 ≤ 50）

## 安全 / 边界

- **`/api/actors/preview-prompts` 无副作用** — 仅 in-memory prompt 计算 + 返回；不写磁盘 / 不调 Kling
- **`seeds` 输入面**: 用户可控的整数数组。Backend 校验 `list[int] + len==count`；seeds 仅作为 `_variance_for(seed, gender)` 的 RNG seed，不直接进入文件路径或 shell 命令，无新 injection 面
- **JSON 响应大小**: 50 prompts × 1500 chars ≈ 75 KB；仍在合理 JSON response 范围
- **No new outbound HTTP** — preview 不调 Kling

## 不在本 follow-up 范围

- 不引入 prompt 编辑（用户只能 review；要改 prompt 须改 attrs 重新 preview）
- 不引入 per-image 不同 attrs（一 batch 仍 share base attrs）
- 不引入 prompt 历史 / 复制按钮（v2）
- 不写 backend pytest / Vitest（推迟）
- 不动 follow-up 031 的 anti-wax / camera pool
- 不动 follow-up 030 的 grid select mode / bulk delete / assign
