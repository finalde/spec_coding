# Validation — Accessibility

Run: `spec_driven-20260503-145859` (stage 5, level-specialist-07-accessibility, parent-direct).

Scope: every interactive surface produced by FR-15..FR-36 plus the cross-cutting theme contract from NFR-16 / `agent_refs/project/development.md`. Each check follows a fixed shape: **Surface** (which spec FR / region of the SPA the check inspects), **WCAG ref** (success-criterion identifier — 2.1 AA baseline), **Method** (how a validator proves the check passes — automated tool, scripted assertion, or scripted manual walkthrough), **Pass criterion** (what counts as green). Severity per `agent_refs/validation/general.md`: **Mandatory** ⇒ ARIA / a11y mandatory check fail = `blocker`; **Recommended** ⇒ a11y recommended gap = `warning` (logged, never halts).

Manual walkthrough is a real validation level (general.md principle 4). Visual contrast, focus visibility, motion, and keyboard ergonomics are surfaced via `validation.requires_manual_walkthrough` events so the parent prompts the user before stage-6 sign-off (A11Y-17).

## Tools assumed available to validators

- `axe-core` (or `@axe-core/playwright`) for automated rule sweeps in stage-6 e2e validators.
- Playwright keyboard / focus assertions for scripted keyboard checks.
- A contrast helper (e.g., `wcag-contrast` npm package or a local computation against the foreground/background hex pairs declared in `frontend/src/styles.css`) for ratio assertions on the two themes.
- Manual walkthrough script: a numbered list the user (or a stage-6 reviewer) follows on a real localhost build; the parent emits `validation.requires_manual_walkthrough` when a check is in the manual-walkthrough subset.

## Checks

### A11Y-1 — Sidebar tree exposes ARIA tree semantics
- **Surface:** FR-15 recursive sidebar (`frontend/src/components/Sidebar.*` or equivalent).
- **WCAG ref:** 4.1.2 Name, Role, Value (Level A); ARIA Authoring Practices "Tree View" pattern.
- **Method:** Automated DOM assertion via Playwright + axe-core. Query `[role="tree"]` for the sidebar root; query `[role="treeitem"]` for every node; assert non-leaf nodes carry `aria-expanded="true|false"` matching their visual state. Exempt the top-level "Claude Settings & Shared Context" / "Projects" headings only if they are non-interactive container labels (in which case they get `role="group"` with an `aria-labelledby`).
- **Pass criterion:** every visible non-leaf node has `aria-expanded`; every leaf (file) has `role="treeitem"` without `aria-expanded`; `aria-selected` is set on the active node when one is open in the main pane.
- **Severity:** Mandatory.

### A11Y-2 — Breadcrumb is a navigation landmark with aria-current on the current crumb
- **Surface:** FR-16 breadcrumb above the main pane.
- **WCAG ref:** 2.4.8 Location (Level AAA, but breadcrumb-pattern best practice at AA); 1.3.1 Info and Relationships.
- **Method:** DOM assertion. The breadcrumb container is `<nav aria-label="Breadcrumb">`; the final crumb (current page) has `aria-current="page"` and is rendered as plain text (not an `<a>`).
- **Pass criterion:** axe-core reports no `aria-current` violations; manual screen-reader spot-check announces "current page".
- **Severity:** Mandatory.

### A11Y-3 — Keyboard navigation: focus tree, traverse, open
- **Surface:** FR-18 keyboard parity (`Ctrl/Cmd+Shift+E` focuses sidebar; arrows traverse; `Enter` opens).
- **WCAG ref:** 2.1.1 Keyboard (Level A); 2.1.2 No Keyboard Trap (Level A).
- **Method:** Playwright scripted run. (1) Press `Control+Shift+E` (and on macOS `Meta+Shift+E`); assert `document.activeElement` is inside the sidebar tree and matches `[role="treeitem"]`. (2) Press `ArrowDown`/`ArrowUp` four times; assert the active treeitem changes per ARIA tree pattern. (3) Press `Enter` on a file node; assert the main pane mounts that file (URL updates to `/file/<path>`). (4) Press `Tab` repeatedly from the focused tree; assert focus eventually exits the tree (no trap).
- **Pass criterion:** all four assertions hold on Chromium; A11Y-15 covers the macOS chord on Webkit when feasible.
- **Severity:** Mandatory.

