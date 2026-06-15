# Kanban Board — drag-and-drop app with local persistence

**Stack:** single `index.html` (vanilla JS + localStorage) · **Est:** 15–25 min · **Output:** a real Trello-lite that remembers your data

## ✨ 1. Expectation — what you'll get
Run the prompt, pick a theme, and a single `index.html` opens as a working Trello-lite: add and rename columns, create cards with descriptions, color labels, and due dates, drag cards smoothly between and within lists, double-click to edit inline, and filter everything with a live search box. Every change writes to `localStorage` under one namespaced key, so a full refresh restores your board exactly — and JSON export/import lets you back it up or move it between machines. No backend, no account, no deploy step: it's a genuinely usable productivity tool living in one local file.

**Why it's cool:** Drag-and-drop reordering, inline editing, and persistence that survives a refresh are the hard parts of any real app — and here they all run from a single self-contained HTML file with no framework, no server, and nothing to install.

**Use cases:** Keep a private personal task board that never phones home and works on a plane; track a small project or sprint without paying for or signing into a SaaS tool; hand a client a self-contained, brandable board demo they can open by double-clicking; or study the vanilla-JS drag-and-drop and `localStorage` serialization code to learn how state-persisting frontends work under the hood.

## ▶️ 2. How to run
Copy-paste-and-walk-away. Drop the prompt below into Claude Code in an empty folder, answer the 2 short setup questions (theme, and seed-with-example-data or start-empty), and it builds autonomously, self-reviewing against a checklist until the app is done, then opens it. Prerequisites: none — it opens directly in a modern browser.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [riktar/jkanban](https://github.com/riktar/jkanban) · **Expected result:** [reference images](https://www.google.com/search?q=trello+kanban+board+ui&tbm=isch)

---

## 📋 COPY-PASTE PROMPT

```
You are building a fully-working Kanban app as a SINGLE self-contained index.html file
(vanilla JS, CSS, and localStorage for persistence; no frameworks, no backend, no build step).

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. Theme? (clean-light / dark / notion-like-minimal)
2. Seed it with example data, or start empty? (default: seed with a small example board)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, self-review against the checklist, fix, repeat.

App design:
- Columns (lists) you can add, rename, reorder, and delete.
- Cards with title, optional description, color label, and optional due date.
- Drag-and-drop cards between and within columns (HTML5 DnD or pointer events); order persists.
- Inline edit on double-click; delete with confirm. Add-card composer at the bottom of each column.
- Search/filter box that highlights/filters matching cards.
- Everything persists to localStorage under one namespaced key; reloading restores exact state.
- Export/import board as JSON (download + file picker). Keyboard: Enter to save, Esc to cancel.
- Responsive, smooth, with subtle drag animations and empty-state hints.

ACCEPTANCE CHECKLIST (finish line):
- [ ] Opens from index.html with zero console errors.
- [ ] Add/rename/delete columns and cards all work.
- [ ] Drag-and-drop reorders cards within and across columns; order is preserved on reload.
- [ ] Inline editing, labels, and due dates work and persist.
- [ ] Search filters cards live.
- [ ] JSON export downloads; JSON import restores a board.
- [ ] State survives a full page refresh (localStorage verified).

STOP CONDITIONS: stop when every item passes, OR after 6 self-review rounds.
Then open index.html and give me a 3-line tour.
```

---

## Remix ideas
"Add swimlanes." · "Add card cover images." · "Add a calendar view of due dates." · "Add multiple boards with a sidebar switcher."
