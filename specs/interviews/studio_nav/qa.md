# Interview — studio_nav

**Initial prompt:** see `initial_prompt.md`.

**Rounds:** 1 (sufficient — moving to spec compile)

## Round 1

### Scope — module set

#### Q1: Which existing tabs survive as their own top-level module in the new left nav, alongside the new **Input** module?
- a) Keep **Adjustments** as its own module
- b) Keep **Execute & Validate** as its own module
- c) Fold Adjustments into **Input**
- d) Fold Execute & Validate's run controls into each phase's own module
- e) Drop Execute & Validate from the UI entirely (run via CLI only)
- **f) Other: _____  ← user picked**

**Notes:** "redo from scratch". The existing 6 tabs are dropped entirely. The new left-nav module set is exactly the five the user listed in the initial prompt: **Input · Interview Questions · Specs · Findings · Execution Plan**. No Adjustments tab, no Execute & Validate tab. Run controls and adjustment editing must be re-located inside one of the five modules (or dropped in v1 — see Open Questions).

#### Q2: What does the **Input** module include?
- a) `CLAUDE.md` + initial prompt only — read-only
- **b) `CLAUDE.md` + initial prompt + a per-task "system prompt" — all editable in place  ← user picked**
- c) (b) plus user adjustments + arbitrary reference docs the user uploads
- d) Other: _____

#### Q3: What does "system prompt" in the Input module concretely refer to?
- **a) The agent_team `SKILL.md` content (the orchestrator entry-point)  ← user picked**
- **b) The current phase's manager agent file (e.g. `agent_team__interview_manager.md` while interviewing)  ← user picked**
- c) A new per-task editable `system_prompt.md` the user authors
- d) All three — separate sub-sections inside the Input module
- e) Other: _____

**Notes:** Combining Q2 + Q3: the **Input** module surfaces FOUR things — `CLAUDE.md`, `SKILL.md`, the current phase's manager `.md`, and the task's `initial_prompt.md`. All four editable in place. Edits to the first three write back to the repo files (since those are the actual files Claude reads at runtime); edits to the initial prompt write to `specs/interviews/{task_id}/initial_prompt.md`. Saving repo-level files should require a confirm step because the change affects every task. *(Confirm vs no-confirm is an open question.)*

### Scope — editing semantics

#### Q4: When the user edits the Interview Q&A in the right pane and saves, what happens?
- **a) Persist only — user manually re-runs the spec phase if they want downstream regenerated  ← user picked**
- b) Auto-trigger spec recompilation on save (eager)
- c) Persist + flag downstream artifacts as **stale** (warning badge), user clicks to re-run
- d) Other: _____

**Notes:** Edits across all editable artifacts (qa, spec, adjustments-equivalents, plan, the four Input sources) follow the same rule — persist only, no implicit downstream effects.

### Origin / runtime

#### Q5: Where does the `spec_studio` task entry on the left nav come from?
- a) Synthesize at runtime — backend exposes a virtual entry; nothing in `specs/index.json`
- b) Persist a real entry in `specs/index.json` for `spec_studio`, treating it like a normal task
- c) Don't show `spec_studio` in the task list at all — manage it manually
- **d) Other: _____  ← user picked**

**Notes:** "left nav just show those high level modules, not adhoc tasks." The left nav inside `/tasks/:id` is **only the five module entries** — no task tree. Tasks are listed on the existing Dashboard (`/`); clicking a task takes you to `/tasks/:id` and the left nav there is just modules. The question of whether `spec_studio` itself is persisted as a task entry in `index.json` is no longer load-bearing for the nav design (it can be either; we'll persist for consistency with future tasks).

### Tech constraints

#### Q6: How much backend change is acceptable?
- a) Frontend-only — read `CLAUDE.md` / SKILL.md via existing artifact endpoint; no new routes
- b) Frontend + minimal backend — 2–3 new GET endpoints (e.g. `/api/inputs/{task_id}`) to consolidate Input content
- **c) Frontend + significant backend — model `Input` as a first-class artifact, persist edits with versioning, add PUT endpoints for editable artifacts (qa, spec, adjustments)  ← user picked**
- d) Other: _____

**Notes:** "just redo everything". OK to redesign the API surface: PUT endpoints for all editable artifacts (qa, spec, plan, the four Input sources), an `/api/inputs/{task_id}` aggregator that returns the four Input sources together, and an `ArtifactKind` enum extension to cover the new editable kinds. Versioning was suggested but not committed — defer to spec compile (see Open Questions).

#### Q7: Left-nav visual style?
- **a) Always-expanded tree (every task always shows its modules indented underneath)  ← user picked**
- b) Collapsible accordion (click task to expand/collapse its modules)
- c) Two-column nav: tasks list on far left, modules of the selected task in a second column
- d) Other: _____

**Notes:** With Q5=d (no task tree in nav), Q7=a simplifies to: **a flat, always-visible vertical list of the five module names** — Input, Interview Questions, Specs, Findings, Execution Plan. Selected module gets visual emphasis. No nesting.

#### Q8: URL routing for deep links?
- a) `/tasks/:taskId/:module` — module is a route segment, deep-linkable, browser back/forward works
- b) `/tasks/:taskId` only — module is component state, not in URL
- c) `/tasks/:taskId?module=interview` — module as query param
- **d) Other: _____  ← user picked  → "you can decide" → defaulting to (a)**

**Notes:** Going with `/tasks/:taskId/:module` (option a) — best for shareable links, browser back/forward, and tab-restore on reload.

### Bonus directive

User added: "you can download some front design plugin and use it to guide your front end desgin."

**Notes:** I'll evaluate component libraries during research (Phase 3). Top candidates: **Mantine v8** (best for admin/dashboard UIs out of the box), **Ant Design v5** (most polished admin look), **shadcn/ui** (current direction — most flexible, requires more design work). The chosen library will dictate AppShell/Sider, NavLink, code-highlight, markdown editor, and YAML viewer choices. Final pick: research will recommend, user can override at adjustments phase.

## Open Questions (carry forward to spec / plan)

- **Editing repo-level files from the UI** — confirm dialog required when saving `CLAUDE.md`, `SKILL.md`, or a manager agent file from Spec Studio? (Likely yes — those affect every task.) Or do we restrict those to read-only and only allow editing `initial_prompt.md` of the current task?
- **Run controls / event log** — with Execute & Validate dropped, where do the existing "Run interview round" / "Run spec compile" / "Run plan compile" / "Run execute" buttons go? Three options: (1) inline at the top of each module's right pane; (2) a floating action button or top-bar menu; (3) drop UI run controls entirely in v1 and rely on `/agent_team` from Claude Code.
- **Versioning for edited artifacts** — Q6=c mentioned "persist edits with versioning". Concretely: save N most-recent versions per artifact, full history with timestamps in a sidebar, or no versioning (last-write-wins)? v1 default proposal: last-write-wins + a single `.bak` of the prior version.
- **"Beautified" interview Q&A** — render style: collapsible question cards with selected option highlighted, side-by-side options, alternating row backgrounds? Pin to a specific style only after the design library is chosen.
- **Front-end design library choice** — locked during research / spec compile, surfaced as a single recommendation with rationale.