### A11Y-4 — Visible focus indicator on every interactive element
- **Surface:** every focusable element across FR-15..FR-36 — sidebar treeitems, breadcrumb (none focusable), toolbar buttons (✎ Edit, Save, Discard, Close-editor), per-Q/A ✎ inline buttons, 📌 pin buttons, Build prompt buttons, Copy buttons, soft-wrap toggle, autonomous-mode toggle, module checkboxes, Save-error banner Reload button.
- **WCAG ref:** 2.4.7 Focus Visible (Level AA); 2.4.11 Focus Not Obscured (WCAG 2.2 Level AA, recommended).
- **Method:** Scripted manual walkthrough — tab through the page, screenshot focus state on each control. Automated axe-core does NOT cover visual focus rings; this is a `validation.requires_manual_walkthrough` event.
- **Pass criterion:** every focused control has a focus ring with at least 3:1 contrast against the adjacent background, and the ring is not clipped by parent overflow.
- **Severity:** Mandatory.

### A11Y-5 — Icon-only buttons (✎, 📌, Save, Discard, Close, Copy) carry accessible names
- **Surface:** FR-25 toolbar; FR-30 per-Q/A inline edit; FR-33 Copy button; FR-35 📌 pin toggle; FR-26 Discard / Close.
- **WCAG ref:** 4.1.2 Name, Role, Value (Level A); 2.5.3 Label in Name (Level A).
- **Method:** axe-core `button-name` rule + DOM assertion that every `<button>` matching `[aria-label]` has a non-empty value, OR has visible text content (not just an icon glyph).
- **Pass criterion:** axe-core reports zero `button-name` failures; every icon-only button has either `aria-label="Edit"` / `"Pin"` / etc. or a `<span class="sr-only">` companion.
- **Severity:** Mandatory.

### A11Y-6 — Editor textarea has a programmatic label
- **Surface:** FR-25 editor textarea.
- **WCAG ref:** 1.3.1 Info and Relationships (Level A); 3.3.2 Labels or Instructions (Level A).
- **Method:** DOM assertion — the `<textarea>` carries `aria-labelledby` pointing to the file-pane title (filename) OR an `aria-label` containing the filename.
- **Pass criterion:** screen reader announces the filename as the textarea label; axe-core reports no `label` violation.
- **Severity:** Mandatory.

### A11Y-7 — Dirty indicator is announced
- **Surface:** FR-27 dirty dot `●` in toolbar + `*` in `document.title`.
- **WCAG ref:** 4.1.3 Status Messages (Level AA).
- **Method:** DOM assertion + scripted manual walkthrough. The toolbar dot has `role="status"` (or sits inside a region with `aria-live="polite"`) and an accessible name like `aria-label="Unsaved changes"`. The `document.title` change is naturally announced by screen readers on title-change.
- **Pass criterion:** when the user types into the editor, the dirty status is announced within 1s without stealing focus; the title shows `*` prefix.
- **Severity:** Mandatory.

### A11Y-8 — Save-error banner uses role="alert"
- **Surface:** FR-28 persistent inline save-error banner above the textarea.
- **WCAG ref:** 4.1.3 Status Messages (Level AA); 3.3.1 Error Identification (Level A).
- **Method:** DOM assertion — the banner has `role="alert"` (which implies `aria-live="assertive"` and `aria-atomic="true"`). Confirmed via axe-core + screen-reader manual spot-check.
- **Pass criterion:** when a `PUT /api/file` returns 5xx and the banner mounts, NVDA / VoiceOver / Narrator announce the error text immediately; the banner persists (NOT a toast — toasts are explicitly forbidden mid-recovery per FR-28).
- **Severity:** Mandatory.

### A11Y-9 — Stale-write conflict banner has a focusable Reload button
- **Surface:** FR-29 conflict banner (`409 stale_write` response).
- **WCAG ref:** 2.1.1 Keyboard (Level A); 4.1.3 Status Messages (Level AA).
- **Method:** Playwright scripted run — simulate a stale-write 409 (set `If-Unmodified-Since` to a stale value); assert the banner mounts with `role="alert"`; tab to the Reload button; assert it is focusable; press Enter; assert the file reloads and the editor content updates.
- **Pass criterion:** keyboard-only user can recover from a stale-write conflict end-to-end.
- **Severity:** Mandatory.

### A11Y-10 — Copy button label flip is announced via aria-live="polite"
- **Surface:** FR-33(d) Copy button — label flips to "Copied!" for ~1.5s.
- **WCAG ref:** 4.1.3 Status Messages (Level AA); 3.2.2 On Input (Level A — no context change).
- **Method:** DOM assertion + scripted manual walkthrough. The Copy button (or a sibling status node) has `aria-live="polite"`; the label change is wrapped in a node that announces "Copied" without stealing focus. The button has a fixed `min-width` so the layout does NOT shift when the label flips (FR-33d explicit), which preserves focus position.
- **Pass criterion:** screen reader announces "Copied" within 500 ms of the click; no focus shift; layout-shift score < 0.01 on the click frame.
- **Severity:** Mandatory.

