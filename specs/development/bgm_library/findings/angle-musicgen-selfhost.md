---
worker_id: researcher-01-musicgen-selfhost
stage: 3
role: researcher
angle: musicgen-selfhost
status: complete
blockers: []
confidence: high
---

# Angle — MusicGen self-host (deterministic `tools/musicgen_gen.py`)

## 1. What this angle covers

How to self-host Meta's MusicGen (via the AudioCraft library) so a `tools/musicgen_gen.py`
subprocess — mirroring `tools/kling_autopilot/` — can produce **one BGM mp3 per
(prompt, seed, duration)** call, deterministically and royalty-free. Concretely: install
& dependency footprint, CPU-vs-GPU feasibility, which model variant to default to, max
length + how to get longer/loopable tracks, sample-rate/mp3 output, seed/determinism,
prompt design for mood BGM, and the commercial-license picture.

## 2. Key findings (with citations)

**Install & deps.** AudioCraft is the official Meta library exposing MusicGen + the EnCodec
codec. Stable install: `pip install -U audiocraft`; it pins **Python 3.9 and PyTorch 2.1.0**
(install torch *before* audiocraft so xformers builds against it). **ffmpeg is required**
for audio I/O. Models are pulled from Hugging Face (`facebook/musicgen-*`) on first use and
cached. ([AudioCraft GitHub README](https://github.com/facebookresearch/audiocraft),
[MUSICGEN.md](https://github.com/facebookresearch/audiocraft/blob/main/docs/MUSICGEN.md))

**Model variants & VRAM.** Ten HF checkpoints exist
([MUSICGEN.md](https://github.com/facebookresearch/audiocraft/blob/main/docs/MUSICGEN.md)):

| id | params | VRAM (approx) | notes |
|---|---|---|---|
| `facebook/musicgen-small` | 300M | ~4 GB | fastest; lowest fidelity |
| `facebook/musicgen-medium` | 1.5B | ~16 GB rec. | "best quality/compute trade-off" per docs |
| `facebook/musicgen-large` | 3.3B | ~10–16 GB+ | best fidelity, slowest |
| `facebook/musicgen-melody` | 1.5B | ~8 GB | text+melody conditioning |
| `facebook/musicgen-stereo-*` | — | similar | stereo fine-tunes of each above |

For **instrumental short-drama mood BGM**, default to **`musicgen-small`** when running CPU/modest
GPU (it's the only size that's tolerable without a strong GPU), and offer **`musicgen-medium`**
(or `-stereo-medium`) as the quality tier on a ≥16 GB GPU. MusicGen is already instrumental-only
(no vocals), so it fits BGM directly. (VRAM figures are community-reported, not in the official
card — flagged as approximate.) ([HF musicgen-large card](https://www.aimodels.fyi/models/huggingFace/musicgen-large-facebook),
[MUSICGEN.md](https://github.com/facebookresearch/audiocraft/blob/main/docs/MUSICGEN.md))

**Max length & longer/loopable tracks.** A single forward pass is capped at **30 s** by the
sinusoidal positional embeddings (1503 tokens). For `duration > 30`, AudioCraft auto-chains:
it keeps the tail of the previous window as an audio prompt (`extend_stride` controls the
hop) and continues — i.e. **continuation is the mechanism for longer tracks**, exposed via
`set_generation_params(duration=…, extend_stride=…)` and `generate_continuation(...)`.
There is **no built-in seamless-loop maker**; a loop is an author/render concern (crossfade
the clip onto itself in ffmpeg, or generate a slightly longer clip and trim to a bar). The
BGM library should treat "loopable" as a metadata flag the prompt aims for, not a guaranteed
gapless loop. ([HF transformers MusicGen docs](https://huggingface.co/docs/transformers/model_doc/musicgen),
[AudioCraft API docs](https://facebookresearch.github.io/audiocraft/api_docs/audiocraft/models/musicgen.html))

**Output format.** `model.sample_rate` is **32 kHz**. Canonical write is
`audio_write(stem, wav.cpu(), model.sample_rate, strategy="loudness", loudness_compressor=True)`,
which normalizes to **−14 dB LUFS** and writes a `.wav` by default. To get **mp3** either pass
a format/encoder to `audio_write` (recent AudioCraft supports `format="mp3"` when ffmpeg is
present) or, more robustly for our pipeline, write the wav then transcode with ffmpeg
(`ffmpeg -i out.wav -codec:a libmp3lame -q:a 2 bgm_NNNN.mp3`). The −14 LUFS target is also
convenient for the later sidechain-duck mux. ([MUSICGEN.md](https://github.com/facebookresearch/audiocraft/blob/main/docs/MUSICGEN.md))

**Determinism (the load-bearing caveat).** `set_generation_params` has **no `seed` argument**
(its knobs are `use_sampling, top_k, top_p, temperature, duration, cfg_coef, extend_stride`).
Reproducibility is done by seeding torch *before* `generate`: `torch.manual_seed(seed)` (and
`torch.cuda.manual_seed_all(seed)` on GPU). **Important regression:** AudioCraft issue #111
reports that since ~0.0.2 a fixed seed reproduces only the **first ~2–3 seconds**, then
diverges; full-clip determinism that worked in 0.0.1 was lost. Community workaround: drive
sampling through an explicit `torch.Generator(...).manual_seed(seed)` passed into the
sampling call. So a stored `seed` is a **best-effort** reproducer (good for short stings,
weakening over a 30 s clip) — NOT a hard guarantee like an actor still-image seed. The honest
contract is "seed + prompt + model + duration recorded for re-generation," with a warning that
exact bit-reproduction across versions/hardware isn't assured.
([issue #111](https://github.com/facebookresearch/audiocraft/issues/111),
[issue #402](https://github.com/facebookresearch/audiocraft/issues/402),
[AudioCraft API docs](https://facebookresearch.github.io/audiocraft/api_docs/audiocraft/models/musicgen.html))

**Generation time.** Generation is autoregressive and roughly **linear in duration**. On GPU
it's well below realtime (high-end GPUs hit ~4–6× realtime; a modest GPU like a T4/3060 still
does a 30 s `small`/`medium` clip in tens of seconds). **CPU is feasible only for `small`**
and is slow — community reports put a 30 s `small` clip at **several minutes** on CPU, and
`medium`/`large` on CPU are impractical. (No official CPU benchmark table exists — these are
community figures, flagged.) Practical implication: default `small`, make the model an arg,
and run generation as a detached subprocess with progress, never inline in a request thread.
([Spheron deploy guide](https://www.spheron.network/blog/deploy-open-source-ai-music-generation-gpu-cloud-2026/),
[MUSICGEN.md](https://github.com/facebookresearch/audiocraft/blob/main/docs/MUSICGEN.md))

**Prompt design for mood BGM.** Text conditioning works on a frozen T5 text encoder; effective
prompts stack **genre/style + instrumentation + mood + tempo(BPM)**. BPM and instrument names
*do* steer output (e.g. "tense cinematic confrontation, low strings and timpani, staccato,
90 bpm, building dread, instrumental"); keyword-stack style ("Cinematic, Tense, Strings,
Timpani, Percussion, Action") also works. Keep prompts instrumental ("no vocals"), one mood
per clip. This maps cleanly onto our fixed mood-enum categories — each category gets a default
prompt template with slots for bpm/intensity.
([Scenario MusicGen essentials](https://help.scenario.com/articles/9565411648-meta-musicgen-text-to-music-the-essentials),
[Envato prompt guide](https://elements.envato.com/learn/ai-music-prompts),
[musicgenai prompts](https://musicgenai.org/musicgen-prompts/))

**License (commercial).** The AudioCraft **code is MIT**. The **MusicGen model weights are
CC-BY-NC 4.0 — NON-commercial**. This is the key risk for the spec's claim that "weights are
commercially safe." The MIT code is fine commercially; the *weights* are not, per Meta's own
cards. The library `license` metadata field is therefore essential and the project should
treat MusicGen-generated BGM as **non-commercial-by-default** unless legal sign-off says
otherwise (or a permissively-licensed model is swapped in later — e.g. Stable Audio Open /
other CC-BY models). **I could not verify any commercial grant for the weights** — every source
I found states CC-BY-NC. This contradicts the revised prompt and must be surfaced to the user.
([HF musicgen-large overview](https://www.aimodels.fyi/models/huggingFace/musicgen-large-facebook),
[AudioCraft GitHub](https://github.com/facebookresearch/audiocraft))

## 3. Implications for the spec

**`tools/musicgen_gen.py` CLI (mirror `kling_autopilot/run.py` shape — argparse, single-purpose):**

- `--prompt <text>` (or `--prompt-file`) — the conditioning text.
- `--seed <int>` — `torch.manual_seed(seed)` (+ `cuda.manual_seed_all`) before `generate`;
  recorded for re-gen. Document that determinism is best-effort (issue #111).
- `--duration <float>` (3–N s) — `set_generation_params(duration=…)`; >30 s auto-continues,
  expose `--extend-stride`.
- `--model <id>` default `facebook/musicgen-small`; allow medium/large/stereo.
- `--out <path.mp3>` — write wav via `audio_write(strategy="loudness")` then ffmpeg→mp3
  (libmp3lame), or native `format="mp3"`; preserve 32 kHz unless `--resample`.
- `--dry-run` — print the resolved generation plan (model, seed, duration, prompt) without
  loading torch, mirroring kling_autopilot's `--dry-run`.
- Own `requirements.txt` (audiocraft, torch==2.1.0) isolated in the tools dir; webapp calls it
  by subprocess so the heavy torch/CUDA deps never enter the webapp process.

**`bgm__writer` must:** build the prompt from category template + bpm/mood/intensity params;
pick/record a `seed` (random if unspecified, like the actor seed); shell out to
`tools/musicgen_gen.py` with prompt/seed/duration/model/out; on success write
`ai_videos/_bgm/{category}/bgm_NNNN/bgm_NNNN.mp3` + the metadata table including
`generator: musicgen-<variant>`, `seed`, `sample_rate: 32000`, `duration`, `loopable`,
and **`license: CC-BY-NC-4.0`** (not "commercial"). Generation must run as a detached/streamed
subprocess (minutes on CPU), not block the request.

## 4. Open questions

- **License vs. prompt assumption.** Revised prompt says weights are "commercially safe";
  every source says **CC-BY-NC 4.0 (non-commercial)**. Needs user decision: accept
  non-commercial, get legal sign-off, or plan a swap to a commercially-licensed model.
- **Determinism guarantee strength.** Is "best-effort seed, first few seconds stable" acceptable
  given the actor library implies hard seed reproducibility? May need the `torch.Generator`
  workaround patched in, or accept non-bit-exact re-gen.
- **Target host.** Will generation run on a CPU-only box (→ default `small`, expect minutes) or
  is a GPU available (→ `medium`/`stereo`)? Drives default model + UX timeouts. Not specified.
- **mp3 write path** — confirm the installed AudioCraft version's `audio_write` supports
  `format="mp3"` directly vs. needing the ffmpeg transcode step (version-dependent; verify at impl).
- **Loop quality** — no native gapless loop; decide whether "loopable" means a crossfade pass in
  `mux_av.py`/render or just a metadata aspiration.
