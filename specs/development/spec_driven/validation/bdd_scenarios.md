# BDD scenarios — spec_driven

Stage: 5 (Validation strategy) — clean-state regeneration
Run: spec_driven-20260503-030434

Gherkin scenarios for the spec_driven viewer/editor + regeneration-prompt assembler. Each Feature maps to a §3 functional area or a §2 user journey; each Scenario starts with `Given` and ends with `Then`. Selectors and endpoint contracts are quoted verbatim from `final_specs/spec.md`.

---

## Feature: Sidebar tree and render dispatch

  Scenario: Sidebar boots with both top-level sections
    Given the FastAPI server is running on `127.0.0.1:8765`
    And the SPA is loaded at `http://127.0.0.1:8765/`
    When the frontend issues `GET /api/tree`
    Then the response status is 200
    And the JSON shape is `{name, path, type, children[]}` recursively
    And the element with `data-testid="sidebar"` is present in the DOM
    And at least one `data-testid="tree-leaf"` descends from the "Claude Settings & Shared Context" section
    And at least one `data-testid="tree-leaf"` descends from the "Projects" section

  Scenario: Sidebar tree includes the canonical artifact set
    Given the EXPOSED_TREE walker has indexed the repo
    When the user inspects `GET /api/tree`
    Then the tree contains `CLAUDE.md`
    And the tree contains every file matching `.claude/skills/agent_team/playbooks/*.md`
    And the tree contains every file matching `.claude/agent_refs/**/*.md`
    And under each `specs/{type}/{name}/` it contains `user_input/`, `interview/`, `findings/`, `final_specs/`, `validation/` subfolders only
    And it contains each stage's `promoted.md` sidecar when present
    And it contains `changelog.md` when present

  Scenario Outline: Render dispatch picks the correct view per file path
    Given the user navigates to `/file/<path>`
    When the main pane resolves the renderer for `<path>`
    Then the active component is `<component>`

    Examples:
      | path                                                            | component         |
      | specs/development/spec_driven/final_specs/spec.md               | MarkdownView      |
      | specs/development/spec_driven/interview/qa.md                   | QaView            |
      | .audit/adhoc_agents/2026-05-03/run-x/events.jsonl               | JsonlView         |
      | .claude/settings.json                                           | CodeView          |
      | specs/development/spec_driven/findings/diagram.png              | ImagePlaceholder  |

  Scenario: Per-project link opens the project parent page
    Given the sidebar has rendered the "Projects" section
    And there is a project entry for `development/spec_driven`
    When the user clicks the `data-testid="project-link"` `↗` icon next to that entry
    Then the route changes to `/project/development/spec_driven`
    And the project parent page lists six stages with module checkboxes
    And the master Regenerate panel is visible

  Spec refs: FR-1, FR-2, FR-15, FR-16, FR-17, FR-18, AC-1, AC-27

---

## Feature: File reader and safe_resolve sandbox

  Scenario: Read a known markdown artifact end-to-end
    Given the file `specs/development/spec_driven/final_specs/spec.md` exists on disk
    When the client issues `GET /api/file?path=specs/development/spec_driven/final_specs/spec.md`
    Then the response status is 200
    And the JSON body has fields `{path, content, mtime, bytes}`
    And `content` decodes as UTF-8 and matches the file bytes
    And the response carries header `X-Content-Type-Options: nosniff`
    And the response carries header `Content-Disposition: attachment`

  Scenario Outline: Path traversal and sandbox escapes return 404 (single status)
    Given the EXPOSED_TREE is rooted at the repo
    When the client issues `GET /api/file?path=<path>`
    Then the response status is 404
    And the response body does not distinguish "outside tree" from "not found"

    Examples:
      | path                                                          |
      | ../etc/passwd                                                 |
      | specs/../../etc/passwd                                        |
      | specs/development/spec_driven/CON.md                          |
      | specs/development/spec_driven/PRN                             |
      | specs/development/spec_driven/final_specs/spec.md::$DATA      |
      | specs/development/spec_driven/final_specs/spec.md:hidden      |
      | C:/Windows/System32/drivers/etc/hosts                         |

  Scenario: Reparse points (junctions and symlinks) are rejected
    Given a junction at `specs/development/spec_driven/leak` points outside the EXPOSED_TREE
    When the client issues `GET /api/file?path=specs/development/spec_driven/leak/anything.md`
    Then the response status is 404
    And `safe_resolve` rejected the request before any `open()` call

  Scenario Outline: Disallowed extension returns 415
    Given the file `<path>` exists
    When the client issues `GET /api/file?path=<path>`
    Then the response status is 415

    Examples:
      | path                                              |
      | specs/development/spec_driven/scratch.exe         |
      | specs/development/spec_driven/diagram.svg         |
      | specs/development/spec_driven/notes.docx          |

  Scenario: Files larger than 1 MB return 413
    Given a file `specs/development/spec_driven/huge.md` is 1.5 MB
    When the client issues `GET /api/file?path=specs/development/spec_driven/huge.md`
    Then the response status is 413

  Scenario: Verb whitelist on the file endpoint
    Given the server is running
    When the client issues `PATCH /api/file` or `DELETE /api/file`
    Then the response status is 405

  Spec refs: FR-3, FR-4, FR-5, NFR-4, NFR-5, NFR-6, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-12

