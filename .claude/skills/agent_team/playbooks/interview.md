# Interview playbook (stage 2)

This file is the procedural runbook the parent (Claude in the `agent_team` skill) reads to drive stage 2 — interview — of a spec-driven task. There is **no separate manager subagent**. The parent is the manager. The parent is also the spawner of any worker subagents this stage uses.

## Required pre-reading (BEFORE doing anything else)

Before identifying probe categories, the parent MUST read:

1. `.claude/agent_refs/interview/general.md` — task-type-agnostic interview principles. **Always required.**
2. `.claude/agent_refs/interview/{task_type}.md` — task-type-specific tips. **Required if the file exists for this task's type.**

These accumulate lessons learned across past interview runs. Per-task-type rules override this playbook's defaults when they conflict.

The parent records the absolute paths it actually read in a `pre_reading_consulted` array inside the run's `events.jsonl` event for stage start. A missing array is a critical failure — it means institutional memory wasn't loaded.

## Inputs

The skill passes in:
- `task_type` (e.g., `development`, `ai_video`)
- `task_name` (e.g., `spec_driven`)
- `task_id` (e.g., `spec_driven-20260502-140000`)
- `revised_prompt_path` — `specs/{task_type}/{task_name}/user_input/revised_prompt.md`

## Procedure

### 1. Analyze the use case

Read the revised prompt. Identify which categories need probing for THIS task. Common categories — pick only those that are load-bearing here, ignore the rest:

- **User roles & goals** — who uses this and why
- **Functional scope** — what's in / out, MVP boundaries
- **Data model** — entities, relationships, sources of truth
- **Integrations** — external systems, APIs, file formats
- **UX & interaction** — UI conventions, accessibility, primary flows
- **Non-functional** — performance, scale, security, deployment
- **Edge cases & failure modes**
- **Success criteria** — how the user knows it's done

Pick 3–6 categories. More than 6 dilutes focus; fewer than 3 usually misses something.

### 2. Generate the question pool

For each chosen category, produce **3–5 multi-choice questions** that probe a real ambiguity in that category for this specific use case. The parent has two execution shapes; pick the one that fits the task:

**Shape A — direct (default).** The parent generates the question pool itself, in one pass, after reading the revised prompt and pre-reading. Cheaper, lower latency, fewer round-trips. Use this when the categories are tight and the parent can reason about each one without extra context isolation.

**Shape B — fan-out (when categories diverge).** The parent spawns one general-purpose worker subagent per category in parallel via the `Agent` tool. Each worker reads the revised prompt + its assigned category and returns its 3–5 questions as JSON. Use this when (a) the categories require divergent reasoning that would crowd the parent's context, or (b) total questions would exceed ~15 and parallelism beats sequential synthesis.

When using shape B, capture each worker spawn under `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/spawns/interview-worker-NN-{category}/{prompt.md, output.md}`.

Each question MUST:
- Be specific to this use case (not generic).
- Have 2–4 distinct, mutually-exclusive options. The harness adds an "Other" option automatically.
- Mark the parent's recommended option with `(Recommended)` suffix when there's a clear best default. Don't make the user reverse-engineer the recommendation from option ordering.
- Probe a real ambiguity, not a settled fact.

If the parent finds itself wanting to ask a free-text question, that's a signal the category isn't crisp enough — refine the category until the question fits a 2-5 option multi-choice.

### 3. Ask the user via `AskUserQuestion`

`AskUserQuestion` is parent-only — that's why this stage is parent-direct. Constraints:
- Max **4 questions per `AskUserQuestion` call** — batch and make multiple calls if needed.
- Group questions by category when possible so the user doesn't context-switch.
- Preserve each question's options and `multiSelect` flag.

### 4. Iterate to crystal clarity

After collecting answers, re-evaluate each category:

**Shape A.** The parent re-reads the prompt + answers and decides per-category whether the aspect is now crystal clear or still has gaps.

**Shape B.** The parent re-invokes each category worker in parallel with the prompt + answers and asks "is this category clear, or are there follow-ups?". Each returns `{"clear": true}` or `{"clear": false, "follow_ups": [<more multi-choice questions>]}`.

If any category is still unclear, run another round of questions. **Cap at 3 rounds total.** If still unclear after 3, escalate to the user with a plain-text summary of what remains ambiguous and let them decide whether to push on or stop.

### 5. AUTONOMOUS mode

Under `# EXECUTION MODE: AUTONOMOUS`, the parent does NOT call `AskUserQuestion`. Instead, for each generated question, the parent pre-answers with its best-judgment default and annotates the chosen answer in `qa.md` as `*(judgment call — chose X because Y)*`. Each annotation cites the FR slice it binds into so a future interactive run can revise without re-deriving the rationale.

### 6. Write `qa.md`

Save the consolidated transcript to `specs/{task_type}/{task_name}/interview/qa.md`:

```markdown
# Interview — {task_name}

Run: {task_id}

## Categories probed
- {category 1} — {1-line why}
- {category 2} — {1-line why}
- ...

## Round 1

### {category 1}
**Q:** {question text}
- A: {selected option label} — {selected option description}
- (or "Other: {user's free-text}")
- (or "A *(judgment call — chose X because Y)*: {label}" under autonomous mode)

**Q:** ...
**A:** ...

### {category 2}
...

## Round 2 (if any)
...

## Team consensus
All categories marked clear after {N} round(s).
```

### 7. Promotion preservation

If `specs/{task_type}/{task_name}/interview/promoted.md` exists and is non-empty, every pinned Q/A item in it MUST appear verbatim in the regenerated `qa.md`. If a pin's natural insertion point no longer exists, append it to a `## Pinned items (orphaned)` section at the end of `qa.md` rather than silently dropping it. See CLAUDE.md → "Regeneration semantics → Pinned items survive regeneration".

## Tools used by the parent at this stage

- `Read` — revised prompt, pre-reading, prior `qa.md` (if resuming).
- `Write` — `qa.md`.
- `Bash` — `mkdir -p` for audit folders, ISO timestamps for events.
- `Agent` — only for shape B (per-category workers).
- `AskUserQuestion` — interactive mode only; deferred, load via `ToolSearch(query="select:AskUserQuestion", max_results=1)` if not already in scope.

## Failure modes to refuse

- **Plaintext fallback for `AskUserQuestion` is forbidden.** If the tool is unavailable, halt and tell the user — do NOT dump questions inline as plain prose hoping for free-text replies.
- **Don't fabricate sub-interviewer "outputs"** as if shape B ran when shape A actually did. The audit trail and the artifact must agree.
- **Don't pad** when the use case is already clear. 3 categories with 3 sharp questions each beats 6 categories with filler.
