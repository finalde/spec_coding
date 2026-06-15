# Particle Life — emergent lifelike behavior from simple attraction rules

**Stack:** single `index.html` (canvas + JS, no deps) · **Est:** 15–25 min · **Output:** an emergent-life sim that looks alive

## ✨ 1. Expectation — what you'll get
Run the prompt and thousands of glowing colored dots swarm a black canvas, attracting and repelling each other by a random matrix of signed weights — and from those trivially simple rules, membranes, chasing pairs, pulsing cells, and whole crawling "organisms" *emerge* and drift across the screen. Hit "Randomize rules" and the universe reseeds instantly into a completely new set of lifeforms; nudge the force, friction, and radius sliders and watch a stable ecosystem melt into a roiling soup or freeze into crystalline lattices.

**Why it's cool:** It's the ultimate "wait, that's just math?" demo — lifelike, self-organizing, reproducing-looking structure with zero biology coded in, just signed weights and a distance, a striking illustration of how complexity bootstraps itself from almost nothing.

**Use cases:** A vivid hook for teaching emergence, self-organization, and artificial-life concepts without any equations on the board. A generative-art engine for endless one-of-a-kind glow visuals or installation loops. A mesmerizing ambient background / screensaver you can leave running. A compact study piece for learning spatial-grid partitioning and N-body force integration by reading the code, since the whole sim hinges on making thousands of short-range interactions cheap.

## ▶️ 2. How to run
Copy-paste-and-walk-away. Paste the prompt below into Claude Code in an empty folder, answer the 2 short setup questions, and it builds the whole thing autonomously, then opens the sim. Prerequisites: none — opens in any modern browser.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [hunar4321/particle-life](https://github.com/hunar4321/particle-life) · **Expected result:** [reference videos](https://www.youtube.com/results?search_query=particle+life+simulation)

---

## 📋 COPY-PASTE PROMPT

```
You are building a "particle life" emergent-behavior simulation as a SINGLE self-contained index.html file
(canvas + inline JS, no libraries, no build step).

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. Palette? (vivid-neon / earthy-organic / pastel)
2. Particle count? (default ~1500–3000 depending on performance)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, self-review against the checklist, fix, repeat.

Design:
- N particles in K color types (e.g. 4–6 colors). A KxK "attraction matrix" of signed weights defines how
  each type is attracted to/repelled by each other type within a max radius.
- Per frame: compute interaction forces (short-range repulsion to avoid collapse + the matrix attraction),
  integrate with velocity + friction, wrap or bound edges. Tune constants so lifelike structures emerge
  (clusters, chasers, membranes) rather than instant collapse or explosion.
- Performance: use a spatial grid so it stays smooth at the chosen count (target 60fps).
- Controls: a "Randomize rules" button (reseed the matrix → new lifeforms), sliders for force strength,
  friction, radius, and particle count; pause/reset; and a small visualization of the current rule matrix.
- Beautiful additive-glow rendering in the chosen palette.

ACCEPTANCE CHECKLIST (finish line):
- [ ] Opens from index.html with zero console errors.
- [ ] Emergent structures clearly form (clusters/chasers/cells) — not collapse-to-a-dot or fly-apart.
- [ ] "Randomize rules" produces visibly different behavior each time.
- [ ] Sliders change dynamics live; pause/reset work; the rule matrix is shown.
- [ ] Holds ~60fps at the chosen count via spatial partitioning.
- [ ] Looks striking with glow rendering in the chosen palette.

STOP CONDITIONS: stop when every item passes, OR after 6 self-review rounds.
Then open index.html and tell me to keep hitting "Randomize rules" to discover new lifeforms.
```

---

## Remix ideas
"Let me save/load interesting rule seeds." · "Add a 3D version with Three.js." · "Show a 'fitness' metric per ecosystem." · "Mouse-stir the soup."
