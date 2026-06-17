---
worker_id: researcher-02-ffmpeg-duck-mux
stage: 3
role: researcher
angle: ffmpeg-duck-mux
status: complete
blockers: []
confidence: high
---

# Angle: ffmpeg-duck-mux

## 1. What this angle covers

The concrete ffmpeg approach `tools/mux_av.py` must implement: take a video MP4
(silent or dialogue-less) + a dialogue/台词 MP3 + a BGM MP3, and produce one
finished MP4 where (a) the video stream is **copied without re-encoding**, (b) the
BGM **automatically ducks under the dialogue** via `sidechaincompress` keyed on the
dialogue, (c) dialogue stays at full level, and (d) BGM is looped/trimmed/faded to
the video duration. Also: silence-padding when dialogue is shorter than video,
per-cue offset/volume, and whether pure ffmpeg suffices vs. needing python/pydub.

## 2. Key findings (with citations + the command)

### 2.1 `sidechaincompress` is the right filter; the routing is the gotcha

`sidechaincompress` takes **two audio inputs**: the **first** is the signal that gets
compressed (the BGM), the **second** is the *sidechain key* that drives the gain
reduction (the dialogue). So `[bgm][dialogue]sidechaincompress=...` lowers the BGM
whenever the dialogue is loud. This is the single most-confused point — reversing the
inputs ducks the voice under the music, which is backwards.

Official parameter defaults/ranges (from the ffmpeg filter docs):

| param | default | range | meaning for ducking |
|---|---|---|---|
| `threshold` | 0.125 | 0.00097563–1 | dialogue level above which BGM starts ducking. For a normalized voice MP3, **0.02–0.05** triggers reliably; 0.125 is too high (only ducks on shouts). |
| `ratio` | 2 | 1–20 | how hard BGM is pushed down. **6–12** gives a clear, audible duck; 2 is barely noticeable. |
| `attack` | 20 ms | 0.01–2000 | how fast BGM drops when voice starts. **20–60 ms** = snappy without a click. |
| `release` | 250 ms | 0.01–9000 | how fast BGM returns after voice stops. **300–800 ms** avoids "pumping" between words. |
| `makeup` | 1 | 1–64 | post-gain on the compressed BGM; leave at 1. |
| `knee` | 2.82843 | 1–8 | soft-knee smoothness; default fine. |
| `level_sc` | 1 | — | gain applied to the sidechain key before detection — raise if the voice MP3 is quiet so ducking still triggers. |
| `detection` | rms | peak/rms | `rms` (default) is smoother for speech. |

Source: <https://ffmpeg.org/ffmpeg-filters.html#sidechaincompress> (confirmed defaults
and ranges via WebFetch).

### 2.2 Canonical, copy-pasteable ducking command (confident)

A widely-published, working pattern (verified phrasing from two independent sources):

```bash
ffmpeg -y \
  -i input_video.mp4 \
  -i dialogue.mp3 \
  -i bgm.mp3 \
  -filter_complex "\
    [2:a]aloop=loop=-1:size=2e9,afade=t=in:st=0:d=1.5[bgm_loop];\
    [bgm_loop][1:a]sidechaincompress=threshold=0.03:ratio=8:attack=40:release=400:level_sc=1[bgm_ducked];\
    [1:a]apad[voice];\
    [voice][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,afade=t=out:st=58:d=2[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k -shortest \
  output.mp4
```

What each stage does:

- `[2:a]aloop=loop=-1:size=2e9` — loop the BGM indefinitely so it covers any video
  length (`size` is the per-loop sample buffer; a large value loops the whole clip).
  `-stream_loop -1 -i bgm.mp3` on the **input side** is an equivalent alternative and is
  often cheaper, but it must be placed *before* `-i bgm.mp3`, which complicates dynamic
  arg building in python — `aloop` inside the graph keeps all the looping logic in one
  place.
- `afade=t=in:st=0:d=1.5` — 1.5 s BGM fade-in; `afade=t=out:st=58:d=2` on the mix tail
  is the fade-out (start time = video_duration − fade_dur, computed in python).
- `[bgm_loop][1:a]sidechaincompress=...` — **BGM first, dialogue (`[1:a]`) second**:
  duck the looped BGM under the voice.
- `[1:a]apad` — pad the dialogue with trailing silence so it never ends before the
  video (relevant for `amix=duration=first` and for `-shortest`).
- `amix=inputs=2:duration=first:normalize=0` — mix full-level voice with ducked BGM.
  **`normalize=0` is critical**: `amix` defaults to dividing each input by N (here ×0.5),
  which silently halves the dialogue. With `normalize=0` the voice stays at full level
  and you control BGM level explicitly (via a `volume` filter before the duck, e.g.
  `[2:a]...,volume=0.6`).
- `-map 0:v -map "[aout]" -c:v copy` — video stream copied verbatim (no re-encode);
  only the new audio is encoded.
- `-c:a aac -b:a 192k` — AAC is the MP4-native audio codec.
- `-shortest` + `duration=first` — bound output to the video length.

Sources for the command shape and amix/afade usage:
<https://www.ffmpeg.media/articles/extract-replace-mix-audio-tracks>,
<https://ffmpeg.org/ffmpeg-filters.html#sidechaincompress>,
ffmpeg-user list confirming sidechain ducking is the technique
<https://ffmpeg.org/pipermail/ffmpeg-user/2018-August/040933.html>.

**Confidence note:** `aloop=size=2e9` and the `level_sc`/`normalize=0` flags I am
highly confident on. The exact `threshold`/`ratio` *values* are taste-dependent — the
ranges above are the safe band, but they should be **CLI-exposed** so the user tunes
per-track rather than hard-coded.

### 2.3 amix vs amerge

