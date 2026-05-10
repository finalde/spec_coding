# Revised prompt — ai_video_management

**task_type:** development
**task_name:** ai_video_management
**Composed from:** `raw_prompt.md` + `follow_ups/001-20260505-121536-ai-videos-only-scope.md` + `follow_ups/002-20260505-130548-zero-claude-coupling.md` + `follow_ups/003-20260509-152135-research-folder-and-viewer.md` + `follow_ups/004-20260509-194837-allow-chinese-filenames.md` + `follow_ups/005-20260510-161839-media-display-playback.md` + `follow_ups/006-20260510-164054-stale-runtime-instructions.md` + `follow_ups/007-20260510-170438-rename-media-to-parent-folder.md` + `follow_ups/008-20260510-201826-archive-unarchive-media.md`

**Last regenerated:** 2026-05-10 20:18:26 — header bump for follow-up 008（per-file archive / unarchive media — SiblingMedia tile 上 inline button 把单个 image/video 移动到同 folder 下的 `archive/` 子目录，反向亦可；后端两个新 endpoint `POST /api/archive-media` + `POST /api/unarchive-media`；archive/ 在 tree sidebar 作为常规 folder 显示；unarchive 后若 archive/ 空则自动 rmdir；rename-media batch 规则不变（archive/ 内文件也参与 rename））。

**Prior follow-up 007:** 2026-05-10 17:04:38 — drama-level rename-media 按钮 + `POST /api/rename-media`（保持有效）。

**Prior follow-up 006:** 2026-05-10 16:40:54 — runtime reload procedure documentation（保持有效 — 仅 documentation）。

**Prior follow-up 005:** 2026-05-10 16:18:39 — media display + playback (backend `/api/media` route + frontend Reader video/image rendering + SiblingMedia gallery)（保持有效）。

**Prior follow-up 004:** 2026-05-09 19:48:37 — 中文 filename opt-in（保持有效）。
**Prior follow-up 003:** 2026-05-09 15:21:35 — research/ folder + viewer（保持有效）。

## Goal

Build a focused viewer / editor SPA + FastAPI backend at `projects/ai_video_management/` for the artifacts under `ai_videos/{name}/` — character bibles, Seedream立绘 prompts, style guides, scripts, shotlists, dual Kling+Seedance shot prompts, publish metadata, README. The webapp ships three custom view modes that make the ai_video output structure navigable: **ShotPairView** (Kling + Seedance side-by-side), **ShotlistTableView** (clickable shot-row navigation), and **ImageRefView** (Seedream prompt + companion `.png` preview). It reuses spec_driven's security posture (Origin/Host gate, EXPOSED_TREE sandbox, RFC 7232 mtime concurrency, IPv4 loopback, light theme, CSP) but targets a single tree root: `ai_videos/`. Bound port: **8766** (parallels spec_driven's 8765 for simultaneous run).

**Per follow-up 001 + 002:** the webapp does not load, read, reference, or anchor on `specs/`, the workspace `CLAUDE.md`, or `.claude/` — at any layer. Source files contain zero references to those paths. Regen-prompt and pinning features are out of scope; users who need to drive an ai_video pipeline run regen prompts through a separate webapp dedicated to that purpose. `RepoRoot.find()` anchors on `ai_videos/` directory presence, the only path this webapp cares about.

## Context

- **Why a focused tool:** the existing `spec_driven` webapp already manages the spec pipeline (intake, interview, findings, final_specs, validation, regen prompts, pinning) for both `development` and `ai_video` task types. The user wants a complementary tool that opens directly into the *output* tree of ai_video projects, without forcing them through the spec-pipeline navigation chrome. Division of concern: spec_driven for the pipeline; ai_video_management for the artifacts.
- **Why a parallel of spec_driven structurally:** the security posture (Origin/Host gate, sandbox, traversal hardening, mtime concurrency, IPv4 loopback only, light-theme chrome, extension allowlist, CSP) is battle-tested. Reusing it verbatim is the right call. The render-mode dispatch + sidebar pattern also ports — it's just the EXPOSED_TREE membership and the stage-pipeline features that change.
- **What's specific to ai_video output:** the `prompts/shot{NN}_{kling|seedance}.md` paired-file pattern, the `shotlist.md` table that needs row-click navigation, the `characters/ref_images/{role}_seedream.md` + companion `.png` preview, and the locked-descriptor block sentinel that should render with a "锁定块" pill. These four cases drive the three new view modes plus the locked-block pill in MarkdownView.

