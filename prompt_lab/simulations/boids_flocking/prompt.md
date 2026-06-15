# Boids — flocking simulation in one HTML file

**Stack:** single `index.html` (canvas + JS, no deps) · **Est:** 10–20 min · **Output:** a hypnotic flocking sim with live controls

## ✨ 1. Expectation — what you'll get
Run the prompt and a few hundred arrow-shaped agents scatter across the canvas, then within seconds self-organize into rippling, splitting, re-merging flocks — Craig Reynolds' classic boids, each steering by only three local rules: separation, alignment, cohesion. Drag your mouse through the swarm and the whole murmuration bends around it like a predator passing through starlings; nudge the sliders and the flock loosens into a loose scatter or tightens into a dense, banking school in real time.

**Why it's cool:** Nothing here is choreographed — the hypnotic, ever-shifting murmuration is pure emergence from three lines of vector math, the textbook example of how trivially simple local rules produce lifelike global behavior.

**Use cases:** A classroom demo for teaching emergence and complex adaptive systems — toggle one rule off and watch coherence collapse. A live generative-art or projection-installation visual that never loops or repeats. A calm ambient screensaver / second-monitor backdrop. A readable reference for learning spatial-hashing / neighbor-query optimization, since the code must keep thousands of pairwise checks at 60fps.

## ▶️ 2. How to run
Copy-paste-and-walk-away. Paste the prompt below into Claude Code in an empty folder, answer the 2 short setup questions, and it builds the whole thing autonomously, then opens the sim. Prerequisites: none — opens in any modern browser.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [beneater/boids](https://github.com/beneater/boids) · **Expected result:** [reference videos](https://www.youtube.com/results?search_query=boids+flocking+simulation)

---

## 📋 COPY-PASTE PROMPT

```
You are building a boids flocking simulation as a SINGLE self-contained index.html file
(canvas + inline JS, no libraries, no build step).

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. Vibe? (starlings-dusk / neon-particles / minimal-ink)
2. Flock size? (default ~300 boids)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, self-review against the checklist, fix, repeat.

Design:
- Classic boids: each agent steers by separation + alignment + cohesion within a neighbor radius,
  plus speed limits and edge handling (wrap or steer-back). Smooth, stable flocking.
- The mouse acts as an attractor (or predator the flock flees — pick one and make it feel alive).
- Live control panel: sliders for separation/alignment/cohesion weights, neighbor radius, max speed,
  and boid count; a pause/reset button; an FPS readout.
- Boids rendered as oriented triangles/arrows with subtle trails. Performant for the chosen count
  (spatial hashing or grid if needed to keep 60fps).
- Cohesive look for the chosen vibe.

ACCEPTANCE CHECKLIST (finish line):
- [ ] Opens from index.html with zero console errors.
- [ ] Agents form coherent, lifelike flocks (not random or clumped-frozen).
- [ ] All sliders visibly change behavior in real time; pause/reset work.
- [ ] Mouse interaction visibly affects the flock.
- [ ] Holds ~60fps at the chosen count (optimize neighbor lookups if needed).
- [ ] Looks polished in the chosen vibe with oriented boids + trails.

STOP CONDITIONS: stop when every item passes, OR after 5 self-review rounds.
Then open index.html and tell me which sliders to play with for the coolest effects.
```

---

## Remix ideas
"Add obstacles the flock avoids." · "Add multiple species with different rules." · "Add a real hawk predator." · "Add a day/night color cycle."
