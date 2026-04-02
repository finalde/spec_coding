---
name: storyboard-master
description: "电影分镜大师：将文字描述拆解为短视频分镜脚本，生成 AI 图片/视频 prompt。Use this skill whenever the user wants to create storyboards, break a narrative into shots, generate image prompts for video production, or says things like '帮我做分镜', '拆解成镜头', 'create storyboard', 'break this into shots', '生成分镜', '短视频脚本'. Also trigger when the user provides a story/scene description and wants visual prompts for AI image/video generation tools like Midjourney, DALL-E, Flux, Seedance, Kling, or Sora."
---

# Storyboard Master 分镜大师

Transform narrative text into grouped 15-second video segments with AI-generation-ready prompts, optimized for vertical video (9:16).

## Core Workflow

```
用户描述 → 润色叙事 → 视觉圣经 → 拆分 Group → 每组分镜 → Prompt 生成 → 输出文件
```

### Step 1: Receive & Enhance the Narrative

When the user provides a description:

1. **Understand the core story** — what is the emotional arc? What is the hook?
2. **Polish the narrative** — fill gaps in logic, sharpen imagery, add sensory detail. Each 15s group needs its own micro-arc (hook → action → beat).
3. **Present the enhanced version** to the user for confirmation before proceeding. Show what you changed and why.

If the description is vague or too short, interview the user:
- What emotion should the viewer feel?
- Is there a specific setting or time period?
- Any character details (age, look, clothing)?
- Reference videos or visual style inspiration?

### Step 2: Establish the Visual Bible

Before writing any shot, define a **Visual Bible** that locks the visual identity across ALL groups and shots. This is the single most important step for consistency.

```
## Visual Bible

**Style**: [e.g., cinematic photorealistic / anime / oil painting]
**Aspect Ratio**: 9:16 (vertical, mobile-first)
**Color Palette**: [specific colors]
**Lighting**: [specific lighting setup]
**Mood/Atmosphere**: [emotional tone]

### Characters
- **Character A**: [detailed physical description — be specific enough to repeat verbatim in every prompt]

### Environment
- **Primary Location**: [detailed description]
- **Time of Day / Weather / Season**: [specifics]

### Style Anchors
[Short phrase prepended to EVERY prompt. Example: "cinematic photo, 9:16 vertical, sharp focus, Arri Alexa look, film grain"]
```

Determine these automatically from the narrative content. The style should serve the story.

### Step 3: Split into 15-Second Groups

Divide the full story into **groups of ~15 seconds each**:

- **15s story** → 1 group
- **30s story** → 2 groups
- **45s story** → 3 groups
- **60s story** → 4 groups

Each group is a self-contained mini-chapter with its own emotional beat. Think of them as "scenes" in a film.

For each group, decide:
- **Group theme/label** — a short descriptive name (e.g., "the_encounter", "the_chase")
- **Number of shots** — typically 3-5 per 15s group
- **Narrative beat** — what this group accomplishes in the story

Ensure smooth narrative flow between groups — the last shot of group N should connect naturally to the first shot of group N+1.

### Step 4: Generate Shots & Prompts per Group

For each group, generate 3-5 shots. Each shot becomes one image prompt.

#### Prompt Format

Use the simple flat format:

```
Picture 1: [prompt text]

Picture 2: [prompt text]

Picture 3: [prompt text]
```

#### Prompt Rules

1. **所有提示词使用中文** — prompts must be written in Chinese. 标题和描述保持中英双语。
2. **Always start with the Style Anchors** from the Visual Bible (用中文表达，如"3D电影级渲染，9:16竖屏，戏剧性灯光")
3. **Describe characters using the SAME words** from the Visual Bible every time — never paraphrase
4. **Be specific about pose and expression** — "低头微微皱眉" not just "悲伤"
5. **Include lighting details** per shot
6. **Avoid negatives** — describe what IS in the scene, not what isn't
7. **Keep each prompt 80-120 Chinese characters equivalent** — detailed enough for consistency and rich generation
8. **Total prompts per group must be under 600 words**
9. **Avoid text/words in prompts** — AI generators handle text poorly

#### Shot Variety

Vary shot types across each group. Never use the same framing twice in a row:

- **ECU (Extreme Close-up)**: Eyes, hands, details — emotion
- **CU (Close-up)**: Head and shoulders
- **MS (Medium Shot)**: Waist up — most versatile
- **FS (Full Shot)**: Entire body + environment
- **Wide/Establishing**: Environment dominant
- **Low/High Angle**: Power/vulnerability
- **Dutch Angle**: Tension (use sparingly)

### Step 5: Generate Script / Voiceover Lines (台词/旁白)

For each group, write the spoken lines — either character dialogue or narrator voiceover — that accompany the visuals. These are the words a viewer would hear while watching.

**Guidelines:**
- Write in Chinese by default (the primary audience). Add English translation if the user requests it.
- Match the tone to the visuals: poetic for atmospheric pieces, punchy for action, emotional for drama.
- Each group's lines should last ~15 seconds when read aloud (~40-60 Chinese characters per group). Do NOT overwrite — silence is powerful.
- Mark whether each line is **旁白 (voiceover/narration)** or **角色台词 (character dialogue)** with the speaker name.
- If a shot has no dialogue, mark it as **[静默]** (silence) or **[音乐]** (music only) — don't force words onto every shot.
- Lines should align with the shot sequence: indicate which shot(s) each line covers.

**Output**: Save as `lines.md` in each group subfolder.

```markdown
# Group X — Lines 台词

Shot 1: [静默]
Shot 2: （旁白）台词内容...
Shot 3: （角色A）台词内容...
```

### Step 6: Generate 3D Asset Reference Prompts (角色与场景 3D 建模参考)

