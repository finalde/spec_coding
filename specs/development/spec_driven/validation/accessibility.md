# Validation level — Accessibility

Stage: 5 (Validation strategy) — clean-state regeneration
Run: spec_driven-20260503-030434 (autonomous full-pipeline)
Source spec: `specs/development/spec_driven/final_specs/spec.md`
Anchored requirements: NFR-14, NFR-15, NFR-16 plus implicit a11y claims throughout FRs.

Pre-reading consulted:
- `C:/workspace/spec_coding/.claude/skills/agent_team/playbooks/validation.md`
- `C:/workspace/spec_coding/.claude/agent_refs/validation/general.md`
- `C:/workspace/spec_coding/.claude/agent_refs/validation/development.md`

Severity policy (from `agent_refs/validation/general.md`):
- ARIA / mandatory a11y check fail = `blocker` (standard 3-revision-round cap).
- A11y "Recommended" gap = `warning` (logged; never halts).
- Manual-walkthrough items emit `validation.requires_manual_walkthrough` per principle #4.

Scope of automation: cases A11Y-01 through A11Y-16 are automatable via Playwright + `@axe-core/playwright` and DOM snapshot assertions. A11Y-17 is a manual-walkthrough pass — visual hierarchy, focus visibility under real keyboard input, motion/animation perceptibility — which axe alone cannot certify.

---

## A11Y-01 — Sidebar keyboard navigation (Tab / Enter / Esc)

