# Specification — spec_driven

Run: spec_driven-20260503-145859 (autonomous full-pipeline regen, stage 4 parent-direct from `user_input/revised_prompt.md` + `interview/qa.md` + `findings/dossier.md`)

## Goal

Build `spec_driven`, an interactive viewer/editor SPA for the artifacts produced by the spec-driven workflow (`specs/{task_type}/{task_name}/`) plus the cross-cutting context the workflow reads (`CLAUDE.md`, `.claude/skills/**/*.md`, `.claude/agent_refs/**/*.md`). The webapp lets the user browse, edit, pin atomic items, and emit copy-paste regeneration prompts that drive any subset of the six stages back through Claude Code, in either INTERACTIVE or AUTONOMOUS mode.

## Out of scope (v1)

- Authentication, multi-user access, deployment beyond `localhost`.
- Live event-feed of pipeline runs / file watchers / auto-refresh.
- Search across artifacts.
- Running Claude inline from the webapp (regen prompts are still copy-paste into Claude Code CLI).
- Diff / version history beyond what `git` already provides.
- IPv6 (`[::1]`) — uvicorn binds IPv4-only.
- Cross-port LAN binding (`0.0.0.0`).
- A user-toggleable theme picker (light-only per `agent_refs/project/development.md`).
- Server-side persistence of UI preferences (autonomous toggle is per-tab in `localStorage`; soft-wrap toggle is per-render).

## User roles & primary flows

Single role: **the spec author** (the user running Claude Code locally on the same machine). Primary flows:

1. **Browse:** open the SPA at `http://127.0.0.1:8765/` (single-process) or `http://127.0.0.1:5173/` (Vite dev), navigate the recursive sidebar, click a file, see it render in the main pane.
2. **Edit a whole file:** click ✎ Edit in the toolbar, modify the textarea, Save (Ctrl+S) or Discard.
3. **Edit a Q/A pair in `interview/qa.md`:** click the ✎ on a single Q or A block (color-differentiated), edit in place, Save.
4. **Pin / unpin atomic items:** click 📌 next to a Q/A pair, an FR/NFR/AC block, or a recommendation bullet to add it to `<stage>/promoted.md`. Pins survive future regeneration.
5. **Build a regen prompt for one stage:** open the per-stage Regenerate `<details>` panel, select modules, toggle autonomous mode, click "Build prompt", copy the assembled prompt from the inline visible bordered block.
6. **Build a regen prompt for the whole project:** open `/project/{type}/{name}`, select stages and modules, click "Build prompt", copy.

## Functional requirements

### Backend — read path

**FR-1.** FastAPI backend at `127.0.0.1:8765` (IPv4 loopback only — never `0.0.0.0`). Single-process mode also serves the SPA bundle from `backend/static/`.

**FR-2.** `EXPOSED_TREE` definition (the union of paths the backend will serve and let the SPA edit):
- `CLAUDE.md` (root file).
- `.claude/skills/**/SKILL.md` and `.claude/skills/agent_team/playbooks/*.md` (skill defs + stage playbooks).
- `.claude/agent_refs/**/*.md` (recursive — picks up `interview/`, `research/`, `validation/`, `project/`, and any future subfolder).
- `specs/**` and `projects/**` (under repo root).

**FR-3.** `GET /api/tree` returns a recursive JSON shape `{type: "section", name, path, children: [...]}`. Every non-leaf has a `children: []` field; leaves have `type: "file"` and no `children`. Top-level sections: "Claude Settings & Shared Context" and "Specs". *(Lesson from run `spec_driven-20260502-clean` consumer-walk: uniform `children` field, never `task_type.projects` / `project.stages`.)*

**FR-4.** `GET /api/file?path=<rel>` returns `{path, content, mtime, bytes}` for a file inside `EXPOSED_TREE`. Allowed extensions: `.md`, `.json`, `.yaml`, `.yml`, `.jsonl`, `.txt`, `.png`, `.jpg`. Disallowed extensions return **415**. Files >1 MB return **413**. Path outside `EXPOSED_TREE` returns **404** (single status — no enumeration side-channel).

**FR-5.** Every successful `GET /api/file` carries headers `X-Content-Type-Options: nosniff` and `Content-Disposition: attachment` (defense-in-depth against content-sniffing exploits per OWASP).

