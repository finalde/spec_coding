# Follow-up draft 025 — 2026-05-18
> **SUPERSEDED by follow-up 026 (rule #12.5 v10, 7s locked-framing single-take, cross-project ripple from ai_video_management 096)** — 025's patch script was never run; the character md files were still at v8 when 026's script applied v8 → v10 directly. v9 design rationale (slow push-in + slow orbit for face MCU + multi-angle silhouette) was reversed by v10 after follow-up 093's extract-3-views pipeline exposed that v9's mixed framing produced inconsistent 3-still framings. Kept on file as audit trail of the abandoned v9 attempt.

Apply the new v9 slow-push-in + slow-orbit 15s schema (cross-cutting rule `.claude/agent_refs/project/ai_video.md` rule #12.5 v8 → v9, originated from ai_video_management follow-up 092) to all 10 mozun_chongsheng character files. Supersedes 024 (v8 7s static-camera) — user rejected v8's trade-off (no face close-up read + no 侧身/背面 silhouette reference).

## Why

User directive in ai_video_management this turn: 「镜头由远到近，要能拍清楚脸部，而且缓慢旋转能看到侧身和背面」. v8 static frontal full-body never captures face at close-up scale (~1/6 frame), and provides no reference for character's side body or back side — both are needed for downstream shot prompts that need to reference 角色侧身 or 背面 silhouette.

v9 hypothesis: Kling validator's "cut/transition" rejection was triggered by speed + direction reversal, not motion itself. v5/v6 ran 0.5s 360° whip (~720°/s) + 6-segment push/pull reversals; v9 caps at ≤ 45°/s slow orbit + monotone push-in + reverse-dolly hidden inside orbit arc.

5-phase continuous-take design:
- 0-2s: 锁定机位 正面全身远景 (与 v8 byte-identical, 一/二 truncate contract preserved)
- 2-5s: 缓慢 dolly-in to medium close-up (face clear at ~50mm framing, 角色说"三, 我是 {角色名}")
- 5-13s: 缓慢顺时针 360° orbit ≤45°/s + 同步缓慢 reverse-dolly to wide (揭示正面 → 左侧身 → 背面 → 右侧身 → 回正面, 角色说标志台词 #1 + 标志台词 #2 起声)
- 13-15s: 锁定机位 正面全身远景 (settle, 角色完成标志台词 #2 final lock + 0.3s 定格)

## Per-character dialogue (slots #4 + #5 only, same lines that 088 → 091 → 092 plugged in)

The dialogue plug doesn't change from v8 → v9 — only the camera setup + time windows do. v8 had slot #4 in 3-5s / #5 in 5-7s. v9 stretches them to slot #4 in 5-10s (over orbit front-half) and slot #5 in 10-15s (over orbit back-half + settle). Same character-specific lines:

| Char | 5-10s (台词 #1, baseline over orbit 前半圈) | 10-15s (台词 #2, catch + peak + final lock over orbit 后半圈 + settle) |
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

## Per-file mechanical changes (10 files)

For each `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md`:

1. **Header schema 块** — v8 `7s static-camera single-shot` 文案 → v9 `15s slow-push-in + slow-orbit single continuous take` 文案. 文件说明 line, 用法 line, prompt title 块, 标题块全部 v8 → v9 wording (see rule #12.5 v9 schema for byte-identical template).

2. **镜头 line** — v8 `静态单镜头 single take · 锁定机位 locked camera · 正面全身远景 (~35mm wide) · 9:16 竖屏 · 7 秒内无任何镜头运动 (no orbit / no push-in / no pull-out / no pan / no tilt / no zoom / no dolly / no handheld)。...` → v9 `单镜头连续运镜 single continuous take · 9:16 竖屏 · 5 阶段连续运动 (0-2s 锁定机位 正面全身远景 ~35mm wide + 2-5s 缓慢 dolly-in 推近到面部 medium close-up ~50mm + 5-13s 缓慢顺时针 360° 环绕 ≤ 45°/s + 5-13s 同段缓慢 reverse-dolly 拉远回 ~35mm wide + 13-15s 锁定机位 正面全身远景收尾)。全程匀速 / 无方向反转 / 无定格中断 / 无 cut / transition / fade。...`

3. **动作 5 段** — v8 5 段 「同机位同构图」 prefix → v9 5 阶段 motion phases (0-2s 锁定 / 2-5s 缓慢 dolly-in / 5-13s 缓慢 360° orbit + reverse-dolly / 13-15s 锁定收尾). Dialogue 内容不动, 但时段重排: slot 3 (2-3s → 2-5s), slot 4 (3-5s → 5-10s), slot 5 (5-7s → 10-15s).

4. **台词 / 字幕 list** — slot 3/4/5 时段 column 重排同上.

5. **5-row dialogue table** — slot 3 时段 2-3s → 2-5s, slot 4 时段 3-5s → 5-10s, slot 5 时段 5-7s → 10-15s. 情绪基调 + 用途 + 台词 不变 (用途 column micro-edit: slot 4 "标准声线 baseline" → "标准声线 baseline（over slow orbit 前半圈）"; slot 5 "情绪 peak + catch + final lock" → "情绪 peak + catch + final lock（orbit 后半圈 + 锁定收尾）"; slot 3 "落声 + 自我识别" → "落声 + 自我识别 + 面部 close-up read").

6. **节奏 line** — v8 `静态（7s 内无任何镜头运动 + 无任何 cut / transition，仅角色自然呼吸 + 头部微动 + 说话；前 2s 必须 self-sufficient）` → v9 `缓慢连续运镜（15s 内单 take, 镜头匀速运动, 全程单方向无反转, 仅 13-15s 段锁定; 角色站定 + 自然呼吸 + 说话; 前 2s 必须 self-sufficient byte-identical）`.

7. **时长 line** — `7s` → `15s`.

8. **负向 line** — v8 11-item ban list → v9 11-item ban list with the following swaps:
   - DROP: `不要 任何镜头运动 (no orbit / push-in / pull-out / pan / tilt / zoom / dolly / handheld / motion blur)` (v9 reintroduces controlled motion).
   - KEEP: `不要 任何 cut / transition / scene change / fade / dissolve / cross-fade — 全程单镜头单 take`.
   - KEEP (modify): `不要 角色转身 / 走动 / 大幅度肢体动作` → `... (角色站定让镜头围绕, 而非角色自身旋转 — 保 Kling character detector 锁定主体)`.
   - KEEP: `不要 唇形与台词错位`, `不要 角色跑出画面`, `不要 把 "一" / "二" 延后到 2s 之后`, `不要 在 0-2s 段加入额外台词`, `不要 让任何台词 over-emote 至失真`.
   - MODIFY: `不要 超过 7s (reference 上传硬上限 v8)` → `不要 超过 15s (reference 上传上限 v9)`.
   - ADD: `不要 快速运镜 (no fast orbit / no fast push / no fast pull / no whip-pan / no snap-zoom — orbit 旋转速度 ≤ 45°/s, push-in dolly ≥ 3s 完成)`.
   - ADD: `不要 任何方向反转 (no orbit reversal / no push-in-then-pull-out reversal / no pan back-and-forth — 全程单方向; 5-13s 段的 orbit + reverse-dolly 是同弧线内的连续运动, 不构成方向反转)`.
   - ADD: `不要 任何定格中断 (no freeze frame mid-shot / no stop-and-go — 镜头连续运动直到 13s, 仅最后 0.3s 自然定格收尾)`.
   - ADD: `不要 旋转过程中角色脸部 motion blur (慢速 orbit + 角色站定 → 角色清晰 / character detector 可锁定)`.

9. **画面 / framing** — character standing posture, lighting, render style, 比例 9:16 不变 (光照三点布光 + cyc wall + 渲染样式 byte-identical to v8). Light positions stay static; orbit moves camera + 灯位关系 (not 灯位 itself).

## Touch list

- `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md` — 10 files patched via one-shot Python script (user runs after reviewing this draft; parallel to 091's `/tmp/patch_chars_v8.py`).
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — header bump 025.
- `specs/ai_video/mozun_chongsheng/changelog.md` — append 025 entry (supersedes 024 note).

## Out-of-band steps after script run

- Re-render 10 turntable mp4 files at 15s with the v9 prompt.
- Upload one v9 mp4 to Kling reference channel for empirical validator test before re-rendering all 10. **Fail-fast checkpoint**: if Kling rejects with the same "cuts or transitions, no clear character" error as v6, halt and fall back to v9.1 (drop 5-13s orbit; keep only 2-5s push-in; upload 5s clip) or v8 (091's 7s static).
- Re-trigger ai_video_management 短角色合辑 + ✂ 截到 2s tool — confirm 0-2s 切片 byte-identical to v8 output (frontal full-body + 一/二 voice baseline).

## Status of v8 (follow-up 024)

024 + 091 (parent) marked SUPERSEDED at top with a one-line note pointing to 025 + 092. Kept on file as audit trail. v8's character file patches (already applied by 091's script) are overwritten by 025's script — git diff will show the line-level swaps documented in §「Per-file mechanical changes」 above.
