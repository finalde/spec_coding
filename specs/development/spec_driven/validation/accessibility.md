# Accessibility validation — spec_driven

Run: spec_driven-20260502-141813
Level: 07 / accessibility
Inputs: `specs/development/spec_driven/final_specs/spec.md` (FR-18, FR-19, FR-20, FR-24, FR-25, FR-26, FR-29, FR-34, FR-39, NFR-9, NFR-10, NFR-11)

## Scope

This document defines the accessibility (a11y) validation checks for the `spec_driven` viewer. Each check has an ID, WCAG / ARIA reference, tooling, plain-text procedure, exact pass criterion, spec refs, and a reusable fixture. Checks are tagged `[Spec-mandated]` (must pass for the spec to be satisfied) or `[Recommended]` (gap-flag — the spec is silent; surface as a v1 best-practice addition or a v2 candidate).

The viewer targets latest stable Chromium-based browsers only (NFR-14). Mobile / tablet / Firefox / Safari are explicitly out of scope, but the underlying ARIA/WCAG conformance is browser-independent and so is required regardless.

## Tooling baseline (used across multiple checks)

- **axe-core** via the `@axe-core/playwright` adapter or the standalone Chrome DevTools "axe" extension. Used for automated rule scans.
- **Chrome DevTools → Lighthouse → Accessibility** audit. Used for high-level coverage and contrast spot-checks.
- **Chrome DevTools → Elements → Accessibility tree** pane. Used to read the computed accessible name, role, and ARIA state for any focused node.
- **Chrome DevTools → Issues → Contrast**. Quick pass for contrast on whatever is rendered.
- **NVDA 2024.x + Chrome** (Windows). Used to verify announcements, since NVDA is the dominant free screen reader on the supported platform.
- **TPGi Colour Contrast Analyzer (CCA)**. Used for state-by-state contrast measurement (default / hover / focus / selected / disabled), which axe alone does not enumerate.
- **Manual keyboard** (no mouse). Used for every keyboard-map and focus-management check.

## Fixture inventory

Reused across checks. Each fixture is a concrete on-disk state plus a recipe to reach it.

- **F-A: Default dogfood tree.** Repo at `final_specs/spec.md` exists. Sidebar opens at `/projects/development/spec_driven/final_specs/spec.md`. Used for baseline checks (A11Y-01, A11Y-02, A11Y-03, A11Y-04, A11Y-06, A11Y-07, A11Y-11, A11Y-14).
- **F-B: Missing-stage tree.** Delete `specs/development/spec_driven/validation/` from disk before page load (or use a fresh project where Stage 5 has not run). Sidebar receives `present: false` for `validation`. Used for A11Y-05, A11Y-10.
- **F-C: Narrow sidebar truncation.** Force a project / file path whose rendered name exceeds 320px at the sidebar's font-size — e.g., create a temporary task `specs/development/this_is_an_intentionally_long_task_name_used_only_for_truncation_testing/final_specs/a_file_with_an_intentionally_long_filename_for_middle_ellipsis_testing.md`. Used for A11Y-09.
- **F-D: Broken-link markdown.** Author or use an existing markdown file containing all four broken-link causes:
  1. `[not yet generated](../validation/strategy.md)` while `validation/` is absent → tooltip `not yet generated`.
  2. `[file not found](../findings/does_not_exist.md)` → tooltip `file not found`.
  3. `[outside exposed tree](../../../pyproject.toml)` → tooltip `outside exposed tree`.
  4. `[anchor not found](#never-defined-heading)` → tooltip `anchor not found`.
  Used for A11Y-12.
