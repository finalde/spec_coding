---
name: agent_team
description: Launch the autonomous agent team for any task. Runs interview → research → execution → validation with automatic feedback loops and self-evolution. Invoke with /agent_team followed by your task description.
---

# Agent Team — Orchestrator Skill

You are now the **Agent Team Orchestrator**. You directly spawn and coordinate all agents. Read `.claude/agents/agent_team__orchestrator.md` for full instructions.

**CRITICAL CONSTRAINT**: Claude Code subagents cannot spawn other subagents. YOU spawn ALL agents directly. The agent template files (`.claude/agents/agent_team__*.md`) are reference templates — they define roles, not spawning agents.

## Quick Start

1. Parse the task from `$ARGUMENTS`
2. Derive `{task_name}` (snake_case, short)
3. Create two directories:
   - **User-facing deliverable:** `reports/{YYYY-MM-DD}/{task_name}/` — top-level repo folder, **git-tracked**. This is what the user consumes (playbooks, recommendations, code, decks).
   - **Internal pipeline data:** `.audit/adhoc_agents/{YYYY-MM-DD}/{task_name}/` — interview/, research/, validation/, findings_report.md. `.audit/` is gitignored.
4. Read `.claude/agents/agent_team__orchestrator.md` for detailed workflow
5. Execute the pipeline: Interview → Research → Execution → Validation → Feedback Loop → Self-Evolution

## Output location convention — MANDATORY

| Artifact | Location |
|---|---|
| Primary user deliverable (playbook, recommendations, idea deck, code project) | `reports/{date}/{task_name}/` |
| interview/requirements.md + perspective files | `.audit/adhoc_agents/{date}/{task_name}/interview/` |
| research/dossier.md + angle files | `.audit/adhoc_agents/{date}/{task_name}/research/` |
| validation/report.md | `.audit/adhoc_agents/{date}/{task_name}/validation/` |
| findings_report.md | `.audit/adhoc_agents/{date}/{task_name}/` |
| Self-evolution log | `.audit/self_evolving/{date}_{task_name}.md` |
| Prompt history entry | `.audit/prompt_history/{date}.md` |

Rationale: users want one clean folder (`reports/`) that contains ONLY the finished artifact they can copy/forward. Process exhaust (interviews, research dossiers, validation noise, self-evolution) belongs separately so it doesn't clutter the handoff.

## Content-quality bar — MANDATORY

Every primary deliverable under `reports/` must be:

1. **100% explicit** — every step specifies the exact URL, exact settings, exact text to paste. No "pick whatever works." No "depending on your setup." If a value varies, state the decision criterion inline ("if X, use Y; else use Z").
2. **Copy-paste ready** — code blocks, prompts, templates all work verbatim. Placeholders use `{angle-brackets}` or are explicitly labeled as such.
3. **MVP-first** — lead with the minimum viable path. Nice-to-haves go to an appendix or a "Fallback shortcuts" section. If the user says "build the first MVP asap," cut everything not on the critical path to shipping.
4. **Time-budgeted** — every major step has a wall-time estimate. Sequence has a cumulative total so the user knows when they'll finish.

## Pipeline Summary

```
PHASE 1: INTERVIEW
  → Classify task (small: 10+ questions, large: 30+)
  → Spawn 3-5 interview agents in parallel (each covers 2-3 perspectives)
  → Collect questions, deduplicate, present to user in CHOICE-BASED format
  → Write: interview/requirements.md

PHASE 2: RESEARCH
  → Read requirements
  → Spawn 3-8 research agents in parallel (one per angle)
  → Collect findings, consolidate
  → Write: research/dossier.md + research/{angle}.md

PHASE 3: EXECUTION
  → Read requirements + dossier
  → Write execution plan
  → For copy-paste operational docs (playbook, SOP, script): ORCHESTRATOR writes directly — subagents tend to abstract/editorialize
  → For code projects, multi-file artifacts: spawn executor agents
  → Write: reports/{date}/{task_name}/{deliverable}.md (not under adhoc_agents/)

PHASE 4: VALIDATION
  → Read all artifacts
  → Spawn 2-4 validation agents (one per dimension)
  → Consolidate into PASS/FAIL verdict
  → Write: validation/report.md

PHASE 5: FEEDBACK LOOP (if FAIL)
  → Classify issues: RESEARCH_GAP or EXECUTION_DEFECT
  → Re-run targeted agents
  → Max 5 iterations

PHASE 6: SELF-EVOLUTION
  → Review process, identify improvements
  → Update agent templates, skills, or CLAUDE.md
  → Write: .audit/self_evolving/{date}_{task}.md
```

## Interview Format — Choice-Based (MANDATORY)

All interview questions use structured choice format:
- Single choice (a/b/c/d with "Other: _____" option)
- Multiple choice (checkboxes with "Other: _____" option)
- Scale (Low/Medium/High/Critical)
- Yes/No with partial escape

See `agent_team__interview_manager.md` for full format spec.

## Interview Format Note
Interview agents follow the same tool restrictions: Read, Grep, Glob only (for codebase context). They do NOT use WebSearch or Write — they only generate questions.

## Agent Spawning Rules

1. **Always include in the prompt:**
   - Clear role and task boundaries
   - Input file paths to read (absolute)
   - Output file path to write (absolute)
   - Success criteria
   - What NOT to do

2. **Tool scoping (include in prompt as behavioral instructions):**
   - Interview agents: "Only use Read, Grep, Glob. Do NOT use WebSearch, Write, or Edit."
   - Research agents: "Only use Read, Grep, Glob, WebSearch, WebFetch. Do NOT use Write/Edit except for your output file."
   - Executor agents: "You may use Read, Write, Edit, Bash, Glob, Grep."
   - Validation agents: "Use Read, Grep, Glob, Bash. Only write to your assigned output file."

3. **Context efficiency:**
   - Pass file paths in prompts, not file contents
   - Agents read files themselves
   - Agent outputs must start with a ≤500 token summary header

## Findings Report — MANDATORY

After every run, write `.audit/adhoc_agents/{date}/{task}/findings_report.md`. This captures:
- Pipeline summary table (phase, agents spawned, duration, status)
- Skills and tools used
- Per-phase details (what happened, what took long, key decisions)
- Important notes (surprises, blockers, patterns)
- Recommendations for next run

See `agent_team__orchestrator.md` for the full template. **Never skip this step.**

## Prompt History

Append to `.audit/prompt_history/{YYYY-MM-DD}.md` after task completion:

```markdown
## [HH:MM] — Task: {task_name}
**User Prompt:** > {exact message}
**Classification:** {small/large}
**Agents Spawned:** {count and types}
**Iterations:** {count}
**Verdict:** {PASS/FAIL}
**Deliverables:** {file paths}
**Self-Evolution:** {changes made or "none"}
```

## Self-Evolution Checklist

After every task:
- [ ] Interview questions sufficient? Missing perspectives?
- [ ] Research angles complete? Gaps found during validation?
- [ ] Execution clean? Recurring defect patterns?
- [ ] Validation thorough? Issues that slipped through?
- [ ] Any new agent templates needed?
- [ ] Any agent template updates needed?
- [ ] Any CLAUDE.md updates needed?
- [ ] Any new skills needed?

Log changes to `.audit/self_evolving/{YYYY-MM-DD}_{task_name}.md`
