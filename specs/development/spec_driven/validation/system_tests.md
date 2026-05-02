# System Tests — spec_driven

End-to-end scenarios driving the live FastAPI backend, the built React bundle (or Vite dev server), the filesystem under `REPO_ROOT`, and a Chromium browser. Each scenario is reproducible by a human or a future test-writer worker. Assertion values are exact.

Conventions:
- `REPO_ROOT` = `C:\workspace\spec_coding`.
- `BACKEND_DIR` = `C:\workspace\spec_coding\projects\spec_driven\backend`.
- `FRONTEND_DIR` = `C:\workspace\spec_coding\projects\spec_driven\frontend`.
- `BASE_URL` = `http://127.0.0.1:8765` unless overridden by `SPEC_DRIVEN_PORT`.
- `EXPOSED_TREE` is the union from FR-1.
- "Browser" means latest stable Chrome / Chromium-based, driven by Playwright unless `Method: manual visual check` is stated.
- Backend launch (single-process production) is `make run` from `projects/spec_driven/`. Two-process dev is `make dev`.
- All `curl` commands assume PowerShell-quoting; `curl.exe` is invoked explicitly to avoid the PowerShell `Invoke-WebRequest` alias.

---

## SYS-01 — `make run` builds frontend then serves both `/` and `/api/` from one FastAPI process

- Components exercised: backend, frontend (built bundle), filesystem, build pipeline (`Makefile`, Vite).
- Spec refs: FR-11, FR-13, FR-14, NFR-3.

Setup:
1. Working tree is clean. `projects/spec_driven/backend/static/` is empty (or absent) before this scenario starts.
2. `uv sync` has been run at `REPO_ROOT`; `npm install` has been run in `FRONTEND_DIR`.
3. No process is listening on TCP port 8765.

Action:
1. From `projects/spec_driven/`, run `make run`. Capture stdout/stderr.
2. Wait until the FastAPI server logs `Uvicorn running on http://127.0.0.1:8765`.
3. Run `curl.exe -sS -o NUL -w "%{http_code}\n" http://127.0.0.1:8765/`.
4. Run `curl.exe -sS -o NUL -w "%{http_code}\n" http://127.0.0.1:8765/api/tree`.
5. Run `curl.exe -sS -i http://127.0.0.1:8765/` (capture full response headers + body prefix).
6. Identify all listening processes on port 8765 (`Get-NetTCPConnection -LocalPort 8765`).

Assertions:
1. `make run` exits 0 from the build step (Vite build) and then keeps the FastAPI process running in the foreground.
2. `projects/spec_driven/backend/static/` exists after step 1 and contains at least `index.html` and one JS bundle file under an assets folder.
3. Step 3 returns either `200` (HTML body for SPA) or `302` to a spec URL (per FR-15); the response body or `Location` header contains `final_specs/spec.md` or `revised_prompt.md`.
4. Step 4 returns `200`; body parses as JSON with top-level keys `settings` and `projects` in that order.
5. Step 6 reports exactly one process bound to port 8765, owned by the `make run` python/uvicorn process (not a separate Vite/Node process).

---

## SYS-02 — `make dev` starts two processes; both URLs reachable

- Components exercised: backend (uvicorn `--reload`), frontend (Vite dev server), `Makefile`, README documentation.
- Spec refs: FR-13, FR-14.

Setup:
1. No process listening on 8765 or on the Vite dev port (default 5173 unless README states otherwise).
2. README at `projects/spec_driven/README.md` exists and documents the two URLs.

Action:
1. From `projects/spec_driven/`, run `make dev` in a background terminal. Capture stdout/stderr to a log file.
2. Wait until both the FastAPI reload server logs `Uvicorn running on` and the Vite dev server logs `ready in` / `Local: http://localhost:5173/`.
3. `curl.exe -sS -o NUL -w "%{http_code}\n" http://127.0.0.1:8765/api/tree`.
4. `curl.exe -sS -o NUL -w "%{http_code}\n" http://localhost:5173/`.
5. List child processes spawned by the make target.
6. Read `projects/spec_driven/README.md`.