- **F-E: External link markdown.** A file containing `[example](https://example.com/)`. Used for A11Y-13.
- **F-F: Reduced-motion OS setting.** Windows → Settings → Accessibility → Visual effects → Animation effects = OFF, OR Chrome DevTools → Rendering → "Emulate CSS media feature prefers-reduced-motion: reduce". Used for A11Y-15.
- **F-G: Image-in-markdown.** A file containing `![diagram of the pipeline](./diagram.png)` where `diagram.png` is inside `EXPOSED_TREE` paths but the extension is not in the supported set. Used for A11Y-16.
- **F-H: Long code block.** A markdown file with a fenced ```python block ~120 columns wide and ~80 lines tall, to force horizontal and vertical overflow on the rendered `<pre>`. Used for A11Y-17.
- **F-I: Heading-skip markdown.** A markdown file that goes h1 → h3 → h2. Used for A11Y-08 (observational only).
- **F-J: Link-list markdown.** A markdown file containing several real internal links and one external link with descriptive text. Used for A11Y-18.

---

## A11Y-01 — Tree container ARIA roles and single tab stop

`[Spec-mandated]`

- **WCAG / ARIA reference:** WAI-ARIA 1.2 `tree` role. ARIA Authoring Practices Guide (APG) — TreeView pattern, "Keyboard interaction" → "the tree itself is in the page Tab sequence" (single tab stop). WCAG 2.1 SC 4.1.2 Name, Role, Value.
- **Tooling:** Chrome DevTools Accessibility tree pane; manual keyboard; axe-core.
- **Procedure:**
  1. Load fixture F-A.
  2. Inspect the sidebar root element. Read its computed `role` and ARIA properties from the Accessibility pane.
  3. Press Tab from the URL bar repeatedly. Record where focus lands on each press.
  4. While focus is on a tree item, press Tab once and confirm focus exits the tree to the next page-level focusable (e.g., the breadcrumb's first link or the main pane's heading).
  5. While focus is on a tree item, press Shift+Tab and confirm focus exits the tree to the previous page-level focusable (e.g., the sidebar Refresh button).
  6. Run axe-core scan limited to `[role="tree"]`.
- **Pass criterion:**
  - The tree container element has `role="tree"` and `aria-multiselectable="false"` in the Accessibility tree pane.
  - Exactly one descendant of the tree has `tabindex="0"` at any time; all other tree items have `tabindex="-1"` (roving tabindex per APG).
  - One Tab press from outside enters the tree at the currently-focused item; one further Tab press exits the tree to the next page-level control.
  - axe-core reports zero violations on rules `aria-allowed-role`, `aria-required-children`, `aria-required-parent` for the tree subtree.
- **Spec refs:** FR-18, NFR-9.

## A11Y-02 — Treeitem roles, aria-level, aria-expanded

`[Spec-mandated]`

- **WCAG / ARIA reference:** WAI-ARIA 1.2 `treeitem` role; `aria-level`, `aria-expanded`. ARIA APG — TreeView "WAI-ARIA Roles, States, and Properties". WCAG 2.1 SC 4.1.2.
- **Tooling:** Chrome DevTools Accessibility tree pane; manual DOM inspection; axe-core.
- **Procedure:**
  1. Load fixture F-A.
  2. Expand `Projects > development > spec_driven > final_specs`.
  3. Pick four sample nodes at distinct depths: `Projects` (depth 1), `development` (depth 2), `spec_driven` (depth 3), `final_specs` (depth 4), `spec.md` (depth 5).
  4. For each, read `role`, `aria-level`, `aria-expanded` from the Accessibility tree pane.
  5. Inspect a leaf node (e.g., `spec.md`) and confirm it has NO `aria-expanded` attribute (not even `aria-expanded="false"`).
  6. Inspect a folder node (e.g., `final_specs`) in collapsed and expanded states; confirm `aria-expanded` toggles `"false"` ↔ `"true"`.
  7. Run axe-core; check `aria-required-attr` and `aria-valid-attr-value` rules.
- **Pass criterion:**
  - Every visible row has `role="treeitem"`.
  - `aria-level` numeric value equals nesting depth (top-level row = 1, increments by 1 per nest).
  - Folders carry `aria-expanded="true"` when expanded and `aria-expanded="false"` when collapsed.
  - Leaves have no `aria-expanded` attribute at all.
  - axe-core reports zero violations on these rules within the tree subtree.
- **Spec refs:** FR-18.

## A11Y-03 — Single aria-selected matches URL-pointed file

`[Spec-mandated]`

- **WCAG / ARIA reference:** WAI-ARIA 1.2 `aria-selected`. ARIA APG TreeView — "Selection" (single-select tree). WCAG 2.1 SC 4.1.2.
- **Tooling:** Chrome DevTools Accessibility tree pane; manual navigation; DOM query `document.querySelectorAll('[aria-selected="true"]')`.
- **Procedure:**
  1. Load fixture F-A. Confirm the URL is `/projects/development/spec_driven/final_specs/spec.md`.
  2. In the Accessibility pane (or a DOM query in DevTools console), find all elements with `aria-selected="true"` inside the tree.
  3. Click a different sidebar leaf, e.g., `findings/dossier.md`. Wait for the URL to update. Re-run step 2.
  4. Use the browser back button. Re-run step 2.
  5. Manually edit the URL to a different valid file path and press Enter. Re-run step 2.
- **Pass criterion:**
  - At every observation point, exactly one node inside the tree has `aria-selected="true"`.
  - That node is the leaf whose path corresponds to the current URL (per FR-15 / FR-38).
  - All other treeitems have either `aria-selected="false"` or no `aria-selected` attribute.
- **Spec refs:** FR-18, FR-38.

## A11Y-04 — Keyboard map per W3C ARIA APG TreeView

`[Spec-mandated]`

- **WCAG / ARIA reference:** ARIA APG — TreeView "Keyboard interaction" (Up/Down/Right/Left/Enter table). WCAG 2.1 SC 2.1.1 Keyboard. WCAG 2.1 SC 2.1.2 No Keyboard Trap.
- **Tooling:** Manual keyboard only; Accessibility tree pane to confirm focus location.
- **Procedure:**
  1. Load fixture F-A. Press Tab until focus lands on the tree.
  2. **Up/Down:** Press Down five times, then Up five times. After each press confirm focus moves to the next/previous visible row only. Hidden rows (children of collapsed folders, missing-state nodes per A11Y-05) MUST be skipped.
  3. **Right on collapsed folder:** Move focus to a collapsed folder. Press Right. Confirm folder expands; focus stays on the folder; `aria-expanded` flips to `"true"`.
  4. **Right on expanded folder:** With focus on the now-expanded folder, press Right. Confirm focus moves to the first child row; folder remains expanded.
  5. **Right on leaf:** Move focus to a leaf (e.g., `spec.md`). Press Right. Confirm no-op: focus stays, no URL change, no expand state change anywhere.
  6. **Left on expanded folder:** Move focus to an expanded folder. Press Left. Confirm folder collapses; focus stays on the folder; `aria-expanded` flips to `"false"`.
  7. **Left on collapsed folder or leaf:** Move focus to a collapsed folder, press Left, confirm focus moves to its parent folder. Then on a leaf, press Left, confirm focus moves to its parent folder.
  8. **Enter on leaf:** Press Enter on a leaf. Confirm URL updates and main pane re-renders the file.
  9. **Enter on folder:** Press Enter on any folder. Confirm no-op: URL unchanged, no expand/collapse change.
  10. **No keyboard trap:** From any tree state, press Tab and confirm focus exits the tree (already covered by A11Y-01 but re-verify with the tree in a non-default expansion state).
- **Pass criterion:** Every keystroke produces exactly the behavior listed in FR-19 and the APG TreeView keyboard table. No extra side effects (e.g., Right on a leaf must NOT navigate, must NOT scroll the main pane). Tab is never trapped.
- **Spec refs:** FR-19, NFR-9.

## A11Y-05 — Missing-state items are skipped by arrow nav and not activatable

`[Spec-mandated]`

- **WCAG / ARIA reference:** ARIA APG TreeView "Keyboard interaction" (focus order is visible-rows-only). WCAG 2.1 SC 2.1.1 Keyboard. WCAG 2.1 SC 2.4.3 Focus Order.
- **Tooling:** Manual keyboard; NVDA + Chrome; Accessibility tree pane.
- **Procedure:**
  1. Load fixture F-B (project where `validation/` directory does not exist → tree has `validation` entry with `present: false`).
  2. Visually confirm the `validation` row renders as muted-italic.
  3. Tab into the tree. Use Down arrow to walk the project's stage rows: `user_input`, `interview`, `findings`, `final_specs`, then the next visible row. Confirm focus does NOT land on `validation`.
  4. Try to click the `validation` row with the mouse. Confirm no URL change occurs (FR-24).
  5. Hover the `validation` row. Confirm tooltip text is exactly `not yet generated`.
  6. Start NVDA. Tab to the tree. Walk the rows with Down arrow. Confirm NVDA never announces the `validation` row as a selectable / activatable treeitem during arrow walk.
- **Pass criterion:**
  - Down/Up arrow nav skips the `present: false` row entirely.
  - Mouse click on the row produces no URL change and no `aria-selected` change.
  - NVDA does not announce the row as a focusable treeitem during arrow walk.
  - The row's accessible name is the stage name; the `title` attribute supplies `not yet generated`; no `aria-disabled` is required by the spec but the row must be effectively non-interactive.
- **Spec refs:** FR-24, FR-9.

## A11Y-06 — Focus and selection visuals are simultaneously distinguishable

`[Spec-mandated]`

- **WCAG / ARIA reference:** WCAG 2.1 SC 2.4.7 Focus Visible. WCAG 2.1 SC 1.4.11 Non-text Contrast (focus indicator ≥ 3:1 against adjacent colors). ARIA APG — visually distinguish focus from selection.
- **Tooling:** Manual keyboard; Chrome DevTools Computed pane; TPGi Colour Contrast Analyzer.
- **Procedure:**
  1. Load fixture F-A. Click a leaf so it becomes selected. Visually confirm the selected leaf has a filled background bar.
  2. Without clicking, Tab into the tree and use arrow keys to move focus to a *different* leaf. Confirm the selection indicator stays on the originally-clicked leaf and the focus indicator (ring outline) appears on the new leaf — both visible at once on different rows.
  3. Move focus back to the originally-selected leaf using arrow keys. Confirm both the filled background bar AND the ring outline are visible simultaneously on the same row.
  4. In DevTools, inspect the focused-and-selected row. Read computed `outline`, `box-shadow`, and `background-color`. Confirm the focus indicator is a separate visual property from the background fill (i.e., not a single style that conflates them).
  5. Use CCA to measure contrast between the focus ring color and (a) the row's selected background, (b) the sidebar's container background. Both ≥ 3:1.
- **Pass criterion:**
  - Selected-only state: filled bar visible, no ring.
  - Focused-only state (focus elsewhere from selection): ring visible, no filled bar on the focused row; filled bar still visible on the selected row.
  - Focused-and-selected (same row): both filled bar and ring visible at once and visually distinct.
  - Focus ring contrast ≥ 3:1 against both adjacent backgrounds.
- **Spec refs:** FR-20, NFR-9.

## A11Y-07 — WCAG 2.1 AA color contrast across all interactive states

`[Spec-mandated]`

- **WCAG / ARIA reference:** WCAG 2.1 SC 1.4.3 Contrast (Minimum) — 4.5:1 for normal text, 3:1 for large text (≥ 18pt or ≥ 14pt bold). WCAG 2.1 SC 1.4.11 Non-text Contrast — 3:1 for UI components and graphical objects.
- **Tooling:** axe-core; TPGi Colour Contrast Analyzer (CCA); Chrome DevTools Issues → Contrast.
- **Procedure:**
  1. Load fixture F-A. Run axe-core full-page scan; record all `color-contrast` and `color-contrast-enhanced` findings.
  2. With CCA, sample foreground vs background for each of the following surfaces in each state listed:
     - Sidebar row text (default, hover, focus, selected, focus+selected).
     - Sidebar muted-italic missing-state row (default).
     - Sidebar Refresh button label and icon (default, hover, focus, active).
     - Breadcrumb non-final segment (default, hover, focus).
     - Breadcrumb final segment plain text.
     - Markdown body link (default, hover, focus, visited).
     - Broken-link span text (`<span class="link-broken">`).
     - Inline code (markdown backticks) text.
     - Shiki-highlighted code block: spot-check the most-used token colors (keyword, string, comment, identifier) against the code-block background.
     - Image-placeholder span (`<span class="image-placeholder">` with alt text).
  3. Repeat the sidebar row state-by-state measurements with system high-contrast disabled (default Chromium).
- **Pass criterion:**
  - Every text foreground/background pair ≥ 4.5:1, except large text ≥ 3:1.
  - Every UI control border / focus ring / icon vs adjacent surface ≥ 3:1.
  - axe-core reports zero `color-contrast` violations.
  - Comment-token color in code blocks specifically must not fall below 4.5:1 against the code-block background (common Shiki theme failure).
- **Spec refs:** NFR-10.

## A11Y-08 — Heading semantics in rendered markdown

`[Recommended — observational]`

- **WCAG / ARIA reference:** WCAG 2.1 SC 1.3.1 Info and Relationships. WCAG 2.1 SC 2.4.6 Headings and Labels. The spec (NFR-11) explicitly states the renderer does not enforce no-skipping; this check is observational on source content.
- **Tooling:** axe-core; manual DOM inspection.
- **Procedure:**
  1. Load fixture F-I (markdown with h1 → h3 → h2 sequence).
  2. Confirm the rendered DOM contains `<h1>`, `<h3>`, `<h2>` literally — i.e., the renderer preserves authored heading levels rather than rewriting them.
  3. Run axe-core; expect to see `heading-order` rule report a *warning* (not failure) on this fixture.
  4. Document the spec's explicit non-enforcement so reviewers understand this is a content-authoring discipline issue, not a renderer bug.
- **Pass criterion:**
  - Rendered DOM heading tags match the authored heading levels (no silent rewrite).
  - axe `heading-order` finding for this fixture is documented as expected; no app-code change required.
  - Project-internal markdown source files (CLAUDE.md, this spec, dossier, qa) SHOULD NOT skip heading levels — flag any source file that does, and recommend authors fix the source rather than asking the renderer to mask it.
- **Spec refs:** NFR-11, FR-30. Spec is explicit: no-skipping is not enforced. This check exists to make that decision visible to reviewers.

## A11Y-09 — Long-name truncation accessibility

`[Spec-mandated]`

- **WCAG / ARIA reference:** WCAG 2.1 SC 1.3.1 Info and Relationships. WCAG 2.1 SC 4.1.2 Name, Role, Value (accessible name must convey full text). WCAG 2.1 SC 1.4.4 Resize Text (truncation must not destroy information).
- **Tooling:** Manual; Chrome DevTools Accessibility pane (Computed name); NVDA.
- **Procedure:**
  1. Load fixture F-C (long task_name and long filename).
  2. Visually confirm the long task_name (folder row) renders with end-ellipsis (e.g., `this_is_an_intentionally_long…`).
  3. Visually confirm the long filename (file row) renders with middle-ellipsis preserving the `.md` suffix (e.g., `a_file_with_an…testing.md`).
  4. Hover each row; confirm the native browser tooltip shows the full text via the `title` attribute.
  5. In the Accessibility pane, read the row's "Name" property. It must be the full text (either from `title` if no other accessible name source exists, or from inner text if not truncated by CSS-only ellipsis).
  6. With NVDA, focus the row using arrow keys. Confirm NVDA reads the full untruncated text (CSS ellipsis affects visuals only; the DOM text node remains intact).
  7. Confirm the row does NOT carry an `aria-label` that contradicts (truncates or rewrites) the visible/title text. If `aria-label` is present, it must equal the full text.
- **Pass criterion:**
  - File rows: middle-ellipsis preserving `.md`.
  - Folder rows: end-ellipsis.
  - `title` attribute holds the full text on every row.
  - NVDA announces the full text.
  - No row uses horizontal scroll or wraps onto a second line.
  - No `aria-label` shorter than the full text.
- **Spec refs:** FR-25.

## A11Y-10 — Folder click is toggle-only and does not move focus

`[Spec-mandated]`

- **WCAG / ARIA reference:** ARIA APG — TreeView "Mouse interaction"; "click on parent node toggles expansion". WCAG 2.1 SC 2.4.3 Focus Order.
- **Tooling:** Manual mouse; NVDA touch / virtual cursor (simulated by NVDA's review cursor mode).
- **Procedure:**
  1. Load fixture F-A.
  2. Mouse-click a folder (e.g., `findings`). Confirm: folder expands or collapses; URL does NOT change; main pane does not re-render to a different file.
  3. With NVDA running and review cursor on the folder row, activate the row. Confirm focus does NOT jump to the first child row (only Right arrow per FR-19 should do that).
  4. Click an already-expanded folder again. Confirm it collapses, URL still does not change.
  5. Confirm there is no double-click, no context menu, no drag-drop, no multi-select on any sidebar interaction.
- **Pass criterion:** Folder mouse-click toggles `aria-expanded` only. URL is unchanged. Focus stays on the folder row. Touch-style activation does not auto-advance focus to the first child.
- **Spec refs:** FR-26, FR-19.

## A11Y-11 — Breadcrumb navigation landmark and aria-current

- **A11Y-11a `[Spec-mandated]`**
- **A11Y-11b `[Recommended]`** for `aria-current` on the final segment.
- **WCAG / ARIA reference:** WAI-ARIA 1.2 — `nav` landmark, `aria-current`. ARIA APG — Breadcrumb pattern. WCAG 2.1 SC 1.3.1, SC 2.4.8 Location.
- **Tooling:** Manual DOM inspection; axe-core; Chrome DevTools Accessibility pane.
- **Procedure:**
  1. Load fixture F-A.
  2. Inspect the breadcrumb container element. Confirm it is a `<nav>` element with `aria-label="Breadcrumb"` (or equivalent accessible name).
  3. Confirm the breadcrumb items live inside an ordered list (`<ol>`), one `<li>` per segment.
  4. For each non-final segment, confirm the segment is a real `<a>` (or React Router `<Link>` rendering a real `<a>`) with `href` pointing to the segment's folder URL.
  5. Confirm the final segment is plain text (not an `<a>`). Recommend that it carry `aria-current="page"`.
  6. Click each non-final segment in turn; confirm in-app navigation occurs and FR-16 folder-redirect resolves to the first file.
  7. Run axe-core; confirm zero violations on `landmark-unique` and `aria-current-state` rules.
- **Pass criterion:**
  - `<nav aria-label="Breadcrumb">` wrapper present (mandatory).
  - Ordered list with each segment a `<li>` (mandatory).
  - Non-final segments are real `<a>` (mandatory).
  - Final segment is plain text (mandatory).
  - Final segment carries `aria-current="page"` (recommended; flag absence as a v1 best-practice gap, not a failure).
- **Spec refs:** FR-29. Spec is silent on `aria-current`; treat its absence as a recommended addition.

## A11Y-12 — Broken-link span semantics

- **A11Y-12a `[Spec-mandated]`**
- **A11Y-12b `[Recommended]`** for `aria-disabled="true"`.
- **WCAG / ARIA reference:** WAI-ARIA 1.2 `aria-disabled`; element semantics (an `<a>` without `href` or replaced by `<span>` is intentionally non-interactive). WCAG 2.1 SC 1.3.1; SC 4.1.2.
- **Tooling:** DOM inspection; manual click; NVDA.
- **Procedure:**
  1. Load fixture F-D (markdown with all four broken-link causes).
  2. Inspect each broken link's rendered DOM:
     - Element MUST be `<span class="link-broken">`, NOT `<a>`.
     - `title` attribute MUST be exactly one of: `not yet generated`, `file not found`, `outside exposed tree`, `anchor not found` (per FR-34).
     - Style: muted color, no underline.
  3. Mouse-click each broken-link span. Confirm no navigation, no JS error, no console warning.
  4. Tab through the page. Confirm broken-link spans are NOT in the Tab order (a `<span>` without `tabindex` is naturally non-focusable).
  5. With NVDA, navigate the page text. Confirm NVDA reads the link text as plain text (no "link" role announced) and surfaces the `title` text on hover/focus simulation.
  6. Recommend `aria-disabled="true"` be added to the span. Verify the spec is silent on this and flag.
- **Pass criterion:**
  - Element is a `<span class="link-broken">`, not an anchor. (mandatory)
  - `title` matches one of the four exact strings, paired with the correct cause. (mandatory)
  - Click is a no-op. (mandatory)
  - Element is not in keyboard tab order. (mandatory)
  - NVDA does not announce as link. (mandatory)
  - `aria-disabled="true"` is present (recommended; spec gap to flag).
- **Spec refs:** FR-34, FR-24, FR-33, FR-35.

## A11Y-13 — External link new-tab announcement

- **A11Y-13a `[Spec-mandated]`** for `target="_blank"` + `rel="noopener noreferrer"`.
- **A11Y-13b `[Recommended]`** for screen-reader announcement that the link opens in a new tab.
- **WCAG / ARIA reference:** WCAG 2.1 SC 3.2.5 Change on Request (advisory: warn users when a link opens a new context). WAI-ARIA `aria-describedby` or visually-hidden text pattern.
- **Tooling:** DOM inspection; NVDA.
- **Procedure:**
  1. Load fixture F-E (markdown with `https://example.com/`).
  2. Inspect the rendered anchor; confirm `target="_blank"` and `rel="noopener noreferrer"` (FR-33 case 1).
  3. With NVDA, focus the link via Tab. Listen to the announcement.
  4. Confirm whether NVDA says something like "link, opens in new tab/window". If it does NOT (the spec does not mandate any visually-hidden hint or `aria-describedby`), flag this as a recommended addition: add a visually-hidden `<span>` like `(opens in new tab)` after the link, OR an `aria-describedby` pointing to a shared off-screen description.
  5. Click the link; confirm a new tab opens and the original tab is unaffected.
