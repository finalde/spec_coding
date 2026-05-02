# Validation — Accessibility

Run: spec_driven-20260502-clean
Stage: 5
Source spec: `specs/development/spec_driven/final_specs/spec.md`
Inputs read: spec.md only (read-zero)

## Posture

The spec mandates WCAG 2.1 Level AA (NFR-10) and the W3C ARIA APG TreeView pattern (NFR-9, FR-18, FR-19). Browser support is locked to latest stable Chromium (NFR-14), so axe-core, Lighthouse, and the Chrome DevTools Accessibility tab are the primary tools. Manual NVDA + Chrome on Windows covers screen-reader announcement checks; manual keyboard-only walkthroughs cover focus management.

Each check is tagged either **[Spec-mandated]** (derived from a specific FR/NFR — failure blocks release) or **[Recommended]** (best-practice extrapolation — failure files an issue but does not block).

Tooling shorthand:
- `axe`: axe-core via `@axe-core/cli` or the axe DevTools browser extension, ruleset WCAG 2.1 AA.
- `lh`: Lighthouse Accessibility audit (DevTools → Lighthouse → Accessibility category only).
- `nvda`: NVDA screen reader (latest) on Windows + Chrome.
- `cca`: Colour Contrast Analyser (TPGi).
- `kb`: Manual keyboard-only walkthrough (Tab / Shift+Tab / arrow keys / Enter / Space / Escape / Home / End).

## Checks

### A11Y-01 — Tree container roles [Spec-mandated]

- **Tooling.** axe + DOM inspection.
- **Method.** Open `/`. In DevTools Elements tab, select the sidebar tree root. Verify `role="tree"` and `aria-multiselectable="false"`. Run axe with selector scoped to the sidebar.
- **Pass criterion.** Sidebar root has `role="tree"`, `aria-multiselectable="false"`, and exactly one accessible name (via `aria-label` or `aria-labelledby`). axe reports zero violations under this subtree.
- **WCAG 2.1 SC.** 1.3.1 Info and Relationships, 4.1.2 Name, Role, Value.
- **Spec refs.** FR-18.

### A11Y-02 — Treeitem attributes including `aria-level` [Spec-mandated]

- **Tooling.** DOM inspection + axe.
- **Method.** Iterate every node under the tree:
  ```
  $$('[role="treeitem"]').forEach(n => console.log(
    n.getAttribute('aria-level'),
    n.getAttribute('aria-expanded'),
    n.getAttribute('aria-selected'),
    n.tabIndex
  ));
  ```
  Verify each treeitem has `aria-level` set to its depth (root level = 1). Folders carry `aria-expanded="true|false"`. Leaves omit `aria-expanded` (or set it absent — never `aria-expanded="false"` on a leaf).
- **Pass criterion.** Every `[role="treeitem"]` has a numeric `aria-level`. Folders carry `aria-expanded`; leaves do not. axe reports zero violations.
- **WCAG 2.1 SC.** 1.3.1, 4.1.2.
- **Spec refs.** FR-18.

### A11Y-03 — `aria-selected` matches URL [Spec-mandated]

- **Tooling.** DOM inspection + manual navigation.
- **Method.** Navigate to several files (via sidebar click, via direct URL change, via in-app link). After each navigation, query `$$('[role="treeitem"][aria-selected="true"]')` — exactly one match should appear, and its data-path should equal the URL's `/file/<rel-path>` value.
- **Pass criterion.** Across at least 5 navigations (sidebar click, direct URL, in-app cross-link, browser back, browser forward), `aria-selected="true"` is set on exactly one treeitem and that treeitem's path matches the URL.
- **WCAG 2.1 SC.** 1.3.1, 4.1.2.
- **Spec refs.** FR-18, FR-38.

### A11Y-04 — Full APG TreeView keyboard map including Home/End [Spec-mandated]

