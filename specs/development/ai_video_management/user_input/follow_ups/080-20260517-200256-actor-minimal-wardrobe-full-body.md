# Follow-up draft 080 — 2026-05-17
Strengthen the actor-generation wardrobe so each generated actor photo is a true industry comp-card / model-portfolio body-evaluation shot — head-to-toe framing maintained, with **as minimal wardrobe as possible** so that body fat / leg length / leg straightness or bow / breast size / shoulder-hip ratio are all visually verifiable from a single photo.

## Why

User: "生成actor时，请确保生成的actor是全身照，从头到脚，我要看到身材，要知道腿长还是腿短，退直的还是弯的，胸大还是胸小，所以穿越少越好".

The previous comp-card wardrobe introduced in the orphan follow-up 076 (tank top + booty shorts level) is tight but still covers torso + most thighs, leaving leg-straightness and ribcage / waist proportions partially ambiguous. The new wardrobe is a step closer to industry swimwear-standard comp-card (sports bikini / 赤膊 + 高叉短) — the same convention talent agencies use for fit-cast body reads.

## Spec — exact changes to `libs/infrastructure/writers/actor__chinese_prompt.py`

### 1. `_casting_wardrobe(gender_zh)` rewrite (lines 400-412)

The function still returns a single locked outfit per gender (not derived from `attrs.style`) so the cast photo stays a body-shape reference, not a costume preview.

**Female (`女性`)** — new:

```
"运动比基尼上装（窄肩带细带 + 紧贴胸型 + 完全露肩 / 露上胸 / 露背 / 露腹 / 露腰）+ 高叉紧身运动比基尼下装（高腰线露髋骨 + 高开叉露大腿全长 / 显腿型 / 腿长短 / 腿型直弯 / 大腿内外侧线条 / 臀型）+ 赤足"
```

**Male (`男性`)** — new:

```
"上身赤膊（露胸肌 / 腹肌 / 肋骨线 / 肩宽 / 腰线 / 腰臀比）+ 紧身贴身运动短裤（高开叉短款露大腿全长 / 显腿型 / 腿长短 / 腿型直弯 / 大腿内外侧线条 / 臀型）+ 赤足"
```

Notes for the implementation:
- Keep the function single-responsibility — gender-only dispatch, no `attrs.style` plumbing.
- Keep `_GENDER_ZH` mapping unchanged (`"male" → "男性"`, `"female" → "女性"`).
- Update the docstring: replace "Per follow-up 076" → "Per follow-ups 076 + 079" so the lineage stays auditable. Brief one-line addition: "079 升级 tank/booty-shorts 到 industry swimwear-standard 以最大化 body-shape visibility".

### 2. `_CASTING_REQUIREMENTS_ZH` (lines 415-419) — tighten the explicit visibility list

Replace the body-feature list to enumerate every metric the user named:

```
"要求：全身定妆 comp-card 标准照, 从头到脚完整可见（头顶到脚趾, 一帧定格不裁切）, "
"中性纯灰背景, 自然光均匀曝光, 真实质感 8K 高清, 真实毛孔, "
"形体清晰可辨（胖瘦 / 腿长短 / 腿型直弯 / 大腿内外侧线条 / 胸大胸小 / 胸型 / 肩宽 / 腰线 / 腰臀比 / 臀型 / 上身肌肉线条）"
```

Three deltas: (a) "头顶到脚踝" → "头顶到脚趾, 一帧定格不裁切" — `脚踝` allowed framing to crop the feet, `脚趾` enforces toe inclusion; (b) "腿型直弯" expanded with "大腿内外侧线条"; (c) "胸型" expanded with explicit "胸大胸小" (which is the user's literal phrasing) plus "上身肌肉线条" for the male赤膊 case.

### 3. Framing line inside `build_face_prompt` (line ~455) + `build_body_prompt` (line ~495)

Currently:
- face: `"画面：从头顶到脚踝全身可见, 中性纯灰背景, 头部居画上 1/3"`
- body: `"画面：从头顶到脚踝完整全身可见, 中性纯灰背景, 头部居画上 1/4 形体居画中"`

Update both `脚踝` → `脚趾` for consistency with the requirements line. Otherwise unchanged.

### 4. `_NEGATIVES_ZH` (lines 394-397) — add the framing-failure cases

Append three negatives so the model can't degrade the body read:

```
"避免：塑料感皮肤, 蜡像感, 卡通比例, 过度磨皮, "
"对称完美脸, AI 生成同质化脸, 影楼美化, 千篇一律的网红脸, "
"裁切脚部 / 裁切大腿 / 半身构图 / 头肩特写, "
"宽松遮形衣物 / T 恤 / 长裤 / 长裙 / 大衣 / 任何遮挡躯干或大腿轮廓的服装, "
"故意性感化姿势 / 媚态 / 内衣广告感 (本图是 body-reference comp-card, 中性站姿即可)"
)
```

The final negative is load-bearing — minimal wardrobe must serve body-shape evaluation, not glamour. The pose stays the existing `自然站立, 双臂自然下垂略外开 15°, 正脸面向镜头, 重心均匀` (face variant) / `... 双腿略分开半肩宽显腿型` (body variant); no changes there.

## Out of scope

- `_classify_actor_attrs` fallback / age range distribution — unchanged.
- `_LOOK_FEATURE_BIAS_ZH` / archetype bias (follow-up 077) — unchanged. Look-driven 五官 + 综合描述 + 气质 overlay continue to fire on top of the new wardrobe.
- Per-shot character video prompts (`ai_videos/{drama}/characters/*.md`) — unchanged. Character bibles describe **in-story costume**, not casting comp-card; the two pipelines are intentionally distinct.
- The face/body variant split (`build_face_prompt` vs `build_body_prompt`) and their seed-sharing identity anchor — unchanged. Both variants get the new wardrobe through the same `_casting_wardrobe` call.
- HTTP routes + JSON shapes — unchanged. Preview pane simply renders the new prompt text.

## Touch list

- `projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py` — `_casting_wardrobe` body, `_CASTING_REQUIREMENTS_ZH` body, framing line in `build_face_prompt` + `build_body_prompt`, `_NEGATIVES_ZH` body.
- `specs/development/ai_video_management/changelog.md` — append follow-up 079 entry.
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bump (Composed-from + Last-regenerated lines).
