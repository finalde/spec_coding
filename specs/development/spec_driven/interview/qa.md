# Interview â€” spec_driven

Run: spec_driven-20260502-clean
Stage: 2 (Interview) â€” clean-state regeneration
Compiled by: parent (agent_team skill, parent_direct synthesis under EXECUTION MODE: AUTONOMOUS)
Inputs read: `user_input/revised_prompt.md`, `CLAUDE.md`, `.claude/agents/agent_team__interview_manager.md`
Inputs explicitly NOT read (per `CLAUDE.md â†’ ## Regeneration prompts & autonomous mode â†’ ### Regeneration semantics: read-zero from prior outputs`): any prior `interview/qa.md`, `findings/*`, `final_specs/*`, `validation/*`, `projects/spec_driven/*`.

> **Architecture note (clean-state autonomous regen).** Per CLAUDE.md "Tool scoping and team coordination", the parent owns spawning. The interview manager subagent identifies probe categories and emits a question pool back to the parent. Under `# EXECUTION MODE: AUTONOMOUS` the parent does NOT call `AskUserQuestion`; instead it pre-answers each probe with a best-judgment default, recording the choice as `*(judgment call â€” chose X because Y)*` so a future interactive run can revise with full visibility.

## Categories probed

The interview manager identified seven probe categories from the revised prompt:

- **functional-scope** â€” what the viewer/editor surfaces in each sidebar section, the v1 in/out boundary, and how non-markdown files render.
- **discovery-data-model** â€” how the backend finds projects on disk, what root directories it scans, caching policy, and target scale.
- **ux-navigation** â€” sidebar grouping, landing page, code/markdown rendering, in-app link resolution, large-file behavior.
- **deployment-runtime** â€” process topology (single binary vs. two processes), default port, startup commands, and how the backend locates the repo root.
- **editing-and-regen** â€” file-level editor controls, structured Q/A view contract, per-stage and project-master regen panels, autonomous-mode toggle.
- **success-criteria** â€” what counts as v1 done, target browser, validation layers (BDD/e2e/unit), e2e framework, and whether a second project ships in v1.
- **security-and-failure** â€” path-traversal sandbox boundaries, symlink policy, atomic-write semantics, error UX for stale-tree and concurrent-write situations.

## Round 1 (autonomous, all judgment-call answers)

### functional-scope

**Q:** Section 1 ("Claude Settings & Shared Context") â€” exact sources?
- A *(judgment call â€” chose "fixed three globs")*: `CLAUDE.md` at repo root, `.claude/agents/*.md`, `.claude/skills/**/SKILL.md`. Nothing else. The revised prompt names exactly these three sources; no additional `specs/`-rooted shared context in v1.

**Q:** Per-project tree â€” which subfolders does the Projects section expose?
- A *(judgment call â€” chose "all five canonical stages")*: `user_input/`, `interview/`, `findings/`, `final_specs/`, `validation/`. No `changelog.md`, no audit folder, no output folder, no follow-ups directory in v1 (follow-ups view is deferred â€” they live under `user_input/follow_ups/`).

**Q:** Non-markdown files (YAML, JSON, JSONL) â€” how do they render?
- A *(judgment call â€” chose "Shiki-highlighted with line numbers")*: client-side syntax highlighting via Shiki; line numbers in the gutter. `.jsonl` renders as one Shiki block per line, malformed lines fall through as plain text.

**Q:** Implicit out-of-scope items â€” confirm v1 excludes search, watcher, multi-user, deletes, uploads?
- A *(judgment call â€” chose "all confirmed out, but editing IS in")*: no auth, no search, no file-watch, no auto-refresh, no run controls, no deletes, no uploads. Editing IS in scope (revised prompt explicitly lifted the readonly constraint via follow-up 001). Image rendering is out â€” placeholder only.

### discovery-data-model

**Q:** How does the viewer discover projects?
- A *(judgment call â€” chose "scan per request")*: backend walks `specs/{task_type}/{task_name}/` on every API call. No persistent index, no manifest, no watcher.