Assertions:
1. Step 3 returns `200` and JSON body parses with `settings` + `projects` keys.
2. Step 4 returns `200` and the body is HTML referencing the Vite client (`/@vite/client`).
3. Step 5 shows at least two distinct PIDs: one Python/uvicorn, one Node (Vite).
4. README contains both URLs literally — `http://127.0.0.1:8765` and `http://localhost:5173` (or the documented dev URL) — under a section explaining the two-process dev mode.

---

## SYS-03 — Default port 8765, override via env var, port-in-use exits non-zero

- Components exercised: backend startup, environment, filesystem.
- Spec refs: FR-12.

Setup:
1. No process on port 8765 or 9000.
2. A scratch process holds port 8766 (e.g., `python -c "import socket,time; s=socket.socket(); s.bind(('127.0.0.1',8766)); s.listen(); time.sleep(600)"`).

Action:
1. Run backend with no env overrides: `uv run python projects/spec_driven/backend/main.py` (or equivalent `make run`). Verify it binds to 8765 and `curl.exe -sS http://127.0.0.1:8765/api/tree` returns 200. Stop the process.
2. Run backend with `SPEC_DRIVEN_PORT=9000` set: `$env:SPEC_DRIVEN_PORT='9000'; uv run python projects/spec_driven/backend/main.py`. Verify it binds to 9000 and `curl.exe -sS http://127.0.0.1:9000/api/tree` returns 200. Stop the process.
3. Run backend with `SPEC_DRIVEN_PORT=8766` (the held port). Capture exit code and stderr.

Assertions:
1. Step 1 — uvicorn log line contains `Uvicorn running on http://127.0.0.1:8765`. Step 2 — log contains `:9000`.
2. Step 3 process exits with non-zero code within 5 seconds of launch.
3. Step 3 stderr contains a clear human-readable message naming the port (e.g., `port 8766 is already in use` or `address already in use`); the message MUST include the port number 8766. The error is NOT a raw Python traceback only — at minimum a one-line summary above any traceback.

---

## SYS-04 — `REPO_ROOT` discovery walks up from cwd; outside repo exits non-zero

- Components exercised: backend startup, filesystem traversal.
- Spec refs: FR-2, NFR-16.

Setup:
1. Create deeply nested cwd `C:\workspace\spec_coding\projects\spec_driven\backend\libs\__pycache__\nested\deeper\` (mkdir -p the chain).
2. Create scratch dir `C:\Temp\not-a-repo\` containing no `CLAUDE.md`, no `specs/`, no `.claude/`.

Action:
1. From the deeply nested cwd in step 1, launch backend (`uv run python C:\workspace\spec_coding\projects\spec_driven\backend\main.py`). Capture startup log lines.
2. Stop the process.
3. From `C:\Temp\not-a-repo\`, copy `main.py` and any sibling `libs/` into a sibling location, then launch the backend whose own file lives at `C:\Temp\not-a-repo\backend\main.py`. Capture exit code and stderr.

Assertions:
1. Step 1 — startup logs include `REPO_ROOT=C:\workspace\spec_coding` (or the equivalent `repo_root` resolved log line). The first `/api/tree` from this run lists projects from the real repo.
2. Step 3 — process exits non-zero within 5 seconds. Stderr contains a clear message naming the missing markers, e.g., `could not locate REPO_ROOT (no ancestor contains all of CLAUDE.md, specs/, .claude/)`. Error is NOT a bare traceback only.

---

## SYS-05 — First-open redirect: `/` → spec.md, falls back to revised_prompt.md

- Components exercised: backend, frontend redirect logic, filesystem.
- Spec refs: FR-15, primary flow 1, AC-1.

Setup:
1. `make run` is up at 127.0.0.1:8765.
2. `specs/development/spec_driven/final_specs/spec.md` exists.
3. `specs/development/spec_driven/user_input/revised_prompt.md` exists.
4. Browser cache empty / Playwright fresh context.

Action:
1. Launch a fresh Playwright Chromium context. Navigate to `http://127.0.0.1:8765/`.
2. Wait for `networkidle`. Capture final URL and the title of the rendered file (first `<h1>` text).
3. Stop backend. Rename `specs/development/spec_driven/final_specs/spec.md` to `spec.md.bak`. Restart `make run`.
4. Open a new fresh Playwright context. Navigate to `http://127.0.0.1:8765/`.
5. Capture final URL and rendered first heading.
6. Restore `spec.md.bak` → `spec.md`.