- **WCAG criterion:** 2.1.1 Keyboard (Level A); 2.4.3 Focus Order (Level A).
- **Anchors:** NFR-14, FR-16, FR-17.
- **Setup:** Boot the app at `http://127.0.0.1:8765/`. Wait for `data-testid="sidebar"`.
- **Steps:**
  1. Press `Tab` repeatedly from page load. Tab order MUST traverse: skip-to-main link → sidebar root → each tree node in document order → main pane.
  2. With focus on a collapsible tree node, press `Enter` — the node MUST toggle expanded/collapsed.
  3. With focus on a leaf, press `Enter` — the leaf MUST navigate (URL becomes `/file/<rel>`).
  4. With focus on an expanded node, press `Esc` — the node MUST collapse (or, equivalently, focus returns to its parent without losing the tree's expanded ancestors).
- **Expected:** every assertion above true; `consoleErrors === []`.
- **Severity if fail:** `blocker` (mandatory keyboard support).

## A11Y-02 — Skip-to-main-content link

- **WCAG criterion:** 2.4.1 Bypass Blocks (Level A).
- **Anchors:** NFR-14 (implicit).
- **Setup:** Load `/`.
- **Steps:**
  1. Press `Tab` once. The first focusable element MUST be a "Skip to main content" link (visible on focus, may be visually-hidden until focus).
  2. Press `Enter`. Focus MUST move to the `<main>` element (or the first focusable child therein); URL MAY include `#main`.
- **Expected:** link is reachable as the first tab stop; activating it skips past the sidebar.
- **Severity if fail:** `blocker`.

## A11Y-03 — Sidebar tree uses native semantics

- **WCAG criterion:** 4.1.2 Name, Role, Value (Level A); 1.3.1 Info and Relationships (Level A).
- **Anchors:** NFR-15, FR-16.
- **Setup:** Inspect the rendered sidebar DOM.
- **Steps:**
  1. Assert the sidebar root uses either nested `<ul><li>` markup OR `role="tree"` with `role="treeitem"` children. NO `<div>`-soup.
  2. Each leaf MUST be focusable via keyboard alone (verified by Tab traversal in A11Y-01).
  3. Expand/collapse state MUST be conveyed via `aria-expanded` on parent nodes (or implied by `<details>` if used).
- **Expected:** axe-core rule `aria-required-children` and `list` pass without violations.
- **Severity if fail:** `blocker` for missing roles; `warning` if `aria-expanded` is missing on otherwise-correct structure.

## A11Y-04 — Breadcrumb semantics and aria-current

- **WCAG criterion:** 1.3.1 Info and Relationships (Level A); 4.1.2 Name, Role, Value (Level A).
- **Anchors:** NFR-15 (implicit), FR-15 (route → breadcrumb).
- **Setup:** Navigate to `/file/specs/development/spec_driven/interview/qa.md`.
- **Steps:**
  1. Assert a `<nav aria-label="Breadcrumb">` element exists ABOVE the main pane.
  2. Children form an ordered list (`<ol>`) of links; the LAST item MUST carry `aria-current="page"` and MAY be a non-link span.
- **Expected:** axe-core rule `aria-valid-attr-value` passes; manual DOM assert.
- **Severity if fail:** `blocker`.

## A11Y-05 — Editor toolbar uses native buttons; Save remains focusable on error

- **WCAG criterion:** 4.1.2 Name, Role, Value (Level A); 2.1.1 Keyboard (Level A).
- **Anchors:** FR-25, FR-27, NFR-14.
- **Setup:** Open any `.md` file; click ✎ Edit.
- **Steps:**
  1. Assert toolbar controls are `<button>` elements (not `<div role="button">`): ✎ Edit, **Save**, **Discard**, **Close editor**.
  2. Tab order is left-to-right matching DOM order.
  3. Inject a save failure (mock `PUT /api/file` to return 500). After the save-error banner appears, assert **Save** is still in the focusable set (`document.activeElement` can land on it via Tab) AND `disabled` attribute is NOT set.
- **Expected:** Save remains focusable so a keyboard-only user can retry without a mouse.
- **Severity if fail:** `blocker` (FR-25 is explicit on this).

## A11Y-06 — Editor dirty-dot has accessible name

- **WCAG criterion:** 1.3.1 Info and Relationships (Level A); 4.1.2 Name, Role, Value (Level A).
- **Anchors:** FR-26, NFR-15.
- **Setup:** Open a `.md` file in edit mode; type one character.
- **Steps:**
  1. Assert the dirty-dot element carries `aria-label="unsaved changes"` (or equivalent: `role="status"` with a sr-only text node, or `<span class="sr-only">unsaved changes</span>` accompanying the visual dot).
  2. Erase the character so content matches last-saved; the accessible name MUST disappear (the dot is removed, not just visually hidden).
- **Expected:** screen-reader users learn dirty state without sight.
- **Severity if fail:** `blocker`.

## A11Y-07 — Save error banner uses role="alert"

- **WCAG criterion:** 4.1.3 Status Messages (Level AA).
- **Anchors:** FR-27, NFR-15.
- **Setup:** Open a `.md` file in edit mode; mock `PUT /api/file` → 500.
- **Steps:**
  1. Click **Save**. Assert the banner element carries `role="alert"` (or `aria-live="assertive"` with `aria-atomic="true"`).
  2. Banner text matches the FR-27 template: `Could not save: <message>`.
  3. The textarea content is unchanged after the failure (FR-27 cross-check).
- **Expected:** screen readers immediately announce the error.
- **Severity if fail:** `blocker` (NFR-15 calls this out explicitly).

## A11Y-08 — Q/A view: semantic landmarks and pencil aria-labels

- **WCAG criterion:** 4.1.2 Name, Role, Value (Level A); 1.3.1 Info and Relationships (Level A).
- **Anchors:** FR-29, FR-30.
- **Setup:** Navigate to `/file/specs/development/spec_driven/interview/qa.md`. Assert `data-testid="qa-view"` is mounted.
- **Steps:**
  1. Each Round renders as a section with an `<h2>`; each category renders with an `<h3>`; Q and A blocks are within `<article>` or `<section>` with appropriate aria labels (e.g., `aria-label="Question"`/`aria-label="Answer"`).
  2. Each Q's ✎ pencil button MUST carry `aria-label="Edit question"`.
  3. Each A's ✎ pencil button MUST carry `aria-label="Edit answer"`.
  4. Pencil buttons are focusable via Tab in document order.
- **Expected:** axe-core `button-name` rule passes; manual DOM assertions for labels match.
- **Severity if fail:** `blocker`.

## A11Y-09 — Regenerate panel native semantics; Wrap is a labeled checkbox

- **WCAG criterion:** 1.3.1 Info and Relationships (Level A); 4.1.2 Name, Role, Value (Level A).
- **Anchors:** FR-33, NFR-15.
- **Setup:** Open a stage file, e.g. `/file/specs/development/spec_driven/interview/qa.md`.
- **Steps:**
  1. Assert the Regenerate panel is a `<details>` with a `<summary>` titled "Regenerate" (default-collapsed per AC-22).
  2. Module rows are `<input type="checkbox">` elements with associated `<label for="...">` (or wrapped-label) text matching the module label.
  3. The "Autonomous mode" toggle is a labeled `<input type="checkbox">`.
  4. Inside the assembled-prompt block (after Build), the **Wrap** toggle is a labeled `<input type="checkbox">` (NOT a `<button>` with `aria-pressed`); its label reads "Wrap" and is `for=`-associated to the input.
- **Expected:** axe-core `label` rule passes; native semantics throughout.
- **Severity if fail:** `blocker` for missing labels; `warning` if a button-with-`aria-pressed` is used in place of `<details>`/`<summary>` (still accessible, but deviates from FR-33 contract).

## A11Y-10 — Copy button: aria-live="polite" and stable width

- **WCAG criterion:** 4.1.3 Status Messages (Level AA); 1.4.10 Reflow (Level AA, related — no layout shift).
- **Anchors:** FR-33(f), AC-24.
- **Setup:** Open a stage file; click Build prompt; locate the Copy button.
- **Steps:**
  1. Assert the Copy button element carries `aria-live="polite"`.
  2. Measure `getBoundingClientRect().width` BEFORE click (label "Copy") and AFTER click during the ~1500 ms "Copied!" window. Width MUST be identical (within 1 px tolerance) — a fixed `min-width` prevents layout-shift.
  3. After ~1500 ms the label flips back to "Copy"; width unchanged.
- **Expected:** screen reader announces the "Copied!" change; sighted users see no layout shift.
- **Severity if fail:** `blocker` for missing `aria-live`; `warning` for measurable width drift (still announces correctly, just visually janky).

## A11Y-11 — Color contrast on dark code-block theme

- **WCAG criterion:** 1.4.3 Contrast (Minimum) (Level AA).
- **Anchors:** NFR-16.
- **Setup:** Build a regen prompt; measure foreground/background of the `<pre>` body and the surrounding `regen-prompt-block` border, header bar, and header-bar text.
- **Steps:**
  1. Run `@axe-core/playwright` with the `color-contrast` rule on the page; collect violations scoped to `.regen-prompt-block` and any `<pre>` rendered by `shiki`.
  2. Sample shiki theme tokens (keyword, string, comment) against the chosen background; compute contrast ratio. Body text MUST be ≥ 4.5:1; large text (≥18pt or 14pt bold) MUST be ≥ 3:1.
  3. The "Wrap" label, "Copy" button label (both states), and breakdown line MUST pass AA against their backgrounds.
- **Expected:** zero `color-contrast` violations from axe in the assembled-prompt region.
- **Severity if fail:** `blocker` (NFR-16 is explicit on AA).

## A11Y-12 — Visible focus outline on every interactive control

- **WCAG criterion:** 2.4.7 Focus Visible (Level AA).
- **Anchors:** NFR-14.
- **Setup:** Tab through the app from a fresh load; visit the sidebar, breadcrumb, editor toolbar (in edit mode), Q/A pencils, Regenerate panel, Copy/Wrap controls.
- **Steps:**
  1. For each focused element, capture computed `outline-style`, `outline-width`, `outline-color`, `box-shadow` (focus rings sometimes emulated). Assert at least one of: outline ≠ `none`/0px, OR `box-shadow` includes a non-transparent ring with ≥ 2px spread.
  2. The focus ring MUST meet 3:1 contrast against its adjacent background (per WCAG 2.4.11 Focus Appearance, AAA — but enforced as a NFR-14 floor here).
  3. NO global `*:focus { outline: none; }` style with no replacement; if present, fail.
- **Expected:** every interactive control shows a perceptible focus indicator.
- **Severity if fail:** `blocker` for any control with no indicator at all; `warning` if some controls' rings fall below 3:1 contrast but are still perceptible.

## A11Y-13 — Broken links: span, aria-disabled, focusable, title

- **WCAG criterion:** 4.1.2 Name, Role, Value (Level A); 1.3.1 Info and Relationships (Level A).
- **Anchors:** FR-24, AC-21.
- **Setup:** Open a markdown artifact containing a relative link to a non-existent file.
- **Steps:**
  1. Assert the broken-link node is a `<span class="link-broken" aria-disabled="true">` and NOT an `<a>` element.
  2. Assert it carries a `title="<cause>"` attribute (e.g., `file not found`).
  3. Assert it is in the focusable set (`tabindex="0"`) so screen-reader users can land on it and have the title narrated; pressing Enter MUST do nothing (no navigation).
  4. Hovering surfaces the tooltip in sighted UA.
- **Expected:** broken links are semantically distinct from working links and are perceivable to AT users.
- **Severity if fail:** `blocker` for using `<a>` (the user can mistakenly click and trigger nav); `warning` if the span is correct but lacks `tabindex="0"` (still perceivable on hover, but not focusable).

## A11Y-14 — Form controls have associated labels

- **WCAG criterion:** 1.3.1 Info and Relationships (Level A); 3.3.2 Labels or Instructions (Level A); 4.1.2 Name, Role, Value (Level A).
- **Anchors:** NFR-15 (implicit), FR-25, FR-30, FR-33.
- **Setup:** Walk every `<input>`, `<textarea>`, `<select>` rendered across: file editor textarea (FR-25), per-block Q/A textarea (FR-30), Regenerate-panel module checkboxes (FR-33a), Autonomous toggle (FR-33b), Wrap toggle (FR-33f).
- **Steps:**
  1. Run axe-core `label` rule on every page state above. Zero violations expected.
  2. Each control has EXACTLY ONE of: `<label for="...">` pointing to its `id`, wrapped-label, `aria-label`, or `aria-labelledby` referencing visible text. The textarea MUST have an accessible name (e.g., `aria-label="File content editor"` or `aria-label="Edit answer"`).
- **Expected:** every form control has a programmatically-associated name.
- **Severity if fail:** `blocker`.

## A11Y-15 — Reduced-motion respect on the assembled prompt block

- **WCAG criterion:** 2.3.3 Animation from Interactions (Level AAA, but enforced as a floor here per NFR-14 spirit).
- **Anchors:** FR-33(f), AC-24, NFR-14.
- **Setup:** Set OS / browser to honor `prefers-reduced-motion: reduce` (Playwright: `await page.emulateMedia({ reducedMotion: 'reduce' })`).
- **Steps:**
  1. Build a regen prompt. Assert no auto-running animations on the `regen-prompt-block` (no marquee, no auto-scrolling, no infinite spinners).
  2. Click **Copy**. The "Copy" → "Copied!" → "Copy" label flip MUST happen via direct text-content change OR a transition that is suppressed under `prefers-reduced-motion: reduce` (computed `transition-duration` ≤ 0.01s under the reduced-motion media query).
  3. The Wrap toggle changes `<pre>` layout instantly (no transitioned width/height).
- **Expected:** no motion that would violate `prefers-reduced-motion: reduce`.
- **Severity if fail:** `warning` (Recommended-tier; never halts) per the severity table — but log every violation.

## A11Y-16 — Promotion 📌 toggle: aria-pressed and aria-label

- **WCAG criterion:** 4.1.2 Name, Role, Value (Level A).
- **Anchors:** FR-36.
- **Setup:** Open `interview/qa.md`; hover a Q/A block to reveal the 📌 toggle.
- **Steps:**
  1. Assert the 📌 control is a `<button>` (NOT a `<div>` or `<span>`).
  2. Unpinned state: `aria-pressed="false"` AND `aria-label="Pin item"`.
  3. After click (pin succeeds): `aria-pressed="true"` AND `aria-label="Unpin item"`.
  4. The button is focusable via Tab and activatable via Enter or Space.
- **Expected:** screen-reader users can perceive the toggle's state and label.
- **Severity if fail:** `blocker` (a toggle with no `aria-pressed` is mute to AT).

## A11Y-17 — Manual walkthrough pass

Emits `validation.requires_manual_walkthrough` event per `agent_refs/validation/general.md` core principle #4. A human reviewer MUST visually confirm the items below; axe-core cannot certify any of them.

Checklist:

1. **Visual hierarchy** — sidebar section headers are visually distinct from leaves; Q tint (blue) and A tint (green) are perceivable but not the SOLE channel of meaning (the Q/A label text is also present, satisfying 1.4.1 Use of Color).
2. **Focus visibility under real keyboard input** — tab through the app on Windows + Chrome; confirm every control's focus ring is perceptible against its background under typical viewing conditions (not just synthetically passing 3:1 contrast in axe).
3. **Motion / animation perceptibility** — confirm the Copy button's "Copied!" flip is noticeable but not jarring; with reduced-motion preference enabled, confirm no animations run.
4. **Screen reader sanity check** — drive the app with NVDA (Windows) for ≥ 5 minutes through the primary journeys (browse → render Q/A → edit a Q → build a regen prompt → pin an item). Note any control whose announced name is misleading or empty.
5. **High-contrast / forced-colors mode** — switch Windows to High Contrast (forced-colors media query). Confirm no critical UI element vanishes (broken-link spans should remain perceivable; focus rings should remain).
6. **Zoom to 200%** — per WCAG 1.4.4 Resize Text. Confirm no content is clipped or requires two-axis scrolling at 200% zoom on a 1280px-wide viewport.
7. **`prefers-reduced-motion` end-to-end** — flip the system preference; replay the Copy button + the Wrap toggle + any other transitions. Confirm A11Y-15 holds in real conditions.
8. **Tooltip accessibility for broken links** — confirm the `title` tooltip surfaces under hover AND keyboard focus (some browsers omit `title` on focus; if so, log as `warning` and propose `aria-describedby` instead in a follow-up).

Manual-walkthrough severity policy:
- Items 1, 2, 4, 5 failing on their golden path → `blocker` (mandatory a11y).
- Items 3, 6, 7, 8 failing → `warning` (logged; never halts).

The reviewer records pass/fail per item in the validation event log and emits a single `validation.requires_manual_walkthrough` event with the checklist results inline (or a path to the per-item notes).

---

## Cross-cutting notes

- **Tooling:** `@axe-core/playwright` is the automated baseline; manual checks layer on top per A11Y-17. Running `axe.run()` on every page state visited by the e2e suite is cheap and catches regressions outside the explicit cases here.
- **No silent-pass:** every case above MUST emit either `validation.pass` or `validation.issue.raised`. A case that ran without an event is treated as if it didn't run (per general.md principle #5).
- **Pin preservation:** none of the a11y cases here change the pin-preservation contract; they live alongside it. If `validation/promoted.md` exists at regen time, those pins are inlined verbatim above (this run has no validation pins as of writing).
- **Out-of-scope for v1:** WCAG 2.4.11 Focus Appearance (AAA) is partially enforced via A11Y-12's 3:1 ring-contrast floor but not as a strict AAA pass. Full AAA conformance is deferred.
