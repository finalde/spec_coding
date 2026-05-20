# Follow-up draft 087 — 2026-05-17
Fix the remaining half-body output that 085's canvas fix couldn't reach. Root cause this time is **prompt engineering anti-patterns**, not API geometry. Two structural problems:

1. **Negative tokens inside the positive prompt backfire.** Diffusion models (Kling included) parse each token's semantic meaning, not its negation context. Putting `严禁 portrait`, `不要 头肩特写`, `生成失败 = portrait crop` in the positive prompt **injects portrait-related tokens into the model's attention** — the model sees `portrait` repeated across 1660 chars and gradually drifts toward what it sees most. Every 081 → 083 escalation made this worse.
2. **Kling's `negative_prompt` API field is unused.** Current submit body is `{model_name, prompt, aspect_ratio, n}` — only 4 fields. `kling-v1` accepts `negative_prompt` as a dedicated field with a separate negative attention pass. That's where every `严禁 / 不要 / 失败 / portrait / half-body / close-up / crop` token belongs.

Plus: the positive prompt is now **1660 chars** — well past Kling's effective attention budget. The actual subject description is drowning under framing-instruction text.

## Why

User: "生成的图片还是只有上半身" (post-085 follow-up).

085 fixed the canvas from 1:1 → 9:16 so Kling returns a 720×1280 image. But aspect ratio doesn't dictate composition — Kling can still frame the subject as upper-body within a 9:16 canvas if the prompt biases compositional attention that way. Our 4-anchor framing language was doing exactly that: every `严禁 portrait`, `不要 头肩`, `headshot crop = 失败` token in the positive prompt activated the portrait neurons we were trying to suppress.

## Design

### Part A — KlingProvider accepts `negative_prompt`

`projects/ai_video_management/libs/infrastructure/writers/actor__writer.py`:

```python
class KlingProvider:
    def generate(
        self,
        prompt: str,
        seed: int,
        width: int,
        height: int,
        negative_prompt: str | None = None,
    ) -> bytes:
        ...

    def _submit(
        self,
        client: httpx.Client,
        token: str,
        prompt: str,
        seed: int,
        width: int,
        height: int,
        negative_prompt: str | None = None,
    ) -> str:
        body: dict[str, object] = {
            "model_name": self._model,
            "prompt": prompt,
            "aspect_ratio": _kling_aspect_ratio(width, height),
            "n": 1,
        }
        if negative_prompt:
            body["negative_prompt"] = negative_prompt
        ...
```

Backward compatible — when `negative_prompt` is None/empty, the body shape is byte-identical to pre-087.

### Part B — `_build_prompts_for_slot` returns `(face_prompt, body_prompt, negative_prompt)`

`ActorPool._build_prompts_for_slot` now returns a 3-tuple. The negative prompt is shared between face + body (the framing failures and modesty-fallback bans apply equally to both shots). Call sites in `preview_prompts` + `generate_batch` thread it through:

```python
face_prompt, body_prompt, neg_prompt = self._build_prompts_for_slot(...)
face_bytes = self._provider.generate(face_prompt, seed, IMAGE_WIDTH, IMAGE_HEIGHT, negative_prompt=neg_prompt)
body_bytes = self._provider.generate(body_prompt, seed, IMAGE_WIDTH_BODY, IMAGE_HEIGHT_BODY, negative_prompt=neg_prompt)
```

`preview_prompts` also includes `negative_prompt` in each slot's payload so the user can see exactly what gets sent.

### Part C — Positive prompt: positive-only, shortened to ~500 chars

Refactored 4 builder variants (`build_face_prompt`, `build_body_prompt`, `build_face_prompt_with_picks`, `build_body_prompt_with_picks`). Each emits a positive-only prompt with this shape:

```
镜头：full body shot · head to toe · 9:16 vertical · long shot · 全身照
正面全身模特造型照 / fashion comp card full-body shot：{ethn} {gender}，{age}
眼睛：...
鼻子：...
嘴巴：...
眉毛：...
轮廓：...
皮肤：...
体型：...
综合描述：...
气质：...   (optional, when look has overlay)
姿态：自然站立, 双臂自然下垂略外开 15°, 正脸面向镜头, 重心均匀
服装：{wardrobe}
画面：9:16 竖屏, 头顶到脚趾完整入画, 头部 1/5 + 身体 4/5, 中性纯灰背景
摄影：{camera cue}
要求：全身模特造型照, 真实质感 8K, 形体清晰可辨（胖瘦 / 腿型 / 胸型 / 腰臀比 / 肩宽）
```

