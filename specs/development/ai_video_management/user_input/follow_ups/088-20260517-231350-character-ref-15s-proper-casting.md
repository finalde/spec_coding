# Follow-up draft 088 — 2026-05-17
Bump character reference turntable from 4s to **15s** so each character gets proper screen time to showcase casting (more camera angles, more dialogue, voice/emotion range). The 0-2s self-sufficient contract from follow-up 078 stays — `_CONCAT_SEGMENT_S = 2.0` truncation use case unchanged.

## Why

User: "lets change the charactor video prompt to from 4s to 15s, you have a lot more time and roomt to show a proper casting, and let the charactor speak a lot more than 1,2,3. but since I have a use case to also need to truncate the vidoe to 2s, so lets make sure we have a proper first 2s, and charactor speak 1,2 at least, and then you can use the result of time, to show more angle of the charactor in casting and let him talk more".

Follow-up 078 (rule #12.5 v5) gave each character 4s — enough to ship "0-2s 一+二 / 2-3s 三 / 3-4s 1s close-up". User now wants the casting reference to be a real character read: multiple camera angles + character's actual signature lines + voice range. The 15s budget matches the scene-reference v3 walk-through (rule #12.10) — so character + scene reference videos are dim-comparable on Seedance / Sora / Veo / Runway uploads (all these models now accept ≥ 15s reference uploads in 2026-05).

The 2s truncate contract (shot-char concat reel `_CONCAT_SEGMENT_S = 2.0` + ✂ 截到 2s button `_TRUNCATE_DURATION_S = 2.0`) **must continue to work**. So 0-2s stays byte-identical across all characters (一 + 二 + 正面定场 + 360° 回正), exactly as v5 already locks. 2-15s is the new "extension" that gets dropped by the trim and only matters when the full 15s is uploaded to Seedance.

## Spec — rule #12.5 v5 → v6

### Locked 0-2s prefix (UNCHANGED from v5 — this is the truncate-compat half)

```
0-1s: 正面**全身远景**起手, {角色姿态 + 眼神跟镜 + 自然呼吸}; 说"一"。
1-2s: 镜头**快速 360° 顺时针环绕一圈**（侧面 90° → 正背 180° → 另一侧 270° → 回正 360°）, 全身始终在画面内, 覆盖正/侧/背/侧四向轮廓; 说"二"。**必须在 2.0s 前完成发声 + 回正到正面**。
```

### New 2-15s casting-reel extension (per-character variable)

```
2-3s: 镜头由全身远景**推**至**面部中近景特写**（眉眼 + 服装领口 + 标志特征点 row #11）; 说"三, 我是 {角色姓名}"。
3-5s: 面部中近景定格 1s 让特征落定, 然后**反向慢速 90° 环绕**（正面 → 左侧 45° → 左侧 90°）; 角色说出**标志台词 #1**（character bible 中第 1 句, 演员标准声线, 平稳中音 timbre 锚点 — 给下游 voice-clone / TTS 训练用的 baseline）。
5-8s: 镜头由侧面拉远至**3/4 全身侧像**（左侧 45° + 全身可见）; 角色说出**标志台词 #2**（character bible 中第 2 句, 切换情绪锚点 — 若 bible 标注 "杀气凛然" 则压低声+咬字加重, 若 "温润如玉" 则放缓+尾音上扬）。
8-11s: 镜头**横向 pan** 经背面 180° → 右侧 90° → 右侧 45°; 角色无台词, 仅**表情 range**（中性 → 微笑 → 严肃 → 凝视）, 让下游 capture micro-expression 区间。
11-13s: 镜头回正 + **拉近至胸像 medium close-up**（含 双手手势 + 标志道具 if any）; 角色说出**标志台词 #3**（character bible 中第 3 句, 情绪 peak — bible 中 "情绪基调" 段标注的最 character-defining 声线）。
13-15s: 镜头最终**推至特写**（眼神直视镜头, 标志特征点 row #11 占满下半画面, 例: 沧冥右眼下方朱砂痣, 司空玄左颈侧十字暗纹）; 角色说出**character bible 中"配音参考"段标注的最终语气基线**（如 "本尊从不解释, 只清算" — 一句 ≤ 10 字的 catch-phrase）, 定格 0.5s 结束。
```

### Dialogue source — character-specific

The 0-2s segment is byte-identical across all characters (`一` then `二`). The 2-15s segment is **per-character**, sourced from each character md's existing `## 标志台词或口头禅` section (every character bible has 3 catch phrases) + the `## 配音参考` section's "声线 / 语速 / 情绪基调" descriptors. The shot mapping:

- 2-3s: `三, 我是 {角色名}` (locked template — just `三` + name).
- 3-5s: `{角色名}.bible["标志台词"][0]` verbatim.
- 5-8s: `{角色名}.bible["标志台词"][1]` verbatim.
- 8-11s: silent (expression range only — no dialogue).
- 11-13s: `{角色名}.bible["标志台词"][2]` verbatim.
- 13-15s: `{角色名}.bible["配音参考 catch-phrase"]` (the most character-defining ≤10-char line; if the character only has 3 catch phrases total, repeat #1 as the closing tag).

### Camera-move template (byte-identical across characters)

The 6 camera moves (推近 / 反向 90° / 拉远 3/4 / 横向 pan 360° / 拉近 medium / 特写) are byte-identical across characters — the casting reel structure is locked. Per-character variation lives only in: (a) dialogue text, (b) standout feature focused in 13-15s close-up (row #11 标志特征点), (c) prop / wardrobe details visible in 11-13s medium close-up.

### Time-budget / Seedance upload contract

- New ceiling: **15s** (was 4s in v5; 2.9s in v4; 12s in pre-v4).
- Seedance / Sora / Veo / Runway Gen-3 / Kling reference upload limits per 2026-05 testing: ≥ 15s comfortably accepted; aligns with the scene-reference v3 walk-through (rule #12.10) so character + scene refs are dim-comparable.
- Existing 2s truncation paths (`_CONCAT_SEGMENT_S = 2.0` in `ShotConcatBuilder._ffmpeg_concat`, `_TRUNCATE_DURATION_S = 2.0` in `CharacterVideoTruncator.truncate`) keep working unchanged — they slice 0-2s which is still self-sufficient per the locked prefix.

### Negatives (additions)

Append to the per-character video reference prompt's `负向:` section:

- `不要 超过 15s（reference 上传硬上限 v6）`
- `不要 把 "一" / "二" 延后到 2s 之后（下游 2s 截取依赖此契约）`
- `不要 在 0-2s 段加入额外台词（保 byte-identical 跨角色 truncate 输出）`
- `不要 跳过任何 6 个 camera-move 段（结构性破坏 casting reel 完整性）`
- `不要 让任何台词 over-emote 至失真（声线 timbre baseline 优先 — 配音参考段 baseline 标注覆盖）`

Drop the old v5 negative `不要 超过 4s（reference 上传硬上限 v5）`.

### Locked-fields list (10+ character byte-identical)

Per rule #12.5 v5 footer: 9 fields are byte-identical across all character turntable prompts; only `角色:` line varies. v6 extends:

| Field | v6 state |
|---|---|
| `场景` | byte-identical (中性灰 cyc) |
| `镜头` (camera framing list) | byte-identical (6-move template) |
| `光线 / 色调` | byte-identical (3-point lighting) |
| `节奏` | byte-identical ("分 7 段, 0-2s lock, 2-15s casting reel") |
| `渲染样式` | byte-identical |
| `比例` | byte-identical (9:16) |
| `时长` (= 15s) | byte-identical |
| `台词` (0-2s = "一", "二") | byte-identical |
| `台词` (2-15s) | **PER-CHARACTER** — pulled from `标志台词` + `配音参考` |
| 视频专属负向 | byte-identical (5 new negatives above) |

Goal preserved: 10+ character turntable outputs剪辑成「角色介绍合集」 still feasible because 0-2s is byte-identical truncate-compat + camera-move template is byte-identical; only spoken text + standout feature differ per character (which is exactly what a casting reel should differ on).

## Why slot 088 (not 086)

Concurrent parallel work has been claiming slots 084 (toast TTL fix) + 086 (assigned filter chip). Slot 087 = my just-shipped `negative_prompt` split. This new work takes 088.

## Touch list

- `.claude/agent_refs/project/ai_video.md` rule #12.5 v5 → v6 — bump duration 4s → 15s, rewrite timed-beats schema (3 locked-prefix beats + 6 new casting-reel beats), rewrite dialogue sourcing section (per-character from bibles), update negatives (drop "≤ 4s", add 5 new), update locked-fields list (per-character dialogue carve-out), update footer attribution `rev — follow-up 088 …`.
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bump 088.
- `specs/development/ai_video_management/changelog.md` — append 088 entry.
- `specs/ai_video/mozun_chongsheng/user_input/follow_ups/022-{ts}-character-ref-15s-casting-reel.md` — sibling follow-up applying the schema to all 10 mozun_chongsheng character files using each character's own 标志台词.
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — header bump.
- `specs/ai_video/mozun_chongsheng/changelog.md` — append entry.
- `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md` — patch each character file's video reference prompt section to the 15s schema + insert that character's 3 标志台词 into the per-character dialogue slots.

## Out of scope

- `ai_video_management` webapp code — **no code change**. The 2s concat trim path in `character_video__writer.py` already does what 088 needs (slices 0-2s). The `✂ 截到 2s` button likewise. New 15s source mp4s just have more material after the 2s mark; the truncator doesn't care.
- Frontend — unchanged. The webapp displays whatever video duration the user renders.
- Existing rendered 4s mp4s under `characters/c*/`. Untouched. User re-renders at their discretion.
- Scene reference v3 (rule #12.10, 15s walk-through) — already 15s, unchanged.
- Shot prompts (rule #12.6) — only reference `{ref_cN_xxx}` placeholder, no embedded duration text. Unchanged.

## User-side action after this lands

For each of the 10 mozun_chongsheng characters, render a new 15s turntable using the updated prompt. Replace the existing `characters/cN_*/cN_*.mp4` files. Concat reel and ✂ 截到 2s continue to work because 0-2s is locked. The full 15s gives Seedance a much richer voice / emotion / silhouette / standout-feature reference per character.
