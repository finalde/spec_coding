# BDD scenarios — ai_video_management

Run: ai_video_management-20260505-002710
Stage: 5 (validation strategy) — level 02 (bdd_scenarios)
Inputs consumed: `final_specs/spec.md`, `agent_refs/validation/general.md`, `agent_refs/validation/development.md`

Scenarios are grouped by **load-bearing FEATURE** (not by FR or work unit). Every scenario is tagged `[automated]` (Vitest / pytest / Playwright) or `[manual_walkthrough_only]`. Each scenario cites the FRs whose contract it pins. Severity routing for each feature appears at the end of the document.

Conventions:
- "Given the backend is bound to 127.0.0.1:8766" = `make run-prod` mode unless otherwise stated.
- "Given the dev workflow" = `make run-backend` (8766) + `make run-frontend` (Vite at 5174) per FR-6.
- "the user" = the sole human creator; same actor across all primary flows.
- All file content stays in Chinese; app chrome is English (NFR-6, FR-43).

---

## Feature 1 — Tree walk + sub_type detection

**FRs covered:** FR-18, FR-19, FR-20, FR-21, FR-22, FR-23, FR-24, FR-44.

Anchored in: backend `tree_walker.py` + `sub_type_lookup.py`; frontend `Sidebar.tsx` consumes the result.

### Scenario 1.1 — `/api/tree` returns three sections in fixed order [automated]

```gherkin
Given the backend is bound to 127.0.0.1:8766
And ai_videos/ contains projects "wukong_juexing" and "test_short"
And specs/ai_video/ contains the matching workflow folders
When the client GETs /api/tree
Then the response body is a TreeNode[]
And the top-level node names are exactly ["AI Videos", "Specs", "Context"] in that order
And every dir node sorts: dirs first, then files, both alphabetical (FR-20)
```

Citation: FR-18, FR-20. Pytest fixture mirrors the on-disk layout; assert exact ordering, not "contains".

### Scenario 1.2 — TreeNode shape includes the new `image` leaf type and `project_meta` [automated]

```gherkin
Given ai_videos/wukong_juexing/characters/ref_images/main_seedream.png exists
When the client walks the tree
Then the leaf at that path has type == "image"
And the node at ai_videos/wukong_juexing/ has project_meta with sub_type ∈ {"novel", "short", null}
And no node outside ai_videos/{name}/ carries project_meta
```

Citation: FR-19. Walks ALL `ai_videos/{name}/` dir nodes; assert `project_meta` absent everywhere else (no leakage to `specs/` nodes or sub-folders).

### Scenario 1.3 — sub_type detection: settled-facts row variants [automated]

Data table:

| qa.md row contents | Expected `sub_type` | Notes |
|---|---|---|
| `\| sub_type \| novel \|`                              | `"novel"` | bare value |
| `\| \`sub_type\` \| \`novel\` \|`                     | `"novel"` | backticked key + value |
| `\|  sub_type  \|  short  \|`                         | `"short"` | extra whitespace |
| `\| sub_type \| Short \|`                             | `null`    | case mismatch — strict regex |
| `\| sub_type \| series \|`                            | `null`    | not in enum |
| `\| sub_type \| novel \|` AND `\| sub_type \| short \|` | `null`    | multiple rows = ambiguous (FR-23) |
| qa.md missing                                          | `null`    | per FR-23 |
| qa.md present, no sub_type row                         | `null`    | per FR-23 |

```gherkin
Given specs/ai_video/{name}/interview/qa.md contains <row contents>
When sub_type_lookup.lookup("{name}") is called
Then it returns <expected sub_type>
And no exception is raised even on the ambiguous / missing cases
```

Citation: FR-22, FR-23. Pytest parametrized over the table.

### Scenario 1.4 — Single source of truth: badge and scope-toggle agree [automated]

```gherkin
Given ai_videos/wukong_juexing has sub_type=="novel" per qa.md
When the user opens the SPA
Then the sidebar badge for wukong_juexing shows "剧" (FR-44)
And opening RegeneratePanel for stage="execution" of wukong_juexing reveals the scope selector (FR-73)
When the user edits qa.md to delete the sub_type row and saves
And the tree auto-bumps after PUT
Then the next /api/tree call returns project_meta.sub_type == null for that project
And the sidebar badge disappears
And the scope selector hides (forced to "project")
```

Citation: FR-22, FR-24, FR-44, FR-73. Asserts the `sub_type_lookup` result is consumed by BOTH consumers — protects against backend/frontend field-drift (per `development.md` rule 3).

### Scenario 1.5 — Refresh semantics: manual + auto-bump only [automated]

```gherkin
Given the SPA is open with the tree fetched at T0
When an external editor modifies ai_videos/wukong_juexing/world.md at T0+5s
Then the SPA does NOT automatically refresh (no fs-watcher per FR-21)
When the user clicks the sidebar Refresh button
Then /api/tree is re-fetched and the new mtime is reflected
When the user PUTs an edit to any file via /api/file
Then the tree auto-bumps without a manual click
```

Citation: FR-21. Use Playwright with file mutations done via the test harness.

---

