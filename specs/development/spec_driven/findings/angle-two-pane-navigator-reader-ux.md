# Research angle — Two-pane navigator + reader UX

Stage 3 / spec_driven-20260503-fullregen / researcher-two-pane

## Scope

`spec_driven`'s primary surface is a **left sidebar tree + main content pane**. The sidebar holds two top-level groups (`Claude Settings & Shared Context`, `Projects/{type}/{name}`) and exposes per-stage subtrees. The main pane renders the selected file (Markdown rendered, YAML/JSON syntax-highlighted, or the structured `qa.md` view), or an empty-state with a regen panel for not-yet-generated artifacts.

This research nails down **concrete v1 component behavior** for the navigator and the reader by comparing six well-known two-pane viewers and the W3C ARIA APG `treeview` pattern. The output is a set of recommendations the spec author can drop into FRs without further research.

Out of scope for this angle: the editor's textarea behavior, save semantics, the structured Q/A block view, and the regen-prompt panel. Those live in sibling angles.

## Comparator matrix

| Comparator | Keyboard map (key actions) | Selection vs focus | Long-name handling | URL-as-state? | Tab stop model |
|---|---|---|---|---|---|
| **W3C ARIA APG TreeView** | Up/Down move focus; Right opens / moves to first child; Left closes / moves to parent; Enter activates; Home / End jump to first / last visible node; type-ahead jumps. | Distinct: DOM focus is the active node; `aria-selected` (or `aria-current` for nav trees) is independent. Selection MAY follow focus in single-select but isn't required. | Pattern is presentational-agnostic, but the navigation example in APG renders truncation via host CSS; the pattern itself doesn't dictate ellipsis position. | The navigation-treeview example uses `aria-current="page"` synced to the URL. | **Roving tabindex**: only the current item has `tabindex="0"`, others `-1`. Tabbing into the tree lands on the current page. |
| **VS Code Explorer** | Up/Down move highlight; Right expands / steps into children; Left collapses / steps to parent; Enter opens file in editor; type-ahead filters; Ctrl+Alt+F opens Find inside Explorer. | Highlight = focus = "preview-open" target; "auto-reveal" auto-selects the file matching the active editor tab unless turned off (`explorer.autoReveal: false`). Active community discussion (issue #175690, #83639) about splitting *focus* and *selection* because cut/copy/paste act on the selected node, which currently couples to whatever the editor revealed. | End-truncation with native ellipsis; full path shown in tooltip on hover. | No — Explorer is in-memory state inside a desktop shell. (Web variants like vscode.dev hash-encode the workspace, but file selection is not part of the URL.) | Single conceptual selection; arrow keys move it. Behaves like a roving-focus list inside the panel — the panel is the tab stop; arrows don't escape it. |
| **JetBrains Project tool window** | Alt+1 focus the tool window; arrow keys traverse; Enter / F4 opens for edit; Esc returns focus to editor; type-ahead "Speed Search". | Selection and focus coincide on the highlighted row. Two named modes are exposed in the header gear: **Autoscroll to Source** (selecting a node opens the file) and **Autoscroll from Source** / **Always Select Opened File** (the editor's active file is auto-revealed in the tree). Both are off by default; users opt in. | End-truncation with ellipsis; full path in tooltip; case-sensitive Speed Search highlights matched substring. | No — desktop IDE; in-memory project model. | Tool window itself is a Tab destination; inside, arrows are the navigation model. |
| **GitHub repo file tree** | `t` opens fuzzy file finder over the whole repo; `y` rewrites the current URL to a permalinked SHA; arrow keys are NOT a documented file-tree primitive (their `←/→/↑/↓` shortcuts apply to the network graph, not the tree). | The current URL determines highlighted file/folder; selection follows the URL, not a separate in-memory selection. | End-truncation with ellipsis; hover tooltip shows full name. | **Yes — the URL is the source of truth.** `/owner/repo/blob/{ref}/{path}` and `/owner/repo/tree/{ref}/{path}` deep-link to a file or folder; refresh reproduces the same view. `y` canonicalises the ref to a SHA. | Standard tab order through visible links; not a roving-tabindex tree. Each row is a normal anchor. |
| **MkDocs Material sidebar** | Tab through links; Enter activates; arrow keys do native page-scroll, no tree-specific arrow handling. Anchor tracking syncs the URL hash to the active heading as you scroll the content pane. | Highlight follows the URL (`aria-current` semantics on the active link). No focus/selection split — there is one tab-stop-per-link model. | Long titles truncated with `.md-ellipsis` end-truncation; content-tooltips feature shows the full title on hover; known bug: tooltips on links inside collapsed sections only appear after expand. | **Yes** — page state is fully encoded in the URL path, in-page anchor in the hash. Refresh is lossless. | Single tab stop **per link** (every link is tabbable). Not a roving-tabindex tree — it's a nested `<nav>` of links and details/summary toggles. |
| **Storybook sidebar** | `s` toggles sidebar; `/` (or `Cmd/Ctrl+K`) opens fuzzy component finder; arrow keys traverse the sidebar list; Enter opens story; Alt+ArrowUp/Down jumps between stories (cause of the historic "sidebar jumps and you can't see what's selected" bug, issue #13040). | Highlight follows the URL (which story is open). Recently-opened list is in-memory. | End-truncation with ellipsis; full name in tooltip. | **Yes** — Storybook URLs encode the active story id (`?path=/story/<kind>--<name>`); deep-links work. | Sidebar rows are focusable; ongoing accessibility work (discussion #32189, issue #33041) is hardening the focus model — historically not a strict roving-tabindex tree. |
| **Backstage TechDocs sidebar** | Inherits MkDocs Material's keyboard model since TechDocs renders MkDocs output. Tab through links; Enter activates; native scrolling. | Highlight follows URL. Documented bugs: scroll position not reset on link click (#7145), content flash during navigation (#13696), sidebar doesn't collapse on small viewports (#8479). | End-truncation with ellipsis (inherited). | **Yes** — TechDocs uses MkDocs' URL-as-state model wrapped in Backstage routing; subdirectory deployments have caused breakage (#18441) when the base path is wrong. | Same single-tab-stop-per-link model as MkDocs Material. |

## Findings by behaviour

### Selection vs focus

The cleanest split in the literature is the W3C APG one: focus is *where keyboard events go*, selection is *what is currently chosen*, and they MAY couple but don't have to. JetBrains makes this user-visible by exposing "Autoscroll to Source" / "Autoscroll from Source" as separate settings. VS Code couples them by default and the community is asking for a split because operations like copy/paste act on the *selected* node — coupling means autoreveal silently changes the operation target.

For a **read+edit document viewer** (which is what spec_driven is), the simpler model wins: **selection = the currently-rendered file = the URL**. Focus is the keyboard cursor inside the tree and is allowed to wander without changing the rendered file; activation (Enter) commits a focus position into a selection / route change. This matches the APG navigation-treeview example exactly (`aria-current="page"` + roving tabindex with `tabindex="0"` on the current page).

### URL-as-state vs in-memory state

GitHub, MkDocs Material, Storybook, and Backstage TechDocs all encode "what is currently open" in the URL. VS Code and JetBrains, being desktop shells, keep it in memory. For a localhost web app whose users will paste links into chat to point teammates at a stage artifact, URL-as-state is non-negotiable: refresh, deep-link, and "share this view" all collapse to the same primitive.

### Keyboard model

APG's tree-view spec is the canonical contract: arrows for movement, Right/Left for expand/collapse, Enter for activate, Home/End for first/last, type-ahead for jumping. VS Code and JetBrains both implement this faithfully (with vendor-specific extras like Speed Search and Find-in-Explorer). MkDocs Material and Storybook deliberately *don't* implement a tree-keyboard model — they fall back to "every row is a link, tab through them" — which is acceptable for shallow navs but degrades on deep trees.

For spec_driven's tree (Settings/Agents/Skills, plus per-project per-stage subtrees), the depth is 4-5 levels; the APG keyboard model pays for itself.

### Tab stop / roving tabindex

The two viable models:

1. **Roving tabindex** (APG, VS Code, JetBrains): one element in the tree is `tabindex="0"`, the rest are `-1`; arrows move which is `0`; the whole tree is a single tab stop.
2. **All-links-tabbable** (MkDocs, Storybook, GitHub, Backstage): every row is a regular anchor; tab cycles through every visible row.

Roving tabindex is strictly better for deep trees because it lets the user Tab past the navigator quickly when they want to focus the reader. All-links-tabbable is friendlier for screen-reader users *only if* the tree is shallow and doesn't dynamically expand — which spec_driven's does.

### Long-name handling and ellipsis position

Every comparator surveyed uses **end-truncation with ellipsis** (CSS `text-overflow: ellipsis`) for the sidebar. None implement middle-ellipsis natively, because for a vertical sidebar the meaningful disambiguator is usually the leading folder name (e.g. `interview/` vs `findings/`).

But spec_driven has a known collision: paths like `follow_ups/001-20260502-095822-editable-webapp.md` and `follow_ups/002-20260503-...md` differ in the *middle* of the leaf node. Standard end-truncation collapses both to `001-20260502-095822-edita...` if the panel is narrow. CSS `text-overflow: ellipsis` cannot do middle-truncation; the canonical solution is a JS component (e.g. `react-truncate`'s `MiddleTruncate`) that measures and inserts an ellipsis between the prefix and the file extension. The MDN `text-overflow` page documents that two-value `text-overflow` is for line ends only (start + end); the CSSWG issue #3937 proposing a middle-ellipsis third value remains open.

The pragmatic recipe: **end-truncation by default for nav rows; middle-truncation specifically on `follow_ups/*.md` leaf labels**, where the date+slug pattern means the meaningful disambiguator is in the middle of the string and the `.md` extension at the tail is stable.

### Overflow handling beyond ellipsis

VS Code and JetBrains both expose horizontal scroll on the panel as a fallback when text doesn't fit, plus a hover tooltip with the full label. MkDocs Material adds tooltips on `.md-ellipsis`-truncated entries via the `content.tooltips` feature. For spec_driven, **always show a `title` attribute (or accessible-tooltip equivalent) carrying the full label** so the user can hover-disambiguate even when both end- and middle-truncation are insufficient.

### Breadcrumbs

None of the seven comparators makes breadcrumbs the primary surface — they're all either tree-only or tree+address-bar. GitHub gets the closest: above the file content it renders `repo / dir1 / dir2 / file.ext` as clickable segments, each segment a link to the corresponding tree URL. MkDocs renders breadcrumbs above the page content when configured (`navigation.path`), each segment linking to the parent section.

For spec_driven, the canonical breadcrumb above the reader pane should be `<type> / <name> / <stage> / <file>` (e.g. `development / spec_driven / interview / qa.md`), each segment a link to a route. This gives the user a redundant disambiguation channel when the sidebar is collapsed or scrolled.

### Behavior when the file doesn't exist yet

This is spec_driven-specific: the empty-state design ("Not yet generated — paste this prompt to produce it" with the regen panel mounted) is consistent with how Storybook treats stories that throw on render (sidebar entry remains, content pane shows the error/empty state) and how GitHub treats a 404 path (sidebar/breadcrumbs may still render, content shows the empty state). The pattern works because the route stays canonical even when the artifact isn't there yet — supporting copy-pasteable URLs.

## Recommendations for v1

1. **Adopt the W3C ARIA APG `tree` / `treeitem` pattern** for the sidebar. Roles: `role="tree"` on the outer list, `role="treeitem"` on each row, `role="group"` on each child container, `aria-expanded` on parent rows, `aria-current="page"` on the active leaf. Source: APG TreeView pattern + navigation-treeview example.

2. **Implement roving tabindex.** The current-page row carries `tabindex="0"`; every other row is `tabindex="-1"`. Arrow keys move the `0` and update DOM focus; the whole tree is a single tab stop so users can Tab past the navigator into the reader cheaply. (APG navigation-treeview, JetBrains, VS Code all use this.)

3. **Keyboard map (verbatim):**
   - `Up` / `Down` — move focus to previous / next visible row.
   - `Right` — on a closed parent, expand it (no focus move). On an open parent, move focus to first child. On a leaf, no-op.
   - `Left` — on an open parent, collapse it. On a closed parent or a leaf, move focus to its parent. On the root, no-op.
   - `Enter` — activate the focused row: navigate to its route (parent or leaf).
   - `Home` / `End` — focus first / last visible row.
   - Type-ahead — jump to next visible row whose label starts with the typed characters (debounce 500 ms).

4. **URL-as-state.** Routes:
   - `/settings/{claude-md|agents/<name>.md|skills/<path>/SKILL.md}`
   - `/project/{type}/{name}` (the project parent page)
   - `/project/{type}/{name}/{stage}/{filename}` (a specific artifact)

   The active route drives `aria-current="page"` on exactly one tree node. Refresh and deep-link are lossless. (GitHub, MkDocs Material, Storybook, Backstage TechDocs all do this.)

5. **Selection follows the URL, not focus.** Arrow-key navigation moves focus only; the route changes only on Enter or click. This avoids VS Code's open issue where autoreveal silently retargets cut/copy/paste, and matches APG's "selection MAY follow focus, but doesn't have to" — we deliberately uncouple them so a user can scroll the tree by arrows without fetching content for every row.

6. **End-truncation by default; middle-truncation for `follow_ups/*.md` leaves.** Standard rows: `overflow: hidden; text-overflow: ellipsis; white-space: nowrap;` plus `title=` carrying the full label. For `follow_ups/NNN-{date}-{slug}.md` rows specifically, render a JS-driven middle-truncation component (or a pre-computed `{prefix}…{slug}.md` server-side label that fits the panel's nominal width) so two follow-ups with shared timestamp prefixes remain visually distinguishable. (MDN `text-overflow`; CSSWG #3937; react-truncate `MiddleTruncate`.)

7. **Render breadcrumbs above the reader pane** (e.g. `development / spec_driven / interview / qa.md`), each segment a link to its route. Supplements the sidebar when the navigator is collapsed or scrolled. (GitHub-style.)

8. **Empty-state route is canonical.** When the URL points at a non-existent artifact, render the empty-state pane with the regen panel mounted — *do not* redirect. The route, the breadcrumb, and the sidebar's `aria-current` all stay consistent so the user can copy-paste the URL even before the artifact exists. (Matches the qa.md decision in the interview's `success-and-failure` category.)

## Sources

- [Tree View Pattern — W3C ARIA APG](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/)
- [Navigation Treeview Example — W3C ARIA APG](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/examples/treeview-navigation/)
- [Developing a Keyboard Interface — W3C ARIA APG](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/)
- [VS Code User Interface — Microsoft](https://code.visualstudio.com/docs/getstarted/userinterface)
- [Navigating VSCode's File Explorer Without a Mouse — Adam Tuttle](https://adamtuttle.codes/blog/2024/navigating-vscode-file-explorer-without-mouse/)
- [Separate explorer.autoReveal into 2 options — VS Code issue #175690](https://github.com/microsoft/vscode/issues/175690)
- [Add option to disable automatic selection on focus in explorer — VS Code issue #83639](https://github.com/microsoft/vscode/issues/83639)
- [Project tool window — JetBrains IntelliJ IDEA documentation](https://www.jetbrains.com/help/idea/project-tool-window.html)
- [Tool windows — JetBrains IntelliJ IDEA documentation](https://www.jetbrains.com/help/idea/tool-windows.html)
- [10 places you don't need to use the mouse in IntelliJ IDEA — JetBrains blog](https://blog.jetbrains.com/idea/2021/08/10-places-you-don-t-need-to-use-the-mouse-in-intellij-idea/)
- [GitHub keyboard shortcuts — GitHub docs](https://docs.github.com/en/get-started/accessibility/keyboard-shortcuts)
- [Setting up navigation — Material for MkDocs](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/)
- [Tooltips — Material for MkDocs](https://squidfunk.github.io/mkdocs-material/reference/tooltips/)
- [Feature suggestion: tooltip on overflowing nav items — mkdocs-material #3785](https://github.com/squidfunk/mkdocs-material/issues/3785)
- [Tooltip doesn't appear on links with ellipsis when inside collapsed nav sections — mkdocs-material #4026](https://github.com/squidfunk/mkdocs-material/issues/4026)
- [Storybook's new component finder and sidebar — Storybook blog](https://medium.com/storybookjs/new-component-finder-and-sidebar-3f47bd915cc8)
- [Keyboard navigation causes glitches in the sidebar — Storybook #13040](https://github.com/storybookjs/storybook/issues/13040)
- [Accessibility Roadmap — Storybook discussion #32189](https://github.com/storybookjs/storybook/discussions/32189)
- [TechDocs scroll position not reset on nav — Backstage #7145](https://github.com/backstage/backstage/issues/7145)
- [TechDocs flashing on navigation — Backstage #13696](https://github.com/backstage/backstage/issues/13696)
- [TechDocs side menu doesn't collapse on small devices — Backstage #8479](https://github.com/backstage/backstage/issues/8479)
- [text-overflow CSS property — MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/text-overflow)
- [Ellipsizing text in middle of string — CSSWG issue #3937](https://github.com/w3c/csswg-drafts/issues/3937)
- [MiddleTruncate — react-truncate documentation](https://truncate.js.org/reference/middle-truncate/)
- [aria-current — MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-current)
- [aria-selected — MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-selected)

## Open questions / not researched

- Drag-to-resize behaviour for the sidebar / reader split (no comparator deeply documents the keyboard story for resizers; recommend deferring to a sibling angle if the spec calls for keyboard-resizable panes).
- Mobile / narrow-viewport collapse behaviour (Backstage #8479 hints at the constraint; spec_driven is localhost-only and likely desktop-first, so this is parked).
- Screen-reader announcement copy on route change (the APG navigation-treeview moves focus to the new page's main heading; whether spec_driven should do the same is a stage-4 spec question, not a comparator-driven one).
- Search-across-artifacts UX (revised_prompt explicitly puts cross-artifact search out of scope; finder-style fuzzy search like Storybook's `/` or GitHub's `t` is therefore deferred).
- Exact CSS pixel widths for sidebar default / min / max (this is a spec/visual-design call, not something the comparators converge on; deferring to stage 4).
- "Auto-reveal active editor file" toggle (VS Code-style) — for spec_driven the URL drives selection so this question dissolves; flagging in case stage 4 wants to revisit.
