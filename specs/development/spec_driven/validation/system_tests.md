# System Tests — spec_driven

Run: spec_driven-20260502-clean
Stage: 5 (Validation strategy — system_tests level)
Source spec: `specs/development/spec_driven/final_specs/spec.md`
Inputs read: spec.md only (read-zero).

End-to-end scenarios driving the live FastAPI backend, the built React bundle (or Vite dev server), the filesystem under REPO_ROOT, and a Chromium browser.

---

## SYS-01 — `make run` build + serve happy path

Setup:
1. Clean working tree at `projects/spec_driven/` with `backend/`, `frontend/`, and `Makefile` present.
2. `make install` previously executed (Python deps synced, `frontend/node_modules/` populated).
3. `backend/static/` removed if present so the build is fresh.
4. No process listening on port 8765.

Action:
1. From `projects/spec_driven/` run `make run` and capture stdout/stderr.
2. Wait until the Vite build emits `built in <t>ms` and Uvicorn logs `Application startup complete.` on `http://127.0.0.1:8765`.
3. Issue `GET http://127.0.0.1:8765/` with a Playwright Chromium context.
4. Issue `GET http://127.0.0.1:8765/api/tree`.
5. Send SIGTERM (or `Ctrl+C` equivalent) to the FastAPI process.

Assertions:
1. `backend/static/index.html` exists and references hashed JS/CSS bundles (`assets/index-*.js`).
2. `GET /` returns HTTP 200 and a body containing `<div id="root">` (the React shell).
3. The browser, after settling, lands on URL `/file/specs/development/spec_driven/final_specs/spec.md`.
4. `GET /api/tree` returns 200 with `application/json` and a top-level shape `{settings: {claude_md, agents, skills}, projects: [...]}`.
5. The process bound exactly one socket on `127.0.0.1:8765` (verified via `psutil.Process.connections()` or `netstat`).
6. Process exits cleanly (return code 0 or signal-terminated) after SIGTERM.

Spec refs: FR-11, FR-12, FR-13 (`make run`), FR-15, NFR-3, NFR-7, AC-1, AC-24.
Components exercised: `backend/main.py`, `backend/libs/api.py` (tree + root redirect), `frontend/src/routes.tsx`, `frontend/src/api.ts`, `Makefile`.

---

## SYS-02 — `make dev` two-process happy path

Setup:
1. Working tree as in SYS-01 with `make install` already run.
2. No process on port 8765 (FastAPI) and no process on port 5173 (Vite default).
3. `frontend/vite.config.ts` proxies `/api` to `http://127.0.0.1:8765`.

Action:
1. Run `make dev` in a subshell that captures both child PIDs.
2. Wait for both Uvicorn (`Application startup complete`) and Vite (`Local: http://localhost:5173/`) banners.
3. Open Playwright at `http://127.0.0.1:5173/`.
4. Issue `GET /api/tree` from inside the Vite dev origin (browser fetch via the page).
5. Touch `backend/libs/api.py` (append a comment) and observe that Uvicorn `--reload` restarts.
6. SIGTERM the parent `make` process.

Assertions:
1. Two distinct child PIDs are alive after step 2 (FastAPI + Vite).
2. Page at `:5173/` renders the React shell and routes to the default file.
3. `/api/tree` proxied through Vite returns the same JSON shape as in SYS-01 (200 + `settings` + `projects`).
4. Uvicorn re-emits the `Application startup complete` banner after the file touch.
5. Both child processes terminate within 5 seconds of the parent SIGTERM.

Spec refs: FR-13 (`make dev`), FR-15.
Components exercised: `Makefile`, `backend/main.py`, `frontend/vite.config.ts`, `frontend/src/api.ts`.

---

## SYS-03 — `SPEC_DRIVEN_PORT` override + unavailable-port exit

Setup:
1. As in SYS-01.
2. A separate sentinel TCP listener occupies port 9090 (e.g., a Python socket bound on `127.0.0.1:9090`) for the unavailable-port subcase.

Action:
1. **Override case:** with port 9090 free, run `SPEC_DRIVEN_PORT=9090 make run`. Wait for startup. `GET http://127.0.0.1:9090/api/tree`. Stop the process.
2. **Conflict case:** start the sentinel listener on 9090. Run `SPEC_DRIVEN_PORT=9090 make run`. Capture exit code, stdout, and stderr.
3. **Default case:** unset `SPEC_DRIVEN_PORT`, ensure 8765 is free, run `make run`, confirm port 8765 is bound.

Assertions:
1. Override case: `/api/tree` on `:9090` returns 200; no listener appears on `:8765`.
2. Conflict case: process exits with non-zero code within 5 seconds; stderr contains a clear error message naming the port (e.g., "port 9090 unavailable") and not a raw Python traceback.
3. Default case: process binds `:8765` exactly when `SPEC_DRIVEN_PORT` is absent.

Spec refs: FR-12, AC-27.
Components exercised: `backend/main.py` (port resolution + bind error handling).

---

## SYS-04 — `REPO_ROOT` walk-upward + failure mode

