# Follow-up draft 005 — 2026-05-03

Summary: Move the light-theme rule (added to `CLAUDE.md` under `## Project rules (under projects/)` by follow-up 004) out of `CLAUDE.md` and into a NEW shared-refs hierarchy that mirrors the existing per-stage `agent_refs/` layout, so cross-cutting spec-driven project rules can accumulate in one structured place instead of inflating `CLAUDE.md`. The light-theme rule is the seed entry; future cross-project rules land in the same hierarchy.

## Why

`CLAUDE.md` is the rules-and-conventions surface for the harness as a whole. Per-project / per-task-type behavioral rules (light-theme app chrome, future analogues) should live next to the existing per-stage institutional memory under `.claude/agent_refs/`, not as bullets inside `CLAUDE.md`'s "Project rules" section. This keeps `CLAUDE.md` focused on workflow contracts and lets project rules accumulate the same way validation / interview / research lessons do — `general.md` for task-type-agnostic principles, `<task_type>.md` for task-type-specific ones, surgical updates over wholesale rewrites.

## New hierarchy

`.claude/agent_refs/project/` — new sibling of `agent_refs/{interview,research,validation}/`. Layout:

- `.claude/agent_refs/project/general.md` — project-level rules that apply to ALL spec-driven projects regardless of `task_type`. Required reading at the start of every coordinated stage (2, 3, 5) and at every stage-6 work unit.
- `.claude/agent_refs/project/<task_type>.md` (e.g., `development.md`, `ai_video.md`) — task-type-specific project rules. Loaded selectively: `development.md` is required reading only when the current task has `task_type=development`; same pattern for `ai_video.md`. Missing files are not loaded; this matches the existing convention where validation/`ai_video.md` does not exist.
- `.claude/agent_refs/project/development.md` — created by this follow-up to host the light-theme rule, the seed entry.
- `.claude/agent_refs/project/ai_video.md` — NOT created in this follow-up (no content yet); will be added when the first `task_type=ai_video` cross-cutting rule emerges.

Why a sibling under `agent_refs/` rather than a new top-level folder: the spec_driven webapp's `EXPOSED_TREE` already exposes `.claude/agent_refs/**/*.md` for view+edit (per `CLAUDE.md → ## Stage playbooks and reference docs`), so the new files are visible and editable through the existing UX with zero webapp changes. The semantic distinction (stage refs vs project refs) is carried by the subfolder name, not by a separate top-level concept.

## What this changes in `CLAUDE.md`

- `## Project rules (under projects/)`: the bullet **"UI theme: light only..."** is removed. In its place, a one-line forward pointer notes that cross-cutting project rules now live under `.claude/agent_refs/project/{general.md, <task_type>.md}`. Other bullets in that section (one folder per project, backend/frontend layout, Python conventions, README requirement, etc.) stay where they are — they are workflow conventions for the harness, not accumulating institutional memory.
- `## Stage playbooks and reference docs`: extended to describe the new `agent_refs/project/` sibling alongside the existing per-stage subfolders. The reading-rules paragraph adds: at every coordinated stage AND every stage-6 work unit, the parent additionally reads `agent_refs/project/general.md` (always) and `agent_refs/project/<task_type>.md` (when present), and records both paths in the same `pre_reading_consulted` array as the stage refs.
- The `EXPOSED_TREE` glob (`.claude/agent_refs/**/*.md`) already covers the new subfolder — no spec_driven backend or frontend code needs to change.

## What this changes in `.claude/agent_refs/project/`

- New file `general.md`: documents what the folder is for, the loading contract, the surgical-update protocol (mirrors the existing per-stage `general.md` files), and a placeholder "Common principles" section that is intentionally empty in v1 (no rule yet applies to BOTH `development` AND `ai_video` outputs in a way that isn't already a workflow contract in `CLAUDE.md`).
- New file `development.md`: hosts the light-theme rule verbatim, plus the existing carve-out for intentional dark `<pre>` surfaces (regen-prompt panel, code-block palettes), plus the source citation (originated from follow-up 004 of run `spec_driven`). Future development-task project rules append here.

## What this changes in `specs/development/spec_driven/`

- `user_input/revised_prompt.md`: the "Light-theme app chrome" cross-cutting-constraints bullet is updated to reference the new location (`.claude/agent_refs/project/development.md`) instead of `CLAUDE.md → Project rules`. The substantive rule and the carve-outs are unchanged. "Last regenerated" line bumped.
- `changelog.md`: a new "Follow-up 005" entry is appended documenting this restructure.
- No spec FR / NFR / AC / BDD / system-test / unit-test / security / performance / accessibility line is added or removed — the rule's substance (light app chrome, dark `<pre>` carve-outs, no `prefers-color-scheme: dark` on app chrome) is unchanged. The styles.css and api_security.py changes from follow-up 004 are unaffected.

## What this does NOT change

- The light-theme rule itself (substance, scope, carve-outs) — only its storage location.
- Follow-up 004's record. The historical prose in `004-...-light-theme-and-loopback-403-fix.md` continues to say "the source of truth is `CLAUDE.md`" because that was true at the time it was written; this follow-up 005 supersedes the location aspect. Future readers see the evolution by reading 004 then 005.
- The spec_driven webapp's `EXPOSED_TREE` definition or the tree walker. The existing `**/*.md` glob covers the new subfolder.
- The autonomous-mode contract, regeneration semantics, pinning rules, or any other state-surface rule.
- `task_type=ai_video`. No `ai_video.md` is created; the file appears only when an actual cross-cutting rule for that task type emerges.

## Out of scope (this follow-up)

- Migrating any of the *other* "Project rules" bullets from `CLAUDE.md` (Python conventions, backend/frontend folder layout, README requirement, etc.) into the new hierarchy. Those are workflow conventions for the harness; they stay in `CLAUDE.md` unless the user explicitly asks to move them.
- Promoting the new `agent_refs/project/general.md` to mandatory pre-reading for stages 1 and 4 (intake / spec compilation). Those stages are parent-direct without team coordination, and the `general.md` contents are sufficiently slim in v1 that a missing-read in those stages is not a critical failure. If non-trivial general-project rules accumulate later, this can be revisited.
- Editing follow-up 004's prose to reflect the new location. Follow-ups are append-only records of intent at the time they were written.
