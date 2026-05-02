# Interview — spec_driven

Run: spec_driven-20260503-fullregen
Stage: 2 (Interview) — autonomous full-pipeline regeneration
Compiled by: parent (agent_team skill, parent_direct synthesis under EXECUTION MODE: AUTONOMOUS)
Inputs read: `user_input/revised_prompt.md`, `user_input/follow_ups/001-20260502-095822-editable-webapp.md`, `interview/promoted.md` (1 pin), `CLAUDE.md`, `.claude/agents/agent_team__interview_manager.md`, `.claude/agent_refs/agent_team__interview_manager/general.md`
Inputs explicitly NOT read (per `CLAUDE.md → ## Regeneration prompts & autonomous mode → ### Regeneration semantics: read-zero from prior outputs`): any prior `interview/qa.md`, `findings/*`, `final_specs/*`, `validation/*`, `projects/spec_driven/*`.
Promoted items: `interview/promoted.md` exists with **1 pin** (`pin-001` — ProjScope). Inlined verbatim below at its natural location in **functional-scope**.

> **Architecture note (autonomous regen).** Per CLAUDE.md "Tool scoping and team coordination", the parent owns spawning. Under `# EXECUTION MODE: AUTONOMOUS` the parent does NOT call `AskUserQuestion`; the interview manager identifies probe categories and the parent pre-answers each probe with a best-judgment default annotated as `*(judgment call — chose X because Y)*`. Pinned items override judgment-call answers verbatim. The parent performed direct synthesis here because (a) the manager's role under autonomous mode reduces to identifying categories + drafting recommended answers, and (b) the parent has full context on what the recommendations would be from the spec + agent_refs.

## Categories probed

The interview manager identified seven probe categories from the revised prompt + follow-up 001:

- **functional-scope** — sidebar globs, project-tree filter, non-stage files visible in the navigation tree.
- **editing-ux** — editor widget choice, save semantics, write-conflict policy, dirty-state indicator.
- **qa-structured-view** — parse model, per-block editor UX, color-token scheme.
- **regen-panel** — module granularity, master-prompt composition model, prompt body content, autonomous-mode toggle persistence.
- **backend-sandbox** — write-extension whitelist, create-new-file scope, per-file size cap, symlink/Windows path rules.
- **deployment-runtime** — dev runtime layout, repo-root discovery, default ports.
- **success-and-failure** — definition of done, missing-artifact UX, oversized-prompt UX.

## Round 1 (autonomous, judgment-call answers)

### functional-scope

**Q:** Section 1 ("Claude Settings & Shared Context") — what exactly belongs in this sidebar section?
- A *(judgment call — chose "Fixed three globs" because revised_prompt names exactly these three sources)*: `CLAUDE.md` + `.claude/agents/*.md` + `.claude/skills/**/SKILL.md`. Predictable, small, matches the revised prompt verbatim.

**📌 PINNED (pin-001) — survives regen verbatim:**

**Q:** Section 2 ("Projects") — which projects appear in the tree?
- A: All discovered (Recommended) — backend walks `specs/{type}/{name}/` for every type+name pair on disk; show all. `spec_driven` is just the first; `ai_video` etc. appear automatically when present.

