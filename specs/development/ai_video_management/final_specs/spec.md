# Final spec — ai_video_management

Run: ai_video_management-20260505-002710
Stage: 4 (spec compilation)
Inputs consumed: `revised_prompt.md`, `interview/qa.md`, `findings/dossier.md`, `findings/angle-{spec-driven-parallel-audit, ai-video-render-mode-design, regen-prompt-ai-video-semantics, ai-video-tree-and-detection}.md`

## Goal

Build an interactive viewer/editor SPA + FastAPI backend at `projects/ai_video_management/`, paralleling `projects/spec_driven/` for the **ai_video** half of the spec-driven workflow. The webapp visualizes and manages two trees side-by-side: `ai_videos/{name}/` (output artifacts — character bibles, Seedream立绘 prompts, style guides, scripts, shotlists, dual Kling+Seedance shot prompts, publish metadata) and `specs/ai_video/{name}/` (workflow trail — intake, interview, findings, final_specs, validation, changelog, follow_ups). It reuses spec_driven's security posture (Origin/Host gate, EXPOSED_TREE sandbox, RFC 7232 mtime concurrency, IPv4 loopback only) and pinning model (`<stage>/promoted.md` sidecars). It adds three ai_video-specific view modes (ShotPairView, ShotlistTableView, ImageRefView) and an ai_video-specific regen-scope axis (`scope=project | episode N | episodes M..N` for novels; shorts force `project`). Bound port: **8766** (parallels spec_driven's 8765 for simultaneous run).

## Out of scope

- Render-API integration with Kling / Seedance / Seedream (text-prompt management only; user runs render externally).
- Multi-tenant / multi-user; auth; WebSockets / SSE real-time collaboration; mobile-responsive layout.
- Storyboard horizontal-scroll view with auto-frame thumbnails (v2; needs externally rendered shot `.png` files).
- Cross-publish manager (one-click 抖音 / 视频号 metadata variants); English-language publish translation.
- Compare-two-ai_videos-projects diff view.
- File create / delete / upload through the webapp (explicitly never; same as spec_driven).
- Dark-mode chrome toggle (per `agent_refs/project/development.md` rule 1).
- File-system watcher / auto-refresh on filesystem mtime change (manual refresh + post-PUT auto-bump only).
- Polling for new `.png` files in `ref_images/` (manual refresh).

## Primary flows

The user is the sole actor — a creator running the pipeline manually. Webapp is a localhost productivity tool.

1. **Browse projects** — open `http://127.0.0.1:8766/`, see recursive sidebar with three sections: AI Videos / Specs / Context.
2. **View shot prompt as pair** — click any `prompts/shot{NN}_{kling|seedance}.md` → ShotPairView renders both files side-by-side with copy buttons.
3. **View shotlist as navigable table** — click any `shotlist.md` under `ai_videos/` → ShotlistTableView; each shot id in column 1 is a button that opens that shot's ShotPairView.
4. **Preview Seedream立绘 ref** — click `characters/ref_images/{role}_seedream.md` → ImageRefView; left pane shows prompt, right pane shows companion `.png` (or fallback message if not generated yet).
5. **Edit a file** — click "Edit" on any markdown view → `Editor` (textarea + save) → `PUT /api/file` with `If-Unmodified-Since` mtime; 409 → "file changed externally — Reload?".
6. **Pin an item** — on any qa.md / dossier / spec / strategy view, click pin → `POST /api/promote` writes to `<stage>/promoted.md`.
7. **Generate a regen prompt** — click "Generate regen prompt" on any stage → RegeneratePanel surfaces stage selector + scope toggle (gated on `sub_type === "novel"`) + INTERACTIVE/AUTONOMOUS mode → `POST /api/regen-prompt` returns assembled prompt → user copy-pastes into Claude Code CLI.
8. **Cross-tree jump** — when viewing a file under `ai_videos/{name}/`, sidebar shows "查看规格" link → click jumps to `specs/ai_video/{name}/`.

## Functional requirements

### Backend module layout

