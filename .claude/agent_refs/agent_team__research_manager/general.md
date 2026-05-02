# Research playbook — task-type-agnostic

Required pre-reading for `agent_team__research_manager` on every run.

## Core principles

### 1. Angles come from the use case, not from a checklist

Each angle MUST identify a specific business or use-case question the spec author would otherwise have to guess at. "Survey of comparable tools" is not an angle; "what UX pattern do mature read-only artifact viewers converge on for the sidebar" is.

### 2. Real WebSearch + WebFetch only — never paraphrase from training data

Every factual claim in an angle file MUST trace to a fetched URL cited inline. If a researcher subagent reports it couldn't load `WebSearch` / `WebFetch`, the run halts and is escalated to the user. Fabricated citations are a critical failure.

### 3. Manager halts itself, parent spawns researchers

The `Agent` (subagent-spawn) tool is parent-only. The research manager's actual workflow: define angle list + worker prompt template, return the list to the parent, the parent spawns researcher subagents in parallel from parent scope. Each researcher writes its angle file AND its spawn audit pair under `.audit/adhoc_agents/{date}/{task_id}/spawns/researcher-{angle-id}/`.

### 4. Synthesis is the manager's job

After researchers finish, the manager (or the parent doing parent-direct synthesis) reads the angle files and produces `dossier.md` with cross-cutting insights and concrete recommendations for the spec stage. Cross-cutting insights MUST be cited to specific angle files (e.g., `*(prior-art + filesystem-risks)*`).

### 5. Every angle ends with "Open questions / not researched"

Honest gaps make the next stage's job easier. A perfect-looking angle that quietly omits what couldn't be answered hurts more than helps.

## Update protocol

Add lessons from past research runs as numbered principles. Cite the run id where the lesson surfaced.
