---
name: youtube-channel-audit
description: Scrape and analyze a YouTube channel (or playlist) and produce a clear, evidence-backed content strategy audit. Use when the user asks to analyze a YouTube channel, review a creator's content, identify themes, posting cadence, or suggest what to make next.
argument-hint: "[channel_or_playlist_url] [optional: max_videos]"
disable-model-invocation: true
---

## YouTube Channel Audit

You will produce an easy-to-skim audit of a YouTube channel (or playlist) using **public metadata**.

### Inputs

- URL: `$ARGUMENTS[0]` (required)
- `max_videos`: `$ARGUMENTS[1]` (optional; default 30; cap at 100)

If the URL is missing, ask for it.

### Data collection (preferred: MCP)

If the `youtube` MCP server is available, use it:

1. Call `youtube.list_channel_videos` with:
   - `channel_url`: the URL
   - `limit`: max_videos
2. For the top ~10 videos (or fewer if the limit is small), call `youtube.get_video_details` for richer fields.

If MCP is not available, fall back to `yt-dlp`:

```bash
yt-dlp --flat-playlist -J --playlist-end 30 "<CHANNEL_OR_PLAYLIST_URL>" > channel.json
```

Then (optionally) fetch details for a few videos:

```bash
yt-dlp -J "https://www.youtube.com/watch?v=<VIDEO_ID>" > video.json
```

### Output format (use this exact structure)

#### Executive summary
- 2–5 bullets: what the channel is about (as evidenced), what’s working, what’s unclear.

#### Snapshot (from the scraped sample)
- Channel / playlist URL
- Sample size (N)
- Date range covered (best-effort; otherwise “Unknown”)
- Upload cadence (qualitative if exact dates aren’t available)

#### Evidence table (sample)

Provide a table with at least 8 rows if available:

| Video | Published | Views | Duration | Primary topic signals |
|------|-----------|-------|----------|------------------------|
| [title](url) | YYYY-MM-DD or Unknown | # or Unknown | mm:ss or Unknown | 3–6 keywords |

Primary topic signals should be derived from title + tags + description keywords (not guessing).

#### Themes & patterns (evidence-backed)
- 3–7 themes. For each theme:
  - What it is
  - Why you believe it (cite 2–4 videos from the table)
  - What the audience likely expects next

#### Opportunities
- Content gaps (what’s missing given current themes)
- Packaging improvements (titles/thumbnails consistency, series naming, hooks)
- SEO opportunities (keyword clusters you can plausibly infer)

#### Recommendations (actionable)
- 5–10 specific video ideas
- Each idea includes: working title, target audience, why it fits (cite evidence), and a suggested format/structure.

### Guardrails

- Never claim subscriber counts, CTR, retention, RPM, or revenue unless explicitly provided.
- Don’t hallucinate published dates/views if the source data doesn’t contain them.
- If metadata is sparse (e.g., flat playlist only), say so and base conclusions primarily on titles.
