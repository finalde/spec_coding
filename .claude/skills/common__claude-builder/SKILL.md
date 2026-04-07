---
name: common__claude-builder
description: Design or update Claude Code components under `.claude/`, including skills, agents, and `CLAUDE.md` rules. Use this whenever the user wants to add an agent, create or rename a skill, reorganize Claude components, introduce naming conventions, or otherwise customize how Claude behaves in this repo.
---

# Common Claude Builder

Help the user choose the right Claude component and implement it cleanly.

## Choose The Right Component

- Use a **skill** for a reusable workflow Claude should follow step by step.
- Use an **agent** for a delegated specialist that reviews or researches independently.
- Use `CLAUDE.md` for always-on rules and conventions.

If the user seems to be asking for the wrong component type, explain the better fit briefly and continue.

## Workflow

### 1. Inspect what already exists

Before creating anything, scan `.claude/` and look for overlap. Prefer extension or consolidation over adding another near-duplicate component.

### 2. Capture the contract

Identify:

- when the component should trigger
- what inputs it expects
- what outputs it should return
- what is explicitly out of scope

### 3. Apply repository conventions

Follow these naming rules:

- `common__...` for broadly reusable components
- `video_generation__...` for AI video workflow components

Do not create new unprefixed repo-owned skills.

### 4. Build the component

When writing a skill or agent:

- make the description field concrete and easy to trigger
- explain the "why" behind important steps
- keep scopes narrow and composable

### 5. Update docs

When component names or responsibilities change, update:

- `CLAUDE.md`
- `.claude/README.md`
- any user-facing README that documents the workflow
