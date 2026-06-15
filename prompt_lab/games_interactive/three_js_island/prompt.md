# Floating Island — flyable 3D scene (Three.js)

**Stack:** single `index.html` + Three.js via CDN · **Est:** 15–30 min · **Output:** a 3D world you fly through in-browser

## ✨ 1. Expectation — what you'll get
Pick a time-of-day vibe and a movement style, and Claude builds a low-poly floating island suspended over a void that you actually pilot in real time: click to capture the mouse, fly with WASD, and roam past animated water lapping the island's edge, trees swaying in the breeze, clouds drifting overhead, soft dynamic shadows, fireflies that wink on as dusk falls, and a slow day/night cycle that recolors the whole sky — all wrapped in a warm bloom glow. It runs from a single HTML file in one browser tab (Three.js streams from a CDN, no install) and holds a smooth ~60fps on a laptop. The result is a living, atmospheric 3D world you can explore and screenshot the moment it opens.

**Why it's cool:** It's the most jaw-dropping "show this to anyone" demo in the library — a self-contained file with no build step that produces a breathing, cinematic 3D environment, complete with post-processing bloom and a moving sun, that you'd swear came out of a game engine.

**Use cases:** Use it as the centerpiece "wow" exhibit in a creative-coding portfolio or demo reel; spin it up as a Three.js project starter and grow it into a walking sim, level, or product showcase; study the one file to learn scene graphs, PointerLock/Orbit camera controls, shader-ish water, and post-processing passes; or run it live as a teaching demo for how real-time 3D lighting and day/night cycles work in the browser.

## ▶️ 2. How to run
Copy-paste-and-walk-away: paste the prompt below into Claude Code in an empty folder, answer the 2 short setup questions (time of day, movement style), then it builds autonomously to completion and opens the scene. Click to capture the mouse, WASD to fly. Prerequisites: none — opens in any modern browser (Three.js loads from a CDN).

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [mrdoob/three.js](https://github.com/mrdoob/three.js) · **Expected result:** [reference images](https://www.google.com/search?q=low+poly+floating+island+three.js&tbm=isch)

---

## 📋 COPY-PASTE PROMPT

```
You are building an interactive 3D scene as a SINGLE self-contained index.html file using
Three.js loaded from a CDN (import map / module CDN). No build step, no local install.

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. Time of day vibe? (golden-hour / blue-hour-night / overcast-dawn)
2. Movement style? (free-fly WASD+mouse / orbit-only camera)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, self-review against the checklist by
reasoning through the code, fix failures, repeat.

Scene design:
- A low-poly floating island (terrain mesh with a few elevation zones) suspended over a void.
- Animated water plane (vertex-displacement or shader) around/under the island.
- Scatter stylized low-poly trees and rocks; trees sway subtly.
- A few volumetric-ish clouds drifting slowly.
- Directional sun light with soft shadows; ambient + hemisphere light for the chosen time of day.
- Particle "fireflies" that become visible as the day/night cycle dims.
- A slow automatic day/night cycle (sun moves, sky color + fog shift). Bloom post-processing for glow.
- Controls per my choice (PointerLockControls for free-fly, OrbitControls otherwise).
- Lightweight: keep poly counts modest so it holds 60fps on a laptop.

ACCEPTANCE CHECKLIST (finish line):
- [ ] Loads with zero console errors; renders the island immediately.
- [ ] Chosen controls work (fly or orbit) and feel smooth.
- [ ] Water animates; trees sway; clouds drift.
- [ ] Shadows render and the day/night cycle visibly changes lighting + sky.
- [ ] Fireflies appear at night; bloom makes lights glow.
- [ ] Holds ~60fps (no obvious stutter) on a typical laptop.

STOP CONDITIONS: stop when every item passes, OR after 6 self-review rounds.
Then open index.html in my browser and tell me the controls in 3 lines.
```

---

## Remix ideas
"Add a controllable low-poly airplane." · "Add a waterfall off the island edge." · "Add ambient wind audio." · "Make a second island with a rope bridge."