**Q:** Which root directories surface as projects?
- A *(judgment call â€” chose "specs/ only")*: Projects tree is derived solely from `specs/{task_type}/{task_name}/`. Output folders (`projects/`, `ai_videos/`) are NOT surfaced as projects in v1.

**Q:** Caching strategy?
- A *(judgment call â€” chose "none")*: read filesystem on every request. No ETag, no TTL, no in-memory cache. Locked scale (â‰¤50 projects, â‰¤200 files per project) makes this safe.

**Q:** Target scale?
- A *(judgment call â€” chose "small")*: â‰¤50 projects, â‰¤200 files per project, individual files <500 KB. Hard ceiling 2 MB. Optimize for clarity, not throughput.

### ux-navigation

**Q:** Relative-link behavior between artifacts?
- A *(judgment call â€” chose "internal clickable, external new tab, broken muted")*: relative links resolving inside the exposed tree become in-app navigations. External (`http`/`https`/`mailto`) open in a new tab with `rel="noopener noreferrer"`. Broken links render muted with `title` tooltip â€” never as dead `<a>` elements.

**Q:** Sidebar grouping when multiple `task_type`s exist?
- A *(judgment call â€” chose "collapsible by type")*: one collapsible section per `task_type` (development, ai_video, â€¦). The section containing the current project default-expands.

**Q:** Landing page on first open?
- A *(judgment call â€” chose "spec_driven's spec.md")*: auto-redirect to `/projects/development/spec_driven/final_specs/spec.md` if it exists, else `/projects/development/spec_driven/user_input/revised_prompt.md`.

**Q:** Syntax highlighter?
- A *(judgment call â€” chose "Shiki")*: VS-Code-grade tokenization, dark-mode-friendly, identical themes for code blocks in markdown and standalone YAML/JSON files.

**Q:** Large-file behavior?
- A *(judgment call â€” chose "render in full")*: render any file in full regardless of size. No truncation, no streaming, no virtualization. Hard ceiling 2 MB enforced server-side.

**Q:** Sidebar width?
- A *(judgment call â€” chose "fixed 320px")*: simpler than a draggable splitter; revisit if dogfood shows constant ellipsis on real spec_driven paths.

### deployment-runtime

**Q:** Process topology â€” single FastAPI or two processes?
- A *(judgment call â€” chose "single FastAPI in production, two-process in dev")*: `make run` builds the React bundle into `backend/static/` and starts a single FastAPI process serving both `/` and `/api/`. `make dev` runs FastAPI with `--reload` and Vite dev server simultaneously for hot-reload.

**Q:** Default port?
- A *(judgment call â€” chose "8765, env override")*: fixed `8765` by default; overridable via `SPEC_DRIVEN_PORT` env var. Process exits non-zero if the port is in use.

**Q:** Startup convention?
- A *(judgment call â€” chose "Makefile with make run / make dev")*: Makefile at `projects/spec_driven/`. README documents both targets and the URL.

**Q:** How does the backend locate the repo root?
- A *(judgment call â€” chose "walk upward from main.py")*: from its own file, walks parent directories until a directory contains all three of `CLAUDE.md`, `specs/`, `.claude/`. Caches the resolved value. Fails fast (non-zero exit) if not found.

### editing-and-regen

**Q:** File-level editor toolbar contents and placement?
- A *(judgment call â€” chose "Save / Discard / Close-editor toolbar above the textarea")*: âœŽ Edit button on the reader header swaps the rendered view for a plain `<textarea>` with a toolbar above it. The toolbar shows: Save (Ctrl+S / Cmd+S), Discard changes, Close editor, plus a status slot for "Unsaved changes" / "Saved." indicators.

