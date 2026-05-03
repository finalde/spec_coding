# Interview refs — task-type-agnostic

Institutional memory for stage 2. The pre-reading contract, parent-direct model, and audit paths are in `CLAUDE.md` (§ Stage playbooks and reference docs) — this file is just the principles. Per-task-type files in this same folder override these defaults when they conflict.

## Principles

### 1. Probe categories come from the use case, not from a template

Read the revised prompt and identify which categories actually matter for *this* task. A canned 7-category template is a starting point, not a destination. Adding/merging per task is normal; padding with categories that don't apply is wasteful.

### 2. Multi-choice questions only

Free-text is the implicit "Other" option, not a default. Wanting a free-text question = the category isn't crisp enough. Refine until it fits 2–5 multi-choice options.

### 3. Recommended option flagged explicitly

Every question MUST surface the recommended answer with `(Recommended)` after the option text. Don't make the user reverse-engineer the recommendation from option ordering.

### 4. Round 1 mostly clear; rounds 2–3 close open threads

Cap at 3 rounds total. Still unclear after 3 → escalate to the user, don't keep probing.

### 5. AUTONOMOUS mode: judgment call + inline annotation

Pre-answer with best judgment, annotated `*(judgment call — chose X because Y)*`. Each annotation cites the FR slice it binds into so an interactive run can revise without re-deriving.

## Update protocol

Surgical: one new principle per lesson. Cite the run id where the lesson surfaced.