Setup:
1. Two test workspaces:
   - **A (valid repo):** mirrors the real layout — contains `CLAUDE.md`, `specs/`, and `.claude/` at the root, with `projects/spec_driven/backend/main.py` somewhere below.
   - **B (no repo):** an empty temp directory with no `CLAUDE.md`, `specs/`, or `.claude/`.
2. Two copies of `backend/` are placed: one at `A/projects/spec_driven/backend/`, one at `B/somewhere/backend/`.

Action:
1. Run `python -m projects.spec_driven.backend.main` (or equivalent entry) from inside workspace A. Inspect logs for the resolved `REPO_ROOT`.
2. Hit `GET /api/tree`; verify it walks the A repo's `specs/`.
3. Stop, then re-run the same entry from inside workspace B.
4. Capture exit code and stderr from the B invocation.

Assertions:
1. In A, the resolved `REPO_ROOT` matches workspace A's absolute root path (logged or surfaced via a debug endpoint / log line).
2. `/api/tree` in A enumerates entries that resolve under `A/`, never under `B/`.
3. In B, the process exits non-zero within 2 seconds.
4. B's stderr names the missing markers (`CLAUDE.md`, `specs/`, `.claude/`) and instructs the user to run from inside the spec_coding repo.

Spec refs: FR-2, AC-26.
Components exercised: `backend/main.py`, `backend/libs/api.py` (REPO_ROOT discovery).

---

## SYS-05 — `/` → final_specs/spec.md redirect with revised_prompt.md fallback

Setup:
1. Backend running per SYS-01 against a controlled fixture repo where:
   - **Subcase A:** `specs/development/spec_driven/final_specs/spec.md` exists.
   - **Subcase B:** `final_specs/spec.md` is renamed away; `specs/development/spec_driven/user_input/revised_prompt.md` exists.
   - **Subcase C:** both files removed; only `raw_prompt.md` exists under `user_input/`.

Action:
1. Open Playwright at `http://127.0.0.1:8765/` for each subcase in turn (with a fresh browser context to clear `localStorage`).
2. Wait for the URL bar and main pane to settle.
3. Press the browser's Back button.

Assertions:
1. Subcase A: final URL is `/file/specs/development/spec_driven/final_specs/spec.md`; the rendered pane shows the spec's `# Spec — spec_driven` heading.
2. Subcase B: final URL is `/file/specs/development/spec_driven/user_input/revised_prompt.md`; the pane renders that file.
3. Subcase C: pane shows a muted "no files yet" / equivalent message; URL falls back to the user_input folder route per FR-16.
4. The redirect uses `replaceHistory` — pressing Back from `/file/...` does NOT return to `/`, it leaves the spec_driven origin.

Spec refs: FR-15, FR-16, FR-17, AC-1.
Components exercised: `frontend/src/routes.tsx`, `frontend/src/api.ts`, `backend/libs/api.py` (`/api/tree`, `/api/file`).

---

## SYS-06 — Path traversal blocked across encodings

Setup:
1. Backend running per SYS-01.
2. A canary file outside REPO_ROOT (e.g., on Linux `/etc/hosts`, on Windows `C:/Windows/System32/drivers/etc/hosts`) is readable by the backend process but MUST NOT be served.

Action:
1. For each attack vector, issue `GET /api/file?path=<vector>` and capture status, JSON body:
   - `../../../etc/hosts` (raw dot-dot)
   - `..%2F..%2F..%2Fetc%2Fhosts` (percent-encoded slashes)
   - `%2E%2E%2F%2E%2E%2F%2E%2E%2Fetc%2Fhosts` (percent-encoded dots and slashes)
   - `%252E%252E%252Fetc%252Fhosts` (double-encoded)
   - `..\\..\\..\\Windows\\System32\\drivers\\etc\\hosts` (mixed backslash)
   - `specs/development/spec_driven/../../../../CLAUDE.md` (unicode-normalized embedded dot-dot)
   - `/etc/hosts` (absolute path)
   - `C:/Windows/System32/drivers/etc/hosts` (absolute Windows path)
2. Repeat each vector against `PUT /api/file` with a small JSON body.

Assertions:
1. Every GET returns HTTP 400 with JSON body `{"detail": {"kind": "outside_sandbox", ...}}` (or 404 `outside_exposed_tree` if the resolved path lands inside REPO_ROOT but outside EXPOSED_TREE).
2. None of the responses leak file contents from the canary file (assert response body length and that no `127.0.0.1` line / hosts-file marker appears).
3. PUT vectors return the same 400 / 404 shape; the canary file's mtime is unchanged after the test run.
4. `safe_resolve` is invoked exactly once per request (verifiable via a code-review check / pytest spy in the unit-test layer; system layer asserts no double-decoding by sending `path=foo%2520.md` and observing the literal `%20` is NOT stripped).

Spec refs: FR-5, FR-6, AC-7, NFR-4.
Components exercised: `backend/libs/api.py` (`safe_resolve`, `GET /api/file`, `PUT /api/file`).

---

## SYS-07 — Symlink rejection (with Windows skip-test condition)

