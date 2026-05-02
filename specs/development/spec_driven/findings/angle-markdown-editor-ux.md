# Angle: In-place Markdown Editor UX (Comparative)

## Scope

spec_driven adds an in-place markdown editor to its viewer for pipeline artifacts. The interaction surface is small but each detail has prior art. This angle compares six widely-used products on five dimensions:

1. Read↔Edit transition (how the user enters/exits the editor)
2. Dirty-state communication (how unsaved changes are signalled)
3. Save-trigger semantics (auto vs explicit; Ctrl+S vs commit form)
4. Behavior after save (close vs stay)
5. Error surfacing (toast vs modal vs inline banner)

Six products reviewed: GitHub web file editor, Obsidian, MkDocs Material's "Edit this page", GitBook, Notion, and VS Code Web (vscode.dev / github.dev).

---

## 1. GitHub web file editor

**Read↔Edit transition.** A pencil (✎) icon sits in the upper-right of the file view. Clicking it swaps the rendered view for a CodeMirror-backed text editor, with a "Preview" tab to flip back to rendered mode without leaving edit ([GitHub Docs — Editing files](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files)). It is a hard mode flip (read view is replaced, not augmented), unlike Notion's contenteditable.

**Dirty-state communication.** The dirty signal is implicit — the editor stays in edit mode and the "Commit changes…" button becomes the only way out. There is no per-tab dot. A "Cancel" link discards.

