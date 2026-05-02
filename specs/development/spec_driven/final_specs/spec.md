# Spec — spec_driven

Run: spec_driven-20260502-141813
Stage: 4 (Spec compilation)
Compiled by: parent (agent_team skill, no agent), 2026-05-02
Inputs:
- `specs/development/spec_driven/user_input/revised_prompt.md`
- `specs/development/spec_driven/interview/qa.md`
- `specs/development/spec_driven/findings/dossier.md`

## Goal

Build `spec_driven`, the inaugural project of the `spec_coding` monorepo: a **single-user, localhost FastAPI + React viewer/editor** for the artifacts produced by the spec-driven workflow itself. The viewer surfaces a fixed "exposed tree" — `CLAUDE.md`, `.claude/agents/*.md`, `.claude/skills/**/SKILL.md`, and the per-project five-stage subfolders under `specs/{task_type}/{task_name}/` — and lets the user browse, render markdown with Shiki-highlighted code, click through internal cross-links between artifacts, **edit any of those files in place**, and **assemble copy-paste regeneration prompts** at per-stage and per-project granularity (with an autonomous-mode toggle). The deliverable's first dogfood is itself: a user opens the app, sees `Projects/development/spec_driven/`'s own pipeline output (revised_prompt → qa → dossier → spec → validation strategy), navigates every artifact this very spec describes how to render, and can edit any of them. **Editing scope was added by follow-up 001** (the original revised prompt called the viewer readonly).

## Out of scope (v1)

Hard non-goals (refreshed by follow-up 001):

- Authentication, multi-user, sessions, or any access control.
- Creating new files, deleting files, uploading files (only **editing existing files in the exposed tree** is in scope).
- A "run" or "trigger pipeline" UI control of any kind. Regeneration is exposed as **copy-paste prompts** that the user pastes into Claude Code CLI; the webapp does not invoke the model itself.
- Diff / version history beyond what git already provides.
- Search across artifacts (full-text, semantic, or keyword).
- Filesystem watching, auto-refresh, server-sent events, or WebSocket pushes.
- A second example project bundled with v1 (multi-project rendering is verified by component tests using fixture data).
- Browsing the `.audit/adhoc_agents/{date}/{task_id}/` audit log via the UI (defer to v2).
- Browsing `projects/{name}/` or `ai_videos/{name}/` output folders (only `specs/` is surfaced).
- Image rendering: markdown images render as a placeholder span with alt text and a tooltip "v1: images not rendered". The file-read endpoint does not serve image bytes.
- Cross-line code anchoring (URL fragments like `#L42-L48`).
- Single-line code anchoring (URL fragment `#L42`) — deferred to v2.
- Mobile / tablet support; only desktop Chromium-based browsers.
- Cross-project cross-links (a markdown link from project A's spec to project B's spec is NOT in scope; if such a link exists it resolves as broken).
- Backlinks / graph view / per-page metadata sidebar / recursive expand-all / Ctrl+P quick-open / per-heading "copy link" affordance.

## User roles & primary flows

### Roles

One role only: **developer using spec_driven** (the dogfood user). Single user, localhost-only. No anonymous / external user category.

### Primary flows

