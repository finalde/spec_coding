# Follow-up draft 099 — 2026-05-19
Rule #12.5 v10.2 → v11 — **simplified prompt language, camera motion described ONCE only**. Same 5-phase schedule as v10.2 (3 static landings at 0°/90°/180° + 2 short transitions) and same `CANONICAL_VIEWS` timestamps `(1.0, 3.5, 6.0)` — no code change. The change is purely in how the prompt talks to the video model: drop the multi-field redundancy (镜头 + 动作 + 节奏 + 负向 all repeating the motion path with different jargon), put motion in the 动作 timed beats only, use plain Chinese instead of "motion bridge" / "static landing" / "locked-framing" jargon.

## Why

User report after re-rendering with v10.2 prompt:
> "the camera did not move as you intended in the charactor prompt, I think kling got confused, you need to tell it in a more simple way and only once in the prompt. currently the it shart to turn around to side view at only about 5s."

Diagnosis: v10.2's prompt has the camera motion path described in **4 different fields** with different vocabularies:
- `镜头:` line — enumerates all 5 phases with "motion bridge" / "锁定机位" / "no dolly / no zoom" jargon
- `动作:` beats — 5 timed entries each repeating the phase description
- `节奏:` line — "锁定 framing 5-phase 单 take, 3 static landings + 2 motion bridges"
- `负向:` 14-item list — contains qualifiers like "1s motion bridge 必须精确终止在 90° (t=3s) / 180° (t=5s)" + "3-4s 段 + 5-7s 段必须完全静止"

When a video model sees the same motion described 4 times with different framings, it doesn't trust any single specification — it averages, and tends to under-commit to motion. Kling specifically is biased toward static front-facing content in short clips, so when the prompt is ambiguous about timing it defaults to "keep the character static for most of the clip, do brief motion near the end." User observation that motion starts at ~5s (3 seconds past v10.2 spec's 2s start) is consistent with the model averaging across the 4 redundant descriptions and discounting the precise timing.

## Design — v11 simplified prompt

Same schedule as v10.2. Same `CANONICAL_VIEWS` timestamps. **Only the prompt rendering changes.**

### Field consolidation

| Field | v10.2 content | v11 content |
|---|---|---|
| 镜头 | 5-phase enumeration with motion path + framing + lens specs all mixed | Framing + lens specs ONLY — no motion path |
| 动作 | 5 timed beats each repeating "锁定机位 X medium-full" / "motion bridge 缓慢顺时针 orbit X° → Y°" jargon | 5 timed beats in plain Chinese — single source of truth for motion |
| 节奏 | "锁定 framing 5-phase 单 take, 3 static landings (0-2s / 3-4s / 5-7s) + 2 motion bridges (2-3s / 4-5s 各 1s)" — REPEATS the motion path | "单 take 7s, 角色站立不动只说话, 镜头按动作 timed beats 旋转 + 停顿" — minimal, no path repetition |
| 负向 | 14 items with qualifier paragraphs (`不要 motion 跨越目标角度 (1s motion bridge 必须精确终止在 90° (t=3s)...)`, `不要 静态段内继续微调机位 (3-4s 段 + 5-7s 段必须完全静止...)`, etc.) | 10 simple bans, no qualifier paragraphs — `不要 dolly / zoom / 距离变化 / framing 变化 / 角色转身 / 走动 / cut / transition / fade / 超过 7s` |

### New v11 prompt body schema