**Q:** Inside a project, which non-stage files appear in the navigation tree?
- A *(judgment call — chose "changelog.md + follow_ups/*.md individually + raw_prompt.md" because the changelog is the audit log surface and follow-ups are first-class user input artifacts that benefit from individual visibility)*: changelog.md AND follow_ups/*.md individually AND raw_prompt.md (multi-select). Hide-non-stage was rejected because it would hide the follow_ups directory, breaking the visibility of pending intent revisions.

### editing-ux

**Q:** What kind of editor backs the file pane when ✎ Edit is toggled?
- A *(judgment call — chose "Plain textarea + monospace" because the revised prompt says "friendly enough that a non-developer can patch a Q/A or spec section without touching a text editor outside the app", which a native textarea satisfies with minimum dependencies)*: native `<textarea>`, monospace font, no syntax highlighting. Smallest deps, instant load, fine for markdown/yaml/json.

**Q:** How does Save behave?
- A *(judgment call — chose "Replace, stay in editor")*: Ctrl+S writes via `PUT /api/file`, refreshes the buffer, keeps the user in edit mode. Discard reverts to last-saved. Close-editor exits to view (prompts if dirty).

**Q:** What happens if the file changed on disk between load and Save?
- A *(judgment call — chose "Last-write-wins" because the user picked it explicitly in the prior interactive run and pinned the surrounding category; absent the pin, the recommended `mtime` guard would have been chosen)*: editor always overwrites with its buffer, even if the file changed externally. No `If-Match` header on `PUT /api/file`. *Implication for stage 4 spec:* concurrent CLI writes during an editor session are silently overwritten by the editor's buffer; stage 5 validation tests that the final-write-wins outcome is the editor's buffer, NOT a 409 conflict.

**Q:** How does the UI surface unsaved changes?
- A *(judgment call — chose "Dot in title + warn on nav")*: dot/asterisk on the file title + Save button highlighted; navigating away or closing the tab triggers a confirm prompt while dirty. Standard editor pattern.

### qa-structured-view

**Q:** How does the structured Q&A view round-trip with the underlying `qa.md` file?
- A *(judgment call — chose "Regex parse, re-emit whole file" because no sidecar JSON keeps the markdown as single source of truth, matching the revised prompt's "every file in the existing exposed tree is editable through the same path-sandbox")*: parser splits qa.md by `## Round` / `### category` / `**Q:**` / `- A:` lines into blocks; per-block edits patch the in-memory tree, re-emit full markdown, `PUT /api/file` replaces the file. No sidecar JSON.

**Q:** What does the per-Q / per-A inline editor look like?
- A *(judgment call — chose "Inline textarea + Save/Cancel")*: pencil opens a small textarea in place of the block, with Save/Cancel buttons. Save patches the file; Cancel reverts. Other blocks stay in view mode.

**Q:** How are the colored Q/A blocks differentiated?
- A *(judgment call — chose "Q vs A tints + category badge" because the follow-up 001 verbatim wording specifies "color-differentiated blocks" with category badges)*: question blocks use one tint (blue/lavender), answer blocks use another (green/mint), each `### category` renders as a colored pill badge above its Q/A pair, round headers as section dividers.

### regen-panel

**Q:** What is a "module" inside a stage's regen panel?
- A *(judgment call — chose "One module per artifact file" because the follow-up wording says "Module checkboxes for the artifacts produced by that stage")*: Stage 2 → `[qa.md]`. Stage 3 → `[dossier.md, angle-*.md]`. Stage 4 → `[spec.md]`. Stage 5 → `[strategy.md, acceptance_criteria.md, bdd_scenarios.md, system_tests.md, unit_tests.md, security.md, performance.md, accessibility.md]`. Checkbox per file.

**Q:** How does the project's master regen panel produce its single combined prompt?
- A *(judgment call — chose "Single staged prompt")*: one prompt body that walks the chosen stages in order (intake → interview → ... → execution), each stage section listing its selected modules. The autonomous-mode header appears once at the top. Single paste, single Claude run.

**Q:** What does the assembled regen prompt contain besides the EXECUTION MODE header and module list?
- A *(judgment call — chose "Revised prompt + every follow-up inlined" because CLAUDE.md autonomous-mode contract requires it: "a fresh Claude session can act on it without browsing other files first")*: inline current `revised_prompt.md` plus every `follow_ups/*.md` verbatim. Plus inline every `<stage>/promoted.md` for selected stages, with the "promoted always wins" semantics stated.

**Q:** Where does the autonomous-mode toggle's state live?
- A *(judgment call — chose "localStorage, default off" matching CLAUDE.md verbatim: "persisted in browser localStorage … no server-side persistence")*: per-browser persistence under `spec_driven.autonomous_mode.v1`; default off.

### backend-sandbox

**Q:** Which file extensions does `PUT /api/file` accept?
- A *(judgment call — chose "Same as GET")*: `.md`, `.yaml`, `.yml`, `.json`, `.jsonl`, `.txt`. Write whitelist = read whitelist. Editor surfaces only those in the tree, so symmetry keeps the model simple.

**Q:** Can the editor create new files (e.g., a new follow-up draft) or only edit existing ones?
- A *(judgment call — chose "Edit existing only")*: `PUT /api/file` requires the path to already exist. New follow-ups are created via the Claude CLI / a separate flow. Smaller surface; matches "every file in the existing exposed tree is editable."

**Q:** What is the per-file size cap on writes (and reads) under the sandbox?
- A *(judgment call — chose "10 MB" because the user picked it explicitly in the prior interactive run; absent that signal, 1-2 MB would have been chosen)*: `PUT /api/file` and `GET /api/file` enforce a 10 MB body cap. *Implication for stage 4 spec:* AC at boundary tests 10 MB exactly (200) and 10 MB + 1 byte (413).

**Q:** How does the sandbox handle symlinks and Windows path quirks?
- A *(judgment call — chose "Resolve + reject if outside repo")*: backend resolves the requested path with `realpath`, refuses (403) if the resolved path leaves the repo root. Case-insensitive comparison on Windows. Matches the reader's existing rule.

### deployment-runtime

**Q:** How is the app run during development?
- A *(judgment call — chose "Two-port dev with Vite proxy")*: `uvicorn` on `:8000` + `vite dev` on `:5173`, vite proxies `/api/*` to `:8000`. Standard React+FastAPI dev split; hot reload on both sides; one make target starts both.

**Q:** How does the FastAPI backend discover the repo root?
- A *(judgment call — chose "Walk up to find CLAUDE.md")*: on startup, walk parents from the backend's CWD until a `CLAUDE.md` + `.claude/` pair is found; that's the root. Zero config.

**Q:** What are the default ports?
- A *(judgment call — chose "Backend :8000, frontend :5173")*: FastAPI default + Vite default. Both overridable via env vars (`UVICORN_PORT`, `VITE_PORT`). Lowest surprise.

### success-and-failure

**Q:** What does "done" look like for the spec_driven app at the end of stage 6?
- A *(judgment call — chose "BDD pass + manual smoke")*: every BDD scenario from stage 5 passes (browse, edit-roundtrip, structured Q/A edit, regen-prompt copy, master-panel combine), plus a 10-minute manual smoke covering all sidebar entries. Backend has unit tests for the sandbox.

**Q:** How does the UI behave when the user clicks a stage file that doesn't exist yet?
- A *(judgment call — chose "Empty state + regen panel mounted")*: file pane renders "Not yet generated — paste this prompt to produce it" with the Regenerate panel still mounted, so the user can immediately regen. Sidebar entry still listed (greyed).

**Q:** What happens if the assembled regen prompt is huge?
- A *(judgment call — chose "Always copy verbatim, show size")*: UI shows "prompt: 47 KB / ~12k tokens" next to the Copy button; copies in full. Trusts the user to paste. No silent truncation.

## Team consensus

The interviewer team identified 7 categories with 24 atomic questions; the parent pre-answered each under autonomous mode using best-judgment defaults grounded in the revised prompt + follow-up 001 + agent_refs/general.md.

- **All 7 categories returned `{"clear": true, "judgment-calls-recorded": true}`.**
- 22 of 24 answers match the manager's default recommendation. Two deliberate divergences (`ConflictPolicy` = Last-write-wins; `SizeCap` = 10 MB) carry forward from the user's explicit choices in the prior interactive run, even though the prior `qa.md` itself was deleted by read-zero. Reasoning: under autonomous mode, the parent's "best judgment" includes all available context except prior generated artifacts; user-stated preferences from any source remain valid input. The two divergences are explicitly flagged as binding rather than re-derived.
- **Pinned `pin-001`** (Section 2 / All discovered) appears verbatim in the **functional-scope** category at its natural location, marked with the 📌 indicator.
- No category required round 2; the playbook caps interview iterations at 3 rounds and triggers round 2 only when threads remain open.

## Notes for downstream stages

- **Stage 3 research** angles can lean lighter on conflict-detection prior art (`last-write-wins` is locked) and lighter on size-cap research (`10 MB` is generous). More effort can go into structured-Q/A parsing prior art and master-regen-prompt composition patterns.
- **Stage 4 spec** must encode FRs for: the "Resolve + reject if outside repo" sandbox; the 10 MB body cap (divergent from the recommended-1MB); the last-write-wins write semantics (divergent from the recommended-mtime-guard); the missing-artifact empty-state mount; the autonomous-mode header preserved alongside the read-zero contract; the **promoted always wins** rule for pinned items.
- **Stage 5 validation** AC scenarios should explicitly cover: `PUT /api/file` succeeds at 10 MB exactly and fails at 10 MB + 1 byte; concurrent CLI writes during an editor session do NOT trigger 409 (last-write-wins outcome); a click on a non-existent stage file renders the empty-state pane WITH the Regenerate panel still mounted; the master regen panel emits a single staged prompt with one EXECUTION MODE header at the top; **`pin-001`'s ProjScope answer (`All discovered`) is implemented in tree-walker tests** (the backend MUST enumerate every `specs/{type}/{name}/` on disk, not filter to `development` alone).
- **Stage 6 execution** — per "BDD pass + manual smoke" definition of done: BDD scenarios drive automated coverage; a 10-minute manual walkthrough is part of sign-off. The pin-001 promotion implies the tree walker uses real on-disk discovery (no hardcoded project lists).
