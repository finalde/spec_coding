## Monorepo project conventions

### Structure
Each project lives in its own folder under the repo root (e.g. `projects/my_tool/` or `tools/my_tool/`). Projects must **never** share source files across folders — treat each folder as an independent unit.

```
spec_coding/
├── requirements.txt          # global: aggregates all project deps via -r includes
├── Makefile                  # global: venv, sync, run, new-project targets
├── CLAUDE.md                 # global rules (this file)
├── tools/
│   ├── mcp_youtube/          # example project
│   │   ├── requirements.txt  # project-local deps
│   │   └── main.py           # entry point (or app.py / run.sh)
│   └── ollama_cursor_proxy/
│       ├── requirements.txt
│       └── app.py
└── projects/                 # future projects go here
    └── <new_project>/
        ├── requirements.txt
        ├── main.py
        └── libs/
            ├── __init__.py
            └── <module>.py
```

### Rules for every new project
- **Own folder**: one folder per project, no cross-project imports.
- **Own `requirements.txt`**: list only that project's direct dependencies.
- **Entry point**: name it `main.py` (preferred), `app.py`, `server.py`, or `run.sh` — `make run` auto-detects these in order.
- **Register in global deps**: add `-r <project_folder>/requirements.txt` to the root `requirements.txt`.
- **Scaffold with make**: run `make new-project PROJECT=projects/my_tool` to create the standard layout.
- **Thin entry point + `libs/`**: `main.py` must contain only argument parsing and a
  single call into `libs/`. All application logic belongs in `libs/<module>.py`.
  Keep `main.py` to ~15 lines maximum.
- **README required**: every project must have a `README.md`. Update it in the same
  commit as any feature change — new flags, log messages, exit codes, error conditions,
  and new `libs/` modules must all be reflected immediately.
- **Object-oriented `libs/`**: model domain concepts as classes, not collections of
  functions. Each class owns its state and validation (e.g. raise in `__init__` for
  invalid input). Use `@dataclass(frozen=True)` for immutable data containers.
  Avoid free-standing module-level functions unless they are pure utilities with no
  associated state.
- **Strong typing**: every function and method must have type hints on all parameters
  and the return value. Annotate class attributes in `__init__`. Annotate local
  variables when the type is not obvious from the right-hand side. Use `str | None`
  (union syntax, Python 3.10+) rather than `Optional[str]`.

### Running and syncing
```bash
make run PROJECT=tools/mcp_youtube           # run a project
make sync-project PROJECT=tools/mcp_youtube  # install only that project's deps
make new-project PROJECT=projects/my_tool    # scaffold a new project folder
make sync                                    # install all deps (global requirements.txt)
```

---

## Repo purpose

This repository demonstrates how Claude Code components work together:

- **Rules** (this `CLAUDE.md`): always-on project guidance and constraints
- **Skills** (`.claude/skills/*/SKILL.md`): reusable task playbooks (slash commands)
- **Agents** (`.claude/agents/*.md`): specialized subagents Claude can delegate to
- **MCP** (`.mcp.json` + local server): external tools Claude can call for real data/actions

## Claude component naming

- All repo-owned skills must use a prefix.
- Use `common-...` for reusable cross-domain skills such as project scaffolding, skill authoring, meetings, and general YouTube metadata work.
- Use `video_generation-...` for skills and agents that exist specifically to support AI video planning, prompt packaging, continuity control, or Seedance-oriented workflows.
- Prefer a small number of broader, composable skills over many tiny overlapping ones. If two skills are routinely used back-to-back by default, consider merging them.
- Treat legacy unprefixed video skills as deprecated. Future work should use the prefixed names documented in `.claude/README.md`.

## Global rules for this repo

- Prefer **progressive disclosure**: start with a short plan + the minimum useful output, then go deeper as needed.
- When producing an analysis, include an **Evidence** section (links, video ids, or raw fields) so conclusions are auditable.
- Do not invent metrics you cannot derive. If a value is unknown, label it **Unknown** and state what is needed to compute it.

## AI video production rules

- Treat **Seedance 2.0** as the default renderer for this repository unless the user explicitly asks for a different generator.
- Claude's job in AI video workflows is to produce **planning artifacts**, not media. Preferred outputs are prompt packs, shot lists, continuity bibles, voiceover maps, and asset checklists.
- For any video longer than a single short clip, lock a **Visual Bible** before writing scene prompts. At minimum this must freeze character wording, wardrobe, environment, lighting, camera language, and style anchors.
- For any multi-scene video, also define a **Continuity Bible** covering what must remain stable across scenes and what is allowed to vary.
- Prefer building long videos from **15-second scene units** that can be generated independently in Seedance and stitched later.
- When writing generation prompts, reuse the exact locked character and environment wording verbatim rather than paraphrasing. Consistency should be engineered, not implied.
- When packaging assets for Seedance, include explicit generation specs rather than just prose prompts. Say how many images to generate, what views are required, what must stay fixed, what file naming to use, and what makes an output acceptable.
- Default deliverables for a production-ready pack should include:
  - scene outline
  - visual bible
  - continuity bible
  - Seedance-ready prompts
  - character reference-set prompts
  - background reference-set prompts
  - reference-frame prompts
  - narration / voiceover timing
  - edit / assembly notes
- Do not claim that prompts will guarantee perfect identity consistency. Instead, explicitly call out drift risks and provide reinforcement language or fallback strategies.
- The canonical video workflow is:
  - `video_generation-reference-scout`
  - `video_generation-preproduction`
  - `video_generation-storyboard-master`
  - `video_generation-seedance-packager`
  - `video_generation-continuity-director`
  - `video_generation-assembly-planner`

## External APIs — known issues

- **YouTube API / trending feeds** return 403 without authentication. When encountering YouTube API or trending feed access issues, immediately fall back to `WebSearch`-based approaches or `yt-dlp` rather than retrying API calls. Do not spend more than one attempt on a failing endpoint before switching strategies.
- When a research task combines multiple strict filters (recency + virality + language + AI-generated), start with broader criteria and narrow down. Set an explicit search-attempt budget (e.g., max 10 queries) and fall back to relaxed constraints before exhausting it.

## Content defaults

- All content generation skills and outputs should default to **Chinese (中文)** unless explicitly told otherwise.
- Character limits defined in skill files must be respected — validate outputs against them before reporting success.

## Environment setup

- Before attempting CUDA/GPU-dependent Python projects, first verify compatibility:
  1. Run `nvidia-smi` to check driver and CUDA driver version.
  2. Run `nvcc --version` to check toolkit version.
  3. Confirm PyTorch CUDA version matches (`python -c “import torch; print(torch.version.cuda)”`).
  4. Do **not** proceed with model downloads or heavy setup until the environment is confirmed working.
- Report any version mismatches to the user immediately rather than attempting repeated reinstalls.

## YouTube analysis rules

- Only analyze **publicly accessible** YouTube data.
- If the user asks to “scrape” content, use the project MCP server (`youtube`) when available; otherwise fall back to `yt-dlp` in the shell. If MCP is unavailable and `yt-dlp` fails, use `WebSearch` as a final fallback.
- Keep outputs structured and skimmable:
  - a short executive summary
  - a table of sampled videos
  - themes/patterns grounded in that sample
  - actionable recommendations

## Quick start (what to try in Claude Code)

- Run the skill directly:
  - `common-youtube-info` for fast public YouTube metadata work
- Or ask naturally and let Claude delegate to the `youtube-researcher` subagent:
  - “Use `video_generation-youtube-researcher` to analyze this channel and suggest 10 next video ideas: https://www.youtube.com/@SomeChannel”
