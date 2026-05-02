# BDD scenarios — spec_driven

Run: spec_driven-20260502-141813
Stage: 5 (Validation strategy)
Authored by: validation_manager / level-specialist-02-bdd_scenarios, 2026-05-02

This artifact is per-flow Gherkin. The sister artifact `acceptance_criteria.md` is per-FR. Some overlap is expected; verbatim duplication is not. All scenarios use real fixture filenames, the real port `8765`, the real localStorage key `spec_driven.sidebar.v1`, and real URL paths.

---

## Feature: Flow 1 — First open redirects to the dogfood spec

  As a developer using spec_driven on localhost
  I want the root URL to take me directly to the most useful artifact
  So that I can start reading the dogfood project's compiled spec without typing a path

  Background:
    Given the spec_driven backend is running on port 8765
    And REPO_ROOT is `C:\workspace\spec_coding`
    And the dogfood project at `specs/development/spec_driven/` has Stages 1-4 artifacts on disk
    And `specs/development/spec_driven/user_input/revised_prompt.md` exists
    And `specs/development/spec_driven/final_specs/spec.md` exists

  Scenario: Happy path — `/` redirects to the compiled spec
    Given the user opens a fresh tab
    When the user navigates to `http://localhost:8765/`
    Then the browser receives a 302 redirect to `/projects/development/spec_driven/final_specs/spec.md`
    And the main pane renders the markdown of `specs/development/spec_driven/final_specs/spec.md`
    And the sidebar `Projects > development > spec_driven > final_specs` chain is auto-expanded
    And the leaf `spec.md` has `aria-selected="true"`

  Scenario: Edge — spec.md missing → fallback to revised_prompt.md
    Given `specs/development/spec_driven/final_specs/spec.md` does NOT exist on disk
    And `specs/development/spec_driven/user_input/revised_prompt.md` exists
    When the user navigates to `http://localhost:8765/`
    Then the browser receives a 302 redirect to `/projects/development/spec_driven/user_input/revised_prompt.md`
    And the main pane renders the contents of `revised_prompt.md`
    And the sidebar `Projects > development > spec_driven > user_input` chain is auto-expanded

  Spec refs: FR-15, FR-22, NFR-3

---

## Feature: Flow 2 — Browse a project's five stage subfolders

  As a developer
  I want to click into each of the five stage subfolders of a project
  So that I can read every artifact the spec-driven workflow produced

  Background:
    Given the spec_driven app is running on port 8765
    And REPO_ROOT is `C:\workspace\spec_coding`
    And the project `specs/development/spec_driven/` has Stages 1-4 artifacts on disk
    And the user has navigated to `/projects/development/spec_driven/final_specs/spec.md`

  Scenario: Happy path — expand each of the five stage folders in turn
    Given the sidebar shows `Projects > development > spec_driven` with its five stage children
    When the user clicks the `user_input` folder row
    Then the `user_input` folder expands and shows `raw_prompt.md` and `revised_prompt.md`
    When the user clicks the `interview` folder row
    Then the `interview` folder expands and shows `qa.md`
    When the user clicks the `findings` folder row
    Then the `findings` folder expands and shows `dossier.md` and any `angle-*.md` files
    When the user clicks the `final_specs` folder row
    Then the `final_specs` folder expands and shows `spec.md`
    When the user clicks the `validation` folder row
    Then the `validation` folder expands and shows `strategy.md`, `acceptance_criteria.md`, `bdd_scenarios.md`

  Scenario Outline: Click a file in each stage and verify URL + render
    When the user clicks the leaf `<filename>` under `<stage>` of `Projects > development > spec_driven`
    Then the URL becomes `/projects/development/spec_driven/<stage>/<filename>`
    And the main pane renders the contents of `specs/development/spec_driven/<stage>/<filename>`
    And the sidebar leaf for `<filename>` has `aria-selected="true"`

    Examples:
      | stage           | filename                  |
      | user_input      | revised_prompt.md         |
      | interview       | qa.md                     |
      | findings        | dossier.md                |
      | final_specs     | spec.md                   |
      | validation      | strategy.md               |

  Scenario: Folder click does not navigate
    Given the URL is `/projects/development/spec_driven/final_specs/spec.md`
    When the user clicks the `findings` folder row in the sidebar
    Then the URL remains `/projects/development/spec_driven/final_specs/spec.md`
    And the `findings` folder toggles its `aria-expanded` state
    And the main pane content does not change

  Spec refs: FR-7, FR-8, FR-15, FR-22, FR-26, FR-38

