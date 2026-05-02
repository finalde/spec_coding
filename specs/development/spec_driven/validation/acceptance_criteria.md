# Acceptance Criteria — spec_driven (Gherkin)

Run: spec_driven-20260502-141813
Stage: 5 (Validation strategy — acceptance_criteria level)
Source spec: `C:\workspace\spec_coding\specs\development\spec_driven\final_specs\spec.md`

Each numbered scenario AC-1..AC-15 maps 1:1 to the spec's `## Acceptance criteria summary`. AC-16..AC-23 cover additional FR/NFR items called out for explicit Gherkin coverage.

---

## Feature: Frontend routing

### Scenario: AC-1 (first open) — root URL renders final_specs/spec.md with tree expanded
Given the FastAPI process is running on `http://localhost:8765/`
And the file `C:\workspace\spec_coding\specs\development\spec_driven\final_specs\spec.md` exists on disk
And the user has no prior `localStorage` state under key `spec_driven.sidebar.v1`
When the user navigates the browser to `http://localhost:8765/`
Then the browser is redirected (302) to `/projects/development/spec_driven/final_specs/spec.md`
And the main pane renders the rendered markdown of `spec.md`
And the sidebar tree path `Projects > development > spec_driven > final_specs` is expanded
And the leaf row for `spec.md` carries the DOM attribute `aria-selected="true"`
Spec refs: FR-15, FR-22, AC-1, primary flow #1

### Scenario: AC-4 (cross-link navigation) — relative link from spec.md to ../findings/dossier.md
Given the user is viewing `/projects/development/spec_driven/final_specs/spec.md`
And the file `C:\workspace\spec_coding\specs\development\spec_driven\findings\dossier.md` exists on disk
And the rendered markdown contains a link with `href="../findings/dossier.md"`
When the user clicks that link
Then the link is rendered as a React Router `<Link>` (not a raw `<a>` with `target="_blank"`)
And the browser URL updates to `/projects/development/spec_driven/findings/dossier.md` via push-history
And the main pane re-renders with the contents of `dossier.md`
And clicking the browser's Back button returns to `/projects/development/spec_driven/final_specs/spec.md`
Spec refs: FR-15, FR-17, FR-33 case 3 (internal), AC-4, primary flow #4

### Scenario: AC-6 (external link) — https link opens in a new tab with rel attributes
Given the user is viewing any markdown file rendered by the app
And the markdown source contains the literal text `[Example](https://example.com)`
When the rendered DOM is inspected for that link
Then the link is rendered as `<a href="https://example.com" target="_blank" rel="noopener noreferrer">`
And clicking it opens the URL in a new browser tab
Spec refs: FR-33 case 1, AC-6, primary flow #6

---

## Feature: Frontend sidebar

