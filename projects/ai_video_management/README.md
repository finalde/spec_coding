# ai_video_management

## Layout (follow-up 039 — 2026-05-13)

Follows the `apps/+libs/` layout from `.claude/agent_refs/project/development.md` §1–6:

```
ai_video_management/
├── apps/
│   ├── api/        # FastAPI executable (main.py, container.py, routes.py, asgi.py, static/)
│   └── ui/         # React SPA (was frontend/)
├── libs/
│   ├── common/     # env_loader, repo_root, safe_resolve, exposed_tree, sub_type_lookup
│   ├── domain/     # (v1 empty; populated incrementally as splits refine)
│   ├── infrastructure/  # __reader/__writer/__middleware/__importer/__extractor/__archiver/__renamer files
│   └── application/     # (v1 empty; per-endpoint Query/Command split is a planned follow-up)
├── tests/
├── Makefile
├── pyproject.toml  # canonical deps (includes dependency-injector)
└── requirements.txt
```

DI wiring: `apps/api/container.py` declares the `Container` with singletons for ExposedTree, SafeResolver, FileReader/Writer, TreeReader, MediaRenamer, MediaArchiver, FrameExtractor, DownloadsImporter, ActorPool, Casting. Route handlers are module-level in `apps/api/routes.py`, decorated with `@inject` + `Depends(Provide[Container.x])`. `main.py` overrides `repo_root_path`/`bound_origin` and wires the routes module.

Focused viewer / editor SPA for the artifacts under `ai_videos/{name}/` — character bibles, Seedream立绘 prompts, style guides, scripts, shotlists, dual Kling+Seedance shot prompts, publish metadata, README. Three custom view modes make the ai_video output structure navigable: **ShotPairView** (Kling + Seedance side-by-side), **ShotlistTableView** (clickable shot rows), and **ImageRefView** (Seedream prompt + companion `.png` preview).

The webapp's only concern is `ai_videos/`. It does not read, reference, or anchor on any other directory in the workspace.

## Run

The webapp supports three runtime modes. All bind IPv4 loopback only (`127.0.0.1`) — never `0.0.0.0`.

### Production single-process — `make run-prod`

Builds the frontend bundle into `apps/api/static/` and serves SPA + API from one FastAPI process.

```
make build-frontend
make run-prod
```

Open `http://127.0.0.1:8766/`.

### Backend-only alias — `make run`

Alias for `make run-backend`. Expects a previously built bundle in `apps/api/static/` (or treat as API-only).

### Backend + frontend separately (dev) — two terminals

Terminal 1 (backend on `127.0.0.1:8766`):

```
make run-backend
```

Terminal 2 (Vite dev server on `127.0.0.1:5174`):

```
make run-frontend
```

Open `http://127.0.0.1:5174/`. The Vite proxy forwards `/api/*` to the backend with `Origin` rewrite to `http://127.0.0.1:8766` so the backend's Origin/Host gate sees a same-shape request in both runtime modes.

## Test

| Target | What it runs |
|---|---|
| `make test-backend` | `pytest` over `backend/tests/` (boot-smoke + sub_type lookup + tree consumer walk + Origin/Host shapes). |
| `make test-frontend` | Vitest unit tests (`shotPairing`, `shotlistParser`). |
| `make e2e` | Playwright suite — 2 mode profiles × 8 scenarios covering the three view modes, locked-block pill, sub-type badge, Origin gate, sandbox 404 verification. |
| `make boot-smoke` | Boot-smoke pytest: process starts, `GET /api/tree` returns single-section shape. |

## Install

| Target | What it does |
|---|---|
| `make install` | Runs both install targets below. |
| `make install-backend` | `pip install -r backend/requirements.txt` (pip-only). |
| `make install-frontend` | `npm install` inside `frontend/`. |

## Architecture

