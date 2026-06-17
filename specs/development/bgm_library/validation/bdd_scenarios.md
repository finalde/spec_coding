---
worker_id: level-specialist-02-bdd_scenarios
stage: 5
role: level-specialist
level: bdd_scenarios
status: complete
blockers: []
confidence: high
---

# BDD scenarios — bgm_library

Feature-level behaviors from the user's perspective, mirroring the actor/voice library
patterns (`ActorGrid`, `VoiceGrid`, `CastingView`, `ActorPoolGenerator`) that `BgmGrid`
and the BGM generation modal copy. Each scenario asserts on **what the user observes**
(rendered DOM, played audio, written files, exit codes), never on implementation internals.

Severity legend (per `validation/general.md` + `development.md`): golden-path scenario
failure = `blocker`; latent render error / deep-link blank page = `critical`; subprocess
error not surfaced to UI = `blocker` (silent failure); license/商用 metadata wrong = `blocker`
per spec anchor 7. The 12-category enum is the canonical filter dimension; scenarios use a
representative subset in tables.

The 12 categories: `tension` / `combat` / `climax_hype` / `faceslap` / `tragic` / `warm` /
`romance_pain` / `suspense` / `daily` / `flashback` / `theme_open` / `system_cue`.

---

## Feature: BGM library grid rendering

As a drama author
I want to browse the shared BGM pool in a grid
So that I can find a reusable cue by ear instead of re-generating one

Background:
  Given the webapp is running against `ai_videos/_bgm/`
  And the route `/api/media` serves `.mp3` as `audio/mpeg`

### Scenario: grid renders one tile per BGM with metadata chips
  Given the BGM pool contains the following entries
    | id        | category    | bpm | duration | intensity | loopable |
    | bgm_0001  | tension     | 120 | 30       | 4         | true     |
    | bgm_0002  | combat      | 140 | 24       | 5         | true     |
    | bgm_0003  | warm        | 72  | 40       | 2         | false    |
  When I open the BGM library view
  Then I see 3 tiles
  And the tile for `bgm_0001` shows its id, a `tension` chip, a `120 bpm` chip, and an intensity indicator
  And each tile with an `.mp3` exposes a play/preview control
  And the header count reads "3 / 3"
  # Mirrors VoiceGrid header "{filtered} / {total}".

### Scenario: count reflects filter vs total
  Given the pool contains 10 BGM across `tension` and `combat`
  And 4 are `tension`
  When I filter category to `tension`
  Then the header count reads "4 / 10"
  And exactly 4 tiles are visible

### Scenario Outline: a tile with prompt-only entry (no mp3) shows a pending affordance
  # Spec keeps create-prompts optional (§4, §11); if an entry has .md but no .mp3,
  # the grid must not offer a broken play button (mirrors VoiceGrid "无样本").
  Given `bgm_0007` has a `.md` metadata file but no `.mp3`
  When I open the BGM library view
  Then the `bgm_0007` tile shows a "<pending_label>" indicator
  And the `bgm_0007` tile does NOT render an enabled play control

  Examples:
    | pending_label |
    | 无音频         |

---

## Feature: BGM library empty state

### Scenario: empty pool shows guidance, not a blank grid
  Given `ai_videos/_bgm/` exists but contains no `bgm_NNNN/` folders
  When I open the BGM library view
  Then I see an empty-state panel with the count "(0)"
  And the panel text tells me how to generate the first BGM (sidebar `_bgm/` 行 "🎵 生成 BGM" 入口)
  And no error banner is shown
  # Parity with ActorGrid / VoiceGrid empty states — informative, not an error.

### Scenario: load failure shows an error banner with retry, not the empty state
  Given the BGM list endpoint returns a 500
  When I open the BGM library view
  Then I see an alert banner reading "加载失败" with the status
  And I see a "重试" button
  And I do NOT see the empty-state guidance (which would mislead the user into thinking the pool is empty)

---

## Feature: BGM category filter

As an author
I want to narrow the grid by emotion category
So that I only audition cues that fit the beat