### Scenario: AC-2 (browse stages) — five stage subfolders are expandable and contain renderable files
Given the user is viewing the app with `Projects > development > spec_driven` visible
And on disk each of `user_input\`, `interview\`, `findings\`, `final_specs\`, `validation\` under `C:\workspace\spec_coding\specs\development\spec_driven\` contains at least one supported file
When the user clicks each of the five stage folder rows in turn
Then each folder row toggles `aria-expanded="true"`
And each folder reveals at least one leaf row beneath it
And clicking a leaf renders that file in the main pane and updates the URL via push-history
And the stage folder click never causes navigation by itself (folder click toggles expand/collapse only)
Spec refs: FR-7, FR-22, FR-26, FR-38, AC-2, primary flow #2

### Scenario: AC-3 (browse settings) — CLAUDE.md, every agent, every skill render
Given the sidebar's Section 1 `Settings & Shared Context` is rendered with three always-expanded subgroups: `CLAUDE.md`, `Agents`, `Skills`
And `C:\workspace\spec_coding\CLAUDE.md` exists
And at least one file exists under `C:\workspace\spec_coding\.claude\agents\*.md`
And at least one folder under `C:\workspace\spec_coding\.claude\skills\*\` contains a `SKILL.md`
When the user clicks the `CLAUDE.md` leaf
And then clicks an agent leaf (e.g., `agent_team__interview_manager.md`)
And then clicks a skill leaf (e.g., the leaf representing `agent_team/SKILL.md`)
Then for `CLAUDE.md` the URL becomes `/settings/claude-md` and the file renders
And for the agent leaf the URL becomes `/settings/agents/agent_team__interview_manager.md` and the file renders
And for the skill leaf the URL becomes `/settings/skills/agent_team` and `agent_team/SKILL.md` renders
And in each case `aria-selected="true"` moves to the clicked leaf
Spec refs: FR-7, FR-15, FR-21, AC-3, primary flow #3

### Scenario: AC-11 (missing stage rendering) — validation/ absent renders muted-italic, not expandable
Given a project `Projects > development > new_project` whose `validation\` directory does NOT exist on disk
And `GET /api/tree` therefore returns the `validation` stage entry with `present: false` and an empty file list
When the sidebar renders the project node
Then the `validation` row is rendered as a muted-italic leaf
And the row's `title` attribute equals `not yet generated`
And the row is NOT expandable (no toggle chevron, no children)
And keyboard arrow navigation skips this row
And clicking this row produces no URL change
Spec refs: FR-9, FR-24, FR-34, AC-11

### Scenario: AC-12 (refresh) — externally-created validation/strategy.md appears after Refresh click
Given the user is viewing the app and `validation\` for `Projects > development > spec_driven` shows zero files
And the user externally creates the file `C:\workspace\spec_coding\specs\development\spec_driven\validation\strategy.md`
When the user clicks the sidebar's `Refresh` button at the top of the sidebar
Then the frontend issues `GET /api/tree`
And the re-rendered tree includes a new leaf `strategy.md` under `validation`
And per FR-8 priority order `strategy.md` is the first file under `validation`
Spec refs: FR-8, FR-28, AC-12, primary flow #7

### Scenario: AC-13 (state restoration) — reload restores URL selection and unrelated collapse state
Given the user has expanded `Projects > ai_video > some_project > findings` and that state has been written to `localStorage` key `spec_driven.sidebar.v1`
And the user is currently at URL `/projects/development/spec_driven/final_specs/spec.md`
When the user presses F5 to reload the page
Then the URL remains `/projects/development/spec_driven/final_specs/spec.md`
And `final_specs/spec.md` re-renders in the main pane
And the leaf for `spec.md` carries `aria-selected="true"`
And the previously-expanded `Projects > ai_video > some_project > findings` chain remains expanded after reload
And other unrelated branches restore their previously-saved collapse state from `localStorage`
Spec refs: FR-22, FR-23, AC-13, primary flow #9

### Scenario: AC-14 (keyboard navigation) — Tab/Up/Down/Right/Left/Enter behave per W3C ARIA APG
Given the sidebar is rendered with `role="tree"` on the container, `aria-multiselectable="false"`, and the document has just loaded
When the user presses `Tab` from the address bar
Then keyboard focus lands on the sidebar tree (a single tab stop for the whole tree)
When the user presses `Down`
Then focus moves to the next visible node
When the user presses `Up`
Then focus moves to the previous visible node
When focus is on a collapsed folder and the user presses `Right`
Then that folder expands (`aria-expanded` becomes `"true"`) and focus stays on the folder
When focus is on an already-expanded folder and the user presses `Right`
Then focus moves to the first child node
When focus is on a leaf and the user presses `Right`
Then nothing happens (no-op)
When focus is on an expanded folder and the user presses `Left`
Then that folder collapses (`aria-expanded` becomes `"false"`)
When focus is on a collapsed folder or a leaf and the user presses `Left`
Then focus moves to the parent node
When focus is on a leaf and the user presses `Enter`
Then the app navigates to that leaf's file (push-history) and `aria-selected="true"` moves to it
When focus is on a folder and the user presses `Enter`
Then nothing happens (no-op on folders)
Spec refs: FR-18, FR-19, FR-20, NFR-9, AC-14

---

## Feature: Frontend main pane

### Scenario: AC-5 (broken link) — link to non-existent file renders muted with file-not-found tooltip, not clickable
Given the user is viewing `final_specs/spec.md`
And the markdown contains a relative link with `href="../validation/strategy.md"`
And the file `C:\workspace\spec_coding\specs\development\spec_driven\validation\strategy.md` does NOT exist on disk
When the page renders that link
Then the link is rendered as a `<span class="link-broken">` element (NOT an `<a>` element)
And the `title` attribute equals `file not found`
And clicking the span performs no navigation and no URL change
Spec refs: FR-33 case 3 (broken-missing), FR-34, AC-5, primary flow #5

### Scenario: AC-16 (FR-37) — link from CLAUDE.md to pyproject.toml renders broken-outside
Given the user is viewing `/settings/claude-md`
And the rendered markdown contains a relative link with `href="pyproject.toml"`
And `pyproject.toml` lives at `C:\workspace\spec_coding\pyproject.toml` (outside `EXPOSED_TREE`)
When the page renders that link
Then the link is rendered as a `<span class="link-broken">` element
And the `title` attribute equals `outside exposed tree`
And the element is NOT an `<a>` and is not clickable for navigation
Spec refs: FR-33 case 3 (broken-outside), FR-34, FR-37

### Scenario: AC-17 (FR-33 case 2) — same-file anchor click with no matching slug is silent no-op
Given the user is viewing `final_specs/spec.md`
And the markdown contains an anchor link with `href="#nonexistent-heading"`
And no heading in `spec.md` produces the GFM kebab-case slug `nonexistent-heading`
When the user clicks that anchor link
Then no navigation occurs (URL hash may change to `#nonexistent-heading` but no scroll target is found)
And no warning UI is shown (silent fall-through)
And the rendered DOM did NOT mark the link as broken (it remains a normal anchor `<a>` per FR-33 case 2 in-app handler)
Spec refs: FR-33 case 2, FR-30

