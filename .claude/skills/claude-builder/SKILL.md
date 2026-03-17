---
name: claude-builder
description: Design and scaffold new Claude Code components under .claude/ — skills, agents, MCP servers, hooks, or CLAUDE.md additions. Use this whenever the user wants to add any new capability to their Claude Code setup, create a new slash command, build an agent, customize how Claude behaves, or extend their project with AI tooling. Trigger on phrases like "add an agent", "create a skill", "build a command", "set up an MCP", "add a hook", "help me customize Claude", or any request that involves creating something under .claude/. Even if the user says "build me an agent for X" but X sounds like a workflow, use this skill to help them pick the right component first.
---

# Claude Builder

Guide the user through designing and creating the right Claude Code component.

Your job has two phases: **clarify first, build second**. Jumping straight to building the wrong component wastes effort. A brief check-in upfront saves everyone time.

---

## Phase 1: Validate the component choice

Before writing anything, scan the project's `.claude/` directory to understand what already exists — you might be extending something rather than creating from scratch.

Then look at what the user asked for and check it against the table below.

### Component reference

| Component | Lives at | Best for |
|-----------|----------|----------|
| **Skill** | `.claude/skills/<name>/SKILL.md` | Reusable workflows, slash commands, step-by-step playbooks. Claude *follows* the skill's instructions. |
| **Agent** | `.claude/agents/<name>.md` | Specialized subagents the main conversation *delegates tasks to*. Gets its own model, MCP servers, and skills. |
| **MCP Server** | `.mcp.json` + server code | Connecting Claude to external APIs or systems as callable tools. |
| **CLAUDE.md** | repo root or `.claude/` | Persistent rules, conventions, and guidance that are always in context. |
| **Hooks** | `.claude/settings.json` | Shell commands that fire on Claude Code events (before/after tool calls, session end, etc.). |

### Skill vs Agent — the most common confusion

This is worth getting right. Ask yourself about the thing they want to build:

- Is it a *recipe Claude follows step-by-step* when the user invokes it? → **Skill**
- Is it a *separate worker Claude hands a task off to*, operating somewhat independently? → **Agent**
- Does it need its own model choice or its own set of MCP/tool access? → **Agent**
- Is it something the user wants to invoke with a slash command like `/do-thing`? → **Skill**
- Does it need to run in parallel while the main conversation continues? → **Agent**

**Common mismatches to catch:**

| User asks for... | Often actually needs... | Why |
|---|---|---|
| "an agent that writes commit messages" | a **skill** | It's a deterministic workflow, not a delegated worker |
| "a skill that does background research" | an **agent** | Parallel execution + focused tooling = agent |
| "an agent to enforce coding standards" | a **CLAUDE.md** addition | Rules that are always active belong in CLAUDE.md, not a worker |
| "an agent that connects to our Jira" | an **MCP server** + optional agent | The connection layer is MCP; an agent wraps it only if you need specialized behavior |
| "a skill to remind me to write tests" | a **hook** or **CLAUDE.md** | Always-on guidance isn't a slash command |

### Clarification step

1. Identify what the user asked for
2. Check if it matches the best-fit component
3. If there's a mismatch, explain it briefly — one short paragraph, not a lecture. Recommend the right component and explain *why* it's a better fit. Let the user confirm or override your suggestion — it's their project.
4. If it's genuinely ambiguous, ask one targeted question to decide
5. Once you're aligned, move to Phase 2

---

## Phase 2: Interview (optional but recommended)

After agreeing on the component, ask:

> "Would you like to go through a quick interview so I can build this well, or should I write a first draft from what you've already told me?"

If they want an interview, run the relevant section below. Ask one group of questions at a time — don't dump everything at once. Follow up naturally. Stop when you have enough.

If they skip the interview, use what you know and write a draft. Offer to refine it.

---

### Skill Interview

Goal: understand the workflow deeply enough to write instructions Claude will reliably follow.

**Round 1 — Core purpose**
- Walk me through the workflow end-to-end. What does Claude do, in what order?
- What does the user typically say to kick this off? (Informs the trigger description.)

**Round 2 — Inputs and outputs**
- What does Claude need as input? (Files, URLs, selected text, nothing?)
- What should the output look like? (A file, printed report, code edits, a message to the user?)

**Round 3 — Constraints and edge cases**
- What should happen if the input is missing, ambiguous, or malformed?
- Anything this skill should explicitly *not* do?
- Any tools, MCP servers, or external resources it depends on?

**Round 4 — Quality bar**
- What does a great result look like vs. a mediocre one?
- Are there examples of good output you can share or describe?

---

### Agent Interview

Goal: define a tight scope and the right tooling so the agent is focused and doesn't over-reach. Good agents do one thing well.

**Round 1 — Purpose and scope**
- What is the single core job this agent does? (The narrower, the better.)
- What triggers the main conversation to delegate to this agent?

**Round 2 — Tools and model**
- Does it need access to external systems? Which ones? (→ determines MCP servers)
- Does it need any skills of its own?
- Does this task require deep reasoning (→ Opus/Sonnet) or is it fast and repetitive (→ Haiku)?