- **Tooling.** `kb` only.
- **Method.** Tab to the tree. Then exercise every key per FR-19:
  - Up / Down → previous/next visible node.
  - Right on collapsed folder → expands.
  - Right on expanded folder → moves to first child.
  - Right on leaf → no-op.
  - Left on expanded folder → collapses.
  - Left on collapsed folder or leaf → moves to parent.
  - Enter on leaf → navigates (URL changes).
  - Enter on folder → no-op.
  - Home → first visible node.
  - End → last visible node.
  Document each result.
- **Pass criterion.** Every key behaves as specified. Zero observed deviations.
- **WCAG 2.1 SC.** 2.1.1 Keyboard, 2.1.2 No Keyboard Trap.
- **Spec refs.** FR-19, NFR-9, AC-14.

### A11Y-05 — Missing-state items skipped by arrow nav [Spec-mandated]

- **Tooling.** `kb`.
- **Method.** Find a project where one stage is missing on disk (e.g., temporarily rename `validation/` so `present: false`). Reload sidebar. Tab into tree, navigate to the project, expand it. Press Down repeatedly. Confirm the muted-italic missing-stage row is **never** focused.
- **Pass criterion.** Down-arrow traversal of a project with one missing stage skips the missing-state leaf. Pressing Enter on adjacent siblings still works.
- **WCAG 2.1 SC.** 2.1.1, 2.4.3 Focus Order.
- **Spec refs.** FR-9, FR-24.

### A11Y-06 — Focus + selection visuals simultaneously visible [Spec-mandated]

- **Tooling.** `kb` + screenshot.
- **Method.** Select a leaf via click (selection), then arrow Down to a different leaf (focus moves but selection stays). Screenshot. Verify both visuals are present: filled background bar on the selected row, separate ring outline on the focused row.
- **Pass criterion.** In the screenshot, the selected row and the focused row are visually distinct AND both visible at the same time. The focus ring is not occluded by the selection bar.
- **WCAG 2.1 SC.** 2.4.7 Focus Visible.
- **Spec refs.** FR-20.

### A11Y-07 — WCAG 2.1 AA contrast on every interactive state [Spec-mandated]

- **Tooling.** `cca` + axe.
- **Method.** For each of: default text, hover, focus ring, selected background, dirty-dot color, broken-link muted color, "Saved." aria-live text, regen-prompt warning banner — sample foreground/background pixels with cca. Run axe full-page on `/file/specs/development/spec_driven/final_specs/spec.md`.
- **Pass criterion.** Every measured pair meets 4.5:1 (normal text) or 3:1 (UI component, large text). axe `color-contrast` rule reports zero violations.
- **WCAG 2.1 SC.** 1.4.3 Contrast (Minimum), 1.4.11 Non-text Contrast.
- **Spec refs.** NFR-10.

### A11Y-08 — Heading semantics observational [Spec-mandated]

- **Tooling.** axe + manual outline check (`document.querySelectorAll('h1,h2,h3,h4,h5,h6')`).
- **Method.** Render `final_specs/spec.md`. Inspect rendered headings. Verify levels descend without skipping (no h1 → h3 jump unless the source markdown does it). Run axe `heading-order` rule.
- **Pass criterion.** axe reports zero `heading-order` or `empty-heading` violations on any rendered markdown file in the dogfood project. Skipped levels in the source markdown surface as warnings only.
- **WCAG 2.1 SC.** 1.3.1, 2.4.6 Headings and Labels.
- **Spec refs.** FR-30, NFR-11.

### A11Y-09 — Long-name truncation: accessible name = full text via `title` [Spec-mandated]

- **Tooling.** DOM inspection + `nvda`.
- **Method.** Create a fixture file `specs/development/spec_driven/user_input/aaaaaaaaaaaaaaaaaaaaaaaaa-very-long-filename-that-overflows.md`. Reload sidebar. Inspect the row: confirm CSS truncates visually (ellipsis), and the row's `title` attribute (or `aria-label` if `title` collides with tooltip semantics) equals the full filename. With NVDA running, focus the row and confirm NVDA announces the full filename, not the truncated visible text.
- **Pass criterion.** Visible text shows ellipsis. `title` (or `aria-label`) equals full filename. NVDA announces full filename.
- **WCAG 2.1 SC.** 1.3.1, 2.4.6, 4.1.2.
- **Spec refs.** FR-25.

