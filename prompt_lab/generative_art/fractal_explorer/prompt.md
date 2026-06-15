# Fractal Explorer — infinite-zoom Mandelbrot/Julia, GPU-fast

**Stack:** single `index.html` (WebGL shader, no deps) · **Est:** 15–25 min · **Output:** a smooth, deep-zoomable fractal explorer

## ✨ 1. Expectation — what you'll get
Run the prompt and you get a real-time fractal explorer rendered on the GPU through a WebGL fragment shader: drag to pan, scroll to plunge deep into the Mandelbrot set, toggle to animated Julia sets that morph under your mouse, cycle colors on the fly, and screenshot any frame. Iterations auto-scale as you zoom, so filigree detail keeps unfolding sharply instead of dissolving into mush — you can fall toward infinity and the boundary stays crisp. Every view is a coordinate you can return to and export as a print-ready image.

**Why it's cool:** The whole image is computed per-pixel, in parallel, by a shader Claude writes by hand — and the infinite, self-similar detail isn't drawn anywhere, it's generated on the fly from one tiny escape-time formula. Watching a hand-written shader hold razor detail while you free-fall into the set is hypnotic.

**Use cases:** Capture screenshots of striking deep-zoom coordinates as abstract wallpapers, posters, and large-format prints; record a cinematic zoom for a music-video or social loop; build a curated series of named "locations" in the set as an art project; or read the shader code to genuinely learn WebGL fragment shaders, smooth/continuous coloring, and zoom-toward-cursor math.

## ▶️ 2. How to run
Copy-paste-and-walk-away: paste the prompt below into Claude Code in an empty folder, answer 2 short setup questions (default fractal + color scheme), then it builds and opens autonomously. Scroll to zoom, drag to pan, S to save a screenshot. Prerequisites: none — opens in any modern browser with WebGL.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [Shadertoy (live WebGL fractals)](https://www.shadertoy.com/) · **Expected result:** [reference images](https://www.google.com/search?q=mandelbrot+julia+fractal+zoom&tbm=isch)

---

## 📋 COPY-PASTE PROMPT

```
You are building a real-time fractal explorer as a SINGLE self-contained index.html file using a WebGL
fragment shader (no libraries, no build step). The fractal is computed in the shader for smooth deep zoom.

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. Default fractal? (mandelbrot / julia / let-me-toggle-both)
2. Color scheme? (fire / electric-blue / psychedelic-cycling / grayscale-elegant)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, self-review against the checklist, fix, repeat.

Design:
- WebGL setup: fullscreen quad + a fragment shader implementing the escape-time iteration with smooth
  (continuous) coloring. Uniforms for center, zoom, max-iterations, color params, and Julia constant.
- Interaction: drag to pan, scroll wheel to zoom toward the cursor (deep zoom), and auto-increase
  iterations as you zoom so detail holds. Keyboard to reset view.
- Mode toggle Mandelbrot <-> Julia; in Julia mode let the mouse position (or an animation) drive the
  Julia constant for live morphing. Color-scheme selector + a smooth color-cycling toggle.
- An FPS/zoom-depth readout and S = save a PNG screenshot. Handle context-lost gracefully.
- Looks crisp and vivid; no aliasing-soup at depth (raise iterations with zoom).

ACCEPTANCE CHECKLIST (finish line):
- [ ] Opens from index.html with zero console errors; the fractal renders immediately via WebGL.
- [ ] Drag-pan and scroll-zoom-toward-cursor work smoothly and zoom deep without falling apart.
- [ ] Iterations auto-scale with zoom so detail stays sharp.
- [ ] Mandelbrot/Julia toggle works; Julia morphs with the mouse (or animates).
- [ ] Color scheme selector + smooth coloring look great; S saves a PNG.
- [ ] Maintains good FPS while zooming.

STOP CONDITIONS: stop when every item passes, OR after 6 self-review rounds.
Then open index.html and tell me the controls (zoom/pan/toggle/save) in 3 lines.
```

---

## Remix ideas
"Add a bookmark list of cool coordinates." · "Add a cinematic auto-zoom recording mode." · "Add the Burning Ship fractal." · "Add double-precision emulation for deeper zoom."