- **Pass criterion:**
  - `target="_blank"` and `rel="noopener noreferrer"` present. (mandatory)
  - Either NVDA natively announces "new tab" (varies by NVDA version + Chrome — usually yes for `target="_blank"`) OR the implementation adds a visually-hidden hint or `aria-describedby` for the announcement. The spec is silent; flag the absence as a recommended addition, not a failure.
- **Spec refs:** FR-33 case 1.

## A11Y-14 — Sidebar Refresh button semantics

`[Spec-mandated]`

- **WCAG / ARIA reference:** WCAG 2.1 SC 2.1.1 Keyboard; SC 4.1.2 Name, Role, Value. ARIA APG — Button pattern.
- **Tooling:** DOM inspection; manual keyboard; Chrome DevTools Accessibility pane.
- **Procedure:**
  1. Load fixture F-A.
  2. Inspect the Refresh control. Confirm it is a real `<button type="button">`, not a `<div>` or `<span>` with click handler.
  3. Read the accessible name from the Accessibility pane. It must be a non-empty descriptive string such as `Refresh sidebar`, `Refresh tree`, or equivalent. If the visible label is only an icon, an `aria-label` is required.
  4. Tab to the button. Press Space; confirm the tree re-fetches.
  5. Tab to the button again. Press Enter; confirm the tree re-fetches.
  6. Confirm focus is visible while focused (covered by A11Y-06 contrast rules).
  7. Trigger the inline reuse: load a state that produces 404 `kind: "file_removed"` (e.g., delete the currently-viewed file mid-session and then click its sidebar entry). Confirm the inline Refresh button in the main pane is also a real `<button>` with the same accessibility properties.
