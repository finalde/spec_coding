# Follow-up draft 096 — 2026-05-18
Re-design character reference turntable as **7s locked-framing single-take with extraction-ready angle landings**. Rule #12.5 v9 → v10 (supersedes v9): 时长 15s → 7s, drop the dolly-in to MCU (no framing change anywhere in the shot), keep slow continuous orbit but trimmed to 180° + bookend statics. The new 7s clip is designed bottom-up around the **extract-3-views + audio** pipeline introduced in follow-up 093: every angle pick lands at IDENTICAL medium-full framing so the 3 extracted png stills (front/side/back) form a clean consistent character-sheet, suitable as image-to-video reference for downstream Kling/Seedream shots.

## Why

Two compounding problems with v9 (15s slow push-in + slow orbit):

1. **Mixed framing across extracted angles.** v9's 2-5s dolly-in pulls the camera from wide (~35mm) to medium close-up (~50mm), then 5-13s orbit reverse-dollys back to wide. So the front pick at t=1.0s is at wide framing (full body), but the side pick at t=7.0s (25% into the orbit window) lands at a framing partway between MCU and wide — head ~1/3 of frame, lower body partially cropped. The back pick at t=9.0s (50% into the orbit) is closer to wide but still mid-pull-back. The 3 extracted stills come out with **different framings** — they can't be used as a coherent 3-view character sheet for downstream image-input models, and a downstream shot prompt that needs "back-body silhouette" gets a half-body crop instead.

2. **7s is enough for the casting-grade information density the user actually needs.** v9's 15s budget was set to fit dolly-in + 360° orbit + 360° dolly-out + settle + 5 dialogue slots × ~3s each. The 360° orbit was a planning decision (right-side angle for symmetry), but in practice the body is bilaterally symmetric — left-side at 90° + back at 180° covers the unique silhouette information, right-side at 270° is redundant. Halving the orbit to 180° + collapsing the dolly phase saves ~8s with no information loss for the extract-3-views pipeline.

User instruction this turn: 「我需要 character 视频生成后能可靠地抽出 4 样东西 — 全身正面（要能看清脸）/ 全身侧面 / 全身背面 + 一段音频。7s 的视频 prompt 你帮我设计成抽取这 4 样东西最容易的形态」.

User selected (via clarifying question this turn): **locked medium-full framing throughout** — accept that v10 drops v9's dedicated face MCU window in exchange for 3 angle stills at identical framing. Face is still recognizable at medium-full (head occupies ~1/5 of frame height, ~720px tall at 9:16 1080p), just not a true close-up.

## Design — v10 7s locked-framing single-take

### Continuous single-take camera path

| Phase | Time | Camera | Framing throughout |
|---|---|---|---|
| Static front lock | 0-2s | 锁定机位 正面, no dolly, no orbit | medium-full ~40mm, 头顶到脚趾完整入画, 头部约占画面高度 1/5, 头顶 ~5% 顶边, 脚趾 ~5% 底边, 角色中线对齐画面中线 |
| Slow ccw 180° orbit | 2-6s | 顺时针 orbit at 45°/s × 4s (= 180°), no dolly, no zoom, camera distance to character locked | identical medium-full framing — only the angle changes; head still ~1/5 frame, feet still in safe zone |
| Static back lock | 6-7s | 锁定机位 背面 (= terminal angle of orbit), no further motion | identical medium-full framing, character's back to camera, full body visible |

**Critical anti-cut design rules:**
- **Single direction, no reversals.** Orbit is monotone 顺时针 throughout 2-6s. Static segments bookend the motion (0-2s and 6-7s). No mid-shot stop-and-go: the only stillness is at the very start and very end of the take. Motion transitions are velocity-handoff (orbit's initial velocity at t=2s ramps up from 0 over ~0.2s; orbit's terminal velocity at t=6s ramps down to 0 over ~0.2s — both ramps are smooth, not snap stops).
- **Locked camera distance.** No dolly, no zoom, no parallax change. The orbit radius is constant. This is the load-bearing rule for v10 — it's what makes the 3 extracted angle stills come out at IDENTICAL framing.
- **45°/s orbit speed cap preserved.** Same speed as v9, so the Kling validator hypothesis (slow continuous motion passes; only fast / direction-reversing motion is judged as cut) is unchanged.