Assertions:
1. Step 2 — final URL equals `http://127.0.0.1:8765/projects/development/spec_driven/final_specs/spec.md`. Rendered first heading matches the H1 of that spec (`Spec — spec_driven`).
2. The redirect from `/` is HTTP 302 (verify by `curl.exe -sS -o NUL -w "%{http_code} %{redirect_url}\n" http://127.0.0.1:8765/`); status `302` and `redirect_url` points to the spec.md path.
3. Step 5 — final URL equals `http://127.0.0.1:8765/projects/development/spec_driven/user_input/revised_prompt.md`. Rendered first heading matches the revised_prompt H1.
4. Sidebar in step 2 has `Projects > development > spec_driven > final_specs` expanded (DOM check: tree node for `final_specs` has `aria-expanded="true"`).

---

## SYS-06 — Path traversal end-to-end

- Components exercised: backend `safe_resolve`, HTTP layer, URL decoding.
- Spec refs: FR-5, FR-6, AC-7, NFR-4.

Setup:
1. `make run` is up at 127.0.0.1:8765.

Action:
1. `curl.exe -sS -o response1.json -w "%{http_code}\n" "http://127.0.0.1:8765/api/file?path=../../../etc/hosts"`.
2. `curl.exe -sS -o response2.json -w "%{http_code}\n" "http://127.0.0.1:8765/api/file?path=..\..\..\Windows\System32\drivers\etc\hosts"` (backslash-encoded variant; quote so PowerShell does not eat backslashes — pass via single quotes or a hex-escaped form).
3. `curl.exe -sS -o response3.json -w "%{http_code}\n" "http://127.0.0.1:8765/api/file?path=%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fhosts"`.
4. `curl.exe -sS -o response4.json -w "%{http_code}\n" "http://127.0.0.1:8765/api/file?path=specs/../../../etc/hosts"`.
5. `curl.exe -sS -o response5.json -w "%{http_code}\n" "http://127.0.0.1:8765/api/file?path=C:/Windows/System32/drivers/etc/hosts"` (absolute Windows path).

Assertions:
1. Steps 1–5 — every status code is `400`.
2. Each response body parses as JSON and contains `"error":"outside_sandbox"` (or equivalent canonical key with that exact string value).
3. None of the responses contain any byte from the host's actual `hosts` file content (sanity check: assert response body length < 500 bytes and does not contain the string `localhost` from `C:\Windows\System32\drivers\etc\hosts`).
4. No 500 status appears in any response.

---

## SYS-07 — Symlink rejection

- Components exercised: backend tree-walk, backend file-read, filesystem.
- Spec refs: FR-4, FR-5.2, NFR-5.

Setup:
1. `make run` is up.
2. Create a real file `specs/development/spec_driven/final_specs/_real_target.md` containing the string `target file body`.
3. Attempt to create symlink `specs/development/spec_driven/final_specs/spec_link.md` pointing at `_real_target.md`. On Windows: run `New-Item -ItemType SymbolicLink -Path .\spec_link.md -Target .\_real_target.md` from PowerShell. If the command fails with a privilege error (no `SeCreateSymbolicLinkPrivilege` and Developer Mode disabled), record the failure and `Method: skipped on this host — document the symlink-privilege precondition`.

Action (only if symlink creation succeeded):
1. `curl.exe -sS http://127.0.0.1:8765/api/tree` → save response. Search JSON for any node whose `name` or `path` ends in `spec_link.md`.
2. `curl.exe -sS -o response.json -w "%{http_code}\n" "http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/spec_link.md"`.
3. `curl.exe -sS -o real.json -w "%{http_code}\n" "http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/_real_target.md"` (sanity).

