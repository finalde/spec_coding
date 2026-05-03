# Acceptance criteria — spec_driven
Run: spec_driven-20260503-030434

Each scenario below is self-contained and independently executable. URLs assume the FastAPI backend is bound to `http://127.0.0.1:8765` (per FR-38). Concrete paths are repo-relative; the backend root is `C:/workspace/spec_coding/`.

---

## Feature: Sidebar tree shape (Spec refs: FR-1, FR-2, FR-16, AC-1)

### Scenario: AC-1 — sidebar tree returns recursive children and renders ≥1 leaf per top-level section
Given the FastAPI backend is running on `http://127.0.0.1:8765`
And the repo contains `CLAUDE.md`, `.claude/skills/agent_team/SKILL.md`, and `specs/development/spec_driven/final_specs/spec.md` on disk
When a client issues `GET http://127.0.0.1:8765/api/tree`
Then the response status is `200`
And the response body is JSON of shape `{name, path, type, children}` where `type` ∈ `{section, file, type, project, stage}`
And every non-leaf node carries a `children` array (single field name across all node types — no `task_type.projects` or `project.stages` drift)
And the top-level array contains exactly two sections: `Claude Settings & Shared Context` and `Projects`
When the SPA at `http://127.0.0.1:8765/` mounts and calls the same endpoint
Then the DOM contains exactly one element with `data-testid="sidebar"`
And under that root, at least one descendant with `data-testid="tree-leaf"` exists under `Claude Settings & Shared Context` (e.g., the leaf for `CLAUDE.md`)
And at least one descendant with `data-testid="tree-leaf"` exists under `Projects` (e.g., the leaf for `specs/development/spec_driven/final_specs/spec.md`)
And `console.error` collected during this load equals `[]`

---

## Feature: File read happy path and security headers (Spec refs: FR-3, FR-5, NFR-2, AC-2)

### Scenario: AC-2 — GET /api/file returns spec.md content with nosniff and attachment headers
Given the file `specs/development/spec_driven/final_specs/spec.md` exists on disk and is <500 KB
When a client issues `GET http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/spec.md`
Then the response status is `200`
And the JSON body has shape `{path, content, mtime, bytes}`
And `body.path == "specs/development/spec_driven/final_specs/spec.md"` (forward-slash normalized)
And `body.content` decoded as UTF-8 equals the bytes of the file on disk
And `body.bytes` equals the file size in bytes
And response header `X-Content-Type-Options` equals `nosniff`
And response header `Content-Disposition` equals `attachment`
And the response is delivered within 100 ms (NFR-2)

---

## Feature: Path traversal sandbox (Spec refs: FR-3, FR-4, NFR-4, AC-3)

### Scenario: AC-3 — traversal attempts return single 404 (no 403/404 split)
Given the FastAPI backend is running
When a client issues `GET http://127.0.0.1:8765/api/file?path=../etc/passwd`
Then the response status is exactly `404` (NOT `403`)
And the response body does not enumerate whether the file exists outside the tree
When a client issues `GET http://127.0.0.1:8765/api/file?path=specs/../../etc/passwd`
Then the response status is exactly `404`
And the response body is identical in shape to the previous request (no enumeration side-channel)

---

## Feature: Windows reserved device names (Spec refs: FR-4, AC-4)

### Scenario: AC-4 — CON.md inside the exposed tree returns 404
Given the backend is running on Windows
When a client issues `GET http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/CON.md`
Then the response status is `404`
And no file is opened on disk (the request is rejected by `safe_resolve` before any open() call)
And the rejection also applies to `PRN.md`, `AUX.md`, `NUL.md`, `COM1.md`..`COM9.md`, `LPT1.md`..`LPT9.md`, including extension variants

---

## Feature: Alternate Data Stream rejection (Spec refs: FR-4, AC-5)

### Scenario: AC-5 — ::$DATA suffix returns 404
Given the file `specs/development/spec_driven/final_specs/spec.md` exists
When a client issues `GET http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/spec.md::$DATA`
Then the response status is `404` (NOT `200`)
And the rejection also applies to any path containing `:stream` or `::$DATA` at any segment

---

## Feature: Reparse point (junction) rejection (Spec refs: FR-4, NFR-5, AC-6)

