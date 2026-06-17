---
worker_id: level-specialist-03-unit_tests
stage: 5
role: level-specialist
level: unit_tests
status: complete
blockers: []
confidence: high
---

# Validation — unit_tests level (bgm_library)

Scope: the discrete, pure-logic units in the `bgm__*` DDD slice + `tools/stableaudio_gen.py` + `tools/mux_av.py`. **Descriptions only — no test code.** Test framework = `pytest` (matches the actor slice; run via plain `pip` + repo `.venv`, never `uv` — development.md §6). POSIX-only behaviors get explicit `pytest.mark.skipif(sys.platform == "win32", reason=...)` markers (development.md §5, general.md §3); silent passing is forbidden.

Suggested test file layout (mirrors the actor slice's test placement):
- `tests/unit/test_bgm_valueobject.py` — id regex + `BgmAttrs` + cue parse.
- `tests/unit/test_bgm_writer.py` — id allocation, md build/parse round-trip, reaper, soft-delete.
- `tests/unit/test_bgm_reference_reader.py` — assignments reverse-lookup scan.
- `tests/unit/test_mux_av.py` — filtergraph string assembly (pure-string, no ffmpeg exec).
- `tests/unit/test_stableaudio_gen.py` — `--dry-run` CLI path (no torch import).

Severity policy for this level inherits general.md (acceptance/contract failure = `blocker`; security/sandbox = `critical`). Per-unit severities noted inline where they escalate.

---

## A. `validate_bgm_id` — regex `^bgm_\d{4,}$`

Mirrors `validate_actor_id` (`actor__valueobject.py:143`). Raises `InvalidBgmIdError` on mismatch, returns `None` on match.

| Test | Input | Expected |
|---|---|---|
| `test_validate_bgm_id_accepts_4_digits` | `"bgm_0001"` | no raise |
| `test_validate_bgm_id_accepts_more_than_4_digits` | `"bgm_12345"`, `"bgm_000123"` | no raise |
| `test_validate_bgm_id_rejects_3_digits` | `"bgm_001"` | raises `InvalidBgmIdError` |
| `test_validate_bgm_id_rejects_missing_prefix` | `"0001"`, `"bgm0001"` | raises |
| `test_validate_bgm_id_rejects_wrong_prefix` | `"actor_0001"`, `"voice_0001"` | raises |
| `test_validate_bgm_id_rejects_non_digit_tail` | `"bgm_00a1"`, `"bgm_12 3"`, `"bgm_"` | raises |
| `test_validate_bgm_id_rejects_leading_trailing_ws` | `" bgm_0001"`, `"bgm_0001\n"` | raises (anchored `^…$`, no `re.MULTILINE`) |
| `test_validate_bgm_id_rejects_category_path` | `"tension/bgm_0001"` | raises (id is bare, category is a separate axis) |
| `test_validate_bgm_id_rejects_empty` | `""` | raises |

Edge cases: confirm `^…$` anchoring so an embedded match inside a longer string (e.g. `"xbgm_0001y"`) is rejected — this is the regex used for both id validation AND (in a distinct, non-anchored form `bgm_\d{4,}`) cue-token extraction; the two MUST stay separate. A test asserting the *validation* regex is anchored guards against accidentally reusing the loose extraction pattern for validation.

---

## B. `BgmAttrs` value object construction + enum/bounds validation

Frozen dataclass mirroring `ActorAttrs` (`__post_init__` → `validate()`), raising `InvalidBgmAttributeError`. Fields per spec §3: `category / mood / bpm / duration / loopable / intensity(1-5 int) / instruments / generator / model / seed / license / notes (+ optional tags)`.

### B.1 category enum (12 categories — closed set)

The 12 categories (spec §3): `tension, combat, climax_hype, faceslap, tragic, warm, romance_pain, suspense, daily, flashback, theme_open, system_cue`.

| Test | Input | Expected |
|---|---|---|
| `test_bgm_attrs_accepts_each_of_12_categories` | parametrized over all 12 | constructs, no raise |
| `test_bgm_attrs_category_count_is_12` | `len(CATEGORY_OPTIONS) == 12` | guards against accidental add/drop; also asserts exact membership set (catch a typo'd slug) |
| `test_bgm_attrs_rejects_unknown_category` | `"epic"`, `"action"`, `"Tension"` (case), `""` | raises `InvalidBgmAttributeError` |
| `test_bgm_attrs_rejects_actor_enum_leakage` | `"romance"` (almost `romance_pain`) | raises — near-miss slug |

### B.2 intensity — int in [1,5]

| Test | Input | Expected |
|---|---|---|
| `test_bgm_intensity_accepts_bounds` | `1`, `3`, `5` | no raise |
| `test_bgm_intensity_rejects_below` | `0`, `-1` | raises |
| `test_bgm_intensity_rejects_above` | `6`, `100` | raises |
| `test_bgm_intensity_rejects_non_int` | `3.0` (float), `"3"` (str), `True` (bool — note `isinstance(True, int)` is True; **decide & test**: spec says "int"; recommend rejecting `bool` explicitly) | raises |
| `test_bgm_intensity_rejects_none` | `None` | raises (intensity is required) |

*Ambiguity (non-blocking):* spec doesn't say whether `bool` counts as int. Best-judgment recommendation: reject `bool` explicitly (`type(x) is not int`) and pin it with a test, since `intensity=True` silently coercing to `1` is a latent data-quality bug. Flag to implementer; if they accept bool→int coercion, the test inverts but MUST still exist.

### B.3 loopable

Spec lists `loopable` as a metadata field. Likely a bool (loop-friendly track) — mirror actor's enum-validation discipline.

| Test | Input | Expected |
|---|---|---|
| `test_bgm_loopable_accepts_bool` | `True`, `False` | no raise |
| `test_bgm_loopable_rejects_non_bool` | `"yes"`, `1`, `None` | raises `InvalidBgmAttributeError` |
| `test_bgm_loopable_round_trips_md` | construct → build md → parse → `loopable` preserved as the same bool | covered in §D |

*Ambiguity (non-blocking):* spec doesn't pin loopable's type (bool vs `loopable/non-loopable` string enum). Recommend `bool`; if the md table stores it as `是/否` or `true/false` text, the parse test (§D) must assert the str→bool mapping is total and round-trips. Implementer's choice; test exists either way.

### B.4 other field validations (mirror actor discipline)

| Test | Input | Expected |
|---|---|---|
| `test_bgm_bpm_rejects_nonpositive` | `bpm <= 0` | raises (a 0/negative BPM is meaningless) |
| `test_bgm_duration_rejects_nonpositive` | `duration <= 0` | raises |
| `test_bgm_notes_length_cap` | notes > cap (mirror `NOTES_MAX_LEN=500`) | raises |
| `test_bgm_attrs_is_frozen` | attempt attribute set after construction | raises `FrozenInstanceError` |
| `test_bgm_attrs_post_init_runs_validate` | construct with bad category directly | raises at construction (not a separate `.validate()` call) — mirrors actor follow-up 114 |
| `test_bgm_license_default_recorded` | construct via generate path | `license == "Stability AI Community License"` (spec §2/§10.7) |

---

## C. Global-unique id allocation across the `{category}/` layer

**Key structural divergence from actor** (spec §3, dossier insight 3): actor is flat `_actors/actor_NNNN/`; BGM is `_bgm/{category}/bgm_NNNN/`, so id allocation must scan **ALL categories** for the global max, then `+1`, and atomically claim via `mkdir(exist_ok=False)`. Mirrors `_next_actor_id_num` + `_allocate_actor_id` (`actor__writer.py:2367,2449`).

| Test | Setup | Expected |
|---|---|---|
| `test_next_id_empty_library` | empty `_bgm/` (no categories) | returns `1` → first id `bgm_0001` |
| `test_next_id_single_category` | `_bgm/tension/bgm_0003/` exists | next = `bgm_0004` |
| `test_next_id_max_across_all_categories` | `_bgm/tension/bgm_0002/` + `_bgm/combat/bgm_0005/` + `_bgm/warm/bgm_0001/` | next = `bgm_0006` (**global** max+1, not per-category) — this is THE divergence test |
| `test_next_id_ignores_non_bgm_dirs` | a `_bgm/tension/notes/` non-matching dir + a stray file | skipped; only `bgm_\d{4,}` folders count |
| `test_next_id_ignores_category_dir_itself` | the `{category}/` folder is a container, not an id | category dirs never counted as ids |
| `test_alloc_new_id_creates_folder_under_correct_category` | allocate for `category=combat` | folder is `_bgm/combat/bgm_NNNN/`, returns `(id, path)` |
| `test_alloc_no_collision_two_categories` | pre-seed `_bgm/tension/bgm_0001`, allocate for `combat` | gets `bgm_0002`, NOT `bgm_0001` again — proves cross-category global uniqueness |
| `test_alloc_mkdir_exist_ok_false` | (white-box) pre-create the target folder, then allocate | allocator skips the occupied id and walks forward (`FileExistsError` → `candidate+1`), mirroring actor `_allocate_actor_id` |
| `test_alloc_exhaustion_raises` | force `_MAX_ID_ALLOC_SCAN` consecutive collisions | raises the bgm equivalent of `ActorGenerationDirMissingError` |

### C.1 Concurrency / atomicity (POSIX-leaning — mark per platform)

The atomicity guarantee rests on `mkdir(exist_ok=False)` being atomic. On Windows/NTFS it is atomic enough for the no-collision property, but a *power-loss* / true-concurrency stress test is POSIX-flavored.

- `test_alloc_concurrent_no_dup_ids` — spawn N threads each allocating once against a shared `_bgm/`; assert all returned ids are distinct and contiguous from the start max. **Threaded variant runs cross-platform** (threads, not `os.fork`). Keep it.
- `test_alloc_atomicity_under_power_loss` — simulated interrupt between mkdir and sidecar write. **Mark `skipif(sys.platform == "win32", reason="os.replace/mkdir power-loss atomicity is best-effort on NTFS")`** (general.md §3, development.md §5). Skip on Windows; do not silently pass.

*Severity:* a failing cross-category global-uniqueness test = `blocker` (id collision corrupts cross-drama references — the whole point of the library).

---

## D. Markdown metadata table build → parse round-trip

Mirrors actor `_build_sidecar` / its parse counterpart. The `.md` carries a 12-field table (§3) + a trailing `## 生成 prompt` block. **Round-trip is the contract**: `parse(build(attrs)) == attrs` for every field.

| Test | Description | Expected |
|---|---|---|
| `test_md_build_contains_all_12_fields` | build sidecar from a fully-populated `BgmAttrs` | rendered md table has rows for all of: `category, mood, bpm, duration, loopable, intensity, instruments, generator, model, seed, license, notes` |
| `test_md_roundtrip_preserves_every_field` | build → parse → assert each field byte/value-equal | all 12 fields preserved; `intensity` parses back as `int` (not str), `loopable` as bool, `bpm`/`duration`/`seed` as their numeric types |
| `test_md_roundtrip_optional_tags` | attrs with + without `tags` | present round-trips; absent stays absent (not `""` vs `None` drift — pick one and pin it) |
| `test_md_roundtrip_empty_notes` | `notes=""` | round-trips to empty, not the literal string `"None"` |
| `test_md_roundtrip_unicode_instruments` | Chinese/mixed instrument text (e.g. `"低音弦乐 + 定音鼓"`) | preserved exactly (file content is allowed Chinese; pipe `|` in a markdown-table cell must be escaped or the field must not contain a raw `|` — **test a value containing `|` if the table is pipe-delimited**) |
| `test_md_parse_preserves_generation_prompt_block` | build with a multi-line English Stable Audio prompt after the table | `## 生成 prompt` block parsed back intact incl. newlines |
| `test_md_parse_tolerates_whitespace` | hand-edited md with extra spaces around `|` / `:` | parser strips and still maps fields (matches actor parser leniency) |
| `test_md_parse_missing_field_behavior` | md missing one row (older/hand-edited file) | **decide & pin**: either default-fill or raise a clear `InvalidBgm*Error`; recommend raising for required fields, defaulting only `tags`. (general.md §1 — validate the contract the consumer relies on.) |
| `test_md_build_records_stable_audio_provenance` | build via generate | `generator=stable_audio`, `model=stable-audio-open-1.0` (or `--model` override), `license=Stability AI Community License` present in table (spec §2) |

*Note (development.md §10):* the md parser consumes upstream-generated text. At least one round-trip test MUST run against a **real on-disk `bgm_NNNN.md`** produced by the actual `_build_sidecar` (not a hand-written fixture), so the parser regex can't drift from the builder. Marked as a `blocker` if absent.

---

## E. cue line parse — `起-止(秒) bgm_NNNN | vol= | duck=on/off | fade=in/out`

Pipe-delimited, line-oriented (spec §8, dossier insight 3). One parse function turns a cue line into a structured cue (start, end, bgm_id, vol, duck, fade). The format serves three consumers (grep / `mux_av.py` parse / human read) — tests assert all three remain satisfiable.

### E.1 Well-formed

| Test | Input line | Expected |
|---|---|---|
| `test_cue_parse_full` | `12.0-30.5 bgm_0007 | vol=0.6 | duck=on | fade=in` | `(start=12.0, end=30.5, bgm_id="bgm_0007", vol=0.6, duck=True, fade="in")` |
| `test_cue_parse_integer_seconds` | `0-15 bgm_0001 | vol=0.5 | duck=off | fade=out` | start/end parse as numbers (int or float — pin one) |
| `test_cue_parse_duck_off` | `… | duck=off …` | `duck=False` |
| `test_cue_parse_fade_both_directions` | `fade=in`, `fade=out` | mapped to the afade direction; (decide whether `fade=in/out` both-at-once is a thing — spec lists `in/out` as alternatives) |

### E.2 Missing optional fields (vol / duck / fade are optional per task brief)

| Test | Input | Expected |
|---|---|---|
| `test_cue_parse_only_required` | `12-30 bgm_0007` (no pipes) | parses start/end/id; vol/duck/fade take documented defaults (e.g. `vol=1.0` or library `vol`, `duck=off`, no fade) — **pin the defaults** |
| `test_cue_parse_partial_options` | `12-30 bgm_0007 | duck=on` | duck set, vol/fade defaulted |
| `test_cue_parse_options_any_order` | `… | fade=in | vol=0.6 | duck=on` | order-independent key=value parsing |

### E.3 Malformed (must fail loudly, not silently mis-parse)

| Test | Input | Expected |
|---|---|---|
| `test_cue_parse_rejects_bad_timecode` | `30-12 bgm_0007 …` (end < start) | raises / flagged (negative-duration cue) |
| `test_cue_parse_rejects_missing_id` | `12-30 | vol=0.6` | raises (no `bgm_NNNN` token) |
| `test_cue_parse_rejects_bad_id_shape` | `12-30 bgm_07 …` (3-digit) | raises — reuse the `bgm_\d{4,}` shape |
| `test_cue_parse_rejects_unknown_key` | `… | gain=0.6` | raises or warns (pin: unknown key is an error) |
| `test_cue_parse_rejects_vol_out_of_range` | `vol=2.0`, `vol=-0.1` | raises (spec §11 leans 0-1 linear vol) |
| `test_cue_parse_rejects_bad_duck_value` | `duck=maybe` | raises (only `on`/`off`) |
| `test_cue_parse_rejects_bad_fade_value` | `fade=sideways` | raises (only `in`/`out`) |
| `test_cue_parse_blank_and_comment_lines` | empty line, whitespace-only, `# comment` | skipped, not parsed as a cue (mirror `subtitles.md` leniency) |

### E.4 grep-compatibility (the reverse-lookup consumer)

- `test_cue_line_grep_token_extractable` — a well-formed cue line contains exactly the substring matched by `bgm_\d{4,}` (the assignments-scan regex, §F). This couples the cue format to the scanner; if the format ever drops the bare `bgm_NNNN` token, this fails. (general.md §1, §10.)

---

## F. assignments reverse-lookup scan

Mirrors `Casting.find_assignments_for_actor` / `assigned_actor_ids` (`casting__writer.py:272,312`), but scans `bgm.md` files instead of `casting.md`, and extracts `bgm_NNNN` tokens via the loose `bgm_\d{4,}` pattern. Per spec §4.2: scan `ai_videos/<drama>/episodes/ep*/bgm.md` (novel) AND short-root `ai_videos/<drama>/bgm.md`; **skip `_`-prefixed dirs** (the `_bgm`, `_actors`, `_deleted` library/system dirs) and symlinks.

| Test | Setup | Expected |
|---|---|---|
| `test_find_assignments_empty_when_no_ai_videos` | no `ai_videos/` dir | returns `[]` (mirror actor guard `casting__writer.py:284`) |
| `test_find_assignments_novel_episodes` | `ai_videos/dramaA/episodes/ep01/bgm.md` + `ep02/bgm.md` both cue `bgm_0007` | returns rows for dramaA ep01 + ep02 |
| `test_find_assignments_short_root_bgm` | `ai_videos/shortB/bgm.md` cues `bgm_0007` | returns a row for shortB (short layout — root-level `bgm.md`) |
| `test_find_assignments_multiple_ids_one_file` | one `bgm.md` cues `bgm_0007` + `bgm_0009` | querying `bgm_0007` returns only its rows; `bgm_0009` rows excluded |
| `test_find_assignments_dedup_within_file` | same id cued twice (two cue lines) in one `bgm.md` | **pin**: either one row per file or one row per cue — recommend per-file dedup for the "which dramas use this" UI question (spec §10.4) |
| `test_find_assignments_skips_underscore_dirs` | a `bgm_NNNN` token literally present under `ai_videos/_bgm/…` and `ai_videos/_deleted/…` | NOT returned — `_`-prefixed dirs skipped (`casting__writer.py:290`) |
| `test_find_assignments_skips_symlinked_drama` | symlinked drama dir | skipped (`is_symlink()` guard) — **mark `skipif(win32)`** since creating a symlink needs Developer Mode (development.md §5) |
| `test_assigned_bgm_ids_bulk_scan` | several dramas referencing a mix of ids | returns the `set` union of all referenced `bgm_NNNN` — mirrors `assigned_actor_ids`, backs the grid `is_assigned` filter |
| `test_find_assignments_validates_id_shape` | call with `bgm_07` | raises `InvalidBgmIdError` before scanning (mirror `casting__writer.py:281`) |
| `test_find_assignments_ignores_non_bgm_tokens` | `bgm.md` also containing `actor_0001` text | only `bgm_NNNN` tokens extracted |
| `test_find_assignments_token_regex_not_anchored` | id token embedded mid-line within a cue | extraction uses the **loose** `bgm_\d{4,}` (not the anchored `^…$` validation regex) — guards the two-regex separation called out in §A |

*Edge:* a `bgm.md` with malformed cue lines should still allow grep-style token extraction (the scanner uses regex `findall`, not the full cue parser of §E) — `test_find_assignments_tolerates_malformed_cue_lines`: a `bgm.md` with a broken cue line but a valid `bgm_0007` token still returns the assignment. This matches the spec's "grep is one of three independent consumers" design (dossier insight 3) — the reverse-lookup MUST NOT depend on the cue line being fully well-formed.

---

## G. `mux_av.py` filtergraph assembly (pure-string, no ffmpeg exec)

The filtergraph + arg-list builder is pure Python (ffprobe-derived durations + a string). Tests assert on the **assembled ffmpeg arg list / filtergraph string**, mocking `ffprobe` duration lookups; they do NOT spawn ffmpeg. (Actual A/V muxing is a stage-6 runtime/integration concern, not unit.)

### G.1 sidechain input order (THE classic-error guard)

| Test | Scenario | Expected |
|---|---|---|
| `test_filtergraph_sidechain_input_order` | video + dialogue + bgm, duck on | the `sidechaincompress` consumes inputs in order `[bgm][dialogue]` — **BGM first (compressed signal), dialogue second (sidechain key)**. Assert the filtergraph substring orders bgm before dialogue feeding sidechaincompress. Reversed order = `blocker` (spec §7, dossier ffmpeg-duck-mux: "反了是经典错误"). |
| `test_filtergraph_duck_default_params` | defaults | `threshold=0.03 ratio=8 attack=40 release=400` appear (spec §7) |
| `test_filtergraph_duck_param_overrides` | CLI `--duck-threshold/ratio/attack/release` | overridden values flow into the `sidechaincompress` string |

### G.2 `amix=normalize=0` present (台词-halving guard)

| Test | Scenario | Expected |
|---|---|---|
| `test_filtergraph_amix_normalize_zero` | any mux with both tracks | filtergraph contains `amix=...:normalize=0` — **`normalize=0` MUST be present**; without it ffmpeg silently halves dialogue loudness (spec §7/§10.5). Missing = `blocker`. |

### G.3 video stream copy (no re-encode)

| Test | Scenario | Expected |
|---|---|---|
| `test_mux_args_video_copy` | any mux | arg list contains `-c:v copy` (spec §7); assert `-c:v libx264`/re-encode is NOT present |
| `test_mux_args_audio_aac` | any mux | `-c:a aac` present |

### G.4 missing-track behavior matrix (spec §7 / dossier ffmpeg-duck-mux)

| Test | Inputs | Expected |
|---|---|---|
| `test_mux_missing_dialogue_no_duck` | `--video --bgm`, no `--dialogue` | NO `sidechaincompress` in filtergraph (nothing to duck against); BGM laid under video directly; still `amix` or direct map as designed; `-c:v copy` kept |
| `test_mux_missing_bgm_dialogue_only` | `--video --dialogue`, no `--bgm` | only dialogue mapped; no `amix`/`sidechaincompress`; `-c:v copy` kept |
| `test_mux_both_missing` | `--video` only | **pin**: either copy-through (audio-less) or error; recommend error with a clear message (`mux_av` v1 is single-BGM compose) |
| `test_mux_dialogue_and_bgm_present` | full | both tracks → sidechain (if duck on) → amix(normalize=0) → aac |
| `test_mux_duck_off_skips_sidechain` | cue/flag `duck=off` | no `sidechaincompress`, BGM + dialogue go straight to `amix=normalize=0` |

### G.5 loop / pad / fade string assembly

| Test | Scenario | Expected |
|---|---|---|
| `test_filtergraph_loop_when_bgm_shorter` | bgm duration < video, loopable | `-stream_loop`/`aloop` present, trimmed to target via ffprobe duration |
| `test_filtergraph_apad_when_bgm_shorter_non_loop` | bgm shorter, not loopable | `apad` pads silence to target |
| `test_filtergraph_afade_in_out` | `--fade-in`/`--fade-out` | `afade=t=in` / `afade=t=out` with correct durations |
| `test_filtergraph_bgm_start_offset` | `--bgm-start=5` | BGM delayed/started at offset in the graph |
| `test_filtergraph_bgm_volume` | `--bgm-volume=0.4` | a `volume=0.4` filter on the bgm branch |

*Note:* these are pure-string assembly tests. A single stage-6 **integration** smoke (real ffmpeg, tiny fixtures, assert output has 1 video + 1 audio stream and dialogue loudness ~unchanged) belongs in `integration_tests.md` / runtime validation, not here — flag the boundary so it isn't dropped (development.md §4 boot/smoke discipline applies to the tool too).

---

## H. `stableaudio_gen.py --dry-run` (no torch invocation)

CLI contract `--prompt --seed --duration --model --out [--dry-run]` (spec §6). `--dry-run` prints the prompt/params and exits **without importing torch / stable-audio-tools** — this is the path the webapp uses to validate generation wiring without paying the heavy-model cost.

| Test | Scenario | Expected |
|---|---|---|
| `test_dry_run_prints_prompt_and_params` | `--dry-run --prompt "tense …" --seed 7 --duration 30 --model stable-audio-open-1.0 --out x.mp3` | stdout contains the prompt, seed, duration, model, out path; exit code 0 |
| `test_dry_run_does_not_import_torch` | run `--dry-run` in a subprocess (or monkeypatch `sys.modules` so `import torch` raises) | completes successfully — torch/`stable_audio_tools` are NOT imported on the dry-run path. **This is the load-bearing isolation test** (spec §2/§6: torch must not enter the webapp process; dry-run proves the import is lazy/guarded). |
| `test_dry_run_writes_no_file` | `--dry-run --out some.mp3` | `some.mp3` is NOT created |
| `test_cli_missing_required_arg` | omit `--prompt` | argparse error, non-zero exit |
| `test_cli_default_model` | omit `--model` | defaults to `stable-audio-open-1.0` (spec §2) |
| `test_dry_run_seed_best_effort_noted` | n/a | (doc-level) dry-run output / README notes seed is best-effort, not hard-reproducible (spec §2/§6) — assert the printed params label seed accordingly if the tool emits it |

*Implementation note for testability:* the `import torch` / `get_pretrained_model` calls MUST live **inside** the non-dry-run branch (function-local import), not at module top level — otherwise `test_dry_run_does_not_import_torch` and even importing the module for any other test fails on a torch-less webapp venv. If the implementer puts the heavy import at module scope, that's a `blocker` (defeats the whole subprocess-isolation design, spec §6).

---

## Cross-cutting required-move checklist (development.md / general.md)

- **pip, not uv** (development.md §6): any Makefile `test` target for these units runs under plain `pip` + `.venv`. No `uv run` without a pip fallback — flag as `blocker`.
- **Cross-platform skip markers** (development.md §5, general.md §3): symlink-skip drama (§F), power-loss atomicity (§C.1) marked `skipif(win32)`; threaded concurrency (§C.1) kept cross-platform. No silently-passing assertion-less test.
- **Real-upstream-output parser test** (development.md §10): the md round-trip (§D) and at least one cue-parse test (§E) run against an actual artifact produced by the builder/generator, not a hand fixture.
- **Contract over implementation** (general.md §1): id-allocation, cue parse, and assignments tests assert on the *consumer contract* (global uniqueness, grep-token extractability, cross-category no-collision), not on internal scan order.
- **Audit events** (general.md §5): this unit_tests level, when run in stage 6, emits `validation.started` / `validation.pass` | `validation.issue.raised`.

## Open ambiguities surfaced (non-blocking, best-judgment pinned above)
1. `intensity` bool-as-int handling (§B.2) — recommend reject `bool`.
2. `loopable` type: bool vs string enum (§B.3) — recommend bool; round-trip test adapts.
3. cue `vol` units: 0-1 linear vs dB (§E) — spec §11 leans 0-1 linear; tests assume 0-1, range-checked.
4. assignments dedup granularity: per-file vs per-cue (§F) — recommend per-file for the "which dramas reference this" UI.
5. md missing-field behavior (§D) — recommend raise for required fields, default only `tags`.
6. both-tracks-missing mux behavior (§G.4) — recommend explicit error.

Each is a `## Pinned items`-style decision the implementer (stage 6) confirms; none blocks writing the tests since both branches are described.
