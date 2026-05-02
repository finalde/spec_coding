# Interview playbook — task-type-agnostic

Required pre-reading for `agent_team__interview_manager` on every run.

## Core principles

### 1. Probe categories come from the use case, not from a template

The manager's first job is to read the revised prompt and identify which categories actually matter for *this* task. A canned 7-category template (functional / discovery / ux / deployment / success / security / …) is a starting point, not a destination. Adding or merging categories per task is normal; padding with categories that don't apply is wasteful.

### 2. Multi-choice questions only

Free-text is the implicit "Other" option, not a default. If the manager finds itself wanting to ask a free-text question, that's a signal the probe category isn't crisp enough — refine the category until the question fits a 2-5 option multi-choice.

### 3. Recommended option flagged explicitly

Every multi-choice question MUST surface the manager's recommended answer with `(Recommended)` after the option text. The user shouldn't have to reverse-engineer the manager's opinion from the option ordering.

### 4. Round 1 is mostly clear; rounds 2-3 close the open threads

Cap interview iterations at 3 rounds total. If a category is still unclear after round 3, that's a signal to escalate to the user, not to keep probing.

### 5. AUTONOMOUS mode: judgment call + inline annotation

Under `# EXECUTION MODE: AUTONOMOUS`, the manager pre-answers each probe with a best-judgment default annotated as `*(judgment call — chose X because Y)*`. Each annotation cites the FR slice it binds into so a future interactive run can revise without re-deriving the rationale.

## Update protocol

Add lessons learned from past interview runs as numbered principles. Cite the run id where the lesson surfaced.
