# YouTube Shorts Affiliate Playbook — Copy-Paste Execution Guide

**Date:** 2026-04-19
**Base idea:** Money-loop deck #3, pivoted from TikTok to YouTube Shorts
**Channel profile:** New (<100 subs), bilingual (EN primary + ZH captions), 100% AI-generated
**Money loop:** High-ticket SaaS/AI affiliate ($50-$200/signup) via description + pinned comment
**MVP niche:** AI productivity tools → first Short demos ElevenLabs (self-use = authentic POV)
**MVP format:** "I Tried X for 7 Days" micro case-study (45-55s, matches our 60s pipeline; first-person POV satisfies YT inauthentic-content policy)
**Cadence:** 1-2 Shorts/week
**Budget:** ~$59/mo (ElevenLabs $22 + CapCut Pro $8 + Ayrshare $29)
**Human time:** ≤5 hr/wk

---

## 0. How to use this document

Work top-down. Every ▶ block is **copy-paste ready**. Every 🔗 is a URL to open. Every ✅ is a checkbox — tick it and move on. Don't optimize ahead; run the sequence as written for the first 3 Shorts, then iterate with the Week 4 rules.

When you're ready to delegate: say **"run the playbook, script Short #N demoing tool X"** and the agent_team picks up from §3.2 with your tool pick.

---

## 1. Week 0 Setup (one-time, ~4 hours total)

### 1.1 Channel hygiene (30 min)

Open YouTube Studio and do these in order. If the channel already exists, patch the gaps.

🔗 https://studio.youtube.com

