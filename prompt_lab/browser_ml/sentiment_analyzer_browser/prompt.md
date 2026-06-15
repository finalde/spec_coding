# Type Text → Live Sentiment, 100% In-Browser

**Stack:** single `index.html` + Transformers.js (CDN) · **Est:** 15–20 min · **Output:** live local sentiment / zero-shot text classification

## ✨ 1. Expectation — what you'll get
You open one web page with a big text box. As you type, a positive/negative meter slides in real time — "This product is amazing" lights up green at 99% POSITIVE, "the wait was unbearable" swings red. Flip to zero-shot mode, type your own candidate labels (`urgent, billing, feedback`), paste any sentence, and watch it get scored against *your* categories on the fly. Every keystroke is judged by a transformer running inside your tab.

**Why it's cool:** Real text-classification models run 100% locally in the browser — no API keys, no server, nothing typed ever leaves your machine, yet it feels instant after the one-time model download.

**Use cases:** A privacy-preserving sentiment widget for sensitive text (support tickets, journals, HR notes) · a live demo of on-device NLP for a talk or class · a hackable reference for learning `transformers.js` text pipelines and zero-shot classification · a prototyping sandbox for routing/triage logic before you commit to a backend.

## ▶️ 2. How to run
Copy the prompt below into Claude Code inside an empty folder and walk away. Claude asks 2–3 setup questions, then builds autonomously — implementing, self-reviewing against an acceptance checklist, and fixing itself until everything passes. The first run streams a small model (a few MB–tens of MB) from a CDN with a visible loading state; after that it's cached and every classification is fully local. Because the page fetches the model over HTTP, serve it with a tiny static server rather than opening the file directly: `python -m http.server 8080`, then open `http://localhost:8080`.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [huggingface/transformers.js](https://github.com/huggingface/transformers.js) · **Expected result:** [Transformers.js docs + demos](https://huggingface.co/docs/transformers.js/index)

---

## 📋 COPY-PASTE PROMPT

```
Build me a SINGLE self-contained `index.html` that does in-browser text classification.
It loads the Transformers.js library from a CDN via an ES module import (e.g.
`import { pipeline, env } from "https://cdn.jsdelivr.net/npm/@huggingface/transformers"`)
and runs entirely in the browser. There is NO backend, NO API key, and NO build step —
one HTML file, inference on-device. Model weights download once from the Hugging Face CDN on
first run and are then cached; after that, classifying text makes zero network calls.

I will serve it locally with `python -m http.server 8080` and open http://localhost:8080,
and you must do exactly that at the very end to confirm it works.

=== PHASE 1 — SETUP (ask, then STOP) ===
Ask me these 2–3 questions, then STOP and wait for my answers. Do not write any code yet:
1. Sentiment model: default DistilBERT SST-2 (`Xenova/distilbert-base-uncased-finetuned-sst-2-english`),
   or a multilingual option? (default: DistilBERT SST-2)
2. Should I include the zero-shot custom-labels mode too? (default: yes — both modes)
3. Theme: light or dark UI? (default: dark)

=== PHASE 2 — AUTONOMOUS BUILD (do NOT ask anything else) ===
After I answer, DO NOT ask any further questions. Loop until the ACCEPTANCE CHECKLIST below
fully passes. Treat the file system as your memory: each round, (a) implement or revise
`index.html`, (b) self-review it line-by-line against every checklist item, (c) fix whatever
fails, (d) repeat. Keep going autonomously — no check-ins between rounds.

Build details:
- One file: `index.html` with inline `<style>` and a `<script type="module">`.
- Import Transformers.js from a CDN as an ES module. Configure `env` sensibly (allow remote models).
- Two modes, toggled by a tab/switch:
  * SENTIMENT mode: a `text-classification` (sentiment) pipeline. A large textarea; as I type,
    re-run classification DEBOUNCED (~300–400ms) so it updates live without thrashing. Render a
    single positive↔negative confidence bar (green→red) plus the label and percentage.
  * ZERO-SHOT mode: a `zero-shot-classification` pipeline (e.g. `Xenova/nli-deberta-v3-small` /
    `Xenova/bart-large-mnli`). Let me enter the text AND a comma-separated list of my own candidate
    labels; score the text against them and show each label with its probability bar, sorted desc.
- Lazily construct each pipeline on first use, with a `progress_callback` driving a visible
  loading/progress UI ("Downloading model… 53%" → "Ready"). The first model needed loads on start.
- While a model is loading, show a clear loading state and don't let input trigger a crash —
  queue or ignore input until the pipeline is ready, then classify the current text.
- Handle empty input gracefully (no classification, neutral UI). Style it cleanly and responsively.

=== ACCEPTANCE CHECKLIST (must ALL pass) ===
[ ] Model loads from a CDN with a VISIBLE progress/loading indicator (not a frozen page).
[ ] Sentiment updates LIVE (debounced) as I type, with no crash if I type before the model is ready.
[ ] A positive/negative confidence bar renders with the label and percentage.
[ ] Zero-shot mode accepts MY custom comma-separated labels and scores the text against them.
[ ] Zero-shot results render as sorted per-label probability bars.
[ ] Running many classifications in a row makes NO per-inference network requests
    (verify by reasoning about the code: weights are cached, inference is local).
[ ] Empty / whitespace input is handled gracefully (neutral state, no error spam).
[ ] The page is styled and usable (responsive, readable, intentional layout).

=== STOP CONDITIONS ===
Stop when EVERY checklist item passes, OR after 6 build rounds — whichever comes first. Then:
run `python -m http.server 8080`, open http://localhost:8080, and tell me what to try
(type a glowing review, then a furious one; switch to zero-shot and label a sentence as
`urgent, billing, feedback`). Remind me that the FIRST load downloads the model (slow once)
and every classification afterward is fully local and offline-capable.
```

---

## Remix ideas
Add an emotion model (joy/anger/fear/…) as a third mode with a radar chart · Highlight the most positive and most negative words inline · Batch-classify a pasted CSV of rows into a sortable table · Add a tiny on-device summarizer so long text gets a one-line TL;DR before scoring
