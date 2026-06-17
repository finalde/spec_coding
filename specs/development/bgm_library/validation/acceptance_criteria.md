---
worker_id: level-specialist-01-acceptance_criteria
stage: 5
role: level-specialist
level: acceptance_criteria
status: complete
blockers: []
confidence: high
---

# Acceptance Criteria — bgm_library

Gherkin Given/When/Then, one scenario per primary flow of `final_specs/spec.md`.
Severity per `agent_refs/validation/general.md`: any criterion failure on a golden path = `blocker` (standard 3-revision-round cap). Carve-outs (§ Out-of-scope confirmations) surfaced per general.md principle 6.

Conventions used below:
- `_bgm` = `ai_videos/_bgm/`; `<cat>` ∈ the 12-emotion enum (`tension / combat / climax_hype / faceslap / tragic / warm / romance_pain / suspense / daily / flashback / theme_open / system_cue`).
- "the library" = the on-disk `_bgm/{category}/bgm_NNNN/` tree, the single source of truth (filesystem-derived, no cache).

---

## AC-1 — Generate a BGM via the UI/command produces mp3 + .md metadata table

```gherkin
Feature: Generate a BGM through the webapp command path

  Scenario: A category=combat generation writes bgm_NNNN.mp3 and its sidecar .md
    Given the BGM library is empty
    And tools/stableaudio_gen.py is available on the configured interpreter
    When a client POSTs to the bgm generate endpoint with
      | category   | combat |
      | duration   | 30     |
      | bpm        | 140    |
      | intensity  | 4      |
      | instruments| taiko drums, brass, low strings |
    Then bgm__command.generate runs subprocess.run([... stableaudio_gen.py ...]) exactly once
    And a folder ai_videos/_bgm/combat/bgm_0001/ is created
    And it contains bgm_0001.mp3 (non-empty, decodable mp3)
    And it contains bgm_0001.md whose metadata table carries the fields
        category, mood, bpm, duration, loopable, intensity (int 1-5),
        instruments, generator, model, seed, license, notes
    And the table is followed by a "## 生成 prompt" block containing the English Stable Audio prompt
    And the response JSON reports the new bgm id and its mp3 relative path
    And the webapp process imported no torch / stable-audio-tools module
        (heavy deps live only in the subprocess)

  Scenario: subprocess failure maps to a domain error, not a 500 traceback
    Given tools/stableaudio_gen.py exits non-zero (model load / inference failure)
    When a client POSTs a valid generate request
    Then bgm__command.generate raises StableAudioFailedError
    And the global FastAPI handler returns a structured JSON error (not an unhandled 500)
    And no partial bgm_NNNN/ folder is left behind containing a 0-byte mp3
        (judgment call: mirror actor reaper — an mp3-less folder must be reaped
         or never committed; flag as a finding if neither holds)

  Scenario: missing generator script is distinguishable from a runtime failure
    Given tools/stableaudio_gen.py does not exist at the configured path
    When a client POSTs a valid generate request
    Then bgm__command.generate raises StableAudioMissingError (distinct from StableAudioFailedError)
```

## AC-2 — Global-unique id allocation across categories (the {category}/ difference from actor)

```gherkin
Feature: bgm_NNNN ids are globally unique across all 12 category folders

  Scenario: next id is max-of-ALL-categories + 1, not per-category
    Given _bgm/combat/ contains bgm_0001/ and bgm_0003/
    And _bgm/tragic/ contains bgm_0002/
    And _bgm/warm/ contains bgm_0005/
    When a new BGM is generated with category=suspense
    Then the allocated id is bgm_0006 (global max 0005 + 1)
    And the folder created is _bgm/suspense/bgm_0006/
    And no id is reused from a deleted/soft-deleted slot
        (judgment call: allocator scans _bgm/*/bgm_* across every category,
         matching ^bgm_\d{4,}$, and takes max+1 — verify it does NOT scan a
         single category only, which is the actor-vs-bgm structural divergence)

  Scenario: id claim is atomic — concurrent generations never collide
    Given two generate requests run concurrently against an empty library
    When both attempt to claim the next id
    Then each lands in a distinct bgm_NNNN/ folder via mkdir(exist_ok=False)
    And no two folders share the same NNNN
    And neither request overwrites the other's mp3 or .md

  Scenario: id padding and regex contract hold
    Given any allocated bgm id
    Then it matches ^bgm_\d{4,}$ (zero-padded to at least 4 digits)
```

## AC-3 — Browse / filter by the 12 emotion categories in the UI

