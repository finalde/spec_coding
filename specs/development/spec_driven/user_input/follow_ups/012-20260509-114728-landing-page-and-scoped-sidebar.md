# Follow-up draft 012 — 2026-05-09

Summary: Add a landing-page project picker to the spec_driven webapp, and scope the sidebar to the picked project.

## Original wording

> in the spec_driven project lets add a landing page, in the landing you get a list of projects first, like devleopment porjects like spec driven or ai video management, or ai_video projects. And once user click one project, he gets redirect to the main page which as the left nav and main view, the left nav will just show this particular project related files + the common files such as claude settings

## Desired behavior

1. **Landing page (`/`).** When the webapp opens at `/`, the user sees ONLY a project picker — no left sidebar, no other chrome. The picker lists every `{task_type}/{task_name}` discovered under `specs/` (e.g. `development/spec_driven`, `development/ai_video_management`, `ai_video/<name>`, …). Each row is a clickable link.
2. **Click → scoped main view.** Clicking a project navigates the user into the existing main layout (left nav + main pane) at `/project/{type}/{name}` (the master Regenerate page introduced by FR-32; that page is the natural project-level entry point and already exists). The chosen project becomes the **active project**.
3. **Sidebar scoped to active project.** Anywhere the sidebar is rendered (i.e. any non-landing route), the **Specs** top-level section MUST be filtered to ONLY the active `{type}/{name}` subtree. The other top-level section, **Claude Settings & Shared Context**, stays unchanged — those files are common to all spec-driven projects.
4. **"Back to projects" link.** The sidebar gets a small "← Back to projects" affordance at the top that returns the user to `/` and clears the active project. (Not a tree node — a sidebar header row, so it doesn't conflict with the keyboard-nav contract on tree items.)

## State surface

`activeProject` is a string of the form `"{type}/{name}"` persisted in `localStorage` under the key `spec_driven.active_project.v1`. It is:

- **Set** when the user clicks a project on the landing page.
- **Set/refreshed** when the user navigates to any URL that carries `{type}/{name}` (the `/project/:projectType/:projectName`, `/stage/:projectType/:projectName/:stage`, and `/file/specs/{type}/{name}/...` routes). This guarantees deep-link / bookmarked URLs continue to "just work" — the URL is the source of truth, the localStorage entry is a recovery cache for routes (`/file/CLAUDE.md`, `/file/.claude/...`) that do not name a project.
- **Cleared** by the "Back to projects" link.

If `activeProject` is unset AND the current URL has no project context (e.g. someone deep-links to `/file/CLAUDE.md` with a fresh browser), the sidebar still renders, but the Specs section is empty (still shows Claude Settings & Shared Context). The user can hit "Back to projects" to pick one.

## Why `/project/{type}/{name}` as the click target

That route already exists (FR-32) and renders the master Regenerate panel — a useful project-level home. Adding a separate "project home view" with no purpose beyond a welcome screen would be needless surface; the existing page is exactly what a user lands on next. If we later decide a project home should show something else (project README, last-edited file, etc.), that's a future follow-up.

## Concrete deltas

### Spec — `final_specs/spec.md`

- **FR-15 amend.** Append: "When an active project is set (see FR-42), the Specs section is filtered to that single `{type}/{name}` subtree only — every other project under `specs/` is hidden from the sidebar. The Claude Settings & Shared Context section is unchanged in either mode."
- **New FR-42 — Landing project picker.** Route `/` renders a project picker WITHOUT the sidebar (full-width main pane). Picker lists every `{type, name}` pair discovered from the tree's "Specs" section's first two levels. Clicking a row sets `activeProject = "{type}/{name}"` (in `localStorage`, key `spec_driven.active_project.v1`) and navigates to `/project/{type}/{name}`. The sidebar's "Back to projects" link clears `activeProject` and navigates to `/`. Active-project state is also re-derived from the URL whenever a project-scoped route is loaded directly (deep-link / bookmark resilience).
- **FR-15 / Home overlap cleanup.** The previous Home (`/`) auto-rendered both the picker AND the sidebar. The picker is now the *only* thing on `/`; the sidebar mounts on every non-landing route. The "Build regen prompt for the whole project" copy on the picker rows is dropped — the click target is now the project page itself, no longer a separate "build prompt" link.

No new ACs are added in this surgical patch. The existing AC-3 (recursive `children` shape from `/api/tree`) and AC-26 (sidebar structural sanity) still hold; the filtering happens client-side and does not change the wire shape.

### Frontend — `projects/spec_driven/frontend/src/`

- **New module `lib/activeProject.ts`.** Wraps `TypedLocalStorage<string | null>` with the key `spec_driven.active_project.v1`; exports `read()`, `write(value: string | null)`, `clear()`, and `parse(raw: string | null) -> {type, name} | null`. Fallback is `null`.
- **`App.tsx`.** Reads activeProject from localStorage on mount; tracks it in state. On every route change, syncs from URL params (`/project/:type/:name`, `/stage/:type/:name/:stage`, `/file/specs/{type}/{name}/...`). Layout split: at `/`, render `<ProjectPicker tree={tree} onPick={(p) => { setActive(p); navigate(`/project/${p.type}/${p.name}`); }}/>` inside `<main className="picker-pane">` — no `<Sidebar>`, no `.app-root` two-column grid. On any non-landing route, render `.app-root` two-column grid as before, but pass `activeProject` to `<Sidebar>` so it filters the tree.
- **`components/Sidebar.tsx`.** Receives `activeProject: {type, name} | null` prop. Before walking, derives a `filteredTree` whose Specs section's children are pruned to only the active project's `{type}` node containing only the active project's `{name}` node (with the rest of that subtree intact). When `activeProject` is null, the Specs section's children are an empty list. Adds a header row above the tree: a `<button>` "← Back to projects" that calls `onBackToProjects()` (passed from App.tsx) — clears activeProject, navigates to `/`. The button is NOT a treeitem; it lives outside `[role="tree"]` so the keyboard-nav contract on the tree is preserved.
- **`components/Home.tsx` → repurposed as `components/ProjectPicker.tsx`.** Renames the file (or keeps the file and renames the export — a one-line change in `App.tsx`'s import). Renders a clean centered list of projects (no "Build regen prompt" sub-text, no "{N} top-level sections loaded" fallback — the picker is now a primary surface, not a secondary one).
- **`styles.css`.** New `.picker-pane` rule for the landing layout (full-width container, centered content, no grid). New `.sidebar-back` rule for the "Back to projects" button (sits above `.tree`, same light theme as the rest of the sidebar). Existing `.app-root` `grid-template-columns: 280px 1fr` rule is unchanged for non-landing routes.

### Backend

No changes. The filtering is purely client-side; the wire shape from `/api/tree` is unchanged. Note: the backend tree-walker still walks every project — that's correct, because the Claude Settings section is shared across projects and the picker page also needs the full list.

## Out of scope

- A separate "project home" view distinct from `/project/{type}/{name}` — current design reuses the existing master Regenerate page as the entry point. If a user wants a different welcome screen, that's a future follow-up.
- Filtering the **Claude Settings & Shared Context** section by project — those files (`CLAUDE.md`, `.claude/agent_refs/**/*.md`, `.claude/skills/**/SKILL.md`) are intentionally cross-project and stay visible regardless of the active project.
- Any change to the path-sandbox in the file API — `/api/file?path=...` continues to admit any path under `EXPOSED_TREE`. Sidebar visibility is a UX concern, not a security boundary.
- Server-side persistence of `activeProject` — per-tab `localStorage` is sufficient (mirrors the autonomous-mode toggle precedent set by FR-34).
- New e2e or unit tests — the existing `test_tree_walker.py` consumer-walk test still passes (wire shape unchanged); a Playwright scenario for the picker → scoped-sidebar flow would be a useful future addition but is not bundled here to keep this surgical.
- Renaming the `/project/{type}/{name}` route to something more "home-like" — keep stable URLs.