Assertions:
1. Step 1 response contains zero entries for `spec_link.md` (symlink silently skipped).
2. Step 2 returns status `400` with body containing `"error":"outside_sandbox"`.
3. Step 3 returns status `200` with body containing `target file body` (proves the underlying file IS in `EXPOSED_TREE`, so the rejection is purely on the symlink itself).
4. If symlink creation was skipped due to privilege: scenario records `STATUS=SKIPPED-PRIVILEGE` and the documentation in `projects/spec_driven/README.md` includes a one-line note that this test requires Windows Developer Mode or admin elevation.

Cleanup: delete `spec_link.md` and `_real_target.md`.

---

## SYS-08 — Bind address `127.0.0.1`, NOT `0.0.0.0`

- Components exercised: backend startup, OS network stack.
- Spec refs: NFR-7.

Setup:
1. Host has at least two reachable network interfaces (e.g., loopback + LAN). Determine LAN IP with `Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike '*Loopback*'}`.
2. `make run` is up at 127.0.0.1:8765.

Action:
1. From the same host, `curl.exe -sS --max-time 3 http://127.0.0.1:8765/api/tree`.
2. From the same host, `curl.exe -sS --max-time 3 http://<LAN_IP>:8765/api/tree`.
3. From a separate host on the same LAN (or from a different network namespace if available), `curl.exe -sS --max-time 3 http://<LAN_IP>:8765/api/tree`.
4. Inspect listening sockets: `Get-NetTCPConnection -LocalPort 8765 | Select-Object LocalAddress,LocalPort,State`.

Assertions:
1. Step 1 returns 200.
2. Step 2 fails — connection refused, timeout, or empty reply (NOT a 200). Exit code is non-zero.
3. Step 3 fails — connection refused or timeout. Non-zero curl exit code.
4. Step 4 — exactly one row with `LocalAddress=127.0.0.1` and `State=Listen`. NO row with `LocalAddress=0.0.0.0` or `LocalAddress=::`.
5. If a second host is unavailable, mark step 3 as `Method: skipped — record interface bind result from step 4 as the binding evidence`.

---

## SYS-09 — No CORS wildcard

- Components exercised: backend HTTP, CORS middleware (or absence thereof).
- Spec refs: NFR-8.

Setup:
1. `make run` is up.

Action:
1. `curl.exe -sS -i -X OPTIONS "http://127.0.0.1:8765/api/tree" -H "Origin: https://evil.example" -H "Access-Control-Request-Method: GET"`.
2. `curl.exe -sS -i "http://127.0.0.1:8765/api/tree" -H "Origin: https://evil.example"`.

Assertions:
1. Step 1 response headers do NOT contain `Access-Control-Allow-Origin: *`.
2. Step 1 response headers do NOT contain `Access-Control-Allow-Origin: https://evil.example`.
3. Step 2 response headers do NOT contain `Access-Control-Allow-Origin: *`.
4. If any `Access-Control-Allow-Origin` header is present at all, its value MUST NOT be `*` and MUST NOT echo the `evil.example` origin.

---

## SYS-10 — No write endpoints

- Components exercised: backend HTTP, FastAPI routing.
- Spec refs: NFR-6.

Setup:
1. `make run` is up.

Action:
1. `curl.exe -sS -o NUL -w "%{http_code}\n" -X POST "http://127.0.0.1:8765/api/file" -H "Content-Type: application/json" -d '{"path":"foo.md","contents":"x"}'`.
2. `curl.exe -sS -o NUL -w "%{http_code}\n" -X PUT "http://127.0.0.1:8765/api/tree" -H "Content-Type: application/json" -d '{}'`.
3. `curl.exe -sS -o NUL -w "%{http_code}\n" -X DELETE "http://127.0.0.1:8765/api/file?path=foo.md"`.
4. `curl.exe -sS -o NUL -w "%{http_code}\n" -X PATCH "http://127.0.0.1:8765/api/file?path=foo.md"`.

Assertions:
1. Steps 1–4 each return status `405` (Method Not Allowed).
2. None of the responses contain the string `internal server error`.
3. Filesystem is unchanged after these calls (verify by `git status` showing no new/modified files under `EXPOSED_TREE`).

