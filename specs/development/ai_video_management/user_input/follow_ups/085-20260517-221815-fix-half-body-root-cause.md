# Follow-up draft 085 — 2026-05-17
Fix the actual root cause that follow-ups 080-083 couldn't reach with prompt-text alone: the face-shot **canvas is 1:1 (512×512)** while the prompt insists "9:16 竖屏". Text instructions cannot win against canvas geometry — a full body does not lay out top-to-bottom in a square frame, so Kling crops to chest-up no matter how many `【强制 MANDATORY】` markers we prepend.

## Why prompt-only fixes failed

User reports: the prompts produced by 081/082/083 still come back half-body. Looking at the exact prompt text the user pasted, all 4 anchors are correctly present (lead `【强制 MANDATORY · 全身从头到脚】`, restate `① 头顶 → ... → ⑩ 脚趾`, descriptor `**【强制全身】**`, tail `【强制构图 · 最后强调】`). The prompt text is doing everything it can.

Three stacked structural causes:

### 1. The canvas is square (root cause, ~70% of the issue)

`actor__writer.py` lines 92-93:
```python
IMAGE_WIDTH: int = 512
IMAGE_HEIGHT: int = 512
```

The face shot's `generate(prompt, seed, 512, 512)` tells Kling to render into a 1:1 frame. The body shot uses `IMAGE_WIDTH_BODY = 576, IMAGE_HEIGHT_BODY = 1024` (9:16) and almost certainly DOES come back full-body. The user has been looking at the face-shot JPEG which physically cannot contain a head-to-toe body.

`_kling_aspect_ratio(width, height)` (line 1126) maps the (512, 512) → "1:1" aspect_ratio param sent to Kling. The model then optimizes its sampler for square composition, which for human subjects means face/upper-body emphasis. Compositional priors locked at the API level beat any prompt-text framing markers.

### 2. "定妆照" is a beauty-headshot Chinese prior (~20%)

All 4 builders open their descriptor row with `正面全身定妆照` (or `**【强制全身】**正面全身定妆照` after 083). In Chinese photography taxonomy, **「定妆照」overwhelmingly means beauty / headshot / makeup-test shot** — it is the standard term TV/film productions use for the close-up makeup reference taken right before shooting. Models trained on Chinese photography captions have a strong prior `定妆照 → portrait crop`. The `全身` modifier in front does not override the noun-level prior.

Industry comp-card terminology that doesn't carry the headshot prior: **「模特造型照」** / **「全身模特照」** / **「fashion comp card / Z-card 全身照」**. Talent agencies use these for body-evaluation shots specifically.

### 3. The photography pool actively biases toward portrait (~10%)

`_PHOTOGRAPHY_ZH` (10 entries) — at least 5 actively pull toward portrait composition:

| # | Entry | Portrait bias |
|---|---|---|
| 1 | `佳能 EOS R5 85mm f/1.4 人像镜头` | "85mm 人像镜头" = literally "portrait lens" |
| 4 | `哈苏中画幅人像` | Explicitly "人像" / portrait |
| 5 | `柯达 Portra 400 胶片` | THE most famous portrait film, name = "Portra" |
| 9 | `尼康 Z9 105mm f/1.4` | 105mm is portrait focal length |
| 10 | `宝丽来 SX-70 拍立得` | SX-70 produces square format → reinforces 1:1 |

The current prompt the user pasted picked entry #5 (Portra 400). Of course Kling produced a portrait — the user explicitly asked for portrait film.

## Spec

### Part A — canvas geometry (fixes root cause)

`projects/ai_video_management/libs/infrastructure/writers/actor__writer.py`:

```python
IMAGE_WIDTH: int = 720       # was 512
IMAGE_HEIGHT: int = 1280     # was 512
IMAGE_WIDTH_BODY: int = 720  # was 576 — align both shots at the same 9:16 res
IMAGE_HEIGHT_BODY: int = 1280  # was 1024
```

Both face + body shots are now 720×1280 (9:16 portrait canvas, full-body capable). 720×1280 chosen because it matches short-form-vertical-video standards (Douyin / TikTok / YouTube Shorts native 720p vertical) which is the downstream use case for these actor reference photos.

`_kling_aspect_ratio(720, 1280)` will map → "9:16" sent to Kling.

### Part B — `_resize_jpeg` must be aspect-preserving

Current (line 1615-1628):

```python
img = img.resize((target_px, target_px), Image.LANCZOS)  # forced square
```

This squashes a 720×1280 source into 2048×2048 for "2k" mode → broken. New:

```python
src_w, src_h = img.size
if src_w >= src_h:
    new_w, new_h = target_px, round(target_px * src_h / src_w)
else:
    new_h, new_w = target_px, round(target_px * src_w / src_h)
img = img.resize((new_w, new_h), Image.LANCZOS)
```