---

## Feature: Flow 3 — Browse Settings & Shared Context

  As a developer
  I want to read the repo-level Claude config alongside the per-project specs
  So that I can correlate orchestrator instructions with their downstream artifacts

  Background:
    Given the spec_driven app is running on port 8765
    And REPO_ROOT is `C:\workspace\spec_coding`
    And `CLAUDE.md` exists at REPO_ROOT
    And `.claude/agents/agent_team__interview_manager.md` exists
    And `.claude/agents/agent_team__research_manager.md` exists
    And `.claude/agents/agent_team__validation_manager.md` exists
    And `.claude/skills/agent_team/SKILL.md` exists
    And the dogfood project has Stages 1-4 artifacts on disk

  Scenario: Happy path — open CLAUDE.md from the sidebar
    Given the sidebar `Settings & Shared Context` section is visible with three subgroups
    When the user clicks the `CLAUDE.md` leaf
    Then the URL becomes `/settings/claude-md`
    And the main pane renders the contents of `CLAUDE.md` from REPO_ROOT
    And the breadcrumb reads `Settings / CLAUDE.md / CLAUDE.md`

  Scenario Outline: Open every kind of Settings entry
    When the user clicks the leaf at `<sidebar_path>` in the sidebar
    Then the URL becomes `<expected_url>`
    And the main pane renders the contents of `<file_on_disk>`

    Examples:
      | sidebar_path                                                         | expected_url                                              | file_on_disk                                              |
      | Settings / CLAUDE.md / CLAUDE.md                                     | /settings/claude-md                                       | CLAUDE.md                                                 |
      | Settings / Agents / agent_team__interview_manager.md                 | /settings/agents/agent_team__interview_manager.md         | .claude/agents/agent_team__interview_manager.md           |
      | Settings / Agents / agent_team__research_manager.md                  | /settings/agents/agent_team__research_manager.md          | .claude/agents/agent_team__research_manager.md            |
      | Settings / Agents / agent_team__validation_manager.md                | /settings/agents/agent_team__validation_manager.md        | .claude/agents/agent_team__validation_manager.md          |
      | Settings / Skills / agent_team                                       | /settings/skills/agent_team                               | .claude/skills/agent_team/SKILL.md                        |

  Scenario: Section 1 subgroups are not collapsible
    Given the sidebar Section 1 is rendered
    When the user attempts to click on the `Agents` subgroup header
    Then no expand/collapse animation runs
    And the `Agents` subgroup remains expanded with all agent leaves visible
    And the `Settings & Shared Context` section header itself is not collapsible

  Spec refs: FR-7, FR-15, FR-21, FR-29, FR-37

---

## Feature: Flow 4 — Follow an internal cross-link

  As a developer reading the compiled spec
  I want to jump from `final_specs/spec.md` to `findings/dossier.md` via a relative markdown link
  So that I can verify which research findings drove which spec decisions

  Background:
    Given the spec_driven app is running on port 8765
    And REPO_ROOT is `C:\workspace\spec_coding`
    And the dogfood project has Stages 1-4 artifacts on disk
    And `specs/development/spec_driven/final_specs/spec.md` contains a relative link `../findings/dossier.md`
    And `specs/development/spec_driven/findings/dossier.md` exists

  Scenario: Happy path — relative link navigates in-app and pushes history
    Given the user is on `/projects/development/spec_driven/final_specs/spec.md`
    And the rendered link to `../findings/dossier.md` is a real `<a>` element (React Router `<Link>`)
    When the user clicks the link to `../findings/dossier.md`
    Then the URL changes to `/projects/development/spec_driven/findings/dossier.md`
    And the navigation pushes a new entry onto the browser history stack
    And the main pane re-renders with the contents of `findings/dossier.md`
    And the sidebar `aria-selected` moves to the `dossier.md` leaf
    And no full-page reload occurs

  Scenario: Edge — browser back-button returns to source AND scroll position is restored
    Given the user is on `/projects/development/spec_driven/final_specs/spec.md`
    And the user has scrolled the main pane to the heading "Functional requirements"
    And the user has clicked the link to `../findings/dossier.md`
    And the URL is now `/projects/development/spec_driven/findings/dossier.md`
    When the user presses the browser back-button
    Then the URL returns to `/projects/development/spec_driven/final_specs/spec.md`
    And the main pane re-renders `final_specs/spec.md`
    And the scroll position is restored to the "Functional requirements" heading
    And the sidebar `aria-selected` moves back to `spec.md`

  Spec refs: FR-15, FR-17, FR-33, FR-38

