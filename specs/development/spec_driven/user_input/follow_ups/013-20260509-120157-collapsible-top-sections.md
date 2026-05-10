# Follow-up draft 013 — 2026-05-09

Summary: Make the sidebar's top-level sections (specifically **Claude Settings & Shared Context**, but for symmetry also **Specs**) collapsible.

## Original wording

> claude settings and shared context should be collapsable on the left nav

## Current behavior

`Sidebar.tsx::flat` hardcodes `const isOpen = depth === 0 ? true : expanded[node.path] === true;` — top-level sections are always rendered open and have no working disclosure toggle. The user wants to fold the **Claude Settings & Shared Context** section away when they're focused on the active project's pipeline files.

## Desired behavior

- Both top-level sections render with a working disclosure caret (▾/▸) and respond to clicks + Enter/Space toggling.
- Default state on first load: **expanded** (no behavior regression for users who never click the caret).
- Toggle state is held in component-local React state (the existing `expanded: Record<string, boolean>`); no `localStorage` persistence in v1 — collapse is a per-tab convenience, not a setting.
- Keyboard contract (FR-18) preserved: ArrowRight expands a collapsed section, ArrowLeft collapses an expanded section, Enter/Space toggles.

## Implementation note — empty-path sections

`tree_walker.py` emits both top-level sections with `path: ""`, so the existing `expanded[node.path]` keying would collide on the empty string and the existing `data-path=""` would make `focusByPath` ambiguous (querySelector returns only the first). Surgical fix: introduce a `nodeKey(node)` helper that returns `node.path || \`section:${node.name}\`` and use it everywhere the sidebar keys expansion or DOM-targets a node (`data-path`, `expanded` map, `toggle()` arg, `focusByPath` arg). Real file/dir paths still resolve to `node.path` exactly as before — the helper is a no-op for non-empty paths, so deep-link auto-expansion (`useEffect` walking `currentPath` segments) is unaffected.

The pre-seed `useEffect` that default-expands every interior node on tree (re)load also walks sections (their `nodeKey` becomes `section:Claude Settings & Shared Context` and `section:Specs`), seeding them as `true`. Toggling a section flips its key to `false`; toggling again removes the override and the next load re-seeds back to `true`. Behavior is consistent.

## Concrete deltas

### Spec — `final_specs/spec.md`

- **FR-15 amend.** Append: "Both top-level sections (**Claude Settings & Shared Context** and **Specs**) are collapsible — clicking the disclosure caret or pressing Enter/Space on the section row toggles its open/closed state. Default on first render: expanded. Collapse state is component-local React state (no `localStorage` persistence in v1)."

### Frontend — `projects/spec_driven/frontend/src/components/Sidebar.tsx`

- New `nodeKey(node: TreeNode): string` helper returning `node.path || \`section:${node.name}\``.
- `flat` walker drops the `depth === 0 ? true : …` special case and uses `expanded[nodeKey(node)] === true` uniformly.
- Pre-seed `useEffect` walks sections too (it already returns early for files; the existing `if (node.path)` early-out is replaced with the unified `nodeKey()` so empty-path sections get keys).
- `data-path={nodeKey(item.node)}` on the treeitem (was `item.node.path`).
- `toggle(nodeKey(item.node))` in the click and keyboard handlers (was `item.node.path`).
- `focusByPath` continues to take a string; callers pass `nodeKey(node)` instead of `node.path`. The selector still works because `data-path` mirrors the same key.
- `currentPath === item.node.path` (active-state highlight) is unchanged — sections never match a file URL, so they never light up active.

No CSS changes needed — the existing `.tree-item.tree-branch` + `.tree-disclosure` rules already render the section row with a working caret; the rule only didn't fire because of the hardcoded `isOpen=true`.

### No backend changes

`tree_walker.py` continues to emit `path: ""` on top-level sections — making it emit unique synthetic paths would be a larger schema change and isn't needed: the frontend keying handles the collision locally.

### No new tests

`test/Sidebar.test.tsx` (3 cases) renders the sidebar without inspecting the open/closed state of top-level sections; assertions on leaf-name visibility continue to pass since the default state is expanded.

## Out of scope

- `localStorage` persistence of collapse state — defer; a per-tab convenience suffices for v1.
- A "collapse all" / "expand all" affordance — not requested.
- Animating the collapse — not requested; hard cut is consistent with the existing per-directory toggle.
- Renaming the sections — kept as "Claude Settings & Shared Context" and "Specs".
