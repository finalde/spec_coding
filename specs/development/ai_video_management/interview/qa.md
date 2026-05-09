# Interview — ai_video_management

Run: ai_video_management-20260505-002710
Mode: AUTONOMOUS (user explicit: "please continue to next stage" — read as continuation in same autonomous flow as wukong_juexing run)
Shape: A (parent-direct, single-pass — no fan-out workers; categories tight enough)

## Settled facts (no probe — locked by `revised_prompt.md` or precedent)

| Field | Value | Source |
|---|---|---|
| `task_type` | `development` | revised prompt |
| Backend stack | FastAPI + Python 3 + strong-typed `@dataclass(frozen=True)` containers | revised hard constraint #9; `spec_driven` precedent |
| Frontend stack | React + TypeScript + Vite | revised hard constraint #10; `spec_driven` precedent |
| Bound port | **8766** (parallels spec_driven 8765, allows simultaneous run during dev) | revised soft target → locked |
| Bind address | `127.0.0.1` IPv4 loopback only | revised hard constraint #1 |
| Mutation endpoints | 4 (`PUT /api/file`, `POST /api/regen-prompt`, `POST /api/promote`, `DELETE /api/promote`) | revised hard constraint #5 |
| Origin / Host gate | port-strict, loopback aliases admit | revised hard constraint #2 |
| EXPOSED_TREE membership | `ai_videos/**`, `specs/ai_video/**`, `CLAUDE.md`, agent_team SKILL + playbooks, agent_refs/{interview,research,validation,project}/{general,ai_video,development}.md | revised hard constraint #12 |
| Extension allowlist | `.md`, `.json`, `.yaml`, `.yml`, `.jsonl`, `.txt`, `.png`, `.jpg` (SVG NOT) | revised hard constraint #4 |
| Concurrency | RFC 7232 `If-Unmodified-Since` mtime → 409 stale | revised hard constraint #6 |
| Markdown sanitization | `rehype-sanitize` default schema | revised hard constraint #7 |
| Pinning | `<stage>/promoted.md` sidecar at interview / findings / final_specs / validation; stage 6 carved out per `ai_video.md` rule 10 + `validation/ai_video.md` move #7 | revised soft target → locked from `spec_driven` precedent |
| Mode toggle | INTERACTIVE / AUTONOMOUS, default INTERACTIVE | revised soft target → locked from `spec_driven` precedent |
| Theme | light chrome, dark `<pre>` carve-outs | `agent_refs/project/development.md` rule 1 |
| Make targets | `install`, `install-backend`, `install-frontend`, `run-prod`, `run-backend`, `run-frontend`, `run`, `test-backend`, `test-frontend`, `e2e`, `boot-smoke`, `clean` | revised hard constraint #11 |
| CJK font stack | system fallback (`-apple-system`, `BlinkMacSystemFont`, `PingFang SC`, `Microsoft YaHei`, `Noto Sans CJK SC`, sans-serif) | revised soft target → locked (no bundled webfont; instant render, smaller bundle) |
| Co-existence with `spec_driven` | simultaneous run, different port (8766 vs 8765), independent processes | revised soft target → locked |
| 3 nav roots in sidebar | `ai_videos/`, `specs/ai_video/`, `context/` (= `CLAUDE.md` + `.claude/...`) | revised soft target → locked |
| Render-API integration | OUT (v2) | revised out-of-scope #1 |
| Storyboard horizontal-scroll view | OUT (v2) | revised out-of-scope #6 |

## Categories probed

- **V1 view-mode scope** — exact set of custom views beyond MarkdownView; what ships in v1 vs deferred.
- **Shot-pair detection rule** — how the webapp identifies + renders the Kling/Seedance pair; behavior on navigation; partial-match handling.
- **Image preview model** — how `.png` files alongside Seedream prompts surface; refresh semantics; missing-image fallback.
- **Regen-scope UI for ai_video** — how to surface novel-only `scope=episode N` toggle when current data is short-only; whether to ship the UI now or wait until first novel exists.
- **Sidebar organisation** — three nav roots locked above, but how should each root be presented; what about cross-task-type traversal (e.g., ai_video projects also have a counterpart spec dir).

