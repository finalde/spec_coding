# Specification — spec_driven

Stage: 4 (Spec compilation) — clean-state regeneration
Run: spec_driven-20260503-030434 (autonomous full-pipeline)

Inputs read: `user_input/revised_prompt.md`, `interview/qa.md`, `findings/dossier.md` (+ `findings/angle-*.md` consulted for cross-cutting insights). Prior `final_specs/spec.md` was deleted before this run; no surgical preservation.

---

## 1. Goal

`spec_driven` is the first concrete project in the `spec_coding` monorepo. It is an interactive **viewer / editor** for the artifacts produced by the spec-driven workflow (the six-stage pipeline `intake → interview → research → spec compilation → validation strategy → execution + streaming validation`), plus a **regeneration-prompt assembler** the user copies into Claude Code CLI to re-run any subset of stages.

Stack: FastAPI backend + React + Vite frontend, single project at `projects/spec_driven/` with `backend/` and `frontend/` subfolders sharing one README. Localhost-only (`127.0.0.1:8765`); not bound to `0.0.0.0`.

The webapp does NOT invoke Claude — it only assembles copy-paste prompts (per OQ resolved in qa.md and prior-art angle). Regeneration is user-triggered, header-driven (`# EXECUTION MODE: AUTONOMOUS|INTERACTIVE`).

## 2. User journeys (primary flows)

1. **Browse the exposed tree.** User opens the app at `/`. Sidebar shows two top-level sections — **Claude Settings & Shared Context** (CLAUDE.md, .claude/agents/, .claude/skills/) and **Projects** (every `specs/{type}/{name}/` discovered on disk). User clicks any leaf to render it.
2. **Render a markdown artifact.** Files with extension `.md` render as HTML via a sanitizing renderer. Relative links resolve against the file's directory; absolute http(s) links open in a new tab; broken links render as muted spans (NOT anchors) with a `title` describing the cause.
3. **Render a code artifact.** Files with extension `.json|.yaml|.yml` render as syntax-highlighted text. `.jsonl` renders one record per row in a JsonlView.
4. **Render the structured Q/A view.** When the active file is `interview/qa.md`, the main pane renders a tree of rounds → categories → Q/A blocks. Q tinted blue, A tinted green; category badge in the header. Each Q and each A has a ✎ inline edit pencil.
5. **Edit a file.** User clicks ✎ Edit in the toolbar → main pane swaps to a textarea editor with Save (Ctrl+S) / Discard / Close-editor controls and a dirty-dot indicator. Save errors render as a persistent inline banner above the textarea; the textarea content is preserved across save failures. Save calls `PUT /api/file`.
6. **Edit a single Q or A inside qa.md.** User clicks the ✎ pencil on a single Q or A. A small editor scoped to that block appears. Save persists back to the same `qa.md` via `PUT /api/file` (atomic full-file rewrite). Per-block editors and the file-level ✎ are mutually exclusive — the file-level toggle is disabled (visible but inert) while any per-block editor is open.
7. **Add a follow-up.** Out of scope for the webapp (follow-ups are persisted by Claude Code, not the webapp). The webapp surfaces existing follow-ups via the file-tree.
8. **Browse a project parent page.** User clicks a project entry in the sidebar (an `↗` icon next to it) → `/project/{type}/{name}` shows the stage map and a master Regenerate panel.
9. **Resolve a broken link.** User clicks a muted link → no nav happens; a tooltip names the cause. User opens the right path manually.
10. **Build a regen prompt for one stage.** User opens any file inside a project's stage subfolder. A collapsible Regenerate `<details>` panel is shown above the file content. User picks modules (default all checked), toggles Autonomous mode, clicks **Build prompt**. The assembled prompt renders inline immediately inside a bordered `regen-prompt-block` whose header bar carries the title, a "Wrap" soft-wrap toggle (default ON, not persisted), and a prominent **Copy** button. The actions row beside Build prompt shows a section-breakdown line `{N} stages selected, {K} follow-ups inlined, autonomous={…}, {bytes} KB`. A muted warning banner renders above the block when the response carries `warning != null`.
11. **Build a regen prompt for the whole project.** User clicks the project link in the sidebar → `/project/{type}/{name}`. Master Regenerate panel selects any subset of stages and modules; one combined prompt is assembled.
12. **Boot smoke.** `make run-prod` (or `python main.py`) starts FastAPI; `GET /api/tree` returns 200 with the expected sidebar shape; the SPA loads at `http://127.0.0.1:8765/`.

