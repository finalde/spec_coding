# spec_coding

A monorepo for **spec-coding workflows** — a disciplined two-stage pipeline that injects an explicit *execution plan* between human-readable specs and machine code, in order to push more determinism into AI-driven implementation.

```
┌─── Stage 1 — Planning ────────────────────────────────────────┐
│  initial prompt                                                │
│   → multi-turn interview Q&A   (specs/interviews/{id}/qa.md)   │
│   → spec compile               (specs/specs/{id}/spec.md)      │
│   → research fan-out           (specs/findings/{id}/...)       │
│   → optional adjustments       (specs/specs/{id}/adjustments)  │
│   → execution-plan compile     (specs/execution_plans/{id}/    │
│                                  plan.yaml)                    │
└────────────────────────────────────────────────────────────────┘
┌─── Stage 2 — Execution ───────────────────────────────────────┐
│  execute  ⇄  validate          (parallel; events.jsonl stream) │
│   → revisions loop                                             │
│   → final validation pass                                      │
│   → outputs land in projects/{name}/ or ai_videos/{name}/      │
└────────────────────────────────────────────────────────────────┘
```

## Repo layout

| Path                         | What lives there |
|------------------------------|------------------|
| `CLAUDE.md`                  | Repo-wide conventions and pipeline overview. |
| `pyproject.toml`             | Canonical Python deps. `uv sync` reads this. |
| `requirements.txt`           | Mirror of the above, kept for the pip fallback path. |
| `.claude/agents/`            | The six `agent_team__*` manager agents. |
| `.claude/skills/agent_team/` | The pipeline-orchestrator SKILL. |
| `specs/`                     | Persistence layer (interviews, specs, findings, execution_plans, `index.json`). |
| `projects/`                  | All projects, including the platform itself. User code outputs land here. |
| `projects/spec_studio/`      | The FastAPI + React platform that drives the pipeline. Run backend + frontend in two terminals. |
| `ai_videos/`                 | User AI-video task outputs. |
| `.audit/adhoc_agents/`       | Local-only audit trail for adhoc subagents (gitignored). |
| `.venv/`                     | Local Python virtualenv (gitignored). |

## Two ways to drive the pipeline

1. **From Claude Code itself** — invoke `/agent_team <your task>` and the SKILL walks the six phases, spawning the manager agents and adhoc subagents directly. No web UI required.
2. **From the browser** — run `spec_studio` (FastAPI backend + React frontend) and drive the same phases through a UI with a live event log. Same agents, same artifacts, same `specs/` persistence — different surface.

## Quick start

Two terminals.

```bash
# one-time install (from repo root)
uv sync                                                       # install Python deps
( cd projects/spec_studio/frontend && npm install --legacy-peer-deps )

# terminal 1 — backend (FastAPI on http://127.0.0.1:8000)
python projects/spec_studio/main.py

# terminal 2 — frontend (Vite dev on http://127.0.0.1:5173)
cd projects/spec_studio/frontend && npm run ui
```

Open the UI at `http://127.0.0.1:5173`. Vite proxies `/api` → `http://127.0.0.1:8000`.

If you don't have `uv` yet: install it from https://docs.astral.sh/uv/ — fastest. Or fall back to `python -m venv .venv && .venv/bin/pip install -r requirements.txt`.

### Configurable env vars

Override before running either entry. CLI flags on `npm run ui` (e.g. `-- --port 3000`) also work.

| Var               | Default                                | Used by              |
|-------------------|----------------------------------------|----------------------|
| `BACKEND_HOST`    | `127.0.0.1`                            | backend              |
| `BACKEND_PORT`    | `8000`                                 | backend, vite proxy  |
| `BACKEND_RELOAD`  | empty (false)                          | backend (dev reload) |
| `BACKEND_URL`     | `http://$BACKEND_HOST:$BACKEND_PORT`   | vite proxy override  |
| `FRONTEND_HOST`   | `127.0.0.1`                            | vite                 |
| `FRONTEND_PORT`   | `5173`                                 | vite                 |

### Production build (optional sanity check)

```bash
python -m compileall projects/spec_studio/backend
( cd projects/spec_studio/frontend && npm run build )
```

## What's a "task" and how does it produce output

A task is one trip through the pipeline. You give it a name (e.g. `affiliate_dashboard`), a `root_folder` (`projects` or `ai_videos`), and an initial prompt. The SKILL orchestrates the six manager agents in turn:

| # | Manager                                | Adhoc workers it spawns                         | Output |
|---|----------------------------------------|--------------------------------------------------|--------|
| 1 | `agent_team__interview_manager`        | none — interviews the user directly              | `specs/interviews/{id}/qa.md` |
| 2 | `agent_team__spec_compiler`            | none                                             | `specs/specs/{id}/spec.md` |
| 3 | `agent_team__research_manager`         | one researcher per angle (3–8 in parallel)       | `specs/findings/{id}/{angle}.md`, `dossier.md` |
| 4 | (user adjustments — optional)          | —                                                | `specs/specs/{id}/adjustments.md` |
| 5 | `agent_team__execution_plan_compiler`  | none                                             | `specs/execution_plans/{id}/plan.yaml` |
| 6 | `agent_team__execution_manager` ‖ `agent_team__validation_manager` | one executor + one validator per work-unit (parallel) | `projects/{name}/...` or `ai_videos/{name}/...` + `events.jsonl` |

Adhoc subagents are traced to `.audit/adhoc_agents/{date}/{task_id}/spawns/{agent_id}/{prompt.md, tools.json, output.md}` — every dynamic spawn is replayable and inspectable.

## Iteration bounds and circuit-breaker

- Default `max_iterations: 3` per work-unit.
- Halt + emit `pipeline.halted` when (a) the same issue id repeats across two iterations, (b) more than five issues stay open after iteration 2, or (c) wall-clock exceeds 30 minutes on a single unit.
- After halt, the SKILL escalates to the user. There are no silent retries past the cap.

## Conventions

See `CLAUDE.md` for the load-bearing rules (project layout, OOP, strong typing, agent-name `<prefix>__<name>` pattern, 500-char description ceiling on agent frontmatter, etc.).
