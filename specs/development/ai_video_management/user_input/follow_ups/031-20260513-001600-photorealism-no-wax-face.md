# Follow-up draft 031 — 2026-05-13

修 Kling 输出 "AI 蜡像脸" 观感。当前 follow-up 029 的 17 池 variance 让脸够不同，但还是普遍"AI 风" — 过度光滑 / 完美对称 / 雕像质感。解决思路两层叠加:

1. **Base prompt 加 anti-AI/anti-wax 永久注入**: 现在的 base 是 "portrait headshot of {ethn} {gender}, {age}, {look}, ..., photorealistic, sharp focus, 8k"。"8k" + "sharp focus" 实际上**鼓励**AI/雕像感（过度清晰 + 无机理）。改为 "candid unposed photograph, natural skin texture with visible pores, slight natural asymmetry, RAW photo, unretouched"。
2. **新增 photorealism variance pool**: 每张图片再额外抽 2-3 个真实摄影 cue（相机型号 / 镜头 / 胶卷感 / 自然光场景 / 业余拍摄感）。
3. **删除/替换误导关键词**: "8k" / "photorealistic" / "sharp focus" 单独使用反而让 Kling 走超清雕像路径；改为 "photorealistic candid documentary photo, medium-format film, soft skin micro-texture"。

## 用户原话

> 请确保kling生成的人像是真人，目前生成的太假了，一看就是AI生成的，有的甚至像是蜡像脸

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| Base prompt 改写 | 移除 "photorealistic / sharp focus / 8k" 三连，替换为 candid + natural texture + RAW 系列 | 经验：模型 fine-tune 时 "photorealistic 8k sharp focus" 关联 AI/CG 训练数据；改用真实摄影术语 |
| 加 anti-wax 永久注入 | 在 base prompt 末尾固定追加 "natural skin texture with visible pores, slight facial asymmetry, candid unposed expression, RAW unedited photograph aesthetic, no plastic skin, no waxy smoothness, no symmetrical perfection" | 显式 negative 描述（Kling 不支持 negative_prompt 字段，但 positive 提及 "no X" 有缓解效果） |
| 新增 photorealism pool | `_VARIANCE_PHOTOREALISM` 含 12 个真实摄影 cue（Canon 5D + 85mm f/1.4，Sony A7 + 50mm，Fujifilm X-T5，medium-format Hasselblad，Kodak Portra 400 grain，Cinestill film，iPhone candid，etc.） | 每张图片不同 camera/film 让 batch 看起来像多个摄影师拍的，不是同一 AI 出 |
| 替换 follow-up 029 photography pool 还是新增？ | **新增 pool 并行**，原 `_VARIANCE_PHOTOGRAPHY` 不动 | 029 的 photography pool 是 style ("editorial / film grain")；031 是 camera/film 具体型号，正交 |
| Variance 整体字数 | 保持 ≥ 1000 chars（不变） | 029 contract 不变；只是 fragment 内容更"真" |
| 影响范围 | 仅 backend `actor_pool.py`；frontend 零改动 | UX 不变；用户感知改进在生成结果 |
| Retro-fit 已存在的 actors | 不重新生成 | 老 sidecar 保留；新生成立刻生效 |

## 功能要求

### Backend

**`projects/ai_video_management/backend/libs/actor_pool.py`**:

1. 改写 `_build_prompt(attrs, variance="")`:
   - 移除 `"photorealistic"`, `"sharp focus"`, `"8k"` 三个 fragment
   - 在 base parts 末尾固定追加新的 anti-AI/anti-wax 句子
2. 新增 `_VARIANCE_PHOTOREALISM: tuple[str, ...]`，~12 items 含真实相机 / 镜头 / 胶卷感
3. 修改 `_variance_for(seed, gender)`:
   - 加 `rng.sample(_VARIANCE_PHOTOREALISM, k=min(2, ...))` 抽样
   - 总长仍 ≥ 1000 chars（length-guard 不动）

### Frontend

零改动。用户感知通过 backend prompt 改写自动生效。

### Spec / validation

- `final_specs/spec.md` FR-9f: 更新 prompt 描述 — 删除 "8k" 等 + 提及 anti-wax 永久注入 + 第 18 池 `_VARIANCE_PHOTOREALISM`
- `validation/security.md`: 无新 carve-out — variance 仍 server-side hardcoded
- `validation/acceptance_criteria.md` U3.15: 加 "sidecar prompt 不含 'photorealistic' / 'sharp focus' / '8k' 单独短语" + "含 'natural skin texture' / 'candid' / 'RAW' 等 anti-wax keywords" 断言

## 安全 / 边界

- **No new surface** — 仅 backend prompt 改写 + 一个新硬编码 pool
- **Backwards compat** — `_build_prompt` 签名不变；调用方零影响
- **Test fixture** — 现有 7 boot-smoke 测试不依赖 prompt 内容；零回归

## 不在本 follow-up 范围

- 不引入 Kling negative_prompt 字段（确认 Kling text-to-image 是否支持后才能引入；当前未确认）
- 不引入 model_name 切换（kling-v1 vs kling-v1-5）
- 不重写老 sidecar（不 retro-fit）
- 不写 backend pytest / Vitest
- 不动 follow-up 029 的 17 池或 length-guard 机制
- 不动 follow-up 030 的 grid / select mode
