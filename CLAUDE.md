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