---

## Feature: File editor — toolbar, dirty-dot, error banner, Ctrl+S

  Scenario: Entering edit mode shows the editor controls
    Given the user is viewing a rendered markdown file at `/file/specs/development/spec_driven/final_specs/spec.md`
    When the user clicks the ✎ Edit toolbar button
    Then the rendered view is replaced by a `<textarea>`
    And the toolbar shows three controls: **Save**, **Discard**, **Close editor**
    And the toolbar's filename has no dirty dot

  Scenario: Dirty dot appears on edit and clears on save
    Given the editor is open with the file's last-saved text
    When the user types a character into the textarea
    Then a filled-circle dirty dot is rendered next to the toolbar's filename
    When the user presses Ctrl+S
    And `PUT /api/file` returns 200
    Then the dirty dot disappears
    And the editor remains open with the saved content as the new baseline

  Scenario: Discard reverts the textarea to last-saved
    Given the editor is open and the textarea has unsaved edits
    And the dirty dot is visible
    When the user clicks **Discard**
    Then the textarea content reverts to the last-saved text
    And the dirty dot disappears

  Scenario: Save error renders a persistent inline banner; content is preserved
    Given the editor is open with edits in the textarea
    When the user presses Ctrl+S
    And `PUT /api/file` returns 413 with `{detail: {kind: "too_large"}}`
    Then a persistent banner is rendered above the textarea
    And the banner reads `Could not save: <message>`
    And the banner has `role="alert"`
    And the textarea content is preserved (no auto-clear, no auto-revert)
    And the **Save** button is still focusable and clickable
    When the user fixes the issue and presses Ctrl+S again
    And `PUT /api/file` returns 200
    Then the banner disappears

  Scenario: PUT roundtrip persists content
    Given the user opens `specs/development/spec_driven/scratch.md` for edit
    When the user replaces the body with `x` and presses Ctrl+S
    And the client issues `PUT /api/file` with `{path: "specs/development/spec_driven/scratch.md", content: "x"}`
    Then the response status is 200
    And a subsequent `GET /api/file?path=specs/development/spec_driven/scratch.md` returns `content == "x"`

  Scenario: Cross-origin save attempt is rejected
    Given the editor calls `PUT /api/file` with `Origin: http://evil.example.com`
    When the request reaches the FastAPI app
    Then the response status is 403
    And no file on disk is mutated

  Scenario: Image and SVG paths cannot be written
    Given the user crafts a `PUT /api/file` to a `.png` or `.svg` path
    When the request reaches the FastAPI app
    Then the response status is 415

  Spec refs: FR-6, FR-7, FR-8, FR-9, FR-25, FR-26, FR-27, FR-28, AC-9, AC-10, AC-11, NFR-7, NFR-8, NFR-9, NFR-15

---

