# Follow-up draft 100 — 2026-05-20

Make the Reader breadcrumb segments clickable so the user can jump to an
ancestor in the path.

## Intent

The breadcrumb at the top of the Reader (e.g. `ai_videos / _actors /
actor_0187 / actor_0187.md`) currently renders each segment as plain text.
Each non-last segment must become an in-app navigation control that brings
the user "up one level" toward the indicated ancestor.

## Behaviour

1. The last segment (the file currently being viewed) stays non-interactive
   and keeps the `breadcrumb-current` styling.
2. Every preceding segment is rendered as an accessible button / link
   (anchor-like styling, keyboard-focusable, `aria-label` describing the
   target).
3. Activation of a segment navigates as follows:
   - If a self-named markdown index file exists at
     `<accumulated-prefix>/<segment>.md` inside `knownPaths`, navigate to
     that file (`/file/<encoded>`). This covers conventional folders such
     as `actor_<id>/actor_<id>.md` and `c<n>_<slug>/c<n>_<slug>.md`.
   - Otherwise navigate to the accumulated prefix itself
     (`/file/<accumulated-prefix>`). The existing `currentPath` effect in
     `Sidebar` will expand the tree to that ancestor even if the Reader has
     no canonical rendering for the folder.
4. The separator (` / `) stays visually identical and remains
   non-interactive.
5. Styling: clickable segments use the existing `--text-muted` colour with
   an underline / accent hover state; no layout shift versus the current
   plain-text version.

## Out of scope

- No new backend route for folder browsing — this is a pure UI change.
- No change to the `/file/<path>` route contract. Clicking a folder
  segment without a self-named markdown index will load that path through
  the existing Reader code path (which simply shows whichever error /
  empty state already exists for non-file paths).
- No change to the Home (`/`) or sidebar tree behaviour beyond what
  already follows from `currentPath` updates.
