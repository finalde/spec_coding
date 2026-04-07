---
name: video_generation__reference-scout
description: Research winning AI-video references and convert them into usable production guidance. Use this whenever the user wants viral AI shorts collected, wants to reverse-engineer a niche, compare reference videos, extract hook and pacing patterns, or build a prompt library from existing AI-generated videos.
---

# Video Generation Reference Scout

This skill combines two jobs that are usually part of the same research step:

- scouting reference videos
- extracting reusable format and prompt patterns

## Modes

### Mode A: Viral Shorts Scout

Use when the user wants a list or report of strong AI-generated or AI-style short videos.

Deliver:

- ordered list of candidate videos
- public metadata
- original links
- recreated Chinese prompt blocks when requested

### Mode B: Trend Gap Brief

Use when the user wants higher-level strategy rather than a list.

Deliver:

- hook patterns
- pacing patterns
- visual motifs
- loop or payoff strategies
- what to copy vs. what to avoid

## Inputs

Accept any combination of:

- topic or niche
- reference channels
- specific YouTube URLs
- target audience
- runtime or platform constraints

Reuse `common__youtube-info` or `video_generation__youtube-researcher` when channel or video metadata work becomes substantial.

## Workflow

### 1. Define the research frame

Lock:

- platform
- content family
- target promise
- selection criteria (views threshold, duration limit, upload window, AI-generated flag)

### 2. Gather evidence

Collect only public evidence and record the exact references behind each conclusion.

Use `yt-dlp` for direct YouTube searches and channel scraping:

- Search: `yt-dlp "ytsearch50:<query>" --print "%(id)s|%(title)s|%(view_count)s|%(duration)s|%(upload_date)s|%(channel)s" --skip-download`
- Channel shorts: `yt-dlp --flat-playlist --print "%(id)s|%(title)s|%(view_count)s" "https://www.youtube.com/@<handle>/shorts"`
- Full metadata: `yt-dlp --print "%(id)s|%(title)s|%(view_count)s|%(duration)s|%(upload_date)s|%(channel)s" --skip-download "https://www.youtube.com/shorts/<id>"`
- Filter by duration/views: pipe through `awk -F'|' '{v=$3+0; d=$4+0; if(v>1000000 && d<=20) print}'`

Known high-performing AI shorts channels (as of April 2026):

- **kitten Storys** (UCIeZESv8skwy5Y0GJIwCqjQ) — kitten + transformer / autobots genre, 3D cartoon
- **VividNova AI** — monkey/dog rescue genre, 3D animal adventure
- **sora ai video generator free** (UC7tQKYftJRjQRMw1nujXZow) — emotional cat + tornado genre, Sora 2 realistic
- **NİKİ ai** (UCt8PQ00rvH4K70UPwm6Eq3Q) — kitten + transformer genre
- **facts rishuu 08** — monkey/puppy dance genre, ultra-short 5s clips

When `--flat-playlist` returns `NA` for duration or upload_date, fetch full metadata per-video with `--skip-download` instead.

### 3. Separate signal from surface

Explicitly distinguish:

- structural patterns worth copying
- optional style flourishes
- saturated clichés
- open opportunities

### 4. Translate for production

Turn research into instructions a production skill can use immediately.

### 5. Write Chinese prompts

For each selected video, reconstruct a Chinese generation prompt (AI视频提示词) covering:

- style and genre
- scene and background
- camera and framing (always note 竖屏9:16)
- lighting
- character description
- action sequence and pacing
- mood and color palette
- exact duration

## Output Formats

### Viral Scout Report

Save to `reports/shorts/YYYY-MM-DD.md`:

```markdown
# AI Shorts Scout Report

**Date**: YYYY-MM-DD
**Videos found**: N
**Selection criteria**: <criteria summary>
**Note**: <any caveats about data availability>

---

## 1. <Video Title>

- **Creator**: <channel name>
- **Views**: <view count>
- **Duration**: <Ns>
- **Uploaded**: <YYYY-MM-DD>
- **Link**: [Watch](https://www.youtube.com/shorts/<id>)

> **AI视频提示词：** <reconstructed Chinese generation prompt>

---
```

Repeat the video block for each entry, numbered sequentially and sorted by view count descending.

### Trend Gap Brief

```markdown
# Trend Gap Brief

## Executive Summary
- ...

## Evidence
- ...

## What Is Working
- ...

## What To Copy
- ...

## What To Avoid
- ...

## Production Implications
- ...
```
