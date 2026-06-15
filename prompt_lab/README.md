# prompt_lab — autonomous AI build prompts for Opus 4.8

A personal library of **copy-paste prompts** that turn Claude Code (Opus 4.8) into a one-shot builder.
Every task is designed to:

- **Run locally with near-zero setup** — single HTML files that open in a browser, or Python/Node
  projects whose only deps are a `pip install` / `npm install` away.
- **Run as a "Ralph loop"** — after a tiny setup Q&A, the agent works *autonomously*: it builds,
  self-reviews against an explicit acceptance checklist, fixes what fails, and repeats until the
  checklist passes or a round cap is hit. **No babysitting after you answer the first questions.**
- **Impress** — each one is chosen to show off something Claude does shockingly well.

## How to use a task

1. Make an **empty folder** somewhere outside this repo, e.g. `mkdir ~/lab/gravity-golf && cd ~/lab/gravity-golf`.
2. Open Claude Code in that folder.
3. Open the task `.md`, copy the block under **📋 COPY-PASTE PROMPT**, paste it as your first message.
4. Answer the 2–4 setup questions. Then walk away — it loops to completion and opens/runs the result.

> Tip: if you want it to skip even the setup questions, paste the prompt and add one line at the top:
> `Use sensible defaults for all setup questions, do not ask me anything, just build.`

### Layout & one-click autonomous execution

Each task is its own folder — `prompt_lab/{category}/{task}/` with `prompt.md` (the instruction) and a
`workspace/` where a run builds. In the **spec_driven webapp's Prompt Lab section** you can hit **▶ Execute**
on any task: it spawns a headless, fully-autonomous `claude` session in that task's `workspace/`, answers
every setup question itself with sensible defaults, and **logs each decision** (`decisions.jsonl`). The run's
status, the decisions it made, live output, and generated files all show up in the UI; ⏹ Stop cancels it.

## What's a "Ralph loop"?

Named after the Simpsons' cheerfully persistent Ralph Wiggum: instead of "one prompt → one answer → stop,"
the agent treats the **file system as its memory** and **loops** — read current state, do the next
piece, verify against a finish line, repeat. The trick that makes it work is a *machine-checkable
finish line* (an acceptance checklist), so the agent iterates toward something concrete rather than
guessing when it's "done." Every prompt here bakes that loop in. ([background](https://github.com/snarktank/ralph))

## Categories

| Folder | What it shows off |
|---|---|
| [`games_interactive/`](games_interactive/) | Single-file browser games & 3D scenes — instant, shareable, zero build step |
| [`web_apps/`](web_apps/) | Polished UIs & offline apps that look professionally designed |
| [`data_and_ml/`](data_and_ml/) | Real data pipelines, dashboards, and ML written from scratch |
| [`creative_media/`](creative_media/) | Video, music, and slide decks generated entirely in code |
| [`terminal_tools/`](terminal_tools/) | Beautiful TUIs and agentic CLI tools that do real work |
| [`simulations/`](simulations/) | Emergent-behavior simulations — boids, particle life, ecosystems |
| [`generative_art/`](generative_art/) | Algorithmic art you can seed, tweak, and export |

## Recommended first runs (biggest wow, least friction)

- `generative_art/flow_field_art.md` — mesmerizing, one HTML file, ~5 min.
- `games_interactive/three_js_island.md` — fly through a 3D world you can show anyone.
- `simulations/particle_life.md` — simple rules, lifelike emergent behavior.
- `data_and_ml/csv_insight_engine.md` — point it at *any* CSV and get an analyst report.

## Conventions every task follows

- **Setup Q&A first, then silence.** The prompt asks up front, then declares autonomous mode.
- **Explicit acceptance checklist.** The loop's finish line. You can read it to know what "done" means.
- **Round cap + clean stop.** Loops at most N self-review rounds, then stops and summarizes — never spins forever.
- **No surprise dependencies.** Each task states its stack and the one install command, if any.
- **Self-opening output.** Browser tasks end with the file opened; CLI/Python tasks end with a run + summary.
- **Fixed 3-section structure.** Every task `.md` opens with the title + a one-line `Stack / Est / Output` meta, then exactly three sections in this order:
  1. **✨ Expectation — what you'll get** — after you run the prompt, what happens and the impressive result, then a **Why it's cool** line (the wow / innovation angle) and a **Use cases** line (2–4 concrete applicable uses — who'd use it and for what).
  2. **▶️ How to run** — how to actually run it (it's copy-paste-and-walk-away) plus any prerequisites.
  3. **🔗 Reference & prior art** — these prompts are original (not copied from one place); this section links a real, well-known prior-art repo / canonical implementation (`**Source:**`) to compare against and learn the technique from, plus an `**Expected result:**` link (a representative gallery / video / demo — not the exact output).
  Then the `## 📋 COPY-PASTE PROMPT` block, then `## Remix ideas`.
- **One-click copy.** In the spec_driven webapp, the copy-paste prompt block renders highlighted with a **Copy** button (and clicking the block opens it for editing); the metadata + both links surface on the Prompt Lab page.

---

*Sources / inspiration:*
[Ralph loop](https://asdlc.io/patterns/ralph-loop/) ·
[Fable 5 3D worldbuilding](https://www.explainx.ai/blog/claude-fable-5-minecraft-3d-worldbuilding-2026) ·
[creative coding](https://github.com/terkelg/awesome-creative-coding) ·
[awesome Textual](https://github.com/oleksis/awesome-textualize-projects)
