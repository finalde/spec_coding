# Findings dossier — ai_video_management

Run: ai_video_management-20260505-002710
Stage: 3 (research)
Researchers: 4 parallel angle workers, all returned

## Angles researched

1. **spec-driven-parallel-audit** — file-by-file inventory of `projects/spec_driven/` for port-verbatim vs port-with-adaptation vs new
2. **ai-video-render-mode-design** — concrete React patterns for ShotPairView / ShotlistTableView / ImageRefView + CJK rendering + locked-block pill
3. **regen-prompt-ai-video-semantics** — paste-ready prompt-body templates for ai_video stages 1–6 with scope axis (project / episode N / episodes M..N) and HTTP contract for `POST /api/regen-prompt`
4. **ai-video-tree-and-detection** — EXPOSED_TREE membership, TreeNode shape extension, sub_type regex from qa.md, sort + refresh semantics

## Cross-cutting insights

- **The actual spec_driven file naming is the source of truth, not my revised prompt's tentative naming.** R01 caught that my Stage-1 sketch named modules `server.py / tree.py / files.py / security.py / render_views.py` — but the actual `projects/spec_driven/backend/libs/` ships `api.py / tree_walker.py / file_reader.py / file_writer.py / api_security.py / safe_resolve.py / promotions.py / regen_prompt.py / repo_root.py / stages.py` (no `render_views.py` — view dispatch is purely client-side `extOf(path)` heuristics in `Reader.tsx`). **Stage 4 must adopt the actual names so port operations are mechanical.** *(spec-driven-parallel-audit)*

- **The vast majority of code ports verbatim with mechanical substitutions** (`8765` → `8766`, `spec_driven` → `ai_video_management`, `EXPOSED_TREE` membership). R01's inventory: backend libs `repo_root.py`, `file_reader.py`, `file_writer.py`, `promotions.py` and most tests are byte-identical; `safe_resolve.py`, `exposed_tree.py`, `tree_walker.py`, `regen_prompt.py`, `stages.py`, `api_security.py`, `main.py` need surgical changes only. Frontend: `Reader.tsx` gains 3 new view-dispatch arms; `Sidebar.tsx` gains a sub-type badge slot; `RegeneratePanel` gains a scope selector; everything else ports unchanged modulo a localStorage key rename. *(parallel-audit + tree-detection + regen-prompt)*

- **Three new components + helpers fully delineate the ai_video specialization.** New components: ShotPairView, ShotlistTableView, ImageRefView (all wrapped in `<ParseFallback>` per project error-boundary rule). Pure helpers: `shotPairing.ts` (regex `shot(\d+)_(kling|seedance)\.md` + partner resolution), `shotlistParser.ts` (parse pipe-table row → shot rows), and one backend helper `sub_type_lookup.py` (parse `qa.md` → `"novel" | "short" | None`, used to enrich ai_videos/{name}/ tree nodes with subtype in one round-trip). *(parallel-audit + render-mode-design + tree-detection)*

- **A single qa.md regex powers BOTH the sidebar badge AND the regen-scope toggle gating.** R04's regex `^\|\s*\`?sub_type\`?\s*\|\s*\`?(novel|short)\`?\s*\|` is anchored on the canonical settled-facts pipe-table row (verified against `wukong_juexing/interview/qa.md:10`). All edge cases — missing qa.md, missing row, typo value, multiple rows — collapse to `sub_type=None` (no badge, scope force-defaults to project), never crash. R03's regen-prompt scope toggle gates on the same value. **Single source of truth for sub_type.** *(tree-detection + regen-prompt)*

- **Image preview routes through the existing `/api/file` endpoint with no special handling.** R02 picks plain same-origin `<img src="/api/file?path=...&mtime=...">` (no blob URL indirection). The extension allowlist already covers `.png` / `.jpg` for read; image extensions are already excluded from `PUT /api/file` per spec_driven precedent + revised hard constraint #4. The mtime query string busts the browser cache when the user re-renders the立绘. CSP requires `img-src 'self'`. *(render-mode-design + parallel-audit)*

