---
name: ai-shorts-scout
description: "Find top 20 popular AI-generated YouTube Shorts, watch each video, and produce a detailed Chinese prompt for every video so it can be recreated with AI video tools. Use this skill whenever the user says things like 'find popular AI shorts', 'top AI-generated YouTube Shorts', 'scout AI shorts', 'find viral AI videos on YouTube', '找AI短视频', '热门AI视频', or '/ai-shorts-scout'. Also trigger when the user wants to build a prompt library from existing YouTube Shorts or wants to reverse-engineer viral short videos into AI generation prompts."
---

# AI Shorts Scout

Search YouTube for the top 20 most popular AI-generated / AI-style Shorts, watch each one, and produce a report with a detailed Chinese video-generation prompt per video.

## Output

A single Markdown file saved to:

```
reports/shorts/YYYY-MM-DD.md
```

The date is today's date. If the file already exists, append a counter: `YYYY-MM-DD-2.md`.

---

## Workflow

### Step 1: Search for popular AI-generated YouTube Shorts

Use multiple search queries via yt-dlp to find candidate videos. Run these searches in parallel:

```bash
yt-dlp --flat-playlist -J "ytsearch20:AI generated short film viral 2025 2026"
yt-dlp --flat-playlist -J "ytsearch20:sora AI video shorts viral"
yt-dlp --flat-playlist -J "ytsearch20:AI generated cinematic shorts most viewed"
yt-dlp --flat-playlist -J "ytsearch20:kling AI video shorts popular"
yt-dlp --flat-playlist -J "ytsearch20:runway gen 3 AI shorts viral"
yt-dlp --flat-playlist -J "ytsearch20:AI animation short film youtube shorts 2025 2026"
yt-dlp --flat-playlist -J "ytsearch20:人工智能生成短视频 热门"
yt-dlp --flat-playlist -J "ytsearch20:AI视频 爆款 shorts"
```

Also use WebSearch to find curated lists:

```
top AI generated YouTube Shorts 2026 most viewed
viral AI-made short videos YouTube 2025 2026 list
best sora kling runway AI shorts on YouTube
```

From WebSearch results, extract any specific video URLs mentioned.

### Step 2: Collect & Deduplicate Candidates

Merge all results. Deduplicate by video ID. For each candidate, extract:
- `id` (video ID)
- `title`
- `view_count`
- `duration` (must be <=60s to qualify as a Short)
- `url` → normalize to `https://www.youtube.com/shorts/{id}`

### Step 3: Filter for AI-generated content

From the candidate list, keep only videos that appear to be AI-generated. Signals:
- Title or description contains: AI, Sora, Kling, Runway, Pika, Midjourney, Minimax, Hailuo, 人工智能, AI生成, AI视频
- Channel is known AI video creator
- Visual style is clearly AI-generated (check description/comments)

If you have more than 20, sort by `view_count` descending and take the top 20.
If you have fewer than 20, broaden searches or include "AI-style" videos that could plausibly be recreated with AI tools.

### Step 4: Fetch full metadata for each video

For each of the 20 selected videos, fetch detailed metadata:

```bash
yt-dlp -j --no-download "https://www.youtube.com/shorts/VIDEO_ID"
```

Extract: title, channel, view_count, like_count, upload_date, duration, description, thumbnail URL.

### Step 5: Analyze video content and generate prompts

This is the critical step. For each video, you must carefully analyze its content to write a detailed prompt.

**How to analyze the video:**

1. **Read the title and description** — they often describe the scene
2. **Check the thumbnail** — use the thumbnail URL to understand the visual style, setting, and characters
3. **Read comments** (if accessible) — they often describe what happens
4. **Cross-reference** — search for the video title + "reaction" or "breakdown" to find descriptions of the content

**Then generate a Chinese prompt for each video following these strict rules:**

#### Prompt Rules