### A11Y-11 — Dark `<pre>` carve-outs meet WCAG AA contrast
- **Surface:** NFR-16 carve-outs — `.regen-prompt-block pre`, `.markdown-view pre`, `.code-view pre` (FR-19, FR-22, FR-33d/e). Per `agent_refs/project/development.md`, these dark surfaces are unconditional (NOT gated on `prefers-color-scheme: dark`) and MUST be validated for contrast.
- **WCAG ref:** 1.4.3 Contrast (Minimum) — 4.5:1 for body text, 3:1 for large text (Level AA).
- **Method:** Compute the contrast ratio from the hex colors declared in `frontend/src/styles.css`. If the regen-prompt body is `color: #c9d1d9` on `background: #0d1117`, the ratio is ~12.6:1 — passes. The validator reads the active palette and asserts every text-on-background pair inside the dark `<pre>` reaches 4.5:1 minimum. Syntax-highlighted tokens (rehype-highlight default theme) get a separate sweep against the same background.
- **Pass criterion:** every foreground/background pair in dark carve-outs is ≥ 4.5:1 for body text and ≥ 3:1 for code-comment / muted tokens; if any token fails, raise the issue with the exact pair.
- **Severity:** Mandatory.

### A11Y-12 — Light-theme app chrome contrast
- **Surface:** NFR-16 light theme — `body`, sidebar text on sidebar background, toolbar buttons on toolbar background, breadcrumb link text, modal/banner text. Excludes the dark carve-outs from A11Y-11.
- **WCAG ref:** 1.4.3 Contrast (Minimum) — 4.5:1 for body text, 3:1 for large text (Level AA); 1.4.11 Non-text Contrast — 3:1 for UI component boundaries (Level AA).
- **Method:** Compute contrast for every chrome text/background pair declared in `frontend/src/styles.css`. Run axe-core `color-contrast` rule on a rendered page in CI.
- **Pass criterion:** every chrome pair ≥ 4.5:1 (body) / ≥ 3:1 (large or UI-component); axe-core reports zero `color-contrast` failures on the light theme.
- **Severity:** Mandatory.

### A11Y-13 — QaView color-block tints have non-color cues
- **Surface:** FR-20 — Q tinted blue, A tinted green, category badge. Color is one channel of differentiation; it MUST NOT be the only one.
- **WCAG ref:** 1.4.1 Use of Color (Level A).
- **Method:** DOM assertion + visual inspection. Each Q block carries an `aria-label` or visible "Q:" / "Question" prefix; each A block carries "A:" / "Answer". The category badge is a labeled chip with text, not a colored dot only. Optionally, an icon (❓ for Q, 💬 for A) provides a redundant non-color cue — the requirement is that *some* non-color cue exists, not which one.
- **Pass criterion:** a user with Achromatopsia (or a forced-colors-mode walkthrough — see A11Y-16) can still tell Q from A without relying on hue; axe-core has no specific rule for this, so the check is a scripted manual walkthrough.
- **Severity:** Mandatory.

### A11Y-14 — Soft-wrap toggle in regen-prompt header is a labeled checkbox
- **Surface:** FR-33(d) "Wrap" toggle in the regen-prompt-block header bar.
- **WCAG ref:** 4.1.2 Name, Role, Value (Level A); 1.3.1 Info and Relationships (Level A).
- **Method:** DOM assertion — the toggle is `<input type="checkbox">` (or `role="switch"` with `aria-checked`) with an associated `<label>` reading "Soft wrap" / "Wrap". Default ON per FR-33d.
- **Pass criterion:** axe-core reports no label violation; keyboard user can toggle with Space; screen reader announces state change.
- **Severity:** Mandatory.

### A11Y-15 — prefers-reduced-motion respected in transitions
- **Surface:** Copy → "Copied!" 1.5s flip (FR-33d), any Edit/View toggle transition, sidebar expand/collapse animation if present.
- **WCAG ref:** 2.3.3 Animation from Interactions (Level AAA, but recommended at AA for vestibular safety).
- **Method:** CSS / scripted walkthrough. Run with the OS / DevTools `prefers-reduced-motion: reduce` emulation; assert no opacity / transform animations exceeding 200 ms; instant state swaps are fine. The Copy label still flips for 1.5s but as an instant text swap, not a fade.
- **Pass criterion:** under `prefers-reduced-motion: reduce`, no animation > 200 ms ms duration runs; the Copy label still announces "Copied" via aria-live (A11Y-10).
- **Severity:** Recommended (warning if violated; the spec does not mandate animations of any kind, so the more frequent failure is "we added one and forgot to gate it").

