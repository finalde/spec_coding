# Findings dossier — spec_driven

Run: spec_driven-20260502-clean
Stage: 3 (Research) — clean-state regeneration
Compiled by: parent (agent_team skill, parent_direct synthesis under EXECUTION MODE: AUTONOMOUS) on 2026-05-02
Inputs read: `user_input/revised_prompt.md`, `interview/qa.md`, `CLAUDE.md`, `.claude/agents/agent_team__research_manager.md`, plus the six `angle-*.md` files written by parallel researcher subagents during this same run.
Inputs explicitly NOT read: any prior `findings/dossier.md`, prior `final_specs/spec.md`, prior `validation/*`, prior `projects/spec_driven/*`. Per CLAUDE.md "Regeneration semantics: read-zero from prior outputs."

> **Architecture note (clean-state autonomous regen).** The research manager subagent halts on its own because the `Agent` (subagent-spawn) tool is parent-only. All six researchers were spawned directly from parent scope per the contract in `.claude/agents/agent_team__research_manager.md`. Each loaded `WebSearch` + `WebFetch` via ToolSearch, did real fetches, cited sources inline, and wrote a spawn audit pair under `.audit/adhoc_agents/2026-05-02/spec_driven-20260502-clean/spawns/`. This dossier was synthesized by the parent — no synthesis subagent was invoked.

## Angles researched

The interview's seven probe categories collapsed to six research angles (success-criteria was confirmed by qa.md alone and didn't require web research):

1. **prior-art-readonly-viewers** *(11 sources)* — GitHub web file browser, Sourcegraph, MkDocs Material, Docusaurus, GitBook, Backstage TechDocs, Storybook, Obsidian Publish.
2. **two-pane-navigator-reader-ux** *(18 sources)* — VS Code Explorer, JetBrains Project tool window, GitHub repo tree, MkDocs Material sidebar, Storybook sidebar, Backstage TechDocs, W3C ARIA APG TreeView pattern.
3. **markdown-link-resolution-patterns** *(12 sources)* — GFM heading slug rules, MkDocs `onBrokenLinks`, Docusaurus `onBrokenAnchors`, Obsidian wiki-link vs markdown-link, OWASP path-traversal guidance.
4. **filesystem-readonly-viewer-risks** *(28 sources)* — Starlette CVE-2023-29159, OWASP path-traversal cheat sheet, nginx / Dufs / Plesk symlink knobs, Python `pathlib` semantics, POSIX `rename` vs Windows `MoveFileEx` atomic-replace, anti-patterns (`os.path.commonprefix`, double-decode, MIME-sniffing).
5. **markdown-editor-ux** *(11 sources)* — GitHub web file editor, Obsidian (Ctrl+E), MkDocs Material's delegated "Edit this page", GitBook change-requests, Notion always-editable, VS Code Web (vscode.dev / github.dev).
6. **autonomous-mode-and-copypaste-regen** *(20 sources)* — Claude Code plan mode (verbatim phrasing), OpenAI Model Spec authority hierarchy, Cursor `.cursor/rules/*.mdc`, Aider `CONVENTIONS.md`, AGENTS.md / Codex (32 KiB silent truncation), Continue.dev rules, GitHub Spec Kit, Anthropic blog posts on agentic prompt patterns.

**Total: ~100 cited web sources across 6 angle files.**

## Cross-cutting insights

These emerge from combining angles and are load-bearing for the spec stage:

### 1. The "exposed tree" must be a single named concept used by every endpoint

The sidebar listing (prior-art angle), the link resolver (markdown-links angle), and the file-read/write endpoint sandbox (filesystem-risks angle) must all derive from one definition: `CLAUDE.md` (repo root) ∪ `.claude/agents/*.md` ∪ `.claude/skills/**/SKILL.md` ∪ `specs/{task_type}/{task_name}/{user_input,interview,findings,final_specs,validation}/**`. **Letting these three diverge is exactly the CVE-2023-29159 bug class** — the renderer "knew" the link was external while the file server still served it. The filesystem-risks angle confirms this is the canonical Python-idiomatic shape: `pathlib.Path.resolve(strict=False)` + `is_relative_to(base.resolve())` against the same single root, never `os.path.commonprefix`.

### 2. URL-as-state is the single most load-bearing v1 decision

