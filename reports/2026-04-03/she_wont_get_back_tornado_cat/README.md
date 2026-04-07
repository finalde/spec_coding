# Seedance Material Pack

## Selected Example

- Source report: `reports/shorts/2026-04-04.md`
- Selected item: `She won't get back 😭#sora2 #aivideo #cat #tornado #shorts`
- Reason selected: single main character, single dominant environment, easy to expand into a 30-second two-scene Seedance test run

## Folder Structure

- `charactors/`
  - role and identity prompts for character image generation
  - should produce a reusable reference set, not just one picture
  - put your generated character reference images in this folder later
- `background/`
  - background and environment prompts
  - should produce a reusable environment set with multiple camera angles
  - put your generated background reference images in this folder later
- `scene/`
  - `scene_01.md`
  - `scene_02.md`
  - each file contains only one final copy-paste-ready prompt

## Recommended Seedance Order

1. Generate the full cat reference set from `charactors/main_cat_prompt.md`.
2. Generate the full storm-road background set from `background/storm_road_prompt.md`.
3. Generate the first 15-second video using `scene/scene_01.md`.
4. Generate the second 15-second video using `scene/scene_02.md`.
7. If identity drifts, keep the same cat wording and regenerate from the uploaded reference images instead of rewriting the character description.

## Output Discipline

- Keep the chosen best cat identity image as the master identity reference.
- Keep the chosen best wide background image as the master environment reference.
- Use the same uploaded role and background references for both scenes.
- Reject outputs that change species proportions, cat face structure, or the core storm-road layout.