---

## SYS-11 — Dogfood self-render

- Components exercised: backend, frontend, filesystem (this very repo).
- Spec refs: primary flows 1 + 2, AC-1, AC-2, FR-7, FR-8, FR-15.
- Method: Playwright automation + manual visual check for layout polish.

Setup:
1. `make run` is up; the live `specs/development/spec_driven/` tree contains `user_input/`, `interview/`, `findings/`, `final_specs/`, `validation/`.
2. Each of the five stages contains at least one `.md` (or `.json` / `.jsonl`) file.

Action:
1. Open Chromium via Playwright at `http://127.0.0.1:8765/`.
2. Wait for `networkidle`. Capture the final URL.
3. Take a full-page screenshot.
4. Read sidebar DOM: enumerate top-level tree nodes; under `Projects > development > spec_driven`, enumerate child node names and their on-screen DOM order.
5. Click each of the five stage entries one at a time. After each click, capture the URL and assert the main pane re-renders.
6. For each stage, click the first file leaf inside it and capture the URL plus the rendered first heading.

Assertions:
1. Step 2 final URL equals `…/projects/development/spec_driven/final_specs/spec.md`.
2. Sidebar tree (step 4) under `Projects > development > spec_driven` contains exactly five children, in this DOM order: `user_input`, `interview`, `findings`, `final_specs`, `validation`.
3. Step 5 — clicking a stage folder toggles its `aria-expanded` between `true` and `false`; URL does NOT change on folder click (per FR-26).
4. Step 6 — each stage's first file is clickable, URL updates to `/projects/development/spec_driven/<stage>/<filename>`, and the rendered main pane has at least one non-empty heading or pre-block.
5. Manual visual check (screenshot from step 3): sidebar is fixed-width 320px, no horizontal scroll, file rows use middle-ellipsis preserving `.md`. Record `Method: manual visual check`.

---

## SYS-12 — Cross-link follow + back-button + scroll restore

- Components exercised: frontend router, link resolver, backend `/api/file`.
- Spec refs: FR-17, FR-33 case 3, primary flow 4, AC-4.
- Method: Playwright + manual visual check for scroll-position best-effort.

Setup:
1. `make run` is up.
2. `final_specs/spec.md` contains a relative markdown link of the form `[..]( ../findings/dossier.md )`. If not present, append a temporary line `See [dossier](../findings/dossier.md)` to the bottom of the spec for the duration of this test (revert after).
3. `findings/dossier.md` exists and contains content > one viewport tall.

Action:
1. Navigate Playwright to `http://127.0.0.1:8765/projects/development/spec_driven/final_specs/spec.md`.
2. Scroll main pane down by 800px. Record scroll position `S0`.
3. Click the `dossier.md` link.
4. Wait for navigation. Capture URL and rendered first heading.
5. Click browser back button.
6. Wait for navigation. Capture URL, rendered first heading, and main-pane scroll position.

Assertions:
1. After step 4 — URL equals `http://127.0.0.1:8765/projects/development/spec_driven/findings/dossier.md`. Rendered first heading matches dossier H1.
2. After step 6 — URL equals the original spec.md URL. Spec H1 renders again.
3. Scroll position after step 6 is non-zero (i.e., the scroll did NOT reset to top). Best-effort: it is within 100px of `S0`. Record `Method: manual visual check / best-effort` if exact restore is not implemented.
4. The dossier link in step 3 is rendered as a real anchor with an in-app router push (network panel shows NO full-page reload between steps 1 and 4 — same browser document instance).

---

## SYS-13 — Folder-only URL redirect (replace history)

- Components exercised: frontend router, FR-16 redirect logic.
- Spec refs: FR-16, FR-17.

Setup:
1. `make run` is up.
2. `findings/` contains at least one `.md` file; the alphabetically-first one is recorded as `FIRST_FILE`.

