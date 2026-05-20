# Follow-up draft 093 — 2026-05-18
Add a new character-video aggregate operation: **extract 3 angle views (front / side / back) + the full audio track** from a character turntable mp4. Outputs land in a new `views/` subfolder next to the source. UI exposed as a per-tile button gated by character-folder path detection.

## Why

Rule #12.5 v9 (per follow-up 092) renders the character turntable as a single 15s continuous-take video: 0-2s static frontal full-body (truncate-compat) + 2-5s slow dolly-in to medium close-up (face clear) + 5-13s slow clockwise 360° orbit + 13-15s settle. The video as a single asset is hard to use downstream — Seedance / Kling shot prompts that need a **side-body silhouette** or a **back-side reference** want a still image, not a 15s clip; voice-line tooling wants the audio track separately from the video. Today the user is screencap-scrubbing for these manually.

This feature automates the 3-still + audio extraction so the v9 turntable becomes a single source-of-truth that fan-outs into:
- `{prefix}_front.png` (t=1.0s, mid-way through the 0-2s static intro — clean frontal full-body)
- `{prefix}_side.png` (t=7.0s, 25% into the 5-13s slow orbit = 90° of the 360° revolution — left-side body)
- `{prefix}_back.png` (t=9.0s, 50% into the orbit = 180° — back-side body)
- `{prefix}_audio.mp3` (full 15s audio — 一/二/三/我是X/标志台词#1/标志台词#2)

Timestamps are anchored to v9's 5-phase camera path: the user explicitly designed the orbit window (5-13s = 8s for 360°) so the 1/4 and 1/2 marks of the orbit window are predictable angle landings.

## Design

### Coordinate timing math

Given v9's 15s schedule:
- 0-2s static frontal (locked camera) — front pick anywhere in 0-2s; midpoint t=1.0s avoids the 0s discontinuity + the 2s motion-start handoff.
- 2-5s slow dolly-in — not used; camera framing changes throughout this phase, no clean angle landing.
- 5-13s slow 360° orbit (8s for full revolution = 45°/s) — angle = (t - 5) * 45°:
  - t=5.0s → 0° (front again, redundant with the static intro)
  - t=7.0s → 90° (left side, 25% into orbit)
  - t=9.0s → 180° (back, 50% into orbit)
  - t=11.0s → 270° (right side, redundant with t=7.0s left side)
  - t=13.0s → 360° (back to front, redundant)
- 13-15s settle — back at front, redundant.

Three picks at t=1.0 / 7.0 / 9.0 cover the three orthogonal angles the user named (front / side / back) with the cleanest motion behavior at each timestamp.

**Why these timestamps are hard-coded against v9.** They are not arbitrary — they are the algebraic image of v9's 5-phase camera path. If the rule #12.5 schedule changes (e.g., a future v10 with a different orbit window), these constants must change too. The constants live in a domain value object next to a comment that names rule #12.5 v9 explicitly, so a future v10 rev knows where to look.

### DDD+CQRS placement

Per project layout rules (CLAUDE.md § Project rules / development.md):

**New file:**
- `libs/domain/value_objects/character_video__valueobject.py` — `CharacterViewSpec` (frozen dataclass: timestamp, role) + `CANONICAL_VIEWS` (tuple of 3) + `audio_output_filename(prefix)` + `view_output_filename(prefix, spec)`. The existing `frame__valueobject.py` is the analog for scene videos; this is the parallel for character videos.

**Extended files (additive, no breaking changes):**
- `libs/infrastructure/errors/character_video__error.py` — add `ViewExtractFailed`, `AudioExtractFailed` (each are distinct infra exceptions; shared `InvalidPath`/`NotFound`/`FfmpegMissing`/`NotCharacterVideo` reused).
- `libs/domain/errors/character_video__error.py` — add `ViewExtractFailedError`, `AudioExtractFailedError` (named domain errors, subclasses of `CharacterVideoDomainError`).
- `libs/infrastructure/writers/character_video__writer.py` — add `CharacterViewExtractor` class (a 3rd operation alongside `CharacterVideoTruncator` + `ShotConcatBuilder`). It reuses the existing path-shape validation pattern (`_is_under_character_folder`) and `imageio_ffmpeg`-backed subprocess invocation.
  - Operation: `extract(rel)` → `ViewExtractResult` (3 `ViewResult` + 1 `AudioResult` + tuple of failures).
  - Output folder: `{src.parent}/views/` (mkdir + sweep stale `.png` / `.mp3` on every run for idempotency).
  - Output naming: `{src.parent.name}_{role}.png` (front / side / back) + `{src.parent.name}_audio.mp3`. The prefix is the **parent dir name**, NOT the mp4 stem — matches `FrameExtractor`'s convention so re-extracting from a re-render in the same folder overwrites.
- `libs/application/dtos/character_video__dto.py` — add 3 new frozen Cdtos: `CharacterViewCdto` (timestamp, role, path), `CharacterAudioCdto` (path, duration_seconds), `ExtractCharacterViewsResultCdto` (src_rel, views, audio, failures).
- `libs/application/mappers/character_video__mapper.py` — add `views_to_cdto(r: ViewExtractResult)` static method.
- `libs/application/commands/character_video__command.py` — add `extract_views(rel_path) -> ExtractCharacterViewsResultCdto` method to `CharacterVideoCommand` (third method alongside `truncate` + `concat_shot`). `__init__` gains a 3rd dep `extractor: CharacterViewExtractor`.
- `apps/api/routes/character_video__route.py` — add `POST /api/extract-character-views` with `ExtractCharacterViewsBody{path: str}` Pydantic model. Maps the 6 named domain errors (Invalid / NotCharacterVideo / NotFound / FfmpegMissing / ViewExtractFailed / AudioExtractFailed) to `detail.kind` strings.
- `apps/api/container.py` — add `character_view_extractor: Singleton[CharacterViewExtractor]`. Update `character_video_command` Factory to pass the new dependency.

### UI exposure

**New api.ts function:** `extractCharacterViews(path: string): Promise<ExtractCharacterViewsResult>` + typescript types matching the Cdtos.

**SiblingMedia.tsx** — the existing 🎞 "Extract Frames" button is for SCENE videos (rule #12.10 v3, 8 canonical frames). For CHARACTER videos (path matches `ai_videos/{drama}/characters/{cN_xxx}/*.{mp4|mov|...}`) the 8-frame schedule timestamps don't align with v9's camera path. So:
- Show 🖼 "提取三视图+音频" button as an ADDITIONAL button on character-video tiles. The existing 🎞 "Extract Frames" button stays untouched (scene videos still need it; an advanced user might still want the 8-frame schedule applied to a character video).
- Gate by path-shape: `path` matches `^ai_videos/[^/]+/characters/c\d+(_[^/]+)?/[^/]+\.{video_ext}$`. Only character mp4s show the new button.
- Button is disabled while `extractingViewsPath === path` (parallels the existing `extractingPath` state for the frame extractor).

Toast feedback: `Extracted 3 views + audio from {filename} → views/` on success, `Extract views failed: {kind}` on error.

### File-naming examples

For `ai_videos/mozun_chongsheng/characters/c1_沧冥/c1_沧冥.mp4`:
- `ai_videos/mozun_chongsheng/characters/c1_沧冥/views/c1_沧冥_front.png` (t=1.0s)
- `ai_videos/mozun_chongsheng/characters/c1_沧冥/views/c1_沧冥_side.png` (t=7.0s)
- `ai_videos/mozun_chongsheng/characters/c1_沧冥/views/c1_沧冥_back.png` (t=9.0s)
- `ai_videos/mozun_chongsheng/characters/c1_沧冥/views/c1_沧冥_audio.mp3` (full 15s, mp3 encoder via ffmpeg `-c:a libmp3lame -q:a 4`)

Prefix is the parent dir name `c1_沧冥`, NOT the mp4 stem. If the user later renders a `c1_沧冥_take2.mp4` alongside, re-extracting overwrites the same 4 outputs (so `views/` always reflects the LATEST extraction in the folder, single source of truth).

### Idempotency + cleanup

On every extract:
1. `views/` mkdir (parents=True, exist_ok=True).
2. Sweep: delete every `*.png` and every `*.mp3` directly in `views/` (non-recursive, no symlinks). Catches stale outputs from a renamed source or a prior different prefix.
3. Run 3 ffmpeg frame-extract subprocess calls (sequential — total wall time ~3-5s, no need for parallel). Each: `-ss {t} -i {src} -frames:v 1 -q:v 1 {out}.png`.
4. Run 1 ffmpeg audio-extract subprocess call: `-i {src} -vn -c:a libmp3lame -q:a 4 {out}.mp3`. No `-t` cap — extracts the full source audio (15s for v9 sources, but works for any duration).
5. Failures (per-view or audio) accumulate in a `failures` tuple but do not raise unless **all 4 outputs fail** (parallels `FrameExtractor`'s "raise if no frames produced" semantics).

### Tests

The existing test suite is light on character-video coverage. No new tests in scope for this turn — boot-smoke verifies route registration, and the existing pattern of relying on integration smoke + manual UI test holds. If a future bug demands regression coverage, a fixture mp4 + unit test for `CharacterViewExtractor` lands then.

## Out of scope

- No changes to v9 rule #12.5 / character file schema — this is a downstream-of-v9 webapp tool, not a spec change.
- No changes to the existing scene-frame extractor (`FrameExtractor` + `FrameCommand`). Scene videos keep the 8-frame schedule.
- No batch button at characters/ folder level (deferred — per-tile button is what the user picked).
- No auto-run-on-upload (deferred — per-tile button is what the user picked).
- No segmented audio output (single full-length .mp3 is what the user picked; the existing 截到 2s tool still produces the 2s frontal voice-baseline clip if the user wants that segment specifically — wait, that's the truncate operation on the mp4, not on the mp3. If a future ask wants a 0-2s .mp3 voice-baseline, it can be added then).
- No .wav option (deferred — .mp3 is what the user picked).
- No agent_refs / spec changes — this is project-scoped, not a cross-cutting rule.

## Touch list

- `projects/ai_video_management/libs/domain/value_objects/character_video__valueobject.py` (NEW)
- `projects/ai_video_management/libs/infrastructure/errors/character_video__error.py` — add `ViewExtractFailed`, `AudioExtractFailed`.
- `projects/ai_video_management/libs/domain/errors/character_video__error.py` — add `ViewExtractFailedError`, `AudioExtractFailedError`.
- `projects/ai_video_management/libs/infrastructure/writers/character_video__writer.py` — add `CharacterViewExtractor` class (~120 lines).
- `projects/ai_video_management/libs/application/dtos/character_video__dto.py` — add `CharacterViewCdto`, `CharacterAudioCdto`, `ExtractCharacterViewsResultCdto`.
- `projects/ai_video_management/libs/application/mappers/character_video__mapper.py` — add `views_to_cdto` static method.
- `projects/ai_video_management/libs/application/commands/character_video__command.py` — add `extract_views` method + `__init__` 3rd dep.
- `projects/ai_video_management/apps/api/routes/character_video__route.py` — add `/api/extract-character-views` route.
- `projects/ai_video_management/apps/api/container.py` — wire `character_view_extractor` Singleton + update command Factory.
- `projects/ai_video_management/apps/ui/src/api.ts` — add `extractCharacterViews` + types.
- `projects/ai_video_management/apps/ui/src/components/SiblingMedia.tsx` — add 🖼 button gated by character-folder path detection.
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bump 093.
- `specs/development/ai_video_management/changelog.md` — entry for 093.