---

## Round 1

### V1 view-mode scope

**Q1:** Beyond `MarkdownView`, which custom view modes ship in v1?

- A: ShotPairView + ShotlistTableView + ImageRefView (3 new) **(Recommended)**
- B: ShotPairView only — defer table + image preview to v2
- C: All 3 from option A + minimal Storyboard view (5 thumbnails in row, no `.png` integration; just `[shot01]` placeholders)
- D: All 3 + Storyboard view + Render-API stub (placeholder for v2 render integration)

**A** *(judgment call — chose A because: revised prompt's success-checklist points 2/3/4 explicitly cover ShotPairView, ImageRefView, and ShotlistTableView; Storyboard view depends on `.png` thumbnails not yet generated for any project; Render-API stub adds half-implemented surface area. Binds into FR-views-v1.)*

**Q2:** What does `MarkdownView` show for files inside `ai_videos/{name}/` that contain Chinese content + hex codes + locked-descriptor blocks?

- A: Standard markdown render with `rehype-sanitize`; hex codes inside backticks render as inline-code; locked-descriptor block (sentinel-bracketed) gets a subtle "锁定块" pill in the corner **(Recommended)**
- B: Plain markdown only — no special treatment of locked blocks or hex
- C: Standard render + per-hex-code color swatch (a tiny colored square next to each `#XXXXXX`)

**A** *(judgment call — chose A because: locked-descriptor "锁定块" pill creates visual affordance for the byte-equality contract (FR-12/13 of wukong project); option C is nice but adds rendering complexity for low ROI in v1; revised prompt's ShotPairView already exposes the descriptor via the side-by-side render. Binds into FR-markdown-render.)*

**Q3:** Should `MarkdownView` render Chinese content with text-direction-sensitive line wrapping (e.g., breaking at CJK boundaries vs whitespace)?

- A: Default browser CJK wrapping (`word-break: normal`) **(Recommended)**
- B: `word-break: break-all` — break anywhere (avoids long-line overflow but ugly for prose)
- C: `word-break: keep-all` + `overflow-wrap: anywhere` — keep CJK words whole, only break at whitespace + emergency overflow

**A** *(judgment call — chose A because: revised prompt expects clean Chinese rendering (note about PingFang/Noto Sans CJK fallback); browser default works well for CJK in markdown contexts; option B looks bad for prose; option C is more conservative but adds CSS complexity. Binds into FR-markdown-render.)*

### Shot-pair detection rule

**Q1:** What pattern triggers ShotPairView when the user clicks a single shot file?

- A: Filename pattern `shot(\d+)_(kling|seedance)\.md` — clicking either auto-loads the partner; renders side-by-side **(Recommended)**
- B: Folder pattern `prompts/` — any `*.md` inside `prompts/` triggers pair detection by stripping the `_kling`/`_seedance` suffix
- C: Manual toggle — user clicks a "View as pair" button on each shot file individually

**A** *(judgment call — chose A because: regex is unambiguous and matches the `agent_refs/project/ai_video.md` rule 4 schema (every shot ships dual prompts); option C creates UX friction; option B is too loose (would match any `prompts/*.md`, including hypothetical future variants). Binds into FR-shot-pair-detection.)*

**Q2:** When the partner file does NOT exist (e.g., user renamed `shot02_seedance.md` → `shot02_seedance_v2.md`), what does ShotPairView do?

- A: Render the clicked file in single-pane mode (left only) + a yellow banner "缺少配对文件: prompts/shot02_seedance.md" with a link to the partner's expected path **(Recommended)**
- B: Hard error: refuse to render, show "ShotPairView requires both files; falling back to MarkdownView"
- C: Render single-pane silently — no warning

**A** *(judgment call — chose A because: silent failure (option C) hides drift; hard error (option B) breaks user flow; banner-with-link gives actionable feedback while staying functional. Binds into FR-shot-pair-fallback.)*

**Q3:** Should ShotPairView's two panes be horizontally scrollable independently or scroll-synced?

- A: Independently scrollable (each pane has its own scrollbar) **(Recommended)**
- B: Scroll-synced (scrolling left pane scrolls right pane proportionally; useful for diff-style compare)
- C: Scroll-synced with toggle switch (default: synced; user can toggle to independent)

**A** *(judgment call — chose A because: Kling and Seedance prompts have different lengths (Kling has `[参考图: ...]` + `negative_prompt:`; Seedance has `约束:` + per-second timeline); proportional sync gets ugly fast; user typically reads one pane then jumps to the other, not line-by-line compare. Option C is over-engineering for v1. Binds into FR-shot-pair-layout.)*

### Image preview model

**Q1:** When the user clicks `characters/ref_images/main_seedream.md`, the prompt itself is markdown. If `main_seedream.png` exists in the same folder, where does it render?

- A: Inline alongside the prompt (left pane: prompt markdown; right pane: image), like ShotPairView **(Recommended)**
- B: Above the prompt, full-width thumbnail
- C: Below the prompt, full-width thumbnail
- D: Hidden behind a "Show generated立绘" button (default collapsed)

**A** *(judgment call — chose A because: side-by-side mirrors ShotPairView UX (consistency); `agent_refs/project/ai_video.md` rule 4 explicitly calls out the prompt → image lock as the load-bearing pipeline contract — co-locating them visually reinforces the contract; A also lets the user copy the prompt while looking at the image. Binds into FR-image-ref-layout.)*

**Q2:** When `main_seedream.png` does NOT exist (user hasn't run Seedream yet), what does ImageRefView show in the right pane?

- A: A placeholder with the text "尚未生成立绘 — 复制左侧 prompt 至 Seedream 后保存为 main_seedream.png 并刷新" **(Recommended)**
- B: Hide the right pane; render the prompt full-width
- C: Show the placeholder + a "Refresh" button that re-checks the folder

**A** *(judgment call — chose A because: placeholder text doubles as in-context instructions to the user (matches the README's usage steps for wukong_juexing); option B loses the affordance that an image is expected; option C adds a button but the user can already F5 the page or click the file again. Binds into FR-image-ref-fallback.)*

**Q3:** Are `.png` files writeable through `PUT /api/file`?

- A: NO — `.png` is read-only; user drops files into the folder via OS file system **(Recommended)**
- B: YES — `PUT /api/file` accepts `.png` body; user can paste image data through the webapp

**A** *(judgment call — chose A because: revised hard constraint #4 says "Image extensions are not writable" verbatim; `spec_driven` precedent; binary upload through the 4-mutation surface would also break the body-content contract. Binds into FR-image-readonly.)*

### Regen-scope UI for ai_video

**Q1:** The `scope=episode N` toggle is novel-only. Currently the only ai_video project (`wukong_juexing`) is a short. Do we ship the scope toggle UI in v1?

- A: Ship the toggle behind a `sub_type === 'novel'` gate — for shorts, the toggle is hidden and `scope=project` is the only behavior **(Recommended)**
- B: Defer the entire toggle to v2 — for v1, every ai_video regen prompt uses `scope=project` regardless
- C: Ship the toggle visible always — for shorts, only `scope=project` is enabled (other options greyed out)

**A** *(judgment call — chose A because: building the UI now while the contract is fresh (post-wukong_juexing run) avoids cold-start pain when the first novel arrives; gating on `sub_type` keeps the UX clean for short users (no greyed-out options to puzzle over); option C confuses short users with non-applicable choices; option B creates a v2 cost spike. Binds into FR-regen-scope-toggle.)*

**Q2:** How does the webapp determine `sub_type` for an ai_video project?

- A: Read `specs/ai_video/{name}/interview/qa.md` — look for `sub_type ∈ {novel, short}` token in the settled-facts table **(Recommended)**
- B: Heuristic — if `ai_videos/{name}/episodes/` exists, novel; else short
- C: Read `specs/ai_video/{name}/final_specs/spec.md` — parse for `sub_type` declaration

**A** *(judgment call — chose A because: `agent_refs/interview/ai_video.md` rule 1 explicitly says `sub_type` is captured in `qa.md` metadata as authoritative; option B is brittle (a novel with no episodes generated yet would misdetect); option C requires Stage 4 to have run, which not every project will have completed. Binds into FR-subtype-detection.)*

**Q3:** For novel scope=`episodes M..N`, how does the user input the range?

- A: Two number inputs (M, N) with validation `1 ≤ M ≤ N` **(Recommended)**
- B: A single text input parsing strings like `"5..8"` or `"5,6,7,8"` (comma-separated)
- C: A multi-select listbox showing all available episode numbers

**A** *(judgment call — chose A because: simpler input widget, validation is trivial; option B requires parser + error UI; option C requires the webapp to know which episodes exist (extra API call) and the listbox grows past 60 items unmanageably. Binds into FR-regen-episode-range.)*

### Sidebar organisation

**Q1:** The 3 nav roots (`ai_videos/`, `specs/ai_video/`, `context/`) — how are they ordered top-to-bottom?

- A: `ai_videos/` first (the main artifact tree), then `specs/ai_video/` (workflow audit), then `context/` (`CLAUDE.md` + `.claude/...`) **(Recommended)**
- B: `specs/ai_video/` first (the spec-pipeline trail leads), then `ai_videos/` (output tree), then `context/`
- C: `context/` first (always-on reference), then `ai_videos/`, then `specs/ai_video/`

**A** *(judgment call — chose A because: revised prompt's primary success scenarios (#1, #2, #3, #4) all start in `ai_videos/`; the spec trail is the audit / what-led-to-this surface, accessed less often; context is reference material, appropriate as the bottom anchor. Binds into FR-sidebar-order.)*

**Q2:** When the user is viewing a file under `ai_videos/wukong_juexing/...`, should the sidebar offer a "jump to spec counterpart" affordance (linking to `specs/ai_video/wukong_juexing/...`)?

- A: YES — show a "查看规格" link at the top of every file viewer when a counterpart project exists in `specs/ai_video/{name}/` **(Recommended)**
- B: NO — user navigates manually via the sidebar (cleaner, no link maintenance)
- C: YES + reverse direction (when viewing a `specs/ai_video/` file, link to `ai_videos/` counterpart)

**A** *(judgment call — chose A (without the reverse direction in v1) because: the most common cross-link is "I'm looking at a generated artifact and want to know why" → spec direction; the reverse (looking at a spec and wanting to see the output) is less load-bearing per `spec_driven` usage data; option C is a v2 enhancement. Binds into FR-cross-tree-link.)*

**Q3:** Sidebar entries for `ai_videos/{name}/`: do we surface the project's `sub_type` as a visual badge?

- A: YES — render a small "短" or "剧" badge next to the project name in the sidebar **(Recommended)**
- B: NO — keep sidebar entries plain text
- C: YES + add a count badge for shots (e.g., "短 · 5 镜")

**A** *(judgment call — chose A because: at-a-glance differentiation matters once 3+ projects exist; option C requires parsing shotlist.md per-project on every tree request (expensive); the simple sub_type badge requires only one `qa.md` read per project per refresh and is cacheable. Binds into FR-project-badges.)*

---

## Round 2

Not run. All 5 categories clear after one autonomous round — each question has a locked answer with cited rationale. No internal contradictions detected; no follow-up ambiguity that the spec stage couldn't resolve from the dossier.

## Cross-cutting reminders for stage 3 / 4

- The webapp targets BOTH `ai_videos/{name}/` (output tree) AND `specs/ai_video/{name}/` (workflow trail) — Stage 4's FR set must cover both navigation paths.
- Pinning sidecar paths under `specs/ai_video/{name}/<stage>/promoted.md` are identical to `spec_driven`'s; reuse the parser.
- Regen-prompt assembly must respect the ai_video-specific delete-then-regenerate table from `CLAUDE.md` § Regeneration semantics, including `<stage>/promoted.md` preservation.
- The webapp does NOT auto-trigger any regeneration — it only emits copy-paste prompts (same as `spec_driven`).
- v2 follow-up candidates already accumulated: render-API integration, storyboard view, cross-publish manager, English translation, project-diff view, file create/delete/upload, dark-mode toggle.

## Team consensus

All 5 probed categories marked clear after **1 autonomous round**. Stage 3 (research) inputs are fully specified.