Action:
1. Open Playwright. Navigate to `http://127.0.0.1:8765/`.
2. Capture history length: `len0 = await page.evaluate(() => history.length)`.
3. Navigate via `page.goto('http://127.0.0.1:8765/projects/development/spec_driven/findings/')` (with trailing slash).
4. Wait for navigation. Capture URL `URL_AFTER_REDIRECT` and `len1 = history.length`.
5. Click browser back button.
6. Capture URL `URL_AFTER_BACK`.

Assertions:
1. `URL_AFTER_REDIRECT` equals `http://127.0.0.1:8765/projects/development/spec_driven/findings/<FIRST_FILE>`.
2. `len1 - len0` is `<= 1` (replace, not push: the folder URL did NOT add a separate history entry beyond the goto itself).
3. `URL_AFTER_BACK` is NOT the folder URL `…/findings/`. It is the URL from before step 3 (the home redirect target). The back button does not bounce back into `findings/`.

---

## SYS-14 — Refresh after external write

- Components exercised: backend `/api/tree`, frontend Refresh button, filesystem.
- Spec refs: FR-3, FR-28, AC-12.

Setup:
1. `make run` is up.
2. `specs/development/spec_driven/validation/strategy.md` does NOT yet exist (rename it away if necessary, restore at end).
3. Open Playwright at `http://127.0.0.1:8765/`. Wait for tree to render.

Action:
1. In the sidebar, locate the `validation` stage folder under `spec_driven`. Capture its child file list (DOM). Expect zero `.md` children visible (or just the muted-italic `not yet generated` leaf if `validation/` itself is missing — record which case applies).
2. Externally (via filesystem write outside the app), create `specs/development/spec_driven/validation/strategy.md` with body `# Strategy\n\nbody`.
3. Without doing anything in the browser, re-read the sidebar DOM. Confirm `strategy.md` is NOT present.
4. Click the sidebar's "Refresh" button.
5. After the refresh request completes, re-read the sidebar DOM under `validation`.

Assertions:
1. Step 3 — no entry named `strategy.md` under the `validation` node (proves no auto-watcher).
2. Step 5 — exactly one new leaf named `strategy.md` appears under `validation`. It is clickable; clicking it navigates to `…/validation/strategy.md` and renders `# Strategy`.
3. Network tab shows a single `GET /api/tree` between steps 4 and 5 returning 200.

Cleanup: remove the test `strategy.md` if not the real one.

---

## SYS-15 — Stale-tree click after external delete

- Components exercised: backend `/api/file`, frontend stale-state UI.
- Spec refs: FR-28, AC-15, FR-5.7.

Setup:
1. `make run` is up.
2. Create `specs/development/spec_driven/findings/_temp_stale.md` with body `# Temp`.
3. Open Playwright at `http://127.0.0.1:8765/`; click Refresh in the sidebar so `_temp_stale.md` is in the tree.

Action:
1. Confirm sidebar shows `_temp_stale.md` under `findings`.
2. Externally delete the file from disk (`Remove-Item …\_temp_stale.md`).
3. In the browser, click the still-visible `_temp_stale.md` leaf in the sidebar.
4. Inspect the main pane content and the inline message rendered.
5. Inspect the network response that triggered the stale UI.

Assertions:
1. Step 3 — sidebar click triggers a `GET /api/file?path=…_temp_stale.md` request returning status `404` with JSON body containing `"kind":"file_removed"`.
2. Step 4 — main pane shows the inline non-modal message containing the literal text `this file no longer exists` (case-insensitive substring match) and the word `refresh` along with a clickable refresh affordance.
3. The page does NOT navigate away; URL still points to `_temp_stale.md`.
4. Clicking the inline refresh button issues `GET /api/tree`; after that, the stale leaf disappears from the sidebar.
5. No `500` response observed for the entire scenario.

---

## SYS-16 — Concurrent-write tolerance

- Components exercised: backend `/api/tree`, backend `/api/file`, filesystem.
- Spec refs: NFR-12, AC-15, FR-5.7.

Setup:
1. `make run` is up.
2. Pick a target file `specs/development/spec_driven/findings/_concurrent.md`. Initial content `# concurrent` (~12 bytes).

