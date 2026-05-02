# Interview — spec_driven

Run: spec_driven-20260503-stage2-regen
Stage: 2 (Interview) — interactive regeneration
Compiled by: parent (agent_team skill, parent_direct synthesis under EXECUTION MODE: INTERACTIVE)
Inputs read: `user_input/revised_prompt.md`, `user_input/follow_ups/001-20260502-095822-editable-webapp.md`, `CLAUDE.md`, `.claude/agents/agent_team__interview_manager.md`, `.claude/agent_refs/agent_team__interview_manager/general.md`
Inputs explicitly NOT read (per `CLAUDE.md → ## Regeneration prompts & autonomous mode → ### Regeneration semantics: read-zero from prior outputs`): any prior `interview/qa.md`, `findings/*`, `final_specs/*`, `validation/*`, `projects/spec_driven/*`.
Promoted items: `interview/promoted.md` does not exist on disk; no pinned items to preserve.

> **Architecture note (interactive regen).** Per CLAUDE.md "Tool scoping and team coordination", the parent owns spawning. The interview manager subagent identified probe categories and emitted a JSON question pool. The parent forwarded the questions to the user via `AskUserQuestion` across six batches (max 4 questions / 4 options per batch by harness contract). All 24 multi-choice questions across 7 categories returned closed-form answers; no "Other" free-text was used. The manager's playbook (`general.md`) calls for round 2 only when threads remain open — they don't here, so round 1 closed the interview.

## Categories probed

The interview manager identified seven probe categories from the revised prompt + follow-up 001:

- **functional-scope** — sidebar globs, project-tree filter, non-stage files visible in the navigation tree.
- **editing-ux** — editor widget choice, save semantics, write-conflict policy, dirty-state indicator.
- **qa-structured-view** — parse model, per-block editor UX, color-token scheme.
- **regen-panel** — module granularity, master-prompt composition model, prompt body content, autonomous-mode toggle persistence.
- **backend-sandbox** — write-extension whitelist, create-new-file scope, per-file size cap, symlink/Windows path rules.
- **deployment-runtime** — dev runtime layout, repo-root discovery, default ports.
- **success-and-failure** — definition of done, missing-artifact UX, oversized-prompt UX.

## Round 1 (interactive, AskUserQuestion)

### functional-scope

**Q:** Section 1 ("Claude Settings & Shared Context") — what exactly belongs in this sidebar section?
- A: Fixed three globs (Recommended) — `CLAUDE.md` + `.claude/agents/*.md` + `.claude/skills/**/SKILL.md`. Matches the revised prompt verbatim. Predictable, small.

**Q:** Section 2 ("Projects") — which projects appear in the tree?
- A: All discovered (Recommended) — backend walks `specs/{type}/{name}/` for every type+name pair on disk; show all. `spec_driven` is just the first; `ai_video` etc. appear automatically when present.

