# Follow-up draft 052 — 2026-05-17

Summary: Three coupled upgrades to actor pool generation: **(A) Realism** — photographer-name + camera-spec anchors per gen replace the generic studio-headshot prior that bakes in AI-stock-photo look; **(B) Diversity** — rotate STYLE-level variance (medium + framing + lighting paradigm + type-anchor + negative-prompt rotation) on top of existing feature-level variance (031's 18-pool descriptor list operates at micro-feature level, doesn't escape Kling's macro latent); **(C) Body shot** — every actor gen now produces a second 9:16 full-body casting image (heather-gray fitted tee + black athletic shorts, neutral standing pose) saved as `{ethnicity}__{gender}__{age_range}__body.jpg` alongside the existing face jpg. Same seed across face+body for identity coherence; doubles Kling cost per actor. Casting cast/ copy (follow-up 050) extends to copy body jpg too; `_cast.md` embeds both.

## 用户原话

> there are two problem with the current actor genreation, one is hte face gets genreated is too fake, so please think about a strategy to make the reuslt look like real person, the second problem is the pictures genreated out of the batch are so correlated to each other they all look them same, although I added some randomness to the prompt, but it seems not enough, help me think about a better strategy. Another thing is this is for casting, I am wondering if wes should have a full body front view casting picture, like wearing some standard uniform better in shorts so we can see the charactor body shape as well, what do you think, what do we do in a real casting?

…and after I outlined three strategies:

> all of them

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| 范围 | 三个一起做 | 用户明确 "all of them"；body shot 是最小爆炸半径，realism + diversity 必须组合（单独 realism 不解决 same-face；单独 diversity 不解决 fake-look） |
| Body-shot opt-in vs always-on | **Always-on**（每个 actor 强制双图） | 用户 framing 是 "casting"，body 是 casting 标准；opt-in 增加 UX 复杂度且默认 OFF 会让 feature 蒙尘 |
| Body wardrobe | **heather-gray fitted t-shirt + black athletic shorts + neutral athletic footwear**（gender-neutral） | 行业标准 unsigned-talent comp card；form-fitting 显身材但非裸露；leotard / swimwear 选项过 fraught，留给未来 follow-up |
| Body aspect ratio | 9:16 (576×1024) | 全身 standing pose 自然 vertical；与 character ref turntable 比例一致 |
| Body 同 seed | 是 — face + body 同 seed 同 variance | 让 face/body 看起来是"同一人的两张照片"，不是两个无关 AI 生成 |
| 失败隔离 | face 成功 + body 失败 → actor 保留（仅 errors[] 加 `body_http_failed` 等条目）；face 失败 → actor folder 直接 reap | face 是 actor 身份锚点；body 是 supplementary |
| 文件命名 | face 保持 `{eth}__{gen}__{age}.jpg`（向后兼容）；body 加 `__body` 后缀 → `{eth}__{gen}__{age}__body.jpg` | follow-up 033 命名约定不变；新 suffix 唯一 |
| Sidecar md | 加 `## 生成 prompt (body shot)` 段 + body filename 行 | reproducibility |
| `_find_actor_jpg` 排除 `__body.jpg` | 是 | face lookup 不能误返 body；regex 加 `(?!.*__body)` 否定前瞻或后端 filter `not name.endswith("__body.jpg")` |
| `actor_face_filename` | 不变（只返 face）| 调用方 (casting / list_actors) 不需要 body via 这个 API |
| 新 `actor_body_filename(actor_id)` | 是 | casting follow-up 050 copy 用 |
| Cast copy 扩展 | follow-up 050 的 `_copy_actor_face` 扩为 `_copy_actor_artifacts`；同时复制 body；cast/ 内文件: `{actor_id}_face.{ext}` + `{actor_id}_body.{ext}` | 自包含 character folder 同时支持 face + body reference |
| `_cast.md` 嵌图 | 同时嵌 face + body image markdown link | reader 视图一眼看到两张 |
| Sweep regex | `^actor_\d{4,}_(face\|body)\.[a-zA-Z0-9]+$` | 反映 follow-up 052 命名 |
| Style-level variance dimensions（新增 5 个池）| medium / framing / lighting paradigm / type-anchor / negative-rotation | 现有 17 池都是 micro-feature；这 5 池是 macro-paradigm |
| Variance 数据结构 | 把 `_variance_for(seed, gender)` 从 returns `str` 改为 returns `Variance` dataclass（含 medium / framing / lighting / type_anchor / photographer / features_text / negatives 命名 slot）| 让 face / body prompt builder 共享同一 Variance 实例 → identity coherence |
| Variance 跨 face/body 复用 | 是 — 同一 Variance 喂两个 prompt builder | face + body 都用同 type_anchor / 同 photographer / 同 medium 同 features，仅 framing + wardrobe 不同 |
| Photographer pool 含真实摄影师姓名 | 是 — Annie Leibovitz / Steve McCurry / Mary Ellen Mark / Platon / Vivian Maier / Magnum / Sebastiao Salgado / Wolfgang Tillmans | 真实 photographer style anchor 是 Kling 训练分布上 well-represented 的 distribution 锚；不引入 IP 风险（style reference 行业内通用） |
| Type anchor pool 内容 | 20+ archetypes per gender，e.g. "rugby scrum-half build", "violinist careful hands", "monastery upbringing", "ex-soldier bearing", "academic library aesthetic", "fisherman weathered look", "rock-climber lean", "chef focused gaze" | NO 真实 celebrity 名（fraught）；只用 vocation/build/upbringing archetype |
| 现有 `_VARIANCE_PHOTOREALISM` 池 | 保留 + 扩到 ~16 entries；移到 medium pool 命名空间 | 已经在做对的事（camera/film 锚定）；扩大 + 重命名 + 合并 |
| 现有 `_VARIANCE_LIGHTING` 池 | 保留 fragment-level；新加 paradigm pool 用于 macro lighting | 双层 lighting variance |
| Negative-prompt rotation | rotate 2-3 emphases per gen 从 6 池中抽 | "no plastic skin" 已变成 model de-facto target；rotation 让 negatives 不再 anchor 同一 anti-pattern |
| `_build_prompt` 拆分 | 拆为 `_build_face_prompt(attrs, variance)` + `_build_body_prompt(attrs, variance)` | face/body 两条 prompt path |
| Wardrobe 在 face shot | face shot 用 `style` enum 的 wardrobe（modern-casual / period-ancient-china / ...） | face 与原 028+033 行为一致 |
| Wardrobe 在 body shot | body shot OVERRIDE `style` enum → 固定 "neutral casting wardrobe: heather-gray fitted t-shirt, black athletic shorts, plain athletic footwear" | casting comp card 规范；不用项目 style 干扰 build 判读 |
| ActorView 显示 body | 加第二 image panel（点击切换 face/body 或 side-by-side responsive） | user 能看到 body 用于 casting decision |
| Tree walker 暴露 body_path | 是 — collapsed actor leaf 加 `body_path: str \| None` field | 让 frontend 通过 knownPaths 解析到 body jpg |
| `linkResolver.collectFilePaths` 加 body_path | 是 | ActorView 经 knownPaths 找 body |
| ActorGrid tile | 不动 — 仍只显 face | 列表识别度；body 是 detail view |
| Generator UI | 不动 | always-on 不需要 toggle |

## 功能要求

### A. Backend — `libs/infrastructure/actor_pool__writer.py`

**常量新增：**
```python
IMAGE_WIDTH_BODY: int = 576
IMAGE_HEIGHT_BODY: int = 1024
BODY_FILENAME_SUFFIX: str = "__body"
```

**Variance dataclass：**
```python
@dataclass(frozen=True)
class Variance:
    medium: str                # e.g. "shot on Canon EOS R5..."
    photographer: str          # e.g. "in the style of Annie Leibovitz"
    type_anchor: str           # e.g. "rugby scrum-half build with broken-nose"
    framing_face: str          # face-only: "candid 3/4 environmental portrait"
    lighting_paradigm: str     # e.g. "Rembrandt 45-degree key"
    features_text: str         # joined micro-feature variance (existing 17 pools)
    negatives_emphasis: str    # rotated negative tokens (2-3 picked per gen)
```

**新池：**
- `_VARIANCE_PHOTOGRAPHER_STYLE` (~10 entries)
- `_VARIANCE_TYPE_ANCHOR_MALE` (~20 entries) + `_VARIANCE_TYPE_ANCHOR_FEMALE` (~20 entries)
- `_VARIANCE_FRAMING_FACE` (~6 entries)
- `_VARIANCE_LIGHTING_PARADIGM` (~6 entries)
- `_VARIANCE_NEGATIVE_ROTATION` (~8 entries)
- 扩展 `_VARIANCE_PHOTOREALISM` (现 12 → 18+，加更多 camera/lens specifics)

**重写 `_variance_for(seed, gender) -> Variance`：**
- 用 `random.Random(seed)` 同一 RNG 保证 reproducibility
- 各池 pick 一项；features_text 沿用现有 micro-feature 抽样组装
- negatives_emphasis 从 negative rotation 池 sample 2-3 项 join

**Prompt builders：**
```python
def _build_face_prompt(attrs, variance: Variance) -> str: ...
def _build_body_prompt(attrs, variance: Variance) -> str: ...
```

Face prompt 大致结构：
```
candid unposed portrait photograph of {ethnicity} {gender}, {age_phrase}, {look},
{type_anchor},
{features_text},
{framing_face} composition,
{lighting_paradigm},
{photographer_style},
{medium_spec},
{style wardrobe per attrs.style},
natural skin texture with visible pores and subtle imperfections,
slight natural facial asymmetry,
RAW unedited photograph aesthetic,
{negatives_emphasis}
```

Body prompt 大致结构：
```
full-body standing casting photograph of {ethnicity} {gender}, {age_phrase}, {look},
{type_anchor},
{features_text},
full body visible from head to feet, neutral standing pose, arms relaxed at sides, facing camera, slight weight on left leg,
wearing heather-gray fitted t-shirt, black athletic shorts, neutral athletic footwear,
plain neutral-gray studio backdrop, even soft lighting from front,
{photographer_style},
{medium_spec},
9:16 vertical full-figure framing,
natural skin texture, real body proportions, no idealized model proportions,
RAW unedited photograph aesthetic,
{negatives_emphasis}
```

**`generate_batch` 改造：**
- 同 seed 调 `_variance_for(seed, gender)` → 单 Variance instance
- 两次 Kling 调用：
  1. face: `_provider.generate(face_prompt, seed, IMAGE_WIDTH, IMAGE_HEIGHT)` → 1:1
  2. body: `_provider.generate(body_prompt, seed, IMAGE_WIDTH_BODY, IMAGE_HEIGHT_BODY)` → 9:16
- face 失败 → reap actor folder + 记 error `http_failed` 等；body 失败 → 保留 actor folder + 记 error `body_http_failed`
- resolution preset 同时作用于两图（face: target_px × target_px；body: 维持 9:16 比例后 resize）
- 实际：body 的 resolution upscale 暂时用 简单方案 — 取 target_px 作为高，宽按 9:16 推 → max_size 控制

实现简化：v1 让 body 跳过 resolution upscale（直接保留 Kling 9:16 原生输出）；resolution preset 仅作用于 face。理由：upscale 9:16 维度推断 + Pillow resize 两路代码合并易出错；body 是 casting reference 不需要 print-quality。Sidecar 明确记录 face_resolution / body_resolution。

**Sidecar：**
```markdown
| body_image | {eth}__{gen}__{age}__body.jpg |
| body_resolution | normal |

## 生成 prompt (face shot)

```text
{face_prompt}
```

## 生成 prompt (body shot)

```text
{body_prompt}
```
```

**Helpers：**
- `_find_actor_jpg(folder)` filter 排除 `__body.jpg`：return first jpg whose name does NOT contain `BODY_FILENAME_SUFFIX`
- 新 `_find_actor_body_jpg(folder)` → first jpg matching `__body.jpg` pattern
- `actor_body_filename(actor_id) -> str | None` — 给 casting 用

### B. Backend — `libs/infrastructure/casting__writer.py` (follow-up 050 扩展)

- 改名常量 `_CAST_FACE_RE` → `_CAST_ARTIFACT_RE`，regex 改 `^actor_\d{4,}_(face|body)\.[a-zA-Z0-9]+$`
- `_copy_actor_face` → `_copy_actor_artifacts(character_folder, actor_id) -> tuple[str | None, str | None]`：copy face → `cast/{actor_id}_face.{ext}`，copy body → `cast/{actor_id}_body.{ext}`（如果存在）；返回 `(face_filename, body_filename)`
- `_build_character_link_body` 参数加 `body_copy_filename: str | None`；body markdown image link `![{actor_id} body](cast/{body_copy_filename})` 在 face image 之下显示
- `_write_character_link` 调 new artifacts copy；body 失败不阻塞
- Sweep regex 更新即可（`_CAST_ARTIFACT_RE`）

### C. Backend — `libs/infrastructure/tree__reader.py`

- 在 `_actors/{id}/` 的 collapsed leaf 中新增 `body_path` field（与 `face_path` 并列）：
  ```python
  {
    "type": "actor",
    "name": actor_id,
    "path": <md path>,
    "face_path": <face jpg path | None>,
    "body_path": <body jpg path | None>,
    "children": [],
  }
  ```
- `_first_face_image` 重命名 `_first_face_jpg` 已存在；加 `_first_body_jpg(folder)` 查 `__body.jpg`

### D. Frontend — `apps/ui/src/`

- `types.ts`：`TreeNode` 加 `body_path?: string | null`
- `lib/linkResolver.ts`：`collectFilePaths` 在 actor leaf 同时 push `node.body_path`（与 `face_path` 同 pattern）
- `components/ActorView.tsx`：
  - 加 `findBodyImage(primaryPath, knownPaths)` 类似 `findFaceImage` 但匹配 `__body.{jpg|png|webp}`
  - 在 face image panel 右侧加 body image panel（responsive: 大屏 side-by-side，小屏 stacked）
  - 加 CSS class `.actor-view-body-pane` + `.actor-view-body-image`
- 不动 `ActorGrid.tsx` / `CastingView.tsx` / `Sidebar.tsx`

### E. Spec / validation

- `final_specs/spec.md`:
  - FR-9f 重写描述：每 actor 双图（face 1:1 + body 9:16）；style-level variance 新 5 池命名 + 数量；photographer style + type anchor 描述；negative rotation；body wardrobe lock
  - FR-9g + FR-9h（cast/ copy）amend：cast/ copies face + body
  - FR-87 / FR-93（actor leaf）amend：body_path field
  - FR-95（ActorView）amend：body image panel
- `validation/acceptance_criteria.md`:
  - U3.17 (actor delete) 不动
  - U3.23 (assign chain) 扩展：cast/ 内含 `actor_NNNN_face.jpg` AND `actor_NNNN_body.jpg`；reassign sweep 两个；unassign sweep 两个
  - 新 scenario U3.24：generate batch → 每 actor folder 含 face jpg + body jpg + sidecar md（含两段 prompt）

### F. User input + audit

- `revised_prompt.md` header bump for 052
- `changelog.md` append follow-up 052
- `specs/ai_video/mozun_chongsheng/changelog.md` 平行 entry（行为契约前置；当前项目不 backfill）

## 安全 / 边界

- **Kling cost x2**：每 actor 两 Kling 调用；batch count 上限 50 不变；用户 batch 实际成本翻倍。**接受** — 用户明确 "all of them"。
- **Sandbox**：body jpg 写入路径仍在 `_actors/{id}/`，跟 face 同 folder；cast/ 同 character folder 内；无 sandbox 逃逸。
- **Resolution 不一致**：body 默认 normal（不 upscale），face 跟随用户选 `resolution` enum。Sidecar 显式分两行记录避免歧义。
- **Identity drift**：同 seed 不保证 Kling 100% 同人脸 — 文本→图像模型本身 stochastic。**接受 v1** — 这是 limitations of current model；若 future 需 100% identity lock 可走 face-swap pipeline（不在范围）。
- **Body wardrobe 不可由项目 style override**：所有 dramas / 所有 style 选择，body shot 都是 athletic uniform。**有意为之** — body shot 是 raw build judgment，戏装会污染 build perception。Future 可加 "in-character body shot" 作为独立 follow-up。
- **Negative-rotation 风险**：rotation 让每 gen 的 negative 不同，违反 follow-up 029 "所有 actors share negative" 微契约。**接受** — 029 的 negative 一致性目的是为合集剪辑 byte-identical；本 follow-up 是 *casting pool* 多样性目的，与剪辑合集目的冲突时 diversity 优先。
- **Photographer-name IP**：用真实 photographer style anchor 是 prompt engineering 通用做法；style reference 不构成 IP 侵权（不复制 specific photograph）；选取的 8 位都是 portrait/documentary 公开 attribution 群。**接受**。
- **Type anchor 不含 real celebrity**：池中只用 archetype（vocation / build / upbringing）；不写 "Brad Pitt type" 等以避免 model 输出近似真人。

## 不在本 follow-up 范围

- 不引入 face-swap / img2img 二次精修 pipeline
- 不引入 in-character body shot（戏装 body shot）— v2
- 不引入 4 张 comp card（profile / 3/4 / candid）— v2
- 不引入 Kling 之外的 image model
- 不写 backend pytest / frontend Vitest
- 不动 actor pool reap / id allocator 逻辑
- 不调整 batch count cap (50)
- 不动 audit log
- 不 backfill 现有 5 个 actor（actor_0013 ~ actor_0017）— 用户若要 backfill 重新 generate
