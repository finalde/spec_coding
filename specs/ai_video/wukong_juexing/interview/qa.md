# Interview — wukong_juexing

Run: wukong_juexing-20260503-201831
Mode: AUTONOMOUS (user explicit: "you can make best judgement, proceed to stage 2 please")

## Settled facts (no probe — locked by `revised_prompt.md`)

| Field | Value | Source |
|---|---|---|
| `sub_type` | `short` | User: "short one like youtube shorts not a series" |
| Aspect ratio | 9:16 | `agent_refs/project/ai_video.md` rule 7; revised prompt hard constraint |
| Length target | ~40 s (35–55 s acceptable) | revised prompt soft target |
| Shot count | ~5 (4–6 acceptable) | revised prompt soft target |
| Cast size | 1 (孙悟空 only) | revised prompt out-of-scope rules out multi-character |
| File-content language | Chinese | `agent_refs/project/ai_video.md` rule 1 |
| Prompt-output language | Chinese | `agent_refs/project/ai_video.md` rule 5 (locked descriptor) |
| Audio / SFX prompts | None (visuals only) | `CLAUDE.md` § ai_video rules; revised prompt out-of-scope |
| Text overlays | None | revised prompt out-of-scope |
| Genre | Chinese mythology / cinematic transformation | revised prompt context paragraph |

## Categories probed

- **Visual register** — cinematic style is the largest unlocked variable; sets every shot's mood.
- **Hook shot opener** — first 2–2.5 s is decisive for Shorts retention; needs a literal image, not just an idea.
- **Character look** — Sun Wukong has multiple iconic visual treatments; one must be locked before the Seedream prompt is written.
- **Setting / environment** — five shots in one location vs five locations is a fundamentally different shotlist.
- **Payoff structure** — the closing 2 s decides whether the Short is loop-able and whether it triggers replays.

(Platform was a candidate probe but `revised_prompt.md` already commits to YouTube Shorts; cross-publish to 抖音/视频号 is captured below as a low-risk optional add since the file content is already Chinese.)

---

## Round 1

### Visual register

**Q:** Which cinematic style do we lock in `style_guide.md`?

- A: **Photoreal "weighty mythic realism" — *Black Myth: Wukong* register** — grounded textures, naturalistic lighting, dust/dirt/wear, restrained colour palette **(Recommended)**
- B: Stylised cel-shaded anime — flat colour planes, ink linework, exaggerated proportions
- C: Traditional Chinese ink painting (水墨) — desaturated greys, brush-stroke aesthetic, negative space
- D: Hybrid — photoreal character + stylised painterly background

**A** *(judgment call — chose A because: revised prompt explicitly anchors to *Black Myth: Wukong* register; AI generators (Kling/Seedance) are strongest on photoreal physics + fluid motion, weaker on consistent flat-line cel-shaded styles; one-character single-IP cinematic is the lowest-risk first-pipeline test. Binds into FR-style_guide.)*

### Hook shot opener (Shot 01)

**Q:** What literal image fills frame 0–2.5 s?

- A: **Stone egg cracking — golden light bursting from fissures, slow zoom on the breaking surface** **(Recommended)**
- B: Extreme close-up on a closed monkey eye → eye snaps open with golden iris glow
- C: Lightning strike on a mountaintop → silhouette of a monkey figure revealed mid-pose
- D: Bird's-eye view of 花果山 + 水帘洞 → camera dives toward the cave entrance

**A** *(judgment call — chose A because: stone-egg crack is canonical 西游记 origin imagery (instant recognition for Chinese audience, intriguing for Western); golden-light bursts give the dramatic FX moment Kling/Seedance handle best; matches the loop-back payoff (option A in the payoff probe below). Binds into FR-shot01.)*

### Character look

**Q:** Which Sun Wukong visual treatment locks the Seedream descriptor?

- A: **Battle-worn warrior — fur scarred, simple cloth wrap + light armor pieces, traditional 凤翅紫金冠 headpiece, 金箍棒 visible — "post-rebellion Wukong" *Black Myth*-leaning** **(Recommended)**
- B: Classical 戏曲 opera Wukong — full red-yellow opera costume, painted face, ornate headdress, theatrical
- C: Minimalist origin Wukong — just fur and a simple loincloth, no armor, no weapon yet (matches "just-awakened" beat)
- D: Modern reinterpretation — sleek dark armor, glowing rune accents, minimal traditional cues

**A** *(judgment call — chose A because: visually unambiguous and unmistakably Wukong, complements the *Black Myth* visual register, and the headpiece + 金箍棒 are the two highest-recognition visual cues in Chinese mythology — they read instantly even in a 2-second hook frame. Option C ("just awakened") is internally inconsistent with showing him summon a cloud + brandish a staff in later shots; option B is too theatrical for the photoreal register; option D dilutes IP recognition. Binds into FR-character-main.)*

### Setting / environment

**Q:** How many distinct settings across the 5 shots?

- A: **Single setting — mountaintop at dusk under starry sky, with the broken stone in foreground throughout** — character moves around the same locale
- B: **Two-setting micro-arc — open on cracking-stone close-up (no establishing locale) → wide reveal mountain + sky for shots 2–5** **(Recommended)**
- C: Three-act setting — cave interior (origin) → mountain (transformation) → sky/cloud (ascension)
- D: Pure black void — character against featureless dark backdrop, light/effects only

**A** *(judgment call — chose A's intent but executed as B because: single-setting keeps continuity tight for AI generation (lighting + background lock = far easier character consistency across shots), but the opening close-up on the stone benefits from NOT showing the wider locale until shot 02 — this lets the wide-reveal moment double as the second hook beat. Three-act setting (C) blows the Seedream-ref-image budget and is too ambitious for a first project. Binds into FR-shotlist + FR-style_guide.)*

### Payoff structure

**Q:** What does the closing 2 s of Shot 05 do?

- A: **Loop-back — final frame echoes the opening cracking-stone close-up (golden light fading), inviting replay** **(Recommended)**
- B: Power-pose freeze — Wukong mid-stance with 金箍棒 raised, frozen for ~1 s
- C: Cliffhanger — silhouette of an unseen adversary appears at frame edge (sets up nothing; pure tease)
- D: Camera pull-back — mountaintop shrinks into a vast starscape, "smallness against the cosmos" beat

**A** *(judgment call — chose A because: research-confirmed loop-able Shorts retrigger the algorithm via replay-counts; the cracking-stone callback ties the short into a complete circle without requiring a sequel, which matches the "single piece, no series" scope. Option B is fine but doesn't loop. Option C is dishonest (no payoff coming) and may frustrate viewers. Option D is the most "art-film" but lowest-energy ending for the Shorts algorithm. Binds into FR-shot05.)*

---

## Round 2

Not run. All five categories are clear after one autonomous round — each has a locked answer with cited rationale. No internal contradictions, no follow-up ambiguity that the spec stage couldn't resolve.

## Optional cross-publish note

The user said "youtube shorts" but file content is Chinese, which equally suits 抖音 / 视频号 / 小红书. `publish.md` will be written in Chinese with hashtags that work cross-platform; specific platform metadata variants are deferred to a follow-up if the user wants them. *(judgment call — same Chinese metadata covers both YouTube Shorts (Chinese-content channels) and Douyin without a per-platform fork; if the user later wants English-language YouTube Shorts metadata too, that's a one-paragraph follow-up.)*

## Team consensus

All probed categories marked clear after **1 autonomous round**. Stage 3 (research) inputs are fully specified.