---

## Feature: Flow 5 — Hit a broken link

  As a developer following links across stages
  I want broken links rendered as muted, non-clickable text with a tooltip explaining the cause
  So that I learn which artifact is missing without crashing the page

  Background:
    Given the spec_driven app is running on port 8765
    And REPO_ROOT is `C:\workspace\spec_coding`
    And the dogfood project has Stages 1-4 artifacts on disk
    And `specs/development/spec_driven/validation/strategy.md` does NOT exist (Stage 5 has not run)

  Scenario: Happy path — link to not-yet-generated file is muted
    Given the user opens `/projects/development/spec_driven/findings/dossier.md`
    And `dossier.md` contains a markdown link `[strategy](../validation/strategy.md)`
    When the user looks at the rendered link
    Then the link text "strategy" appears inside a `<span class="link-broken">` (no `<a>` element)
    And the `title` attribute of the span is `not yet generated` OR `file not found`
    And the span has muted color and no underline
    When the user clicks the broken link
    Then nothing happens (no URL change, no main-pane change)

  Scenario Outline: Broken-link cause classification renders the right tooltip
    Given the user is on a markdown file with a link whose href is `<href>`
    When the link is rendered
    Then it renders as `<span class="link-broken" title="<tooltip>">`
    And the span is not a clickable `<a>`

    Examples:
      | href                                  | tooltip                  |
      | ../validation/strategy.md             | not yet generated        |
      | ../findings/missing_angle.md          | file not found           |
      | ../../../etc/hosts                    | outside exposed tree     |
      | spec.md#nonexistent-anchor            | anchor not found         |

  Spec refs: FR-9, FR-24, FR-33, FR-34, FR-35

---

## Feature: Flow 6 — Hit an external link

  As a developer reading dossiers and specs that cite outside sources
  I want external links to open in a new tab with safe rel attributes
  So that I do not lose my place in the viewer and the destination cannot reach back via window.opener

  Background:
    Given the spec_driven app is running on port 8765
    And REPO_ROOT is `C:\workspace\spec_coding`
    And the dogfood project has Stages 1-4 artifacts on disk
    And the user is viewing a markdown file that contains an external link

  Scenario: Happy path — https link opens in a new tab with safe rel
    Given the rendered markdown contains `[example](https://example.com)`
    When the user clicks the link
    Then the link is rendered as `<a href="https://example.com" target="_blank" rel="noopener noreferrer">example</a>`
    And the click opens `https://example.com` in a new browser tab
    And the current viewer tab remains on its original URL

  Scenario Outline: External classification covers schemes and protocol-relative URLs
    Given the rendered markdown contains a link with href `<href>`
    When the renderer classifies the link per FR-33 case 1
    Then the link is classified as **external**
    And it is rendered as `<a href="<href>" target="_blank" rel="noopener noreferrer">`

    Examples:
      | href                          |
      | https://example.com           |
      | http://example.com            |
      | mailto:dalu198649@gmail.com   |
      | ftp://files.example.com/x.zip |
      | //cdn.example.com/lib.js      |

  Spec refs: FR-33

---

