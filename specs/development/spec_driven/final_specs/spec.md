# Spec — spec_driven

Run: spec_driven-20260502-clean
Stage: 4 (Spec compilation) — clean-state regeneration
Compiled by: parent (agent_team skill, no agent) under EXECUTION MODE: AUTONOMOUS, 2026-05-02
Inputs read: `user_input/revised_prompt.md`, `interview/qa.md`, `findings/dossier.md` (+ `findings/angle-*.md`).
Inputs explicitly NOT read: any prior `final_specs/spec.md`, prior `validation/*`, prior `projects/spec_driven/*`.

## Goal

Build `spec_driven`, the inaugural project of the `spec_coding` monorepo: a **single-user, localhost FastAPI + React viewer/editor** for the artifacts produced by the spec-driven workflow itself. The viewer surfaces a fixed "exposed tree" — `CLAUDE.md`, `.claude/agents/*.md`, `.claude/skills/**/SKILL.md`, and the per-project five-stage subfolders under `specs/{task_type}/{task_name}/` — and lets the user browse, render markdown with Shiki-highlighted code, click through internal cross-links, **edit any of those files in place**, and **assemble copy-paste regeneration prompts** at per-stage and per-project granularity (with an autonomous-mode toggle). The deliverable's first dogfood is itself: a user opens the app, sees `Projects/development/spec_driven/`'s own pipeline output (revised_prompt → qa → dossier → spec → validation strategy), navigates every artifact this very spec describes, and can edit any of them.

## Out of scope (v1)

- Authentication, multi-user, sessions, any access control.
- Creating new files, deleting files, uploading files (only **editing existing files in the exposed tree** is in scope).
- A "run" or "trigger pipeline" UI control. Regeneration is exposed as **copy-paste prompts** that the user pastes into Claude Code CLI; the webapp does not invoke the model.
- Diff / version history beyond what git already provides.
- Search across artifacts.
- Filesystem watching, auto-refresh, server-sent events, WebSocket pushes.
- A second example project bundled with v1.
- Browsing the `.audit/adhoc_agents/` log via the UI.
- Browsing `projects/{name}/` or `ai_videos/{name}/` output folders (only `specs/` is surfaced).
- Image rendering: markdown images render as a placeholder span with alt text + tooltip "v1: images not rendered". The file-read endpoint does not serve image bytes.
- Code line-number anchoring (`#L42`).
- Mobile / tablet support; only desktop Chromium-based browsers.
- Cross-project cross-links (a markdown link from project A's spec to project B's spec resolves as broken).
- Backlinks / graph view / per-page metadata sidebar / recursive expand-all / Ctrl+P quick-open.

## User roles & primary flows

### Roles

One role only: **developer using spec_driven** (the dogfood user). Single user, localhost-only.

### Primary flows

