# Follow-up draft 091 — 2026-05-18
> **SUPERSEDED by follow-up 092 (rule #12.5 v9, slow-push-in + slow-orbit 15s)** — user rejected v8's trade-off (static frontal full-body sacrifices face close-up + 侧身/背面 silhouette). 092 reverses the static-camera lockdown with a slow-motion hypothesis (≤ 45°/s orbit, no direction reversals) about Kling's validator. Kept on file as audit trail of the static-camera retreat that 092 reverses; v8 also remains the documented fallback if v9 fails the validator.

Rebuild the character reference turntable around Kling's upload-validator constraint: **single shot, no cuts or transitions, clear character throughout**. Locked-camera 7s frontal shot; character speaks the entire 7s; no orbit, no push-in, no pull-out. Supersedes 090 (v7) which was never implemented because its 360° orbit + camera-direction reversals would have been rejected the same way 088 (v6) was.

## Why

Kling's actual feedback on uploaded character ref videos (post-088 v6 15s casting reel, post any earlier multi-camera-move attempt):

> the current video contains cuts or transitions, and no clear, complete character is detected, please upload a single shot clear character video

Three things are happening:
1. Kling's content validator interprets **any aggressive camera move** (fast orbit, push-in, pull-out, direction reversal) as a "cut" or "transition", even when it's a single continuous take.
2. The fast 0-2s 360° orbit (in every version v5/v6/v7) **blurs the character** so Kling's character-detector can't lock onto a clear, identifiable subject.
3. Kling's character-reference upload expects a single-shot clean read of the subject — same convention as casting headshot / standing portrait video, not a "casting reel" with multiple framings.

Every prior version (v5 4s / v6 15s / v7 7s) violates rule #1 in the 0-2s segment alone (fast 360° = "transition" to the validator), and v6 + v7 also violate rule #1 in the tail (push-in / pull-out / direction change). They all violate rule #2 (fast spin blurs character).

The only way to make Kling accept the upload is **drop the multi-angle ambition entirely** and ship a single-shot static-camera reference. This sacrifices the 0-2s 360° silhouette pass that v5 introduced for truncate-compat, but per the user's clarification this turn ("Static frontal full-body + 一/二 recommended"), the 2s truncate output still yields a useful frontal voice + identity reference even without the silhouette catalog.

## Design — v8 static-camera 7s

### Single fixed camera

- **Position**: frontal full-body, ~35mm wide, centered subject. Camera locked for the full 7 seconds. No orbit, no push, no pull, no pan, no tilt.
- **Subject**: stays in place. Slight natural breathing + micro head turns + speaking lip movement only. No turn-in-place. No walking.
- **Framing**: 9:16 portrait canvas, head-to-toe in frame, head ~1/6 of frame height, feet near bottom with ~5% safety margin (per 081/083 framing language, which is still valid for the still-camera shot).

### 7s timed beats (5 segments)

```
0-1s: 静态正面全身远景, 角色站定, 自然呼吸, 眼神看镜; 说"一"。
1-2s: 同机位同构图 (无任何镜头变化); 角色说"二"。**必须在 2.0s 前完成发声**。
2-3s: 同机位同构图; 角色说"三, 我是 {本角色姓名}"。
3-5s: 同机位同构图; 角色说**{本角色 bible "标志台词" 第 1 句}** (演员标准声线 baseline)。
5-7s: 同机位同构图; 角色说**{本角色 bible "标志台词" 第 2 句}** (catch + 情绪 peak + 标志特征点 final lock); 0.3s 自然定格收尾。
```

Every segment starts with "同机位同构图" — explicit anti-cut language. The camera literally does nothing for 7 seconds.

### 5-row dialogue table

| # | 台词 | 用途 | 时段 | 情绪基调 |
|---|---|---|---|---|
| 1 | 一 | 起声 / 声线 timbre 锚点 | 0-1s | 平稳 / 中音 (byte-identical 跨角色) |
| 2 | 二 | 中段 / 节奏校准 (**2s 前结束**) | 1-2s | 平稳 / 中音 (byte-identical 跨角色) |
| 3 | 三, 我是 {角色名} | 落声 + 自我识别 | 2-3s | 平稳 / 中音 |
| 4 | {标志台词 #1} | 标准声线 baseline | 3-5s | character-specific (per bible 配音参考) |
| 5 | {标志台词 #2} | 情绪 peak + catch + final lock | 5-7s | character-specific |

### 2s truncate-compat — preserved but reshaped

Slicing the first 2 seconds of a v8 source yields: **静态正面全身远景 + 角色说"一"+"二"**. Lost: the 360° silhouette pass (side / back / other side). Kept: the character's voice baseline + clean frontal full-body identity + 2 spoken syllables.

This is a deliberate downgrade of the truncate output. The user explicitly approved the tradeoff this turn ("Static frontal full-body + 一/二") because:
- Kling reference upload was already broken with the 360° → no working pipeline regardless.
- The static 2s clip is still a useful baseline for the shot-char concat reel (`_CONCAT_SEGMENT_S = 2.0`) — every character now contributes 2s of "frontal full-body + voice baseline" to the concat, which is still a per-character cue card.

### 镜头 field — explicitly single-shot

```
镜头: 静态单镜头 single take · 锁定机位 locked camera · 正面全身远景 (~35mm wide) · 9:16 竖屏 · 7 秒内无任何镜头运动 (no orbit / no push-in / no pull-out / no pan / no tilt / no zoom)
```

This positive declaration is the strongest signal to Kling's renderer to NOT add camera moves. The negatives below reinforce.

### Negatives (Kling-validator-aware)

Append / rewrite the v6 negatives to:

- `不要 超过 7s (reference 上传硬上限 v8)`
- `不要 任何镜头运动 (no orbit / push-in / pull-out / pan / tilt / zoom / dolly / handheld / motion blur)`
- `不要 任何 cut / transition / scene change / fade / dissolve / cross-fade — 全程单镜头单 take`
- `不要 角色转身 / 走动 / 大幅度肢体动作 (保 Kling character detector 锁定主体)`
- `不要 把 "一" / "二" 延后到 2s 之后 (下游 2s 截取依赖此契约)`
- `不要 在 0-2s 段加入额外台词 (保 byte-identical 跨角色 truncate 输出)`
- `不要 让任何台词 over-emote 至失真 (声线 timbre baseline 优先)`

Drop from v6: `不要 跳过任何 6 个 camera-move 段` (no camera moves at all in v8).
Drop from v6: `不要 镜头回切倒退 (要单向 360°)` (no 360° at all in v8).

### Locked-fields list

- `时长` = 7s (byte-identical)
- `镜头` = 静态单镜头 single take, locked frontal full-body (byte-identical, structural)
- `台词 0-2s` = 一, 二 (byte-identical)
- `台词 2-7s` = per-character (from bible `## 标志台词或口头禅` slots #1 + #2)
- All other locked fields (场景, 光线 / 色调, 节奏 = 缓慢 7s 内角色仅自然呼吸 + 说话, 渲染样式, 比例, video-specific negatives) byte-identical.

## Out of scope

- ai_video_management webapp code — **no code change**. 2s trim path still slices first 2s. Concat reel still works (per-character contribution is now 2s of static frontal + voice).
- Existing rendered mp4s (4s v5 / 15s v6 / older). User re-renders to v8 7s static at their discretion.
- Scene reference rule #12.10 v3 (15s walk-through) — orthogonal, unchanged. (Scenes have no character-detector constraint; movement is fine.)
- Shot prompts (rule #12.6) — only reference `{ref_cN_xxx}` placeholders, no embedded duration text.
- Future: if Kling later supports multi-shot character references, we can re-introduce the v6 casting-reel design. v8 is the conservative spec that just works.

## Touch list

- `.claude/agent_refs/project/ai_video.md` rule #12.5 v6 → v8 (skip v7) — bump duration 15s → 7s, replace 7-segment beats with 5-segment static-camera beats, replace 镜头 field with single-shot declaration, replace 8-row table with 5-row, swap negatives (drop multi-camera-move + 360° bans, add no-camera-motion + no-cut + no-turn-in-place bans), update locked-fields list (镜头 now byte-identical structural), update 节奏 (= 缓慢 7s 角色仅自然呼吸 + 说话), append footer attribution `rev — follow-up 091 (v8 supersedes v7 which was specced but never shipped due to Kling validator feedback) …`.
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bump 091.
- `specs/development/ai_video_management/changelog.md` — append 091 entry (with explicit "supersedes 090" note).
- `specs/ai_video/mozun_chongsheng/user_input/follow_ups/024-{ts}-character-ref-7s-static-camera-kling-compat.md` — sibling follow-up (supersedes 023).
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — header bump.
- `specs/ai_video/mozun_chongsheng/changelog.md` — entry (supersedes 023 note).
- `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md` — patch via one-shot script: v6 7-segment dynamics → v8 5-segment static, 8-row table → 5-row, 时长 15s → 7s, 镜头 line single-shot declaration, negatives swap. Each character's existing bible 标志台词 #1 and #2 (the same lines plugged in by 088) stay in slots 4 + 5.

## Status of 090 + 023 (v7)

Both files marked "SUPERSEDED before implementation" at the top. Kept on file as audit trail of the design iteration that led to v8. Do NOT patch character files from 090's spec.
