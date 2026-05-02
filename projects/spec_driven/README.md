# spec_driven

A readonly viewer for the artifacts produced by the spec-driven workflow in this monorepo.

## What it shows

Two top-level sidebar sections:

1. **Claude Settings & Shared Context** — `CLAUDE.md`, every `.claude/agents/*.md`, every `.claude/skills/<folder>/SKILL.md`.
2. **Projects** — for each `task_type` (`development`, `ai_video`, …), every project's five-stage subtree under `specs/{task_type}/{task_name}/`: `user_input/`, `interview/`, `findings/`, `final_specs/`, `validation/`.

The main pane renders the selected file: markdown via CommonMark + GFM with Shiki-highlighted code blocks; YAML / JSON / JSONL via Shiki with line numbers (one block per line for `.jsonl`).

## Run

```sh
make run
```

Builds the React bundle, then starts a single FastAPI process on `127.0.0.1:8765` serving both `/` (static) and `/api/`. Open `http://localhost:8765/` in Chrome.

```sh
make dev
```

Two-process dev: FastAPI with `--reload` on `127.0.0.1:8765` and Vite dev server on `127.0.0.1:5173`. Use the Vite URL while developing.

## Configure

- `SPEC_DRIVEN_PORT` env var overrides the default port (`8765`).
- The backend walks parent directories from its own file at startup until it finds a directory containing `CLAUDE.md`, `specs/`, and `.claude/`. That's `REPO_ROOT`. If none is found, the process exits non-zero.

## Install

```sh
# from this folder
uv sync                                # backend deps via the root pyproject.toml
cd frontend && npm install              # frontend deps
```

## Security model

Localhost-only. The backend binds to `127.0.0.1`, has no auth, and exposes only `GET` endpoints. Running on a multi-user machine without a network sandbox is **out of scope for v1** — the threat model assumes one user, one machine.

## Browser support

Latest stable Chrome / Chromium-based browsers. No IE, Firefox, or Safari guarantees. No mobile responsiveness.

## Layout

```
projects/spec_driven/
├── README.md
├── Makefile
├── .gitignore
├── backend/
│   ├── main.py                        # ~15-line entry; argparse, env, hand off to libs.api
│   ├── requirements.txt               # mirrored into root pyproject.toml
│   ├── libs/
│   │   ├── repo_root.py               # walk-upward discovery
│   │   ├── exposed_tree.py            # the EXPOSED_TREE concept (FR-1)
│   │   ├── safe_resolve.py            # path sandbox (FR-5, FR-6, NFR-4)
│   │   ├── tree_walker.py             # /api/tree shape (FR-7..FR-10)
│   │   ├── file_reader.py             # /api/file with full error mapping (FR-5)
│   │   └── api.py                     # FastAPI app wiring + static-files mount
│   └── tests/
│       ├── unit/                      # pytest unit tests
│       └── fixtures/                  # checked-in test data
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api.ts                     # fetch wrapper for /api/tree, /api/file
        ├── routes.tsx                 # React Router config (FR-15)
        ├── localStorage.ts            # spec_driven.sidebar.v1 helpers
        ├── components/
        │   ├── Sidebar.tsx            # ARIA tree (FR-18..FR-28)
        │   ├── Reader.tsx             # main pane
        │   ├── Breadcrumb.tsx         # FR-29
        │   ├── BrokenLink.tsx         # FR-34 muted-tooltip component
        │   └── RefreshButton.tsx
        ├── markdown/
        │   ├── slug.ts                # GFM kebab-case slug (FR-30)
        │   ├── classifier.ts          # link classification (FR-33)
        │   ├── renderer.tsx           # CommonMark + GFM + Shiki
        │   └── jsonl.ts               # per-line JSON (FR-32)
        └── styles.css
```

See `specs/development/spec_driven/final_specs/spec.md` for the full contract (39 FRs, 16 NFRs).