**FR-6.** `GET /api/stages?project_type=&project_name=` returns the canonical six-stage definition with each stage's `{id, label, folder, invocation, modules: [{id, label, relative_path, description}]}`. Hard-coded server-side from a single source of truth.

### Backend — write path

**FR-7.** `PUT /api/file` accepts `{path, content}` for a file inside `EXPOSED_TREE`. Same path-sandbox + extension allowlist + 1 MB body cap as the reader. Atomic write via temp file + `os.replace`. Returns `{bytes, mtime}` on success.

**FR-7b.** `PUT /api/file` honors `If-Unmodified-Since: <RFC7232-mtime>`. If the on-disk mtime is newer, returns **409** with `{detail: {kind: "stale_write", current_mtime}}` so the SPA can show a "file changed under you — reload?" banner. *(Dossier rec #3.)*

**FR-8.** `PUT /api/file` validates the body's first 16 bytes as plain text (no NUL bytes, valid UTF-8) for the text extensions. Image extensions (`.png`/`.jpg`) are NOT writable — `PUT` to an image path returns **415**. SVG is NOT in the allowlist (treated as code-execution vector).

**FR-9.** Every state-changing endpoint (`PUT /api/file`, `POST /api/regen-prompt`, `POST /api/promote`, `DELETE /api/promote`) validates `Origin` and `Host` headers. Allow-list at the bound port: `{http://127.0.0.1:<port>, http://localhost:<port>}` for `Origin` and `{127.0.0.1:<port>, localhost:<port>}` for `Host`. Anything else (missing, foreign, wrong port, IPv6) → **403** (CSRF / DNS-rebind defense). Loopback aliases admit because they resolve to the same socket.

**Dev-server proxy contract:** under `make run-frontend`, the Vite proxy MUST rewrite `Origin` to `http://127.0.0.1:8765` (and `changeOrigin: true` rewrites `Host` to the target) so the backend gate sees a same-shape request in both runtime modes. The backend allow-list is NOT widened to the dev-server port; the rewrite happens at the proxy boundary.

### Backend — regen prompt assembly

**FR-10.** `POST /api/regen-prompt` accepts `{project_type, project_name, stages: string[], modules: {stage_id: string[]}, autonomous: bool}` and returns `{prompt, warning, selected_stages_count, follow_ups_count, autonomous, bytes}`.

**FR-11.** The assembled prompt MUST:
- (a) Open with the literal first line `# EXECUTION MODE: AUTONOMOUS` or `# EXECUTION MODE: INTERACTIVE`. No header → INTERACTIVE.
- (b) Inline `revised_prompt.md` (or `raw_prompt.md` if no revised yet) verbatim.
- (c) List every `user_input/follow_ups/*.md` filename in numerical order, each with its full body inlined.
- (d) For each selected stage, include the stage's invocation hint + module list + any non-empty `<stage>/promoted.md` inlined verbatim under "Pinned items (MUST survive regeneration)".
- (e) Close with a `### Constraints` section restating the read-zero contract verbatim from `CLAUDE.md` + the audit-event protocol.

**FR-12.** Size policy: warn-don't-truncate. `bytes <= 50 KB` → `warning: null`. `50 KB < bytes < 1 MB` → `warning: {kind: "approaching_ceiling", bytes, soft_limit: 51200}`. `bytes >= 1 MB` → **413** with `{detail: {kind: "too_large"}}`. *(Dossier: convergent — never silently truncate.)*

### Backend — promotions / pinning

**FR-13.** `POST /api/promote` accepts `{project_type, project_name, stage_folder, source_file, item_id, item_text}` where `stage_folder ∈ {interview, findings, final_specs, validation}` (allowlist). Appends the pin to `specs/{type}/{name}/{stage_folder}/promoted.md`. Returns `{status, item_id}`. Stage 6 (project code) does NOT support promotion in v1 — different granularity story.

**FR-14.** `DELETE /api/promote` accepts `{project_type, project_name, stage_folder, item_id}` and removes the pin. Returns `{status, item_id}`. If the item doesn't exist, idempotent 200.

### Frontend — sidebar & navigation

**FR-15.** Recursive sidebar walks `node.children` uniformly (no `task_type.projects` / `project.stages` branches). Tree section names: "Claude Settings & Shared Context" + "Specs". The `Specs/{type}/{name}/` subtree shows per-stage subfolders (`user_input/`, `interview/`, `findings/`, `final_specs/`, `validation/`).

**FR-16.** Breadcrumb above the main pane (NOT inside the sidebar). Current crumb rendered as plain text with `aria-current="page"`. *(Convergent prior-art pattern.)*

**FR-17.** Deep-link / bookmarkable URL: `/file/<encoded path>` mounts the file in the main pane. Direct paste of any such URL renders the file with the sidebar collapsed-to-current.

**FR-18.** Keyboard navigation: `Ctrl/Cmd+Shift+E` focuses sidebar tree; arrows traverse; `Enter` opens. Floor-level VS Code parity.

### Frontend — reader (per render mode)

**FR-19.** `MarkdownView`: react-markdown + rehype-sanitize (default schema; raw HTML dropped) + rehype-highlight. Internal links (relative paths) resolve against the current file's directory; external `http(s)` opens in new tab; broken links render as muted spans (NOT `<a>`) with a `title` tooltip.

**FR-20.** `QaView`: discrete color-differentiated blocks for `interview/qa.md` — Round → category → Q/A pair. Q tinted blue, A tinted green, category badge in header. Per-Q and per-A ✎ inline edit pencil.

**FR-21.** `JsonlView`: each line parsed independently and rendered as a collapsible JSON object. Parse failures show the raw line + an inline parse-error badge.

**FR-22.** `CodeView`: `.json`, `.yaml`, `.yml` rendered in a monospace block with syntax highlighting. Dark fixed palette (intentional carve-out from the light-theme rule per `agent_refs/project/development.md`).

**FR-23.** `ImagePlaceholder`: `.png`/`.jpg` rendered as a placeholder card showing filename + size + "binary content not previewed."

**FR-24.** `ParseFallback`: every render component is wrapped in a real React Error Boundary class (`componentDidCatch` / `getDerivedStateFromError`, NOT `try { return <Foo/> } catch`). On render failure, fallback shows the raw text in a `<pre>` with a banner explaining the parse error. *(Dossier rec #4 — generalized from QaErrorBoundary.)*

### Frontend — editor

**FR-25.** ✎ Edit toggle in the file-pane toolbar switches view → editor. Editor is a textarea (full file content), not split-pane / WYSIWYG. *(Dossier: keep-it-simple for canonical-input artifacts.)*

**FR-26.** Save controls: Save (Ctrl+S) / Discard (revert to last-saved) / Close-editor (return to view; warns if dirty).

**FR-27.** Dirty indicator: filled dot `●` in toolbar AND `*` in `document.title`. `beforeunload` guard while dirty. *(Convergent — VS Code, GitHub web, MkDocs.)*

**FR-28.** Save-error banner: persistent inline banner above the textarea (NOT a toast — toasts mid-recovery are an anti-pattern). Re-Save retries; banner clears on success.

**FR-29.** Concurrency: editor sends `If-Unmodified-Since: <last-loaded-mtime>`. On 409, banner says "file changed externally — Reload?" with a Reload button that fetches the latest content (and discards in-memory edits).

**FR-30.** Per-Q/A inline edit (in `QaView`): clicking ✎ on a Q or A opens a small inline editor scoped to that block. Save persists back to the same `qa.md` via `PUT /api/file` (full-file write, not patch). Mutually exclusive with file-level Edit (the file-level toggle is disabled while a per-block edit is open).

### Frontend — regenerate panels

**FR-31.** Per-stage Regenerate `<details>` panel above any file under a stage subfolder. Default closed. Contents: module checkboxes (default all checked), autonomous-mode toggle, "Build prompt" button.

**FR-32.** Project parent route `/project/{type}/{name}` renders the stage map with a master Regenerate panel: stage selectors + per-stage module checkboxes + autonomous toggle + Build prompt. Single combined prompt walks chosen stages in order.

**FR-33.** Build prompt UI:
- (a) Section-breakdown summary line beside the "Build prompt" button: `{N} stages selected, {K} follow-ups inlined, autonomous={…}, {bytes} KB`.
- (b) On warning (50 KB < bytes < 1 MB): yellow banner above the prompt block.
- (c) On 413 (≥1 MB): build-error banner; prompt block NOT rendered.
- (d) On success: bordered `regen-prompt-block` rendered inline (NO inner `<details>`). Header bar: "Assembled prompt" title + "Wrap" toggle (default ON, per-render preference, NOT persisted) + prominent **Copy** button (label flips to "Copied!" for ~1.5s; `aria-live="polite"`; fixed min-width to prevent label-flip layout shift).
- (e) `<pre>` body: `font-size: 13px`, `line-height: 1.55`, `max-height: 520px`. Soft-wrap on by default; toggle off restores horizontal scroll.

**FR-34.** Autonomous-mode toggle persists in `localStorage` under `spec_driven.autonomous_mode.v1`. Default off (interactive). Same value drives per-stage and project-page panels via the native `storage` event.

### Frontend — pinning

**FR-35.** 📌 toggle next to each pinnable atomic item (Q/A pair, FR-NN / NFR-NN / AC-NN / SYS-NN block, recommendation bullet). Calls `POST /api/promote`; unpin calls `DELETE /api/promote`.

**FR-36.** Pinned items render with a small 📌 indicator in the artifact view; clicking shows the source pin file path.

### Cross-cutting

**FR-37.** Read-zero regeneration contract: regenerating any stage deletes that stage's prior outputs (per CLAUDE.md per-stage table) and reads ONLY the inputs (current stage's input artifacts + `CLAUDE.md` + shared `.claude/` + user-input layer + `<stage>/promoted.md`). Surgical preservation of prior text is forbidden during regen. The webapp's `regen_prompt.py` includes this contract verbatim in every assembled prompt's `### Constraints` section.

**FR-38.** Audit event protocol on every regen: emit `regen.delete.planned` (one per file) → `regen.delete.completed` (with count) → `regen.write.completed` (path + bytes) into `events.jsonl`.

**FR-39.** `Makefile` targets: `install` / `install-backend` / `install-frontend` / `run-backend` / `run-frontend` / `run-prod` / `run` (alias for `run-backend`) / `build-frontend` / `test-backend` / `test-frontend` / `e2e` / `boot-smoke` / `clean`. Every target binds `127.0.0.1` (NEVER `0.0.0.0`).

**FR-40.** Cross-cutting project-output rules from `.claude/agent_refs/project/development.md` apply: light-theme app chrome (no `prefers-color-scheme: dark` overrides), dark `<pre>` carve-outs allowed for code/regen-prompt blocks.

**FR-41.** AGENTS.md / Codex CLI precedent for the `# EXECUTION MODE` H1 directive: the convention is a parser-free Markdown directive (vs Cursor's YAML frontmatter or Junie's UI toggle) — appropriate for copy-paste prompts that have no parser. Document the rationale in `CLAUDE.md` § Regeneration prompts & autonomous mode.

## Non-functional requirements

- **NFR-1.** `GET /api/tree` returns within 250 ms for the canonical scale (50 projects × 200 files = 10 000 leaves).
- **NFR-2.** `GET /api/file` returns within 100 ms for files <500 KB.
- **NFR-3.** Initial app load (HTML + JS + first `/api/tree` + first `/api/file`) < 2 s on localhost.
- **NFR-4.** All Python in `backend/libs/` is strongly typed, OOP-modeled, with `@dataclass(frozen=True)` for immutable containers. `str | None`, never `Optional[str]`.
- **NFR-5.** `EXPOSED_TREE` is the only path-resolution surface. No file-read or file-write code path bypasses it.
- **NFR-6.** Mutation surface is exactly four endpoints (`PUT /api/file`, `POST /api/regen-prompt`, `POST /api/promote`, `DELETE /api/promote`). No DELETE on file, no upload, no create-new-file. `PATCH/DELETE` on `/api/file` → **405**.
- **NFR-7.** `Origin` and `Host` validation on every state-changing route. Foreign / missing / wrong-port → **403**.
- **NFR-8.** No raw HTML in markdown render path. `rehype-sanitize` default schema; raw HTML dropped.
- **NFR-9.** SVG NOT in extension allowlist (code-execution vector).
- **NFR-10.** Symlinks / Windows junctions refused outright (since `EXPOSED_TREE` is curated). 404, no realpath leak.
- **NFR-11.** Path traversal probes (`..`, percent-encoded, ADS, Windows reserved names, 8.3 short names, mixed slashes) all collapse to **single 404** (no existence oracle).
- **NFR-12.** **Vite CVE-2025-62522** (trailing-backslash bypass) explicitly defended: reject literal `\`, `:`, NUL byte before `realpath` resolution.
- **NFR-13.** Markdown XSS via raw `<script>` AND via event-handler / `javascript:` URIs — both stripped by sanitizer.
- **NFR-14.** Single-process mode (`make run-prod`) serves the SPA bundle from `backend/static/`. No second process required.
- **NFR-15.** Per-stage promoted.md is INPUT, not output. Read-zero regen preserves it.
- **NFR-16.** Light-theme app chrome per `agent_refs/project/development.md`. `:root { color-scheme: light; }` only; no `@media (prefers-color-scheme: dark)` on chrome. Dark `<pre>` palettes inside `.regen-prompt-block`, `.markdown-view pre`, `.code-view pre` are intentional carve-outs (validated WCAG AA).

## Acceptance criteria summary

29 ACs in `validation/acceptance_criteria.md`. Highlights:

- **AC-1..2:** GET /api/file happy path + traversal probes → single 404.
- **AC-3:** GET /api/tree returns recursive `children` shape; consumer-walk passes.
- **AC-4..6:** Render-mode dispatch (markdown, Q/A, code, image placeholder, parse-fallback).
- **AC-7:** Editor save round-trip (textarea → PUT → reload shows new content).
- **AC-8:** Per-Q inline edit round-trip; mutual exclusion with file-level edit.
- **AC-9:** Dirty indicator dot + title `*` + `beforeunload` guard while dirty.
- **AC-10:** PUT 1.5 MB body → 413 `{kind: "too_large"}`.
- **AC-11:** Origin/Host validation: foreign → 403; loopback aliases (`localhost` ↔ `127.0.0.1`) → 200; raw `localhost:5173` direct-to-backend → 403; proxied `make run-frontend` flow → 200.
- **AC-12:** PATCH/DELETE on `/api/file` → 405.
- **AC-13..15:** Stale-write conflict (PUT with stale `If-Unmodified-Since` → 409 + reload banner).
- **AC-16..18:** Regen-prompt assembly (interactive header, autonomous header, follow-ups inlined, pinned items inlined, read-zero contract present).
- **AC-19:** Regen-prompt size policy (50 KB warn, 1 MB → 413).
- **AC-20..21:** Build-prompt UI (inline visible block, header-bar Copy, soft-wrap toggle, breakdown line, warning banner).
- **AC-22..23:** Autonomous toggle persistence + cross-tab `storage` event sync.
- **AC-24..25:** Promotion roundtrip (POST then DELETE), parse-fallback Error Boundary on `qa.md` malformed input.
- **AC-26..27:** Sidebar structural sanity (≥N leaves under each top-level section), broken-link span (NOT `<a>`).
- **AC-28..29:** `make run-prod` boot smoke + `make run` localhost-only bind.

## Open questions

- **OQ-1.** Concurrency header: `If-Unmodified-Since` (RFC 7232 mtime) vs `If-Match` (sha-based ETag). Recommended: mtime in v1, ETag deferred.
- **OQ-2.** Per-block edit conflict policy in `QaView` when two Q-edits race. Recommended: last-write-wins per Q with a banner; defer better resolution to v2.
- **OQ-3.** Soft-wrap toggle persistence — explicitly off per follow-up 002, but users find reset jarring. Re-confirm in a future round.
- **OQ-4.** Refuse symlinks outright vs `realpath`-and-re-verify. Recommended: refuse outright (simpler, EXPOSED_TREE is curated).
- **OQ-5.** Dossier rec #1 (byte/line count chip near Copy button) — implement as a small `<span class="regen-size-chip">` or fold into the breakdown line? Recommended: fold into existing breakdown line.
- **OQ-6.** Stage-6 promotion granularity (per-file? per-symbol?) — deferred to v2.
- **OQ-7.** Theme picker — out of scope for v1; revisit if a sibling project needs the affordance.
- **OQ-8.** IPv6 (`[::1]`) bind — uvicorn IPv4-only in v1; revisit if dual-stack ever lands.
- **OQ-9.** Cross-port LAN bind (`0.0.0.0`) — explicitly out of scope; SEC-20 audit prevents accidental introduction.

(Pinned-item check: `final_specs/promoted.md` did not exist at run start; nothing to preserve verbatim.)
