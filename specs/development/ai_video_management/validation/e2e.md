# Validation Level 5 — End-to-End (Playwright)

Run: `ai_video_management-20260505-002710`
Stage: 5 (validation strategy)
Level specialist: 05 — e2e
Inputs consumed: `final_specs/spec.md` (FR-5..FR-6, FR-47..FR-78, FR-85), `agent_refs/validation/general.md`, `agent_refs/validation/development.md` (moves #1, #8, #9)

## 总览

End-to-end Playwright suite for `projects/ai_video_management/frontend/`. Drives a real browser against the real FastAPI backend at port 8766 and asserts on rendered DOM the way the user actually sees it.

**Three load-bearing rules** drive every scenario in this strategy:

1. **Multi-mode parity (development.md move #1).** The spec advertises TWO runtime modes (FR-5 `make run-prod` single-process; FR-6 `make run-backend` + `make run-frontend` Vite-proxied). `playwright.config.ts` therefore declares **2 projects**: `prod-mode` and `dev-mode`. Every render-mode scenario runs once per project. A scenario that passes in `prod-mode` but blows up in `dev-mode` is a `blocker`, not a carve-out.
2. **One scenario per render mode (development.md move #8).** Eight render dispatch paths exist in `Reader.tsx` (FR-47–48): `MarkdownView`, `ShotPairView`, `ShotlistTableView`, `ImageRefView`, `QaView`, `JsonlView`, `CodeView`, `ImagePlaceholder` (image-absent fallback). Each gets its own scenario opening a **real triggering file** under `ai_videos/wukong_juexing/` or `specs/ai_video/wukong_juexing/`. No synthetic fixtures.
3. **What the user actually sees (development.md move #8).** Every scenario asserts:
   - `await expect(page.locator('main')).not.toBeEmpty()` — rendered output exists.
   - A render-mode-specific selector resolves (e.g., for ShotPairView: `[data-testid="shot-pair-left"]` AND `[data-testid="shot-pair-right"]`).
   - `consoleErrors.length === 0` — no `console.error` swallowed by deferred render. Caught via `page.on('console', ...)` listener registered before navigation.

A failed-to-render mode that prints "Loading..." forever and a 4xx asset reference both fail rule 3. This is the exact class of bug move #8 was created to catch (autonomous-mode QaView blank page, run `spec_driven-20260502-clean`).

**Severity policy** (per development.md):
- Missing e2e for any non-default render mode → `blocker`.
- Latent render error on deep-link (blank `main` after navigation) → `critical`.
- Runtime mode advertised in spec without an exercising profile → `blocker`.
- Console error during render → `blocker` (per move #9: error-boundary coverage).

## `playwright.config.ts` skeleton

Paste-ready TypeScript. Lives at `projects/ai_video_management/frontend/playwright.config.ts`.

```typescript
import { defineConfig, devices } from "@playwright/test";

const REPO_ROOT = "../../..";  // frontend/ → project/ → projects/ → repo root

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: false,            // serialize: each project boots its own backend
  retries: 0,                       // surface flake; do not paper over
  reporter: [["list"], ["html", { open: "never", outputFolder: "playwright-report" }]],

  projects: [
    {
      // FR-5: single-process production mode.
      // make run-prod builds the Vite bundle into backend/static/ and serves SPA + API
      // from one FastAPI process bound at 127.0.0.1:8766.
      name: "prod-mode",
      use: {
        ...devices["Desktop Chrome"],
        baseURL: "http://127.0.0.1:8766",
      },
    },
    {
      // FR-6: dev mode. Backend on 127.0.0.1:8766, Vite dev server on 127.0.0.1:5174,
      // Vite proxy forwards /api/* to backend with Origin rewrite (per spec_driven 006).
      // Browser hits the Vite port; the proxy is part of the test surface.
      name: "dev-mode",
      use: {
        ...devices["Desktop Chrome"],
        baseURL: "http://127.0.0.1:5174",
      },
    },
  ],

  // Two webServer entries — one per advertised mode. Playwright boots ALL listed
  // webServers; each project's baseURL selects which one its tests target.
  webServer: [
    {
      // prod-mode: single-process. Build then run.
      command: `cd ${REPO_ROOT} && make run-prod`,
      url: "http://127.0.0.1:8766/",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      stdout: "pipe",
      stderr: "pipe",
    },
    {
      // dev-mode: backend (8766) + Vite (5174). Single make target boots both.
      command: `cd ${REPO_ROOT} && make run-frontend`,
      url: "http://127.0.0.1:5174/",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      stdout: "pipe",
      stderr: "pipe",
    },
  ],
});
```

**Notes on the skeleton:**

- `fullyParallel: false` because both modes share the backend port (8766). Running them concurrently would race for the bind. If U7 implementers want concurrency, they MUST split prod-mode and dev-mode backends onto separate ports, which is a spec change (re-prompt user).
- `make run-frontend` is assumed (per FR-81) to chain backend startup. If it doesn't, the U7 implementer adds `make run-backend & make run-frontend` orchestration; the test surface is unchanged.
- The `dev-mode` project's `baseURL` points at the Vite port (5174). This is load-bearing — it exercises the proxy `configure` hook (development.md move #11 / FR-6). If a future implementer "simplifies" both projects to point at 8766, the proxy regression bug from `spec_driven-006` re-introduces silently. → `blocker` finding at code review.
- `consoleErrors` listener pattern (used by every spec) — codified in `e2e/_helpers.ts`:

  ```typescript
  import type { Page, ConsoleMessage } from "@playwright/test";

  export function trackConsoleErrors(page: Page): string[] {
    const errors: string[] = [];
    page.on("console", (msg: ConsoleMessage) => {
      if (msg.type() === "error") errors.push(msg.text());
    });
    page.on("pageerror", (err: Error) => errors.push(err.message));
    return errors;
  }
  ```

  Every spec calls `const errors = trackConsoleErrors(page)` BEFORE the first `goto`, then asserts `expect(errors).toEqual([])` after the render assertion. `pageerror` is included to catch React reconciliation throws that `console.error` does NOT receive (development.md move #9 — the exact class of bug `try { return <Foo /> } catch` does not catch).

## 测试文件清单

All files under `projects/ai_video_management/frontend/e2e/`. Each scenario name is the `test(...)` title; both projects (`prod-mode`, `dev-mode`) run every spec — Playwright's project matrix doubles the row count automatically.

| 文件 | Mode profile | Render mode | 触发文件路径 | 场景名 |
|---|---|---|---|---|
| `markdown.spec.ts` | both | `MarkdownView` | `ai_videos/wukong_juexing/style_guide.md` | renders generic markdown with sanitization |
| `markdown.spec.ts` | both | `MarkdownView` (locked-block pill) | `ai_videos/wukong_juexing/characters/main.md` | renders 锁定描述符 v1 block with pill |
| `shot_pair.spec.ts` | both | `ShotPairView` | `ai_videos/wukong_juexing/prompts/shot01_kling.md` | side-by-side panes, both partners present |
| `shot_pair.spec.ts` | both | `ShotPairView` (partner-missing) | `ai_videos/wukong_juexing/prompts/shot01_kling.md` (synthetic missing partner — see scenario notes) | yellow banner when partner absent |
| `shotlist_table.spec.ts` | both | `ShotlistTableView` | `ai_videos/wukong_juexing/shotlist.md` | row-click navigates to ShotPairView |
| `image_ref.spec.ts` | both | `ImageRefView` (image-present) | `ai_videos/wukong_juexing/characters/ref_images/main_seedream.md` (with companion `main_seedream.png` present) | both panes resolve, `<img>` 200 |
| `image_ref.spec.ts` | both | `ImagePlaceholder` (image-absent) | `ai_videos/wukong_juexing/characters/ref_images/main_seedream.md` (companion `.png` removed/never created) | placeholder text replaces `<img>` |
| `qa_view.spec.ts` | both | `QaView` | `specs/ai_video/wukong_juexing/interview/qa.md` | Q/A pairs render, no console errors, error boundary not triggered |
| `jsonl_view.spec.ts` | both | `JsonlView` | `.audit/adhoc_agents/2026-05-05/ai_video_management-20260505-002710/events.jsonl` | each line as a card, no truncation |
| `code_view.spec.ts` | both | `CodeView` | `ai_videos/wukong_juexing/publish.md` (rendered in code-view override) OR a `.json` file; see scenario | syntax-highlighted `<pre>` |
| `regen_panel.spec.ts` | both | (panel chrome — not a render mode) | `specs/ai_video/wukong_juexing/final_specs/spec.md` (any spec to surface the panel) | scope-toggle gating: novel surfaces episode/episodes options; short hides them; `sub_type=None` hides them |
| `cross_tree.spec.ts` | both | (toolbar chrome — not a render mode) | `ai_videos/wukong_juexing/script.md` | "查看规格" link present and navigates to `specs/ai_video/wukong_juexing/` |
| `security.spec.ts` | both | (Origin gate — backend behavior) | `POST /api/promote` from `http://127.0.0.1:8765` Origin | 403 rejection at 8765 (FR-11, FR-85e) |
| `primary_flows.spec.ts` | both | (golden path) | walks all 8 primary flows from spec § Primary flows | each flow reaches its asserted-DOM checkpoint |

**Total spec files:** 11. **Total render-mode scenarios:** 8 (MarkdownView, ShotPairView, ShotlistTableView, ImageRefView, QaView, JsonlView, CodeView, ImagePlaceholder). **Total scenarios across all files:** 14. **Total runs (× 2 projects):** 28.

**Synthetic missing-partner note (shot_pair.spec.ts):** The "partner-missing" scenario uses a `test.beforeEach` that copies `shot01_kling.md` to a temp location named `shot99_kling.md` (where `shot99_seedance.md` does NOT exist) under a folder ALREADY inside `EXPOSED_TREE` — concretely `ai_videos/wukong_juexing/prompts/shot99_kling.md`. `test.afterEach` `rm`s it. This satisfies "open a real triggering file" (the file IS real, written to a real path) without polluting the canonical project. Alternative — provoke the 404 by deleting `shot01_seedance.md` mid-test — is REJECTED because it permanently mutates a canonical artifact if the teardown fails.

## 场景定义 (Gherkin-style)

### Scenario M1 — MarkdownView renders style_guide.md

Triggering file: `ai_videos/wukong_juexing/style_guide.md`. Render mode: `MarkdownView`. Mode profiles: prod, dev.

```gherkin
Given the backend serves the wukong_juexing tree
And I am tracking console errors
When I navigate to "/?file=ai_videos/wukong_juexing/style_guide.md"
Then the <main> element is non-empty
And a heading with role="heading" level 1 is visible
And no element with class "locked-block" appears (style_guide.md has no 锁定描述符 block)
And no <script> tag from the rendered markdown exists in <main> (sanitization)
And consoleErrors is empty
```

### Scenario M2 — MarkdownView locked-block pill on characters/main.md

Triggering file: `ai_videos/wukong_juexing/characters/main.md`. Render mode: `MarkdownView` + locked-block pre-processor (FR-65–66).

```gherkin
Given the backend serves the wukong_juexing tree
And I am tracking console errors
When I navigate to "/?file=ai_videos/wukong_juexing/characters/main.md"
Then the <main> element is non-empty
And exactly one <span class="locked-block" data-version="v1"> exists
And the locked-block element has computed CSS "position: relative" (so the ::before pill positions correctly)
And the pill text "锁定块" is visually present (computed CSS ::before content)
And consoleErrors is empty
```

(If `characters/main.md` does not yet contain a `【...锁定描述符 v1】` block, the U7 implementer adds one byte-identically per `agent_refs/project/ai_video.md` rule 6; this is a stage-6 prerequisite recorded in `acceptance_criteria.md`.)

### Scenario S1 — ShotPairView side-by-side both partners present

Triggering file: `ai_videos/wukong_juexing/prompts/shot01_kling.md`. Partner: `shot01_seedance.md` (exists). Render mode: `ShotPairView` (FR-50–54).

```gherkin
Given the backend serves the wukong_juexing tree
And both shot01_kling.md and shot01_seedance.md exist
And I am tracking console errors
When I navigate to "/?file=ai_videos/wukong_juexing/prompts/shot01_kling.md"
Then the <main> element is non-empty
And [data-testid="shot-pair-left"] is visible and contains rendered markdown
And [data-testid="shot-pair-right"] is visible and contains rendered markdown
And the resizable-panel handle (role="separator") is interactable
And a button with text "复制 Kling prompt" exists
And a button with text "复制 Seedance prompt" exists
And NO yellow banner with class "partner-missing" exists
And consoleErrors is empty

When I click "复制 Kling prompt"
Then the aria-live region announces "已复制" within 500ms
```

### Scenario S2 — ShotPairView partner-missing yellow banner

Triggering file: `ai_videos/wukong_juexing/prompts/shot99_kling.md` (synthetic, see § 测试文件清单 note). No partner. Render mode: `ShotPairView` partner-missing branch (FR-52).

```gherkin
Given the backend serves the wukong_juexing tree
And shot99_kling.md exists (created by beforeEach)
And shot99_seedance.md does NOT exist
And I am tracking console errors
When I navigate to "/?file=ai_videos/wukong_juexing/prompts/shot99_kling.md"
Then the <main> element is non-empty
And [data-testid="shot-pair-left"] is visible and contains rendered markdown
And [data-testid="shot-pair-right"] is NOT visible
And a yellow banner with class "partner-missing" is visible
And the banner text contains "缺少配对文件: ai_videos/wukong_juexing/prompts/shot99_seedance.md"
And the banner contains a link whose href routes to the partner path under a BrokenLink view
And consoleErrors is empty
```

### Scenario T1 — ShotlistTableView row-click navigates to ShotPairView

Triggering file: `ai_videos/wukong_juexing/shotlist.md`. Render mode: `ShotlistTableView` (FR-55–58).

```gherkin
Given the backend serves the wukong_juexing tree
And I am tracking console errors
When I navigate to "/?file=ai_videos/wukong_juexing/shotlist.md"
Then the <main> element is non-empty
And a <table> element exists with at least 1 <tbody> row
And the first column of each row contains a <button> whose text matches /^shot\d+$/

When I click the button with text "shot01"
Then the URL becomes "/?file=ai_videos/wukong_juexing/prompts/shot01_kling.md&view=shot-pair"
And [data-testid="shot-pair-left"] is visible (handing over to S1's ShotPairView assertions)
And consoleErrors is still empty
```

### Scenario I1 — ImageRefView image-present

Triggering file: `ai_videos/wukong_juexing/characters/ref_images/main_seedream.md`. Companion: `main_seedream.png` (assumed present — `test.beforeAll` writes a 1×1 PNG bytestring if absent, since stage 6 outputs do not yet include the rendered立绘). Render mode: `ImageRefView` (FR-59–63).

```gherkin
Given the backend serves the wukong_juexing tree
And main_seedream.md exists in characters/ref_images/
And main_seedream.png exists in characters/ref_images/ (created by beforeAll if absent)
And I am tracking console errors
When I navigate to "/?file=ai_videos/wukong_juexing/characters/ref_images/main_seedream.md"
Then the <main> element is non-empty
And [data-testid="image-ref-prompt-pane"] is visible and contains rendered markdown
And [data-testid="image-ref-image-pane"] is visible
And exactly one <img> with alt ending "立绘" is present in the right pane
And the <img> resolves (response status 200, naturalWidth > 0)
And the <img> src includes "?path=" AND "&mtime=" (FR-26 cache-busting)
And NO placeholder text "尚未生成立绘" appears
And consoleErrors is empty
```

### Scenario I2 — ImagePlaceholder image-absent fallback

Triggering file: `ai_videos/wukong_juexing/characters/ref_images/main_seedream.md`. Companion: `main_seedream.png` (REMOVED for this test via `test.beforeEach` rename to `.bak`, restored in `afterEach`). Render mode: `ImagePlaceholder` (FR-62).

```gherkin
Given the backend serves the wukong_juexing tree
And main_seedream.md exists in characters/ref_images/
And main_seedream.png does NOT exist (renamed to .bak by beforeEach)
And I am tracking console errors
When I navigate to "/?file=ai_videos/wukong_juexing/characters/ref_images/main_seedream.md"
Then the <main> element is non-empty
And [data-testid="image-ref-prompt-pane"] is visible and contains rendered markdown
And [data-testid="image-ref-image-pane"] is visible
And NO <img> element with alt ending "立绘" exists in the right pane
And the right pane contains the exact text "尚未生成立绘 — 复制左侧 prompt 至 Seedream 后保存为 main_seedream.png 并刷新"
And consoleErrors is empty

After the test:
The afterEach restores main_seedream.png from main_seedream.png.bak
```

### Scenario Q1 — QaView renders interview/qa.md

Triggering file: `specs/ai_video/wukong_juexing/interview/qa.md`. Render mode: `QaView` (FR-48 path matcher `/interview/qa\.md$`). Critically: this scenario MUST cover BOTH the standard `- A: text` form AND the autonomous-mode `- A *(judgment call ...)*: text` form — per development.md move #10 (parser regex tested against real upstream output).

```gherkin
Given the backend serves the wukong_juexing tree
And specs/ai_video/wukong_juexing/interview/qa.md exists with at least one Q/A block
And I am tracking console errors
And the QaErrorBoundary is mounted (FR-49 — real React Error Boundary, not try/catch)
When I navigate to "/?file=specs/ai_video/wukong_juexing/interview/qa.md"
Then the <main> element is non-empty
And at least one element with [data-testid="qa-question"] is visible
And at least one element with [data-testid="qa-answer"] is visible
And NO element with [data-testid="qa-error-boundary-fallback"] is visible (boundary did NOT trigger)
And NO blank-page state ("main" computed height > 100px)
And consoleErrors is empty
And no "pageerror" event fired during render
```

This scenario is the regression net for the `spec_driven-20260502-clean` blank-page bug. The `pageerror` listener is the load-bearing addition — `console.error` did NOT catch the React reconciliation throw in that bug.

### Scenario J1 — JsonlView renders events.jsonl

Triggering file: `.audit/adhoc_agents/2026-05-05/ai_video_management-20260505-002710/events.jsonl` (a real audit log from this run). EXPOSED_TREE includes `.claude/agent_refs/**/*.md`, NOT `.audit/`. Therefore the test instead uses an EXPOSED_TREE-resident `.jsonl`: `specs/ai_video/wukong_juexing/findings/dossier.md`'s sibling — wait, none exist by default. **Resolution:** the scenario uses `specs/ai_video/wukong_juexing/validation/bdd_scenarios.md` if any `.jsonl` is added during stage 6, OR the U7 implementer adds a small fixture `.jsonl` to a writable EXPOSED_TREE location: `ai_videos/wukong_juexing/sample_log.jsonl` (one line per event, ≤5 lines). Render mode: `JsonlView`.

```gherkin
Given the backend serves the wukong_juexing tree
And ai_videos/wukong_juexing/sample_log.jsonl exists with N JSON objects (one per line)
And I am tracking console errors
When I navigate to "/?file=ai_videos/wukong_juexing/sample_log.jsonl"
Then the <main> element is non-empty
And exactly N elements with [data-testid="jsonl-card"] are visible
And no card text is truncated to "..." (each card's textContent contains its full source line modulo formatting)
And consoleErrors is empty
```

### Scenario C1 — CodeView renders publish.md as code

Triggering file: `ai_videos/wukong_juexing/publish.md` rendered with `?view=code` override (FR-47 view-override URL param). Render mode: `CodeView`.

```gherkin
Given the backend serves the wukong_juexing tree
And I am tracking console errors
When I navigate to "/?file=ai_videos/wukong_juexing/publish.md&view=code"
Then the <main> element is non-empty
And a <pre> element exists containing the file's raw text (no markdown rendering)
And the <pre> has computed background color matching the dark carve-out palette (FR-80)
And the WCAG AA contrast ratio between <pre> text and <pre> background ≥ 4.5:1
And consoleErrors is empty
```

### Scenario R1 — RegeneratePanel scope-toggle gating

Triggering file: `specs/ai_video/wukong_juexing/final_specs/spec.md` (any file under wukong_juexing surfaces the panel). Tests three sub_type cases: `novel`, `short`, `None`. Per FR-22–24 + FR-73.

```gherkin
Given the backend serves the wukong_juexing tree
And the user has opened the regen panel
And I am tracking console errors

# Case 1: novel (wukong_juexing's qa.md sets sub_type=novel)
When I open the panel for project "wukong_juexing" and select stage "execution"
Then a scope selector is visible
And it offers options "project", "episode N", "episodes M..N"
And the default selection is "project"

# Case 2: novel + select "episode N"
When I select "episode N" and enter 5
Then the input validates ≥1 (rejects 0 with inline error)
And the "Generate" button is enabled

# Case 3: short (test fixture — beforeAll writes a temp project ai_videos/_test_short/ with sub_type=short qa.md)
When I open the panel for project "_test_short" and select stage "execution"
Then NO scope selector is visible
And the request payload sent to /api/regen-prompt has scope="project"

# Case 4: sub_type=None (test fixture — beforeAll writes ai_videos/_test_unknown/ with no qa.md)
When I open the panel for project "_test_unknown" and select stage "execution"
Then NO scope selector is visible
And the request payload sent to /api/regen-prompt has scope="project"

And consoleErrors is empty across all cases
```

### Scenario X1 — Cross-tree counterpart link

Triggering file: `ai_videos/wukong_juexing/script.md` (any file under `ai_videos/{name}/`). Per FR-78.

```gherkin
Given the backend serves the wukong_juexing tree
And I am tracking console errors
When I navigate to "/?file=ai_videos/wukong_juexing/script.md"
Then the <main> element is non-empty
And a link with text "查看规格" is visible in the toolbar
And its href is "/?file=specs/ai_video/wukong_juexing/"

When I click "查看规格"
Then the URL becomes "/?file=specs/ai_video/wukong_juexing/"
And the file viewer renders the project root listing for that path

When I navigate to "/?file=specs/ai_video/wukong_juexing/interview/qa.md"
Then NO link with text "查看规格" is visible (reverse link deferred to v2 per FR-78)

And consoleErrors is empty
```

### Scenario SEC1 — Origin gate rejects 8765

Verifies FR-11 + FR-85(e). Direct API call from a foreign origin; not a UI flow — pure browser-driven HTTP. Both modes run this; in dev mode it confirms the Vite proxy doesn't accidentally relax the gate.

```gherkin
Given the backend serves the wukong_juexing tree
When the browser POSTs to {baseURL}/api/promote with:
  Origin: http://127.0.0.1:8765
  body: {stage: "interview", source_path: "specs/ai_video/wukong_juexing/interview/qa.md", item_id: "test", item_text: "test"}
Then the response status is 403
And NO promoted.md mutation occurred (assert mtime unchanged on the file)
```

### Scenario PF — 8 primary flows golden path

Walks the 8 flows from spec § Primary flows in sequence within one test. Each step asserts its DOM checkpoint; failure of any step fails the whole test (golden path is atomic per move #1).

```gherkin
Given the backend serves the wukong_juexing tree
And I am tracking console errors

# Flow 1: Browse projects
When I navigate to "/"
Then a sidebar with sections "AI Videos", "Specs", "Context" is visible
And a tree node "wukong_juexing" with badge "剧" is visible (sub_type=novel; FR-44)

# Flow 2: View shot prompt as pair (covered by Scenario S1 — abbreviated here)
When I click the sidebar node for shot01_kling.md
Then [data-testid="shot-pair-left"] AND [data-testid="shot-pair-right"] are visible

# Flow 3: View shotlist as navigable table (covered by Scenario T1)
When I click the sidebar node for shotlist.md
Then a <table> with shot-id buttons is visible

# Flow 4: Preview Seedream立绘 ref (covered by Scenario I1)
When I click the sidebar node for main_seedream.md
Then [data-testid="image-ref-prompt-pane"] AND [data-testid="image-ref-image-pane"] are visible

# Flow 5: Edit a file
When I click "Edit" on style_guide.md
And I change the textarea content
And I click "Save"
Then the PUT /api/file response is 200
And the sidebar tree mtime auto-bumps (FR-21)

# Flow 6: Pin an item
When I navigate to qa.md and click pin on the first Q/A block
Then POST /api/promote returns 200
And specs/ai_video/wukong_juexing/interview/promoted.md is appended to (verify via subsequent GET /api/file)

# Flow 7: Generate a regen prompt (covered by Scenario R1)
When I open the regen panel and click "Generate"
Then a <pre data-testid="regen-prompt-output"> is visible with non-empty text

# Flow 8: Cross-tree jump (covered by Scenario X1)
When I click "查看规格" while viewing a file under ai_videos/wukong_juexing/
Then the URL routes to specs/ai_video/wukong_juexing/

And consoleErrors is empty across all 8 flows
```

## 覆盖矩阵

Maps each Functional Requirement (FR) and required move to its covering scenario(s). A row with no covering scenario is a coverage gap and a `blocker` finding at sign-off.

| FR / Rule | Scenario(s) | Severity if uncovered |
|---|---|---|
| FR-5 prod-mode runtime | `prod-mode` project × every spec | `blocker` |
| FR-6 dev-mode runtime + Vite proxy | `dev-mode` project × every spec, esp. SEC1 | `blocker` |
| FR-44 sub-type badge `剧` / `短` / none | PF (flow 1), R1 (case 1+3+4) | `blocker` |
| FR-47–48 view dispatch | M1, S1, T1, I1, Q1, J1, C1 (one per render mode) | `blocker` |
| FR-49 ParseFallback Error Boundary | Q1 (consoleErrors + pageerror + boundary not triggered) | `critical` |
| FR-50–54 ShotPairView | S1, S2 | `blocker` |
| FR-52 partner-missing yellow banner | S2 | `blocker` |
| FR-53 clipboard + aria-live | S1 (copy-button click + aria-live announcement) | `blocker` |
| FR-55–58 ShotlistTableView | T1 | `blocker` |
| FR-59–63 ImageRefView image-present | I1 | `blocker` |
| FR-62 image-absent placeholder | I2 | `critical` (FR-62 text is exact-match) |
| FR-64 Editor hidden in image-ref view | I1 (assert NO Edit button visible when src ends `.png`) | `blocker` |
| FR-65–66 locked-block pill | M2 | `blocker` |
| FR-67–69 CJK rendering | M1, M2 (assert `lang="zh-Hans"` on render container; computed font-family contains CJK fallbacks) | `warning` |
| FR-70–75 RegeneratePanel | R1 | `blocker` |
| FR-73 scope-toggle novel/short/None gating | R1 (cases 1, 3, 4) | `blocker` |
| FR-76–77 Editor + image-extension hide | PF (flow 5), I1 (no Edit button) | `blocker` |
| FR-78 cross-tree link forward direction + reverse-deferred | X1 | `blocker` |
| FR-79–80 light theme + dark `<pre>` carve-out + WCAG AA | C1 (background color + contrast ratio) | `warning` |
| FR-11 Origin/Host gate at 8765 | SEC1 | `critical` |
| FR-85 Playwright e2e suite minimum (a–e) | (a) S1, T1; (b) T1; (c) I1, I2; (d) R1; (e) SEC1 | `blocker` |
| Move #1 multi-mode parity | playwright.config.ts × 2 projects × every spec | `blocker` |
| Move #8 per-render-mode scenario | M1, S1, T1, I1, Q1, J1, C1, I2 (all 8 render dispatch paths) | `blocker` |
| Move #9 error-boundary coverage (no `try { return <Foo /> } catch`) | Q1 (pageerror listener + no fallback element) | `blocker` |
| Move #10 parser regex against real upstream output | Q1 (asserts both standard AND autonomous-mode Q/A forms render) | `blocker` |
| Move #11 Origin/Host pre-rewrite shape | SEC1 (× dev-mode profile — proves the Vite proxy `configure` hook is wired) | `blocker` |
| Move #4 boot smoke (validation.requires_manual_walkthrough → handled by accessibility_and_manual specialist) | (out of scope for this level) | n/a |

**Render-mode coverage (move #8 explicit checklist):**

| Render mode | Scenario | Triggering file (real, on disk) |
|---|---|---|
| MarkdownView | M1 | `ai_videos/wukong_juexing/style_guide.md` |
| MarkdownView (locked-block pill) | M2 | `ai_videos/wukong_juexing/characters/main.md` |
| ShotPairView (both partners) | S1 | `ai_videos/wukong_juexing/prompts/shot01_kling.md` |
| ShotPairView (partner missing) | S2 | `ai_videos/wukong_juexing/prompts/shot99_kling.md` (synthetic) |
| ShotlistTableView | T1 | `ai_videos/wukong_juexing/shotlist.md` |
| ImageRefView (image present) | I1 | `ai_videos/wukong_juexing/characters/ref_images/main_seedream.md` (+ `.png`) |
| ImagePlaceholder (image absent) | I2 | `ai_videos/wukong_juexing/characters/ref_images/main_seedream.md` (`.png` removed) |
| QaView | Q1 | `specs/ai_video/wukong_juexing/interview/qa.md` |
| JsonlView | J1 | `ai_videos/wukong_juexing/sample_log.jsonl` (U7 fixture) |
| CodeView | C1 | `ai_videos/wukong_juexing/publish.md` (with `?view=code`) |

Eight render dispatch paths in `Reader.tsx`, eight covering scenarios (MarkdownView counted once for the dispatch — M1 + M2 are two scenarios on the same render mode for FR-65 pill coverage).

## Deferrals + open items for sign-off

- **JsonlView fixture.** No `.jsonl` exists in EXPOSED_TREE today. U7 ships `ai_videos/wukong_juexing/sample_log.jsonl` (≤1 KB, 3–5 representative event-shaped lines). NOT a stage-6 work output — purely a test fixture. Listed in `acceptance_criteria.md` as a fixture prerequisite.
- **Locked-block fixture in characters/main.md.** As noted in M2: requires a real `【...锁定描述符 v1】` block in `characters/main.md`. If absent at stage-6 start, U7 adds it. Per `agent_refs/project/ai_video.md` rule 6 — byte-identical descriptor.
- **Companion `.png` for ImageRefView.** `test.beforeAll` writes a 1×1 PNG to `main_seedream.png` if absent (the canonical project does not yet have the rendered立绘). Restore (delete or revert) in `afterAll`. The image-absent scenario (I2) reverses this in `beforeEach`/`afterEach`.
- **Scope-toggle test fixtures.** Cases 3 + 4 of R1 require temp ai_video projects (`_test_short`, `_test_unknown`). U7 ships a `e2e/_fixtures/setup_temp_projects.ts` that creates them in `beforeAll` + tears down in `afterAll`. Underscore prefix excludes them from sidebar's natural sort if the user happens to run the dev server during testing — paranoia, not load-bearing.
- **Reverse cross-tree link.** Spec defers to v2 (FR-78). X1 explicitly asserts NO reverse link — protects against a well-intentioned future implementer adding it without spec change.
- **Manual walkthrough.** NOT in this level's scope — handled by `accessibility_and_manual.md` (specialist 06). Stage-5 strategy ensures `validation.requires_manual_walkthrough` is emitted after this level passes (per general.md principle 4 + development.md move #7).
- **Boot smoke.** NOT in this level's scope — covered by `backend_tests.md` (specialist 03) per development.md move #4.
