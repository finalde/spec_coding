---
name: video_generation__assembly-planner
description: Plan how separately generated clips should be stitched into one coherent video. Use this whenever the user needs edit order, transition logic, bridge-shot planning, voiceover pacing, or soundtrack guidance after scene generation.
---

# Video Generation Assembly Planner

Design the edit plan after scene generation has been planned or completed.

## Workflow

### 1. Build the timeline spine

Decide the default clip order and explain the emotional logic.

### 2. Plan transitions

For each scene boundary, say whether it needs:

- hard cut
- motion carryover
- sound bridge
- zoom or push transition
- bridge shot or cutaway

### 3. Align narration and sound

Map voice, silence, ambience, and music energy to the timeline.

### 4. Flag missing assets

If the edit depends on shots the user does not have yet, call them out clearly.

## Output Format

```markdown
# Assembly Plan

## Timeline Overview
- ...

## Scene Order
| Order | Scene | Function | Audio Role |
| --- | --- | --- | --- |

## Transition Strategy
| From -> To | Transition | Why | Extra Asset Needed |
| --- | --- | --- | --- |

## Voiceover Pacing Notes
- ...

## Missing Bridge Shots
- ...
```
