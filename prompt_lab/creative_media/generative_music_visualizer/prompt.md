# Generative Music + Visualizer — endless ambient, audio-reactive

**Stack:** single `index.html` (Web Audio API + canvas, no deps) · **Est:** 15–25 min · **Output:** never-repeating music with a reactive visualizer

## ✨ 1. Expectation — what you'll get
Run the prompt and a single `index.html` opens to a "Start" overlay; one click and the browser begins *composing* endless ambient music in real time — evolving chords, arpeggios, melodic notes, and reverb with no audio files anywhere — while a full-window visualizer blooms, pulses, and morphs straight off the live frequency data. Mood, tempo, volume, and a "regenerate" button let you steer the piece on the fly, and it runs for as long as you leave the tab open.

**Why it's cool:** There's no soundtrack and nothing pre-recorded — every note is synthesized note-by-note through a Web Audio lookahead scheduler and every pixel is driven by an AnalyserNode, so it genuinely never sounds or looks the same twice.

**Use cases:** A living wallpaper or stream-overlay background for a Twitch/YouTube livestream; an infinite focus/sleep ambient generator that never loops; a kinetic visual installation for a screen at an event or gallery; or a hands-on way to learn the Web Audio API (oscillators, envelopes, convolver reverb, FFT analysis) by reading one coherent file.

## ▶️ 2. How to run
Copy-paste-and-walk-away. Paste the prompt below into Claude Code in an empty folder, answer 2 short setup questions (mood + visualizer style), then it builds autonomously and opens the page. Prerequisites: none — just a modern browser; click once to start audio (browser autoplay rule).

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [Tonejs/Tone.js](https://github.com/Tonejs/Tone.js) · **Expected result:** [reference videos](https://www.youtube.com/results?search_query=web+audio+api+music+visualizer)

---

## 📋 COPY-PASTE PROMPT

```
You are building a generative-music + audio-reactive-visualizer toy as a SINGLE self-contained index.html
file using the Web Audio API and canvas. No audio files, no libraries, no build step. All sound is
synthesized; all visuals react to the live audio via an AnalyserNode.

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. Default mood? (calm-ambient / dreamy-pads / tense-cinematic)
2. Visualizer style? (radial-frequency-bloom / flowing-waveform-ribbons / particle-field)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, self-review against the checklist, fix, repeat.

Design:
- A generative engine: a scale/key, an evolving chord progression, an arpeggiator, and occasional melodic
  notes, all scheduled with Web Audio timing (lookahead scheduler). Oscillators + gain envelopes + a
  convolver/feedback-delay reverb for space. It should never sound the same twice but always musical.
- An AnalyserNode feeds the visualizer (FFT). The visuals pulse, bloom, and morph to amplitude + frequency bands.
- Controls: mood selector (calm/dreamy/tense), tempo slider, master volume, and a "regenerate" button that
  reseeds the progression. A big "Start" overlay to satisfy the browser autoplay gesture.
- Beautiful, full-window canvas. Smooth 60fps. No clipping/distortion in the audio (watch your gain staging).

ACCEPTANCE CHECKLIST (finish line):
- [ ] Opens from index.html with zero console errors; clicking Start begins audio + visuals.
- [ ] Music is clearly generative (chords/arps evolve) and musically coherent, not random noise.
- [ ] Visualizer demonstrably reacts to the audio (pulses with the music, not a fixed animation).
- [ ] Mood, tempo, volume, and regenerate controls all audibly/visibly work.
- [ ] No audio clipping/clicks; runs smoothly for minutes without degrading.

STOP CONDITIONS: stop when every item passes, OR after 6 self-review rounds.
Then open index.html and tell me (3 lines) what to click and how the controls change it.
```

---

## Remix ideas
"Add a drum/percussion layer." · "Sync the background color to the key." · "Add a record-to-WAV button." · "Add a 'rain' and 'space' preset."
