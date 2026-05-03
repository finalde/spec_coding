# BDD scenarios — `spec_driven`

Run: `spec_driven-20260503-145859`

Feature-level Gherkin specs grouping related user-perceived behaviors. Each Feature is broader than the granular ACs in `acceptance_criteria.md`; ACs are checkpoint assertions, scenarios are end-to-end flows. Cross-references at the end of every Feature.

Conventions:
- `Given` sets up filesystem / SPA state.
- `When` is a single user-visible action (click, paste URL, keypress, send HTTP request).
- `Then` asserts on rendered DOM, response shape, on-disk content, or `events.jsonl`.
- HTTP examples assume the backend is bound at `127.0.0.1:8765` unless otherwise stated.
- Module identifiers (`FR-NN`, `NFR-NN`, `AC-NN`) refer to `final_specs/spec.md` and `validation/acceptance_criteria.md`.

---

## Feature: Browse the artifact tree

  As the spec author
  I want to navigate every file the workflow reads or writes from a single sidebar
  So that I never have to switch to a file explorer to inspect a stage's output

  Background:
    Given the backend is running at "http://127.0.0.1:8765"
    And the SPA is loaded in a browser tab against the backend
    And the repo contains at least one project under "specs/development/spec_driven/"

  Scenario: Sidebar exposes the two top-level sections with recursive children
    When the SPA fetches "GET /api/tree"
    Then the response is a single JSON object with shape "{type, name, path, children: [...]}"
    And exactly two top-level sections exist with names "Claude Settings & Shared Context" and "Projects"
    And every non-leaf node carries a "children" field (possibly empty)
    And every leaf node has "type": "file" and no "children" field
    And the "Claude Settings & Shared Context" subtree includes "CLAUDE.md" as a leaf
    And the "Claude Settings & Shared Context" subtree includes ".claude/skills/agent_team/SKILL.md" as a leaf
    And the "Claude Settings & Shared Context" subtree includes ".claude/agent_refs/validation/general.md" as a leaf
    And the "Projects" subtree includes "specs/development/spec_driven/final_specs/spec.md" as a leaf

  Scenario: Sidebar walks "node.children" uniformly with no special branches
    Given the consumer-walk recurses only via "node.children" and never via "node.projects" or "node.stages"
    When the consumer-walk visits every node in the response of "GET /api/tree"
    Then no leaf is reached via a path that requires a non-"children" field
    And the total leaf count for the "Projects" section is at least 1

  Scenario: Click a sidebar leaf renders the file in the main pane
    Given the sidebar is rendered
    When the user clicks the leaf "specs/development/spec_driven/final_specs/spec.md"
    Then the URL changes to "/file/specs%2Fdevelopment%2Fspec_driven%2Ffinal_specs%2Fspec.md"
    And the main pane renders a markdown view
    And the breadcrumb above the main pane shows "specs / development / spec_driven / final_specs / spec.md"
    And the current crumb is rendered as plain text with attribute aria-current="page"

  Scenario: Sidebar keyboard navigation reaches the focused leaf
    Given the sidebar tree has been built
    When the user presses "Ctrl+Shift+E"
    Then focus moves to the sidebar tree root
    When the user presses "ArrowDown" three times
    Then a leaf or section node is focused
    When the user presses "Enter"
    Then the focused file is mounted into the main pane

  Scenario: Sidebar response is fast at canonical scale
    Given the canonical scale (50 projects x 200 files = 10000 leaves) is staged on disk
    When the SPA fetches "GET /api/tree"
    Then the response arrives within 250 ms

  References: FR-3, FR-15, FR-16, FR-17, FR-18, NFR-1, AC-3, AC-26.

---

