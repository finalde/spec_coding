# Procedural Roguelike — dungeon crawler in one HTML file

**Stack:** single `index.html` (canvas + JS, no deps) · **Est:** 20–40 min · **Output:** a replayable roguelike with procedural levels

## ✨ 1. Expectation — what you'll get
Choose a tileset, run length, and difficulty, and Claude builds a complete turn-based roguelike that opens in your browser as one HTML file: move with arrow keys or WASD through procedurally generated dungeons where every floor is a fresh maze of rooms and corridors, peel back the fog-of-war as your field-of-view reveals the map, bump into wandering enemies that chase and fight back, grab loot, level up HP and XP, descend the stairs floor by floor, and try to survive permadeath to the final level. Because the dungeons, loot, and encounters regenerate every run, it stays replayable instead of being a one-shot demo. The result is a real, finishable game — message log, HUD, victory and game-over screens included — in a single shareable file.

**Why it's cool:** It's the meatiest "Claude built a whole game" showcase in the library — procedural map generation, shadowcasting-style field-of-view, chase AI, and bump-to-attack combat all clicking together in one no-dependency file, with no two runs ever the same.

**Use cases:** Show it off as a substantial portfolio piece that proves you can ship a real game loop, not just a toy; use it as a game-jam starter and graft on a boss, shopkeeper, hunger, or shareable seeds; read the single file to learn the classic roguelike building blocks — BSP/random-walk dungeon gen, FOV, and turn scheduling — from working code; or run it as a teaching demo for procedural generation and grid-based AI.

## ▶️ 2. How to run
Copy-paste-and-walk-away: paste the prompt below into Claude Code in an empty folder, answer the 3 short setup questions (tileset, run length, difficulty), then it builds autonomously to completion and opens the game. Arrow keys / WASD to move. Prerequisites: none — opens in any modern browser.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [ondras/rot.js](https://github.com/ondras/rot.js) · **Expected result:** [reference images](https://www.google.com/search?q=javascript+browser+roguelike+dungeon&tbm=isch)

---

## 📋 COPY-PASTE PROMPT

```
You are building a turn-based roguelike as a SINGLE self-contained index.html file
(canvas or styled grid + inline JS, no external libraries, no build step).

PHASE 1 — SETUP (ask me these 3 questions, then STOP and wait):
1. Tileset style? (ascii-glyphs / emoji-tiles / simple-colored-blocks)
2. Run length? (short ~5 floors / medium ~10 floors)
3. Difficulty? (forgiving / classic-permadeath)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, self-review against the checklist,
fix failures, repeat.

Game design:
- Procedural dungeon generation: rooms connected by corridors (BSP or random-walk), per floor.
- Grid movement, turn-based: enemies act after each player move.
- Fog-of-war / field-of-view so the map reveals as you explore.
- Enemies with basic AI (wander, then chase when they see you). Bump-to-attack combat.
- Stats: HP, attack, XP/level-up. Loot on the floor (potions, weapons) that change stats.
- Stairs to descend; reaching the final floor = victory. Death = game over with run stats + restart.
- Clean HUD (HP bar, depth, level, message log) and readable map at the chosen tile style.

ACCEPTANCE CHECKLIST (finish line):
- [ ] Opens from index.html with zero console errors.
- [ ] Each run generates a different, fully-connected, walkable dungeon (no unreachable stairs).
- [ ] FOV/fog reveals correctly as the player moves.
- [ ] Combat works; enemies chase and can kill the player; player can kill enemies.
- [ ] Loot, XP/level-up, descending floors, victory, and death+restart all function.
- [ ] Message log narrates events; HUD always accurate.

STOP CONDITIONS: stop when every item passes, OR after 7 self-review rounds.
Then open index.html and give me a 4-line "how to play" summary.
```

---

## Remix ideas
"Add a shopkeeper between floors." · "Add a final boss." · "Add hunger/torch mechanics." · "Add a seed input so runs are shareable."