Extract all **key characters** and **key scenes/environments** from the story. For each, write **one single prompt** that produces a multi-angle reference sheet image — all views arranged in a grid within one picture. This is more efficient and keeps proportions/style locked across angles.

Save as `3d_references.md` in the root output folder.

#### Format

Each character or environment gets exactly **one prompt**. Inside the prompt, use bold markers (`**Top-left: front view**`, etc.) to specify the grid layout and what each panel shows.

```markdown
# 3D 建模参考提示词

## 角色

### {角色名称}
3D角色模型转面参考图，四个视角以2×2网格排列，纯白背景，摄影棚灯光。主体：[Visual Bible中的完整角色描述]。**左上：正面视角**，全身T-pose，展示[正面关键细节]。**右上：右侧面视角**，全身T-pose，展示[侧面关键细节]。**左下：背面视角**，全身T-pose，展示[背面关键细节]。**右下：细节特写面板**，分为[头部特写描述]和[标志性特征特写描述]。

### {变形过程}（如有角色变形）
3D变形序列参考图，四个阶段以1×4横条排列，深色背景，戏剧性灯光。主体：[变形主体描述]。**阶段1（最左）：原始形态**——[描述]。**阶段2：[阶段名]**——[描述]。**阶段3：[阶段名]**——[描述]。**阶段4（最右）：完成体**——[描述]。

## 场景

### {场景名称}
3D环境参考图，两个视角上下排列，中性背景，戏剧性灯光。场景：[Visual Bible中的完整场景描述]。**上方面板：[角度]全景**，展示[全景关键细节]。**下方面板：[第二角度/细节]**，展示[不同视角或关键细节]。
```

#### 3D 参考提示词规则
1. **所有提示词使用中文** — 与分镜提示词保持一致。
2. **一条提示词 = 一张参考图** — 所有角度排列在一张生成图中（角色2×2网格，变形过程1×4横条，场景上下两幅）。
3. **使用粗体视角标记** — `**左上：正面视角**`、`**右下：细节特写**`、`**阶段1（最左）**` 等，指导AI生成器在网格中放置各角度。
4. **角色使用纯白/摄影棚背景** — "纯白背景，摄影棚灯光" 隔离主体。场景可使用符合氛围的戏剧性灯光。
5. **角色描述保持一致** — 使用 Visual Bible 中完全相同的角色/场景描述，逐字复制，不要改写。
6. **角色使用中性姿势** — T-pose 或自然站立，不要动作姿势。变形序列例外，可展示各阶段动态。
7. **包含材质纹理细节** — 金属质感、织物类型、表面磨损、发光效果。
8. **每条提示词 120-200 字** — 一条提示词覆盖所有角度，需要比单视角提示词更多篇幅。

### Step 7: Generate Title & Description

Create a compelling title and description in both Chinese and English.

**Title**: Short, punchy, curiosity-driven. Works on Douyin/TikTok/YouTube Shorts. Chinese version should feel native, not translated.

**Description**: 2-3 sentences that hook the viewer. Include hashtags.

### Step 8: Output Structure

Create a task ID (short descriptive slug, e.g., `lonely_astronaut`).

```
ai_videos/{YYYY-MM-DD}_{task_id}/
├── all_prompts.md          ← ALL shot prompts across all groups, numbered sequentially
├── 3d_references.md        ← 角色多角度 + 场景 3D 建模参考 prompts
├── group_01_{label}/
│   ├── prompts.md          ← prompts for this 15s group only
│   └── lines.md            ← 台词/旁白 for this group
├── group_02_{label}/
│   ├── prompts.md
│   └── lines.md
├── group_03_{label}/
│   ├── prompts.md
│   └── lines.md
└── group_04_{label}/
    ├── prompts.md
    └── lines.md
```

#### all_prompts.md format

```markdown
# {Title Chinese} | {Title English}

## Title
**中文**: ...
**English**: ...

## Description
**中文**: ...
**English**: ...
**Hashtags**: ...

## All Prompts

Picture 1: [prompt]

Picture 2: [prompt]

...

Picture N: [prompt]
```

Prompts are numbered sequentially across all groups (1, 2, 3... through the entire story).

#### group_XX_{label}/prompts.md format

```markdown
# Group X — {label Chinese} | {label English}

Picture 1: [prompt]

Picture 2: [prompt]

Picture 3: [prompt]
```

Picture numbers restart at 1 within each group file. Keep it simple.

## Examples

**Example — 1 minute story (4 groups):**

User: "一个外卖小哥在暴风雨中送最后一单"

Output structure:
```
ai_videos/2026-03-23_delivery_storm/
├── all_prompts.md                    (12 prompts total)
├── group_01_the_order/
│   ├── prompts.md                    (3 prompts)
│   └── lines.md                      (台词/旁白)
├── group_02_the_storm/
│   ├── prompts.md                    (3 prompts)
│   └── lines.md
├── group_03_the_struggle/
│   ├── prompts.md                    (3 prompts)
│   └── lines.md
└── group_04_the_delivery/
    ├── prompts.md                    (3 prompts)
    └── lines.md
```

**Example — 15 second story (1 group):**

User: "一个女生在雨中等人"

Output structure:
```
ai_videos/2026-03-23_rain_wait/
├── all_prompts.md                    (3 prompts)
└── group_01_waiting_in_rain/
    ├── prompts.md                    (3 prompts)
    └── lines.md                      (台词/旁白)
```

## Edge Cases

- **No characters**: Focus on environment and objects. Still apply shot variation.
- **Very short description** (< 20 words): Interview the user for more detail.
- **User specifies exact shot count or group count**: Follow their instruction, override defaults.
- **User wants a specific style**: Override auto-detected style with their preference.
- **Single scene, no story progression**: Treat as 1 group, vary camera angles to create visual interest.