## Feature: Flow 7 — Refresh the sidebar after external file changes

  As a developer who just ran a pipeline stage that wrote new artifacts
  I want a manual refresh button on the sidebar
  So that the tree picks up new or removed files without an auto-watcher

  Background:
    Given the spec_driven app is running on port 8765
    And REPO_ROOT is `C:\workspace\spec_coding`
    And the dogfood project has Stages 1-4 artifacts on disk
    And `specs/development/spec_driven/validation/strategy.md` does NOT exist initially

  Scenario: Happy path — refresh after external add
    Given the sidebar shows `Projects > development > spec_driven > validation` as a muted-italic stage with `present: false`
    When an external process writes `specs/development/spec_driven/validation/strategy.md` to disk
    And the user clicks the sidebar's "Refresh" button
    Then the sidebar re-fetches `GET /api/tree`
    And the `validation` folder is no longer muted-italic
    And `validation` now contains a leaf `strategy.md` (priority-ordered first per FR-8)

  Scenario: Edge — refresh after deletion (file gone from tree)
    Given `specs/development/spec_driven/findings/angle-architecture.md` exists on disk
    And the sidebar shows `angle-architecture.md` under `findings`
    When an external process deletes `specs/development/spec_driven/findings/angle-architecture.md`
    And the user clicks the sidebar's "Refresh" button
    Then the sidebar re-fetches `GET /api/tree`
    And `angle-architecture.md` no longer appears under `findings`
    And the user's currently-selected file (if any) elsewhere in the tree is unchanged

  Spec refs: FR-3, FR-9, FR-28, NFR-12

---

