# Changelog — spec_driven

## Follow-up 001 — 2026-05-02 09:58:22
Source: user_input/follow_ups/001-20260502-095822-editable-webapp.md
Summary: Drop readonly constraint. Editable in place for every file, structured colored Q/A view for `interview/qa.md`, per-stage and per-project regen-prompt panels with autonomous-mode toggle, autonomous-mode contract documented in `CLAUDE.md`.

Auto-updated:
- `specs/development/spec_driven/user_input/revised_prompt.md` — full regenerate (raw + 001) per the auto-regen rule.
- `specs/development/spec_driven/interview/qa.md` — round-1 functional-scope answer about "no editing/etc" rewritten to confirm editing is now in scope and call out 001 as the source.
- `specs/development/spec_driven/final_specs/spec.md` — Goal restated as viewer/editor; "Out of scope" rewritten (editing struck, deletes/uploads/diff still out, copy-paste regen explained); new FR-14a/14b/14c (backend write + stages + regen-prompt endpoints); new FR-40..FR-44 (frontend Edit toggle, structured Q/A view, per-stage and project-page Regenerate panels, autonomous-mode persistence); NFR-6 reworded to permit the new endpoints with the same sandbox.
- `specs/development/spec_driven/findings/dossier.md` — appended "Addendum (follow-up 001)" calling out atomic write, server-side prompt assembly, and the autonomous-mode-as-CLAUDE.md-contract decisions.
- `specs/development/spec_driven/validation/acceptance_criteria.md` — AC-23 rewritten so PUT/POST hit the sanctioned endpoints and only PATCH/DELETE/upload return 405.
- `specs/development/spec_driven/validation/security.md` — SEC-10 expected-behavior block rewritten for the new mutation surface; pass criterion updated to enforce the three-route, three-verb shape.
- `specs/development/spec_driven/validation/system_tests.md` — SYS-10 rewritten to round-trip a scratch file via PUT, exercise the regen-prompt endpoint, and re-confirm PATCH/DELETE/upload remain 405.
- `specs/development/spec_driven/validation/unit_tests.md` — 8.11 rewritten so the routing-surface unit covers PUT-200 / POST-regen-200 / PATCH-405 / DELETE-405.
- `projects/spec_driven/backend/libs/api.py` — added `PUT /api/file`, `GET /api/stages`, `POST /api/regen-prompt`.
- `projects/spec_driven/backend/libs/file_writer.py` — new module: atomic temp+rename write, same sandbox/extension/size/symlink rules as the reader.
- `projects/spec_driven/backend/libs/regen_prompt.py` — new module: canonical six-stage definition + prompt builder (inlines current `revised_prompt.md` and `follow_ups/*.md`).
- `projects/spec_driven/frontend/src/api.ts` — added `saveFile`, `fetchStages`, `buildRegenPrompt` and their types.
- `projects/spec_driven/frontend/src/components/Editor.tsx` — new file-level editor (Save/Discard/Close, Ctrl+S, dirty indicator).
- `projects/spec_driven/frontend/src/components/Reader.tsx` — wired Edit toggle, structured Q/A view dispatch, Regenerate panel hook (panel + Q/A view files arrive in subsequent commits per the in-progress task list).

Pending follow-on edits not auto-applied:
- `CLAUDE.md` — needs the new `## Regeneration prompts & autonomous mode` section (next on the in-progress task list, will be done in this same session).
- The frontend pieces still in flight: `QaView.tsx`, `RegeneratePanel.tsx`, project parent route, CSS for editor/Q-A blocks/regen panel. Tracked under tasks #3–#5; the changelog will not get a second entry for these because they belong to the same follow-up 001.

No conflicts found in:
- `specs/development/spec_driven/findings/angle-prior-art-readonly-viewers.md`
- `specs/development/spec_driven/findings/angle-two-pane-navigator-reader-ux.md`
- `specs/development/spec_driven/findings/angle-markdown-link-resolution-patterns.md`
- `specs/development/spec_driven/findings/angle-filesystem-readonly-viewer-risks.md`
  (these are historical research outputs; their findings still apply to the editable scope and the dossier addendum captures the deltas)
- `specs/development/spec_driven/validation/strategy.md`
- `specs/development/spec_driven/validation/bdd_scenarios.md`
- `specs/development/spec_driven/validation/accessibility.md`
- `specs/development/spec_driven/validation/performance.md`