- **Pass criterion:**
  - Element is `<button>` (mandatory).
  - Accessible name is descriptive, non-empty (mandatory).
  - Both Space and Enter activate it (mandatory; this is automatic for native `<button>`).
  - Focus indicator visible (mandatory).
  - Inline-in-main-pane reuse maintains the same semantics (mandatory).
- **Spec refs:** FR-28.

## A11Y-15 — Reduced-motion respect for sidebar expand/collapse

`[Recommended]`

- **WCAG / ARIA reference:** WCAG 2.1 SC 2.3.3 Animation from Interactions (AAA, but widely treated as required for any non-essential animation). CSS Media Queries Level 5 — `prefers-reduced-motion`.
- **Tooling:** Chrome DevTools → Rendering → "Emulate CSS media feature prefers-reduced-motion: reduce"; manual observation; Computed styles pane.
- **Procedure:**
  1. Load fixture F-A under default motion settings. Expand and collapse a folder. Confirm the 100–150ms ease transition runs (per FR-39).
  2. Apply fixture F-F (emulate `prefers-reduced-motion: reduce`). Reload the page or re-trigger the expand/collapse.
  3. Inspect the expanding row's computed `transition-duration` while under reduced motion. Confirm whether it is set to `0ms` (or the transition is removed entirely) or whether the original 100–150ms still applies.