STATUS=SKIPPED-WINDOWS-NO-DEVELOPER-MODE: This scenario REQUIRES symlink-create privileges. On Windows hosts without Developer Mode enabled or the `SeCreateSymbolicLinkPrivilege`, the test runner MUST skip with a `pytest.skip("requires symlink privilege")` and emit a CI warning. The CI matrix runs this test on Linux + macOS unconditionally and on Windows only when the privilege is available.

Setup:
1. Backend running per SYS-01.
2. Inside `specs/development/spec_driven/findings/`, create symlinks:
   - `symlink_to_outside.md` → `/etc/hosts` (or Windows equivalent canary).
   - `symlink_to_inside.md` → `final_specs/spec.md` (still inside EXPOSED_TREE).
3. Inside `specs/development/spec_driven/`, create a directory symlink `link_dir/` → `final_specs/`.

Action:
1. `GET /api/tree` and inspect whether the symlink leaves appear.
2. `GET /api/file?path=specs/development/spec_driven/findings/symlink_to_outside.md`.
3. `GET /api/file?path=specs/development/spec_driven/findings/symlink_to_inside.md`.
4. `GET /api/file?path=specs/development/spec_driven/link_dir/spec.md`.
5. `PUT /api/file` against each of the three symlink paths.

Assertions:
1. The tree response does NOT include any of the three symlink entries (silently skipped per FR-4).
2. Step 2 returns 400 `outside_sandbox`.
3. Step 3 returns 400 `outside_sandbox` even though the target lives inside EXPOSED_TREE (FR-5.2 / NFR-5).
4. Step 4 returns 400 `outside_sandbox` because a parent segment is a symlink.
5. PUT against any symlink returns 400 with no write occurring (target file mtime unchanged).

Spec refs: FR-4, FR-5.2, FR-14a, NFR-5.
Components exercised: `backend/libs/api.py` (tree walker, `safe_resolve`, file endpoints).

---

## SYS-08 — `127.0.0.1` bind verification (not `0.0.0.0`)

Setup:
1. Backend started with `make run` on the default port 8765.
2. A second host on the LAN (or a docker container with a separate IP) reachable from the dev machine.

STATUS=SKIPPED-NO-SECOND-HOST when the CI environment cannot route from a non-loopback IP to the host running uvicorn. Tests fall back to a local check (assertion 3) only.

