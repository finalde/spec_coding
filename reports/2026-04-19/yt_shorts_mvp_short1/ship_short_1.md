# SHIP YT SHORTS #1 — TODAY

**Goal:** Have Short #1 **published on YouTube** before end of day.
**Total wall time:** ~3h 40m from zero.
**Every decision is pre-made.** Do not deviate. If a step says "paste this," paste *exactly* that.

---

## At-a-glance sequence

| # | Section | Time | Cumulative |
|---|---|---|---|
| §0 | Pre-flight | 30 min | 0:30 |
| §1 | Tool pick (already decided) | 0 min | 0:30 |
| §2 | Grab affiliate link | 5 min | 0:35 |
| §3 | Write the script | 15 min | 0:50 |
| §4 | Generate narration | 5 min | 0:55 |
| §5 | Generate visuals | 45 min | 1:40 |
| §6 | Stitch in CapCut | 40 min | 2:20 |
| §7 | Captions (EN + ZH) | 15 min | 2:35 |
| §8 | Export MP4 | 3 min | 2:38 |
| §9 | Thumbnail | 5 min | 2:43 |
| §10 | Metadata | 5 min | 2:48 |
| §11 | Upload to YT | 10 min | 2:58 |
| §12 | Pin the comment | 2 min | 3:00 |
| §13 | Track at T+6h, T+24h | 10 min spread over next day | — |

If you fall more than 30 min behind at any checkpoint, go to the **Fallback shortcuts** section at the bottom.

---

## Pre-decided defaults (do NOT change these for Short #1)

| Thing | Locked value | Why |
|---|---|---|
| Tool to demo | **ElevenLabs** | You already use it → authentic POV. Auto-approve affiliate. |
| Format | **"I Tried X for 7 Days"** micro case-study | 45-55s fits one Seedance clip budget; first-person POV satisfies YT inauthentic-content policy. |
| Voice | **Aaron** (ElevenLabs default) | Authoritative, works for tech demos. Lock this for first 10 Shorts. |
| Voice settings | Stability **40%**, Similarity **75%**, Style **25%**, Speaker Boost **ON** | Tested tone for demos. |
| TTS model | `eleven_turbo_v2` | Fast, cheap, English-only. |
| Video length | **58-60s** | Max-length Short = more algorithm real estate. |
| Aspect ratio | **9:16, 1080×1920, 30fps** | Shorts native. |
| Bitrate | **8 Mbps, H.264** | Upload quality sweet spot. |
| Music bed | CapCut built-in → "minimal tech" or "ambient lofi" 90-110 BPM | In-app audio = no Content ID risk. |
| Thumbnail | 16:9, 1280×720, 3-5 word punchline | YT Shorts shows thumbnails in feed + search. |
| `short_id` | **`s001`** | Used in every UTM + SubID. |

---

## §0 — Pre-flight (30 min)

### 0.1 Accounts you MUST have open before starting (5 min)

Open all 7 tabs right now. If any fails to load, stop and fix it before moving on.