### A11Y-16 — Forced-colors mode (Windows High Contrast / contrast-more) usability
- **Surface:** every chrome and content surface; specifically the QaView color tints (A11Y-13), the sidebar selection state, the dirty dot, the focus rings, the dark `<pre>` carve-outs.
- **WCAG ref:** 1.4.11 Non-text Contrast (Level AA); 1.4.1 Use of Color (Level A).
- **Method:** Scripted manual walkthrough in Windows High Contrast (Edge / Chromium honor `forced-colors: active`). The light-theme rule does NOT prevent forced-colors override — the user agent rewrites colors regardless of `color-scheme: light`. The validator checks: (a) sidebar text remains readable; (b) selected treeitem is distinguishable via something other than color (an outline / border survives forced-colors); (c) focus rings remain visible; (d) the dark `<pre>` carve-outs accept the forced palette without clipping content.
- **Pass criterion:** forced-colors walkthrough completes the primary flows (browse, edit, build prompt, copy) without any unreadable surface.
- **Severity:** Mandatory (forced-colors is a legal accessibility floor on Windows).

### A11Y-17 — Manual walkthrough event surfaces visual-only checks
- **Surface:** A11Y-4 (focus visibility), A11Y-7 (dirty announcement), A11Y-13 (QaView non-color cue), A11Y-15 (reduced motion), A11Y-16 (forced colors), A11Y-20 (200% zoom).
- **WCAG ref:** N/A (process check; flows from `agent_refs/validation/general.md` principle 4).
- **Method:** The stage-6 validator emits a `validation.requires_manual_walkthrough` event into `events.jsonl` for each check in the manual subset, with a numbered checklist payload the user follows on the running localhost build. The event MUST surface BEFORE stage-6 sign-off; missing event ⇒ the validation level "didn't run" per general.md principle 5.
- **Pass criterion:** every manual-subset check has a corresponding event with the user's pass/fail recorded; `validation.pass` for the level is only emitted after every walkthrough check is green.
- **Severity:** Mandatory (a missing manual-walkthrough event is treated as a failed level run, not as "not yet checked").

### A11Y-18 — Headings hierarchy is in order
- **Surface:** every page rendered by the SPA — `/file/<path>`, `/project/{type}/{name}`, root.
- **WCAG ref:** 1.3.1 Info and Relationships (Level A); 2.4.6 Headings and Labels (Level AA).
- **Method:** axe-core `heading-order` and `page-has-heading-one` rules; DOM assertion that there is exactly one `<h1>` per page (the page title) and that heading levels do not skip downward (h1 → h3 with no h2 is a fail unless wrapped in a labeled section).
- **Pass criterion:** axe-core reports zero heading-order violations; one and only one `<h1>` per route.
- **Severity:** Mandatory.

### A11Y-19 — Landmark regions are present and labeled
- **Surface:** FR-15 sidebar, FR-16 breadcrumb area, FR-19..FR-24 main file pane, FR-25 editor toolbar.
- **WCAG ref:** 1.3.1 Info and Relationships (Level A); 4.1.2 Name, Role, Value (Level A).
- **Method:** axe-core `region` and `landmark-unique` rules. The page has: `<nav aria-label="File tree">` for the sidebar, `<nav aria-label="Breadcrumb">` for the breadcrumb (already covered in A11Y-2), `<main>` for the file pane, `<header>` (or `role="toolbar"` with `aria-label`) for the editor toolbar.
- **Pass criterion:** axe-core reports no region violations; every primary section is inside a labeled landmark; no two landmarks share an `aria-label`.
- **Severity:** Mandatory.

### A11Y-20 — 200% zoom usability
- **Surface:** every page; specifically the breadcrumb, toolbar, editor textarea, regen-prompt-block.
- **WCAG ref:** 1.4.4 Resize Text (Level AA); 1.4.10 Reflow (Level AA).
- **Method:** Scripted manual walkthrough — set browser zoom to 200%; assert no horizontal scroll on a 1280×800 viewport (1.4.10 reflow at 320 CSS pixels); assert toolbar buttons remain visible (do not get clipped behind a fixed sidebar); assert textarea wraps text instead of overflowing.
- **Pass criterion:** primary flows (browse, edit, build prompt, copy) still complete at 200% zoom without horizontal scrolling at 1280-CSS-pixel viewport width.
- **Severity:** Mandatory.