## Feature: Render a file in the appropriate mode

  As the spec author
  I want each file to render in the mode that matches its extension and shape
  So that JSONL is collapsible, Q/A is color-differentiated, and code is syntax-highlighted

  Background:
    Given the SPA is loaded
    And every render component is wrapped in a real React Error Boundary class

  Scenario Outline: Render-mode dispatch by file shape
    Given the file "<path>" exists inside EXPOSED_TREE
    When the user opens the file via the sidebar
    Then the main pane mounts the "<component>" component
    And the selector "<selector>" resolves inside the main pane
    And the browser console reports zero errors

    Examples:
      | path                                                     | component         | selector                  |
      | specs/development/spec_driven/final_specs/spec.md        | MarkdownView      | .markdown-view            |
      | specs/development/spec_driven/interview/qa.md            | QaView            | .qa-view .qa-pair         |
      | .audit/adhoc_agents/2026-05-03/spec_driven-20260503-145859/events.jsonl | JsonlView | .jsonl-view .jsonl-line  |
      | projects/spec_driven/backend/static/manifest.json        | CodeView          | .code-view pre code       |
      | specs/development/spec_driven/findings/diagram.png       | ImagePlaceholder  | .image-placeholder        |

  Scenario: MarkdownView strips raw HTML through rehype-sanitize default schema
    Given a file "specs/development/spec_driven/findings/dossier.md" containing "<script>alert(1)</script>" inline
    When the user opens that file
    Then the rendered DOM contains zero "<script>" elements
    And the rendered DOM contains zero attributes whose name starts with "on"
    And no anchor in the rendered DOM has href starting with "javascript:"

  Scenario: MarkdownView renders broken internal links as muted spans, not anchors
    Given the file "specs/development/spec_driven/findings/dossier.md" links to "[gone](./removed.md)" and "./removed.md" does not exist
    When the user opens that file
    Then the link "gone" renders as a "<span class='broken-link'>" element
    And the span carries a "title" attribute containing the broken target
    And the link is NOT rendered as an "<a>" element

  Scenario: MarkdownView opens external links in a new tab
    Given a file links to "[OWASP](https://owasp.org/)"
    When the user opens that file
    Then the link "OWASP" is an "<a>" with attribute target="_blank"
    And the anchor has rel containing "noopener" and "noreferrer"

  Scenario: QaView color-differentiates question and answer blocks
    Given "specs/development/spec_driven/interview/qa.md" contains a Round 1 General-shape Q/A pair
    When the user opens "interview/qa.md"
    Then each Q block has class containing "qa-q" and resolved background-color is the blue tint
    And each A block has class containing "qa-a" and resolved background-color is the green tint
    And every Q/A block carries a "category" badge in its header

  Scenario: QaView regex matches the autonomous-mode judgment-call form
    Given a Q/A pair in "qa.md" written as "- A *(judgment call: Y because Z)*: text"
    When the user opens "interview/qa.md"
    Then the answer renders inside a ".qa-a" block with the same body text
    And no parse-fallback banner is shown

  Scenario: ParseFallback Error Boundary catches a malformed Q/A file
    Given "interview/qa.md" contains a corrupted line that throws inside QaView's parse-on-render
    When the user opens "interview/qa.md"
    Then the main pane renders a "<pre>" with the raw file content
    And a banner above the "<pre>" reads "Parse error — falling back to raw text"
    And the browser console reports the caught error exactly once

  Scenario: JsonlView parses each line independently
    Given a file "events.jsonl" contains three valid JSON object lines and one malformed line
    When the user opens that file
    Then exactly three ".jsonl-line.parsed" elements render
    And exactly one ".jsonl-line.parse-error" element renders
    And clicking a parsed line toggles a collapsed/expanded JSON tree

  Scenario: CodeView uses the dark fixed palette (intentional carve-out)
    Given a file "manifest.json" is opened
    Then the ".code-view pre" element resolves background-color to a dark color
    And the contrast ratio between the rendered text and that background meets WCAG AA

  Scenario: Image placeholder for binary files
    Given a file "specs/development/spec_driven/findings/diagram.png" is opened
    Then the main pane renders a card showing the filename, the byte count, and the text "binary content not previewed"
    And no "<img>" tag is rendered

  References: FR-19, FR-20, FR-21, FR-22, FR-23, FR-24, NFR-8, NFR-13, NFR-16, AC-4, AC-5, AC-6, AC-25.

---

## Feature: Edit a whole file in the textarea editor

  As the spec author
  I want to switch a file into edit mode, change it, and save without losing the cursor's place
  So that I can fix a typo without leaving the SPA

  Background:
    Given the SPA is loaded
    And a file "specs/development/spec_driven/final_specs/spec.md" is open in MarkdownView
    And the file's mtime on disk is "T0"

  Scenario: Toggle edit, modify, save round-trip
    When the user clicks the "Edit" pencil in the file-pane toolbar
    Then the main pane swaps to a "<textarea>" containing the full file content
    When the user appends "\n\n## Scratch" to the textarea
    Then the toolbar shows a filled dot "●"
    And document.title contains an asterisk "*"
    When the user presses "Ctrl+S"
    Then a "PUT /api/file" request is sent with body "{path, content}"
    And the request includes header "If-Unmodified-Since: <T0 in RFC 7232>"
    And the response is 200 with body "{bytes, mtime: T1}"
    And the editor stays mounted but the dirty dot disappears
    And document.title no longer contains the asterisk
    When the user clicks "Close editor"
    Then the main pane re-mounts MarkdownView with the new content
    And the rendered markdown contains the heading "Scratch"

  Scenario: Discard reverts to last-saved content
    Given the user has typed "garbage" into the editor
    And the toolbar shows the dirty dot
    When the user clicks "Discard"
    Then the textarea content reverts to the last-saved version
    And the dirty dot disappears

  Scenario: Closing a dirty editor warns via beforeunload
    Given the user has typed "garbage" into the editor
    When the user attempts to navigate away (closes the tab)
    Then the browser fires a "beforeunload" event
    And the user is prompted whether to discard unsaved changes

  Scenario: Save error shows a persistent inline banner, not a toast
    Given the user has typed valid changes
    And the next "PUT /api/file" will return 500
    When the user presses "Ctrl+S"
    Then a banner appears above the textarea with class "save-error-banner"
    And the banner is NOT a transient toast (the element is still present after 5 seconds)
    And the dirty dot remains visible
    When the next "PUT /api/file" returns 200
    And the user presses "Ctrl+S" again
    Then the banner is removed and the dirty dot clears

  Scenario: Stale-write conflict — file changed under the user
    Given the user opened the file at mtime "T0"
    And another process wrote the file at mtime "T1 > T0"
    When the user presses "Ctrl+S"
    Then "PUT /api/file" responds 409 with body '{"detail":{"kind":"stale_write","current_mtime":"T1"}}'
    And a banner reads "file changed externally — Reload?"
    And the banner shows a "Reload" button
    When the user clicks "Reload"
    Then the editor fetches the latest content (mtime T1)
    And the in-memory edits are discarded
    And the dirty dot is cleared

  Scenario: PUT body validates UTF-8 / no NUL on text extensions
    When the user pastes content beginning with a NUL byte and presses "Ctrl+S"
    Then "PUT /api/file" responds 400 with a "kind: invalid_text" detail
    And the editor shows a save-error banner with that message

  Scenario: 1.5 MB content is rejected with 413
    Given the user pastes content of 1.5 MB into the editor
    When "Ctrl+S" is pressed
    Then "PUT /api/file" responds 413 with body '{"detail":{"kind":"too_large"}}'
    And a save-error banner shows "file too large"

  References: FR-7, FR-7b, FR-8, FR-25, FR-26, FR-27, FR-28, FR-29, NFR-6, AC-7, AC-9, AC-10, AC-13, AC-14, AC-15.

