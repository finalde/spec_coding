# Follow-up draft 024 — 2026-05-18
> **SUPERSEDED by follow-up 025 (rule #12.5 v9, slow-push-in + slow-orbit 15s, cross-project ripple from ai_video_management 092)** — user rejected v8's trade-off; 025's script overwrites the character md patches that 024's script applied. Kept on file as audit trail.

Apply the new v8 static-camera 7s schema (cross-cutting rule `.claude/agent_refs/project/ai_video.md` rule #12.5 v6 → v8, originated from ai_video_management follow-up 091) to all 10 mozun_chongsheng character files. Supersedes 023 (v7 7s with camera moves) which was specced but never patched because v7's design — like v5/v6 — would have been rejected by Kling's "single shot, clear character" upload validator.

## Why

Kling rejected the v6 15s casting reel uploads with:
> the current video contains cuts or transitions, and no clear, complete character is detected, please upload a single shot clear character video

The validator interprets fast 360° orbits + camera-direction reversals + push-ins as "transitions" even within one continuous take. v8 drops all camera motion: 7s of static frontal full-body, character speaks throughout. The 0-2s truncate output is now a clean frontal full-body of the character speaking 一/二 (loses the 360° silhouette pass that v5/v6/v7 had, but per user clarification this turn the simpler truncate is acceptable).

## Per-character dialogue (slots #1 + #2 only, same lines that 088 plugged in)

The dialogue plug doesn't change from v6 → v8 — only the camera setup does. v6 used 4 slots (slots 4/5/7/8) per character; v8 uses 2 slots (slots 4/5). The lines reused are exactly v6's slot 4 (台词 #1) + slot 5 (台词 #2):

| Char | 3-5s (台词 #1, baseline) | 5-7s (台词 #2, catch + final lock) |
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

1. Title line: `(15s casting reel + 0-2s 一/二 lock + 2-15s per-character dialogue)` → `(7s static-camera single-shot + 0-2s 一/二 lock + 2-7s per-character dialogue)`.
2. 文件说明 line: `**15s casting reel — Seedance reference 上传约束 v6;前 2s 自包含（一/二）byte-identical truncate-compat**` → `**7s static-camera single-shot — Kling reference 上传约束 v8 (无任何镜头运动 / 无 cut / 无 transition);前 2s 自包含（一/二）byte-identical truncate-compat**`.
3. Outer section header: `(15s casting reel + 0-2s 一/二 lock + 13s character dialogue)` → `(7s static-camera + 0-2s 一/二 lock + 5s character dialogue)`.
4. `镜头:` line — replace 6-camera-move enumeration with `镜头: 静态单镜头 single take · 锁定机位 locked camera · 正面全身远景 (~35mm wide) · 9:16 竖屏 · 7 秒内无任何镜头运动 (no orbit / no push-in / no pull-out / no pan / no tilt / no zoom)`.
5. 动作 block (v6 7-segment → v8 5-segment) — every beat starts with "同机位同构图" so the model can't add camera moves. No 360°, no 反向 90°, no 拉远 3/4, no 横向 pan, no 拉近 medium close-up — all replaced by static-frame character speaking.
6. 台词 / 字幕 enumeration: 8 rows → 5 rows. Drop slot 6 (silent expression range — needs camera motion to be meaningful), drop slot 7 (台词 #3, no time in 7s static), drop slot 8 (separate catch close, slot 5 doubles).
7. 节奏 line: `分段（15s 内...）` → `静态（7s 内无任何镜头运动，仅角色自然呼吸 + 说话；前 2s 必须 self-sufficient）`.
8. 时长: 15s → 7s.
9. 负向 line — drop v6's "不要 跳过任何 6 个 camera-move 段" + "不要 镜头回切倒退（要单向 360°）"; add v8's "不要 任何镜头运动" + "不要 任何 cut / transition / scene change / fade / dissolve / cross-fade — 全程单镜头单 take" + "不要 角色转身 / 走动 / 大幅度肢体动作 (保 Kling character detector 锁定主体)"; swap "不要 超过 15s（v6）" → "不要 超过 7s（v8）".
10. Bottom 8-row table → 5-row table.
11. Bottom table heading: `8 段 timed-beats + dialogue 对照表 (0-2s lock byte-identical 跨角色 + 2-15s per-character)` → `5 段 timed-beats + dialogue 对照表 (静态单镜头 7s; 0-2s lock byte-identical 跨角色 + 2-7s per-character)`.

## Out of scope

- ai_video_management webapp code — unchanged.
- Existing rendered character mp4s (15s v6 / 4s v5 / older). User re-renders to v8 7s static at their discretion.
- Shot prompts under `episodes/ep{NN}/prompts/shotNN/` — unchanged.
- Scene reference v3 (rule #12.10, 15s walk-through) — scenes don't have a character-detector constraint, so multi-camera is fine there; unchanged.
- Character bibles' `## 标志台词或口头禅` section — read-only reference.

## User-side action after this lands

1. Re-render the 10 character turntable mp4s using the new v8 7s static-camera prompt.
2. Upload to Seedance / Kling — should pass validator now (no cuts/transitions, clear character throughout).
3. Re-trigger ai_video_management `✂ 截到 2s` button + `生成角色合辑` button to refresh the 2s slices in any downstream shot concat.