### Scenario Outline: filtering by category shows only matching BGM
  Given the pool contains
    | id       | category    |
    | bgm_0001 | tension     |
    | bgm_0002 | tension     |
    | bgm_0003 | combat      |
    | bgm_0004 | tragic      |
    | bgm_0005 | system_cue  |
  When I select category "<category>"
  Then I see exactly <visible_count> tiles
  And every visible tile's category chip reads "<category>"

  Examples:
    | category    | visible_count |
    | tension     | 2             |
    | combat      | 1             |
    | tragic      | 1             |
    | system_cue  | 1             |
    | daily       | 0             |

### Scenario: clearing the filter restores the full pool
  Given I have filtered to `combat` and see 1 tile
  When I reset the category filter to "全部"
  Then all 5 tiles are visible again

### Scenario: the filter offers all 12 categories
  When I open the category filter dropdown
  Then I see options for all 12 categories plus an "全部" option
  # Guards against a hard-coded subset drifting from the BgmAttrs enum.

---

## Feature: BGM audio preview

As an author
I want to play a BGM in place
So that I can judge it without leaving the grid

### Scenario: clicking play streams the mp3 and marks the tile as playing
  Given `bgm_0001` has an `.mp3`
  When I click the play control on the `bgm_0001` tile
  Then an `<audio>` source resolves to `mediaUrl("ai_videos/_bgm/tension/bgm_0001/bgm_0001.mp3")`
  And the `bgm_0001` tile shows a playing/pause state
  And no console error is emitted
  # Mirrors VoiceGrid playSample(): new Audio(mediaUrl(...)), onended→clear, onpause→clear.

### Scenario: starting a second preview stops the first
  Given `bgm_0001` is currently playing
  When I click play on `bgm_0002`
  Then `bgm_0001` stops
  And only `bgm_0002` shows the playing state
  # Single audioRef; previous .pause() before new Audio().

### Scenario: a media fetch failure surfaces a toast, not a silent no-op
  Given the `.mp3` for `bgm_0003` 404s
  When I click play on `bgm_0003`
  Then I see a "播放失败" toast
  And the tile is not stuck in the playing state

---

## Feature: generate a new BGM from the form

As an author
I want to fill a category/duration/bpm/intensity/instruments form and generate a cue
So that the pool grows with cues I need on demand

The generate flow mirrors `ActorPoolGenerator`: a preview step renders the exact
Stable Audio prompt the subprocess will run, then a confirm fires
`bgm__command.generate` → `tools/stableaudio_gen.py`.

### Scenario: opening the generate modal shows the form fields
  When I open "🎵 生成 BGM"
  Then I see a category dropdown listing all 12 categories
  And I see a duration input
  And I see a bpm input
  And I see an intensity control (1–5)
  And I see an instruments input
  And I see a "预览 prompt" action

### Scenario: previewing renders the Stable Audio prompt with the form values inlined
  Given I have filled the form
    | field       | value                      |
    | category    | tension                    |
    | duration    | 30                         |
    | bpm         | 120                        |
    | intensity   | 4                          |
    | instruments | low strings, taiko, pulse  |
  When I click "预览 prompt"
  Then I see an English Stable Audio prompt
  And the prompt reflects the `tension` template with bpm 120 / intensity 4 / the named instruments slotted in
  And the prompt is the same text that the subprocess will receive (a `--dry-run` round-trip would print it byte-identical)
  # development.md §10: parser/round-trip must match real upstream output, not a hand fixture.

### Scenario: confirming generation writes the mp3 + metadata and the new tile appears
  Given I previewed a `tension` BGM at 30s / 120 bpm / intensity 4
  And the highest existing id across all categories is `bgm_0042`
  When I confirm generation
  Then `bgm__command.generate` runs `tools/stableaudio_gen.py` as a subprocess
  And a new folder `ai_videos/_bgm/tension/bgm_0043/` is created
  And `ai_videos/_bgm/tension/bgm_0043/bgm_0043.mp3` exists
  And `ai_videos/_bgm/tension/bgm_0043/bgm_0043.md` contains a metadata table with
    | field     | value                            |
    | category  | tension                          |
    | bpm       | 120                              |
    | duration  | 30                               |
    | intensity | 4                                |
    | generator | stable_audio                     |
    | model     | stable-audio-open-1.0            |
    | license   | Stability AI Community License   |
  And the grid reloads and a `bgm_0043` tile is visible
  # id allocated by global scan-max+1 across categories (spec §3, anchor 2).

