# System tests — `spec_driven`

End-to-end and multi-component scenarios. Each `SYS-NN` boots one of the spec's runtime modes (`make run-prod` single-process, or `make run-frontend` Vite + backend), drives a real browser (Playwright) or shell harness against a real backend, and asserts on observable outcomes — rendered DOM, HTTP status, file contents on disk, and `events.jsonl` audit lines. Pure-shape unit tests live in `unit_tests.md`; this file owns the contracts that span layers.

Pre-reading consulted (recorded for the run's `events.jsonl` `validation.started` event):

- `C:/workspace/spec_coding/.claude/skills/agent_team/playbooks/validation.md`
- `C:/workspace/spec_coding/.claude/agent_refs/validation/general.md`
- `C:/workspace/spec_coding/.claude/agent_refs/validation/development.md`

Per `agent_refs/validation/development.md` move 1, **mode count = e2e profile count**: the spec advertises `make run-prod` (single-process at 8765) AND `make run-frontend` (Vite at 5173 proxying to 8765). Both modes are first-class targets in this file. SYS-16b in particular pins down the proxy contract per move 11 (header-mutating-layer middleware tests cover both shapes).

Per `agent_refs/validation/development.md` move 8, every UI render mode has its own e2e scenario opening a real triggering file — SYS-2..SYS-6 cover MarkdownView, QaView, JsonlView, CodeView, and ImagePlaceholder, with SYS-13 covering the ParseFallback Error Boundary path (move 9).

## Notation

- **Setup** — preconditions: runtime mode, fixtures on disk, browser / harness state.
- **Action** — what the test does (page navigation, button click, HTTP call).
- **Assertions** — what must be observably true on success.
- **Spec refs** — FR / NFR / AC citations from `final_specs/spec.md` + `validation/acceptance_criteria.md`.
- **Components exercised** — backend module(s) and frontend component(s) the scenario touches.
- **Severity on failure** — per `agent_refs/validation/general.md` severity policy, with development.md escalations applied.

`PORT_BACKEND = 8765`, `PORT_FRONTEND = 5173` throughout. All scenarios assert `consoleErrors == []` (no uncaught browser-side exceptions during the run) unless a SYS explicitly tolerates a known parse error (SYS-13).

---

### SYS-1 — Boot smoke under `make run-prod`

**Setup.**
- Fresh checkout, `make install` complete (backend deps in `.venv`, frontend bundle built into `projects/spec_driven/backend/static/`).
- No prior `uvicorn` listener on `127.0.0.1:8765`.
- Canonical fixture tree: at least one project under `specs/development/`, one under `projects/`, plus `CLAUDE.md` and `.claude/skills/agent_team/SKILL.md` populated.

**Action.**
1. Run `make run-prod` in a background process; wait up to 5 s for the listener.
2. `GET http://127.0.0.1:8765/` — expect HTTP 200, `Content-Type: text/html`, body contains `id="root"`.
3. `GET http://127.0.0.1:8765/api/tree` — expect HTTP 200, JSON body parses.
4. Open `http://127.0.0.1:8765/` in Playwright Chromium, wait for `[data-testid="sidebar"]` to be visible.
5. Expand both top-level sections in the sidebar.

**Assertions.**
- `make run-prod` exits with code 0 from the launcher's foreground process when sent SIGTERM after the test (no spurious `KeyError` / `ImportError` at boot — boot-time exception in any service is `critical` per development.md).
- `/api/tree` JSON has top-level shape `{type: "section", name, path, children: [...]}` with exactly two top-level sections named "Claude Settings & Shared Context" and "Projects".
- Each top-level section has at least one descendant `type: "file"` leaf (structural sanity assertion per development.md move 1).
- Sidebar DOM in Playwright shows ≥1 leaf `<button>` under EACH top-level section (no empty-tree drift — the failure mode that hit `spec_driven-20260502-clean`).
- No `Error` / `Failed to fetch` console messages during initial render.

**Spec refs.** FR-1, FR-2, FR-3, FR-15, NFR-3, NFR-14, AC-3, AC-26, AC-28.

**Components exercised.** `backend/main.py` launcher, `backend/libs/api_files.py` (tree), `backend/libs/safe_resolve.py`, `backend/static/index.html`, `frontend/src/components/Sidebar.tsx`, `frontend/src/components/App.tsx`.

**Severity on failure.** `critical` (boot-smoke failure in any service per development.md move 4).

---

### SYS-2 — MarkdownView deep-link (default render)

**Setup.**
- `make run-prod` running. Fixture file: `specs/development/spec_driven/final_specs/spec.md` (canonical, ≥10 KB markdown with headings, code fences, internal cross-file links, and one external https link).
- Cold browser context (no localStorage seeded).

**Action.**
1. Open Playwright at `http://127.0.0.1:8765/file/specs%2Fdevelopment%2Fspec_driven%2Ffinal_specs%2Fspec.md` directly (deep-link, no prior navigation).
2. Wait for `[data-render-mode="markdown"]` to be visible.
3. Click an internal relative link (e.g., `[acceptance criteria](../validation/acceptance_criteria.md)`).
4. Use browser back navigation, then click an external `https://` link.

**Assertions.**
- `<main>` contains rendered HTML (≥3 `<h1>`/`<h2>` elements, ≥1 `<pre><code>` fence, syntax highlighting class on at least one code block).
- Internal-link click navigates the SPA to `/file/specs/development/spec_driven/validation/acceptance_criteria.md` and renders the target file (no full page reload — `window.history` length increments by 1).
- External `https://` link has `target="_blank"` and `rel="noopener"` attributes; click opens a new browser context page.
- A deliberately broken internal link (e.g., `./does-not-exist.md`) renders as `<span class="broken-link" title="...">` — NOT `<a>` (per FR-19, AC-27).
- Sidebar collapsed-to-current after deep-link load (the path's ancestor chain is expanded; siblings outside the chain are collapsed) per FR-17.
- Breadcrumb above main pane shows current crumb as `<span aria-current="page">` (NOT a link) — FR-16.
- No raw `<script>` element survives in the rendered tree (rehype-sanitize default schema; NFR-8, NFR-13).

**Spec refs.** FR-17, FR-19, FR-16, NFR-8, NFR-13, AC-4, AC-27.

**Components exercised.** `backend/libs/api_files.py` (file read + sandbox), `frontend/src/components/MarkdownView.tsx`, `frontend/src/components/Breadcrumb.tsx`, `frontend/src/components/Sidebar.tsx` (collapse-to-current logic), react-markdown + rehype-sanitize + rehype-highlight.

**Severity on failure.** `blocker` (missing-e2e-for-render-mode would be `blocker` per development.md move 8; deep-link blank page would be `critical`).

---

### SYS-3 — QaView render mode (interview/qa.md)

**Setup.**
- `make run-prod` running.
- Fixture: a canonical `interview/qa.md` from a recent autonomous-mode run (NOT a hand-written fixture — per development.md move 10, parser regexes must be tested against real upstream output). Includes both legacy `- A: ...` and autonomous-mode `- A *(judgment call ...)*: ...` answer forms across at least 2 rounds, 3 categories, 6 Q/A pairs.

**Action.**
1. Playwright deep-link to `/file/specs/development/spec_driven/interview/qa.md`.
2. Wait for `[data-render-mode="qa"]`.
3. Inspect the rendered Q/A blocks.

**Assertions.**
- Render mode is `qa` (NOT `markdown` — file path triggers QaView).
- Page shows ≥2 Round headers, ≥3 distinct category badges in block headers.
- Each Q/A pair: question rendered with class `qa-question` (blue tint per FR-20), answer rendered with class `qa-answer` (green tint).
- BOTH the legacy `- A:` form AND the autonomous-mode `- A *(judgment call ...)*:` form parse into a green answer block (no fall-through to MarkdownView; no blank rendering).
- Per-Q and per-A pencil controls (`[data-action="edit-q"]`, `[data-action="edit-a"]`) are present and focusable.
- A 📌 pin button is present next to each Q/A pair (FR-35).
- `consoleErrors == []` and the document does NOT contain the ParseFallback `<pre>` banner.

**Spec refs.** FR-20, FR-35, AC-4, AC-25.

**Components exercised.** `frontend/src/components/QaView.tsx`, `frontend/src/components/QaErrorBoundary.tsx`, `frontend/src/lib/parseQa.ts`.

**Severity on failure.** `critical` if deep-link renders blank (per development.md "latent render error on deep-link" row); `blocker` if Q/A blocks render but autonomous-form answers fall through.

---

### SYS-4 — JsonlView render mode

**Setup.**
- `make run-prod` running.
- Fixture: `.audit/adhoc_agents/2026-05-03/spec_driven-20260503-145859/events.jsonl` exists with ≥10 lines, including (a) well-formed JSON objects of varying depth and (b) at least one deliberately malformed line (e.g., trailing comma) appended by the test fixture.
- File is in `EXPOSED_TREE` because `.audit/` is NOT — verify the path-sandbox refuses it. Use a JSONL fixture at an EXPOSED path instead: `specs/development/spec_driven/findings/sample_events.jsonl` (created by the test setup; deleted on teardown).

**Action.**
1. Playwright deep-link to `/file/specs/development/spec_driven/findings/sample_events.jsonl`.
2. Wait for `[data-render-mode="jsonl"]`.
3. Click the disclosure triangle on at least one line to expand the JSON object.
4. Locate the malformed line.

**Assertions.**
- Each well-formed line renders as a collapsible JSON object (`<details>` with class `jsonl-line`).
- Expanded form shows nested key/value structure (not raw text) for at least one line.
- The malformed line renders as `<div class="jsonl-line jsonl-parse-error">` containing the raw text AND an inline parse-error badge (`[data-testid="jsonl-parse-error-badge"]`) — per FR-21.
- The render does NOT trip the file-level Error Boundary (per-line failure is contained — FR-21 says "each line parsed independently").
- Default extension allowlist includes `.jsonl` (FR-4).

**Spec refs.** FR-4, FR-21, FR-24.

**Components exercised.** `frontend/src/components/JsonlView.tsx`, per-line collapsible renderer.

**Severity on failure.** `blocker` (missing-e2e-for-render-mode per development.md move 8).

---

### SYS-5 — CodeView render mode

**Setup.**
- `make run-prod` running.
- Fixture: `.claude/settings.json` (a real file in EXPOSED_TREE? — check. `.claude/settings.json` is NOT under `.claude/skills/**` or `.claude/agent_refs/**`; per FR-2 it is NOT in EXPOSED_TREE). Use a JSON file that IS exposed: e.g., `projects/spec_driven/backend/package.json` if one exists, otherwise `package.json`-style fixture under `projects/spec_driven/frontend/`.

**Action.**
1. Playwright deep-link to a `.json` file inside `projects/spec_driven/`.
2. Wait for `[data-render-mode="code"]`.
3. Repeat for a `.yaml` file under the same project (e.g., `projects/spec_driven/frontend/playwright.config.yaml` if present, or a fixture).

**Assertions.**
- Both `.json` and `.yaml` files render under `<pre class="code-view ...">` with a syntax-highlighting class (e.g., `hljs-string`, `hljs-keyword`).
- Background palette is the dark fixed palette per FR-22 (intentional carve-out from the light-theme rule per NFR-16).
- File-level pencil ✎ Edit toggle is present (FR-25).
- Pin 📌 controls are NOT shown for individual lines in code mode (pinning targets atomic items in stages 2–5 only — FR-13's `stage_folder` allowlist).

**Spec refs.** FR-22, FR-25, NFR-16, AC-4.

**Components exercised.** `frontend/src/components/CodeView.tsx`, syntax-highlight bundle.

**Severity on failure.** `blocker` (move 8).

---

### SYS-6 — ImagePlaceholder render mode

**Setup.**
- `make run-prod` running.
- Fixture: `specs/development/spec_driven/findings/sample.png` (valid 1×1 PNG, ≤10 KB), and `specs/development/spec_driven/findings/sample.jpg` (valid 1×1 JPEG).

**Action.**
1. Playwright deep-link to the `.png` fixture.
2. Wait for `[data-render-mode="image"]`.
3. Repeat for the `.jpg` fixture.
4. Attempt to enter edit mode by clicking ✎ Edit.

**Assertions.**
- Each image file renders as a placeholder card (`[data-testid="image-placeholder"]`) showing filename + byte-size + the literal text "binary content not previewed" per FR-23.
- The `<img>` element is NOT rendered (the placeholder is the contract; we do not stream binary bytes through an `<img src="...">`).
- ✎ Edit button is either hidden OR disabled with a tooltip explaining "image files are read-only" — per FR-8 (`PUT` to image path returns 415).
- Direct `PUT /api/file?path=...sample.png` from a fetch in the browser console returns **415**.

**Spec refs.** FR-4, FR-8, FR-23, AC-4.

**Components exercised.** `frontend/src/components/ImagePlaceholder.tsx`, `backend/libs/api_files.py` (415 path).

**Severity on failure.** `blocker` (move 8).

---

### SYS-7 — Editor save round-trip (file-level)

**Setup.**
- `make run-prod` running.
- Fixture: `specs/development/spec_driven/findings/dossier.md` (≥1 KB markdown). Record its `mtime` and SHA-256 before the test.

**Action.**
1. Playwright deep-link to `/file/specs/development/spec_driven/findings/dossier.md`.
2. Click ✎ Edit.
3. Append the literal line `\n<!-- sys-7 round-trip marker -->` to the textarea.
4. Verify dirty indicator: filled `●` in toolbar AND `*` prefix in `document.title`.
5. Press Ctrl+S.
6. After the save banner clears, click "Close editor".
7. Reload the page (`Ctrl+R`).
8. Inspect the rendered markdown.

**Assertions.**
- Dirty indicator appears within 100 ms of the first textarea keystroke (FR-27).
- A `beforeunload` guard fires if the test triggers `window.close()` while dirty (FR-27).
- Save sends `PUT /api/file` with `If-Unmodified-Since: <mtime captured at load>` (FR-29) — captured by Playwright's `request` event listener.
- Save returns 200 with body `{bytes, mtime}` and the on-disk SHA-256 of `dossier.md` matches the new content.
- After reload, the rendered markdown contains the marker line; the dirty indicator is gone.
- The on-disk write was atomic (file never appears as zero bytes between read attempts during save — checked by a 50 ms polling loop in a parallel thread; tolerate-of-temp-file-existing).

**Spec refs.** FR-7, FR-7b, FR-25, FR-26, FR-27, FR-29, AC-7, AC-9.

**Components exercised.** `backend/libs/api_files.py` (PUT path, atomic temp-file + `os.replace`), `frontend/src/components/Editor.tsx`, `frontend/src/components/EditorToolbar.tsx`.

**Severity on failure.** `blocker` (acceptance criterion failure).

---

### SYS-8 — Per-Q inline edit + mutual exclusion with file-level edit

**Setup.**
- `make run-prod` running.
- Fixture: `specs/development/spec_driven/interview/qa.md` (real autonomous-mode output as in SYS-3).

**Action.**
1. Playwright deep-link to `/file/specs/development/spec_driven/interview/qa.md`.
2. Locate Q-1 of Round 1; click its `[data-action="edit-q"]` pencil.
3. Verify the file-level ✎ Edit button in the toolbar is now disabled (FR-30 mutual exclusion).
4. Modify the question text in the inline editor; click Save.
5. Wait for the inline editor to close; verify the rendered Q now shows the new text.
6. Reload the page.
7. Verify the rendered Q still shows the new text (disk persisted).
8. Repeat with the per-A inline edit on Q-1's A.

**Assertions.**
- File-level ✎ is `disabled` (DOM `disabled` attr or `aria-disabled="true"`) while a per-Q editor is open.
- Save sends a single `PUT /api/file` with the FULL file content (not a patch) per FR-30.
- After save, `qa.md` on disk contains the modified Q text and is otherwise byte-identical to the pre-test version (other Q/A pairs unchanged).
- Re-mounting the page re-parses `qa.md` and shows the modification (no stale cache; deep-link survives reload).
- After all per-block editors close, the file-level ✎ is enabled again.

**Spec refs.** FR-7, FR-20, FR-30, AC-8.

**Components exercised.** `frontend/src/components/QaView.tsx` (per-block editor state), `frontend/src/components/EditorToolbar.tsx` (mutual-exclusion gate), `backend/libs/api_files.py` (PUT).

**Severity on failure.** `blocker`.

---

### SYS-9 — Regen-prompt assembly (small, no warning)

**Setup.**
- `make run-prod` running.
- Fixture project: `specs/development/spec_driven/` (the project that owns this validation file). `revised_prompt.md` ≈ 8 KB; one follow-up file ≈ 2 KB; no `<stage>/promoted.md`. Total assembled bytes expected to land below 50 KB.

**Action.**
1. Playwright opens `/project/development/spec_driven`.
2. Select stages "interview" + "research"; default modules (all checked); autonomous toggle OFF.
3. Click "Build prompt".

**Assertions.**
- Frontend issues `POST /api/regen-prompt` with body `{project_type: "development", project_name: "spec_driven", stages: ["interview", "research"], modules: {...}, autonomous: false}`.
- Response: `200 OK` with `{prompt, warning: null, selected_stages_count: 2, follow_ups_count: 1, autonomous: false, bytes: <number>}`.
- Breakdown line beside Build button reads: `2 stages selected, 1 follow-ups inlined, autonomous=off, <K> KB` (FR-33a).
- Inline `<div class="regen-prompt-block">` appears (NOT inside an inner `<details>`) with header bar containing "Assembled prompt" title, "Wrap" toggle (default ON), and a prominent **Copy** button. (FR-33d.)
- The prompt body's first line is exactly `# EXECUTION MODE: INTERACTIVE` (FR-11a).
- The prompt body inlines the full `revised_prompt.md` verbatim AND lists the follow-up filename in numerical order with its full body inlined (FR-11b, FR-11c).
- The prompt body ends with a `### Constraints` section containing the read-zero contract verbatim from `CLAUDE.md` (FR-11e, FR-37).
- Clicking the Copy button: label flips to "Copied!" for ~1.5 s with `aria-live="polite"`; the clipboard contains the assembled prompt text exactly (Playwright `context.grantPermissions(['clipboard-read'])`); the button has a fixed `min-width` so the label flip does NOT shift the surrounding layout (measured via `getBoundingClientRect` on the toolbar).
- No yellow warning banner is rendered (`bytes < 50 KB`).

**Spec refs.** FR-10, FR-11, FR-12, FR-32, FR-33, FR-37, FR-41, AC-16, AC-18, AC-20.

**Components exercised.** `backend/libs/regen_prompt.py`, `frontend/src/components/RegenPanel.tsx`, `frontend/src/components/RegenPromptBlock.tsx`, `frontend/src/components/CopyButton.tsx`.

**Severity on failure.** `blocker`.

---

### SYS-10 — Regen-prompt approaching-ceiling warning

**Setup.**
- `make run-prod` running.
- Synthetic fixture: temporarily extend the project's `revised_prompt.md` (or a follow-up) with filler text so the assembled prompt for "all stages" lands in the **50 KB < bytes < 1 MB** band. Tear-down restores the original file.

**Action.**
1. Playwright opens `/project/development/spec_driven`.
2. Select all stages + all modules + autonomous OFF.
3. Click "Build prompt".

**Assertions.**
- Response: `200 OK` with `warning: {kind: "approaching_ceiling", bytes: <N>, soft_limit: 51200}` (FR-12).
- A yellow banner is rendered above the prompt block with text along the lines of "Approaching size ceiling — currently {N} KB; max is 1024 KB" (FR-33b).
- The bordered `regen-prompt-block` IS still rendered (warn-don't-truncate per dossier rec convergent finding).
- Breakdown line shows updated byte count.
- Copy still works.

**Spec refs.** FR-12, FR-33b, AC-19.

**Components exercised.** `backend/libs/regen_prompt.py` (size policy), `frontend/src/components/RegenPanel.tsx` (banner rendering).

**Severity on failure.** `blocker`.

---

### SYS-11 — Regen-prompt 413 hard ceiling

**Setup.**
- `make run-prod` running.
- Synthetic fixture: pad `revised_prompt.md` to push assembled bytes ≥ 1 MB. Restore on teardown.

**Action.**
1. Playwright opens `/project/development/spec_driven`, select all stages + modules.
2. Click "Build prompt".

**Assertions.**
- Response: HTTP `413` with body `{detail: {kind: "too_large"}}` (FR-12).
- A red build-error banner is rendered with text indicating the prompt exceeded the 1 MB ceiling (FR-33c).
- The bordered `regen-prompt-block` is **NOT** rendered (FR-33c — "prompt block NOT rendered").
- The Copy button is NOT present (no prompt to copy).
- The breakdown line either reads "build failed" or shows the byte count with the error variant.

**Spec refs.** FR-12, FR-33c, AC-19.

**Components exercised.** `backend/libs/regen_prompt.py` (413 path), `frontend/src/components/RegenPanel.tsx` (error banner).

**Severity on failure.** `blocker`.

---

### SYS-12 — Autonomous toggle persistence + cross-tab `storage` event

**Setup.**
- `make run-prod` running.
- Two Playwright pages in the same browser context (shared origin → shared localStorage), both pointed at `/project/development/spec_driven`.
- localStorage cleared before the test.

**Action.**
1. Page A: load the project page; assert autonomous toggle is OFF (default per FR-34).
2. Page A: click the autonomous toggle to ON.
3. Page B (already loaded BEFORE step 2): observe the toggle.
4. Page A: navigate to a per-stage Regenerate panel (e.g., open `/file/specs/development/spec_driven/findings/dossier.md` and expand the Regenerate `<details>`).
5. Page A: build a prompt.
6. Reload Page A entirely.

**Assertions.**
- Page A's localStorage now contains key `spec_driven.autonomous_mode.v1` with value `"true"` after step 2 (FR-34).
- Page B's autonomous toggle flips to ON within 250 ms of step 2 — via the native `storage` event (FR-34, AC-23). Verify Page B's component subscribed to `window.addEventListener('storage', ...)` (Playwright `evaluate` to inspect listener count is fragile; instead assert on observable DOM: the toggle's `aria-checked` flips).
- Page A's per-stage Regenerate panel ALSO shows autonomous = ON (the same value drives both per-stage and project-page panels per FR-34).
- The assembled prompt's first line is `# EXECUTION MODE: AUTONOMOUS` (FR-11a, AC-22).
- After reload, the toggle is still ON (persistence survives reload).

**Spec refs.** FR-11, FR-34, AC-22, AC-23.

**Components exercised.** `frontend/src/components/AutonomousToggle.tsx`, `frontend/src/lib/autonomousStore.ts`, `backend/libs/regen_prompt.py` (header selection).

**Severity on failure.** `blocker`.

---

### SYS-13 — QaView Error Boundary fallback (real-shape malformed input)

**Setup.**
- `make run-prod` running.
- Fixture: a deliberately-malformed `qa.md` placed at a real path under `specs/development/spec_driven/interview/` (e.g., temporarily replace the canonical `qa.md` with one whose Round headers, category badges, or Q/A delimiters violate the parser regex in plausible ways: missing Round number, unclosed `*(judgment call ...)*` parenthetical, mixed indentation). Original restored on teardown.

**Action.**
1. Playwright deep-link to `/file/specs/development/spec_driven/interview/qa.md`.
2. Wait for either `[data-render-mode="qa"]` or `[data-testid="parse-fallback"]`.

**Assertions.**
- The page does NOT render blank (the failure mode that hit `spec_driven-20260502-clean` and prompted move 9).
- The page does NOT crash the SPA (the test continues navigating other paths after).
- The ParseFallback Error Boundary catches the render error: `[data-testid="parse-fallback"]` is present, containing
  - a banner explaining "QaView failed to parse this file" with the parse error message,
  - a `<pre>` showing the raw text of `qa.md` so the user can still see and edit it.
- The Error Boundary is a real React class component (not a `try { return <QaView /> } catch`) — verified by injecting a known throw inside the `<QaView>` render path during a separate harness test, with Sentry-style stack capture.
- The file-level ✎ Edit button is still operable (the user can fix the file from the fallback view).
- A Playwright `page.on('pageerror')` listener captures the error event but no second uncaught error fires (boundary contained it).

**Spec refs.** FR-20, FR-24, NFR-3, AC-4, AC-25 (and development.md move 9 — error boundaries wrap parse-then-render).

**Components exercised.** `frontend/src/components/QaErrorBoundary.tsx`, `frontend/src/components/ParseFallback.tsx`, `frontend/src/components/QaView.tsx`.

**Severity on failure.** `blocker` (the bug class that originated move 9).

---

### SYS-14 — Path traversal probes collapse to single 404 (no existence oracle)

**Setup.**
- `make run-prod` running.
- Fixtures on disk: a real file inside EXPOSED_TREE (`specs/development/spec_driven/findings/dossier.md`); an existence-oracle target outside EXPOSED_TREE (e.g., a file under `tools/`, `secrets/`, or any cousin folder that exists but is not exposed); a non-existent path with the same shape.

**Action.**
For each probe in the list below, issue an HTTP `GET /api/file?path=<probe>` from the test harness and record the status + body shape:

1. `../../etc/passwd`
2. `..%2f..%2f.claude%2fsettings.local.json` (URL-encoded)
3. `specs/development/spec_driven/findings/dossier.md::$DATA` (NTFS Alternate Data Stream)
4. `specs/development/spec_driven/findings/COM1` (Windows reserved name)
5. `specs/development/spec_driven/findings/dossier.md\foo` (literal backslash — Vite CVE-2025-62522 trailing-backslash bypass; NFR-12)
6. `specs/development/spec_driven/findings/dossier.md\x00.txt` (NUL byte; NFR-12)
7. `SPECS~1\\DEVELO~1\\dossier.md` (8.3 short name)
8. `specs/development/spec_driven/findings//dossier.md` (mixed double slashes)
9. A path that exists outside EXPOSED_TREE — e.g., `tools/foo.py` (verify it really exists on disk).
10. A path that does not exist — e.g., `tools/does-not-exist.py`.

**Assertions.**
- Every probe (1)–(10) returns **single status 404** with **byte-identical** response body (no enumeration side-channel — NFR-11).
- Probes (5) and (6) (literal backslash, NUL) are rejected BEFORE `realpath` resolution (NFR-12 — Vite CVE-2025-62522 explicit defense). Verified by latency parity: the rejection latency is comparable to the not-found 404, NOT inflated by an `os.realpath` round-trip.
- No symlink / junction is followed: a fixture symlink under `specs/` (created via `mklink` on Windows in dev mode, or `os.symlink` if available; otherwise `pytest.skip` per move 5) targeting a file outside EXPOSED_TREE returns 404 (NFR-10).
- No `realpath` of any probe leaks in the 404 body (no path strings, no absolute filesystem hints).
- All 404 bodies are JSON of the form `{detail: "not_found"}` (or equivalent constant).

**Spec refs.** NFR-5, NFR-10, NFR-11, NFR-12, AC-1, AC-2.

**Components exercised.** `backend/libs/safe_resolve.py`, `backend/libs/api_files.py`.

**Severity on failure.** `critical` (path traversal / sandbox escape per general.md severity policy).

---

### SYS-15 — Symlink / junction refusal (Windows + POSIX)

**Setup.**
- `make run-prod` running.
- On Windows with Developer Mode ON or admin: create a junction `specs/development/spec_driven/findings/junction-out` → `C:\Windows\System32`. On POSIX: create a symlink `specs/development/spec_driven/findings/symlink-out` → `/etc`. (Test parity-skipped via `pytest.mark.skipif` if neither is creatable in the runner — per development.md move 5.)
- Fixture restored on teardown via `os.unlink` / `rmdir`.

**Action.**
1. `GET /api/file?path=specs/development/spec_driven/findings/junction-out/win.ini` (Windows).
2. `GET /api/file?path=specs/development/spec_driven/findings/symlink-out/passwd` (POSIX).
3. `GET /api/file?path=specs/development/spec_driven/findings/junction-out` (the junction itself, not a child).

**Assertions.**
- All three return single **404** with no realpath leak (NFR-10, NFR-11).
- The junction / symlink itself is recognized via `os.lstat` + `S_ISLNK` (or Windows reparse-point detection) and rejected outright BEFORE traversal — not "resolved and then denied because outside tree". Validate by inspecting the backend log for a `safe_resolve.refused_link` entry (or whatever the chosen log line is; the contract is "refused at the link, not at the resolved target").
- Tree listing (`GET /api/tree`) does NOT enumerate the junction / symlink as a child of `findings/` (the link is excluded from the tree — NFR-10).

**Spec refs.** NFR-10, NFR-11, AC-2.

**Components exercised.** `backend/libs/safe_resolve.py`, `backend/libs/api_files.py` (tree walker).

**Severity on failure.** `critical`.

---

### SYS-16 — Origin / Host validation on state-changing routes (`make run-prod` mode)

**Setup.**
- `make run-prod` running on `127.0.0.1:8765`.
- A test harness that issues raw HTTP requests with controlled headers (Python `httpx` — bypasses browser same-origin protections).

**Action.** For each row in the table below, issue a `PUT /api/file?path=specs/development/spec_driven/findings/dossier.md` with body `{path, content: "x"}` and record the status:

| # | `Origin` header | `Host` header | Expected status |
|---|---|---|---|
| a | `http://127.0.0.1:8765` | `127.0.0.1:8765` | **200** |
| b | `http://localhost:8765` | `localhost:8765` | **200** (loopback alias admits — same socket) |
| c | `http://127.0.0.1:8765` | `localhost:8765` | **200** (Origin and Host independently match the allow-list) |
| d | `http://example.com` | `127.0.0.1:8765` | **403** (foreign Origin) |
| e | (none — header omitted) | `127.0.0.1:8765` | **403** (missing Origin) |
| f | `http://127.0.0.1:5173` | `127.0.0.1:8765` | **403** (raw dev-server Origin direct-to-backend — wrong port) |
| g | `http://localhost:5173` | `localhost:8765` | **403** (raw dev-server Origin direct-to-backend — wrong port) |
| h | `http://[::1]:8765` | `[::1]:8765` | **403** (IPv6 not in allow-list per OQ-8 / FR-9) |
| i | `http://127.0.0.1:8765` | `attacker.example.com` | **403** (DNS-rebind probe — Host header outside allow-list) |
| j | `http://127.0.0.1.nip.io` | `127.0.0.1.nip.io:8765` | **403** (DNS-rebind via wildcard host) |

Repeat for `POST /api/regen-prompt`, `POST /api/promote`, `DELETE /api/promote` — all four state-changing routes (FR-9, NFR-7).

**Assertions.**
- Every row matches the expected status, on every state-changing route.
- Row (f) and (g) — the raw dev-server Origin shapes — return 403 even though loopback aliases (b) admit. This is the **pre-rewrite shape** check from development.md move 11 (header-mutating-layer), and it MUST fail when sent direct-to-backend so the proxy hook is provably load-bearing.
- 403 body is the constant `{detail: "forbidden"}` (no header value echoed back — no header-name oracle either).
- `GET /api/tree`, `GET /api/file`, `GET /api/stages` are NOT subject to Origin/Host gating (read paths) — verify with the same headers but expect 200 / 404 per the read-path contract.

**Spec refs.** FR-9, NFR-6, NFR-7, AC-11.

**Components exercised.** `backend/libs/api_security.py` (Origin/Host middleware), `backend/libs/api_files.py` (PUT), `backend/libs/regen_prompt.py` (POST), `backend/libs/promotions.py` (POST/DELETE).

**Severity on failure.** `critical` (security failure per general.md severity policy).

---

### SYS-16b — Dev-server proxy mode under `make run-frontend` (multi-mode parity)

**Setup.**
- A second Playwright project (`webServer` entry per development.md move 1) that starts BOTH the backend (`make run-backend`) AND the Vite dev server (`make run-frontend` → `npm run dev`).
- Frontend served at `http://127.0.0.1:5173`; Vite proxy forwards `/api/*` to `http://127.0.0.1:8765`.
- Per FR-9 dev-server proxy contract: the proxy MUST rewrite outgoing `Origin` to `http://127.0.0.1:8765` and `Host` to `127.0.0.1:8765` (`changeOrigin: true`).

> Note: wiring the second `webServer` entry into `playwright.config.ts` is itself a follow-on stage-6 implementation task. SYS-16b is the **contract** the implementation must satisfy. Stage-5 strategies that follow MUST schedule this scenario in the e2e profile for `make run-frontend` mode (development.md move 1 — mode count = e2e profile count).

**Action.**

(1) Browser-driven build-prompt flow under proxy.
1. Open Playwright at `http://127.0.0.1:5173/project/development/spec_driven`.
2. Select interview stage; click "Build prompt".

(2) Direct-to-backend with raw browser-shape Origin (no proxy).
3. From a Node-side `httpx` / `fetch` call (NOT via the dev-server), `POST http://127.0.0.1:8765/api/regen-prompt` with `Origin: http://localhost:5173` and `Host: localhost:5173` and a valid body.

(3) Proxied through Vite.
4. From the SAME page context (so the request goes through the dev-server proxy at 5173), fetch `/api/regen-prompt` with the same body and observe the request the BACKEND sees.

**Assertions.**
- (1) The Build-prompt UX works under `make run-frontend` mode — assembled prompt block renders, Copy works (this is the regression check for the bug that originated development.md moves 1 and 11: run `spec_driven-006`'s "Build-prompt 403 under `make run-frontend`").
- (2) The direct-to-backend request with raw `Origin: http://localhost:5173` returns **403** — proves the Vite proxy's `Origin` rewrite is **load-bearing** (development.md move 11 pre-rewrite shape).
- (3) The proxied request returns **200** AND the backend sees `Origin: http://127.0.0.1:8765`, `Host: 127.0.0.1:8765` (post-rewrite shape). Capture this by adding a one-shot debug log line in `api_security.py` during the test and asserting on its content; OR by wiring a request-tap in the test harness on the backend port.
- Both modes render the SAME breakdown line, the SAME `regen-prompt-block`, the SAME Copy behavior (parity check — feature works in EVERY advertised mode per development.md move 1).
- Vite config under `projects/spec_driven/frontend/vite.config.ts` has a `server.proxy['/api'].configure(proxy, options) { proxy.on('proxyReq', (proxyReq) => { proxyReq.setHeader('origin', 'http://127.0.0.1:8765'); }); }` hook (or equivalent `headers: { Origin: ... }` shorthand). Validation grep: any commit removing this hook MUST trip a unit test in `unit_tests.md` that asserts the post-rewrite header shape — that's the move 11 "pre-rewrite shape" unit test that prevents silent regression.

**Spec refs.** FR-9 (dev-server proxy contract), FR-39, AC-11 (raw `localhost:5173` direct-to-backend → 403; proxied → 200).

**Components exercised.** `frontend/vite.config.ts` (proxy `configure` hook), `backend/libs/api_security.py`, `backend/libs/regen_prompt.py`.

**Severity on failure.** `blocker` (runtime mode in spec without an e2e profile = `blocker` per development.md). If the proxy hook is missing AND no pre-rewrite unit test exists, also `blocker` per move 11.

---

### SYS-17 — `make run` binds 127.0.0.1 only (not 0.0.0.0)

**Setup.**
- Clean shell. No prior process on port 8765.

**Action.**
1. Start `make run` (alias for `run-backend` per FR-39) in a background process.
2. From the same machine: `curl -sS http://127.0.0.1:8765/api/tree` — expect 200.
3. From the same machine, on a non-loopback interface address (e.g., the host's primary LAN IP discovered via `ipconfig` / `ip addr`): `curl --max-time 2 http://<lan-ip>:8765/api/tree` — expect connection refused / timeout (NOT 200).
4. Inspect the listener: `netstat -ano | findstr :8765` (Windows) / `ss -tlnp | grep 8765` (POSIX). Capture the bound address.
5. Source-grep: `git grep -nE '0\.0\.0\.0' projects/spec_driven/` and `git grep -nE 'host\s*=\s*"0\.0\.0\.0"' projects/spec_driven/` — must return zero matches.
6. Source-grep: `git grep -nE 'host\s*=\s*"127\.0\.0\.1"' projects/spec_driven/backend/` — must return at least one match (the actual `uvicorn.run` call).

**Assertions.**
- Step 2 succeeds (loopback works).
- Step 3 fails with `Connection refused` or timeout (LAN unreachable per NFR-1, OQ-9).
- Step 4: the bound address is `127.0.0.1:8765`, NOT `0.0.0.0:8765` and NOT `[::]:8765`.
- Step 5: zero matches (no `0.0.0.0` literal in project source).
- Step 6: at least one match (loopback bind is explicit, not implicit).
- Repeat the loopback-only assertion for `make run-prod` (single-process mode also binds 127.0.0.1 per FR-1).

**Spec refs.** FR-1, FR-39, NFR-7, AC-28, AC-29 (and OQ-9 cross-port LAN bind out of scope).

**Components exercised.** `backend/main.py` (uvicorn invocation), `Makefile` (`run` / `run-backend` / `run-prod` targets).

**Severity on failure.** `critical` (security failure — exposing the local-only mutation surface to LAN is the bug class FR-9 + NFR-7 + OQ-9 jointly forbid).

---

### SYS-18 — HTTP verb whitelist on `/api/file`

**Setup.**
- `make run-prod` running.

**Action.**
For path `/api/file?path=specs/development/spec_driven/findings/dossier.md`, issue:
1. `GET` — expect 200.
2. `PUT` (with valid Origin/Host + body) — expect 200.
3. `PATCH` — expect 405.
4. `DELETE` — expect 405.
5. `OPTIONS` — backend default (FastAPI returns 405 for unconfigured OPTIONS, or 200 with `Allow` header — check the actual contract).
6. `HEAD` — accepted as a synonym of GET in FastAPI; expect 200 with empty body.

**Assertions.**
- GET, PUT return 200.
- PATCH and DELETE return 405 with an `Allow: GET, PUT` (or equivalent) response header (FR-7, NFR-6, AC-12).
- The 405 body is JSON, not HTML.
- No DELETE-on-file endpoint exists (NFR-6 — mutation surface is exactly four endpoints, none of which is `DELETE /api/file`).

**Spec refs.** FR-7, NFR-6, AC-12.

**Components exercised.** `backend/libs/api_files.py`, FastAPI router method whitelist.

**Severity on failure.** `blocker` (acceptance criterion failure).

---

### SYS-19 — Extension allowlist (415) and 1 MB body cap (413) on `PUT /api/file`

**Setup.**
- `make run-prod` running.
- Fixture: a `.svg` file path attempted under `specs/`; a `.exe` file path attempted; a 1.5 MB text body for an existing `.md` path.

**Action.**
1. `PUT /api/file` for path ending in `.svg` — expect 415 (NFR-9 — SVG NOT in allowlist).
2. `PUT /api/file` for path ending in `.exe` — expect 415.
3. `PUT /api/file` for path ending in `.png` — expect 415 (FR-8 — image extensions are read-only, no PUT).
4. `PUT /api/file` for `.md` path with 1.5 MB body — expect 413 with `{detail: {kind: "too_large"}}` (FR-7, AC-10).
5. `PUT /api/file` for `.md` path with 999 KB body — expect 200.
6. `PUT /api/file` for `.md` path with body that's bytes-valid but starts with `\x00` (NUL) in first 16 bytes — expect 415 (FR-8 — text extensions validate first 16 bytes as plain text, no NUL).
7. `PUT /api/file` for `.md` path with body that is invalid UTF-8 (lone continuation byte) — expect 415.

**Assertions.**
- Every status matches expectation.
- 415 bodies are JSON of the form `{detail: "unsupported_media"}` (or equivalent constant) — no leak of allowed-extension list.
- 413 body matches the dossier-rec-#3 shape.
- Reads (GET) for `.svg` paths still 404 (the path is not in the allowlist — NFR-9 covers the read path too).
- Image extensions `.png`/`.jpg` ARE readable (FR-4, FR-23, SYS-6) but NOT writable (FR-8).

**Spec refs.** FR-4, FR-7, FR-8, NFR-9, AC-10.

**Components exercised.** `backend/libs/api_files.py` (PUT path — extension check, body cap, first-16-bytes validation).

**Severity on failure.** `blocker` (NFR-9 SVG enforcement is `critical` if SVG ever rendered as `<img>`/`<object>`).

---

### SYS-20 — Sidebar structural sanity (≥N leaves under each top-level section)

**Setup.**
- `make run-prod` running.
- Real fixture tree (the live `specs/`, `projects/`, `.claude/skills/`, `.claude/agent_refs/`, `CLAUDE.md`).

**Action.**
1. Playwright opens `/`.
2. Expand "Claude Settings & Shared Context"; count direct-leaf `.md` files (`CLAUDE.md`, every `.claude/skills/**/*.md`, every `.claude/agent_refs/**/*.md`).
3. Expand "Projects"; count visible projects under at least one task-type subfolder.
4. Drill into one project and assert it has the per-stage subfolders (`user_input/`, `interview/`, `findings/`, `final_specs/`, `validation/`).

**Assertions.**
- `Claude Settings & Shared Context` has ≥3 leaf descendants visible after full expansion (CLAUDE.md, ≥1 skill MD, ≥1 agent_ref MD).
- `Projects` has ≥1 task-type subfolder visible (`development/`, possibly `ai_video/`).
- Each project subtree exposes the canonical six-stage layout (`user_input/`, `interview/`, `findings/`, `final_specs/`, `validation/`).
- Tree walks `node.children` recursively (no `task_type.projects` / `project.stages` shapes leak — the bug class from `spec_driven-20260502-clean` per development.md move 2; AC-3, AC-26).

**Spec refs.** FR-2, FR-3, FR-15, AC-3, AC-26.

**Components exercised.** `backend/libs/api_files.py` (tree builder), `frontend/src/components/Sidebar.tsx` (recursive `node.children` walker).

**Severity on failure.** `critical` (API shape drift between front and back per development.md severity table).

---

### SYS-21 — Project-page master Regenerate panel (multi-stage build) + Wrap toggle + breakdown line

**Setup.**
- `make run-prod` running.
- Project: `specs/development/spec_driven/`.
- 0 follow-ups in `user_input/follow_ups/` (or 1 — record the count for the assertion).

**Action.**
1. Playwright opens `/project/development/spec_driven`.
2. Verify the page shows a stage map with all six stages, each with module checkboxes.
3. Toggle stages: select interview + final_specs only.
4. Within interview, deselect a module if more than one exists (otherwise leave default).
5. Toggle autonomous = ON.
6. Click "Build prompt".
7. After the prompt block renders, click the "Wrap" toggle in the prompt block header to OFF, then back to ON.

**Assertions.**
- Breakdown line shows: `2 stages selected, {follow_ups_count} follow-ups inlined, autonomous=on, {N} KB` (FR-33a).
- Inline `regen-prompt-block` renders with header bar (Title, Wrap toggle ON by default, Copy button) — FR-33d.
- The prompt body's first line is exactly `# EXECUTION MODE: AUTONOMOUS` (FR-11a, AC-22 — header verbatim).
- The prompt body includes the interview + final_specs stage sections in stage order (interview before final_specs — single combined prompt walks chosen stages in order per FR-32). Verify by locating the stage-id markers in the prompt text.
- Modules deselected in the UI do NOT appear in the assembled prompt (their per-module file paths are omitted).
- Wrap toggle OFF: `<pre>` style switches from `white-space: pre-wrap` to `white-space: pre`, horizontal scroll appears when text overflows. Wrap toggle ON: vertical-only scroll.
- Wrap toggle is per-render (NOT persisted to localStorage per OQ-3 / FR-33e). Reload the page and verify Wrap is back to default ON.
- `<pre>` body has `font-size: 13px`, `line-height: 1.55`, `max-height: 520px` per FR-33e (verified via `getComputedStyle`).

**Spec refs.** FR-32, FR-33, FR-34, AC-20, AC-22.

**Components exercised.** `frontend/src/components/ProjectPage.tsx`, `frontend/src/components/RegenPanel.tsx`, `frontend/src/components/RegenPromptBlock.tsx`, `frontend/src/components/WrapToggle.tsx`.

**Severity on failure.** `blocker`.

---

### SYS-22 — Broken internal markdown links render as muted span (NOT `<a>`)

**Setup.**
- `make run-prod` running.
- Fixture markdown file with three link forms: (a) valid relative `./valid.md` (target exists); (b) broken relative `./does-not-exist.md` (no target); (c) external `https://example.com`. Place at `specs/development/spec_driven/findings/link-fixture.md` and create the `./valid.md` sibling. Teardown deletes both.

**Action.**
1. Playwright deep-link to `/file/specs/development/spec_driven/findings/link-fixture.md`.
2. Inspect each link element.

**Assertions.**
- (a) Valid relative renders as `<a href="...">` and clicking navigates within the SPA.
- (b) Broken relative renders as `<span class="broken-link" title="link target not found">` — NOT `<a>` (FR-19, AC-27). Hovering shows the `title` tooltip.
- (c) External `https://` renders as `<a target="_blank" rel="noopener">`.
- The broken-link span receives muted-color CSS (verify computed `color` is in the `--text-muted` band — `agent_refs/project/development.md` light-theme rule).

**Spec refs.** FR-19, AC-27.

**Components exercised.** `frontend/src/components/MarkdownView.tsx` (link resolver hook); `frontend/src/lib/resolveLink.ts`.

**Severity on failure.** `blocker`.

---

### SYS-23 — Editor save-error banner persistence (NOT a toast)

**Setup.**
- `make run-prod` running.
- Mid-test, simulate a transient backend failure on PUT (e.g., the test harness intercepts `PUT /api/file` once and returns 500; or write the test against a file under a path that the harness temporarily marks read-only on disk so PUT fails with 500/403/409).

**Action.**
1. Playwright opens `/file/specs/development/spec_driven/findings/dossier.md`, click ✎ Edit, type a change.
2. Click Save while the failure injection is active.
3. Wait 5 seconds.
4. Disable the failure injection.
5. Click Save again.

**Assertions.**
- After step 2, an inline banner appears ABOVE the textarea (`[data-testid="save-error-banner"]`) with text describing the failure. (FR-28.)
- The banner does NOT auto-dismiss after the typical toast timeout (3–5 s) — verified at step 3 (banner is still present).
- The banner is NOT a `[role="status"]` toast in a corner — it is positioned in normal flow above the textarea (verify via DOM ancestry under the editor container).
- The textarea content is preserved (the user did NOT lose their edits while the banner is up).
- After step 5 (successful retry), the banner clears (`[data-testid="save-error-banner"]` disappears).
- During the failed save, the dirty indicator (`●` in toolbar, `*` in title) remains set.

**Spec refs.** FR-28.

**Components exercised.** `frontend/src/components/Editor.tsx`, `frontend/src/components/SaveErrorBanner.tsx`.

**Severity on failure.** `blocker`.

---

### SYS-24 — Pin survival in regen prompt (promotion roundtrip → assembly verbatim)

**Setup.**
- `make run-prod` running.
- Project: `specs/development/spec_driven/`. Empty `validation/promoted.md` at start.

**Action.**
1. Playwright opens `/file/specs/development/spec_driven/validation/acceptance_criteria.md`.
2. Locate AC-7; click its 📌 pin button.
3. Verify the SPA issues `POST /api/promote` with `{stage_folder: "validation", item_id: "AC-7", item_text: <verbatim AC-7 block>, ...}`.
4. Inspect `specs/development/spec_driven/validation/promoted.md` on disk — must now contain AC-7's verbatim text.
5. Open `/project/development/spec_driven`; select stage = validation; build prompt.
6. Inspect the assembled prompt.
7. Unpin AC-7 (click 📌 again); verify `DELETE /api/promote` is sent and `promoted.md` is updated.
8. Re-test the assembled prompt has the unpinned text removed.

**Assertions.**
- After step 4, `promoted.md` contains the literal AC-7 block verbatim, parsed correctly by `libs/promotions.py::parse_promoted_text` (development.md / general.md principle 8).
- After step 6, the assembled prompt contains a `## Pinned items (MUST survive regeneration)` section under the validation stage with the AC-7 text appearing verbatim (FR-11d, AC-25).
- The verbatim assertion uses the parser per general.md principle 8 (asserted modulo whitespace).
- After step 7, `promoted.md` no longer contains the AC-7 block (idempotent DELETE per FR-14).
- After step 8, the assembled prompt's pinned-items section either omits AC-7 entirely or, if no other pins remain, omits the `## Pinned items` section.

**Spec refs.** FR-11d, FR-13, FR-14, FR-35, FR-37, NFR-15, AC-24, AC-25.

**Components exercised.** `backend/libs/promotions.py`, `backend/libs/regen_prompt.py`, `frontend/src/components/PinButton.tsx`, `frontend/src/components/RegenPanel.tsx`.

**Severity on failure.** `critical` (missing pin = `critical` per general.md principle 8 — silent loss of user-pinned content is the highest-priority regression).

---

### SYS-25 — NFR-3 latency budget (initial app load < 2 s on localhost)

**Setup.**
- `make run-prod` running.
- Cold browser context (no cache). Realistic fixture: ≥10 projects, ≥1000 leaves total in the tree.
- Playwright with `page.goto(url, { waitUntil: 'networkidle' })`.

**Action.**
1. `performance.now()` before `page.goto('/')`.
2. Wait for sidebar to render its first leaf AND the initial file (default landing — likely `CLAUDE.md`) to render its first heading.
3. Capture `performance.now()` end.

**Assertions.**
- Total elapsed wall-clock from `goto` to "first heading visible AND ≥1 sidebar leaf visible" is **< 2000 ms** (NFR-3).
- `GET /api/tree` server-side latency (captured via Playwright `request.timing()` or backend log) is **< 250 ms** for the canonical-scale fixture (NFR-1).
- `GET /api/file` for `CLAUDE.md` (the default landing file) is **< 100 ms** (NFR-2 — file is well under 500 KB).
- Run 3 times consecutively; the **median** must satisfy the budgets (single-run noise tolerance per validation/general.md severity policy — observe-only metric outside expected range = `warning`, but consistent failure = `blocker` per development.md hard-performance-budget row).

**Spec refs.** NFR-1, NFR-2, NFR-3.

**Components exercised.** Full stack — initial load is the integrating measurement.

**Severity on failure.** `warning` for a single outlier; `blocker` if median fails (hard performance budget per general.md).

---

### SYS-26 — Stale-write 409 conflict via `If-Unmodified-Since`

**Setup.**
- `make run-prod` running.
- Fixture: `specs/development/spec_driven/findings/conflict-fixture.md` (created by the test, deleted on teardown), initial content "v1".

**Action.**
1. Playwright opens `/file/specs/development/spec_driven/findings/conflict-fixture.md`. Editor enters edit mode; capture the `mtime` the SPA stored in component state.
2. **Side-channel write:** the test harness (NOT the SPA) modifies the file directly via shell — write content "v2" — bumping `mtime` by ≥1 second.
3. In the Playwright editor, append "user-edit" to the textarea content; click Save.
4. Inspect the response.
5. The save-error banner offers a "Reload" button — click it.
6. Edit again ("user-edit-2"); click Save.

**Assertions.**
- Step 3's `PUT /api/file` includes `If-Unmodified-Since: <captured-mtime-from-step-1>` header (FR-29).
- Backend returns **409** with body `{detail: {kind: "stale_write", current_mtime: <new-mtime>}}` (FR-7b).
- Save-error banner shows "file changed externally — Reload?" with a Reload button (FR-29).
- Step 5's Reload button: SPA re-fetches the file, replaces textarea content with "v2", updates the captured mtime, and discards the in-memory "user-edit" (per FR-29 — "discards in-memory edits").
- Step 6 succeeds (200) because the mtime is now fresh.
- Final on-disk content is "v2user-edit-2" (or however the post-reload edit composed).
- Pinned items in `promoted.md` are NOT touched by this scenario (NFR-15 sanity).

**Spec refs.** FR-7b, FR-29, OQ-1 (mtime in v1), AC-13, AC-14, AC-15.

**Components exercised.** `backend/libs/api_files.py` (409 path, mtime check), `frontend/src/components/Editor.tsx` (If-Unmodified-Since + 409 handler), `frontend/src/components/SaveErrorBanner.tsx` (Reload button).

**Severity on failure.** `blocker`.

---

### SYS-27 — Manual UI walkthrough handoff after automated levels pass

**Setup.**
- All preceding SYS-1..SYS-26 passing on the runtime.

**Action.**
1. Validation runner emits the final automated-level summary.
2. Runner emits a `validation.requires_manual_walkthrough` event into the run's `events.jsonl` per development.md move 7.
3. The skill surfaces the walkthrough checklist to the user before declaring done.

**Assertions.**
- An event of type `validation.requires_manual_walkthrough` is present in `events.jsonl` for the run (development.md move 7).
- The event payload includes a checklist covering at minimum:
  - Visual contrast on light-theme app chrome under macOS / Windows / Linux defaults (NFR-16, AC dossier rec).
  - Focus visibility on every interactive element (sidebar items, toolbar buttons, editor controls, pin/promote buttons, Wrap toggle, autonomous toggle, Copy button).
  - Motion / transitions (no jarring jumps when switching render modes; banner animations subtle).
  - Perceived latency: regen-prompt block render after Build click feels responsive (subjective, but a complement to NFR-3's hard budget).
  - Soft-wrap toggle UX feels right per OQ-3 (the open question — flag if users find reset jarring).
  - Read the prompt-block text for legibility under the dark `<pre>` carve-out (NFR-16) at 13px / 1.55 line-height.
- The `agent_team` skill flow halts (does not advance past stage 6 unit "done") until the user acknowledges the walkthrough.

**Spec refs.** NFR-16, OQ-3, plus the full set of interactive surfaces (FR-19..FR-36).

**Components exercised.** Validation runner / skill's stage-6 closing step.

**Severity on failure.** `warning` (skipping the manual gate is an audit hole; it does not break a feature). General.md principle 4 — "Manual walkthrough is a level too" — promotes this from afterthought to first-class artifact.

---

## Severity summary

Mapped per general.md severity policy + development.md escalations:

| Class of finding (across SYS-1..SYS-27) | Severity |
|---|---|
| SYS-1 boot-smoke failure | `critical` |
| SYS-14 / SYS-15 path-traversal or symlink-refusal failure | `critical` |
| SYS-16 / SYS-16b Origin/Host gate failure | `critical` |
| SYS-17 0.0.0.0 leak | `critical` |
| SYS-13 ParseFallback boundary missing / latent blank-page | `critical` |
| SYS-24 missing pin in regen prompt | `critical` |
| Acceptance-criterion failure (most SYS-* on assertion mismatch) | `blocker` |
| SYS-2..SYS-6 missing render-mode e2e | `blocker` |
| SYS-16b missing dev-server proxy profile | `blocker` |
| SYS-25 latency budget median miss | `blocker` |
| SYS-25 single-run outlier | `warning` |
| SYS-27 manual walkthrough not surfaced | `warning` |

## Open questions surfaced from this strategy

- **OQ-A.** SYS-16b assumes the `playwright.config.ts` second-`webServer` wiring is part of stage 6's deliverable. If stage 6 ships only the single-process Playwright profile, SYS-16b falls back to a manual-walkthrough variant (open browser at 5173, drive Build-prompt manually, observe success). Recommendation: schedule the second `webServer` as a stage-6 work unit; do not allow the cheaper fallback past sign-off.
- **OQ-B.** SYS-14 row (5) (literal backslash) and (6) (NUL byte) are explicitly defended by NFR-12 (Vite CVE-2025-62522). Confirm during stage 6 that the rejection happens in `safe_resolve.py` BEFORE `os.path.realpath` — not after. The latency-parity check in SYS-14 partially probes this; a `unit_tests.md` row (`test_safe_resolve_rejects_backslash_before_realpath`) makes it ironclad.
- **OQ-C.** SYS-23's failure-injection mechanism — Playwright route interception vs read-only-on-disk — is harness-dependent. If the runner can't easily set Windows file ACLs, prefer route interception. Either way, the contract is "PUT fails non-transiently for at least 5 s and the banner persists."
- **OQ-D.** SYS-24's verbatim assertion uses `parse_promoted_text` from `libs/promotions.py` (general.md principle 8). If that function does not yet exist at stage 5 sign-off, the strategy must schedule it as a stage-6 work unit.
