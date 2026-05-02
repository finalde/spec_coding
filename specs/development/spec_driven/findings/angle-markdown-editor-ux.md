# Angle — Markdown editor UX (in-place edit affordances)

Stage: 3 (Research)
Run: spec_driven-20260503-fullregen
Researcher: spawn `researcher-editor-ux`
Inputs read: `specs/development/spec_driven/user_input/revised_prompt.md`, `specs/development/spec_driven/interview/qa.md`. Prior findings explicitly NOT read (per autonomous-mode read-zero contract).

## Why this angle

The interview locked five editor decisions:

1. **Editor widget** — plain `<textarea>` + monospace, no syntax highlighting.
2. **Save trigger** — Ctrl+S writes via `PUT /api/file`, refreshes buffer, **stays in editor**.
3. **Dirty indicator** — dot/asterisk on the file title + Save highlighted; warn-on-nav while dirty.
4. **Conflict policy** — last-write-wins; no `If-Match`/mtime guard.
5. **Body cap** — 10 MB on read and write.

These choices are deliberately minimalist. The job of this angle is to (a) confirm the picks are coherent against six well-known prior-art editors, (b) flag pitfalls that bite teams who chose the same simple primitives, and (c) propose 5–8 concrete recommendations the spec/validation stages should encode.

The six prior-art systems compared (one is delegated and one is browser-only, intentionally a wide spread):

