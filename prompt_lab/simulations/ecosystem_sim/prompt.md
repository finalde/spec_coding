# Ecosystem Sim — predator/prey world with live population charts

**Stack:** single `index.html` (canvas + JS, no deps) · **Est:** 20–35 min · **Output:** an evolving ecosystem with real population dynamics

## ✨ 1. Expectation — what you'll get
Run the prompt and a petri-dish world fills with plants, herbivores, and predators that move, hunt, graze, breed, mutate, and starve — while a live line chart beside the canvas traces their populations into genuine Lotka–Volterra boom-and-bust waves you watch ripple in real time. Each creature carries genes for speed, sense radius, and size that pass on slightly mutated to its offspring, so over generations the average herbivore visibly gets faster or sharper-eyed as predation selects for it; let it run for minutes and you may witness a population crash, a recovery, or a real extinction.

**Why it's cool:** A whole self-balancing, *evolving* world emerges from one prompt with no scripted outcomes — just energy budgets, mutation, and natural selection — turning the abstract predator-prey equations from a textbook into something living you can actually watch adapt.

**Use cases:** A standout teaching tool for ecology, evolution, and population dynamics — let students tune mutation rate or plant growth and predict the crash. A research / intuition-building sandbox for exploring how trait distributions drift under selection pressure. A data-visualization showpiece pairing an agent world with live charts. A worked example for learning agent-based simulation, energy bookkeeping, and real-time charting by reading the code.

## ▶️ 2. How to run
Copy-paste-and-walk-away. Paste the prompt below into Claude Code in an empty folder, answer the 2 short setup questions, and it builds the whole thing autonomously, then opens the sim with its live charts. Prerequisites: none — opens in any modern browser.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [davidrmiller/biosim4](https://github.com/davidrmiller/biosim4) · **Expected result:** [reference videos](https://www.youtube.com/results?search_query=predator+prey+ecosystem+evolution+simulation)

---

## 📋 COPY-PASTE PROMPT

```
You are building an evolving predator/prey ECOSYSTEM simulation as a SINGLE self-contained index.html file
(canvas for the world + a live line chart for populations; inline JS, no libraries, no build step).

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. World style? (top-down-petri-dish / cute-meadow / abstract-cells)
2. Starting balance? (stable / boom-bust-dramatic)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, self-review against the checklist, fix, repeat.

Design:
- Three trophic levels: plants (grow/spread), herbivores (eat plants), predators (eat herbivores).
- Agents have energy: they move (costs energy), eat (gains energy), reproduce when energy is high
  (passing on slightly MUTATED genes: speed, sense radius, size, metabolism), and die at zero energy or old age.
- Simple sensing/steering: herbivores seek plants + flee predators; predators hunt herbivores.
- A live population line chart (plants/herbivores/predators over time) showing emergent cycles.
- Controls: speed slider, pause/reset, and sliders for plant growth rate + mutation rate. A stats panel
  (counts, average genes per species so you can watch evolution).
- Tune parameters so the system is interesting and doesn't trivially go extinct in seconds (but extinction
  is allowed to happen — it's a real sim).

ACCEPTANCE CHECKLIST (finish line):
- [ ] Opens from index.html with zero console errors.
- [ ] All three levels interact (predators eat herbivores eat plants); energy/reproduction/death work.
- [ ] The population chart shows real dynamics (cycles / boom-bust), not flat lines.
- [ ] Genes mutate across generations and average gene values visibly drift over time (evolution).
- [ ] Speed/growth/mutation sliders and pause/reset all work; stats panel is accurate.
- [ ] Runs smoothly for minutes without breaking.

STOP CONDITIONS: stop when every item passes, OR after 7 self-review rounds.
Then open index.html and tell me what to watch for (population cycles + evolving genes) in 3 lines.
```

---

## Remix ideas
"Add seasons that change plant growth." · "Add a disease that spreads." · "Add a second prey species competing." · "Let me click to drop food or a predator."
