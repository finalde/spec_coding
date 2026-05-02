# Angle — two-pane navigator + reader UX

Researcher: researcher-02
Run: spec_driven-20260502-141813
Date: 2026-05-02

## 1. What this angle covers

Conventions for two-pane "navigator (left tree) + reader (main content)" doc/code tools, applied to a readonly viewer that shows ≤50 projects × ≤200 files spread across 5 fixed stage subfolders per project. Locked decisions feeding this angle: collapsible-by-type sidebar (one section per task_type, default-expand the section containing the current project), spec_driven readme as landing page, in-app relative markdown link navigation, Shiki highlighting. The angle's job is to translate "what mature tools do" into concrete v1 component behavior for the viewer's sidebar tree, selection model, breadcrumbs, keyboard support, and overflow handling.

Reference tools probed: VS Code Explorer, JetBrains Project tool window, GitHub repo file view, MkDocs Material, Storybook sidebar, Backstage TechDocs.

## 2. Key findings

### Click semantics: folder vs file

- VS Code uses single-click as **preview** (reuses one tab); double-click or edit promotes to a permanent tab; folders single-click to expand/collapse. Source: [VS Code User interface](https://code.visualstudio.com/docs/getstarted/userinterface).
- GitHub renders folders as in-place navigations (URL changes, content swaps) and renders files in a content pane below a breadcrumb derived from the path. Established practice: clicking the path **is** the navigation.
- For a readonly viewer with no edit-vs-preview distinction, the simple convention is: **folder click = toggle expand/collapse, file click = render in main pane**. No double-click required.

### Selection state in URL (deep-linking)

- GitHub uses path-based URLs (`/{owner}/{repo}/blob/{branch}/{path}`); the URL **is** the selected file. Storybook uses query-style story IDs that round-trip.
- MkDocs Material exposes `navigation.tracking` (URL updates on scroll to anchor) and `navigation.instant` for SPA-like navigation. Source: [Material for MkDocs setup](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/).
- Established practice: **selected file should be reflected in the URL**, so any state (which project, which file, which heading) is shareable and refresh-safe. This is consistent across GitHub, Storybook, MkDocs, and Backstage TechDocs.

### Tree expansion default

- VS Code Explorer: collapses everything except the workspace root; the user expands as needed. Provides `explorer.autoReveal` (default on) which auto-expands the path of the currently active file. Source: [Bobby Hadz — reveal current file](https://bobbyhadz.com/blog/vscode-reveal-current-file-in-explorer).
- JetBrains: explicit "Always Select Opened File" (formerly "Autoscroll from Source") that expands the path of the active editor file in the Project tool window. Source: [JetBrains support — Autoscroll to Source](https://intellij-support.jetbrains.com/hc/en-us/community/posts/360006983339-Autoscroll-to-Source).
- MkDocs Material: `navigation.expand` opens all sections by default; without it, only the section containing the current page expands. Source: [MkDocs Material discussion #2173](https://github.com/squidfunk/mkdocs-material/discussions/2173).
- Established practice: **collapse by default, auto-expand the ancestor chain of the selected file**. This matches the locked decision "default-expand the section containing the current project".

### Breadcrumbs above content

- GitHub renders a clickable breadcrumb above every file/folder content view (each segment is a link to its directory).
- Backstage TechDocs Reader has breadcrumbs in the page header pointing back to the docs homepage. Source: [Backstage TechDocs](https://backstage.io/docs/features/techdocs/).
- MkDocs Material added `navigation.path` specifically for breadcrumb rendering above content.
- Established practice: **breadcrumbs above content are standard for hierarchical doc/code tools**, especially when a sidebar tree could be collapsed. Worth including in v1 because the viewer's path is meaningful (`task_type / task_name / stage / file`).

### Keyboard navigation

| Tool | Tree keys | Quick-open |
|---|---|---|
| VS Code | Up/Down move, Right expand/move-into, Left collapse/move-out, Enter renames (Ctrl+Down to open), filter with Ctrl+F | Ctrl+P |
| Storybook | Arrow keys for tree, "/" for search | "/" |
| JetBrains | Speed-search by typing, arrow keys for tree | Shift+Shift |

- Source: [Adam Tuttle — Navigating VS Code File Explorer without a mouse](https://adamtuttle.codes/blog/2024/navigating-vscode-file-explorer-without-mouse/) and [VS Code tips and tricks](https://code.visualstudio.com/docs/getstarted/tips-and-tricks).
- Storybook's accessibility tracker explicitly notes the sidebar should implement the ARIA `tree` role for proper keyboard support. Source: [Storybook accessibility roadmap](https://github.com/storybookjs/storybook/issues/33041).
- W3C ARIA APG specifies arrow-key behavior for tree role: Up/Down move, Right expand-or-into-children, Left collapse-or-to-parent, Home/End jump to first/last visible. Source: [W3C ARIA Tree View Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/).

### Selected vs focused (visual state)

- W3C ARIA APG requires the visual design distinguish **focus** (which item arrow-keys are on) from **selection** (which item's content is shown). Both indicators must be visible simultaneously. Source: [W3C ARIA Tree View Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/) and [aria-selected attribute](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-selected).
- Common convention: filled background bar for selected (`aria-selected="true"`), thin outline ring for keyboard focus.

### Long file names

- Carbon Design System tree view: ellipsis truncation **with browser tooltip showing the full string**. Source: [Carbon Tree view](https://carbondesignsystem.com/components/tree-view/usage/).
- PatternFly Truncate: prefer **middle-ellipsis for filenames** so the extension and any trailing identifier remain visible (e.g. `angle-two-pa…ux.md`). Source: [PatternFly Truncate guidelines](https://www.patternfly.org/components/truncate/design-guidelines/).
- GitHub historically: end-ellipsis without tooltip — community has flagged this as worse UX than middle-ellipsis. Source: [isaacs/github issue #171](https://github.com/isaacs/github/issues/171).
- Established practice: **single-line, ellipsis-on-overflow, native title tooltip on hover**. Do not horizontal-scroll the sidebar; do not wrap.

### "Currently selected" visual

- VS Code, JetBrains, GitHub, MkDocs, Storybook: all use a **filled background row + accent text colour** for the selected node. None rely on bold-only or icon-only.
- Storybook explicitly tracks bugs where keyboard nav loses sync with visual selection — selection styling must move atomically with the URL/route. Source: [Storybook issue #13040](https://github.com/storybookjs/storybook/issues/13040).

## 3. Implications for the spec (concrete, actionable)

1. **Routing.** Spec a single deep-linkable route shape, e.g. `/{section}/{task_type}/{task_name}/{stage}/{file_path}` for Projects and `/settings/{kind}/{file}` for Section 1. The full URL must round-trip on reload. The landing page (spec_driven readme) is just the canonical URL `/projects/development/spec_driven/final_specs/spec.md` (or `/.../user_input/revised_prompt.md` if the spec doesn't exist yet).
2. **Click model.** Folder click toggles expand/collapse only — never opens a "folder index" page in v1. File click navigates and renders. This avoids the GitHub-style folder-index ambiguity and matches the locked "5 fixed stage subfolders" model where folders are pure containers.
3. **Default expansion.** On any URL load, expand the ancestor chain of the selected file (task_type section → project → stage). All other sections collapsed. Matches locked decision and matches VS Code `autoReveal` semantics.
4. **Breadcrumbs.** Render a breadcrumb above the reader pane: `task_type / task_name / stage / filename`. Each segment except the last is a link that navigates to that node (folder click in the tree = expand; breadcrumb segment click = navigate-and-expand). Section 1 gets a parallel breadcrumb: `Settings / kind / filename`.
5. **Selected-state visual.** Filled background bar on the tree row for `aria-selected="true"`; separate ring outline for keyboard focus. Identical visual treatment for Section 1 leaves and Section 2 leaves.
6. **Long names.** Single-line ellipsis with native `title` attribute = full file/folder name. Use middle-ellipsis for files (preserves `.md` extension), end-ellipsis for folders. No wrapping, no horizontal scroll.
7. **Keyboard support — v1 minimum.** Tab to focus the tree, arrow keys per ARIA tree pattern (Up/Down move, Right expand, Left collapse), Enter to navigate. Defer Ctrl+P quick-open to v2 — Storybook and VS Code both treat it as a power-user accelerator, not a baseline.
8. **In-app relative links.** Already locked. Implementation note: resolve them against the current file's directory; if the resolved path is inside the exposed tree, push to history and update URL. If not, fall through to default browser behavior (broken-link tooltip per locked decision).
9. **No multi-select, no drag, no context menus.** Readonly scope. ARIA: `aria-multiselectable="false"` on the tree.
10. **Accessibility baseline.** Implement the W3C ARIA tree pattern (`role="tree"`, `role="treeitem"`, `aria-expanded`, `aria-selected`, `aria-level`). This is the minimum vendors like Storybook and Backstage are explicitly working toward; doing it correctly from day one costs almost nothing.

## 4. Open questions surfaced

- **Sidebar width / resize.** Do we ship a fixed-width sidebar (simpler, matches Storybook's earlier versions) or a draggable splitter (matches VS Code/JetBrains)? Affects ellipsis frequency. Recommend fixed-width in v1 with sensible default (~280–320px); revisit if dogfooding shows constant ellipsis on real spec_driven paths.
- **Section 1 vs Section 2 separator.** Locked decision says collapsible-by-type for Projects, but Section 1 is a separate top-level region. Is Section 1 always-visible above Section 2, or also a collapsible top-level section? Recommend always-visible header + always-expanded subgroups for Section 1 — it's small (1 + N agents + M skills), no benefit to collapsing.
- **URL encoding of file paths.** Many `/`-separated path segments inside a single route param. Pick a strategy: nested route segments (clean URLs, more router config) vs single splat param with encoded `/` (simpler, uglier). Recommend nested segments — matches GitHub, future-proofs against deeper paths.
- **Browser back/forward.** Should clicking in the tree push history entries (every click adds to history) or replace (only the address bar updates)? GitHub pushes; VS Code in browser pushes. Recommend push so back-button matches user mental model — but explicit decision needed.
- **Active tree node when URL is a folder-only route.** If the user shares `/projects/development/spec_driven/findings/` (no file), what does the reader pane show? Empty state? Folder listing? Auto-pick first child? Spec must answer this; recommend auto-redirect to the first file alphabetically (or first markdown file) and keep the URL canonical.
- **Settings section breadcrumb wording.** Locked decision says three subgroups: CLAUDE.md, Agents, Skills. Breadcrumb root: literal "Settings" or "Claude Settings & Shared Context"? The latter matches the in-app section name; the former is shorter for the breadcrumb bar. Minor, but spec should pick one.

## Sources

- [VS Code User interface](https://code.visualstudio.com/docs/getstarted/userinterface)
- [VS Code tips and tricks](https://code.visualstudio.com/docs/getstarted/tips-and-tricks)
- [Adam Tuttle — Navigating VS Code File Explorer without a mouse](https://adamtuttle.codes/blog/2024/navigating-vscode-file-explorer-without-mouse/)
- [Bobby Hadz — reveal the current file in Explorer in VS Code](https://bobbyhadz.com/blog/vscode-reveal-current-file-in-explorer)
- [JetBrains support — Autoscroll to Source](https://intellij-support.jetbrains.com/hc/en-us/community/posts/360006983339-Autoscroll-to-Source)
- [JetBrains support — automatically select current file](https://intellij-support.jetbrains.com/hc/en-us/community/posts/206333529-How-to-automatically-select-current-file-in-left-project-view)
- [Material for MkDocs — Setting up navigation](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/)
- [MkDocs Material discussion #2173 — Navigation section collapse](https://github.com/squidfunk/mkdocs-material/discussions/2173)
- [Storybook — features and behavior](https://storybook.js.org/docs/configure/user-interface/features-and-behavior)
- [Storybook — new component finder and sidebar](https://storybook.js.org/blog/new-component-finder-and-sidebar/)
- [Storybook accessibility roadmap (issue #33041)](https://github.com/storybookjs/storybook/issues/33041)
- [Storybook keyboard navigation glitches (issue #13040)](https://github.com/storybookjs/storybook/issues/13040)
- [Backstage TechDocs](https://backstage.io/docs/features/techdocs/)
- [Backstage TechDocs — getting started](https://backstage.io/docs/features/techdocs/getting-started/)
- [Carbon Design System — Tree view](https://carbondesignsystem.com/components/tree-view/usage/)
- [Carbon Design System — Overflow content](https://carbondesignsystem.com/patterns/overflow-content/)
- [PatternFly Truncate design guidelines](https://www.patternfly.org/components/truncate/design-guidelines/)
- [isaacs/github issue #171 — middle ellipsis for file names](https://github.com/isaacs/github/issues/171)
- [W3C ARIA APG — Tree View Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/)
- [MDN — ARIA tree role](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/tree_role)
- [MDN — ARIA aria-selected attribute](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-selected)
