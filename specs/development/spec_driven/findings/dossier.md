# Findings dossier — spec_driven

Run: spec_driven-20260503-145859 (autonomous full-pipeline regen, parent-direct synthesis from 4 parallel researcher subagent outputs)

## Angles researched

1. **prior-art-readonly-viewers** — sidebar+main-pane patterns for hybrid file-viewer SPAs (GitHub web, github.dev, VS Code Web, Obsidian, MkDocs Material, GitBook, Notion read-mode).
2. **markdown-editor-ux** — in-place editing affordances for non-developer users (textarea vs split-pane vs CodeMirror, autosave vs explicit save, dirty indicators, structured-block editing, conflict handling).
3. **localhost-fs-sandbox-risks** — sandbox-escape and CSRF traps for a localhost FastAPI file-server with PUT, on Windows + POSIX.
4. **copypaste-prompt-ux** — how production tools (Cursor, Aider, Continue, Spec Kit, AGENTS.md/Codex, Junie, Claude Code plan mode) signal mode and structure copy-paste LLM prompts.

## Cross-cutting insights

- **Tree shape and consumer-walk discipline are the same problem** *(prior-art-readonly-viewers + markdown-editor-ux)*. Every survey'd viewer ships a recursive `{name, path, type, children}` tree fetched in one shot — confirms FR-7 / FR-8's uniform `children` choice. The class-of-bug from run `spec_driven-20260502-clean` (backend `task_type.projects` vs frontend `node.children`) is exactly what the survey'd tools avoid by uniform descent.
- **Edit/save model is governed by what the file IS, not by user preference** *(markdown-editor-ux + prior-art-readonly-viewers)*. When the file is canonical input downstream stages read (git, MkDocs, our regen pipeline), explicit-save + dirty dot + Ctrl+S + `beforeunload` is the convergent pattern (GitHub web, VS Code Web, MkDocs "Edit this page"). When it's user-private notes, autosave wins (Notion, StackEdit). spec_driven artifacts are the former — the existing explicit-save model is correct; do NOT drift toward Notion-style autosave.
- **Parse-failure fallback is "raw text + inline banner," not blank-page or alert** *(prior-art-readonly-viewers + markdown-editor-ux + copypaste-prompt-ux)*. YAML frontmatter is the dominant failure point across the surveyed tools (foam, copilot-cli, opencode trackers cite it). The existing `QaErrorBoundary` (AC-25) IS the converged pattern; generalize it across every render component (CodeView, JsonlView, ImagePlaceholder, MarkdownView).
- **"Localhost-only" is NOT equivalent to "safe-from-the-browser"** *(localhost-fs-sandbox-risks)*. DNS rebinding and CSRF both reach `127.0.0.1` services. Strict `Origin` + `Host` allowlists, IPv4-only `127.0.0.1` bind (never `0.0.0.0`), `Content-Disposition: attachment` + `X-Content-Type-Options: nosniff` on every read, exact-extension allowlist, hard size cap — these are not optional, even with no auth.
- **Mode-signaling via literal H1 directive is novel but on-pattern for parser-free Markdown** *(copypaste-prompt-ux)*. Cursor `.mdc` uses YAML frontmatter, OpenAI Model Spec uses channel hierarchy, Junie uses a UI toggle. None are right for copy-paste flows that have no parser. AGENTS.md / Codex CLI sets the precedent: parser-free Markdown with prose directives. The `# EXECUTION MODE: AUTONOMOUS / INTERACTIVE` H1 is the right shape — but the spec should capture *why* (citing AGENTS.md being parser-free, Cursor frontmatter requiring tool support) so the convention isn't migrated later.
- **"Inline everything, never truncate, warn loudly" is the converged copy-paste prompt model** *(copypaste-prompt-ux + markdown-editor-ux)*. Cursor inlines rules into system prompts; Codex CLI concatenates AGENTS.md top-down with later wins; Continue.dev `.prompt` bodies inline verbatim. No mainstream tool hard-truncates copy payloads silently. FR-14c's 50 KB warn / 1 MB hard-413 ceiling is on-pattern; Build-prompt → Copy UI from follow-up 002 (inline visible block, header bar with title + Wrap toggle + prominent Copy) matches PatternFly / Cloudscape / Flowbite design-system guidance.

## Per-angle highlights

### prior-art-readonly-viewers
- Convergent sidebar shape: recursive `{name, path, type, children}` fetched in one shot; no per-node lazy fetch (GitHub web, github.dev, VS Code Web, Obsidian).
- Breadcrumb lives ABOVE the main pane (not inside the sidebar) with current crumb as `aria-current="page"` plain text.
- Per-extension render dispatch with `README.md` / `index.md`-as-section-page (MkDocs `navigation.indexes`).
- Keyboard nav floor = VS Code's `Cmd/Ctrl+Shift+E → arrows → Enter`. Obsidian community ships ≥3 replacement explorers because default lacks j/k.
- Deep-link contract: github.dev's host-swap pattern + MkDocs `navigation.tracking` (URL hash follows active heading) define the bookmarkability ceiling.

### markdown-editor-ux
- Dirty-state convention: dot in toolbar + `*` in document title (VS Code, Obsidian, GitHub web). Match this verbatim — users have it in muscle memory.
- Per-block / structured editing (Notion, GitBook, CodeMirror rich-Markdoc) is convergent for nested data BUT every editor ships a verbatim-source escape hatch alongside. Keep BOTH per-Q/A pencils AND the whole-file textarea — that dual mode IS the production pattern.
- Concurrency check on `PUT /api/file`: `If-Unmodified-Since` or `If-Match: <sha>` returning **409** with a reload banner is the convergent guard against "I edited the file in VS Code while the webapp was open."
- Persistent inline banners > toasts for save errors (AWS Cloudscape "communicating unsaved changes" guidance — toasts disappearing mid-recovery is the documented anti-pattern).

