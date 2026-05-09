# ai_video_management

Focused viewer / editor SPA for the artifacts under `ai_videos/{name}/` — character bibles, Seedream立绘 prompts, style guides, scripts, shotlists, dual Kling+Seedance shot prompts, publish metadata, README. Three custom view modes make the ai_video output structure navigable: **ShotPairView** (Kling + Seedance side-by-side), **ShotlistTableView** (clickable shot rows), and **ImageRefView** (Seedream prompt + companion `.png` preview).

The webapp's only concern is `ai_videos/`. It does not read, reference, or anchor on any other directory in the workspace.

## Run

The webapp supports three runtime modes. All bind IPv4 loopback only (`127.0.0.1`) — never `0.0.0.0`.

### Production single-process — `make run-prod`

Builds the frontend bundle into `backend/static/` and serves SPA + API from one FastAPI process.

```
make build-frontend
make run-prod
```

Open `http://127.0.0.1:8766/`.

### Backend-only alias — `make run`

Alias for `make run-backend`. Expects a previously built bundle in `backend/static/` (or treat as API-only).

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

- **Backend.** FastAPI on `127.0.0.1:8766` (IPv4 loopback). Strongly typed Python in `backend/libs/` (`@dataclass(frozen=True)` containers, `str | None` syntax). Single-process mode also serves `backend/static/`.
- **Frontend.** React + Vite (TypeScript). Recursive sidebar walks `node.children` uniformly; render-mode dispatch in `Reader.tsx` chooses `MarkdownView` / `ShotPairView` / `ShotlistTableView` / `ImageRefView` / `JsonlView` / `CodeView` / `ImagePlaceholder`; every parse-on-render component is wrapped in `<ParseFallback>` (real React Error Boundary class).
- **API surface (3 endpoints).** `GET /api/tree`, `GET /api/file?path=…`, `PUT /api/file`.
- **Sandbox (single root).** `ai_videos/**/*.{md,json,jsonl,yaml,yml,txt,png,jpg}`. No other workspace path is reachable.
- **Workspace-root anchor.** `RepoRoot.find()` walks up from CWD looking for a directory containing `ai_videos/` as a child; the parent of that match becomes the workspace root.

### ai_video-specific UX

- **ShotPairView**: matches `prompts/shot{NN}_{kling|seedance}.md` and renders both partners side-by-side using `react-resizable-panels`. Yellow banner if partner is missing. Per-pane copy buttons announce via shared `aria-live` region.
- **ShotlistTableView**: renders `shotlist.md` as standard markdown table; overrides `<td>` to wrap shot-id cells in `<button>`s that programmatically navigate to the matching ShotPairView.
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