---

## Feature: Edit a Q/A pair in place

  As the spec author
  I want to fix a single Q or A in interview/qa.md without retyping the rest of the file
  So that small interview corrections stay surgical

  Background:
    Given the SPA is loaded
    And "specs/development/spec_driven/interview/qa.md" renders in QaView with at least three Q/A pairs

  Scenario: Per-Q inline edit round-trip
    When the user clicks the per-Q "✎" pencil on the second Q block
    Then a small inline editor opens scoped to that Q
    And the file-level "Edit" toggle in the toolbar becomes disabled
    When the user changes the Q text and clicks "Save"
    Then a "PUT /api/file" request is sent with the WHOLE file content (not a patch)
    And the response is 200
    And the QaView re-renders with the new Q text
    And the file-level "Edit" toggle re-enables

  Scenario: Per-A inline edit round-trip
    When the user clicks the per-A "✎" pencil on the first A block
    Then a small inline editor opens scoped to that A
    When the user changes the A text and clicks "Save"
    Then "PUT /api/file" is sent with the whole file
    And the response is 200
    And the QaView shows the new A text in the same color-differentiated block

  Scenario: Per-block edit and file-level edit are mutually exclusive
    Given a per-Q inline editor is open
    When the user attempts to click the file-level "Edit" pencil in the toolbar
    Then nothing happens (the button is disabled)

  Scenario: Per-block edit on autonomous-mode judgment-call form
    Given the second Q/A pair was written by an autonomous-mode regen as "- A *(judgment call: chose B because cost)*: text"
    When the user clicks "✎" on that A
    Then the inline editor opens with the answer body "text" (judgment-call annotation visible above)
    When the user edits the answer and saves
    Then the file's exact "*(judgment call ...)*" annotation is preserved verbatim

  Scenario: Two Q-edits race — last-write-wins per Q with banner
    Given the user opens a per-Q inline editor at mtime "T0"
    And another tab has already saved the same Q at mtime "T1 > T0"
    When the user clicks "Save"
    Then "PUT /api/file" responds 409
    And a banner above the inline editor reads "Q changed externally — Reload?"
    When the user clicks "Reload"
    Then the inline editor re-fetches and re-mounts with the T1 version
    And the user's in-memory edit is discarded

  References: FR-20, FR-30, OQ-2, AC-8, AC-13.

---

## Feature: Pin / unpin atomic items

  As the spec author
  I want to mark a Q/A pair, FR-NN, NFR-NN, AC-NN, or recommendation bullet as pinned
  So that the next regeneration of that stage cannot silently drop it

  Background:
    Given the SPA is loaded
    And "specs/development/spec_driven/interview/promoted.md" does not exist

  Scenario: Pin a Q/A pair
    Given QaView is rendered for "interview/qa.md"
    When the user clicks "📌" on the first Q/A pair
    Then a "POST /api/promote" request is sent with body
      """
      {
        "project_type": "development",
        "project_name": "spec_driven",
        "stage_folder": "interview",
        "source_file": "qa.md",
        "item_id": "round1.general.q1",
        "item_text": "...verbatim Q+A markdown..."
      }
      """
    And the response is 200 with body '{"status":"ok","item_id":"round1.general.q1"}'
    And the file "specs/development/spec_driven/interview/promoted.md" now exists
    And it contains the verbatim "...Q+A markdown..." block
    And the rendered Q/A pair shows a small "📌" indicator
    When the user hovers the indicator
    Then a tooltip displays the path "specs/development/spec_driven/interview/promoted.md"

  Scenario: Pin an FR block
    Given the user is viewing "final_specs/spec.md" rendered as MarkdownView
    When the user clicks "📌" next to the "**FR-9.**" block
    Then "POST /api/promote" is sent with stage_folder "final_specs", item_id "FR-9"
    And "specs/development/spec_driven/final_specs/promoted.md" contains the verbatim FR-9 paragraph

  Scenario: Pin an AC block
    Given the user is viewing "validation/acceptance_criteria.md"
    When the user clicks "📌" next to "**AC-11**"
    Then "POST /api/promote" is sent with stage_folder "validation", item_id "AC-11"
    And the response is 200
    And "validation/promoted.md" contains the AC-11 block

  Scenario: Unpin an item is idempotent
    Given an item "round1.general.q1" is pinned in "interview/promoted.md"
    When the user clicks the "📌" again to unpin
    Then "DELETE /api/promote" is sent with stage_folder "interview", item_id "round1.general.q1"
    And the response is 200
    And the pin is removed from "interview/promoted.md"
    When the user immediately clicks unpin a second time (race)
    Then the second request also returns 200 (idempotent)

  Scenario: Promotion endpoint rejects unknown stage_folder
    When a "POST /api/promote" sends stage_folder "scratch"
    Then the response is 400 with detail "kind: invalid_stage"

  Scenario: Stage 6 (project code) does not support promotion
    Given the user is viewing "projects/spec_driven/backend/main.py"
    Then no "📌" pin affordance is rendered next to any code symbol or block

  References: FR-13, FR-14, FR-35, FR-36, NFR-15, AC-24.

