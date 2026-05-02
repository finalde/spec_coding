# Angle: Two-pane navigator + reader UX

This angle covers concrete v1 component behavior for spec_driven's left sidebar tree and right reader pane: how the sidebar tree should expand/collapse, how selection and keyboard focus relate, what to render in breadcrumbs, what keyboard map to wire up, and how to handle long filenames and overflow. The frame is "what should a small localhost spec viewer copy from production tools, and what should it skip?" — so the comparators below are limited to behaviors a single developer can implement on a Saturday with React + a tree library, not full-blown IDE telemetry. We compare six tools: VS Code Explorer, JetBrains "Project" tool window, GitHub's repo file tree, MkDocs Material sidebar, Storybook sidebar, and Backstage TechDocs sidebar — all anchored against the [W3C ARIA APG TreeView pattern](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/) since it is the canonical reference every other tool either implements or diverges from.

## The W3C reference (anchor)

The [APG Tree View pattern](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/) defines the keyboard contract every other comparator is measured against:

- Up/Down: move focus to previous/next visible node, do not open or close.
- Right: on a closed node, open it; on an already-open node, move to first child; on an end node, do nothing.
- Left: on an open node, close it; on a child or end node, move to parent.
- Home: first node in tree (no expand/collapse).
- End: last visible node in tree.
- Enter: activate the node (default action — for a navigator, that is "open the file in the reader").
- Type-ahead: focus moves to next node whose name starts with the typed character; search wraps.
- `*` (optional): expand all siblings at the current level.

The recommended **focus model is roving tabindex**: the tree itself is the single tab stop, exactly one `treeitem` carries `tabindex="0"`, every other carries `tabindex="-1"`, and arrow keys move both DOM focus and the tabindex marker. The [navigation treeview example](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/examples/treeview-navigation/) makes the convention explicit: the item matching `aria-current="page"` is the one that gets `tabindex="0"`, so when the user tabs back into the sidebar, focus lands on "where you are" rather than the top of the tree.

The pattern also distinguishes **selection** (`aria-selected`) from **focus** (the DOM-focused element). For navigator-style trees with single-select-follows-focus, the two are wired together; for trees that allow lasso-select (file managers, multi-select tag pickers), they are independent. spec_driven is squarely a navigator, so single-select-follows-focus is the right default.

## VS Code Explorer

