# Markdown Notes — installable offline PWA

**Stack:** `index.html` + `manifest.json` + `sw.js` (vanilla, no deps) · **Est:** 20–35 min · **Output:** an installable, offline-capable notes app

## ✨ 1. Expectation — what you'll get
Run the prompt, pick a theme and layout, and it builds a real Progressive Web App — then starts a tiny static server and opens it at `http://localhost:8080`. You get a live markdown editor with split preview, a sidebar of notes organized by folders or tags, full-text search, a persisted dark/light toggle, and keyboard shortcuts, with every keystroke autosaved to IndexedDB. Because it ships a service worker and manifest, you can click "Install app" to add it to your desktop or phone, then turn the network completely off and keep reading, editing, and creating notes — and export any note as `.md` or the whole library as JSON.

**Why it's cool:** This isn't a static page dressed up as an app — it's genuine app infrastructure (service worker, web manifest, IndexedDB) generated from one prompt, so it installs like a native app and stays fully functional with the network off.

**Use cases:** Carry a fast, private, offline-first notes app that lives only on your device with no cloud account; keep a portfolio piece that proves you can ship installable, offline-capable web apps; draft markdown for docs, journaling, or code snippets on flaky or no connectivity; or read the generated service-worker precache, IndexedDB autosave, and `beforeinstallprompt` code to learn exactly how PWAs are built.

## ▶️ 2. How to run
Copy-paste-and-walk-away. Drop the prompt below into Claude Code in an empty folder, answer the 2 short setup questions (theme default, editor layout), and it builds autonomously, self-reviewing against a checklist until done. Prerequisites: a PWA must be served over http (not file://), so it needs a tiny static server — the prompt sets one up with `python -m http.server 8080`, starts it, and opens the app at the end.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [mdn/pwa-examples](https://github.com/mdn/pwa-examples) · **Expected result:** [reference images](https://www.google.com/search?q=markdown+notes+pwa+app&tbm=isch)

---

## 📋 COPY-PASTE PROMPT

```
You are building an installable, offline-capable Progressive Web App for markdown note-taking.
Vanilla HTML/CSS/JS — no frameworks. Files: index.html, app.js, styles.css, manifest.json, sw.js.
A PWA must be served over http (not file://), so also provide the exact one-line command to serve it
(prefer `python -m http.server 8080`) and use that to launch it at the end.

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. Theme default? (dark / light / system)
2. Editor layout? (split editor+preview / tabbed / live-WYSIWYG-ish)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, self-review against the checklist, fix, repeat.

App design:
- Markdown editor with live preview (implement a small markdown renderer or inline a tiny one; no network deps at runtime).
- Notes stored in IndexedDB with autosave (debounced); titles derived from first heading.
- Sidebar: list of notes, folders or tags, create/delete/rename, and a full-text search box.
- Dark/light theme toggle persisted. Keyboard shortcuts (new note, search, toggle preview).
- manifest.json with name, icons (inline SVG or generated data-URI PNGs), display: standalone, theme color.
- sw.js service worker that precaches the app shell so it loads and works fully OFFLINE after first visit.
- An "Install app" affordance when the browser fires beforeinstallprompt.
- Export a note as .md and export all notes as JSON.

ACCEPTANCE CHECKLIST (finish line):
- [ ] Served over http and opens with zero console errors.
- [ ] Service worker registers; reloading with the network OFF still loads the app and existing notes.
- [ ] Lighthouse-style PWA basics present: manifest, installable, offline shell.
- [ ] Create/edit/delete notes; markdown preview renders correctly; autosave persists across reloads.
- [ ] Search filters notes; theme toggle persists.
- [ ] Export single .md and full JSON both work.

STOP CONDITIONS: stop when every item passes, OR after 7 self-review rounds.
Then start the server, open http://localhost:8080, and tell me in 3 lines how to install it + test offline.
```

---

## Remix ideas
"Add note linking with [[wikilinks]]." · "Add a graph view of links." · "Add per-note password encryption." · "Sync via exported/imported JSON files."