Independently confirmed by prior-art (GitHub `/{owner}/{repo}/blob/{branch}/{path}`), two-pane (VS Code `autoReveal` exists *because* it's not URL-driven), and markdown-links (the link resolver pushes history on internal navigation). With URL = current selection, deep links / refresh / back-button / "open in new tab" all work for free, AND it eliminates the entire class of "tree disagrees with editor" sync bugs that VS Code's `autoReveal` and JetBrains' "Always Select Opened File" exist to paper over.

### 3. The W3C ARIA APG TreeView pattern is free correctness

Two-pane and prior-art both recommend it; Storybook is explicitly working toward it and considers their current state a bug (issue #18888). Implementing `role="tree"` + `role="treeitem"` + `aria-expanded` + `aria-selected` + `aria-level` from day one costs almost nothing, gives the keyboard map for free per APG, and avoids a future a11y rewrite. Two specific implementation moves per APG: **single tab stop with roving tabindex** (the focused node has `tabindex="0"`, others have `tabindex="-1"`), and **selection-follows-focus on Enter only** — focus moves with arrows but selection (`aria-selected="true"` + URL push) only on Enter.

### 4. "Expected but missing" is the dominant shape of broken state and its UX should converge

Across all six angles the same pattern emerges: missing stage subfolders (no `validation/` yet), missing files (link to a not-yet-written `final_specs/spec.md`), broken anchors (heading renamed), files removed mid-request (Claude Code rewriting while the viewer reads), an `outside_sandbox` rejection. The established UX from MkDocs / Docusaurus / GitHub: **render the affected element as muted text + native `title` tooltip giving the cause, never emit a dead `<a>`, never throw 500.** Adopt one component (`<span class="link-broken" aria-disabled="true">`) and one CSS class for all five cases, just different `title` strings.

### 5. Render-time validation is the right call here, not build-time

All four "viewer" angles converge: spec_driven has no build step (markdown-links), no watcher / auto-refresh (filesystem-risks), no precomputed index (prior-art's "scan per request" matches the GitHub render-time pattern, not the MkDocs/Docusaurus build-time pattern). At locked scale (≤200 files × <500 KB), per-request resolution is well within the latency budget.

### 6. The path resolver, the file server, and the editor must NOT trust each other

From filesystem-risks + markdown-links + editor-ux: the link resolver decides what the user *sees* as a clickable in-app link; the file-read endpoint decides what bytes ever leave the disk; the editor decides what bytes go *back* to disk. **All three independently sandbox to the exposed tree.** CVE-2023-29159 happened because the prefix check trusted the renderer's assumption. The editor must compute its own dirty state via deep equality (deciding NOT to send), and the backend `PUT /api/file` must independently re-validate every check from the read path before writing.

### 7. Header-based execution-mode contracts are non-standard among surveyed tools

The autonomous-mode angle confirms that **none** of Claude Code plan mode, OpenAI Model Spec, Cursor rules, Aider conventions, AGENTS.md / Codex, Continue.dev, or GitHub Spec Kit use a literal in-prompt `# EXECUTION MODE: …` header. They all enforce execution semantics either harness-side (rule injection, tool gating) or via role hierarchy. **spec_driven is filling a real gap.** Mitigations: (a) byte-for-byte agreement between the header and `CLAUDE.md`, (b) imperative MUST/MUST NOT phrasing under the header (mirrors plan mode's literal "Plan mode is active. The user indicated that they do not want you to execute yet — you MUST NOT make any edits …"), (c) recording every judgment call inline so a future interactive run has a starting point.

### 8. VS Code's filled-dot dirty marker is the right primitive for the editor

Editor-ux angle's strongest cross-comparator finding: **the dot-where-the-close-button-goes convention** is universal in mature editors (VS Code, github.dev, JetBrains tabs) and survives the GitHub web editor's known anti-pattern (CRLF/trailing-newline auto-normalization tripping a "user typed" boolean even when content is identical). Compute dirty state via deep equality of `currentText` vs `lastSavedText`, not from a typed flag. Pair with a textual "Unsaved changes" badge for a11y, and a persistent inline error banner above the textarea (per Notion's pattern) so save errors don't vanish while unsaved work sits in the buffer.

### 9. Codex's 32 KiB silent truncation is the strongest single argument for warn-don't-truncate

Autonomous-mode angle's load-bearing finding: AGENTS.md / Codex defaults to `project_doc_max_bytes=32768` and silently truncates above that. For spec_driven this would silently drop follow-ups from the regen prompt — exactly the wrong behavior. **Recommend warn at 50 KB, hard 413 ceiling at 1 MB, never silently truncate.** A section-breakdown line beside the Copy button (`{N} stages selected, {K} follow-ups inlined, autonomous=true, {bytes} KB`) gives the user a sanity-check before pasting.

### 10. Decode-once is the canonical anti-traversal-bypass rule

OWASP path-traversal cheat sheet (filesystem-risks) and OWASP-cited Docusaurus / MkDocs guidance (markdown-links) agree: **URL-decode exactly once**, between fragment-strip and normpath; never re-decode. FastAPI's query-param layer does this for `GET /api/file?path=...`, so `safe_resolve` MUST receive already-decoded input and MUST NOT decode again. The frontend link classifier decodes once when classifying. Two layers, one decode each, never compose.

## Per-angle highlights

### prior-art-readonly-viewers

- Three universal patterns across MkDocs Material, Docusaurus, GitBook, Storybook, Backstage TechDocs: **collapsible-by-category sidebar**, **auto-expand the path to the active file (collapse the rest)**, **breadcrumbs above content**.
- Headline anti-pattern: **VS Code Explorer losing tree state on every launch** (vscode#116190, vscode#228788). Persist sidebar collapse state + last-selected file in `localStorage`.
- Other anti-patterns to skip for v1: search (locked out), backlinks/graph view (Obsidian's signature; spec_driven links are forward-only), per-page metadata sidebar (no metadata to display), recursive expand-all toolbar, GitBook-style icon-only sidebar rail (GitBook explicitly moved away from it), generic FTP-style file managers as the model.
- Notable: **Backstage TechDocs PrimarySidebar / SecondarySidebar split** is a clean three-pane reference if a per-page TOC is added in v2; v1 stays two-pane.

### two-pane-navigator-reader-ux

- Five conventions to adopt: **URL-reflected selection (deep-linkable)**, **collapse-by-default with auto-reveal of the selected file's ancestor chain**, **folder-click = expand/collapse, file-click = render** (no folder-index pages), **breadcrumbs above content**, **W3C ARIA APG TreeView for keyboard nav**.
- APG-specific moves: **single tab stop with roving tabindex**, `aria-selected="true"` only on the URL-pointed leaf, `aria-current="page"` on the final breadcrumb segment, `aria-multiselectable="false"` on the tree container.
- Selected-state requires two distinct visuals: **filled background bar for `aria-selected="true"`** + **separate ring outline for keyboard focus**. Both visible simultaneously per APG.
- Long filenames: **single-line ellipsis with native `title` tooltip**. **CSS has no native middle-ellipsis** — use a two-element `direction: rtl` flex split for files (preserves the `.md` extension); end-ellipsis for folders.
- Defer to v2: type-ahead search inside the tree, virtualization, Ctrl+P quick-open, drag/drop, multi-select.

### markdown-link-resolution-patterns

- **Four-bucket classification**, in this exact order, decoding URL-percent-encoding exactly once before any normalization:
  1. Scheme present (`^[a-z][a-z0-9+.-]*:`) or starts with `//` → external → `<a target="_blank" rel="noopener noreferrer">` + visually-hidden "(opens in new tab)" SR text.
  2. Starts with `#` → same-file anchor → in-app scroll-to-id; silent fall-through if heading missing.
  3. Resolves inside `EXPOSED_TREE` and the file exists → internal → React Router `<Link>` push-history. Filename matching is case-sensitive; on Windows a case-mismatch resolves but emits the broken-link tooltip "case mismatch — fix the link".
  4. Otherwise → broken-outside or broken-missing → `<span class="link-broken" aria-disabled="true">` muted + tooltip; **never** an `<a>`.
- **Anchors are the most fragile sub-case.** Heading IDs auto-regenerate from heading text via the GFM kebab-case slug rule (lowercase, drop punctuation, spaces→hyphens, append `-1`/`-2` on collisions). Renaming a heading silently breaks every inbound `#anchor`. Docusaurus added a separate `onBrokenAnchors` config because anchor validation lagged page-link validation. **spec_driven should keep the path-vs-anchor severity split internally** even if both render identically, so future tooling can treat them differently.
- **Edge cases that wreck naive implementations**: percent-encoded paths (decode once, never twice — double-decode is a path-traversal bypass per OWASP); Linux/Windows case-sensitivity skew; `..`-traversal escaping the exposed root (must verify `is_relative_to` independently in both renderer and file server); GFM kebab-case slug collision rules; the markdown-syntax-vs-HTML-tag asymmetry (markdown `[label](path)` and `![alt](path)` get resolved; HTML `<a>` and `<img>` bypass resolution).
- **GFM does NOT specify the slug rule.** It's a GitHub render-time convention every renderer reimplements. spec_driven needs the same algorithm in BOTH the renderer (TOC + anchors) and any validator.

### filesystem-readonly-viewer-risks

- **Path traversal is the only real security risk in v1**, even on single-user localhost — user-authored markdown can contain `../../../.ssh/id_rsa` links. Established mitigation: `(base / user).resolve(strict=False)` + `relative_to(base.resolve())` catching `ValueError` → 400. **Do NOT use `os.path.commonprefix`** — that's the exact mistake behind Starlette CVE-2023-29159.
- **Refuse symlinks rather than follow them** (Dufs default). nginx, Dufs, and Plesk all expose explicit disable-symlinks knobs; the spec_coding repo never legitimately uses symlinks under `specs/` or `.claude/`. Cheapest correct policy: skip `Path.is_symlink()` entries during directory listing AND walk parents to verify no segment is a symlink (TOCTOU-resistant).
- **EAFP for file reads** — `try: open() except (FileNotFoundError, PermissionError, IsADirectoryError)` returning structured 404/403 JSON. Don't pre-check with `os.path.exists` — textbook race-condition antipattern.
- **Atomic writes via `tempfile.mkstemp` (same dir) + `os.fsync` + `os.replace`.** Documented caveat: on Windows `os.replace` lowers to `MoveFileEx`, not `ReplaceFile`, so atomicity is best-effort across power-loss. For spec_driven's localhost dogfood that's acceptable; flagged in the spec's open questions.
- **Encoding/binary safety is a 5-line problem, not a `chardet` dependency.** Read at most 2 MB with `encoding="utf-8", errors="replace"`, scan first 4 KB for `\x00` to reject binary (WHATWG mime-sniffing rule), whitelist file extensions (`.md`, `.yaml`, `.yml`, `.json`, `.jsonl`) at the API boundary. Defer ETag, file-watching, MIME sniffing, encoding auto-detection.

### markdown-editor-ux

- **Five comparators converge on Save-mode:** GitHub uses commit-form (heavy), Obsidian autosaves (no save concept), MkDocs delegates (out-of-app), GitBook uses change-requests (heavy), Notion autosaves, VS Code Web has explicit `Ctrl+S`. spec_driven's choice (explicit Save with Ctrl+S, stay-in-editor-after-save) is closest to **VS Code Web** and diverges deliberately from GitHub (no commit-form needed for localhost dogfood).
- **Dirty-state indicator: filled-circle dot + textual badge.** VS Code's tab-dot convention (where the close `×` normally lives) is the universal glanceable indicator. GitHub web editor's known anti-pattern: cosmetic CRLF→LF normalization trips the leave-warning even when the diff is empty. Mitigation: **deep equality of `currentText` vs `lastSavedText`**, not a "user typed" boolean.
- **Save error surfacing: persistent inline banner above the textarea.** Toasts disappear; user has unsaved work in the buffer; vanishing error is a footgun. VS Code Web pins push failures to the status bar; Notion uses a persistent connectivity banner. Adopt the persistent-banner pattern with the same muted-tooltip component used for broken links (just a different `cause` string).
- **Keyboard shortcuts: Ctrl+S and Cmd+S only in v1.** Resist Obsidian's three-mode toggle — Obsidian users themselves complain it's confusing.

### autonomous-mode-and-copypaste-regen

- **Verbatim plan-mode reminder captured.** Claude Code plan mode injects: "Plan mode is active. The user indicated that they do not want you to execute yet — you MUST NOT make any edits …". This is a model-side instruction-following contract, not a harness-side guard. spec_driven's `# EXECUTION MODE: AUTONOMOUS` header follows the same shape.
- **OpenAI Model Spec authority chain** (Root → System → Developer → User → Guideline) gave a clean rhetorical pattern: spec_driven's pasted prompt arrives as one user message, so the header reads as the most-authoritative instruction in *that message*, and `CLAUDE.md` (Claude Code's project memory) backs it up at session level.
- **Cursor / AGENTS.md / Continue / Aider** all use frontmatter or fixed-name files for rules; **none** use an in-prompt execution-mode header. The closest analogue is GitHub Spec Kit's slash-commands, which are harness-driven, not in-prompt.
- **Codex's 32 KiB silent truncation is the killer anti-pattern.** spec_driven must **warn-don't-truncate** at 50 KB and emit a 413 only above 1 MB. A section-breakdown line beside the Copy button is the user-visible mitigation.
- **Recommend "audit-log every assembled prompt"** — append a `regen.prompt.assembled` event to the run's `events.jsonl` carrying byte-count + selected stages + autonomous flag.

## Recommendations for the spec

These are the concrete moves the Stage-4 spec must pin down:

1. **Define `EXPOSED_TREE` as a single named concept used by every endpoint.** It is the union of `CLAUDE.md`, `.claude/agents/*.md`, `.claude/skills/**/SKILL.md`, and `specs/{task_type}/{task_name}/{user_input,interview,findings,final_specs,validation}/**/*.{md,yaml,yml,json,jsonl}`. Sidebar listing, link resolver, and file server all derive from this one constant.

2. **Sandboxed path resolver.** Single helper `safe_resolve(rel: str, root: Path) -> Path` doing `(root / rel).resolve(strict=False).relative_to(root.resolve())` (catch `ValueError` → HTTP 400). Used by every API endpoint that takes a path. Reject `Path.is_symlink()` entries before resolving. Walk parent segments to verify no parent is a symlink (TOCTOU-resistant).

3. **Whitelisted file extensions:** `.md`, `.yaml`, `.yml`, `.json`, `.jsonl`. Anything else → 415. Read with `encoding="utf-8", errors="replace"`, scan first 4 KB for `\x00`, cap at 2 MB.

4. **Atomic-write contract for `PUT /api/file`:** write to `tempfile.mkstemp` in the same directory, `os.fsync`, `os.replace`. On Windows note that atomicity is best-effort across power-loss.

5. **Routing.** Frontend uses URL as the single source of truth: `/file/<encoded-rel-path>` for the reader, `/project/<task_type>/<task_name>` for the project parent page, `/` redirects to the spec.md (or revised_prompt.md fallback). Push-history on internal navigation; `replace` history on folder-only-URL redirects.

6. **Sidebar component** — implements W3C ARIA APG TreeView (`role="tree"`, `role="treeitem"`, `aria-expanded`, `aria-selected`, `aria-level`, `aria-multiselectable="false"`). Single tab stop + roving tabindex. Persist collapse state per node-path and last-selected file in `localStorage` keyed `spec_driven.sidebar.v1`. On URL load, expand the ancestor chain of the selected file; collapse the rest. Folder click toggles expand only — never opens a "folder index" page. File click navigates and renders.

7. **Selected-state visual** — filled background bar for `aria-selected="true"`, separate ring outline for keyboard focus. Both visible simultaneously.

8. **Long names** — single-line ellipsis with native `title` attribute. Files use the two-element `direction: rtl` flex split for middle-ellipsis (preserves `.md`). Folders use end-ellipsis. No wrapping, no horizontal scroll.

9. **Keyboard support v1** — APG TreeView arrow-key map (Up/Down move focus, Right expand or descend, Left collapse or ascend, Enter navigate). Ctrl+P quick-open is v2.

10. **Breadcrumb above content** — `task_type / task_name / stage / filename` for Projects; `Settings / kind / filename` for Section 1. Each segment except the last is clickable. Last crumb is plain text with `aria-current="page"`.

11. **Markdown link classification** in this exact order: scheme/`//` → external (`target="_blank" rel="noopener noreferrer"` + sr-only "(opens in new tab)"); `#` → same-file anchor scroll-to (silent fall-through if missing); otherwise URL-decode once → normalize → join against source file's directory → if inside `EXPOSED_TREE` AND file exists → internal `<Link>`; else broken (muted span + `title` tooltip with cause). **Never emit a dead `<a>`.**

12. **Anchor handling** — generate heading IDs with the GFM kebab-case slug rule (lowercase ASCII, drop punctuation, spaces→hyphens, append `-1`/`-2` on collisions; non-ASCII dropped; if the slug is empty, use `section` as base). Resolve `path#anchor` by file-resolution + scroll-to-id-on-navigate. Same algorithm in renderer AND any validator.

13. **One "muted + tooltip" component** used uniformly for all "expected but missing" cases: missing stage subfolders, broken file links, broken anchors (cross-file), files removed mid-request, paths escaping the exposed root, and **save-failure banners** in the editor. Same CSS class, same `title` pattern; just different cause strings.

14. **Stale-tree affordance** — when a sidebar click resolves to a now-missing file, the API returns `{"error": "not_found", "kind": "file_removed"}`. Frontend shows a non-modal inline message with a "refresh sidebar" button. No watcher, no WebSocket — manual refresh.

15. **Section 1 layout** — always-visible header + always-expanded subgroups (`CLAUDE.md` / Agents / Skills). Section 1 is small (1 + N agents + M skills); no collapse benefit.

16. **Animation** — single 100–150ms ease on sidebar expand/collapse. Gated by `@media (prefers-reduced-motion: reduce) { transition: none }`. No other animations in v1.

17. **Browser history** — push (not replace) on every internal navigation, so back-button matches user mental model.

18. **Editor dirty-state indicator** — filled-circle dot near the file path/Close button + textual "Unsaved changes" badge in toolbar. Dirty computed via deep equality of `currentText` vs `lastSavedText` (avoid GitHub web editor's CRLF anti-pattern).

19. **Editor stays in edit mode after save** — Save success clears the dot but keeps the buffer open. "Close editor" is a separate explicit user action.

20. **Editor save errors render as a persistent inline banner above the textarea** — never a toast. Clears only on successful save. Keep the dirty dot lit during error state.

21. **Structured Q/A view for `interview/qa.md`** — parse `## Round N` → `### category` → `**Q:**` paragraph → `- A:` bullet shape. Color-tinted question/answer blocks with category badge. Per-Q and per-A pencil opens an inline editor scoped to that block; save splices into `qa.md` and writes the whole file via `PUT /api/file`. Fall back to plain markdown rendering if parse fails (no error UI).

22. **Per-stage Regenerate panel** — collapsible `<details>` above file content. Module checkboxes (default all checked). Autonomous-mode toggle persisted in `localStorage` under `spec_driven.autonomous_mode.v1` (default false). "Build prompt" button calls `POST /api/regen-prompt`. Result shown inside `<details>` with Copy button + section breakdown line `{N} stages selected, {K} follow-ups inlined, autonomous=true|false, {bytes} KB`.

23. **Project parent page at `/project/:type/:name`** — master Regenerate panel selecting any subset of stages and modules; produces one combined prompt. Sidebar's project-folder rows link to this page.

24. **`POST /api/regen-prompt` size policy: warn-don't-truncate.** Above 50 KB the response carries a `warning` field naming the size; the prompt is still emitted in full. Above 1 MB returns 413. Codex's silent 32 KiB truncation is the explicit anti-pattern to avoid.

25. **Header contract:** assembled prompt opens with `# EXECUTION MODE: AUTONOMOUS` or `# EXECUTION MODE: INTERACTIVE`. Under AUTONOMOUS, the next non-blank line is the verbatim sentence "Do not call AskUserQuestion. For anything unclear, use your best judgment, record the choice inline in the artifact, and keep going. Produce every requested artifact below in this single turn before stopping." Contract is anchored in `CLAUDE.md → ## Regeneration prompts & autonomous mode`.

26. **Read-zero contract surfaced in the prompt's constraints.** The assembled prompt's `### Constraints` section includes a constraint stating that regeneration deletes prior outputs first and re-reads only the inputs (per CLAUDE.md → "Regeneration semantics: read-zero from prior outputs"). This is the contract added in this very regen run.

27. **Audit-log every assembled prompt.** `POST /api/regen-prompt` appends a `regen.prompt.assembled` event to `.audit/adhoc_agents/{date}/{task_id}/events.jsonl` carrying byte-count, selected-stages, autonomous flag, and `warning` (if any).

## Open questions surviving research

These are gaps the research did not close — the spec stage must take a position on each, or explicitly defer.

- **Empty / missing stage folders** — render as muted-italic with "not yet generated" tooltip (recommended), hide, or show disabled? *(prior-art, two-pane)*
- **Sub-stage file ordering** — alphabetical with a small known-name priority list (`strategy.md` first), or pure alphabetical? *(prior-art)*
- **Manual reload affordance** — "refresh tree" button in scope, or strictly browser reload only? *(prior-art, filesystem-risks)*
- **Section 1 link-resolution scope** — does a markdown link from `CLAUDE.md` to `.claude/agents/foo.md` resolve in-app the same way `specs/`-internal links do? Recommend yes — same `EXPOSED_TREE` membership rule applies. *(prior-art, markdown-links)*
- **Folder-only URL** — if user navigates to `/file/specs/development/spec_driven/findings/` with no file, what does the reader pane show? Recommend auto-redirect to first markdown alphabetically with `replace` history. *(two-pane)*
- **Settings breadcrumb wording** — literal "Settings" (shorter) or "Claude Settings & Shared Context" (matches in-app section name)? *(two-pane)*
- **Broken anchor with valid file** — render fully broken, or partial (file link works, no scroll target, tooltip explains)? Docusaurus splits these via `onBrokenAnchors`; recommend partial with tooltip. *(markdown-links)*
- **CLAUDE.md cross-refs to outside-tree files** (e.g., `pyproject.toml` at repo root) — promote to internal, or leave broken? Recommend broken-outside-tree to keep `EXPOSED_TREE` strict. *(markdown-links)*
- **Image with disallowed extension** — block, or render placeholder? Recommend placeholder span with `title="v1: images not rendered"`. *(markdown-links, filesystem-risks)*
- **Symlink policy display** — refuse silently, or surface as a leaf marked "symlink — not followed"? Recommend silent skip (consistent with "expected but missing" UX). *(filesystem-risks)*
- **Code/JSON line-number anchoring** (`#L42` GitHub-style) — defer to v2. *(prior-art)*
- **In-app navigation scroll preservation** — back-button restores source file's scroll position? *(markdown-links)*
- **Windows long-path (>260 chars)** — flag if the e2e suite hits it. *(filesystem-risks)*
- **Editor dirty-dot exact placement** — beside the file path in toolbar, beside Close button, or both? Pick during implementation; dogfood will surface the right spot. *(editor-ux)*
- **`mtime_ns` round-trip for save conflicts** — flag a 409 if the file was edited externally between read and save? Filesystem-risks angle recommends; spec stage may defer to v2. *(filesystem-risks)*
- **`fsync` after write** — POSIX-portable but adds latency; spec_driven is localhost-only so the value is mostly resilience-against-power-loss. Recommend yes. *(filesystem-risks)*
- **CLAUDE.md size-cap behavior in Claude Code** — not measured by the autonomous-mode angle; an open question for v2 dogfood. *(autonomous-mode)*

## Synthesis (what changed our understanding)

Going in, the use case looked like "render markdown in a tree, also let users edit, also generate prompts" — three obvious feature pillars. Coming out, the dominant insight is that **all three pillars rest on the same exposed-tree contract, fail in the same shape (expected but missing), and must independently sandbox to the same root.** That reframes the spec from "build three components" to "define one tree contract and three views on it (read, edit, regen-prompt) with one shared 'broken' UX." Security shifts from a footnote to a load-bearing v1 requirement: even on single-user localhost, user-authored markdown is the attacker, and CVE-2023-29159 shows that sloppy sandboxing is how mature frameworks ship file-disclosure bugs. The `localStorage` sidebar persistence and ARIA APG TreeView are cheap, high-leverage moves that materially differentiate this viewer from naive comparators (VS Code Explorer, simple file servers) for almost no implementation cost. The autonomous-mode header is filling a real gap in agent tooling — no surveyed peer uses an in-prompt execution-mode header, so spec_driven's contract has to self-enforce inside one user message and be backed by `CLAUDE.md` at session memory level. And the editor's VS Code-style dirty dot + persistent inline banner is a small addition that sidesteps GitHub web editor's known anti-pattern at almost zero cost.