## Feature 2 — Shot-pair contract

**FRs covered:** FR-50, FR-51, FR-52, FR-53, FR-54.

Anchored in: `shotPairing.ts` regex + `ShotPairView.tsx`.

### Scenario 2.1 — Regex correctly identifies shot-pair files [automated, Vitest]

Data table:

| Input path | partner | dispatch view |
|---|---|---|
| `ai_videos/wukong_juexing/episodes/ep01/prompts/shot01_kling.md`    | `.../shot01_seedance.md`  | `shot-pair` |
| `ai_videos/wukong_juexing/episodes/ep01/prompts/shot01_seedance.md` | `.../shot01_kling.md`     | `shot-pair` |
| `ai_videos/test_short/prompts/shot12_kling.md`                       | `.../shot12_seedance.md` | `shot-pair` |
| `ai_videos/wukong_juexing/episodes/ep01/prompts/shot01_kling.png`    | (no match)               | image-ref / fallback |
| `ai_videos/wukong_juexing/episodes/ep01/prompts/shot1_kling.md`      | `.../shot1_seedance.md`  | `shot-pair` (single digit allowed) |
| `ai_videos/wukong_juexing/episodes/ep01/prompts/shot001_kling.md`    | `.../shot001_seedance.md`| `shot-pair` (zero-padding tolerated) |
| `ai_videos/wukong_juexing/episodes/ep01/notes/shot01_kling.md`       | (no match)               | markdown (path lacks `/prompts/`) |

```gherkin
Given <input path>
When shotPairing.parse(path) is called
Then it returns {partner: <partner>, view: <dispatch view>} OR null when no match
```

Citation: FR-51. Parametrized Vitest. Note the regex anchors on `/prompts/` segment so `notes/` is not pulled in.

### Scenario 2.2 — Both partners present: side-by-side render with copy buttons [automated, Playwright]

```gherkin
Given the user opens ?file=ai_videos/wukong_juexing/episodes/ep01/prompts/shot01_kling.md
Then ShotPairView mounts with two react-resizable-panels (autoSaveId="shot-pair-split")
And the left pane renders shot01_kling.md content via MarkdownView
And the right pane renders shot01_seedance.md content via MarkdownView
And each pane has a "复制 Kling prompt" / "复制 Seedance prompt" button
When the user clicks "复制 Kling prompt"
Then navigator.clipboard.writeText is called with the Kling content (verbatim)
And the app-root aria-live region announces "已复制"
```

Citation: FR-50, FR-53, FR-54.

### Scenario 2.3 — Partner-missing fallback [automated, Playwright]

```gherkin
Given ai_videos/test/prompts/shot07_kling.md exists
And ai_videos/test/prompts/shot07_seedance.md does NOT exist
When the user opens ?file=ai_videos/test/prompts/shot07_kling.md
Then ShotPairView renders the kling pane on the left
And a yellow banner reads "缺少配对文件: ai_videos/test/prompts/shot07_seedance.md"
And the banner contains a link to the partner path that opens BrokenLink view
And no console error is logged
```

Citation: FR-52.

### Scenario 2.4 — Markdown content in each pane uses the same MarkdownView [automated, Vitest]

```gherkin
Given a kling prompt file containing a 【...锁定描述符 v3】 block
When ShotPairView renders that pane
Then the locked-block pill (FR-65) appears on that block
And the same rehype-sanitize schema applies (raw HTML stripped)
And CJK font stack applies (lang="zh-Hans")
```

Citation: FR-54 (cross-link to FR-16, FR-65, FR-67-69). Asserts pane content goes through the **same** `MarkdownView`, not a forked renderer.

### Scenario 2.5 — Resizable split persists via autoSaveId [manual_walkthrough_only]

```gherkin
Given the user has dragged the ShotPairView splitter to ~30/70
When the user navigates to a different shot pair
Then the splitter retains the 30/70 ratio (react-resizable-panels autoSaveId="shot-pair-split")
When the user reloads the page
Then the splitter is still at 30/70
```

Citation: FR-50. Manual because keyboard-only resize and visual perception drive the validation; Playwright drag is fragile and would not catch the visual outcome.

---

## Feature 3 — Shotlist table navigation

**FRs covered:** FR-55, FR-56, FR-57, FR-58.

Anchored in: `ShotlistTableView.tsx` + the `td` override + `shotlistParser.ts`.

### Scenario 3.1 — Shotlist `td` override only fires for column 1 with shot-id text [automated, Vitest]

Data table:

| Cell column | Cell text | Override fires? |
|---|---|---|
| 1 | `shot01`            | yes |
| 1 | `shot42`            | yes |
| 1 | `shot01 备注`       | no  (regex anchors `^shot\d+$`) |
| 1 | `Shot01`            | no  (case-sensitive) |
| 1 | `镜头 01`           | no  |
| 2 | `shot01`            | no  (column != 1) |

```gherkin
Given a shotlist <tr> with columns [<column 1 text>, "其他", "..."]
When ShotlistTableView's td override sees <column 1 text>
Then it <fires|does not fire> the button replacement
```

Citation: FR-56, FR-58.