### Scenario: AC-6 — junction inside specs/ pointing outside the tree returns 404
Given a junction has been created at `specs/development/spec_driven/escape` pointing to `C:/Windows/`
And the junction is detectable via `GetFileAttributesW` returning `FILE_ATTRIBUTE_REPARSE_POINT`
When a client issues `GET http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/escape/win.ini`
Then the response status is `404`
And `safe_resolve` rejected the path because at least one segment is a reparse point (junction or symlink)
And no bytes from `C:/Windows/win.ini` appear in the response body

---

## Feature: File-size cap on read (Spec refs: FR-3, AC-7)

### Scenario: AC-7 — files larger than 1 MB return 413
Given a fixture file `specs/development/spec_driven/findings/huge_fixture.md` exists with size 1,572,864 bytes (1.5 MB)
When a client issues `GET http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/findings/huge_fixture.md`
Then the response status is `413`
And the response body shape is `{detail: ...}` (FastAPI default for HTTP errors)
And the file content is NOT included in the response body

---

## Feature: Extension whitelist on read (Spec refs: FR-3, AC-8)

### Scenario: AC-8 — disallowed extensions return 415
Given a fixture file `specs/development/spec_driven/findings/sample.exe` exists on disk
When a client issues `GET http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/findings/sample.exe`
Then the response status is `415`
And the file content is NOT included in the response body
And the same status is returned for `.svg`, `.bat`, `.dll`, `.html` (SVG explicitly excluded per NFR-9)

---

## Feature: PUT round-trip (Spec refs: FR-6, NFR-10, AC-9)

### Scenario: AC-9 — PUT then GET returns the same content
Given the file `specs/development/spec_driven/findings/scratch.md` exists or is creatable inside the EXPOSED_TREE
When a client issues `PUT http://127.0.0.1:8765/api/file` with header `Origin: http://127.0.0.1:8765` and JSON body `{"path": "specs/development/spec_driven/findings/scratch.md", "content": "x"}`
Then the response status is `200`
And the JSON body has shape `{path, bytes, mtime}` with `bytes == 1`
And the write was atomic (temp file + `os.replace`) — verifiable by absence of partial-write artifacts
When a client immediately issues `GET http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/findings/scratch.md`
Then the response status is `200`
And `body.content == "x"`

---

## Feature: PUT body size cap (Spec refs: FR-7, AC-10)

### Scenario: AC-10 — PUT body >1 MB returns 413 with kind too_large
Given the FastAPI backend is running with the 1 MB body cap configured
When a client issues `PUT http://127.0.0.1:8765/api/file` with header `Origin: http://127.0.0.1:8765` and a JSON body whose `content` field is 1,572,864 bytes (1.5 MB)
Then the response status is `413`
And the JSON body equals `{"detail": {"kind": "too_large"}}`
And no file on disk was modified

---

## Feature: Origin / Host validation (CSRF defense) (Spec refs: FR-9, NFR-7, AC-11)

### Scenario: AC-11 — PUT from foreign Origin returns 403
Given the FastAPI backend is bound on `127.0.0.1:8765`
When a client issues `PUT http://127.0.0.1:8765/api/file` with headers `Origin: http://evil.example.com` and `Host: 127.0.0.1:8765` and JSON body `{"path": "specs/development/spec_driven/findings/scratch.md", "content": "y"}`
Then the response status is `403`
And no file on disk was modified
When a client issues the same `PUT` with `Origin: http://127.0.0.1:8765` and `Host: evil.example.com`
Then the response status is `403`
And the same protection applies to `POST /api/regen-prompt`, `POST /api/promote`, and `DELETE /api/promote`

---

## Feature: HTTP verb whitelist (Spec refs: NFR-6, AC-12)

### Scenario: AC-12 — PATCH and DELETE on /api/file return 405
Given the FastAPI backend is running
When a client issues `PATCH http://127.0.0.1:8765/api/file` with any body
Then the response status is `405`
And the response carries `Allow: GET, PUT` (or equivalent) in the header
When a client issues `DELETE http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/findings/scratch.md`
Then the response status is `405`
And the file on disk is unchanged

---

