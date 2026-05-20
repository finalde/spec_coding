# Follow-up draft 078 — 2026-05-17
Bump character reference video duration from 2.9s to 4s so each character has more screen time to showcase identity, and lock the timing contract so the first 2 seconds remain self-sufficient — the user can keep using a 2s truncation downstream without losing critical information. Reaffirms the existing shot-character-reel auto-truncate-to-2s behavior as the canonical contract (no code change required — already implemented).

## Why 4s (not 2.9s any more)

- The earlier 2.9s ceiling (follow-up 015 over on the ai_video side, codified as agent_refs/project/ai_video.md rule #12.5 v4) was driven by 2026-05 Seedance reference-upload limits. Those limits have eased; 4s comfortably fits within current Seedance / Sora / Veo / Runway Gen-3 reference budgets and leaves room for a slower, more legible turntable.
- 4s gives the character ≈ 38% more on-screen seconds for identity capture (face/profile/voice timbre) without breaking the "极速 reference, not a viewer-facing shot" framing.

## Why first 2s must remain self-sufficient

- The chars-reel concat operation (`ShotConcatBuilder` in `libs/infrastructure/writers/character_video__writer.py`) trims each per-character clip to `_CONCAT_SEGMENT_S = 2.0` seconds before concatenation. That is the canonical "短角色合辑" path and stays at 2s — it is the right length for a per-shot character cue reel.
- The user also pulls 2s clips ad-hoc via the existing **✂ 截到 2s → video.mp4** button (follow-up 054 truncator, `_TRUNCATE_DURATION_S = 2.0`).
- Both 2s consumers slice the **first** 2 seconds of the source. Therefore the character ref prompt MUST front-load identity beats: the character finishes saying "一" and "二" (Chinese count) within the first 2 seconds, with the visible turntable pass covering正/侧/背/侧 in that window. "三" is then said in the 2-4s tail along with the face推近 close-up.

## Authoritative prompt-timing contract (post-follow-up)

```
时长: 4s

动作 timed beats:
  - 0-1s: 正面**全身远景**起手；自然呼吸；说 "一"（中文数字一）。
  - 1-2s: 镜头**快速 360° 顺时针环绕一圈**（侧 90° → 正背 180° → 另一侧 270° → 回正 360°），全身始终在画面内；说 "二"（中文数字二）。
  - 2-3s: 镜头由全身远景**推**至面部中近景特写（眉眼 + 服装领口 + 标志特征点可辨）；说 "三"（中文数字三）。
  - 3-4s: 面部中近景定格 1s（眼神跟镜，自然呼吸，无台词），用于身份特征 final lock。

台词 / 字幕: 内嵌唇形对齐音频（中文数字 "一, 二, 三"）。
  1. "一" 0-1s — 起声 / 声线 timbre 锚点
  2. "二" 1-2s — 中段 / 节奏校准（**必须在 2s 前结束**：下游 2s 截取边界）
  3. "三" 2-3s — 落声 / 咬字校准

负向（新增 / 修订）:
  - 移除: 不要 超过 2.9s（reference 上传硬上限）
  - 新增: 不要 超过 4s（reference 上传硬上限 v5）
  - 新增: 不要 把 "一" / "二" 延后到 2s 之后（下游 2s 截取依赖此契约）
```

`场景` / `镜头`（修订后整段） / `光线 / 色调` / `节奏（4s 内）` / `渲染样式` / `比例` / `负向` 其余字段 byte-identical 跨角色（与 v4 同）；唯一逐角色字段仍是 `角色:` 段。

## Auto-truncate-to-2s on shot-char video — confirmed unchanged

- The webapp already enforces this. `ShotConcatBuilder._ffmpeg_concat` (lines ~605-625 of `character_video__writer.py`) runs each input through `trim=duration={_CONCAT_SEGMENT_S},...` inside `-filter_complex`, where `_CONCAT_SEGMENT_S = 2.0`. Each character contributes its first 2 seconds; the segments concatenate into a uniform 720x1280 30fps reel with normalised audio.
- Character source selection is the existing "first mp4 in folder, alphabetical" rule (follow-up 064) — unchanged.
- **No code change is required for this follow-up.** This follow-up only updates the upstream prompt template so the first 2 seconds of every generated character video carry enough identity information for the trimmer to land on something useful.

## Touch list (downstream walk)

- `.claude/agent_refs/project/ai_video.md` rule #12.5 — bump duration 2.9s → 4s, swap "1, 2, 3" → "一, 二, 三", restructure timed beats to the 4-segment table above, update negatives, update "Turntable 视频 prompt 锁定字段" duration value (= 4s), update rationale paragraph + footer "(Originated from … rev — follow-up 078 …)".
- `specs/development/ai_video_management/user_input/revised_prompt.md` — regenerated from raw + every follow-up (this follow-up appended).
- `specs/development/ai_video_management/changelog.md` — append follow-up 078 entry.
- `projects/ai_video_management/libs/infrastructure/writers/character_video__writer.py` — **no change**. The 2s concat-segment constant is the right one and is already in place.

## Cross-project ripple

- `specs/ai_video/mozun_chongsheng/user_input/follow_ups/019-{date}-character-ref-4s.md` — sibling follow-up on the mozun_chongsheng ai_video project, applying the new 4s schema to the 10 existing character md files (`ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md`). That project's `changelog.md` gets its own entry. The cross-cutting rule update under `.claude/agent_refs/project/ai_video.md` makes every future ai_video project inherit the new schema without per-project follow-ups.

## Out of scope

- Existing rendered `*.mp4` artifacts inside `ai_videos/{drama}/characters/cN_*/` — those are user-rendered media (gitignored per NFR-18). Re-renders happen at the user's discretion using the updated prompt; no automatic re-rendering.
- The actor-comp-card pipeline (`actor__chinese_prompt.py`) — that pipeline produces *still images* for the casting pool, not character reference videos. It is not affected.
- The chars-reel concat output filename, location, timing-annotation patch (`参考: 请参考视频 {ref_chars_reel}, 0~2s 为 …` line at the top of each shot prompt) — all unchanged.