## Desired outcome

A `projects/ai_video_management/` folder following the same structural conventions as `projects/spec_driven/`, but functionally narrowed to ai_videos/:

```
projects/ai_video_management/
├── README.md
├── Makefile                       # install / install-* / run-prod / run-backend / run-frontend / run / test-* / e2e / boot-smoke / clean
├── backend/
│   ├── main.py                    # ~15 lines — argparse + create_app + uvicorn
│   ├── requirements.txt
│   ├── libs/
│   │   ├── repo_root.py           # find CLAUDE.md + .claude/ to anchor (NOT exposed)
│   │   ├── safe_resolve.py        # path traversal hardening; allowed top-level = {"ai_videos"}
│   │   ├── exposed_tree.py        # is_inside admits ONLY ai_videos/**
│   │   ├── file_reader.py         # GET /api/file: text + image (.png/.jpg) routes
│   │   ├── file_writer.py         # PUT /api/file: text only, If-Unmodified-Since required
│   │   ├── tree_walker.py         # single-section "AI Videos" tree
│   │   ├── sub_type_lookup.py     # heuristic: episodes/ exists → novel, else → short
│   │   ├── api_security.py        # Origin/Host gate + CSP middleware
│   │   ├── api.py                 # 2 endpoints only: GET /api/tree, GET/PUT /api/file
│   │   └── __init__.py
│   ├── static/                    # bundled SPA for single-process mode
│   └── tests/                     # pytest unit + boot-smoke + Origin/Host shapes
└── frontend/
    ├── package.json               # react-resizable-panels for ShotPairView/ImageRefView
    ├── vite.config.ts             # Vite proxy /api/* → 127.0.0.1:8766 with Origin rewrite
    ├── tsconfig.json
    ├── index.html
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx                # Routes: / and /file/* only (no /project, no /stage)
    │   ├── api.ts                 # 3 calls: fetchTree, fetchFile, putFile (+ imageUrl helper)
    │   ├── localStorage.ts
    │   ├── types.ts               # TreeNode + ProjectMeta + FileResult — no Stage/Regen/Promote types
    │   ├── styles.css             # light-theme chrome + dark <pre> carve-outs
    │   ├── components/
    │   │   ├── Sidebar.tsx        # single section "AI Videos" with sub-type badges
    │   │   ├── Reader.tsx         # render-mode dispatch (no regen-panel, no cross-tree link)
    │   │   ├── Editor.tsx
    │   │   ├── BrokenLink.tsx
    │   │   ├── Breadcrumb.tsx
    │   │   ├── Home.tsx
    │   │   ├── ParseFallback.tsx
    │   │   ├── ShotPairView.tsx
    │   │   ├── ShotlistTableView.tsx
    │   │   └── ImageRefView.tsx
    │   ├── markdown/
    │   │   ├── renderer.tsx       # locked-block "锁定块" pill via pre-render regex
    │   │   ├── CodeView.tsx
    │   │   ├── JsonlView.tsx
    │   │   └── ImagePlaceholder.tsx
    │   └── lib/
    │       ├── linkResolver.ts
    │       ├── shotPairing.ts
    │       └── shotlistParser.ts
    ├── e2e/                       # Playwright (2 mode profiles)
    └── test/                      # Vitest
```