### Scenario 3.2 — Click on shot-id button programmatically navigates [automated, Playwright]

```gherkin
Given the user opens ?file=ai_videos/wukong_juexing/episodes/ep01/shotlist.md
Then ShotlistTableView mounts and renders the table
And column-1 cells with text matching ^shot\d+$ are <button> elements
When the user clicks shot03's button
Then the URL becomes ?file=ai_videos/wukong_juexing/episodes/ep01/prompts/shot03_kling.md&view=shot-pair
And ShotPairView mounts for shot03
And the click does NOT trigger a full page reload (programmatic navigate, not <a href>)
```

Citation: FR-56.

### Scenario 3.3 — Other table cells render plain markdown [automated, Vitest]

```gherkin
Given a shotlist row [shot05, "白天", "中景"]
When the table renders
Then column 2 ("白天") and column 3 ("中景") render as plain <td>text
And no button is wrapped around them
And inline emphasis / links / code in those cells render via standard react-markdown
```

Citation: FR-57.

### Scenario 3.4 — Non-table content in shotlist.md renders standard [automated, Vitest]

```gherkin
Given shotlist.md contains an H1 "# 第一集分镜表" before the table
And a paragraph "本集共 12 个镜头" after the table
When ShotlistTableView renders
Then the H1 and paragraph appear as standard markdown above/below the table
And the locked-block pill regex still applies if present (FR-65)
```

Citation: FR-55, FR-57.

### Scenario 3.5 — Column-1 invariant: shot id MUST be in column 1 [manual_walkthrough_only]

```gherkin
Given a shotlist.md (e.g., from a hypothetical author who put shot id in column 2)
Then no button appears (column 1 is the only place the override fires)
And the user MUST notice the missing buttons during their stage-6 review
```

Citation: FR-58. Manual because v1 of this webapp ASSUMES the convention; the formal enforcement lives in stage-6 ai_video pipeline validators (per FR-58 last sentence). Surfaced here so the user is reminded during sign-off.

---

## Feature 4 — Image-ref preview

**FRs covered:** FR-25, FR-26, FR-59, FR-60, FR-61, FR-62, FR-63, FR-64, FR-77.

Anchored in: `ImageRefView.tsx` + `/api/file` image route.

### Scenario 4.1 — Image-ref view dispatch on `_seedream.md` and on `.png|.jpg` paths [automated, Vitest]

Data table:

| Input path | Dispatch view |
|---|---|
| `.../characters/ref_images/main_seedream.md`     | `image-ref` |
| `.../characters/ref_images/wangba_seedream.md`   | `image-ref` |
| `.../characters/ref_images/main_seedream.png`    | `image-ref` |
| `.../characters/ref_images/main.jpg`             | `image-ref` |
| `.../characters/ref_images/main_notes.md`        | `markdown`  (suffix not `_seedream.md`) |
| `.../shotlist.md`                                | `shotlist-table` (precedence — different feature) |

Citation: FR-48 (path-based default), FR-59.

### Scenario 4.2 — Companion `.png` discovered when present [automated, Playwright]

```gherkin
Given ai_videos/wukong_juexing/characters/ref_images/main_seedream.md exists
And ai_videos/wukong_juexing/characters/ref_images/main_seedream.png exists in the SAME folder
When the user opens ?file=.../main_seedream.md
Then ImageRefView mounts with two panels (autoSaveId="image-ref-split")
And the left pane renders the markdown prompt
And the right pane renders <img src="/api/file?path=...main_seedream.png&mtime=<float>" alt="main_seedream立绘" />
And the URL's mtime query parameter equals the tree node's mtime (cache-buster)
```

Citation: FR-60, FR-61, FR-63.

### Scenario 4.3 — Fallback message when `.png` is absent [automated, Playwright]

```gherkin
Given main_seedream.md exists
And no main_seedream.png exists in the same folder
When the user opens ?file=.../main_seedream.md
Then ImageRefView's right pane renders the placeholder text:
  "尚未生成立绘 — 复制左侧 prompt 至 Seedream 后保存为 main_seedream.png 并刷新"
And NO "Refresh" button appears (sidebar refresh + reclick is the documented flow)
And no <img> tag is in the right pane
And the discovery prefers .png over .jpg if both exist (re-run with .jpg present + .png present asserts .png wins)
```

Citation: FR-62, FR-63.

### Scenario 4.4 — Image-readonly: PUT rejects image extensions [automated, pytest]

```gherkin
Given a valid Origin and fresh If-Unmodified-Since
When the client PUTs /api/file with path=".../main_seedream.png", content="..."
Then the response status is 400
And the error body identifies extension allowlist violation (image extensions excluded from writeable list)
```

Citation: FR-13, FR-28.

### Scenario 4.5 — Editor button hidden when current view is image-ref + target is image [automated, Playwright]

```gherkin
Given ?file=.../main_seedream.png&view=image-ref is open
Then the Editor button is NOT visible in the toolbar
Given ?file=.../main_seedream.md&view=image-ref is open (same view, but target is .md)
Then the Editor button IS visible (image-ref + .md = prompt is editable)
```

