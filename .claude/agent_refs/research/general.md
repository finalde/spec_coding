# Research playbook — task-type-agnostic

Required pre-reading for stage 3 (research) on every run. The parent (Claude in the `agent_team` skill) reads this before identifying angles. See also `.claude/skills/agent_team/playbooks/research.md` for the procedural runbook.

## Core principles

### 1. Angles come from the use case, not from a checklist

Each angle MUST identify a specific business or use-case question the spec author would otherwise have to guess at. "Survey of comparable tools" is not an angle; "what UX pattern do mature read-only artifact viewers converge on for the sidebar" is.

### 2. Real WebSearch + WebFetch only — never paraphrase from training data

Every factual claim in an angle file MUST trace to a fetched URL cited inline. If a researcher worker reports it couldn't load `WebSearch` / `WebFetch`, the parent either runs the angle directly (web tools work at parent scope) or halts and escalates to the user. Fabricated citations are a critical failure.

### 3. Parent spawns researchers in parallel; no manager indirection

The `Agent` (subagent-spawn) tool is parent-only and the parent IS the manager — there is no separate manager subagent. The parent reads the revised prompt + Q&A, picks the angles itself, and spawns one researcher worker per angle in parallel (one message, multiple `Agent` tool calls). Each researcher writes its angle file AND its spawn audit pair under `.audit/adhoc_agents/{date}/{task_id}/spawns/researcher-{angle-id}/`.

### 4. Synthesis is the parent's job

After researchers finish, the parent reads the angle files and produces `dossier.md` with cross-cutting insights and concrete recommendations for the spec stage. Cross-cutting insights MUST be cited to specific angle files (e.g., `*(prior-art + filesystem-risks)*`).

### 5. Every angle ends with "Open questions / not researched"

Honest gaps make the next stage's job easier. A perfect-looking angle that quietly omits what couldn't be answered hurts more than helps.

## Update protocol

Add lessons from past research runs as numbered principles. Cite the run id where the lesson surfaced.
