# System tests — `spec_driven`

Run: `spec_driven-20260503-030434`
Spec: `specs/development/spec_driven/final_specs/spec.md`
Pre-reading consulted: `.claude/agent_refs/validation/general.md`, `.claude/agent_refs/validation/development.md`.

## Conventions

- All scenarios run against the production single-process server: `make run-prod` from `projects/spec_driven/` binds `127.0.0.1:8765`. Each SYS-NN that needs the server starts it via the `serve_prod` Playwright fixture (autouse: spawns `make run-prod` in a subprocess, polls `GET http://127.0.0.1:8765/api/tree` until 200 with a 30 s timeout, yields, then `terminate()` + `wait()` on teardown).
- Browser scenarios use **Playwright (Chromium)** via `pytest-playwright`. Selectors are stable `data-testid` attributes from the spec (`sidebar`, `tree-leaf`, `project-link`, `qa-view`, `markdown-view`, `code-view`, `jsonl-view`, `image-placeholder`, `regen-prompt-block`, `regen-build-button`, `regen-copy-button`, `regen-wrap-toggle`, `regen-breakdown`, `regen-warning-banner`, `editor-textarea`, `editor-save`, `editor-discard`, `editor-close`, `editor-dirty-dot`, `editor-error-banner`, `qa-q-edit-{id}`, `qa-a-edit-{id}`, `qa-block-q-{id}`, `qa-block-a-{id}`, `link-broken`, `autonomous-toggle`).
- API-only scenarios use **`httpx.Client(base_url="http://127.0.0.1:8765")`**. Browser-driven scenarios MUST assert on rendered DOM, never on raw API JSON.
- The `consoleErrors` assertion uses a Playwright `page.on("console", ...)` listener installed in the fixture; failure is any message with `type in {"error"}` other than the explicitly-allowed "Failed to load resource" 404 noise that the test triggered intentionally.
- Windows-vs-POSIX: every scenario that depends on POSIX-only behavior is marked `@pytest.mark.skipif(sys.platform == "win32", reason=...)`. Junctions are exercised on Windows in lieu of symlinks; POSIX symlink tests are skipped on Windows. The canonical dev host IS Windows + Git Bash, so the default expectation is Windows-pass + POSIX-skip.
- Scenarios that mutate disk state use a `scratch_path` fixture under `specs/development/spec_driven/__scratch__/` (an allow-listed subfolder); fixture tears down by `os.remove` on exit. No scenario writes outside the EXPOSED_TREE.
- Each SYS-NN is independently runnable: `pytest tests/system/test_sysNN_*.py -v` (or for Playwright + headed debugging, append `--headed --slowmo=300`).
- Make targets used: `make e2e` (runs every Playwright scenario), `make test-backend` (runs every httpx scenario), `make boot-smoke` (just SYS-1).

---

## SYS-1 — Boot smoke (process starts, /api/tree 200, structurally meaningful endpoint returns expected shape)

**Setup.** Working directory `projects/spec_driven/`. No prior server process listening on 8765. `frontend/dist/` has been built (`make build-frontend`).

**Action.**
1. From a subprocess, run `make run-prod` (which executes `python backend/main.py` after asserting the SPA build is present).
2. Poll `httpx.get("http://127.0.0.1:8765/api/tree")` once per 250 ms until 200 or 30 s elapses. Capture every transient exception in a list `boot_errors`.
3. Once 200, fetch `GET /api/tree` (capture `tree`) and `GET /api/file?path=specs/development/spec_driven/final_specs/spec.md` (capture `file_resp`).
4. Tear down by `proc.terminate(); proc.wait(timeout=10)`.