### localhost-fs-sandbox-risks
- **Vite CVE-2025-62522** — trailing-backslash bypass on Windows. Mitigation: canonicalize via `realpath` AND re-verify the base prefix; reject literal `\`, `:`, NUL byte, percent-encoded `../`, trailing `/`/`\`.
- **CWE-22** path traversal family: probe sets must include `..`, absolute paths, percent-encoded variants, mixed slash directions.
- **Windows reserved device names**: CON, PRN, AUX, NUL, COM1-9, LPT1-9 — all collapse to single 404.
- **NTFS Alternate Data Streams** (`file.md::$DATA`), **8.3 short names** (`PROGRA~1`), **POSIX symlinks / Windows junctions** — all single 404.
- **DNS rebinding**: `Host: 127.0.0.1.evil.com` reaches a localhost service via DNS rebind. Strict `Host` allowlist mandatory, NOT optional.
- **Origin/Host validation under reverse proxies**: per follow-up 006, dev-server proxy must rewrite `Origin` to bound origin; backend trust list stays narrow.
- **Defense-in-depth on the read path**: `X-Content-Type-Options: nosniff` + `Content-Disposition: attachment` for every `GET /api/file`. Recommended: refuse symlinks outright (since EXPOSED_TREE is curated) rather than `realpath`-and-re-verify.

### copypaste-prompt-ux
- Literal `# EXECUTION MODE: AUTONOMOUS` / `INTERACTIVE` H1 directive — novel but right for parser-free Markdown copy-paste flows. Cite AGENTS.md / Codex CLI as the precedent.
- Inline-everything is the norm: Cursor inlines rules into system prompts, Codex concatenates AGENTS.md top-down, Continue.dev `.prompt` bodies inline verbatim. FR-14c's plan to inline `revised_prompt.md` + each non-empty `<stage>/promoted.md` + every `follow_ups/*.md` filename is on-pattern.
- Recommended section ordering for assembled prompts: mode header → intent line → revised prompt → follow-ups → per-stage modules + pinned items → regeneration contract verbatim → output contract.
- Build-prompt → Copy UI: inline visible bordered block (no inner `<details>`), header bar with title + Wrap toggle (default ON) + prominent Copy button with transient "Copied!". Matches PatternFly / Cloudscape / Flowbite design-system guidance verbatim. No mainstream tool hard-truncates copy payloads silently.
- Add: byte/line count chip near the header, soft yellow warning above ~100 KB, never block Copy, Ctrl/⌘-C inside the block copies the entire payload.

## Recommendations for the spec

1. **Lock the recursive `{name, path, type, children}` tree shape** — FR-7/FR-8/AC-3 already do this; consumer-walk test from `agent_refs/validation/development.md` move 2 enforces it.
2. **Keep the explicit-save model**, name the dirty indicator (dot in toolbar + `*` in document title), persistent inline error banner not toast.
3. **Add a 409 conflict path on `PUT /api/file`** with `If-Unmodified-Since` mtime header; on conflict, return 409 + a reload banner. (New: FR-7b.)
4. **Generalize parse-fallback Error Boundary across every render component**, not just QaView. (New: FR-41-fallback applies to MarkdownView / CodeView / JsonlView / ImagePlaceholder.)
5. **Sandbox check matrix**: every probe in the localhost-fs-sandbox-risks angle MUST appear in `validation/security.md` SEC-* with CWE/CVE citations.
6. **Origin/Host gate**: dev-server proxy contract from follow-up 006 stays load-bearing — backend allow-list does NOT widen to dev port; Vite proxy rewrites Origin/Host. SYS-16b is the multi-mode parity check.
7. **Copy-paste prompt UX**: keep the inline visible block + header-bar Copy + soft-wrap toggle + section-breakdown line + size-warning banner. Add a byte/line count chip near the Copy button if not already present.
8. **Capture the `# EXECUTION MODE` H1 rationale** in the spec or in `CLAUDE.md` (AGENTS.md / Codex CLI precedent) so the convention isn't migrated later.

## Open questions surviving research

- **Concurrency on `PUT /api/file`**: which header — `If-Unmodified-Since` (RFC 7232 mtime semantics) vs `If-Match` (sha-based ETag)? Different complexity tradeoffs.
- **Per-block edit conflict policy** for `interview/qa.md`: does a single Q-edit invalidate other in-flight Q-edits, or do they merge? The angle research didn't resolve this; defer to interactive interview.
- **Soft-wrap toggle persistence**: explicitly NOT in localStorage per follow-up 002, but the angle survey shows users find it jarring when their preference resets across panel opens. Worth re-confirming with the user in a future round.
- **Extension allowlist for `PUT`** vs `GET`: image extensions (`.png`/`.jpg`) read OK but writes return 415. Should `.svg` ever be in the allowlist (NFR-9 says no — code-execution vector)? Confirmed.
- **IPv6 `[::1]`**: uvicorn binds IPv4-only in v1; the localhost-fs-sandbox-risks angle confirms this is acceptable but flags it for v2 if ever the bind changes.

(Pinned-item check: no `findings/promoted.md` existed at run start; nothing to preserve verbatim.)
