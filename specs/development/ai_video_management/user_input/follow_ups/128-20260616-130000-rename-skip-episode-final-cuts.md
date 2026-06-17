# Follow-up draft 128 — 2026-06-16
Episode-level final-cut videos must not be mangled by the import/rename pass.

The drama-scoped batch rename (`MediaRenamer.rename_drama`, used by both the
standalone rename button and the import button) recursively walks every folder
under `ai_videos/{drama}/` and renames media files to match their parent
folder name. This sweeps the final-cut videos that the subtitle-burn / episode-
concat feature writes directly into each episode root (`episodes/ep{NN}/
ep{NN}_{lang}.mp4`): a folder named `ep01` holding two `.mp4` files gets them
renamed to `ep011.mp4` / `ep012.mp4` (e.g. a user's `ep1_zh.mp4` became
`ep012.mp4`), destroying the meaningful language-tagged name and breaking
playback selection.

Rule: the rename pass MUST NOT rename media that lives anywhere under the
`episodes/` subtree. Shot renders there are already preserved (they live in the
name-excluded `renders/` subfolder); episode-root final cuts are the only other
media under `episodes/` and they carry deliberate names (`ep{NN}_{lang}.mp4`)
that must be preserved byte-for-byte. Only the asset folders the rename is
designed to canonicalize — `characters/`, `scenes/` and their `bg*` plate
subfolders — should be touched. Excluding the whole `episodes/` subtree from the
rename walk is the fix; it changes nothing for renders (already excluded) and
stops the final-cut mangling.
