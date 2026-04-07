---
name: common__skill-creator
description: Create or improve a repo-owned Claude skill. Use this whenever the user wants to draft a new skill, rename an existing skill, merge overlapping skills, improve a skill description, or refactor a skill's workflow and output contract.
---

# Common Skill Creator

Create or revise skills so they trigger reliably and stay easy to maintain.

## Workflow

### 1. Capture intent

Understand:

- what workflow the skill should encode
- what user requests should trigger it
- what output shape it should produce
- what quality bar matters most

### 2. Check for overlap

Before creating a new skill, ask whether an existing skill should be:

- extended
- merged
- renamed
- deprecated

Prefer fewer skills with clearer ownership.

### 3. Write the skill

Each skill should include:

- a precise `name`
- a trigger-rich `description`
- a compact workflow
- a clear output format
- handling for ambiguity and edge cases

### 4. Apply naming rules

- `common__...` for cross-domain skills
- `video_generation__...` for AI video skills

### 5. Validate

Before finishing, sanity-check:

- the skill does not duplicate another skill
- the description is likely to trigger on real user phrasing
- the output format is explicit enough to be reused by later steps