Citation: FR-64, FR-77. Two-case scenario protects against accidentally hiding the editor for the prompt half.

### Scenario 4.6 — Image route Cache-Control + URL cache-busting [automated, pytest]

```gherkin
Given /api/file?path=.../main_seedream.png&mtime=1714875600.123 is GETted
Then the response Content-Type is image/png
And Cache-Control is "private, max-age=0, must-revalidate"
And Last-Modified is an RFC 1123 date matching the file mtime
And the response body is the raw .png bytes
When the file is regenerated externally and the tree mtime updates to 1714875700.456
And the URL re-issued with the new mtime
Then the browser fetches fresh (URL-uniqueness skips its cache)
```

Citation: FR-25, FR-26.

---

## Feature 5 — Locked-block pill

**FRs covered:** FR-65, FR-66.

Anchored in: `MarkdownView.tsx` pre-processing regex + `app.css` pill styles.

### Scenario 5.1 — Regex matches the canonical locked-descriptor block [automated, Vitest]

Data table for `/【.+? · .+? · 锁定描述符 v\d+】[\s\S]*?禁用 .*?。/g`:

| Source markdown snippet | Matches? |
|---|---|
| `【主角 · 男性 · 锁定描述符 v1】描述... 禁用 任何风格变化。`         | yes (v1) |
| `【王霸 · 男性 · 锁定描述符 v3】\n多行\n描述... 禁用 替换。`         | yes (multiline body via [\s\S]*?) |
| `【主角 · 男性 · 锁定描述符 v12】... 禁用 改色。`                  | yes (multi-digit version) |
| `【主角 · 男性 · 锁定描述符】... 禁用 ...。`                       | no  (missing `vN`) |
| `【主角 · 男性 · locked descriptor v1】... 禁用 ...。`             | no  (English literal not matched) |
| `【主角 · 男性 · 锁定描述符 v1】... 禁用 ...`                      | no  (missing terminating `。`) |

Citation: FR-65. Vitest parametrized.

### Scenario 5.2 — Wrapped span carries `data-version` and renders pill via CSS [automated, Vitest + jsdom]

```gherkin
Given a markdown source with 【主角 · 男性 · 锁定描述符 v3】... 禁用 ...。
When MarkdownView renders
Then the rendered DOM contains <span class="locked-block" data-version="v3">...</span>
And the computed style on .locked-block::before draws the "锁定块" pill
And the pill's cursor is "help"
And tabbing focus reaches the pill's tooltip trigger (a11y check via Playwright)
```

Citation: FR-65, FR-66.

### Scenario 5.3 — Multiple locked blocks in one file each get a pill [automated, Vitest]

```gherkin
Given a single markdown file containing 3 locked-block matches
When MarkdownView renders
Then exactly 3 <span class="locked-block"> elements exist
And each carries its own data-version attribute (v1, v2, v3 say)
```

Citation: FR-65 (the regex is `/g` flagged).

### Scenario 5.4 — Light-theme pill contrast (a11y) [manual_walkthrough_only]

```gherkin
Given the SPA loaded with `:root { color-scheme: light; }`
And a file containing a locked-block
When the user views it
Then the pill background (#f3f4f6) on top of the page background passes WCAG AA contrast for the pill text
And in OS dark mode, the pill chrome stays light (no @media prefers-color-scheme override per FR-79)
```

Citation: FR-66, FR-79, FR-80. Manual because real-monitor color rendering is the validation gate.

---

## Feature 6 — Regen-prompt scope axis

**FRs covered:** FR-34, FR-35, FR-36, FR-37, FR-38, FR-39, FR-72, FR-73.

Anchored in: backend `regen_prompt.py` + frontend `RegeneratePanel.tsx`.

### Scenario 6.1 — Scope selector visibility gated on stage and sub_type [automated, Playwright]

Data table:

| stage selected | project sub_type | Scope selector visible? | Forced scope value |
|---|---|---|---|
| `intake`              | novel | no | `project` |
| `interview`           | novel | no | `project` |
| `research`            | novel | no | `project` |
| `spec`                | novel | no | `project` |
| `validation_strategy` | novel | no | `project` |
| `execution`           | novel | yes | (user choice) |
| `execution`           | short | no | `project` (forced) |
| `execution`           | null  | no | `project` (forced; same as short) |

```gherkin
Given the user opens RegeneratePanel for project <name> with sub_type <sub_type>
When the user picks stage = <stage>
Then the scope selector is <visible|hidden>
And when hidden, the request body's scope field is "project"
```

Citation: FR-73.

### Scenario 6.2 — `episode N` and `episodes M..N` request bodies + responses [automated, pytest]

Data table:

| scope | scope_episode | scope_episode_range | Request valid? | Response.scope_resolved |
|---|---|---|---|---|
| `episode`  | 5              | null              | yes (novel)        | `episode 5` |
| `episode`  | 0              | null              | 400 (must be ≥1)   | — |
| `episode`  | null           | null              | 400 (required)     | — |
| `episodes` | null           | {start: 5, end: 7}| yes (novel)        | `episodes 5,6,7` (explicit list, no shorthand) |
| `episodes` | null           | {start: 7, end: 5}| 400 (start ≤ end)  | — |
| `episodes` | null           | null              | 400 (required)     | — |
| `episode`  | 5              | null              | 400 (sub_type=short)| — (FR-36) |
| `episode`  | 5              | null              | 409 (sub_type=null / qa.md missing)| — (FR-36) |

