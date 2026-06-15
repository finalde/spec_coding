# Drop an Image → AI Labels It, 100% In-Browser

**Stack:** single `index.html` + Transformers.js (CDN) · **Est:** 15–25 min · **Output:** drag-drop / webcam image classification running locally

## ✨ 1. Expectation — what you'll get
You open a single web page, drag a photo onto it (or pick one, or snap one from your webcam), and within a heartbeat the page shows the image preview next to a ranked list of "what is this?" guesses — *Egyptian cat 91%, tabby 6%, tiger cat 2%…* — each with an animated confidence bar. No spinner-to-nowhere, no "uploading," no account. The neural network itself is running inside your tab.

**Why it's cool:** A real image-recognition model downloads once from a CDN, then every classification after that happens entirely on-device — no API keys, no server, no data ever leaving your machine.

**Use cases:** A jaw-dropping demo of on-device AI for a talk or interview · privacy-preserving image tagging where photos must never hit a server · a hackable reference for learning how `transformers.js` pipelines work · a teaching aid for explaining what a CNN/ViT actually predicts.

## ▶️ 2. How to run
Copy the prompt below, drop it into Claude Code inside an empty folder, and walk away. Claude first asks you 2–3 quick setup questions, then builds the whole thing autonomously — implementing, self-reviewing against an acceptance checklist, and fixing itself until it passes. On the very first run the model (tens of MB) streams down from a CDN with a visible progress bar; after that it's cached and every classification is fully local. Because file-picking and the webcam want a real HTTP origin (not `file://`), serve it with a tiny static server: `python -m http.server 8080`, then open `http://localhost:8080`.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [huggingface/transformers.js](https://github.com/huggingface/transformers.js) · **Expected result:** [Transformers.js docs + demos](https://huggingface.co/docs/transformers.js/index)

---

## 📋 COPY-PASTE PROMPT

```
Build me a SINGLE self-contained `index.html` that does in-browser image classification.
It loads the Transformers.js library from a CDN via an ES module import (e.g.
`import { pipeline, env } from "https://cdn.jsdelivr.net/npm/@huggingface/transformers"`),
and runs an `image-classification` pipeline on a small model (e.g. MobileViT or a small
ResNet such as `Xenova/mobilevit-small` / `Xenova/resnet-50`) entirely in the browser.
There is NO backend, NO API key, and NO build step — everything lives in one HTML file and
inference runs on-device. The model weights download once from the Hugging Face CDN on first
run and are then cached; after that, classifications make zero network calls.

I will serve it locally with `python -m http.server 8080` and open http://localhost:8080,
and you must do exactly that at the very end to confirm it works.

=== PHASE 1 — SETUP (ask, then STOP) ===
Ask me these 2–3 questions, then STOP and wait for my answers. Do not write any code yet:
1. Model preference: smallest/fastest (MobileViT) or more accurate (ResNet-50)? (default: MobileViT)
2. Input methods: drag-and-drop + file-pick only, or also add webcam capture? (default: all three)
3. Theme: light or dark UI? (default: dark)

=== PHASE 2 — AUTONOMOUS BUILD (do NOT ask anything else) ===
After I answer, DO NOT ask any further questions. Loop until the ACCEPTANCE CHECKLIST below
fully passes. Treat the file system as your memory: each round, (a) implement or revise
`index.html`, (b) self-review it line-by-line against every checklist item, (c) fix whatever
fails, (d) repeat. Keep going autonomously — no check-ins between rounds.

Build details:
- One file: `index.html` with inline `<style>` and a `<script type="module">`.
- Import Transformers.js from a CDN as an ES module. Set a sensible `env` (allow remote models).
- Lazily construct the `image-classification` pipeline. Pass a `progress_callback` and render a
  real loading/progress UI (percent or MB downloaded), with status text like
  "Downloading model… 42%" → "Model ready".
- Input: a big drag-and-drop zone AND a file-pick button (and a webcam "capture frame" button
  if I chose webcam). Show a preview of the chosen image.
- On classify, show the TOP-5 labels, each as a row: label name + percentage + an animated
  confidence bar whose width = confidence.
- Disable / show a clear "model loading…" state on the classify controls until the pipeline is
  ready, so clicking early never throws. Handle errors (bad file, decode failure) gracefully
  with a visible message — never a silent console-only failure.
- Clean, responsive, single-column UI that looks intentional (not raw default HTML).

=== ACCEPTANCE CHECKLIST (must ALL pass) ===
[ ] Model loads from a CDN with a VISIBLE progress/loading indicator (not a frozen page).
[ ] Controls are disabled or clearly marked "loading" until the model is ready (no early-click crash).
[ ] Drag-and-drop works AND the file-pick button works (and webcam capture if selected).
[ ] The chosen image renders as a preview.
[ ] Top-5 labels render with percentages and animated confidence bars.
[ ] Running multiple classifications in a row makes NO per-inference network requests
    (verify by reasoning about the code: weights are cached, inference is local).
[ ] Bad/non-image input is handled with a visible, friendly error.
[ ] The page is styled and usable (responsive, readable, intentional layout).

=== STOP CONDITIONS ===
Stop when EVERY checklist item passes, OR after 6 build rounds — whichever comes first. Then:
run `python -m http.server 8080`, open http://localhost:8080, and tell me what to try
(drag in a photo of a pet, a car, a piece of fruit). Remind me that the FIRST load downloads
the model (so it's slow once) and every classification afterward is fully local and offline-capable.
```

---

## Remix ideas
Add a webcam "live classify every 500ms" mode with a running top-1 readout · Let me classify a whole batch of dropped images into a sortable grid · Swap in a zero-shot CLIP model so I can type my own candidate labels · Add an "explain" overlay that highlights which region drove the top prediction