- **Stages 1–5 regen-prompt body is byte-identical to spec_driven** (modulo `project_type=ai_video` and an optional `sub_type` line). R03 explicitly says: copy `_READ_ZERO_CONTRACT` and `_AUTONOMOUS_IMPERATIVE` constants from `projects/spec_driven/backend/libs/regen_prompt.py` rather than re-paraphrase — drift between webapps' regen contracts would defeat the read-zero workflow. **Stage 6 is the only delta surface** with 4 variants (`short × project`, `novel × {project, episode N, episodes M..N}`). *(regen-prompt + parallel-audit)*

## Per-angle highlights

### spec-driven-parallel-audit (R01)

- **Backend module names (actual, not from revised prompt):** `repo_root.py`, `file_reader.py`, `file_writer.py`, `promotions.py`, `safe_resolve.py`, `exposed_tree.py`, `tree_walker.py`, `regen_prompt.py`, `stages.py`, `api_security.py`, `api.py`, `main.py`. **No** `render_views.py` (view dispatch is client-side).
- **Frontend structure:** `App.tsx`, `Sidebar.tsx`, `Reader.tsx`, `RegeneratePanel.tsx`, `Editor.tsx`, `BrokenLink.tsx`, `Breadcrumb.tsx`, `markdown/{QaView, JsonlView, CodeView, ParseFallback, QaErrorBoundary, MarkdownView, ImagePlaceholder}.tsx`, helpers `linkResolver.ts`, `qaParser.ts`, `autonomousMode.ts`. **No** `components/views/` subfolder; views split between `components/` and `markdown/`.
- **Surgical changes for port-with-adaptation files:**
  - `exposed_tree.py:65-92` `is_inside` predicate: drop `projects` from allowed-top-level set, add `ai_videos`; tighten `specs/**` to `specs/ai_video/**`.
  - `tree_walker.py`: add a third tree section "AI Videos" (currently has "Specs" + "Context"); enrich `ai_videos/{name}/` directory nodes with `project_meta` from `sub_type_lookup`.
  - `regen_prompt.py`: add `scope=episode|episodes M..N` body field handling; honor `agent_refs/project/ai_video.md` rule 10 delete contracts; reuse `_READ_ZERO_CONTRACT` constant verbatim.
  - `stages.py`: add ai_video stage definitions (mostly the same 6 stages but stage-6 outputs to `ai_videos/{name}/`, not `projects/{name}/`).
  - `api_security.py`: swap port `8765` → `8766` in test fixtures.
  - `main.py`: bind port `8766`.
  - `Reader.tsx`: add 3 view-dispatch arms — `ShotPairView` (when `path matches /prompts/shot\d+_(kling|seedance)\.md/`), `ShotlistTableView` (when `path ends with /shotlist.md and is under ai_videos/`), `ImageRefView` (when `path matches /ref_images/.*_seedream\.md/` OR `path ends with .png|.jpg`).
  - `Sidebar.tsx`: render sub-type badge from `node.project_meta.sub_type` if present.
  - `RegeneratePanel.tsx`: add scope selector; gate `scope=episode|episodes M..N` options on `sub_type === "novel"`.
- **Open questions:** sidebar label language (`AI Videos` English or `AI 视频` Chinese?); sub-type badge fallback text; ShotPairView fall-through for non-pair files in `prompts/`; shotlist column schema lock; image-refresh semantics; single-endpoint vs enriched-tree for sub-type lookup; scope-prompt expansion for `episodes M..N`; EXPOSED_TREE membership of `agent_refs/project/development.md`.

### ai-video-render-mode-design (R02)