## 3. Functional requirements

### Backend — sidebar tree & file reads

**FR-1.** `GET /api/tree` returns the EXPOSED_TREE: a recursive JSON node `{name, path, type, children[]}` rooted at the repo. Type ∈ `{section, file, type, project, stage}`. Frontend descends `node.children` uniformly (single field name across all node types — no `task_type.projects`/`project.stages` drift).

**FR-2.** EXPOSED_TREE includes: `CLAUDE.md`, every `.claude/agents/*.md`, every `.claude/skills/**/SKILL.md`, every `.claude/skills/agent_team/playbooks/*.md`, every `.claude/agent_refs/**/*.md`, and every `specs/{type}/{name}/` walked recursively (limited to canonical stage subfolders: `user_input/`, `interview/`, `findings/`, `final_specs/`, `validation/`, plus their `promoted.md` sidecars and the `changelog.md`).

**FR-3.** `GET /api/file?path=<rel>` returns `{path, content, mtime, bytes}` for a file inside the EXPOSED_TREE. Allowed extensions: `.md, .json, .yaml, .yml, .jsonl, .txt, .png, .jpg`. Disallowed extensions return 415. Files >1 MB return 413. Path outside the EXPOSED_TREE returns **404** (single error, NOT 403/404 split — removes enumeration side-channel per localhost-fs-sandbox-risks angle).

