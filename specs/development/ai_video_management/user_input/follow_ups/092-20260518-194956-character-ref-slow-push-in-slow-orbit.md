# Follow-up draft 092 — 2026-05-18
Re-introduce multi-angle character reference: **slow push-in + slow 360° orbit**, single continuous take, 15s. User-directed reversal of 091's v8 static-camera lockdown — the v8 truncate-output downgrade (lost the side/back reference) is no longer acceptable. Hypothesis: Kling's "cut/transition" rejection was triggered by *speed*, not motion itself; v5/v6 spun the camera at ~720°/s in the 0-2s segment (a half-second whip-around 360°), which both registered as a "cut" to the validator and motion-blurred the subject. v9 keeps the camera moving the entire shot but at ≤ 45°/s for orbit and gentle dolly speed for the push-in. Single-take continuous motion (no stops, no direction reversals) — the validator's "single shot" contract is reasserted via *continuity*, not via stillness.

## Why this turn

User instruction: 「镜头由远到近，要能拍清楚脸部，而且缓慢旋转能看到侧身和背面」.

091 (v8) was a defensive concession to Kling's upload validator after v6 15s casting reel uploads were rejected. v8 sacrificed the entire 0-2s 360° silhouette pass + every camera move 2-7s for a flat static frontal full-body. The user explicitly accepts that trade-off was over-correcting — a static frontal carries no body-side or back reference, and the only face information is at the same full-body framing distance, so the face is never clearly captured for casting-detail purposes.

