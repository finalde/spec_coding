# Follow-up draft 023 — 2026-05-18 — **SUPERSEDED by follow-up 024 before implementation**

**Status: spec-only, never shipped.** Parent follow-up `ai_video_management/090` (v7 7s casting reel) was superseded by `091` (v8 static-camera 7s) before any character file got patched, in response to Kling's "single shot, clear character" upload-validator feedback. This sibling follow-up is therefore moot; see `024-{ts}-character-ref-7s-static-camera-kling-compat.md` for the actual implementation.

---

Apply the new 7s casting schema (cross-cutting rule `.claude/agent_refs/project/ai_video.md` rule #12.5 v6 → v7, originated from ai_video_management follow-up 090) to all 10 mozun_chongsheng character files.

## Why

15s (v6) was generous but heavy. 7s (v7) keeps the highest-signal beats and drops the redundant ones: removes 拉远 3/4 (silhouette already in 0-2s 360°), removes silent expression range (can't do justice in compressed budget), removes 标志台词 #3 + standalone catch row (slot #5 now doubles as catch + emotion peak). 0-2s lock unchanged → ai_video_management 短角色合辑 + ✂ 截到 2s 工具仍 self-sufficient.

## Per-character dialogue mapping (slots #1 and #2 only)

The v6 mapping used #1/#2/#3 + catch. v7 only needs #1 + #2. Reuse what was at v6 slot #1 + #2:

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

1. Title line: `(15s casting reel + 0-2s 一/二 lock + 2-15s per-character dialogue)` → `(7s casting reel + 0-2s 一/二 lock + 2-7s per-character dialogue)`.
2. 文件说明 line: `15s casting reel — Seedance reference 上传约束 v6` → `7s casting reel — Seedance reference 上传约束 v7`.
3. Outer section header: `(15s casting reel + 0-2s 一/二 lock + 13s character dialogue)` → `(7s casting reel + 0-2s 一/二 lock + 5s character dialogue)`.
4. 动作 timed-beats block (7-segment v6 → 5-segment v7) per the rule #12.5 v7 template.
5. 台词 / 字幕 enumeration (8 rows → 6 rows).
6. 节奏 line: `分段（15s 内 ...）` → `分段（7s 内: 0-2s 极速定场 + 360° 锁定 truncate-compat / 2-7s casting tail 紧凑呈现 voice + 标志特征点 final lock；前 2s 必须 self-sufficient）`.
7. 时长: 15s → 7s.
8. 负向: `不要 超过 15s（v6）` → `不要 超过 7s（v7）`; drop `不要 跳过任何 6 个 camera-move 段（结构性破坏 casting reel 完整性）` (v7 only has 3 camera moves in tail).
9. Bottom 8-row table → 6-row table.
10. Bottom table heading: `8 段 timed-beats + dialogue 对照表 (0-2s lock byte-identical 跨角色 + 2-15s per-character)` → `6 段 timed-beats + dialogue 对照表 (0-2s lock byte-identical 跨角色 + 2-7s per-character)`.

## Out of scope

- ai_video_management webapp code — unchanged.
- Existing rendered character mp4s (15s) — user re-renders to 7s at their discretion.
- Shot prompts under `episodes/ep{NN}/prompts/shotNN/` — unchanged.
- Scene reference v3 (rule #12.10, 15s walk-through) — unchanged.
- Character bibles' `## 标志台词或口头禅` section — read-only reference, never modified by this follow-up.
