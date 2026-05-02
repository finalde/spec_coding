# Research playbook (stage 3)

This file is the procedural runbook the parent (Claude in the `agent_team` skill) reads to drive stage 3 — research — of a spec-driven task. There is **no separate manager subagent**. The parent is the manager. Always focus on the **business value and use case**, not technology trivia.

## Required pre-reading (BEFORE doing anything else)

Before identifying research angles, the parent MUST read:

1. `.claude/agent_refs/research/general.md` — task-type-agnostic research principles. **Always required.**
2. `.claude/agent_refs/research/{task_type}.md` — task-type-specific tips. **Required if the file exists for this task's type.**

These accumulate lessons across past research runs. Per-task-type rules override this playbook's defaults when they conflict.

The parent records the absolute paths it actually read in a `pre_reading_consulted` array inside the run's `events.jsonl` event for stage start.

## Inputs

- `task_type`, `task_name`, `task_id`
- `revised_prompt_path` — `specs/{task_type}/{task_name}/user_input/revised_prompt.md`
- `qa_path` — `specs/{task_type}/{task_name}/interview/qa.md`

## Procedure

### 1. Identify research angles

Read the revised prompt and Q&A. Pick 3–6 angles where **missing knowledge would degrade the spec**. Examples (pick only what applies):

- **Prior art** — existing solutions in this space and how they solve it (named products, OSS projects).
- **Domain knowledge** — vocabulary, standards, mental models the user is implicitly invoking.
- **User workflow patterns** — how target users actually do this work today.
- **Integration constraints** — APIs, data formats, rate limits of named external systems.
- **Risk areas** — places where wrong technical choices are expensive (e.g., concurrency, data loss, auth).
- **Regulatory / compliance** — only if the spec touches regulated data.
- **UX conventions** — only if the spec involves UI.

Don't research for research's sake. If the use case is well understood, fewer angles is fine.

Each angle MUST have a one-line goal that names a specific business or use-case question the spec author would otherwise have to guess at. "Survey of comparable tools" is not an angle; "what UX pattern do mature read-only artifact viewers converge on for the sidebar" is.

### 2. Spawn researcher workers in parallel

The parent spawns ONE general-purpose worker subagent per angle, **all in parallel** in a single message with multiple `Agent` tool calls. Each researcher:
- Has access to `WebSearch`, `WebFetch`, `Read`, `Write`, `Bash` (for mkdir).
- Receives the revised prompt, the Q&A, and its assigned angle + 1-line goal.
- Writes findings to `specs/{task_type}/{task_name}/findings/angle-{slug}.md`.
- Returns a 3-bullet executive summary in its final message.

Capture each worker spawn under `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/spawns/researcher-NN-{slug}/{prompt.md, output.md}`.

#### Worker prompt template

```
You are a researcher for the "{angle}" angle of a spec-driven task.

Step 0 — load deferred tools (REQUIRED, do this before any web call):
  ToolSearch(query="select:WebSearch,WebFetch", max_results=2)
If either schema fails to load, return {"angle": "{slug}", "status": "deferred_tool_unavailable", "missing": [...], "partial_findings_from_repo_only": "<anything from local files>"} and STOP. Do not paraphrase training data as if researched. Do not pad.

Revised user prompt:
{paste}

Interview Q&A:
{paste}

Your angle: {angle}
What this angle should answer: {1-line goal}

Constraints:
- Focus on the BUSINESS and USE CASE — not language/library/framework choices unless the spec explicitly hinges on them.
- Cite sources (URLs) for non-obvious facts (must come from real WebSearch/WebFetch results, never invented).
- Distinguish established practice from your opinion.
- 600–1200 words; bullets and tables are fine.
- If you can't find anything substantive, say so explicitly — don't pad.

Write findings to specs/{task_type}/{task_name}/findings/angle-{slug}.md with sections:
1. What this angle covers
2. Key findings (bulleted, with citations)
3. Implications for the spec (concrete, actionable)
4. Open questions surfaced

Return a 3-bullet executive summary.
```

#### Halting on deferred-tool failure

If any worker returns `status: "deferred_tool_unavailable"`, the parent does NOT proceed to dossier consolidation as if the angle were covered. Two recovery paths:
1. **Run the missing web calls from the parent** (web tools are known to work at parent scope) and write `angle-{slug}.md` directly. Cheapest path.
2. **Halt and escalate** to the user with `{"status": "halted", "reason": "deferred_tool_unavailable", "missing": [...]}` if the parent can't recover the angle either. Plaintext-fallback / fabricated-citation behavior is forbidden.

Empty is better than invented.

### 3. Consolidate into a dossier

After all workers finish, the parent reads every `angle-*.md` and writes `specs/{task_type}/{task_name}/findings/dossier.md`:

```markdown
# Findings dossier — {task_name}

Run: {task_id}

## Angles researched
1. {angle slug} — {1-line goal}
2. ...

## Cross-cutting insights
- {insight that emerged from combining angles} *(angle-a + angle-b)*
- ...

## Per-angle highlights
### {angle 1 slug}
- {highlight 1}
- {highlight 2}
- {highlight 3}

### {angle 2 slug}
...

## Recommendations for the spec
- {concrete recommendation}
- ...

## Open questions surviving research
- {question}, asked from angle {slug}
- ...
```

Cross-cutting insights MUST cite the specific angle files that combined to surface them (e.g., `*(prior-art + filesystem-risks)*`).

### 4. Promotion preservation

If `specs/{task_type}/{task_name}/findings/promoted.md` exists and is non-empty, every pinned recommendation/insight/highlight in it MUST appear verbatim in the regenerated `dossier.md`. If a pin's natural insertion point no longer exists, append it to a `## Pinned items (orphaned)` section at the end of `dossier.md`. See CLAUDE.md → "Regeneration semantics → Pinned items survive regeneration".

## Tools used by the parent at this stage

- `Read` — revised prompt, qa.md, pre-reading, worker outputs.
- `Write` — dossier.md (and angle files in the recovery path).
- `Bash` — mkdir, timestamps.
- `Agent` — researcher workers in parallel.
- `WebSearch` / `WebFetch` — only if the parent runs an angle directly (recovery path); load via `ToolSearch(query="select:WebSearch,WebFetch", max_results=2)` first.

## Failure modes to refuse

- **No paraphrasing from training data as if it were researched.** Every factual claim traces to a fetched URL.
- **No fabricated worker outputs.** If the parent runs an angle directly (recovery path), the audit folder records that — don't pretend a worker did it.
- **No padding.** Honest "open questions / not researched" sections beat thin angle files.
