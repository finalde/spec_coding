# Deckdown — write markdown → present a slide deck

**Stack:** single `index.html` (vanilla JS, no deps) · **Est:** 15–25 min · **Output:** a markdown-to-slides presenter with speaker notes + PDF export

## ✨ 1. Expectation — what you'll get
You type markdown in the left pane and a polished slide deck builds itself live on the right. A `---` starts a new slide, `--` nests a vertical one, and your headings, bullet lists, fenced code (syntax-highlighted), and images all render the way you'd hope. Hit present mode for a full-screen deck you drive with arrow keys — progress bar at the bottom, slide counter in the corner, speaker notes tucked behind each slide, and a one-click print-to-PDF when you need to hand it out. Your markdown autosaves as you go, so a refresh never loses your talk.

**Why it's cool:** It's reveal.js-grade presenting compressed into one offline HTML file — your slides are just text you can version-control, diff, and paste anywhere.

**Use cases:** A real presentation tool for a talk or standup · Lightning-fast lecture/teaching slides from notes · A code-walkthrough deck that lives next to the repo · Quick client demos you can email as a single file.

## ▶️ 2. How to run
Open Claude Code in an empty folder, paste the prompt below, answer the 2–3 setup questions, then walk away while it builds and self-checks. The only prerequisite is a modern browser — the deliverable is one `index.html` you double-click, no install and no server. Syntax highlighting and markdown parsing are hand-rolled or inlined so it works fully offline.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [hakimel/reveal.js](https://github.com/hakimel/reveal.js) · **Expected result:** [reveal.js demo](https://revealjs.com/)

---

## 📋 COPY-PASTE PROMPT

```
Build me a single-file, dependency-free markdown-to-slides presenter. Everything must live in ONE `index.html` (inline CSS + JS). No build step, no npm, no CDN — it must open from the local file system and work fully offline in a modern browser. Vanilla JS only; write or inline a small markdown parser and a small code-highlighter rather than pulling external libraries. No network requests at all.

PHASE 1 — SETUP (ask, then STOP and wait for my answers):
1. Default theme set — which two or three themes should ship (e.g. light/"paper", dark/"midnight", high-contrast)? Default: light + dark + high-contrast.
2. Code highlighting scope — a few common languages well (JS, Python, HTML/CSS, JSON, bash) or a generic token highlighter for everything? Default: a generic token highlighter that looks good for those common languages.
3. Editor layout — split-pane editor+preview that collapses into pure present mode, or editor and presenter as two separate views you toggle? Default: split-pane that goes full-screen for present mode.
Ask these three, then STOP. Do not start building until I answer.

PHASE 2 — AUTONOMOUS BUILD:
After I answer, DO NOT ask anything else. Loop until the acceptance checklist passes. Treat the file system as your memory — write index.html, open/inspect it, write sample markdown fixtures and trace them through your splitter + renderer. Each round: implement, RUN/inspect it (open in a browser or reason carefully over the produced DOM), self-review against the checklist, fix what fails, repeat. Don't ask me to confirm between rounds.

WHAT TO BUILD:
- A two-pane layout: left = markdown editor (textarea), right = live-rendered slides.
- Slide splitting: a line containing only `---` separates horizontal slides; a line containing only `--` separates vertical (nested) slides within the current horizontal group.
- Markdown rendering: headings, bold/italic, ordered + unordered lists, links, images, blockquotes, and fenced code blocks with syntax highlighting.
- Navigation: arrow keys (← → for horizontal, ↑ ↓ for vertical) AND on-screen prev/next buttons; a slide counter (e.g. "3 / 12") and a progress bar across the bottom.
- A full-screen present mode (uses the Fullscreen API) that hides the editor.
- Speaker notes: any lines under a `Note:` marker in a slide are NOT shown on the slide but are available in a notes/presenter panel.
- Theme switcher among the chosen themes.
- Print-to-PDF: a print stylesheet so the browser's Print dialog produces one clean slide per page (no editor chrome, no UI buttons).
- localStorage autosave: the editor content is saved and restored across reloads.

ACCEPTANCE CHECKLIST (every item must pass before you stop):
[ ] `---` and `--` split slides correctly into horizontal and vertical groups.
[ ] Arrow-key navigation, on-screen buttons, counter, and progress bar all work.
[ ] Full-screen present mode hides the editor and shows only the slide.
[ ] Fenced code blocks render with visible syntax highlighting.
[ ] Speaker notes are hidden from the slide but visible in the presenter/notes panel.
[ ] localStorage autosave persists the markdown across a page reload.
[ ] Theme switching changes the deck's appearance live.
[ ] Print/PDF output is clean — one slide per page, no editor or buttons.
[ ] Opens from file:// with zero console errors and zero external requests.

STOP CONDITIONS: Stop when EVERY checklist item passes, OR after 6 build rounds — whichever comes first. Then open/inspect the final index.html, load a sample deck into it, and give me a short summary: what works, any checklist item still failing (with why), and one line on how to use it.
```

---

## Remix ideas
Add a presenter view (current slide + next slide + notes + timer on a second window) · Add slide transitions/animations toggleable per theme · Support `<!-- .slide: data-background="#000" -->` style per-slide config · Add an "export to standalone HTML" button that bakes the current deck into a shareable single file.
