---
name: youtube-info
description: "Fetch YouTube video info, metadata, and channel data efficiently at scale. Use this skill whenever the user asks about YouTube videos, channels, or playlists — including requests like 'get info on this video', 'what are the recent uploads from this channel', 'pull metadata for these YouTube links', 'how many views does this video have', 'list videos from a playlist', or 'scrape this YouTube channel'. Also trigger when the user pastes YouTube URLs and wants details extracted, or when building datasets from YouTube content. Works without API keys using yt-dlp and public endpoints."
---

# YouTube Info

Extract video metadata, channel listings, and playlist contents from YouTube — efficiently and at scale, with no API key required.

## How It Works

This skill uses a two-tier data fetching strategy:

1. **MCP server (`youtube`)** — preferred when available. Provides `list_channel_videos` and `get_video_details` tools backed by yt-dlp. Check if the `youtube` MCP server is connected before falling back.
2. **Direct yt-dlp via Bash** — fallback when MCP is unavailable. Same underlying tool, called directly.
3. **WebFetch + oEmbed** — lightweight fallback for basic info (title, author, thumbnail) when yt-dlp is not installed.

Always try tier 1 first, then tier 2, then tier 3.

---

## Capabilities

### 1. Single Video Metadata

Extract rich metadata for one video.

**Via MCP (preferred):**
Use the `get_video_details` tool with the video URL.

**Via yt-dlp CLI (fallback):**
```bash
yt-dlp -j --no-download "VIDEO_URL"
```

**Via oEmbed (minimal fallback):**
Use WebFetch to hit:
```
https://www.youtube.com/oembed?url=VIDEO_URL&format=json
```
This returns only: title, author_name, author_url, thumbnail_url, and embed HTML.

**Fields to extract and present:**

| Field | Source key | Notes |
|-------|-----------|-------|
| Title | `title` | |
| Channel | `channel` or `uploader` | |
| Upload date | `upload_date` | Format: YYYYMMDD → reformat to YYYY-MM-DD |
| Duration | `duration` | Seconds → format as HH:MM:SS or MM:SS |
| Views | `view_count` | Format with commas |
| Likes | `like_count` | May be null |
| Description | `description` | Truncate to first 500 chars in summaries |
| Tags | `tags` | Array of strings |
| Categories | `categories` | Array of strings |
| Thumbnail | `thumbnail` | URL to best thumbnail |
| URL | `webpage_url` | Canonical URL |

### 2. Channel Video Listing

List recent videos from a channel or playlist.

**Via MCP (preferred):**
Use `list_channel_videos` with channel/playlist URL and a limit (default 30, max 100).

**Via yt-dlp CLI (fallback):**
```bash
yt-dlp --flat-playlist -J --playlist-end N "CHANNEL_OR_PLAYLIST_URL"
```

The `--flat-playlist` flag is critical for performance — it fetches only index-level metadata (title, id, duration, view_count) without downloading full video pages. This makes channel scans fast even for channels with hundreds of videos.

**Output:** A table with columns: #, Title, Date, Duration, Views, URL

### 3. Batch Video Metadata

When the user provides multiple video URLs or wants details on many videos from a channel listing:

**Strategy for scale:**
- For **up to 5 videos**: fetch details sequentially, one `get_video_details` or `yt-dlp -j` call per video.
- For **6-20 videos**: use parallel subagents (Agent tool) — spawn one per video to fetch in parallel. Each subagent should use `yt-dlp -j --no-download "URL"` and return the JSON.
- For **20+ videos**: use `--flat-playlist` to get the index-level metadata (which includes title, views, duration, upload_date for most videos) rather than fetching full details for each. Only fetch full details for specific videos the user cares about.

This tiered approach keeps things fast — a 100-video channel scan takes seconds with `--flat-playlist`, whereas fetching full details for each would take minutes.

### 4. Playlist Contents

Playlists work identically to channels — same URL patterns, same `--flat-playlist` approach.

```bash
yt-dlp --flat-playlist -J "PLAYLIST_URL"
```

### 5. Search (Limited)

yt-dlp supports YouTube search:
```bash
yt-dlp --flat-playlist -J "ytsearch10:QUERY"
```
This returns up to N results for the search query. Useful when the user wants to find videos on a topic.

---

## Output Formatting

Present results in clean, skimmable formats:

**Single video** — use a structured block:
```
## Video: [Title]
- **Channel**: ...
- **Uploaded**: YYYY-MM-DD
- **Duration**: MM:SS
- **Views**: 1,234,567
- **Likes**: 12,345
- **Tags**: tag1, tag2, tag3
- **URL**: https://...

### Description (first 500 chars)
...
```

**Multiple videos** — use a markdown table:
```
| # | Title | Channel | Date | Duration | Views | URL |
|---|-------|---------|------|----------|-------|-----|
| 1 | ...   | ...     | ...  | ...      | ...   | ... |
```

For large result sets (20+ videos), add a summary line at the top:
```
**Found 47 videos** | Total duration: 12h 34m | Avg views: 5,432
```

---

## Error Handling

- **yt-dlp not installed**: Tell the user to install it (`pip install yt-dlp` or `brew install yt-dlp`), then fall back to oEmbed for basic info.
- **Rate limiting**: If yt-dlp returns errors about too many requests, add `--sleep-interval 1` between fetches. For batch operations, slow down to 1 request per second.
- **Private/deleted videos**: Report them as "unavailable" in the results rather than failing the entire batch.
- **Age-restricted content**: yt-dlp may need cookies. Suggest `--cookies-from-browser chrome` if needed.
- **Invalid URL**: Validate URLs match YouTube patterns before fetching. Accept common formats:
  - `https://www.youtube.com/watch?v=VIDEO_ID`
  - `https://youtu.be/VIDEO_ID`
  - `https://www.youtube.com/@CHANNEL`
  - `https://www.youtube.com/channel/CHANNEL_ID`
  - `https://www.youtube.com/playlist?list=PLAYLIST_ID`

---

## Examples

**Example 1: Single video info**
User: "What's this video about? https://www.youtube.com/watch?v=dQw4w9WgXcQ"
Action: Fetch video details via MCP or yt-dlp, present structured metadata block.

**Example 2: Channel scan**
User: "List the last 20 videos from https://www.youtube.com/@mkbhd"
Action: Use `list_channel_videos` with limit=20, present as table sorted by date.

**Example 3: Batch with analysis**
User: "Get metadata for all videos in this playlist and tell me which ones performed best"
Action: Fetch via `--flat-playlist`, sort by view_count, present top performers with analysis.

**Example 4: Quick search**
User: "Find me some YouTube videos about Rust programming"
Action: Use `ytsearch10:Rust programming` via yt-dlp, present results as table.
