# Follow-up draft 029 — 2026-05-13

两个 batch generation 增强:

1. **大幅扩张 variance**: 当前 follow-up 027 的 5 池 × 1 pick = 5 fragment ≈ 80-150 字符 的 variance 仍然让一 batch 内的图片偏趋同。用户要求 **每张图片注入 ≥1000 字符** random 形容词；example 标签覆盖 "小鲜肉" / "秀气" / "俊朗" / "邪魅" 这类整体气质轴；外加面部各部位 / 肤色 / 肤质 / 眼型 / 发型 / 表情 / 光照 / 摄影风格 等子轴。**全部 server-side hardcoded English fragments**（用户给的中文 label 是意图描述，prompt 用 English 与 base 一致避免 Kling 重点散乱）。
2. **像素分辨率选择器**: 当前 hardcoded 512×512 (映射到 Kling aspect_ratio 1:1，Kling 实际返回 ~1024px native)。用户要 UI 提供 选项；user interactive 选择 **普通 / 2K / 4K**，default 普通 (Kling native，无 resize)；2K → Pillow Lanczos upscale 到 2048×2048；4K → 4096×4096。

## 用户原话

> 当生成一个batch的时候，你需要加一些random的形容词到prompt里，然后再发给kling api，比如同一个batch里，图片1是小鲜肉，图片二是秀气长相，图片三是俊朗长相，图片4是邪魅长相等等，你至少要加1000字以上的random形容词，然后在发给kling api。 然后生成的时候应该让我选在像素，default可以不用2k，4k 普通画质就可以

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| Variance 总字符数 | **≥ 1000 chars** per image | 用户 explicit 要求 |
| 池数 | **17 池** (含 gender-aware look archetype + 面部 6 部位 + 发 3 子轴 + 肤 2 子轴 + 表情 + 氛围 + 光照 + 摄影 + photography style) | 覆盖 face 生成的所有可控维度 |
| 每池规模 | 10-14 items, 30-50 chars 每项 | 池足够大避免一 batch 内重复；item 够长达到字符量 |
| 池语言 | **English** | 与 base prompt 一致；Kling 英文 prompt 解析最稳；用户的中文 label 翻译到 English 等价词 (小鲜肉 → "fresh-faced youthful idol" 等) |
| Variance 抽样策略 | 每池 1-3 picks (`rng.sample` 或 `rng.choices`)，总 ~30-40 fragments | 保证 ≥1000 chars 且每张都不同 |
| Random 种子 | 仍复用 actor seed (follow-up 027) | 同 seed 重现同 variance；不同 seed 自然变化 |
| 1000-char 保底 | `_variance_for` 实现内 assert `len(result) >= 1000`，达不到则补 photography quality 短语 | 不允许 silently 出短 prompt |
| Resolution UI | dropdown "画质" with 普通 / 2K / 4K | 用户 explicit interactive 选择 |
| Resolution default | **普通 (Kling native，无 resize)** | 用户原话 "default可以不用2k，4k 普通画质就可以" |
| Resolution mapping | 普通 → 不 resize；2K → 2048×2048 (Pillow `LANCZOS` upscale)；4K → 4096×4096 | upscale 是显式 user choice；模型本身只输出 ~1024px 真细节，更大主要是显示/存档需求 |
| Pillow dep | 加 `pillow>=10.0` 到 `backend/requirements.txt` | 标准成熟图像库，无替代 |
| Resolution 后端实现 | 在 `generate_batch` 内，收到 Kling bytes 后用 `PIL.Image.open(BytesIO(...))` → `resize((target, target), Image.LANCZOS)` → `save(buf, "JPEG", quality=95)` → 写文件 | 集中在 ActorPool 内；不动 KlingProvider（Kling 仍 hardcoded 接收 1:1 aspect） |
| Resolution enum 校验 | 后端 + 前端两层 enum {"normal", "2k", "4k"}；无效 → 400 invalid_resolution | 与现有 attribute 校验对齐 |
| Sidecar 记录 | sidecar `actor_NNNN.md` 加 `resolution` 字段 + 长 variance prompt 全文 | 用户能从 md 看具体生成参数复现 |
| Aspect ratio | 保持 1:1 (face headshot 默认) | 用户没要求 aspect；focus 在 pixel resolution |

## 功能要求

### Backend

**`projects/ai_video_management/backend/requirements.txt`**: 加 `pillow>=10.0`

**`projects/ai_video_management/backend/libs/actor_pool.py`**:

1. **替换 5 个变异池为 17 个池**:
   - `_LOOK_ARCHETYPES_MALE` / `_LOOK_ARCHETYPES_FEMALE` (gender-aware 整体气质轴 - 涵盖 小鲜肉 / 秀气 / 俊朗 / 邪魅 / 沉稳 / 学者 / 顽皮 等 12 item)
   - `_FACE_FEATURES_MALE` / `_FACE_FEATURES_FEMALE` (10-12 item, 详细面部特征)
   - `_JAWLINE_DESCRIPTORS` (8-10 item)
   - `_CHEEKBONE_DESCRIPTORS` (8-10 item)
   - `_BROW_DESCRIPTORS` (10 item)
   - `_NOSE_DESCRIPTORS` (10 item)
   - `_LIPS_DESCRIPTORS` (10 item)
   - `_EYE_DESCRIPTORS` (扩 12-14 item)
   - `_HAIR_LENGTH` (8 item)
   - `_HAIR_STYLE` (10 item)
   - `_HAIR_COLOR` (10 item)
   - `_SKIN_TONE` (扩 10 item)
   - `_SKIN_TEXTURE` (8 item)
   - `_EXPRESSION_DESCRIPTORS` (12 item)
   - `_MOOD_DESCRIPTORS` (10 item)
   - `_LIGHTING_DESCRIPTORS` (10 item)
   - `_PHOTOGRAPHY_DESCRIPTORS` (10 item)

