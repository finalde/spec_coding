# Follow-up draft 008 — 2026-05-03

Summary: Two coupled UI fixes against the current dogfood state.

(a) **Sidebar "Projects" section no longer mirrors `specs/`.** It currently wraps the entire `specs/` tree inside a literal `specs/` folder (so the user sees `Projects > specs > development > spec_driven > <stages>`) AND walks each `projects/{name}/` as a sibling under the same section (so `Projects > spec_driven` appears next to the `specs/` wrapper). FR-15 says the `Projects/{type}/{name}/` subtree shows per-stage subfolders — `{type}/{name}/` should be the *direct* children of "Projects", not nested behind the literal storage-folder name `specs`. Drop the wrapper; drop the parallel `projects/{name}/` walk (FR-15 does not include the project-code output in the sidebar).

(b) **No UI affordance to build a project-wide regen prompt.** `/project/:projectType/:projectName` (FR-32) is reachable only by typing the URL. The Home page lists nothing about discovered projects. Fix: Home derives `{type}/{name}` pairs from the just-loaded tree's "Projects" section and renders a "Build regen prompt" link to `/project/{type}/{name}` per project.

## (a) — sidebar restructure

### Root cause

`backend/libs/tree_walker.py::_projects_section` does:

```python
specs_dir = self._root / "specs"
if specs_dir.is_dir():
    specs_children = self._walk_filtered(specs_dir, self._is_allowed_leaf)
    children.append({
        "type": "directory", "name": "specs", "path": self._rel(specs_dir),
        "children": specs_children,
    })
for project_dir in self._exposed.project_dirs():
    project_children = self._walk_filtered(project_dir, self._is_allowed_leaf)
    children.append({...})
```

That produces:

```
Projects
├── specs/                          ← wrapper, NOT in spec
│   └── development/
│       └── spec_driven/
│           ├── user_input/, interview/, findings/, final_specs/, validation/
│           └── changelog.md
└── spec_driven/                    ← parallel projects/{name}/, NOT in FR-15
    ├── backend/, frontend/, …
```

FR-15 wants:

```
Projects
└── development/
    └── spec_driven/
        ├── user_input/, interview/, findings/, final_specs/, validation/
        └── changelog.md
```

### Fix

- Replace `_projects_section` body so its `children` are the direct children of `specs/` walked through `_walk_filtered` — i.e., elide the literal `specs/` directory node. The first level under "Projects" is the task-type; the second is the task-name; from there it's the regular per-stage walk.
- Remove the `for project_dir in self._exposed.project_dirs(): …` loop — `projects/{name}/` is the stage-6 output and is not in the sidebar contract. It remains accessible by the file-API path-sandbox (`is_inside` still admits `projects/...`); only the sidebar visibility goes away.
- Leave `ExposedTree.project_dirs()` and `project_stage_dirs()` defined as-is (no longer called, but trimming public methods is out of scope and risks unrelated regressions).

### What stays

- Path strings remain canonical filesystem-relative (`specs/development/spec_driven/final_specs/spec.md`, etc.). Only the *name* of the parent visual node changes — paths are unaffected, so `test_tree_walker.py::test_consumer_walk_finds_known_files`, `test_no_path_uses_backslash`, and the deep-link `/file/<encoded path>` (FR-17) all keep working.
- "Claude Settings & Shared Context" section is untouched.

## (b) — Home page lists discovered projects with a regen link

### Root cause

`/project/:projectType/:projectName` (FR-32) renders the master Regenerate panel (project-wide stages + modules + autonomous toggle + Build prompt). The route is wired in `App.tsx`. **Nothing links to it from inside the app.** The sidebar entries are file/folder treeitems that toggle on click; the Home view is a static blurb. The user has no way to reach the project page short of typing the URL.

### Fix

`frontend/src/components/Home.tsx`:

- Receive the same `tree` prop it already gets.
- Find the "Projects" top-level section in `tree.children`; its first-level children are task-types, the second-level are task-names. Yield `(type, name)` pairs from that walk. (Pure-frontend derivation — no new API.)
- Render each pair as a link: `<Link to={`/project/${type}/${name}`}>`. Label: `{type}/{name} — Build regen prompt for the whole project`.
- If zero projects are discovered, fall back to the existing "{count} top-level sections loaded" copy.

`react-router-dom` is already a dependency (App.tsx + ProjectPage.tsx import from it). No new dependency; no new API endpoint; no new persisted state.

### Why Home, not the sidebar entry

- Sidebar treeitems already have a single click action (toggle/open). Repurposing the project `{name}/` node to *navigate* would silently break the toggle UX and conflict with the existing keyboard-nav contract (FR-18: Enter on a directory toggles).
- Home is the default landing view and is empty real estate today; it's the natural place to put a project index.

## Out of scope

- E2E sidebar selectors (`[data-testid="sidebar"]`, `[data-section-toplevel]`, `[data-folder-name]`, `[data-leaf]`) — `Sidebar.tsx` does not currently emit any of these attributes. The dogfood spec was already targeting them; that mismatch predates this follow-up. Fixing it should be a separate follow-up scoped to "wire dogfood selectors."
- Restoring `projects/{name}/` to the sidebar in some other shape — FR-15 doesn't include it; if the user later wants it, do it as a separate follow-up.
- Touching `final_specs/spec.md` (FR-15 already describes the correct shape; the implementation drifted, the spec did not).
- New unit/system tests. The existing `test_tree_walker.py` already guards FR-3 (two top-level sections) and FR-15 (consumer-walk via `node.children`) at the structural level; the visible-name change ("Projects" → `{type}/{name}/...`) is a name-shape detail not covered by an existing assertion. A targeted assertion ("first-level child of `Projects` has `name` matching a `task_type` enum value, not the literal string `specs`") would belong in a future follow-up that strengthens the regression guard — not bundled here.