### 7s timed beats (5 segments — same slot count as v8/v9, retimed)

```
0-1s: 静态正面全身 medium-full (锁定机位), 角色站定, 自然呼吸, 眼神看镜; 说"一"。
1-2s: 静态正面全身 medium-full (锁定机位), 角色继续站定; 说"二"。**必须在 2.0s 前完成发声**。
2-3s: 镜头开始缓慢顺时针 orbit (45°/s, 单方向, no dolly), 0° → 45°. 角色站定, 眼神可缓慢跟随; 说"三, 我是 {本角色姓名}"。
3-5s: 镜头继续缓慢 orbit, 45° → 135° (经过 90° = 左侧身); 说**{本角色 bible "标志台词" 第 1 句}** (标准声线 baseline)。
5-6s: 镜头继续缓慢 orbit, 135° → 180° (= 背面 终点); 说**{本角色 bible "标志台词" 第 2 句}** 起声 (catch + 情绪 peak)。
6-7s: 镜头锁定 180° (背面 medium-full), 角色完成 标志台词 #2 final lock; 自然定格收尾。
```

### Angle landings (extract-ready timestamps)

The `CANONICAL_VIEWS` value object in `libs/domain/value_objects/character_video__valueobject.py` (introduced by follow-up 093) currently hardcodes v9's timestamps `(1.0 front, 7.0 side, 9.0 back)`. v10 changes these to:

| Role | Timestamp | Math against v10 schedule | Framing at landing |
|---|---|---|---|
| front | t=1.0s | middle of 0-2s static front lock | medium-full, 0° angle |
| side | t=4.0s | (4.0 - 2.0) × 45°/s = 90° → 左侧身 | medium-full, 90° angle, mid-orbit |
| back | t=6.0s | (6.0 - 2.0) × 45°/s = 180° → 背面; coincides with the start of the 6-7s back lock | medium-full, 180° angle, just-arrived-at-back |
| audio | full 7s | n/a — single full-length mp3 | n/a |

**Why t=6.0s for back, not t=6.5s.** t=6.0s is the boundary between the orbit-end and the back-static-lock. Picking exactly at the boundary means the still captures the character at clean 180° with zero residual orbit blur (camera has just decelerated to 0). Picking at t=6.5s (mid-static-lock) would also work but loses 0.5s of safety margin against possible v10.1 revisions that extend the orbit through 6.0s.

**Why t=4.0s for side, not t=4.5s.** Same logic — pick at the clean integer half-second mark closest to 90°. ((4.0-2.0)×45 = 90° exactly.)

### 5-row dialogue table (v10 — same 5 slots as v8/v9, retimed shorter)

