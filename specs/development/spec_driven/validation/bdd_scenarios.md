# BDD scenarios — spec_driven

Run: spec_driven-20260502-clean
Stage: 5 (Validation strategy — bdd_scenarios level)
Source spec: `C:\workspace\spec_coding\specs\development\spec_driven\final_specs\spec.md`
Inputs read: spec.md only. No prior validation/*.md files (read-zero).

These scenarios are written in Gherkin (Cucumber) style. They are intentionally framework-agnostic: they describe observable behavior so that the same scenario can drive a Playwright e2e test, a pytest+httpx backend test, or a manual smoke pass. Each Feature ties back to one primary flow from the spec or to a cross-cutting concern derived from the FRs/NFRs.

Conventions used below:

- The repo root in fixtures is `C:\workspace\spec_coding\` (Windows dev box) but tests SHOULD run on a tmp clone so deletes/edits don't dirty the working repo.
- The app is started with `make run` and reachable at `http://localhost:8765/`.
- Backend file API base: `http://localhost:8765/api/`.
- The dogfood project under test is `specs/development/spec_driven/`.
- `localStorage` keys: `spec_driven.sidebar.v1` (collapse + last-selected) and `spec_driven.autonomous_mode.v1` (boolean toggle).
- "the URL bar" = `window.location.pathname + search`.
- "the breadcrumb" = the `<nav aria-label="Breadcrumb">` block above the reader pane.

---

## Feature: First open + landing page (Flow 1)

  Background:
    Given the spec_driven app is built and running on `http://localhost:8765/`
    And the repo's `specs/development/spec_driven/final_specs/spec.md` exists
    And the repo's `specs/development/spec_driven/user_input/revised_prompt.md` exists
    And the browser has no `spec_driven.sidebar.v1` value in localStorage
    And the browser has no `spec_driven.autonomous_mode.v1` value in localStorage

  Scenario: Happy path — landing redirects to the canonical spec
    When the user navigates to `http://localhost:8765/`
    Then the URL replaces (no extra history entry) to `http://localhost:8765/file/specs/development/spec_driven/final_specs/spec.md`
    And the reader pane renders the contents of `final_specs/spec.md` as CommonMark+GFM markdown
    And the breadcrumb reads `development / spec_driven / final_specs / spec.md`
    And the sidebar's `Projects > development > spec_driven > final_specs` chain is expanded
    And the leaf for `spec.md` has `aria-selected="true"`

  Scenario: Spec missing, fall back to revised_prompt
    Given the file `specs/development/spec_driven/final_specs/spec.md` does NOT exist
    And the file `specs/development/spec_driven/user_input/revised_prompt.md` exists
    When the user navigates to `http://localhost:8765/`
    Then the URL replaces to `http://localhost:8765/file/specs/development/spec_driven/user_input/revised_prompt.md`
    And the reader pane renders `revised_prompt.md`
    And the sidebar's `Projects > development > spec_driven > user_input` chain is expanded

  Scenario: Both landing targets missing
    Given neither `final_specs/spec.md` nor `user_input/revised_prompt.md` exist for the dogfood project
    When the user navigates to `http://localhost:8765/`
    Then the reader pane shows a muted "no files yet" or equivalent empty-state message
    And the sidebar still loads with the `Settings & Shared Context` section visible

---

## Feature: Browse a project's stages (Flow 2)

  Background:
    Given the user is on `http://localhost:8765/` (landed on `final_specs/spec.md`)
    And the dogfood project has at least one file in each of the five stage subfolders

  Scenario: Click each stage subfolder and load a file from each
    When the user clicks the sidebar folder `Projects > development > spec_driven > user_input`
    Then the folder expands and the click does NOT navigate
    When the user clicks the leaf `revised_prompt.md` under `user_input`
    Then the URL pushes to `http://localhost:8765/file/specs/development/spec_driven/user_input/revised_prompt.md`
    And the reader pane renders that file
    When the user clicks the folder `interview` and then the leaf `qa.md`
    Then the URL pushes to `.../interview/qa.md`
    And the reader pane renders the structured Q/A view (per FR-41)
    When the user clicks the folder `findings` and then the leaf `dossier.md`
    Then the URL pushes to `.../findings/dossier.md`
    When the user clicks the folder `final_specs` and then the leaf `spec.md`
    Then the URL pushes to `.../final_specs/spec.md`
    When the user clicks the folder `validation` and then the first leaf
    Then the URL pushes to that leaf's path

  Scenario: Folder click toggles only — never navigates
    When the user clicks the folder `interview`
    Then the folder's `aria-expanded` flips
    And the URL bar does NOT change
    And the reader pane content does NOT change

  Scenario Outline: Stage-folder URL auto-redirects to the first file
    When the user navigates to `http://localhost:8765/file/specs/development/spec_driven/<stage>/`
    Then the URL replaces (not pushes) to the first file under `<stage>` per FR-8 ordering
    And the reader pane renders that file

    Examples:
      | stage       |
      | user_input  |
      | interview   |
      | findings    |
      | final_specs |
      | validation  |

---

## Feature: Browse Settings & Shared Context (Flow 3)

  Background:
    Given the user is on `http://localhost:8765/`
    And `CLAUDE.md` exists at the repo root
    And `.claude/agents/agent_team__interview_manager.md` exists
    And `.claude/skills/agent_team/SKILL.md` exists

  Scenario: Open CLAUDE.md from the always-expanded subgroup
    When the user clicks the leaf `CLAUDE.md` under `Settings & Shared Context > CLAUDE.md`
    Then the URL pushes to `http://localhost:8765/file/CLAUDE.md`
    And the reader pane renders the file
    And the breadcrumb reads `Settings / CLAUDE.md / CLAUDE.md` (or the FR-29 form)

  Scenario: Open an Agent definition file
    When the user clicks the leaf `agent_team__interview_manager.md` under `Settings & Shared Context > Agents`
    Then the URL pushes to `http://localhost:8765/file/.claude/agents/agent_team__interview_manager.md`
    And the reader pane renders that file's markdown

  Scenario: Open a Skill SKILL.md
    When the user clicks the leaf `agent_team` (folder name) under `Settings & Shared Context > Skills`
    Then the URL pushes to `http://localhost:8765/file/.claude/skills/agent_team/SKILL.md`
    And the reader pane renders that file's markdown

  Scenario: Settings subgroups are not collapsible
    When the user attempts to collapse the subgroup `Agents`
    Then the subgroup remains expanded (no aria-expanded toggle exists on subgroup headers per FR-21)

---

## Feature: Follow internal cross-link (Flow 4)

  Background:
    Given the file `specs/development/spec_driven/final_specs/spec.md` contains a relative link `[dossier](../findings/dossier.md)`
    And `specs/development/spec_driven/findings/dossier.md` exists
    And the user is viewing `final_specs/spec.md`

  Scenario: Click an in-tree relative link, then back-button
    When the user clicks the rendered link with text `dossier`
    Then the click is intercepted by the React Router `<Link>` component (not a full page reload)
    And the URL pushes to `http://localhost:8765/file/specs/development/spec_driven/findings/dossier.md`
    And the reader pane renders `dossier.md`
    And the sidebar's `aria-selected` moves to the `dossier.md` leaf
    When the user presses the browser Back button
    Then the URL returns to `.../final_specs/spec.md`
    And the reader pane renders `spec.md` again

  Scenario: Cross-file anchor — file resolves, anchor scrolls
    Given `final_specs/spec.md` contains `[dossier-overview](../findings/dossier.md#overview)`
    And `dossier.md` contains a heading `## Overview` whose generated id is `overview`
    When the user clicks the link
    Then navigation succeeds to `dossier.md`
    And the page scrolls to the element with id `overview`

  Scenario: Cross-file anchor — file resolves but heading missing
    Given `final_specs/spec.md` contains `[ghost](../findings/dossier.md#nonexistent)`
    When the user clicks the link
    Then navigation succeeds to `dossier.md`
    And the page lands at the top of the document
    And no error UI is shown (silent fall-through per FR-35)

---

## Feature: Hit broken link (Flow 5)

  Background:
    Given the file `specs/development/spec_driven/final_specs/spec.md` is rendered
    And the file `specs/development/spec_driven/findings/missing.md` does NOT exist on disk

  Scenario: Link to a missing in-tree file renders muted, not clickable
    Given `spec.md` contains the markdown `[missing notes](../findings/missing.md)`
    When the file is rendered
    Then the text "missing notes" is wrapped in `<span class="link-broken" aria-disabled="true">`
    And the wrapper's `title` attribute equals `file not found`
    And the wrapper is NOT an `<a>` element
    When the user clicks the muted text
    Then no navigation occurs
    And the URL does NOT change

  Scenario: Link to a path outside EXPOSED_TREE renders muted with different cause
    Given `spec.md` contains `[outside](../../../etc/hosts)`
    When the file is rendered
    Then the text is wrapped in `<span class="link-broken">` with `title="outside exposed tree"`
    And it is not clickable

  Scenario: Windows case-mismatch tooltip
    Given the runtime is Windows (case-insensitive filesystem) and the spec contains `[mixed](../findings/Dossier.md)` while the actual file is `dossier.md`
    When the file is rendered
    Then the link's `title` reads `case mismatch — fix the link` per FR-33

---

## Feature: Hit external link (Flow 6)

  Background:
    Given a markdown file is being rendered in the reader pane
    And the file contains `[label](<href>)` for the href under test

  Scenario Outline: External-scheme classification opens new tab with safe rel
    When the markdown is rendered with href `<href>`
    Then the rendered link is an `<a>` element with `target="_blank"`
    And it has `rel="noopener noreferrer"`
    And it contains a visually-hidden `<span class="sr-only">(opens in new tab)</span>` per FR-33
    When the user clicks the link
    Then the browser opens `<href>` in a new tab/window
    And the current tab's URL does NOT change

    Examples:
      | href                            |
      | https://example.com/path        |
      | http://internal.box/page        |
      | mailto:dev@example.com          |
      | ftp://ftp.example.org/file.zip  |
      | //cdn.example.com/lib/x.js      |

  Scenario: Schemeless absolute path is NOT external
    Given a markdown file contains `[a](/api/file?path=foo.md)`
    When rendered
    Then the link is classified per FR-33 case 3 (relative-internal) — NOT external
    And it is treated as a broken-internal link (since `/api/...` is not under EXPOSED_TREE) with title `outside exposed tree`

---

## Feature: Edit a file (Flow 7)

  Background:
    Given the user is viewing `specs/development/spec_driven/findings/dossier.md`
    And the file is well under 2 MB
    And the file's text on disk is `LAST_SAVED`

  Scenario: Happy path — edit, save with Ctrl+S, dirty state clears
    When the user clicks the ✎ Edit button
    Then the rendered markdown is replaced by a textarea editor
    And the toolbar shows Save, Discard, and Close-editor buttons
    And the Save button is disabled
    And no dirty-dot is visible
    When the user types ` edit-marker` at the end of the textarea
    Then the textarea text differs from `LAST_SAVED`
    And the textual badge "Unsaved changes" is shown
    And the filled-circle dirty-dot appears near the file path / Close button
    And the Save button is enabled
    When the user presses Ctrl+S
    Then the frontend calls `PUT http://localhost:8765/api/file` with `{path: "specs/development/spec_driven/findings/dossier.md", text: <textarea contents>}`
    And the backend writes via `tempfile.mkstemp` + `os.fsync` + `os.replace()` (atomic-replace per FR-14a)
    And the response is 200
    And the `lastSavedText` is updated to the new text
    And the dirty-dot clears
    And the textual badge "Unsaved changes" is removed
    And the aria-live region announces "Saved."
    And the editor remains open (closing is an explicit user action per FR-40)

  Scenario: Discard reverts edits without writing
    When the user types changes
    And the user clicks Discard
    Then the textarea content reverts to `LAST_SAVED`
    And the dirty-dot is cleared
    And no `PUT /api/file` call is made

  Scenario: Close-editor with unsaved changes warns
    When the user types changes
    And the user clicks Close-editor
    Then a confirmation prompt or inline warning surfaces (implementation-defined modal vs inline)
    And declining keeps the editor open with edits intact
    And confirming closes the editor and discards unsaved edits

  Scenario: Cmd+S on macOS-class browsers also saves
    Given the platform reports macOS
    When the user presses Cmd+S inside the textarea
    Then the same save flow as Ctrl+S runs
    And the browser's own "Save Page" dialog is suppressed (preventDefault)

  Scenario: Dirty state uses deep equality, not a "user typed" flag
    When the user types an extra character
    And then deletes that character so the textarea matches `LAST_SAVED` exactly
    Then the dirty-dot is NOT lit
    And the Save button is disabled (the GitHub-CRLF anti-pattern is avoided per FR-40c)

---

## Feature: Hit save error (Flow 8)

  Background:
    Given the user is viewing `specs/development/spec_driven/findings/dossier.md` in editor mode
    And the user has typed unsaved changes (dirty-dot lit)

  Scenario: 415 unsupported_extension yields a persistent inline banner
    Given the backend will respond to the next `PUT /api/file` with `415 {"detail": {"kind": "unsupported_extension"}}`
    When the user presses Ctrl+S
    Then a persistent inline banner appears ABOVE the textarea
    And the banner names the error kind `unsupported_extension`
    And the banner uses the same `link-broken` muted-style component family per FR-34/FR-40e
    And the banner does NOT auto-dismiss
    And no toast and no modal is rendered
    And the dirty-dot stays lit
    And `lastSavedText` is NOT updated

  Scenario Outline: Other error codes are surfaced verbatim with the structured kind
    Given the backend will respond with `<status> {"detail": {"kind": "<kind>"}}`
    When the user presses Ctrl+S
    Then the inline banner displays kind `<kind>`
    And the dirty-dot stays lit until a future save succeeds

    Examples:
      | status | kind                |
      | 400    | outside_sandbox     |
      | 400    | is_directory        |
      | 403    | permission_denied   |
      | 404    | file_removed        |
      | 413    | too_large           |
      | 415    | binary_content      |
      | 500    | write_failed        |

  Scenario: A subsequent successful save clears the banner
    Given the previous save failed and the banner is shown
    When the cause is fixed (e.g., user trims content under the size cap)
    And the user presses Ctrl+S and the backend returns 200
    Then the banner is removed
    And the dirty-dot clears
    And "Saved." announces

---

## Feature: Edit a single Q/A in `qa.md` (Flow 9)

  Background:
    Given the user is viewing `specs/development/spec_driven/interview/qa.md`
    And `qa.md` parses cleanly into the `## Round N` → `### {category}` → `**Q:**` → `- A:` shape (FR-41)

  Scenario: Pencil on a single Q/A opens an inline scoped editor
    Then the rendered view shows discrete blocks per round, category badge, Q tint, A tint
    And every Q and every A has its own ✎ pencil button
    When the user clicks the ✎ next to the Q text in Round 1, category "Scope"
    Then an inline editor opens scoped to JUST that Q's text
    And other Q/A blocks remain rendered (not editable)

  Scenario: Saving a single Q/A splices the change into the whole file
    When the user edits the Q text and presses Save
    Then the frontend constructs the full updated `qa.md` text by splicing the new block in place
    And calls `PUT http://localhost:8765/api/file` with `{path: "specs/development/spec_driven/interview/qa.md", text: <full new file>}`
    And on 200 the inline editor closes
    And the rendered structured view re-renders with the updated Q

  Scenario: Whole-file Edit toggle still available alongside per-block edits
    When the user clicks the file-level ✎ Edit button
    Then the structured Q/A view is replaced by the generic textarea editor (Flow 7)

  Scenario: Malformed qa.md falls back to generic markdown
    Given `qa.md` does NOT match the `## Round N` → `###` → `**Q:**` → `- A:` pattern
    When the user opens the file
    Then the reader pane renders generic markdown (FR-30)
    And no error UI is shown
    And no per-block pencils are rendered

---

## Feature: Build per-stage regen prompt (Flow 10)

  Background:
    Given the user is viewing a file inside a project's stage subfolder, e.g. `specs/development/spec_driven/findings/dossier.md`
    And `localStorage["spec_driven.autonomous_mode.v1"]` is `false`
    And the project has 0 follow-ups under `user_input/follow_ups/`

  Scenario: Default-collapsed Regenerate panel
    When the file renders
    Then a `<details>` element titled "Regenerate" is shown above the file content
    And the `<details>` is closed by default

  Scenario: Build a prompt for the Findings stage (default modules, interactive)
    When the user opens the Regenerate panel
    Then module checkboxes for stage `findings` appear, all checked, derived from `GET /api/stages?project_type=development&project_name=spec_driven`
    And the Autonomous-mode toggle reflects `false`
    When the user clicks "Build prompt"
    Then the frontend sends `POST /api/regen-prompt` with `{project_type: "development", project_name: "spec_driven", stages: ["findings"], modules: {findings: [<all>]}, autonomous: false}`
    And the response is `{prompt, warning, selected_stages_count: 1, follow_ups_count: 0, autonomous: false, bytes: <N>}`
    And the prompt opens with `# EXECUTION MODE: INTERACTIVE`
    And the prompt inlines `revised_prompt.md` (or `raw_prompt.md` if missing)
    And the `### Constraints` section includes the read-zero language (delete-then-regenerate)
    And the assembled prompt is rendered inline inside a bordered `regen-prompt-block` (no inner `<details>`)
    And the prompt block has a header bar containing the title "Assembled prompt", a "Wrap" toggle (default checked), and a prominent **Copy** button (label "Copy")
    And the breakdown line reads `1 stages selected, 0 follow-ups inlined, autonomous=false, X KB` in the actions row beside "Build prompt"
    And no warning banner is shown (response.warning is null)

  Scenario: Toggling Autonomous mode flips header and inserts the imperative line
    When the user flips the Autonomous-mode toggle to ON
    And clicks "Build prompt"
    Then the prompt opens with `# EXECUTION MODE: AUTONOMOUS`
    And the next non-blank line is the verbatim sentence "Do not call AskUserQuestion. For anything unclear, use your best judgment, record the choice inline in the artifact, and keep going. Produce every requested artifact below in this single turn before stopping."
    And `localStorage["spec_driven.autonomous_mode.v1"]` is now `"true"`

  Scenario: Above 50 KB the response carries a non-empty warning and a banner shows
    Given the assembled prompt's byte length will exceed 51200
    When the user clicks "Build prompt"
    Then the response.warning is a non-empty string
    And the prompt is still emitted in full (warn-don't-truncate per FR-14c)
    And a muted banner reads `warning: <text> — verify your selection before pasting` per FR-42e

  Scenario: Above 1 MB the endpoint returns 413
    Given the assembled prompt's byte length would exceed 1048576
    When the user clicks "Build prompt"
    Then the response is `413 {"detail": {"kind": "too_large"}}`
    And the `regen-prompt-block` is not rendered
    And an error banner names the kind

  Scenario: Copy flips its label briefly
    Given a prompt has been built and the `regen-prompt-block` is visible
    When the user clicks the **Copy** button in the prompt block's header bar
    Then the button label reads "Copied!" for ~1.5 seconds
    And the system clipboard contains the full prompt text

  Scenario: Soft-wrap toggle controls prompt-body wrapping
    Given a prompt has been built and the `regen-prompt-block` is visible
    And the "Wrap" checkbox in the header bar is checked by default
    Then the `<pre>` body has `white-space: pre-wrap` and long lines wrap inside the block
    When the user unchecks the "Wrap" checkbox
    Then the `<pre>` body switches to fixed-width with horizontal scroll for lines wider than the block
    And the wrap state is NOT persisted to `localStorage`

---

## Feature: Build whole-project regen prompt (Flow 11)

  Background:
    Given the dogfood project exists at `specs/development/spec_driven/`
    And the user is on any page

  Scenario: Sidebar "↗ project page" link navigates to the project parent
    When the user clicks the "↗ project page" affordance on the sidebar entry for `Projects > development > spec_driven`
    Then the URL pushes to `http://localhost:8765/project/development/spec_driven`
    And the reader pane shows the project parent page (FR-43)
    And the page lists all six stages with module checkboxes (default all checked)

  Scenario: Master Regenerate panel selects any subset of stages and modules
    When the user un-checks every module under the `interview` and `validation` stages
    And clicks "Build prompt"
    Then the frontend sends `POST /api/regen-prompt` with `stages` listing only the stages with at least one module checked
    And `modules` reflects the user's selection per stage
    And the response's `selected_stages_count` matches the number of stages with at least one module
    And the assembled prompt includes invocation hints + module paths only for the selected scopes

  Scenario: Autonomous-mode toggle is shared with the per-stage panel
    Given the per-stage panel toggled autonomous-mode ON earlier
    When the project page loads
    Then the master panel's Autonomous-mode toggle is also ON
    When the user toggles it OFF on the project page
    Then the per-stage panel (in another tab) reflects OFF on its next render via the storage event
    And `localStorage["spec_driven.autonomous_mode.v1"]` is `"false"`

  Scenario: Follow-ups are inlined and counted
    Given the project has two `user_input/follow_ups/*.md` files
    When the user clicks "Build prompt" with default selection
    Then `follow_ups_count` in the response equals 2
    And the prompt body lists both follow-up relative paths under a "Follow-ups inlined" section

---

## Feature: Refresh sidebar (Flow 12)

  Background:
    Given the app is loaded and the sidebar is rendered
    And `specs/development/spec_driven/findings/extra.md` does NOT yet exist

  Scenario: Externally adding a file becomes visible after Refresh
    When an external process creates `specs/development/spec_driven/findings/extra.md`
    Then the sidebar still does NOT show `extra.md` (no filesystem watcher per FR-3 / Out of Scope)
    When the user clicks the sidebar's "Refresh" button
    Then the frontend re-fetches `GET /api/tree`
    And the response includes `extra.md` under `findings`
    And the sidebar re-renders showing the new leaf
    And expand state is preserved for unchanged folders

  Scenario: Externally removing a file disappears after Refresh
    Given `findings/extra.md` exists and is shown in the sidebar
    When an external process deletes the file
    And the user clicks Refresh
    Then `extra.md` is no longer present in the sidebar
    And no error is raised in the console

---

## Feature: Stale-tree click (Flow 13)

  Background:
    Given the sidebar shows a leaf for `specs/development/spec_driven/findings/extra.md`
    And the file has been deleted on disk after the last `GET /api/tree`

  Scenario: Click a stale leaf — main pane shows non-modal "no longer exists" with refresh
    When the user clicks the stale leaf
    Then the URL pushes to `http://localhost:8765/file/specs/development/spec_driven/findings/extra.md`
    And the frontend calls `GET /api/file?path=specs/development/spec_driven/findings/extra.md`
    And the backend returns `404 {"detail": {"kind": "file_removed"}}` per FR-5.7
    And the main pane shows an inline non-modal message: "this file no longer exists — refresh sidebar"
    And a "Refresh" button is rendered inline in the main pane (the same affordance as FR-28)
    When the user clicks the inline Refresh button
    Then `GET /api/tree` re-fetches and the stale leaf disappears

  Scenario: Tree-walk silently handles mid-walk file removal (NFR-12 / AC-15)
    Given the tree-walk is in progress
    And the file `specs/development/spec_driven/findings/extra.md` is removed concurrently
    When the response is returned
    Then the response status is 200
    And `extra.md` is either present or absent (no torn state) but the API does NOT return 500

---

## Feature: Restore session (Flow 14)

  Background:
    Given the user has the app open and has expanded a specific tree-state
    And the user is currently viewing `specs/development/spec_driven/findings/dossier.md`

  Scenario: Reload preserves URL-driven selection
    When the user presses F5 / reload
    Then the URL is unchanged
    And the reader pane re-renders the same `dossier.md`
    And the sidebar restores the previously expanded folder set from `localStorage["spec_driven.sidebar.v1"]`
    And the leaf for `dossier.md` has `aria-selected="true"` (URL takes precedence over saved last-selected)

  Scenario: URL takes precedence over saved last-selected file
    Given `localStorage["spec_driven.sidebar.v1"]` records last-selected `final_specs/spec.md`
    When the user opens the app at URL `.../file/specs/development/spec_driven/findings/dossier.md`
    Then the reader pane renders `dossier.md` (NOT `spec.md`)
    And the saved last-selected is overridden by the URL per FR-23

  Scenario: Corrupted localStorage falls back to defaults silently
    Given `localStorage["spec_driven.sidebar.v1"]` is the literal string `not-json`
    When the user opens `http://localhost:8765/`
    Then the app loads without throwing
    And the sidebar uses default collapse state (Settings expanded; Projects fully collapsed except the current ancestor chain)
    And no console error is logged about the corrupted JSON

  Scenario: Fresh browser visit — no localStorage at all
    Given the browser has no `spec_driven.*` localStorage keys
    When the user opens `http://localhost:8765/`
    Then the sidebar is fully collapsed under `Projects` except for the ancestor chain of the URL-pointed file
    And `Settings & Shared Context` is expanded with its three subgroups

---

## Feature: Cross-cutting — Markdown rendering (CommonMark + GFM + Shiki + image placeholder + .jsonl per-line)

  Background:
    Given the reader pane is visible
    And the active file is one of the supported renderable kinds

  Scenario: CommonMark + GFM features are rendered
    Given a `.md` file with: ATX headings, fenced code blocks, GFM tables, task lists, autolinks, and strikethrough
    When the file is rendered
    Then the headings have ids generated per FR-30 GFM kebab-case rule (lowercase ASCII, drop punctuation, hyphenate spaces, dedupe with `-1`/`-2`)
    And the GFM table is rendered as an HTML `<table>`
    And task-list checkboxes appear as disabled checkboxes
    And autolinks render as `<a>` elements (classified per FR-33)
    And strikethrough renders as `<del>`

  Scenario: Heading-id collision suffixing
    Given a file contains two headings both with text "Overview"
    When rendered
    Then the first heading gets id `overview`
    And the second gets id `overview-1`

  Scenario: Empty-after-slug heading uses `section` base
    Given a heading consists only of punctuation that the slugger would strip
    When rendered
    Then its id is `section` (or `section-1` etc. on collision)

  Scenario Outline: Fenced code blocks use Shiki by language
    Given a fenced block with info string `<lang>`
    When rendered
    Then the `<pre>` is highlighted by Shiki with language `<resolved>`
    And the `<pre>` has `tabindex="0"` per FR-31
    And the pre is keyboard-scrollable when overflowing

    Examples:
      | lang        | resolved    |
      | python      | python      |
      | ts          | typescript  |
      | bash        | bash        |
      | json        | json        |
      | (none)      | plaintext   |
      | klingon     | plaintext (unknown languages render as plain monospace) |

  Scenario: .yaml / .yml / .json render as Shiki blocks with line numbers
    Given the active file is `something.yaml`
    When rendered
    Then a single Shiki block is shown highlighted as YAML with visible line numbers per FR-32

  Scenario: .jsonl renders one Shiki block per non-blank line
    Given the active file is `events.jsonl` with three valid JSON lines, one blank line, and one malformed line
    When rendered
    Then three lines are rendered as independently highlighted JSON Shiki blocks
    And the blank line is skipped
    And the malformed line renders as plain text (no syntax highlighting)
    And no error UI is shown for the malformed line

  Scenario: Internal-image markdown renders a placeholder span
    Given the markdown contains `![Architecture diagram](./diagram.png)` resolving inside EXPOSED_TREE
    When rendered
    Then a `<span class="image-placeholder">` is rendered containing the alt text "Architecture diagram"
    And the span has `title="v1: images not rendered"` per FR-36
    And no `<img>` element is emitted
    And no `/api/file` request is issued for the image

  Scenario: External-image markdown renders straight `<img>`
    Given the markdown contains `![logo](https://cdn.example.com/logo.png)`
    When rendered
    Then an `<img src="https://cdn.example.com/logo.png" alt="logo">` is emitted (no proxying, FR-36)

---

## Feature: Cross-cutting — Sidebar tree shape & ordering (FR-7/8/9/10 incl. validation/ priority)

  Background:
    Given the backend serves `GET /api/tree`
    And the repo contains the dogfood project `specs/development/spec_driven/`

  Scenario: Top-level shape is Settings then Projects, in that order
    When the frontend fetches `GET /api/tree`
    Then the JSON has two top-level sections, `settings` first, `projects` second per FR-7

  Scenario: Settings has the three fixed subgroups in fixed order
    Then `settings` contains `claude_md`, `agents`, `skills`
    And `claude_md` is a single leaf for `CLAUDE.md`
    And `agents` is one leaf per `.claude/agents/*.md` sorted alphabetically
    And `skills` is one leaf per `.claude/skills/*/SKILL.md` sorted by folder name

  Scenario: Projects -> task_type -> task_name -> five fixed stages
    Then `projects` lists task types alphabetically
    And each task_type lists task_names alphabetically
    And each project has exactly the five entries `user_input`, `interview`, `findings`, `final_specs`, `validation` in that fixed order per FR-7

  Scenario: Files within a stage sorted alphabetically (case-insensitive ASCII)
    Given `findings/` contains `dossier.md`, `Angle-A.md`, `angle-b.md`
    When the tree is fetched
    Then the file order is `Angle-A.md`, `angle-b.md`, `dossier.md` (case-insensitive ASCII compare with stable tie-break per FR-8)

  Scenario: validation/ priority order
    Given `validation/` contains `acceptance_criteria.md`, `bdd_scenarios.md`, `strategy.md`, `system_tests.md`, `unit_tests.md`, `security.md`
    When the tree is fetched
    Then the file order under `validation` is exactly:
      | 1 | strategy.md             |
      | 2 | acceptance_criteria.md  |
      | 3 | bdd_scenarios.md        |
      | 4 | security.md             |
      | 5 | system_tests.md         |
      | 6 | unit_tests.md           |
    And this matches FR-8 (priority three first; remainder alphabetical)

  Scenario: Missing stage subfolder is included with `present: false`
    Given `specs/development/spec_driven/validation/` does NOT exist on disk
    When the tree is fetched
    Then the `validation` entry is present with `present: false` and an empty file list per FR-9
    And the sidebar renders the entry as a muted-italic non-expandable leaf with `title="not yet generated"` per FR-24
    And keyboard arrow navigation skips it (cannot focus)

  Scenario: Per-project tree only exposes the five stage subfolders
    Given the project directory contains an extra subfolder `notes/` (NOT one of the five)
    When the tree is fetched
    Then `notes/` does NOT appear under the project per FR-10
    And no leaf inside `notes/` appears in the tree

  Scenario: Symlinks are silently skipped
    Given `specs/development/spec_driven/findings/symlink.md` is a symlink to `dossier.md`
    When the tree is fetched
    Then `symlink.md` does NOT appear in the file list per FR-4
    And `dossier.md` still appears

  Scenario: Long filenames middle-ellipsize on files, end-ellipsize on folders
    Given a file with a very long name `a-very-long-filename-that-overflows-the-sidebar-row.md`
    When rendered
    Then the row is single-line with middle-ellipsis preserving the `.md` extension per FR-25
    And the full name appears in the row's `title` attribute
    And the parent folder rows use end-ellipsis when overflowing

---

## Feature: Cross-cutting — Dogfood self-render (open app -> spec.md -> dossier.md -> strategy.md, all in-app)

  Background:
    Given the dogfood project's `final_specs/spec.md` contains a relative link to `../findings/dossier.md`
    And `findings/dossier.md` contains a relative link to `../validation/strategy.md`
    And all three files exist on disk

  Scenario: Three-hop dogfood navigation, all push-history, no full reloads
    When the user navigates to `http://localhost:8765/`
    Then the URL replaces to `.../file/specs/development/spec_driven/final_specs/spec.md`
    And the reader renders `spec.md`
    When the user clicks the in-app link to `dossier.md`
    Then the URL pushes (NOT a full page reload — confirm via `window.performance.navigation` or a sentinel JS flag set on first load)
    And the URL is `.../file/specs/development/spec_driven/findings/dossier.md`
    And the reader renders `dossier.md`
    When the user clicks the in-app link to `strategy.md`
    Then the URL pushes to `.../file/specs/development/spec_driven/validation/strategy.md`
    And the reader renders `strategy.md`
    When the user presses Back twice
    Then the URL returns to `final_specs/spec.md`
    And the reader pane re-renders `spec.md`

  Scenario: All three files render with no markdown error UI
    Then `spec.md`, `dossier.md`, and `strategy.md` all render without inline error banners
    And all internal cross-links between them are clickable (not muted)
    And all external links open in new tabs with `rel="noopener noreferrer"`