```gherkin
Given the project's sub_type is <sub_type>
When the client POSTs /api/regen-prompt with scope=<scope>, scope_episode=<n>, scope_episode_range=<range>
Then the response status is <status>
And on success, response.scope_resolved equals <expected>
And on success, the prompt body contains the explicit episode folder list (e.g., "ep05, ep06, ep07") with NO `M..N` shorthand
```

Citation: FR-34, FR-36, FR-38.

### Scenario 6.3 — Stages 1–5 prompt body byte-identical to spec_driven [automated, pytest]

```gherkin
Given a fixture project at specs/ai_video/test_byte_identity/ with revised_prompt.md, follow_ups/*, and <stage>/promoted.md populated
And the corresponding spec_driven fixture at specs/development/test_byte_identity_dev/ with the SAME logical content
When /api/regen-prompt is called for ai_video stage <stage> ∈ {intake, interview, research, spec, validation_strategy}
And spec_driven's /api/regen-prompt is called for the same stage with project_type=development
Then the two prompt bodies differ ONLY in:
  (a) the project_type literal ("ai_video" vs "development")
  (b) the optional `sub_type:` line (present in ai_video, absent in development)
And the _READ_ZERO_CONTRACT and _AUTONOMOUS_IMPERATIVE constants appear byte-identically in both outputs
```

Citation: FR-37. This guards against drift between the two backends' read-zero contract text.

### Scenario 6.4 — Stage-6 regen-prompt body variants [automated, pytest]

Data table (4 variants per FR-38):

| (sub_type, scope) | Delete contract | Preserves |
|---|---|---|
| `short × project`        | `ai_videos/{name}/` whole tree | none beyond outside the folder |
| `novel × project`        | `ai_videos/{name}/` whole tree | none beyond outside the folder |
| `novel × episode 5`      | `ai_videos/{name}/episodes/ep05/` ONLY | `characters/`, `world.md`, `style_guide.md`, `arc_outline.md`, sibling `episodes/epNN/` for NN≠5 |
| `novel × episodes 5..7`  | `ai_videos/{name}/episodes/{ep05,ep06,ep07}/` (explicit list) | same as above except for episodes 5,6,7 |

```gherkin
Given project <name> has sub_type=<sub_type>
When /api/regen-prompt is called for stage="execution" with scope=<scope>
Then the prompt body declares the delete-targets above
And the prompt body declares the forbid-edit set above (preserved paths)
And the prompt body inlines: revised_prompt.md, every follow_ups/*.md, the read-zero contract, audit-event tags (regen.delete.planned/completed, regen.write.completed), and the execution-mode header
```

Citation: FR-38, FR-39.

### Scenario 6.5 — Mode toggle persists in the namespaced localStorage key [automated, Playwright]

```gherkin
Given the user opens RegeneratePanel
And toggles mode to AUTONOMOUS
Then localStorage["ai_video_management.autonomous_mode.v1"] == "true"
And localStorage["spec_driven.autonomous_mode.v1"] is unaffected (untouched by this webapp)
When the user reloads the page
Then the mode is still AUTONOMOUS
And the assembled prompt's first line is "# EXECUTION MODE: AUTONOMOUS"
When the toggle returns to INTERACTIVE
Then localStorage["ai_video_management.autonomous_mode.v1"] == "false"
And the assembled prompt's first line is "# EXECUTION MODE: INTERACTIVE"
```

Citation: FR-39, FR-72. Cross-link to Feature 9 (localStorage namespacing).

### Scenario 6.6 — Body cap and soft warning [automated, pytest]

```gherkin
Given /api/regen-prompt would assemble a body of size N
When N == 1.5 MiB
Then the response is 413 (FR-36)
When N == 60 KiB
Then the response is 200
And a soft-warning log entry is emitted (50 KiB threshold)
When N == 30 KiB
Then 200 with no soft warning
```

Citation: FR-36, with cross-link to FR-14.

---

## Feature 7 — Cross-tree counterpart link

**FRs covered:** FR-78.

### Scenario 7.1 — `查看规格` link appears only on ai_videos paths [automated, Playwright]

Data table:

| Current path | "查看规格" link visible? | Link target |
|---|---|---|
| `ai_videos/wukong_juexing/world.md`            | yes | `?file=specs/ai_video/wukong_juexing/` |
| `ai_videos/wukong_juexing/episodes/ep01/shotlist.md` | yes | `?file=specs/ai_video/wukong_juexing/` (project root, not per-file mirror) |
| `specs/ai_video/wukong_juexing/interview/qa.md`| no  | — (no reverse link in v1) |
| `specs/ai_video/wukong_juexing/findings/dossier.md` | no  | — |
| `CLAUDE.md`                                    | no  | — (Context section) |
| `.claude/skills/agent_team/SKILL.md`           | no  | — |