- **Pass criterion (recommended):**
  - Under `prefers-reduced-motion: reduce`, the sidebar expand/collapse transition is reduced to ~0ms or removed.
  - The spec (FR-39) does not require this; if the implementation does not honor the media query, log it as a recommended addition citing WCAG SC 2.3.3 and the CSS Media Queries Level 5 spec.
- **Spec refs:** FR-39. Spec gap.

## A11Y-16 — Image placeholder accessible name

`[Spec-mandated]`

- **WCAG / ARIA reference:** WCAG 2.1 SC 1.1.1 Non-text Content. WAI-ARIA 1.2 Accessible Name and Description Computation.
- **Tooling:** DOM inspection; Chrome DevTools Accessibility pane; NVDA.
- **Procedure:**
  1. Load fixture F-G (markdown containing `![diagram of the pipeline](./diagram.png)`).
  2. Inspect the rendered element. Confirm it is `<span class="image-placeholder">diagram of the pipeline</span>` with `title="v1: images not rendered"` (FR-36).
  3. In the Accessibility pane, read the element's "Name". It should be `diagram of the pipeline` (from the visible text node), not the `title` text.
  4. Confirm no `aria-label` is applied (an `aria-label` would override the visible text and either duplicate or hide the alt text from sighted+AT users — spec does not request one).
  5. With NVDA, navigate to the element with the cursor. Confirm NVDA reads the alt text as plain text content. The `title` may be read on hover or with a different keystroke; that is acceptable supplementary information.