- **Split-pane primitive: `react-resizable-panels` v4** (the same library shadcn/ui wraps). Adopted for both ShotPairView + ImageRefView. Buys WAI-ARIA `role="separator"` + keyboard resize for free; persist split position via library-native `autoSaveId`.
- **ShotlistTableView mechanism:** keep standard `react-markdown` + `remark-gfm` + `rehype-sanitize` pipeline; **override `components.td`** to regex-match the shot id on the first cell and replace it with a `<button>` that calls `useNavigate` (programmatic nav avoids invalid `<a>`-inside-`<tr>` and keeps the `.md` source URL-agnostic).
- **Image preview: plain same-origin `<img src="/api/file?path=...&mtime=...">`** — no blob-URL indirection. CSP needs `img-src 'self'`. Mtime query string busts browser cache.
- **Locked-block pill: pre-render regex pass** on the markdown source wrapping `【...锁定描述符...】` blocks in a `<span class="locked-block">`. Not a remark plugin (simpler).
- **CJK rendering:** `lang="zh-Hans"` on the render container + system font stack + `word-break: normal` per qa.md lock.
- **Copy-to-clipboard:** `navigator.clipboard.writeText` plus a single app-root `aria-live="polite"` region for "已复制" toast.
- **10 FR seeds delivered:** FR-views-v1, FR-split-pane-lib, FR-shotlist-link-mechanism, FR-image-fetch-mode, FR-locked-block-pill, FR-cjk-rendering, FR-copy-button, FR-shot-pair-fallback, FR-image-ref-fallback, FR-image-readonly.
- **Open questions:** lock the AI-video shotlist-row layout convention so the regex stays stable; pin the URL scheme `?file=...&view=shot-pair` so deep links survive reload.

### regen-prompt-ai-video-semantics (R03)

- **Stages 1–5 prompt body byte-identical to spec_driven** (modulo `project_type=ai_video` + optional `sub_type` line). New `regen_prompt.py` should COPY `_READ_ZERO_CONTRACT` + `_AUTONOMOUS_IMPERATIVE` constants from spec_driven, not re-paraphrase. Drift between webapps' regen contracts would defeat the read-zero workflow.
- **Stage 6 is the only delta surface, with 4 variants:** `short × project`, `novel × project`, `novel × episode N`, `novel × episodes M..N`. The `scope` axis drives a sub_type-aware `Folder` declaration + a strictly-scoped delete contract:
  - `episode N`: delete only `ai_videos/{name}/episodes/ep{NN}/`, preserve `characters/`, `world.md`, `style_guide.md`, `arc_outline.md`, sibling episodes — and forbid edits to those preserved paths during regen, halting with `pipeline.halted` on conflict.
- **Sub_type read from `specs/ai_video/{name}/interview/qa.md`** per qa.md Regen-scope-UI Q2 answer A; missing/unparseable → 409.
- **HTTP contract:** `POST /api/regen-prompt` extends spec_driven's `RegenPromptBody` with `scope` (default `"project"`), `scope_episode: int` (required iff `scope="episode"`), `scope_episode_range: {start, end}` (required iff `scope="episodes"`). Response adds `scope` + `scope_resolved` echoes. 4xx surface: 400 bad scope/wrong project_type, 409 sub_type unknown, 413 oversized (1 MiB hard, 50 KiB soft warning — same constants as spec_driven).
- **Open questions:** reject `scope=episode` on development projects with 400 (strict)? Cap upper bound on `episodes M..N`? (R03 recommendation: do NOT cap — regen is what creates beyond-batch-size episodes in the first place.)

### ai-video-tree-and-detection (R04)

- **EXPOSED_TREE membership locked to 4 roots:**
  1. `ai_videos/**/*.{md,json,jsonl,yaml,yml,txt,png,jpg}`
  2. `specs/ai_video/**/*.{md,json,jsonl,yaml,yml,txt}`
  3. `CLAUDE.md`
  4. `.claude/{skills/agent_team/{SKILL.md, playbooks/*.md}, agent_refs/**/*.md}`