### A11Y-10 — Folder-click toggle-only semantics [Spec-mandated]

- **Tooling.** `kb` + `nvda`.
- **Method.** Click a folder row in the sidebar. Verify URL does NOT change (FR-26). Verify `aria-expanded` flips. Press Right then Left on a folder via keyboard — confirm the same toggle behavior, no URL change.
- **Pass criterion.** Folder click never produces a navigation. `aria-expanded` reflects state. NVDA announces "expanded" / "collapsed" on toggle.
- **WCAG 2.1 SC.** 4.1.2.
- **Spec refs.** FR-26.

### A11Y-11 — Breadcrumb landmark + nav element with `aria-current="page"` [Spec-mandated]

- **Tooling.** DOM inspection + `nvda`.
- **Method.** Inspect the breadcrumb on `/file/specs/development/spec_driven/final_specs/spec.md`. Verify `<nav aria-label="Breadcrumb">` wraps an ordered list, each segment except the last is an `<a>`, and the last segment is plain text with `aria-current="page"`. NVDA in browse mode lists Breadcrumb as a navigable landmark.
- **Pass criterion.** All structural assertions hold. NVDA's landmark list (`D` quick-nav) includes "Breadcrumb".
- **WCAG 2.1 SC.** 1.3.1, 2.4.8 Location.
- **Spec refs.** FR-29.

### A11Y-12 — Broken-link span as `<span>` not `<a>` with `aria-disabled="true"` [Spec-mandated]

- **Tooling.** DOM inspection + axe.
- **Method.** Render a markdown file containing `[ghost](./does-not-exist.md)`. Inspect the rendered node: must be a `<span class="link-broken" aria-disabled="true">` with `title` set to the cause string. Confirm Tab does NOT focus it (it has no `tabindex` and is not an interactive element).
- **Pass criterion.** Rendered element is `<span>`, not `<a>`. Has `aria-disabled="true"`. Has a non-empty `title`. Is not in the tab order.
- **WCAG 2.1 SC.** 1.3.1, 4.1.2.
- **Spec refs.** FR-34.

### A11Y-13 — External-link new-tab announcement via sr-only span [Spec-mandated]

- **Tooling.** DOM inspection + `nvda`.
- **Method.** Render a markdown file containing `[Example](https://example.com)`. Inspect the rendered anchor: must be `<a target="_blank" rel="noopener noreferrer">` followed by `<span class="sr-only">(opens in new tab)</span>`. With NVDA, navigate to the link — NVDA reads "Example, link, opens in new tab".
- **Pass criterion.** sr-only span present, visually hidden via `clip` / `clip-path` CSS, NVDA reads the announcement. Link target opens in a new tab on click.
- **WCAG 2.1 SC.** 2.4.4 Link Purpose, 3.2.5 Change on Request.
- **Spec refs.** FR-33 case 1.

### A11Y-14 — Refresh button is a real `<button>` keyboard-activatable [Spec-mandated]

- **Tooling.** DOM inspection + `kb`.
- **Method.** Inspect the sidebar Refresh button: must be `<button>` (not `<div role="button">`). Tab to it. Press Space and Enter — both must trigger a `/api/tree` re-fetch (verify in Network tab).
- **Pass criterion.** Element is a `<button>`. Both Space and Enter trigger the fetch. Receives a visible focus ring.
- **WCAG 2.1 SC.** 2.1.1, 2.4.7, 4.1.2.
- **Spec refs.** FR-28.

### A11Y-15 — Reduced-motion preference [Spec-mandated]