## Feature: Flow 8 — Stale-tree click after file disappears

  As a developer whose sidebar may briefly disagree with disk
  I want a clear inline message and a refresh affordance when I click a now-deleted leaf
  So that I can recover without restarting the app

  Background:
    Given the spec_driven app is running on port 8765
    And REPO_ROOT is `C:\workspace\spec_coding`
    And the dogfood project has Stages 1-4 artifacts on disk
    And the sidebar lists `specs/development/spec_driven/findings/dossier.md`

  Scenario: Happy path — click a stale leaf shows inline refresh component
    Given the sidebar still shows `dossier.md` under `findings`
    And `specs/development/spec_driven/findings/dossier.md` was just deleted on disk
    When the user clicks the `dossier.md` leaf in the sidebar
    Then the frontend issues `GET /api/file?path=specs/development/spec_driven/findings/dossier.md`
    And the backend returns 404 with `kind: "file_removed"`
    And the main pane shows an inline non-modal message "this file no longer exists — refresh sidebar"
    And the inline message contains the same Refresh affordance as the sidebar (FR-28's secondary use)
    When the user clicks the inline Refresh button
    Then the sidebar re-fetches `GET /api/tree`
    And `dossier.md` is removed from the sidebar

  Spec refs: FR-5, FR-28, FR-34, NFR-12

---

## Feature: Flow 9 — Restore session via URL + localStorage

  As a developer who reloads the page mid-task
  I want my selection and collapse state restored
  So that the viewer feels like a stable workbench between reloads

  Background:
    Given the spec_driven app is running on port 8765
    And REPO_ROOT is `C:\workspace\spec_coding`
    And the dogfood project has Stages 1-4 artifacts on disk
    And the localStorage key `spec_driven.sidebar.v1` may carry collapse state

  Scenario: Happy path — URL drives selection; localStorage drives collapse state for unrelated subtrees
    Given the localStorage key `spec_driven.sidebar.v1` contains a JSON object recording `Projects > ai_video` as collapsed and `Projects > development > spec_driven` as expanded
    And the user is on `/projects/development/spec_driven/final_specs/spec.md`
    When the user reloads the page
    Then the URL remains `/projects/development/spec_driven/final_specs/spec.md`
    And the main pane re-renders `spec.md`
    And `Projects > development > spec_driven > final_specs` is expanded (URL ancestor chain)
    And `Projects > ai_video` is still collapsed (restored from localStorage)
    And the leaf `spec.md` has `aria-selected="true"`

  Scenario: URL takes precedence over localStorage's last-selected file
    Given the localStorage key `spec_driven.sidebar.v1` records last-selected file as `/projects/development/spec_driven/findings/dossier.md`
    When the user navigates directly to `http://localhost:8765/projects/development/spec_driven/interview/qa.md`
    Then the main pane renders `qa.md`
    And the leaf `qa.md` has `aria-selected="true"`
    And `dossier.md` is NOT auto-selected

  Scenario: Edge — localStorage corrupted falls back to default collapsed
    Given the localStorage key `spec_driven.sidebar.v1` contains the literal string `{not-valid-json`
    When the user navigates to `http://localhost:8765/`
    Then the redirect lands on `/projects/development/spec_driven/final_specs/spec.md`
    And the sidebar renders without throwing
    And only the URL ancestor chain is expanded
    And every other section of `Projects` is fully collapsed (default first-visit state)

  Scenario: Edge — localStorage missing entirely falls back to default collapsed
    Given the localStorage key `spec_driven.sidebar.v1` does not exist
    When the user navigates to `http://localhost:8765/`
    Then the sidebar renders without throwing
    And only the URL ancestor chain is expanded
    And every other section of `Projects` is fully collapsed

  Spec refs: FR-15, FR-22, FR-23

---

## Feature: Markdown rendering — Shiki + GFM

  As a developer reading mixed-language artifacts
  I want code blocks highlighted by Shiki, GFM features supported, and non-markdown files rendered with line numbers
  So that the viewer is useful for both spec prose and configuration / data files

  Background:
    Given the spec_driven app is running on port 8765
    And REPO_ROOT is `C:\workspace\spec_coding`
    And the dogfood project has Stages 1-4 artifacts on disk

  Scenario Outline: Fenced code blocks highlight by language
    Given the user is on a markdown file with a fenced code block whose info string is `<lang>`
    When the renderer processes the block
    Then the block is wrapped in Shiki output for `<expected_renderer_behavior>`

    Examples:
      | lang        | expected_renderer_behavior                                          |
      | python      | Shiki Python token classes applied                                  |
      | typescript  | Shiki TypeScript token classes applied                              |
      | xyz-unknown | plain monospace `<pre>` with no token classes (FR-31 fallback)      |

  Scenario: GFM kebab-case heading IDs and collision suffixes
    Given the markdown contains two `## Functional requirements` headings
    When the renderer generates heading IDs per FR-30
    Then the first heading gets id `functional-requirements`
    And the second heading gets id `functional-requirements-1`
    And punctuation other than hyphens is dropped during slug generation
    And ASCII-only lowercase output is produced

  Scenario Outline: Non-markdown files render with line numbers as Shiki blocks
    Given the user opens a file `<filename>` whose extension is in the supported set
    When the reader pane renders the file per FR-32
    Then the file is rendered as `<rendering_shape>`
    And every line has a visible gutter line-number

    Examples:
      | filename                       | rendering_shape                                                                |
      | pyproject.toml                 | N/A — file is OUTSIDE exposed tree, returns 404                                |
      | qa.md                          | markdown with embedded Shiki for any fenced blocks                             |
      | sample-config.yaml             | single Shiki YAML block                                                        |
      | sample-config.yml              | single Shiki YAML block                                                        |
      | sample-data.json               | single Shiki JSON block                                                        |
      | events.jsonl                   | one Shiki JSON block per line, each independently parsed                       |

  Scenario: Edge — `.jsonl` malformed line falls back to plain text
    Given the user opens a `.jsonl` file with three lines
    And line 1 is `{"ok":true}`
    And line 2 is `not valid json {`
    And line 3 is `{"ok":true,"id":2}`
    When the reader pane renders the file
    Then line 1 is a Shiki-highlighted JSON block
    And line 2 is rendered as plain text (no Shiki, no error UI)
    And line 3 is a Shiki-highlighted JSON block

  Scenario Outline: Image rendering (FR-36)
    Given the user is on a markdown file containing the image markup `<markup>`
    When the renderer processes the image
    Then the rendered output is `<rendered>`

    Examples:
      | markup                                       | rendered                                                                                                       |
      | ![diagram](./diagram.png)                    | `<span class="image-placeholder" title="v1: images not rendered">diagram</span>`                               |
      | ![hero](https://example.com/hero.jpg)        | `<img src="https://example.com/hero.jpg">` rendered straight, no proxy, no placeholder                         |
      | ![logo](../findings/logo.svg)                | `<span class="image-placeholder" title="v1: images not rendered">logo</span>`                                  |

  Spec refs: FR-30, FR-31, FR-32, FR-36

---

## Feature: Sidebar tree shape and ordering

  As a developer scanning the sidebar
  I want a stable, predictable two-section tree with deterministic ordering
  So that I can find any artifact without searching

  Background:
    Given the spec_driven app is running on port 8765
    And REPO_ROOT is `C:\workspace\spec_coding`
    And the dogfood project has Stages 1-4 artifacts on disk

  Scenario: Top-level section order
    When the frontend fetches `GET /api/tree`
    Then the response document has exactly two top-level sections in this order
      | order | section   |
      | 1     | settings  |
      | 2     | projects  |
    And the `settings` section has exactly three subgroups in this order: `claude_md`, `agents`, `skills`
    And `projects` lists `task_type` directories alphabetically (e.g., `ai_video` before `development`)
    And under each `task_type`, projects are sorted alphabetically by `task_name`
    And each project lists exactly five stage entries in this fixed order: `user_input`, `interview`, `findings`, `final_specs`, `validation`

  Scenario: Stage files alphabetical except validation/ priority order
    Given `specs/development/spec_driven/validation/` contains `acceptance_criteria.md`, `bdd_scenarios.md`, `extra_notes.md`, `strategy.md`
    When the tree response is rendered
    Then the file order under `validation/` is exactly:
      | order | filename                  |
      | 1     | strategy.md               |
      | 2     | acceptance_criteria.md    |
      | 3     | bdd_scenarios.md          |
      | 4     | extra_notes.md            |
    And under every other stage subfolder, files are alphabetical by filename

  Scenario: Missing stage subfolder still renders as muted-italic leaf
    Given `specs/development/spec_driven/validation/` does NOT exist on disk
    When the frontend fetches `GET /api/tree`
    Then the project entry for `spec_driven` still includes a `validation` stage entry with `present: false`
    And the file list for that stage is empty
    And the sidebar renders the `validation` row as muted-italic
    And the `validation` row has `title="not yet generated"`
    And the `validation` row is not expandable
    And keyboard arrow navigation skips that row

  Scenario: Per-project tree ignores extra directories outside the five stages
    Given `specs/development/spec_driven/scratch/` exists on disk
    When the frontend fetches `GET /api/tree`
    Then the response for `spec_driven` lists exactly the five stage entries
    And `scratch` is NOT present in the response

  Spec refs: FR-7, FR-8, FR-9, FR-10, FR-24

---

## Feature: Dogfood self-render

  As the inaugural user of spec_driven
  I want to open the running app and read the very spec that describes the app
  So that I confirm the deliverable is its own first happy-path consumer

  Background:
    Given the spec_driven app is running on port 8765
    And REPO_ROOT is `C:\workspace\spec_coding`
    And the dogfood project at `specs/development/spec_driven/` has Stages 1-4 artifacts on disk
    And `specs/development/spec_driven/final_specs/spec.md` exists
    And `specs/development/spec_driven/findings/dossier.md` exists
    And `specs/development/spec_driven/validation/strategy.md` exists
    And `final_specs/spec.md` contains a relative link to `../findings/dossier.md`
    And `findings/dossier.md` contains a relative link to `../validation/strategy.md`

  Scenario: Self-render walk — spec → dossier → strategy via cross-links
    Given the user opens a fresh tab
    When the user navigates to `http://localhost:8765/`
    Then the URL becomes `/projects/development/spec_driven/final_specs/spec.md` after the redirect
    And the main pane renders the contents of the spec describing this very app
    And the breadcrumb reads `development / spec_driven / final_specs / spec.md`

    When the user clicks the in-spec link `../findings/dossier.md`
    Then the URL becomes `/projects/development/spec_driven/findings/dossier.md`
    And the main pane renders `dossier.md`
    And the sidebar `aria-selected` moves to the `dossier.md` leaf

    When the user clicks the in-dossier link `../validation/strategy.md`
    Then the URL becomes `/projects/development/spec_driven/validation/strategy.md`
    And the main pane renders `strategy.md`
    And the sidebar `aria-selected` moves to the `strategy.md` leaf
    And `strategy.md` is the first file under `validation/` per FR-8 priority order

  Scenario: Back-button walks the dogfood path in reverse
    Given the user has just navigated spec → dossier → strategy
    When the user presses the browser back-button
    Then the URL returns to `/projects/development/spec_driven/findings/dossier.md`
    When the user presses the browser back-button again
    Then the URL returns to `/projects/development/spec_driven/final_specs/spec.md`
    And each step re-renders the appropriate file in the main pane

  Spec refs: FR-15, FR-17, FR-22, FR-33, FR-38, NFR-3

---

End of bdd_scenarios.md.