---

## Feature: Backend file system contract

### Scenario: AC-7 (path traversal blocked) — GET /api/file with traversal returns 400 outside_sandbox
Given the FastAPI process is running with `REPO_ROOT = C:\workspace\spec_coding`
When an HTTP client issues `GET /api/file?path=..%2F..%2F..%2Fetc%2Fhosts`
Then the response status is `400`
And the JSON body contains the key/value `"error": "outside_sandbox"` (or equivalent error code key `outside_sandbox`)
And no file content is returned
And the same applies for the Windows equivalent `..\..\..\Windows\System32\drivers\etc\hosts`
Spec refs: FR-5.1, FR-6, NFR-4, AC-7

### Scenario: AC-8 (extension whitelist) — GET /api/file?path=foo.png returns 415
Given a file at a valid `EXPOSED_TREE` path with extension `.png`
When an HTTP client issues `GET /api/file?path=foo.png`
Then the response status is `415`
And the JSON body contains the error code `unsupported_extension`
And no file bytes are returned
Spec refs: FR-5.4, AC-8

### Scenario: AC-9 (binary content rejected) — .md file containing \x00 returns 415 binary_content
Given a file at `C:\workspace\spec_coding\specs\development\spec_driven\final_specs\spec.md` whose bytes contain at least one `\x00` byte
When an HTTP client issues `GET /api/file?path=specs/development/spec_driven/final_specs/spec.md`
Then the response status is `415`
And the JSON body contains the error code `binary_content`
Spec refs: FR-5.6, NFR-13, AC-9

### Scenario: AC-10 (size limit) — file >2 MB returns 413
Given a file at a valid `EXPOSED_TREE` path whose size on disk is 2_097_153 bytes (>2 MB)
When an HTTP client issues `GET /api/file?path=<that_relative_path>`
Then the response status is `413`
And the JSON body contains the error code `too_large`
Spec refs: FR-5.5, NFR-15, AC-10

### Scenario: AC-15 (concurrent write tolerance) — mid-write file removal does not produce 500
Given Claude Code is mid-write to `C:\workspace\spec_coding\specs\development\spec_driven\final_specs\spec.md` (truncate-then-write, non-atomic)
And during that window the file may transiently not exist on disk
When the frontend issues `GET /api/tree` during the write window
Then the response status is `200`
And no `500` is returned (the missing file is either skipped during the walk or surfaces only via per-file requests)
When the frontend issues `GET /api/file?path=specs/development/spec_driven/final_specs/spec.md` and the file is currently absent
Then the response status is `404`
And the JSON body contains `"kind": "file_removed"`
And the response is structured (no traceback, no 500)
Spec refs: FR-5.7, NFR-12, AC-15, primary flow #8