### A11Y-21 — Promotion (📌) toggle has accessible state
- **Surface:** FR-35..FR-36 — 📌 toggle next to each pinnable atomic item (Q/A, FR-NN / NFR-NN / AC-NN / SYS-NN, recommendation bullet); pin indicator on already-pinned items.
- **WCAG ref:** 4.1.2 Name, Role, Value (Level A).
- **Method:** DOM assertion — the toggle is `<button role="switch" aria-checked="true|false" aria-label="Pin <item-id>">` (or equivalent). The pin indicator shown after promotion (FR-36) is announced via `aria-label` like "Pinned to validation/promoted.md".
- **Pass criterion:** axe-core reports no aria-allowed-attr / role-has-required-aria-props violations; screen-reader user can promote and unpin items end-to-end without sighted help.
- **Severity:** Mandatory.

### A11Y-22 — Module checkbox lists in regen panels are grouped and labeled
- **Surface:** FR-31 per-stage Regenerate `<details>` panel; FR-32 project-page master Regenerate panel.
- **WCAG ref:** 1.3.1 Info and Relationships (Level A); 4.1.2 Name, Role, Value (Level A).
- **Method:** DOM assertion — the checkbox group is wrapped in `<fieldset>` with a `<legend>` like "Modules" (or a `role="group"` with `aria-labelledby`). Each `<input type="checkbox">` has an associated `<label>` with the module name.
- **Pass criterion:** axe-core reports no label / fieldset violations; screen reader announces the group label before each checkbox.
- **Severity:** Mandatory.

### A11Y-23 — Recommended: skip-to-main-content link
- **Surface:** root layout (every route).
- **WCAG ref:** 2.4.1 Bypass Blocks (Level A) — typically satisfied by landmarks (A11Y-19), but a skip-link is best practice for keyboard-only users facing a deep sidebar.
- **Method:** DOM assertion — a `<a href="#main">Skip to main content</a>` is the first focusable element on the page; activating it moves focus to the main pane.
- **Pass criterion:** Tab once from page load → focus is on the skip link; press Enter → focus jumps to `<main>`.
- **Severity:** Recommended (warning if absent — landmarks already satisfy 2.4.1, but the skip-link improves the keyboard-only ergonomics noticeably).

### A11Y-24 — Recommended: respect prefers-contrast: more
- **Surface:** entire SPA.
- **WCAG ref:** 1.4.6 Contrast (Enhanced) — Level AAA, but recommended via `prefers-contrast: more` user query.
- **Method:** CSS check — when `@media (prefers-contrast: more) { ... }` is active, chrome contrast pairs reach 7:1 for body text and 4.5:1 for large text.
- **Pass criterion:** under `prefers-contrast: more` emulation, every chrome pair reaches AAA contrast; if no media query is implemented, the existing AA contrast (A11Y-12) carries (warning, not blocker).
- **Severity:** Recommended.

### A11Y-25 — Error pages and 404 / 403 / 413 / 415 / 409 responses are labeled
- **Surface:** FR-4 (404, 415, 413), FR-7b (409), FR-9 (403), FR-12 (413). When the SPA receives any of these from `GET /api/file` or `PUT /api/file`, it surfaces an inline banner.
- **WCAG ref:** 3.3.1 Error Identification (Level A); 4.1.3 Status Messages (Level AA).
- **Method:** Playwright — for each error code, induce the response (e.g., `GET /api/file?path=does-not-exist` → 404; `GET /api/file?path=foo.svg` → 415; `PUT /api/file` 1.5 MB → 413). Assert the banner is `role="alert"` and contains both the error class (`stale_write`, `too_large`, `forbidden_origin`) and a human-readable explanation.
- **Pass criterion:** every error code produces an alert banner with `role="alert"` and a clear cause + next step (e.g., 409 → "Reload?" button per A11Y-9).
- **Severity:** Mandatory.

## Severity summary

| Severity | Count |
|---|---|
| Mandatory (blocker on fail) | 22 |
| Recommended (warning on fail) | 3 |

Manual-walkthrough subset (per A11Y-17): A11Y-4, A11Y-7, A11Y-13, A11Y-15, A11Y-16, A11Y-20.

## Audit hooks

Per `agent_refs/validation/general.md` principle 5, every level run MUST emit:

- `validation.started` with `level=accessibility` at the top of the run.
- One `validation.issue.raised` per failed check (or `validation.requires_manual_walkthrough` for the manual subset awaiting user confirmation).
- `validation.pass` only when (a) every Mandatory check is green AND (b) every manual-walkthrough check has a recorded user pass.

A level run with no audit events is treated as if it didn't run.