**Assertions.**
- `proc.returncode is None` while polling (no startup crash).
- `boot_errors == []` after the first successful 200 (no startup-time exceptions on stderr; assert by reading `proc.stderr` accumulator and grepping for `Traceback`).
- `tree["type"] == "section"` AND `tree["children"]` is a non-empty list AND every non-leaf node has a `children` key (recursive walk; consumer-walk parity with FR-1, per `agent_refs/validation/development.md` move #2).
- `tree` has at least two top-level sections whose `name` matches `Claude Settings & Shared Context` and `Projects`.
- `file_resp.status_code == 200` AND `"# Specification — spec_driven"` in `file_resp.json()["content"]` (not a fixture; this is the real on-disk spec).
- `file_resp.headers["X-Content-Type-Options"] == "nosniff"` AND `file_resp.headers["Content-Disposition"].startswith("attachment")` (FR-5).

**Spec refs:** FR-1, FR-2, FR-3, FR-5, FR-38, FR-39, NFR-1, AC-1, AC-2, AC-28.
**Components exercised:** `backend/main.py`, `backend/libs/tree.py`, `backend/libs/safe_resolve.py`, `backend/libs/files.py`, Makefile `run-prod` target, the boot path itself.

---

## SYS-2 — Render mode: MarkdownView (deep-link to `final_specs/spec.md`)

**Setup.** `serve_prod` fixture running. Playwright Chromium context, `consoleErrors=[]` listener attached.

**Action.**
1. `await page.goto("http://127.0.0.1:8765/file/specs/development/spec_driven/final_specs/spec.md")`.
2. Wait for `[data-testid="markdown-view"]` (timeout 5 s).
3. Capture `main_html = await page.locator("main").inner_html()`.

**Assertions.**
- `data-testid="markdown-view"` is visible AND `data-testid="qa-view"` is NOT in the DOM.
- `main_html` contains the rendered text `# Specification — spec_driven` rendered as an `<h1>` (assert via `page.locator("main h1").first.text_content()`).
- At least one `<code>` element (inline code) and at least one `<pre>` element (fenced code block) are in the DOM (FR-22).
- No raw `<script>` or `<iframe>` element appears under `main` (rehype-sanitize, NFR-8).
- `consoleErrors == []`.

**Spec refs:** FR-17, FR-18, FR-22, NFR-8, AC-1.
**Components exercised:** Sidebar, router, MarkdownView, react-markdown + rehype-sanitize + shiki path.

---

## SYS-3 — Render mode: QaView (deep-link to `interview/qa.md`)

**Setup.** `serve_prod` fixture. The on-disk `specs/development/spec_driven/interview/qa.md` exists (canonical, written by stage 2 of this very run).

**Action.**
1. `await page.goto("http://127.0.0.1:8765/file/specs/development/spec_driven/interview/qa.md")`.
2. Wait for `[data-testid="qa-view"]` (timeout 5 s).

**Assertions.**
- `data-testid="qa-view"` is visible AND `data-testid="markdown-view"` is NOT in the DOM (FR-18 dispatches to QaView for this path).
- `await page.locator("main").inner_html() != ""` (page is non-empty, AC-18).
- At least one element matching `[data-block="q"]` (Q-tinted block) AND at least one `[data-block="a"]` (A-tinted block) is in the DOM (FR-29).
- At least one `[data-testid^="qa-q-edit-"]` pencil and one `[data-testid^="qa-a-edit-"]` pencil are present (FR-30).
- Each rendered Round has a `[data-category-badge]` element child (FR-29 category badge).
- `consoleErrors == []` (AC-18).

**Spec refs:** FR-17, FR-18, FR-21, FR-29, FR-30, AC-18, AC-19.
**Components exercised:** Sidebar, router, QaView parser + renderer, Error Boundary (must NOT trip on the canonical file).

---

## SYS-4 — Render mode: JsonlView (deep-link to a real `.jsonl`)

**Setup.** `serve_prod` fixture. The on-disk `.audit/adhoc_agents/2026-05-03/spec_driven-20260503-030434/events.jsonl` exists with at least 3 records. (Pre-create via fixture if the audit directory is gitignored: write 3 sample event lines to `specs/development/spec_driven/__scratch__/sample.jsonl`. The EXPOSED_TREE includes that scratch path under specs.) Use the scratch file to keep the test deterministic.

**Action.**
1. Write the scratch jsonl: 3 distinct JSON objects, one per line.
2. `await page.goto("http://127.0.0.1:8765/file/specs/development/spec_driven/__scratch__/sample.jsonl")`.
3. Wait for `[data-testid="jsonl-view"]` (timeout 5 s).

**Assertions.**
- `data-testid="jsonl-view"` is visible AND `data-testid="markdown-view"` is NOT in the DOM.
- Exactly 3 row elements `[data-row]` are rendered, in order (FR-18: one record per row).
- The third row's text contains the third object's distinguishing field value (assert on rendered DOM text, not API JSON).
- `consoleErrors == []`.

**Spec refs:** FR-17, FR-18, AC-1.
**Components exercised:** Sidebar, router, JsonlView.

---

## SYS-5 — Render mode: CodeView (deep-link to a real `.json`)

**Setup.** `serve_prod` fixture. Use `projects/spec_driven/backend/static/manifest.json` if present, else write `specs/development/spec_driven/__scratch__/sample.json` with `{"key": "value", "n": 42}`.

**Action.**
1. `await page.goto("http://127.0.0.1:8765/file/specs/development/spec_driven/__scratch__/sample.json")`.
2. Wait for `[data-testid="code-view"]` (timeout 5 s).

**Assertions.**
- `data-testid="code-view"` is visible.
- A shiki-highlighted token element exists (e.g., a `<span>` carrying `class*="token"` or shiki's class scheme); text "value" is present in the rendered DOM (FR-22 syntax highlighting).
- `consoleErrors == []`.

**Spec refs:** FR-17, FR-18, FR-22.
**Components exercised:** Sidebar, router, CodeView, shiki.

---

## SYS-6 — Render mode: ImagePlaceholder (deep-link to a real `.png`)

**Setup.** `serve_prod` fixture. The on-disk PNG at `specs/development/spec_driven/__scratch__/sample.png` (write a 1×1 PNG via fixture, ≤200 bytes) exists.

**Action.**
1. `await page.goto("http://127.0.0.1:8765/file/specs/development/spec_driven/__scratch__/sample.png")`.
2. Wait for `[data-testid="image-placeholder"]` (timeout 5 s).

**Assertions.**
- `data-testid="image-placeholder"` is visible.
- A child `<img>` element with `src` resolving to `/api/file?path=specs/development/spec_driven/__scratch__/sample.png` is present.
- The `<img>` element's `naturalWidth > 0` after `await page.locator("img").evaluate("e => e.complete && e.naturalWidth")` (image actually loaded).
- `consoleErrors == []`.

**Spec refs:** FR-17, FR-18, FR-3 (image extensions allowlisted).
**Components exercised:** Sidebar, router, ImagePlaceholder, `GET /api/file` for `.png`.

---

## SYS-7 — File editor save round-trip (PUT /api/file via UI → reload → content persists)

**Setup.** `serve_prod` fixture. `scratch_path = "specs/development/spec_driven/__scratch__/sys7.md"` pre-seeded with `original\n`.

**Action.**
1. `await page.goto(f"http://127.0.0.1:8765/file/{scratch_path}")`. Wait for `[data-testid="markdown-view"]`.
2. Click `[data-testid="editor-toggle"]` (the toolbar ✎). Wait for `[data-testid="editor-textarea"]`.
3. Clear the textarea, type `edited\n`. Assert `[data-testid="editor-dirty-dot"]` becomes visible (FR-26).
4. Press `Ctrl+S`. Wait for the dirty dot to disappear (successful save, FR-26 + FR-28).
5. Click `[data-testid="editor-close"]`. Assert the editor is replaced by `[data-testid="markdown-view"]`.
6. `await page.reload()`. Wait for `[data-testid="markdown-view"]`.
7. Assert `await page.locator("main").inner_text()` contains `edited`.
8. Out-of-band: `httpx.get(f"/api/file?path={scratch_path}")` returns content `edited\n` and an `mtime` strictly greater than the pre-test `mtime` (atomicity/round-trip via FR-6).

**Assertions.**
- All numbered steps complete without `consoleErrors`.
- The final `GET /api/file` returns `{path: scratch_path, content: "edited\n", bytes: 7, mtime: <fresh>}`.

**Spec refs:** FR-3, FR-6, FR-25, FR-26, FR-28, NFR-10, AC-9.
**Components exercised:** Editor toolbar, textarea, Ctrl+S handler, `PUT /api/file`, `os.replace` atomic write, dirty-dot indicator.

---

## SYS-8 — Per-Q inline edit on `qa.md` → save → reload → structured view shows updated text → file still parses

**Setup.** `serve_prod` fixture. The canonical `specs/development/spec_driven/interview/qa.md` is checkpointed (`shutil.copy` to `__scratch__/qa.md.bak`) before the test; restored after via finalizer. The test edits ONE answer text in place.

**Action.**
1. `await page.goto("http://127.0.0.1:8765/file/specs/development/spec_driven/interview/qa.md")`. Wait for `[data-testid="qa-view"]`.
2. Identify the first A-block: `first_a = page.locator("[data-testid^=qa-a-edit-]").first`. Capture its parent block's `data-block-id` attribute as `block_id`.
3. Click the pencil. A `<textarea>` scoped to that block appears (`[data-testid="qa-block-editor-${block_id}"]`).
4. Append the literal token ` __SYS8_MARK__` to the existing answer text. Press Ctrl+S. Wait for the per-block editor to close and the rendered A-block to show the new text.
5. While the per-block editor is open (between steps 3 and 4), assert the file-level `[data-testid="editor-toggle"]` has attribute `aria-disabled="true"` AND is still visible (FR-31).
6. After save, `await page.reload()`. Wait for `[data-testid="qa-view"]` (NOT the markdown fallback — FR-20 is fallback path; this MUST stay on QaView, AC-19).
7. Assert the same A-block (matched by `data-block-id="${block_id}"`) renders with the updated text containing `__SYS8_MARK__`.
8. Out-of-band: `GET /api/file?path=...qa.md` returns content that, when re-fed through the QaView parser (call the parser via a small bundled `node` script run by the test fixture against the file content, OR via the production `/file` route which is what the next assertion verifies), yields > 0 Q/A pairs (file still parses).

**Assertions.**
- Steps 1–7 complete without `consoleErrors`.
- The reloaded QaView dispatches to `qa-view`, NOT to `markdown-view` (Error Boundary did NOT fire, AC-19).
- The file's bytes contain the literal `__SYS8_MARK__`; the Q/A structure is preserved (run the QaView parser against the persisted file via a Node-run import of `frontend/src/lib/qa_parser.ts` and assert `pairs.length >= 1`).

**Spec refs:** FR-6, FR-29, FR-30, FR-31, AC-9, AC-19.
**Components exercised:** QaView, per-block editor, mutual-exclusion logic with file-level toggle, `PUT /api/file` round-trip, the QaView parser.

---

## SYS-9 — Regen-prompt assemble: small (<50 KB) shows no warning

**Setup.** `serve_prod` fixture. The project `development/spec_driven` exists with stages populated. Use `httpx` since this scenario does not exercise the UI's render path of the assembled body.

**Action.**
1. `POST /api/regen-prompt` with body `{"project_type": "development", "project_name": "spec_driven", "stages": ["interview"], "modules": {"interview": []}, "autonomous": false}` (single stage, no module body to keep it small).

**Assertions.**
- `resp.status_code == 200`.
- `body = resp.json()`; `body["warning"] is None` (FR-12 small bucket).
- `body["bytes"] < 50 * 1024`.
- `body["prompt"].startswith("# EXECUTION MODE: INTERACTIVE")` (FR-11(a), AC-15).
- `body["prompt"]` does NOT contain the autonomous imperative line (FR-11(b)).
- `body["prompt"]` contains the literal `### Constraints` and the read-zero sentence `regeneration deletes prior outputs first; new generation reads only the inputs.` (AC-16).
- `body["selected_stages_count"] == 1` AND `body["follow_ups_count"]` is a non-negative int.

**Spec refs:** FR-10, FR-11, FR-12, AC-13, AC-15, AC-16.
**Components exercised:** `POST /api/regen-prompt`, the prompt assembler in `backend/libs/regen_prompt.py`.

---

## SYS-10 — Regen-prompt assemble: medium (50 KB–1 MB warning) UI banner renders

**Setup.** `serve_prod` fixture. To force a medium-sized prompt deterministically, the test fixture writes a synthetic large `revised_prompt.md` (~80 KB of repeated lorem) into `specs/development/spec_driven/user_input/revised_prompt.md` after a checkpoint copy. Restore on teardown.

**Action.**
1. `await page.goto("http://127.0.0.1:8765/file/specs/development/spec_driven/interview/qa.md")` to land on a stage file.
2. Open the Regenerate `<details>` (default-collapsed per AC-22; assert it is closed first, then click to expand).
3. Click `[data-testid="regen-build-button"]`.
4. Wait for `[data-testid="regen-prompt-block"]` to appear.

**Assertions.**
- `[data-testid="regen-warning-banner"]` is visible AND its text matches `/^warning: .* — verify your selection before pasting$/` (FR-33(e)).
- `[data-testid="regen-prompt-block"]` is visible (no inner `<details>` to expand, AC-23).
- `[data-testid="regen-breakdown"]` text matches `/^\d+ stages? selected, \d+ follow-ups? inlined, autonomous=(true|false), [\d.]+ KB$/` (FR-33(d)).
- The `<pre>` body's text length corresponds to a payload between 50 KB and 1 MB (assert via `await page.locator("[data-testid=regen-prompt-block] pre").evaluate("e => e.textContent.length")` returning a value > 50 * 1024).
- `consoleErrors == []`.

**Spec refs:** FR-12, FR-33, AC-13, AC-22, AC-23.
**Components exercised:** Regenerate panel, breakdown line, warning banner, prompt block render.

---

## SYS-11 — Regen-prompt assemble: large (>1 MB → 413 → no `regen-prompt-block` rendered)

**Setup.** `serve_prod` fixture. Fixture writes a synthetic huge `revised_prompt.md` (~1.2 MB of repeated content) into `specs/development/spec_driven/user_input/revised_prompt.md` after checkpoint. Restore on teardown.

**Action.**
1. Direct API: `POST /api/regen-prompt` (httpx) with all stages selected → expect 413.
2. Browser: navigate to the stage file, open Regenerate, click Build prompt.

**Assertions.**
- API: `resp.status_code == 413` AND `resp.json()["detail"]["kind"] == "too_large"` AND `resp.json()["detail"]["bytes"] > 1024 * 1024` (FR-12, AC-13).
- UI: after Build prompt, an error banner is rendered (the same broken-link/error component class `link-broken` style or a `[role="alert"]` banner) reading something like `Could not build prompt: too large (… MB)`. **No** `[data-testid="regen-prompt-block"]` element exists in the DOM.
- `consoleErrors == []` (the 413 is an expected error path, NOT a console error).
- `[data-testid="regen-copy-button"]` does NOT exist (no block to copy from).

**Spec refs:** FR-12, FR-24, AC-13.
**Components exercised:** size-cap enforcement in the assembler, frontend error rendering for the 413 case.

---

## SYS-12 — Autonomous-mode toggle persistence + cross-tab `storage` event

**Setup.** `serve_prod` fixture. Two Playwright contexts (or two pages within a single shared context — same origin/storage → `storage` events fire across tabs only when contexts share storage; use **two pages in the same context** because Playwright contexts share localStorage per-domain).

Note: Playwright fires `storage` events between tabs of the same `BrowserContext`; using two contexts would be true cross-tab from the user's POV but does NOT fire `storage` events. The spec language (FR-35 "via a `storage` event listener for cross-tab") refers to the browser-native `storage` event, which fires for same-origin tabs of the same browser session — modeled accurately by two pages in one Playwright context.

**Action.**
1. Page A: `await page_a.goto("http://127.0.0.1:8765/project/development/spec_driven")`. Open the master Regenerate panel.
2. Assert `[data-testid="autonomous-toggle"]` initial state is unchecked (FR-35 default false; AC-26).
3. Page B (same context): `await page_b.goto("http://127.0.0.1:8765/file/specs/development/spec_driven/interview/qa.md")`. Open the per-stage Regenerate `<details>`. Assert its `[data-testid="autonomous-toggle"]` is also unchecked.
4. Page A: click the autonomous toggle. Assert checkbox flips to checked.
5. Page A: `localStorage.getItem("spec_driven.autonomous_mode.v1") === "true"` (evaluate in browser).
6. Page B: WITHOUT explicit reload, assert that within 2 s the page B autonomous toggle has flipped to checked (driven by the `storage` event, FR-35).
7. Page A: `await page_a.reload()`. After reload, the toggle remains checked.
8. Page A: click again to uncheck. Assert localStorage is `"false"` AND page B updates within 2 s.

**Assertions.**
- All steps complete; no `consoleErrors`.
- Cross-tab propagation latency < 2 s.

**Spec refs:** FR-33(b), FR-34, FR-35, AC-26.
**Components exercised:** `autonomous-toggle` component, localStorage persistence, in-process subscription, native `storage` event listener.

---

## SYS-13 — QaView fallback via Error Boundary (deliberately-malformed qa.md → MarkdownView fallback, consoleErrors empty)

**Setup.** `serve_prod` fixture. Fixture writes a deliberately-malformed file at `specs/development/spec_driven/__scratch__/interview/qa.md` (the path is `interview/qa.md` so the dispatcher routes to QaView; content is a real-looking but unparseable structure: e.g., `## Round X\n\n### category\n\n- Q: this question has no matching A`, repeated, with NO answer lines that the regex recognizes — neither interactive `- A:` nor autonomous `- A *(...)*:` form). Not a synthetic oddity; a representative "real qa.md the parser cannot handle" file (per FR-20 + AC-20).

**Action.**
1. `await page.goto("http://127.0.0.1:8765/file/specs/development/spec_driven/__scratch__/interview/qa.md")`.
2. Wait for `[data-testid="markdown-view"]` (the Error Boundary fallback target, FR-20).

**Assertions.**
- `[data-testid="markdown-view"]` is visible AND `[data-testid="qa-view"]` is NOT in the DOM (Error Boundary fell back, FR-19, FR-20).
- A one-line banner with `role="alert"` is visible above the markdown body, text starting with `Could not parse structured Q/A view; rendering raw markdown.` and containing `(cause:` (FR-20).
- `await page.locator("main").inner_text() != ""` (page is non-empty, AC-20).
- `consoleErrors == []` (the boundary swallowed the parse error gracefully; AC-20 explicitly asserts empty consoleErrors). Note: React in dev mode logs caught boundary errors to console as warnings — the production build (which `make run-prod` serves from `backend/static/`) does NOT. SYS-13 runs against the production build, so this assertion is meaningful.

**Spec refs:** FR-19, FR-20, FR-21, AC-20.
**Components exercised:** QaView parser, the Error Boundary class component, MarkdownView as fallback target, the production React build.

---

## SYS-14 — `safe_resolve` under attack: path-traversal probes (single 404)

**Setup.** `serve_prod` fixture. httpx.

**Action.** For each probe in the table below, `GET /api/file?path=<probe>` and capture status:

| Probe | Reason |
|---|---|
| `../etc/passwd` | classic relative traversal |
| `specs/../../etc/passwd` | embedded traversal |
| `..\\windows\\system32\\drivers\\etc\\hosts` | backslash variant |
| `/etc/passwd` | absolute POSIX |
| `C:\\Windows\\System32\\drivers\\etc\\hosts` | absolute Windows |
| `specs/development/spec_driven/final_specs/../../../../etc/passwd` | deep traversal |
| `specs%2F..%2F..%2Fetc%2Fpasswd` | URL-encoded |
| `specs/development/spec_driven/./final_specs/./spec.md/../../../../../etc/passwd` | dot-segment + traversal |

**Assertions.**
- Every probe returns status `404` (single status — NOT 403 — per FR-3 "removes enumeration side-channel" and AC-3).
- Response body for every probe is identical (or at least carries no enumeration information distinguishing "outside tree" from "not found"): `resp.json() == {"detail": "not found"}` or equivalent canonicalized shape.
- For the canonical legitimate path `specs/development/spec_driven/final_specs/spec.md`, status is 200 (control case to ensure the server is actually serving).

**Spec refs:** FR-3, FR-4, NFR-4, AC-3.
**Components exercised:** `safe_resolve`, `GET /api/file` error handling.

---

## SYS-15 — `safe_resolve` under attack: junctions, ADS, reserved device names (single 404)

**Setup.** `serve_prod` fixture. httpx.

**Windows-specific fixtures** (skip on POSIX, `@pytest.mark.skipif(sys.platform != "win32", reason="...")`):
- Create a junction at `specs/development/spec_driven/__scratch__/_junc` pointing to `C:\Windows\System32` via `subprocess.run(["cmd", "/c", "mklink", "/J", junc_path, target])`. Teardown removes it via `os.rmdir`.
- A real on-disk file `specs/development/spec_driven/final_specs/spec.md` exists (control).

**POSIX-specific fixtures** (skip on Windows, `@pytest.mark.skipif(sys.platform == "win32", reason="symlink test requires Developer Mode and is exercised via junction on Windows in this test (separate skip)")`):
- Create a symlink at `specs/development/spec_driven/__scratch__/_sym` pointing to `/etc`. Teardown unlinks.

**Action.** For each probe (combining Windows + POSIX as gated), `GET /api/file?path=<probe>` and capture status:

| Probe | Platform | Reason |
|---|---|---|
| `specs/development/spec_driven/CON.md` | both | Windows reserved name (AC-4) |
| `specs/development/spec_driven/PRN` | both | Windows reserved name |
| `specs/development/spec_driven/COM1.txt` | both | Windows reserved name |
| `specs/development/spec_driven/LPT9.json` | both | Windows reserved name |
| `specs/development/spec_driven/AUX.yaml` | both | Windows reserved name |
| `specs/development/spec_driven/final_specs/spec.md::$DATA` | both | NTFS Alternate Data Stream (AC-5) |
| `specs/development/spec_driven/final_specs/spec.md:hidden` | both | NTFS named ADS |
| `specs/development/spec_driven/__scratch__/_junc/cmd.exe` | Windows-only | NTFS junction (AC-6) |
| `specs/development/spec_driven/__scratch__/_sym/passwd` | POSIX-only | symlink (NFR-5) |
| `specs/development/spec_~1/final_specs/spec.md` | Windows-only | 8.3 short name |

**Assertions.**
- Every probe returns status `404` (single status, FR-3 + FR-4).
- The control path `specs/development/spec_driven/final_specs/spec.md` returns 200.
- No probe results in a 403 / 415 / 200 (would indicate an enumeration side-channel or, worse, a successful sandbox escape — `critical` failure per the development.md severity table).

**Spec refs:** FR-3, FR-4, NFR-4, NFR-5, NFR-12, AC-4, AC-5, AC-6.
**Components exercised:** `safe_resolve` reserved-name check, ADS rejection, reparse-point detection, 8.3-short-name detection (Windows), symlink rejection (POSIX).

---

## SYS-16 — Origin validation: state-changing routes from foreign Origin return 403

**Setup.** `serve_prod` fixture. httpx with explicit `headers={"Origin": "http://evil.example.com", "Host": "127.0.0.1:8765"}`.

**Action.** For each state-changing endpoint, send a request with the foreign Origin and capture status:

| Method + path | Body |
|---|---|
| `PUT /api/file` | `{"path": "specs/development/spec_driven/__scratch__/sys16.md", "content": "x"}` |
| `POST /api/regen-prompt` | `{"project_type": "development", "project_name": "spec_driven", "stages": ["interview"], "modules": {}, "autonomous": false}` |
| `POST /api/promote` | `{"project_type": "development", "project_name": "spec_driven", "stage_folder": "interview", "source_file": "qa.md", "item_id": "test", "item_text": "x"}` |
| `DELETE /api/promote` | `{"project_type": "development", "project_name": "spec_driven", "stage_folder": "interview", "item_id": "test"}` |

Then repeat each request with `Origin: http://127.0.0.1:8765` and `Host: 127.0.0.1:8765` (the legitimate same-origin headers).

**Assertions.**
- Every request with the foreign Origin returns `403` (FR-9, NFR-7, AC-11).
- Every request with the legitimate Origin/Host returns 2xx (200 or 201) — control case proving the endpoint is reachable on legitimate calls.
- A request with a `Host: spec-driven.evil.com` (DNS-rebind probe) returns `403` even when Origin is `http://127.0.0.1:8765` (FR-9 validates BOTH headers).
- `GET /api/file` with a foreign Origin still returns `200` (read endpoints are NOT Origin-validated; FR-9 lists state-changing routes specifically).

**Spec refs:** FR-9, NFR-7, AC-11.
**Components exercised:** Origin/Host middleware, all four state-changing routes.

---

## SYS-17 — `make run` binds to 127.0.0.1 only (NOT 0.0.0.0; LAN IP unreachable)

**Setup.** No prior server. Fresh shell. The host has at least one non-loopback IPv4 address `LAN_IP` (capture via `socket.gethostbyname(socket.gethostname())` or platform-equivalent).

**Action.**
1. Run `make run` in a subprocess (NOT `run-prod`; this asserts the dev target binds correctly too, since both targets feed the FR-38 invariant).
2. Poll `httpx.get("http://127.0.0.1:8765/api/tree")` until 200 (timeout 30 s).
3. Run `httpx.get(f"http://{LAN_IP}:8765/api/tree", timeout=3)` and capture the result (expect connection refused / timeout).
4. Inspect the running process's listening sockets: on Windows, `subprocess.check_output(["netstat", "-ano", "-p", "TCP"])`; on POSIX, `subprocess.check_output(["ss", "-tlnp"])`. Capture rows for port 8765.
5. `grep -ri "0.0.0.0" projects/spec_driven/ --include="*.py" --include="Makefile" --include="*.cfg"` — must return zero matches in default invocation paths.
6. Tear down via `proc.terminate()`.

**Assertions.**
- Step 2: 127.0.0.1 returns 200.
- Step 3: connection to `LAN_IP:8765` fails with `ConnectionError` or `ReadTimeout` (the server is unreachable on the LAN IP, FR-38).
- Step 4: the netstat/ss row for port 8765 shows local address `127.0.0.1:8765` exactly — NOT `0.0.0.0:8765` and NOT `::*` IPv6 wildcard.
- Step 5: zero matches for `0.0.0.0` in the default invocation paths (FR-38, AC-29).

**Spec refs:** FR-38, FR-39, AC-28, AC-29.
**Components exercised:** Uvicorn bind config, Makefile `run` target, `python main.py` entrypoint.

---

## SYS-18 — Verb whitelist: PATCH/DELETE on `/api/file` return 405

**Setup.** `serve_prod` fixture. httpx with legitimate Origin/Host.

**Action.**
1. `PATCH /api/file` with `{"path": "specs/development/spec_driven/__scratch__/sys18.md", "content": "x"}`.
2. `DELETE /api/file?path=specs/development/spec_driven/__scratch__/sys18.md`.
3. `OPTIONS /api/file` (sanity probe).

**Assertions.**
- Step 1: status `405` (NFR-6, AC-12).
- Step 2: status `405` (NFR-6, AC-12).
- Step 3: status `200` or `405` — record but don't assert (CORS preflights are out of scope; the test exists to confirm OPTIONS doesn't accidentally enable mutation).
- The scratch file is NOT created on disk after step 1 (PATCH must not silently write).

**Spec refs:** FR-6, NFR-6, AC-12.
**Components exercised:** verb routing, FastAPI method registration.

---

## SYS-19 — Extension whitelist (FR-3, AC-8) + size cap (FR-3, AC-7)

**Setup.** `serve_prod` fixture. httpx. Fixture writes a 1.5 MB file at `specs/development/spec_driven/__scratch__/big.md` (over the 1 MB cap) and a `.exe` file at `specs/development/spec_driven/__scratch__/blocked.exe` (1 KB).

**Action.**
1. `GET /api/file?path=specs/development/spec_driven/__scratch__/big.md`.
2. `GET /api/file?path=specs/development/spec_driven/__scratch__/blocked.exe`.
3. `GET /api/file?path=specs/development/spec_driven/__scratch__/blocked.svg` (SVG must be blocked, NFR-9).
4. `PUT /api/file` with `{"path": "specs/development/spec_driven/__scratch__/sample.png", "content": "<bytes>"}` — image extensions are NOT writable (FR-8).
5. `PUT /api/file` with body > 1 MB (well above the 1 MB cap, FR-7).
6. `PUT /api/file` with body containing a NUL byte in the first 16 bytes (FR-8 plain-text check).

**Assertions.**
- Step 1: `413` (AC-7).
- Step 2: `415` (AC-8).
- Step 3: `415` (NFR-9).
- Step 4: `415` (FR-8 image extensions not writable).
- Step 5: `413` with `{"detail": {"kind": "too_large"}}` (FR-7, AC-10).
- Step 6: `415` (FR-8 plain-text validation).

**Spec refs:** FR-3, FR-7, FR-8, NFR-9, AC-7, AC-8, AC-10.
**Components exercised:** extension allowlist, size cap (read + write), plain-text body validator.

---

## SYS-20 — Sidebar structural sanity (≥1 leaf under each top-level section, both sections present)

Mandated by `agent_refs/validation/development.md` move #1 ("Concrete requirement: structural sanity assertion: the sidebar contains at least the expected number of leaf rows under each top-level section").

**Setup.** `serve_prod` fixture. Playwright Chromium.

**Action.**
1. `await page.goto("http://127.0.0.1:8765/")`. Wait for `[data-testid="sidebar"]`.
2. Expand all `<details>` under sidebar (recursively click every collapsed expander; or programmatically `await page.evaluate("document.querySelectorAll('[data-testid=sidebar] details').forEach(d => d.open = true)")`).
3. Capture `claude_section = page.locator('[data-testid=sidebar] [data-section="claude"]')`.
4. Capture `projects_section = page.locator('[data-testid=sidebar] [data-section="projects"]')`.

**Assertions.**
- `claude_section.locator('[data-testid="tree-leaf"]').count() >= 1` (CLAUDE.md alone guarantees ≥1, FR-2).
- `projects_section.locator('[data-testid="tree-leaf"]').count() >= 5` (the canonical stage subfolders alone for spec_driven contribute ≥5: revised_prompt, qa.md, dossier.md, spec.md, strategy.md).
- `projects_section.locator('[data-testid="project-link"]').count() >= 1` (the `↗` next to spec_driven, FR-16).
- `consoleErrors == []`.

**Spec refs:** FR-1, FR-2, FR-16, AC-1, AC-28.
**Components exercised:** Sidebar, recursive `<TreeNode>`, EXPOSED_TREE walk.

---

## SYS-21 — Project parent page master Regenerate panel (`/project/development/spec_driven`)

**Setup.** `serve_prod` fixture.

**Action.**
1. `await page.goto("http://127.0.0.1:8765/project/development/spec_driven")`. Wait for the page to render.
2. Capture stage rows: `await page.locator('[data-testid="project-stage"]').count()`.
3. Locate the master Regenerate panel `[data-testid="master-regen"]`.
4. Within the master panel, count module checkboxes per stage.
5. Click `[data-testid="master-regen"] [data-testid="regen-build-button"]`.
6. Wait for `[data-testid="regen-prompt-block"]`.
7. Click `[data-testid="regen-copy-button"]`. Assert label flips to `Copied!` for ~1500 ms then back (AC-24).
8. Toggle `[data-testid="regen-wrap-toggle"]` off; assert the `<pre>` element gets `style*="white-space: pre"` (NOT `pre-wrap`) and re-checking restores `pre-wrap` (AC-25).

**Assertions.**
- Step 2: exactly 6 stage rows (FR-34: "Lists all six stages").
- Step 4: each stage row has ≥1 module checkbox; default-checked (FR-33(a) defaults).
- Step 7: button label is `Copied!` immediately after click; reverts within 2 s; clipboard contents (read via `await page.evaluate("navigator.clipboard.readText()")` — granted via Playwright permission `clipboard-read`) match the rendered prompt's text (AC-24).
- Step 8: wrap-toggle behavior matches FR-33(f); state is NOT persisted to localStorage (assert `localStorage.getItem("spec_driven.wrap.v1")` is `null`, AC-25).
- `consoleErrors == []`.

**Spec refs:** FR-15, FR-33, FR-34, AC-23, AC-24, AC-25, AC-27.
**Components exercised:** project-parent route, master Regenerate panel, Copy button with `aria-live="polite"`, Wrap toggle, breakdown line.

---

## SYS-22 — Broken-link rendering (relative link to non-existent file → muted span, NOT anchor)

**Setup.** `serve_prod` fixture. Fixture writes `specs/development/spec_driven/__scratch__/sys22.md` containing the literal markdown:

```markdown
This is [a broken link](does-not-exist.md) and this is [a real one](../final_specs/spec.md).
```

**Action.**
1. `await page.goto("http://127.0.0.1:8765/file/specs/development/spec_driven/__scratch__/sys22.md")`. Wait for `[data-testid="markdown-view"]`.
2. Locate the broken-link element: `broken = page.locator('[data-testid="markdown-view"] .link-broken')`.
3. Locate the real link: `real = page.locator('[data-testid="markdown-view"] a[href="/file/specs/development/spec_driven/final_specs/spec.md"]')`.

**Assertions.**
- `broken.count() == 1` AND it's a `<span>`, NOT an `<a>` (assert via `await broken.evaluate("e => e.tagName")` returning `"SPAN"`) (FR-24, AC-21).
- `await broken.getAttribute("aria-disabled") == "true"` (FR-24).
- `await broken.getAttribute("title")` is non-empty AND contains `not found` or `outside exposed tree` or `case mismatch` (FR-24 cause taxonomy).
- `real.count() == 1` AND clicking it navigates the SPA (no full reload — assert `page.url` ends with `/final_specs/spec.md` AND `page.locator('[data-testid="markdown-view"]').first.text_content()` contains `# Specification — spec_driven`, FR-23).
- `consoleErrors == []`.

**Spec refs:** FR-23, FR-24, AC-21.
**Components exercised:** MarkdownView link rewriting, broken-link component, SPA navigation.

---

## SYS-23 — Editor save error: persistent inline banner, textarea preserved, button stays focusable

**Setup.** `serve_prod` fixture. Fixture writes a small file at `specs/development/spec_driven/__scratch__/sys23.md` (`baseline\n`). The test forces a save failure by intercepting `PUT /api/file` via Playwright's `route` API to return a 500 once, then succeed on the second call.

**Action.**
1. Navigate to the file. Open editor. Type new content `pending_unsaved_change`.
2. Install `await page.route("**/api/file", lambda route: route.fulfill(status=500, body='{"detail":"forced"}') if route.request.method == "PUT" else route.continue_())` for the FIRST PUT only (using a counter; second PUT lets through).
3. Press Ctrl+S. Wait briefly for the banner to render.
4. Inspect: `[data-testid="editor-error-banner"]` is visible AND its text matches `/^Could not save: .+/` (FR-27).
5. Inspect: textarea content still equals `pending_unsaved_change` (NOT cleared, NOT reverted) (FR-27).
6. Inspect: `[data-testid="editor-save"]` is still focusable (`await page.focus(...)` succeeds) AND not disabled (FR-25).
7. Press Tab to confirm focus order; press Ctrl+S again. The route handler now lets the request through; the save succeeds; the banner disappears; the dirty-dot disappears (FR-26).
8. Out-of-band: `GET /api/file?path=...` returns the new content.

**Assertions.**
- All steps complete; the banner is a real persistent element (NOT a toast / NOT auto-dismissed) — assert it stays visible for at least 5 s while no save is retried.
- After successful retry, the banner is gone.
- The textarea content matches what the user typed across the failure boundary.
- The Save button remained focusable throughout (Tab-focus accessibility).
- `consoleErrors` may include the deliberate 500 "Failed to load resource" — that is expected and allow-listed by this test.

**Spec refs:** FR-25, FR-26, FR-27, FR-28, NFR-14.
**Components exercised:** editor save error path, banner component, focus management.

---

## SYS-24 — Pin survives in regen prompt (`AC-17`)

**Setup.** `serve_prod` fixture. Fixture writes a non-empty `specs/development/spec_driven/interview/promoted.md` with a small distinguishable block, e.g.:

```
## Pin pin-001
Source: qa.md / Round 1 / functional-scope
Body:
This is the pinned answer that MUST appear verbatim.
```

**Action.**
1. `POST /api/regen-prompt` with `{"project_type": "development", "project_name": "spec_driven", "stages": ["interview"], "modules": {"interview": ["qa"]}, "autonomous": false}`.

**Assertions.**
- `resp.status_code == 200`.
- `prompt = resp.json()["prompt"]`.
- `### Pinned items (MUST survive regeneration)` appears in `prompt` AC-17, FR-11(f)).
- The literal string `This is the pinned answer that MUST appear verbatim.` appears in `prompt` verbatim (after newline normalization).
- The Constraints section still includes the read-zero sentence (AC-16).