---

## Feature: Build a per-stage regeneration prompt

  As the spec author
  I want to assemble a copy-paste regeneration prompt for one stage with my chosen modules and mode
  So that I can drive Claude Code to re-run that stage without hand-writing the prompt

  Background:
    Given the SPA is loaded
    And the project "specs/development/spec_driven/" has at least two follow-ups under "user_input/follow_ups/"
    And the autonomous-mode toggle is in its persisted state

  Scenario: Build a small interactive prompt — happy path
    Given the user has opened "specs/development/spec_driven/interview/qa.md"
    And the per-stage Regenerate "<details>" panel is closed by default
    When the user opens the Regenerate panel
    Then all module checkboxes are checked
    And the autonomous toggle reflects localStorage "spec_driven.autonomous_mode.v1" (default off)
    When the user clicks "Build prompt"
    Then a "POST /api/regen-prompt" is sent with body
      """
      {
        "project_type": "development",
        "project_name": "spec_driven",
        "stages": ["interview"],
        "modules": {"interview": ["qa"]},
        "autonomous": false
      }
      """
    And the response is 200 with body shape "{prompt, warning, selected_stages_count, follow_ups_count, autonomous, bytes}"
    And "warning" is null
    And the assembled "prompt" starts with the literal first line "# EXECUTION MODE: INTERACTIVE"
    And the prompt inlines the verbatim content of "user_input/revised_prompt.md"
    And the prompt lists "user_input/follow_ups/001-..." and "user_input/follow_ups/002-..." in numerical order with full bodies inlined
    And the prompt contains "### Constraints" with the read-zero contract verbatim
    And a bordered ".regen-prompt-block" renders inline (no inner "<details>")
    And the breakdown line beside the Build button reads "1 stages selected, 2 follow-ups inlined, autonomous=false, X KB"

  Scenario: Build a prompt in autonomous mode
    Given the autonomous toggle is on
    When the user opens the Regenerate panel and clicks "Build prompt"
    Then the response "autonomous" field is true
    And the assembled prompt's first line is "# EXECUTION MODE: AUTONOMOUS"

  Scenario: Pinned items appear inlined in the per-stage prompt
    Given "specs/development/spec_driven/interview/promoted.md" contains a verbatim Q/A pair
    When the user clicks "Build prompt" for the interview stage
    Then the assembled prompt contains a section header "Pinned items (MUST survive regeneration)"
    And the section contains the verbatim Q/A pair from "promoted.md"

  Scenario: Copy button places the prompt on the clipboard
    Given a regen-prompt-block is rendered
    When the user clicks the "Copy" button in the header bar
    Then navigator.clipboard.readText() returns the same string as the rendered "<pre>" body
    And the button's label flips to "Copied!"
    And the button's aria-live attribute is "polite"
    And after 1500 ms the label flips back to "Copy"
    And the button's bounding box width does not change between states (fixed min-width)

  Scenario: Soft-wrap toggle defaults on, off restores horizontal scroll
    Given a regen-prompt-block is rendered
    Then the "<pre>" element has CSS "white-space: pre-wrap"
    When the user clicks the "Wrap" toggle off
    Then the "<pre>" element has CSS "white-space: pre" and "overflow-x: auto"
    When the user clicks "Build prompt" again on a different stage
    Then the new prompt block reverts to soft-wrap on (per-render preference, not persisted)

  Scenario: Regen prompt shows assembled-style preference
    Given a regen-prompt-block is rendered
    Then the "<pre>" computed font-size is "13px"
    And the "<pre>" computed line-height is "1.55"
    And the "<pre>" computed max-height is "520px"

  Scenario Outline: Size policy — warn don't truncate
    Given the user has selected stages and modules that produce a prompt of "<bytes>" bytes
    When the user clicks "Build prompt"
    Then the response status is "<status>"
    And the response "warning" field is "<warning>"
    And the UI behavior is "<ui>"

    Examples:
      | bytes  | status | warning                                                            | ui                                                                            |
      | 12000  | 200    | null                                                               | bordered prompt block rendered; no banner                                     |
      | 51199  | 200    | null                                                               | bordered prompt block rendered; no banner                                     |
      | 75000  | 200    | {"kind":"approaching_ceiling","bytes":75000,"soft_limit":51200}    | yellow banner above prompt block; prompt block still rendered                 |
      | 999999 | 200    | {"kind":"approaching_ceiling","bytes":999999,"soft_limit":51200}   | yellow banner above prompt block; prompt block still rendered                 |
      | 1100000| 413    | n/a (response detail is {"kind":"too_large"})                      | build-error banner; prompt block NOT rendered                                 |

  Scenario: Build prompt in single-process mode (`make run-prod`)
    Given the SPA is loaded at "http://127.0.0.1:8765/" (single-process)
    And the autonomous toggle is off
    When the user clicks "Build prompt"
    Then the request "POST /api/regen-prompt" sends with header "Origin: http://127.0.0.1:8765"
    And the request sends with header "Host: 127.0.0.1:8765"
    And the response is 200

  Scenario: Build prompt in dev-server proxy mode (browser at `localhost:5173`)
    Given the user opens the SPA at "http://localhost:5173/" (Vite dev server, `make run-frontend`)
    And the backend is running at "http://127.0.0.1:8765/"
    When the user clicks "Build prompt"
    Then the browser sends "POST /api/regen-prompt" via "fetch" to a same-origin path
    And the Vite proxy intercepts the request
    And the Vite proxy rewrites the request "Origin" header to "http://127.0.0.1:8765"
    And the Vite proxy (changeOrigin: true) rewrites the request "Host" header to "127.0.0.1:8765"
    And the backend receives the rewritten request
    And the backend Origin/Host gate sees a same-shape request (Origin matches the bound port)
    And the response is 200
    And the regen-prompt-block renders in the browser at "localhost:5173"

  Scenario: Pre-rewrite Origin sent direct to backend is refused
    Given the backend is running at "http://127.0.0.1:8765/"
    When a tester sends "POST /api/regen-prompt" directly to the backend with header "Origin: http://localhost:5173"
    Then the response is 403 (Origin not in the bound-port allow-list)
    And no prompt body is returned

  References: FR-9, FR-10, FR-11, FR-12, FR-31, FR-32, FR-33, FR-34, FR-37, FR-41, NFR-7, AC-11, AC-16, AC-17, AC-18, AC-19, AC-20, AC-21.