v9 explicitly reverses three v8 design points:
1. **Re-enable camera motion** — slow push-in 2-5s + slow 360° orbit 5-13s, plus a continuous-pull-back tail 13-15s.
2. **Force a face close-up window** — at ~5s the camera reaches medium close-up (~50mm framing), face fills upper half of frame, this is the casting-grade face read.
3. **Re-introduce 360° body reveal** — slow orbit (45°/s, vs v5's 720°/s) shows 正面 → 左侧身 → 背面 → 右侧身 → 回正面 for body-shape + costume back-side capture.

**Risk acknowledgment.** v9 is a *hypothesis* about Kling's validator: slow continuous motion will pass where v5/v6's fast direction-reversing motion failed. v5/v6 had: 0.5s 360° (≈720°/s), plus push-in/pull-out reversals. v9 has: 5s 360° (≈72°/s during the orbit phase, or 45°/s averaged across 2-13s if we include the linked push-in), single direction, no reversal. **If Kling still rejects v9 uploads**, the user has two retreat paths: (a) reintroduce v8's static frontal for the upload-required ref clip while keeping v9 as a separate planning/preview clip; (b) compress motion further (e.g., 0-2s static + 2-5s slow push-in only, drop the 360°, ship as v9.1).

## Design — v9 slow-orbit + slow-push-in 15s

### Continuous single-take camera path

| Phase | Time | Motion | Framing at end of phase |
|---|---|---|---|
| Static intro | 0-2s | 锁定机位 (camera locked) | 正面全身远景 ~35mm wide, 头到脚完整入画 |
| Slow push-in | 2-5s | dolly-in 缓慢推近, no orbit, no pan | 面部 medium close-up ~50mm, 面部占画面上 1/3, 头肩入画 |
| Slow orbit + slow pull-back (combined) | 5-13s | continuous 顺时针 360° orbit + concurrent slow pull-back to wide | 正面全身远景 ~35mm wide (returns to starting framing after one full revolution) |
| Settle | 13-15s | 锁定机位 (camera locked again, same as 0-2s framing) | 正面全身远景, 0.3s 自然定格收尾 |

**Critical anti-cut design rules:**
- **No direction reversals.** Push-in is monotone 2-5s, orbit is monotone 顺时针 5-13s, pull-back is monotone 5-13s. The camera never "snaps back" — every transition between phases is smooth (push-in's terminal velocity hands off to orbit's initial velocity; orbit + pull-back end at the same wide frame as 0-2s started; settle phase is a gentle stop, not a snap).
- **Slow speeds throughout.** Orbit at ≤ 45°/s (5x slower than v5's blink-360°). Push-in: 35mm → 50mm equivalent over 3 seconds (gentle dolly, not a punch). Pull-back: 50mm → 35mm over 8s (very gentle, hidden within orbit motion).
- **Single continuous take.** No fades, no dissolves, no scene changes. The camera is always observing the same character in the same studio space.

### 15s timed beats (5 segments)

```
0-2s: 静态正面全身远景, 锁定机位, 角色站定, 自然呼吸, 眼神看镜; 说"一"+"二"。**必须在 2.0s 前完成发声**。
2-5s: 镜头缓慢推近 (slow dolly-in) — 从全身远景 → 面部 medium close-up; 角色头部对焦, 眼神跟随镜头; 说"三, 我是 {本角色姓名}"。
5-13s: 镜头一边缓慢顺时针环绕角色一圈 360° (≤ 45°/s), 一边缓慢拉远回到全身远景。揭示正面 → 左侧身 → 背面 → 右侧身 → 回正面。角色站定不动, 仅自然呼吸 + 头部微动; 说**{本角色 bible "标志台词" 第 1 句}** (3-5s 段标准声线 baseline 起声, 续到 8-10s 完成)。
10-13s: (镜头仍在环绕末段) 说**{本角色 bible "标志台词" 第 2 句}** (catch + 情绪 peak 起声)。
13-15s: 镜头回正面全身远景锁定 (back to 0-2s framing), 角色完成 标志台词 #2 final lock; 0.3s 自然定格收尾。
```

### 5-row dialogue table (same slots as v8, retimed)

| # | 台词 | 用途 | 时段 | 情绪基调 |
|---|---|---|---|---|
| 1 | 一 | 起声 / 声线 timbre 锚点 | 0-1s | 平稳 / 中音 (byte-identical 跨角色) |
| 2 | 二 | 中段 / 节奏校准 (**2s 前结束**) | 1-2s | 平稳 / 中音 (byte-identical 跨角色) |
| 3 | 三, 我是 {角色名} | 落声 + 自我识别 + 面部 close-up read | 2-5s | 平稳 / 中音 |
| 4 | {标志台词 #1} | 标准声线 baseline (over slow orbit) | 5-10s | character-specific (per bible 配音参考) |
| 5 | {标志台词 #2} | 情绪 peak + catch + final lock (orbit tail + settle) | 10-15s | character-specific |

**Why slots 4 + 5 are stretched.** v8 had slot #4 in 3-5s and #5 in 5-7s (2s each). v9 gives them 5s each (5-10s, 10-15s) — more breathing room for the slow-orbit shot to register the body-side and back-side body shapes while the actor is mid-line, so each 标志台词 reads as continuous performance rather than a sliced clip.

### 2s truncate-compat — preserved unchanged

Slicing the first 2 seconds of a v9 source yields: **静态正面全身远景 + 角色说"一"+"二"** — *identical* output to v8's 2s slice. The downstream `ShotConcatBuilder._ffmpeg_concat` `_CONCAT_SEGMENT_S = 2.0` trim + `✂ 截到 2s` button (`_TRUNCATE_DURATION_S = 2.0`) both continue to land on frontal-full-body + voice-baseline content, byte-identical to v8.

This means **no code change to ai_video_management.** The 2s contract is what the webapp depends on; the 2-15s rest of the clip is upload material that webapp doesn't touch.

### 镜头 field — explicit single-take continuous motion

```
镜头: 单镜头连续运镜 single continuous take · 9:16 竖屏 · 4 段连续运动 (2-5s 缓慢推近 + 5-13s 缓慢顺时针 360° 环绕 + 同段 5-13s 缓慢拉远 + 13-15s 锁定收尾) · 全程匀速 / 无方向反转 / 无定格中断 / 无 cut / transition / fade
```

The positive declaration enumerates the moves and explicitly calls out "no reversal / no stop-and-go" — the design lessons learned from v6's rejection.

### Negatives (Kling-validator-aware, v9 update)

Replace v8's "no motion" negatives with v9's "slow continuous motion only" negatives:

- `不要 超过 15s (reference 上传上限 v9)`
- `不要 快速运镜 (no fast orbit / fast push / fast pull / fast pan / whip-pan / snap-zoom — 旋转速度 ≤ 45°/s, 推拉镜头 ≥ 3s 完成)`
- `不要 任何方向反转 (no orbit reversal / no push-in-then-pull-out reversal / no pan back-and-forth — 全程单方向)`
- `不要 任何定格中断 (no freeze frame mid-shot / no stop-and-go — 镜头连续运动直到 13s, 仅最后 0.3s 自然定格收尾)`
- `不要 任何 cut / transition / scene change / fade / dissolve / cross-fade — 全程单镜头单 take`
- `不要 角色转身 / 走动 / 大幅度肢体动作 (角色站定让镜头围绕, 而非角色自身旋转)`
- `不要 把 "一" / "二" 延后到 2s 之后 (下游 2s 截取依赖此契约)`
- `不要 在 0-2s 段加入额外台词 (保 byte-identical 跨角色 truncate 输出)`
- `不要 让任何台词 over-emote 至失真 (声线 timbre baseline 优先)`
- `不要 旋转过程中角色脸部 motion blur (慢速 orbit + 角色站定 → 角色清晰 / character detector 可锁定)`

Dropped from v8: `不要 任何镜头运动` (v9 reintroduces controlled motion).
Dropped from v8: `不要 角色转身` is kept (still want camera-orbit, not character-turn-in-place).

### Locked-fields list (v9)

- `时长` = 15s (byte-identical)
- `镜头` = 单镜头连续运镜 single continuous take, 5-phase template (byte-identical, structural)
- `节奏` = 缓慢连续运镜 15s 内角色仅站定 + 自然呼吸 + 说话, 镜头匀速运动 (byte-identical, structural)
- `台词 0-2s` = 一, 二 (byte-identical)
- `台词 2-15s` = per-character (from bible `## 标志台词或口头禅` slots #1 + #2)
- All other locked fields (场景, 光线 / 色调, 渲染样式, 比例, video-specific negatives) byte-identical.

## Out of scope

- ai_video_management webapp code — **no code change**. 2s trim path slices the same byte-identical first 2s; concat reel still works.
- Existing rendered mp4s (v8 7s static, v6 15s casting reel, older). User re-renders to v9 15s at their discretion.
- Scene reference rule #12.10 v3 (15s walk-through) — orthogonal, unchanged.
- Shot prompts (rule #12.6) — only reference `{ref_cN_xxx}` placeholders, no embedded duration text.
- Future: if Kling rejects v9 uploads, retreat to v9.1 (drop the orbit phase, keep push-in only) or back to v8. v9 is the user-directed reversal of v8's over-correction; empirical validation pending after first 10 character renders.

## Touch list

- `.claude/agent_refs/project/ai_video.md` rule #12.5 v8 → v9 — bump 时长 7s → 15s, replace 5-segment static beats with 5-segment slow-motion beats, replace 镜头 field with single-take continuous-motion declaration, retime dialogue table slot #3 (2-3s → 2-5s) + #4 (3-5s → 5-10s) + #5 (5-7s → 10-15s), swap negatives (drop no-camera-motion + no-cut bans, add slow-motion-only + no-reversal + no-stop-and-go bans), update 节奏 (= 缓慢连续运镜), append footer attribution `rev — follow-up 092 (v9 supersedes v8, user-directed reversal: re-enable slow camera motion to recover side/back reference + face close-up that v8 sacrificed) …`.
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bump 092.
- `specs/development/ai_video_management/changelog.md` — append 092 entry (with explicit "supersedes 091" note + risk acknowledgment).
- `specs/ai_video/mozun_chongsheng/user_input/follow_ups/025-20260518-194956-character-ref-15s-slow-orbit.md` — sibling follow-up (supersedes 024's v8 patch; new v9 patch).
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — header bump.
- `specs/ai_video/mozun_chongsheng/changelog.md` — entry.
- `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md` — patch via one-shot script (parallel to 091's `/tmp/patch_chars_v8.py`): v8 5-segment static → v9 5-segment slow-motion, 时长 7s → 15s, 镜头 line static-declaration → continuous-motion-declaration, negatives swap, 节奏 line update. Each character's existing bible 标志台词 #1 + #2 (the same lines plugged in by 088 → 091) stay in slots #4 + #5 with retimed slots (now 5-10s / 10-15s). User runs the script after reviewing this draft.

## Status of v8 (follow-up 091)

091 marked SUPERSEDED at top with a one-line note pointing to 092. Kept on file as audit trail of the static-camera retreat that v9 reverses. The Kling validator concern from 091 is *not refuted* — it's reinterpreted: speed (not motion) was the cause. v9 tests the slow-motion hypothesis. If empirical evidence supports v8 (i.e., v9 also gets rejected), 091 stays the de-facto active spec and v9 is recorded as a tried-and-failed iteration.