- **Three sidebar sections in fixed order:** AI Videos, Specs (ai_video), Context.
- **TreeNode shape extends spec_driven's by exactly two things:**
  - Optional `project_meta: {sub_type: "novel" | "short" | None, shot_count: int | None, episode_count: int | None}` populated only on `ai_videos/{name}/` directory nodes.
  - New `type: "image"` leaf for `.png` / `.jpg` so the sidebar can render an icon and the Reader can route to ImageRefView without each component re-checking suffixes.
- **Sub_type detection regex:** `^\|\s*\`?sub_type\`?\s*\|\s*\`?(novel|short)\`?\s*\|` (multiline). Verified against `wukong_juexing/interview/qa.md:10`. All 4 edge cases — qa.md missing, no sub_type row, typo value, multiple rows — collapse to `sub_type=None` (no badge, scope force-defaults to project), never crash, never invent a third value.
- **"查看规格" link** maps to project root (`specs/ai_video/{name}/`), not per-file mirror — chosen for simplicity since the user can navigate within the spec tree from the root landing.
- **Sort order:** alphabetical (dirs first), ported verbatim from `tree_walker.py:105`.
- **Refresh semantics:** manual button + auto-bump on `PUT /api/file` success per `App.tsx:13-31`. No fs-watcher.

## Recommendations for the spec (stage 4 must honor)

1. **Adopt actual spec_driven module names** — backend libs land at `backend/libs/{api, api_security, exposed_tree, file_reader, file_writer, main, promotions, regen_prompt, repo_root, safe_resolve, stages, sub_type_lookup, tree_walker}.py`. **No** `render_views.py`. Stage 4 spec FRs reference these names.

2. **Add `react-resizable-panels` v4 to frontend dependencies.** Used by both ShotPairView and ImageRefView. WAI-ARIA + autoSaveId for free.

3. **Lock the 4 EXPOSED_TREE roots** per R04 §3.

4. **Lock TreeNode extension** — `project_meta` field on `ai_videos/{name}/` dir nodes; `type: "image"` for `.png/.jpg` leaves.

