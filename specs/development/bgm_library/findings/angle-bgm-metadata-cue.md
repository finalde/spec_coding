---
worker_id: researcher-04-bgm-metadata-cue
stage: 3
role: researcher
angle: bgm-metadata-cue
status: complete
blockers: []
confidence: high
---

# Angle — BGM mood taxonomy, per-track metadata, and bgm.md cue format

## 1. What this angle covers

A concrete, fixed proposal for three coupled artifacts of the shared BGM library:
(a) a fixed Chinese **mood-category enum** for vertical short-drama (爽剧/重生/穿越/打脸/虐恋); (b) the **per-track metadata table** in `bgm_NNNN.md`, mirroring `actor_0001.md`; and (c) the **`bgm.md` cue-timeline line format** that scripts use to reference tracks by `bgm_NNNN` and that `tools/mux_av.py` consumes. The aim is parseability (grep `bgm_NNNN` for assignments reverse-lookup; deterministic parse for mux), mirroring the terseness of `subtitles.md`.

## 2. Key findings

### 2.1 Fixed mood-category enum (proposed — 12 categories)

Short-drama practitioners score by **scene-emotion beat**, not by genre. A 2026 industry BGM guide frames the craft as "3秒抓眼球、10秒造反转、1分钟戳中情绪" and explicitly splits selection by beat: fast-percussion 近身打斗/绝境反杀/追车/突围 for 逆袭/动作, and tear-jerk 诀别/误会/隐忍 for 古风虐恋 ([sohu 2026 短剧 BGM 榜单](https://www.sohu.com/a/1001377183_122145242)). Stock libraries (爱给网) likewise bucket by emotion-beat — 紧张/危急, 卡点, 叙事, 情感史诗 ([aigei 紧张](https://www.aigei.com/music/class/rock/), [aigei 卡点](https://www.aigei.com/music/short/card_point/), [aigei 叙事](https://www.aigei.com/music/class/narrative/), [aigei 情感](https://www.aigei.com/music/class/emotional_epic/)). Mapping those beats onto the short-drama tropes in the prompt yields:

| enum (`category`) | 中文标签 | 用途（典型 beat） |
|---|---|---|
| `tension` | 紧张对峙 | 摊牌、威胁、僵持（裴霆拍案那类） |
| `combat` | 打斗 | 近身打斗、追车、绝境反杀 |
| `climax_hype` | 高燃爽点 | 实力暴露、碾压、登场名场面 |
| `faceslap` | 打脸反转 | 打脸、身份反转、当众逆袭 |
| `tragic` | 悲情 | 诀别、死亡、悲怆 |
| `warm` | 温情 | 亲情/和解/守护 |
| `romance_pain` | 虐恋 | 误会、隐忍、求而不得 |
| `suspense` | 悬疑 | 阴谋、伏笔、诡异 |
| `daily` | 日常 | 过场、铺垫、轻松对话 |
| `flashback` | 回忆 | 暖黄泛旧闪回（EP1「四、回忆」段） |
| `theme_open` | 片头主题 | 片头/标题/钩子 |
| `system_cue` | 系统音 | 金手指「叮」鎏金对话框点缀（本剧 system OS 高频） |

Fact: the beat-based split and the named tropes are sourced above. **Practitioner-opinion:** the exact 12-bucket cut, the English enum keys, and including `system_cue` (driven by this repo's 系统/金手指 convention seen in `dialogue.md`) are my synthesis, not a quoted standard. 12 is a deliberate middle of the requested 8–14 — enough to filter UI meaningfully without forcing authors to guess between near-duplicates. `category` is both the folder level (`ai_videos/_bgm/{category}/`) and a metadata field; `mood` below stays free-text for nuance within a category.

### 2.2 Per-track metadata table (`bgm_NNNN.md`)

Confirm the prompt's field list, refined: drop nothing, add `key`/`tags` as optional. Mirror `actor_0001.md` exactly — H1 = id, one-line caption, a `| 字段 | 值 |` table, then a fenced generation prompt.

```markdown
# bgm_0001

MusicGen-generated BGM — 紧张对峙铺底（可循环）。

| 字段 | 值 |
|---|---|
| category | tension |
| mood | 冷峻、压迫、低频脉冲 |
| bpm | 90 |
| duration | 30 |
| loopable | true |
| intensity | 4 |
| instruments | 低音提琴, 定音鼓, 合成器 pad |
| generator | musicgen |
| model | facebook/musicgen-medium |
| seed | 1779292638 |
| license | CC-BY-NC / MIT-weights (MusicGen) |
| tags | 对峙, 摊牌, 男频 |
| notes | — |

## 生成 prompt

```
tense cinematic underscore, low pulsing synth bass, taut staccato strings,
sparse timpani hits, dark and oppressive, no melody lead, loopable 30s, 90 bpm
```
```

Notes on fields: `intensity` is an integer 1–5 (1=ambient bed, 5=full 高燃); it lets the UI sort and lets mux pick a duck depth. `loopable` (bool) gates whether mux may tile the track to fill a long cue. `duration` in seconds (int) is the rendered mp3 length. `seed`/`model` make a track regenerable (deterministic, mirrors actor's `seed`). `license` defaults to MusicGen's commercial-safe weights but is kept explicit so future non-MusicGen sources are flagged.

### 2.3 `bgm.md` cue-timeline line format

Mirror `subtitles.md`: a short header doc comment, then one fenced `text` block, one cue per line. Proposed grammar (pipe-delimited, fixed field order, all-but-first optional with defaults):

```text
> 每行: `起-止(秒) bgm_NNNN | vol=<0-1或dB> | duck=on|off | fade=<in>/<out>`
> 字段顺序固定；vol 默认 1.0，duck 默认 on，fade 默认 0/0（秒）。省略尾部字段即取默认。
> 单 bgm.md 管一集（novel）或一项目（short），与 dialogue.md/subtitles.md 同级。

```text
0-18    bgm_0011 | vol=0.7 | duck=on  | fade=2/2     # 片头主题
18-42   bgm_0001 | vol=0.8 | duck=on  | fade=1/1     # 紧张对峙
42-55   bgm_0007 | vol=0.6 | duck=on  | fade=0.5/3   # 回忆 暖黄
55-70   bgm_0021 | vol=1.0 | duck=on  | fade=1/2     # 高燃爽点 cliffhanger
```
```

Parse contract: split on first whitespace → time range `start-end` (seconds, int or float); next token = `bgm_\d{4}`; remaining `key=value` tokens are order-free after the id. This keeps `grep -o 'bgm_[0-9]\{4\}'` valid for assignments reverse-lookup, and gives `mux_av.py` a line-oriented, regex-parseable feed. `vol` accepts either `0.0–1.0` (linear gain) or a `dB` suffix (`vol=-6dB`); mux normalizes. Optional trailing `# comment` is ignored by the parser (author-facing only).

### 2.4 Fade / duck / loop interplay with `mux_av.py`

`mux_av.py` is ffmpeg-driven (video stream copy, no re-encode; mix 台词 MP3 + BGM). The cue fields map to ffmpeg filters:

- **duck=on** → BGM is the carrier into `sidechaincompress`, keyed by the 台词 MP3 sidechain — BGM auto-dips under speech and recovers in gaps. Practitioner-validated ffmpeg params: `threshold≈0.015, ratio≈15, attack≈30ms, release≈800ms` ([ffmpeg-user ducking thread](https://ffmpeg.org/pipermail/ffmpeg-user/2018-August/040933.html), [orchestkit audio-mixing-patterns](https://raw.githubusercontent.com/NeverSight/skills_feed/refs/heads/main/data/skills-md/yonatangross/orchestkit/audio-mixing-patterns/SKILL.md)). `duck=off` mixes flat (use for music-only stretches with no dialogue, e.g. 片头).
- **fade=in/out** → `afade=t=in:d=<in>` and `afade=t=out:d=<out>` on the BGM segment at cue boundaries; cross-cue overlaps fall out naturally when one cue's fade-out meets the next's fade-in.
- **loop** → if a cue's duration exceeds the track's `duration` AND `loopable=true`, mux tiles via `aloop`/`-stream_loop` then trims to the cue window; if `loopable=false` it pads with silence and SHOULD warn.
- **Loudness targets** (practitioner standard, not a hard repo rule): voice ≈ -14 LUFS, ducked music bed -30…-35 LUFS, music-only -16 LUFS ([orchestkit SKILL.md](https://raw.githubusercontent.com/NeverSight/skills_feed/refs/heads/main/data/skills-md/yonatangross/orchestkit/audio-mixing-patterns/SKILL.md)). Apply `loudnorm` (EBU R128) as a final pass. `vol` in the cue is a pre-duck author trim layered on top of these targets.

## 3. Implications for the spec

- **value object:** `category` is a fixed enum of the 12 keys above (stage-4 must pin the exact list); `intensity` is constrained int 1–5; `loopable` bool. These belong in `bgm__valueobject`.
- **cue is the assignments source:** `CastingRepository`-analog scans every `episodes/*/bgm.md` (+ short-root `bgm.md`) for `bgm_\d{4}` to answer "which dramas reference this track."
- **mux contract is downstream of the cue grammar** — `mux_av.py` and the `bgm.md` parser must share one grammar definition; spec should name the line format as the single source of truth.
- **ai_video.md rule addendum** (Desired-outcome #5) should encode: the 12-key enum, the metadata table shape, the cue line grammar, and the duck/fade/loop→ffmpeg mapping.

## 4. Open questions

- Should `vol` be restricted to linear-`0–1` only (simpler parser) or keep the `dB` dual-form? I lean dual-form but flag the parser cost.
- Is `system_cue` BGM or SFX? It's arguably a one-shot sting, not a bed — stage-4 may move it out of the loopable-music enum into an SFX track type.
- Cue overlap policy: are two simultaneous cues (layered bed + sting) allowed, or is `bgm.md` strictly one-track-at-a-time? Current grammar assumes sequential, non-overlapping windows.
- Per-cue `start-end` vs. anchoring to shot ids (`shot03`): time-range is mux-friendly; shot-anchoring is edit-stable. Proposed time-range; flag if authors prefer shot anchors resolved to seconds at mux time.
