---
name: video_generation__storyboard-master
description: Break a video concept into shot groups and scene prompts for AI video generation. Use this whenever the user wants storyboards, wants scenes split into 15-second groups, or needs Chinese shot prompts derived from a locked preproduction pack.
---

# Video Generation Storyboard Master

Translate a locked preproduction pack into scene-by-scene shot prompts.

## Preconditions

Prefer to start from:

- `video_generation__preproduction` output
- locked Visual Bible
- locked Continuity Bible

If those do not exist, create a minimal version first instead of improvising loosely.

## Workflow

### 1. Split by scene unit

Default to 15-second groups. Each group should have its own mini-arc and visual purpose.

### 2. Generate shots

For each group, create 3-5 shots with varied framing and clear action.

### 3. Reuse locked wording

Repeat the same character and environment wording verbatim across prompts when identity matters.

### 4. Attach audio intent

Include short voiceover or silence notes that match the visual beats.

## Output Format

```markdown
# Storyboard Pack

## Group 01
Picture 1: ...
Picture 2: ...
Picture 3: ...

## Group 01 Lines
Shot 1: ...
Shot 2: ...
```

## Rules

- prompts should be in Chinese unless the user asks otherwise
- camera language must be explicit
- do not paraphrase locked identity blocks
- if one group is too dense, split it before packaging
