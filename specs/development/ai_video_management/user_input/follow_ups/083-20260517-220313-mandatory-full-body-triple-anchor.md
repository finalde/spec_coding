# Follow-up draft 083 — 2026-05-17
Reinforce the full-body head-to-toe framing as **MANDATORY** and emphasize it at the very start of every prompt — repeated at multiple positions so Kling cannot lose the constraint to attention dilution mid-prompt.

## Why

User: "请确保生成的actor照片是全身照从头到脚，请在所有prompt 提开始强调这点，而且是必须执行".

Follow-up 081 added a leading `镜头:` line at the top of every prompt. Follow-up 082 preserved that line through batch-coordinated builders. But the line currently reads as a descriptive cue, not as a hard contract:

```
镜头：full-body wide shot / long shot, 9:16 竖屏构图, 头顶到脚趾完整入框, 头部上方 ~5% 顶边, 双脚下方 ~5% 底边, 严禁任何 portrait crop / head-shoulder framing / 半身像 / close-up。
```

The `严禁` token lands at the tail of the line where attention is weakest, and the rest of the line reads as enumeration of preferences. User is reporting (implicitly) that Kling still drops the full-body intent some fraction of the time. We need:

1. **Imperative prefix** — `【强制 MANDATORY · 全身从头到脚】` at the very start of the leading line, before any framing tokens.
2. **A second, restated line** right after — different phrasing, longer enumeration of the anatomy that must be in frame (头顶含发丝 → 面部 → 颈 → 肩 → 胸 → 腰 → 臀 → 大腿 → 小腿 → 脚趾), and an explicit "failure" definition so the model treats it as a hard fail-mode.
3. **A tail reminder** right before the `避免:` line — restate the framing contract once more so the model rereads it just before applying the negatives.

Three anchor positions = redundancy. Prompt attention is leaky; one tail keyword can drift, but three tokens distributed across the prompt at prefix / middle / pre-tail positions cannot all be ignored simultaneously.

## Spec — exact text

### New leading line (replaces current 镜头: line in all 4 builder variants)

```
镜头【强制 MANDATORY · 全身从头到脚】：full-body wide shot · long shot · 9:16 竖屏 · 头顶到脚趾完整入画 · MUST show entire body from top of head to toes · 严禁 portrait / half-body / close-up / head-shoulder crop · 任何裁切均视为生成失败。
```

Key changes vs 081/082:
- `【强制 MANDATORY · 全身从头到脚】` prefix puts the MUST contract in the highest-attention position.
- `MUST show entire body from top of head to toes` English duplicate for models trained primarily on EN captions.
- `·` separator (raised dot) instead of `,` — visually distinct, fewer token-merging issues.
- `任何裁切均视为生成失败` adds explicit failure semantics.

### New second line (inserted immediately after the leading line, before the 正面 line)

```
【再次强调 · 必须执行】整张图必须显示完整全身：从 ① 头顶（含发丝）→ ② 面部 → ③ 颈 → ④ 肩 → ⑤ 胸 → ⑥ 腰 → ⑦ 臀 → ⑧ 大腿 → ⑨ 小腿 → ⑩ 脚趾, 上下 zero crop。生成任何 portrait / 半身 / 特写 / 头肩 / 腰上 / 胸上 构图 = 生成失败。
```

Enumerating the 10 anatomy waypoints binds the model to a concrete checklist, not just an abstract "full body". The numbered list further reduces drift — the model can count and see each waypoint.

### Tail reminder (insert immediately above `_NEGATIVES_ZH`, after `_CASTING_REQUIREMENTS_ZH`)

```
【强制构图 · 最后强调】整图必须 9:16 竖屏 + 头顶到脚趾 zero-crop + 头部仅占画面 1/5 + 身体占 4/5 + 头顶留 ~5% 顶边 + 脚趾下方留 ~5% 底边。如未满足任何一项均视为不合格。
```

This sits right before `_NEGATIVES_ZH` (which is the last line of the prompt) so the framing contract is the last token batch the model reads before applying constraints.

### Opening descriptor line — strengthen the literal "full-body" tag

For `build_face_prompt` + `build_face_prompt_with_picks`:

```
**【强制全身】**正面全身定妆照（远景 wide / long shot · 整图必须包含头顶到脚趾 zero-crop · 头部清晰仅用于身份识别, 不主导构图）：{ethn} {gender}，{age}
```

For `build_body_prompt` + `build_body_prompt_with_picks`:

```
**【强制全身】**正面全身定妆照（远景 wide / long shot · 整图必须包含头顶到脚趾 zero-crop · 形体对焦）：{ethn} {gender}，{age}
```

`**【强制全身】**` markdown-bold + bracketed-Chinese-imperative makes the full-body contract land in the descriptor row too — second anchor inside the high-attention prefix.

## Out of scope

- Pool / wardrobe / negative-style lines (080, 081, 082 changes) — untouched.
- `_BIAS_WILD_PROB` / look bias (074, 077) / look-led classifier (079) — untouched.
- Batch coordination (082) — `*_with_picks` builders get the same triple anchors, so batch-coordinated mode still benefits.
- HTTP routes / JSON shapes / API contracts — byte-identical (only prompt body changes).
- Diverse-mode preview/generate path — kept consistent automatically (same builders).

## Touch list

- `projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py` — 4 builder variants (`build_face_prompt`, `build_body_prompt`, `build_face_prompt_with_picks`, `build_body_prompt_with_picks`) get the new leading line + second line + tail-reminder + strengthened descriptor opening.
- `specs/development/ai_video_management/changelog.md` — append 083 entry.
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bump.