| # | 台词 | 用途 | 时段 | 情绪基调 |
|---|---|---|---|---|
| 1 | 一 | 起声 / 声线 timbre 锚点 | 0-1s | 平稳 / 中音 (byte-identical 跨角色) |
| 2 | 二 | 中段 / 节奏校准 (**2s 前结束**) | 1-2s | 平稳 / 中音 (byte-identical 跨角色) |
| 3 | 三, 我是 {角色名} | 落声 + 自我识别 + orbit 起 | 2-3s | 平稳 / 中音 |
| 4 | {标志台词 #1} | 标准声线 baseline (over orbit 0-90°) | 3-5s | character-specific (per bible 配音参考) |
| 5 | {标志台词 #2} | 情绪 peak + catch + final lock (over orbit 90°-180° + 背面 settle) | 5-7s | character-specific |

**Why slots 4 + 5 are 2s each (vs v9's 5s each).** v9 stretched these slots over the long orbit window to let body-side + back-side silhouettes register while actor mid-line. v10's 4s orbit is short enough that 2s/2s is comfortable for one bible line each — slot #4 covers the orbit through 90° (side reveal mid-line), slot #5 covers the orbit through 180° + back lock (back reveal + final emotional read).

### 2s truncate-compat — preserved unchanged

Slicing the first 2 seconds of a v10 source yields: **静态正面 medium-full + 角色说"一"+"二"** — same content as v8/v9 in the 0-2s window. Framing tightness differs from v8/v9 (v10 is medium-full ~40mm; v8/v9 were wide ~35mm), but the 2s segment remains: (a) static, (b) frontal, (c) full-body, (d) carries "一+二" voice baseline byte-identical across characters.

The downstream `ShotConcatBuilder._ffmpeg_concat` (`_CONCAT_SEGMENT_S = 2.0`) and `✂ 截到 2s` button (`_TRUNCATE_DURATION_S = 2.0`) both continue to land on frontal-full-body + voice-baseline content. **No code change needed to the truncate path.**

### 镜头 field — locked-distance single-take orbit

```
镜头: 单镜头连续运镜 single continuous take · 9:16 竖屏 · 3 阶段 (0-2s 锁定机位 正面 medium-full + 2-6s 缓慢顺时针 180° orbit ≤ 45°/s 同距离同 framing 无 dolly + 6-7s 锁定机位 背面 medium-full) · 全程匀速 / 单方向 / 无方向反转 / 无 dolly / 无 zoom / 无 cut / transition / fade · 头顶到脚趾完整入画 throughout, 头部约占画面高度 1/5 throughout
```

### Negatives (v10 — adds locked-distance bans on top of v9's slow-motion-only bans)

Same 11-item ban list as v9, plus:
- `不要 任何 dolly / zoom / 推拉镜头 (相机距角色的距离全程锁定不变, 仅旋转 — 抽帧时 front / side / back 三张 png 必须同 framing)`
- `不要 任何 framing 变化 (头部占画面高度比例锁定 ~1/5, 头顶到脚趾完整入画全程 — 抽帧时 3 个角度的 png 必须 head-size + feet-position byte-identical)`

Dropped from v9: `2-5s 缓慢推近` motion segment (no more dolly-in to MCU). Dropped from v9: `5-13s 同步缓慢 reverse-dolly 拉远` (no more reverse-dolly).

### Locked-fields list (v10)

- `时长` = 7s (was 15s in v9, was 7s in v8, was 15s in v6, was 4s in v5, was 2.9s in v4)
- `镜头` = 单镜头连续运镜 single continuous take, 3-phase locked-framing template (NEW v10 — was 5-phase mixed-framing in v9)
- `节奏` = 锁定 framing 单方向慢速 orbit 7s 单 take, 角色站定 + 自然呼吸 + 说话 (was 缓慢连续运镜 15s with dolly in v9)
- `台词 0-2s` = 一, 二 (byte-identical, v5-v10 invariant)
- `台词 2-7s` = per-character (from bible `## 标志台词或口头禅` slots #1 + #2)
- All other locked fields (场景, 光线 / 色调, 渲染样式, 比例, video-specific negatives 11-item base) byte-identical to v9.

### CANONICAL_VIEWS code change

File: `projects/ai_video_management/libs/domain/value_objects/character_video__valueobject.py`

Current (v9-anchored):
```python
CANONICAL_VIEWS: tuple[CharacterViewSpec, ...] = (
    CharacterViewSpec(1.0, "front"),
    CharacterViewSpec(7.0, "side"),
    CharacterViewSpec(9.0, "back"),
)
```

New (v10-anchored):
```python
CANONICAL_VIEWS: tuple[CharacterViewSpec, ...] = (
    CharacterViewSpec(1.0, "front"),
    CharacterViewSpec(4.0, "side"),
    CharacterViewSpec(6.0, "back"),
)
```

Module docstring updated to reference v10's 3-phase camera path instead of v9's 5-phase. The `front` constant is unchanged (t=1.0s is mid 0-2s static intro in both v9 and v10).

## Risks + retreat paths

1. **Kling validator may still reject 7s slow-orbit clips.** Same hypothesis as v9: slow continuous single-direction motion passes; only fast / direction-reversing motion is judged as cut. v10's orbit is at the same 45°/s speed cap as v9 — if v9 passes, v10 should pass. If empirical data shows v10 rejected, retreat paths:
   - (a) v10.1: drop the orbit entirely, ship 7s of static front lock (= v8 with byte-identical 0-2s + per-character 标志台词 in 2-7s, but loses side/back reference). The extract pipeline then only gets the front view + audio reliably; side/back fall back to "extract failed" status.
   - (b) v10.2: keep orbit but shorter — 0-2s static + 2-4s 90° orbit + 4-5s static at side + 5-6s 90° orbit + 6-7s static at back. This breaks the "no mid-shot stop-and-go" rule but each motion segment is < 2s so the validator may still pass. Worth trying only if v10.0 fails AND v10.1's reference loss is unacceptable.

2. **Medium-full framing may make face too small for casting decisions.** At 9:16 1080×1920, head ~1/5 frame height = ~384px tall. For casting eye-color / mouth-shape reads this is borderline. If users find face details insufficient, follow-up retreat: introduce a separate FACE-only short clip (~3s static MCU) as a second sibling file to the turntable, decoupling "body silhouette ref" from "face detail ref". v1 sticks with the single-clip 3-view design per user pick this turn.

3. **Pre-v10 mp4s already rendered in `ai_videos/mozun_chongsheng/characters/c*` won't extract cleanly with the new t=4.0s / t=6.0s timestamps.** The CANONICAL_VIEWS change is a hard cut — old v9 mp4s extracted post-fix would land side at t=4.0s (still in the dolly-in window, not at any clean angle) and back at t=6.0s (also pre-orbit-arrival in v9's schedule). Mitigation: users re-render character refs to v10 before extracting. The webapp's extract button returns the same 200 / `views=[…]` shape for old + new sources; only the visual quality of the 3 stills differs. Documented in the changelog so users know to re-render after this follow-up ships.

## Out of scope

- No `agent_team` orchestrator changes — this is a project-scoped fix to the character ref schema + the extract value object timestamps.
- No new endpoint / Cdto / route changes — follow-up 093's `POST /api/extract-character-views` route + value object plumbing already exist. v10 only changes the 3 timestamp constants inside the value object.
- No frontend UI changes — the 🖼 "提取三视图+音频" button + path-gate logic from 093 work unchanged.
- No mozun_chongsheng character md file ripple in this turn (deferred to user). Same pattern as 092 → 091 → 088: a sibling follow-up under `specs/ai_video/mozun_chongsheng/user_input/follow_ups/` would patch the 10 character `c{N}_*.md` files via a one-shot script. The script is straightforward (s/15s/7s/ + replace the timed-beats table + replace the 镜头 line + replace the negatives clauses) but the user runs it after reviewing this draft, matching the 092 + 091 + 088 + 078 convention. The follow-up does NOT auto-trigger character re-rendering — users re-render at their discretion.
- No test changes — the existing extract pipeline has integration smoke + manual UI test only (per 093 "no new tests in scope").
- No 0-2s segment change — byte-identical to v8 + v9 (still 一/二 + static frontal + medium-full framing now instead of wide). This is intentional: the 2s truncate-compat contract is preserved.

## Touch list

- `.claude/agent_refs/project/ai_video.md` rule #12.5 v9 → v10: replace v9 design rationale + 5-phase schedule + dialogue table + negatives + locked-fields block. Demote v9 to archive footer attribution alongside v8/v6/v5/v4. Add v10 design rationale + 3-phase schedule + retimed dialogue table + 2 new negatives.
- `projects/ai_video_management/libs/domain/value_objects/character_video__valueobject.py`: update `CANONICAL_VIEWS` tuple side timestamp 7.0 → 4.0, back timestamp 9.0 → 6.0; update module docstring to reference v10's 3-phase camera path.
- `specs/development/ai_video_management/user_input/revised_prompt.md`: header bump 096.
- `specs/development/ai_video_management/changelog.md`: append 096 entry with explicit "supersedes v9" + risk acknowledgment + retreat-path notes.

## Status of v9 (follow-up 092)

092 supersedes v8 (091). 096 (v10) supersedes 092 (v9). v9 stays on file as audit trail of the 15s slow-push-in-and-orbit attempt; user empirical feedback (this turn) is that the variable framing across the dolly window made the 3-view extract pipeline produce inconsistent stills — locked-distance orbit is the chosen reversal.