```gherkin
Feature: BgmGrid browses and filters the library by emotion category

  Scenario: grid lists every bgm with its category from the on-disk tree
    Given the library holds BGMs across combat, tragic, and warm
    When the user opens the BGM library view
    Then the grid renders one card per bgm_NNNN
    And each card shows the bgm's category (derived from its {category}/ folder)
    And the count of cards equals the count of bgm_NNNN/ folders on disk

  Scenario: filtering by a category narrows the grid to that category
    Given the library holds 3 combat BGMs and 2 tragic BGMs
    When the user selects the category filter "tragic"
    Then exactly the 2 tragic BGMs are shown
    And no combat BGM remains visible

  Scenario: the filter exposes exactly the 12 enum categories
    When the user opens the category filter control
    Then it offers exactly: tension, combat, climax_hype, faceslap, tragic,
        warm, romance_pain, suspense, daily, flashback, theme_open, system_cue
    And no 13th / free-text category is selectable
```

## AC-4 — Audio preview playback

```gherkin
Feature: In-grid mp3 preview playback

  Scenario: a card plays its mp3 with no new server endpoint
    Given a bgm_0001.mp3 exists under _bgm/combat/bgm_0001/
    When the user clicks play on that card
    Then the <audio> element's src is the existing /api/media URL for that mp3 (via mediaUrl())
    And /api/media serves it as audio/mpeg (already covered by MEDIA_EXTENSIONS)
    And audio playback starts (no 404, no new playback route added)
```

## AC-5 — assignments reverse-lookup resolves "which dramas use this BGM"

```gherkin
Feature: Reverse-lookup a bgm id to the dramas that cue it

  Scenario: a bgm.md referencing bgm_0007 is resolved to its drama
    Given _bgm/combat/bgm_0007/ exists
    And ai_videos/<dramaA>/episodes/ep03/bgm.md contains a cue line referencing bgm_0007
    And ai_videos/<dramaB>/bgm.md (a short) contains a cue line referencing bgm_0007
    When the assignments query is asked for bgm_0007
    Then the result lists both <dramaA> (ep03) and <dramaB>
    And the scan walks ai_videos/<drama>/episodes/ep*/bgm.md AND short-root bgm.md
        (NOT casting.md — that is the actor path)
    And directories whose name starts with "_" are skipped (e.g. _bgm, _actors, _deleted)

  Scenario: an unreferenced bgm reports no assignments
    Given bgm_0008 exists but no bgm.md anywhere references it
    When the assignments query is asked for bgm_0008
    Then the result is empty (and the response is a normal 200, not an error)

  Scenario: a malformed / unreadable bgm.md surfaces as a scan failure, not silent loss
    Given a bgm.md exists but cannot be read (OSError)
    When the assignments scan runs
    Then the failure is surfaced as a structured scan-failed error
        (mirroring actor's AssignmentsScanFailedError), never swallowed
```

## AC-6 — tools/mux_av.py v1 composites video + dialogue + bgm

```gherkin
Feature: Single-BGM AV mux (v1)

  Scenario: video stream is copied, dialogue is not halved, duck is active
    Given an input video MP4, a dialogue MP3, and a bgm MP3
    When mux_av.py runs with --video --dialogue --bgm --out
    Then the output is a composited MP4
    And the ffmpeg command uses -c:v copy (video stream NOT re-encoded)
    And the audio is encoded with -c:a aac
    And the filtergraph applies sidechaincompress in the order [bgm][dialogue]
        (bgm is the compressed input, dialogue is the sidechain key)
    And the filtergraph uses amix=normalize=0
        (so dialogue loudness is NOT silently halved)
    And in segments where dialogue is present the bgm level audibly ducks
    And the default duck params are threshold/ratio/attack/release = 0.03/8/40/400

  Scenario: bgm shorter than the video is looped and faded to fill duration
    Given the bgm MP3 is shorter than the video
    When mux_av.py runs
    Then ffprobe reads the video duration
    And the bgm is looped (-stream_loop / aloop) and apad-padded to the video length
    And afade applies the requested fade-in/out

  Scenario: missing-dialogue and missing-bgm behavior matrix (angle-2 contract)
    Given a run with --bgm but no --dialogue
    When mux_av.py runs
    Then no sidechaincompress/duck is applied and the bgm is laid in directly
    Given a run with --dialogue but no --bgm
    When mux_av.py runs
    Then only the dialogue track is muxed (no bgm bed)

  Scenario: pure ffmpeg, no pydub
    When mux_av.py executes
    Then it shells out to ffmpeg/ffprobe only and imports no pydub
```

## AC-7 — License metadata = Stability AI Community License