Scales the **longest edge** to `target_px`, preserves source aspect. 720×1280 + "2k" → 1152×2048. 720×1280 + "4k" → 2304×4096. Docstring updated to reflect new behavior; the "Kling returns ~1024×1024 natively for 1:1 aspect" note becomes "Kling returns the requested width × height; resolution presets scale the longest edge".

### Part C — replace "定妆照" + rewrite photography pool

`projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py`:

**4 builder descriptor rows** (`build_face_prompt`, `build_body_prompt`, `build_face_prompt_with_picks`, `build_body_prompt_with_picks`) — current line 2:

```
**【强制全身】**正面全身定妆照（远景 wide / long shot · 整图必须包含头顶到脚趾 zero-crop · ...）：...
```

New:

```
**【强制全身】**正面全身模特造型照 / fashion comp card full-body shot（远景 wide / long shot · 整图必须包含头顶到脚趾 zero-crop · ...）：...
```

`_CASTING_REQUIREMENTS_ZH` — drop "定妆 comp-card 标准照", use "全身模特造型 / fashion editorial full-body shot":

```python
_CASTING_REQUIREMENTS_ZH: str = (
    "要求：全身模特造型照 / fashion editorial full-body shot, 从头到脚完整可见"
    "（头顶到脚趾, 一帧定格不裁切）, 中性纯灰背景, 自然光均匀曝光, 真实质感 "
    "8K 高清, 真实毛孔, 形体清晰可辨（胖瘦 / 腿长短 / 腿型直弯 / 大腿内外侧线条 / "
    "胸大胸小 / 胸型 / 肩宽 / 腰线 / 腰臀比 / 臀型 / 上身肌肉线条）"
)
```

**`_PHOTOGRAPHY_ZH`** — 10 new entries, all wide/standard lenses + full-body cue, no portrait films:

```python
_PHOTOGRAPHY_ZH: tuple[str, ...] = (
    "佳能 EOS R5 35mm 全身广角镜头, fashion editorial 真实质感",
    "索尼 A7 IV 24mm 全身镜头, 模特造型构图, 真实皮肤微纹理",
    "富士 X-T5 28mm 全身, 自然胶片颗粒感, 真实人物",
    "哈苏 X2D 50mm 全身大画幅, 油画般层次, 真实毛孔",
    "柯达 Ektar 100 胶片 35mm 全身, 鲜艳真实色彩, 自然光",
    "Cinestill 50D 35mm 全身, 写实电影感, 自然光",
    "徕卡 SL2 28mm 全身抓拍, 自然环境光, 真实质感",
    "iPhone 15 Pro 0.5x 超广角 全身街拍, 真实生活感",
    "尼康 Z9 35mm 全身镜头, 超自然渲染, 不平滑皮肤",
    "富士 GFX 100S 32mm 全身中画幅, 化学色偏, 真诚记录",
)
```

Every entry now:
- Names a wide-to-standard focal length (24mm / 28mm / 32mm / 35mm / 50mm — never 85mm or 105mm).
- Includes "全身" so the photography cue itself reinforces full-body intent.
- Drops portrait-named films (Portra, SX-70) for landscape/fashion films (Ektar, Cinestill 50D, Ektar 100).
- Keeps the realism / texture cues that 074/077/080 depend on for non-AI-face look.

## Why this works

Canvas geometry is a hard constraint at the API layer — Kling cannot return a square image when the request is 720×1280. With a 9:16 canvas + a prompt that says "head to toe" + a photography cue that says "35mm full body", every layer of the request now agrees. Today they disagree (canvas says square / prompt says full-body / photography says portrait lens) and the model resolves the conflict by averaging toward the strongest prior — which has been portrait.

## Out of scope

- Frontend `ActorPoolGenerator.tsx` / `ActorGrid` / `ActorView` — no change. The JPEG dimensions change but the file format + filename convention + sidecar shape stay the same; the React components display whatever pixel ratio comes back.
- HTTP routes / JSON shapes / endpoint behaviors — byte-identical.
- Look bias (077) / minimal wardrobe (080) / batch coordination (082) / triple-anchor framing (083) — all unchanged, continue to apply on the new 9:16 canvas.
- Historical generated JPEGs (1:1 squares) — left as-is. User re-generates whoever needs the new framing.
- The face-vs-body shot distinction itself — kept for now (both 9:16; face emphasizes face within the full body, body emphasizes proportions). Future follow-up could collapse to single shot if dual generation becomes unnecessary cost.

## Touch list

- `projects/ai_video_management/libs/infrastructure/writers/actor__writer.py` — `IMAGE_WIDTH / IMAGE_HEIGHT / IMAGE_WIDTH_BODY / IMAGE_HEIGHT_BODY` constants + `_resize_jpeg` aspect-preserving rewrite + docstring updates.
- `projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py` — 4 builder descriptor rows (定妆照 → 全身模特造型照) + `_CASTING_REQUIREMENTS_ZH` + `_PHOTOGRAPHY_ZH` (10 entries).
- `specs/development/ai_video_management/changelog.md` — append 084 entry.
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bump.
