# Angle: markdown-editor-ux

## 1. What this angle covers

This research angle answers, for the spec_driven webapp's artifact-editing UX, what conventions mature web-based markdown editors have converged on for:

- Explicit edit toggles vs. always-editable surfaces (and the default "view" or "edit" mode).
- Dirty-state indicators (the "unsaved changes" signal).
- Save semantics — autosave vs. explicit Save (Ctrl+S) and the rationale for each in document editors.
- Error surfacing when a save fails (inline banner vs. toast vs. modal).
- Granularity: per-block / per-section editing vs. whole-file editing.
- Patterns that reduce the *mistake-cost* for non-developers patching structured artifacts (a Q/A entry, a single FR/AC block) without leaving the surrounding context.

The output here will inform the FastAPI + React webapp that surfaces files under `specs/{type}/{name}/` for in-place editing.

## 2. Key findings

### View-by-default, explicit toggle to edit is the dominant convention for "review-then-revise" surfaces

- **Obsidian** ships two top-level views — *Reading view* (clean, no Markdown syntax) and *Editing view* — and the user toggles explicitly between them; inside Editing view there is a further mode choice (Source vs. Live Preview) ([Obsidian Help — Views and editing mode](https://help.obsidian.md/edit-and-read)).
- **GitHub's web file editor** opens a file in a code-style editor with a separate "Preview" tab, i.e. an explicit toggle rather than a single hybrid surface; you commit (save) only when you click the commit button ([Modus Create — Editing Markdown for GitHub](https://moduscreate.com/blog/editing-markdown-for-github/)).
- **VS Code** (incl. VS Code Web) defaults to source editing with a separate Markdown preview opened via `Ctrl+Shift+V`; there is no implicit "tap-to-edit" — the file is in an editor or it is a preview, never both ([VS Code — Basic editing](https://code.visualstudio.com/docs/editing/codebasics)).
- **GitBook** and **Notion** lean the other way (always-editable WYSIWYG-ish surface), but they target authoring as the primary task. For *review-and-occasionally-revise* (the spec_driven use case — a non-developer scanning Q/A or a spec, occasionally fixing a wrong wording), the explicit toggle is what avoids accidental edits ([GitBook editor UX](https://www.thepassionatecoder.com/post/building-in-public-choosing-a-documentation-tool); [Material for MkDocs issue #5894 contrasts the two models](https://github.com/squidfunk/mkdocs-material/issues/5894)).
- VS Code itself has an open proposal (issue #303697) to add a *preview-first* mode for `.md` files with inline section editing — explicit recognition that the "always-editable source" default is wrong for read-heavy markdown ([VS Code issue #303697](https://github.com/microsoft/vscode/issues/303697)).

### Explicit Save (Ctrl+S) is the right default for document editors with structured semantics

- **Primer (GitHub's design system)** is unambiguous: "Start with an explicit saving pattern" for forms; reserve autosave for *imperative* controls (toggles, single-selects) where instant feedback matches user expectation, and avoid autosave on *declarative* controls like free-form text because of "accidental submission risks" ([Primer — Saving](https://primer.style/ui-patterns/saving/)).
- **Pajamas (GitLab's design system)** and **NN/g** echo the same: explicit Save fits when the user wants to *review* changes before committing, and autosave is best for "simple settings that are easy to undo" — neither describes a markdown spec well ([NN/g — Don't Prioritize Efficiency Over Expectations](https://www.nngroup.com/articles/efficiency-vs-expectations/)).
- **VS Code's** default is explicit `Ctrl+S`; auto-save is opt-in via the `Files: Auto Save` setting ([VS Code keybindings](https://code.visualstudio.com/docs/configure/keybindings)).
- **Markdown Monster** and similar standalone editors offer autosave only as a *backup* (auto-save-as-draft) layered on top of an explicit Save — the explicit save remains the canonical commit ([Markdown Monster — Auto-Save and Auto-Backup](https://markdownmonster.west-wind.com/docs/_4sv0nob04.htm)).
- The often-cited UX-pattern guidance: "Autosave does not need to replace save: they can both coexist," but **don't mix autosave-elements and save-required-elements on the same page** — it confuses users about which model is in force ([Damian Wajer — Autosave or explicit save](https://www.damianwajer.com/blog/autosave/); [ui-patterns.com — Autosave](https://ui-patterns.com/patterns/autosave)).

### The "dirty dot" is the de-facto standard unsaved-state indicator

- **VS Code** marks unsaved tabs with a filled dot next to the filename (and on the window title); when saved, the dot collapses back into the close-button. Multiple bug reports (e.g. microsoft/vscode #2357, #23950, #132705, #212173) treat this dot as *load-bearing* — when it disappears or fails to update, users file it as a regression ([VS Code issue #2357](https://github.com/microsoft/vscode/issues/2357), [#132705](https://github.com/microsoft/vscode/issues/132705)).
- **Zed** has the same pattern and a tracked discussion on showing it when the tab bar is hidden ([Zed discussion #15107](https://github.com/zed-industries/zed/discussions/15107)).
- Variants: bold tab title, asterisk after the name, dot replacing the close-button. The dot-replacing-close-button form (VS Code) is the most copied. The convention extends to web apps and dialog titles, often paired with a `beforeunload` prompt on navigation ([Webawesome discussion #1579](https://github.com/shoelace-style/webawesome/discussions/1579); [Primer — Saving](https://primer.style/ui-patterns/saving/)).

### Save errors should be a persistent inline banner, not a toast

- **NN/g** and **Carbon Design System** and the **Smashing Magazine** error-message guide all converge: "Avoid using toast for error messages. Always try to use a banner to prominently inform users about persistent errors." Toasts disappear before the user can read or act, and they appear far from the failing input ([NN/g — Errors in Forms](https://www.nngroup.com/articles/errors-forms-design-guidelines/); [Smashing — Error Messages UX](https://www.smashingmagazine.com/2022/08/error-messages-ux-design/); [LogRocket — Toast notifications](https://blog.logrocket.com/ux-design/toast-notifications/)).
- **Primer** is concrete on the layering: "If the change occurred without a redirect or page refresh, you can use the InlineMessage component… If the change occurred and the page refreshes or redirects, you can use a Banner component" — and toasts are explicitly discouraged on github.com for accessibility reasons ([Primer — Saving](https://primer.style/ui-patterns/saving/)).
- Correlated rule from Primer: **don't disable the Save button** when the form is invalid or unchanged — disabled buttons can't be focused via Tab; instead surface validity state via the inline banner when the user actually clicks Save.
- **Primer** also says: on save failure, the *user's edits must be preserved in the form*, never silently discarded. Pair the banner with the still-dirty editor.

### Per-block editing is worth the complexity only when blocks are semantically meaningful

- **Notion / BlockNote / Tiptap notion-like** editors put each paragraph, heading, list, etc. on its own block with hover-revealed `+` and drag handles — this works because *every* block is a meaningful unit users move/edit/transform individually ([Notion — Block basics](https://www.notion.com/help/guides/block-basics-build-the-foundation-for-your-teams-pages); [BlockNote](https://www.blocknotejs.org/)).
- For mixed content where only *some* sections have semantic identity, the better pattern is **explicit per-section edit affordances on those sections only**, leaving the rest as whole-file. PatternFly calls this out: use *field-specific* inline edit "to make small edits to specific fields," and *full-page edit* "when you want to allow users to edit a larger area with many editable elements all at once" — the two coexist on the same page when justified ([PatternFly — Inline edit](https://www.patternfly.org/components/inline-edit/design-guidelines/)).
- The publiclab `inline-markdown-editor` is a worked example of inline section editing layered on top of rendered markdown: each section gets its own edit button, and the section text is the unit of save ([publiclab/inline-markdown-editor](https://github.com/publiclab/inline-markdown-editor)).
- **Inline edit save/cancel mechanics** (PatternFly, Apiko): a pencil/✎ toggles read→edit; the action area becomes a check (save) and an X (cancel/discard); save commits, cancel reverts to the pre-edit value with no confirmation ([Apiko — Inline editing](https://apiko.com/blog/inline-editing/); [Andrew Coyle — Inline edit pattern](https://coyleandrew.medium.com/the-inline-edit-design-pattern-e6d46c933804)).

### Mistake-cost reducers for non-developers

Established practice (cited above) plus my synthesis from the same sources:

- **View-by-default** prevents accidental keystrokes from corrupting text the user only meant to read.
- **Explicit Save with a visible dirty indicator** makes "I have unsaved work" legible — the user always knows whether their change has been committed.
- **`beforeunload` prompt when leaving a dirty editor** is the standard last-line defence (Primer notes the prompt's message is now browser-controlled, but the trigger is still expected).
- **Discard returns to pre-edit value, not to empty** — the affordance is "abandon this edit," not "wipe the field" (PatternFly).
- **Persistent inline error banner on save failure**, with the user's edits still in the editor, lets the user fix the cause without retyping (Primer).
- **Per-Q/per-A inline edit on top of structured Q&A** (not whole-file) means a wrong answer can be corrected in place; the surrounding Q/A grid keeps the user oriented (PatternFly field-specific edit + publiclab pattern).
- **Keep the per-section edit and the whole-file edit non-overlapping** — Notion-style hover handles on every paragraph are overkill for a spec; one explicit ✎ per Q and one toolbar ✎ for the whole file is enough, and matches Primer's "don't mix save patterns on the same surface" guidance.

## 3. Implications for the spec (concrete, actionable)

1. **Default mode is "view"; ✎ Edit toggle is the only way into editing.** Codify in the FR list. Match Obsidian/GitHub web/VS Code-Web convention.
2. **Save = explicit, via a Save button AND `Ctrl+S` (Cmd+S on macOS).** No autosave in v1. (Optional later: autosave-as-draft to a sidecar file, never to the canonical artifact — same pattern as Markdown Monster.)
3. **Dirty indicator: filled dot adjacent to the filename / artifact title** (VS Code pattern), shown iff `editor_value !== last_saved_value`. The dot disappears on successful save.
4. **Save button is always enabled** (Primer rule). Validation and "no changes" feedback go via the inline banner on click, not via a disabled state.
5. **`beforeunload` and intra-app navigation guard** when the editor is dirty — pop the browser-default "leave site?" prompt; for in-app navigation away from a dirty editor, show a confirm-discard modal with three actions: *Save*, *Discard*, *Cancel navigation*.
6. **Discard control reverts the textarea to the last-saved value** (no confirmation needed if the user explicitly clicked Discard — the action label is the warning).
7. **Save errors render as a persistent inline banner *above* the editor**, never as a toast. The textarea retains the user's edits. The banner stays until the user dismisses it or successfully re-saves. Aligns with Primer / NN/g / Carbon.
8. **`interview/qa.md` gets per-Q and per-A inline ✎** that opens a tiny editor *for that Q or A only*, with check (save) and X (discard) actions adjacent to the field — PatternFly field-specific edit. Whole-file ✎ remains in the toolbar for cases that need it (re-ordering Qs, adding a section).
9. **Mixed granularity is fine but mutually exclusive at runtime**: when whole-file edit is active, per-Q ✎ buttons are hidden (and vice versa) so the user can't open two save scopes at once. Matches Primer's "don't mix save patterns on the same form."
10. **Close-editor button** behaves like Discard if dirty (with confirm-modal), like a no-op if clean. Avoids an asymmetric close path that loses work silently.
11. **Keyboard contract** (cite VS Code as the user mental model): `Ctrl+S` save, `Esc` close-editor (treat as Close, with the dirty-confirm rule above), `Ctrl+Z` undo within the textarea.
12. **Per-Q/per-A save semantics** should write the *whole file* atomically (the structured view is a projection over `qa.md`) — the user's mental model is "I edited this answer," but the disk model is still "the file is the unit of save," matching the file-on-disk-is-truth invariant the rest of the pipeline relies on.

## 4. Open questions surfaced

- **Versioning / undo across saves.** None of the cited editors specify what happens after a successful save — recover-via-disk is delegated to git or the OS. Should the webapp keep an N-deep server-side undo of saved versions per artifact? (Recommend: defer, lean on git in stage 6 outputs and on file mtime for spec artifacts.)
- **Concurrent edit by another process** (CLI editor, another tab, regen pipeline) while the webapp's editor is open. Need a "file changed on disk since you opened it" detector and a merge-or-overwrite prompt. Not covered by the surveyed editors at this granularity.
- **Promoted/pinned items.** The pin mechanism (📌) writes to `<stage>/promoted.md`. Should the editor surface "this Q is pinned" inside the structured Q&A view (e.g., a small lock icon) so the user knows their edit will survive regeneration? Not addressed by any general markdown-editor convention — it's spec_driven-specific.
- **Mobile / narrow viewport.** Inline ✎ per Q is dense on a phone; PatternFly's guidance assumes desktop. Probably out of scope for v1.
- **Live preview alongside source.** Obsidian's Live Preview and VS Code's side-by-side preview are popular but add complexity. Recommend deferring — the spec_driven artifacts are mostly read in the rendered view (the default mode) and edited in source (the toggle), so a side-by-side adds little.
- **Conflict between per-section edits and whole-file edits during a regeneration.** Read-zero contract deletes the file before rewrite; if the user has the whole-file editor open and dirty when stage N regenerates, the dirty buffer must be detected and protected (or at least loudly warned about). Out of scope for the editor itself but worth flagging to the regen flow.