---

## Feature: Build a regeneration prompt for the whole project

  As the spec author
  I want to assemble a single regen prompt that walks multiple stages in order
  So that I can re-run a slice of the pipeline with one paste

  Background:
    Given the SPA is loaded
    And the user navigates to "/project/development/spec_driven"

  Scenario: Project parent route renders the stage map and master panel
    Then the page shows six stage entries (intake, interview, research, spec, validation, execution)
    And each stage entry has a checkbox (default checked)
    And each stage's modules are listed as nested checkboxes (default checked)
    And one autonomous-mode toggle drives the project-level prompt
    And one "Build prompt" button drives the project-level prompt

  Scenario: Combined prompt walks selected stages in order
    Given the user un-checks the "intake" stage and the "execution" stage
    When the user clicks "Build prompt"
    Then "POST /api/regen-prompt" sends "stages": ["interview","research","final_specs","validation"]
    And the response 200's "selected_stages_count" is 4
    And the assembled prompt contains exactly four stage sections
    And the stage sections appear in the order: interview, research, final_specs, validation
    And each section names its invocation hint and module list

  Scenario: Project autonomous toggle and per-stage panels share state
    Given the project-level autonomous toggle is off
    When the user toggles it on
    Then localStorage "spec_driven.autonomous_mode.v1" is "true"
    And every per-stage Regenerate panel in any other tab updates via the "storage" event
    When the user toggles it off
    Then the value is "false" and propagates again

  References: FR-32, FR-34, AC-22, AC-23.

---

## Feature: CSRF defense via Origin / Host gate

  As a security-conscious operator
  I want every state-changing endpoint to refuse foreign origins or wrong ports
  So that a malicious page cannot drive the local backend through a CSRF or DNS-rebind

  Background:
    Given the backend is running at "http://127.0.0.1:8765/"
    And the SPA is loaded in a browser tab against the backend
    And the Origin/Host allow-list at the bound port is {"http://127.0.0.1:8765","http://localhost:8765"} for Origin and {"127.0.0.1:8765","localhost:8765"} for Host

  Scenario Outline: Foreign and malformed origins are refused
    When a request "<method>" "<endpoint>" is sent direct to the backend with header Origin "<origin>" and Host "<host>"
    Then the response is "<status>"

    Examples:
      | method | endpoint              | origin                       | host                  | status |
      | PUT    | /api/file             | http://127.0.0.1:8765        | 127.0.0.1:8765        | 200    |
      | PUT    | /api/file             | http://localhost:8765        | localhost:8765        | 200    |
      | PUT    | /api/file             | http://localhost:8765        | 127.0.0.1:8765        | 200    |
      | PUT    | /api/file             | http://127.0.0.1:8765        | localhost:8765        | 200    |
      | PUT    | /api/file             | http://localhost:5173        | localhost:5173        | 403    |
      | PUT    | /api/file             | http://attacker.example.com  | 127.0.0.1:8765        | 403    |
      | PUT    | /api/file             | (missing)                    | 127.0.0.1:8765        | 403    |
      | PUT    | /api/file             | http://127.0.0.1:8765        | (missing)             | 403    |
      | PUT    | /api/file             | http://[::1]:8765            | [::1]:8765            | 403    |
      | POST   | /api/regen-prompt     | http://localhost:5173        | localhost:5173        | 403    |
      | POST   | /api/promote          | http://attacker.example.com  | 127.0.0.1:8765        | 403    |
      | DELETE | /api/promote          | http://localhost:5173        | localhost:5173        | 403    |

  Scenario: PATCH and DELETE on /api/file are not advertised
    When a request "PATCH /api/file" is sent with valid Origin/Host
    Then the response is 405
    When a request "DELETE /api/file" is sent with valid Origin/Host
    Then the response is 405

  Scenario: Vite proxy mode — full e2e with rewritten headers
    Given the SPA is loaded at "http://localhost:5173/" (Vite dev)
    When the SPA performs any state-changing fetch ("PUT /api/file", "POST /api/regen-prompt", "POST /api/promote", "DELETE /api/promote")
    Then the Vite proxy rewrites Origin to "http://127.0.0.1:8765" and Host to "127.0.0.1:8765"
    And the backend gate accepts the rewritten request
    And the response is 200

  Scenario: Pre-rewrite middleware unit test (post-mutation contract)
    Given a unit test posts "PUT /api/file" to the FastAPI app via TestClient
    When the test sets Origin "http://127.0.0.1:8765" and Host "127.0.0.1:8765" (post-rewrite shape)
    Then the response is 200

  Scenario: Pre-rewrite middleware unit test (pre-mutation contract)
    Given a unit test posts "PUT /api/file" to the FastAPI app via TestClient
    When the test sets Origin "http://localhost:5173" and Host "localhost:5173" (pre-rewrite shape — what the browser sends in dev mode)
    Then the response is 403
    # This shape is what would arrive if the Vite proxy "configure" hook is dropped.

  References: FR-9, NFR-7, AC-11, AC-12.