**Spec refs:** FR-11(f), AC-17, "Pinned items survive regeneration" in CLAUDE.md.
**Components exercised:** regen-prompt assembler's promoted.md inclusion path.

---

## SYS-25 — Autonomous header + verbatim imperative line

**Setup.** `serve_prod` fixture. httpx.

**Action.**
1. `POST /api/regen-prompt` with `{"project_type":"development", "project_name":"spec_driven", "stages":["interview"], "modules":{"interview":[]}, "autonomous": true}`.
2. `POST /api/regen-prompt` with the same body, `autonomous: false`.
3. `POST /api/regen-prompt` with the body OMITTING the `autonomous` field (no header → INTERACTIVE per FR-11(a)).

**Assertions.**
- Step 1 prompt's first line is exactly `# EXECUTION MODE: AUTONOMOUS` AND the next non-blank line is exactly the verbatim sentence: `Do not call AskUserQuestion. For anything unclear, use your best judgment, record the choice inline in the artifact, and keep going. Produce every requested artifact below in this single turn before stopping.` (FR-11(b), AC-14).
- Step 2 prompt's first line is exactly `# EXECUTION MODE: INTERACTIVE` (AC-15) AND the prompt does NOT contain the imperative line (FR-11(b)).
- Step 3 returns either 422 (if the field is required-by-schema) OR a 200 whose prompt opens with `# EXECUTION MODE: INTERACTIVE` (the spec wording is "no header → INTERACTIVE" which implies the server's default is interactive). The accepted contract is one of these two; assert exactly one of them.
- All three responses include `### Constraints` with the read-zero sentence.

**Spec refs:** FR-11, AC-14, AC-15, AC-16.
**Components exercised:** regen-prompt assembler header logic, autonomous-mode body propagation.

---

## SYS-26 — Promotion round-trip (POST → file appended; DELETE → file pruned; other pins untouched)

**Setup.** `serve_prod` fixture. httpx with legitimate Origin/Host. Fixture checkpoints `specs/development/spec_driven/interview/promoted.md` (or notes its absence). Restore on teardown.

**Action.**
1. `POST /api/promote` `{project_type:"development", project_name:"spec_driven", stage_folder:"interview", source_file:"qa.md", item_id:"sys26-a", item_text:"Pin A body."}`.
2. `POST /api/promote` `{...item_id:"sys26-b", item_text:"Pin B body."}`.
3. Read the file via `GET /api/file?path=specs/development/spec_driven/interview/promoted.md`.
4. `DELETE /api/promote` `{...item_id:"sys26-a"}`.
5. Re-read the file.
6. `POST /api/promote` with `stage_folder:"projects"` (NOT in the allowed list).

**Assertions.**
- Step 3: response 200; content contains both `Pin A body.` and `Pin B body.`.
- Step 4: response 200/204.
- Step 5: content contains `Pin B body.` but NOT `Pin A body.` (FR-14: "Other pins are untouched").
- Step 6: response 4xx (likely 400 or 422); the file is unchanged (FR-13: stage 6 / non-canonical stage_folder is rejected).

**Spec refs:** FR-13, FR-14, FR-37.
**Components exercised:** `POST /api/promote`, `DELETE /api/promote`, the promoted.md parse/serialize path in `libs/promotions.py`.

---

## SYS-27 — Initial app load latency (NFR-3 budget: <2 s on localhost)

**Setup.** `serve_prod` fixture. Browser cache cleared via fresh Playwright context. Network not throttled.

**Action.**
1. `t0 = time.perf_counter()`.
2. `await page.goto("http://127.0.0.1:8765/", wait_until="networkidle")`.
3. Wait for `[data-testid="sidebar"]` and at least one `[data-testid="tree-leaf"]` to be visible.
4. `dt = time.perf_counter() - t0`.

**Assertions.**
- `dt < 2.0` (NFR-3). Soft-fail: emit a `validation.warning` event but do NOT halt if 2.0 ≤ dt < 3.0; hard-fail at dt ≥ 3.0.
- HTML-document load + first `/api/tree` + first `/api/file` requests all completed (assert via Playwright's network-event listener captured during `goto`).
- `consoleErrors == []`.

**Spec refs:** NFR-1, NFR-2, NFR-3.
**Components exercised:** the entire boot path, exercised under timing.

---

## Coverage matrix

| Coverage area | SYS-NN |
|---|---|
| Boot smoke (move #4) | SYS-1 |
| MarkdownView render | SYS-2 |
| QaView render | SYS-3 |
| JsonlView render | SYS-4 |
| CodeView render | SYS-5 |
| ImagePlaceholder render | SYS-6 |
| File editor save round-trip | SYS-7 |
| Per-Q inline edit on qa.md | SYS-8 |
| Regen-prompt small | SYS-9 |
| Regen-prompt medium (warning banner) | SYS-10 |
| Regen-prompt large (413, no block) | SYS-11 |
| Autonomous toggle + cross-tab `storage` | SYS-12 |
| QaView Error Boundary fallback | SYS-13 |
| Path-traversal probes (single 404) | SYS-14 |
| Junctions / ADS / reserved names (single 404) | SYS-15 |
| Origin validation (foreign → 403) | SYS-16 |
| `make run` binds 127.0.0.1 only | SYS-17 |
| Verb whitelist (PATCH/DELETE → 405) | SYS-18 |
| Extension allowlist + size caps | SYS-19 |
| Sidebar structural sanity | SYS-20 |
| Project parent page + master Regenerate | SYS-21 |
| Broken-link span rendering | SYS-22 |
| Editor save error banner persistence | SYS-23 |
| Pin survives in regen prompt | SYS-24 |
| Autonomous header + imperative line | SYS-25 |
| Promotion round-trip | SYS-26 |
| Initial-load latency budget | SYS-27 |

Total: **27** SYS-NN scenarios (≥20 required).

## Make targets

- `make e2e` — runs every Playwright scenario (SYS-2..SYS-8, SYS-10..SYS-13, SYS-20..SYS-23, SYS-27). Wraps `pytest tests/system/ -m e2e --browser chromium`.
- `make test-backend` — runs every httpx scenario (SYS-1, SYS-9, SYS-11 [API half], SYS-14..SYS-19, SYS-24..SYS-26). Wraps `pytest tests/system/ -m api`.
- `make boot-smoke` — just SYS-1; runs first on every CI invocation. Failure is `critical`, halts immediately, no revision rounds (`agent_refs/validation/development.md` move #4).
- `make e2e-headed` — `make e2e` with `--headed --slowmo=300` for debugging.

## Cross-platform handling summary

| Test | Windows | POSIX |
|---|---|---|
| SYS-15 junction probe | Run | Skip with `skipif sys.platform != "win32"` |
| SYS-15 symlink probe | Skip with `skipif sys.platform == "win32"` | Run |
| SYS-15 8.3 short-name probe | Run | Skip |
| SYS-17 netstat | `netstat -ano -p TCP` | `ss -tlnp` |
| All others | Run | Run |

## Manual walkthrough trigger

After all automated SYS-NN pass, runtime validation MUST emit a `validation.requires_manual_walkthrough` event listing the visual-only checks not exercised by Playwright: visual hierarchy of the QaView Q vs A tints, color contrast on the regen-prompt-block dark theme (NFR-16), focus visibility through the editor (NFR-14, NFR-15), motion/transition feel of the Copy button label flip (AC-24), and overall navigation rhythm. The skill surfaces this event to the user before declaring stage 6 complete (`agent_refs/validation/development.md` move #7).