### Scenario: id allocation scans across categories, not within one
  Given the pool has `tension/bgm_0040` and `combat/bgm_0041`
  When I generate a new `tragic` BGM
  Then the new id is `bgm_0042`
  And it is placed under `tragic/bgm_0042/`
  # Differs from actor's flat allocation; cross-category max+1 with mkdir(exist_ok=False).

### Scenario: two concurrent generations never collide on an id
  Given two generate requests fire in the same tick
  When both allocate ids
  Then they receive distinct ids
  And neither overwrites the other's folder
  # mkdir(exist_ok=False) atomic placeholder; one retries on EEXIST.

---

## Feature: generation in progress

### Scenario: the modal shows progress while the subprocess runs
  Given I confirmed a generation
  When the subprocess is still running
  Then I see a "生成中…" indicator
  And the confirm button is disabled
  And I can cancel/close

### Scenario: the grid does not show a half-written tile mid-generation
  Given a generation is in flight and the `.mp3` is not yet written
  When the grid reloads
  Then the in-progress entry either is absent or shows the pending (no-audio) affordance
  And no tile offers a play control over a non-existent `.mp3`

---

## Feature: generation failure (subprocess error surfaced to UI)

As an author
I want a clear error when generation fails
So that I am never left thinking it silently worked

### Scenario Outline: a subprocess failure surfaces a typed error to the UI
  Given generation will fail with "<failure>"
  When I confirm generation
  Then `bgm__command.generate` maps it to "<error_kind>"
  And I see an error toast/banner showing "<error_kind>"
  And no orphaned half-written `bgm_NNNN/` folder is left in the pool
  And no empty `.mp3` is presented as a playable tile

  Examples:
    | failure                                   | error_kind              |
    | stableaudio_gen.py missing / not on disk  | StableAudioMissingError |
    | torch/CUDA error, non-zero exit code      | StableAudioFailedError  |
    | ffmpeg mp3 encode step fails              | StableAudioFailedError  |

### Scenario: a failed generation does not increment the visible pool
  Given the pool shows "12 / 12"
  When a generation fails with `StableAudioFailedError`
  Then the header count still reads "12 / 12"
  And the error is visible to the user

---

## Feature: assignments panel — "which dramas reference this BGM"

As an author
I want to see which episodes reference a BGM
So that I know the blast radius before deleting or replacing it

Reverse lookup scans `ai_videos/<drama>/episodes/ep*/bgm.md` (and short-root `bgm.md`)
for `bgm_NNNN` tokens — NOT `casting.md` (spec §4.2). Pattern mirrors
`find_assignments_for_actor` / the VoiceView assignments section.

### Scenario: a referenced BGM lists its referencing episodes
  Given `ai_videos/wushen_juexing/episodes/ep01/bgm.md` contains a cue line referencing `bgm_0001`
  And `ai_videos/wushen_juexing/episodes/ep03/bgm.md` also references `bgm_0001`
  When I open `bgm_0001`'s detail / assignments panel
  Then I see 2 assignment rows
    | drama          | episode |
    | wushen_juexing | ep01    |
    | wushen_juexing | ep03    |

### Scenario: an unreferenced BGM shows an empty assignments state
  Given no `bgm.md` references `bgm_0099`
  When I open `bgm_0099`'s assignments panel
  Then I see an empty assignments state reading "(0)"
  And the delete control is enabled (nothing blocks removal)

### Scenario: a short's root-level bgm.md is scanned
  Given `ai_videos/my_short/bgm.md` (no episodes/ layout) references `bgm_0005`
  When I open `bgm_0005`'s assignments panel
  Then `my_short` appears as a referencing project

### Scenario: the scanner skips `_`-prefixed system folders
  Given `ai_videos/_bgm/` and `ai_videos/_deleted/` exist
  When assignments are computed for any BGM
  Then no `_`-prefixed directory is scanned as a drama
  # Same skip rule as casting/actor reverse-lookup.