Action:
1. From the same machine: `curl http://127.0.0.1:8765/api/tree`.
2. From the same machine: `curl http://<host-LAN-ip>:8765/api/tree` (where `<host-LAN-ip>` is the dev machine's LAN address, distinct from 127.0.0.1).
3. Inspect the bound socket via `psutil.net_connections()` filtered to PID, OR run `netstat -an | grep 8765`.

Assertions:
1. Step 1 returns HTTP 200 with the tree JSON.
2. Step 2 fails with connection-refused (not "no route") — confirming the listener never accepted the LAN-address connection.
3. The bound local address for the listening socket is exactly `127.0.0.1:8765` (NOT `0.0.0.0:8765` and NOT `::`/`*`).

Spec refs: FR-12, NFR-7, AC-24.
Components exercised: `backend/main.py` (uvicorn host arg).

---

## SYS-09 — No CORS wildcard

Setup:
1. Backend running per SYS-01.
2. A second origin `http://localhost:9999/` serving a tiny static page that fetches `/api/tree` cross-origin.

Action:
1. From a curl, send `GET /api/tree` with header `Origin: http://evil.example.com`. Capture all response headers.
2. From the second origin (`:9999`), open a page in Playwright that runs `await fetch('http://127.0.0.1:8765/api/tree', {credentials:'omit'})`. Capture network panel response headers + JS-side success/failure.
3. Send `OPTIONS /api/file?path=CLAUDE.md` with `Origin: http://evil.example.com` and `Access-Control-Request-Method: PUT`. Capture status and headers.

Assertions:
1. The response from step 1 contains NO `Access-Control-Allow-Origin: *` header. It SHOULD contain no `Access-Control-Allow-Origin` header at all.
2. The cross-origin fetch in step 2 fails the browser CORS check (the page-side promise rejects with a `TypeError`); no JSON body is observable to the cross-origin script.
3. Step 3 returns either 405 or 400 — not a permissive 200 with CORS allow headers. No `Access-Control-Allow-Methods` listing PUT is emitted.

Spec refs: NFR-8, AC-25.
Components exercised: `backend/main.py` (no `CORSMiddleware`), `backend/libs/api.py`.

---

## SYS-10 — GET-only API + sanctioned PUT/POST endpoints

Setup:
1. Backend running per SYS-01.
2. A small writable test file at `specs/development/spec_driven/user_input/raw_prompt.md` (snapshot the original bytes for restoration).

Action:
1. For each verb in `{GET, HEAD, OPTIONS, POST, PUT, PATCH, DELETE}`, send a request to `/api/file?path=specs/development/spec_driven/user_input/raw_prompt.md`. Use a 1-byte JSON body where required by the verb.
2. Send `POST /api/regen-prompt` with a minimal valid body.
3. Send `PATCH /api/regen-prompt` and `DELETE /api/regen-prompt`.
4. Send `POST /api/tree` (read-only endpoint should reject writes).
5. Restore the test file from the snapshot.

Assertions:
1. `GET /api/file` → 200 with the file body.
2. `PUT /api/file` (with valid JSON `{path, text}`) → 200; file content updated.
3. `PATCH /api/file` and `DELETE /api/file` → 405 with an `Allow:` header listing only sanctioned verbs.
4. `POST /api/file` (no FR sanction) → 405 or 404.
5. `POST /api/regen-prompt` (valid body) → 200 with the documented response shape.
6. `PATCH` and `DELETE` against `/api/regen-prompt` → 405.
7. `POST /api/tree` → 405 with `Allow: GET`.
8. No file is created, removed, or otherwise mutated outside the explicitly-tested PUT.

Spec refs: NFR-6, FR-14a, FR-14c, AC-23.
Components exercised: `backend/libs/api.py` (route registration, method whitelist).

---

## SYS-11 — Dogfood self-render

Setup:
1. Backend running per SYS-01 against the real spec_coding repo (this repo).
2. Playwright Chromium context with cleared `localStorage`.

Action:
1. Open `http://127.0.0.1:8765/`.
2. For each of the five stages of `development/spec_driven`, click the stage subfolder in the sidebar; observe the auto-redirect (FR-16) to the first file.
3. Capture the rendered page text and the URL after each click.
4. Click `CLAUDE.md` under `Settings & Shared Context > CLAUDE.md`.
5. Click each entry under `Agents` (3 expected: `agent_team__interview_manager.md`, `agent_team__research_manager.md`, `agent_team__validation_manager.md`).
6. Click each entry under `Skills` (at least `agent_team`).

Assertions:
1. Initial render shows `# Spec — spec_driven` with a parsed H1 (`<h1>` with id `spec-spec_driven` per FR-30).
2. Each of the five stage clicks lands on a real file route; rendered pane contains a non-empty `<article>` / markdown body.
3. URL after each stage click matches `/file/specs/development/spec_driven/{stage}/<first-file>`.
4. CLAUDE.md renders with at least one `<h1>` and Shiki-highlighted code blocks for the fenced examples.
5. Every agent file renders without a 404 banner; breadcrumb shows `Settings / Agents / <filename>`.
6. Every skill file renders without a 404 banner; breadcrumb shows `Settings / Skills / <folder>`.

Spec refs: FR-3, FR-7, FR-15, FR-16, FR-21, FR-29, FR-30, FR-31, FR-37, AC-1, AC-2, AC-3.
Components exercised: `backend/libs/api.py` (`/api/tree`, `/api/file`), `frontend/src/components/Sidebar.tsx`, `frontend/src/components/Reader.tsx`.

---

## SYS-12 — Cross-link + browser back-button

Setup:
1. Backend running with a fixture spec at `specs/development/spec_driven/final_specs/spec.md` containing this exact relative link in the body:
   ```
   See [the dossier](../findings/dossier.md) for details.
   ```
2. `specs/development/spec_driven/findings/dossier.md` exists.

Action:
1. Open `http://127.0.0.1:8765/file/specs/development/spec_driven/final_specs/spec.md`.
2. Click the `the dossier` link.
3. After the navigation, press the browser Back button.
4. Press Forward.

Assertions:
1. After step 2, the URL is `/file/specs/development/spec_driven/findings/dossier.md` (push-history entry, not a full page load — assert via Playwright's `page.evaluate(() => performance.getEntriesByType('navigation').length)` staying at 1).
2. The link rendered is an `<a>` (not a broken span) and the click DID NOT open a new tab.
3. After step 3 (Back), URL returns to `final_specs/spec.md` and the spec heading re-renders.
4. After step 4 (Forward), URL returns to `findings/dossier.md`.
5. `aria-selected="true"` follows the URL on each navigation (assert sidebar state).

Spec refs: FR-17, FR-33 case 3, FR-38, AC-4.
Components exercised: `frontend/src/routes.tsx`, `frontend/src/components/Reader.tsx` (link resolver), `frontend/src/components/Sidebar.tsx`.

---

## SYS-13 — Folder-only-URL replace-history redirect

Setup:
1. Backend running. `specs/development/spec_driven/findings/` contains at least `angle-business.md` and `dossier.md`.
2. Empty fixture: `specs/development/spec_driven/validation/` exists but contains zero files.

Action:
1. Manually navigate to `http://127.0.0.1:8765/file/specs/development/spec_driven/findings/` (trailing slash, folder URL).
2. Observe the redirect.
3. Press Back.
4. Manually navigate to `http://127.0.0.1:8765/file/specs/development/spec_driven/validation/`.
5. Observe behavior.

Assertions:
1. Step 2: URL replaces to `/file/specs/development/spec_driven/findings/angle-business.md` (alphabetical first per FR-8) within 500 ms.
2. The redirect uses `replaceHistory` — pressing Back does NOT cycle through the folder URL; it goes directly to the previous entry (or leaves the page if there was none).
3. Step 5: pane shows a muted "no files yet" / equivalent message; URL stays on the folder URL (or replaces to a sentinel) without crashing the app.

Spec refs: FR-8, FR-16, FR-17.
Components exercised: `frontend/src/routes.tsx`, `frontend/src/components/Reader.tsx`.

---

## SYS-14 — Refresh after external write

Setup:
1. Backend running. Open Playwright at `http://127.0.0.1:8765/`.
2. Note the rendered sidebar entries under `findings/` (snapshot the list).

Action:
1. From a separate shell, `touch specs/development/spec_driven/findings/angle-late-add.md` AND write a small markdown body to it.
2. WITHOUT clicking refresh, observe the sidebar — confirm it still shows the snapshot list.
3. Click the Refresh button at the top of the sidebar.
4. Click the new entry once it appears.
5. From the shell, delete `angle-late-add.md`.
6. Click Refresh again.

Assertions:
1. Step 2: sidebar entries unchanged (no auto-refresh — confirms FR's no-watcher rule).
2. After step 3 click, `GET /api/tree` is re-issued (assert via Playwright network log) and the new file appears in the tree.
3. Step 4: clicking the new entry navigates to its URL and renders the body.
4. After step 6, the entry is gone from the sidebar and `aria-selected` no longer points to it.

Spec refs: FR-3, FR-28, AC-12.
Components exercised: `backend/libs/api.py` (`/api/tree`), `frontend/src/components/Sidebar.tsx`, `frontend/src/api.ts`.

---

## SYS-15 — Stale-tree click inline refresh

Setup:
1. Backend running. Open Playwright.
2. Sidebar shows `specs/development/spec_driven/findings/angle-tmp.md`.
3. The frontend has the tree cached in memory (post-initial-load).

Action:
1. From a shell, delete `angle-tmp.md`.
2. In the browser (without clicking sidebar Refresh), click the `angle-tmp.md` entry.
3. Observe the main pane.
4. Click the inline Refresh affordance shown in the pane.

Assertions:
1. Step 2 triggers `GET /api/file?path=...`, which returns 404 with `kind: "file_removed"`.
2. The main pane renders an inline non-modal message "this file no longer exists — refresh sidebar" using the same broken-link visual component as FR-34.
3. The message includes a clickable Refresh affordance.
4. Step 4 re-fetches `/api/tree`; the stale entry disappears from the sidebar.
5. URL remains on the now-broken path until the user clicks something else (no auto-redirect).

Spec refs: FR-5.7, FR-28, FR-34, AC-15.
Components exercised: `backend/libs/api.py` (`/api/file`), `frontend/src/components/Reader.tsx`, `frontend/src/components/Sidebar.tsx`.

---

## SYS-16 — Concurrent-write tolerance (mid-write read)

Setup:
1. Backend running.
2. A test fixture at `specs/development/spec_driven/findings/big.md` of ~400 KB.

Action:
1. Spawn a background goroutine/thread that, in a tight loop, opens `big.md`, truncates it, writes ~400 KB of content, and closes — repeated for 10 seconds.
2. In parallel (5 concurrent client coroutines), issue 200 `GET /api/file?path=specs/development/spec_driven/findings/big.md` against the backend.
3. Also issue 50 `GET /api/tree` requests concurrently to walk the same area.
4. Stop the writer after 10 seconds.
5. Final read.

Assertions:
1. Of the 200 file GETs, every response is one of: 200 with valid UTF-8 text, 404 `file_removed`, or 415 `binary_content` (if the truncate-and-write window momentarily yields a NUL byte). NEVER a 5xx.
2. All 50 tree responses return 200 with valid JSON; the entry appears or disappears but the response shape is always valid.
3. Final read after step 4 returns 200 with the writer's last fully-written content.

Spec refs: FR-3, FR-5.7, NFR-12, AC-15.
Components exercised: `backend/libs/api.py` (`/api/file`, `/api/tree`).

---

## SYS-17 — Session restore on reload (sidebar + URL)

Setup:
1. Backend running. Playwright with a persistent storage state file.
2. Initial state: localStorage cleared.

Action:
1. Open `http://127.0.0.1:8765/`. Wait for initial redirect.
2. Click `Projects > development > spec_driven > findings > dossier.md`.
3. Expand the `Settings & Shared Context > Agents` subgroup; collapse the `final_specs` stage.
4. Inspect `localStorage['spec_driven.sidebar.v1']`; it should now contain expand/collapse state and last-selected file.
5. Reload the page (full browser reload).
6. Manually navigate to `http://127.0.0.1:8765/file/specs/development/spec_driven/interview/qa.md` (URL takes precedence over saved last-selected).
7. Reload again.
8. Corrupt `localStorage['spec_driven.sidebar.v1']` to literal string `"{not json"`. Reload.

Assertions:
1. After step 5, the sidebar is in the same expand/collapse state as before reload AND `aria-selected` is on `dossier.md`. URL is `/file/.../findings/dossier.md`.
2. After step 7, URL is on `qa.md`; sidebar selected entry is `qa.md`, NOT the previously-saved `dossier.md`.
3. After step 8, the app loads with default expand/collapse state, no thrown error in the console (assert via `page.on('pageerror', ...)` capturing zero entries).

Spec refs: FR-22, FR-23, AC-13.
Components exercised: `frontend/src/components/Sidebar.tsx`, `frontend/src/routes.tsx`, localStorage logic in `frontend/src/api.ts` or a sidebar state module.

---

## SYS-18 — Section 1 navigation (CLAUDE.md, every agent, every skill)

Setup:
1. Backend running against the real repo. Verify counts: `CLAUDE.md` exists; `.claude/agents/*.md` count = 3; `.claude/skills/*/SKILL.md` count >= 1.

Action:
1. Open Playwright at `/`. Wait for sidebar to populate.
2. For `CLAUDE.md`: click the entry; capture URL + first H1.
3. For each entry in `Agents` (iterate Playwright locator `[role="treeitem"][aria-level="3"]` under the Agents group): click; capture URL + first H1; press Back.
4. For each entry in `Skills`: click; capture URL + first H1; press Back.
5. Issue `GET /api/tree` and compare counts against the visible sidebar.

Assertions:
1. CLAUDE.md click → URL `/file/CLAUDE.md`; rendered pane shows the file's first H1.
2. Each agent click → URL `/file/.claude/agents/<file>.md`; pane renders without 404 / broken-link banner.
3. Each skill click → URL `/file/.claude/skills/<folder>/SKILL.md`.
4. Tree response's `settings.agents` length === count of clickable agent entries; same for `settings.skills`.
5. Each agent and skill leaf has `role="treeitem"` and a focusable element with the correct `aria-level` (3 = leaf under a group under Section 1).

Spec refs: FR-1, FR-7, FR-21, FR-37, AC-3.
Components exercised: `backend/libs/api.py` (`/api/tree`), `frontend/src/components/Sidebar.tsx`, `frontend/src/components/Reader.tsx`.

---

## SYS-19 — Image placeholder + non-image-bytes rejection

Setup:
1. Backend running. Fixture markdown at `specs/development/spec_driven/findings/with-images.md` containing:
   ```
   Internal: ![diagram alt text](./diagram.png)
   External: ![remote](https://example.com/x.png)
   ```
2. A real `diagram.png` (1×1 PNG, ~70 bytes) sits next to the markdown file inside EXPOSED_TREE.

Action:
1. Open `/file/specs/development/spec_driven/findings/with-images.md`.
2. Inspect the rendered DOM for the two image directives.
3. Hover the internal image placeholder; capture the tooltip.
4. Issue `GET /api/file?path=specs/development/spec_driven/findings/diagram.png`.
5. Issue `GET /api/file?path=specs/development/spec_driven/findings/diagram.bin` (a fake binary file with NUL bytes).

Assertions:
1. The internal image renders as `<span class="image-placeholder" title="v1: images not rendered">diagram alt text</span>` — NO `<img>` element with `src` pointing at `/api/file`.
2. The external image renders as a real `<img src="https://example.com/x.png">` (no proxying, no placeholder).
3. The tooltip on hover reads exactly `v1: images not rendered`.
4. Step 4 returns HTTP 415 with body `{"detail": {"kind": "unsupported_extension", ...}}`.
5. Step 5 returns 415 either as `unsupported_extension` (if `.bin` not whitelisted) or as `binary_content` (if served and detected) — never 200 with raw bytes.

Spec refs: FR-5.4, FR-5.6, FR-36, AC-8, AC-9, NFR-13.
Components exercised: `backend/libs/api.py` (`/api/file`), `frontend/src/components/Reader.tsx` (markdown image transformer).

---

## SYS-20 — JSONL render (well-formed + malformed + blank line)

Setup:
1. Backend running. Fixture `specs/development/spec_driven/validation/example.jsonl` containing exactly these 5 lines:
   ```
   {"event":"validation.started","ts":"2026-05-02T00:00:00Z"}

   {"event":"validation.pass","unit":"u1"}
   {"event": this is not json
   {"event":"exec.unit.completed","unit":"u1","ms":42}
   ```
   (Line 2 blank, line 4 malformed.)

Action:
1. Open `/file/specs/development/spec_driven/validation/example.jsonl`.
2. Inspect the rendered DOM.
3. Count the rendered Shiki blocks.
4. Locate the malformed line in the DOM.

Assertions:
1. Exactly 3 Shiki-highlighted JSON blocks render (one per well-formed line); blank line is skipped (FR-32).
2. The malformed line renders as plain monospace text (no Shiki highlight tokens), with the raw original text intact, including the partial `{"event":` prefix.
3. Each well-formed JSON block has correct token highlighting (string vs number vs key) — assert by selecting `.token.property` / `.token.string` Shiki classes.
4. No 5xx thrown; the page settles in under NFR-2's 100 ms file-read budget for the 200-byte fixture.

Spec refs: FR-32.
Components exercised: `frontend/src/components/Reader.tsx` (jsonl renderer).

---

## SYS-21 — Editor round-trip: ✎ Edit → type → Ctrl+S → 200 → file equals new text

Setup:
1. Backend running.
2. Fixture markdown at `specs/development/spec_driven/findings/edit-me.md` with body `# Original\n` (snapshot).

Action:
1. Open `/file/specs/development/spec_driven/findings/edit-me.md`.
2. Click the ✎ Edit button.
3. Confirm the rendered pane swaps for a textarea preloaded with `# Original\n`. Save button is disabled.
4. Type ` (edited)` after `# Original`. Observe the dirty-dot lights up and "Unsaved changes" badge appears. Save becomes enabled.
5. Press Ctrl+S.
6. Capture the network call, the in-app feedback, and finally read the file from disk via the shell.
7. Restore the file from the snapshot.

Assertions:
1. After step 3, textarea content === `# Original\n` and Save is `disabled`.
2. After step 4, the dirty-dot has class indicating filled state (`.dirty-dot[data-dirty="true"]` or equivalent), the "Unsaved changes" element is in the DOM, and Save is enabled.
3. Step 5 triggers exactly one `PUT /api/file` with JSON body `{"path":"specs/development/spec_driven/findings/edit-me.md","text":"# Original (edited)\n"}`.
4. Response is 200; aria-live region announces "Saved.".
5. Dirty-dot is cleared (`data-dirty="false"`); editor remains in edit mode (per FR-40 closing is explicit).
6. On-disk content of the file is exactly `# Original (edited)\n`.

Spec refs: FR-14a, FR-40, AC-16.
Components exercised: `backend/libs/api.py` (`PUT /api/file`), `frontend/src/components/Editor.tsx`, `frontend/src/api.ts`, atomic-write helper in `backend/libs/file_writer.py`.

---

## SYS-22 — Editor save failure: stub PUT to fail → persistent banner appears, dirty stays lit

Setup:
1. Backend running, but with a route override (test-mode flag or Playwright route interception) that makes `PUT /api/file` for path `specs/development/spec_driven/findings/edit-me.md` always return `415 {"detail": {"kind": "unsupported_extension"}}`.
2. Fixture file as in SYS-21.

Action:
1. Open the fixture, click ✎ Edit, type a change.
2. Press Ctrl+S.
3. Observe the response and the resulting UI.
4. Wait 5 seconds — banner must NOT auto-dismiss.
5. Click Discard. Observe whether the banner clears.
6. Re-edit, press Ctrl+S again.

Assertions:
1. After step 2 the network panel shows a 415 response with the documented JSON body.
2. A persistent inline banner appears above the textarea bearing both the kind (`unsupported_extension`) and a structured error message. The banner is rendered using the same broken-link / error component class as FR-34 (`link-broken` or shared error-banner styling).
3. After step 4, the banner is still in the DOM (no toast auto-dismiss).
4. The dirty-dot is still lit (`data-dirty="true"`) — save did not succeed.
5. After Discard (step 5), the banner clears AND the textarea reverts to last-saved text.
6. Step 6 (re-attempt) issues a fresh PUT and re-renders the banner on each repeated failure.

Spec refs: FR-14a, FR-34, FR-40, AC-17.
Components exercised: `frontend/src/components/Editor.tsx`, `backend/libs/api.py` (`PUT /api/file`), `frontend/src/api.ts`.

---

## SYS-23 — Regen-prompt warn-don't-truncate: 60 KB fixture → warning field; 1.2 MB fixture → 413

Setup:
1. Backend running.
2. Three fixtures under `specs/development/spec_driven/`:
   - **Small (~5 KB):** baseline `revised_prompt.md` and 2 follow-ups totaling under 50 KB assembled.
   - **Medium (~60 KB):** synthesized `revised_prompt.md` + follow-ups so the assembled prompt lands between 50 KB and 1 MB.
   - **Large (~1.2 MB):** assembled prompt exceeds the 1 MB hard cap.
3. The frontend at `/project/development/spec_driven`.

Action:
1. **Small case:** click "Build prompt" with all stages selected. Capture response JSON.
2. **Medium case:** swap fixtures, click "Build prompt".
3. **Large case:** swap fixtures, click "Build prompt".
4. Inspect the rendered breakdown line and warning banner for cases 1 and 2.

Assertions:
1. Small case: response is 200, `warning === null`, `bytes` < 50_000, no warning banner in DOM. Breakdown line reads `{N} stages selected, {K} follow-ups inlined, autonomous=false, {bytes} KB`.
2. Medium case: response is 200, `warning` is a non-empty string, `bytes` is in `[50_000, 1_048_576]`, prompt body is full-length (NOT truncated — assert character count of the returned `prompt` matches `bytes`). UI renders a muted warning banner reading `warning: {warning} — verify your selection before pasting`.
3. Large case: response is **HTTP 413** with JSON body `{"detail": {"kind": "too_large", "bytes": <count>, ...}}`. UI surfaces the error inline; the `regen-prompt-block` is not rendered.
4. Across all cases, no 5xx; backend never silently truncates.

Spec refs: FR-14c, FR-42(d)(e), AC-19.
Components exercised: `backend/libs/api.py` / `backend/libs/regen_prompt.py` (prompt assembler), `frontend/src/components/RegeneratePanel.tsx`.

---

## SYS-24 — Read-zero contract surfacing in assembled prompt's Constraints section

Setup:
1. Backend running.
2. `specs/development/spec_driven/user_input/revised_prompt.md` and at least one `user_input/follow_ups/001-*.md` exist so the assembler has substantive input.
3. Stage definitions returned by `GET /api/stages` include the canonical six stages.

Action:
1. Open `/project/development/spec_driven`.
2. Toggle Autonomous ON.
3. Select all six stages, default modules.
4. Click "Build prompt".
5. The assembled prompt renders inline inside the `regen-prompt-block`; click the **Copy** button in the header bar (or read the `<pre>` body directly) and inspect the prompt.
6. Toggle Autonomous OFF and rebuild.
7. Compare the two assembled prompts.

Assertions:
1. The autonomous prompt opens with the literal first line `# EXECUTION MODE: AUTONOMOUS`. The next non-blank line is the verbatim imperative sentence from FR-14c(b) — character-for-character match.
2. The interactive prompt opens with `# EXECUTION MODE: INTERACTIVE` and does NOT include the autonomous imperative line.
3. Both prompts contain a `### Constraints` section (or equivalently labeled). The Constraints section MUST include all five items: CLAUDE.md, canonical paths, manager-spawn contract, no-AskUserQuestion-in-autonomous-mode, AND the **read-zero contract** verbatim ("regeneration deletes prior outputs first; new generation reads only the inputs" or the FR-14c(f) wording).
4. The prompt contains the verbatim text of `revised_prompt.md` (or `raw_prompt.md` if no revised exists) as a literal block (assert by comparing to the file bytes).
5. The prompt lists every `user_input/follow_ups/*.md` by relative path; assert by walking the directory and matching every entry against the prompt body.
6. The prompt embeds, for each selected stage, that stage's invocation hint and module paths from `/api/stages`.
7. Rebuild from step 6 yields the same Constraints listing minus the no-AskUserQuestion clause being demoted to "interactive default" wording (or kept verbatim depending on assembler choice — the read-zero clause remains regardless).

Spec refs: FR-14c, AC-19, AC-20, AC-21.
Components exercised: `backend/libs/regen_prompt.py`, `backend/libs/api.py` (`POST /api/regen-prompt`, `GET /api/stages`), `frontend/src/components/RegeneratePanel.tsx`, `frontend/src/components/ProjectPage.tsx`.

---

## Cross-cutting setup notes

### Playwright

- Use `@playwright/test` against Chromium only (NFR-14). Configure `use: { baseURL: 'http://127.0.0.1:8765' }` and a `webServer` block that runs `make run` from the project directory. Add a second profile that runs `make dev` and points at `http://127.0.0.1:5173`.
- Fixtures clear `localStorage` between tests via `await context.clearCookies(); await context.addInitScript(() => localStorage.clear())`. Tests that depend on persisted state (SYS-17) use a dedicated `storageState`.
- Network interception (`page.route('**/api/file', route => route.fulfill(...))`) is the supported way to stub PUT failures (SYS-22) without wiring a backend test-mode flag.
- Capture `pageerror` on every test to fail-fast on uncaught exceptions; required for SYS-17 corruption assertion.

### Windows symlink privilege

- SYS-07 requires the test process to hold `SeCreateSymbolicLinkPrivilege`. The simplest path is enabling Developer Mode on the test host (Settings → Privacy & Security → For developers → Developer Mode). CI runners on Windows MUST either enable Developer Mode in the image or skip SYS-07 via the documented `STATUS=SKIPPED-WINDOWS-NO-DEVELOPER-MODE` marker, surfaced in the test report as a warning, not a failure.
- Symlink fixtures are created with `os.symlink(target, link, target_is_directory=...)` inside a per-test temp directory layered on top of REPO_ROOT via a fixture that copies the real `specs/` tree into a writable workspace. The test never modifies the live repo.
- Linux/macOS runners require no extra privilege; they execute SYS-07 unconditionally.

### Port collisions

- Default port 8765 may collide with a developer's running session. Tests SHOULD allocate an ephemeral port per run via `socket.socket().bind(('127.0.0.1', 0))` → release → pass that as `SPEC_DRIVEN_PORT`. SYS-03 explicitly tests the override path; other tests inherit the ephemeral port via a Playwright `webServer` config.
- The "unavailable port" subcase (SYS-03 step 2) creates a sentinel listener with `SO_REUSEADDR=0` on the chosen port, then asserts the backend exits non-zero. The sentinel is closed in test teardown.
- SYS-08 needs LAN reachability; on CI that lacks it, the test enters the documented `STATUS=SKIPPED-NO-SECOND-HOST` mode and validates only the local socket binding via `psutil.net_connections()`. Cross-host validation runs only in environments where two reachable IPs exist.

### Fixture isolation

- Tests that mutate the filesystem (SYS-14, SYS-15, SYS-16, SYS-21, SYS-22) operate inside a fixture workspace constructed by copying the relevant `specs/` subtree into a temp dir; the backend is started against that temp dir as REPO_ROOT (FR-2 walk-upward target). The live repo is never touched by automated runs.
- Snapshots are taken via `pathlib.Path.read_bytes()` and restored on test teardown, even on assertion failure, via `pytest`'s `addfinalizer` / Playwright's `test.afterEach`.