1. **First open.** User runs `make run`, opens `http://localhost:8765/`. App auto-redirects to `/file/specs/development/spec_driven/final_specs/spec.md` (or `…/user_input/revised_prompt.md` if the spec doesn't exist yet). The selected file renders; sidebar's `Projects > development > spec_driven > final_specs` is expanded.
2. **Browse a project's stages.** User clicks each of the five stage subfolders; each expands. User clicks a file under each; file renders. URL reflects the selection on every click.
3. **Browse Settings & Shared Context.** User clicks `CLAUDE.md`, an entry under `Agents`, an entry under `Skills`; each renders.
4. **Follow an internal cross-link.** User opens `final_specs/spec.md`, clicks a relative link to `../findings/dossier.md`; app navigates in-app to dossier, URL updates, browser back-button returns to spec.
5. **Hit a broken link.** User clicks a link to a not-yet-written file; link renders muted with tooltip "file not found"; nothing happens on click.
6. **Hit an external link.** User clicks `https://example.com`; opens in a new tab with `rel="noopener noreferrer"`.
7. **Edit a file.** User clicks ✎ Edit on the reader pane; the rendered view swaps for a textarea editor with Save / Discard / Close-editor controls. Types changes; "Unsaved changes" appears AND a filled-circle dirty-dot lights near the file path. Presses Ctrl+S; backend `PUT /api/file` writes atomically; dot clears, "Saved." appears in aria-live.
8. **Hit a save error.** User edits, presses Ctrl+S; backend rejects (e.g., 415 unsupported_extension). A persistent inline banner appears above the textarea naming the error. Banner does not auto-dismiss; dirty dot stays lit.
9. **Edit a single Q/A in `qa.md`.** User opens `interview/qa.md`; structured Q/A view shows color-tinted blocks. Clicks the pencil on one Q; an inline editor opens scoped to that block. Saves; that block's text is spliced into the file and the whole `qa.md` is written via `PUT /api/file`.
10. **Build a regen prompt for one stage.** User opens any file inside a project's stage subfolder; collapsible Regenerate panel is shown above the content. Picks modules, toggles Autonomous mode, clicks "Build prompt"; the assembled prompt opens in `<details>` with a Copy button + section breakdown line + (if >50 KB) a warning banner.
11. **Build a regen prompt for the whole project.** User clicks the "↗ project page" link on a project folder in the sidebar; navigates to `/project/development/spec_driven`. Master Regenerate panel selects any subset of stages and modules; one combined prompt is assembled.
12. **Refresh the sidebar.** User externally adds or removes a file; clicks the sidebar's "Refresh" button; tree re-fetches.
13. **Stale-tree click.** User clicks a sidebar entry that no longer exists on disk; main pane shows an inline non-modal "this file no longer exists — refresh sidebar" message with the same refresh affordance.
14. **Restore session.** User reloads; URL drives the selected file; sidebar restores collapse state and last-selected file from `localStorage`.

## Functional requirements

### Backend — file system contract

**FR-1.** Define `EXPOSED_TREE` as a single named concept used by every file-touching endpoint. Its value is the union of:
- `CLAUDE.md` at repo root.
- `.claude/agents/*.md`.
- `.claude/skills/**/SKILL.md`.
- `specs/{task_type}/{task_name}/{user_input,interview,findings,final_specs,validation}/**/*.{md,yaml,yml,json,jsonl}`.

The sidebar listing, the link resolver, and the file-read/write endpoints MUST derive from this single constant.

**FR-2.** At process startup the backend walks parent directories from `main.py` until it finds a directory containing all three of `CLAUDE.md`, `specs/`, and `.claude/`. That directory is `REPO_ROOT`. The walk runs once; the resolved value is cached. If no such directory is found, the process exits non-zero with a clear error.

**FR-3.** The backend computes the sidebar tree on every `GET /api/tree` request by walking `EXPOSED_TREE` against `REPO_ROOT`. No persistent index, no in-memory cache, no filesystem watcher.

**FR-4.** During tree-walk, entries where `Path.is_symlink()` is true are silently skipped. Symlink targets are never followed.

**FR-5.** `GET /api/file?path=<rel>` serves a single file's contents. The `path` query param is URL-decoded exactly once by FastAPI's query-param layer; `safe_resolve` receives already-decoded input and MUST NOT double-decode. The handler:
1. Calls `safe_resolve(rel, REPO_ROOT)`, the single helper that does `(REPO_ROOT / rel).resolve(strict=False).relative_to(REPO_ROOT.resolve())` and catches `ValueError` → 400 `outside_sandbox`.
2. If the resolved path's `is_symlink()` is true → 400 `outside_sandbox`. (Also walks parent segments to verify no parent is a symlink.)
3. If the resolved path is not under one of the four `EXPOSED_TREE` source globs → 404 `kind: "outside_exposed_tree"`.
4. If the extension is not in `{.md, .yaml, .yml, .json, .jsonl}` → 415 `unsupported_extension`.
5. If the file size exceeds 2 MB → 413 `too_large`.
6. Read with `encoding="utf-8", errors="replace"`. If the result contains `\x00` → 415 `binary_content`.
7. EAFP: catch `FileNotFoundError` → 404 `kind: "file_removed"`; `PermissionError` → 403 `permission_denied`; `IsADirectoryError` → 400 `is_directory`. Never let these bubble into a 500.

**FR-6.** `safe_resolve` is the only path that joins user-supplied input to `REPO_ROOT`. The frontend link resolver and the file endpoints independently validate that the requested path resolves inside `EXPOSED_TREE`. They MUST NOT trust each other.

### Backend — tree shape

**FR-7.** `GET /api/tree` returns a JSON document with two top-level sections, in this order:
1. `settings` — three subgroups, each a fixed list:
   - `claude_md`: a single leaf for `CLAUDE.md`.
   - `agents`: one leaf per file in `.claude/agents/*.md`, sorted alphabetically.
   - `skills`: one leaf per `<folder>` in `.claude/skills/*/SKILL.md`, sorted alphabetically by folder name.
2. `projects` — one entry per `task_type` directory found under `specs/`, sorted alphabetically. Each task_type contains one entry per `task_name` directory under `specs/{task_type}/`, sorted alphabetically. Each project contains exactly five stage entries: `user_input`, `interview`, `findings`, `final_specs`, `validation`, in that fixed order.

**FR-8.** Within a stage subfolder, files are listed alphabetically by filename (case-insensitive ASCII compare, stable tie-break by raw filename ordering), with one exception: inside `validation/`, the priority order is `strategy.md` first, `acceptance_criteria.md` second, `bdd_scenarios.md` third, then any remaining files alphabetically.

**FR-9.** If a stage subfolder does not exist on disk for a given project, the tree response still includes that stage entry with `present: false` and an empty file list. The sidebar component renders these as muted-italic leaves; see FR-24.

**FR-10.** Per-project tree only exposes the five stage subfolders. Other directories under `specs/{task_type}/{task_name}/` are ignored.

### Backend — deployment

**FR-11.** A single FastAPI process serves the built React static assets at `/` and the JSON API under `/api/`.

**FR-12.** Default port is `8765`. The `SPEC_DRIVEN_PORT` environment variable overrides it. If the port is unavailable at startup, the process exits non-zero with a clear error. Default Uvicorn bind is `127.0.0.1`.

**FR-13.** A `Makefile` at `projects/spec_driven/` provides:
- `make dev` — starts FastAPI (with `--reload`) and Vite dev server in two processes.
- `make run` — builds the React bundle into `projects/spec_driven/backend/static/`, then starts a single FastAPI process.
- `make test` — runs `pytest` for the backend.
- `make install` — runs `uv sync` (or `pip install -r backend/requirements.txt`) and `npm install` in `frontend/`.

**FR-14.** The README at `projects/spec_driven/README.md` documents installation, the `make` targets, the default URL, the localhost-only security model, and the autonomous-mode contract.

### Backend — editing & regeneration

**FR-14a.** `PUT /api/file` accepts `{path: str, text: str}` and writes `text` back to the resolved path. The handler MUST reuse the same checks as `GET /api/file` (single `safe_resolve` call, `is_symlink` rejection, `EXPOSED_TREE` membership, allowed extension, 2 MB cap on the encoded payload, NUL-byte rejection) before writing. The write MUST be atomic-replace: write to a sibling temp file in the same directory via `tempfile.mkstemp`, `os.fsync`, then `os.replace()`. On failure, the temp file is removed and the original is left untouched. Error mapping mirrors `GET /api/file` (400 / 403 / 404 / 413 / 415); a generic `OSError` during write is 500 `write_failed`.

**FR-14b.** `GET /api/stages?project_type=&project_name=` returns the canonical six-stage definition with each stage's id, label, folder, invocation hint, and module list (id / label / relative_path / description). Hard-coded server-side from a single source of truth.

**FR-14c.** `POST /api/regen-prompt` accepts `{project_type, project_name, stages: string[], modules: {stage_id: string[]}, autonomous: bool}` and returns `{prompt: string, warning: string | null, selected_stages_count: number, follow_ups_count: number, autonomous: bool, bytes: number}`. The prompt MUST:
- (a) Open with `# EXECUTION MODE: AUTONOMOUS` or `# EXECUTION MODE: INTERACTIVE`.
- (b) Under autonomous, immediately follow the header with the verbatim imperative line "Do not call AskUserQuestion. For anything unclear, use your best judgment, record the choice inline in the artifact, and keep going. Produce every requested artifact below in this single turn before stopping."
- (c) Inline the current `revised_prompt.md` (or fall back to `raw_prompt.md` if no revised exists).
- (d) List every `user_input/follow_ups/*.md` by relative path.
- (e) For each selected stage, include the stage's invocation hint and the in-scope module paths.
- (f) State the constraints: CLAUDE.md, canonical paths, manager-spawn contract, no-AskUserQuestion in autonomous mode, **and the read-zero contract** (regeneration deletes prior outputs first; new generation reads only the inputs).

**Size policy:** above 50 KB the response carries a non-empty `warning` field; the prompt is still emitted in full (warn-don't-truncate). Above 1 MB returns 413 `too_large`.

The endpoint reads the filesystem at request time — no caching.

### Frontend — routing

**FR-15.** URL is the source of truth for current selection. Routes:
- `/` → redirect to `/file/specs/development/spec_driven/final_specs/spec.md` if it exists, else `/file/specs/development/spec_driven/user_input/revised_prompt.md`.
- `/file/<rel-path>` → renders the file at the resolved path. The `<rel-path>` segment is URL-encoded; React Router uses a splat pattern.
- `/project/<task_type>/<task_name>` → project parent page with master Regenerate panel.

**FR-16.** A folder-only URL (`/file/specs/development/spec_driven/findings/`) auto-redirects (replace history) to the first file in that folder per FR-8. If empty, the reader pane shows a muted "no files yet" message.

**FR-17.** Internal navigation pushes a new history entry. Folder-only-URL redirects (FR-16) replace history.

### Frontend — sidebar

**FR-18.** Sidebar implements the W3C ARIA APG TreeView pattern: `role="tree"` on the container, `role="treeitem"` on each node, with `aria-expanded` (folders), `aria-selected` (the leaf matching the URL), `aria-level`, `aria-multiselectable="false"` on the tree.

**FR-19.** Keyboard navigation per W3C ARIA APG, with **single tab stop and roving tabindex** (the focused node has `tabindex="0"`, others have `tabindex="-1"`):
- Tab focuses the tree (one tab stop).
- Up/Down arrow: move focus to previous/next visible node.
- Right arrow: if focused node is a collapsed folder, expand; if expanded, move focus to first child; if leaf, no-op.
- Left arrow: if focused node is an expanded folder, collapse; if collapsed or leaf, move focus to parent.
- Enter: navigate to the focused leaf (no-op on folders).
- Home: focus first visible node. End: focus last visible node.

**FR-20.** Selected-state visual: filled background bar on the row matching `aria-selected="true"`. Keyboard focus visual: separate ring outline. Both visible simultaneously.

**FR-21.** Section 1 (`Settings & Shared Context`): always-visible header, three always-expanded subgroups (`CLAUDE.md`, `Agents`, `Skills`). Subgroups not collapsible.

**FR-22.** Section 2 (`Projects`): one collapsible section per `task_type`. On URL load, the ancestor chain of the URL-pointed file auto-expands; other sections collapse to their default state from `localStorage` (or fully collapsed on first visit).

**FR-23.** Sidebar collapse state per node-path AND last-selected file path persist to `localStorage` under key `spec_driven.sidebar.v1`. State is restored on page load. URL takes precedence over saved last-selected file when both are present. Corrupted JSON falls back to defaults with no console error.

**FR-24.** Missing-state rendering: a stage entry with `present: false` (FR-9) renders as a muted-italic leaf, not expandable, with `title="not yet generated"`. Cannot be focused via keyboard arrow.

**FR-25.** Long-name truncation: every tree row is single-line, ellipsis-on-overflow, with full text in `title`. **Files use middle-ellipsis** (preserves `.md` extension via a two-element `direction: rtl` flex split). Folders use end-ellipsis. No wrapping, no horizontal scroll.

**FR-26.** Folder click toggles expand/collapse only; never triggers navigation. File click navigates (push-history). No double-click distinction. No multi-select. No drag. No context menu.

**FR-27.** Sidebar width: fixed 320px. No drag-resize splitter in v1.

**FR-28.** A "Refresh" button at the top of the sidebar re-fetches `GET /api/tree`. The button is also rendered inline in the main pane when the API returns 404 with `kind: "file_removed"`.

### Frontend — main pane and rendering

**FR-29.** Breadcrumb above the reader pane, rendered as `<nav aria-label="Breadcrumb">` containing an ordered list. For Projects: `task_type / task_name / stage / filename`. For Settings: `Settings / kind / filename`. Each segment except the last is a clickable `<a>`. The last crumb is plain text with `aria-current="page"`.

**FR-30.** Markdown rendering uses a CommonMark + GFM-compliant parser. Heading IDs are generated using the GFM kebab-case slug rule: lowercase ASCII, drop non-ASCII characters and punctuation except hyphens, replace whitespace with hyphens, collapse multiple hyphens, trim leading/trailing hyphens, append `-1`, `-2`, … on collisions within the file. If the slug is empty, use `section` as the base before applying collision suffixes.

**FR-31.** Fenced code blocks rendered with Shiki for syntax highlighting. Language derived from the fence info string. Unknown languages render as plain monospace `<pre>`. Every rendered `<pre>` has `tabindex="0"` so keyboard users can scroll an overflowing block.

**FR-32.** Non-markdown files (`.yaml`, `.yml`, `.json`, `.jsonl`) render as a Shiki-highlighted block with line numbers. `.jsonl` renders as a sequence of one Shiki block per line, each independently parsed and highlighted as JSON; malformed lines render as plain text. Blank lines in `.jsonl` are skipped.

**FR-33.** Markdown link classification, in this exact order:
1. If `href` matches `^[a-z][a-z0-9+.-]*:` (case-insensitive) or starts with `//` → external. Render as `<a href target="_blank" rel="noopener noreferrer">` + visually-hidden `<span class="sr-only">(opens in new tab)</span>`.
2. If `href` starts with `#` → same-file anchor. In-app scroll-to-id. If no heading matches, no-op on click; no warning UI (silent fall-through).
3. Otherwise: URL-decode the path component once. Normalize `..` and `.`. Join against the source file's parent directory. Verify the result resolves inside `EXPOSED_TREE` AND the target file exists:
   - Inside `EXPOSED_TREE` AND exists → internal `<Link>` push-history.
   - Outside `EXPOSED_TREE` (or `REPO_ROOT`) → broken-outside, FR-34 with cause "outside exposed tree".
   - Inside `EXPOSED_TREE` but missing → broken-missing, FR-34 with cause "file not found".
   - Filename matching is case-sensitive on Linux/macOS, with a Windows-aware case-mismatch tooltip "case mismatch — fix the link".

**FR-34.** Broken-link rendering: a single component renders the muted+tooltip pattern. Link text is wrapped in `<span class="link-broken" aria-disabled="true">` (muted color, no underline, NOT an `<a>`) with `title` set to the cause string. Same component used for missing stage subfolders (FR-24), broken file links, broken anchors (FR-35), Windows case-mismatch links, the inline stale-tree message (FR-28), AND save-failure banners (FR-40).

**FR-35.** Broken-anchor handling for `path#anchor` cross-file links: file resolution succeeds (per FR-33 case 3), so the link IS clickable and navigates. After navigation, the frontend attempts to scroll to the heading whose generated id matches the fragment. If no such heading exists, the page lands at the top (no error UI). Silent fall-through.

**FR-36.** Internal images (`![alt](path)` resolving inside `EXPOSED_TREE` with extension not in the supported set) render as `<span class="image-placeholder">` containing the alt text, with `title="v1: images not rendered"`. External images render as `<img src>` straight, no proxying. NOT in v1: serving image bytes via `/api/file`.

**FR-37.** Section 1 link resolution: links from `CLAUDE.md`, agent files, or skill files resolve in-app exactly like `specs/`-internal links — if the resolved path is inside `EXPOSED_TREE`, navigate in-app; otherwise broken per FR-33 / FR-34.

**FR-38.** Sidebar-tree-click semantics: click on a tree leaf updates URL (push history) and the main pane re-renders. Sidebar's `aria-selected` moves to the new leaf. Click on a missing-state leaf produces no URL change.

**FR-39.** Sidebar expand/collapse animates with a single 100–150ms ease (CSS transition on `height` or `max-height`), gated by `@media (prefers-reduced-motion: reduce) { transition: none }`.

### Frontend — editing

**FR-40.** Every file in the main pane shows a ✎ Edit button that toggles the file from rendered view to a textarea editor. The editor MUST:
- (a) Show Save / Discard / Close-editor controls in a toolbar above the textarea.
- (b) Disable Save when there are no unsaved changes.
- (c) Flag dirty state with **both** a textual badge ("Unsaved changes") AND a filled-circle dirty-dot near the file path / Close button. Dirty state is computed from a deep equality of `currentText` vs `lastSavedText`, NOT a "user typed" flag (sidesteps the GitHub web editor CRLF anti-pattern).
- (d) Accept Ctrl+S / Cmd+S as the Save shortcut.
- (e) Call `PUT /api/file` with `{path, text}`. On failure render a **persistent inline banner** above the textarea with the structured error key + kind (no toast, no modal). The dirty dot stays lit until save actually succeeds.
- Save success updates `lastSavedText`, clears the dot, shows "Saved." in an aria-live region, and stays in editor mode (closing is an explicit user action).

**FR-41.** When the active file's path matches `*/interview/qa.md`, the rendered view is the **structured Q/A view** instead of generic markdown: parse `## Round N` → `### {category}` → `**Q:**` paragraph → `- A:` bullet pattern. Render rounds, categories, and Q/A pairs as discrete blocks. Question blocks use one tint, answer blocks use another, the category gets a small badge above its block group. Each Q and each A has its own ✎ pencil that opens an inline editor scoped to that block; saving rewrites the whole `qa.md` via `PUT /api/file`. Whole-file editing remains via the file-level Edit toggle. If parse fails, fall back to generic markdown rendering with no error UI.

### Frontend — regeneration UI

**FR-42.** When the active file is inside a project's stage subfolder, the main pane shows a collapsible **Regenerate** panel (`<details>`) above the file content. Default-collapsed. Contents:
- (a) Module checkboxes derived from `GET /api/stages` for the file's stage (default all checked).
- (b) An "Autonomous mode" toggle persisted in `localStorage` under key `spec_driven.autonomous_mode.v1` (default false).
- (c) "Build prompt" button calls `POST /api/regen-prompt`.
- (d) After build: a one-line section breakdown beside the Copy button reading `{N} stages selected, {K} follow-ups inlined, autonomous={true|false}, {bytes} KB` (using locale-formatted number for bytes).
- (e) When the API response carries a non-null `warning`, render a muted banner reading `warning: {warning} — verify your selection before pasting`.
- (f) The assembled prompt is shown inside a `<details>` element; a "Copy to clipboard" button copies the full text and flips its label to "Copied!" for ~1.5s.

**FR-43.** Route `/project/:type/:name` shows the project parent page. Lists all six stages with their modules and exposes a single master Regenerate panel that lets the user select **any subset of stages and modules** (default: all). Same breakdown + warning + Copy contract as FR-42. Sidebar entries for projects link to this page; per-file routes still work.

**FR-44.** The autonomous-mode toggle is the same value across the per-stage panel and the project parent page. Editing it in either updates `localStorage` and re-renders both consumers (via a `storage` event listener for cross-tab + an in-process subscription for same-tab). Default is **interactive** (toggle off).

## Non-functional requirements

### Performance

- **NFR-1.** `GET /api/tree` returns within 200 ms for the locked scale (≤50 projects, ≤200 files per project) on a typical developer laptop.
- **NFR-2.** `GET /api/file?path=<rel>` returns within 100 ms for files under 500 KB.
- **NFR-3.** Initial app load (HTML + JS + first `/api/tree` + first `/api/file`) completes within 2 seconds on localhost.

### Security

- **NFR-4.** All file-touching endpoints use `safe_resolve`. Direct filesystem access bypassing `safe_resolve` is a code-review-blocking issue.
- **NFR-5.** Symlinks are never followed and never serve content. Behavior enforced even if the symlink points inside `EXPOSED_TREE`.
- **NFR-6.** Only sanctioned mutation endpoints exist: `PUT /api/file` and `POST /api/regen-prompt`. No DELETE, no upload, no create-new-file. PATCH/DELETE return 405.
- **NFR-7.** No authentication; localhost-only deployment is the security model. Default Uvicorn bind is `127.0.0.1`.
- **NFR-8.** No CORS configuration (single-origin); explicitly DO NOT enable `allow_origins=["*"]`.

### Accessibility

- **NFR-9.** Sidebar implements W3C ARIA APG TreeView (FR-18, FR-19). Keyboard-only navigation reaches every interactive element.
- **NFR-10.** All interactive elements meet WCAG 2.1 Level AA color contrast (4.5:1 for normal text, 3:1 for UI elements).
- **NFR-11.** Headings within rendered markdown have appropriate semantic levels.

### Concurrency / consistency

- **NFR-12.** Backend tolerates concurrent writes by Claude Code: EAFP-based reads (FR-5.7) handle mid-write file removal. Torn reads accepted as known UX wrinkle: user refreshes manually.

### Encoding

- **NFR-13.** All text read as UTF-8 with `errors="replace"`. Files containing `\x00` bytes rejected as binary. No `chardet` dependency.

### Browser support

- **NFR-14.** Latest stable Chrome / Chromium-based browsers only.

### Scale

- **NFR-15.** Designed for ≤50 projects, ≤200 files per project, individual files <500 KB. Hard ceiling: single file <2 MB. Beyond these bounds, behavior undefined.

### Code organization

- **NFR-16.** Backend at `projects/spec_driven/backend/`, frontend at `projects/spec_driven/frontend/`. Backend's own `requirements.txt` lists direct deps; mirror into root `pyproject.toml`. Backend entry point is `main.py`, ~15 lines max. All Python application logic in `libs/<module>.py`. Strong typing on every parameter, return value, attribute. Use `str | None`, not `Optional[str]`. Domain concepts as classes; `@dataclass(frozen=True)` for immutable data containers. `node_modules/` in `.gitignore`.

## Acceptance criteria summary

Full Gherkin scenarios live in `validation/acceptance_criteria.md`. Top-level summary:

- **AC-1 (first open).** Opening `http://localhost:8765/` results in `final_specs/spec.md` rendering with the project tree expanded.
- **AC-2 (browse stages).** All five stage subfolders are clickable, expand on click, contain at least one renderable file each.
- **AC-3 (browse settings).** All three Section 1 file kinds are clickable and render correctly.
- **AC-4 (cross-link navigation).** A relative markdown link from `final_specs/spec.md` to `../findings/dossier.md` is clickable and navigates in-app with URL update.
- **AC-5 (broken link).** A markdown link to a non-existent file renders muted with the correct tooltip and is not a clickable `<a>`.
- **AC-6 (external link).** An `https://` link renders with `target="_blank" rel="noopener noreferrer"` + sr-only "(opens in new tab)".
- **AC-7 (path traversal blocked).** `GET /api/file?path=../../../etc/hosts` returns 400 `outside_sandbox`.
- **AC-8 (extension whitelist).** `GET /api/file?path=foo.png` returns 415.
- **AC-9 (binary content rejected).** A `.md` file containing `\x00` bytes returns 415 `binary_content`.
- **AC-10 (size limit).** A file >2 MB returns 413.
- **AC-11 (missing stage rendering).** When `validation/` doesn't exist, the sidebar shows it as muted-italic with `not yet generated` tooltip.
- **AC-12 (refresh).** After externally creating a file, clicking Refresh shows the new entry.
- **AC-13 (state restoration).** Reloading restores URL-driven selection and the previous collapse state from `localStorage`.
- **AC-14 (keyboard navigation).** Tab focuses the tree; Up/Down/Right/Left/Enter behave per APG TreeView.
- **AC-15 (concurrent write tolerance).** Killing a file Claude Code is mid-writing during tree-walk does NOT produce 500.
- **AC-16 (editor save success).** Editing → Ctrl+S → file written atomically; dirty dot clears; "Saved." announces.
- **AC-17 (editor save failure).** A 415 response from `PUT /api/file` renders a persistent inline banner; dirty dot stays lit until next successful save.
- **AC-18 (Q/A view).** `interview/qa.md` renders as colored Q/A blocks with per-block ✎ editing.
- **AC-19 (regen prompt build).** `POST /api/regen-prompt` returns `{prompt, warning, selected_stages_count, follow_ups_count, autonomous, bytes}`. Above 50 KB the warning field is non-null; above 1 MB returns 413.
- **AC-20 (autonomous header).** When `autonomous=true`, the prompt opens with `# EXECUTION MODE: AUTONOMOUS` and the next non-blank line is the verbatim imperative sentence.
- **AC-21 (read-zero contract surfaced).** Every assembled prompt's `### Constraints` section includes the read-zero constraint.
- **AC-22 (project page master regen).** Navigating to `/project/development/spec_driven` shows the six stages with module checkboxes and a master Regenerate panel.
- **AC-23 (verb whitelist).** PATCH/DELETE on `/api/file` return 405; only GET, PUT, POST are sanctioned.
- **AC-24 (NFR-7 bind).** The process binds to `127.0.0.1`, not `0.0.0.0`.
- **AC-25 (NFR-8 no CORS wildcard).** No `Access-Control-Allow-Origin: *` header is emitted.
- **AC-26 (REPO_ROOT discovery).** From a working directory not under any repo, the process exits non-zero with a clear error.
- **AC-27 (port override).** `SPEC_DRIVEN_PORT=9090` honored; unavailable port exits non-zero.

## Open questions

- **OQ-1 — Folder-only-URL behavior.** Recommended: auto-redirect to first markdown file alphabetically (replace history). Confirm.
- **OQ-2 — Settings breadcrumb wording.** Spec uses literal "Settings" for the breadcrumb (shorter); the in-app section header is "Claude Settings & Shared Context". OK?
- **OQ-3 — Editor dirty-dot exact placement.** Spec says "near the file path / Close button" without naming the exact slot. Defer to implementation.
- **OQ-4 — `mtime_ns` round-trip for save conflicts.** Filesystem-risks angle suggested 409-on-stale-mtime; spec defers to v2.
- **OQ-5 — `fsync` after write.** Recommended for resilience-against-power-loss; adds latency. Spec adopts; reconsider if dogfood shows perceptible delay.
- **OQ-6 — Code line-number anchoring (`#L42`).** Defer to v2.
- **OQ-7 — Sidebar fixed width.** 320 px fixed; revisit if dogfood shows constant ellipsis.
- **OQ-8 — JSONL line-by-line vs single block rendering.** Spec picks per-line Shiki blocks for `.jsonl`; reconsider if line count grows large.
- **OQ-9 — Audit-log every assembled prompt.** Recommended by autonomous-mode angle. Spec adopts: emit `regen.prompt.assembled` event to `events.jsonl`.

End of spec.