- ✅ **Channel handle:** pick something tool-demo-flavored, e.g., `@aitoolsdaily` / `@aistacklab` / `@60secAI`. Short, memorable, works in both EN and ZH.
- ✅ **Channel name:** the handle spelled out (same in both tracks — don't localize it).
- ✅ **Channel banner:** Kling prompt: `Minimalist wide banner, "AI TOOLS / DAILY / 60s" in bold modern sans-serif, dark navy gradient background with subtle glowing circuit-line texture, 2560x1440, clean premium tech aesthetic, no logos.` Upload via Studio → Customization → Branding → Banner.
- ✅ **Channel avatar:** Kling prompt: `Minimalist app-icon style symbol, abstract spark or bolt in soft electric-blue gradient on dark navy, square 800x800, premium glass-morphic, no text.`
- ✅ **Channel description (bilingual, paste verbatim then fill channel handle):**

```
Weekly 60-second AI tool demos — what they are, what they actually do, and whether they're worth your money.

每周一分钟 AI 工具评测：它是什么、到底能做什么、值不值得买。

Affiliate disclosure: some links below go to affiliate programs. I earn a small commission if you sign up, at no cost to you. I only feature tools I've tested.
联盟披露：部分链接为联盟推广链接。如果你通过它们注册，我会获得一小笔佣金，对你没有额外费用。我只推荐自己测试过的工具。

Links → beacons.ai/<your_handle>
```

- ✅ **Channel default tags (Studio → Settings → Channel → Basic info → Keywords):** `AI tools, AI productivity, AI tool review, ChatGPT, Claude, ElevenLabs, AI demo, AI for creators, best AI tools 2026, AI 工具, AI 生产力`
- ✅ **Video upload defaults (Studio → Settings → Upload defaults):**
  - **Title prefix:** empty
  - **Description prefix** — paste verbatim:
    ```
    #ad — This video contains affiliate links. I earn a small commission if you sign up, at no extra cost to you.

    ```
  - **Tags:** `AI tools, AI productivity, Shorts, AI demo, AI for creators, AI tutorial, AI 工具`
  - **Visibility:** Public (you'll override to Unlisted during review, but default stays Public for speed)
  - **Category:** Science & Technology
  - **Language:** English (don't pick bilingual here; the CC track handles ZH)
  - **Audience:** "No, this video is not Made for Kids"
  - **Automatic chapters:** off (too short for Shorts)
- ✅ **AI disclosure toggle:** Studio → Settings → Channel → Advanced settings → under "Upload defaults" set *altered/synthetic content disclosure* to **Off by default** (we'll override case-by-case; AI-narrator + AI-b-roll demoing real products usually doesn't require it).
- ✅ **2-step verification ON** (required for future YPP and prevents account loss).

### 1.2 Bio link (10 min)

🔗 https://beacons.ai — sign up free.

- ✅ Create handle matching your YT handle.
- ✅ Add these 6 blocks in order (you'll swap Block 1/2 per new upload):

```
1. [EN] This video's tool →  (empty for now; will point to Dub link after Short #1)
2. [中文] 本期视频的工具 →  (empty for now)
3. [EN] All my AI stack  → (empty; will point to Dub /stack link)
4. [中文] 我的 AI 工具合集 → (empty; will point to Dub /stack-zh link)
5. Weekly "AI Tools Worth Your $" →  (placeholder — future Beehiiv signup)
6. Affiliate disclosure — "Some links are affiliate; I earn a small commission at no cost to you. / 部分链接为联盟推广，我会获得小额佣金，对你没有额外费用。"
```

- ✅ Copy your Beacons URL: `https://beacons.ai/<your_handle>` — this goes in your YT channel banner description + every Short description.

### 1.3 Link shortener (10 min)

🔗 https://dub.co — sign up free. Free tier = 1,000 events/mo + 25 links/mo (plenty for 3-6 months).

- ✅ Create a free workspace.
- ✅ In Dub → Settings → Domains, note your default `dub.sh` subdomain (you'll use it for affiliate short links).
- ✅ Bookmark this UTM pattern (you'll reuse it for every link — see §5):

```
https://<AFFILIATE_URL>?utm_source=yt-shorts&utm_medium=affiliate&utm_campaign=<short_id>&utm_content=<program>&utm_term=<hook_format>
```

### 1.4 Affiliate program applications (90 min, batched)

**Strategy:** apply to 2 networks + 5 direct programs in one block. Most approve in <24h; Tier 2 programs take 3-7 days.

**Network master accounts (apply FIRST — unlocks 80% of targets):**

1. 🔗 **PartnerStack** — https://app.partnerstack.com/join
   - Sign up → once inside, browse "Affiliate programs" and apply to: **ElevenLabs, HeyGen, Descript, Gamma, Fathom, Webflow, Kit**
2. 🔗 **Impact.com** — https://impact.com/creators/ → sign up as a Creator/Publisher
   - Inside, search + apply to: **Jasper, CapCut, Kling AI, Kajabi** (Kajabi will decline until you have a paid Kajabi sub — skip if it declines)

**Direct programs (apply next):**

3. 🔗 **Beehiiv partners** — https://partners.beehiiv.com/signup (sign up for a free beehiiv account first if you don't have one; the free plan qualifies)
4. 🔗 **Framer partners** — https://www.framer.com/partners (Dub-powered, usually auto-approves)
5. 🔗 **Opus Clip** — https://www.opus.pro/affiliate (Rewardful-powered, ~7-day review)
6. 🔗 **Synthesia** — https://www.synthesia.io/partners/affiliates
7. 🔗 **Skool** — https://www.skool.com/affiliate-program (3-7 day manual review)

**Do NOT apply to (confirmed blocked/closed Apr 2026):**
- Notion (closed) — set 60-day reminder to recheck
- Canva Canvassador general tier (closed; Empower/Edu only, not a fit)
- Kajabi (needs active paid Kajabi account — skip for now)

**After you apply — paste this template into a local tracking doc:**

```
| Program     | Applied | Status   | Approved | Commission | Cookie | Link-builder URL |
|-------------|---------|----------|----------|------------|--------|------------------|
| ElevenLabs  | 2026-…  | pending  |          | 22%×12mo   | 90d    |                  |
| HeyGen      | 2026-…  | pending  |          | 35% 3mo    | 30d    |                  |
| Beehiiv     | 2026-…  | pending  |          | 50%×12mo   | 60d    |                  |
| Framer      | 2026-…  | pending  |          | 50%×12mo   | 90d    |                  |
| Jasper      | 2026-…  | pending  |          | 25%×12mo   | 30d    |                  |
| Gamma       | 2026-…  | pending  |          | 30%×12mo   | 30d    |                  |
| Descript    | 2026-…  | pending  |          | $25 flat   | 30d    |                  |
| Synthesia   | 2026-…  | pending  |          | 25%×12mo   | 60d    |                  |
| Opus Clip   | 2026-…  | pending  |          | 25%×12mo   | 30d    |                  |
| Skool       | 2026-…  | pending  |          | 40%-for-life| 60d   |                  |
| Kit         | 2026-…  | pending  |          | 50%×12mo   | 60d    |                  |
| Webflow     | 2026-…  | pending  |          | 50%×12mo   | 90d    |                  |
```

### 1.5 Tool accounts (45 min)

- ✅ **ElevenLabs Creator** — 🔗 https://elevenlabs.io/pricing (~$22/mo). Generate an API key at Settings → API keys and save it to `.env`:
  ```
  ELEVENLABS_API_KEY=sk_...
  ```
- ✅ **CapCut Pro** — 🔗 https://www.capcut.com/pricing (~$8/mo). Install desktop app (Windows). Free tier works for the first 1-2 Shorts if you want to defer the spend.
- ✅ **Ayrshare Premium ($29/mo)** — 🔗 https://www.ayrshare.com/pricing — sign up, connect your YT channel, IG (if you have one), TikTok (if you want to cross-post). Save the API key. You can defer Ayrshare until Week 3; for Week 1-2 upload manually via YT Studio on your phone.
- ✅ **Seedance 2** — you already have this. **Verify Week 0:** open your Seedance account and confirm the generator UI loads (vendor-dependent — likely via the provider you purchased from, e.g., Volcengine/Jimeng for ByteDance direct, or Replicate/fal.ai if you have API access). Note the exact URL you use to start a generation. If you have API access on fal.ai (🔗 https://fal.ai/seedance-2.0), save the API key — it unlocks scripted generation in §3.4.2.
- ✅ **Kling AI** — generator URL: 🔗 https://app.klingai.com/global (English) or https://app.klingai.com (Chinese default). Confirm you can create images (text-to-image) and short video (image-to-video) on your plan.

### 1.6 Repo tool (30 min, optional but recommended)

Per `CLAUDE.md` monorepo conventions, scaffold one helper under `tools/`:

```bash
make new-project PROJECT=tools/shorts_narrator
```

Then add these two files (Claude Code can build them for you — just say "scaffold tools/shorts_narrator with an ElevenLabs narration CLI"):

- `tools/shorts_narrator/main.py` — ~15 lines, parse args, call `libs/narrator.py`
- `tools/shorts_narrator/libs/narrator.py` — a `Narrator` class that takes `script.md` + voice id + settings, writes `narration.mp3` + `timings.json`

This lets you run `make run PROJECT=tools/shorts_narrator` and get narration in 5 seconds. Defer to Week 2 if tight on time.

---

## 2. Daily + weekly rhythm (what the schedule looks like)

| Day | Activity | Time |
|---|---|---|
| **Monday** | Weekly review (§6 template) + decide Short #N tool pick + write script | 45 min |
| **Tuesday** | Produce Short #N (narration → visuals → stitch → metadata) | 90-120 min |
| **Wednesday** | Upload Short #N (morning) + T+6h metrics check evening | 15 min + 10 min |
| **Thursday** | T+24h metrics check; decide kill/iterate/scale | 15 min |
| **Friday** | If 2 Shorts/week: produce Short #N+1 | 90-120 min |
| **Saturday** | Upload Short #N+1 (morning) | 15 min |
| **Sunday** | Off (or batch-generate stills for next week) | — |

Total: ~4-4.5 hr/week steady state. Room for first-3-Shorts overhead.

---

## 3. Per-Short production SOP — copy-paste pipeline

### 3.1 Pick the tool to demo (5 min)

Pick from your **approved** affiliate programs (§1.4 tracker). Round-robin: don't demo the same tool twice in 2 weeks. MVP Short #1 = **ElevenLabs** (you already use it, auto-approved fastest, voice-tool narrated by the same voice is a nice meta-hook).

Capture the three inputs before scripting:

```
Tool name:           ElevenLabs
Tool positioning:    Realistic AI voice generation for creators
The-one-verb:        Clones voices from 60 seconds of audio
Obvious alternative: Descript, Play.ht
Differentiator:      Emotional control (whisper/shout/laughing) + 29 languages
One concrete demo:   Clone my voice → have it narrate a 3-line script
Measurable outcome:  30 seconds of pro narration for $0.04
Affiliate link:      https://elevenlabs.io/?via=<your code>  (from PartnerStack dashboard)
```

### 3.2 Write the script (10 min)

**Format for MVP:** #6 "I Tried X for 7 Days" micro case-study (45-55s, first-person POV satisfies YT inauthentic-content policy, high share-rate in AI-Twitter). Rotate to shorter formats (#5 Before/After 15-20s, #3 Stop Doing X, #1 One-Prompt Wonder) from Week 3 — see §4.

Paste this into Claude Code, fill in the braces:

```
Write a 60-second YouTube Short script in the "I Tried X for 7 Days" micro case-study format.

Tool: {Tool name}
Tool positioning: {positioning}
Demo concrete action: {one concrete demo}
Measurable outcome: {measurable outcome}
Affiliate program: {program}

Rules:
- 140-160 English words total (155 wpm = ~60s, aim for 58-62s final runtime)
- Beat structure + word targets:
  HOOK (0-3s)      7-9 words     Outcome claim + "I tested this for 7 days." Pattern-break.
  PROBLEM (3-10s)  15-20 words   Name the pain I felt before I started.
  TOOL (10-20s)    22-28 words   Tool name + one-line position + differentiator.
  DEMO (20-45s)    60-75 words   3 day-by-day action beats with metric overlay (time saved, $ saved).
  CTA (45-60s)     25-30 words   Quantified final outcome + FTC disclosure + affiliate CTA.
- Include an on-screen text overlay plan (one line per 5s segment).
- Output format: markdown table with columns [time, narration, on-screen-text, visual-cue].
```

Claude Code returns a structured script. Review for: tool name spelled correctly, no "guaranteed" / "free money" claims, on-screen `#ad` overlay in 0-3s.

### 3.3 Generate narration (5 min)

**If you built `tools/shorts_narrator/`:** save script to `scripts/s001.md`, then:

```bash
make run PROJECT=tools/shorts_narrator ARGS="--script scripts/s001.md --voice aaron --out out/s001/"
```

**Manual fallback (ElevenLabs web UI):**

1. 🔗 https://elevenlabs.io/app/text-to-speech
2. Voice: **Aaron** (default starter — authoritative tone, works for tech demos). Alternatives: Josh (documentary), Cassidy (casual). Pick one and stick with it for 10+ Shorts.
3. Settings: Stability 40%, Similarity 75%, Style 25%, Speaker Boost ON.
4. Model: `eleven_turbo_v2` for English-only.
5. Paste the narration column only (not timestamps/overlays). Generate → download `narration.mp3`.

**Cost:** ~$0.04/Short at Creator tier (well inside plan allowance).

### 3.4 Generate visuals (35-50 min)

Plan: **1-2 Seedance clips (15s each) + 8-12 Kling stills** to cover the 60s.

#### 3.4.1 Kling stills (20 min — generate in parallel tabs)

Open 🔗 https://klingai.com → Image → Text-to-image. Generate these 4 reusable stills first (they'll anchor the Short):

**Kling prompt 1 — hero tool icon (anchors the TOOL beat):**
```
A single glass-morphic app icon floating centered on a dark gradient background, icon features a minimalist abstract {voice-wave / microphone / prompt-bubble} symbol, soft rim light, gentle bloom, subtle reflection beneath, premium product-render feel. No text. 9:16 vertical, 1080x1920.
```

**Kling prompt 2 — dashboard mockup (for the DEMO beat):**
```
A stylized floating dashboard card with three soft rising bar charts and one circular progress ring at 87%, translucent glass material with subtle blue and purple gradient, soft shadow beneath, clean dark navy background with faint grid. Minimalist premium SaaS aesthetic, center framing. No text, no logos. 9:16 vertical, 1080x1920.
```

**Kling prompt 3 — before/after split (for the HOOK beat):**
```
Vertical split-screen composition. Left half: cluttered messy desk with scattered papers, muted cool tones, slight desaturation. Right half: same desk but perfectly organized with a single laptop and plant, warm golden tones, cinematic. Clean vertical divider line. 9:16 vertical, 1080x1920.
```

**Kling prompt 4 — environment breather (for the CTA beat):**
```
A minimalist wooden desk from above, single laptop, ceramic coffee cup, small green plant in corner, soft morning sunlight from upper left, shallow depth of field, negative space on right third for text overlay. 9:16 vertical, 1080x1920.
```

Generate 4-6 **variations of prompt 2** (the dashboard) with different chart styles, colors, UI elements — these become your Demo beat stills. Save all to `assets/s001/kling/`.

**Rules:**
- Always "No text, no logos" or Kling hallucinates gibberish.
- Save 1080x1920.
- Re-use stills across Shorts — build a library under `assets/_library/` so each Short only needs 4 new gens.

#### 3.4.2 Seedance 2 clips (15-25 min — mostly wait time)

Open 🔗 https://seed.bytedance.com/en/seedance2_0 (or use fal.ai if you have API access: https://fal.ai/seedance-2.0).

**Seedance prompt 1 — hero b-roll (for hook 0-5s):**
```
Slow push-in on an over-the-shoulder shot of a person at a minimalist wooden desk, warm daylight from a window on the left. Their laptop screen shows a stylized dashboard with soft glowing chart bars rising gently. They lean forward slightly, hands resting near the trackpad. Shallow depth of field, cinematic color grade, 24fps film look. 15 seconds, 9:16 vertical, 1080x1920.
```

**Seedance prompt 2 — demo hero (for 30-38s, the "hands typing" pivot):**
```
Top-down shot of hands typing on a silver laptop keyboard, quick purposeful motion. Soft overhead key light, faint blue accent from the screen. Cut at 7 seconds to a slow orbital push around a floating stylized app icon made of translucent glass and soft gradients, hovering above the laptop. Cinematic, moody, high contrast. 15 seconds, 9:16 vertical.
```

Save both to `assets/s001/seedance/`. One Seedance clip minimum; second one only if your script needs more motion.

**Rules:**
- Always end the prompt with explicit `15 seconds, 9:16 vertical, 1080x1920`.
- Never name a real product ("ChatGPT UI", "real Notion dashboard") — use "stylized dashboard."
- Save every working prompt to `prompts/seedance/` for reuse.

### 3.5 Stitch in CapCut (25 min — 45 min first time)

Open CapCut Pro → New Project → 9:16 (1080x1920) → 30fps.

**Track layout:**
- V1: Seedance b-roll clips
- V2: Kling stills (Ken-Burns them: right-click → Keyframe → scale 100% at start, 108% at end)
- V3: Text overlays (hook, `#ad`, tool name, result metric, CTA)
- V4: (empty, reserved for thumbnail scratch)
- A1: `narration.mp3` (drag in)
- A2: music — use CapCut's built-in library OR download from YT Creator Music first (🔗 YT Studio → left nav → **Audio Library** — no direct URL; each channel's path embeds its channel ID). Pick a "minimal tech" or "ambient lofi" track, 90-110 BPM.

**Timing cues (map to the 5-beat script):**

| Time | What's on screen |
|---|---|
| 0:00-0:03 | Seedance clip 1 on V1. Burned-in hook text (top-center, ~60pt, white on black 50% opacity). Burned-in `#ad — affiliate link below` FTC badge (top-left, **~44pt, white text in high-contrast black rounded box** — meets FTC "clear and conspicuous" bar, not the old tiny-disclaimer style). |
| 0:03-0:10 | Cut to Kling still #3 (before/after split) on V2 with 100%→108% Ken-Burns. |
| 0:10-0:20 | Kling still #1 (hero tool icon) on V2. Text overlay: tool name in bold, appearing at 0:11. |
| 0:20-0:45 | Demo beat (3 day-by-day action beats). Alternate 3 dashboard stills (Kling prompt 2 variants) every 2-4 seconds. At 0:30-0:38, drop Seedance clip 2 (hands typing) on V1 above the stills. |
| 0:45-0:50 | Kling still #4 (environment breather) + large on-screen text of the quantified outcome. |
| 0:50-0:51 | **Music ducks to silence for 1 second.** This is the retention trick — happens *before* the CTA to frame it. |
| 0:51-0:58 | CTA beat (25-30 narrated words fit here at ~155 wpm). On-screen: creator handle + "follow for more AI tool demos" + Dub link. |
| 0:58-0:60 | Final 2-second hold on handle + "link in description & pinned comment" text. Narration silent. |

**Audio mixing:**
- A1 narration: -3 dB, apply light compressor (CapCut → Audio → Compressor preset: Voice).
- A2 music: -18 dB; enable auto-ducking to -26 dB when narration is active (CapCut → Audio → Auto Ducking).
- Music fade-out to silence at 0:50, fade back in at 0:51 at -22 dB.

### 3.6 Captions (10-15 min)

**English captions (burned-in):**

- CapCut → Text → Auto Captions → Language: English → Generate.
- Style: bottom third, white text, black semi-transparent rounded box, 1 line max, ~60pt equivalent.
- Scrub through and fix tool-name spelling (auto-caption mangles "Claude," "HeyGen," etc.).

**Chinese captions (SRT, uploaded separately):**

- CapCut → Subtitle → Translate → Target language: Simplified Chinese.
- Export as `.srt`. Save as `s001_zh-CN.srt`.
- Review: fix tool-name transliterations manually (`克劳德` → leave as `Claude`, `海更` → `HeyGen`, etc.).

### 3.7 Export (3 min)

CapCut → Export → MP4 → 1080x1920 → 30fps → H.264 → bitrate 8 Mbps → file name `s001.mp4`.

### 3.8 Thumbnail (5 min)

Kling prompt (thumbnail is 16:9, not 9:16):
```
A hero still of a glowing glass-morphic tool icon floating on a dark navy gradient, heavy negative space on the left half for text overlay, cinematic premium SaaS feel, bloom and subtle lens flare. No text. 16:9 landscape, 1280x720.
```

Open in CapCut or Photopea → add 3-5 word punch line (e.g., "30s AI VOICE TEST") in sans-serif ~140pt, high-contrast color (electric-blue or yellow). Export as `s001_thumb.png`.

### 3.9 Metadata (5 min)

Paste this into Claude Code, fill in the braces:

```
Generate YouTube Shorts metadata for a 60s Short demoing {Tool name}. Return as markdown.

Tool: {Tool name}
Outcome claim: {one-line result from the demo}
Affiliate program: {program name}
Dub.co link: {dub short url}
short_id: s001

Needed:
1. Title (40-60 chars, tool name + specific outcome + "#Shorts" at end)
2. Description (EXACT structure below):
   Line 1: #ad disclosure
   Line 2: blank
   Line 3: "Try {tool} here: {dub link}"
   Line 4: blank
   Line 5: 1-sentence what the Short shows
   Line 6: blank
   Line 7: 5-7 hashtags starting with #{Tool name} #AITools #AIProductivity #Shorts
   Line 8: blank
   Lines 9+: timestamps (00:00 Hook / 00:03 Problem / 00:10 {Tool} intro / 00:20 Demo / 00:40 Result + link)
3. Pinned comment (this is where the real click-through happens):
   - "Quick links from this Short:"
   - "> Try {tool} (affiliate): {dub link}"
   - "> All my AI tools: beacons.ai/{handle}"
   - "Questions? Drop them below."
4. Tags (≤500 chars, front-load specificity): {Tool name}, {Tool name} review, {Tool name} demo, AI tools, AI productivity, AI tools 2026, best AI tools, AI for creators, AI affiliate, AI software
```

Claude returns the full block. Review for: tool name spelled correctly, Dub link has `utm_campaign=s001`, disclosure on line 1.

### 3.10 Upload via YT Studio (7 min)

🔗 https://studio.youtube.com → Create → Upload videos → `s001.mp4`.

- ✅ **Title:** paste title from §3.9
- ✅ **Description:** paste description from §3.9
- ✅ **Thumbnail:** upload `s001_thumb.png`
- ✅ **Audience:** "Not made for kids"
- ✅ **AI content toggle:** OFF (AI narrator + AI b-roll demoing real products doesn't require it; verify this specific Short doesn't include altered real-person footage)
- ✅ **Affiliate content toggle:** ON (Studio's paid-promotion toggle — YouTube surface-level, not an FTC substitute)
- ✅ **More options → Tags:** paste tags from §3.9
- ✅ **More options → Category:** Science & Technology
- ✅ **More options → Language:** English
- ✅ **Subtitles → Add language → Chinese (Simplified) → Upload file → `s001_zh-CN.srt`**
- ✅ **End screen:** skip for the first 3 Shorts; YT Shorts supports end screens but they add little at <100 subs
- ✅ **Visibility:** Public → Publish
- ✅ **Immediately after publish, do these two steps in order:**
  1. **Post the pinned comment first.** Open the published Short → scroll to Comments → paste the pinned-comment block from §3.9 → **Comment**. (If you skip this, there is nothing to pin in step 2.)
  2. **Then pin it.** Click the three-dot menu (⋮) next to the comment you just posted → **Pin** → confirm. You should see a "Pinned by creator" label appear.

---

## 4. Script templates for the other 2 formats (Week 3+)

After 3 Shorts of format #5, rotate to these.

### Format #3 — Stop Doing X / Do This

```
HOOK (0-3s, 7-9 words):
"Stop using {common tool} like this."

PROBLEM (3-8s, 15-18 words, wrong way):
Show the 5-second wrong-way workflow with a red X overlay and a "this takes {time}" text.

RIGHT WAY (8-20s, 35-45 words, using affiliate tool):
"Do this instead. {Tool name} {differentiator}. Click X, type Y, done in {time}." Show the right-way workflow clearly.

PROOF (20-28s, 20-25 words):
Show the outcome — before vs after metric. Quantify the savings.

CTA (28-30s, 7-10 words):
"Save this before it's patched. Affiliate link below."
```

### Format #1 — One-Prompt Wonder

```
HOOK (0-2s, 5-7 words):
"I typed 9 words. Got this."

PROMPT REVEAL (2-8s, 15-20 words):
Show the exact prompt on-screen for 4 seconds. Narrator reads it aloud.

TOOL UI (8-12s, 12-15 words):
"Here's {Tool name} running it." Stylized UI mockup.

RESULT REVEAL (12-22s, 30-35 words):
Show the output. Callout the "insane" detail.

CTA (22-28s, 15-20 words):
"Full prompt + affiliate link pinned. Follow for 1 prompt every Monday."
```

---

## 5. Dub.co UTM link builder (copy-paste)

Every Short = new Dub link = new `utm_campaign`. Pattern:

```
https://<AFFILIATE_LINK_FROM_PROGRAM>?utm_source=yt-shorts&utm_medium=affiliate&utm_campaign=s001&utm_content=elevenlabs&utm_term=before-after
```

**In Dub:** create a short link pointing to the full URL above.
- **Short key:** `s001-elevenlabs` (short_id + program)
- **Domain:** `dub.sh` (free) or your own
- **Attribution note in Dub:** `Short #s001; ElevenLabs; Before/After format`

**In the affiliate portal's SubID field** (set this at link creation): `s001`
- Impact: `subId1=s001`
- CJ: `sid=s001`
- PartnerStack: `partner_key=s001`
- No SubID field (Beehiiv/Jasper-direct): rely on UTM only, accept ±1-day attribution error

**Result:** Dub click log + affiliate dashboard both tag the conversion with `s001`. Weekly review joins them on `short_id`.

---

## 6. Weekly review template (Monday, 30 min)

Save as `weekly_review_YYYY-MM-DD.md` in your notes app. Fill it out every Monday:

```markdown
# Weekly Review — Week of {Monday date}

## Shorts published this week
| short_id | title | published | views | avg view % | swipe-away % | Dub clicks | conv. (pending) | conv. ($) |
|---|---|---|---|---|---|---|---|---|
| s001 | ... | YYYY-MM-DD | | | | | | |
| s002 | ... | YYYY-MM-DD | | | | | | |

## Cumulative (trailing 7 days)
- Total views:
- Subscribers gained:
- External click-through rate (Dub clicks ÷ views):
- Affiliate clicks:
- Affiliate conversions (pending + confirmed):
- Commission $ confirmed this week:

## Winners (kill/scale rules in §7)
- Scale: short_ids hitting ≥10k views → queue same-format sequel within 72h
- Repeat hook format: ...
- Repeat program: ...

## Losers
- Archive (views <500 at 48h): short_ids ...
- Rewrite hook (avg view % <25%): short_ids ...
- Rewrite title/thumbnail (CTR <3%): short_ids ...

## Niche health check (Week 2+ only)
- [ ] ≥1 Short ≥1k views
- [ ] ≥1 recorded affiliate click
- [ ] ≥1 pending or confirmed conversion
- If 0 of 3 for 2 consecutive weeks → change hook format (not niche)
- If 0 of 3 for 4 consecutive weeks → re-evaluate niche

## Next week plan
- Shorts to publish (2 max):
- One new affiliate program to test:
- One experiment (hook / CTA / thumbnail):
```

---

## 7. Kill / iterate / scale rules (numeric)

All thresholds measured in YT Studio, read at T+48h unless stated. Apply these rules every Monday.

| Rule | Trigger | Action |
|---|---|---|
| **Archive** | Views < 500 at 48h AND swipe-away > 40% | Unlist (not delete). Log hook format as "dud." |
| **Rewrite hook format** | Avg view % < 25% on any Short > 500 views | Next upload uses a different hook family. Keep same tool/niche. |
| **Rewrite title/thumbnail** | Shorts feed impressions CTR < 3% (YT Studio → Reach tab) | Swap title + cover within 24h. If still <3% at T+7d, unlist. |
| **Scale winner** | Views ≥ 10,000 at any point | Queue same-format sequel within **72h**. Reuse hook template, change tool. |
| **Double-down signal** | ≥ 1% external-click rate (Dub clicks ÷ views) | Promote that program to "pinned" block in Beacons for the next 14 days. |
| **Kill program** | Featured program = 0 clicks across 3 Shorts, combined views ≥ 5k | Drop program. Replace with next on §1.4 tracker. |
| **Escalate volume** | 2 consecutive weeks with ≥1 Short above 10k views | Raise cadence from 2 → 3 Shorts/week. Don't go higher — production QA breaks first. |
| **Shorts feed starvation** | Shorts feed views < 20% of total views | Algorithm isn't pushing. Fix first-frame hook + thumbnail, not content. |

---

## 8. First-dollar milestone checklist

| # | Milestone | Realistic day | Depends on |
|---|---|---|---|
| 1 | §1 setup done, FTC disclosure in channel defaults | Day 0 | — |
| 2 | Dub.co account + 5 master affiliate links with UTM | Day 0 | Some approvals instant (ElevenLabs, Framer, Beehiiv), some 3-5 days (Impact) |
| 3 | Beacons bio live w/ EN + 中文 blocks | Day 0 | — |
| 4 | Short #1 uploaded + pinned comment w/ Dub link | Day 1 | §3 pipeline |
| 5 | First 100 views | Day 1-2 | Algorithm warm-up |
| 6 | First 500 views on any Short | Day 3-7 | Usually 2nd/3rd Short breaks through |
| 7 | First Dub click recorded | Day 4-9 | Needs ≥500 views + visible CTA |
| 8 | First pending conversion in affiliate dashboard | Day 7-14 | Free-trial-payout programs (Jasper, HeyGen, Gamma) pay faster than purchase-gated |
| 9 | **First commission confirmed (≥$1)** | **Day 10-21** | Cookie window + advertiser approval lag |
| 10 | First $50 payout threshold crossed | Day 30-60 | One high-ticket OR ~5 low-ticket |

**If Day 21 hits with 0 pending conversions:** 90% of the time the cause is (a) CTA missing on-screen, (b) Dub link not in pinned comment, or (c) featured tool's affiliate program wasn't approved yet. Diagnose these three before changing niche.

---

## 9. Delegation protocol — "run the playbook, Short #N"

When you're ready to hand this off, say one of:

- **"Run the playbook, script Short #N demoing {Tool name}"** → agent does §3.1 through §3.9 and hands back: script + narration mp3 + Kling/Seedance prompts list + CapCut timing doc + metadata block. You do the manual Kling/Seedance/CapCut/upload steps.
- **"Run weekly review for week of {date}"** → agent pulls YT Studio + Dub + affiliate dashboards, fills in §6 template, flags any kill/scale triggers per §7.
- **"Which tool should I demo next?"** → agent reads §1.4 tracker, checks conversion history + last-demo-date, suggests next pick with hook angle.

The agent_team picks up the dossier at `.audit/adhoc_agents/2026-04-19/yt_shorts_affiliate_playbook/` for full context.

---

## 10. Drift risks to monitor monthly

1. **YT inauthentic-content policy is actively evolving** — re-read https://support.google.com/youtube/answer/1311392 on the 1st of every month.
2. **FTC disclosure penalties can escalate** — they're at $53K/post in 2026. If format changes (e.g., description-only disclosure passes), adjust §3.10.
3. **Affiliate program status changes** — Notion closed is the current example. Recheck the §1.4 tracker monthly. Kajabi and Canva Canvassador may reopen.
4. **Seedance / Kling pricing changes** — if either starts charging per-second for generation, budget math shifts. Currently assumed included in your existing plans.
5. **Dub.co free-tier limits** — 1,000 events/mo. Upgrade to Pro ($25/mo) only if you exceed 800 clicks/mo (good problem).
6. **YT Shopping eligibility** — March 2026 dropped to 500 subs + full YPP. When you hit 500 subs + 4k watch-hrs (or 10M Shorts views/90d), apply and add YT Shopping as a second money loop.

---

## 11. Compliance checklist (run this before every upload)

- ✅ `#ad` on-screen in first 3 seconds (burned-in)
- ✅ Affiliate disclosure as line 1 of description
- ✅ Tool name in title (algorithm matches search)
- ✅ Dub link in description (line 3) AND pinned comment
- ✅ No brand-term in description that I'd bid on as a PPC ad (brand-term bidding voids commissions)
- ✅ No "guaranteed income" / "$1M" / "free money" claims
- ✅ No real software UI shown (stylized mockups only) unless it's a tool you personally have a license to screen-record
- ✅ Music from YT Creator Music or in-app Shorts audio (not trending external audio)
- ✅ AI-content toggle honestly set (OFF for AI narrator + AI b-roll demoing real products; ON if you ever show a realistic-person avatar doing something that could mislead)
- ✅ Captions EN (burned-in) + ZH SRT uploaded
- ✅ Thumbnail matches video subject (no clickbait mismatch)

---

## Appendix A — Tools inventory + total cost

| Tool | Purpose | Cost |
|---|---|---|
| Seedance 2 | ≤15s b-roll clips | (user-owned) |
| Kling AI | Unlimited stills + short video | (user-owned) |
| Claude Code | Script, metadata, weekly review | (user-owned) |
| ElevenLabs Creator | AI narration | $22/mo |
| CapCut Pro | Stitching + captions + thumbnails | $8/mo |
| YouTube Studio | Upload + analytics | Free |
| Dub.co Free | Link shortener + per-link analytics | Free |
| Beacons.ai Free | Bio link + bilingual blocks | Free |
| YT Creator Music | Royalty-free music library | Free |
| Ayrshare Premium (optional, Week 3+) | Cross-post + aggregated analytics | $29/mo |
| **Total** | | **$30-$59/mo** (inside $50-$100 budget) |

## Appendix B — Affiliate program cheat sheet (top 5 Week-1 picks)

| Program | Signup | Commission | Cookie | Approval | Payout min |
|---|---|---|---|---|---|
| ElevenLabs | https://elevenlabs.io/affiliates (via PartnerStack) | 22% recurring × 12mo | 90d | Auto | $5 / PayPal / Stripe / bank |
| HeyGen | https://www.heygen.com/affiliate-program (via PartnerStack) | 35% first 3mo | 30d | 1-3 days | $30 / PayPal |
| Beehiiv | https://partners.beehiiv.com/signup | 50% recurring × 12mo | 60d | Auto (for paying users) | $50 / PayPal, Stripe |
| Framer | https://www.framer.com/partners (Dub-powered) | 50% recurring × 12mo | 90d | Auto | Stripe |
| Jasper | https://www.jasper.ai/partners (via Impact) | 25% recurring × 12mo | 30d | 1-3 days | $25 / PayPal |

Full 18-program table in `research/affiliate_programs.md`.

## Appendix C — The 5 files that back this playbook

- `interview/requirements.md` — locked scope
- `research/yt_shorts_policy_algo.md` — YT policy + algorithm 2026
- `research/affiliate_programs.md` — 18 programs + 6 networks
- `research/production_pipeline.md` — Seedance + Kling + ElevenLabs + CapCut SOP
- `research/format_library.md` — 10 formats + 20 hooks + channel study list
- `research/tracking_iteration.md` — Dub + Beacons + Ayrshare + kill/scale rules
- `research/dossier.md` — consolidated facts

Read the ones you want to go deeper on — the playbook is the operational layer.