```gherkin
Given the user opens <current path>
Then the toolbar's "查看规格" link is <visible|absent>
And when visible, clicking it loads <link target>
```

Citation: FR-78. The reverse direction is explicitly deferred (out-of-scope item: "Reverse cross-tree link (specs → ai_videos)" in spec § Open questions).

### Scenario 7.2 — Cross-tree link target is a project-root jump, not a per-file mirror [automated, Playwright]

```gherkin
Given the user is on ai_videos/wukong_juexing/episodes/ep01/prompts/shot01_kling.md
When the user clicks "查看规格"
Then the resolved URL is ?file=specs/ai_video/wukong_juexing/
And it does NOT attempt to construct a per-file mirror path like specs/ai_video/wukong_juexing/episodes/ep01/prompts/shot01_kling.md
```

Citation: FR-78. Explicit because per-file mirror is the obvious wrong implementation.

### Scenario 7.3 — Counterpart project missing → graceful surface [automated, Playwright]

```gherkin
Given ai_videos/test_orphan/ exists with no specs/ai_video/test_orphan/ counterpart
When the user views any file under ai_videos/test_orphan/
Then the "查看规格" link is still visible (the link target is computed from the path, not gated on existence)
When the user clicks it
Then the SPA navigates to ?file=specs/ai_video/test_orphan/
And the BrokenLink view (or equivalent "no such tree node" surface) renders
And no console error is logged
```

Citation: FR-78. Captures the "what happens when the workflow trail wasn't started yet" case.

---

## Feature 8 — Origin/Host gate parity with spec_driven

**FRs covered:** FR-3, FR-4, FR-11.

Anchored in: `api_security.py` middleware. Note: per `general.md` rule 7 + `development.md` rule 11, when a header-mutating Vite proxy exists in dev, BOTH pre- and post-rewrite shapes MUST be tested.

### Scenario 8.1 — Same-loopback-alias admit table [automated, pytest]

Data table for state-changing endpoints (PUT /api/file as the canonical case):

| Origin sent | Host sent | Result |
|---|---|---|
| `http://127.0.0.1:8766` | `127.0.0.1:8766` | 200 (admit) |
| `http://localhost:8766` | `localhost:8766` | 200 (admit; loopback alias) |
| `http://localhost:8766` | `127.0.0.1:8766` | 200 (admit; mismatched-but-aliased) |
| `http://127.0.0.1:8765` | `127.0.0.1:8765` | 403 (spec_driven port is FOREIGN) |
| `http://127.0.0.1:5174` | `127.0.0.1:5174` | 403 (Vite dev port unrewritten = foreign) |
| `http://example.com`     | `example.com`     | 403 |
| (no Origin header)       | `127.0.0.1:8766` | 403 |
| `http://[::1]:8766`      | `[::1]:8766`     | 403 (IPv6 explicitly rejected per FR-3) |

Citation: FR-3, FR-11.

### Scenario 8.2 — Pre-rewrite vs post-rewrite shapes both covered (header-mutating-proxy contract) [automated, pytest]

Per `development.md` rule 11, the unit tests MUST cover all three shapes:

| Shape | Setup | Expected |
|---|---|---|
| **Pre-rewrite** (browser-Origin = Vite dev origin sent direct to backend) | request with `Origin: http://127.0.0.1:5174` to `127.0.0.1:8766` | 403 (proves the rewrite is load-bearing) |
| **Post-rewrite** (Origin = backend bound origin sent direct to backend)   | request with `Origin: http://127.0.0.1:8766` to `127.0.0.1:8766` | 200 (gate accepts under the `make run-prod` shape) |
| **Real proxied** (request through Vite at 5174 → backend)                | Playwright drives the dev server and observes the rewrite                 | 200 (proxy `configure` hook actually wires up) |

```gherkin
Scenario: Each shape exercised in its own test
Given <shape setup>
When the request hits the backend
Then the response status is <expected>
```

Citation: `development.md` rule 11 + general.md principle 7. **Missing pre-rewrite shape = `blocker`.**

### Scenario 8.3 — Bind enforcement (FR-3) [automated, pytest]

```gherkin
Given the backend is started with --host 127.0.0.1 --port 8766
Then the listener is on 127.0.0.1:8766 only
When --host 0.0.0.0 is passed
Then the backend rejects the bind (or argparse rejects the choice)
When --host [::1] is passed
Then the backend rejects the bind
```

Citation: FR-3. Tests the explicit IPv4-loopback-only contract.

### Scenario 8.4 — Read endpoints also gate (parity with spec_driven posture) [automated, pytest]

```gherkin
Given the gate is configured per FR-11
When GET /api/tree is requested with Origin = http://127.0.0.1:8765
Then the result is 403
When GET /api/file?path=ai_videos/.../world.md is requested with no Origin
Then the result is 403
```

Citation: FR-11. The spec phrases the gate as applying to "every state-changing endpoint" — this scenario protects the read paths if the parity contract intends them too. (If the implementation chooses to gate reads only on origin and not require it, mark this scenario `blocker` if it fails on writes only; warning if it fails on reads.)

