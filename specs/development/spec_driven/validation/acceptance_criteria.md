# Acceptance Criteria — spec_driven (Gherkin)

Run: spec_driven-20260502-clean
Stage: 5 (Validation strategy — acceptance_criteria level)
Source spec: `C:\workspace\spec_coding\specs\development\spec_driven\final_specs\spec.md`
Inputs read: spec.md only. No prior validation/*.md files were read (read-zero contract per CLAUDE.md).

## Feature: Frontend routing

### Scenario: AC-1 — First open redirects to spec.md and expands its ancestor chain

Given the backend is running on `http://localhost:8765/` with `REPO_ROOT` resolved
And the file `C:\workspace\spec_coding\specs\development\spec_driven\final_specs\spec.md` exists on disk
When the user navigates a browser to `http://localhost:8765/`
Then the SPA replaces the URL with `http://localhost:8765/file/specs/development/spec_driven/final_specs/spec.md`
And the reader pane renders the markdown content of `final_specs/spec.md`
And the sidebar tree node for `Projects > development > spec_driven > final_specs` has `aria-expanded="true"`
And the leaf node for `spec.md` has `aria-selected="true"`
And if `final_specs/spec.md` is absent at startup the redirect target instead becomes `http://localhost:8765/file/specs/development/spec_driven/user_input/revised_prompt.md`

Spec refs: FR-15, AC-1

### Scenario: AC-4 — Relative cross-file markdown link navigates in-app and updates URL

Given the user is at `http://localhost:8765/file/specs/development/spec_driven/final_specs/spec.md`
And `spec.md` contains a relative markdown link with `href="../findings/dossier.md"`
And the file `C:\workspace\spec_coding\specs\development\spec_driven\findings\dossier.md` exists inside `EXPOSED_TREE`
When the user clicks that link
Then the browser does not perform a full-page navigation
And the URL becomes `http://localhost:8765/file/specs/development/spec_driven/findings/dossier.md` via push-history
And the reader pane re-renders with `dossier.md` content
And the sidebar leaf for `dossier.md` becomes `aria-selected="true"` while the prior leaf loses that attribute
And clicking the browser Back button restores the previous URL and re-renders `spec.md`

Spec refs: FR-15, FR-17, FR-33 (case 3 internal), AC-4

## Feature: Frontend sidebar

### Scenario: AC-2 — All five stage subfolders are clickable and contain at least one renderable file

Given the user is on any URL under `/file/specs/development/spec_driven/...`
And the sidebar has rendered the project node `Projects > development > spec_driven`
When the user clicks each of the five stage folders (`user_input`, `interview`, `findings`, `final_specs`, `validation`) in turn
Then each folder toggles `aria-expanded` from `"false"` to `"true"` without triggering navigation
And each folder lists at least one leaf file
And clicking any one of those leaf files updates the URL to `http://localhost:8765/file/specs/development/spec_driven/{stage}/{filename}` (push-history)
And the reader pane renders that file's contents

Spec refs: FR-7, FR-8, FR-22, FR-26, FR-38, AC-2

### Scenario: AC-11 — Missing stage subfolder renders as muted-italic non-focusable leaf

Given the project `specs/development/spec_driven/` has no `validation/` directory on disk
When `GET /api/tree` returns and the sidebar renders that project
Then the `validation` stage entry is present in the response with `present: false` and an empty file list
And the sidebar row for `validation` carries the muted-italic visual styling
And its `title` attribute equals `"not yet generated"`
And the row is not expandable (no twisty caret) and cannot receive focus via Up/Down arrow keys in the tree
And clicking the row does not change the URL

Spec refs: FR-9, FR-24, FR-38, AC-11

### Scenario: AC-12 — Refresh button re-fetches the tree and surfaces newly added files

Given the sidebar tree has been rendered for project `spec_driven`
And `final_specs/spec.md` is the only file under `final_specs/`
When the user externally creates `C:\workspace\spec_coding\specs\development\spec_driven\final_specs\appendix.md`
And the user clicks the sidebar's `Refresh` button at the top of the tree
Then the frontend issues a fresh `GET http://localhost:8765/api/tree` request
And the response contains a leaf for `appendix.md` under `final_specs`
And the sidebar re-renders so that `appendix.md` is visible under `final_specs` in alphabetical position

Spec refs: FR-3, FR-7, FR-8, FR-28, AC-12

### Scenario: AC-13 — Reload restores URL-driven selection and prior collapse state from localStorage

Given the user previously expanded `Projects > development > spec_driven > findings`, collapsed `interview`, and last selected `findings/dossier.md`
And the key `spec_driven.sidebar.v1` in `localStorage` reflects that collapse state and last-selected path
When the user reloads `http://localhost:8765/file/specs/development/spec_driven/findings/dossier.md`
Then the SPA reads `spec_driven.sidebar.v1` from `localStorage` without throwing on parse
And `findings` is rendered with `aria-expanded="true"` and `interview` with `aria-expanded="false"`
And the leaf for `dossier.md` is `aria-selected="true"` because the URL takes precedence over the saved last-selected path
And if `localStorage["spec_driven.sidebar.v1"]` is corrupt JSON the SPA falls back to default collapse state with no console error

Spec refs: FR-22, FR-23, AC-13

### Scenario: AC-14 — Tree keyboard navigation matches W3C ARIA APG TreeView with single tab stop

Given the sidebar tree has rendered with the focused node carrying `tabindex="0"` and all other nodes carrying `tabindex="-1"`
When the user presses Tab from outside the tree
Then exactly one tree node receives focus (single tab stop)
When the user presses Down arrow on a visible node
Then focus moves to the next visible node and `tabindex` rolls accordingly
When the user presses Right arrow on a collapsed folder
Then the folder expands (`aria-expanded` flips to `"true"`); pressing Right again moves focus to its first child
When the user presses Left arrow on an expanded folder
Then the folder collapses (`aria-expanded` flips to `"false"`); pressing Left on a leaf or collapsed folder moves focus to its parent
When the user presses Enter on a focused leaf
Then the URL updates via push-history to that file's `/file/...` path; pressing Enter on a folder is a no-op
And Home focuses the first visible node, End focuses the last visible node

Spec refs: FR-18, FR-19, NFR-9, AC-14

## Feature: Frontend Section 1 — Settings & Shared Context

### Scenario: AC-3 — All three Section 1 file kinds are clickable and render correctly

Given the sidebar has rendered Section 1 with the three always-expanded subgroups `CLAUDE.md`, `Agents`, and `Skills`
When the user clicks the leaf `CLAUDE.md`
Then the URL becomes `http://localhost:8765/file/CLAUDE.md` and the reader pane renders the content of `C:\workspace\spec_coding\CLAUDE.md`
When the user clicks any leaf under `Agents` (e.g., `agent_team__interview_manager.md`)
Then the URL becomes `http://localhost:8765/file/.claude/agents/agent_team__interview_manager.md` and the reader pane renders that file
When the user clicks any leaf under `Skills` (e.g., the `agent_team` entry)
Then the URL becomes `http://localhost:8765/file/.claude/skills/agent_team/SKILL.md` and the reader pane renders that file
And the breadcrumb above the reader reads `Settings / {kind} / {filename}` with the last segment carrying `aria-current="page"`

Spec refs: FR-1, FR-7 (settings), FR-21, FR-29, AC-3

## Feature: Reader / link rendering

### Scenario: AC-5 — Markdown link to a non-existent file renders muted with tooltip and is not a clickable anchor

Given the user is viewing `http://localhost:8765/file/specs/development/spec_driven/final_specs/spec.md`
And `spec.md` contains a relative link with `href="../validation/strategy.md"`
And `C:\workspace\spec_coding\specs\development\spec_driven\validation\strategy.md` does not exist on disk
When the reader resolves links per FR-33
Then the link is rendered as `<span class="link-broken" aria-disabled="true">` (NOT an `<a>` element)
And its `title` attribute equals `"file not found"`
And it has muted styling with no underline
And clicking the span causes no URL change and no navigation

Spec refs: FR-33 (case 3 broken-missing), FR-34, AC-5

### Scenario: AC-6 — External `https://` link renders with new-tab semantics and sr-only suffix

Given the user is viewing any markdown file in the reader
And that file contains a markdown link with `href="https://example.com"`
When the reader renders the link per FR-33 case 1
Then the rendered DOM is an `<a>` element with `href="https://example.com"`, `target="_blank"`, and `rel="noopener noreferrer"`
And the link is followed by a `<span class="sr-only">(opens in new tab)</span>`
And clicking the link opens `https://example.com` in a new browser tab without affecting the SPA URL

Spec refs: FR-33 (case 1 external), AC-6

## Feature: Backend file API

### Scenario: AC-7 — Path-traversal request returns 400 outside_sandbox

Given the backend is running with `REPO_ROOT` resolved to `C:\workspace\spec_coding`
When a client issues `GET http://localhost:8765/api/file?path=../../../etc/hosts`
Then `safe_resolve` raises `ValueError` because the resolved path is not under `REPO_ROOT`
And the response status is `400`
And the response JSON body contains the structured error key `outside_sandbox`
And no file content is returned

Spec refs: FR-5.1, FR-6, NFR-4, AC-7

### Scenario: AC-8 — Non-whitelisted extension returns 415 unsupported_extension

Given the backend is running
And a file `foo.png` notionally exists somewhere inside `EXPOSED_TREE`
When a client issues `GET http://localhost:8765/api/file?path=foo.png`
Then the response status is `415`
And the response JSON body contains the structured error key `unsupported_extension`
And no file bytes are read or returned

Spec refs: FR-5.4, AC-8

### Scenario: AC-9 — `.md` file containing NUL bytes returns 415 binary_content

Given a file `C:\workspace\spec_coding\specs\development\spec_driven\user_input\raw_prompt.md` exists inside `EXPOSED_TREE`
And the file's bytes contain at least one `\x00` character
When a client issues `GET http://localhost:8765/api/file?path=specs/development/spec_driven/user_input/raw_prompt.md`
Then the backend reads with `encoding="utf-8", errors="replace"` and detects `\x00` in the result
And the response status is `415`
And the response JSON body contains the structured error key `binary_content`

Spec refs: FR-5.6, NFR-13, AC-9

### Scenario: AC-10 — File larger than 2 MB returns 413 too_large

Given a file `specs/development/spec_driven/findings/big.md` exists inside `EXPOSED_TREE` and exceeds 2 MB on disk
When a client issues `GET http://localhost:8765/api/file?path=specs/development/spec_driven/findings/big.md`
Then the size check trips before content read
And the response status is `413`
And the response JSON body contains the structured error key `too_large`

Spec refs: FR-5.5, NFR-15, AC-10

### Scenario: AC-15 — Concurrent file removal during tree-walk does not produce 500

Given Claude Code is mid-write on `specs/development/spec_driven/interview/qa.md` and the file is removed during a tree-walk
When the backend is computing `GET /api/tree` and a stat call raises `FileNotFoundError`
Then the walker catches the EAFP error and silently skips the entry (or re-stats)
And the `GET /api/tree` response status is `200`
And no `500` is emitted
When a follow-up client request is `GET http://localhost:8765/api/file?path=specs/development/spec_driven/interview/qa.md`
Then the handler catches `FileNotFoundError` and returns `404` with JSON `kind: "file_removed"` (not 500)

Spec refs: FR-3, FR-5.7, NFR-12, AC-15

### Scenario: AC-23 — Verb whitelist on `/api/file` rejects PATCH and DELETE with 405

Given the backend is running
When a client issues `PATCH http://localhost:8765/api/file?path=specs/development/spec_driven/final_specs/spec.md`
Then the response status is `405`
When a client issues `DELETE http://localhost:8765/api/file?path=specs/development/spec_driven/final_specs/spec.md`
Then the response status is `405`
And only `GET`, `PUT`, and `POST` (the latter only on dedicated endpoints) are sanctioned mutation/read verbs
And no DELETE/upload/create-new-file endpoint exists in the OpenAPI surface

Spec refs: NFR-6, AC-23

## Feature: Editor

### Scenario: AC-16 — Editor save succeeds atomically, dirty dot clears, "Saved." announces

Given the user is viewing `http://localhost:8765/file/specs/development/spec_driven/final_specs/spec.md` in rendered mode
When the user clicks the `✎ Edit` button
Then the rendered view is replaced by a textarea editor with a toolbar containing `Save`, `Discard`, and `Close-editor`
And the `Save` button is disabled while `currentText === lastSavedText`
When the user types changes so that `currentText !== lastSavedText` (computed via deep equality, not a "user typed" flag)
Then the badge `Unsaved changes` appears AND a filled-circle dirty-dot with class `editor-dirty-dot` lights near the file path
And the `Save` button becomes enabled
When the user presses `Ctrl+S`
Then the frontend issues `PUT http://localhost:8765/api/file` with JSON body `{path: "specs/development/spec_driven/final_specs/spec.md", text: <currentText>}`
And the backend writes via `tempfile.mkstemp` + `os.fsync` + `os.replace()` atomically (temp sibling in the same directory)
And the response status is `200`
And `lastSavedText` is updated to the just-saved value, `editor-dirty-dot` clears, the badge disappears
And the text `Saved.` is announced via an aria-live region
And the editor remains open (closing is an explicit user action)

Spec refs: FR-14a, FR-40, AC-16

### Scenario: AC-17 — Editor save failure (415) renders persistent inline banner; dirty dot stays lit

Given the user has edited a file in the editor and the dirty-dot is lit
When the user presses `Ctrl+S` and the backend responds `415` with JSON `{kind: "unsupported_extension"}` (e.g., the file extension is not in the whitelist)
Then the frontend renders a persistent inline banner above the textarea naming the structured error key `unsupported_extension`
And the banner does NOT auto-dismiss (no toast, no modal)
And the `editor-dirty-dot` element remains lit
And `lastSavedText` is unchanged
And the user can fix the situation and re-save; only an actually-successful save clears the banner and the dot

Spec refs: FR-14a (error mapping), FR-40 (persistent banner), AC-17

### Scenario: AC-18 — `interview/qa.md` renders as colored Q/A blocks with per-block ✎ editing

Given the user navigates to `http://localhost:8765/file/specs/development/spec_driven/interview/qa.md`
And `qa.md` follows the `## Round N` → `### {category}` → `**Q:**` → `- A:` structure
When the reader detects the path matches `*/interview/qa.md`
Then the rendered view is the structured Q/A view (NOT generic markdown)
And rounds, categories, and Q/A pairs render as discrete blocks
And question blocks use one tint, answer blocks use a different tint, and each category gets a small badge above its block group
And each `Q` and each `A` block carries its own `✎` pencil control
When the user clicks the pencil on a single answer block
Then an inline editor opens scoped to that block (the rest of the file remains rendered)
When the user saves the inline edit
Then the frontend splices the new text into the block and writes the whole file via `PUT http://localhost:8765/api/file` with `{path: "specs/development/spec_driven/interview/qa.md", text: <whole-file>}`
And whole-file editing is still available via the file-level `✎ Edit` toggle
And if the parser fails on the file's structure, the view falls back to generic markdown rendering with no error UI