## Feature: Structured Q/A view and per-block editing

  Scenario: QaView renders rounds, categories, and tinted Q/A blocks
    Given the user deep-links to `/file/specs/development/spec_driven/interview/qa.md`
    When the SPA boots and dispatches by path
    Then the main pane mounts the component with `data-testid="qa-view"`
    And `<main>` content is non-empty
    And `consoleErrors` collected during boot equal `[]`
    And at least one Q-tinted block (blue) is present
    And at least one A-tinted block (green) is present
    And each round renders with a `## Round N` heading
    And each category renders as a colored badge above its Q/A list

  Scenario: Autonomous-form Q/A renders parsed (not via fallback)
    Given the qa.md contains a line `- A *(judgment call — chose X because Y)*: text`
    When QaView's parser walks the file
    Then the answer regex matches both interactive `- A: <text>` and autonomous `- A *(judgment call — chose X because Y)*: <text>`
    And the block renders as a parsed A-tint block
    And the Error Boundary fallback is NOT engaged

  Scenario: Per-Q inline edit persists via PUT /api/file
    Given QaView is mounted on `interview/qa.md`
    When the user clicks the ✎ pencil on a single Q block
    Then a small `<textarea>` scoped to that block appears with **Save** and **Cancel** controls
    When the user edits the Q and presses Ctrl+S
    Then the client issues `PUT /api/file` with the full file's new content
    And the response status is 200
    And QaView re-renders with the updated Q text

  Scenario: File-level ✎ Edit is disabled (but visible) while a per-block editor is open
    Given QaView is mounted and a per-Q editor is open
    When the user looks at the toolbar
    Then the file-level ✎ Edit toggle is rendered
    And the file-level ✎ Edit toggle is disabled (inert) — not hidden
    When the user closes the per-block editor
    Then the file-level ✎ Edit toggle becomes enabled again

  Scenario: Whole-file edit on qa.md ignores the structured view
    Given QaView is mounted on `interview/qa.md`
    And no per-block editor is open
    When the user clicks the file-level ✎ Edit toolbar button
    Then the structured QaView is replaced by the standard `<textarea>` editor
    And the textarea content equals the raw markdown of `qa.md`
    And Save/Discard/Close-editor controls behave per FR-25–FR-28

  Spec refs: FR-18, FR-21, FR-29, FR-30, FR-31, FR-32, AC-18, AC-19

---

## Feature: QaView fallback via Error Boundary

  Scenario: Malformed qa.md falls back to MarkdownView with a banner
    Given a deliberately malformed `interview/qa.md` exists in a fixture project
    And the user deep-links to `/file/specs/development/<broken-fixture>/interview/qa.md`
    When QaView's parser throws during render
    Then a real React Error Boundary class component catches the error via `componentDidCatch`
    And the fallback renders `MarkdownView` over the raw markdown
    And a one-line banner reads `Could not parse structured Q/A view; rendering raw markdown. (cause: <message>)`
    And `<main>` content is non-empty
    And `consoleErrors` collected during boot equal `[]`

  Scenario: Fallback does NOT use a try/catch around JSX
    Given the QaView component is reviewed
    When the implementation is inspected
    Then it does NOT use the pattern `try { return <Foo .../> } catch { return <Fallback /> }`
    And it relies on a class-component Error Boundary using `componentDidCatch` / `getDerivedStateFromError`

  Spec refs: FR-19, FR-20, AC-20

---

## Feature: Markdown rendering and link resolution

  Scenario: Relative links resolve against the current file's directory and SPA-navigate
    Given the user is viewing `/file/specs/development/spec_driven/final_specs/spec.md`
    And the markdown contains a link `[interview qa](../interview/qa.md)`
    When the user clicks the link
    Then the SPA navigates to `/file/specs/development/spec_driven/interview/qa.md`
    And no full page reload occurs

  Scenario: Absolute http(s) links open in a new tab
    Given the markdown contains `[OWASP](https://owasp.org/)`
    When the user clicks the link
    Then a new tab opens with `target="_blank"` and `rel="noopener noreferrer"`

  Scenario: Anchor-only links scroll without navigation
    Given the markdown contains `[top](#section-1)`
    When the user clicks the link
    Then the page scrolls to the in-page anchor
    And the route is unchanged

  Scenario Outline: Broken links render as muted spans, not anchors
    Given the markdown contains a link to `<target>` that resolves as broken
    When the renderer visits that link
    Then the rendered element is `<span class="link-broken" aria-disabled="true">` (NOT an `<a>`)
    And the span carries a `title="<cause>"` attribute

    Examples:
      | target                               | cause                  |
      | ../missing/no-such-file.md           | file not found         |
      | ../../etc/passwd                     | outside exposed tree   |
      | ../Interview/qa.md                   | case mismatch          |
      | #not-a-real-anchor                   | anchor not in document |

  Scenario: No raw HTML survives the sanitizer
    Given a markdown source contains `<script>alert(1)</script>` and `<img onerror=...>`
    When the renderer pipeline runs `react-markdown` + `rehype-sanitize`
    Then the rendered DOM contains no `<script>` element
    And no `on*` event handler attributes are present

  Spec refs: FR-22, FR-23, FR-24, NFR-8, AC-21