### Scenario 8.5 — Manual same-host concurrent verification [manual_walkthrough_only]

```gherkin
Given the user runs spec_driven on 8765 AND ai_video_management on 8766 simultaneously
When the user opens both SPAs in adjacent browser tabs
Then neither SPA's API calls leak into the other (cross-port = 403)
And both SPAs operate without console errors
```

Citation: FR-11, NFR-3. Manual because the validation is the felt experience of running both side-by-side.

---

## Feature 9 — localStorage namespacing

**FRs covered:** FR-72, NFR-3.

### Scenario 9.1 — All app-scoped keys carry the `ai_video_management.` prefix [automated, Playwright]

```gherkin
Given the SPA is loaded fresh (localStorage empty)
When the user toggles mode to AUTONOMOUS in RegeneratePanel
And drags ShotPairView splitter (autoSaveId="shot-pair-split")
And drags ImageRefView splitter (autoSaveId="image-ref-split")
Then the keys present in localStorage are EXACTLY a subset of:
  - ai_video_management.autonomous_mode.v1
  - react-resizable-panels:shot-pair-split  (library default key — see scenario 9.3)
  - react-resizable-panels:image-ref-split  (same)
And NO key starts with "spec_driven."
```

Citation: FR-72.

### Scenario 9.2 — Coexistence with spec_driven: keys do not collide [automated, Playwright]

```gherkin
Given the user has spec_driven open at 8765 in one tab
And ai_video_management open at 8766 in another tab
When the user sets spec_driven.autonomous_mode.v1 = "true" via spec_driven
And ai_video_management.autonomous_mode.v1 = "false" via this webapp
Then both keys exist independently in the same localStorage origin... 
  (note: they actually live in DIFFERENT origins because port differs — 127.0.0.1:8765 vs 127.0.0.1:8766 — so localStorage is naturally partitioned)
And neither webapp reads the other's key
```

Citation: NFR-3. Browser localStorage is partitioned per `(scheme, host, port)`, so by virtue of distinct ports the partitioning is automatic. The scenario is still load-bearing because someone could refactor to a shared origin later.

### Scenario 9.3 — Splitter persistence keys: explicit assertion [automated, Vitest + jsdom]

```gherkin
Given react-resizable-panels v4 with autoSaveId="shot-pair-split"
When a panel is resized
Then the key written to storage starts with "react-resizable-panels:" and contains "shot-pair-split"
And NO writes occur to "spec_driven.*" keys
```

Citation: FR-50, FR-60, FR-72. Documents the library's prefix so future audits know what to expect.

### Scenario 9.4 — Manual cleanup verification [manual_walkthrough_only]

```gherkin
Given the user clears localStorage in DevTools
When the SPA is reloaded
Then no JS errors occur
And RegeneratePanel defaults to INTERACTIVE
And splitters default to 50/50
```

Citation: FR-72. Manual because resilience to a missing key is best validated by visual sanity.

---

## Severity routing table

Per `agent_refs/validation/general.md` § Standard severity policy + `agent_refs/validation/development.md` § Severity escalations specific to development. Per-task-type rows win.