- **Backend.** FastAPI on `127.0.0.1:8766` (IPv4 loopback). Strongly typed Python in `backend/libs/` (`@dataclass(frozen=True)` containers, `str | None` syntax). Single-process mode also serves `apps/api/static/`.
- **Frontend.** React + Vite (TypeScript). Recursive sidebar walks `node.children` uniformly; render-mode dispatch in `Reader.tsx` chooses `MarkdownView` / `ShotPairView` / `ShotlistTableView` / `ImageRefView` / `JsonlView` / `CodeView` / `ImagePlaceholder`; every parse-on-render component is wrapped in `<ParseFallback>` (real React Error Boundary class).
- **API surface (3 endpoints).** `GET /api/tree`, `GET /api/file?path=…`, `PUT /api/file`.
- **Sandbox (single root).** `ai_videos/**/*.{md,json,jsonl,yaml,yml,txt,png,jpg}`. No other workspace path is reachable.
- **Workspace-root anchor.** `RepoRoot.find()` walks up from CWD looking for a directory containing `ai_videos/` as a child; the parent of that match becomes the workspace root.

### ai_video-specific UX

- **ShotPairView**: matches `prompts/shot{NN}_{kling|seedance}.md` and renders both partners side-by-side using `react-resizable-panels`. Yellow banner if partner is missing. Per-pane copy buttons announce via shared `aria-live` region.
- **ShotlistTableView**: renders `shotlist.md` as standard markdown table; overrides `<td>` to wrap shot-id cells in `<button>`s that programmatically navigate to the matching ShotPairView.
- **合成本集视频 (episode concat, per-language)**: when viewing an episode's `shotlist.md` (`episodes/ep{NN}/shotlist.md`), the toolbar shows **four** 🎬 buttons (原片 / 中文 / EN / 中英) that `POST /api/concat-episode` `{path, lang}` (`lang ∈ original|zh|en|both`). `original` walks `shots/shot*/renders/` in shot order picking each shot's **newest** `.mp4` (`archive/` excluded) → `ep{NN}.mp4`; the subtitle variants pick each shot's burned language master `shot{NN}_{zh|en|zhen}.mp4` → `ep{NN}_{zh|en|zhen}.mp4`. Shots lacking the requested source are skipped. So an episode can have up to 4 versions. Uniform 720×1280 9:16 H.264+AAC, overwriting any prior build. Aggregate: `episode__{route,command,dto,mapper}` + `infrastructure/writers/episode__writer.py` (`EpisodeConcatBuilder`).
- **📋 复制全部视频 prompt (copy all video prompts)**: when viewing any episode-level markdown (`episodes/ep{NN}/{shotlist,script,dialogue,publish,…}.md`), the toolbar shows a **📋 复制全部视频 prompt** button. One click gathers each shot's `视频 prompt` fenced block (the `## 视频 prompt` block — **only** that, never the `台词配音` block), in shot order (`shots/shot{NN}/shot{NN}.md`, sorted), joins them with a blank line, and writes the lot to the clipboard. A toast reports how many were copied (and how many shots were skipped for lacking a video block). Pure client-side: shot paths come from the already-loaded `knownPaths`, each shot md is fetched via `GET /api/file`, and the block is classified by its nearest preceding `##` heading (same rule as the inline per-block editor) — no new endpoint. Helpers in `apps/ui/src/lib/videoPrompts.ts` (`extractVideoPromptBody` / `episodeDirOf` / `shotMdPathsInEpisode`); wired in `Reader.tsx`'s episode toolbar.
- **双语字幕烧录 (bilingual subtitle burn-in)**: each shot render mp4 (`shots/shot{NN}/…`) tile shows 「📝 生成台词」 (`POST /api/scaffold-subtitles` → seeds a bilingual `shots/shot{NN}/subtitles.md`, each cue `起-止 中文 || English` with English left blank) plus **three burn buttons** 「💬中文 / 💬EN / 💬中英」 (`POST /api/burn-subtitles` `{path, lang}`, `lang ∈ zh|en|both`). The chosen language is rendered to ASS (中文 微软雅黑 / 英文 Arial; `both` stacks 中 above 英; L/R safe margin 120px, bottom 170px) and ffmpeg-burned into a stable per-shot master `shots/shot{NN}/shot{NN}_{zh|en|zhen}.mp4` in the shot-folder **root** (so multiple imported takes can coexist under `renders/`; burning any take overwrites the language master). Original renders are kept. Aggregate: `subtitle__{route,command,dto,mapper}` + `domain/value_objects/subtitle__valueobject.py` (parse + per-lang ASS) + `infrastructure/writers/subtitle__writer.py` (`SubtitleBurner`).
- **共享 BGM 库 (background-music library)**: 与演员库 / 配音库同构的共享音乐库，落盘 `ai_videos/_bgm/{category}/bgm_NNNN/{bgm_NNNN.md, bgm_NNNN.mp3}`，`bgm_NNNN` id 全局唯一（跨 12 类情绪 category），剧本按裸 id 引用（像 actor）。webapp 切片 `bgm__{route,query,command,dto,mapper}` + `domain/{value_objects,errors,repositories}/bgm__*` + `infrastructure/writers/bgm__{writer,prompt}.py`（`BgmPool`）+ `infrastructure/readers/bgm_reference__reader.py`（扫每集 / 短根 `bgm.md` 反查「哪些剧引用了某 bgm」）。生成走**两步流程**（follow-up 002）：**步骤1** `POST /api/bgms/create-prompts` 只分配 track + 写 sidecar（含 prompt/seed/duration），不出音频；**步骤2 按条**二选一——`POST /api/bgms/{id}/generate-audio`（本地 GPU 跑 `tools/stableaudio_gen.py`，自托管 Stable Audio，开源权重商用安全，torch 不入 webapp 进程，需专用 venv + `BGM_PYTHON`）或 `POST /api/bgms/{id}/import-audio`（把 prompt 复制到外部平台出音乐、下载后把 Downloads 最新音频移入该 track，**此路径不需要 torch**）。prompt-only track（有 sidecar 无 mp3）不会被 reaper 回收。UI：`BgmGrid`（网格 + 12 类分类 filter + mp3 试听 + 被引用 badge + 软删，删除被引用的会 409 拒绝）/ `BgmView`（元数据表 + prompt + 试听 + references 反查 + 无音频时「🎧 本地 GPU 生成」「📥 导入下载音乐」按钮）/ `BgmPoolGenerator`（preview-prompts + 生成 prompt 表单，mood/配器 = dropdown 预设 + 可选自定义框）。成片合成由 `tools/mux_av.py` 完成（视频 `-c:v copy` + 台词 MP3 + BGM sidechain duck + `amix=normalize=0`）。详见 `.claude/agent_refs/project/ai_video.md` rule 13。
- **ImageRefView**: triggered by `/ref_images/.+_seedream\.md` or any `.png/.jpg`. Left pane: prompt markdown. Right pane: companion `<img src="/api/file?path=…&mtime=…">` if present, or fallback Chinese instruction.
- **Locked-block pill**: pre-renders `【...锁定描述符 vN】 ... 禁用 ...。` blocks with a "锁定块" badge so the byte-equality contract is visually reinforced.
- **Sub-type badge**: `短` / `剧` next to each `ai_videos/{name}/` project node in the sidebar; resolved heuristically from `episodes/` directory existence (novel) vs presence of `script.md`/`shotlist.md` at project root (short).

