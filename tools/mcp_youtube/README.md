## YouTube MCP server (local)

This is a small local MCP server that exposes YouTube scraping as tools, powered by `yt-dlp`.

### What you get

- `youtube.list_channel_videos(channel_url, limit=30)`
- `youtube.get_video_details(video_url)`

### Install

From repo root:

```bash
make venv
```

This uses `uv` to create `.venv` and sync the repo-level `requirements.txt`.
The MCP dependencies are included from `tools/mcp_youtube/requirements.txt`.

### Configure Claude Code

This repo includes a project MCP config at `.mcp.json` registering the server as `youtube`.

If Claude Code doesn’t auto-enable project MCP servers in your setup, enable it in your Claude Code settings or via `/config`.

### Quick manual smoke test (optional)

```bash
make run-mcp
```

You should see the server start (stdio transport). In practice, Claude Code launches it for you.

