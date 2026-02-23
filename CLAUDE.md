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
        └── main.py
```

### Rules for every new project
- **Own folder**: one folder per project, no cross-project imports.
- **Own `requirements.txt`**: list only that project's direct dependencies.
- **Entry point**: name it `main.py` (preferred), `app.py`, `server.py`, or `run.sh` — `make run` auto-detects these in order.
- **Register in global deps**: add `-r <project_folder>/requirements.txt` to the root `requirements.txt`.
- **Scaffold with make**: run `make new-project PROJECT=projects/my_tool` to create the standard layout.

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

## Global rules for this repo

- Prefer **progressive disclosure**: start with a short plan + the minimum useful output, then go deeper as needed.
- When producing an analysis, include an **Evidence** section (links, video ids, or raw fields) so conclusions are auditable.
- Do not invent metrics you cannot derive. If a value is unknown, label it **Unknown** and state what is needed to compute it.

## YouTube analysis rules

- Only analyze **publicly accessible** YouTube data.
- If the user asks to “scrape” content, use the project MCP server (`youtube`) when available; otherwise fall back to `yt-dlp` in the shell.
- Keep outputs structured and skimmable:
  - a short executive summary
  - a table of sampled videos
  - themes/patterns grounded in that sample
  - actionable recommendations

## Quick start (what to try in Claude Code)

- Run the skill directly:
  - `/youtube-channel-audit https://www.youtube.com/@SomeChannel 30`
- Or ask naturally and let Claude delegate to the `youtube-researcher` subagent:
  - “Analyze this channel and suggest 10 next video ideas: https://www.youtube.com/@SomeChannel”