**Q:** Inside a project, which non-stage files appear in the navigation tree?
- A: changelog.md (Recommended) AND follow_ups/*.md individually AND raw_prompt.md (multi-select) — the changelog leaf is navigable at a glance; each follow-up draft gets its own leaf under `user_input/follow_ups/`; the raw prompt is editable via the same path-sandbox. The "hide non-stage files" option was rejected.

### editing-ux

**Q:** What kind of editor backs the file pane when ✎ Edit is toggled?
- A: Plain textarea + monospace (Recommended) — native `<textarea>`, monospace font, no syntax highlighting. Smallest deps, instant load, fine for markdown/yaml/json. Matches "friendly enough that a non-developer can patch a Q/A or spec section without touching a text editor outside the app."

**Q:** How does Save behave?
- A: Replace, stay in editor (Recommended) — `Ctrl+S` writes via `PUT /api/file`, refreshes the buffer, keeps the user in edit mode. Discard reverts to last-saved. Close-editor exits to view (prompts if dirty).

**Q:** What happens if the file changed on disk between load and Save (e.g., another process touched it)?
- A: **Last-write-wins (NOT the recommended option)** — the editor always overwrites with its buffer, even if the file changed externally. The recommended `mtime` guard with 409 conflict was rejected. *Implication for stage 4 spec:* no `If-Match`/`If-Unmodified-Since`-style header on `PUT /api/file`; backend writes unconditionally; the user accepts that running Claude CLI side-by-side with the editor can silently clobber CLI-side changes. Stage 5 validation should test that concurrent CLI writes during an editor session are not detected, only that the final-write-wins outcome is the editor's buffer.

**Q:** How does the UI surface unsaved changes?
- A: Dot in title + warn on nav (Recommended) — dot/asterisk on the file title + Save button highlighted; navigating away or closing the tab triggers a confirm prompt while dirty. Standard editor pattern.

### qa-structured-view

**Q:** How does the structured Q&A view round-trip with the underlying `qa.md` file?
- A: Regex parse, re-emit whole file (Recommended) — parser splits `qa.md` by `## Round` / `### category` / `**Q:**` / `- A:` lines into blocks; per-block edits patch the in-memory tree, re-emit the full markdown, and `PUT /api/file` replaces the file. No sidecar JSON. Single source of truth stays in markdown.

**Q:** What does the per-Q / per-A inline editor look like?
- A: Inline textarea + Save/Cancel (Recommended) — pencil opens a small textarea in place of the block, with Save/Cancel buttons. Save patches the file; Cancel reverts. Other blocks stay in view mode.

**Q:** How are the colored Q/A blocks differentiated?
- A: Q vs A tints + category badge (Recommended) — question blocks: one tint (blue/lavender). Answer blocks: another (green/mint). Each `### category` renders as a colored pill badge above its Q/A pair. Round headers as section dividers. Matches the follow-up's verbatim wording.

### regen-panel

**Q:** What is a "module" inside a stage's regen panel?
- A: One module per artifact file (Recommended) — Stage 2 → `[qa.md]`. Stage 3 → `[dossier.md, angle-*.md]`. Stage 4 → `[spec.md]`. Stage 5 → `[strategy.md, acceptance_criteria.md, bdd_scenarios.md, system_tests.md, unit_tests.md, security.md]`. Checkbox per file. Matches "module checkboxes for the artifacts produced by that stage" verbatim.

**Q:** How does the project's master regen panel produce its single combined prompt?
- A: Single staged prompt (Recommended) — one prompt body that walks the chosen stages in order (intake → interview → ... → execution), each stage section listing its selected modules. The autonomous-mode header appears once at the top. Single paste, single Claude run.

**Q:** What does the assembled regen prompt contain besides the EXECUTION MODE header and module list?
- A: Revised prompt + every follow-up inlined (Recommended) — inline current `revised_prompt.md` plus every `follow_ups/*.md` verbatim, so the pasted prompt is self-contained — a fresh Claude session can act without browsing other files. Matches the autonomous-mode contract in CLAUDE.md.

**Q:** Where does the autonomous-mode toggle's state live?
- A: localStorage, default off (Recommended) — per-browser persistence under `spec_driven.autonomous_mode.v1`; default off. Per CLAUDE.md "the toggle's value is persisted in browser localStorage … there is no server-side persistence." Matches verbatim.

### backend-sandbox

**Q:** Which file extensions does `PUT /api/file` accept?
- A: Same as GET (Recommended) — `.md`, `.yaml`, `.yml`, `.json`, `.txt`. Write whitelist = read whitelist. Editor surfaces only those in the tree, so symmetry keeps the model simple.

**Q:** Can the editor create new files (e.g., a new follow-up draft) or only edit existing ones?
- A: Edit existing only (Recommended) — `PUT /api/file` requires the path to already exist. New follow-ups are created via the Claude CLI / a separate flow. Smaller surface; matches "every file in the existing exposed tree is editable."

**Q:** What is the per-file size cap on writes (and reads) under the sandbox?
- A: **10 MB (NOT the recommended option)** — the recommended 1 MB cap was rejected. *Implication for stage 4 spec:* `PUT /api/file` and `GET /api/file` enforce a 10 MB body cap rather than 1 MB. Any individual artifact is allowed up to 10 MB. Stage 5 validation checks the boundary at 10 MB (200 OK at 10 MB exactly; 413 above). Largest current file in the repo is well under 100 KB, so this cap is principally a defensive ceiling against accidental binary paste.

**Q:** How does the sandbox handle symlinks and Windows path quirks?
- A: Resolve + reject if outside repo (Recommended) — backend resolves the requested path with `realpath`, refuses (403) if the resolved path leaves the repo root. Case-insensitive comparison on Windows. Matches the reader's existing rule.

### deployment-runtime

**Q:** How is the app run during development?
- A: Two-port dev with Vite proxy (Recommended) — `uvicorn` on `:8000` + `vite dev` on `:5173`, vite proxies `/api/*` to `:8000`. Standard React+FastAPI dev split; hot reload on both sides; one make target starts both.

**Q:** How does the FastAPI backend discover the repo root (which it serves files from)?
- A: Walk up to find CLAUDE.md (Recommended) — on startup, walk parents from the backend's CWD until a `CLAUDE.md` + `.claude/` pair is found; that's the root. Zero config; matches the monorepo's invariant.

**Q:** What are the default ports?
- A: Backend `:8000`, frontend `:5173` (Recommended) — FastAPI default + Vite default. Both overridable via env vars (`UVICORN_PORT`, `VITE_PORT`). Lowest surprise.

### success-and-failure

**Q:** What does "done" look like for the spec_driven app at the end of stage 6?
- A: BDD pass + manual smoke (Recommended) — every BDD scenario from stage 5 passes (browse, edit-roundtrip, structured Q/A edit, regen-prompt copy, master-panel combine), plus a 10-minute manual smoke covering all sidebar entries. Backend has unit tests for the sandbox.

**Q:** How does the UI behave when the user clicks a stage file that doesn't exist yet (e.g., `final_specs/spec.md` before stage 4 has run)?
- A: Empty state + regen panel mounted (Recommended) — file pane renders "Not yet generated — paste this prompt to produce it" with the same Regenerate panel mounted, so the user can immediately regen. Sidebar entry is still listed (greyed).

**Q:** What happens if the assembled regen prompt is huge (e.g., 50+ KB after inlining revised_prompt + every follow-up)?
- A: Always copy verbatim, show size (Recommended) — UI shows "prompt: 47 KB / ~12k tokens" next to the Copy button; copies in full. Trusts the user to paste. No silent truncation.

## Team consensus

After one round of user-facing questions (24 multi-choice across 7 categories), the interviewer team reached consensus:

- All 7 categories returned `{"clear": true}`. No category had remaining open threads.
- 22 of 24 answers matched the manager's recommended option. Two deliberate divergences:
  1. **ConflictPolicy** = `Last-write-wins` (recommended was the `mtime` guard with 409 conflict). The user accepts that concurrent CLI writes can be silently clobbered by the editor's buffer.
  2. **SizeCap** = `10 MB` (recommended was 1 MB). The user wants a more permissive ceiling.
- No category required round 2; the playbook caps interview iterations at 3 rounds and triggers round 2 only when threads remain open.

The interview manager declared the requirement crystal-clear for spec compilation. Stage 4 (spec compilation) has closed-form answers for every load-bearing decision; the two non-recommended choices are flagged inline so the spec author treats them as binding rather than re-deriving from the recommendation.

## Notes for downstream stages

- **Stage 3 research** angles can lean lighter on conflict-detection prior art (since the project picked `last-write-wins`) and lighter on size-cap research (since 10 MB is a generous ceiling). More effort can go into structured-Q/A parsing prior art and master-regen-prompt composition patterns (those got the greatest specificity here).
- **Stage 4 spec** must encode FRs for: the "Resolve + reject if outside repo" sandbox (FR-resolve), the 10 MB body cap (FR-size, divergent from recommendation), the last-write-wins write semantics (FR-write-conflict, divergent), and the missing-artifact empty state (FR-missing).
- **Stage 5 validation** AC scenarios should explicitly cover: (a) a `PUT /api/file` succeeds at 10 MB exactly and fails at 10 MB + 1 byte; (b) a concurrent CLI write before save is silently overwritten by the editor (no 409); (c) a click on a non-existent stage file renders the empty-state pane WITH the Regenerate panel still mounted; (d) the master regen panel emits a single staged prompt with one EXECUTION MODE header; (e) all three Section 1 globs render as clickable leaves and CLAUDE.md / agent / skill files all open in the reader.
- **Stage 6 execution** — per "BDD pass + manual smoke" definition of done: BDD scenarios drive automated coverage; a 10-minute manual walkthrough is part of sign-off.
