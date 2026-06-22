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

- **中文 display_name in the sidebar (left nav)**: pinyin/English folder names surface their Chinese name via the tree node's `display_name` (rendered by `Sidebar` as `display_name || name`). `tree__reader._project_zh_title` resolves a **drama** folder's title from `README.md` H1 `《…》` (legacy) **or** the staged-pipeline `1_立项/concept.md` H1 (`# 立项策划单 · 武神觉醒` → 武神觉醒). `tree__reader._sidecar_zh_label` resolves a **scene** folder (`…/scenes/{pinyin}/`) from its `{pinyin}.md` H1 `（中文名）` (`# zhenbei_wangfu_zhengting（镇北王府正厅）` → 镇北王府正厅). Shared extractor `_h1_zh` (《…》 → （…） → text after a `·` separator → whole H1). Scene resolution is scoped to `parent.name == "scenes"` so character folders (already Chinese) aren't mislabeled.
- **ShotPairView**: matches `prompts/shot{NN}_{kling|seedance}.md` and renders both partners side-by-side using `react-resizable-panels`. Yellow banner if partner is missing. Per-pane copy buttons announce via shared `aria-live` region.
- **ShotlistTableView**: renders `shotlist.md` as standard markdown table; overrides `<td>` to wrap shot-id cells in `<button>`s that programmatically navigate to the matching ShotPairView.
- **合成本集视频 (episode concat, per-language)**: when viewing an episode's `shotlist.md` (`episodes/ep{NN}/shotlist.md`), the toolbar shows **four** 🎬 buttons (原片 / 中文 / EN / 中英) that `POST /api/concat-episode` `{path, lang}` (`lang ∈ original|zh|en|both`). `original` walks `shots/shot*/renders/` in shot order picking each shot's **newest** `.mp4` (`archive/` excluded) → `ep{NN}.mp4`; the subtitle variants pick each shot's burned language master `shot{NN}_{zh|en|zhen}.mp4` → `ep{NN}_{zh|en|zhen}.mp4`. Shots lacking the requested source are skipped. So an episode can have up to 4 versions. Uniform 720×1280 9:16 H.264+AAC, overwriting any prior build. **Output framerate follows the source** (`_target_fps` probes the clips, takes the median, snaps to the nearest standard rate — 24/25/30/50/60 — falling back to 30 only if unprobeable, follow-up 138): the ~24fps i2v renders are NOT up-converted to 30, which would duplicate ~1 in 5 frames (4:5 pulldown) and judder across the whole video. Aggregate: `episode__{route,command,dto,mapper}` + `infrastructure/writers/episode__writer.py` (`EpisodeConcatBuilder`). **承接接缝自动抹平 (seam de-stutter, follow-up 133/137)**: a 承接 shot (per its `衔接:` line) is generated from the previous shot's last frame, so the join carries a ~0.2s 卡顿. That hitch is **not** a held duplicate frame — it's a **velocity ramp on both sides**: the outgoing clip decelerates into the final frame it was told to end on, and the incoming clip accelerates from rest off that same still (frames keep changing, just slowly, so a tight freeze threshold misses them, follow-up 137). So at every 承接 seam the builder trims **both** sides into a clean motion-to-motion cut: the **incoming head** via `freezedetect` at a loose -45dB threshold (`_detect_head_freeze` / `_parse_head_freeze`: leading freeze only, capped 1s, fail-open) floored at `_SEAM_MIN_EDGE_TRIM_S` 0.15s, and the **outgoing predecessor's tail** by a fixed `_SEAM_MIN_EDGE_TRIM_S` bite (the decel settle reads as a long fragmented near-frozen span that detection over-estimates, so only the final dead sliver is removed, deterministically). A ~0.12s seam cross-fade was tried (follow-up 135) and **reverted** (follow-up 136): post-trim the seam frames are no longer identical, so the dissolve read as a visible image switch. `_probe_duration` measures the **video-stream** length (`-map 0:v:0 -c copy -f null -`), not the container Duration, since an over-long audio track otherwise overstates the timeline and drops content (follow-up 135c). 硬切 shots are intended cuts — untouched (the hard-cut text 「无承接帧」 contains the substring 承接, so `_is_continuity_shot` checks 硬切 first). Each used shot's trimmed seconds (`trimmed_s` = head + tail) flows to the result; the toast reports 「抹平 N 处承接接缝」. The concat is otherwise **faithful**: every clip plays at its natural speed and length (audio included via `atrim`→`asetpts`→`aresample`→`aformat`, audio-less clips falling back to a length-matched `anullsrc`), so the episode total ≈ the sum of the source clips and speech is never altered. `_probe_duration` measures the **video-stream** length (`-map 0:v:0 -c copy -f null -`), not the container Duration, since an over-long audio track otherwise overstates the timeline and drops content (follow-up 135c). **No transitions** — joins are clean butt-cuts. Three softening experiments were all tried and **reverted**: a de-freeze pass (`mpdecimate`+`atempo`, follow-up 139/140 → 141) sped/dropped speech; a near-identical-frame seam cross-fade (follow-up 135 → 136) flashed; and a whole-episode cross-dissolve (`xfade`+`acrossfade`, follow-up 142 → 143) did not read as softer than a clean cut — it looked worse. The remaining seam jolt (「画面先跳一下才切」), shot11→12 背身 pose misalignment, and mid-shot stalls are **generation defects** no concat-side transition can fix — they're resolved by regenerating the shot (wushen follow-up 042 regen list).
- **📋 复制全部视频 prompt (copy all video prompts)**: when viewing any episode-level markdown (`episodes/ep{NN}/{shotlist,script,dialogue,publish,…}.md`), the toolbar shows a **📋 复制全部视频 prompt** button. One click gathers each shot's `视频 prompt` fenced block (the `## 视频 prompt` block — **only** that, never the `台词配音` block), in shot order (`shots/shot{NN}/shot{NN}.md`, sorted), joins them with a blank line, and writes the lot to the clipboard. A toast reports how many were copied (and how many shots were skipped for lacking a video block). Pure client-side: shot paths come from the already-loaded `knownPaths`, each shot md is fetched via `GET /api/file`, and the block is classified by its nearest preceding `##` heading (same rule as the inline per-block editor) — no new endpoint. Helpers in `apps/ui/src/lib/videoPrompts.ts` (`extractVideoPromptBody` / `episodeDirOf` / `shotMdPathsInEpisode`); wired in `Reader.tsx`'s episode toolbar.
- **⏮ 生成末帧 (extract shot last frame · cross-shot continuity-frame, follow-up 132)**: each shot render mp4 (`shots/shot{NN}/…`) tile shows a **⏮ 生成末帧** button (`POST /api/extract-last-frame` `{path}`). One click ffmpeg-extracts that shot render's **final frame** to `shots/shot{NN}/shot{NN}_lastframe.png` at the shot-folder **root** (re-click overwrites) **and copies the same PNG into the next shot's folder as `shot{NN+1}_firstframe.png`** so the 承接 hand-off is done in one click — no manual copy. This is the cross-shot first-frame handoff (跨镜首帧承接, `.claude/agent_refs/project/ai_video.md` 2026-06-21): a 承接 shot's first frame = the previous shot's last frame. The next shot is matched by numeric adjacency (`_next_shot_folder`, zero-padding-agnostic: shot09→shot10); when there is no next shot (episode's last) only the lastframe is written and the response's `first_frame` is null. ffmpeg trick: `-sseof -3` decodes only the tail, `-update 1` leaves the PNG holding the last decoded frame. Reuses the **frame** aggregate (`frame__{route,command,dto,mapper}` + `FrameExtractor.extract_last_frame` in `infrastructure/writers/frame__writer.py`, `_shot_folder` resolving the shot root) and the already-registered frame error handlers; no new container provider. Frontend: `extractLastFrame` in `api.ts`, button gated by `isShotVideoPath` in `SiblingMedia.tsx`.
- **双语字幕烧录 (bilingual subtitle burn-in)**: each shot render mp4 (`shots/shot{NN}/…`) tile shows 「📝 生成台词」 (`POST /api/scaffold-subtitles` → seeds a bilingual `shots/shot{NN}/subtitles.md`, each cue `起-止 中文 || English` with English left blank) plus **three burn buttons** 「💬中文 / 💬EN / 💬中英」 (`POST /api/burn-subtitles` `{path, lang}`, `lang ∈ zh|en|both`). The chosen language is rendered to ASS (中文 微软雅黑 / 英文 Arial; `both` stacks 中 above 英; L/R safe margin 120px, bottom 170px) and ffmpeg-burned into a stable per-shot master `shots/shot{NN}/shot{NN}_{zh|en|zhen}.mp4` in the shot-folder **root** (so multiple imported takes can coexist under `renders/`; burning any take overwrites the language master). Original renders are kept. Aggregate: `subtitle__{route,command,dto,mapper}` + `domain/value_objects/subtitle__valueobject.py` (parse + per-lang ASS) + `infrastructure/writers/subtitle__writer.py` (`SubtitleBurner`).
- **共享 BGM 库 (background-music library)**: 与演员库 / 配音库同构的共享音乐库，落盘 `ai_videos/_bgm/{category}/bgm_NNNN/{bgm_NNNN.md, bgm_NNNN.mp3}`，`bgm_NNNN` id 全局唯一（跨 12 类情绪 category），剧本按裸 id 引用（像 actor）。webapp 切片 `bgm__{route,query,command,dto,mapper}` + `domain/{value_objects,errors,repositories}/bgm__*` + `infrastructure/writers/bgm__{writer,prompt}.py`（`BgmPool`）+ `infrastructure/readers/bgm_reference__reader.py`（扫每集 / 短根 `bgm.md` 反查「哪些剧引用了某 bgm」）。生成走**两步流程**（follow-up 002）：**步骤1** `POST /api/bgms/create-prompts` 只分配 track + 写 sidecar（含 prompt/seed/duration），不出音频；**步骤2 按条**二选一——`POST /api/bgms/{id}/generate-audio`（本地 GPU 跑 `tools/stableaudio_gen.py`，自托管 Stable Audio，开源权重商用安全，torch 不入 webapp 进程，需专用 venv + `BGM_PYTHON`）或 `POST /api/bgms/{id}/import-audio`（把 prompt 复制到外部平台出音乐、下载后把 Downloads 最新音频移入该 track，**此路径不需要 torch**）。prompt-only track（有 sidecar 无 mp3）不会被 reaper 回收。UI：`BgmGrid`（网格 + 12 类分类 filter + mp3 试听 + 被引用 badge + 软删，删除被引用的会 409 拒绝）/ `BgmView`（元数据表 + prompt + 试听 + references 反查 + 无音频时「🎧 本地 GPU 生成」「📥 导入下载音乐」按钮）/ `BgmPoolGenerator`（preview-prompts + 生成 prompt 表单，mood/配器 = dropdown 预设 + 可选自定义框）。成片合成由 `tools/mux_av.py` 完成（视频 `-c:v copy` + 台词 MP3 + BGM sidechain duck + `amix=normalize=0`）。详见 `.claude/agent_refs/project/ai_video.md` rule 13。
- **Episode 级 BGM 编排 + 烧录 (episode BGM arrange + burn, follow-up 004)**: 每集一条**稀疏** cue 时间线 `episodes/ep{NN}/bgm/bgm.md`（pipeline 按剧情人工写，只在强烈激情/武打/悲伤等段落铺 BGM、其余留白；行式 `起-止(秒) bgm_NNNN｜- | cat=情绪 | vol= | duck=on/off | fade=`）。查看该 `bgm/bgm.md` 时 `Reader` 渲染 **`BgmEpisodePanel`**：列出每条 cue（时间窗 + 情绪 + 剧情注释），每槽一个按 `cat` 过滤库内 `bgm_NNNN` 的下拉**像 casting 一样分配**（`POST/DELETE /api/episode-bgm/assign` 改写 cue 行 slot），顶部 **「🎵 烧录 BGM」** 按钮（`POST /api/episode-bgm/burn`）把已分配 cue 按窗烧进**带字幕整集** `ep{NN}_zh.mp4` → **`ep{NN}_zh_bgm.mp4`**（重烧覆盖；源与 `renders/` 不动；`duck=on` 用整集自身音轨 sidechain 让路；未分配 cue 跳过并在结果里报）。切片 `episode_bgm__{route,command,query,dto,mapper}` + `domain/{value_objects,errors,repositories}/episode_bgm__*` + `infrastructure/writers/episode_bgm__writer.py`（`EpisodeBgmManager`，多 cue ffmpeg filtergraph）。`GET /api/episode-bgm?path=` 读 cue + 源/成片状态。
- **ImageRefView**: triggered by `/ref_images/.+_seedream\.md` or any `.png/.jpg`. Left pane: prompt markdown. Right pane: companion `<img src="/api/file?path=…&mtime=…">` if present, or fallback Chinese instruction.
- **Locked-block pill**: pre-renders `【...锁定描述符 vN】 ... 禁用 ...。` blocks with a "锁定块" badge so the byte-equality contract is visually reinforced.
- **Sub-type badge**: `短` / `剧` next to each `ai_videos/{name}/` project node in the sidebar; resolved heuristically from `episodes/` directory existence (novel) vs presence of `script.md`/`shotlist.md` at project root (short).
- **回收站 (recycle bin / `DeletedView`)**: soft-deletes (mp4 / 图片 Reader 的 🗑 Delete) move files into `ai_videos/_deleted/{原路径}`. The `/deleted` route renders a media-preview grid plus two purge paths: **selected media** (`POST /api/hard-delete-media` per file — media-extension only) and **🧹 清空回收站（全部）** (`POST /api/purge-deleted` — one shot, recursively wipes the **entire** `ai_videos/_deleted/` subtree including `.md` sidecars and empty folders, returns `{purged}` count). Both gated by a typed-`DELETE` confirm modal. The header count reflects **all** files in the bin (not just previewable media), so the per-media purge no longer leaves `.md` sidecars + skeleton folders behind. `ai_videos/_deleted/` is fully gitignored — nothing in the bin is ever tracked. Aggregate: `MediaCommand.purge_deleted` → `MediaArchiver.purge_deleted` (`shutil.rmtree` of `_deleted/`).

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