**Round 3 — Autonomy and communication**
- How much should it decide on its own vs. surface questions back to the user?
- What should it return to the main conversation — just the final result, or a summary with artifacts?
- What is explicitly *out of scope* for this agent?

**Round 4 — Failure handling**
- What should it do when it hits an obstacle or is uncertain?
- Any hard constraints — things it must never do (delete files, make costly API calls, etc.)?

---

### MCP Server Interview

**Round 1 — Integration**
- What external system or API is this connecting to?
- What specific operations/tools should it expose to Claude?

**Round 2 — Auth and environment**
- How does it authenticate? (API key, OAuth, env var, service account?)
- Should it run as a local process or connect to a remote server?

**Round 3 — Scope**
- Any read-only constraints?
- Rate limits or cost implications Claude should be aware of?

---

### CLAUDE.md Interview

**Round 1**
- What rule, convention, or guidance needs to be added?
- Is this project-wide or scoped to a subdirectory?
- Is it a hard constraint ("never do X") or a strong preference ("prefer Y")?
- Does it fit into an existing section, or does it need its own?

---

### Hooks Interview

**Round 1**
- What event should trigger the hook? (`PreToolUse`, `PostToolUse`, `Stop`, `Notification`, etc.)
- What shell command should run?
- Should it be blocking (Claude waits for it to finish) or fire-and-forget?
- Any environment variables or context it needs?

---

## Phase 3: Build using official builders when available

Once you have enough information, don't build from scratch if Anthropic has an official skill or tool for that component type. Delegate to it — it will produce a higher-quality result and handle iteration, evals, and description optimization that you'd otherwise have to do manually.

### Check for official builders first

Before writing any files, check what skills are currently available (they appear in your `available_skills` list at the top of context). Then follow this priority order:

| Building a... | Preferred approach |
|---|---|
| **Skill** | If `skill-creator` is available, invoke `/skill-creator` and let it run the full create→test→iterate loop. Only write the SKILL.md yourself if skill-creator is not available. |
| **Agent** | If an official `agent-builder` skill exists (check available_skills), use it. Otherwise build manually per the spec below. |
| **MCP Server** | If `mcp-builder` is available, use it. Otherwise scaffold manually. |
| **CLAUDE.md / Hooks** | No official builder exists for these — write them directly. |

The reason to prefer official builders: they handle quality validation, iterative testing, and description optimization that you can't easily replicate inline. Think of yourself as the coordinator who gathered the requirements, and the specialist skill as the craftsperson who builds it.

**How to hand off:** Share the full context from the interview — the user's goals, inputs/outputs, constraints, quality bar — so the specialist skill has everything it needs without re-interviewing the user.

### If no official builder is available, build directly

Once you have enough information, create the files.

### Skill
Create `.claude/skills/<name>/SKILL.md` with proper YAML frontmatter:
```yaml
---
name: <name>
description: <trigger description — see notes below>
---
```
Add `references/`, `scripts/`, or `assets/` subdirectories only when they carry genuine weight (reusable scripts, large reference docs, templates). Don't add them speculatively.

### Agent
Create `.claude/agents/<name>.md` with frontmatter:
```yaml
---
name: <name>
description: <what the main conversation uses to decide whether to delegate here>
model: haiku | sonnet | opus   # pick based on task complexity
skills:               # optional
  - skill-name
mcpServers:           # optional
  - server-name
---
```
The system prompt body should be focused and specific. State what it does and what it doesn't do.

### MCP Server
Update `.mcp.json` and scaffold the server code (Python or Node) in a sensible location, usually `tools/<name>/`.

### CLAUDE.md
Add to the right section in the relevant CLAUDE.md. If the rule is project-wide, it goes in the root CLAUDE.md. Create a new section only if no existing section fits.

### Hooks
Update `.claude/settings.json` under the `hooks` key.

---

## Writing quality guidelines

**For descriptions (both skills and agents):** The description is the primary mechanism Claude uses to decide whether to invoke a skill or delegate to an agent. Include real phrases users will say, not just formal definitions. Lean toward being "pushy" — if there's any reasonable chance the user's request matches this component, the description should pull it in.

**Explain the why:** In skill instructions and agent system prompts, explain *why* something matters, not just *what* to do. Claude reasons well when it understands the intent — over-specified rules with no rationale tend to fail on edge cases.

**Agents should be narrow:** An agent that tries to do everything does nothing well. If the scope keeps expanding during the interview, suggest splitting into two agents or reconsidering whether a skill is more appropriate.

**Skills should stay lean:** Keep SKILL.md under ~300 lines. If it's growing large, move reference material to `references/` and point to it with clear guidance on when to read it.

---

## After building

Show the user what was created — file paths and a one-line description of each file's purpose. Then ask:
1. Does this look right, or should we adjust anything?
2. Want to test it? (For skills: invoke it with a sample prompt. For agents: delegate a test task.)