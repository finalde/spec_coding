# Project refs — task-type-agnostic

Cross-cutting rules about the *outputs* of every spec-driven project (everything under `projects/{name}/` or `ai_videos/{name}/`), independent of stage.

Loading contract, precedence, and update protocol are in `CLAUDE.md` (§ Stage playbooks and reference docs). In short: required at every coordinated stage AND every stage-6 work unit; per-task-type sibling (`development.md`, `ai_video.md`) overrides this file when present; per-project spec under `specs/{type}/{name}/` overrides this folder for that one project (with a divergence note).

## Common principles

*(intentionally empty in v1 — no rule yet spans both `development` and `ai_video` outputs in a way not already covered by a `CLAUDE.md` workflow contract. Add here only when a rule genuinely spans task types; most rules start in a `<task_type>.md` and only graduate here once a sibling task type adopts the same constraint.)*

## What does NOT belong here

- Project-specific facts → `specs/{type}/{name}/`.
- Harness workflow contracts → `CLAUDE.md`.
- Stage-time-of-use lessons (interview probe shape, validation severity, etc.) → `agent_refs/{stage}/`.
