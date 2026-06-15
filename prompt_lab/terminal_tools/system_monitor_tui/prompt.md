# System Monitor TUI — a beautiful live dashboard in your terminal

**Stack:** Python (textual, psutil) · **Est:** 15–25 min · **Output:** a real-time `htop`-but-prettier full-screen TUI

## ✨ 1. Expectation — what you'll get
You run `python monitor.py` and a polished full-screen dashboard takes over your terminal: per-core CPU bars, memory and swap gauges, disk usage per mount, and network up/down rates — each refreshing several times a second with scrolling history sparklines trailing behind them. A sortable, scrollable process table lists PID, name, CPU%, MEM% and user, and you flip its sort order with a keystroke while gauges shade green→amber→red under load. It's all flicker-free, mouse- and keyboard-driven, in a cohesive 16M-color theme; `q` quits cleanly and the layout reflows when you resize the window.

**Why it's cool:** It's `htop` reimagined as a *shippable product* — scrolling history graphs, threshold coloring, and a consistent visual identity — built end-to-end with Textual, proving a terminal app can look as designed as a web dashboard.

**Use cases:** Keep it as your everyday glanceable monitor for spotting a runaway process or a memory leak during a long build or training run. Read its source to learn Textual's app lifecycle — timer/worker-driven live updates, reactive widgets, sparkline rendering, and CSS-style theming. Show it off as a "terminals can be beautiful" demo in a talk or screen recording. Drop it onto a spare monitor or a server SSH session as a permanent, dependency-light ops dashboard.

## ▶️ 2. How to run
Copy-paste-and-walk-away: drop the prompt below into Claude Code in an empty folder, answer 2 short setup questions, then it builds and launches the dashboard autonomously. Prerequisite: `pip install textual psutil` (the prompt runs this). Press `q` to quit once it's running.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [Textualize/textual](https://github.com/Textualize/textual) · **Expected result:** [reference images](https://www.google.com/search?q=textual+python+system+monitor+tui&tbm=isch)

---

## 📋 COPY-PASTE PROMPT

```
You are building a real-time system-monitor TUI in Python using Textual + psutil
(run `pip install textual psutil` yourself). One command: `python monitor.py`. Full-screen, mouse + keyboard.

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. Color theme? (cyber-neon / nord / gruvbox / mono-minimal)
2. Refresh rate? (smooth ~4/sec / chill ~1/sec)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, RUN it briefly (or reason carefully about the
Textual app lifecycle), self-review against the checklist, fix, repeat. NOTE: it's an interactive app —
launch it, confirm it renders without error, then exit; don't block forever in the loop.

Design:
- Header with hostname/OS/uptime. A grid layout of panels:
  - Per-core CPU bars + a scrolling CPU history sparkline/graph.
  - Memory + swap gauges. Disk usage per mount. Network up/down rate with a rolling graph.
  - A sortable, scrollable process table (PID, name, CPU%, MEM%, user) — sort by CPU or MEM via keybinds.
- Live updates at the chosen rate via a Textual timer/worker; flicker-free, smooth.
- Color-coded thresholds (green/amber/red) on gauges. Footer with keybinds. `q` quits, `s` toggles sort.
- Cohesive styling in the chosen theme. Responsive to terminal resize.

ACCEPTANCE CHECKLIST (finish line):
- [ ] `python monitor.py` launches a full-screen TUI with no traceback and renders all panels.
- [ ] CPU/mem/disk/network values are live and update at the chosen rate.
- [ ] History graphs/sparklines scroll over time; gauges color-code by load.
- [ ] Process table populates and can be sorted by CPU and by MEM.
- [ ] `q` quits cleanly; layout reflows on terminal resize.
- [ ] Styling matches the chosen theme.

STOP CONDITIONS: stop when every item passes, OR after 6 self-review rounds.
Then launch it so I can see it, tell me the keybinds, and remind me to press q to exit.
```

---

## Remix ideas
"Add a GPU panel." · "Add per-process kill (with confirm)." · "Add a temperature/battery panel." · "Log metrics to CSV in the background."