| Failing scenario | Severity | Rationale |
|---|---|---|
| **1.1** /api/tree top-level shape wrong (sections / order) | `blocker` | Frontend contract; consumer walk regression (`development.md` rule 2). |
| **1.2** TreeNode missing `children`, `type`, or `project_meta` field | `critical` | API shape drift between front and back (`development.md` table). |
| **1.3** sub_type regex parses a value not in {novel, short, null} | `blocker` | Spec invariant; downstream gating broken. |
| **1.4** badge and scope-toggle disagree on sub_type | `blocker` | Backend/frontend field-drift class; `development.md` rule 3. |
| **1.5** fs-watcher introduced (auto-refresh fires without manual click) | `warning` | Out-of-scope feature; surface to user. |
| **2.1** shotPairing regex misses a kling/seedance variant | `blocker` | Render-mode dispatch failure → BrokenLink for valid file. |
| **2.2** clipboard not invoked OR aria-live silent | `blocker` | a11y mandatory + golden-path BDD. |
| **2.3** partner-missing case crashes / blank page | `critical` | Latent render error on deep-link (`development.md` table). |
| **2.4** locked-block pill / sanitization not applied in pane | `blocker` | Component reuse contract (FR-54). |
| **2.5** splitter doesn't persist on reload | `warning` | Cosmetic; logged. |
| **3.1** td override fires for column ≠ 1 OR for non-shot-id text | `blocker` | False navigations; user trust break. |
| **3.2** programmatic navigate fails OR causes full reload | `blocker` | Golden-path BDD. |
| **3.3** non-shot cells get accidental buttons | `blocker` | Dispatch contract drift. |
| **3.4** non-table content in shotlist.md doesn't render | `blocker` | Markdown contract. |
| **3.5** column-1-invariant violation in user data | `warning` | Manual-only; surface for stage-6 ai_video pipeline to enforce. |
| **4.1** dispatch picks wrong view for `_seedream.md` / `.png` | `blocker` | Golden-path BDD. |
| **4.2** image preview renders broken `<img>` (404 src) | `blocker` | Visible breakage. |
| **4.3** fallback message wording / missing `expected-png-name` | `blocker` | Spec text is contractual (FR-62). |
| **4.4** PUT image returns 200 instead of 400 | `critical` | Read-only contract violated; auditable surface. |
| **4.5** Editor button shown for image / hidden for `_seedream.md` | `blocker` | UX contract; user can't edit prompts. |
| **4.6** Cache-Control header wrong → stale render after save | `blocker` | Round-trip experience broken. |
| **5.1** locked-block regex matches wrong substring | `critical` | Markdown XSS risk if a malicious crafted block bypasses sanitization (general.md principle 2). |
| **5.2** pill not rendered / data-version missing | `blocker` | Spec contract. |
| **5.3** multi-block file: only first pill renders (non-`/g` regex) | `blocker` | Common-case regression. |
| **5.4** pill contrast fails WCAG AA | `blocker` | a11y mandatory check (general.md table). |
| **6.1** scope selector visible on a non-execution stage OR for `short`/`null` sub_type | `blocker` | Gate contract; invalid request paths. |
| **6.2** episode/episodes validation missing → 400 not raised | `blocker` | Spec carve-out enforcement. |
| **6.3** stages-1–5 prompt body diverges from spec_driven beyond the documented 2 differences | `critical` | Spec carve-out conflicts with another spec section (`development.md` table) — read-zero contract drift across both webapps. |
| **6.4** stage-6 prompt body declares wrong delete-targets / wrong preserve-set | `critical` | Regen would destroy preserved artifacts; user data loss. |
| **6.5** localStorage key written under `spec_driven.*` namespace | `blocker` | NFR-3 coexistence violation. |
| **6.6** body cap not enforced (>1 MiB returns 200) | `blocker` | Resource exhaustion. |
| **7.1** "查看规格" link visible on specs/ paths OR missing on ai_videos/ paths | `blocker` | Reverse-link is explicitly out of scope; appearing is contract drift. |
| **7.2** link target uses per-file mirror path | `blocker` | Spec text explicit (FR-78). |
| **7.3** orphan-counterpart click triggers console error | `blocker` | Latent render error class. |
| **8.1** any admit/reject row in the table fails | `critical` | Path traversal / sandbox escape class (general.md). |
| **8.2** **pre-rewrite shape test missing** | `blocker` | `development.md` rule 11; missing case re-introduces `spec_driven-006` class bug. |
| **8.2** post-rewrite or proxied test missing | `blocker` | Rule 11 + general principle 7. |
| **8.3** bind accepts 0.0.0.0 or [::1] | `critical` | Spec-explicit IPv4-loopback-only (FR-3). |
| **8.4** read endpoint allows foreign Origin (if gate is intended on reads) | `warning` | Spec scopes gate to mutations only; surface for explicit confirmation. |
| **8.5** simultaneous-run UX regression (cross-port leakage) | `critical` | Coexistence contract (NFR-3). |
| **9.1** non-namespaced key written | `blocker` | NFR-3 + FR-72. |
| **9.2** spec_driven and ai_video_management share a key | `blocker` | NFR-3. |
| **9.3** library autosave key writes outside the documented prefix | `warning` | Library upgrade detection signal. |
| **9.4** missing-key reload throws | `blocker` | Resilience to fresh-install / cleared-storage state. |

### Halting policy

- Any `critical` finding → halt immediately; no revision rounds without explicit user approval (per `general.md` table).
- Any `blocker` finding → standard 3-revision-round cap (per `general.md` § Iteration bounds).
- Any `warning` finding → log to `events.jsonl` as `validation.issue.raised` with severity warning; never halts.
- Manual-walkthrough scenarios emit `validation.requires_manual_walkthrough` after all automated levels pass; the parent surfaces the list to the user before declaring stage 6 done (per `development.md` rule 7 + `general.md` principle 4).

### Cross-feature notes

- **Feature 6 ↔ Feature 9.** The mode-toggle scenario (6.5) and the namespacing scenario (9.1) overlap by design — the same persisted key is the contract surface for two features. Counted twice intentionally so each feature's checklist is self-contained.
- **Feature 4 ↔ Feature 8.** Image-route GET (4.6) and the read-endpoint gate (8.4) are independent: cache-control is the response shape; the gate is the request shape.
- **Feature 2 ↔ Feature 5.** ShotPairView panes use the same `MarkdownView` (2.4) — locked-block pill regression (Feature 5) implicitly fails Feature 2 too.

### Deferred / explicitly-not-scenarios

Per spec § Out of scope, the following are NOT covered by stage-5 BDD scenarios. The parent will surface them to the user at stage-5 sign-off per `general.md` principle 6:

- Render-API integration with Kling / Seedance / Seedream.
- Storyboard horizontal-scroll view with auto-frame thumbnails.
- File create / delete / upload through the webapp.
- Dark-mode chrome toggle.
- File-system watcher / auto-refresh.
- Cross-publish manager / English publish translation.
- Compare-two-projects diff view.
- Reverse cross-tree link (specs → ai_videos).
