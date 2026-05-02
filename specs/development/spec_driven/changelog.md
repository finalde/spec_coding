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

## Autonomous regen — 2026-05-02 (run spec_driven-20260502-autoregen)
Source: user invoked the full-pipeline autonomous regen prompt (EXECUTION MODE: AUTONOMOUS, all six stages selected).
Summary: Re-ran every stage. Stage 1 was a no-op (revised_prompt already canonical, only the timestamp line was bumped). Stages 2–5 received targeted updates rather than full rewrites — preserving prior user-facing Q&A and research, and adding new content for the two follow-up-001 areas that prior runs only addended (in-place markdown editor UX; autonomous-mode header / copy-paste regen pattern). Stage 6 implemented the new spec language.

Auto-updated:
- `specs/development/spec_driven/user_input/revised_prompt.md` — bumped "Last regenerated" line to mark this as an autonomous full-pipeline regen.
- `specs/development/spec_driven/interview/qa.md` — added Round 3 (autonomous, follow-up-001 categories) with judgment-call answers for editing-ux, qa-structured-view, regen-panel, and autonomous-mode. Each answer is annotated `*(judgment call — chose X because Y)*` and bound to the FR/CLAUDE.md slice it informs. Rounds 1–2 (real user-facing Q&A) preserved verbatim.
- `specs/development/spec_driven/findings/angle-markdown-editor-ux.md` — new angle file (researched via WebSearch + WebFetch by a subagent: GitHub web editor, Obsidian, MkDocs Material, GitBook, Notion, VS Code Web). 8 evidence-backed recommendations.
- `specs/development/spec_driven/findings/angle-autonomous-mode-and-copypaste-regen.md` — new angle file (researched via WebSearch + WebFetch: Claude Code plan mode, OpenAI Model Spec, Cursor rules, Aider, AGENTS.md/Codex, Continue.dev, Spec Kit, JetBrains Junie). 8 recommendations.
- `specs/development/spec_driven/findings/dossier.md` — angle list updated to 6; added 4 new cross-cutting insights (editor and file-server must not trust each other; header-based mode contracts non-standard; editor save and pipeline regen are the same mutation shape; etc.); added recommendations 17–24 (dirty dot, stay-in-editor, persistent inline error banner, literal header + MUST NOT pairing, CLAUDE.md backing, no Jinja in v1, section breakdown beside Copy, warn-don't-truncate). Addendum reworked to point at the two new angle files.
- `specs/development/spec_driven/final_specs/spec.md` — Run id bumped to autoregen. FR-14c extended with the verbatim imperative line under autonomous mode AND the warn-don't-truncate size policy (50 KB warn / 1 MB hard ceiling). FR-40c extended with dirty-dot indicator + deep-equality dirty computation. FR-40e extended with persistent inline banner. FR-42 extended with the section-breakdown line (FR-42d) and the size-warning banner (FR-42e). FR-43 references the same. FR-44 documents the cross-tab `storage` event mechanism. New OQ-8/9/10.
- `specs/development/spec_driven/validation/strategy.md` — Run id bumped; FR/AC counts updated.
- `specs/development/spec_driven/validation/acceptance_criteria.md` — Run id bumped. New AC-24 (dirty dot), AC-25 (persistent banner), AC-26 (size policy warn-don't-truncate), AC-27 (breakdown line + warning banner).
- `specs/development/spec_driven/validation/bdd_scenarios.md` — Run id bumped. New Features: Editor dirty-dot + persistent error banner; Regen-prompt size policy (Scenario Outline with three Examples rows); Regen panel section breakdown.
- `specs/development/spec_driven/validation/unit_tests.md` — Run id bumped. New Group 11 (regen-prompt size policy + section breakdown — 6 cases) and Group 12 (editor dirty-state + persistent error banner — 4 cases).
- `specs/development/spec_driven/validation/system_tests.md` — New SYS-21 (warn-don't-truncate end-to-end), SYS-22 (editor dirty-dot + banner Playwright round-trip).
- `projects/spec_driven/backend/libs/regen_prompt.py` — new `RegenPromptResult` dataclass + `build_regen_prompt_result` wrapper; 50 KB warn / 1 MB hard ceiling enforcement.
- `projects/spec_driven/backend/libs/api.py` — `POST /api/regen-prompt` now returns `{prompt, warning, selected_stages_count, follow_ups_count, autonomous, bytes}` and a 413 on hard-ceiling overflow.
- `projects/spec_driven/frontend/src/api.ts` — `buildRegenPrompt` now returns `RegenPromptResponse` (not raw string); error path threads through structured error keys.
- `projects/spec_driven/frontend/src/components/RegeneratePanel.tsx` — added section breakdown line beside Copy button; warning banner when API returns a `warning` field; build-error banner.
- `projects/spec_driven/frontend/src/components/Editor.tsx` — separated `lastSavedText` from `initialText` (deep equality dirty); added filled-circle dirty-dot in toolbar; converted save error from in-toolbar text to a persistent inline banner above the textarea.
- `projects/spec_driven/frontend/src/styles.css` — new classes for `.editor-dirty-dot`, `.editor-error-banner`, `.regen-summary-line`, `.regen-breakdown`, `.regen-warning`, `.regen-error`.

No conflicts found in:
- `.claude/agents/*.md` (manager contracts unchanged)
- `CLAUDE.md` autonomous-mode section (already byte-for-byte aligned with the new FR-14c imperative line)
- `projects/spec_driven/backend/libs/{exposed_tree,file_reader,file_writer,repo_root,safe_resolve,tree_walker}.py` (unchanged)
- `projects/spec_driven/frontend/src/components/{QaView,Sidebar,Reader,Breadcrumb,RefreshButton,BrokenLink,ProjectPage}.tsx` (the new dirty-dot/breakdown logic lives in Editor.tsx and RegeneratePanel.tsx only)
- `specs/development/spec_driven/validation/{security,performance,accessibility}.md` (no behavioral changes to the surfaces they cover; the new editor banner is a string change inside an already-asserted `<div role="alert">`).

## Clean-state autonomous regen — 2026-05-02 (run spec_driven-20260502-clean)
Source: user clarified the regeneration contract — "regenerate means regenerate from a clean state, which means remove all previous files and caches" — and ran the full-pipeline autonomous regen under that rule.
Summary: All stage 2-5 spec artifacts and the entire `projects/spec_driven/` folder were deleted on disk, then every artifact was regenerated from scratch reading ONLY the inputs (`user_input/*`, prior stages' new outputs, `CLAUDE.md`, `.claude/agents/*`). No prior file content carried forward.

Hardening before the run (the contract addition):
- `CLAUDE.md` — added `### Regeneration semantics: read-zero from prior outputs` subsection under `## Regeneration prompts & autonomous mode`. Per-stage delete-then-regenerate table; explicit prohibition on surgical edits during regeneration; audit-event contract (`regen.delete.planned` / `regen.delete.completed` / `regen.write.completed`).
- `projects/spec_driven/backend/libs/regen_prompt.py` — added the read-zero contract paragraph to the assembled prompt's `### Constraints` section, plus the audit-event guidance, so every future copy-paste prompt carries the rule.

Files deleted before regen (real `rm -rf`, not logical):
- `specs/development/spec_driven/{interview,findings,final_specs,validation}/` (all 17 files).
- `projects/spec_driven/` (45+ files including backend Python, frontend TS/CSS, tests, package-lock, node_modules, dist, .vite cache). Empty `frontend/` directory entry persisted due to an IDE file-handle lock; all CONTENT was deleted.

Files regenerated:
- `specs/development/spec_driven/user_input/revised_prompt.md` — timestamp bumped (intake stage has no prior outputs to delete; revised_prompt is rewritten from raw + follow-ups in place).
- `specs/development/spec_driven/interview/qa.md` — clean-slate Round 1 with judgment-call answers across 7 probe categories under autonomous mode.
- `specs/development/spec_driven/findings/{dossier.md, angle-prior-art-readonly-viewers.md, angle-two-pane-navigator-reader-ux.md, angle-markdown-link-resolution-patterns.md, angle-filesystem-readonly-viewer-risks.md, angle-markdown-editor-ux.md, angle-autonomous-mode-and-copypaste-regen.md}` — six fresh research angles produced by parallel researcher subagents using real WebSearch + WebFetch, ~100 cited sources total.
- `specs/development/spec_driven/final_specs/spec.md` — 44 FRs, 16 NFRs, 27 ACs, 9 OQs.
- `specs/development/spec_driven/validation/{strategy.md, acceptance_criteria.md, bdd_scenarios.md, unit_tests.md, system_tests.md, security.md, performance.md, accessibility.md}` — 303 testable items total (27 AC + 70 BDD + 129 unit + 24 system + 8 perf + 20 sec + 25 a11y).
- `projects/spec_driven/{Makefile, README.md, backend/**, frontend/**}` — full FastAPI + React app rebuilt from the spec by two parallel implementation subagents (backend 25 files / ~1475 LOC, frontend 23 files / 11 components).

Validation outcomes:
- One blocker raised by runtime validation (extension-vs-EXPOSED_TREE check ordering on `findings/diagram.png` — AC-8 expected 415 but the implementation returned 404). Fixed by separating structural-membership from extension-whitelist enforcement: `is_inside` no longer couples extension into the specs/ glob, file_reader still does the 415 extension check after membership. Three files revised; all tests green after.
- Backend pytest: **50 passed, 2 skipped** (2 Windows-symlink + os.replace-PermissionError tests skip on Windows).
- Frontend `tsc -b`: **exit 0** (strict mode, noUnused* clean).
- Frontend `vite build`: produces `dist/` bundle.
- Smoke test: `python main.py` boots; `GET /api/tree` returns 200 with the development task type and 3 agents; `GET /api/file?path=specs/development/spec_driven/final_specs/spec.md` returns 200 with the new spec content; `POST /api/regen-prompt {autonomous: true}` emits the literal `# EXECUTION MODE: AUTONOMOUS` header, the verbatim imperative line, AND the read-zero contract language in the constraints section.
- Backend deps installed via repo `.venv` (`fastapi`, `uvicorn[standard]`, `pydantic`, `pytest`, `httpx`).
- Frontend deps installed via `npm install` (managed by the impl-frontend subagent).

Audit:
- `.audit/adhoc_agents/2026-05-02/spec_driven-20260502-clean/events.jsonl` (full event stream including delete/spawn/write/validation events).
- `.audit/adhoc_agents/2026-05-02/spec_driven-20260502-clean/spawns/` (8 spawn audit pairs: 6 researchers + 5 validation level specialists + 2 implementation builders).