- **FR-1** Backend libs at `projects/ai_video_management/backend/libs/`: `repo_root.py`, `file_reader.py`, `file_writer.py`, `promotions.py`, `safe_resolve.py`, `exposed_tree.py`, `tree_walker.py`, `regen_prompt.py`, `stages.py`, `api_security.py`, `api.py`, `sub_type_lookup.py`, `main.py`. **No `render_views.py`** (view dispatch is purely client-side).
- **FR-2** `main.py` is ≤15 lines: argparse → call `api.create_app()` → `uvicorn.run(app, host="127.0.0.1", port=8766)`.

### Bind + serve

- **FR-3** Backend binds **`127.0.0.1`** (IPv4 loopback) only. IPv6 (`[::1]`) and `0.0.0.0` are explicitly rejected.
- **FR-4** Default bound port: **8766** (parallels spec_driven's 8765 for simultaneous run).
- **FR-5** Single-process production mode: `make run-prod` builds the frontend bundle into `backend/static/` and serves SPA + API from one FastAPI process.
- **FR-6** Dev mode: backend on `127.0.0.1:8766`; Vite dev server on `127.0.0.1:5174` (parallels spec_driven's 5173). Vite proxy forwards `/api/*` to backend with `Origin` rewrite to `http://127.0.0.1:8766` (per spec_driven follow-up 006).

### EXPOSED_TREE membership

- **FR-7** EXPOSED_TREE includes exactly these 5 roots (recursive globs auto-pick subfolders):
  1. `ai_videos/**/*.{md,json,jsonl,yaml,yml,txt,png,jpg}`
  2. `research/**/*.{md,json,jsonl,yaml,yml,txt,png,jpg}` (added by follow-up 003 — free-form reference dumps; NOT spec-pipeline output)
  3. `specs/ai_video/**/*.{md,json,jsonl,yaml,yml,txt}`
  4. `CLAUDE.md`
  5. `.claude/{skills/agent_team/{SKILL.md, playbooks/*.md}, agent_refs/**/*.md}`
- **FR-8** `is_inside` predicate (port from `spec_driven/backend/libs/exposed_tree.py:65-92`): drop `projects/` from allowed top-level set; admit `ai_videos/` and `research/` (added by follow-up 003 — same `_EXCLUDED_DIRS` filter applies); tighten `specs/**` to `specs/ai_video/**`.

### Mutation surface

- **FR-9** Exactly 4 state-changing endpoints, no more: `PUT /api/file`, `POST /api/regen-prompt`, `POST /api/promote`, `DELETE /api/promote`. No file create / delete / upload endpoints. <!-- Per follow-up 001: regen-prompt + promote endpoints are dropped. Per follow-up 007: drama-scoped `POST /api/rename-media` added (rename-only, no create/delete/upload — see FR-9b). -->
- **FR-9b** (follow-up 007) `POST /api/rename-media` — drama-scoped batch rename for image+video files. Body `{path: "ai_videos/{drama}"}` (must resolve to an immediate child directory of `ai_videos/`). Recursively scans, renames each media file to `{immediate-parent-folder-name}.{ext}` (one file per ext) or `{name}{N}.{ext}` (multiple, lexicographic order, N starting at 1). Two-pass via temp names to avoid intra-folder collisions. Returns `{renamed:[{from,to}],skipped:[],errors:[{path,message}]}`. Origin/Host gate applies. No file create/delete/upload — rename only.
- **FR-10** Read endpoints: `GET /api/tree`, `GET /api/file?path={path}`, `GET /api/media?path={path}` (added by follow-up 005 — bypasses 1 MiB cap with HTTP-range FileResponse). All honor EXPOSED_TREE sandbox.

### Security

- **FR-11** **Origin / Host gate** on every state-changing endpoint. Foreign / missing / wrong-port → **403**. Loopback aliases (`localhost` ↔ `127.0.0.1` at the bound port) admit. Port `8766` is the only valid port; `8765` (spec_driven) is foreign.
- **FR-12** **Path traversal hardening** — all probes (`..`, percent-encoded, ADS, Windows reserved names, 8.3 short names, mixed slashes, Vite CVE-2025-62522 trailing-backslash) collapse to a single **404** (no existence oracle). Symlinks / Windows junctions refused outright.
- **FR-13** **Extension allowlist** for reads: `.md`, `.json`, `.yaml`, `.yml`, `.jsonl`, `.txt`, `.png`, `.jpg`. SVG NOT allowed (code-execution vector). Image extensions are NOT in the writeable list (`PUT /api/file` rejects them with 400).
- **FR-14** **1 MiB body cap** on `PUT /api/file`. 50 KiB soft warning logged. >1 MiB → 413.
- **FR-15** **`If-Unmodified-Since`** (RFC 7232 mtime) required on `PUT /api/file`. Stale mtime → **409** so the SPA can offer "file changed externally — Reload?".
- **FR-16** **Markdown sanitization** uses `rehype-sanitize` default schema; raw HTML, event handlers, `javascript:` URIs are stripped on render.
- **FR-17** **CSP header** on responses: `default-src 'self'; img-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'`. (`'unsafe-inline'` for styles is required by Vite-bundled CSS-in-JS; scripts stay strict.)

### Tree walk

- **FR-18** `GET /api/tree` returns a recursive `TreeNode[]` with sections in fixed order: **AI Videos**, **Research**, Specs (ai_video), Context. (Research added by follow-up 003 — walks `research/**` recursively. Specs / Context sections remain not-yet-implemented in current code; that drift is acknowledged and tracked separately. AI Videos and Research are live.)
- **FR-19** TreeNode shape (port from spec_driven `tree_walker.py` + 2 ai_video extensions):
  ```python
  @dataclass(frozen=True)
  class TreeNode:
      name: str
      path: str                       # path relative to repo root
      type: Literal["dir", "file", "image"]   # NEW: "image" for .png/.jpg leaves
      mtime: float                    # epoch seconds
      children: tuple["TreeNode", ...] = ()
      project_meta: ProjectMeta | None = None  # NEW: only on ai_videos/{name}/ dir nodes
  
  @dataclass(frozen=True)
  class ProjectMeta:
      sub_type: Literal["novel", "short"] | None
      shot_count: int | None
      episode_count: int | None
  ```
- **FR-20** Sort order: alphabetical, dirs first (port from spec_driven `tree_walker.py:105`).
- **FR-21** Refresh semantics: manual button + auto-bump on `PUT /api/file` success (per spec_driven `App.tsx:13-31`). NO file-system watcher.

### Sub_type detection

- **FR-22** `sub_type_lookup.py` parses `specs/ai_video/{name}/interview/qa.md` for the canonical settled-facts pipe-table row using regex (multiline):
  ```
  ^\|\s*`?sub_type`?\s*\|\s*`?(novel|short)`?\s*\|
  ```
- **FR-23** Edge-case handling: qa.md missing / row missing / value typo / multiple rows → return `None`. Never crash, never invent a third value.
- **FR-24** Single source of truth: BOTH the sidebar badge AND the regen-scope toggle gating consume the same `sub_type_lookup.lookup(project_name)` result.

### `/api/file` (read)

- **FR-25** `GET /api/file?path={path}` returns:
  - For text files (`.md`, `.json`, `.jsonl`, `.yaml`, `.yml`, `.txt`): JSON `{content: str, mtime: float}`.
  - For images (`.png`, `.jpg`): raw binary with `Content-Type: image/png` or `image/jpeg`, `Cache-Control: private, max-age=0, must-revalidate`, `Last-Modified: <RFC 1123>`.
- **FR-26** Image route accepts `?mtime={float}` query-string for cache-busting; the value is informational (response is always fresh per Cache-Control); the browser uses URL-uniqueness to skip its cache when the user re-renders the立绘.

### `/api/file` (write — `PUT`)

- **FR-27** `PUT /api/file` body schema (JSON): `{path: str, content: str}`. Headers: `If-Unmodified-Since: <RFC 1123>` required.
- **FR-28** Rejects:
  - Path outside EXPOSED_TREE → 404.
  - Extension not in writeable allowlist (image extensions excluded) → 400.
  - Body >1 MiB → 413.
  - Stale mtime → 409.
  - Missing/foreign Origin → 403.
- **FR-29** On success: writes atomically (write to temp file in same directory + rename). Returns `{mtime: float}` (the new mtime). Triggers tree auto-bump on the client.

### `/api/promote` and `/api/promote` DELETE

- **FR-30** `POST /api/promote` body schema: `{stage: str, source_path: str, item_id: str, item_text: str}` where `stage ∈ {"interview", "findings", "final_specs", "validation"}`. Appends to `specs/ai_video/{name}/<stage>/promoted.md` per the spec_driven `promotions.py` contract.
- **FR-31** `DELETE /api/promote` body schema: `{stage: str, item_id: str}`. Removes the matching block from `<stage>/promoted.md`.
- **FR-32** Stage 6 (project code under `ai_videos/{name}/`) does NOT support promotion in v1. Endpoints reject `stage="execution"` or paths under `ai_videos/{name}/` (not `specs/ai_video/{name}/`) with 400.
- **FR-33** Port `_parse_promoted_text` and `_serialize_promoted_block` from spec_driven `promotions.py` byte-identically.

### `/api/regen-prompt`

- **FR-34** `POST /api/regen-prompt` body schema (JSON):
  ```typescript
  {
    project_name: string,            // ai_video project name (e.g., "wukong_juexing")
    project_type: "ai_video",        // hard-locked; "development" rejected with 400
    stage: "intake" | "interview" | "research" | "spec" | "validation_strategy" | "execution",
    modules: string[],               // optional, per-stage module slugs (defaults to all)
    mode: "INTERACTIVE" | "AUTONOMOUS",  // default INTERACTIVE
    scope: "project" | "episode" | "episodes",  // default "project"
    scope_episode: number | null,    // required iff scope === "episode"
    scope_episode_range: {start: number, end: number} | null,  // required iff scope === "episodes", start ≤ end
  }
  ```
- **FR-35** Response schema: `{prompt: string, scope: string, scope_resolved: string, byte_size: number}`.
- **FR-36** 4xx surface:
  - 400: bad scope, `project_type` not "ai_video", `scope=episode|episodes` on a `short` sub_type, missing required `scope_episode` / `scope_episode_range`.
  - 409: `sub_type` unknown (qa.md missing / unparseable) when scope ≠ "project".
  - 413: assembled prompt body >1 MiB hard cap. (50 KiB soft warning logged.)
- **FR-37** Stages 1–5 prompt body is **byte-identical to spec_driven** (modulo `project_type=ai_video` + optional `sub_type` line). Reuse `_READ_ZERO_CONTRACT` and `_AUTONOMOUS_IMPERATIVE` constants from `projects/spec_driven/backend/libs/regen_prompt.py` by **copying the bytes verbatim** into the new `regen_prompt.py` (no import; same-line text).
- **FR-38** Stage 6 has 4 prompt-body variants:
  - `short × project`: assembles `ai_videos/{name}/` delete contract + write contract per `agent_refs/project/ai_video.md` rule 10 short layout.
  - `novel × project`: same shape, novel layout.
  - `novel × episode N`: scoped delete to `ai_videos/{name}/episodes/ep{NN:02d}/` only; preserves `characters/`, `world.md`, `style_guide.md`, `arc_outline.md`, sibling episodes; forbids edits to preserved paths during regen.
  - `novel × episodes M..N`: explicit episode list expanded inline (e.g., `ep05`, `ep06`, `ep07`) — no `M..N` shorthand in the prompt body. No upper-bound cap.
- **FR-39** Every regen-prompt body inlines:
  - `revised_prompt.md` content
  - All `user_input/follow_ups/*.md` content
  - The stage's `<stage>/promoted.md` content (if non-empty)
  - The read-zero contract verbatim from `CLAUDE.md` (per stage row of the table)
  - Audit-event tags (`regen.delete.planned`, `regen.delete.completed`, `regen.write.completed`)
  - Execution-mode header (`# EXECUTION MODE: AUTONOMOUS` or `# EXECUTION MODE: INTERACTIVE`)

### Frontend layout

- **FR-40** Frontend at `projects/ai_video_management/frontend/`: `package.json`, `vite.config.ts`, `tsconfig.json`, `index.html`, `src/`.
- **FR-41** `src/` structure (port spec_driven shape, no `components/views/` subfolder):
  ```
  src/
  ├── main.tsx
  ├── App.tsx
  ├── components/
  │   ├── Sidebar.tsx
  │   ├── Reader.tsx
  │   ├── RegeneratePanel.tsx
  │   ├── Editor.tsx
  │   ├── BrokenLink.tsx
  │   ├── Breadcrumb.tsx
  │   ├── ShotPairView.tsx          # NEW
  │   ├── ShotlistTableView.tsx     # NEW
  │   └── ImageRefView.tsx          # NEW
  ├── markdown/
  │   ├── MarkdownView.tsx
  │   ├── QaView.tsx
  │   ├── JsonlView.tsx
  │   ├── CodeView.tsx
  │   ├── ParseFallback.tsx
  │   ├── QaErrorBoundary.tsx
  │   └── ImagePlaceholder.tsx
  ├── helpers/
  │   ├── linkResolver.ts
  │   ├── qaParser.ts
  │   ├── autonomousMode.ts
  │   ├── shotPairing.ts            # NEW
  │   └── shotlistParser.ts         # NEW
  └── styles/
      └── app.css                   # light-theme chrome + dark <pre> carve-outs
  ```
- **FR-42** Frontend dependencies (in `package.json`): `react ^18`, `react-dom ^18`, `react-markdown ^9`, `remark-gfm ^4`, `rehype-sanitize ^6`, `react-router-dom ^6`, **`react-resizable-panels ^4`** (NEW for ShotPairView + ImageRefView), `vite ^5`, `typescript ^5`. Dev deps: `@types/*`, `vitest`, `@playwright/test`. NO exotic dependencies beyond these.

### Sidebar

- **FR-43** Sidebar renders sections in fixed order: **AI Videos** / **Research** / **Specs** / **Context** (English labels for app chrome consistency; file content stays Chinese; **Research** added by follow-up 003 and is live; Specs and Context remain not-yet-implemented).
- **FR-44** For each `ai_videos/{name}/` directory node, render a sub-type badge: `短` (short) or `剧` (novel). When `sub_type=None` (qa.md missing / unparseable), render NO badge.
- **FR-45** When viewing a file under `ai_videos/{name}/...`, the file viewer's top toolbar shows a "查看规格" link → `?file=specs/ai_video/{name}/` (jumps to project root, not per-file mirror).
- **FR-46** Sidebar refresh button + auto-bump on PUT success. No fs-watcher.

### Reader (view dispatch)

- **FR-47** `Reader.tsx` dispatches by `(path, view-override)` pair. URL scheme: `?file={path}&view={mode}` where view override ∈ `{markdown, shot-pair, shotlist-table, image-ref, qa, jsonl, code}`. Default: inferred from path.
- **FR-48** Path-based default inference:
  - `path matches /prompts/shot\d+_(kling|seedance)\.md$/` → `shot-pair`
  - `path under ai_videos/.+/shotlist\.md$` → `shotlist-table`
  - `path matches /ref_images/.*_seedream\.md$/` OR `path ends .png|.jpg` → `image-ref`
  - `path matches /interview/qa\.md$` → `qa`
  - `path ends .jsonl` → `jsonl`
  - Other code (port spec_driven heuristics)
  - Fallback: `markdown`
- **FR-49** Every parse-on-render component is wrapped in `<ParseFallback>` (real React Error Boundary class, port from spec_driven).

### ShotPairView

- **FR-50** Renders `shotNN_kling.md` + `shotNN_seedance.md` side-by-side using `react-resizable-panels` v4 with `autoSaveId="shot-pair-split"`.
- **FR-51** `shotPairing.ts` regex: `^(.+/prompts/)shot(\d+)_(kling|seedance)\.md$`. Given the clicked file path, the partner is constructed by swapping `kling` ↔ `seedance`.
- **FR-52** When the partner file does NOT exist (404 from `/api/file`): render the clicked file in left pane only + a yellow banner: `"缺少配对文件: {partner_path}"` with a link to the partner's expected path (which itself opens a `BrokenLink` view).
- **FR-53** Each pane includes a "复制 Kling prompt" / "复制 Seedance prompt" button using `navigator.clipboard.writeText(content)`. Single app-root `aria-live="polite"` region announces "已复制" on success.
- **FR-54** Markdown content in each pane is rendered through the same `MarkdownView` component used elsewhere — same sanitization, same locked-block pill, same CJK rendering.

### ShotlistTableView

- **FR-55** Renders the shotlist `.md` file using `react-markdown` + `remark-gfm` + `rehype-sanitize`.
- **FR-56** Overrides `components.td` to detect shot-id text (regex `^shot\d+$`) in column 1; replaces text content with a `<button onClick={() => navigate(...)}>` that programmatically navigates to that shot's ShotPairView (`?file=...prompts/shot{NN}_kling.md&view=shot-pair`).
- **FR-57** Other table cells render plain (no special handling). Non-table content in shotlist.md (headings, paragraphs) renders as standard markdown.
- **FR-58** Shotlist column 1 must contain the shot id (per `wukong_juexing/shotlist.md` precedent + `agent_refs/project/ai_video.md` rule 4 implicit convention). Stage-6 validators in the ai_video pipeline can later enforce this; this webapp assumes it.

### ImageRefView

- **FR-59** Triggered when path matches `/ref_images/.+_seedream\.md$` OR path ends `.png|.jpg`.
- **FR-60** Layout: `react-resizable-panels` v4 with `autoSaveId="image-ref-split"`. Left pane: prompt markdown (when triggered by `_seedream.md`) or empty (when triggered by image directly). Right pane: image preview (when companion image exists) or fallback message.
- **FR-61** Image preview: `<img src="/api/file?path={enc}&mtime={mtime}" alt="{stem}立绘" />`. Mtime taken from tree node, baked into URL for browser cache-busting.
- **FR-62** Fallback when companion `.png` does NOT exist (only the prompt does): render the placeholder text **"尚未生成立绘 — 复制左侧 prompt 至 Seedream 后保存为 {expected-png-name}.png 并刷新"** in the right pane. No "Refresh" button (sidebar refresh + reclick handles it).
- **FR-63** Companion image discovery: same folder, same stem (e.g., `main_seedream.md` ↔ `main_seedream.png`). Case-sensitive on the stem; `.png` preferred over `.jpg` if both exist.
- **FR-64** Image extensions are read-only via `/api/file`. The Editor button is hidden when current view is `image-ref` and target is an image file.

### Locked-block pill

- **FR-65** `MarkdownView` pre-processes the markdown source with regex (multiline + dotall):
  ```
  /【.+? · .+? · 锁定描述符 v\d+】[\s\S]*?禁用 .*?。/g
  ```
  Each match wrapped in `<span class="locked-block" data-version="vN">...</span>` BEFORE handing to `react-markdown`. Rendered with a small "锁定块" pill positioned via CSS `::before` on the wrapper.
- **FR-66** Pill CSS: light-theme compliant; positioned absolute top-right of the block; subtle background `#f3f4f6`; small monospace font; cursor `help` with a tooltip "byte-equality contract — see characters/main.md".

### CJK rendering

- **FR-67** Markdown render container has `lang="zh-Hans"` attribute.
- **FR-68** Font stack: `-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif`.
- **FR-69** `word-break: normal` (default browser CJK wrapping).

### RegeneratePanel

- **FR-70** Stage selector (dropdown): `intake | interview | research | spec | validation_strategy | execution`.
- **FR-71** Module multi-select (per stage): renders the per-stage module slugs (port from `stages.py`).
- **FR-72** Mode toggle: `INTERACTIVE` (default) / `AUTONOMOUS`. Persists in `localStorage` under key `ai_video_management.autonomous_mode.v1` (NOT `spec_driven.autonomous_mode.v1` — keep state separate when both webapps coexist).
- **FR-73** Scope selector visible only when `stage === "execution"` AND `sub_type === "novel"`. Options: `project` (default) / `episode N` (with single number input, validated `≥1`) / `episodes M..N` (with two number inputs, validated `1 ≤ M ≤ N`). When `sub_type === "short"`, scope is hidden and forced to `project`. When `sub_type === None`, scope is hidden and forced to `project` (same as short).
- **FR-74** "Generate" button calls `POST /api/regen-prompt`; response prompt is rendered in a copy-ready dark `<pre>` block (carve-out from light theme per `agent_refs/project/development.md` rule 1 — fixed dark palette, NOT `prefers-color-scheme`-driven).
- **FR-75** Copy button on the prompt block uses `navigator.clipboard.writeText`; same `aria-live` pattern as ShotPairView.

### Editor

- **FR-76** Same UX as spec_driven `Editor.tsx`: textarea + save button. PUT with `If-Unmodified-Since`. 409 → toast: "file changed externally — Reload?".
- **FR-77** Hidden when current view is `image-ref` and target is an image file (FR-64).

### Cross-tree counterpart link

- **FR-78** When viewing a file under `ai_videos/{name}/`, the Reader's top toolbar shows "查看规格" link → `?file=specs/ai_video/{name}/`. When viewing a file under `specs/ai_video/{name}/`, NO reverse link in v1 (deferred to v2).

### Theme

- **FR-79** Light-theme chrome per `agent_refs/project/development.md` rule 1: `:root { color-scheme: light; }`, NO `@media (prefers-color-scheme: dark)` overrides on chrome surfaces.
- **FR-80** Dark `<pre>` carve-outs (regen-prompt panel + markdown code blocks + code view): fixed dark palette, NOT OS-toggled. WCAG AA contrast verified.

### Make targets

- **FR-81** `Makefile` targets at project root: `install`, `install-backend`, `install-frontend`, `run-prod`, `run-backend`, `run-frontend`, `run` (alias for `run-backend`), `test-backend`, `test-frontend`, `e2e`, `boot-smoke`, `clean`. Same shapes as spec_driven Makefile (port verbatim).

### Tests

- **FR-82** Backend pytest under `backend/tests/`: unit + boundary tests against EXPOSED_TREE (port spec_driven test files for `repo_root`, `safe_resolve`, `exposed_tree`, `tree_walker`, `file_reader`, `file_writer`, `promotions`, `regen_prompt`, `api_security`); add new tests for `sub_type_lookup` + ai_video-specific regen-scope variants.
- **FR-83** Boot-smoke test: `make boot-smoke` runs a pytest that starts the backend, hits root + `/api/tree`, asserts 200 + expected shape.
- **FR-84** Frontend Vitest unit tests for `shotPairing`, `shotlistParser`, `linkResolver`.
- **FR-85** Playwright e2e suite at `frontend/e2e/`: at minimum (a) browse-to-shot-pair flow, (b) shotlist-table-row-click navigation, (c) image-ref view with both image-present and image-absent cases, (d) regen-prompt scope toggle for short and novel, (e) Origin/Host gate rejection at 8765.

## Non-functional requirements

- **NFR-1 — Tool / library version pinning.** Backend: Python ≥3.11 (per `str | None` syntax); FastAPI ≥0.110; uvicorn[standard]; pip-only (NO `uv` per CLAUDE.md project rules + spec_driven precedent). Frontend: React ^18, Vite ^5, react-resizable-panels ^4. All other versions inherit from spec_driven `package.json` and `requirements.txt`.
- **NFR-2 — Performance.** `GET /api/tree` returns within 200 ms for trees ≤500 files (current `wukong_juexing` is 17 files; budget is forward-looking). `/api/file` reads any allowed file ≤1 MiB within 50 ms. ShotPairView renders within 300 ms after both partner fetches resolve.
- **NFR-3 — Coexistence with spec_driven.** Both webapps can run simultaneously: spec_driven on 8765, ai_video_management on 8766. Their localStorage keys are namespaced (`spec_driven.*` vs `ai_video_management.*`). Neither imports from the other.
- **NFR-4 — Test parity with spec_driven.** Boot-smoke + unit + e2e all pass against single-process AND backend+frontend-separately modes (one Playwright profile per advertised mode, like spec_driven).
- **NFR-5 — Audit / observability.** No structured logging beyond stdout. The webapp does NOT emit `events.jsonl` — that's the agent_team pipeline's surface, not the webapp's. (The webapp surfaces existing `events.jsonl` content via `/api/file` reads only.)
- **NFR-6 — Bilingual content.** App chrome (sidebar labels, button labels, toolbar text) in English. File content (rendered markdown, prompts, descriptors) in Chinese — passed through unmodified by the webapp; CJK font stack applied. NO auto-translation.
- **NFR-7 — Cross-platform.** Backend runs on Windows 10/11 + macOS + Linux. File path handling uses `pathlib.PurePath` consistently. Tests parameterize over `os.sep`.

## Acceptance criteria summary

Full criteria belong to stage 5. High-level shape:

- **Level 1 — file presence.** All backend/libs/* + frontend/src/* + Makefile + README + tests files exist at expected paths (FR-1, FR-40, FR-41, FR-81, FR-82–85).
- **Level 2 — schema.** API endpoint request/response shapes match (FR-9, FR-10, FR-25, FR-27, FR-30, FR-31, FR-34, FR-35); TreeNode shape (FR-19); regen-prompt body assembly (FR-37–39).
- **Level 3 — security.** Origin/Host gate rejects 8765 + foreign origins with 403 (FR-11); path-traversal probes return 404 (FR-12); extension allowlist enforced on read + write (FR-13); 1 MiB body cap (FR-14); If-Unmodified-Since concurrency (FR-15); markdown sanitization strips raw HTML (FR-16); CSP header on responses (FR-17); image extensions rejected on PUT (FR-28).
- **Level 4 — UI behavior.** Shot-pair view dispatches on regex (FR-50–54); shotlist-table view dispatches and links rows (FR-55–58); image-ref view shows image when present and fallback when absent (FR-59–64); locked-block pill renders on `【...锁定描述符 vN】` blocks (FR-65–66); cross-tree link from ai_videos → specs renders (FR-78); sub-type badge renders correctly per `sub_type_lookup` result (FR-44); regen-scope selector gated on novel sub_type (FR-73).
- **Level 5 — manual walkthrough.** User runs both `make run-prod` and `make run-backend` + `make run-frontend` separately; verifies all 8 primary flows; confirms no console errors / no a11y warnings; visual confirmation of light theme + dark `<pre>` carve-outs.

## Stage-6 work-unit decomposition (preview — stage 5 may rebalance)

| Unit | Outputs | Depends on |
|---|---|---|
| **U1 — backend libs core** | `backend/libs/{repo_root, safe_resolve, exposed_tree, file_reader, file_writer, promotions, sub_type_lookup, stages}.py` + their tests | none (port-verbatim majority) |
| **U2 — backend tree + regen** | `backend/libs/{tree_walker, regen_prompt}.py` + their tests | U1 |
| **U3 — backend api + main + security** | `backend/libs/{api, api_security, main}.py` + `requirements.txt` + boot-smoke test | U1, U2 |
| **U4 — frontend scaffolding** | `frontend/{package.json, vite.config.ts, tsconfig.json, index.html}` + `src/{main.tsx, App.tsx, styles/app.css}` | none |
| **U5 — frontend ported components** | `src/components/{Sidebar, Reader, RegeneratePanel, Editor, BrokenLink, Breadcrumb}.tsx` + `src/markdown/*.tsx` + `src/helpers/{linkResolver, qaParser, autonomousMode}.ts` | U4 |
| **U6 — frontend new ai_video views** | `src/components/{ShotPairView, ShotlistTableView, ImageRefView}.tsx` + `src/helpers/{shotPairing, shotlistParser}.ts` + Vitest unit tests | U5 |
| **U7 — Makefile + README + e2e** | `Makefile`, `README.md`, `frontend/e2e/*.spec.ts` | U1–U6 |

Sequential dependency: U1 → U2 → U3 (backend); U4 → U5 → U6 (frontend); U7 last. U1+U4 can run in parallel.

## Open questions

None blocking v1. All 12 questions surfaced in the dossier are pre-resolved as judgment calls (see `findings/dossier.md` § Open questions surviving research).

Deferred to potential v2 follow-up:
- Storyboard horizontal-scroll view with `.png` thumbnails per shot.
- Render-API integration with Kling / Seedance / Seedream.
- Cross-publish manager + English-language publish translation.
- Compare-two-ai_videos-projects diff view.
- File-system watcher for auto-refresh.
- Reverse cross-tree link (specs → ai_videos).
- A "compare two shots side-by-side across projects" power-user view.
- User-toggleable theme picker.
