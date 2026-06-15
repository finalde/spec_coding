# Gravity Golf — orbital physics game in one HTML file

**Stack:** single `index.html` (inline CSS + JS, no deps) · **Est:** 10–20 min · **Output:** a browser game you can share as one file

## ✨ 1. Expectation — what you'll get
Answer three quick setup questions and Claude builds, level by level, a genuinely playable "gravity golf" game that opens in your browser as one shareable HTML file: drag back from the ball to aim and set power, watch a live trajectory arc bend as you adjust, then release to slingshot it through orbits around multiple planets and sink it in the glowing goal in as few strokes as you can. It arrives fully juiced — neon palette, comet-tail particle trail, screen-shake on impact, Web Audio blips on launch and sink, and a handful of hand-authored levels with a real win screen. The end result is a small indie-feeling game in a single file you can double-click to play or email to someone.

**Why it's cool:** The planets pull the ball with real summed inverse-square gravity, so the orbital slingshots and gravity-assist curves actually emerge from physics rather than scripted paths — a tiny no-dependency file that behaves like an orbital mechanics sandbox.

**Use cases:** Drop it in a portfolio as a self-contained "I shipped a physics game" showcase piece; fork it as a game-jam starter and bolt on black holes, wind, or a level editor; read the single file to learn canvas rendering, the game loop, and how N-body gravity integration works in practice; or text the one HTML file to friends as a quick par-chasing challenge.

## ▶️ 2. How to run
Copy-paste-and-walk-away: paste the prompt below into Claude Code in an empty folder, answer the 3 short setup questions (theme, difficulty, level count), then it builds autonomously to completion and opens the game in your browser. Prerequisites: none — opens in any modern browser.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [The Nature of Code (forces & attraction)](https://natureofcode.com/) · **Expected result:** [reference examples](https://www.youtube.com/results?search_query=gravity+golf+orbital+game)

---

## 📋 COPY-PASTE PROMPT

```
You are building a complete browser game as a SINGLE self-contained index.html file
(inline CSS + JavaScript, no external libraries, no build step).

PHASE 1 — SETUP (ask me these 3 questions, then STOP and wait for my answers):
1. Visual theme? (neon-space / pastel-minimal / retro-arcade)
2. Difficulty curve? (chill / balanced / brutal)
3. Number of levels? (default 6)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, then self-review against the
acceptance checklist below by actually reasoning through the code, fix every failing item, repeat.

Game design:
- 2D canvas. Drag from the ball to set aim direction + power (show a predicted trajectory arc while dragging).
- Newtonian gravity from each planet (inverse-square, summed). Ball orbits/slingshots realistically.
- Goal = a glowing hole; sink the ball to win the level. Collisions with planets reset the shot.
- HUD: shot counter, par, level number. Win screen with total strokes and a "next level" button.
- Hand-design each level with distinct planet layouts so they feel authored, not random.
- Juice: particle trail behind the ball, screen-shake on collision, Web Audio API blips for launch/sink.

ACCEPTANCE CHECKLIST (this is the finish line):
- [ ] Opens directly from index.html with zero console errors.
- [ ] Aim-drag shows a live trajectory preview; releasing launches the ball.
- [ ] Gravity visibly curves the ball's path around planets.
- [ ] All levels are completable; sinking advances to the next.
- [ ] Shot counter, par, and win screen all work.
- [ ] Sound plays on launch and sink; particle trail renders.
- [ ] Looks polished in the chosen theme (cohesive palette, glow, smooth 60fps).

STOP CONDITIONS: stop when every checklist item passes, OR after 6 self-review rounds.
Then open index.html in my default browser and give me a 3-line summary of what to try.
```

---

## Remix ideas
"Add a moving black hole on level 5." · "Add a 2-player hot-seat mode." · "Add wind." · "Make a level editor."