### Scenario: deleting a referenced BGM is blocked (or warns) per the actor/voice contract
  # Judgment call: spec §4 says "照搬" the actor/voice delete contract; VoiceView blocks
  # delete while assigned. Validation asserts the same guard for BGM. If the team chooses
  # soft-delete-with-warning instead, this scenario flips to a confirm dialog — flag at sign-off.
  Given `bgm_0001` is referenced by 2 episodes
  When I attempt to delete `bgm_0001`
  Then deletion is refused with a message naming the 2 referencing episodes
  And `bgm_0001` is NOT moved to `_deleted/_bgm/`

---

## Feature: cue authoring flow (`bgm.md` per episode / short)

As an author
I want a grep-able, human-readable cue timeline per episode
So that the same file serves reverse-lookup, the mux tool, and my own reading

Cue line format (spec §8): `起-止(秒) bgm_NNNN | vol= | duck=on/off | fade=in/out`.

### Scenario: a well-formed cue file satisfies all three consumers
  Given an episode `bgm.md` containing
    """
    0-12 bgm_0001 | vol=0.6 | duck=off | fade=in
    12-40 bgm_0002 | vol=0.8 | duck=on | fade=out
    """
  Then `grep -o 'bgm_[0-9]\{4\}'` returns `bgm_0001` and `bgm_0002` (reverse-lookup consumer)
  And a line parser yields 2 cue records with start/end/id/vol/duck/fade fields (mux consumer)
  And the file is plain text a human can read top-to-bottom (author consumer)

### Scenario Outline: cue fields map one-to-one onto mux behavior
  Given a cue line "<line>"
  When the cue is parsed
  Then it requests "<effect>"

  Examples:
    | line                                    | effect                                       |
    | 0-12 bgm_0001 \| duck=on \| fade=in     | sidechaincompress + afade in                 |
    | 0-12 bgm_0001 \| duck=off \| fade=out   | no sidechaincompress, BGM laid flat + afade out |
    | 0-30 bgm_0001 \| vol=0.5                | bgm volume scaled to 0.5 (linear, mux-side dB convert) |

### Scenario: a malformed cue line is reported, not silently dropped
  Given a `bgm.md` line "garbage with no bgm token"
  When the file is parsed
  Then the line is flagged as unparseable (with its line number)
  And valid lines around it still parse
  # A silently-skipped cue is a hidden bug (general.md §3).

### Scenario: vol is interpreted as 0–1 linear
  # Open point (§11): vol unit. Spec leans 0–1 linear, mux converts to dB.
  # Judgment call: scenario fixes 0–1 linear; flag to user if dB is preferred.
  Given a cue with `vol=0.5`
  When mux applies it
  Then the BGM amplitude is scaled to half (≈ −6 dB), not interpreted as 0.5 dB

---

## Feature: mux tool behavior (`tools/mux_av.py` v1)

As an author
I want one video + one dialogue MP3 + one BGM muxed into a finished cut
So that dialogue stays clear and BGM ducks under speech

Pure ffmpeg, `-c:v copy` (no video re-encode). Filtergraph order is load-bearing:
`[bgm][dialogue]` into `sidechaincompress` (BGM ducked, dialogue is the sidechain key) →
`amix=normalize=0` (so dialogue is NOT silently halved) → `-c:a aac`.

### Scenario: video + dialogue + bgm produces a finished cut without re-encoding video
  Given a 30s video, a 28s dialogue MP3, and a 30s BGM
  When I run `mux_av.py --video v.mp4 --dialogue d.mp3 --bgm b.mp3 --out out.mp4`
  Then `out.mp4` is produced with exit code 0
  And the video stream is bit-identical to the input (`-c:v copy`, no re-encode)
  And the audio stream is AAC

### Scenario: dialogue is not halved by amix
  Given dialogue and BGM are mixed
  When the output audio is measured
  Then the dialogue loudness is preserved (amix uses `normalize=0`)
  # The classic amix=normalize=1 bug would silently halve the dialogue.