**Q:** Dirty-state indicator?
- A *(judgment call â€” chose "filled-circle dot + textual badge")*: VS-Code-style filled-circle "dirty dot" near the file path AND a textual "Unsaved changes" badge in the toolbar. Dirty state is computed via deep equality of `currentText` vs `lastSavedText` (NOT a "user typed" flag â€” sidesteps GitHub web editor's CRLF-normalization anti-pattern).

**Q:** Save semantics on success?
- A *(judgment call â€” chose "stay in editor")*: Save success leaves the editor open and updates `lastSavedText`. The dirty dot clears; "Saved." appears in an aria-live region. Closing is a separate user action.

**Q:** Save error surfacing?
- A *(judgment call â€” chose "persistent inline banner above textarea")*: Save failure renders a persistent inline banner above the textarea with the structured error key + kind. NOT a toast (would disappear with unsaved work in the buffer). Banner clears only on a successful Save.

**Q:** Structured Q/A view for `interview/qa.md`?
- A *(judgment call â€” chose "color-blocks with per-Q / per-A pencil; fall back to plain markdown if parse fails")*: parse `## Round N` â†’ `### category` â†’ `**Q:**` paragraph â†’ `- A:` bullet shape. Question blocks get a distinct background tint, answer blocks a different tint, category gets a small badge. Each Q and each A has its own âœŽ pencil that opens an inline editor scoped to that block; saving rewrites the whole `qa.md` via `PUT /api/file`. If parse fails, generic markdown rendering with no error UI.

**Q:** Per-stage Regenerate panel UI?
- A *(judgment call â€” chose "collapsible <details> above file content, default-collapsed")*: native `<details>` element; default-collapsed so the file stays the focal element. Module checkboxes derived from `GET /api/stages` (default all checked); autonomous-mode toggle persisted in `localStorage` under `spec_driven.autonomous_mode.v1` (default off); "Build prompt" button calls `POST /api/regen-prompt` and shows the assembled prompt with a Copy button + section breakdown line + size-warning banner.

**Q:** Project parent page?
- A *(judgment call â€” chose "separate route /project/:type/:name")*: distinct route shows the project's stage map with a single master Regenerate panel that lets the user select any subset of stages and modules; produces one combined copy-paste prompt. Sidebar entries for projects link to this page; the existing per-file routes still work.

**Q:** Autonomous-mode header contract?
- A *(judgment call â€” chose "literal headers + verbatim imperative line, contract anchored in CLAUDE.md")*: the assembled prompt opens with `# EXECUTION MODE: AUTONOMOUS` or `# EXECUTION MODE: INTERACTIVE`. Under AUTONOMOUS, the next non-blank line is the verbatim sentence "Do not call AskUserQuestion. For anything unclear, use your best judgment, record the choice inline in the artifact, and keep going. Produce every requested artifact below in this single turn before stopping." The contract is enforced model-side because Claude Code reads `CLAUDE.md` as project memory; the header restates the contract in the pasted message itself.

**Q:** Read-zero contract surfacing in the prompt?
- A *(judgment call â€” chose "include in the constraints section")*: the assembled prompt's `### Constraints` section includes a constraint stating that regeneration deletes prior outputs first and re-reads only the inputs (per CLAUDE.md â†’ "Regeneration semantics: read-zero from prior outputs").

### success-criteria

**Q:** v1 dogfood demo scope?
- A *(judgment call â€” chose "spec_driven dogfoods itself")*: user can browse all five stage subfolders of `Projects/development/spec_driven/` AND all three Settings file kinds, edit any file in the exposed tree, and assemble copy-paste regen prompts at per-stage and per-project granularity. Audit logs and project-output folders are NOT required in v1.

**Q:** Target browser?
- A *(judgment call â€” chose "latest Chrome / Chromium")*: latest stable Chrome or Chromium-based browsers. No IE, no Safari guarantees, no Firefox guarantees, no mobile responsiveness.

**Q:** Validation layers?
- A *(judgment call â€” chose "pytest unit + Playwright e2e + manual security probes")*: backend gets pytest unit + integration tests; frontend e2e via Playwright against the dogfood happy path; security probes (path traversal, symlink, binary content) executed manually via curl before release.

**Q:** Does v1 ship with a second project?
- A *(judgment call â€” chose "no")*: only `Projects/development/spec_driven/` ships. Multi-project rendering verified by component tests using fixture data.

### security-and-failure

**Q:** Path-traversal sandbox helper?
- A *(judgment call â€” chose "single safe_resolve helper used by every endpoint")*: `safe_resolve(rel: str, root: Path) -> Path` does `(root / rel).resolve(strict=False).relative_to(root.resolve())` and catches `ValueError` â†’ 400 `outside_sandbox`. Used by every API endpoint that takes a path. Reject `Path.is_symlink()` entries before resolving. Critically: do NOT use `os.path.commonprefix` (the Starlette CVE-2023-29159 mistake).

**Q:** Symlink policy?
- A *(judgment call â€” chose "refuse silently")*: skip `Path.is_symlink()` entries during directory listing AND verify resolved paths are not symlinks at `safe_resolve` time. Symlinks never serve content, never appear in the tree.

**Q:** Atomic write for `PUT /api/file`?
- A *(judgment call â€” chose "temp file + os.replace")*: write to a sibling temp file in the same directory followed by `os.replace()`. On failure, the temp file is removed and the original is left untouched. Sidesteps Claude Code's `Write` torn-write window.

**Q:** URL-decode layering?
- A *(judgment call â€” chose "FastAPI decodes once, safe_resolve does not re-decode")*: the `path` query param is URL-decoded exactly once by FastAPI's query-param layer; `safe_resolve` receives already-decoded input. Double-decoding is a path-traversal bypass per OWASP.

**Q:** Encoding/binary handling?
- A *(judgment call â€” chose "UTF-8 errors=replace + NUL-byte rejection")*: read with `encoding="utf-8", errors="replace"`. Files containing `\x00` bytes are rejected as `binary_content`. No `chardet` dependency. 2 MB hard ceiling enforced via `Content-Length`-equivalent on the encoded payload.

**Q:** Stale-tree click UX?
- A *(judgment call â€” chose "structured 404 + inline refresh button")*: when a sidebar click resolves to a now-missing file, the API returns `{"error": "not_found", "kind": "file_removed"}`. The frontend shows a non-modal inline message with a "refresh sidebar" button. No watcher, no WebSocket â€” the user manually refreshes.

**Q:** Concurrent-write tolerance?
- A *(judgment call â€” chose "EAFP; never 500")*: every file-touching endpoint uses EAFP (`try: open() except (FileNotFoundError, PermissionError, IsADirectoryError)`) and returns structured 4xx JSON. Tree-walk silently skips entries that disappear mid-walk. Torn reads (Claude Code's truncate-then-write) are accepted as a known UX wrinkle: user refreshes if a stale read produces obviously-broken content.

**Q:** Bind address?
- A *(judgment call â€” chose "127.0.0.1 only")*: default Uvicorn bind is `127.0.0.1`, NOT `0.0.0.0`. README states this explicitly. No CORS configuration (single-origin); explicitly DO NOT enable `allow_origins=["*"]`.

**Q:** Verb whitelist?
- A *(judgment call â€” chose "GET, PUT, POST only")*: only `GET`, `PUT`, `POST` route handlers under `/api/`. PATCH/DELETE/upload return 405. The PUT and POST endpoints are sanctioned by FR-14a/c; no others.

## Team consensus

The interviewer team (one sub-interviewer per probe category, dynamically built by the manager) reached consensus after one autonomous round:

- All seven categories returned `{"clear": true, "judgment-calls-recorded": true}`.
- Every load-bearing decision is bound to a specific FR or NFR slice in the spec stage's output.
- Open items recorded as `## Open questions` in this file (none survived the autonomous pass â€” all defaults are explicit).

The interview manager declared the requirement crystal-clear for spec compilation. The user is invited to revise any judgment call on a subsequent interactive interview run.

<!-- editor round-trip test marker -->
