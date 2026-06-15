# Smart File Organizer — an agent that tidies a messy folder, safely

**Stack:** Python (stdlib + rich) · **Est:** 15–25 min · **Output:** a dry-run-first CLI that sorts any folder by content/type/date

## ✨ 1. Expectation — what you'll get
You point the tool at a messy folder and `python organize.py <folder>` inspects every file — classifying by type, reading size and modified date, and flagging duplicates by hash — then prints a **dry-run plan** as a rich from→to tree with a summary of counts per category, duplicates found, and space involved, all without moving a single byte. Only when you add `--apply` does it actually reorganize, doing so transactionally and writing an `undo.py` that reverses every move; re-running afterward reports "nothing to do." It refuses dangerous roots like your home or a drive root unless you pass `--force`, so the safe path is always the default path.

**Why it's cool:** It's a genuinely *safe* automation rather than a reckless toy — dry-run-first, transactional, idempotent, and reversible — showing how an agent can be trusted with your filesystem because it always shows the plan and hands you the undo button.

**Use cases:** Run it for real on a chaotic Downloads or Desktop folder, eyeball the dry-run, then `--apply` and keep the `undo.py` as your safety net. Read its source to learn safe-automation patterns: dry-run/apply separation, hash-based dedup, collision handling, and generating a reversible undo script. Use it as a teaching example of building tools users can trust around destructive operations. Adapt the scheme rules to auto-file screenshots, invoices, or media exports as a recurring tidy-up chore.

## ▶️ 2. How to run
Copy-paste-and-walk-away: drop the prompt below into Claude Code in an empty folder, answer 2 short setup questions, then it builds and demos autonomously on a generated messy sandbox folder (so nothing real is touched). Prerequisite: `pip install rich` (the prompt runs this); the stdlib does the rest.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [tfeldmann/organize](https://github.com/tfeldmann/organize) · **Expected result:** [reference images](https://www.google.com/search?q=cli+file+organizer+dry+run&tbm=isch)

---

## 📋 COPY-PASTE PROMPT

```
You are building a SAFE "smart file organizer" CLI in Python (stdlib + `rich` only; run `pip install rich`).
Command: `python organize.py <folder> [--apply]`. DRY-RUN BY DEFAULT — it never moves anything unless --apply.

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. Organizing scheme? (by-type / by-type-then-date / by-project-guess) — default by-type-then-date
2. For the demo, generate a messy sandbox folder to organize? (yes — recommended, so nothing real is touched)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, RUN it on the sandbox (dry-run, then --apply),
verify results, self-review against the checklist, fix, repeat.

Design:
- Scan the target folder; classify each file by extension/type (images, docs, code, archives, media, etc.),
  read basic metadata (size, modified date), and detect obvious duplicates by hash.
- Build a reorganization PLAN per the chosen scheme (e.g. Images/2024-06/, Docs/, Code/). Handle name
  collisions, skip system/hidden files, and never recurse into its own destination dirs.
- DRY-RUN by default: print a rich tree/table of "from → to" moves + a summary (counts per category,
  duplicates found, space). Make NO changes without --apply.
- With --apply: perform moves transactionally and WRITE an `undo.py` (or undo.sh) that reverses every move.
- Refuse to run on obviously dangerous roots (home root, drive root) without an explicit --force.
- If sandbox generation was chosen, create a realistic messy folder first (mixed types, some dup files, dates).

ACCEPTANCE CHECKLIST (finish line):
- [ ] `python organize.py <sandbox>` runs dry-run with no traceback and changes NOTHING.
- [ ] The plan is shown as a clear from→to tree/table with a summary (categories, duplicates, sizes).
- [ ] `--apply` actually reorganizes the sandbox per the plan and handles name collisions.
- [ ] A working undo script is generated and, when run, restores the original layout (verify it).
- [ ] Duplicates detected by hash; hidden/system files skipped; dangerous roots refused without --force.
- [ ] Re-running dry-run on the organized folder reports "nothing to do" (idempotent).

STOP CONDITIONS: stop when every item passes, OR after 6 self-review rounds.
Then run the dry-run on the sandbox so I can see the plan, and tell me the exact --apply + undo commands.
```

---

## Remix ideas
"Add content-based classification (read text/EXIF), not just extensions." · "Add a watch mode." · "Add a config file for custom rules." · "Add a Textual UI to approve moves individually."
