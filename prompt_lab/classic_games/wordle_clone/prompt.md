# a Wordle clone

**Stack:** single `index.html` (vanilla JS, no deps) · **Est:** 15–25 min · **Output:** a daily word-guessing game with stats + share

## ✨ 1. Expectation — what you'll get
Open one file and you've got the full Wordle loop: six tries to guess a five-letter word, tiles flipping green/yellow/gray as you type, an on-screen keyboard that recolors to track your guesses. Everyone who plays on the same day gets the same word, your win streak and guess-distribution survive reloads, and a Share button spits out that familiar emoji grid you can paste anywhere.

**Why it's cool:** It nails the famously fiddly parts — duplicate-letter coloring and a deterministic daily word — in a single dependency-free file you can host anywhere and link to friends.

**Use cases:** A portfolio piece showing tricky game-state logic done right · a clean reference for learning seeded randomness and duplicate-letter handling · a fun daily game to share with a group · a teaching example for keyboard input, CSS animation, and localStorage stats.

## ▶️ 2. How to run
Copy-paste-and-walk-away: paste the prompt below into Claude Code in an empty folder, answer the short setup questions, then it runs autonomously to completion and opens the result. Prerequisites: none — opens in any modern browser.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [cwackerfuss/react-wordle](https://github.com/cwackerfuss/react-wordle) · **Expected result:** [Wordle](https://www.nytimes.com/games/wordle/index.html)

---

## 📋 COPY-PASTE PROMPT

```
Build me a complete, polished Wordle clone as a SINGLE self-contained index.html file.
Everything — HTML, CSS, and JavaScript — lives inline in that one file. No external
libraries, no frameworks, no CDN links, no build step, and NO network calls. The word
lists are embedded directly in the file. It must open and run by double-clicking the file
in any modern browser.

PHASE 1 — SETUP (ask, then STOP):
Ask me these 2–3 short setup questions, then WAIT for my answer before writing any code:
  1. Color theme? (e.g. "classic NYT light", "dark mode", "high-contrast" for
     colorblind-friendly orange/blue, or describe your own)
  2. Hard mode available? (in hard mode, revealed hints MUST be reused in later guesses —
     yes/no, and whether it's on by default)
  3. Daily word, or endless random words? (default: one deterministic daily word that's
     the same for everyone on a given date, with an optional "play random" button)
Do not write code yet. Just ask and stop.

PHASE 2 — AUTONOMOUS BUILD (after I answer):
After I answer, DO NOT ask anything else. Loop until the ACCEPTANCE CHECKLIST below
fully passes. Treat the file system as your memory: write index.html, then re-open and
re-read it each round, self-review it against the checklist, fix what fails, and repeat.
Each round: implement → self-review against every checklist item → fix → repeat.

Build the full game:
  - A 6×5 board: six guesses of a five-letter word.
  - Input via BOTH a clickable on-screen QWERTY keyboard AND the physical keyboard
    (letters type, Backspace deletes, Enter submits). Enter > 4-letter words.
  - Guesses must be validated against an embedded list of allowed five-letter words;
    reject invalid words with a shake animation and a brief toast, without using a guess.
  - Embed TWO word lists directly in the file: a curated answer list (a few hundred common
    five-letter words) and a larger allowed-guess list (the answer list is a subset of
    allowed guesses). Keep them inline as JS arrays.
  - Per-letter color feedback after each guess: GREEN = correct letter, correct spot;
    YELLOW = letter is in the word but wrong spot; GRAY = letter not in the word.
  - DUPLICATE-LETTER HANDLING MUST BE EXACT (this is the part most clones get wrong):
    color greens first, then yellows are limited by how many of that letter remain
    unmatched in the answer. Example: answer "ALLOY", guess "LLAMA" → the first L is
    yellow, the second L is green, extra As beyond the count in the answer are gray.
    Build a few unit-style sanity checks for this in code/comments and verify them.
  - DETERMINISTIC DAILY WORD: the answer is chosen by seeding from the current date (e.g.
    days since a fixed epoch indexed into the answer list) so every player gets the SAME
    word on the same calendar day. The same date always yields the same word.
  - Animations: tiles FLIP to reveal colors (staggered), invalid guesses SHAKE the row,
    and the winning row does a celebratory bounce.
  - Win when a guess is fully green; lose after six wrong guesses (then reveal the answer).
  - STATS in localStorage: games played, win %, current streak, max streak, and a guess
    distribution bar chart (1–6). Show a stats modal after the game ends.
  - SHARE button: copies the classic emoji grid (🟩🟨⬛ rows) plus the puzzle number/date
    and guess count to the clipboard — no letters leaked.

ACCEPTANCE CHECKLIST (the finish line):
  [ ] On-screen keyboard AND physical keyboard both work (type, delete, submit) and the
      keyboard keys recolor to match the best result seen for each letter.
  [ ] Duplicate-letter coloring is exact (greens first, yellows capped by remaining count);
      the "ALLOY"/"LLAMA" case colors correctly.
  [ ] Invalid / not-in-list guesses are rejected with a shake + toast and do NOT use a turn.
  [ ] The daily word is deterministic: same date → same word, every time, no network call.
  [ ] Flip, shake, and win-bounce animations all play correctly.
  [ ] Win and lose states work; losing reveals the answer.
  [ ] Stats (played, win %, streak, max streak, distribution) persist across reloads.
  [ ] Share button copies a correct emoji grid with the date/puzzle number, no letters.

STOP CONDITIONS:
Stop when EVERY checklist item passes, OR after 6 self-review rounds — whichever comes
first. Then open index.html in the browser and give me a short, plain-language how-to-play
summary (rules, controls, what the colors mean, how Share works). If you stopped on the
round cap with anything unchecked, list exactly what remains.
```

---

## Remix ideas
Add a 6-letter and 7-letter mode toggle · Add a "Wordle archive" to replay past days' words · Add a head-to-head mode where two players race the same word · Add a settings panel for theme + hard mode persisted in localStorage
