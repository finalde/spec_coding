---
name: spec_driven first-project status
description: spec_driven is the inaugural project in this monorepo — its deliverable (a readonly FastAPI+React viewer) is meant to view the very pipeline artifacts that produced it. Tracks where the first pipeline run paused.
type: project
---

`spec_driven` is the first concrete project to exercise the spec-driven workflow. Its deliverable is a readonly FastAPI+React viewer for the workflow's own artifacts (CLAUDE.md, agent definitions, skill definitions, plus per-project `specs/{type}/{name}/{stage}/` trees). It is its own first dogfood — once built, it should be able to render the artifacts that produced it.

**Why:** The user wants the platform's first project to also be the platform's introspection tool, so the workflow's plumbing gets exercised end-to-end and the user has an immediate way to inspect what each stage produced.

**How to apply:** When resuming work on `spec_driven`, expect a meta-loop. The interview/research/spec stages discuss the viewer; the validation strategy stage covers the viewer; the execution stage builds the viewer at `projects/spec_driven/{backend,frontend}/`. The "first project shown" in the viewer's own UI tree is `Projects/development/spec_driven/`.

## Run status (2026-05-02)

- Stage 1 (Intake) — **complete**. Artifacts at `specs/development/spec_driven/user_input/{raw_prompt.md, revised_prompt.md}`.
- Stage 2 (Interview) — **paused**. The first attempt to invoke `agent_team__interview_manager` mid-session failed because Claude Code freezes the Agent tool's `subagent_type` enum at session start; agent files written mid-session aren't picked up. User chose to restart. After restart, invoking `/agent_team` should resume at Stage 2.
- Stages 3–6 — not started.
