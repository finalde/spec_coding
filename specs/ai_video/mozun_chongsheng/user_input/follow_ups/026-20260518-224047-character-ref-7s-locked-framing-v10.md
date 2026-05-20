# Follow-up draft 026 — 2026-05-18
> **SUPERSEDED by follow-up 027 (rule #12.5 v10.2, 7s locked-framing 5-phase single-take with 3 static landings + 2 motion bridges, cross-project ripple from ai_video_management 098)** — user empirical test of v10 renders found the model under-rotates v10's single 4s continuous orbit (~22°/s actual vs 45°/s spec) leaving side/back picks in motion segments at wrong angles. v10.2 reverses v10's single-orbit design by introducing explicit static landings at 90° and 180° so each pick lands at a guaranteed-static moment. Kept on file as audit trail of v10's empirically-broken time-×-speed contract.

Apply the new v10 7s locked-framing single-take schema (cross-cutting rule `.claude/agent_refs/project/ai_video.md` rule #12.5 v9 → v10, originated from ai_video_management follow-up 096) to all 10 mozun_chongsheng character files. Supersedes 025 (v9 15s slow-push-in + slow-orbit, never applied — its patch script was deferred and never run; the character md files were still at v8 when 026's script ran, so 026 patches directly from v8 → v10 in one pass).

## Why

v9 (092 / mozun_chongsheng 025) introduced a 15s slow-push-in + slow-orbit + reverse-dolly camera path to recover the face MCU + multi-angle silhouette that v8 had sacrificed. But after follow-up 093 went live (ai_video_management's 「抽 3 视图 + 音频」 pipeline that extracts front / side / back png + full mp3 from a character turntable mp4), the v9 design exposed a structural flaw: v9's dolly-in and reverse-dolly vary head-size-in-frame across the take, so the 3 angle picks land at inconsistent framings — front at wide, side at mid-pull-back (head ~1/3 frame, lower body partially cropped), back near-wide but still mid-pull-back. The 3 extracted pngs cannot be used as a coherent 3-view character sheet for downstream image-to-video reference.

v10 (096) reverses v9's mixed-framing design: **locked medium-full framing throughout** (no dolly, no zoom — camera only rotates), **180° orbit instead of 360°** (body is bilaterally symmetric so right-side is redundant with left-side), **7s instead of 15s** (the 5s saved by halving the orbit + dropping the dolly-in / reverse-dolly windows). The face-MCU window from v9 is sacrificed in favor of consistent extraction framing — user explicitly accepted this trade-off in 096's clarifying question.

User selection summary (096): "locked medium-full throughout" — 3 extracted stills at identical framing (head ~1/5 frame, full body, toe-safe), face still recognizable at medium-full distance (~360-400px head height at 9:16 1080p), suitable as image-to-video reference. Sacrifices v9's dedicated face MCU read but recovers a coherent 3-view character sheet.

## Status of 025 (v9 patch)

025 (v9 15s slow-orbit) was specced but its patch script was never run — character md files at the time this turn started were still at v8 (091/024). 026 patches directly v8 → v10 in one pass, bypassing v9 entirely. 025 stays on file as audit trail of the abandoned v9 attempt. The 024 → 025 → 026 sequence is: v8 applied → v9 specced but never applied → v10 applied (this follow-up).

024 + 025 both marked SUPERSEDED at top with a note pointing to 026.

## Per-character dialogue (slots #4 + #5 — preserved unchanged across v8 → v9 → v10)

Dialogue lines are character bible content, unchanged across all 3 versions. Only the time windows and the surrounding stage-direction wording changed.

| Char | 3-5s (台词 #1, baseline over orbit 0-90°) | 5-7s (台词 #2, catch + peak + final lock over orbit 90°-180° + 背面 settle) |
|---|---|---|
| c1_沧冥 | 当年你们怎么对我，今日我便十倍奉还 | 本尊从不解释，只清算 |
| c2_叶无尘 | 进来吧，喝口热汤——我记着 | 叮——任务发布 |
| c3_苏璃月 | 若道不在此处，此剑便指此处 | 我拜的不是宫，是道 |
| c4_柳红袖 | 进来吧，喝口热汤 | 酒坛比仙气重要 |
| c5_苓夭夭 | 脉里有古伤，不是凡人能受的 | 丹入腹，命在天 |
| c6_白月清 | 璃月，为师所行皆为道 | 天道无亲，惟修者自度 |
| c7_赵焚天 | 好兵器，要凡人血淬 | 天下第一铸 |
| c8_方鼎元 | 魔孽休得猖狂 | 正道一统，方为天下之福 |
| c9_韩夺心 | 剑下无情 | 夺宝灭门，亦是行义 |
| c10_司空玄 | 你前世并非全清白 | 道在何处？道在阴影里 |

## Per-file mechanical changes (10 files, applied via `C:/Users/light/AppData/Local/Temp/patch_chars_v10.py`)

15 fixed-string + 4 regex substitutions per file (19 total). Run output: 9 files × 19 substitutions on the script's second invocation (c10 got 19 on the first invocation before a console-encoding error halted printing; second invocation patched the remaining 9). Final state: all 10 files at v10, zero v8 markers remaining (sanity-checked: `static-camera single-shot` / `同机位同构图` / `7 秒内无任何镜头运动` / `5 段静态单 shot` / `v8)` — all zero).

For each `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md`:

1. **文件说明 line** — v8 `**7s static-camera single-shot — Kling reference 上传约束 v8 (无任何镜头运动 / 无 cut / 无 transition);前 2s 自包含（一/二）byte-identical truncate-compat**` → v10 `**7s locked-framing single continuous take — Kling reference 上传约束 v10 (单 take 连续运镜 / 慢速 / 单方向 / 锁定 framing / 无 dolly / 无 zoom);前 2s 自包含（一/二）byte-identical truncate-compat;180° slow orbit reveals 正/侧/背 at identical framing for downstream extract-3-views 管线**`.
2. **h1 heading** — v8 `7s static-camera single-shot + 0-2s 一/二 lock + 2-7s per-character dialogue` → v10 `7s locked-framing single continuous take + 0-2s 一/二 lock + 180° orbit + 2-7s per-character dialogue`.
3. **Prompt-block title** (per-character: `{NAME} · {ROLE} — 角色 reference 转身样片(…v8…)`) → `{NAME} · {ROLE} — 角色 reference 单 take 连续运镜(…v10…)`. Regex preserves the `{NAME} · {ROLE}` prefix.
4. **镜头 line** — v8 `静态单镜头 single take · 锁定机位 locked camera · 正面全身远景 (~35mm wide) · 9:16 竖屏 · 7 秒内无任何镜头运动 (no orbit / no push-in / …)` → v10 `单镜头连续运镜 single continuous take · 9:16 竖屏 · 3 阶段连续运动 (0-2s 锁定机位 正面 medium-full ~40mm + 2-6s 缓慢顺时针 180° orbit ≤ 45°/s, no dolly, no zoom + 6-7s 锁定机位 背面 medium-full)`. Framing tightened: head ~1/6 (v8 wide) → ~1/5 (v10 medium-full).
5. **动作 heading** — v8 `5 段静态单 shot；全程同机位同构图, 角色仅自然呼吸 + 头部微动 + 说话` → v10 `3 阶段连续运镜单 take；全程单方向 + 慢速 + 无方向反转 + 锁定 framing, 角色站定不动仅自然呼吸 + 头部微动 + 说话`.
6. **动作 beat 0-1s** — v8 `同机位同构图。角色站定, …说"一"` → v10 `锁定机位 正面 medium-full。角色站定, …说"一"`.
7. **动作 beat 1-2s** — v8 `同机位同构图。角色仍站定；说"二"` → v10 `锁定机位 正面 medium-full (与 0-1s 同构图)。角色继续站定；说"二"`.
8. **动作 beat 2-3s** — v8 `同机位同构图；角色说"三, 我是 {NAME}"` → v10 `镜头开始缓慢顺时针 orbit (45°/s, 单方向, no dolly, no zoom), 0° → 45°。角色站定, 眼神可缓慢跟随镜头；说"三, 我是 {NAME}"`. Regex preserves `{NAME}`.
9. **动作 beat 3-5s** — v8 `同机位同构图；角色说: "{TAG1}"` → v10 `镜头继续缓慢 orbit, 45° → 135° (经过 90° = 左侧身 at t=4.0s — 此时间点供下游抽 side png)。角色站定不动, 仅自然呼吸 + 头部微动；说: "{TAG1}" (标准声线 timbre baseline)`. Regex preserves `{TAG1}`.
10. **动作 beat 5-7s** — v8 `同机位同构图；角色说: "{TAG2}"；0.3s 自然定格收尾` → v10 `镜头继续缓慢 orbit 135° → 180° + 锁定 180° 背面 medium-full settle (与 0-2s framing 仅角度差 180°)。说: "{TAG2}" (catch + 情绪 peak + final lock); 自然定格收尾`. Regex preserves `{TAG2}`.
11. **台词 / 字幕 enumeration** — 用途 wording for slots 3 / 4 / 5 micro-tweaked: `落声 + 自我识别` → `落声 + 自我识别 + orbit 起`; `标准声线 baseline` → `标准声线 baseline, over orbit 0-90°`; `情绪 peak + catch + final lock` → `情绪 peak + catch + final lock, over orbit 90°-180° + 背面 settle`.
12. **节奏 line** — v8 `静态（7s 内无任何镜头运动 + 无任何 cut / transition，仅角色自然呼吸 + 头部微动 + 说话；前 2s 必须 self-sufficient）` → v10 `锁定 framing 单方向慢速 orbit 7s 单 take, 镜头匀速运动, 全程单方向无反转, 仅 0-2s + 6-7s 首尾静态; 角色站定 + 自然呼吸 + 说话; 前 2s 必须 self-sufficient byte-identical`.
13. **时长 line** — `7s` (unchanged — v8 and v10 share the 7s duration).
14. **负向 line** — v8 video-specific block (`不要 任何镜头运动 / … / 不要 让任何台词 over-emote 至失真`) → v10 video-specific block (13 items: drops `不要 任何镜头运动`, adds `不要 快速运镜 ≤ 45°/s` / `不要 任何方向反转` / `不要 任何 dolly / zoom / 推拉镜头` / `不要 任何 framing 变化` / `不要 mid-shot freeze` / `不要 旋转过程中角色脸部 motion blur`; rewords `不要 超过 7s` to `(reference 上传上限 v10)`). The character-bible negatives at the start of the line + the anti-AI-generic-face block at the end are unchanged.
15. **5-row table heading** — v8 `(静态单镜头 7s; 0-2s lock byte-identical 跨角色 + 2-7s per-character)` → v10 `(7s locked-framing single-take + 180° orbit; 0-2s lock byte-identical 跨角色 + 2-7s per-character; 抽帧时间戳 front t=1.0s / side t=4.0s / back t=6.0s)`.
16-18. **5-row table 用途 columns** for slots 3 / 4 / 5 — micro-tweaks matching the enumeration changes in step 11.

## Touch list

- `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md` — 10 files patched (script ran successfully, 19 substitutions / file, 0 v8 leaks).
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — header bump 026.
- `specs/ai_video/mozun_chongsheng/changelog.md` — append 026 entry (supersedes 024 + 025 note).
- `specs/ai_video/mozun_chongsheng/user_input/follow_ups/024-…` — add `SUPERSEDED by 026` tag at top (already had `SUPERSEDED by 025`; now superseded by 026 via 025 → which was never applied).
- `specs/ai_video/mozun_chongsheng/user_input/follow_ups/025-…` — add `SUPERSEDED by 026` tag at top.

## Out-of-band steps after this lands (user-side)

1. **Re-render the 10 character turntable mp4 files** at 7s with the v10 prompt. The existing v8 mp4s (if any were rendered) need replacement because v10's orbit changes the visual content — pre-v10 sources extracted with the new (1.0, 4.0, 6.0) timestamps would land side / back at frontal full-body (since v8 was static) — i.e., 3 identical frontal stills instead of 3 distinct angles.
2. **Upload one v10 mp4 to Kling reference channel** for empirical validator test before re-rendering all 10. **Fail-fast checkpoint**: if Kling rejects with the same "cuts or transitions, no clear character" error as v6 did, halt and fall back to v10.1 (drop 2-6s orbit; keep 7s static front lock = degraded v8 with v10 negative-prompt wording) or v10.2 (insert ~0.3s static holds at 90° + 180° in the orbit window).
3. **Re-trigger ai_video_management 短角色合辑 + ✂ 截到 2s tool** — confirm 0-2s 切片 byte-identical content to v8 output (still: 静态 + 正面 + 一/二; only the framing is medium-full instead of wide).
4. **Click the new 🖼 "提取三视图+音频" button** on each v10-rendered character mp4 tile in `apps/ui/src/components/SiblingMedia.tsx` (follow-up 093 feature). With v10 sources, the 3 extracted pngs will be at identical medium-full framing (head ~1/5 frame across all 3) — exactly the coherent 3-view character sheet that v9 couldn't produce.

## Out of scope

- ai_video_management webapp code — already handled in ai_video_management follow-up 096 (CANONICAL_VIEWS timestamps 7.0/9.0 → 4.0/6.0; front t=1.0 unchanged). No additional code change in this sibling follow-up.
- Shot prompts under `episodes/ep{NN}/prompts/shotNN/` — unchanged. Shot prompts only reference `{ref_cN_xxx}` placeholders, no embedded turntable schedule.
- Scene reference rule #12.10 v3 (15s walk-through) — orthogonal, unchanged.
- Character bibles' `## 标志台词或口头禅` section — read-only reference, unchanged.
- Existing character mp4s (v8 7s static) — invalidated by v10. User re-renders.
