---
name: video_generation__topic-scout
description: Search online for trending or evergreen topics suited for AI video generation, evaluate them for AI-friendliness, and produce a validated storyboard. Use this when the user wants to find a new video topic, brainstorm AI video ideas, scout viral trends for short-form video, or kickstart a new AI video project.
---

# Topic Scout — AI Video Topic Discovery & Storyboard

Find the best topic for an AI-generated video, validate it for AI-friendliness, and produce a foundation storyboard ready for downstream scene/character breakdown.

## Modes

### Short Video Mode (under 60 seconds)

**Strategy: Trending Topic Mining**

1. Search the web for current trending topics across platforms (Twitter/X, TikTok, YouTube Shorts, Reddit, Google Trends).
2. Filter for topics that are:
   - Peaking NOW or within the last 48 hours
   - Visual and dramatic (not text-heavy news)
   - Emotionally resonant (awe, humor, curiosity, surprise)
   - Simple enough to convey in under 60 seconds
3. Prioritize topics with high shareability and comment-bait potential.

### Long Video Mode (1–5 minutes)

**Strategy: Evergreen Curiosity**

1. Search for proven "what if" / "how does X work" / "things you didn't know" topics with steady search volume.
2. Look for topics that have worked well on YouTube (high view-to-sub ratio) but haven't been done as AI video.
3. Favor topics with:
   - Clear narrative arc (setup → escalation → payoff)
   - Multiple distinct visual scenes (not talking heads)
   - Universal appeal across cultures

## Workflow

### Step 1 — Research

Use `WebSearch` to find candidate topics. Gather at least 6–8 raw candidates.

For **short mode**: search for trending topics, viral moments, current events with visual potential.
For **long mode**: search for evergreen curiosity topics, popular explainers, "most amazing" lists.

### Step 2 — AI-Friendliness Evaluation

Score each candidate on the **AI Generation Feasibility Scorecard** (0–10 per criterion, out of 60 total):

| Criterion | What it measures |
|-----------|-----------------|
| **Visual Simplicity** | Can scenes be described in 1–2 sentences? Few complex interactions? |
| **Character Feasibility** | No real celebrities or public figures needed? Generic/fictional characters work? |
| **Scene Variety** | Multiple distinct environments/moments? Not just one static setting? |
| **Motion Friendliness** | Avoids fast action, crowds, sports, or complex physics? Slow/medium motion works? |
| **Emotional Hook** | Strong feeling in the first 3 seconds? Curiosity, shock, awe, humor? |
| **Narrative Clarity** | Can the story be understood without dialogue? Visual storytelling works? |

**Threshold**: Only topics scoring **40+/60** proceed.

### Step 3 — Present Candidates (Rich Detail)

Each candidate must contain enough detail for a downstream agent to directly extract scene prompts, character reference prompts, and background prompts **without any further research**. Present each candidate in this format:

