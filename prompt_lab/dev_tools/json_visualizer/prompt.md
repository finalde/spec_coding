# JSON Crackpot — paste JSON → interactive node graph

**Stack:** single `index.html` (canvas/SVG + JS, no deps) · **Est:** 20–30 min · **Output:** paste JSON/YAML → an interactive, pannable node graph

## ✨ 1. Expectation — what you'll get
You drop a wall of nested JSON (or YAML) into a textarea, hit render, and it explodes into a clean node-link diagram — every object and array becomes a card, every key-value relationship becomes an edge you can trace with your eye. You pan across the canvas, zoom into a deeply buried config, drag nodes apart to untangle them, and type in a search box to spotlight the exact keys you're hunting for. Broken JSON doesn't blow up — it tells you, politely, what's wrong and where.

**Why it's cool:** It turns the ritual of squinting at indentation into a spatial, explorable map you actually *navigate* — and it's all one HTML file with zero dependencies you can open from anywhere.

**Use cases:** Debugging a gnarly API response or Kubernetes manifest · Onboarding teammates to an unfamiliar config schema · A teaching prop for explaining tree/graph structures · A quick offline alternative to pasting sensitive payloads into a web service.

## ▶️ 2. How to run
Open Claude Code in an empty folder, paste the prompt below, and answer the 2–3 setup questions — then walk away while it builds and self-checks. The only prerequisite is a modern browser: the deliverable is a single `index.html` you double-click to open, no install, no server, no internet. It works fully offline.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [AykutSarac/jsoncrack.com](https://github.com/AykutSarac/jsoncrack.com) · **Expected result:** [JSON Crack live](https://jsoncrack.com/)

---

## 📋 COPY-PASTE PROMPT

```
Build me a single-file, dependency-free JSON/YAML visualizer that turns pasted data into an interactive, pannable node-link graph. Everything must live in ONE `index.html` (inline CSS + JS, SVG or Canvas for rendering). No build step, no npm, no CDN — it must open from the local file system and work fully offline in a modern browser. Vanilla JS only; you may hand-roll a tiny YAML parser or a minimal inlined one, but no external network requests.

PHASE 1 — SETUP (ask, then STOP and wait for my answers):
1. Render engine — SVG (crisp, easy hit-testing, great for <~2k nodes) or Canvas (faster for huge docs)? Default: SVG.
2. Default layout direction — left-to-right tree or top-down tree? Default: left-to-right.
3. Should I include a YAML input mode in addition to JSON? Default: yes (JSON + YAML).
Ask these three, then STOP. Do not start building until I answer.

PHASE 2 — AUTONOMOUS BUILD:
After I answer, DO NOT ask anything else. Loop until the acceptance checklist passes. Treat the file system as your memory — write index.html, open/inspect it, keep a short notes file if useful. Each round: implement, RUN/inspect it (open in a browser or reason carefully over the DOM/render output, generate test JSON fixtures and trace them through your parser+layout code), self-review against the checklist, fix what fails, repeat. Don't ask me to confirm between rounds.

WHAT TO BUILD:
- A textarea for input (JSON, and YAML if chosen), with a "Render" button and live-ish re-render.
- Parse the input and render a collapsible node-link graph: objects and arrays become nodes; primitive leaves render inside their parent node or as small leaf nodes; edges connect parents to children. Show keys and primitive values readably; truncate very long strings with a tooltip/expand.
- Collapsible nodes: click a node to collapse/expand its subtree.
- Pan (drag background), zoom (wheel / +- buttons / pinch), and drag individual nodes to reposition them.
- A search/filter box that highlights nodes whose key or value matches, and dims the rest; ideally pans to the first match.
- Pretty error messages on invalid input: show line/column or a clear human description, never a blank screen or a thrown-uncaught crash.
- A "Load sample" button with a rich nested fixture (mixed objects, arrays, nested arrays, numbers, strings, booleans, null).
- A clean LIGHT theme: readable fonts, soft node cards, subtle edges, good contrast.

ACCEPTANCE CHECKLIST (every item must pass before you stop):
[ ] Renders deeply nested objects AND nested arrays correctly as a connected graph.
[ ] Invalid JSON/YAML shows a clear, specific error message and the app stays usable (no crash, no blank screen).
[ ] Pan, zoom, and per-node drag all work smoothly with mouse.
[ ] Collapsing a node hides its subtree; expanding restores it.
[ ] Search highlights matching nodes and visibly dims non-matches.
[ ] "Load sample" populates a rich nested fixture that renders correctly.
[ ] Light theme is clean and legible; layout has no overlapping unreadable nodes for the sample.
[ ] Opens from file:// with zero console errors and zero external requests.

STOP CONDITIONS: Stop when EVERY checklist item passes, OR after 6 build rounds — whichever comes first. Then open/inspect the final index.html, and give me a short summary: what works, any checklist item still failing (with why), and one line on how to use it.
```

---

## Remix ideas
Add a "diff two JSON blobs" mode that colors added/removed/changed nodes · Export the current graph as PNG/SVG · Add JSONPath query support that selects + zooms to matching nodes · Add a minimap for navigating huge documents.