---

## Feature: Path sandbox and traversal defense

  As a security-conscious operator
  I want every file path to be resolved inside EXPOSED_TREE
  So that no probe — encoded or not — leaks the filesystem above the repo root

  Background:
    Given the backend is running at "http://127.0.0.1:8765/"

  Scenario Outline: Path traversal and existence-oracle probes collapse to single 404
    When a request "GET /api/file?path=<path>" is sent
    Then the response is 404
    And the response detail does NOT distinguish "exists outside sandbox" from "does not exist"

    Examples:
      | path                                          |
      | ../../../etc/passwd                           |
      | ..%2F..%2Fetc%2Fpasswd                        |
      | %2e%2e/%2e%2e/etc/passwd                      |
      | C:\Windows\win.ini                            |
      | CLAUDE.md::$DATA                              |
      | CON                                           |
      | NUL                                           |
      | PROGRA~1\foo                                  |
      | mixed\\slashes/CLAUDE.md                      |
      | CLAUDE.md\                                    |
      | CLAUDE.md:stream                              |
      | spec.md .md                              |

  Scenario: Symlinks and Windows junctions are refused outright
    Given a symlink "specs/sneaky" pointing to "/etc"
    When a request "GET /api/file?path=specs/sneaky/passwd" is sent
    Then the response is 404
    And no realpath is leaked in any header or body

  Scenario: Disallowed extension returns 415
    When a request "GET /api/file?path=specs/development/spec_driven/scratch.exe" is sent
    Then the response is 415

  Scenario: 1.5 MB file returns 413 on read
    Given "specs/development/spec_driven/findings/big.md" is 1.5 MB
    When a request "GET /api/file?path=specs/development/spec_driven/findings/big.md" is sent
    Then the response is 413

  Scenario: Read response carries hardening headers
    When a request "GET /api/file?path=CLAUDE.md" is sent
    Then the response is 200
    And the response header "X-Content-Type-Options" is "nosniff"
    And the response header "Content-Disposition" is "attachment"

  Scenario: SVG is not in the allowlist
    Given a file "specs/development/spec_driven/findings/diagram.svg" exists
    When a request "GET /api/file?path=specs/development/spec_driven/findings/diagram.svg" is sent
    Then the response is 415

  References: FR-2, FR-4, FR-5, FR-8, NFR-5, NFR-9, NFR-10, NFR-11, NFR-12, AC-1, AC-2.

---