Action:
1. Start a writer loop (run in a separate PowerShell window): repeatedly truncate-and-rewrite `_concurrent.md` with bodies of varying size (between 1 byte and 500 KB). Loop for 30 seconds at ~50 writes/sec. Occasionally remove the file briefly between writes.
2. While the writer is running, run a reader loop: every 100ms, issue both `curl.exe -sS -o NUL -w "%{http_code}\n" "http://127.0.0.1:8765/api/tree"` and `curl.exe -sS -o NUL -w "%{http_code}\n" "http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/findings/_concurrent.md"`. Capture all status codes.
3. When the writer finishes, stop the reader and tally status codes seen.

Assertions:
1. `/api/tree` codes seen: only `200`. Zero `5xx`. Zero `4xx`.
2. `/api/file` codes seen: subset of `{200, 404}`. Zero `5xx`. Any `404` body has `"kind":"file_removed"`.
3. No backend stderr line containing the string `Traceback` was emitted during the run.
4. Optional: any `200` response that contains the U+FFFD replacement character is acceptable (partial-content tolerance per NFR-12).

Cleanup: delete `_concurrent.md`.

---

## SYS-17 — Restore session on reload

- Components exercised: frontend router, `localStorage`, sidebar state.
- Spec refs: FR-23, AC-13.

Setup:
1. `make run` is up.
2. Browser fresh context, `localStorage` empty.

Action:
1. Open Playwright at `http://127.0.0.1:8765/`.
2. Navigate (by clicking sidebar) to `findings/dossier.md`. Capture URL.
3. In the sidebar, expand `interview/` (so its `aria-expanded="true"`) and collapse `validation/` (so its `aria-expanded="false"`).
4. Read `localStorage.getItem('spec_driven.sidebar.v1')` via `page.evaluate`. Record the JSON value.
5. Hard-reload the page (`page.reload({ waitUntil: 'networkidle' })`).
6. Capture URL, rendered first heading, and the `aria-expanded` attribute of `interview` and `validation` nodes.

Assertions:
1. Step 4 returns a non-null JSON string parseable as an object containing both collapse-state per-node-path AND last-selected file path keys.
2. After reload (step 6) — URL still equals the dossier URL from step 2.
3. After reload — main pane renders dossier first heading.
4. After reload — `interview` node `aria-expanded="true"`, `validation` node `aria-expanded="false"`.
5. Clearing `localStorage` and reloading: tree state defaults (per FR-22 default collapse rules); URL still drives selection.

---

## SYS-18 — Section 1 navigation (CLAUDE.md, agent file, skill folder)

- Components exercised: frontend router, FR-15 settings routes, backend `/api/file`.
- Spec refs: FR-7, FR-15, AC-3.

Setup:
1. `make run` is up.
2. `CLAUDE.md` exists at `REPO_ROOT`.
3. `.claude/agents/agent_team__validation_manager.md` exists.
4. `.claude/skills/agent_team/SKILL.md` exists.

Action:
1. Open Playwright at `http://127.0.0.1:8765/`. Wait for networkidle.
2. Click `CLAUDE.md` in Section 1. Capture URL and the first H1 text in the main pane.
3. Click `Agents > agent_team__validation_manager.md`. Capture URL and first H1.
4. Click `Skills > agent_team`. Capture URL and first H1.