## Feature: Regen prompt assembly contract (Spec refs: FR-10, FR-11, FR-12, AC-13)

### Scenario: AC-13 — POST /api/regen-prompt returns the documented response shape with size policy
Given `GET /api/stages?project_type=development&project_name=spec_driven` returns the canonical six-stage definition
When a client issues `POST http://127.0.0.1:8765/api/regen-prompt` with `Origin: http://127.0.0.1:8765` and JSON body `{"project_type": "development", "project_name": "spec_driven", "stages": ["interview"], "modules": {"interview": ["qa"]}, "autonomous": false}`
Then the response status is `200`
And the response JSON has all six keys: `prompt`, `warning`, `selected_stages_count`, `follow_ups_count`, `autonomous`, `bytes`
And `selected_stages_count == 1`
And `autonomous == false`
And `bytes == len(prompt.encode("utf-8"))`
And when `bytes <= 50000`, `warning == null`
When the same client issues a `POST` selecting all six stages (which inflates the prompt above 50 KB but below 1 MB)
Then the response status is `200`
And `warning` is a non-null human-readable string
And `prompt` is emitted in full (no truncation, per NFR-11)
When the same client issues a `POST` whose assembled body would exceed 1,048,576 bytes
Then the response status is `413`
And the JSON body equals `{"detail": {"kind": "too_large", "bytes": <count>}}`

---

## Feature: Autonomous-mode header (Spec refs: FR-11(a), FR-11(b), AC-14)

### Scenario: AC-14 — autonomous=true emits the AUTONOMOUS header and verbatim imperative line
Given a client posts to the regen-prompt endpoint with `autonomous: true`
When the response is received
Then `body.prompt` starts (after stripping leading whitespace) with the literal first line `# EXECUTION MODE: AUTONOMOUS`
And the next non-blank line is verbatim: `Do not call AskUserQuestion. For anything unclear, use your best judgment, record the choice inline in the artifact, and keep going. Produce every requested artifact below in this single turn before stopping.`
And `body.autonomous == true`

---

## Feature: Interactive-mode default (Spec refs: FR-11(a), AC-15)

### Scenario: AC-15 — autonomous=false emits the INTERACTIVE header without the imperative line
Given a client posts to the regen-prompt endpoint with `autonomous: false`
When the response is received
Then `body.prompt` starts (after stripping leading whitespace) with the literal first line `# EXECUTION MODE: INTERACTIVE`
And the AUTONOMOUS imperative sentence (`Do not call AskUserQuestion...`) does NOT appear in `body.prompt`
And `body.autonomous == false`

---

## Feature: Read-zero contract in Constraints (Spec refs: FR-11(g), AC-16)

### Scenario: AC-16 — Constraints section names the read-zero contract verbatim
Given a client posts to the regen-prompt endpoint with any selection
When the response is received
Then `body.prompt` contains a `### Constraints` section
And that section contains the substring `regeneration deletes prior outputs first; new generation reads only the inputs.`
And the same section also references: `CLAUDE.md`, the parent-direct manager-spawn contract, `regen.delete.planned`, `regen.delete.completed`, `regen.write.completed`

---

## Feature: Pin survives in assembled prompt (Spec refs: FR-11(f), Section 7, AC-17)

### Scenario: AC-17 — non-empty interview/promoted.md is inlined under Pinned items
Given `specs/development/spec_driven/interview/promoted.md` exists on disk and contains pin-001 (the verbatim text from the file)
When a client issues `POST http://127.0.0.1:8765/api/regen-prompt` selecting `stages: ["interview"]`
Then the response status is `200`
And `body.prompt` contains a section header beginning `### Pinned items (MUST survive regeneration)`
And every non-empty line of `interview/promoted.md` (excluding the management-instructions header lines if the assembler chooses) appears verbatim in `body.prompt` between that header and the next `###` header
And in particular the substring `All discovered (Recommended)` appears verbatim in `body.prompt`

---

## Feature: Deep-link to qa.md mounts QaView (Spec refs: FR-17, FR-18, FR-29, AC-18)

