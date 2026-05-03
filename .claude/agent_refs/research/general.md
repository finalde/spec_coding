# Research refs — task-type-agnostic

Institutional memory for stage 3. The pre-reading contract, parent-direct model, and audit paths are in `CLAUDE.md` (§ Stage playbooks and reference docs) — this file is just the principles. Per-task-type files in this same folder override these defaults when they conflict.

## Principles

### 1. Angles come from the use case, not a checklist

Each angle must name a specific business / use-case question the spec author would otherwise have to guess at. *"Survey of comparable tools"* is not an angle; *"what UX pattern do mature read-only artifact viewers converge on for the sidebar"* is.

### 2. Real `WebSearch` + `WebFetch` only — never paraphrase from training data

Every factual claim in an angle file MUST trace to a fetched URL cited inline. If a worker reports it couldn't load `WebSearch` / `WebFetch`, the parent either runs the angle directly (web tools work at parent scope) or halts and escalates. Fabricated citations are a critical failure.

### 3. Synthesis is the parent's job

After workers finish, the parent reads angle files and produces `dossier.md` with cross-cutting insights and concrete spec recommendations. Cross-cutting insights MUST cite the specific angle files that combined to surface them (e.g., `*(prior-art + filesystem-risks)*`).

### 4. Every angle ends with "Open questions / not researched"

Honest gaps make the next stage's job easier. A perfect-looking angle that quietly omits what couldn't be answered hurts more than helps.

## Update protocol

Surgical: one new principle per lesson. Cite the run id where the lesson surfaced.
