---
target_stage: 6
target_artifacts:
  - final_specs/spec.md
severity: medium
---
# Follow-up draft 118 — 2026-05-31
Episode-level "合成本集视频" button: concatenate a whole episode's shot renders into one episode mp4.

In the ai_video_management webapp, while viewing an episode, surface a button that, on click,
automatically scans every shot under the current episode for its rendered mp4 and stitches them,
in shot order, into one big per-episode mp4 placed in the episode folder.

Contract:
- Anchor the button on the episode's `shotlist.md` (`ai_videos/{drama}/episodes/ep{NN}/shotlist.md`),
  shown in the reader toolbar alongside the existing per-shot 🎬 button.
- For each `shots/shot{NN}/` in lexicographic order, take the **newest** `.mp4` found in that shot's
  `renders/` subfolder (the canonical rendered-output location). `archive/` is excluded; a derived
  `shot{NN}_chars.mp4` sitting directly in the shot folder (not under `renders/`) is ignored.
- If a shot has no `renders/` mp4, skip that shot (non-fatal; report it in the result).
- ffmpeg-concatenate the selected full-length clips into `ep{NN}.mp4` in the episode folder
  (uniform 720×1280 9:16, H.264 + AAC). If `ep{NN}.mp4` already exists, overwrite it. The output
  lives in the episode folder (not under `shots/`), so a re-run never re-ingests its own output.
- New `episode` aggregate following the repo's DDD layout: `episode__{route,command,dto,mapper}`,
  `infrastructure/writers/episode__writer.py` (`EpisodeConcatBuilder`), `domain/errors/episode__error.py`;
  endpoint `POST /api/concat-episode`; container + routes + app_factory exception-handler wiring.
- Frontend: `concatEpisode()` in `api.ts`, button + handler in `Reader.tsx`, button styles in `styles.css`.

Disambiguation captured at request time: scan scope = **renders/ subfolder only** (chosen by user over
"recurse whole shot folder"), so the 2-second character reel `shot{NN}_chars.mp4` is never mistaken for
the shot's final render.