- **Tooling.** DOM + DevTools rendering panel.
- **Method.** In DevTools → Rendering, enable "Emulate CSS media feature `prefers-reduced-motion: reduce`". Expand and collapse a sidebar folder. Confirm the height transition is gone (instant snap, no animation). Inspect the computed style of the transitioning element — `transition` should resolve to `none`.
- **Pass criterion.** With reduced-motion emulation on, expand/collapse is instant. Computed `transition` is `none`. Without emulation, the 100–150 ms ease is observable.
- **WCAG 2.1 SC.** 2.3.3 Animation from Interactions.
- **Spec refs.** FR-39.

### A11Y-16 — Image placeholder accessible name = alt text [Spec-mandated]

- **Tooling.** DOM inspection + `nvda`.
- **Method.** Render a markdown file containing `![diagram of the pipeline](./pipeline.png)`. Inspect the rendered placeholder: must be `<span class="image-placeholder">` containing the alt text "diagram of the pipeline" with `title="v1: images not rendered"`. NVDA reads the alt text in browse mode.
- **Pass criterion.** Visible text equals alt. `title` equals "v1: images not rendered". NVDA reads the alt text and the tooltip.
- **WCAG 2.1 SC.** 1.1.1 Non-text Content.
- **Spec refs.** FR-36.

### A11Y-17 — Code-block AT compatibility — `<pre tabindex="0">` keyboard scrollable [Spec-mandated]

- **Tooling.** DOM inspection + `kb`.
- **Method.** Render a markdown file with a long fenced code block (50+ lines, line length >120). Tab into the page. Confirm the `<pre>` receives focus (visible ring), then arrow keys scroll its overflow.
- **Pass criterion.** Every rendered `<pre>` has `tabindex="0"`. Tab focuses it; arrow keys scroll. Focus ring visible.
- **WCAG 2.1 SC.** 2.1.1, 2.4.7.
- **Spec refs.** FR-31.

### A11Y-18 — Markdown link semantics — internal `<a>` with `href`, broken `<span>` without `href` [Spec-mandated]

- **Tooling.** DOM inspection + axe.
- **Method.** Render `final_specs/spec.md`. Query `document.querySelectorAll('.link-broken')` — confirm none have `href` and none are anchor elements. Query `document.querySelectorAll('a[href^="/file/"]')` — confirm each has a non-empty `href` and is keyboard focusable.
- **Pass criterion.** Zero `<a class="link-broken">` (broken links never render as anchors). Zero `<span href=...>` (spans never carry href). Internal links are real anchors.
- **WCAG 2.1 SC.** 4.1.2.
- **Spec refs.** FR-33, FR-34.

### A11Y-19 — Editor textarea has `aria-label="Edit {filePath}"` and dirty state announced via aria-live [Spec-mandated]

- **Tooling.** DOM inspection + `nvda`.
- **Method.** Open `/file/specs/development/spec_driven/final_specs/spec.md`. Click ✎ Edit. Inspect the textarea: must have `aria-label` set to e.g. "Edit specs/development/spec_driven/final_specs/spec.md". Type a character. Inspect for an `aria-live="polite"` (or `role="status"`) region that announces the dirty state. With NVDA, type a character — confirm "Unsaved changes" is announced.
- **Pass criterion.** textarea has descriptive `aria-label`. Dirty state is in an aria-live region. NVDA announces "Unsaved changes" on first edit and "Saved." after Ctrl+S succeeds (FR-40 explicitly mandates the "Saved." aria-live announcement).
- **WCAG 2.1 SC.** 1.3.1, 4.1.2, 4.1.3 Status Messages.
- **Spec refs.** FR-40.

### A11Y-20 — Editor error banner has `role="alert"` and is keyboard-reachable [Spec-mandated]

- **Tooling.** `nvda` + `kb` + DOM inspection.
- **Method.** Trigger a save failure (e.g., temporarily make the target file > 2 MB by pasting 2 MB of content, or rename the extension to `.txt` server-side mid-edit to force 415). Press Ctrl+S. Inspect the inline error banner: must have `role="alert"` (NVDA interrupts and reads the banner text immediately), and must be reachable by Tab (focusable container or focusable Close button if the banner has one).
- **Pass criterion.** Banner has `role="alert"`. NVDA announces it without user navigation. Tab focus order includes the banner (or its close affordance) before returning to the textarea.
- **WCAG 2.1 SC.** 4.1.3, 3.3.1 Error Identification.
- **Spec refs.** FR-40 (e).

