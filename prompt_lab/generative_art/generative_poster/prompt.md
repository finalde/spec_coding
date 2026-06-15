# Generative Poster — seeded, export-ready design system

**Stack:** single `index.html` (canvas/SVG + JS, no deps) · **Est:** 15–25 min · **Output:** infinite unique posters, exportable as SVG + hi-res PNG

## ✨ 1. Expectation — what you'll get
Run the prompt and you get a generative graphic-design system in a single `index.html`: each seed composes a complete, balanced poster — a layout grid, a harmonious limited palette, a real type hierarchy, and generative shapes that compose *with* the type rather than fight it — all in a coherent design language you chose. Tap spacebar to reroll into endless fresh-but-tasteful variations, type a seed to reproduce any poster exactly, lock the keepers, then export crisp vector SVG plus a 300-DPI print-grade PNG. The result looks intentionally art-directed, not like random clutter.

**Why it's cool:** A seeded PRNG drives every single choice, so design becomes *deterministic* — the same seed yields the identical poster forever, yet the space of seeds is effectively infinite. It's Claude doing real graphic design with taste and constraints, turning a number into a finished, print-ready composition.

**Use cases:** Reroll until you find a poster, album cover, or event flyer worth printing and framing; generate an on-brand series of social graphics that share a grid and palette but never repeat; produce a unique, reproducible print as a personalized gift (gift the seed with it); or read the code to learn seeded PRNGs, grid systems, type-scale hierarchy, color-theory palettes, and SVG/PNG export — a working lesson in design systems.

## ▶️ 2. How to run
Copy-paste-and-walk-away: paste the prompt below into Claude Code in an empty folder, answer 2 short setup questions (design language + theme/words), then it builds and opens autonomously. Spacebar to reroll, E to export. Prerequisites: none — opens in any modern browser.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [mattdesl/canvas-sketch](https://github.com/mattdesl/canvas-sketch) · **Expected result:** [reference images](https://www.google.com/search?q=swiss+style+generative+poster&tbm=isch)

---

## 📋 COPY-PASTE PROMPT

```
You are building a generative POSTER design system as a SINGLE self-contained index.html file
(canvas or SVG + inline JS, no libraries, no build step). Each seed yields a complete, well-composed poster.

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. Design language? (swiss-international-typographic / bauhaus-geometric / brutalist-web / risograph-retro)
2. Poster theme/words? (give me a short title + subtitle, OR say "you pick" and I'll invent tasteful ones)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, self-review against the checklist, fix, repeat.

Design:
- A seeded PRNG drives EVERY choice so a seed reproduces the exact poster. Reroll = new seed.
- Generate within real design constraints for the chosen language: a layout grid, a harmonious color
  palette (use color theory, limited palette), a type hierarchy (title/subtitle/caption) with good
  scale + spacing, and generative shapes/patterns/lines that compose with — not fight — the type.
- Enforce balance: margins, alignment to the grid, visual weight distribution, and contrast. The output
  should look intentionally designed, like a human did it, not random clutter.
- Controls/keys: spacebar = reroll seed, a seed input field (type a seed to reproduce), L = lock current,
  and E = export. Export BOTH crisp SVG and a 300-DPI PNG (poster-print resolution).
- Show the current seed on screen so good ones can be saved.

ACCEPTANCE CHECKLIST (finish line):
- [ ] Opens from index.html with zero console errors.
- [ ] Each reroll yields a NEW poster that still looks well-composed (grid, hierarchy, balance hold).
- [ ] The same seed reliably reproduces the same poster.
- [ ] Typography is legible with a clear hierarchy; palette is harmonious; layout respects a grid.
- [ ] SVG export is vector-crisp; PNG export is high-resolution (print-grade).
- [ ] Output genuinely looks designed in the chosen language, not like noise.

STOP CONDITIONS: stop when every item passes, OR after 6 self-review rounds.
Then open index.html, reroll a few times to show range, and tell me the keys (reroll/lock/export) + a nice seed.
```

---

## Remix ideas
"Add album-cover and event-flyer formats." · "Add a contact-sheet of 12 thumbnails to pick from." · "Add a dark/light variant per poster." · "Batch-export 20 PNGs."
