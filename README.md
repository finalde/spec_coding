# spec_coding

A monorepo for **spec-coding workflows** — a disciplined two-stage pipeline that injects an explicit *execution plan* between human-readable specs and machine code, in order to push more determinism into AI-driven implementation.

```
┌─── Six-stage spec-driven pipeline ─────────────────────────────────────┐
│  1 Intake              raw prompt → revised_prompt.md                  │
│  2 Interview           multi-choice Q&A → interview/qa.md              │
│  3 Research            parallel researcher fan-out → findings/         │
│  4 Spec compilation    revised + qa + dossier → final_specs/spec.md    │
│  5 Validation strategy parallel level-specialists → validation/        │
│  6 Execute ⇄ validate  per-unit code + parallel validators (events)    │
│                        outputs → projects/{name}/ or ai_videos/{name}/ │
└────────────────────────────────────────────────────────────────────────┘
```

## Repo layout

| Path                                       | What lives there |
|--------------------------------------------|------------------|
| `CLAUDE.md`                                | Repo-wide conventions and pipeline overview. |
| `pyproject.toml`                           | Canonical Python deps. `uv sync` reads this. |
| `requirements.txt`                         | Mirror of the above, kept for the pip fallback path. |
| `.claude/skills/agent_team/SKILL.md`       | The pipeline-orchestrator skill. |
| `.claude/skills/agent_team/playbooks/*.md` | Stage playbooks (interview, research, validation) the parent reads inline. |
| `.claude/agent_refs/{interview,research,validation}/*.md` | Accumulated institutional memory per stage. |
| `specs/`                                   | Persistence layer for the spec-driven workflow (`user_input/`, `interview/`, `findings/`, `final_specs/`, `validation/`). |
| `projects/`                                | All projects, including the platform itself. User code outputs land here. |
| `projects/spec_driven/`                    | The FastAPI + React platform that drives the pipeline. Run backend + frontend in two terminals. |
| `ai_videos/`                               | User AI-video task outputs. |
| `.audit/adhoc_agents/`                     | Local-only audit trail for worker subagents and stage events (gitignored). |
| `.venv/`                                   | Local Python virtualenv (gitignored). |

## Two ways to drive the pipeline

1. **From Claude Code itself** — invoke `/agent_team <your task>` and the skill walks the six phases. The parent is the manager at every stage: it reads the matching playbook + agent_refs, then spawns workers in parallel via the `Agent` tool. No separate manager subagent layer.
2. **From the browser** — run `spec_driven` (FastAPI backend + React frontend) and drive the same phases through a UI with a live event log. Same playbooks, same artifacts, same `specs/` persistence — different surface.

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

A task is one trip through the pipeline. You give it a `task_type` (`development` or `ai_video`), a `task_name`, and a raw prompt. The skill orchestrates six stages, with the parent acting as manager at every coordinated stage:

| # | Stage                          | Parent reads                                                                                              | Workers it spawns                                                       | Output |
|---|--------------------------------|-----------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|--------|
| 1 | Intake                         | (raw prompt)                                                                                              | none                                                                    | `user_input/{raw_prompt.md, revised_prompt.md}` |
| 2 | Interview                      | `playbooks/interview.md` + `agent_refs/interview/*.md`                                                    | optional category workers (parallel) when categories diverge            | `interview/qa.md` |
| 3 | Research                       | `playbooks/research.md` + `agent_refs/research/*.md`                                                      | one researcher per angle (3–6, all parallel)                            | `findings/{angle-*.md, dossier.md}` |
| 4 | Spec compilation               | revised_prompt + qa.md + dossier.md                                                                       | none                                                                    | `final_specs/spec.md` |
| 5 | Validation strategy            | `playbooks/validation.md` (strategy mode) + `agent_refs/validation/*.md`                                  | one level-specialist per validation level (all parallel)                | `validation/{strategy.md, acceptance_criteria.md, bdd_scenarios.md, system_tests.md, unit_tests.md, ...}` |
| 6 | Execution + streaming validation | `playbooks/validation.md` (runtime mode) + `agent_refs/validation/*.md`                                  | per work unit: validators per applicable level (all parallel)           | `projects/{name}/...` or `ai_videos/{name}/...` + `events.jsonl` |

Worker subagents are traced to `.audit/adhoc_agents/{date}/{task_id}/spawns/{worker_id}/{prompt.md, output.md}` — every dynamic spawn is replayable and inspectable. Stage-start events with `pre_reading_consulted` arrays land in `.audit/adhoc_agents/{date}/{task_id}/events.jsonl` alongside execution + validation events.

## Iteration bounds and circuit-breaker

- Default `max_iterations: 3` per work-unit.
- Halt + emit `pipeline.halted` when (a) the same issue id repeats across two iterations, (b) more than five issues stay open after iteration 2, or (c) wall-clock exceeds 30 minutes on a single unit.
- After halt, the SKILL escalates to the user. There are no silent retries past the cap.

## Conventions

See `CLAUDE.md` for the load-bearing rules (project layout, OOP, strong typing, skill-name `<prefix>__<name>` pattern, 500-char description ceiling on skill frontmatter, parent-direct stage execution model, etc.).