### A11Y-21 — Single tab stop with roving tabindex on tree [Spec-mandated]

- **Tooling.** `kb` + DOM inspection.
- **Method.** From a fresh page load, press Tab repeatedly and count stops before re-entering the tree. Inspect treeitems: exactly one must have `tabindex="0"`, all others `tabindex="-1"`. Move focus inside the tree via arrows; confirm the `tabindex="0"` slot moves with focus (roving). Tab away — verify Shift+Tab returns to the same node, not the first one.
- **Pass criterion.** Sidebar consumes exactly ONE tab stop (per FR-19). Roving tabindex visibly moves. Returning focus lands on last-focused node.
- **WCAG 2.1 SC.** 2.1.1, 2.4.3.
- **Spec refs.** FR-19.

### A11Y-22 — Regen-prompt warning banner has `role="status"` [Spec-mandated]

- **Tooling.** DOM inspection + `nvda`.
- **Method.** In the regen-prompt UI, build a prompt large enough to trip the >50 KB warning (FR-14c size policy). Inspect the warning banner that appears: must have `role="status"` (live, non-interruptive — vs `role="alert"` which interrupts). With NVDA, build a prompt and confirm the warning is announced after current speech finishes, not as an interruption.
- **Pass criterion.** Banner has `role="status"` (or `aria-live="polite"`). Visible text matches `warning: {warning} — verify your selection before pasting`. NVDA announces it politely.
- **WCAG 2.1 SC.** 4.1.3.
- **Spec refs.** FR-42 (e), FR-14c.

### A11Y-23 — Editor toolbar buttons reachable and labeled [Recommended]

- **Tooling.** `kb` + DOM inspection.
- **Method.** In edit mode, Tab through the toolbar. Confirm Save / Discard / Close-editor are real `<button>`s with descriptive accessible names. Confirm Save is disabled (`disabled` attribute, NOT just visual) when no unsaved changes.
- **Pass criterion.** All three are `<button>` with text content or `aria-label`. Save's `disabled` attribute reflects FR-40 (b).
- **WCAG 2.1 SC.** 2.1.1, 4.1.2.
- **Spec refs.** FR-40 (a), (b).

### A11Y-24 — Q/A view: each block is a labeled landmark [Recommended]

- **Tooling.** DOM inspection + `nvda`.
- **Method.** Render `interview/qa.md`. Inspect each round/category/Q/A block: each Q block should have an accessible name like "Question N" or include the question text as its label; the inline pencil button should have `aria-label="Edit question N"` (or equivalent). NVDA browse-mode quick-nav by buttons (`B`) should reveal each pencil with an unambiguous label.
- **Pass criterion.** Each pencil button has an unambiguous accessible name. NVDA `B` traversal does not produce duplicate labels like "Edit, Edit, Edit".
- **WCAG 2.1 SC.** 2.4.6, 4.1.2.
- **Spec refs.** FR-41.

### A11Y-25 — Lighthouse Accessibility ≥ 95 [Recommended]

- **Tooling.** `lh`.
- **Method.** Run Lighthouse Accessibility audit on the three principal routes: `/`, `/file/specs/development/spec_driven/final_specs/spec.md`, `/project/development/spec_driven`.
- **Pass criterion.** Each route scores ≥ 95. Sub-100 scores are documented with the specific audits that failed and a remediation note.
- **WCAG 2.1 SC.** Cross-cutting.
- **Spec refs.** NFR-9, NFR-10.

## Reporting

A failure on any **[Spec-mandated]** check is a release blocker. Failures on **[Recommended]** checks file a tracked issue but do not block. Re-run the full suite manually before each release. Reported failures should include screenshots and exact NVDA speech transcripts where applicable.