1. **Written entirely in Chinese** (Simplified)
2. **Must be a single continuous string** — NO line breaks, NO blank lines, NO paragraph breaks. One unbroken block of text.
3. **Must be under 500 Chinese characters** (not bytes, characters)
4. **Must cover these elements** (in this order within the prompt):
   - **画面风格** (visual style): cinematic / anime / 3D / photorealistic / etc.
   - **场景/环境** (scene/environment): location, weather, time of day, architecture, landscape details
   - **镜头** (camera): shot type, angle, movement, aspect ratio
   - **光线** (lighting): direction, color temperature, shadows, special effects
   - **人物** (characters): if present — age, gender, ethnicity, clothing, hair, expression, body position. If no person, describe the main subject in equal detail.
   - **动作** (action): what happens beat by beat, compressed into the character limit
   - **氛围/情绪** (mood/atmosphere): emotional tone, color palette
5. **End with technical specs**: 竖屏9:16, duration in seconds
6. **Do NOT include**: video title, creator name, hashtags, or meta-commentary in the prompt. The prompt is purely a visual generation instruction.

#### Prompt Template (for reference, do not output this template):

```
[风格锚点]，[场景环境描述]，[镜头类型与运动]，[光线描述]，[人物/主体详细描述]，[动作节拍压缩描述]，[氛围与色调]，竖屏9:16，[时长]秒。
```

### Step 6: Write the report

Generate the Markdown file with this exact structure:

```markdown
# AI Shorts Scout Report

**Date**: YYYY-MM-DD
**Videos found**: 20
**Selection criteria**: Top 20 most-viewed AI-generated YouTube Shorts

---

## 1. {Video Title}

- **Creator**: {channel name}
- **Views**: {view_count formatted}
- **Duration**: {seconds}s
- **Uploaded**: {YYYY-MM-DD}
- **Link**: [Watch](https://www.youtube.com/shorts/{video_id})

> **AI视频提示词：**{prompt — single line, no breaks, under 500 chars, Chinese}

---

## 2. {Video Title}

...

(repeat for all 20)
```

**Important formatting rules for the report:**
- The prompt MUST be on a single line after `**AI视频提示词：**` inside a blockquote `>`
- NO blank lines within the prompt
- Videos ordered by view count (highest first)
- Each video separated by `---`

### Step 7: Verify and save

Before saving:
1. Count that there are exactly 20 entries
2. Verify every link uses the format `https://www.youtube.com/shorts/{id}` — these must be real video IDs
3. Verify every prompt is under 500 Chinese characters (count them)
4. Verify no prompt contains line breaks

Save to `reports/shorts/YYYY-MM-DD.md`.

---

## Error Handling

- **yt-dlp not installed**: Fall back to WebSearch + WebFetch to find videos and metadata. Use oEmbed for basic info.
- **Can't determine if video is AI-generated**: Include it if the visual style suggests AI generation. Add a note in the report.
- **Fewer than 20 AI shorts found**: Include as many as found. Note the shortfall at the top of the report.
- **Video is unavailable/private**: Skip it, move to the next candidate.
- **Thumbnail not accessible**: Rely on title + description for content analysis.

---

## Example Output

```markdown
# AI Shorts Scout Report

**Date**: 2026-04-03
**Videos found**: 20
**Selection criteria**: Top 20 most-viewed AI-generated YouTube Shorts

---

## 1. The Last Sunset on Earth

- **Creator**: AI Cinema
- **Views**: 45,234,567
- **Duration**: 15s
- **Uploaded**: 2026-02-14
- **Link**: [Watch](https://www.youtube.com/shorts/abc123xyz)

> **AI视频提示词：**电影级写实风格，末日黄昏地球最后一缕阳光场景，广袤荒芜沙漠延伸至地平线尽头散落锈蚀建筑废墟，天际线处巨大红色太阳正缓缓坠落占据画面三分之一，天空从深紫渐变至血橙再到暗金色，低空漂浮着碎裂的大陆板块碎片。中景缓慢推近镜头，35mm电影镜头质感浅景深。逆光剪影中一名身穿破旧深灰色太空服的年轻女性背对镜头伫立沙丘顶端，短发被风轻拂，右手自然下垂左手微微抬起触碰头盔面罩，姿态沉静而不舍。暖橘侧光勾勒人物轮廓形成金色边缘光，地面长影拖向画面右下角。氛围苍凉壮美带克制的悲伤感，色调为深琥珀与暗紫主调，竖屏9:16，15秒。

---
```