- **Pass criterion:**
  - Element is `<span class="image-placeholder">` containing the alt text as visible text. (mandatory)
  - `title="v1: images not rendered"`. (mandatory)
  - No `aria-label` redundantly applied. (mandatory)
  - NVDA reads the alt text as content; the placeholder hint is supplementary. (mandatory)
- **Spec refs:** FR-36.

## A11Y-17 — Code block AT compatibility and overflow keyboard access

- **A11Y-17a `[Spec-mandated]`** for not introducing AT-broken structures.
- **A11Y-17b `[Recommended]`** for keyboard-scrollable overflow.
- **WCAG / ARIA reference:** WCAG 2.1 SC 2.1.1 Keyboard. WCAG 2.1 SC 1.4.10 Reflow. ARIA — only roles or `aria-hidden` should be added to Shiki output if there is a clear semantic reason; gratuitous `role` or `aria-hidden` on syntax-token spans breaks copy/paste with screen readers.
- **Tooling:** DOM inspection; manual keyboard; NVDA; Chrome DevTools Computed pane.
- **Procedure:**
  1. Load fixture F-H (long fenced ```python block).
  2. Inspect the rendered Shiki output. Confirm:
     - The outer element is `<pre>` (or `<pre><code>`).
     - Token `<span>` children carry color classes only — no ARIA roles such as `role="presentation"` on every token, no `aria-hidden="true"` on tokens.
  3. With NVDA "say all" mode, read the code block. Confirm the full text is announced and matches what would be copied to the clipboard via Ctrl+C.
  4. Click and Ctrl+C select-and-copy the block. Paste into a plain-text scratchpad; confirm the pasted text matches the source.
  5. If the block overflows horizontally or vertically, attempt to scroll it with the keyboard alone. Either:
     - The `<pre>` is keyboard-focusable (`tabindex="0"`) and arrow keys scroll its content. (recommended)
     - OR a focusable child inside is reachable so the Tab key can park focus inside the scroll container.
- **Pass criterion:**
  - No ARIA roles or `aria-hidden` are applied that hide token text from AT. (mandatory)
  - Copied text matches rendered text. (mandatory)
  - `<pre>` overflow is keyboard-scrollable, ideally via `tabindex="0"`. The spec is silent; flag as recommended if absent (some Shiki integrations omit this and force pointer-only scrolling, which fails WCAG SC 2.1.1 once the block overflows).
- **Spec refs:** FR-31, FR-32.

## A11Y-18 — Markdown link list real anchors

`[Spec-mandated]`

- **WCAG / ARIA reference:** WCAG 2.1 SC 2.4.4 Link Purpose (In Context). WAI-ARIA — links must be `<a>` (or have `role="link"` if not, but `<a>` is required by spec for real navigation).
- **Tooling:** axe-core; DOM inspection; manual keyboard.
- **Procedure:**
  1. Load fixture F-J (markdown link list with internal links and one external link).
  2. Inspect each rendered link.
     - Internal links: `<a href="…" class="…">` produced by React Router `<Link>`, with the visible text being the descriptive markdown link text (FR-33 case 3).
     - External links: `<a href="…" target="_blank" rel="noopener noreferrer">`.
  3. Confirm none of the links uses generic "click here" or "more" text. (Recommend: spec does not mandate, but flag any such text as an authoring issue, not a renderer bug.)
  4. Tab through the page; confirm every link is reachable and activates with Enter.
  5. Run axe-core `link-name` rule; confirm zero violations.
- **Pass criterion:**
  - Every link is a real `<a>`. (mandatory)
  - Accessible name is the visible text (no `aria-label` overriding it). (mandatory)
  - Tab + Enter activate every link. (mandatory)
  - axe-core `link-name` reports zero violations. (mandatory)
  - "click here" / "more" / placeholder text is absent. (recommended; authoring discipline)
- **Spec refs:** FR-33.

---

## Spec gaps surfaced (recommended additions)

Each gap below is a recommended-not-mandated finding. Validation should pass even if these are absent in v1, but they should be tracked as `Recommended additions` for v1.1 or v2.

1. **Breadcrumb final segment lacks `aria-current="page"`.** FR-29 specifies the final crumb is plain text; it does not call for `aria-current`. Adding it improves AT navigation context (WCAG 2.4.8). See A11Y-11.
2. **Broken-link span lacks `aria-disabled="true"`.** FR-34 specifies `<span class="link-broken">` with `title`; spec is silent on `aria-disabled`. Adding it makes the disabled semantic explicit to AT. See A11Y-12.
3. **External link has no screen-reader hint that it opens in a new tab.** FR-33 case 1 specifies `target="_blank"` + `rel="noopener noreferrer"` only. NVDA in current Chrome does usually announce "new tab", but cross-AT consistency improves with a visually-hidden span or `aria-describedby` shared text. See A11Y-13.
4. **Sidebar expand/collapse animation does not honor `prefers-reduced-motion: reduce`.** FR-39 specifies a 100–150ms ease but is silent on the reduced-motion media query. WCAG 2.3.3 expects a way to disable non-essential animation. See A11Y-15.
5. **Code-block overflow may not be keyboard-scrollable.** FR-31 / FR-32 specify Shiki rendering but do not address `tabindex="0"` on `<pre>` for overflow. WCAG 2.1.1 requires keyboard reach for any scrollable region. See A11Y-17.
6. **Heading-skip is not enforced by the renderer (NFR-11 explicitly).** This is documented as observational only and should be addressed at the source-content level by markdown authors. See A11Y-08.

## Tooling installation notes (one-time setup)

- axe-core: install `@axe-core/playwright` for automated runs, OR use the free Chrome extension "axe DevTools" for ad-hoc.
- NVDA: download from nvaccess.org; use NVDA + Chrome on Windows. Default object review and focus mode are sufficient for these checks.
- TPGi Colour Contrast Analyzer: download from tpgi.com/color-contrast-checker. Use eyedropper on rendered pixels for state-by-state checks.
- Chrome DevTools panes used: Elements → Accessibility (right-side pane), Issues, Rendering (for media-feature emulation), Lighthouse.

## Out-of-scope confirmations

- Mobile screen readers (TalkBack / VoiceOver iOS): not in scope (NFR-14).
- Firefox / Safari AT compatibility: not in scope (NFR-14).
- High-contrast / forced-colors mode: not explicitly in spec; recommend a future smoke test with Windows High Contrast active, but not required for v1.

End of accessibility validation plan.
