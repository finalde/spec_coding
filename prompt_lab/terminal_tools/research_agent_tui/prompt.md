# Research Agent TUI — watch an agent "think" in your terminal

**Stack:** Python (rich) · **Est:** 15–25 min · **Output:** an offline reasoning-agent CLI with a live animated UI

## ✨ 1. Expectation — what you'll get
You type one command like `python agent.py "what are the biggest files here and why"`, and the terminal lights up as a "research agent" decomposes your question into sub-tasks and works through them live: a task tree grows in real time with a spinner on whatever step is active, green checks dropping onto finished steps, and a streaming "thoughts" panel narrating each plan→act→observe→synthesize move. When the loop converges it prints a plain-English answer backed by a rich evidence table — biggest files, dominant extensions, recent changes — all computed from your actual directory. It feels like watching a frontier model reason out loud, but every number on screen is real.

**Why it's cool:** It *looks* like a costly cloud agent thinking out loud, yet it runs **100% offline with zero API keys** — the "intelligence" is a transparent, deterministic agent loop over real local tools, so the theatrics are honest rather than a black box.

**Use cases:** Keep it as a quick "what's eating my disk / what changed recently" CLI you actually run on cluttered project folders. Read its source to learn the plan→act→observe→synthesize agentic-loop pattern and how to drive a `rich` `Live` task tree with spinners and per-step state. Use it as a crisp, no-keys demo of "agentic AI" reasoning for a talk or workshop. Fork the tool registry to answer questions about a specific repo or download dump without ever sending data off your machine.

## ▶️ 2. How to run
Copy-paste-and-walk-away: drop the prompt below into Claude Code in an empty folder, answer 2 short setup questions, then it builds and demos itself autonomously on a sample question. Prerequisite: `pip install rich` (the prompt runs this). No network, no API keys.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [Textualize/rich](https://github.com/Textualize/rich) · **Expected result:** [reference images](https://www.google.com/search?q=python+rich+live+terminal+tree&tbm=isch)

---

## 📋 COPY-PASTE PROMPT

```
You are building an offline "research agent" CLI in Python that VISUALIZES its reasoning loop in the
terminal using `rich` (run `pip install rich` yourself). No network, no API keys — the "intelligence" is a
deterministic plan→act→observe→synthesize loop over real LOCAL tools. One command: `python agent.py "<question>"`.

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. What should it investigate by default? (my-home-directory / current-folder / a path I give)
2. Pace? (cinematic with deliberate step delays / fast)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, RUN it on a sample question, read the output,
self-review against the checklist, fix, repeat.

Design:
- An agent loop with clear phases: PLAN (decompose the question into sub-tasks) → ACT (run a local "tool":
  list files, sizes, counts, extensions, recent-modified, largest files, keyword grep) → OBSERVE (record
  results) → repeat until enough → SYNTHESIZE a plain-English answer.
- Live UI with rich: a Live-updating task TREE showing each sub-task, a spinner on the active step, green
  checks on completed ones, and a streaming "thoughts" panel. Color-coded by phase. A final answer panel
  with a rich Table of supporting evidence.
- Tools are REAL local operations (os/pathlib) so answers are truthful, e.g. "biggest files and why",
  "what file types dominate this folder", "what changed recently".
- Safe + read-only (never modifies files). Handles missing paths gracefully.

ACCEPTANCE CHECKLIST (finish line):
- [ ] `python agent.py "what are the biggest files here and why"` runs with no traceback.
- [ ] The terminal shows a live, animated task tree with spinners + completion states (not just static prints).
- [ ] The agent visibly PLANS, ACTs on real local tools, OBSERVES, then SYNTHESIZES.
- [ ] The final answer is truthful and backed by an evidence table from actual filesystem data.
- [ ] Works on a different question too (e.g. "what file types dominate this folder").
- [ ] Read-only; degrades gracefully on bad paths.

STOP CONDITIONS: stop when every item passes, OR after 6 self-review rounds.
Then run it once on a sample question so I can watch, and summarize what it concluded.
```

---

## Remix ideas
"Add a 'duplicate file finder' tool." · "Let it answer questions about a Git repo." · "Add a Textual full-screen version." · "Plug in a real LLM via an optional API key."