```gherkin
Feature: Commercial-safe license is recorded and surfaced

  Scenario: every generated bgm records the Stability community license
    Given any bgm generated by the v1 path
    Then its bgm_NNNN.md metadata table has
      | generator | stable_audio                  |
      | model     | stable-audio-open-1.0         |
      | license   | Stability AI Community License|
    And the project README states the commercial boundary
        (free commercial use under USD 1M annual revenue)
    And the README notes seed is best-effort reproducible (not hard-repro like actor)
```

## AC-8 — Soft-delete to _deleted/_bgm/

```gherkin
Feature: Soft-delete mirrors the actor soft-delete

  Scenario: deleting an unreferenced bgm moves its folder to _deleted/_bgm/
    Given bgm_0009 exists and no bgm.md references it
    When the bgm delete command runs for bgm_0009
    Then the folder _bgm/<cat>/bgm_0009/ is MOVED (not erased) under _deleted/_bgm/
    And it no longer appears in the library list or the grid
    And the move source/destination relative paths are returned in the response

  Scenario: deleting a referenced bgm is refused
    Given bgm_0010 is referenced by at least one drama's bgm.md
    When the bgm delete command runs for bgm_0010
    Then the delete is refused with a "still assigned" domain error listing the dramas
        (mirroring ActorAlreadyAssignedError — judgment call: spec §4 says the
         assignments scanner targets bgm.md; reuse the same guard before delete.
         If the spec intends delete to NOT guard, flag as a carve-out for the user.)

  Scenario: deleting a non-existent / already-deleted bgm errors clearly
    When the bgm delete command runs for a bgm id with no live folder
    Then a not-found / already-deleted domain error is raised (no silent success)
```

## AC-9 — cue line is consumable by all three consumers (spec §8 anchor)

```gherkin
Feature: bgm.md cue line satisfies grep, parser, and human reader

  Scenario: one cue line serves all three consumers
    Given a bgm.md cue line "12-30 bgm_0007 | vol=0.6 | duck=on | fade=in"
    When grep -o 'bgm_[0-9]\{4\}' runs over the file
    Then it yields bgm_0007 (reverse-lookup consumer)
    When mux_av.py parses the line
    Then it reads start=12s, stop=30s, vol=0.6, duck=on (→ sidechaincompress), fade=in (→ afade)
    And the cue semantics map 1:1 to the mux filtergraph (duck=on/off ↔ sidechaincompress, fade ↔ afade, loopable ↔ -stream_loop+trim)
    And the line remains human-readable in a terminal
```

## DDD-compliance acceptance gates (spec §10.1 — verified by other stage-5 levels, asserted here as criteria)

```gherkin
Feature: bgm__* slice mirrors actor 1:1

  Scenario: every route maps to exactly one application Query or Command method
    Then bgm__route.py handlers each call exactly one bgm__command / bgm__query method
    And routes import no infrastructure directly

  Scenario: state-changing operations go through the domain layer
    Then generate and delete pass through libs/domain (value objects + repository protocol)
    And read-side list / get / filter / assignments may use the §3 read-side carve-out

  Scenario: strong typing and file-size guidance
    Then every bgm__* parameter, return, and attribute is typed (str | None, not Optional)
    And BgmAttrs and DTOs are @dataclass(frozen=True)
    And each bgm__* file prefers < 100 lines (hard concern only on a >~1000-line file)
```

---

## Out-of-scope confirmations (general.md principle 6 — surface every v1 carve-out)

These are spec-declared carve-outs. Stage 5 must confirm with the user that each is intentionally OUTSIDE the validation gate:

1. **generate-diverse / archetype** omitted for BGM (actor has it). No acceptance test written for diverse generation — confirm intended.
2. **Multi-cue whole-`bgm.md` auto-arrangement** deferred; `mux_av.py` v1 consumes a SINGLE bgm only. No acceptance test for multi-cue stitching — confirm intended.
3. **`create-prompts` (offline prompt-only backfill)** is optional in §4/§11. If shipped, it needs an AC mirroring actor's prompt-only path; if dropped, confirm.
4. **`system_cue` classified as BGM (not SFX)** — self-flagged as a repo-custom call in §3/§11. Confirm the BGM grouping is accepted.
5. **`vol` as 0-1 linear (mux converts internally)** vs dB — §11 open point. Confirm 0-1 linear is the contract so AC-9's `vol=0.6` is unambiguous.
6. **seed = best-effort reproducibility** (not hard-repro like actor). Confirm the weaker guarantee is acceptable and is documented in README per AC-7.