Spec refs: FR-14a, FR-40, FR-41, AC-18

## Feature: Regeneration

### Scenario: AC-19 — `POST /api/regen-prompt` returns the contracted shape with size policy

Given the backend is running and project `development/spec_driven` exists
When a client issues `POST http://localhost:8765/api/regen-prompt` with JSON body `{project_type: "development", project_name: "spec_driven", stages: ["spec_compilation"], modules: {"spec_compilation": ["final_specs/spec.md"]}, autonomous: false}`
Then the response status is `200`
And the response body has all six keys: `prompt: string`, `warning: string | null`, `selected_stages_count: number`, `follow_ups_count: number`, `autonomous: bool`, `bytes: number`
And when the assembled `prompt` byte length is ≤ 50 KB the `warning` field is `null`
And when the assembled `prompt` byte length is > 50 KB the `warning` field is a non-empty string and the prompt is still emitted in full (warn-don't-truncate)
And when the assembled prompt would exceed 1 MB the response status is `413` with the structured error key `too_large` and no prompt field

Spec refs: FR-14c (size policy), AC-19

### Scenario: AC-20 — Autonomous-mode prompt opens with the exact header and verbatim imperative line

Given the user has set the autonomous-mode toggle to true (persisted in `localStorage["spec_driven.autonomous_mode.v1"] = "true"`)
When the frontend issues `POST http://localhost:8765/api/regen-prompt` with `autonomous: true`
Then the response `prompt` field's first non-blank line is exactly `# EXECUTION MODE: AUTONOMOUS`
And the next non-blank line is the verbatim imperative sentence: `Do not call AskUserQuestion. For anything unclear, use your best judgment, record the choice inline in the artifact, and keep going. Produce every requested artifact below in this single turn before stopping.`
And when `autonomous: false` the header line is instead exactly `# EXECUTION MODE: INTERACTIVE` (no imperative sentence)

Spec refs: FR-14c (a)(b), AC-20

### Scenario: AC-21 — Every assembled prompt's `### Constraints` section includes the read-zero contract

Given any valid `POST http://localhost:8765/api/regen-prompt` request (autonomous true OR false)
When the response is assembled
Then the `prompt` body contains a `### Constraints` section
And that section includes references to `CLAUDE.md`, the canonical paths, the manager-spawn contract, the no-AskUserQuestion-in-autonomous-mode rule (when autonomous), AND the read-zero contract (regeneration deletes prior outputs first; new generation reads only the inputs)
And the read-zero constraint text is present regardless of which stages or modules were selected

Spec refs: FR-14c (f), AC-21

### Scenario: AC-22 — Project page exposes six stages with module checkboxes and a master Regenerate panel

Given the user navigates to `http://localhost:8765/project/development/spec_driven`
When the page loads
Then the SPA fetches `GET http://localhost:8765/api/stages?project_type=development&project_name=spec_driven`
And the page lists all six canonical stages with their labels, folders, and modules
And each module has a checkbox (default checked) bound to the master Regenerate panel
And the user can select any subset of stages and modules
And an `Autonomous mode` toggle persists in `localStorage["spec_driven.autonomous_mode.v1"]` and is the same value as on per-stage panels (synced via `storage` events for cross-tab and an in-process subscription for same-tab)
When the user clicks `Build prompt`
Then the frontend issues `POST http://localhost:8765/api/regen-prompt` with the chosen subset
And on success the assembled prompt is rendered inline (no inner `<details>`) inside a bordered `regen-prompt-block` whose header bar carries the title, a "Wrap" soft-wrap toggle (default ON), and a prominent **Copy** button that flips its label to "Copied!" for ~1.5s on click
And a one-line breakdown reads `{N} stages selected, {K} follow-ups inlined, autonomous={true|false}, {bytes} KB` in the actions row beside the `Build prompt` button
And when the response carries a non-null `warning` a muted banner with class `regen-warning` reads `warning: {warning} — verify your selection before pasting`

Spec refs: FR-14b, FR-14c, FR-43, FR-44, AC-22

## Feature: Backend deployment

### Scenario: AC-24 — Default Uvicorn bind is `127.0.0.1`, not `0.0.0.0`

Given the user runs `make run` from `C:\workspace\spec_coding\projects\spec_driven\` with no environment overrides
When the FastAPI process starts under Uvicorn
Then the listening socket is bound to host `127.0.0.1` on port `8765`
And the server is NOT reachable on the machine's LAN IP
And `0.0.0.0` does not appear in the Uvicorn bind configuration

Spec refs: FR-12, NFR-7, AC-24

### Scenario: AC-25 — No CORS wildcard header is emitted

Given the backend is running
When a client issues `GET http://localhost:8765/api/tree` (or any other API endpoint)
Then the response headers do NOT include `Access-Control-Allow-Origin: *`
And no CORS middleware is configured with `allow_origins=["*"]`
And the deployment is single-origin (the same FastAPI process serves both static assets and `/api/`)

Spec refs: FR-11, NFR-8, AC-25

### Scenario: AC-26 — `REPO_ROOT` discovery failure exits non-zero with a clear error

Given a working directory tree where no ancestor of `main.py` contains all three of `CLAUDE.md`, `specs/`, and `.claude/`
When the user starts the backend (e.g., `python projects/spec_driven/backend/main.py`)
Then the parent-walk completes without finding a valid `REPO_ROOT`
And the process writes a clear, human-readable error message naming the three required markers
And the process exits with a non-zero status code
And no port binding occurs

Spec refs: FR-2, AC-26

### Scenario: AC-27 — `SPEC_DRIVEN_PORT` override is honored; unavailable port exits non-zero

Given the user sets `SPEC_DRIVEN_PORT=9090` in the environment
When the backend starts
Then Uvicorn binds to `127.0.0.1:9090` and `http://localhost:9090/` serves the app
Given another process is already listening on `127.0.0.1:9090`
When the backend starts with `SPEC_DRIVEN_PORT=9090`
Then the bind attempt fails
And the process writes a clear error message naming the unavailable port
And the process exits with a non-zero status code

Spec refs: FR-12, AC-27

End of acceptance criteria.
