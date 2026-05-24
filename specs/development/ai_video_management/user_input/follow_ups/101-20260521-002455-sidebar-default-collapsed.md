# Follow-up draft 101 — 2026-05-21

Left-nav (sidebar) tree should default to **everything collapsed** on
initial load.

## Intent

Today the `Sidebar` walks the tree on first load and pre-expands every
directory / section node (`expanded[path] = true`). With hundreds of
characters / actors / episodes under `ai_videos/`, this drowns the user in
a fully-spread tree before they pick a target.

The user wants the opposite default: on first load every collapsible node
is closed. They expand only what they click on.

## Behaviour

1. On initial tree load, every collapsible node defaults to **closed**.
   Top-level sections (`depth === 0` — currently only the "AI Videos"
   root) keep their existing always-open render contract (line 133
   `const isOpen = depth === 0 ? true : expanded[node.path] === true;`),
   because they have no visual collapse affordance.
2. The currentPath auto-expand effect (currently lines 98-108) is
   **preserved** — when the user deep-links to `/file/<path>`, every
   ancestor folder of that path is expanded so the tree leads the eye to
   the highlighted leaf.
3. The user's manual toggles (the existing `toggle()` setter) persist for
   the lifetime of the session; subsequent tree refreshes (`onTreeReload`
   from create/delete/rename) MUST NOT clobber the user's expansion
   state. The current `{ ...accum, ...prev }` merge already does this —
   keep that ordering when flipping defaults.
4. `onCollapseAll` (the ⊟ button) remains a useful no-op-equivalent on
   first load but stays meaningful after the user has expanded things.

## Out of scope

- No new persistence layer (no `localStorage` for expansion state) — the
  default-collapsed behaviour applies fresh on every page load.
- No change to the always-open top-level section render.
- No change to `Reader` / `Breadcrumb` / any other component.