Assertions:
1. Step 2 — URL ends with `/settings/claude-md` (or the spec's exact route). Main pane first H1 matches the H1 of `CLAUDE.md` (literally `CLAUDE.md — spec_coding monorepo`).
2. Step 3 — URL ends with `/settings/agents/agent_team__validation_manager.md`. Main pane renders the file's first heading.
3. Step 4 — URL ends with `/settings/skills/agent_team`. The rendered file is `.claude/skills/agent_team/SKILL.md` (verify by content match: response of `GET /api/file?path=.claude/skills/agent_team/SKILL.md` equals what the pane shows).
4. In all three cases, breadcrumb above the pane reads `Settings / <kind> / <filename>` per FR-29.

---

## SYS-19 — Image placeholder + non-image-bytes rejection

- Components exercised: frontend markdown renderer, backend `/api/file`.
- Spec refs: FR-36, AC-8, FR-5.4.

Setup:
1. `make run` is up.
2. Create a temporary markdown file `specs/development/spec_driven/findings/_img_test.md` containing exactly:
   ```
   # img test
   
   ![diagram](./diagram.png)
   ```
3. Create `specs/development/spec_driven/findings/diagram.png` (any small valid PNG bytes — a 1x1 transparent pixel suffices).
4. Click Refresh in the sidebar.

Action:
1. Navigate Playwright to `http://127.0.0.1:8765/projects/development/spec_driven/findings/_img_test.md`.
2. Inspect the rendered HTML for the image element.
3. `curl.exe -sS -o NUL -w "%{http_code}\n" "http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/findings/diagram.png"`.
4. `curl.exe -sS "http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/findings/diagram.png"` (capture body).

Assertions:
1. Step 2 — DOM contains exactly one element matching `span.image-placeholder` with text content `diagram` and `title="v1: images not rendered"`. NO `<img>` tag is rendered for this image.
2. Step 3 — status code `415`.
3. Step 4 — response body parses as JSON and contains `"error":"unsupported_extension"`.
4. No PNG bytes are present in step 4 response (response body length < 200 bytes; first byte is not the PNG magic `0x89`).

Cleanup: remove `_img_test.md` and `diagram.png`.

---

## SYS-20 — JSONL render

- Components exercised: frontend JSONL renderer (Shiki per-line), backend `/api/file`.
- Spec refs: FR-32.

Setup:
1. `make run` is up.
2. Create a fixture file `specs/development/spec_driven/findings/_events_fixture.jsonl` whose contents are exactly three lines:
   - Line 1: `{"type":"exec.unit.started","unit":"u1"}`
   - Line 2: `{"type":"validation.pass","unit":"u1","level":"unit_tests"}`
   - Line 3: `{this is not valid json,,,`
3. Click Refresh in the sidebar.

Action:
1. Navigate Playwright to `http://127.0.0.1:8765/projects/development/spec_driven/findings/_events_fixture.jsonl`.
2. Read the rendered DOM. Identify how many separate Shiki-highlighted blocks (or `pre` blocks classed as Shiki output) are rendered within the main pane.
3. Inspect the third block's content and class list.

Assertions:
1. Step 2 — exactly three top-level rendered line containers are present (one per source line). Lines 1 and 2 are each a Shiki-highlighted JSON block with token-level coloring (the DOM contains spans whose class names indicate JSON tokens, e.g., `token.string`, `token.punctuation`, or Shiki's theme classes).
2. Line 3 (the malformed line) is rendered as plain text — its container has no Shiki token spans, OR is class-marked as a fallback (e.g., `class="jsonl-line jsonl-malformed"` per the implementation). The literal raw line content `{this is not valid json,,,` is present verbatim in the DOM.
3. None of the three lines triggers a JS console error (capture `page.on('pageerror')` and `console` events; assert empty error list for this navigation).
4. Method: automated DOM inspection for line/block count + manual visual check that color-highlighting is visible on lines 1 and 2 and absent on line 3 (record screenshot).

Cleanup: remove `_events_fixture.jsonl`.

---

## Cross-cutting setup notes

- All scenarios that require a running backend assume a fresh `make run` with no stale `static/` output from a previous run unless explicitly noted.
- Playwright tests run in a fresh browser context per scenario unless a scenario explicitly reuses session state.
- For Windows, prefer `curl.exe` over `Invoke-WebRequest`; status-code captures use `-w "%{http_code}\n"`.
- Where a scenario requires a separate host (SYS-08), record `STATUS=SKIPPED-NO-SECOND-HOST` with the binding evidence (`Get-NetTCPConnection`) standing in.
- Where Windows symlink privilege is unavailable (SYS-07), record `STATUS=SKIPPED-PRIVILEGE` and ensure README documents the prerequisite.
- Do not run these scenarios against shared machines: they create and delete files inside `EXPOSED_TREE`. Prefer a clean checkout or run on a developer laptop.