```text
{中文名} · {身份} — 角色 reference 7s 单 take

角色: {一句话锁定 byte-identical} + {体型 / 发型 / 服装 / 道具 inline 展开 per rule 12.4-A 无参考图分支}

场景: 中性灰 #808080 摄影棚 cyc wall 无缝背景, 地面同灰, 无家具.

镜头: 单 take 7s, 9:16 竖屏, medium-full ~40mm framing 全程不变 (头部约画面高度 1/5, 头顶到脚趾完整入画, 双脚距画面底缘约 5% 安全余量, 相机距角色距离不变 no dolly no zoom).

动作 (7s timed beats):
  - 0-2s: 镜头正面拍角色 medium-full. 角色站定, 自然呼吸, 眼神看镜, 说"一", "二". **必须在 2.0s 前说完**.
  - 2-3s: 镜头围绕角色顺时针绕 90° 到角色左侧身. 角色保持站立不动只呼吸.
  - 3-4s: 镜头停在左侧身角度不动. 角色说"三, 我是 {本角色姓名}".
  - 4-5s: 镜头继续顺时针绕 90° 到角色背面. 角色保持站立不动只呼吸.
  - 5-7s: 镜头停在背面角度不动. 角色说"{本角色 bible 标志台词 #1}", "{本角色 bible 标志台词 #2}".

台词 / 字幕: 内嵌唇形对齐音频 (中文). 前 2s 必须包含 "一" + "二" 完整发声 (下游 2s 截取契约); 2-7s 台词从角色 bible `## 标志台词或口头禅` 段前两句逐字复制.
  1. "一" (0-1s)
  2. "二" (1-2s, **2s 前结束**)
  3. "三, 我是 {角色名}" (2-3s, 自我识别 + 镜头转向)
  4. {标志台词 #1} (3-5s, 标准声线 baseline)
  5. {标志台词 #2} (5-7s, 情绪 peak + final lock)

光线 / 色调: 三点布光 — 5500K key + 4500K fill + 7000K rim; 灰背景中性, 无戏剧化色温偏移; {角色专属光晕, 如魔气/仙气, 可选}.

节奏: 单 take 7s, 角色站立不动只说话, 镜头按 动作 timed beats 旋转 + 停顿.

渲染样式: 影视级真人写实 + cinematic + 4K HDR + 真实皮肤布料质感.

比例: 9:16

时长: 7s

负向: {项目级负向 from style_guide} / {角色专属负向 from bible} / 不要 dolly / 不要 zoom / 不要 距离变化 / 不要 framing 变化 / 不要 角色转身 / 不要 角色走动 / 不要 cut / 不要 transition / 不要 fade / 不要 超过 7s.
```

Key wording principles:
- **Plain Chinese only.** No "motion bridge", no "static landing", no "single continuous take", no "锁定机位" (model interprets this as "don't move ever"). Use 「镜头围绕角色绕」 + 「镜头停在 X 角度不动」.
- **Motion lives in 动作 only.** 镜头 = framing/lens specs (locked distance, no dolly/zoom). 节奏 = single sentence, no path repetition. 负向 = simple ban list, no qualifier paragraphs.
- **Dialogue + camera motion can co-occur in 动作 beats.** Beat 3-4s says "镜头停在 X" AND "角色说 Y" — both happen together, no separate split.
- **Critical timing markers kept inline.** "必须在 2.0s 前说完" stays in beat 0-2s; 标志台词 references stay in beats 5-7s. These are loadbearing for downstream truncate + voice baseline contracts.

### Hypothesis

With camera motion described ONCE and in plain Chinese, the model should follow the 5 timed beats more literally. v10.2's failure mode (motion delayed to ~5s) was the model averaging across 4 conflicting descriptions; v11 gives it ONE description to follow.

### Risk acknowledgment

- **The model may still under-commit to motion.** If v11 also has motion starting late (≥3s), the issue isn't prompt redundancy but a fundamental bias in the model toward static front-facing content. Retreat options:
  - **v12**: shift the schedule earlier, accepting a tighter 0-1s static front (loses 0-2s truncate-compat byte-identical contract). 0-1s static + 1-3s motion + 3-4s static side + 4-5s motion + 5-7s static back. CANONICAL_VIEWS would change to (0.5, 3.5, 6.0).
  - **v13 multi-clip**: render front / side / back as 3 separate clips and concatenate at file-system level. Most expensive but bypasses the model's single-clip timing bias entirely. Each clip is a static shot — no motion required.
- **Bare-bones negatives may let unwanted defaults slip through.** v10.2 had explicit "不要 motion 跨越目标角度" preventing the model from rotating past the spec angle. v11 drops this. If models over-rotate (e.g., past 180° to 270°), retreat is to add back ONE qualifier (`不要 镜头超过 180°`) without re-inflating the entire negatives section.

### CANONICAL_VIEWS code change

**None.** v11 keeps v10.2's `(1.0, 3.5, 6.0)` timestamps. The schedule is the same; only the prompt wording changes. Front pick at mid 0-2s static (t=1.0s), side pick at mid 3-4s static (t=3.5s), back pick at mid 5-7s static back hold (t=6.0s).

## Out of scope

- No frontend changes — 🖼 button (097) + path-gate + api wire-up unchanged.
- No backend changes — `CharacterViewExtractor` and the route both unchanged.
- No value-object code change — `CANONICAL_VIEWS` constants stay `(1.0, 3.5, 6.0)`.
- No frontend UI tooltip rewording (the SiblingMedia tile button's tooltip still says "v9" — separate cleanup).

## Touch list

- `.claude/agent_refs/project/ai_video.md` rule #12.5 v10.2 → v11: rewrite the active prompt body code block (镜头 / 动作 / 节奏 / 负向 + minor others); v10.2 demoted to archive footer with rationale "为什么 v10.2 verbose prompt 不再生效 — model 在 4 字段重复描述下 confuses + 把 motion 全部 squeeze 到 ~5s 之后". Update file schema description (sibling-file comment) for v11 simpler form.
- `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md`: 10 files patched via one-shot script — replace 镜头 line + 动作 block + 节奏 line + 负向 line + 文件说明 + h1 heading + prompt-block title with simpler v11 form. Keep character-specific 角色 line + dialogue contents byte-identical.
- `specs/development/ai_video_management/user_input/revised_prompt.md`: header bump 099.
- `specs/development/ai_video_management/changelog.md`: append 099 entry.
- `specs/ai_video/mozun_chongsheng/user_input/follow_ups/028-…`: sibling follow-up (v10.2 → v11 ripple).
- `specs/ai_video/mozun_chongsheng/user_input/follow_ups/027-…`: add SUPERSEDED tag pointing to 028.
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md`: header bump 028.
- `specs/ai_video/mozun_chongsheng/changelog.md`: append 028 entry.

## User-side action

1. Re-render the 10 character mp4s at 7s with v11 prompt. v10 + v10.2 renders are invalidated.
2. Upload one v11 mp4 to Kling — empirical test whether simpler prompt language fixes the timing.
3. Click 🖼 — check whether motion actually starts at t=2s now (not t=5s).
4. If motion is still delayed, report back — escalate to v12 (shift schedule earlier, break 0-2s truncate-compat) or v13 (multi-clip).