VS Code's Explorer pane is the closest spiritual cousin of what spec_driven wants — it is a tree of file paths feeding a single editor pane on the right. Its keyboard map matches the APG pattern: arrows for traversal, Enter to open (but defaults to **rename** when focus is on a file in the Explorer, which is a famous papercut — keyboard users have to use `Cmd+Down` / `Ctrl+Enter` to actually open the file, see [Adam Tuttle's writeup](https://adamtuttle.codes/blog/2024/navigating-vscode-file-explorer-without-mouse/)). Type-ahead works in the tree.

The interesting wrinkle is `explorer.autoReveal`. By default it is `true`, which means opening a file via Quick Open (`Cmd+P`) or by clicking a tab causes the Explorer to scroll to that file *and* select it. Issue [microsoft/vscode#175690](https://github.com/microsoft/vscode/issues/175690) requested splitting this into two settings — "reveal but do not select" — because auto-selecting steals the keyboard cursor. The shipped values are `true`, `false`, and `focusNoScroll` (reveal without scrolling). The takeaway for spec_driven: **decoupling "reveal" from "select" is real UX work**, but for v1 we have no Quick Open, no editor tabs, and no other entry into "what's open"; URL is the single source of truth. So the issue does not apply yet, but the lesson — selection and focus are separate states — should still inform the data model.

Long names are truncated at the end with a single ellipsis; the full path appears in a tooltip on hover. Selection visual is a filled row background (different shade for focused-vs-selected within the same tree, but most users never notice). Single tab stop, roving tabindex inside the tree.

## JetBrains "Project" tool window

JetBrains is the counter-example. Per the [Project tool window docs](https://www.jetbrains.com/help/idea/project-tool-window.html), the tree is opened with `Alt+1`, navigated with arrows, expanded/collapsed with Right/Left, and supports `Ctrl+F` "Speed Search" — type-ahead with a visible filter bar instead of the silent type-ahead VS Code uses. `Space` previews the current file in a peek pane without committing it as the active editor — a focus/selection split spec_driven could borrow.

The "Always Select Opened File" toggle (renamed in 2022 from "Autoscroll from Source", per the [JetBrains community post](https://intellij-support.jetbrains.com/hc/en-us/community/posts/13016403707666-Toggle-button-for-Always-select-opened-file-in-Project-view)) does what `explorer.autoReveal=true` does in VS Code: when you switch editors, the Project view scrolls and selects the matching node. It is off by default, which is the opposite of VS Code, on the theory that an unsolicited tree-jump while typing is more annoying than the cost of pressing the "locate" button when you actually want to know where you are.

Long names truncate end-ellipsis; tooltip shows full name + path. Selection visual is row highlight; focused-but-unselected is a thin border. Single tab stop, roving tabindex within the tree.

## GitHub repo file tree

GitHub added a persistent file tree to the repo viewer in 2022. It opens with the `t` shortcut (which actually launches the file finder, a fuzzy-match overlay rather than a tree-internal type-ahead), and the tree itself toggles with a button. Per [GitHub community discussion #51306](https://github.com/orgs/community/discussions/51306), the tree's open/closed state persists across navigation. Crucially, **every node click updates the URL** — clicking `src/foo.ts` navigates to `https://github.com/owner/repo/blob/main/src/foo.ts`, which is the canonical permalink for that view. There is no separate "selected file" in-memory state; the URL **is** the selection.

This is the single most important pattern for spec_driven. URL-as-state means deep links work, the back button works, refreshing works, and there is no "selection got out of sync with the editor" bug class because there is no separate selection. Stage and file in the URL pin both panes.

Keyboard support inside the tree is thinner than VS Code's — arrows work, Enter activates, but type-ahead is delegated to the file finder overlay. Long names use end-ellipsis. Single tab stop into the tree.

## MkDocs Material sidebar

Material for MkDocs (the [setup/setting-up-navigation docs](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/)) is the comparator for "documentation sidebar that pretends to be a tree." It is not a real ARIA tree — it is a nested `<nav>` of `<ul>` and `<a>` elements, so each link is its own tab stop and arrow keys do not navigate. Tab/Shift+Tab walk the entire link list, which is acceptable for short docs but painful for a 200-page manual.

Where Material genuinely innovates is **overflow handling** for long titles. The [`md-ellipsis` class](https://github.com/squidfunk/mkdocs-material/issues/3785) applies `overflow: hidden; text-overflow: ellipsis; white-space: nowrap` to nav links so a deeply nested title does not push the sidebar wider than its column. Tooltips on overflow are an open feature request — not built-in. State persistence is partial: the open section state is held in CSS via `<input type="checkbox">` toggles, but the URL itself reflects only the current page, not the open/closed state of unrelated branches. "Anchor tracking" updates the URL hash as you scroll the reader pane, which is a nice touch for jumping back to a particular section.

The takeaway for spec_driven: **adopt `md-ellipsis`-style end-truncation as the cheap default, but reach for middle-ellipsis for filenames** (see recommendations) because file extensions matter at a glance and end-ellipsis hides them.

## Storybook sidebar

Storybook's sidebar is closer to a real tree — keyboard arrows work for parent/child traversal and Left/Right toggle expansion, per [PR #1427](https://github.com/storybookjs/storybook/pull/1427) which originally added keyboard accessibility to the story hierarchy. F6/Shift+F6 cycle landmark regions (sidebar, toolbar, preview, addons), per the [browse-stories docs](https://storybook.js.org/docs/get-started/browse-stories/). Selecting a story updates the URL (`?path=/story/...`), so URL-as-state holds as in GitHub.

Known issues from earlier versions ([#13040](https://github.com/storybookjs/storybook/issues/13040)) included the sidebar "jumping" when components expand/collapse and skipping items across expansion boundaries — a reminder that **virtualization plus tree expansion is fiddly**. For spec_driven's v1 we expect at most a few dozen artifact files per project, so virtualization is not needed; rendering all nodes makes Up/Down behavior trivially correct.

Search is a separate fuzzy-finder overlay, not in-tree type-ahead. Long names get end-truncated and may wrap on hover. Single tab stop, roving tabindex inside the tree.

## Backstage TechDocs sidebar

[Backstage TechDocs](https://backstage.io/docs/features/techdocs/how-to-guides/) embeds an MkDocs build inside a Backstage plugin, so its sidebar inherits MkDocs Material behavior — link list, no in-tree arrow navigation, end-ellipsis on long titles. Where it differs is **deep linking via annotation**: the [`backstage.io/techdocs-entity-path` annotation](https://backstage.io/docs/features/software-catalog/well-known-annotations/) lets a catalog entity link directly to a sub-page within the embedded docs, producing URLs like `/docs/default/component/<entity>/this-is-a-subpage/`. The URL pattern carries: namespace, kind, entity name, and page path. For spec_driven, the analog would be `/projects/<task_type>/<task_name>/stage-<n>/<artifact>`, and the parser is straightforward.

Backstage has had recurring bugs ([#18441](https://github.com/backstage/backstage/issues/18441), [#16544](https://github.com/backstage/backstage/issues/16544)) where TechDocs navigation breaks when the app is not at domain root because relative URLs are baked into the iframe content. Lesson: **build the URL from a single base path constant**, not from `window.location` slices, so dev (`localhost:5173`) and prod (`localhost:5173/spec_driven/`) both work.

## Comparison matrix

| Tool | Up/Down | Left/Right | Enter | Home/End | Type-ahead | Focus vs selection | Long-name handling | URL-as-state | Tab stops |
|---|---|---|---|---|---|---|---|---|---|
| W3C ARIA APG TreeView | move focus | open/close, traverse | activate | first/last | yes, wraps | distinct, selection-follows-focus optional | not specified | not specified | single, roving tabindex |
| VS Code Explorer | move focus | open/close, traverse | rename (papercut) | yes | yes, silent | distinct (`aria-selected` separate from focus); `autoReveal` couples them | end-ellipsis, tooltip on hover | partial: tab/editor state, not Explorer state | single, roving tabindex |
| JetBrains Project | move focus | open/close, traverse | activate | yes | `Ctrl+F` Speed Search bar | distinct; "Always Select Opened File" couples editor->tree | end-ellipsis, full path tooltip | no — IDE state is in workspace | single, roving tabindex |
| GitHub file tree | move focus | open/close, traverse | activate | yes | delegated to `t` finder overlay | URL is selection | end-ellipsis | yes — every click is a permalink | single |
| MkDocs Material | (none — link list) | (none) | follow link | (none) | global `s`/`f` opens search | URL is current page; section open state in CSS | `md-ellipsis` end-truncate, no tooltip | partial — page yes, section state no | many (one per link) |
| Storybook | move focus | open/close | activate | yes | separate finder | URL reflects story | end-ellipsis | yes — `?path=/story/...` | single, roving tabindex |
| Backstage TechDocs | (none — link list) | (none) | follow link | (none) | none in sidebar | URL is current page | `md-ellipsis` end-truncate | yes — `techdocs-entity-path` URL convention | many |

## Filename overflow: middle-ellipsis is worth the JS

End-ellipsis breaks for filenames because the extension is the part that disambiguates: `migration-2024-...md` and `migration-2024-...py` look identical. Per the [MDN `text-overflow` reference](https://developer.mozilla.org/en-US/docs/Web/CSS/text-overflow), CSS does not natively support middle-ellipsis — the closest is the two-value form (`text-overflow: ellipsis ellipsis`) plus a scrolled container, which is awkward and does not preserve the extension specifically.

The two practical approaches:

1. **Two-element split with `direction: rtl`** — wrap the name in a flex row with two children: `.head` containing the first N-3 characters, `.tail` containing the last 3-7 characters. The `.tail` uses `direction: rtl` to keep the extension visible when the row shrinks. This is pure CSS and works in every modern browser ([CodePen example](https://codepen.io/markchitty/pen/RNZbRE)).
2. **JS truncation** — measure the row's available width on resize and replace `name.ext` with `na…ame.ext`. Higher fidelity but requires a `ResizeObserver`. Libraries like [react-truncate's MiddleTruncate](https://truncate.js.org/reference/middle-truncate/) ship this.

For spec_driven v1 the CSS-only `direction: rtl` split is the right tradeoff — zero runtime cost, no observer plumbing, and the extension is always visible. Tooltip on hover (or a focus-revealed full path inline) catches the rare case where the middle is also load-bearing.

## Recommendations for spec_driven v1

1. **Adopt the W3C APG TreeView pattern wholesale** for the sidebar: `role="tree"` on the container, `role="treeitem"` on every node, `role="group"` on each child container, `aria-expanded` on parents, `aria-current="page"` on the node matching the URL, and `aria-level` / `aria-posinset` / `aria-setsize` if any branch is dynamically loaded. Wire the keyboard map exactly as specified — Up/Down/Left/Right/Home/End/Enter/type-ahead. Leave the `*` "expand all siblings" shortcut out of v1; it's a power-user nice-to-have.

2. **Single tab stop with roving tabindex.** Exactly one `treeitem` carries `tabindex="0"` and it is the one matching the current URL (mirroring `aria-current="page"`). All others are `tabindex="-1"`. When the tree gains focus from outside via Tab, focus lands on "where you are," not the top — this is the [APG navigation example's](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/examples/treeview-navigation/) load-bearing detail and it makes the experience feel correct without the user knowing why.

3. **URL is the single source of truth for selection.** Pattern: `/projects/<task_type>/<task_name>/<stage>/<artifact_path>`. Selection in the tree, content in the reader, breadcrumbs at the top, and the open/closed state of every ancestor are all derived from the URL. No `useState` for "currently selected file." This is GitHub's and Storybook's pattern and it makes the back button, refresh, deep-link sharing, and "open in new tab" all work for free, plus it kills the entire class of "tree state drifted from editor state" bugs that plague VS Code's `autoReveal`.

4. **Selection-follows-focus, but keep "activate" explicit.** Arrow keys move focus and update the URL via `history.replaceState` (so back-button history does not fill up with every arrow press). Enter triggers `history.pushState` so users can use the back button to revisit a previous file. This matches the APG "selection follows focus" recommendation while sidestepping the back-button-spam problem.

5. **Middle-ellipsis on filenames; end-ellipsis on directory names.** Use a two-element flex split with `direction: rtl` on the tail (last 6 characters or so) so the extension is always visible — `migration-2024-...md` becomes `migration-...n-2024.md` and the file type stays legible. Directory names get plain `text-overflow: ellipsis` because they have no extension. Tooltip on hover shows the full name; full path lives in the breadcrumb.

6. **Breadcrumbs as deep-link landmarks.** Render breadcrumbs `Project / Stage / Artifact` above the reader. Each segment is a real `<a href>`, so users can jump up a level with a click and copy a permalink to "this stage." Style as a single-line row with end-ellipsis on the middle segments if the name is long.

7. **No virtualization in v1.** Render the full tree at mount. With ~30-50 artifacts per project the DOM cost is trivial, and skipping virtualization eliminates the [Storybook #13040](https://github.com/storybookjs/storybook/issues/13040) family of bugs (focus jump on expand, item skipping). Revisit when a real project lands with >500 nodes.

8. **No in-tree type-ahead for v1.** The tree is small enough that arrow-key traversal is faster than typing a prefix, and silent type-ahead is the kind of feature users do not discover anyway. If a search is wanted later, copy GitHub's and Storybook's pattern — a separate `Cmd+P`-style finder overlay, not in-tree.

## Open questions / not researched

- **Mobile layout.** The two-pane layout assumes desktop. How the tree should collapse on a 375px viewport (drawer? off-canvas?) was out of scope for this angle.
- **Multi-select.** Does spec_driven ever need to select multiple artifacts (for diff, for batch-export)? If so the `aria-selected` model has to split from focus and the keyboard map adds Shift+arrow / Ctrl+click. Not researched.
- **Drag-and-drop reordering.** Out of scope; would require a different selection model and a drop-target spec.
- **Tree filtering UI.** A "filter sidebar" input that hides non-matching nodes is a common pattern (Storybook, Backstage) but the interaction with `aria-current` and roving tabindex when the current node gets filtered out has edge cases that need their own pass.
- **Unsaved-edit indicators on tree nodes.** If the right pane becomes editable (Stage 6 work), each tree node may need a dirty-dot indicator and a confirm-on-navigate hook. Not researched.
- **Concrete focus-ring CSS.** APG specifies behavior, not visual style. The exact focus-vs-selection visual (border color, background opacity, which contrast ratio against which Material/Tailwind palette) is a design call, not a research call.

## Sources

- [W3C ARIA APG Tree View Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/)
- [W3C ARIA APG Navigation Treeview Example](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/examples/treeview-navigation/)
- [Adam Tuttle: Navigating VS Code's File Explorer Panel without Your Mouse](https://adamtuttle.codes/blog/2024/navigating-vscode-file-explorer-without-mouse/)
- [microsoft/vscode#175690 — Separate explorer.autoReveal into 2 options](https://github.com/microsoft/vscode/issues/175690)
- [JetBrains: Project tool window documentation](https://www.jetbrains.com/help/idea/project-tool-window.html)
- [JetBrains community: Toggle button for "Always select opened file"](https://intellij-support.jetbrains.com/hc/en-us/community/posts/13016403707666-Toggle-button-for-Always-select-opened-file-in-Project-view)
- [GitHub community discussion #51306 — file tree show/hide shortcut](https://github.com/orgs/community/discussions/51306)
- [Material for MkDocs — Setting up navigation](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/)
- [squidfunk/mkdocs-material#3785 — Show title on mouseover on overflowing nav items](https://github.com/squidfunk/mkdocs-material/issues/3785)
- [Storybook: Browse stories](https://storybook.js.org/docs/get-started/browse-stories/)
- [storybookjs/storybook PR #1427 — Story hierarchy keyboard accessibility](https://github.com/storybookjs/storybook/pull/1427)
- [storybookjs/storybook#13040 — Keyboard navigation glitches in sidebar](https://github.com/storybookjs/storybook/issues/13040)
- [Backstage TechDocs how-to guides](https://backstage.io/docs/features/techdocs/how-to-guides/)
- [Backstage well-known annotations (`techdocs-entity-path`)](https://backstage.io/docs/features/software-catalog/well-known-annotations/)
- [backstage/backstage#18441 — TechDocs navigation breaks off domain root](https://github.com/backstage/backstage/issues/18441)
- [MDN: text-overflow](https://developer.mozilla.org/en-US/docs/Web/CSS/text-overflow)
- [CodePen: CSS-only middle truncation with ellipsis (markchitty)](https://codepen.io/markchitty/pen/RNZbRE)
- [react-truncate MiddleTruncate reference](https://truncate.js.org/reference/middle-truncate/)