### Scenario: ducking lowers BGM only under speech
  Given a dialogue segment from 5s–10s
  When ducking is enabled (`duck=on` / default threshold/ratio)
  Then during 5s–10s the BGM level is reduced relative to silent stretches
  And outside speech the BGM returns to its set volume
  And the sidechain order is `[bgm][dialogue]` (BGM ducked, dialogue is the key — not reversed)

### Scenario Outline: missing-input behavior matrix
  Given the inputs "<inputs>"
  When I run mux
  Then "<result>"

  Examples:
    | inputs                  | result                                                        |
    | video + dialogue + bgm  | full mix with ducking                                         |
    | video + bgm (no dialogue) | BGM laid flat over video, no ducking, exit 0                |
    | video + dialogue (no bgm) | dialogue-only audio, exit 0                                  |
    | video only              | passthrough / clear error per spec — flag exact behavior at sign-off |

### Scenario: BGM shorter than the video is looped and padded, not truncated to silence
  Given a 60s video and a 20s loopable BGM
  When I run mux with looping
  Then the BGM covers the full 60s via `-stream_loop`/`aloop`
  And any trailing gap is `apad` silence, never an abrupt cut
  And `afade` in/out is applied per the fade flags

### Scenario: a non-loopable BGM shorter than the video pads with silence instead of looping
  Given a 60s video and a 20s BGM marked `loopable=false`
  When I run mux
  Then the BGM plays once and the remainder is padded with silence (no loop seam)

### Scenario: v1 consumes a single BGM, not a multi-cue bgm.md
  # Spec §7 / §1: multi-cue bgm.md orchestration is explicitly deferred. general.md §6
  # requires surfacing every carve-out at sign-off.
  Given a `bgm.md` with 3 cue lines
  When I run mux_av.py v1
  Then it consumes exactly one BGM (the one passed via `--bgm`)
  And it does NOT auto-stitch all 3 cues
  And this carve-out is surfaced to the user at stage-5 sign-off for confirmation

---

## Feature: license & reproducibility metadata

### Scenario: every generated BGM records the商用-safe license
  When any BGM is generated
  Then its `.md` records `license = Stability AI Community License`
  And `generator = stable_audio`, `model = stable-audio-open-1.0`
  And the README states the商用 boundary (annual revenue < $1M) and that seed is best-effort
  # Spec anchor 7; license correctness = blocker (商用 safety is a stated goal).

### Scenario: seed is best-effort, not a hard reproducibility guarantee
  Given the same prompt and seed are used twice
  When two BGM are generated
  Then the metadata records the seed on both
  And the README/spec notes that audio reproduction is best-effort (unlike actor's hard repro)
  # Asserts the documentation contract, not byte-equality of audio.

---

## Carve-outs surfaced for stage-5 sign-off (general.md §6)

- **Multi-cue `bgm.md` auto-orchestration is out of scope (v1).** mux consumes a single BGM.
  A documented cue-timeline format exists but nothing stitches it end-to-end yet — confirm intended.
- **`generate-diverse` / archetype omitted** (actor has them). Confirm BGM intentionally has no
  diversity-batch generation.
- **`create-prompts` offline backfill is optional.** If shipped, prompt-only (no-mp3) entries must
  render with the pending affordance (covered above); if not shipped, the no-mp3 path is unreachable.
- **`system_cue` classified as BGM, not SFX** (spec §11, self-defined). Confirm.
- **vol unit = 0–1 linear** (open point §11). Scenarios assume linear; flag if dB preferred.
- **Delete-while-referenced behavior** (block vs warn) assumed to copy the voice "block" contract;
  confirm.

## Notes / judgment calls

- Exact pending-label text ("无音频"), header-count format ("N / M"), and empty-state copy are
  inferred from VoiceGrid/ActorGrid parity; treat as illustrative, not contractual.
- Whether the assignments panel lives on a BGM detail page (like VoiceView) or inline on the tile
  is a UI choice the spec leaves open; scenarios say "detail / assignments panel" to stay agnostic.
- The mux "video only" branch result is not pinned in the spec; scenario flags it for explicit
  decision rather than asserting a behavior.