### Scenario: AC-18 — deep link renders QaView with Q/A blocks
Given the SPA is built and served at `http://127.0.0.1:8765/`
And `specs/development/spec_driven/interview/qa.md` exists with at least one `## Round N` containing `### category` containing one `- Q:` and one `- A:` line
When a browser navigates to `http://127.0.0.1:8765/file/specs/development/spec_driven/interview/qa.md`
Then the SPA boots without redirect
And the DOM contains exactly one `<main>` element whose innerText length > 0
And the DOM contains exactly one element with `data-testid="qa-view"`
And the DOM contains at least one element with `data-testid="qa-q-block"` carrying a blue-tint class (e.g., `qa-tint-q`)
And the DOM contains at least one element with `data-testid="qa-a-block"` carrying a green-tint class (e.g., `qa-tint-a`)
And `window.console.error` calls collected from page load equal `[]`

---

## Feature: Autonomous-mode Q/A regex acceptance (Spec refs: FR-21, AC-19)

### Scenario: AC-19 — autonomous-mode A line parses inside QaView (no Error Boundary fallback)
Given a fixture qa.md exists at `specs/development/spec_driven/interview/qa_autonomous_fixture.md` containing a Round/category with the line `- A *(judgment call — chose All discovered because spec_driven is the first; others appear when present)*: All discovered.`
When a browser navigates to `http://127.0.0.1:8765/file/specs/development/spec_driven/interview/qa_autonomous_fixture.md`
Then the DOM contains an element with `data-testid="qa-view"`
And the DOM does NOT contain the Error Boundary banner text `Could not parse structured Q/A view`
And the autonomous A block's parsed text equals `All discovered.` (the parenthetical judgment-call note may render as a sibling annotation but is not part of the answer text)
And `window.console.error` calls equal `[]`

---

## Feature: Error-Boundary fallback path (Spec refs: FR-19, FR-20, AC-20)

### Scenario: AC-20 — malformed qa.md falls back to MarkdownView with a banner
Given a fixture qa.md exists at `specs/development/spec_driven/interview/qa_malformed_fixture.md` whose contents are not parseable by the structured QaView parser (e.g., missing the `## Round N` header but otherwise valid markdown)
When a browser navigates to `http://127.0.0.1:8765/file/specs/development/spec_driven/interview/qa_malformed_fixture.md`
Then the DOM does NOT contain `data-testid="qa-view"`
And the DOM contains the literal banner text starting with `Could not parse structured Q/A view; rendering raw markdown. (cause:`
And the DOM contains a MarkdownView region rendering the raw markdown content
And `window.console.error` calls equal `[]` (the React Error Boundary catches the parse error cleanly)
And the `<main>` element's innerText length > 0

---

## Feature: Broken-link rendering (Spec refs: FR-24, AC-21)

