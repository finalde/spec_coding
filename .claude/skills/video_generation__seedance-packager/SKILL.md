---
name: video_generation__seedance-packager
description: Convert a storyboard and locked continuity docs into Seedance-ready asset and scene packages. Use this whenever the user wants detailed Seedance prompts, character reference-set instructions, background reference-set instructions, scene anchor frames, or final per-scene generation bundles.
---

# Video Generation Seedance Packager

Package AI-video materials so a human can run Seedance with minimal guesswork.

## Goal

Do not output only a prose prompt. Output a generation spec.

When the user wants copy-paste-ready prompts, default to **one prompt block per asset file**, written entirely in Chinese, so the user can paste it directly into Seedance without merging multiple prompt fragments manually.

Each package should tell Seedance or the human operator:

- what assets to generate first
- how many images to generate
- what views are required
- what must stay fixed
- what files should be saved and reused

## Default Package Structure

Use the closest structure the user asks for, but by default produce:

```text
<package>/
├── visual_bible.md
├── continuity_bible.md
├── characters/
├── backgrounds/
└── scenes/
```

If the user requests custom folder names such as `charactors/`, honor that request.

## Asset Packaging Rules

### Characters

For each recurring character, create a reference-set spec that includes:

- target image count
- required views such as front, left side, right side, back, 3/4 view, expression close-up
- fixed background and lighting instructions
- file naming convention
- acceptance criteria for identity consistency
- one single Chinese prompt that asks for the full image set in one generation instruction when the user prefers easy copy-paste

### Backgrounds

For each recurring environment, create a background-set spec that includes:

- target image count
- required camera angles such as master wide, playable eye-level, low-angle, detail plate
- time-of-day and weather consistency requirements
- file naming convention
- one single Chinese prompt that asks for the full background set in one generation instruction when possible
- explicitly state that each output must be a standalone complete background image, not a grid sheet, collage, storyboard panel, or multiple views combined into one frame

### Scenes

For each scene, create:

- scene brief
- anchor frame specs
- final video prompt
- voiceover map
- operator notes
- if requested, collapse the anchor-frame spec into one single Chinese prompt that asks for all required anchor frames together

## Output Contract

Every asset prompt file should contain:

- purpose
- generation set requirements
- fixed specs
- one final copy-paste-ready Chinese prompt block by default
- file naming convention
- acceptance checklist
- fallback regeneration guidance

## Rule

If the pack cannot preserve continuity with only a final scene prompt, add more upstream reference assets instead of overloading the video prompt.
