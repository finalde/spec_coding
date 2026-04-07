---
name: common__youtube-info
description: Fetch public YouTube video, channel, playlist, or search metadata. Use this whenever the user wants YouTube URLs analyzed, channel uploads listed, video counts or views extracted, or public metadata gathered at scale.
---

# Common YouTube Info

Fetch public YouTube metadata efficiently and present it in a structured format.

## Preferred Data Order

1. use the repository's YouTube MCP server when available
2. fall back to `yt-dlp`
3. fall back to lightweight public endpoints for minimal metadata

## Capabilities

- single-video metadata
- channel or playlist listing
- search results
- batch metadata collection

## Output Expectations

- single video: structured bullet block
- multiple videos: markdown table
- large result sets: short summary plus table

## Rules

- only use public data
- clearly mark missing fields as `Unknown`
- prefer fast listing methods before expensive per-video detail fetches