1. **First open.** User runs `make run`, opens `http://localhost:8765/`. App auto-navigates to `/projects/development/spec_driven/final_specs/spec.md` (or `/projects/development/spec_driven/user_input/revised_prompt.md` if the spec file doesn't exist yet). The selected file renders in the main pane; sidebar's `Projects > development > spec_driven > final_specs` is expanded.
2. **Browse a project's stages.** User clicks each of the five stage subfolders (`user_input`, `interview`, `findings`, `final_specs`, `validation`) under `Projects/development/spec_driven/`; each expands. User clicks a file under each; file renders. URL reflects the selection on every click.
3. **Browse Settings & Shared Context.** User clicks `CLAUDE.md`, an entry under `Agents`, an entry under `Skills`; each renders.
4. **Follow an internal cross-link.** User opens `final_specs/spec.md`, clicks a relative link to `../findings/dossier.md`; app navigates in-app to dossier, URL updates, browser back-button returns to spec.
5. **Hit a broken link.** User clicks a link to a not-yet-written file (e.g., before Stage 5 runs, a dossier link to `../validation/strategy.md`); link renders muted with tooltip "file not found"; nothing else happens on click.
6. **Hit an external link.** User clicks `https://example.com` in any markdown file; opens in a new tab with `rel="noopener noreferrer"`.
7. **Refresh the sidebar.** User externally adds or removes a file (e.g., the pipeline writes a new `validation/strategy.md`); user clicks the sidebar's "refresh" button; tree re-fetches and includes the new entry.
8. **Stale-tree click.** User clicks a sidebar entry that no longer exists on disk; main pane shows an inline non-modal "this file no longer exists — refresh sidebar" message with the same refresh affordance.
9. **Restore session.** User reloads the page; URL drives the selected file, sidebar restores collapse state and last-selected file from `localStorage`.

## Functional requirements

Each requirement is testable. Numbered for traceability into `validation/`.

### Backend — file system contract

**FR-1.** Define `EXPOSED_TREE` as a single named concept in the backend, used by every file-touching endpoint. Its value is the union of: `CLAUDE.md` at repo root; `.claude/agents/*.md`; `.claude/skills/**/SKILL.md`; `specs/{task_type}/{task_name}/{user_input,interview,findings,final_specs,validation}/**/*.{md,yaml,yml,json,jsonl}`. The sidebar listing, the link resolver, and the file-read endpoint MUST derive from this single constant.

**FR-2.** At process startup, the backend walks parent directories from its own file until it finds a directory containing all three of `CLAUDE.md`, `specs/`, and `.claude/`. That directory is `REPO_ROOT`. The walk runs once; the resolved value is cached. If no such directory is found, the process exits non-zero with a clear error message.

**FR-3.** The backend computes the sidebar tree on every `GET /api/tree` request by walking `EXPOSED_TREE` against `REPO_ROOT`. No persistent index, no in-memory cache, no filesystem watcher.

**FR-4.** During tree-walk, entries where `Path.is_symlink()` is true are silently skipped. Symlink targets are never followed.

**FR-5.** `GET /api/file?path=<rel>` serves a single file's contents. The `path` query param is URL-decoded exactly once by FastAPI's query-param layer; `safe_resolve` receives already-decoded input and MUST NOT double-decode (double-decoding is a path-traversal bypass per OWASP). The handler MUST:
1. Call `safe_resolve(rel, REPO_ROOT)`, a single helper that does `(REPO_ROOT / rel).resolve(strict=False).relative_to(REPO_ROOT.resolve())` and catches `ValueError` → 400 `outside_sandbox`.
2. If the resolved path's `is_symlink()` is true → 400 `outside_sandbox`.
3. If the resolved path is not under one of the four `EXPOSED_TREE` source globs → 404 `not_found` (with `kind: "outside_exposed_tree"`).
4. If the extension is not in `{.md, .yaml, .yml, .json, .jsonl}` → 415 `unsupported_extension`.
5. If the file size exceeds 2 MB → 413 `too_large`.
6. Read with `encoding="utf-8", errors="replace"`. If the result contains `\x00` → 415 `binary_content`.
7. EAFP: catch `FileNotFoundError` → 404 `kind: "file_removed"`; `PermissionError` → 403 `permission_denied`; `IsADirectoryError` → 400 `is_directory`. Never let these bubble into a 500.

**FR-6.** The `safe_resolve` helper is the only path that ever joins user-supplied input to `REPO_ROOT`. The link resolver in the frontend and the file-read endpoint independently validate that the requested path resolves inside `EXPOSED_TREE`. They MUST NOT trust each other.

### Backend — tree shape

**FR-7.** `GET /api/tree` returns a JSON document with two top-level sections, in this order:
1. `settings` — three subgroups, each a fixed list:
   - `claude_md`: a single leaf for `CLAUDE.md`.
   - `agents`: one leaf per file in `.claude/agents/*.md`, sorted alphabetically by filename.
   - `skills`: one leaf per `<folder>` in `.claude/skills/*/SKILL.md`, sorted alphabetically by folder name. Each leaf points to that folder's `SKILL.md`.
2. `projects` — one entry per `task_type` directory found under `specs/`, sorted alphabetically (`ai_video`, `development`, …). Each task_type contains one entry per `task_name` directory under `specs/{task_type}/`, sorted alphabetically. Each project contains exactly five stage entries: `user_input`, `interview`, `findings`, `final_specs`, `validation`, in that fixed order.

**FR-8.** Within a stage subfolder, files are listed alphabetically by filename (case-insensitive ASCII compare, stable tie-break by raw filename ordering), with one exception: inside `validation/`, the priority order is `strategy.md` first, `acceptance_criteria.md` second, `bdd_scenarios.md` third, then any remaining files alphabetically.

**FR-9.** If a stage subfolder does not exist on disk for a given project (e.g., `validation/` before Stage 5 runs), the tree response still includes that stage entry with `present: false` and an empty file list. The sidebar component renders these as muted-italic leaves; see FR-19.

**FR-10.** Per-project tree only exposes the five stage subfolders. Other directories under `specs/{task_type}/{task_name}/` (if any exist for any reason) are ignored.

### Backend — deployment

**FR-11.** A single FastAPI process serves the built React static assets at `/` and the JSON API under `/api/`. No separate static server in production.

**FR-12.** The default port is `8765`. The `SPEC_DRIVEN_PORT` environment variable overrides it. If the port is unavailable at startup, the process exits non-zero with a clear error.

**FR-13.** A `Makefile` at `projects/spec_driven/` provides:
- `make dev` — starts FastAPI (with `--reload`) and the Vite dev server in two processes; documents the two URLs in the README.
- `make run` — builds the React bundle into `projects/spec_driven/backend/static/` (or equivalent), then starts a single FastAPI process serving both static and `/api/`.

**FR-14.** The README at `projects/spec_driven/README.md` documents installation (`uv sync` + `npm install` from `projects/spec_driven/frontend/`), the two `make` targets, and the default URL.

### Backend — editing & regeneration (added by follow-up 001)

**FR-14a.** `PUT /api/file` accepts `{path: str, text: str}` and writes `text` back to the resolved path. The handler MUST reuse the same checks as `GET /api/file` (single `safe_resolve` call, `is_symlink` rejection, `EXPOSED_TREE` membership, allowed extension, 2 MB cap on the **encoded** payload, NUL-byte rejection) before writing. The write MUST be atomic-replace: write to a sibling temp file in the same directory, then `os.replace()` onto the target. On failure, the temp file is removed and the original is left untouched. Error mapping mirrors `GET /api/file` (400 / 403 / 404 / 413 / 415); a generic `OSError` during write is 500 `write_failed`.

**FR-14b.** `GET /api/stages?project_type=&project_name=` returns the canonical six-stage definition with each stage's id, label, folder, invocation hint, and module list (id / label / relative_path / description). The list is hard-coded server-side from a single source of truth so the frontend never has to know stage names.

**FR-14c.** `POST /api/regen-prompt` accepts `{project_type, project_name, stages: string[], modules: {stage_id: string[]}, autonomous: bool}` and returns `{prompt: string}`. The prompt MUST: (a) open with `# EXECUTION MODE: AUTONOMOUS` or `# EXECUTION MODE: INTERACTIVE`; (b) inline the current `revised_prompt.md` (or fall back to `raw_prompt.md` if no revised exists); (c) list every `user_input/follow_ups/*.md` by relative path; (d) for each selected stage, include the stage's invocation hint and the in-scope module paths; (e) state the four constraints (CLAUDE.md, canonical paths, manager-spawn contract, no-AskUserQuestion in autonomous mode). The endpoint reads the filesystem at request time — no caching.

### Frontend — routing

**FR-15.** URL is the source of truth for current selection. Routes:
- `/` → 302 redirect to `/projects/development/spec_driven/final_specs/spec.md` if the file exists, else `/projects/development/spec_driven/user_input/revised_prompt.md` (assumed to always exist after Stage 1).
- `/settings/claude-md` → renders `CLAUDE.md`.
- `/settings/agents/<file>` → renders `.claude/agents/<file>` (the route param is the bare filename, e.g. `agent_team__interview_manager.md`).
- `/settings/skills/<folder>` → renders `.claude/skills/<folder>/SKILL.md`.
- `/projects/<task_type>/<task_name>/<stage>/<...file_path>` → renders the file at the resolved path. The `<...file_path>` segment uses nested route segments (not a single splat with encoded `/`) — for v1, files live directly inside the stage folder, so this is one segment.

**FR-16.** A folder-only URL (e.g., `/projects/development/spec_driven/findings/`) auto-redirects (via React Router programmatic navigate, replacing the history entry) to the first file in that folder per FR-8. If the folder is empty, it stays at the URL and the reader pane shows a muted "no files yet" message.

**FR-17.** Internal navigation pushes a new history entry (browser back/forward navigates between visited files). Folder-only-URL redirects (FR-16) replace the history entry so back-button doesn't loop.

### Frontend — sidebar

**FR-18.** The sidebar implements the W3C ARIA tree pattern: `role="tree"` on the container, `role="treeitem"` on each node, with `aria-expanded` (folders), `aria-selected` (the leaf matching the URL), `aria-level` (1 for top-level, increasing by 1 per nesting), and `aria-multiselectable="false"` on the tree.

**FR-19.** Keyboard navigation per W3C ARIA APG:
- Tab focuses the tree (one tab stop for the whole tree).
- Up/Down arrow: move focus to previous/next visible node.
- Right arrow: if focused node is a collapsed folder, expand; if expanded, move focus to first child; if leaf, no-op.
- Left arrow: if focused node is an expanded folder, collapse; if collapsed or leaf, move focus to parent.
- Enter: navigate to the focused leaf (no-op on folders).

**FR-20.** Selected-state visual: filled background bar on the row matching `aria-selected="true"`. Keyboard focus visual: separate ring outline. Both indicators visible simultaneously when focus and selection are on the same node.

**FR-21.** Section 1 (`Settings & Shared Context`): always-visible header, three always-expanded subgroups (`CLAUDE.md`, `Agents`, `Skills`). Subgroups are NOT collapsible (no benefit at fixed small size). Section 1 itself is NOT collapsible.

**FR-22.** Section 2 (`Projects`): one collapsible section per `task_type`, each containing a flat list of project rows that themselves expand to show the five stage subfolders. On URL load, the ancestor chain of the URL-pointed file auto-expands (task_type → project → stage); other sections collapse to their default state from `localStorage` (or fully collapsed on first visit).

**FR-23.** Sidebar collapse state per node-path AND last-selected file path persist to `localStorage` under key `spec_driven.sidebar.v1`. State is restored on page load. The URL takes precedence over the saved last-selected file when both are present.

**FR-24.** Missing-state rendering: a stage entry with `present: false` (FR-9) renders as a muted-italic leaf, not expandable, with `title="not yet generated"`. Cannot be focused via keyboard arrow; arrow nav skips it. Cannot be clicked (no navigation occurs).

**FR-25.** Long-name truncation: every tree row is single-line, ellipsis-on-overflow, with the full text in the native `title` attribute. Files use middle-ellipsis (preserves `.md` extension), folders use end-ellipsis. No wrapping, no horizontal scroll.

**FR-26.** Folder click toggles expand/collapse only; never triggers navigation. File click navigates (push-history). No double-click distinction. No multi-select. No drag. No context menu.

**FR-27.** Sidebar width: fixed 320px. No drag-resize splitter in v1.

**FR-28.** A "Refresh" button at the top of the sidebar re-fetches `GET /api/tree` and re-renders. The button is also rendered inline in the main pane when the API returns 404 with `kind: "file_removed"` (FR-5.7).

### Frontend — main pane and rendering

**FR-29.** Breadcrumb above the reader pane, rendered as `<nav aria-label="Breadcrumb">` containing an ordered list:
- For Projects: `task_type / task_name / stage / filename`.
- For Settings: `Settings / kind / filename`, where `kind` is `CLAUDE.md`, `Agents`, or `Skills`.
Each segment except the last is a clickable `<a>` that navigates to that node (folder breadcrumbs navigate to the folder URL → triggers FR-16 redirect to the first file). The last crumb is plain non-clickable text with `aria-current="page"`.

**FR-30.** Markdown rendering uses a CommonMark + GFM-compliant parser. Heading IDs are generated using the GFM kebab-case slug rule: lowercase ASCII, drop non-ASCII characters and punctuation except hyphens, replace whitespace with hyphens, collapse multiple hyphens, trim leading/trailing hyphens, append `-1`, `-2`, … on collisions within the file. If the slug is empty after dropping (e.g., a heading containing only non-ASCII characters), use `section` as the base before applying collision suffixes.

**FR-31.** Fenced code blocks in markdown are rendered with Shiki for syntax highlighting. Language is derived from the fence info string (e.g., ```python). Unknown languages render as a plain monospace `<pre>` without highlighting. Every rendered `<pre>` (highlighted or plain) has `tabindex="0"` so keyboard users can scroll an overflowing block.

**FR-32.** Non-markdown files (`.yaml`, `.yml`, `.json`, `.jsonl`) render in the reader pane as a single Shiki-highlighted block with line numbers visible in the gutter. `.jsonl` is rendered as a sequence of one Shiki block per line, each independently parsed and highlighted as JSON; if a line is malformed JSON, render that line as plain text. Blank (whitespace-only) lines in `.jsonl` are skipped, not rendered as empty blocks.

**FR-33.** Markdown link classification, in this exact order:
1. If `href` matches `^[a-z][a-z0-9+.-]*:` (case-insensitive) or starts with `//` → **external**. Render as `<a href target="_blank" rel="noopener noreferrer">`, with a trailing visually-hidden `<span class="sr-only">(opens in new tab)</span>` for screen-reader announcement.
2. If `href` starts with `#` → **same-file anchor**. Render as in-app scroll-to-id handler. If no heading with the matching slug exists in the current file, the link is a no-op on click; no warning UI in v1 (silent fall-through).
3. Otherwise: URL-decode the path component once. Normalize `..` and `.` segments. Join against the source file's parent directory. Verify the result resolves inside `EXPOSED_TREE` AND the target file exists on disk:
   - File exists in `EXPOSED_TREE` → **internal**, render as React Router `<Link to>`. Click navigates in-app, push-history. Filename matching is case-sensitive on Linux/macOS (POSIX-default) and case-insensitive on Windows; on Windows, a case-mismatch between the link text and the actual filename still resolves but emits the broken-link tooltip "case mismatch — fix the link".
   - Resolved path escapes `EXPOSED_TREE` (or escapes `REPO_ROOT`) → **broken-outside**, render per FR-34 with cause "outside exposed tree".
   - Resolved path is inside `EXPOSED_TREE` but file does not exist → **broken-missing**, render per FR-34 with cause "file not found".

**FR-34.** Broken-link rendering: a single component renders the muted+tooltip pattern. The link text is wrapped in a `<span class="link-broken" aria-disabled="true">` (muted color, no underline, not a `<a>` element so it's not clickable) with the `title` attribute set to the cause string (one of: `not yet generated`, `file not found`, `outside exposed tree`, `anchor not found`, `case mismatch — fix the link`). The same component is used for missing stage subfolders (FR-24), broken file links (FR-33 case 3 fail), broken anchors (FR-35), Windows case-mismatch links (FR-33 case 3 internal sub-case), and the inline stale-tree message (FR-28's secondary use). Visually, all five cases look identical except for the tooltip text.

**FR-35.** Broken-anchor handling for `path#anchor` cross-file links: the file resolution succeeds (per FR-33 case 3), so the link IS clickable and navigates. After navigation, the frontend attempts to scroll to the heading whose generated id matches the fragment. If no such heading exists, the page simply lands at the top of the file (no error UI). The link's tooltip while still on the source page shows the path target normally; only after navigation does the missing-anchor situation become evident — silent fall-through.

**FR-36.** Internal images (`![alt](path)` where `path` resolves inside `EXPOSED_TREE` and the extension is not in the supported set) render as a `<span class="image-placeholder">` containing the alt text, with `title="v1: images not rendered"`. External images (scheme present) render as `<img src>` straight, with no proxying. NOT in v1: serving image bytes via `/api/file`.

**FR-37.** Section 1 link resolution: links from `CLAUDE.md`, agent files, or skill files resolve in-app exactly like `specs/`-internal links — if the resolved path is inside `EXPOSED_TREE`, navigate in-app; otherwise broken per FR-33 / FR-34. A link from `CLAUDE.md` to `pyproject.toml` (which is outside `EXPOSED_TREE`) renders as broken-outside.

**FR-38.** Sidebar-tree-click semantics: when the user clicks a tree leaf, the URL updates (push history) and the main pane re-renders. The sidebar's `aria-selected` moves to the new leaf. If the click targets a missing-state leaf (FR-24), no URL change occurs.

### Frontend — animation

**FR-39.** Sidebar expand/collapse animates with a single 100–150ms ease (CSS transition on `height` or `max-height`), gated by `@media (prefers-reduced-motion: reduce) { transition: none }` so users with reduced-motion preference get instant state changes. No other animations in v1.

### Frontend — editing & regeneration (added by follow-up 001)

**FR-40.** Every file in the main pane shows a ✎ Edit button that toggles the file from rendered view to a textarea editor. The editor MUST: (a) show Save / Discard / Close-editor controls; (b) disable Save when there are no unsaved changes; (c) flag "Unsaved changes" until Save succeeds; (d) accept Ctrl+S / Cmd+S as the Save shortcut; (e) call `PUT /api/file` with `{path, text}` and surface the structured error message on failure. Save success updates the in-memory file content but stays in editor mode (closing is an explicit user action).

**FR-41.** When the active file's path matches `*/interview/qa.md`, the rendered view is the **structured Q/A view** instead of generic markdown: parse the document into rounds (`## Round N`), categories (`### {category}`), and Q/A pairs (`**Q:**` paragraph followed by `- A:` bullet) and render them as discrete blocks. Question blocks use a distinct background tint, answer blocks use another, the category gets a small badge above its block group. Each Q and each A has its own ✎ pencil that opens an inline editor scoped to that block; saving rewrites the whole `qa.md` file via `PUT /api/file` after splicing the edited block into the original text. Whole-file editing remains available via the file-level Edit toggle. If the file does not match the expected structure, fall back to generic markdown rendering with no error.

**FR-42.** When the active file is inside a project's stage subfolder (`specs/{type}/{name}/{stage}/...`), the main pane shows a collapsible **Regenerate** panel above the file content. The panel has: (a) a list of module checkboxes derived from `GET /api/stages` for the file's stage (default all checked); (b) an "Autonomous mode" toggle whose state is persisted in `localStorage` under key `spec_driven.autonomous_mode.v1` (default: false); (c) a "Build prompt" button that calls `POST /api/regen-prompt` and renders the resulting text inside a `<details>` element with a "Copy to clipboard" button.

**FR-43.** New route `/project/:type/:name` shows the project parent page. The page lists the six stages with their modules and exposes a single master Regenerate panel that lets the user select **any subset of stages and modules** (default: all). The "Build prompt" button calls `POST /api/regen-prompt` once with the selection and the autonomous flag and shows the assembled prompt with a Copy button. Sidebar entries for projects link to this page; the existing per-file routes still work.

**FR-44.** The autonomous-mode toggle is the same value across the per-stage panel and the project parent page. Editing it in either location updates `localStorage` and re-renders both. The default is **interactive** (toggle off) so accidental autonomous regenerations are not the path of least resistance.

## Non-functional requirements

### Performance

- **NFR-1.** `GET /api/tree` returns within 200ms for the locked scale (≤50 projects, ≤200 files per project) on a typical developer laptop. Per-request filesystem walk is the implementation target — no caching needed at this scale.
- **NFR-2.** `GET /api/file?path=<rel>` returns within 100ms for files under 500 KB.
- **NFR-3.** Initial app load (HTML + JS + first `/api/tree` + first `/api/file`) completes within 2 seconds on localhost.

### Security

- **NFR-4.** All file-touching endpoints use `safe_resolve` (FR-5, FR-6). Direct filesystem access bypassing `safe_resolve` is a code-review-blocking issue.
- **NFR-5.** Symlinks are never followed (FR-4) and never serve content (FR-5.2). The behavior is enforced even if the symlink points to a file inside `EXPOSED_TREE` — symlink-as-source is still rejected, since the symlink itself is not a normal file.
- **NFR-6.** Write endpoint exists (`PUT /api/file`, added by follow-up 001) and inherits the same sandbox/extension/size checks as the read endpoint. `POST /api/regen-prompt` is read-only with respect to the filesystem (it only reads). No `DELETE`, no upload, no create-new-file endpoints.
- **NFR-7.** No authentication; localhost-only deployment is the security model. The README states this explicitly. The default Uvicorn bind address is `127.0.0.1`, NOT `0.0.0.0`.
- **NFR-8.** No CORS configuration is needed (single-origin); explicitly DO NOT enable `allow_origins=["*"]`.

### Accessibility

- **NFR-9.** Sidebar implements W3C ARIA tree pattern (FR-18, FR-19). Keyboard-only navigation reaches every interactive element. `aria-selected` and keyboard focus are visually distinct (FR-20).
- **NFR-10.** All interactive elements meet WCAG 2.1 Level AA color contrast (4.5:1 for normal text, 3:1 for UI elements).
- **NFR-11.** Headings within rendered markdown have appropriate semantic levels (`<h1>` through `<h6>`); no semantic skipping enforced by the renderer.

### Concurrency / consistency

- **NFR-12.** The backend tolerates concurrent writes by Claude Code: EAFP-based reads (FR-5.7) handle mid-write file removal. Torn reads (Claude Code's `Write` is non-atomic truncate-then-write) are accepted as a known UX wrinkle: the user refreshes the sidebar manually if a stale read produces obviously-broken content. No atomic-read shim in v1.

### Encoding

- **NFR-13.** All text is read as UTF-8 with `errors="replace"`. Files containing `\x00` bytes are rejected as binary (FR-5.6). No `chardet` dependency.

### Browser support

- **NFR-14.** Latest stable Chrome / Chromium-based browsers only. No IE, no Safari guarantees, no Firefox guarantees, no mobile responsiveness guarantees. The README states the supported environment explicitly.

### Scale

- **NFR-15.** Designed for ≤50 projects, ≤200 files per project, individual files <500 KB. Hard ceiling: single file <2 MB (enforced by FR-5.5). Beyond these bounds, behavior is undefined (no graceful-degradation requirement in v1).

### Code-organization (per CLAUDE.md `projects/` rules)

- **NFR-16.** Backend at `projects/spec_driven/backend/`, frontend at `projects/spec_driven/frontend/`. Backend's own `requirements.txt` lists direct deps; mirror into root `pyproject.toml`. Backend entry point is `main.py`, ~15 lines max — parses args (port from env), hands off to `libs/`. All Python application logic in `libs/<module>.py`. Strong typing on every parameter, return value, attribute. `str | None`, not `Optional[str]`. Domain concepts as classes; `@dataclass(frozen=True)` for immutable data containers. `node_modules/` in `.gitignore`.

## Acceptance criteria summary

Full Gherkin scenarios live in Stage 5's `validation/acceptance_criteria.md`. Top-level summary (one line each, mapping to primary flows):

- **AC-1 (first open).** Opening `http://localhost:8765/` results in `final_specs/spec.md` rendering with the project tree expanded to that file.
- **AC-2 (browse stages).** All five stage subfolders of `Projects > development > spec_driven` are clickable, expand on click, and contain at least one renderable file each (after Stages 1–5 have run).
- **AC-3 (browse settings).** All three Section 1 file kinds (`CLAUDE.md`, every agent file, every skill folder's SKILL.md) are clickable and render correctly.
- **AC-4 (cross-link navigation).** A relative markdown link from `final_specs/spec.md` to `../findings/dossier.md` is clickable and navigates in-app with URL update.
- **AC-5 (broken link).** A markdown link to a non-existent file renders muted with the correct tooltip and is not a clickable `<a>`.
- **AC-6 (external link).** An `https://` link in any markdown file renders as a real `<a>` with `target="_blank" rel="noopener noreferrer"`.
- **AC-7 (path traversal blocked).** `GET /api/file?path=../../../etc/hosts` (or Windows equivalent) returns 400 with `outside_sandbox`.
- **AC-8 (extension whitelist).** `GET /api/file?path=foo.png` returns 415.
- **AC-9 (binary content rejected).** A `.md` file containing `\x00` bytes returns 415 with `binary_content`.
- **AC-10 (size limit).** A file >2 MB returns 413.
- **AC-11 (missing stage rendering).** When `validation/` doesn't exist on disk, the sidebar still shows it as a muted-italic leaf with the `not yet generated` tooltip.
- **AC-12 (refresh).** After externally creating `validation/strategy.md`, clicking the sidebar's "Refresh" button shows the new entry in the tree.
- **AC-13 (state restoration).** Reloading the page restores the URL-driven selection and (for unrelated parts of the tree) the previous collapse state from `localStorage`.
- **AC-14 (keyboard navigation).** Tab focuses the sidebar tree; Up/Down/Right/Left/Enter keys behave per W3C ARIA APG (FR-19).
- **AC-15 (concurrent write tolerance).** Killing the file Claude Code is mid-writing during a tree-walk does not produce a 500 from `/api/tree`; the missing/partial file is either skipped or returns a structured 404 from `/api/file`.

## Open questions

These are the genuinely-undecided items that survived spec compilation. Stage 5 (validation strategy) and the implementation work units may need to take a position; if not, they remain known v2 candidates.

- **OQ-1 — Code/JSON line-number anchoring.** The dossier flagged URL fragment `#L42` scroll-and-highlight as cheap and useful. v1 spec defers it (Out of scope). Confirm defer is correct, or move it to v1?
- **OQ-2 — Push vs replace history for redirects.** FR-17 says push for navigation, replace for FR-16 folder-redirects. Confirm replace for redirects is right (back-button doesn't bounce through the redirect). Most likely uncontroversial but worth a stakeholder eye.
- **OQ-3 — Settings breadcrumb wording.** FR-29 uses literal `Settings` (shorter for the breadcrumb bar) while the in-app section header uses `Claude Settings & Shared Context`. Two different strings for the same concept may be a minor inconsistency; spec picks "Settings" for breadcrumb-only use. Confirm OK?
- **OQ-4 — Symlink display.** FR-4 silently skips symlinks. The dossier offered an alternative: surface as a marked leaf "symlink — not followed" for discoverability. Spec picks silent skip (smaller code, matches the "expected but missing" UX shape). Confirm silent skip is right?
- **OQ-5 — JSONL line-by-line vs single block.** FR-32 says one Shiki block per line for `.jsonl`. The audit log file is the main consumer. If lines get long (~few KB each), the visual cost is real. Confirm per-line is right vs a single big JSONL block?
- **OQ-6 — Sidebar fixed width.** FR-27 picks 320px fixed. The dossier left this open between fixed and draggable splitter. Spec picks fixed (simpler; revisit if dogfooding shows constant ellipsis on real spec_driven paths).
- **OQ-7 — Future audit-log surfacing.** Not in v1 scope. Worth flagging in the spec so v2 spec author knows the decision was deliberate.

End of spec.