---

## Feature: Regenerate panel — per-stage file

  Scenario: Default-collapsed panel above a stage file
    Given the user is viewing `/file/specs/development/spec_driven/validation/strategy.md`
    When the page first renders
    Then a `<details title="Regenerate">` element is present above the file content
    And the `<details>` is closed (`open` attribute absent)

  Scenario: Module checkboxes default to all-checked
    Given the user expands the Regenerate panel on a `validation/` file
    When the panel reads `GET /api/stages?project_type=development&project_name=spec_driven`
    Then a checkbox is rendered for each module of the `validation` stage
    And every checkbox is checked by default

  Scenario: Build prompt assembles INTERACTIVE prompt and shows breakdown line
    Given the Regenerate panel is expanded on a `validation/` file
    And the autonomous-mode toggle is OFF
    When the user clicks **Build prompt**
    And the client issues `POST /api/regen-prompt` with `{autonomous: false, stages: ["validation"], modules: {validation: [...]}}`
    Then the response status is 200
    And the response body has `{prompt, warning, selected_stages_count, follow_ups_count, autonomous, bytes}`
    And `autonomous` equals `false`
    And `prompt` opens with the literal first line `# EXECUTION MODE: INTERACTIVE`
    And the prompt does NOT contain the autonomous imperative line
    And a one-line breakdown `{N} stages selected, {K} follow-ups inlined, autonomous=false, {bytes} KB` is rendered in the actions row beside Build prompt
    And `warning` is `null`

  Scenario: Autonomous header and verbatim imperative line
    Given the autonomous-mode toggle is ON
    When the user clicks **Build prompt**
    And the client issues `POST /api/regen-prompt` with `{autonomous: true, ...}`
    Then `prompt` opens with the literal first line `# EXECUTION MODE: AUTONOMOUS`
    And the next non-blank line equals "Do not call AskUserQuestion. For anything unclear, use your best judgment, record the choice inline in the artifact, and keep going. Produce every requested artifact below in this single turn before stopping."
    And the breakdown line shows `autonomous=true`

  Scenario: Assembled prompt renders inline with header bar and Copy button
    Given the user has clicked **Build prompt** and the response was 200
    When the assembled prompt is displayed
    Then it is rendered inside a bordered `regen-prompt-block` (no inner `<details>` to expand)
    And the header bar contains, left-to-right: an "Assembled prompt" title, a "Wrap" toggle (default checked), a primary-style **Copy** button
    And the body is a `<pre>` element with `white-space: pre-wrap; word-break: break-word` while Wrap is on

  Scenario: Copy button copies prompt and flips label
    Given the assembled prompt is rendered
    When the user clicks the **Copy** button
    Then the full prompt text is written to the clipboard
    And the button label flips to "Copied!" for ~1500 ms
    And the button has attribute `aria-live="polite"`
    And the button has a fixed minimum width so the label flip does not shift layout

  Scenario: Wrap toggle controls soft-wrap (and is NOT persisted)
    Given the assembled prompt is rendered with Wrap on
    When the user unchecks the "Wrap" toggle
    Then the `<pre>` switches to fixed-width with horizontal scroll
    When the user re-checks the "Wrap" toggle
    Then the `<pre>` reverts to soft-wrap
    And `localStorage` does NOT contain a key for the wrap state

  Scenario Outline: Size policy on `POST /api/regen-prompt`
    Given a regen prompt is assembled with body size `<bytes>`
    When the client issues `POST /api/regen-prompt`
    Then the response status is `<status>`
    And the response `warning` field is `<warning>`
    And the prompt is emitted in full (never truncated) when `<status>` is 200

    Examples:
      | bytes      | status | warning   |
      | 12_000     | 200    | null      |
      | 75_000     | 200    | non-null  |
      | 600_000    | 200    | non-null  |
      | 1_500_000  | 413    | n/a       |

  Scenario: Warning banner above the prompt block
    Given `POST /api/regen-prompt` returned `warning: "prompt is 250 KB; review before pasting"` with status 200
    When the panel renders
    Then a muted banner reading `warning: prompt is 250 KB; review before pasting — verify your selection before pasting` is rendered ABOVE the `regen-prompt-block`

  Scenario: Read-zero contract is in the Constraints section
    Given any successful `POST /api/regen-prompt` response
    When the prompt body is inspected
    Then it contains a `### Constraints` section
    And the section names CLAUDE.md state surfaces, canonical paths, parent-direct manager-spawn contract, no-AskUserQuestion-in-autonomous-mode
    And the section includes the verbatim sentence `regeneration deletes prior outputs first; new generation reads only the inputs.`
    And the section names the audit events `regen.delete.planned`, `regen.delete.completed`, `regen.write.completed`

  Scenario: Pinned items survive in the assembled prompt
    Given `specs/development/spec_driven/interview/promoted.md` is non-empty (contains pin-001)
    And the user selects the `interview` stage in the panel
    When the user clicks **Build prompt**
    Then the assembled prompt contains a `### Pinned items (MUST survive regeneration)` section
    And the contents of `interview/promoted.md` appear verbatim under that section

  Scenario: Follow-ups are inlined in numerical order
    Given `specs/development/spec_driven/user_input/follow_ups/` contains `001-...md`, `002-...md`, `003-...md`
    When the user clicks **Build prompt** with any stage selected
    Then the assembled prompt lists each follow-up filename in numerical order
    And `follow_ups_count` in the response equals 3

  Spec refs: FR-10, FR-11, FR-12, FR-33, NFR-11, NFR-15, NFR-16, AC-13, AC-14, AC-15, AC-16, AC-17, AC-22, AC-23, AC-24, AC-25

