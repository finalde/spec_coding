# Auto Pitch Deck — a real .pptx generated from a prompt

**Stack:** Python (python-pptx) · **Est:** 10–20 min · **Output:** a polished 12-slide `.pptx` you can open in PowerPoint/Keynote

## ✨ 1. Expectation — what you'll get
Run the prompt and a Python script writes `pitch.pptx` to your folder — a genuine PowerPoint file, not a web mock — a 12-slide investor deck (Title → Problem → Solution → Market → Traction → Competition → The Ask) with a consistent brand palette, shape-drawn icons, embedded native charts, and real narrative copy specific to your startup. Open it straight in PowerPoint or Keynote and every shape, chart, and text box is fully editable.

**Why it's cool:** Claude produces an actual, hand-off-ready deliverable end-to-end from one prompt — the charts are real native PowerPoint objects (not flattened images) and the copy is written for your specific company, so you get an editable deck a designer could refine, not a screenshot.

**Use cases:** A first-draft fundraising deck for a real startup you can then edit and pitch; a demo-day or sales template you re-skin per audience; a fast way to mock up board or marketing one-pagers in your brand colors; or a worked example for learning python-pptx (layouts, native charts, shape drawing) by reading and re-running the generator.

## ▶️ 2. How to run
Copy-paste-and-walk-away. Paste the prompt below into Claude Code in an empty folder, answer 2 short setup questions (the startup + brand vibe), then it builds autonomously, generates `pitch.pptx`, and tells you where it is. Prerequisites: `pip install python-pptx` — the prompt runs this for you.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [scanny/python-pptx](https://github.com/scanny/python-pptx) · **Expected result:** [reference decks](https://www.google.com/search?q=startup+pitch+deck+design&tbm=isch)

---

## 📋 COPY-PASTE PROMPT

```
You are writing a Python script that generates a polished investor pitch deck as a real .pptx file using
python-pptx (run `pip install python-pptx` yourself). Output: pitch.pptx. One command: `python deck.py`.

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. What's the startup? — give me 3 fictional options if I say "you pick" (e.g. AI logistics that cuts
   delivery emissions, a creator-payments platform, an AI tutor) and use the one I choose.
2. Brand vibe? (clean-corporate-blue / bold-startup-gradient / elegant-dark)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, RUN the script, (re)open/inspect the produced
pptx structure as best you can, self-review against the checklist, fix, repeat.

Deck design (12 slides, consistent master styling):
1 Title  2 Problem  3 Solution  4 How it works  5 Market size (with a chart)  6 Product  7 Business model
8 Traction (line/bar chart)  9 Competition (matrix)  10 Go-to-market  11 Team  12 The Ask.
- One reusable styling helper: brand palette (3–4 colors), font sizes, consistent margins/footers/slide numbers.
- Real, specific narrative copy for the chosen startup — no placeholder text.
- Icons/visuals drawn with python-pptx shapes (no external image downloads). At least 2 native charts
  (market growth, traction) with real illustrative numbers. A 2x2 or table-based competition slide.
- Cohesive look in the chosen brand vibe across every slide.

ACCEPTANCE CHECKLIST (finish line):
- [ ] `python deck.py` runs with no traceback and writes pitch.pptx.
- [ ] The file is a valid pptx (re-open it with python-pptx to confirm 12 slides + shapes/charts exist).
- [ ] Consistent master styling (palette, fonts, footers, slide numbers) across all slides.
- [ ] At least 2 working native charts with sensible numbers.
- [ ] Copy is specific to the chosen startup, coherent as a narrative, no lorem ipsum.
- [ ] Competition slide renders as a matrix/table.

STOP CONDITIONS: stop when every item passes, OR after 5 self-review rounds.
Then print the absolute path to pitch.pptx and summarize the deck's story in 3 lines.
```

---

## Remix ideas
"Add a financial-projections slide with a chart." · "Generate a matching one-pager PDF." · "Make a 5-slide demo-day version." · "Add speaker notes per slide."
