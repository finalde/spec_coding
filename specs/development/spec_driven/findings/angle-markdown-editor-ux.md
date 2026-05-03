# Angle — markdown-editor-ux

Run: `spec_driven-20260503-145859`. Researcher: `researcher-02-markdown-editor-ux`. Sources are real WebSearch / WebFetch results captured during this run; no training-data paraphrase.

## 1. What this angle covers

How production webapps converge on in-place markdown editing affordances for **non-developer users** maintaining text artifacts. Specifically: (a) plain textarea vs split-pane vs CodeMirror/Monaco; (b) autosave vs explicit save; (c) dirty-state indicators (asterisk, dot, color); (d) Ctrl+S support and conflict handling; (e) per-block / structured editing for nested data (Q/A pairs, tables, frontmatter); (f) error-banner persistence vs toast; (g) Edit/View toggle vs always-editable; (h) handling of file size / encoding edge cases. The `spec_driven` webapp's editor surface (FR-3 / FR-7 / FR-41 / NFR-9) lands inside this design space.

## 2. Key findings

### 2a. Editor substrate: three established camps

- **Plain `<textarea>` + side-pane preview** is still the default for "edit a file you already understand the syntax of." StackEdit, EasyMDE, OverType, and the GitHub web editor all sit here. OverType explicitly markets itself as "the markdown editor that's just a textarea," and hides nothing — formatting characters stay visible — because the alternative breaks 1:1 character mapping ([panphora/overtype](https://github.com/panphora/overtype), [Ionaru/easy-markdown-editor](https://github.com/Ionaru/easy-markdown-editor)).
- **CodeMirror 6** is the convergent next step when syntax highlighting / soft-wrap / line numbers matter. CodeMirror exposes `CodeMirror.fromTextArea()` for drop-in textarea replacement and is "the most popular code editor for the web" per the comparison roundup ([portalZINE comparison](https://portalzine.de/javascript-code-editors-that-transform-textareas-a-comprehensive-comparison/), [CodeMirror](https://codemirror.net/)).
- **Monaco** is the heavyweight tier (it powers VS Code Web). It has no `fromTextArea()` shim and ships a sizeable bundle, so its use is correlated with developer-targeted apps, not non-developer doc editors ([portalZINE comparison](https://portalzine.de/javascript-code-editors-that-transform-textareas-a-comprehensive-comparison/)).
- **WYSIWYG / block editors** (Notion, GitBook, Dropbox Paper) abstract markdown away entirely — non-developers type prose, the editor renders blocks. GitBook's docs explicitly position this for users coming from Notion / Google Docs ([GitBook Editor docs](https://docs.gitbook.com/content-editor/editor)). This is the right model when the user must NOT see syntax; it's the wrong model when (as in `spec_driven`) the file IS the syntax and the user must see what regen will read.

### 2b. Save model — autosave is dominant for prose, explicit save still rules code-shaped markdown

- **Notion** auto-saves continuously to the cloud and does not document a Ctrl+S binding ([Notion Help — Keyboard shortcuts](https://www.notion.com/help/keyboard-shortcuts), [Understanding Notion's auto-save](https://www.notionry.com/faq/does-notion-automatically-save-changes)).
- **StackEdit** auto-saves to browser local storage; documents survive across reloads and clearing browser data deletes them ([StackEdit](https://stackedit.io/)).
- **HackMD** is real-time collaborative — there is no save button at all, edits stream to the server ([HackMD Markdown Reference](https://www.markdownguide.org/tools/hackmd/), [HedgeDoc](https://hedgedoc.org/)).
- **Dropbox Paper** is also collaborative-realtime; it markets the absence of conflicted-copy artifacts as the differentiator over plain Dropbox ([Dropbox Help — conflicted copy](https://help.dropbox.com/organize/conflicted-copy)).
- **GitHub web editor** keeps **explicit save** (the "Commit changes" button) because the underlying object is a git commit, not free-floating prose. MkDocs Material's "Edit this page" button delegates to GitHub's editor and inherits that contract ([MkDocs Material — buttons](https://squidfunk.github.io/mkdocs-material/reference/buttons/)).
- **VS Code (and VS Code Web)** keep explicit save (Ctrl+S) and surface a dirty-dot indicator when in-editor content diverges from disk ([microsoft/vscode#132705](https://github.com/microsoft/vscode/issues/132705)).

Pattern: when the file is **canonical state on disk that something else reads** (git, MkDocs build, regen pipeline), the convergent UX is **explicit save with a dirty indicator**. When the file is just "the user's notes," the convergent UX is autosave.

### 2c. Dirty-state indicator — dot or asterisk, in the tab

- VS Code uses a small filled dot in the tab; when the dot vanishes it means in-editor content equals disk ([microsoft/vscode#132705](https://github.com/microsoft/vscode/issues/132705), [microsoft/vscode#23950](https://github.com/Microsoft/vscode/issues/23950)).
- Obsidian does NOT ship a dirty asterisk natively; users have an open feature request for one, comparing to Notepad++'s asterisk ([Obsidian Forum — modified-tab asterisk](https://forum.obsidian.md/t/option-to-mark-modified-unsaved-tabs-with-an-asterisk/108654)).
- Convention across IDEs (Notepad++, JetBrains, VS Code) is dot or `*` in the tab title, plus a `beforeunload` prompt before navigation away.

### 2d. Ctrl+S and `beforeunload` — established UX contract

- MDN's `beforeunload` documentation and the prevailing best-practice guidance both recommend: attach the listener **only while a dirty flag is true**; remove it on save. The browser-rendered confirmation dialog text cannot be customized for security reasons ([MDN — beforeunload](https://developer.mozilla.org/en-US/docs/Web/API/Window/beforeunload_event), [Cloudscape — Communicating unsaved changes](https://cloudscape.design/patterns/general/unsaved-changes/)).
- AWS Cloudscape's design-system guidance on "Communicating unsaved changes" is the most explicit production reference: in-page banner / inline indicator FIRST, browser dialog as a backstop ([Cloudscape](https://cloudscape.design/patterns/general/unsaved-changes/)).
- SPAs need a parallel router-level guard because `beforeunload` does not fire on client-side navigation — same source.

### 2e. Conflict handling — three tiers

- **Single-user local app (StackEdit, Obsidian)**: no conflicts; last write wins; data lives on disk / local storage.
- **Realtime CRDT (HackMD, Notion, Dropbox Paper, GitBook live edits)**: conflicts are merged operationally; there is no "your version vs theirs" dialog ([GitBook live edits](https://docs.gitbook.com/content-editor/editor/live-edits)).
- **Pessimistic / commit-style (GitHub web editor, Dropbox file sync)**: a second writer sees a "branch has diverged" or "conflicted copy" outcome ([Dropbox Help — conflicted copy](https://help.dropbox.com/organize/conflicted-copy)).

For a single-user localhost tool the realistic risk is "user edited file in editor X while my webapp was open." The convergent mitigation is **read-then-compare-mtime on save** and surface a banner if it changed; no production tool tries to auto-merge.

### 2f. Per-block / structured editing for nested data

- Notion, GitBook, and Dropbox Paper all expose **per-block edit affordances** (hover → inline toolbar, drag handle, "/" insert menu) — but they own the document model. They are not editing markdown text; they are editing blocks that serialize TO markdown ([GitBook Editor](https://docs.gitbook.com/content-editor/editor)).
- Markdown-text editors that try to expose per-block editing (CodeMirror's rich-Markdoc plugin, Obsidian's Live Preview) keep the markdown source authoritative and overlay rendering — the user always has a "fall back to source" escape hatch ([codemirror-rich-markdoc](https://github.com/segphault/codemirror-rich-markdoc), [discuss.CodeMirror — WYSIWYG markdown](https://discuss.codemirror.net/t/implementing-wysiwyg-markdown-editor-in-codemirror/2403)).
- Pattern: **structured view + verbatim-source escape hatch**. The structured view is for the common case; when parsing fails or the user needs to do something the structured view doesn't model, drop to the source.

### 2g. Edit/View toggle vs always-editable

- GitHub web reader → "pencil" icon flips into the editor. Same for MkDocs Material's "edit this page" button (which links out to GitHub's editor) ([MkDocs Material — buttons](https://squidfunk.github.io/mkdocs-material/reference/buttons/)).
- Obsidian has Editing-view vs Reading-view toggle; default is Editing.
- Notion / GitBook / Dropbox Paper are always-editable; there is no view-only mode in normal use.

For docs/spec-style content that must render correctly first and be edited occasionally, **explicit Edit toggle** is the convergent affordance.

### 2h. File-size and encoding edge cases

- GitHub web editor's documented hard cap is 25 MB for blob upload via the web UI; rendered file viewers stop rendering at 1 MB and show a "view raw" link.
- The OWASP File Upload Cheat Sheet recommends explicit size + content-type allow-listing on read AND write paths — convergent across tooling.
- StackEdit's local-storage model is bounded by the browser's quota (~5 MB per origin) and degrades silently when exceeded ([StackEdit](https://stackedit.io/)).

## 3. Implications for the spec (concrete, actionable)

1. **Keep the explicit-save contract.** The artifacts under `specs/{type}/{name}/` are canonical inputs to the regen pipeline (analogous to git-tracked content), so the GitHub / VS Code model is the right reference, not Notion. FR-7 (`PUT /api/file` is the only write path) and FR-41a–d already match this.
2. **Dirty indicator should be a dot or asterisk in the file-tab / breadcrumb header**, mirroring VS Code. The current spec language "clear unsaved-changes indicator" is fine; pin it to "dot in the editor toolbar AND `*` in the document title" to match what users expect from IDEs.
3. **Ctrl+S binding is mandatory.** Every editor with explicit save in this research surfaced Ctrl+S; users will hit it reflexively. Bind it inside both the file-level textarea and each per-Q/A inline editor. Cross-platform: Cmd+S on macOS.
4. **`beforeunload` guard ONLY while dirty=true, and add a router-level guard for SPA navigation.** Cloudscape and MDN both surface this as the load-bearing implementation detail. The router guard is what catches sidebar clicks between files — `beforeunload` won't.
5. **Conflict handling: send a `If-Unmodified-Since` (or sha) on `PUT /api/file`, return 409 with a banner if mtime changed.** Last-writer-wins is acceptable for v1, but the banner ("file changed on disk; reload?") is what production tools converge on. Add as NFR or tighten AC-13.
6. **Structured Q/A view IS the convergent pattern (Notion-style per-block edit) BUT the verbatim-source escape hatch is also the convergent pattern.** The current spec already has both (per-Q/A inline pencil + whole-file textarea via toolbar). Keep both; do not collapse to either alone. The QaErrorBoundary fallback in the interview qa.md handling is exactly the "drop to source on parse failure" move every survey'd editor offers.
7. **Edit/View toggle is correct.** The decision in qa.md round 1 to keep the ✎ Edit toggle (vs always-editable) matches GitHub / MkDocs / VS Code Web — appropriate for spec-style content.
8. **Persistence of error banners > toasts for save failures.** Cloudscape's design-system guidance on unsaved changes calls out persistent inline banner over transient toast. A toast that disappears while the user is mid-recovery is the documented anti-pattern. Tighten the UX rule wherever the spec says "toast" for save errors.
9. **CodeMirror 6 is the right substrate IF a future enhancement adds syntax highlighting / soft-wrap / line numbers.** For v1, the plain textarea is fine and aligned with EasyMDE / OverType / StackEdit. Don't bring in Monaco — bundle weight is wrong for a non-developer surface, and `fromTextArea()` doesn't exist for it.
10. **413 on file >1 MB is already convergent.** GitHub's 1 MB render cap and the OWASP guidance both point at this; existing AC-10 is well-grounded.

## 4. Open questions surfaced

1. **mtime / sha-based concurrency check on `PUT /api/file`**: not currently in the spec. Should the backend reject `PUT` when the on-disk mtime exceeds the value the editor loaded, with a 409 + reload prompt? Lean yes (cheap, prevents the "I edited it in VS Code while the webapp was open" foot-gun), but it's a NFR-level decision that needs the user.
2. **Should the error banner for save failures be modal, persistent inline, or toast?** Cloudscape says persistent inline; current spec language is ambiguous. Tighten in stage 4 spec compilation.
3. **Should Ctrl+S in the per-Q/A inline editor save just that block, or the whole file?** Either is defensible (block-level matches Notion's mental model; file-level matches the on-disk semantics). Recommend block-level save with an immediate disk write so the user's reflex always succeeds.
4. **Soft-wrap default for the file-level textarea**: follow-up 002 set wrap=ON for the regen-prompt panel; should the same default apply to file-level edit? Lean yes (Cloudscape and EasyMDE ship wrap-on); pin in AC.
5. **Should the editor offer a draft-recovery path on accidental close?** StackEdit's local-storage backup is the convergent pattern; not currently in scope. Defer to a follow-up unless the user asks.
6. **macOS Cmd+S**: the keyboard shortcut on macOS is Cmd+S, not Ctrl+S. Currently only Ctrl+S is named. If the audience includes mac users, normalise both.