---

## Feature: Regenerate panel — project parent page

  Scenario: Project parent page lists six stages with a master Regenerate panel
    Given the user navigates to `/project/development/spec_driven`
    When the page renders
    Then six stages are listed (intake, interview, research, spec compilation, validation strategy, execution)
    And each stage shows its module checkboxes
    And a single master Regenerate panel exposes select-any-subset semantics across stages
    And the breakdown / warning / Copy contract matches the per-stage panel exactly

  Scenario: Master panel assembles a multi-stage prompt
    Given the user is on `/project/development/spec_driven`
    And the user selects stages `interview`, `research`, and `validation`
    And the user picks a strict subset of modules under `validation`
    When the user clicks **Build prompt**
    And the client issues `POST /api/regen-prompt` with the selected stages and modules
    Then the response status is 200
    And `selected_stages_count` equals 3
    And the prompt walks each selected stage with its invocation hint and module list
    And the breakdown line reflects the selection

  Spec refs: FR-15, FR-34, AC-27

---

## Feature: Autonomous-mode toggle persistence and storage-event sync

  Scenario: Toggle defaults to OFF (interactive)
    Given the user opens the SPA in a fresh browser profile
    And `localStorage["spec_driven.autonomous_mode.v1"]` is unset
    When the per-stage Regenerate panel renders
    Then the autonomous-mode toggle is unchecked
    And subsequent `POST /api/regen-prompt` calls send `autonomous: false`

  Scenario: Toggling persists to localStorage and survives reload
    Given the user is on `/file/specs/development/spec_driven/validation/strategy.md`
    When the user checks the autonomous-mode toggle
    Then `localStorage["spec_driven.autonomous_mode.v1"]` equals `"true"`
    When the user reloads the page
    Then the toggle renders as checked

  Scenario: Same-tab in-process subscription syncs both consumers
    Given the user has two routes open in one tab: a per-stage file view and the project parent page (e.g., via tabbed UI / split view)
    When the user toggles autonomous mode in the per-stage panel
    Then the project-parent-page panel re-renders with the new toggle state
    And both consumers send the same `autonomous` value on subsequent **Build prompt** clicks

  Scenario: Cross-tab sync via the storage event
    Given two browser tabs are open against `http://127.0.0.1:8765/`
    And tab A is on a stage file, tab B is on `/project/development/spec_driven`
    When the user toggles autonomous mode in tab A
    Then a `storage` event fires for key `spec_driven.autonomous_mode.v1`
    And tab B's master Regenerate panel re-renders with the new toggle state
    And both tabs agree on the toggle value

  Spec refs: FR-33, FR-35, AC-26

