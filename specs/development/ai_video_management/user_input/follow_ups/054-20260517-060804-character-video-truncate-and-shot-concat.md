# Follow-up draft 054 — 2026-05-17
Add two video-pipeline features to the ai_video_management webapp: per-character video truncation, and per-shot character reel.

---

## Feature 1 — Truncate any character mp4 to a 2-second `video.mp4`

- Scope: only files that match `ai_videos/{drama}/characters/{cN_xxx}/*.mp4` (the per-drama character folders). Out of scope: `_actors/`, `episodes/`, `scenes/`.
- UI: an additional per-tile button **"Truncate to 2s → video.mp4"** appears in `SiblingMedia` for character mp4 tiles (alongside the existing Archive / Extract Frames buttons). Visible only for `.mp4/.mov/.webm/.mkv/.avi/.m4v` files whose path matches the character-folder pattern above.
- Backend: new `POST /api/truncate-character-video` endpoint
  - Body: `{ path: string }` — relative path to the source mp4
  - Behavior:
    1. Validate path is under sandbox, is a video extension, lives under `ai_videos/{drama}/characters/{cN_xxx}/`, and the source file exists.
    2. Run `ffmpeg -y -i <src> -t 2 -c:v libx264 -preset veryfast -pix_fmt yuv420p -c:a aac -movflags +faststart <char_folder>/video.mp4` to produce a clean re-encoded 2-second cut.
    3. The output **always** goes to `<char_folder>/video.mp4`, overwriting any existing `video.mp4`. The source file is untouched.
  - Response: `{ src: rel_path_of_source, out: rel_path_of_video_mp4, duration_seconds: 2.0 }`.
  - Errors: same shape as `/api/extract-frames` (`invalid_path` / `not_a_video` / `not_found` / `ffmpeg_missing` / `truncate_failed`) plus a new `not_a_character_video` kind when the path doesn't match `characters/cN_*/`.

## Feature 2 — Concatenate the involved characters' 2-second clips for a shot

- Scope: shot md files at `ai_videos/{drama}/episodes/ep{NN}/prompts/shot{NN}/shot{NN}.md` (novel layout) and `ai_videos/{drama}/prompts/shot{NN}/shot{NN}.md` (short layout).
- UI: a "Build shot character reel" button on the `ShotPairView` header (and on any direct render of a shot md). Triggers the concat call with the current shot md path.
- Backend: new `POST /api/concat-shot-characters` endpoint
  - Body: `{ path: string }` — relative path to the shot md
  - Behavior:
    1. Validate path is under sandbox, ends in `.md`, sits inside a `prompts/shot{NN}/` folder.
    2. Parse the **出场角色 / Characters in this shot** markdown table in the shot md. Detection: locate the header row that contains both `角色` and `character file` (any order, surrounding whitespace OK). For each data row, take the value of the `character file` column, strip backticks, treat it as a relative path; the character folder is its parent directory.
    3. Skip rows whose `character file` cell is empty or doesn't resolve to a path under `ai_videos/{same_drama}/characters/`.
    4. For each character folder, look for `video.mp4`. If missing, record a warning and skip that character. Order = order of the table rows.
    5. If at least one character has `video.mp4`, ffmpeg-concat via the concat demuxer with re-encode (`-c:v libx264 -preset veryfast -pix_fmt yuv420p -c:a aac -movflags +faststart`) so heterogeneous source codecs concatenate cleanly. Output: `<shot_folder>/<shotNN>_chars.mp4` (overwriting if present).
    6. If no character has `video.mp4`, return 200 with `{ used: [], skipped: [...] , out: null }` — no file written.
  - Response: `{ shot_path, out: rel_path_or_null, used: [{ character_folder, rel_path, role }], skipped: [{ character_folder, reason }] }`.
  - Errors: `invalid_path` / `not_a_shot_md` / `not_found` / `ffmpeg_missing` / `concat_failed` / `no_character_table` (the md has no recognisable 出场角色 table).
  - "Only the characters for the current shot" rule is satisfied because the parser only reads the shot md being requested — no cross-shot or whole-episode aggregation.

## Cross-cutting decisions (from the clarification round)

- Truncation output naming: always `video.mp4` in the same character folder. Source mp4 stays. (User chose "Truncate writes to video.mp4 in same folder".)
- Concat input: always `video.mp4` in each involved character folder. (User chose "video.mp4 in char folder".)
- Character detection: every row of the 出场角色 table, regardless of the "turntable 必需" ✅/❌ column. (User chose "All rows of the 出场角色 table".)
- Concat output location: sibling of the shot md, named `<shotNN>_chars.mp4`. (User chose "Sibling of shot md".)

## Architecture / placement (per project rules)

- `routes.py` stays a thin transport layer: two new Pydantic bodies, one application-layer call each, domain-error → HTTP mapping table in line with follow-up 051.
- New application Commands: `TruncateCharacterVideoCommand`, `ConcatShotCharactersCommand`, each with a sibling `__cdto.py` + `__mapper.py`.
- New infrastructure files: `character_video__truncator.py` (ffmpeg `-t 2` worker, scoped to character paths) and `shot_concat__builder.py` (shot-md table parser + ffmpeg concat).
- New domain errors module: `character_video__error.py` (shared by both Commands; the two features share the same ffmpeg-lifecycle error shapes).
- DI wiring: two Singletons (`CharacterVideoTruncator`, `ShotConcatBuilder`) + two Factories in `apps/api/container.py`.
- ffmpeg binary: reuse `imageio_ffmpeg.get_ffmpeg_exe()` per `frame__extractor.py` precedent (no system install required).