5. **Lock regen-prompt HTTP contract additions:**
   - `scope`: `"project" | "episode" | "episodes"` (default `"project"`)
   - `scope_episode`: int (required iff `scope="episode"`)
   - `scope_episode_range`: `{start: int, end: int}` (required iff `scope="episodes"`, `start ≤ end`)
   - `project_type`: `"ai_video"` (vs `spec_driven`'s `"development"`)
   - Response: existing schema + `scope` + `scope_resolved` echoes.
   - 4xx: 400 bad scope, 409 sub_type unknown when scope ≠ project, 413 oversized.

6. **Lock sub_type detection regex** — `^\|\s*\`?sub_type\`?\s*\|\s*\`?(novel|short)\`?\s*\|` (multiline). Implement once in `sub_type_lookup.py`; consume from both `tree_walker.py` (sidebar badge) and `regen_prompt.py` (scope toggle gating).

7. **Lock locked-block pre-render regex** — wrap `【孙悟空 · 觉醒态 · 锁定描述符 v[0-9]+】 ... 禁用 卡通线条、cel-shading、二次元大眼、低多边形。` (and analogous patterns for other characters) in `<span class="locked-block">`. **Generalize the regex** beyond Wukong: the sentinel format is `【{character} · {state} · 锁定描述符 v{n}】 ... {end-sentinel}`. Stage 4 should pin a more general regex pattern.

8. **Lock URL scheme for deep links:** `?file={path}&view={view-mode}` where view-mode is one of `markdown` (default) | `shot-pair` | `shotlist-table` | `image-ref` | `qa` | `jsonl` | `code`. Default = inferred from path; `view=` overrides.

9. **CJK rendering:** `lang="zh-Hans"` on the markdown render container; `word-break: normal`; system font stack `-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif`.

10. **Image preview implementation:** `<img src="/api/file?path={enc}&mtime={mtime}">` with mtime query-string cache-buster. CSP `img-src 'self'`. Image extensions `.png/.jpg` are read-only via `/api/file` (already in extension allowlist for read; not in writeable list). The mtime is taken from the tree node — no separate stat call needed.

11. **Reuse `_READ_ZERO_CONTRACT` and `_AUTONOMOUS_IMPERATIVE` constants from `projects/spec_driven/backend/libs/regen_prompt.py`** — copy bytes, do NOT paraphrase. Stage 6 implementation note: this is a literal `cp` of those constants into the new file.

12. **localStorage key rename** — `spec_driven.autonomous_mode.v1` → `ai_video_management.autonomous_mode.v1` to keep state separate when both webapps coexist (port 8765 + 8766).

## Open questions surviving research (deferred to stage 4)

| # | Question | Surfaced by | Stage 4 path |
|---|---|---|---|
| Q1 | Sidebar label: `AI Videos` English vs `AI 视频` Chinese? | parallel-audit | **judgment call: `AI Videos` English** — matches sidebar's other section labels (`Specs`, `Context`), keeps app chrome bilingual-neutral, file content stays Chinese. |
| Q2 | Sub-type badge fallback text when `sub_type=None`? | parallel-audit | **judgment call: no badge at all** (consistent with R04's "never invent a third value" + clean visual). |
| Q3 | ShotPairView fall-through for non-pair `prompts/` files (e.g., a future `prompts/shared_lighting.md`)? | parallel-audit | **judgment call: fall through to MarkdownView**. The pair-detection regex is strict (`shot(\d+)_(kling|seedance)\.md`); anything not matching just renders as markdown. |
| Q4 | Shotlist column schema lock — does the shot id always live in column 1? | parallel-audit + render-design | Confirmed by reading `wukong_juexing/shotlist.md`: column 1 = shot id (`shot01` etc.). Lock as FR; future shotlists must conform. |
| Q5 | Image-refresh semantics — does the webapp poll for new `.png` files? | parallel-audit + render-design | **judgment call: no polling**. User clicks "刷新" button (existing pattern from spec_driven). The mtime cache-buster handles re-render after manual refresh. |
| Q6 | Single-endpoint `/api/sub-type/{name}` vs enriched tree response for sub-type lookup? | parallel-audit | **judgment call: enriched tree response**. R04 already specs this via `project_meta` on tree node. One round-trip is faster than per-project polling. |
| Q7 | Scope-prompt expansion for `episodes M..N` — explicit episode list or just M..N notation in the prompt body? | parallel-audit + regen-prompt | **judgment call: explicit episode list** — the regen prompt itself names each episode folder being deleted (e.g., `ai_videos/{name}/episodes/ep05/`, `ep06/`, `ep07/`) so the receiving Claude Code instance has zero ambiguity. |
| Q8 | EXPOSED_TREE membership of `agent_refs/project/development.md` (only relevant to spec_driven) — include or exclude? | parallel-audit | **judgment call: include via the wildcard `.claude/agent_refs/**/*.md`**. Cheap; keeps the context section self-explaining; user can read why ai_video webapp itself follows light-theme rules. |
| Q9 | Reject `scope=episode` on development projects with 400? | regen-prompt | **judgment call: yes, 400**. Strict — the webapp only manages ai_video projects, so `scope=episode` requests on `project_type ≠ "ai_video"` are programming errors. |
| Q10 | Cap upper bound on `episodes M..N`? | regen-prompt | **judgment call: no cap**. R03's recommendation — regen is what creates beyond-batch-size episodes in the first place. |
| Q11 | Locked-block pill regex generality — Wukong-specific or generalized? | render-design | **judgment call: generalize**. Pattern: `【.+ · .+ · 锁定描述符 v\d+】[\s\S]*?禁用[\s\S]*?。`. Future projects with other characters get pill rendering for free. |
| Q12 | Deep-link URL scheme — `?file=...&view=...` vs path-based? | render-design | **judgment call: query-string `?file=...&view=...`**. Matches spec_driven precedent (already query-string-based). |

All 12 questions are pre-resolved as judgment calls so stage 4 doesn't have to re-derive. Each is documented with a one-line rationale that an interactive run can revise.
