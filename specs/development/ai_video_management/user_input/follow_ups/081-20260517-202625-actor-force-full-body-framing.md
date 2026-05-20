# Follow-up draft 081 — 2026-05-17
Force every actor generation to render as a **full-body head-to-toe** photo. Reinforces follow-up 080 (which added swimwear-minimal wardrobe + 11-metric body-readability list) by removing ambiguous head-focus phrasing from the prompt template and adding explicit wide-shot framing markers + harder negative guards.

## Why

User: "生成actor是，请强制生成全身从头到脚的全身照".

Even after 080 the `build_face_prompt` opening line still reads `正面全身定妆照（头部对焦）：...` and the 姿态 line ends with `头部对焦清晰`. The phrase `头部对焦` is load-bearing in the wrong direction — Kling reads it as a head-emphasis framing cue and crops to head-and-shoulders. The 画面 line saying `头部居画上 1/3` reinforces head dominance. Net effect: even with `从头顶到脚趾全身可见` in the same prompt, the model still ships portrait-cropped previews ~30-40% of the time. The user's frustration is rooted in this contradiction.

Fix: take the framing decision off the model's plate by pinning it in a leading `镜头：` line + scrubbing every word that hints at head-emphasis.

## Spec — exact changes to `libs/infrastructure/writers/actor__chinese_prompt.py`

### 1. `build_face_prompt` — opening line + pose line + 画面 line

- Line 458 (current): `f"正面全身定妆照（头部对焦）：{ethn} {gender}，{age}"`.
- Line 458 (new): `f"正面**全身**定妆照（远景 wide / long shot; 头到脚完整入框; 头部清晰仅用于身份识别, 不主导构图）：{ethn} {gender}，{age}"`.

- Line 471 (current): `"姿态：自然站立, 双臂自然下垂略外开 15°, 正脸面向镜头, 重心均匀, 头部对焦清晰"`.
- Line 471 (new): `"姿态：自然站立, 双臂自然下垂略外开 15°, 正脸面向镜头, 重心均匀, 头部清晰可辨, 双手 + 双脚 完整入框不可被裁切"`.

- Line 473 (current): `"画面：从头顶到脚趾全身可见（一帧定格不裁切）, 中性纯灰背景, 头部居画上 1/3"`.
- Line 473 (new): `"画面：9:16 竖屏 / 从头顶到脚趾完整可见 / 头部上方留 ~5% 顶边 / 双脚下方留 ~5% 底边 / 头部占画面上 1/5 (留 4/5 给身体) / 中性纯灰背景"`.

### 2. `build_body_prompt` — opening line + pose line + 画面 line

- Line 498 (current): `f"正面全身定妆照（形体对焦）：{ethn} {gender}，{age}"`.
- Line 498 (new): `f"正面**全身**定妆照（远景 wide / long shot; 头到脚完整入框; 形体对焦）：{ethn} {gender}，{age}"`.

- Body pose line (line analogous to face variant): unchanged subject, but append `双手 + 双脚 完整入框不可被裁切` to it.

- Body 画面 line (current): `"画面：从头顶到脚趾完整全身可见（一帧定格不裁切）, 中性纯灰背景, 头部居画上 1/4 形体居画中"`.
- Body 画面 line (new): `"画面：9:16 竖屏 / 从头顶到脚趾完整可见 / 头部上方留 ~5% 顶边 / 双脚下方留 ~5% 底边 / 头部占画面上 1/5 (留 4/5 给身体) / 形体居画中 / 中性纯灰背景"`.

### 3. Insert a leading `镜头：` line at the **very top** of both prompts

Right above the opening "正面**全身**定妆照..." line, prepend:

```
镜头：full-body wide shot / long shot, 9:16 竖屏构图, 头顶到脚趾完整入框, 头部上方 ~5% 顶边, 双脚下方 ~5% 底边, 严禁任何 portrait crop / head-shoulder framing / 半身像 / close-up.
```

Putting framing FIRST anchors the model's compositional decision before any subject description. Both variants get the identical 镜头 line — it's a project-output rule, not a per-variant cue.

### 4. `_NEGATIVES_ZH` — escalate to imperative + add new framing failures

Current trailing segment:

```
"裁切脚部 / 裁切大腿 / 半身构图 / 头肩特写, "
```

New (replace + extend):

```
"**严禁**：头肩特写 / 半身像 / portrait crop / close-up / 任何裁切头部 or 双手 or 双脚 or 大腿 的构图, "
"**严禁**：头部 > 整图 1/4 (头部占比过大暗示 portrait framing), "
"**严禁**：身体高度 < 整图 70% (身体占比不足暗示 framing 错误), "
"**严禁**：手部 or 脚部 越出画面边缘, "
```

The existing "宽松遮形衣物 / T 恤 / 长裤 ..." and "故意性感化姿势 / 媚态 / 内衣广告感" segments stay unchanged.

## Why putting `镜头:` first works

Kling (and most text-to-image models trained on caption-style data) treat the first tokens as compositional anchors. The current prompt opens with `正面全身定妆照（头部对焦）：东亚 女性，30 岁左右` — the model latches onto `东亚 女性 30 岁` as the subject and reaches for a generic portrait template. Leading with `镜头：full-body wide shot, 9:16 竖屏构图, 头顶到脚趾完整入框, ...` forces the framing decision into the high-attention prefix where Kling is most likely to honor it.

## Out of scope

- `_LOOK_FEATURE_BIAS_ZH` / `_LOOK_OVERLAY_ZH` / `_BODY_BIAS_BY_ARCHETYPE` / `_BIAS_WILD_PROB` — all unchanged. 080's wardrobe + 077's look-bias overlay continue to fire on top of the new framing.
- `_classify_actor_attrs` — unchanged.
- HTTP routes + JSON shapes + endpoint behaviors — byte-identical.
- API-level aspect-ratio parameter (already 9:16 via UI selector) — unchanged; the prompt-body 9:16 line is belt-and-suspenders.
- Historical generated jpgs — untouched.

## Touch list

- `projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py` — opening line + pose line + 画面 line for both `build_face_prompt` and `build_body_prompt` (4 line changes per variant = 8 line changes); insert a leading `镜头：` line in both variants (2 inserts); `_NEGATIVES_ZH` body (1 replace).
- `specs/development/ai_video_management/changelog.md` — append 081 entry.
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bump (Composed-from + Last-regenerated lines).