**Removed compared to v0** (per follow-up 001):
- Backend: `regen_prompt.py`, `promotions.py`, `stages.py`. `/api/regen-prompt`, `POST /api/promote`, `DELETE /api/promote`, `/api/stages` endpoints all dropped.
- Frontend: `RegeneratePanel.tsx`, `ProjectPage.tsx`, `StagePage.tsx`, `QaView.tsx`, `QaErrorBoundary.tsx`, `lib/autonomousMode.ts`, `lib/qaParser.ts`. Routes `/project/...` and `/stage/...` dropped.
- TreeNode sections: "Specs" and "Context" sections gone — sidebar emits ONLY the "AI Videos" section.

## Hard constraints (preserved from v0)

1. Localhost-only, IPv4 (`127.0.0.1`); IPv6 + `0.0.0.0` explicitly out of scope.
2. Origin/Host gate on every state-changing endpoint (now just `PUT /api/file`); foreign / wrong-port → 403; loopback aliases admit.
3. Path traversal hardening: every probe collapses to a single 404 (no existence oracle); symlinks/junctions refused.
4. Extension allowlist for reads: `.md`, `.json`, `.yaml`, `.yml`, `.jsonl`, `.txt`, `.png`, `.jpg`. SVG NOT allowed. Image extensions NOT writeable (PUT rejects with 400).
5. RFC 7232 `If-Unmodified-Since` required on PUT for existing files (divergence from spec_driven retained); stale → 409, missing → 400.
6. Markdown sanitization: `rehype-sanitize` default schema.
7. CSP header on responses: `default-src 'self'; img-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'`.
8. Light-theme chrome per `agent_refs/project/development.md` rule 1; dark `<pre>` carve-outs only.
9. FastAPI + Python 3.11+ + strong-typed `@dataclass(frozen=True)` containers; pip-only.
10. React + TypeScript + Vite + react-resizable-panels.
11. Bound port 8766 (Vite dev 5174); coexistence with spec_driven (8765/5173) intact.
12. EXPOSED_TREE membership: **single root — `ai_videos/**/*.{md,json,jsonl,yaml,yml,txt,png,jpg}`**.
13. localStorage namespace `ai_video_management.*` (still relevant for any future cross-tab state).

## Out of scope (v1, post-follow-up)

- Spec-pipeline navigation: `specs/`, `CLAUDE.md`, `.claude/` are not in EXPOSED_TREE.
- Regen-prompt assembly: not a feature of this webapp. Use `spec_driven` for that.
- Pinning (`<stage>/promoted.md`): not a feature.
- QaView render mode for spec interview pages: not applicable.
- Cross-tree link "查看规格": removed.
- Render-API integration with Kling / Seedance / Seedream (text-prompt viewing/editing only).
- Multi-tenant / multi-user; auth; WebSockets; mobile-responsive; storyboard horizontal-scroll view; cross-publish manager; English translation; project-diff view; file create/delete/upload through the webapp; dark-mode chrome toggle; file-system watcher.

## Success looks like

1. `make run-prod` → open `http://127.0.0.1:8766/` → recursive sidebar shows ONE section: AI Videos. The `wukong_juexing` entry has a `短` badge.
2. Click `ai_videos/wukong_juexing/prompts/shot02_kling.md` → ShotPairView with Kling on left + Seedance on right + per-pane copy buttons.
3. Click `ai_videos/wukong_juexing/shotlist.md` → ShotlistTableView; each `shotNN` cell is a button → opens that shot's pair view.
4. Click `ai_videos/wukong_juexing/characters/ref_images/main_seedream.md` → ImageRefView; left = prompt, right = companion `.png` if present, else fallback message.
5. Click `ai_videos/wukong_juexing/characters/main.md` → MarkdownView with the **锁定块** pill on the descriptor.
6. No "Specs" section. No "Context" section. No regen-prompt panel. No cross-tree link.
7. PUT `/api/file` succeeds for editable text files; rejects images with 400; missing `If-Unmodified-Since` returns 400; stale returns 409.
8. spec_driven on 8765 continues to handle regen + pinning for ai_video projects (unchanged).