- **GitHub web file editor** — pencil → CodeMirror buffer → commit form ([editing-files docs](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files), [2025 changelog](https://github.blog/changelog/2025-09-04-improved-file-navigation-and-editing-in-the-web-ui/), [2025 community discussion](https://github.com/orgs/community/discussions/172354)).
- **Obsidian** — Ctrl+E toggle between Edit (Live Preview / Source) and Reading; ~2 s autosave ([edit-and-read docs](https://obsidian.md/help/edit-and-read), [autosave forum thread](https://forum.obsidian.md/t/saving-on-obsidian-please-explain-for-a-noob/53693)).
- **MkDocs Material** — "Edit this page" pencil delegates to GitHub/GitLab/Bitbucket ([adding-a-git-repository](https://squidfunk.github.io/mkdocs-material/setup/adding-a-git-repository/)).
- **GitBook** — Edit button opens a "change request" branch with diff/preview/merge ([editing docs](https://gitbook.com/docs/help-center/editing-content/writing-and-editing), [concepts](https://gitbook.com/docs/getting-started/concepts)).
- **Notion** — always-editable contenteditable; no edit toggle, autosave is invisible ([writing-and-editing-basics](https://www.notion.com/help/writing-and-editing-basics)).
- **VS Code Web (vscode.dev / github.dev)** — buffer in browser local storage, dirty dot, Ctrl+S, Source-Control commit ([github.dev docs](https://docs.github.com/en/codespaces/the-githubdev-web-based-editor), [unsaved-affordance pattern](https://www.waveguide.io/examples/entry/unsaved-file-affordance/), [vscode#2357](https://github.com/microsoft/vscode/issues/2357), [vscode#919](https://github.com/microsoft/vscode/issues/919)).

The remainder of this document compares all six on the five sub-questions and ends with locked-pick recommendations.

---

## 1. GitHub web file editor

**Read↔edit transition.** Pencil icon (top-right of file view). Click swaps the rendered Markdown for a CodeMirror buffer with line numbers and basic syntax coloring. As of September 2025, GitHub added an explicit "Edit options" dropdown next to the pencil so users on a non-default branch / search-result view can pick "edit on default branch" without the previously-disabled greyed-out pencil ([GitHub changelog 2025-09-04](https://github.blog/changelog/2025-09-04-improved-file-navigation-and-editing-in-the-web-ui/)). Transition is destructive in the sense that the rendered view is replaced — there is no side-by-side preview at this level (the Preview tab toggles within the editor).

**Dirty-state communication.** Weak. There is no dot, asterisk, or any indicator on the file title that says "buffer differs from disk." The user's only signal is the Commit button at the bottom becoming usable and the presence of typed characters. Closing the tab triggers the browser's generic `beforeunload` confirmation only when the buffer is non-empty in a meaningful way; the confirmation copy is browser-controlled and gives no specifics ([MDN beforeunload](https://developer.mozilla.org/en-US/docs/Web/API/Window/beforeunload_event)).

**Save trigger semantics.** Save is a two-step ceremony: scroll past the editor, find the **Commit changes…** form, write a commit message, choose direct-commit-to-default vs. open-PR-on-new-branch. Ctrl+S inside the buffer does not commit — it triggers the browser's "Save Page As…" dialog. Save is fundamentally a git operation, not a filesystem write, which is why the form exists.

**Behavior after save.** Page redirects to the file view at the new commit; the editor is dismissed. If the user committed via "create new branch + open PR," the commit form is replaced by a PR-creation page.

**Error surfacing.** Inline banners on the commit form for empty-message and branch-name validation. No structured error surface for the *content* of the edit. The most-cited content-level anti-pattern is **silent CRLF normalization**: GitHub's web editor automatically normalizes mixed line endings on commit and surfaces a one-line "We've detected the file has mixed line endings. When you commit changes we will normalize them to Windows-style" message even when the repo's `.gitattributes` and `.editorconfig` mandate LF ([community#142407](https://github.com/orgs/community/discussions/142407), [docs: configuring-git-to-handle-line-endings](https://docs.github.com/en/get-started/git-basics/configuring-git-to-handle-line-endings)). The result: a "no-op edit" that flips every line in the diff. This is the single most widely-reported failure mode for the GitHub web editor.

**Takeaway for spec_driven.** The CRLF anti-pattern is the canonical example of why a dirty computation cannot be "buffer was typed in." It must be "buffer bytes ≠ disk bytes" — at the same normalization the writer will use. The locked picks already imply this (the textarea writes through `PUT /api/file` exactly what it holds), but the validation strategy should explicitly test the round-trip.

---

## 2. Obsidian

**Read↔edit transition.** Three views: Reading (rendered HTML), Live Preview (rendered with cursor-aware raw markdown), and Source (raw markdown). Default toggle is **Ctrl+E (Cmd+E on macOS)** which flips between the active editing mode and Reading. Source ↔ Live Preview is a separate setting; users wanting Source ↔ Reading specifically use a third-party plugin or the command palette ([edit-and-read docs](https://obsidian.md/help/edit-and-read), [forum: globally-set-default-mode](https://forum.obsidian.md/t/globally-set-editors-default-mode-source-mode-live-preview-reading/48322)).

**Dirty-state communication.** Effectively none. Because the file is autosaved, "dirty" is never user-visible state. There is no asterisk, no dot, no warn-on-nav. Closing the app or window doesn't prompt; the assumption is that the disk already has the bytes.

**Save trigger semantics.** Two simultaneous mechanisms: (a) **autosave** ~2 seconds after the last keystroke and then on every detected change, (b) **manual Ctrl+S** which forces an immediate flush ([forum: saving-on-obsidian](https://forum.obsidian.md/t/saving-on-obsidian-please-explain-for-a-noob/53693), [forum: change-how-often-obsidian-writes](https://forum.obsidian.md/t/change-how-often-obsidian-writes-to-the-file-system/34340)). The 2-second debounce is documented behavior but not exposed as a user setting; a third-party "Autosave Control" plugin exists specifically to override it.

**Behavior after save.** Invisible — buffer remains live, focus stays put, no toast. Save is a non-event by design.

**Error surfacing.** Modal toast at the bottom-right of the workspace if the disk write fails (e.g., file locked by another process, permission denied). For typical happy-path edits no surface is shown.

**Takeaway for spec_driven.** Obsidian is the maximalist autosave end of the spectrum. The locked picks deliberately reject autosave (Ctrl+S only), so the borrowed pattern from Obsidian is narrow: the **Ctrl+S muscle memory works** as an immediate-flush trigger even when most editors call it "save." Obsidian users hitting Ctrl+S in spec_driven will get the result they expect.

---

## 3. MkDocs Material — "Edit this page"

**Read↔edit transition.** Pencil icon in the top-right of the rendered page **delegates** to an external editor. The link is built from `repo_url` + `edit_uri` (e.g., `edit/main/docs/`) and opens GitHub/GitLab/Bitbucket's web editor in the same or new tab. There is no in-app editing; the rendered docs site is read-only. As of recent Material releases the feature must be explicitly enabled via `theme.features: [content.action.edit, content.action.view]` ([adding-a-git-repository](https://squidfunk.github.io/mkdocs-material/setup/adding-a-git-repository/)).

**Dirty-state communication.** N/A — there is no in-app editor to be dirty. After the user clicks Edit, dirty-state ownership moves entirely to the delegated platform.

**Save trigger semantics.** N/A — the user saves on GitHub (commit form) and the Material site re-renders only after the static-site build pipeline runs.

**Behavior after save.** The rendered page does not auto-update; the user has to wait for the site rebuild and refresh.

**Error surfacing.** Errors surface inside the delegated editor (GitHub commit-form validation, branch-protection failures). MkDocs Material has no surface for them.

**Takeaway for spec_driven.** Delegated editing is the simplest possible model — no editor code, no sandbox to write, no save semantics. spec_driven explicitly rejected this option (the user wants in-app editing so a non-developer can patch a Q/A without leaving the browser). What spec_driven *can* steal: **the entry-point pattern**. A consistent ✎ Edit affordance at the top-right of the rendered file pane, identical placement everywhere, identical icon. Material made this the de facto pattern for docs sites.

---

## 4. GitBook

**Read↔edit transition.** Edit button in the top-right of the space view. Click opens a **change request** — a named branch of the content with its own editor session, plus tabs for Editor, Changes (diff), and Preview ([editing docs](https://gitbook.com/docs/help-center/editing-content/writing-and-editing), [concepts](https://gitbook.com/docs/getting-started/concepts)). The transition is heavyweight: the user is now in a versioned branch, not "editing the live page."

**Dirty-state communication.** Implicit through the change-request abstraction. The change request itself *is* the dirty state — it exists as a separate entity from main, and any edits inside it are scoped to it. The Changes tab gives a per-block diff view rather than a single "modified" badge.

**Save trigger semantics.** Continuous autosave inside the change request. The user-meaningful action is **Merge** (top-right) which folds the change request into main. Until merge, edits are persisted but not live.

**Behavior after save.** Autosave is silent; merge collapses the change request, redirects to the main view, and (depending on integration) syncs via Git to the linked repo.

**Error surfacing.** Markdown shortcuts and `/` command picker render inline as the user types; merge conflicts surface in the change-request UI as inline blockers on the Merge button. Save failures are rare because of the change-request branching model — there's nothing to conflict with on the live content.

**Takeaway for spec_driven.** GitBook represents the maximum-ceremony end of the spectrum (every edit is a versioned branch). spec_driven deliberately rejected this. The **last-write-wins decision is exactly the opposite of the change-request model**, and is appropriate for a single-user localhost app: there is no second author, no protected mainline, no review step, so the change-request abstraction would be pure overhead. What's worth borrowing: the **inline-edit / preview separation** as a future option for the Q/A structured view (per-block edit with a preview tab), should the user later want it.

---

## 5. Notion

**Read↔edit transition.** None — there is no read mode and no edit mode. Every block is `contenteditable="true"` permanently. Cursor placement and typing are the entire UX ([writing-and-editing-basics](https://www.notion.com/help/writing-and-editing-basics)). Markdown shortcuts (`**bold**`, `` `code` ``, `~strike~`, `# heading`) are converted to formatted blocks immediately on space/return.

**Dirty-state communication.** Effectively none in the canonical client. Notion does sometimes show a small "Saving…" / "Saved" status in the page header on slow networks, but it's transient and not load-bearing for the user. The mental model is "what you see is the truth."

**Save trigger semantics.** Continuous autosave on every keystroke (debounced server-side). There is no Ctrl+S; Ctrl+S in the desktop app is a no-op or, in the browser, the browser's Save Page As. Saves happen via the Notion API in the background.

**Behavior after save.** Invisible. Cursor stays put, content stays rendered.

**Error surfacing.** A red banner at the top of the workspace appears if the client loses connectivity and can't sync. Local edits are buffered until the connection returns, at which point a "Saved" indicator briefly appears.

**Takeaway for spec_driven.** Notion is the maximalist always-editable end of the spectrum. The locked picks deliberately reject this — spec_driven keeps a Reader/Editor split with an explicit ✎ toggle. This is the right call for plain markdown: a textarea showing raw markdown is unambiguous, while a contenteditable rich-text surface forces a parser/serializer round-trip and inevitable normalization drift (the same problem GitHub's CRLF normalization causes, but on every keystroke). The takeaway is **negative**: do not introduce contenteditable. Plain `<textarea>` is the right primitive for "the disk has the same bytes you typed."

---

## 6. VS Code Web (vscode.dev / github.dev)

**Read↔edit transition.** No transition. Files open directly into an editor pane that supports keyboard editing. The "view" is the editor; what would be a Reader in spec_driven is just the editor showing the content with the cursor as a light visual presence. Press `.` on any GitHub repo / PR view to launch github.dev with that repo loaded ([github.dev docs](https://docs.github.com/en/codespaces/the-githubdev-web-based-editor)).

**Dirty-state communication.** This is the canonical pattern in the industry. VS Code uses a small filled circle ("dirty dot") that replaces the close ✕ on the editor tab; the same dot appears next to the filename in the Explorer; a count badge appears on the Source Control icon in the activity bar; and the title bar of the OS window suffixes the document name with " — Modified" on some platforms ([waveguide unsaved-affordance](https://www.waveguide.io/examples/entry/unsaved-file-affordance/)). Multiple redundant signals at multiple zoom levels.

The dirty computation is **content-based**, not modification-flag-based. Issue [vscode#919](https://github.com/microsoft/vscode/issues/919) explicitly debated this: the team distinguishes "user input initiated a change that round-trips to identity" (acceptable to mark dirty) from "plugin reformat produced no actual change" (must NOT mark dirty). The canonical complaint was that auto-formatters shouldn't dirty an unmodified file. This is the deep-equality dirty-computation pattern.

**Save trigger semantics.** Ctrl+S writes the buffer to the VS Code virtual file system, which (in vscode.dev / github.dev) writes to **browser local storage** rather than directly to the git remote ([github.dev docs](https://docs.github.com/en/codespaces/the-githubdev-web-based-editor)). The user *also* needs to commit via the Source Control view to push to git. Saving and committing are decoupled — Ctrl+S persists the byte-level edit; commit publishes it.

**Behavior after save.** Dot disappears from tab and Explorer; Source Control diff updates to reflect the saved-but-uncommitted file. Buffer remains open, cursor remains in place. **This is exactly the "stay in editor" semantic the spec_driven interview locked.**

**Error surfacing.** A modal "Failed to save" toast at the bottom-right with the underlying error string (quota exceeded, lost remote, file locked). Source-control errors (push rejected, merge conflict) appear in the Source Control panel with inline action buttons. Multiple severity tiers: status-bar inline for per-file warnings, modal toast for blocking errors, problems panel for per-file diagnostics.

**Takeaway for spec_driven.** VS Code Web is the closest prior-art match to the locked picks. The spec_driven editor should adopt the dot-on-title pattern verbatim and the deep-equality dirty computation. The two-step save model (save = local storage, commit = remote) does *not* apply because spec_driven writes through to the filesystem directly — there is only one tier.

---

## Cross-cut summary table

| System | Read↔Edit | Dirty signal | Save trigger | After save | Error surface |
|---|---|---|---|---|---|
| GitHub web | Pencil → CodeMirror | None on title; Commit button enables | Commit form (2-step) | Redirect to file view | Inline banner; CRLF-normalize footgun |
| Obsidian | Ctrl+E (LP/Source ↔ Read) | None (autosave) | ~2s autosave + Ctrl+S | Stays in view | Toast on disk error |
| MkDocs Material | Pencil → external editor | N/A | N/A (delegated) | N/A | N/A |
| GitBook | Edit → change request | Implicit (CR exists) | Autosave + explicit Merge | Redirect to main | Inline merge conflicts |
| Notion | None (always editable) | Tiny "Saving…" tag | Continuous autosave | Invisible | Red banner on disconnect |
| VS Code Web | None (always editor) | Dot on tab + Explorer + status bar | Ctrl+S → local storage; commit separately | Stay in editor | Modal + Problems panel |

---

## Recommendations for spec_driven (locked picks)

The interview locked simplicity. These recommendations keep that simplicity while inheriting the patterns that make VS Code Web's similar simplicity work, and explicitly avoid the GitHub web editor's normalization footgun.

### R1 — Adopt VS Code's dot-on-title dirty indicator verbatim, plus a status-bar mirror

In the file pane title bar, render the filename as `● <filename>` while dirty (filled circle, single character of left padding, replacing nothing). Mirror it in the sidebar tree as `● filename.md`. Optionally show a "● unsaved changes" string in a small status bar at the bottom of the editor. Multiple redundant signals at different zoom levels is the explicit VS Code design rationale ([waveguide unsaved-affordance](https://www.waveguide.io/examples/entry/unsaved-file-affordance/)) and adds essentially zero implementation cost over a single signal.

### R2 — Compute dirty via deep equality (`buffer === lastSavedBuffer`), not a modification flag

This sidesteps the GitHub-web CRLF anti-pattern. Cache the exact bytes that were written (or read) most recently and recompute dirty as `JSON.stringify(buffer) !== JSON.stringify(savedSnapshot)` (or, more efficiently, plain `===` on stable strings) on every keystroke. Specifically: a user who types "X", then deletes "X", should see the dot disappear; a load-then-no-edit-then-Ctrl+S should be a no-op write or be skipped entirely. This is the resolution direction in [vscode#919](https://github.com/microsoft/vscode/issues/919) and the inverse of GitHub's "commit anything we touched" model.

### R3 — Do not normalize line endings, byte-encoding, or trailing newlines on save

The textarea's `.value` is the byte stream. Send it through `PUT /api/file` unchanged. The backend writes bytes-as-received. No `\r\n` ↔ `\n` swap, no UTF-8 BOM injection, no trailing-newline ensure. This makes deep-equality dirty computation honest and avoids the "every line changed" diff pathology documented in [GitHub community#142407](https://github.com/orgs/community/discussions/142407). The validation strategy must include a round-trip test: load → no edits → Ctrl+S → diff = empty.

### R4 — Use the browser's `beforeunload` event for warn-on-nav, scoped to dirty=true

Register a `beforeunload` listener only while dirty; remove it on save / discard / close-editor. This is the [MDN-recommended](https://developer.mozilla.org/en-US/docs/Web/API/Window/beforeunload_event) pattern and avoids Firefox's bfcache penalty. Since spec_driven is an SPA, also intercept React Router navigation (router-level "Are you sure?" modal) for in-app navigation, since `beforeunload` does not fire on client-side route changes. Two surfaces, one source of truth (`isDirty`).

### R5 — Ctrl+S handler must `preventDefault()` before the fetch

The browser's default Ctrl+S is "Save Page As…" — useless and disruptive. Capture it inside the editor pane only (focus-scoped listener or a top-level listener that checks the active editor exists). Then call `PUT /api/file` with the buffer, on 2xx update `lastSavedBuffer = buffer` (which clears the dot), keep focus on the textarea, retain cursor position. This matches the locked "stay in editor" semantic and the VS Code Web behavior.

### R6 — Persistent inline error banner on save failure (not a toast)

Toasts vanish; for a spec_driven user who is mid-thought, a vanished error is worse than a noisy one. On `PUT /api/file` failure (4xx/5xx), render a non-dismissible banner at the top of the editor pane with the HTTP status, a one-line human cause ("file is 11 MB, cap is 10 MB"), and a Retry button. Keep the banner mounted until the next successful save or a Discard. This is closer to VS Code's Problems-panel discipline than to Obsidian's toast. The 10 MB cap means 413 is a real error path that needs a clear surface.

### R7 — Surface the conflict-policy implication once, then never again

Last-write-wins is the locked policy. The first time a user opens the editor in a fresh session, surface a small one-time tooltip/footer note: "Saves overwrite the file on disk. If another tool wrote to it while you were editing, your save still wins." Don't show it on every save (that would be noise), and don't ask for confirmation on save (that would re-introduce the ceremony last-write-wins is meant to avoid). This trades a one-time onboarding cost for a clear mental model, mirroring how GitBook makes its change-request model explicit at first encounter.

### R8 — Keep textarea controls minimal: Save / Discard / Close — and surface their state

Three buttons next to the dot indicator, each with explicit enabled/disabled state derived from dirty:

- **Save** — enabled iff dirty. Highlighted (primary color) iff dirty. Tooltip "Ctrl+S".
- **Discard** — enabled iff dirty. Reverts buffer to `lastSavedBuffer`, clears dot.
- **Close editor** — always enabled. If dirty, opens the same beforeunload-style confirm; otherwise exits to view.

This is the smallest control surface that covers every state transition the locked picks require and matches the discipline Obsidian users already have from Ctrl+S muscle memory and GitHub users have from the Commit button being the only "real" action.

---

## Open questions / not researched

- **Cursor preservation on save.** All major editors (VS Code, Obsidian) preserve cursor position and selection range across a save. This is implicit in "stay in editor" but not exhaustively specified. Stage 4 should decide whether spec_driven preserves cursor + scroll on save (recommended yes) or resets after the buffer-refresh round-trip.
- **Q/A structured-view dirty propagation.** The structured Q/A view edits per-block but writes the whole file. How do the per-block dirty dots and the file-level dirty dot interact? Out of scope for this angle; raised for the qa-view angle / spec.
- **Performance ceiling of textarea at 10 MB.** A `<textarea>` rendering ~10 MB of plaintext is rare but legal under the locked cap. Browser-level text-input perf at that size was not benchmarked. May need a lazy-mount or warning-banner-at-N-MB pattern; not researched here.
- **Mobile/touch.** spec_driven's deployment is localhost-only, but if accessed from a tablet the textarea + Ctrl+S model breaks. Out of scope.
- **Concurrent same-user-multiple-tabs editing.** Last-write-wins applies cross-tool, but two open editor tabs of the same file in spec_driven itself produce a stale-buffer bug nobody asked about. Out of scope; flagging.
- **Accessibility of the dot indicator.** A filled circle is visual-only. Screen-reader text ("file modified, unsaved changes") and aria-live regions are standard practice; specific WCAG-conformant implementation patterns were not researched here.
- **Undo across save.** VS Code preserves undo history across a save by default. Whether the spec_driven textarea preserves undo history (browser-default behavior generally does) was not verified.

## Sources

- [Editing files - GitHub Docs](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files)
- [Improved file navigation and editing in the web UI - GitHub Changelog (2025-09-04)](https://github.blog/changelog/2025-09-04-improved-file-navigation-and-editing-in-the-web-ui/)
- [Improved file navigation and editing - community discussion #172354](https://github.com/orgs/community/discussions/172354)
- [GitHub should not automatically change line endings - community discussion #142407](https://github.com/orgs/community/discussions/142407)
- [Configuring Git to handle line endings - GitHub Docs](https://docs.github.com/en/get-started/git-basics/configuring-git-to-handle-line-endings)
- [The github.dev web-based editor - GitHub Docs](https://docs.github.com/en/codespaces/the-githubdev-web-based-editor)
- [VS Code issue #2357: unsaved file marker should appear when buffer != disk](https://github.com/microsoft/vscode/issues/2357)
- [VS Code issue #919: don't activate dirty indicator if state matches previous written state](https://github.com/microsoft/vscode/issues/919)
- [Unsaved File Affordance - VS Code UX pattern (Waveguide)](https://www.waveguide.io/examples/entry/unsaved-file-affordance/)
- [Views and editing mode - Obsidian Help](https://obsidian.md/help/edit-and-read)
- [Obsidian forum: "Saving" on Obsidian — please explain](https://forum.obsidian.md/t/saving-on-obsidian-please-explain-for-a-noob/53693)
- [Obsidian forum: change how often Obsidian writes to the file system](https://forum.obsidian.md/t/change-how-often-obsidian-writes-to-the-file-system/34340)
- [Obsidian forum: globally set editor's default mode](https://forum.obsidian.md/t/globally-set-editors-default-mode-source-mode-live-preview-reading/48322)
- [MkDocs Material - Adding a git repository (edit-this-page)](https://squidfunk.github.io/mkdocs-material/setup/adding-a-git-repository/)
- [GitBook docs - Editing](https://gitbook.com/docs/help-center/editing-content/writing-and-editing)
- [GitBook docs - Concepts](https://gitbook.com/docs/getting-started/concepts)
- [Notion - Intro to writing & editing](https://www.notion.com/help/writing-and-editing-basics)
- [MDN - Window: beforeunload event](https://developer.mozilla.org/en-US/docs/Web/API/Window/beforeunload_event)
