# Real-Time Webcam Body-Pose Skeleton

**Stack:** single `index.html` + TensorFlow.js + tfjs-models (CDN) · **Est:** 20–30 min · **Output:** live webcam pose detection with a skeleton overlay

## ✨ 1. Expectation — what you'll get
You open one web page, grant camera access, and your own video feed appears with a glowing skeleton drawn over you — dots on your joints, lines connecting shoulders to elbows to wrists — tracking every move in real time. A live FPS counter ticks in the corner, a slider lets you tune how confident a joint must be before it shows, and a mirror toggle flips the view. Wave your arms and the skeleton waves back, frame for frame.

**Why it's cool:** A real pose-estimation neural net (MoveNet) runs 100% locally in your browser on the webcam stream — no API keys, no server, no video ever uploaded, just on-device inference at usable frame rates.

**Use cases:** A showstopper demo of real-time on-device computer vision · privacy-preserving motion tracking where camera frames must never leave the device · a learning reference for `tfjs-models` pose-detection and canvas overlays · a starting point for fitness/rep-counting, gesture, or interactive-art prototypes.

## ▶️ 2. How to run
Copy the prompt below into Claude Code inside an empty folder and walk away. Claude asks 2–3 setup questions, then builds autonomously — implementing, self-reviewing against an acceptance checklist, and fixing itself until it passes. On first run the MoveNet model (a few MB) downloads from a CDN with a visible loading state, then runs entirely locally. The webcam (`getUserMedia`) requires a real HTTP origin, not `file://`, so serve it with a tiny static server: `python -m http.server 8080`, then open `http://localhost:8080` and allow the camera.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [tensorflow/tfjs-models](https://github.com/tensorflow/tfjs-models/tree/master/pose-detection) · **Expected result:** [pose-detection (MoveNet) demos](https://github.com/tensorflow/tfjs-models/tree/master/pose-detection)

---

## 📋 COPY-PASTE PROMPT

```
Build me a SINGLE self-contained `index.html` that does real-time webcam body-pose detection.
It loads TensorFlow.js and the `@tensorflow-models/pose-detection` package from a CDN via ES
module imports (e.g. esm.sh / jsdelivr ESM builds of `@tensorflow/tfjs` and
`@tensorflow-models/pose-detection`), uses the MoveNet detector (SinglePose Lightning for speed),
and runs entirely in the browser. There is NO backend, NO API key, and NO build step — one HTML
file, inference on-device. Model weights download once from a CDN on first run and are then
cached; after that, pose detection per frame makes zero network calls.

I will serve it locally with `python -m http.server 8080` and open http://localhost:8080,
and you must do exactly that at the very end to confirm it works.

=== PHASE 1 — SETUP (ask, then STOP) ===
Ask me these 2–3 questions, then STOP and wait for my answers. Do not write any code yet:
1. Model speed/accuracy: MoveNet Lightning (fastest) or Thunder (more accurate)? (default: Lightning)
2. Include the bonus arm-raise counter effect? (default: yes)
3. Theme: light or dark UI? (default: dark)

=== PHASE 2 — AUTONOMOUS BUILD (do NOT ask anything else) ===
After I answer, DO NOT ask any further questions. Loop until the ACCEPTANCE CHECKLIST below
fully passes. Treat the file system as your memory: each round, (a) implement or revise
`index.html`, (b) self-review it line-by-line against every checklist item, (c) fix whatever
fails, (d) repeat. Keep going autonomously — no check-ins between rounds.

Build details:
- One file: `index.html` with inline `<style>` and a `<script type="module">`.
- Import tfjs + pose-detection from a CDN as ES modules. Show a visible loading state while the
  library and MoveNet model download/initialize ("Loading model…" → "Ready"), driven by the real
  async load — never a frozen page.
- Get the webcam via `navigator.mediaDevices.getUserMedia({ video: true })`. Handle permission
  DENIAL and "no camera" gracefully: show a clear, friendly message and instructions, never a
  silent failure or uncaught exception.
- A `<video>` element (can be hidden) feeds a per-frame loop (`requestAnimationFrame`). Each frame:
  run `detector.estimatePoses(video)`, then draw onto a `<canvas>` OVERLAY that is sized and
  positioned to exactly match the video. Draw keypoints as dots and the skeleton as lines between
  the standard adjacent-keypoint pairs.
- Show a live FPS counter (smoothed) on screen.
- A confidence-THRESHOLD slider: only draw keypoints/edges whose score >= the slider value; the
  drawing updates immediately as I drag.
- A MIRROR toggle that horizontally flips both the displayed video and the overlay so it acts like
  a mirror, kept in sync.
- BONUS (if I said yes): a simple arm-raise counter — detect when both wrists go above the
  shoulders and back down, increment a visible count.
- Style it cleanly and responsively; the video+overlay should be the centerpiece.

=== ACCEPTANCE CHECKLIST (must ALL pass) ===
[ ] Model loads from a CDN with a VISIBLE loading indicator (not a frozen page).
[ ] Webcam starts via getUserMedia, and permission-denied / no-camera is handled with a friendly message.
[ ] A skeleton (keypoints + connecting edges) tracks the body in REAL TIME on a canvas overlay
    aligned to the video.
[ ] A live FPS counter is displayed.
[ ] The confidence-threshold slider works and updates which keypoints/edges are drawn immediately.
[ ] The mirror toggle flips video and overlay together, staying aligned.
[ ] It runs at a usable frame rate (smooth, not a slideshow) on a typical laptop.
[ ] Per-frame detection makes NO network requests (verify by reasoning: weights cached, inference local).

=== STOP CONDITIONS ===
Stop when EVERY checklist item passes, OR after 6 build rounds — whichever comes first. Then:
run `python -m http.server 8080`, open http://localhost:8080, allow the camera, and tell me
what to try (wave, step back so the full body shows, drag the threshold slider, flip the mirror,
raise both arms to test the counter). Remind me that the FIRST load downloads the model (slow once)
and every frame afterward is detected fully locally — no video ever leaves my machine.
```

---

## Remix ideas
Turn arm-raises into a jumping-jack / squat rep counter with audio cues · Add a multi-pose mode to track several people at once · Trigger particle effects or a trail from a chosen keypoint (hand) for interactive art · Add a simple posture alarm that warns when shoulders slump below a threshold