Use **`amix`** (sums to one stereo stream, supports `duration`/`normalize`), not
`amerge` (which *concatenates channels* → a 4-channel file, wrong here). Keep dialogue
full-level via `amix=normalize=0` and set BGM level with a `volume` filter before the
duck.

### 2.4 Dialogue shorter than video → silence padding

Two complementary tools:
- `apad` (already in the graph) appends trailing silence to the dialogue so the mix and
  `-shortest` align to the video, not to the (shorter) voice.
- `adelay=<ms>|<ms>` if a cue's dialogue must *start* at an offset t=Xs (leading silence).
  For BGM cues with a start offset, `adelay` on the BGM branch (or trimming the looped
  BGM with `atrim=start=X`) positions the music start.

### 2.5 Per-cue volume / offset (bgm cue timeline)

The interview locks a per-episode `bgm.md` cue timeline (bgm_NNNN + 起止/音量/duck). A
single `sidechaincompress` pass handles the global duck, but **multiple cues with
different start/stop/volume per segment are not expressible in one static filtergraph**
cleanly. Two options: (a) python builds the filtergraph dynamically — one BGM input per
cue, each with `atrim`/`adelay`/`volume`, all `amix`'d — still pure ffmpeg, just
programmatically assembled; (b) for v1, support **one BGM per mux call** (whole-clip
single track) and let multi-cue stitching be a later iteration. Recommend (b) for the
first cut, with the CLI accepting `--bgm-start`/`--bgm-volume` for that single track.

### 2.6 Pure ffmpeg suffices

No pydub/python audio processing needed — ffmpeg does looping, ducking, fading,
padding, mixing, and copy-mux in one pass. Python's only job is to **probe the video
duration** (`ffprobe -v error -show_entries format=duration -of csv=p=0 input.mp4`) to
compute the fade-out start time, and to **assemble the filtergraph string** + run via
`subprocess`. pydub would force a decode→re-encode round-trip and lose the `-c:v copy`
benefit, so avoid it.

## 3. Implications for the spec (concrete)

### 3.1 `mux_av.py` CLI signature

```
python tools/mux_av.py \
  --video        path/to/video.mp4        # required; video stream copied
  --dialogue     path/to/dialogue.mp3     # optional; if absent → no ducking, BGM at base level
  --bgm          path/to/bgm.mp3          # optional; if absent → just remux dialogue
  --out          path/to/output.mp4       # required
  --bgm-volume   0.6                       # base BGM gain before ducking (default 0.6)
  --duck-threshold 0.03                    # sidechaincompress threshold (default 0.03)
  --duck-ratio   8                         # (default 8)
  --duck-attack  40                        # ms (default 40)
  --duck-release 400                       # ms (default 400)
  --bgm-start    0                         # seconds offset into BGM / cue start (default 0)
  --fade-in      1.5                        # BGM fade-in seconds (default 1.5)
  --fade-out     2.0                        # BGM fade-out seconds (default 2.0)
  --audio-bitrate 192k
```

Behavior matrix:
- video + dialogue + bgm → full duck-mux (the §2.2 command).
- video + dialogue only → map voice to audio, `-c:v copy -c:a aac`.
- video + bgm only → BGM at `--bgm-volume`, no sidechain (no key track).
- video only → passthrough remux (or error — author's choice; recommend error).

### 3.2 Filtergraph (the load-bearing string python must build)

```
[bgm]volume={bgm_volume},aloop=loop=-1:size=2e9,atrim=start={bgm_start},asetpts=PTS-STARTPTS,
     afade=t=in:st=0:d={fade_in}[bgm_loop];
[bgm_loop][dlg]sidechaincompress=threshold={th}:ratio={ratio}:attack={atk}:release={rel}[bgm_ducked];
[dlg]apad[voice];
[voice][bgm_ducked]amix=inputs=2:duration=first:normalize=0,afade=t=out:st={dur-fade_out}:d={fade_out}[aout]
```
with `-map 0:v -map [aout] -c:v copy -c:a aac -b:a {bitrate} -shortest`. `{dur}` comes
from `ffprobe`. Note `[dlg]` (the dialogue) is reused twice (`asplit` not needed because
ffmpeg auto-splits a label used by multiple consumers — but if ffmpeg errors on label
reuse, insert `[1:a]asplit=2[dlg][dlgkey]` and feed `[dlgkey]` to the sidechain).

### 3.3 Repo placement & deps

Pure-ffmpeg + `subprocess`; the only runtime dependency is a system `ffmpeg`/`ffprobe`
on PATH (no torch/audiocraft — those live in the separate `musicgen_gen.py` per the
interview). Strong-typed OOP per CLAUDE.md general coding rules; one `class` building the
filtergraph + one entry function.

## 4. Open questions

1. **asplit reuse**: does this ffmpeg build accept a label (`[dlg]`) consumed by two
   filters, or must we `asplit` explicitly? Low risk — `asplit=2` is the safe default;
   recommend always emitting it.
2. **Multi-cue per episode**: §2.5 — is v1 single-BGM-per-call acceptable, or must
   `mux_av.py` consume the whole `bgm.md` timeline and stitch multiple cues in one pass?
   Affects whether the filtergraph is static or dynamically assembled. Recommend single-
   track v1.
3. **Duck defaults**: confirm `threshold=0.03 / ratio=8 / attack=40 / release=400` as
   project defaults, or expose-only with no opinionated default. Values are in the safe
   band but taste-dependent; tuning belongs to the user.
4. **Dialogue loudness normalization**: should we `loudnorm`/`level_sc`-boost a quiet
   voice MP3 before it keys the sidechain, so soft TTS still triggers ducking? Probably
   yes via `level_sc`, but adds a parameter.