**FR-4.** `safe_resolve(rel)` canonicalizes FIRST then asserts containment. It MUST: normalize `/` and `\`; reject absolute paths; reject paths containing `..` after normalization; reject Windows reserved device names (`CON`, `PRN`, `AUX`, `NUL`, `COM1..COM9`, `LPT1..LPT9`, including with extensions); reject Alternate Data Streams (`::$DATA`, `:stream`); reject 8.3 short names; reject every reparse point including junctions (not just symlinks); case-fold for NTFS. A path that resolves outside the EXPOSED_TREE returns 404 (not 403).

**FR-5.** Every successful `GET /api/file` response carries headers `X-Content-Type-Options: nosniff` and `Content-Disposition: attachment` (defense against content-sniffing exploits per OWASP / localhost-fs-sandbox-risks angle).

### Backend — editing

**FR-6.** `PUT /api/file` accepts JSON body `{path, content}` for a path inside the EXPOSED_TREE. Same safe_resolve sandbox + extension/size rules as `GET /api/file`. Writes via temp file + `os.replace` for atomic-replace. Returns `{path, bytes, mtime}` on success.

**FR-7.** `PUT /api/file` enforces a 1 MB body cap at the FastAPI level AND at any reverse-proxy layer (per OWASP File Upload Cheat Sheet). Above 1 MB returns 413 `{detail: {kind: "too_large"}}`.

**FR-8.** `PUT /api/file` validates the body's first 16 bytes as plain text (no NUL bytes, valid UTF-8) for the text extensions. Image extensions (`.png`/`.jpg`) are NOT writable in v1; PUT to an image path returns 415. SVG is NOT in the allowlist (treated as code-execution vector per localhost-fs-sandbox-risks angle).

**FR-9.** Every state-changing endpoint (`PUT /api/file`, `POST /api/regen-prompt`, `POST /api/promote`, `DELETE /api/promote`) validates `Origin` and `Host` headers. The accepted set is the loopback-equivalence allow-list at the bound port: `{http://127.0.0.1:<port>, http://localhost:<port>}` for `Origin` and `{127.0.0.1:<port>, localhost:<port>}` for `Host`. Anything else (missing header, foreign domain, wrong port, IPv6 literal) returns 403 (defense against DNS rebinding / browser-driven CSRF). The two loopback literals are admitted because they resolve to the same loopback socket and the browser sends whichever the user typed in the address bar — refusing one of them is a usability bug, not added security.

### Backend — regeneration prompt assembly

**FR-10.** `GET /api/stages?project_type=&project_name=` returns the canonical six-stage definition with each stage's `id, label, folder, invocation, modules[]` (each module: `id, label, relative_path, description`). Hard-coded server-side from a single source of truth.

**FR-11.** `POST /api/regen-prompt` accepts `{project_type, project_name, stages: string[], modules: {stage_id: string[]}, autonomous: bool}` and returns `{prompt, warning, selected_stages_count, follow_ups_count, autonomous, bytes}`. The prompt MUST:
- (a) Open with the literal first line `# EXECUTION MODE: AUTONOMOUS` or `# EXECUTION MODE: INTERACTIVE` (no header → INTERACTIVE).
- (b) Under AUTONOMOUS, the next non-blank line is the verbatim sentence: "Do not call AskUserQuestion. For anything unclear, use your best judgment, record the choice inline in the artifact, and keep going. Produce every requested artifact below in this single turn before stopping."
- (c) Inline the current `revised_prompt.md` (or `raw_prompt.md` if no revised exists) as a literal markdown block.
- (d) List every `user_input/follow_ups/*.md` filename in numerical order.
- (e) Walk each selected stage with its invocation hint and module list.
- (f) For each selected stage with a non-empty `<stage>/promoted.md`, inline the promoted file verbatim under a "Pinned items (MUST survive regeneration)" section.
- (g) Close with a `### Constraints` section that names: CLAUDE.md state surfaces, canonical paths, the parent-direct manager-spawn contract, no-AskUserQuestion-in-autonomous-mode, the **read-zero contract** ("regeneration deletes prior outputs first; new generation reads only the inputs"), and the audit-event protocol (`regen.delete.planned`, `regen.delete.completed`, `regen.write.completed`).

**FR-12.** Size policy on `POST /api/regen-prompt`: prompt body ≤ 50 KB → `warning: null`. 50 KB < body ≤ 1 MB → `warning: "<text>"` (warn-don't-truncate). Body > 1 MB → 413 `{detail: {kind: "too_large", bytes: <count>}}`. The prompt is ALWAYS emitted in full when status is 200; truncation is forbidden.

### Backend — promotion (pin/unpin)

**FR-13.** `POST /api/promote` accepts `{project_type, project_name, stage_folder, source_file, item_id, item_text}` and appends a verbatim block to `specs/{type}/{name}/{stage_folder}/promoted.md`. Allowed `stage_folder` values: `interview, findings, final_specs, validation`. Stage 6 is excluded.

**FR-14.** `DELETE /api/promote` accepts `{project_type, project_name, stage_folder, item_id}` and removes the matching block from `promoted.md`. Other pins are untouched.

### Frontend — sidebar and routing

**FR-15.** Routes: `/` (home), `/file/<rel>` (file pane), `/project/<task_type>/<task_name>` (project parent page).

**FR-16.** Sidebar uses a single recursive `<TreeNode>` component that descends `node.children`. Test selector `data-testid="sidebar"` identifies the sidebar root; `data-testid="tree-leaf"` marks each leaf; `data-testid="project-link"` marks the per-project `↗` link to the project parent page.

**FR-17.** Selected file is reflected in the URL via `react-router-dom`. Deep-link to `http://127.0.0.1:8765/file/specs/development/spec_driven/interview/qa.md` boots the app on the correct file with the QaView active.

### Frontend — render dispatch

**FR-18.** Main pane dispatches by file path / extension to one of: `MarkdownView` (default for `.md`), `QaView` (specifically for `interview/qa.md`), `JsonlView` (`.jsonl`), `CodeView` (`.json/.yaml/.yml`), `ImagePlaceholder` (`.png/.jpg`).

**FR-19.** Every render component that performs a non-trivial parse during render MUST be wrapped in a real React **Error Boundary** class component (`componentDidCatch` / `getDerivedStateFromError`) — NOT `try { return <Foo .../> } catch { return <Fallback /> }`. The catch in the latter pattern does NOT catch errors thrown during React reconciliation.

**FR-20.** When QaView's parser fails on a real `qa.md`, the Error Boundary falls back to MarkdownView with a one-line banner: "Could not parse structured Q/A view; rendering raw markdown. (cause: <message>)". The fallback path is reachable and asserted by an e2e scenario opening a real qa.md the parser cannot handle.

**FR-21.** The QaView answer regex MUST accept BOTH:
- Interactive form: `- A: <text>`
- Autonomous form: `- A *(judgment call — chose X because Y)*: <text>`
The unit-test fixture inventory MUST include a real on-disk autonomous-mode `qa.md` snippet alongside the interactive form (per `agent_refs/validation/development.md` move #10).

### Frontend — markdown rendering

**FR-22.** Markdown renders via `react-markdown` + `rehype-sanitize` (no raw HTML allowed). Code fences use `shiki` for syntax highlighting (themes for `python`, `typescript`, `javascript`, `tsx`, `bash`, `json`, `yaml`, `markdown`). Inline code uses a CSS class only (no syntax highlighting).

**FR-23.** Relative markdown links `[text](path)` resolve against the current file's directory: target is rewritten to `/file/<resolved-rel>`; click navigates the SPA (no full reload). Absolute http(s) links open in a new tab via `target="_blank" rel="noopener noreferrer"`. Anchor-only links `[text](#anchor)` scroll to the in-page anchor without nav.

**FR-24.** Broken links render as muted `<span class="link-broken" aria-disabled="true">` (NOT an `<a>` element) with `title="<cause>"` (e.g., `file not found`, `outside exposed tree`, `case mismatch`, `anchor not in document`). The same component renders for missing stage subfolders, the inline stale-tree message, and save-failure banners (single broken-link component).

### Frontend — file editor

**FR-25.** Every file in the main pane shows a ✎ Edit toolbar button. Clicking it swaps the rendered view for a `<textarea>` editor with three controls: **Save** (Ctrl+S), **Discard** (revert to last-saved), **Close editor** (back to rendered view). The Save button is **never disabled** during an in-flight save error — keep it focusable / clickable so the user can retry without using the mouse (Tab-focus accessibility).

**FR-26.** The editor displays a "dirty dot" (filled circle) next to the toolbar's filename whenever the textarea content !== the last-saved text (deep-equality). The dot disappears on successful save and on Discard.

**FR-27.** Save errors render as a **persistent inline banner above the textarea** (NOT a toast). The banner reads: `Could not save: <message>`. The user's textarea content is **preserved across save failures** — no auto-clearing, no auto-revert.

**FR-28.** On successful save the editor stays open with the saved content as the new baseline. The user explicitly clicks "Close editor" to return to rendered view.

### Frontend — structured Q/A view

**FR-29.** When the active file is `interview/qa.md`, the main pane renders a tree-view: `## Round N` → `### category` → Q/A pairs. Q blocks render with a blue tint, A blocks with a green tint; category renders as a colored badge above its Q/A list.

**FR-30.** Each Q and each A has a ✎ inline edit pencil. Clicking it swaps the block for a small `<textarea>` with **Save** (Ctrl+S) / **Cancel** controls scoped to that block. Save persists back to the same `qa.md` via `PUT /api/file` with the full file's new content (the structured view is a projection; disk is always the full markdown).

**FR-31.** While any per-block editor is open, the file-level ✎ Edit toggle is **disabled but still visible** (mutually-exclusive save scopes; never hide a control the user expected to find).

**FR-32.** Whole-file ✎ Edit on `interview/qa.md` works exactly like FR-25–FR-28: ignores the structured view, edits the raw markdown.

### Frontend — Regenerate panel

**FR-33.** When the active file is inside a project's stage subfolder, the main pane shows a collapsible **Regenerate** panel (`<details>` titled "Regenerate", default-collapsed) above the file content. Contents:
- (a) Module checkboxes derived from `GET /api/stages` for the file's stage (default all checked).
- (b) An "Autonomous mode" toggle persisted in `localStorage` under key `spec_driven.autonomous_mode.v1` (default false).
- (c) "Build prompt" button calls `POST /api/regen-prompt`.
- (d) After build: a one-line section breakdown in the actions row beside "Build prompt" reading `{N} stages selected, {K} follow-ups inlined, autonomous={true|false}, {bytes} KB` (locale-formatted bytes).
- (e) When the API response carries a non-null `warning`, render a muted banner reading `warning: {warning} — verify your selection before pasting` ABOVE the prompt block.
- (f) The assembled prompt is rendered **inline** (no inner `<details>` to expand) inside a bordered `regen-prompt-block` consisting of a header bar followed by a `<pre>` body. The header bar contains, left-to-right: an "Assembled prompt" title; a "Wrap" checkbox toggle (soft-wrap on/off; default ON; not persisted); a prominent primary-style **Copy** button whose label flips to "Copied!" for ~1.5s on click and which carries `aria-live="polite"` plus a fixed minimum width so the label flip does not shift layout. The `<pre>` defaults to soft-wrap (`white-space: pre-wrap; word-break: break-word`) and reverts to fixed-width with horizontal scroll when the toggle is off.

**FR-34.** Route `/project/:type/:name` shows the project parent page. Lists all six stages with their modules and exposes a single master Regenerate panel that lets the user select any subset of stages and modules (default: all). Same breakdown + warning + Copy contract as FR-33.

**FR-35.** The autonomous-mode toggle is the same value across the per-stage panel and the project parent page. Editing it in either updates `localStorage` and re-renders both consumers (via a `storage` event listener for cross-tab + an in-process subscription for same-tab). Default: **interactive** (toggle off).

### Frontend — promotion (pin)

**FR-36.** Inside a stage view, every atomic item that is a candidate for pinning (a Q/A pair in qa.md, a recommendation bullet in dossier.md, an FR-NN/AC-NN/SYS-NN block in spec.md / acceptance_criteria.md / system_tests.md) shows a 📌 toggle on hover. Clicking it calls `POST /api/promote` (or `DELETE /api/promote` if already pinned). The pinned state is reflected in `<stage>/promoted.md`.

**FR-37.** Stage 6 (project code) is **excluded** from promotion in v1 — the spec_driven webapp does NOT show 📌 toggles on `projects/{name}/` files.

### Operational

**FR-38.** `python main.py` starts uvicorn on `127.0.0.1:8765` (NOT `0.0.0.0`). The server is unreachable on the LAN IP. `0.0.0.0` is forbidden in any default config.

**FR-39.** A `Makefile` at `projects/spec_driven/` provides targets: `run` (alias for `run-backend`), `run-backend` (FastAPI on `127.0.0.1:8765`), `run-frontend` (Vite dev server on `127.0.0.1:5173`), `run-prod` (single-process: backend serves the prebuilt SPA from `backend/static/`), `test-backend`, `test-frontend`, `e2e`, `build-frontend`. The two split dev-server targets let the operator launch each tier in its own terminal during development; `run` keeps its prior backend-only semantics so AC-29 / SYS-17 stay literal. None of the targets invoke `uv run` without a pip fallback (per `agent_refs/validation/development.md` move #6).

## 4. Non-functional requirements

### Performance

- **NFR-1.** `GET /api/tree` returns within 200 ms for the locked scale (≤50 projects, ≤200 files per project) on a typical developer laptop.
- **NFR-2.** `GET /api/file` returns within 100 ms for files <500 KB.
- **NFR-3.** Initial app load (HTML + JS + first `/api/tree` + first `/api/file`) completes within 2 s on localhost.

### Security

- **NFR-4.** All file-touching endpoints use `safe_resolve`. Direct filesystem access bypassing `safe_resolve` is a code-review-blocking issue.
- **NFR-5.** Symlinks, junctions, and any other reparse point are rejected. No path that includes a reparse point at any segment is served.
- **NFR-6.** Only sanctioned mutation endpoints exist: `PUT /api/file`, `POST /api/regen-prompt`, `POST /api/promote`, `DELETE /api/promote`. No DELETE on `/api/file`, no upload, no create-new-file. PATCH/DELETE on file return 405.
- **NFR-7.** `Origin` and `Host` validation on every state-changing route (FR-9). Requests not from the bound localhost return 403.
- **NFR-8.** No raw HTML injected into the markdown render path. Sanitizer is `rehype-sanitize` with the default schema; raw HTML in source markdown is dropped.
- **NFR-9.** SVG is NOT in the file-extension allowlist (treated as code-execution vector per localhost-fs-sandbox-risks angle).

### Reliability

- **NFR-10.** Writes are atomic via temp file + `os.replace`. Power-loss tests are best-effort on NTFS (skipped on Windows per `agent_refs/validation/development.md` move #5).
- **NFR-11.** `regen-prompt` size policy is warn-don't-truncate per FR-12; the prompt body is never silently truncated.

### Cross-platform

- **NFR-12.** Runs on Windows + Git Bash. POSIX-only tests use `pytest.mark.skipif(sys.platform == "win32", reason="...")`. Skipping is fine; silent passing is not.
- **NFR-13.** Path normalization handles both `/` and `\` separators on input. All persisted paths are forward-slash.

### Accessibility

- **NFR-14.** All interactive controls have visible focus styles. Keyboard navigation works through sidebar, breadcrumb, editor, regen panel.
- **NFR-15.** ARIA: error banners use `role="alert"`; copy-feedback uses `aria-live="polite"`; the Regenerate `<details>` and the file-tree expand/collapse use native semantics.
- **NFR-16.** Color contrast meets WCAG AA on the dark code-block theme used for the assembled regen prompt body.

## 5. Acceptance criteria (Gherkin shorthand)

- **AC-1 (sidebar tree).** `GET /api/tree` returns a recursive `{name, path, type, children}` shape with `children` present on every non-leaf. Frontend Sidebar renders ≥1 leaf under each top-level section using `node.children`.
- **AC-2 (file read).** `GET /api/file?path=specs/development/spec_driven/final_specs/spec.md` returns 200 with `content` ≈ the file bytes (UTF-8). Disposition is `attachment`; `nosniff` header present.
- **AC-3 (path traversal).** `GET /api/file?path=../etc/passwd` and `/api/file?path=specs/../../etc/passwd` both return 404 (single status, NOT 403/404 split).
- **AC-4 (Windows reserved name).** `GET /api/file?path=specs/development/spec_driven/CON.md` returns 404.
- **AC-5 (ADS).** `GET /api/file?path=specs/development/spec_driven/final_specs/spec.md::$DATA` returns 404.
- **AC-6 (junction).** A junction inside `specs/` pointing outside the EXPOSED_TREE is rejected; reading any file via that junction returns 404.
- **AC-7 (size cap on read).** `GET /api/file?path=<huge file >1MB>` returns 413.
- **AC-8 (extension whitelist on read).** `GET /api/file?path=...exe` returns 415.
- **AC-9 (PUT roundtrip).** `PUT /api/file {path: ".../scratch.md", content: "x"}` then `GET` of the same path returns `content == "x"`.
- **AC-10 (PUT size cap).** `PUT /api/file` with a 1.5 MB body returns 413 with `kind: "too_large"`.
- **AC-11 (Origin validation).** `PUT /api/file` from `Origin: http://evil.example.com` returns 403.
- **AC-12 (verb whitelist).** `PATCH /api/file` and `DELETE /api/file` return 405.
- **AC-13 (regen prompt build).** `POST /api/regen-prompt` returns `{prompt, warning, selected_stages_count, follow_ups_count, autonomous, bytes}`. Above 50 KB the warning field is non-null; above 1 MB returns 413.
- **AC-14 (autonomous header).** `POST /api/regen-prompt {autonomous: true}` returns a prompt opening with `# EXECUTION MODE: AUTONOMOUS` and the verbatim imperative line per FR-11(b).
- **AC-15 (interactive default).** `POST /api/regen-prompt {autonomous: false}` returns a prompt opening with `# EXECUTION MODE: INTERACTIVE` (no imperative line).
- **AC-16 (read-zero in constraints).** Every assembled prompt's `### Constraints` section includes the read-zero contract sentence ("regeneration deletes prior outputs first; new generation reads only the inputs.").
- **AC-17 (pin survives in prompt).** When `interview/promoted.md` is non-empty and stage `interview` is selected, the assembled prompt includes a `### Pinned items (MUST survive regeneration)` section with the promoted file's content inlined verbatim.
- **AC-18 (deep-link to qa.md).** Navigating to `/file/specs/development/spec_driven/interview/qa.md` renders `<main>` with non-empty content, the QaView component is mounted (`data-testid="qa-view"` present), `consoleErrors === []`, and at least one Q-tinted block + one A-tinted block is in the DOM.
- **AC-19 (autonomous Q/A parses).** A real autonomous-mode `qa.md` snippet (with `- A *(judgment call — chose X because Y)*: text`) renders parsed by QaView, NOT via the Error Boundary fallback.
- **AC-20 (QaView fallback path is reachable).** A deliberately-malformed `qa.md` opens via deep-link, renders via the Error Boundary fallback (raw MarkdownView + a one-line banner), `consoleErrors === []`, page is non-empty.
- **AC-21 (broken link rendering).** A relative link to a non-existent file renders as `<span class="link-broken" aria-disabled="true">` with a `title` attribute naming the cause; the wrapper is NOT an `<a>`.
- **AC-22 (regen panel default-collapsed).** On a stage file, the `<details title="Regenerate">` is closed on first render.
- **AC-23 (regen prompt visible-after-build).** After clicking Build prompt, the assembled prompt is rendered inline inside a `regen-prompt-block` (no inner `<details>` to expand). The header bar contains the title, a "Wrap" toggle (default checked), and a prominent **Copy** button. The actions row beside Build prompt shows the breakdown line.
- **AC-24 (Copy flips label).** Clicking the **Copy** button copies the full prompt to the clipboard and flips the button label to "Copied!" for ~1500 ms; the button has `aria-live="polite"` and a fixed minimum width so the flip does not shift layout.
- **AC-25 (Wrap toggle).** Unchecking the "Wrap" toggle switches the `<pre>` to fixed-width with horizontal scroll; re-checking restores soft-wrap. Wrap state is NOT persisted to `localStorage`.
- **AC-26 (autonomous toggle persistence).** Toggling autonomous mode in either the per-stage or project-page panel updates `localStorage["spec_driven.autonomous_mode.v1"]`; reloading the page preserves the value; cross-tab updates propagate via `storage` events.
- **AC-27 (project page master regen).** Navigating to `/project/development/spec_driven` shows the six stages with module checkboxes and a master Regenerate panel.
- **AC-28 (boot smoke).** `make run-prod` starts the server cleanly; `GET /api/tree` returns 200; the SPA loads at `http://127.0.0.1:8765/` and the Sidebar contains ≥1 leaf under each top-level section.
- **AC-29 (Uvicorn bind).** `make run` binds to `127.0.0.1:8765`. `0.0.0.0` does NOT appear in the Uvicorn config under any default invocation.

## 6. Open questions (deferred to future runs)

- **OQ-1.** Download .md fallback for >1 MB regen prompts (deferred to v2).
- **OQ-2.** Pre-flight Origin validation in v1 vs. defer to multi-user variant — spec mandates v1 (NFR-7).
- **OQ-3.** SVG handling — spec drops SVG from allowlist for v1 (NFR-9). Sanitize-on-write is a v2 path.
- **OQ-4.** Per-Q vs whole-file lock — spec chose "disabled-but-visible" (FR-31).
- **OQ-5.** Floating Copy for very-tall prompt blocks — deferred to v2 (current max-height 520 px is sufficient for surveyed sizes).
- **OQ-6.** Auto-refresh on file changes — out of scope (revised_prompt §"Out of scope").
- **OQ-7.** Multi-user / auth — out of scope (revised_prompt §"Out of scope").

## 7. Promotion preservation

If `<stage>/promoted.md` is non-empty for any of the four spec-pipeline stages (interview, findings, final_specs, validation), every pin MUST appear verbatim in the regenerated artifact. Severity for a missing pin: `critical`. The validation strategy at stage 5 MUST include a "pin preservation" check that asserts every pin in `<stage>/promoted.md` is a substring (modulo whitespace normalization) of the regenerated artifact. Stage 6 (project code) is excluded from pinning in v1 (FR-37).

For this run: `interview/promoted.md` contains pin-001 (Round 1 / functional-scope / "All discovered" answer). It is preserved verbatim in the regenerated `interview/qa.md` under the functional-scope category.
