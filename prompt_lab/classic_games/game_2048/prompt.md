# a 2048 game

**Stack:** single `index.html` (canvas or CSS grid + JS, no deps) · **Est:** 15–25 min · **Output:** a polished, animated, playable 2048

## ✨ 1. Expectation — what you'll get
Open one file in your browser and you're sliding numbered tiles across a 4×4 grid, watching them glide and merge with buttery animations while your score ticks up. Hit 2048 and a victory overlay drops; jam yourself into a corner and a clean game-over screen offers a restart. Your best score sticks around between sessions, and a single Undo button bails you out of that one fatal swipe.

**Why it's cool:** It's the addictive puzzle everyone knows, rebuilt from scratch in one dependency-free file — the kind of thing you can drop on any static host and instantly share a link to.

**Use cases:** A portfolio piece that proves you can ship game logic + animation in vanilla JS · a readable codebase for learning merge algorithms and `requestAnimationFrame` · something genuinely fun to share with friends · a teaching example for grid state and keyboard/touch input.

## ▶️ 2. How to run
Copy-paste-and-walk-away: paste the prompt below into Claude Code in an empty folder, answer the short setup questions, then it runs autonomously to completion and opens the result. Prerequisites: none — opens in any modern browser.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [gabrielecirulli/2048](https://github.com/gabrielecirulli/2048) · **Expected result:** [play 2048](https://play2048.co/)

---

## 📋 COPY-PASTE PROMPT

```
Build me a complete, polished 2048 game as a SINGLE self-contained index.html file.
Everything — HTML, CSS, and JavaScript — lives inline in that one file. No external
libraries, no frameworks, no CDN links, no build step. It must open and run by
double-clicking the file in any modern browser.

PHASE 1 — SETUP (ask, then STOP):
Ask me these 2–3 short setup questions, then WAIT for my answer before writing any code:
  1. Color theme? (e.g. "classic warm" like the original, "neon dark", "pastel", or
     describe your own)
  2. Grid size? (default 4×4 — the standard; offer 5×5 as an option)
  3. Win tile? (default 2048 — but allow continuing past it after the win overlay)
Do not write code yet. Just ask and stop.

PHASE 2 — AUTONOMOUS BUILD (after I answer):
After I answer, DO NOT ask anything else. Loop until the ACCEPTANCE CHECKLIST below
fully passes. Treat the file system as your memory: write index.html, then re-open and
re-read it each round, self-review it against the checklist, fix what fails, and repeat.
Each round: implement → self-review against every checklist item → fix → repeat.

Build the full game:
  - A 4×4 (or chosen size) grid. New game spawns two tiles (a 2 or 4, weighted ~90%/10%).
  - Arrow keys (and WASD) move all tiles in a direction; touch/pointer SWIPE works on
    mobile and trackpads.
  - Correct merge rules: tiles slide as far as possible, then equal adjacent tiles merge
    into their sum. A tile that just merged this move CANNOT merge again in the same move
    (no chained double-merges). Merging resolves in the direction of travel.
  - A move is only valid if at least one tile actually moved or merged; after a valid
    move, spawn exactly one new tile in a random empty cell.
  - Smooth animations: tiles SLIDE to their new position, merges POP/scale, and newly
    spawned tiles fade/scale in. Use requestAnimationFrame or CSS transitions — motion
    must look fluid, not snap.
  - Score increases by the value of each merged tile. Best score persists in localStorage
    and survives a page reload.
  - Win detection: reaching the win tile shows a "You win!" overlay with options to keep
    going or start fresh. Game-over detection: when no moves remain (board full and no
    adjacent equal tiles), show a "Game over" overlay with a restart button.
  - An Undo button that reverts the last move (restore the prior board + score). One level
    of undo is enough; more is a bonus.
  - A New Game button. A cohesive visual theme matching my chosen colors, with distinct,
    legible tile colors that scale up to large numbers (2048, 4096+).

ACCEPTANCE CHECKLIST (the finish line):
  [ ] Arrow keys AND swipe both move tiles correctly in all four directions.
  [ ] Merge rules are exact: tiles slide fully, equal tiles merge once, and a merged tile
      does NOT merge again in the same move.
  [ ] Slide, merge-pop, and spawn animations are smooth and visually correct.
  [ ] Score updates correctly; best score persists across reloads via localStorage.
  [ ] Win (reaching the win tile) shows an overlay with continue/restart.
  [ ] Game over (no legal moves) is detected and shows a restart overlay.
  [ ] Undo restores the exact previous board state and score.
  [ ] No console errors; layout is responsive and centered; everything is in ONE file.

STOP CONDITIONS:
Stop when EVERY checklist item passes, OR after 6 self-review rounds — whichever comes
first. Then open index.html in the browser and give me a short, plain-language how-to-play
summary (controls, goal, what Undo does). If you stopped on the round cap with anything
unchecked, list exactly what remains.
```

---

## Remix ideas
Add an animated "joined the board" trail when tiles merge · Add a 60-second time-attack mode with a countdown · Add an AI auto-solver that plays itself with a corner strategy · Add sound effects + a mute toggle synced to localStorage
