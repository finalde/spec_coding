# Regex Lab — live regex tester + explainer

**Stack:** single `index.html` (vanilla JS, no deps) · **Est:** 15–25 min · **Output:** a live regex tester with match highlighting + a cheat sheet

## ✨ 1. Expectation — what you'll get
You type a pattern up top, toggle flags like `g` `i` `m` `s`, and watch every match light up in your test text in real time — capture groups colored distinctly so you can see exactly what each `( )` caught. A match list breaks down the index and groups for every hit, a replace mode previews your `$1`-style substitution as you edit, and a built-in pattern library lets you drop in a battle-tested email/URL/IPv4/date regex with one click. A collapsible cheat sheet keeps every token a glance away, and a malformed pattern shows a friendly error instead of a blank screen.

**Why it's cool:** It's a RegExr-style live lab — instant feedback, colored groups, and a learn-as-you-go cheat sheet — packed into one offline HTML file you control.

**Use cases:** Crafting and debugging a tricky regex before pasting it into code · Learning regex with immediate visual feedback · Teaching pattern syntax with live examples · A quick offline tester when you can't paste data into an online tool.

## ▶️ 2. How to run
Open Claude Code in an empty folder, paste the prompt below, answer the 2–3 setup questions, then walk away while it builds and self-checks. The only prerequisite is a modern browser — the deliverable is one `index.html` you double-click, no install and no server. It uses the browser's native RegExp engine, so it works fully offline.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [ziishaned/learn-regex](https://github.com/ziishaned/learn-regex) · **Expected result:** [RegExr](https://regexr.com/)

---

## 📋 COPY-PASTE PROMPT

```
Build me a single-file, dependency-free regex playground. Everything must live in ONE `index.html` (inline CSS + JS) using the browser's native RegExp engine. No build step, no npm, no CDN — it must open from the local file system and work fully offline. Vanilla JS only, no external requests.

PHASE 1 — SETUP (ask, then STOP and wait for my answers):
1. Theme — light, dark, or a switch between both? Default: switchable, defaulting to light.
2. Pattern library scope — which common patterns to ship as one-click inserts (e.g. email, URL, IPv4, ISO date, hex color, phone, slug)? Default: email, URL, IPv4, ISO date, hex color, phone, slug.
3. Should the cheat sheet be a compact always-visible sidebar or a collapsible panel? Default: collapsible panel.
Ask these three, then STOP. Do not start building until I answer.

PHASE 2 — AUTONOMOUS BUILD:
After I answer, DO NOT ask anything else. Loop until the acceptance checklist passes. Treat the file system as your memory — write index.html, open/inspect it, and run sample patterns + test text through the logic to verify matching, grouping, and replace behavior. Each round: implement, RUN/inspect it (open in a browser or reason carefully over the produced DOM and the RegExp results), self-review against the checklist, fix what fails, repeat. Don't ask me to confirm between rounds.

WHAT TO BUILD:
- A regex input field plus flag toggles for g, i, m, s, u, y (checkboxes or pills); the active flags drive the RegExp.
- A test-text area. As I type in either the pattern or the text, LIVE-highlight every match in the text. Color capture groups distinctly (group 1, group 2, … each a different color), with the whole match underlaid.
- A match list panel: for each match, show its start index, the full matched string, and each capture group's value (named groups too if present).
- A replace mode: a replacement input supporting `$1`, `$2`, `$<name>` substitutions, with a LIVE preview of the replaced output (using String.replace with the compiled regex).
- A collapsible cheat sheet of common tokens (anchors `^ $`, classes `\d \w \s`, quantifiers `* + ? {n,m}`, groups, lookarounds, escapes) with one-line explanations.
- A pattern library: one-click buttons that insert a tested, working regex for each chosen common pattern (email, URL, IPv4, etc.) into the pattern field.
- Graceful invalid-regex handling: catch the SyntaxError from `new RegExp`, show a clear inline error message, and keep the UI alive (no crash, no infinite loop). Guard against zero-width-match infinite loops when iterating global matches.

ACCEPTANCE CHECKLIST (every item must pass before you stop):
[ ] Highlighting updates live as I type in EITHER the pattern or the test text.
[ ] Capture groups are shown in the match list AND visually distinguished by color in the text.
[ ] Toggling flags (g/i/m/s/u/y) demonstrably changes matching behavior.
[ ] Replace mode previews `$1`-style substitutions correctly and live.
[ ] An invalid regex shows a clear error message and the app stays usable (no crash, no hang).
[ ] Global matching with a zero-width pattern (e.g. an empty alternation) does NOT infinite-loop.
[ ] The cheat sheet is present and the pattern library inserts working patterns with one click.
[ ] Opens from file:// with zero console errors and zero external requests.

STOP CONDITIONS: Stop when EVERY checklist item passes, OR after 6 build rounds — whichever comes first. Then open/inspect the final index.html, exercise a couple of patterns and a replace, and give me a short summary: what works, any checklist item still failing (with why), and one line on how to use it.
```

---

## Remix ideas
Add a plain-English explainer that describes what the current regex does, token by token · Add a "share" button that encodes pattern+flags+text into the URL hash · Add a unit-test panel: list strings that should match / shouldn't, and show pass/fail · Add a generated railroad/syntax diagram of the pattern.