## Security model

- Localhost-only, IPv4 (`127.0.0.1`). IPv6 (`[::1]`) and `0.0.0.0` are explicitly out of scope.
- `Origin` and `Host` validated on `PUT /api/file` (the only state-changing endpoint); foreign / missing / wrong-port → **403**. Loopback aliases (`localhost` ↔ `127.0.0.1` at the bound port) admit. **Any port other than `8766` is foreign.**
- File access sandboxed through the `ai_videos/` root. Path traversal probes (`..`, percent-encoded, ADS, Windows reserved names, 8.3 short names, mixed slashes, trailing-backslash per Vite CVE-2025-62522) all collapse to a single **404** (no existence oracle). Symlinks / Windows junctions refused outright.
- Extension allowlist for reads: `.md`, `.json`, `.yaml`, `.yml`, `.jsonl`, `.txt`, `.png`, `.jpg`. SVG NOT allowed (code-execution vector). Image extensions are not writable. **PUT extension-rejected returns 400.** 1 MiB body cap on writes.
- **`If-Unmodified-Since` is REQUIRED on PUT for existing files.** Missing → 400; stale → 409.
- Markdown render path uses `rehype-sanitize` default schema; raw HTML, event handlers, and `javascript:` URIs are stripped.
- CSP header on all responses: `default-src 'self'; img-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'`.

## Light-theme app chrome

App chrome (body, sidebars, toolbars, panels, buttons, form controls) is light-only — `:root { color-scheme: light; }`, no `@media (prefers-color-scheme: dark)` overrides. Dark `<pre>` palettes inside `.markdown-view pre`, `.code-view pre` are intentional carve-outs (validated WCAG AA).
