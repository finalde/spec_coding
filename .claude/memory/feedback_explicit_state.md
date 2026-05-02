---
name: agent_team state must be explicit
description: For spec_driven / agent_team workflows, all state must live in explicit, version-trackable surfaces (CLAUDE.md, .claude/settings*.json, or specs/{type}/{name}/). No hidden memory or cache mechanisms.
type: feedback
---

For anything inside the spec_driven workflow or `agent_team` skill/agents, every piece of state, configuration, or behavior-shaping artifact must be one of:

1. `CLAUDE.md` (rules / conventions),
2. `.claude/settings.json` or `.claude/settings.local.json` (harness config, hooks, permissions),
3. Files under `specs/{task_type}/{task_name}/` (per-task pipeline artifacts), or
4. Files under `.audit/adhoc_agents/{date}/{task_id}/` (runtime event stream — already declared in CLAUDE.md).

Do **not** rely on any other mechanism — including auto-memory entries that duplicate pipeline state, ambient prompt-cache assumptions, model-side memory, or user-level (`~/.claude/...`) caches — to influence agent_team behavior.

**Why:** The user wants the workflow to be 100% deterministic and inspectable. If a stage's behavior depends on something not visible in the four surfaces above, the workflow becomes opaque and irreproducible — defeats the whole point of a spec-driven pipeline.

**How to apply:**
- Pipeline progress / status (which stage a run is on, what's paused, etc.) lives in the `specs/{type}/{name}/` tree only — never in `.claude/memory/`. Derive status from which files exist.
- Auto-memory under `.claude/memory/` is fine for cross-conversation user/feedback/reference notes, but must not hold per-task pipeline state.
- Before adding any new mechanism (a sidecar JSON, a session-scoped store, a lookup file), check it lands in one of the four surfaces above. If not, don't add it.
- When resuming a paused run, read the `specs/` tree to determine where it is — don't trust a memory entry that claims a stage is "paused".