2. **重写 `_variance_for(seed, gender) -> str`**:
   - `rng = random.Random(seed)`
   - 每个池 `rng.sample` 抽 2-3 个独立 fragment（look archetype 抽 1，其他面部部位抽 1-2，氛围/光照/摄影抽 1-2）
   - 用 ", " join
   - 实现末尾 assert `len(result) >= 1000`，未达则 append `_PHOTOGRAPHY_DESCRIPTORS` 整池 `random` 短语补足

3. **加 `Resolution` 常量 + 校验**:
   - `_RESOLUTION_PRESETS: dict[str, int | None] = {"normal": None, "2k": 2048, "4k": 4096}`
   - 新 exception `InvalidResolution(InvalidAttribute)` (复用 `InvalidAttribute` 父类映射 400)
   - 实际上直接 `raise InvalidAttribute("resolution=...")` 即可，避免新 exception class
   - `generate_batch(attrs, count, resolution="normal")` 校验 `resolution in _RESOLUTION_PRESETS`

4. **修改 `generate_batch`**:
   - 接收 `resolution: str = "normal"` 参数
   - 在 provider.generate 返回 bytes 后:
     - 若 `_RESOLUTION_PRESETS[resolution] is not None`:
       - `from io import BytesIO; from PIL import Image`
       - `img = Image.open(BytesIO(image_bytes)).convert("RGB")`
       - `target_px = _RESOLUTION_PRESETS[resolution]`
       - `img = img.resize((target_px, target_px), Image.LANCZOS)`
       - `buf = BytesIO(); img.save(buf, "JPEG", quality=95); image_bytes = buf.getvalue()`
     - 写 `jpg_path.write_bytes(image_bytes)`
   - Pillow import 放在 module top-level（与 random 一起）

5. **`_build_sidecar`** 加 `resolution` 字段到属性表

**`projects/ai_video_management/backend/libs/api.py`**:

- `GenerateActorsBody.resolution: str = "normal"`
- `actors_generate` endpoint 把 `body.resolution` 传给 `generate_batch`

### Frontend

**`projects/ai_video_management/frontend/src/api.ts`**:

- `GenerateActorsRequest` 加 `resolution: string` (optional with default in caller)
- `ATTR_OPTIONS` 加 `resolution: ["normal", "2k", "4k"]` (用于 dropdown)

**`projects/ai_video_management/frontend/src/components/ActorPoolGenerator.tsx`**:

- 加 `useState<string>("normal")` for resolution
- 加 dropdown "画质" sibling 于现有 6 个属性 dropdown
- onSubmit 传 `resolution` 到 generateActors

### Spec / validation

- `final_specs/spec.md` FR-9f: body 加 `resolution` field；描述 Pillow resize 流程；variance 总长 1000+ chars
- `final_specs/spec.md` FR-86: 加 `resolution` enum `{"normal", "2k", "4k"}`
- `final_specs/spec.md` FR-88: ActorPoolGenerator 加 resolution dropdown
- `validation/security.md` carve-out #7: 加 Pillow 二进制处理 (受信任 Kling 来源 + JPEG-only 不解析任意格式 + 5MB cap 仍前置限制原图);  注明 Pillow 是新增 dep
- `validation/acceptance_criteria.md` U3.15: 加 variance ≥1000 chars 断言 + resolution = 2k 输出 jpg 是 2048×2048 + 无效 resolution → 400

## 安全 / 边界

- **No new HTTP surface** — 仍单 endpoint `POST /api/actors/generate`，仅 body 扩字段
- **No new user-controlled prompt** — variance pools 服务端硬编码；resolution 来自 enum；同 follow-up 027 立场
- **Pillow 处理面**: 解码 Kling 返回的 JPEG (受信任来源 + SSRF-vetted CDN + 5MB cap，原始 bytes 已通过 Kling provider 的 hardening)；Pillow 解码失败 → raise，归入 `errors[]`；不解析任意 user-upload 图像，所以 Pillow CVE 主要 surface (恶意 PNG/SVG 触发) 不直接暴露
- **Upscale 不是真细节**: 文档化在 sidecar — `resolution=4k` 但 Kling 原始 ~1024px，结果只是 Lanczos 插值，不是 native 4K
- **磁盘开销**: 4K JPEG ~ 1-3 MB；50 batch × 4K ≈ 100MB；用户自行管理

## 不在本 follow-up 范围

- 不动 aspect ratio (保持 1:1)；竖屏 / 横屏 actor 是 v2
- 不引入 image format 选择 (PNG/WEBP)；保持 JPEG
- 不引入"原图同尺寸 download" 选项（用户能从 jpg 文件直接拿）
- 不引入 negative_prompt
- 不动 follow-up 027 的 race-safe 分配 / 9-way 并发
- 不动 follow-up 028 的 grid view (resolution 影响每张 jpg 大小，grid thumbnail 仍懒加载)
- 不引入 batch-level resolution mix (一 batch 内统一 resolution)
- 不写 backend pytest / Vitest (推迟)
- 不引入 quality slider (JPEG quality 仍 hardcoded 95)