---

## Feature: Cross-cutting — Read-zero regeneration contract surfaced in every prompt

  Background:
    Given the dogfood project exists
    And the user can build prompts via the per-stage panel (FR-42) or the project page (FR-43)

  Scenario: Constraints section names the read-zero language
    When the user clicks "Build prompt" with any non-empty stage selection
    Then the response's `prompt` field contains a `### Constraints` section
    And that section includes language equivalent to "regeneration deletes prior outputs first; new generation reads only the inputs"
    And that language appears whether `autonomous` is true or false (it is a hard contract per FR-14c.f / AC-21)

  Scenario Outline: Constraints section is present per-stage and combined-project
    When the user requests a prompt with `stages = <stages>` and default modules
    Then the assembled `prompt` string contains the substring `read-zero` OR equivalent delete-then-regenerate phrasing
    And `selected_stages_count` matches `<count>`

    Examples:
      | stages                                                      | count |
      | ["interview"]                                               | 1     |
      | ["findings"]                                                | 1     |
      | ["final_specs", "validation"]                               | 2     |
      | ["intake", "interview", "findings", "final_specs", "validation", "execution"] | 6 |

  Scenario: Constraints section also names CLAUDE.md, canonical paths, and manager-spawn contract
    When a prompt is built
    Then the `### Constraints` section also references CLAUDE.md, canonical paths under `specs/{type}/{name}/`, and the manager-spawn contract (parent-only Agent/AskUserQuestion) per FR-14c.f
    And under `autonomous=true`, the constraints additionally cite the no-AskUserQuestion rule

End of bdd_scenarios.md.