### Scenario: AC-21 — relative link to a non-existent file renders as muted span (NOT anchor)
Given a markdown file `specs/development/spec_driven/findings/broken_link_fixture.md` exists containing `[ghost](./does-not-exist.md)`
When a browser navigates to `http://127.0.0.1:8765/file/specs/development/spec_driven/findings/broken_link_fixture.md`
Then the DOM contains a `<span>` element matching `span.link-broken[aria-disabled="true"]` whose visible text is `ghost`
And that span carries a `title` attribute whose value is `file not found` (or the matching cause string from FR-24's enum: `outside exposed tree`, `case mismatch`, `anchor not in document`)
And the DOM does NOT contain an `<a>` element with `href` resolving to `./does-not-exist.md`
And clicking the span produces no navigation event (no URL change)

---

## Feature: Regen panel default-collapsed (Spec refs: FR-33, AC-22)

### Scenario: AC-22 — Regenerate <details> is closed on first render of a stage file
Given the SPA is at `http://127.0.0.1:8765/`
And the user has not previously interacted with the panel for this file
When a browser navigates to `http://127.0.0.1:8765/file/specs/development/spec_driven/final_specs/spec.md`
Then the DOM contains a `<details>` element whose `<summary>` text is `Regenerate`
And that `<details>` element does NOT have the `open` attribute (closed on first render)
And the module checkboxes (FR-33(a)) are NOT visible in the rendered region until the user clicks the summary

---

## Feature: Regen prompt visible-after-build (Spec refs: FR-33, FR-11, AC-23)

### Scenario: AC-23 — clicking Build prompt renders the prompt inline with header bar and breakdown
Given the user has opened the Regenerate panel on `/file/specs/development/spec_driven/final_specs/spec.md`
And the module checkboxes default to all checked
When the user clicks the `Build prompt` button
And `POST http://127.0.0.1:8765/api/regen-prompt` returns `200` with a non-empty `prompt` and `warning == null` and (e.g.) `selected_stages_count == 1`, `follow_ups_count == 0`, `autonomous == false`, `bytes == 12345`
Then the DOM contains exactly one element matching `.regen-prompt-block`
And that element contains a header bar with the title `Assembled prompt`
And the header bar contains an input `<input type="checkbox">` with label `Wrap` whose `checked === true` (default ON)
And the header bar contains a `<button>` with visible text `Copy` styled as primary (e.g., `.btn-primary`)
And the `.regen-prompt-block` body is a `<pre>` element whose innerText equals `body.prompt`
And the `.regen-prompt-block` is NOT wrapped in an inner `<details>` element
And the actions row beside `Build prompt` shows the breakdown line `1 stages selected, 0 follow-ups inlined, autonomous=false, 12.06 KB` (or locale-equivalent formatting)

---

## Feature: Copy button label flip (Spec refs: FR-33(f), NFR-15, AC-24)

### Scenario: AC-24 — clicking Copy copies prompt to clipboard and flips label for ~1.5s
Given the assembled prompt block is visible per AC-23
And browser clipboard permission has been granted to `http://127.0.0.1:8765`
When the user clicks the `Copy` button
Then the browser clipboard contains the exact string equal to `body.prompt` from the most recent `/api/regen-prompt` response (verifiable by `navigator.clipboard.readText()`)
And the button's visible label flips from `Copy` to `Copied!` within 50 ms
And the button carries `aria-live="polite"`
And the button has a CSS `min-width` (e.g., 90 px) so the layout does NOT shift when the label flips
And approximately 1500 ms (±200 ms) after the click, the label flips back to `Copy`

---

## Feature: Wrap toggle (Spec refs: FR-33(f), AC-25)

### Scenario: AC-25 — Wrap toggle controls <pre> soft-wrap and is not persisted
Given the assembled prompt block is visible with the `Wrap` checkbox `checked`
And the `<pre>` body has computed style `white-space: pre-wrap` and `word-break: break-word`
When the user clicks the `Wrap` checkbox to uncheck it
Then the `<pre>` body computed style switches to `white-space: pre` (or equivalent fixed-width) with horizontal scroll enabled
And `localStorage.getItem("spec_driven.regen_wrap")` (or any similar key) returns `null` — wrap state is NOT persisted
When the user re-checks the `Wrap` toggle
Then the `<pre>` reverts to `white-space: pre-wrap; word-break: break-word`
When the page is reloaded
Then the `Wrap` checkbox is `checked` (default ON, per FR-33(f))

---

## Feature: Autonomous-mode toggle persistence (Spec refs: FR-33(b), FR-35, AC-26)

### Scenario: AC-26 — autonomous toggle writes to localStorage and propagates cross-tab
Given the SPA is open in tab A at `/file/specs/development/spec_driven/final_specs/spec.md`
And `localStorage["spec_driven.autonomous_mode.v1"]` is initially `null` or `"false"`
When the user opens the Regenerate panel and clicks the `Autonomous mode` toggle ON
Then `localStorage["spec_driven.autonomous_mode.v1"]` equals `"true"`
And the in-process subscription updates any other consumer mounted in the same tab (e.g., the project-page Regenerate panel)
When the page is reloaded in tab A
Then the `Autonomous mode` toggle is rendered in the ON state
When tab B is opened to `/project/development/spec_driven` while tab A is still open
And the user toggles autonomous mode OFF in tab B
Then a `storage` event fires in tab A
And tab A's `Autonomous mode` toggle re-renders to OFF without manual reload
And `localStorage["spec_driven.autonomous_mode.v1"]` equals `"false"` in both tabs

---

## Feature: Project parent page (Spec refs: FR-15, FR-34, AC-27)

### Scenario: AC-27 — /project/development/spec_driven shows six stages and a master Regenerate panel
Given the SPA is at `http://127.0.0.1:8765/`
When a browser navigates to `http://127.0.0.1:8765/project/development/spec_driven`
Then the DOM renders a heading containing `spec_driven` and the task type `development`
And exactly six stage sections are visible with labels including `intake`, `interview`, `research`, `spec compilation`, `validation strategy`, `execution + streaming validation` (matching `GET /api/stages` `id`/`label`)
And each stage section contains module checkboxes for that stage (default all checked)
And the page contains exactly one master Regenerate panel (a `<details title="Regenerate">` or equivalent)
And clicking `Build prompt` in the master panel issues `POST /api/regen-prompt` with `stages` containing every selected stage id and `modules` containing every selected module id per stage
And the same Copy / Wrap / breakdown / warning contract from FR-33 applies (one combined prompt for all selected stages)

---

## Feature: Boot smoke (Spec refs: FR-38, FR-39, AC-28)

### Scenario: AC-28 — make run-prod boots the server and the SPA loads at 127.0.0.1:8765
Given a clean checkout at `C:/workspace/spec_coding/projects/spec_driven/`
And `make build-frontend` has been run, producing `backend/static/index.html`
When the user runs `make run-prod` in `projects/spec_driven/`
Then a single uvicorn process starts and binds to `127.0.0.1:8765` (NOT `0.0.0.0`)
And the boot log contains `Uvicorn running on http://127.0.0.1:8765`
When a client issues `GET http://127.0.0.1:8765/api/tree`
Then the response status is `200`
And the JSON body has the recursive `{name, path, type, children}` shape from AC-1
When a browser navigates to `http://127.0.0.1:8765/`
Then the SPA's HTML loads and the React app mounts
And the DOM contains `data-testid="sidebar"` with at least one `data-testid="tree-leaf"` under each top-level section
And the initial app load (HTML + JS + first /api/tree + first /api/file) completes within 2000 ms (NFR-3)

---

## Feature: Localhost-only bind (Spec refs: FR-38, NFR-7, AC-29)

### Scenario: AC-29 — make run binds to 127.0.0.1:8765 and never 0.0.0.0
Given the user runs `make run` in `projects/spec_driven/`
When uvicorn starts
Then the boot log contains `Uvicorn running on http://127.0.0.1:8765`
And the boot log does NOT contain the substring `0.0.0.0`
And `grep -R "0.0.0.0" projects/spec_driven/backend/` (or PowerShell equivalent) returns no matches in any default-invocation config file (Makefile target, `main.py`, uvicorn run config)
When a different machine on the LAN attempts `GET http://<LAN-IP>:8765/api/tree`
Then the request fails to connect (the socket is bound only to the loopback interface)

---

## Feature: Pin preservation (Spec refs: Section 7, FR-11(f), AC-17)

### Scenario: pin-001 from interview/promoted.md appears verbatim in regenerated interview/qa.md
Given `specs/development/spec_driven/interview/promoted.md` exists on disk and contains the pin-001 block, including the verbatim Q line `**Q:** Section 2 ("Projects") — which projects appear in the tree?` and the verbatim A line `- A: All discovered (Recommended) — backend walks ` followed by the rest of the answer text up to the trailing period
And a regeneration of stage 2 (interview) has just completed (per the read-zero contract: prior `interview/qa.md` was deleted, new `interview/qa.md` written from inputs + `interview/promoted.md`)
When a reader opens `specs/development/spec_driven/interview/qa.md`
Then the file contains the substring `Section 2 ("Projects") — which projects appear in the tree?` verbatim under a `## Round 1` block in a `### functional-scope` category
And the file contains the substring `All discovered (Recommended) — backend walks` verbatim within the same Q/A block, prefixed by `- A:` (interactive form per FR-21)
And the substring `spec_driven` is just the first; `ai_video` etc. appear automatically when present.` appears verbatim in the same A line
And no `## Pinned items (orphaned)` section exists in `interview/qa.md` (the natural insertion point — Round 1 / functional-scope — was preserved during regeneration)
And whitespace normalization (collapsing runs of spaces / line endings) is permitted when comparing, but no token from the pinned text is altered or omitted
