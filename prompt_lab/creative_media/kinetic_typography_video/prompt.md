# Kinetic Typography Video — an animated explainer, all in code

**Stack:** single `index.html` (canvas/SVG + CSS animation, no deps) · **Est:** 10–20 min · **Output:** a 20s vertical animated video you can screen-record

## ✨ 1. Expectation — what you'll get
Run the prompt and a single hand-written `index.html` opens in your browser and immediately auto-plays a 1080×1920 vertical explainer: a tight 5-scene script with staggered word reveals, slide/scale/mask transitions, drifting background motion, and a progress bar that loops cleanly. Hit "R" to replay, screen-record the tab, and you walk away with a polished Shorts/Reels-ready animated video — no editor, no timeline, no video files.

**Why it's cool:** A broadcast-style motion-graphics video comes out of pure code — every frame is computed by a `requestAnimationFrame` sequencer, so you go from a topic sentence to a publishable vertical explainer in minutes instead of an afternoon in After Effects.

**Use cases:** Crank out daily "did you know" explainer Shorts/Reels/TikToks on autopilot; produce branded title cards and animated intros for a YouTube channel; build quick educational micro-lessons (one concept per scene) for a course or social feed; or learn canvas/CSS animation timing and easing by reading a self-contained sequencer you can tweak live.

## ▶️ 2. How to run
Copy-paste-and-walk-away. Paste the prompt below into Claude Code in an empty folder, answer 2 short setup questions (topic + mood), then it builds autonomously and auto-plays the video. Prerequisites: none — just a modern browser. To export a real .mp4, screen-record the tab (the prompt explains how).

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [juliangarnier/anime (anime.js)](https://github.com/juliangarnier/anime) · **Expected result:** [reference videos](https://www.youtube.com/results?search_query=kinetic+typography+animation)

---

## 📋 COPY-PASTE PROMPT

```
You are building an animated kinetic-typography "explainer video" as a SINGLE self-contained index.html
file (canvas or SVG + CSS/JS animation, no libraries, no build step). Canvas is 1080x1920 (vertical, 9:16),
scaled to fit the window. It should auto-play and loop, with a visible progress bar.

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. Topic? (e.g. "How does the internet work?", "Why is the sky blue?", "What is compound interest?")
   — if I say "you pick", choose a punchy one and tell me which.
2. Mood? (energetic-bold / calm-elegant / techy-neon)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, self-review against the checklist, fix, repeat.

Video design:
- Write a tight 5-scene script (~20s total) that explains the topic with one idea per scene.
- A timeline/sequencer drives scenes by elapsed time (requestAnimationFrame), each scene with its own
  staggered word/line reveals, easing, and transitions (slide, scale, mask, color sweeps).
- Editorial typography: strong type scale, kerned headlines, accent color per the mood, motion that
  emphasizes meaning (key words pop, transitions carry the eye).
- Background motion (gradient drift / particles / shapes) that supports, not distracts.
- Progress bar + a subtle scene counter. Loops cleanly. Optional Web Audio "tick" on key reveals (mutable).
- Include a one-line on-screen note "Press R to restart" and a comment explaining how to screen-record to mp4.

ACCEPTANCE CHECKLIST (finish line):
- [ ] Opens from index.html, auto-plays, zero console errors.
- [ ] Exactly 5 scenes play in sequence over ~20s and loop cleanly.
- [ ] Text reveals are staggered and synced; transitions are smooth at 60fps.
- [ ] Typography looks editorial-grade and matches the chosen mood.
- [ ] Progress bar tracks playback; R restarts.
- [ ] Renders correctly at 9:16 and scales to the window without clipping.

STOP CONDITIONS: stop when every item passes, OR after 6 self-review rounds.
Then open index.html and tell me (3 lines) the script + how to screen-record it.
```

---

## Remix ideas
"Make a 30s version." · "Add background music via Web Audio." · "Add my brand colors + logo." · "Generate 3 topic variations I can switch between."
