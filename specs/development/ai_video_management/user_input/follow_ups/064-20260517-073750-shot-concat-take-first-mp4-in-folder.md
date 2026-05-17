# Follow-up draft 064 — 2026-05-17
Refine the shot-concat contract introduced in follow-up 054.

## Change

Replace the per-character `video.mp4` lookup with "first mp4 directly inside the character folder, alphabetical order, case-insensitive extension match against the project's video allowlist." Only when the folder contains no mp4 at the top level do we report it as missing.

## Why

Per follow-up 054 the concat looked for `<char_folder>/video.mp4` specifically, on the assumption that the user would first click "✂ 截到 2s → video.mp4" on a chosen take. In practice the user does not want to pre-stage the clips — they expect the concat button to "just work" against whatever mp4s already exist in the character folders. The truncate button remains as an independent utility but is no longer a prerequisite.

## Spec

- Source selection: `Path.iterdir()` filtered to top-level non-symlink files whose `.suffix.lower()` is in `VIDEO_EXTENSIONS`, sorted by `name`, first element wins. Subdirectories (e.g. `archive/`) are skipped automatically.
- Output filename and location unchanged: `<shot_folder>/<shotNN>_chars.mp4`.
- Skip reasons emitted by the backend:
  - `invalid_character_path` — `character file` cell in the shot md did not resolve to `characters/cN_xxx/` under the same drama.
  - `character_folder_missing` — the resolved folder does not exist on disk.
  - `no_mp4_in_folder` — folder exists but has no mp4 at the top level. **Replaces** the old `video_mp4_missing` reason.

## Touch list

- `libs/infrastructure/writers/character_video__writer.py` —
  - Drop the `_VIDEO_FILENAME = "video.mp4"` constant.
  - Inside `ShotConcatBuilder.build`, replace the fixed-name resolve + `is_file()` check with: resolve folder; new helper `_first_mp4_in_folder(folder: Path) -> Path | None`; map `None` → `no_mp4_in_folder` skip.
  - New `@staticmethod _first_mp4_in_folder` next to `_character_folder_for`.
- `apps/ui/src/components/Reader.tsx` —
  - Toast text for the empty-output case: `未生成 — 没有角色文件夹包含 mp4` (was `未生成 — 0 个角色具备 video.mp4`).
  - Button `aria-label` + `title` updated to describe the new "first mp4 in folder" behavior.

## Out of scope

- Feature 1 ("✂ 截到 2s → video.mp4") is unchanged — still useful on its own, just no longer the prerequisite step for feature 2.