```markdown
## Candidate {N}: {Title (English)} | {Title (Chinese)}

### Overview

**Mode**: Short / Long
**Duration**: {target duration}s
**Aspect Ratio**: 9:16 (default) or as specified
**Source/Trend**: {where you found it, why it's trending or has proven appeal}
**One-line pitch**: {the hook in one sentence}
**Hashtags**: {8–12 hashtags, mixed Chinese + English}

### AI Feasibility Score: {score}/60

| Criterion | Score | Notes |
|-----------|-------|-------|
| Visual Simplicity | {x}/10 | {why this score} |
| Character Feasibility | {x}/10 | {why this score} |
| Scene Variety | {x}/10 | {why this score} |
| Motion Friendliness | {x}/10 | {why this score} |
| Emotional Hook | {x}/10 | {why this score} |
| Narrative Clarity | {x}/10 | {why this score} |

**Drift Risks**: {what might be hard for AI to render consistently}
**Mitigation Strategies**: {how to reduce each drift risk}

### Narrative

{3–5 paragraph prose telling the full story from opening frame to final frame.
Must be vivid and specific — describe what the viewer SEES, not abstract concepts.
Include sensory details: colors, textures, movement, lighting shifts, emotional beats.
This is the primary source a downstream agent will use to understand the story.}

### Character Constraint

**Maximum 1–2 characters per video.** Single-character stories are preferred for AI generation reliability. Two characters are allowed only when the narrative absolutely requires interaction. Never exceed two characters — crowd scenes, group shots, and ensemble casts are out of scope.

### Characters (3D 模型三视图规范)

For EACH character, generate **3 independent view prompts** (front / side / back) in Chinese, each containing ALL of the following (缺一不可):

- **Name/Role**: {e.g., "The Child (主角)"}
- **基础信息**: age, gender, ethnicity/nationality, height, build
- **五官细节**: brow shape, eye shape, nose shape, lip shape, face shape, skin tone + texture (细腻/粗糙/皱纹), makeup (无妆/淡妆/浓妆 + specific effects)
- **发型细节**: hair color (hex), length, style, hair texture
- **穿搭细节**: top, bottom, shoes, accessories — specify material, color (hex), pattern, fit for each
- **神态细节**: expression tied to story emotion, specific eye/gaze description
- **肢体姿态**: natural pose (standing/sitting/holding props) appropriate to each view angle
- **Props**: anything they carry or interact with
- **Body Language**: how they move, posture, energy level
- **Arc**: how their appearance/expression changes from start to end
- **参考说明**: 末尾统一标注 —— 以附带的 3 张人物三视图参考图为基准生成 3D 人物模型
- **画质要求**: 末尾统一标注 —— 4K 超高清，电影级光影，真实质感，全身无裁切，纯白背景便于模型提取
- **Prompt Fragment**: {a reusable 20–40 word description to paste into every generation prompt}

### Environments / Backgrounds (3 张不同视角规范)

For EACH distinct environment, generate exactly **3 prompts** from different viewing angles (远景 + 近景 + 特写, or 正面 + 侧面 + 俯视/仰视). All 3 must depict the **same** scene with unified details.

Each prompt must include (缺一不可):

- **Name**: {e.g., "The Wasteland", "The Underwater Cave"}
- **场景信息**: scene name, purpose in the story
- **Setting**: location type, time of day, season, weather
- **环境细节**: indoor/outdoor, materials, colors, condition
- **Key Elements**: 3–5 must-have visual elements that define this environment
- **道具细节**: position, material, color, and texture of every prop in the scene
- **Color Palette**: 3–4 dominant colors with hex codes
- **光影细节**: light source type, angle, effect (柔光/逆光/阴影 etc.), color temperature
- **氛围色调**: overall mood + color style (暖/冷/高饱和/低饱和)
- **Atmosphere**: fog, particles, volumetric light, dust, rain, etc.
- **Scale/Depth**: how vast or intimate the space feels
- **Sound Impression**: what the viewer imagines hearing — informs mood even in silent
- **参考说明**: 末尾统一标注 —— 以附带的 3 张不同视角背景参考图为基准搭建 3D 场景
- **画质要求**: 末尾统一标注 —— 4K 超高清，极致细节，真实质感，无人物仅场景道具，电影级氛围
- **Prompt Fragment**: a reusable 20–40 word description to paste into every generation prompt

### Scene Breakdown

For EACH scene (target 15-second units):

| # | Duration | Shot Type | Camera | Action Summary |
|---|----------|-----------|--------|----------------|
| 1 | {x}s | {ECU/CU/MS/MFS/WS/EWS} | {movement} | {1-sentence action} |
| ... | | | | |

For each scene, also provide:
- **What the viewer sees**: {2–3 sentence detailed visual description}
- **Emotion/Mood**: {what the viewer should feel}
- **Lighting in this shot**: {specific to this moment}
- **Key motion**: {what moves, how fast, in what direction}
- **Transition**: {how this shot connects to the next}

### Visual Style

- **Overall Style**: {e.g., cinematic photorealistic, stylized illustration, anime-inspired}
- **Reference Look**: {camera/film reference, e.g., "Arri Alexa look, shallow DoF"}
- **Color Strategy**: {how color changes across the story arc}
- **Style Anchors**: {a reusable prompt prefix for ALL shots, ~20 words}

### Music / Audio Direction

- **Overall Mood**: {genre, tempo, instruments}
- **Arc**: {how the audio evolves from start to end}
- **Key Moments**: {which shots need audio emphasis — hits, silence, swells}

### Why This Works for AI Video

- **Virality angle**: {1–2 sentences}
- **AI generation strengths**: {what about this topic is easy for AI}
- **Rewatch / engagement hooks**: {what makes viewers comment, share, or loop}
```

**Ask the user to pick one** (or request more candidates). When generating a batch list (e.g., "find me top 10 topics"), use the same rich format for every entry.

### Step 4 — Develop Foundation Storyboard

Once the user confirms a topic, produce a full storyboard document with:

1. **Title** — bilingual (Chinese + English) catchy title
2. **Description** — 2–3 sentence pitch with hashtags (Chinese + English)
3. **Visual Bible** — style, aspect ratio, color palette, lighting, mood, characters, environments, style anchors
4. **Enhanced Narrative** — the story in prose form, vivid and specific
5. **Storyboard** — shot-by-shot breakdown, each shot with:
   - Duration (target 15s scene units, can be shorter)
   - Shot type and camera movement
   - Action description
   - Audio/mood notes
   - Transition to next shot
   - Generation prompt (reusing exact Visual Bible wording)
6. **Production Notes** — total duration, shot count, music mood, key consistency notes

Use the exact format demonstrated in existing storyboards in `ai_videos/`.

### Step 5 — Save Output

Save the storyboard to:

```
ai_videos/{date}/{story_id}/story/storyboard.md
```

Where:
- `{date}` = today's date in `YYYY-MM-DD` format
- `{story_id}` = a short snake_case slug derived from the title (e.g., `tornado_cat`, `code_world`)

Also save the research evidence to:

```
ai_videos/{date}/{story_id}/story/research.md
```

The research file should contain:
- Search queries used
- Raw candidate list with scores
- Links/sources for the chosen topic
- Rationale for selection

## Output contract

- Always ask for user confirmation before writing the storyboard
- Always include the AI Feasibility Scorecard — never skip scoring
- Never claim AI will perfectly render any topic — call out drift risks explicitly
- Reuse exact character/environment wording in every prompt (no paraphrasing)
- Target 15-second scene units for Seedance compatibility
- Default to 9:16 vertical (mobile-first) unless user specifies otherwise
- The storyboard is the FINAL output — it must be complete enough for a downstream agent to extract scenes, characters, and prompts without needing to re-research the topic

## Edge cases

- If no candidates score above 40/60, report this honestly and suggest the user provide a niche or constraint to narrow the search.
- If the user provides a topic directly, skip Steps 1–3 and go straight to evaluation + storyboard.
- If the user wants both short and long versions of the same topic, produce two separate storyboards.
- Default mode is **short** unless the user specifies otherwise.