## Feature: Resume an autonomous regeneration mid-pipeline

  As the spec author
  I want a paste from the SPA's regen-prompt-block to drive a Claude Code session in autonomous mode without prompting me
  So that long sequences finish without re-asking me trivia

  Background:
    Given the user has copied an "# EXECUTION MODE: AUTONOMOUS" prompt from the SPA
    And the prompt selects stages ["research", "final_specs", "validation"]
    And the prompt inlines "revised_prompt.md" plus follow-ups 001 and 002

  Scenario: Autonomous header suppresses AskUserQuestion
    When the user pastes the prompt into a fresh Claude Code CLI session
    Then Claude does not call "AskUserQuestion" at any point during the run
    And every ambiguous decision is recorded inline in the produced artifact as "judgment call: chose X because Y"
    And every requested artifact (dossier.md, spec.md, strategy.md + per-level files) is produced in the same turn before stopping
    And iteration bounds (3 revision rounds per unit, 30-minute wall clock) still apply
    And on bound trip a clean halt with a "pipeline.halted" event is emitted

  Scenario: Read-zero regeneration deletes prior outputs first
    Given "findings/dossier.md" exists from a prior run
    And "findings/angle-1.md" through "findings/angle-4.md" exist
    And "findings/promoted.md" exists with a pinned recommendation
    When the autonomous regen prompt runs stage 3
    Then "regen.delete.planned" is appended to "events.jsonl" once per file (excluding "findings/promoted.md")
    And "regen.delete.completed" is appended once with the count of deleted files
    And after deletion the deleted files no longer exist on disk
    And "findings/promoted.md" still exists on disk
    Then the new generation reads only the inputs (revised_prompt.md, follow-ups, qa.md, promoted.md, CLAUDE.md, .claude/agent_refs/research/*.md)
    And the new generation writes the new "findings/dossier.md" and per-angle files
    And "regen.write.completed" is appended for each file written (path + bytes)
    And the verbatim text of every pin in "findings/promoted.md" appears in the new "dossier.md" or in a "## Pinned items (orphaned)" section

  Scenario: Pin re-insertion at natural location
    Given "validation/promoted.md" contains a pinned "AC-7" block (verbatim text)
    When the autonomous regen runs stage 5
    Then the regenerated "validation/acceptance_criteria.md" contains "AC-7" verbatim at the natural numerical slot
    And no "## Pinned items (orphaned)" section is present (because AC-7's slot exists)

  Scenario: Pin orphan when natural slot disappears
    Given "interview/promoted.md" contains a pinned Q/A pair attributed to round1.removed-category
    And the new run produces no "round1.removed-category" categories
    When the autonomous regen runs stage 2
    Then the regenerated "interview/qa.md" contains a "## Pinned items (orphaned)" section
    And that section contains the verbatim pinned Q/A pair
    And the pin is NEVER silently dropped

  Scenario: Stage 6 regeneration deletes the entire project folder, not promoted.md
    Given the user pastes a regen prompt selecting stage 6 ("execution") for "projects/spec_driven/"
    And no "projects/spec_driven/promoted.md" exists (stage 6 has no promotion in v1)
    When Claude executes the prompt
    Then "regen.delete.planned" is emitted for every file under "projects/spec_driven/"
    And after deletion "projects/spec_driven/" is empty (or absent)
    And the new generation rebuilds "projects/spec_driven/{README.md, Makefile, backend/, frontend/}" from "final_specs/spec.md" + "validation/*.md"

  Scenario: pre_reading_consulted is recorded for each coordinated stage
    When Claude starts stage 5 of the autonomous run
    Then the first event for stage 5 in "events.jsonl" is "validation.started"
    And that event carries a non-empty array "pre_reading_consulted" listing absolute paths to the playbook + agent_refs files actually loaded
    And the array contains absolute paths matching ".claude/skills/agent_team/playbooks/validation.md"
    And the array contains absolute paths matching ".claude/agent_refs/validation/general.md"
    And the array contains absolute paths matching ".claude/agent_refs/validation/development.md"

  References: FR-37, FR-38, FR-41, NFR-15, AC-16, AC-17, AC-18.

---

## Feature: Stage 6 multi-mode dev workflow runs end-to-end

  As the spec author
  I want every advertised runtime mode (`make run-prod`, `make run-frontend`, plain `make run`) to actually serve the SPA and accept state-changing requests
  So that "documented mode" never means "doesn't actually work"

  Background:
    Given the repo is on the canonical Windows host
    And the python venv is bootstrapped (no `uv run` failure path)

  Scenario: Single-process mode boot smoke
    When the user runs "make run-prod"
    Then the FastAPI process starts cleanly within 5 seconds
    And "GET /api/tree" returns 200 with the recursive shape
    And the SPA bundle is served at "/" from "backend/static/"
    And the SPA loads in a real browser at "http://127.0.0.1:8765/"
    And the browser sidebar walks the recursive children and shows non-empty "Projects" subtree

  Scenario: Vite dev mode boot smoke
    When the user runs "make run-frontend" in one terminal AND "make run-backend" in another
    Then the SPA loads at "http://localhost:5173/"
    And the SPA fetches "GET /api/tree" through the Vite proxy
    And the response 200 carries the recursive shape
    And "POST /api/regen-prompt" through the Vite proxy returns 200 (the proxy `configure` hook rewrites Origin to "http://127.0.0.1:8765")

  Scenario: `make run` is an alias for `make run-backend`
    When the user runs "make run"
    Then the FastAPI process binds "127.0.0.1:8765" only (NOT "0.0.0.0")
    And no listening socket exists on a non-loopback interface

  Scenario: Boot smoke fails fast on bind error
    Given another process is already bound to "127.0.0.1:8765"
    When the user runs "make run-prod"
    Then the process exits non-zero within 3 seconds
    And the error message names the conflicting port

  Scenario: e2e suite has one Playwright project per advertised mode
    When the e2e CI lane runs
    Then "playwright.config.ts" lists at least two project entries
    And one project boots "make run-prod" and runs the golden-path scenario
    And one project boots "make run-frontend + make run-backend" and runs the same golden-path scenario
    And both projects pass

  Scenario: Manual walkthrough is emitted before sign-off
    Given all automated levels (unit, system, security, performance, accessibility) pass for the work unit
    When the parent finalizes the work unit
    Then a "validation.requires_manual_walkthrough" event is appended to "events.jsonl"
    And the parent surfaces a one-line message to the user: "manual walkthrough needed: <unit>"

  Scenario: Cross-platform skip markers respected
    Given a unit test asserts POSIX symlink behavior
    When the test runs on win32
    Then it is recorded as "STATUS=SKIPPED-WINDOWS-symlink-requires-developer-mode"
    And the test does NOT silently pass

  Scenario: `uv run` invocations have a pip fallback
    Given the Makefile target "test-backend" prefers "uv run pytest"
    When "uv run" exits with EXCEPTION_ACCESS_VIOLATION
    Then the Makefile falls back to ".venv/bin/pytest" (or ".venv/Scripts/pytest.exe" on Windows)
    And the test suite still runs to completion

  References: FR-39, NFR-3, NFR-14, AC-28, AC-29 + development.md required-validation-moves §1, §4, §5, §6, §7.

---

## Feature: Light-theme app chrome with intentional dark carve-outs

  As the spec author
  I want the entire app chrome rendered light regardless of OS preference
  So that the cross-project light-only convention is not silently overridden

  Background:
    Given the SPA is loaded
    And the user's OS reports "prefers-color-scheme: dark"

  Scenario: Body chrome is light
    Then the rendered "body" element resolves background-color to a near-white color
    And the rendered "body" element computes "color-scheme: light"
    And no computed CSS rule on body, sidebar, toolbar, or main-pane chrome is gated by "@media (prefers-color-scheme: dark)"

  Scenario Outline: Intentional dark carve-outs
    Given a "<surface>" element is rendered
    Then the computed background-color is a dark color
    And the contrast ratio between rendered text and that background meets WCAG AA (>= 4.5:1)

    Examples:
      | surface                     |
      | .markdown-view pre          |
      | .code-view pre              |
      | .regen-prompt-block pre     |

  Scenario: No dark-mode toggle is exposed in the UI
    Then no element with role "switch" or text matching "dark" / "theme" exists in the toolbar or settings UI

  References: NFR-16, FR-40 + project/development.md light-theme rule.

---

## Feature: Read-zero regeneration audit log

  As the spec author
  I want every regeneration to leave a verifiable trail of what got deleted and what got written
  So that a regen run is reproducible from `events.jsonl` alone

  Background:
    Given a regen prompt selects stage 5 (validation strategy)
    And "validation/strategy.md" and "validation/acceptance_criteria.md" exist
    And "validation/promoted.md" exists with one pin

  Scenario: Audit events fire in the correct order
    When Claude executes the prompt
    Then events.jsonl appends, in this order:
      | event                       | payload field        |
      | validation.started          | pre_reading_consulted |
      | regen.delete.planned        | path                 |
      | regen.delete.planned        | path                 |
      | regen.delete.completed      | count                |
      | regen.write.completed       | path, bytes          |
      | regen.write.completed       | path, bytes          |
      | validation.pass             | unit                 |
    And "validation/promoted.md" is NOT among the deleted paths

  Scenario: A level run with no audit events is treated as not having run
    Given a level worker writes its artifact but emits no "validation.started" event
    When the parent synthesizes the strategy
    Then the parent flags the missing-audit case as a "critical" finding
    And the affected level is re-run before the strategy is finalized

  References: FR-37, FR-38, NFR-15 + general.md principle §5, §8.

---

## Feature: Severity flows from blast radius

  As the validation strategist
  I want severities derived from blast radius, not recency
  So that an unexploited XSS still halts before a flaky test does

  Scenario: XSS in markdown render path is critical
    Given an automated test detects raw "<script>" reaching the rendered DOM
    Then the issue is recorded with severity "critical"
    And the parent halts the work unit immediately
    And no revision rounds proceed without explicit user approval

  Scenario: A11y "Recommended" gap is a warning
    Given a Lighthouse run flags a recommended-tier a11y gap
    Then the issue is recorded with severity "warning"
    And the work unit does not halt

  Scenario: Latent render error on deep-link is critical
    Given a Playwright test opens "/file/specs%2Fdevelopment%2Fspec_driven%2Finterview%2Fqa.md" directly
    And the main pane is empty (no fallback rendered)
    Then the issue severity is "critical"

  Scenario: API shape drift between front and back is critical
    Given a unit test passes on backend (asserting "result['projects']") and frontend (reading "node.children")
    And the consumer-walk test discovers no projects rendered
    Then the issue is recorded as "API shape drift between front and back" with severity "critical"

  References: general.md severity table + development.md severity escalations.

---

## Feature: Manual walkthrough surfaces what e2e cannot

  As the spec author
  I want a final manual pass before sign-off
  So that visual hierarchy, color contrast, motion, and focus visibility are caught

  Scenario: Walkthrough event is emitted after automated levels pass
    Given unit, system, security, performance, and accessibility validation all pass
    When the parent finalizes the work unit
    Then "validation.requires_manual_walkthrough" is appended to events.jsonl
    And the parent surfaces a checklist to the user with items: "visual hierarchy", "color contrast", "motion", "focus visibility"

  Scenario: Walkthrough is required even when all automated levels are green
    Given a development task_type project completes its automated validation
    Then a manual-walkthrough event MUST be emitted before the parent declares the unit done

  References: general.md principle §4 + development.md required-validation-move §7.
