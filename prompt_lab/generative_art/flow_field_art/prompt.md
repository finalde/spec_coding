# Flow Field Art — mesmerizing particle flow, one HTML file

**Stack:** single `index.html` (canvas + JS, no deps) · **Est:** 5–15 min · **Output:** living generative art you can reseed + save as PNG

## ✨ 1. Expectation — what you'll get
Run the prompt and a single `index.html` springs to life: thousands of particles drift through a Perlin/simplex-noise vector field, each leaving a low-alpha trail that accumulates into silky, smoke-like ribbons of color in real time. Press a key to reseed and the whole composition reshuffles into something entirely new; tweak palette and flow, then hit S to export the canvas as a wallpaper-grade PNG. Every seed is a reproducible, gallery-worthy piece — the best wow-per-minute task in the library.

**Why it's cool:** There's no image library and no AI image model — just math: a hand-written noise function steering particles, and beauty *emerges* from a few simple advection rules. Watching organic, painterly structure self-assemble out of pure deterministic code feels like magic the first (and tenth) time.

**Use cases:** Generate one-of-a-kind desktop/phone wallpapers and 4K prints to frame; spin up a cohesive set of palette-matched social, album-cover, or event-poster backdrops where every post shares a signature look; run it as an ongoing generative-art series (save the seeds, mint or print the keepers); or read the source to actually learn noise fields, particle advection, and trail-accumulation rendering on canvas.

## ▶️ 2. How to run
Copy-paste-and-walk-away: paste the prompt below into Claude Code in an empty folder, answer 2 short setup questions (palette + style), then it builds and opens autonomously. Press a key to reseed, S to save. Prerequisites: none — opens in any modern browser.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [Tyler Hobbs — Flow Fields](https://www.tylerxhobbs.com/words/flow-fields) · **Expected result:** [reference images](https://www.google.com/search?q=flow+field+generative+art&tbm=isch)

---

## 📋 COPY-PASTE PROMPT

```
You are building a flow-field generative-art piece as a SINGLE self-contained index.html file
(canvas + inline JS, no libraries — implement your own noise function; no build step).

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. Palette mood? (sunset-gradient / ocean-ink / monochrome-gold / acid-neon)
2. Style? (silky-thin-lines / painterly-thick-strokes / dotted-stipple)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, self-review against the checklist, fix, repeat.

Design:
- A 2D noise field (implement Perlin/simplex or value noise) defines a flow angle at each point.
- Thousands of particles advect through the field, leaving trails that build up into organic patterns.
- Low-alpha accumulation for silky layering; respawn particles to keep the canvas evolving.
- A seed controls the whole composition. Controls/keys: reseed (new artwork), pause, clear,
  and S = save the current canvas as a high-resolution PNG download.
- Tasteful color mapping (by angle / speed / position) per the chosen palette. Full-window, retina-aware.
- It should look gallery-worthy, not like debug output.

ACCEPTANCE CHECKLIST (finish line):
- [ ] Opens from index.html with zero console errors.
- [ ] Particles flow along a coherent noise field, building silky organic patterns.
- [ ] Reseed produces a clearly different composition each time.
- [ ] S saves a high-resolution PNG of the current artwork.
- [ ] Pause/clear work; palette + style match the chosen options.
- [ ] Smooth 60fps, full-window, looks genuinely beautiful.

STOP CONDITIONS: stop when every item passes, OR after 5 self-review rounds.
Then open index.html and tell me the keys (reseed / save) in 2 lines.
```

---

## Remix ideas
"Animate the field over time (curl noise)." · "Add a 'poster' export at 4K." · "Let the mouse bend the flow." · "Generate 5 named presets."