---

## Feature: Promotion (pin / unpin)

  Scenario Outline: Atomic pin candidates show the 📌 toggle on hover
    Given the user is viewing `<file>`
    When the user hovers over a `<item-kind>`
    Then a 📌 toggle is rendered on that item

    Examples:
      | file                                                              | item-kind                  |
      | specs/development/spec_driven/interview/qa.md                     | Q/A pair                   |
      | specs/development/spec_driven/findings/dossier.md                 | recommendation bullet      |
      | specs/development/spec_driven/final_specs/spec.md                 | FR-NN block                |
      | specs/development/spec_driven/validation/acceptance_criteria.md   | AC-NN block                |
      | specs/development/spec_driven/validation/system_tests.md          | SYS-NN block               |

  Scenario: Pinning appends a verbatim block to promoted.md
    Given `specs/development/spec_driven/interview/promoted.md` is empty
    When the user clicks the 📌 toggle on a Q/A pair in `interview/qa.md`
    And the client issues `POST /api/promote` with `{project_type: "development", project_name: "spec_driven", stage_folder: "interview", source_file: "interview/qa.md", item_id, item_text}`
    Then the response status is 200
    And `interview/promoted.md` contains the item's text verbatim
    And the 📌 toggle on that item renders as "pinned"

  Scenario: Unpinning removes only the matching block
    Given `interview/promoted.md` contains pin-001 and pin-002
    When the user clicks the 📌 toggle on pin-001 (already pinned)
    And the client issues `DELETE /api/promote` with `{project_type, project_name, stage_folder: "interview", item_id: "pin-001"}`
    Then the response status is 200
    And pin-001 is removed from `interview/promoted.md`
    And pin-002 remains in `interview/promoted.md` untouched

  Scenario Outline: stage_folder allowlist
    Given the client issues `POST /api/promote` with `stage_folder: "<value>"`
    When the request reaches the FastAPI app
    Then the response status is `<status>`

    Examples:
      | value         | status |
      | interview     | 200    |
      | findings      | 200    |
      | final_specs   | 200    |
      | validation    | 200    |
      | user_input    | 4xx    |
      | projects      | 4xx    |

  Scenario: Stage 6 files do NOT show 📌 toggles
    Given the user is viewing a file under `projects/spec_driven/`
    When the page renders
    Then no 📌 toggle is present on any item
    And `POST /api/promote` is not called by any control on the page

  Scenario: Cross-origin promote attempt is rejected
    Given the client issues `POST /api/promote` with `Origin: http://evil.example.com`
    When the request reaches the FastAPI app
    Then the response status is 403
    And `promoted.md` is not mutated

  Spec refs: FR-13, FR-14, FR-9, FR-36, FR-37, NFR-7

---

## Feature: Boot smoke

  Scenario: `make run-prod` brings up the server cleanly
    Given a fresh checkout with `frontend/` built into `backend/static/`
    When the operator runs `make run-prod`
    Then uvicorn starts on `127.0.0.1:8765`
    And the bind address is NOT `0.0.0.0`
    And `GET /api/tree` returns 200
    And `http://127.0.0.1:8765/` serves the SPA
    And the Sidebar contains ≥1 leaf under "Claude Settings & Shared Context"
    And the Sidebar contains ≥1 leaf under "Projects"

  Scenario: Server is not reachable on the LAN IP
    Given uvicorn is bound to `127.0.0.1:8765`
    When a request hits the host's LAN IP on port 8765
    Then the connection is refused

  Scenario: `make run` also binds localhost-only
    Given a fresh checkout
    When the operator runs `make run`
    Then uvicorn binds to `127.0.0.1:8765`
    And `0.0.0.0` does not appear anywhere in the resolved Uvicorn config

  Scenario: Initial app load completes within 2 s on localhost
    Given the SPA bundle has been built
    When the user opens `http://127.0.0.1:8765/` with a cold cache
    Then HTML + JS + first `/api/tree` + first `/api/file` complete within 2000 ms
    And `GET /api/tree` returns within 200 ms
    And `GET /api/file` for a <500 KB file returns within 100 ms

  Spec refs: FR-38, FR-39, NFR-1, NFR-2, NFR-3, AC-28, AC-29