### Scenario: AC-19 (NFR-5) — symlink-as-source rejection on GET /api/file
Given a symbolic link at `C:\workspace\spec_coding\specs\development\spec_driven\final_specs\spec_link.md` whose target is the real file `spec.md` inside `EXPOSED_TREE`
And the symlink itself satisfies `Path.is_symlink() == True`
When an HTTP client issues `GET /api/file?path=specs/development/spec_driven/final_specs/spec_link.md`
Then the response status is `400`
And the JSON body contains the error code `outside_sandbox`
And no file content is returned
Spec refs: FR-4, FR-5.2, NFR-5

---

## Feature: Backend tree shape

### Scenario: AC-20 (FR-2) — REPO_ROOT resolution failure exits non-zero
Given the backend `main.py` is launched from a working directory that is NOT inside any folder containing all three of `CLAUDE.md`, `specs/`, and `.claude/`
When the process attempts to resolve `REPO_ROOT` by walking parent directories at startup
Then the walk fails to locate such a directory
And the process exits with a non-zero exit code
And stderr contains a clear error message naming the failed `REPO_ROOT` resolution
Spec refs: FR-2

---

## Feature: Backend deployment

### Scenario: AC-21 (FR-12) — SPEC_DRIVEN_PORT override is honored; unavailable port exits non-zero
Given the environment variable `SPEC_DRIVEN_PORT=9090` is set
And TCP port 9090 is currently free on `127.0.0.1`
When the backend is launched via `make run`
Then the FastAPI process binds to `127.0.0.1:9090`
And `GET http://127.0.0.1:9090/api/tree` responds with status `200`
Given instead that port `9090` is already bound by another process
When the backend is launched via `make run` with `SPEC_DRIVEN_PORT=9090`
Then the process exits with a non-zero exit code
And stderr contains a clear error message stating the port is unavailable
Spec refs: FR-12, NFR-7

---

## Feature: Security

### Scenario: AC-18 (NFR-7) — default Uvicorn bind is 127.0.0.1, not 0.0.0.0
Given the backend is launched via `make run` with no `SPEC_DRIVEN_PORT` override
When the process is inspected for its listening socket
Then the bind address is `127.0.0.1` on TCP port `8765`
And the bind address is NOT `0.0.0.0`
And the bind address is NOT any non-loopback interface
And `GET http://127.0.0.1:8765/api/tree` returns `200`
And a connection attempt from a non-loopback host to the machine's LAN IP on port 8765 is refused
Spec refs: FR-12, NFR-7

### Scenario: AC-22 (NFR-8) — no CORS wildcard configured
Given the backend FastAPI app is running
When an HTTP client issues `OPTIONS /api/tree` with header `Origin: http://evil.example.com`
Then the response does NOT include the header `Access-Control-Allow-Origin: *`
And the response does NOT include `Access-Control-Allow-Origin: http://evil.example.com`
And the FastAPI app source contains no `CORSMiddleware` registration with `allow_origins=["*"]`
Spec refs: NFR-8

### Scenario: AC-23 (NFR-6) — no write endpoints (POST/PUT/PATCH/DELETE return 405)
Given the backend FastAPI app is running
When an HTTP client issues `POST /api/file?path=specs/development/spec_driven/final_specs/spec.md` with any body
Then the response status is `405`
When an HTTP client issues `PUT /api/file?path=specs/development/spec_driven/final_specs/spec.md` with any body
Then the response status is `405`
When an HTTP client issues `PATCH /api/file?path=specs/development/spec_driven/final_specs/spec.md` with any body
Then the response status is `405`
When an HTTP client issues `DELETE /api/file?path=specs/development/spec_driven/final_specs/spec.md`
Then the response status is `405`
When an HTTP client issues `POST /api/tree` with any body
Then the response status is `405`
And the FastAPI app source registers ONLY `GET` route handlers under `/api/`
Spec refs: NFR-6

End of acceptance criteria.