Single positive composition tag (`full body shot · head to toe · 9:16 vertical · long shot · 全身照`) replaces the entire triple-anchor framing block (lead + restate + tail). Subject + pool draws unchanged. Wardrobe unchanged. Photography pool unchanged (085's wide-angle entries stay).

Removed entirely from the positive prompt:
- `_LEADING_FRAMING_MANDATE` (3 lines worth of `严禁`-language)
- `_RESTATE_FRAMING_MANDATE` (10-waypoint anatomy + `生成失败` semantics)
- `_TAIL_FRAMING_MANDATE` (4-condition `不合格` verdict)
- The `**【强制全身】**` markdown-bold descriptor prefix (still has the new positive composition tag at line 0)
- The `**严禁**` clauses inside `_NEGATIVES_ZH`
- "宽松遮形衣物 / T 恤 / 长裤 / 长裙 / 大衣 ..." modesty-fallback list
- "故意性感化姿势 / 媚态 / 内衣广告感" glamour-drift list
- "塑料感皮肤, 蜡像感, 卡通比例, 过度磨皮 ..." photorealism negatives

All of the above move into the new `_NEGATIVE_PROMPT_ZH` constant sent via Kling's `negative_prompt` API field.

Target positive length: ~500 chars (down from 1660). Verified with smoke.

### Part D — New `_NEGATIVE_PROMPT_ZH` constant

```python
_NEGATIVE_PROMPT_ZH: str = (
    "portrait, half body, headshot, close-up, head and shoulders, "
    "head-shoulder crop, upper body only, chest up, waist up, "
    "cropped feet, cropped legs, cropped hands, cropped head, "
    "head too large, body too small, "
    "塑料感皮肤, 蜡像感, 卡通比例, 过度磨皮, 对称完美脸, "
    "AI 生成同质化脸, 影楼美化, 千篇一律的网红脸, "
    "宽松衣物, T 恤, 长裤, 长裙, 大衣, 厚外套, 多层服装, "
    "故意性感姿势, 媚态, 内衣广告, glamour pose, "
    "blurry, low quality, deformed, extra limbs, wrong proportions"
)
```

EN + ZH both — Kling-v1 is trained on bilingual captions; either side catches it. Plain comma-separated tokens (no `严禁 / 不要 / 不合格` decoration) because negative_prompt is parsed as a token list, no syntax needed.

The constant is shared across all 4 builders (returned as the 3rd tuple element from `_resolve_batch_picks` / direct builders).

## Why this should work

Diffusion model best practice (documented across SD, Midjourney, Kling, Sora):
- **Positive prompt** = the things you want, in concise positive language.
- **Negative prompt** = the things you don't want, in concise positive-form tokens (negative prompt is a separate inversion pass).
- **Never** put `not X` / `don't X` / `严禁 X` in positive — the model parses `X` and the negation is lost.
- **Keep positive prompt short** (~500-800 chars effective attention budget for kling-v1).

Our 081–083 escalation violated all three rules at once. 085 fixed the geometry. 087 fixes the prompt engineering.

## Out of scope

- Look bias (077) / minimal wardrobe (080) / batch coordination (082) / canvas + photography pool (085) — unchanged, continue to apply.
- The 4 module-level framing constants `_LEADING_FRAMING_MANDATE / _RESTATE_FRAMING_MANDATE / _TAIL_FRAMING_MANDATE` from 083 — **deleted** (superseded by single positive composition tag + dedicated negative_prompt).
- HTTP routes / JSON response shapes — `preview_prompts` response gains a `negative_prompt` field per slot (additive, backward-compat).
- Frontend ActorPoolGenerator / preview modal — preview pane will start showing the negative prompt block alongside the positive; small JSX add to render it (optional polish; if skipped, the preview just won't show negatives but generation still uses them).
- Historical JPEGs — unchanged. User regenerates with the new prompt structure.

## Touch list

- `projects/ai_video_management/libs/infrastructure/writers/actor__writer.py`:
  - `KlingProvider.generate` + `KlingProvider._submit` accept `negative_prompt: str | None = None`.
  - `ActorPool._build_prompts_for_slot` returns 3-tuple `(face_prompt, body_prompt, negative_prompt)`.
  - `ActorPool.preview_prompts` includes `negative_prompt` in each slot's response payload.
  - `ActorPool.generate_batch` + `generate_diverse_batch` pass `negative_prompt` to `self._provider.generate(...)` for both face + body calls.
- `projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py`:
  - Delete `_LEADING_FRAMING_MANDATE`, `_RESTATE_FRAMING_MANDATE`, `_TAIL_FRAMING_MANDATE` (no longer used).
  - Replace `_NEGATIVES_ZH` content with shorter positive-side `_POSITIVE_REQUIREMENTS_ZH` (just the casting-requirement positive list).
  - New `_NEGATIVE_PROMPT_ZH` constant (the negative side).
  - New `build_negatives()` helper (returns `_NEGATIVE_PROMPT_ZH`; future-proof for per-archetype/per-attrs negative tuning).
  - 4 builder variants slim down: drop the triple-anchor lines, drop `**【强制全身】**` prefix, drop the `**严禁**` block from positive. Lead with single positive composition tag.
  - 4 builder variants now return positive prompt only (negative comes from `build_negatives()`).
- `projects/ai_video_management/libs/application/dtos/actor__dto.py`:
  - `PreviewPromptQdto` gains optional `negative_prompt: str | None = None` field for visibility.
- `specs/development/ai_video_management/changelog.md` — append 087 entry.
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bump.

## Why slot 087 (not 086)

Slot 086 taken by parallel "actor-grid-assigned-filter" follow-up (the same concurrent stream that placed the is_assigned DTO comments earlier). Slot 084 was the "delete-toast-never-disappears" frontend fix. This work is unrelated to either — takes 087 to keep the audit log topic-coherent.
