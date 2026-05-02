---
name: follow-up prompt handling for spec-driven projects
description: Every chat prompt is triaged for spec-driven impact. Impacting prompts persist as follow_ups/, regenerate revised_prompt.md immediately, surgically auto-update conflicting downstream artifacts (qa/dossier/spec/validation/code), log to changelog.md, and never auto-regen stages. Full regen is user-triggered.
type: feedback
---

For any spec-driven project, every new chat prompt runs through this triage before any other action:

1. **Classify.** Casual chat / general question → answer normally, no persistence. Real instruction that could change a known project's intent → continue.
2. **Disambiguate.** If the prompt could impact multiple projects or none, **ask the user** which (or "none"). Don't silently pick.
3. **Persist** as `specs/{type}/{name}/user_input/follow_ups/NNN-{YYYYMMDD-HHmmss}-{slug}.md` (zero-padded sequence, drop chitchat, keep spec-relevant content).
4. **Immediately regenerate** `revised_prompt.md` = raw_prompt + all follow_ups in numerical order. No confirmation.
5. **Scan downstreams** for conflicts/gaps in this order: `interview/qa.md`, `findings/dossier.md` + per-angle files, `final_specs/spec.md`, `validation/*.md`, generated code under `projects/{name}/` or `ai_videos/{name}/`.
6. **Auto-update** affected sections in place — surgical edits, smallest change to resolve. No confirmation.
7. **Inline markers in edited files** (`<!-- auto-updated by follow-up NNN -->`): default to NOT adding. If a particular edit is invasive enough that a local marker would help readers, **ask the user** before adding.
8. **Log to** `specs/{type}/{name}/changelog.md` (append-only, one entry per follow-up, listing artifacts touched).
9. **Never auto-regen a stage.** Don't re-invoke any of the three permanent manager agents. Full regen is the user's call.

**Why:** The user wants the spec-driven workflow to be explicit and deterministic, plus low ceremony. Most follow-ups don't need a full pipeline rerun — just a targeted patch and an audit trail. Conversely, silently picking the wrong project or fabricating section-edits without logging would erode trust in the artifacts. Full regen is reserved for when the user explicitly says so.

**How to apply:**
- Run the triage at the **start** of every turn where the user's prompt could plausibly relate to a spec_driven project. Don't conflate it with general code questions or casual chat.
- Treat the triage decision as the first user-facing action in your reply — explain briefly which project you classified the prompt under (or that you classified it as casual / cross-cutting).
- The four allowed state surfaces (CLAUDE.md, `.claude/settings*`, `specs/`, `.audit/`) still apply — follow-up drafts and changelog entries live in `specs/`, never in memory.
- The full canonical contract for this rule lives in `CLAUDE.md` § "Follow-up prompt handling". This memory entry is the always-loaded reminder; defer to CLAUDE.md if there's any drift.