1. 🔗 https://studio.youtube.com — YouTube Studio (logged in, channel selected)
2. 🔗 https://elevenlabs.io/app/text-to-speech — ElevenLabs TTS web UI (Creator plan active)
3. 🔗 https://app.klingai.com/global — Kling AI (logged in, credits available)
4. 🔗 Your Seedance 2 generator URL (provider-dependent: Volcengine/Jimeng if direct, or fal.ai at https://fal.ai/seedance-2.0 if via API). Open it.
5. 🔗 https://app.partnerstack.com/login — PartnerStack (account created, ElevenLabs approved — if not approved yet, apply NOW at https://app.partnerstack.com/join → search "ElevenLabs" → Apply; auto-approves in <5 min)
6. 🔗 https://dub.co/login — Dub.co (free workspace created)
7. **CapCut Pro desktop app** — launched, on the "Create project" screen

### 0.2 Local folders (2 min)

Open a terminal and run:

```bash
mkdir -p "C:\workspace\spec_coding\reports\2026-04-19\yt_shorts_mvp_short1\s001"
cd "C:\workspace\spec_coding\reports\2026-04-19\yt_shorts_mvp_short1\s001"
mkdir kling seedance audio export
```

Every file for Short #1 lands inside `s001/`. Nothing scatters.

### 0.3 Affiliate-link dress rehearsal (3 min)

In PartnerStack dashboard → ElevenLabs → **Link Builder** → you'll see a field for SubID / tracking. Test it: enter `s001` in the SubID field, click **Generate link**. Copy the result.

PartnerStack will give you something like `https://try.elevenlabs.io/abcd1234?via=abcd1234&subid=s001` — here `abcd1234` is YOUR partner code (same value in both spots). Don't edit it; just copy verbatim.

Paste that URL into a scratch note labeled `AFFILIATE_LINK_RAW`. You'll wrap it with Dub in §2.

### 0.4 Quick pre-flight checklist (2 min)

- ✅ YT channel handle set (e.g., `@aitoolsdaily`) — if not, go to YT Studio → Customization → Basic info → set handle now
- ✅ YT channel description has the bilingual affiliate disclosure from §1.1 of the main playbook (if missing, paste it in now — takes 2 min)
- ✅ 2-step verification ON for Google account
- ✅ ElevenLabs API credits > $1 remaining (Settings → Billing)
- ✅ Kling credits ≥ 250 remaining (need ~210 for 6 stills + 1 thumbnail, 30 credits each)
- ✅ Seedance quota: ≥ 2 gens available (you'll use 1, keep 1 as retry buffer)

If any ✅ fails, fix it before continuing. Don't try to work around missing access.

### 0.5 Open a fresh Claude Code terminal (1 min)

Open **one** Claude Code terminal, cd into the monorepo root. You'll paste prompts from §3, §9, §10 into this one terminal.

---

## §1 — Tool pick (0 min — already decided)

**Tool:** ElevenLabs
**Positioning:** Realistic AI voice generation for creators
**The-one-verb:** Clones voices from 60 seconds of audio
**Differentiator:** Emotional control (whisper / shout / laughing) + 29 languages
**Concrete demo (7-day arc):** Day 1 record sample → Day 3 first clone works → Day 5 scale across 3 narrations → Day 7 total cost + time saved
**Measurable outcome:** "30 seconds of pro narration for $0.04; 7 days → saved 6 hours + $240 vs hiring VO"

Skip to §2.

---

## §2 — Grab affiliate link (5 min)

### 2.1 Take the raw PartnerStack link from §0.3

```
RAW: https://try.elevenlabs.io/<your_code>?via=<your_code>&subid=s001
```

### 2.2 Wrap with UTM

Add these query params (paste & adjust):

```
FULL: https://try.elevenlabs.io/<your_code>?via=<your_code>&subid=s001&utm_source=yt-shorts&utm_medium=affiliate&utm_campaign=s001&utm_content=elevenlabs&utm_term=i-tried-7-days
```

### 2.3 Shorten via Dub.co

1. 🔗 https://app.dub.co → **+ Create link**
2. **Destination URL:** paste the `FULL` link above
3. **Short key:** `s001-el`
4. **Domain:** leave `dub.sh`
5. Click **Create**
6. Copy the resulting short URL — e.g., `https://dub.sh/s001-el`

### 2.4 Save both values

In a scratch note, record:

```
DUB_LINK:   https://dub.sh/s001-el
FULL_LINK:  (from 2.2)
```

You'll paste **`DUB_LINK`** into the script CTA, Short description, pinned comment, and Beacons bio.

---

## §3 — Write the script (15 min)

### 3.1 Paste this into Claude Code (verbatim)

```
Write a 60-second YouTube Short script in the "I Tried X for 7 Days" micro case-study format.

Tool: ElevenLabs
Tool positioning: Realistic AI voice generation for creators
Demo concrete action: Day 1 record 60s voice sample → Day 3 first usable clone → Day 5 narrate 3 Shorts back-to-back → Day 7 tally cost + time saved vs a human VO
Measurable outcome: 30 seconds of pro narration for $0.04; 7 days saved 6 hours + $240 vs hiring a voice actor
Affiliate program: ElevenLabs via PartnerStack
Affiliate Dub link: https://dub.sh/s001-el

Rules:
- 140-160 English words total (155 wpm = ~60s; aim for 58-62s final runtime)
- Beat structure + word targets:
  HOOK (0-3s)      7-9 words     Outcome claim + "I tested this for 7 days." Pattern-break.
  PROBLEM (3-10s)  15-20 words   Name the pain I felt before I started.
  TOOL (10-20s)    22-28 words   Tool name + one-line position + differentiator.
  DEMO (20-45s)    60-75 words   3 day-by-day action beats with metric overlay (time saved, $ saved).
  CTA (45-58s)     25-30 words   Quantified final outcome + FTC disclosure (#ad) + affiliate CTA.
  HOLD (58-60s)    0 words       Silent hold on "link in description & pinned comment".

- Include an on-screen text overlay plan (one line per 5s segment).
- First-person POV throughout. No "you" until the CTA.
- No "guaranteed," "free money," "AI will replace you."
- Output format: markdown table with columns [time, narration, on-screen-text, visual-cue].
```

### 3.2 Review Claude's output

Scan for:
- ✅ Total word count between 140-160 (count the "narration" column)
- ✅ "ElevenLabs" spelled correctly (not "Eleven Labs" or "11Labs")
- ✅ `#ad` appears on-screen in 0-3s row
- ✅ CTA row has the Dub link text
- ✅ 3 distinct day beats in the Demo section

If any fails, tell Claude Code: `"Fix: {issue}. Return the full table again."` Don't manually edit the script until the structure is right.

### 3.3 Save the script

```bash
# in the s001/ folder
```

Save the markdown table as `s001/script.md`. Extract just the narration column into `s001/narration.txt` — one line per time segment, 5 lines total (HOOK / PROBLEM / TOOL / DEMO / CTA; HOLD is silent so skip).

---

## §4 — Generate narration (5 min)

### 4.1 Open ElevenLabs TTS

🔗 https://elevenlabs.io/app/text-to-speech

### 4.2 Voice selection (top of UI)

Click the voice dropdown → search **Aaron** → select it.

If "Aaron" isn't in your library, click **VoiceLab → Add a voice → Pre-made → Aaron**.

### 4.3 Settings (right-hand sidebar)

- **Stability:** `40`
- **Similarity:** `75`
- **Style Exaggeration:** `25`
- **Speaker Boost:** `ON` ✓

### 4.4 Model (below voice name)

Select **`eleven_turbo_v2`** from the model dropdown.

### 4.5 Paste and generate

Paste the full contents of `s001/narration.txt` into the text box. You should see ~150 words. Character count ~750-900.

Click **Generate**. Wait ~10 seconds. Listen back once:
- ✅ Total length 55-62 seconds
- ✅ Tool name "ElevenLabs" pronounced correctly (not "Eleven lab-s")
- ✅ No robotic pauses mid-sentence

If length is >62s, the script is too long — cut 10 words from the DEMO beat, regenerate.
If length is <55s, add 10 words to DEMO, regenerate.

### 4.6 Download

Click **Download** → save as `s001/audio/narration.mp3`.

**Cost check:** should read ~$0.03-$0.05 in the generation log.

---

## §5 — Generate visuals (45 min)

Plan: **1 Seedance clip (15s) + 6 Kling stills**. The 1 clip covers the HOOK/TOOL segment (0-15s). Stills cover the rest. You'll re-use stills where possible.

### 5.1 Kling stills — generate in parallel (25 min)

Open 🔗 https://app.klingai.com/global → **AI Images** → **Text to Image** → Aspect ratio **9:16**, Resolution **1080×1920**, Model **Kling 1.6 / latest**.

Generate these 6 prompts **in parallel** (open 6 tabs, paste one prompt per tab, hit Generate on all, they run concurrently).

**Kling 1 — hero: microphone icon (anchors TOOL beat):**
```
A single glass-morphic microphone icon floating centered on a dark navy gradient background, soft rim light, gentle bloom, subtle reflection beneath, premium product-render feel. No text, no logos. 9:16 vertical, 1080x1920.
```

**Kling 2 — dashboard mockup variant A (for DEMO Day 1):**
```
A stylized floating dashboard card showing a single waveform line in soft blue, translucent glass material, soft shadow beneath, clean dark navy background with faint grid. Minimalist premium SaaS aesthetic, center framing. No text, no logos. 9:16 vertical, 1080x1920.
```

**Kling 3 — dashboard mockup variant B (for DEMO Day 3):**
```
A stylized floating dashboard card showing three soft rising bar charts and one circular progress ring at 50 percent, translucent glass material with subtle purple gradient, soft shadow beneath, clean dark navy background. Minimalist premium SaaS aesthetic, center framing. No text, no logos. 9:16 vertical, 1080x1920.
```

**Kling 4 — dashboard mockup variant C (for DEMO Day 5/7):**
```
A stylized floating dashboard card showing three completed progress rings at 100 percent with checkmarks, translucent glass material with warm green gradient, soft shadow beneath, clean dark navy background. Minimalist premium SaaS aesthetic, center framing. No text, no logos. 9:16 vertical, 1080x1920.
```

**Kling 5 — before/after split (for HOOK pattern-break):**
```
Vertical split-screen composition. Left half: cluttered messy desk with scattered papers and an old microphone, muted cool tones, slight desaturation. Right half: same desk but minimalist with a single sleek microphone and laptop, warm golden tones, cinematic. Clean vertical divider line. 9:16 vertical, 1080x1920.
```

**Kling 6 — environment breather (for CTA beat):**
```
A minimalist wooden desk from above, single laptop open to a waveform, ceramic coffee cup, small green plant in corner, soft morning sunlight from upper left, shallow depth of field, negative space on right third for text overlay. No text, no logos. 9:16 vertical, 1080x1920.
```

As each finishes, download to `s001/kling/`:
- `kling_1_mic.png`
- `kling_2_waveform.png`
- `kling_3_bars.png`
- `kling_4_rings.png`
- `kling_5_before_after.png`
- `kling_6_desk.png`

**Rule:** if any image contains garbled text or logos, regenerate with the SAME prompt. Kling is non-deterministic — don't spend more than 2 regen attempts per image.

### 5.2 Seedance clip — 1 clip, 15s (20 min mostly wait)

Open your Seedance 2 generator (from §0.1 tab 4).

**Seedance prompt 1 — hero b-roll (for 0:00-0:15, the HOOK + TOOL beats):**
```
Slow push-in on an over-the-shoulder shot of a person at a minimalist wooden desk, warm daylight from a window on the left. Their laptop screen shows a stylized audio waveform with soft glowing peaks rising gently. They lean forward slightly, hands resting near the trackpad and a microphone. Shallow depth of field, cinematic color grade, 24fps film look. 15 seconds, 9:16 vertical, 1080x1920.
```

Settings:
- **Duration:** 15 seconds (max)
- **Aspect ratio:** 9:16
- **Resolution:** 1080×1920

Click Generate. Wait 3-8 min.

Download to `s001/seedance/seedance_1_hero.mp4`.

**Rule:** if the clip shows garbled text on the laptop screen, it's still fine — we'll crop / blur it in CapCut. Do NOT regenerate unless a face or limb is deformed.

---

## §6 — Stitch in CapCut (40 min)

### 6.1 New project

CapCut Pro → **+ Create project** → **Custom** → **9:16 vertical, 1080×1920, 30 fps**.

### 6.2 Import assets

Drag these into the **Media** panel:
- `s001/seedance/seedance_1_hero.mp4`
- all 6 files from `s001/kling/`
- `s001/audio/narration.mp3`

### 6.3 Build the timeline (track-by-track)

Set the timeline to **60 seconds** (drag the end marker to 0:60.00).

**A1 — Narration track**
Drag `narration.mp3` to audio track A1, aligned at **0:00**.
- Audio → **Compressor** → preset **Voice**
- Volume: **-3 dB**

**A2 — Music track**
CapCut → **Audio** tab → **Audio library** → search "minimal tech" → filter: royalty-free, 90-110 BPM → pick the top result that's at least 65 seconds long. Drag to A2 aligned at **0:00**.
- Volume: **-18 dB**
- **Auto-ducking: ON → target -26 dB when narration active** (Audio menu → Auto Ducking)
- Keyframe fade-out to silent at **0:50.0**; keyframe back to **-22 dB** at **0:51.0**. (CapCut: right-click volume → Add keyframe at each point.)

**V1 — Primary video track**

| Timeline range | Clip | Action |
|---|---|---|
| 0:00-0:15 | `seedance_1_hero.mp4` | Drag to V1. If longer than 15s, trim right edge to exactly 15.00. |
| 0:15-0:20 | `kling_1_mic.png` | Hold for 5s. Ken-Burns: Scale keyframe 100% at 0:15, 108% at 0:20. |
| 0:20-0:27 | `kling_2_waveform.png` | 7s. Ken-Burns 100→110%. |
| 0:27-0:34 | `kling_3_bars.png` | 7s. Ken-Burns 100→110%. |
| 0:34-0:45 | `kling_4_rings.png` | 11s. Ken-Burns 100→112%. |
| 0:45-0:55 | `kling_6_desk.png` | 10s. Ken-Burns 100→106%. |
| 0:55-0:60 | `kling_1_mic.png` | Re-use the hero shot for the final hold. Ken-Burns 100→105%. |

**V2 — Overlay track** (for the HOOK pattern-break)
Drag `kling_5_before_after.png` to V2 at **0:03-0:08** (5 seconds). Scale it to 80%, center it. Add a **crossfade-in** at 0:03 (0.3s) and **crossfade-out** at 0:08 (0.3s).

**V3 — Text overlay track**

Add text boxes on V3 per this table (all text Bebas Neue or Montserrat Bold, white with black rounded-box background unless noted):

| Timeline | Text | Font size | Position | Notes |
|---|---|---|---|---|
| 0:00-0:03 | (your HOOK line, from script 0-3s row) | ~70pt | top-center, y=15% | Bounce-in animation |
| 0:00-0:60 | `#ad — affiliate link below` | **44pt, white on solid black rounded box** | top-left, y=8% | **Stays on entire Short — FTC required** |
| 0:10-0:18 | `ElevenLabs` | 90pt, yellow-on-black | center | Fade-in |
| 0:20-0:26 | `Day 1` | 120pt, yellow-on-black | center-top | Pop-in |
| 0:26-0:33 | `Day 3` | 120pt, yellow-on-black | center-top | Pop-in |
| 0:33-0:45 | `Day 5-7` | 120pt, yellow-on-black | center-top | Pop-in |
| 0:40-0:50 | `$0.04 per 30s narration` | 70pt, white | bottom third, y=75% | Metric overlay |
| 0:45-0:50 | `Saved 6 hours + $240` | 70pt, white | bottom third, y=82% | Metric overlay |
| 0:51-0:58 | `Link ↓ in description` + `@yourhandle` | 80pt, white | center | CTA |
| 0:58-0:60 | `Pinned comment has the link` | 60pt, white | center | Final hold |

Make sure the `#ad` badge NEVER overlaps other overlays (top-left corner, y=8% only).

### 6.4 Quick QA pass (3 min)

Scrub through once at full-screen preview. Check:
- ✅ `#ad` visible at 0:01, 0:20, 0:40, 0:58 (every sample point)
- ✅ Narration audible over music at all points (auto-duck working)
- ✅ Text overlays readable against underlying visuals (if one is lost, increase the black box opacity to 80%)
- ✅ No frozen frame, no audio desync
- ✅ Last frame is `kling_1_mic.png` with CTA text

---

## §7 — Captions (15 min)

### 7.1 English — burned in (10 min)

CapCut → **Text** tab → **Auto Captions** → Source: "Main track (A1 narration)" → Language: English → **Generate**.

Wait ~60s for Auto Captions to finish.

**Fix these manually** (auto-caption usually mangles these):
- `ElevenLabs` — search/replace every instance. Auto-caption often writes "11 labs," "Eleven lab," or "11 Labs." → must be `ElevenLabs`.
- Punctuation on the CTA — add periods for clean line breaks.

**Style captions:**
- CapCut → select all caption text → **Style** tab
  - Font: **Montserrat Bold**
  - Size: **~56pt**
  - Color: white
  - Background: **black, 70% opacity, rounded 8px**
  - Position: bottom third, y=78%
  - Max 1 line at a time

### 7.2 Chinese — SRT export (5 min)

CapCut → **Subtitle** tab → select all English captions → **Translate** → target language: **Simplified Chinese** → Apply.

Preview the Chinese track. **Fix these manually:**
- Tool names stay English: `ElevenLabs` should NOT be translated to `克劳德` or `11实验室`. Keep as `ElevenLabs`.
- Numeric metrics stay English: `$0.04`, `6 hours`, `$240` — leave.

**Export the Chinese track only:**
- Right-click the Chinese subtitle track → **Export subtitles** → format `.srt` → filename `s001_zh-CN.srt` → save to `s001/`.

**Hide the Chinese track from the visual output** (we upload it separately):
- Toggle the Chinese subtitle track's eye icon to OFF so it doesn't burn in.

---

## §8 — Export MP4 (3 min)

CapCut → **Export** (top right).

Settings:
- **Resolution:** 1080×1920
- **Frame rate:** 30fps
- **Bitrate:** 8 Mbps (or "Recommended" → slide to High)
- **Codec:** H.264
- **Format:** MP4
- **Filename:** `s001.mp4`
- **Destination:** `s001/export/s001.mp4`

Click Export. Wait ~60-90s.

**Verify:**
- File size should be 45-90 MB.
- Open the file in a player, scrub to 0:30 → confirm narration + music + caption + `#ad` badge all visible.

---

## §9 — Thumbnail (5 min)

### 9.1 Generate Kling thumbnail (16:9)

In Kling, switch aspect ratio to **16:9** and paste:

```
A hero still of a glowing glass-morphic microphone floating on a dark navy gradient, heavy negative space on the left half for text overlay, cinematic premium SaaS feel, bloom and subtle lens flare. No text, no logos. 16:9 landscape, 1280x720.
```

Download to `s001/kling/thumb_base.png`.

### 9.2 Add headline text

Open `thumb_base.png` in Photopea (🔗 https://photopea.com — free, browser-based, Photoshop-clone) or CapCut image mode.

Add text:
- **Text:** `$0.04 AI VOICE` (3 words max — scannable in feed at thumbnail size)
- **Font:** Bebas Neue Bold or Anton
- **Size:** ~170pt
- **Color:** Electric yellow `#FFDF2A`
- **Stroke:** 4px solid black
- **Position:** left half of image (the negative-space area)

Export as `s001/export/s001_thumb.png` (PNG, 1280×720).

---

## §10 — Metadata (5 min)

### 10.1 Paste into Claude Code (verbatim)

```
Generate YouTube Shorts metadata for a 60s Short demoing ElevenLabs. Return as markdown with clearly labeled sections.

Tool: ElevenLabs
Outcome claim: Cloned my voice and narrated a full Short for $0.04; 7 days saved 6 hours + $240 vs hiring a voice actor
Affiliate program: ElevenLabs via PartnerStack
Dub.co link: https://dub.sh/s001-el
Beacons: beacons.ai/<PLACEHOLDER_HANDLE>
short_id: s001

Needed:

1) TITLE (40-60 chars, must include "ElevenLabs" + specific outcome + "#Shorts" at end)

2) DESCRIPTION with this EXACT structure — output verbatim:
Line 1: #ad — This video contains affiliate links. I earn a small commission if you sign up, at no extra cost to you.
Line 2: (blank)
Line 3: Try ElevenLabs here → https://dub.sh/s001-el
Line 4: (blank)
Line 5: One sentence describing what the Short shows.
Line 6: (blank)
Line 7: Five to seven hashtags starting with #ElevenLabs #AITools #AIProductivity #Shorts
Line 8: (blank)
Line 9+: Timestamps —
00:00 Hook — 7-day test claim
00:03 Problem — why I needed it
00:10 ElevenLabs intro
00:20 Day-by-day demo
00:45 Result + link

3) PINNED COMMENT (copy-paste block):
Quick links from this Short:
→ Try ElevenLabs (affiliate): https://dub.sh/s001-el
→ All my AI tools: beacons.ai/<PLACEHOLDER_HANDLE>
Questions? Drop them below.

4) TAGS (single-line, <=500 chars, front-load specificity): ElevenLabs, ElevenLabs review, ElevenLabs demo, AI voice generation, AI tools, AI productivity, AI tools 2026, best AI tools, AI for creators, AI affiliate, AI software, AI voice clone
```

### 10.2 Review Claude's output

- ✅ Title has "ElevenLabs" + a number + "#Shorts" at end
- ✅ Description line 1 is `#ad — This video contains affiliate links...`
- ✅ Description line 3 has the exact Dub link `https://dub.sh/s001-el`
- ✅ Pinned comment has the Dub link AND beacons link
- ✅ No all-caps clickbait, no "GUARANTEED," no "FREE MONEY"

Save Claude's output as `s001/metadata.md`.

---

## §11 — Upload to YT (10 min)

🔗 https://studio.youtube.com → **Create** → **Upload videos** → pick `s001/export/s001.mp4`.

Walk through the wizard exactly:

### 11.1 Details tab

- **Title:** paste Title from `metadata.md`
- **Description:** paste Description from `metadata.md` (preserve blank lines!)
- **Thumbnail:** upload `s001/export/s001_thumb.png`
- **Playlists:** skip
- **Audience:** select **"No, it's not made for kids"**
- **Age restriction:** No
- **Paid promotion:** click **"Show more"** → scroll to **Paid promotion** → check **"My video contains paid promotion"** ✓ AND check **"Add a message to my video informing viewers of paid promotion"** ✓ (BOTH on — belt-and-suspenders for FTC; your burned-in `#ad` badge is the primary disclosure, YT's auto-message is the backup. FTC wants the disclosure "unavoidable" — two paths beats one.)
- **Altered content (AI disclosure):** select **"No"** — AI narrator + AI b-roll demoing a real product does NOT require the AI-content disclosure. (Disclosure is only for synthetic likeness of real people or misleading altered events.)
- **Tags (under "Show more"):** paste TAGS from `metadata.md`
- **Language:** English
- **Category:** Science & Technology
- **Recording date:** today
- **Location:** leave blank
- **Comments:** Allow all
- **Show how many viewers like:** On
- **Shorts remixing:** Allow video and audio remixing

### 11.2 Video elements tab

- Skip end screen (Shorts don't benefit at <100 subs)
- Skip cards
- **Subtitles:** click **Add** → **Upload file** → **With timing** → select `s001/s001_zh-CN.srt` → Language: Chinese (Simplified) → Save

### 11.3 Checks tab

Wait for copyright/ad-suitability checks. Should pass (music is CapCut in-app library).

If anything flags, screenshot it, stop, post in this thread for diagnosis. **Do NOT publish a flagged Short.**

### 11.4 Visibility tab

- **Save or publish:** Public
- **Instant Premieres:** Off
- **Schedule:** leave "Publish immediately"
- Click **Publish**

### 11.5 Copy the published URL

After publish, YT gives you a URL like `https://www.youtube.com/shorts/abc123`. **Copy it — you need it in §12.**

---

## §12 — Pin the comment (2 min)

### 12.1 Open the published Short

Paste the URL into a new tab (the logged-in one, as the channel owner).

### 12.2 Post the pinned comment first

Scroll down to the comments section. Paste the **PINNED COMMENT** block from `metadata.md` (the "Quick links from this Short:" block). Click **Comment**.

### 12.3 Then pin it

Next to your just-posted comment, click the three-dot menu **⋮** → **Pin** → **Confirm pin**.

You should see a blue "📌 Pinned by @yourhandle" label appear above the comment.

**If the ⋮ menu doesn't show a Pin option:** comments are disabled, or you're not logged in as the channel owner. Check YT Studio → Settings → Community.

---

## §13 — Track at T+6h and T+24h

### 13.1 T+6h (6 hours after publish)

Open YT Studio → Content → click `s001` → Analytics → Reach tab.

Record in `s001/tracking.md`:

```
## T+6h — <timestamp>
Views:                   {number}
Impressions:             {number}
Swipe-away rate:         {%}
Avg view duration:       {%}
Dub.co clicks (from https://app.dub.co):  {number}
```

### 13.2 T+24h

Open all three: YT Studio, Dub.co, PartnerStack.

```
## T+24h — <timestamp>
Views:                   {number}
Avg view duration:       {%}
External CTR (Dub/Views): {%}
PartnerStack clicks:     {number}
PartnerStack conversions (pending): {number}
```

### 13.3 Decision at T+48h (following day)

Consult this table:

| Views @ 48h | Action |
|---|---|
| ≥ 10,000 | Queue **Short #2** as same-format sequel (different tool — try HeyGen) within 72h. |
| 1,000-9,999 | Good baseline. Queue Short #2 with same format, new tool. |
| 500-999 | Keep format, rewrite hook. Queue Short #2. |
| < 500 | Unlist `s001` (not delete). Rewrite hook format for Short #2. |

---

## 🚨 Fallback shortcuts (if you fall > 30 min behind)

| Bottleneck | Shortcut |
|---|---|
| Kling generation slow or failing | Skip Kling 2, 3, 4 (dashboard variants). Re-use Kling 1 (microphone) for the entire 0:15-0:45 stretch with aggressive Ken-Burns (scale 100→140%) + different positional crops. |
| Seedance fails or queues too long | Skip Seedance entirely. Use Kling 1 (microphone) at 0:00-0:15 with a slow Ken-Burns. You lose 2 points of retention signal but still ship today. |
| CapCut auto-caption garbles most of the narration | Type the 5 narration beats manually as 5 text boxes on V3 at the time ranges from §3. No shame. |
| Chinese translation mangles tool names | Skip Chinese SRT for Short #1. Upload EN-only. Add ZH for Short #2. (One day's delay on bilingual is acceptable; zero Shorts shipped is not.) |
| Thumbnail generation fails | Skip custom thumbnail. YouTube auto-picks a frame. Acceptable for Short #1 — Shorts feed often overrides thumbnails anyway. |
| PartnerStack ElevenLabs not yet approved | Use the **direct ElevenLabs affiliate page** — 🔗 https://elevenlabs.io/affiliates — sign up directly (auto-approves). Skip Dub, use the raw link with `?utm_campaign=s001` appended. You lose per-link Dub analytics but ship today. |

---

## ✅ Definition of "Shipped"

You are DONE with Short #1 when ALL of these are true:

- ✅ `s001.mp4` exists at `s001/export/s001.mp4`, 1080×1920, 58-62s
- ✅ YT URL exists, publicly viewable in incognito window
- ✅ Thumbnail loads on the YT URL
- ✅ Pinned comment is visible with Dub link
- ✅ `zh-CN.srt` track is attached on YT Studio's video page
- ✅ Description has the Dub link on line 3 and `#ad` on line 1
- ✅ `s001/tracking.md` has a `## T+6h` section filled in

When all 7 ✅ pass: Short #1 is shipped. Stop. Do not tweak. Go to bed (or lunch). Return at T+24h.

---

## Files produced

```
reports/2026-04-19/yt_shorts_mvp_short1/
└── s001/
    ├── script.md
    ├── narration.txt
    ├── metadata.md
    ├── tracking.md
    ├── audio/
    │   └── narration.mp3
    ├── kling/
    │   ├── kling_1_mic.png
    │   ├── kling_2_waveform.png
    │   ├── kling_3_bars.png
    │   ├── kling_4_rings.png
    │   ├── kling_5_before_after.png
    │   ├── kling_6_desk.png
    │   └── thumb_base.png
    ├── seedance/
    │   └── seedance_1_hero.mp4
    ├── s001_zh-CN.srt
    └── export/
        ├── s001.mp4
        └── s001_thumb.png
```

This exact tree = Short #1 complete.