**Save trigger.** Save is **explicit** and **gated by a commit form**: commit message, optional description, author email selector, and a "commit directly to branch" vs "create a new branch and start a pull request" choice ([GitHub Docs — Editing files](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files)). Ctrl+S in the editor surface does **not** commit; it is intercepted by the browser unless the page handler binds it (GitHub's web editor historically has not bound it to the commit action).

**Behavior after save.** On commit, GitHub navigates **away** from edit mode back to the rendered file view at the new commit SHA. The editor is closed; reopening requires another pencil click.

**Error surfacing.** Server-side validation (e.g., branch protection, conflicting edit) is shown as an inline banner above the commit form, with the form preserved so the user can retry.

**Anti-pattern of note: CRLF line-endings.** GitHub's web editor / merge UIs are known to silently convert content to CRLF on Windows-typed input, including commit messages, which then break tools like `git subtree` that grep with LF assumptions ([GitHub Community discussion #84731](https://github.com/orgs/community/discussions/84731)). The lesson for spec_driven: **never normalize line-endings on save without telling the user, and compute "dirty" against the canonical on-disk bytes** so a no-op edit doesn't look modified.

---

## 2. Obsidian (desktop)

**Read↔Edit transition.** Three modes exist — Source, Live Preview, Reading — toggled via Cmd/Ctrl+E or the eye/pencil button in the pane header ([Obsidian forum — Ctrl+E toggle behavior](https://forum.obsidian.md/t/ctrl-e-toggle-preview-loses-cursor-focus/157)). The toggle is **per-pane**, fast, and preserves scroll position. Live Preview is itself an editable mode, so most users rarely leave edit at all.

**Dirty-state communication.** Obsidian uses **autosave** to disk on a short debounce; the file is the source of truth. Because of this, there is **no traditional dirty dot** — the contract is "what you see is on disk within seconds." A subtle unsaved indicator can appear briefly while the debounce flushes.

**Save trigger.** **Implicit autosave** on debounce. Ctrl+S exists and forces an immediate flush, but is rarely required.

**Behavior after save.** Stay in mode. The edit↔preview toggle is orthogonal to save; switching to preview does not implicitly "commit" anything because everything is already saved.

**Error surfacing.** Local FS errors show as toast notifications in the lower-right; sync conflicts (with Obsidian Sync) surface as a modal merge dialog. Obsidian deliberately avoids blocking the editor on errors — typing continues into the buffer.

---

## 3. MkDocs Material — "Edit this page"

**Read↔Edit transition.** A pencil button on each rendered page links to the source file in the upstream repo via `edit_uri` (e.g., `edit/main/docs/page.md`); the click navigates the user **out of the docs site** to GitHub/GitLab/Bitbucket's web editor ([Material for MkDocs — Adding a git repository](https://squidfunk.github.io/mkdocs-material/setup/adding-a-git-repository/)). This is a **delegated** edit pattern: the docs site itself is read-only, editing is someone else's problem.

**Dirty-state communication.** N/A — delegated.

**Save trigger.** Whatever the upstream forge does (typically GitHub's commit form, see §1).

**Behavior after save.** User lands back in the forge UI; the published site only updates after the next build pipeline runs.

**Error surfacing.** Delegated.

**Lesson for spec_driven.** Delegation is the simplest design but it forfeits the appeal of a unified app. spec_driven's brief explicitly wants in-place editing, so this pattern is rejected — but it sets a useful "do nothing" baseline against which any in-place complexity must justify itself.

---

## 4. GitBook (web editor, change-request model)

**Read↔Edit transition.** An **Edit** button in the top-right opens a *change request* — a branched copy of the page on which edits are made ([GitBook Docs — Change requests](https://gitbook.com/docs/collaboration/change-requests)). The rendered view is replaced by a WYSIWYG block editor.

**Dirty-state communication.** Edits autosave to the change request branch ("Your changes are saved automatically, and other people can join you in a change request to collaborate in real-time" — [GitBook Docs](https://gitbook.com/docs/collaboration/change-requests)). The branch itself is the dirty marker; the main branch is unchanged until merge.

**Save trigger.** **Two-tier**: implicit autosave to the branch, plus an explicit "Request a review" / "Merge" action to publish.

**Behavior after save (autosave tier).** Stay in editor; collaboration cursors keep working.

**Behavior after merge.** GitBook closes the change request and returns to the published page.

**Error surfacing.** GitBook's docs do not enumerate error UI in detail, but the operative pattern is "edits keep working locally; merge is a separate gated action." Conflicts surface at merge time, not at typing time.

**Lesson for spec_driven.** A two-tier model (autosave to a draft, explicit publish) is overkill for editing your own pipeline artifact files, but it confirms that **separating "saved" from "published" reduces the cost of mistakes**. spec_driven doesn't need branches — but it should make Save cheap and reversible (the file's prior content can be re-fetched on demand).

---

## 5. Notion

**Read↔Edit transition.** **There is no transition** — every block is `contenteditable` from the moment the page loads. Notion's editor implementation uses a per-paragraph contenteditable line, similar to Quip ([How to Build a Text Editor Like Notion — Konstantin](https://konstantin.digital/blog/how-to-build-a-text-editor-like-notion)). The "always-editable by default" stance is intentional; a Notion engineer noted on Hacker News that "content locks and editing friction \[are\] *very* annoying" and that the real problem is "accidental edits" rather than the model itself ([HN — Notion engineer comment](https://news.ycombinator.com/item?id=25521937)).

**Dirty-state communication.** Notion shows a small sync indicator near the page title while writes are in flight; otherwise the UI carries no dirty state because there is no "saved vs unsaved" distinction by design.

**Save trigger.** **Pure autosave** via continuous cloud sync ([Notion Help — Common Notion error messages](https://www.notion.com/help/notion-error-messages)).

**Behavior after save.** Stay in editor — there is nothing else to be in.

**Error surfacing.** Notion documents user-visible error strings such as "There was an issue persisting your edits", "Cannot save changes", and "Storage operation did not complete" ([Notion Help — Common Notion error messages](https://www.notion.com/help/notion-error-messages)). These appear as **persistent banners/toasts at the top of the page** rather than blocking modals; editing continues into the local buffer while Notion retries. The "Offline" banner surfaces when network is lost so users know writes are queued, not lost.

**Lesson for spec_driven.** Notion's hard rule — **never block the editor on a save error; show a persistent banner that survives until the next successful save** — is the right pattern when the user might lose typing, and it's exactly what the brief calls for.

---

## 6. VS Code Web (vscode.dev / github.dev)

**Read↔Edit transition.** No transition — VS Code is an editor first, viewer second. Markdown files open editable with a "Preview" command (Ctrl+Shift+V) for the rendered view in a side tab.

**Dirty-state communication.** A **filled dot** replaces the close ✕ on the tab when the buffer differs from disk ([VS Code issue #2357 — dirty marker semantics](https://github.com/microsoft/vscode/issues/2357), [VS Code issue #919 — dirty matching written state](https://github.com/microsoft/vscode/issues/919)). The convention is industry-standard and the visual primitive other tools (Sublime, Atom, IntelliJ) share. Issue #919 is a long-standing request that VS Code clear the dot when buffer content matches the previous written state — i.e., **deep-equality dirty computation** rather than "any keystroke flips dirty true" — and the request is acknowledged but unresolved.

**Save trigger.** **Ctrl+S** (Cmd+S on macOS). On `vscode.dev`/`github.dev`, Ctrl+S **saves to in-browser virtual FS / browser local storage**, not to the remote git repo; commit-and-push is a separate action in the Source Control view ([GitHub Docs — github.dev web editor](https://docs.github.com/en/codespaces/the-githubdev-web-based-editor)). This two-tier semantics is similar to GitBook's autosave-then-publish but is keyboard-driven for the first tier.

**Behavior after save.** Stay in editor. The dot disappears; cursor and selection are preserved.

**Error surfacing.** Save errors raise a toast/notification in the lower-right corner; persistent errors appear as items in the status bar (red badge) and in the Problems panel. Critical write failures show a modal only when user choice is required (e.g., "File on disk has changed — overwrite?").

**Lesson for spec_driven.** The dirty-dot convention is the most copied affordance in any text editor and should be adopted verbatim. Ctrl+S as save shortcut is also universal; binding it inside the textarea (and `preventDefault` on the browser default) is a one-liner that pays back the muscle memory of every developer user.

---

## Synthesis matrix

| Product | Read↔Edit | Dirty signal | Save trigger | After save | Error surfacing |
|---|---|---|---|---|---|
| GitHub web editor | Hard mode flip via ✎ | Implicit (form open) | Explicit commit form | Closes editor, returns to view | Inline banner above form |
| Obsidian | Pane toggle (Ctrl+E) | Brief flush indicator | Autosave (debounce) | Stay | Toast (FS), modal (sync conflict) |
| MkDocs Material | Delegated to forge | N/A | N/A | N/A | N/A |
| GitBook | Edit button → change request | Branch is the dirty marker | Two-tier: autosave + merge | Stay (autosave); close (merge) | Inline at merge time |
| Notion | None — always editable | Sync indicator near title | Pure autosave | Stay | **Persistent banner** + offline mode |
| VS Code Web | None — already editor | **Filled-dot on tab** | **Ctrl+S** to virtual FS; commit separate | Stay; dot clears | Toast + status bar + Problems panel |

---

## Recommendations for spec_driven's editor

1. **Adopt the VS Code dirty-dot convention** at the per-file level. The "✎ Edit" toggle for a file that has unsaved changes should render with a filled dot or asterisk next to the filename in the sidebar tree and at the top of the editor pane. This is the most-recognized affordance in the entire editor ecosystem (VS Code, Sublime, IntelliJ, Atom) and costs nothing to implement.

2. **Compute dirty via deep equality against the last-saved buffer**, not via "any keystroke since edit-mode opened." This is exactly the long-running ask in [VS Code issue #919](https://github.com/microsoft/vscode/issues/919) and sidesteps the GitHub-web-editor anti-pattern where invisible CRLF normalization makes a no-op save look like a real change ([GitHub Community #84731](https://github.com/orgs/community/discussions/84731)). Concretely: store `originalText` when the textarea opens; `isDirty = currentText !== originalText`; refresh `originalText` on successful save.

3. **Stay in the editor after a successful save.** Don't auto-collapse the textarea. Users following the brief's "Save / Discard / Close-editor + Ctrl+S" four-action vocabulary expect Save to be cheap and repeatable, so the editor must remain mounted, the cursor preserved, and the dirty dot cleared. Closing is a separate user-initiated action ("Close editor" button), matching VS Code Web and Notion.

4. **Use a persistent inline banner for save errors, not a transient toast.** Match Notion's pattern: surface the error string above the textarea, keep it visible until the next successful save (or explicit dismiss), and **never block typing** ([Notion Help — error messages](https://www.notion.com/help/notion-error-messages)). Toasts that auto-dismiss are wrong here because the user may have walked away after Ctrl+S — a banner survives a tab-switch.

5. **Bind Ctrl+S inside the textarea with `preventDefault` to trigger Save.** The shortcut is universal across desktop apps and is the dominant save trigger in VS Code Web ([GitHub Docs — github.dev](https://docs.github.com/en/codespaces/the-githubdev-web-based-editor)). Match the OS convention: Cmd+S on macOS via the same `event.metaKey || event.ctrlKey` handler.

6. **Treat the textarea as the single source of truth while open**; render the markdown preview from the in-memory buffer, not from disk. This mirrors Obsidian's Live Preview and Notion's contenteditable: there is no point at which "what you see" diverges from "what you'd save." It also makes the dirty-equality check in (2) trivially correct.

7. **Discard should require a confirmation only if dirty.** When the buffer matches disk (dirty=false), the Discard button is a no-op and can be hidden or disabled. When dirty, a one-click Discard with a confirm dialog is sufficient — no need for a multi-step undo. This matches VS Code's "Revert File" behavior and avoids GitBook-style ceremony for what is, in spec_driven, a single-user local-first edit.

8. **Skip the "two-tier save → publish" pattern.** GitBook's change-request model and github.dev's "save to browser, then commit" model both add a second step that does not pay back here. spec_driven artifacts are local files; Save writes to disk directly. The simpler one-tier flow matches Obsidian and the user's mental model for editing project files.

---

## Open questions / not researched

- **Concurrent multi-tab editing of the same file.** None of the six products were probed on this; spec_driven may need a "file changed on disk" check (VS Code does this via filesystem watcher and prompts). Out of scope for this angle.
- **Mobile/touch keyboard behavior** for Ctrl+S substitutes. Not investigated; assumed desktop browser primary target.
- **Accessibility of the dirty dot** for screen readers. VS Code uses an accessible label ("Modified") on the tab; spec_driven should mirror but the exact ARIA pattern was not researched here.
- **Undo-stack persistence across save.** VS Code preserves undo history past save; the brief is silent on whether spec_driven's textarea must preserve history beyond the native browser textarea behavior. Not researched.
- **Performance of deep-equality dirty check on large files.** For a 1MB markdown file, a string equality check is sub-millisecond in practice but was not benchmarked. If spec_driven artifacts grow beyond ~10MB, a hash-based check may be warranted.
- **Notion's exact UI treatment of "Cannot save changes"** (banner vs toast vs both) was not directly observed because Notion's docs describe the strings but not their presentation. The recommendation in (4) treats "persistent banner" as the goal regardless of what Notion specifically renders.

## Sources

- [GitHub Docs — Editing files](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files)
- [GitHub Community discussion #84731 — CRLF in web-interface commit messages](https://github.com/orgs/community/discussions/84731)
- [Obsidian forum — Ctrl+E toggle behavior](https://forum.obsidian.md/t/ctrl-e-toggle-preview-loses-cursor-focus/157)
- [Material for MkDocs — Adding a git repository](https://squidfunk.github.io/mkdocs-material/setup/adding-a-git-repository/)
- [GitBook Docs — Change requests](https://gitbook.com/docs/collaboration/change-requests)
- [How to Build a Text Editor Like Notion — Konstantin](https://konstantin.digital/blog/how-to-build-a-text-editor-like-notion)
- [Hacker News — Notion engineer (jitl) on always-editable design](https://news.ycombinator.com/item?id=25521937)
- [Notion Help — Common Notion error messages](https://www.notion.com/help/notion-error-messages)
- [VS Code issue #2357 — dirty marker semantics](https://github.com/microsoft/vscode/issues/2357)
- [VS Code issue #919 — dirty indicator should match previous written state](https://github.com/microsoft/vscode/issues/919)
- [GitHub Docs — github.dev web-based editor](https://docs.github.com/en/codespaces/the-githubdev-web-based-editor)
