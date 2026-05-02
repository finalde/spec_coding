# Angle: Autonomous-mode header + copy-paste regen prompt design

This angle surveys prior art for "header-switches-behavior" prompt contracts (Claude Code plan mode, OpenAI Model Spec, Cursor `.mdc`, Aider `CONVENTIONS.md`, AGENTS.md / Codex, Continue.dev, GitHub Spec Kit), maps the design space of copy-paste vs API-driven regeneration, and lists the templating patterns that work for server-side prompt assembly. It closes with concrete recommendations for `spec_driven`'s `# EXECUTION MODE: AUTONOMOUS` header, its CLAUDE.md backing line, the warn-don't-truncate size policy, and the section-breakdown UI that should sit before the Copy button.

---

## 1. Prior art: "header switches behavior" prompt contracts

### 1.1 Anthropic Claude Code — plan mode

Plan mode is the closest analogue in Anthropic's own product to what `spec_driven` is building. It is implemented as a single short `<system-reminder>` block prepended to every user message after the user toggles Shift+Tab into plan mode. The verbatim text, captured from a public reverse-engineering exercise, is:

> "Plan mode is active. The user indicated that they do not want you to execute yet — you MUST NOT make any edits (with the exception of the plan file mentioned below), run any non-readonly tools (including changing configs or making commits), or otherwise make any changes to the system. This supercedes any other instructions you have received." [[Plan mode reverse-engineering, Armin Ronacher](https://lucumr.pocoo.org/2025/12/17/what-is-plan-mode/)] [[Sergey Karayev tweet](https://x.com/sergeykarayev/status/1965575615941411071)]

Three observations matter for `spec_driven`:

1. **Length is short and load-bearing.** The whole reminder is roughly 50 words. Anthropic chose density over hedging.
2. **Imperatives are uppercased.** `MUST NOT` is the only ALL-CAPS clause, and it carries the entire restriction.
3. **A precedence claim is made explicit.** "This supercedes any other instructions you have received" is the precedence override, embedded in the reminder itself rather than enforced harness-side. (Spelling preserved verbatim — note that "supercedes" is the historical variant; Anthropic kept it.)

Enforcement is **model-side / prompt-only**. The Bash tool, Write, and Edit are still wired up; the model is just instructed not to call them. Sondera's analysis demonstrated the obvious failure mode — Claude can be jailbroken into editing `~/.zshrc` while in plan mode, because nothing harness-side blocks the write [[Sondera, Claude Code's plan mode isn't read-only](https://blog.sondera.ai/p/claude-codes-plan-mode-isnt-read)]. A reverse-engineering scrape of Claude Code's bundled prompts shows this is a general pattern: plan/explore/auto/background modes are all "conditional system prompt injection" plus tool-availability changes, not hard mode locks [[Piebald-AI/claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts)].

**Takeaway for spec_driven:** prompt-level enforcement is the industry baseline. It works *most* of the time and degrades gracefully when it doesn't (the worst case is a question being asked despite the header — annoying but not destructive). The verbatim line from `CLAUDE.md` already mirrors plan mode's structure.

### 1.2 OpenAI Model Spec — authority hierarchy

OpenAI's Model Spec defines a five-level chain of command: **Root → System → Developer → User → Guideline** [[Model Spec 2025-12-18](https://model-spec.openai.com/2025-12-18.html)]. Higher levels override lower ones; root rules cannot be overridden by anything (including OpenAI's own system messages); guidelines are the only level that can be implicitly overridden via context.

This is the cleanest published spec of how a header should claim authority over downstream content. The Model Spec's verbatim assertion — "Instructions with higher authority override those with lower authority" — is the rhetorical pattern `spec_driven`'s autonomous header should imitate: declare the level of the instruction, then state what it overrides.

**Takeaway:** `# EXECUTION MODE: AUTONOMOUS` is effectively a developer-level instruction in OpenAI's hierarchy. It should explicitly state which lower-level behaviors it suppresses (asking questions, pausing for confirmation) and which it does NOT touch (safety rules, sandbox, audit, follow-up handling). The current CLAUDE.md text already does this with the "Still honor every other rule in this file" clause — that clause is doing the same work as Model Spec's "guideline-level can be overridden, root-level cannot."

### 1.3 Cursor — `.cursor/rules/*.mdc`

Cursor encodes per-rule activation in YAML frontmatter [[Cursor MDC reference](https://github.com/sanjeed5/awesome-cursor-rules-mdc/blob/main/cursor-rules-reference.md), [Optimal MDC structure](https://forum.cursor.com/t/optimal-structure-for-mdc-rules-files/52260)]:

```yaml
---
description: <when this rule should be applied>
globs: <file pattern>
alwaysApply: <true|false>
---
```

Three activation modes follow from the three-field combination:

- `alwaysApply: true` (description and globs ignored) → in every prompt.
- `alwaysApply: false` + `globs` → in prompt when matching files are open.
- `alwaysApply: false` + `description` → "apply intelligently": the model decides whether to pull the rule in, based on the description.

Enforcement is harness-side for activation (Cursor decides when to inject the rule) and model-side for compliance (Cursor cannot stop the model from ignoring a rule it injected).

**Takeaway:** Cursor's three-mode taxonomy shows that mode flags are *not* the only design point. `spec_driven`'s autonomous header is closest to `alwaysApply: true` for one specific run — it's a per-paste opt-in, not a saved setting. That's the right call for a destructive-by-omission feature (no question-asking).

### 1.4 Aider — `CONVENTIONS.md` + `.aider.conf.yml`

Aider keeps conventions in a regular Markdown file, loaded explicitly via `aider --read CONVENTIONS.md` or via `.aider.conf.yml`'s `read:` key [[Aider conventions](https://aider.chat/docs/usage/conventions.html), [Aider YAML config](https://aider.chat/docs/config/aider_conf.html)]:

```yaml
read:
  - CONVENTIONS.md
```

`--read` marks the file read-only and lets prompt caching kick in. There is no "mode header" — the conventions are always present once configured. Enforcement is model-side only; Aider's own analysis page demonstrates it via "with conventions, Claude correctly used `httpx` and provided type hints," not via a verifier.

**Takeaway:** for stable, always-on rules (coding style, file layout, naming), a flat included file is enough. For *transient* rules (autonomous-mode-only restrictions for a single paste), an inline header is the better fit. `spec_driven` correctly chose the inline-header pattern for autonomous mode and the persistent-file pattern (CLAUDE.md) for the always-on rules.

### 1.5 AGENTS.md / OpenAI Codex — hierarchical override + 32 KiB cap

Codex's AGENTS.md format is a hierarchical, monorepo-aware version of CLAUDE.md [[Codex AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md), [openai/codex docs](https://github.com/openai/codex/blob/main/docs/agents_md.md)]:

- **Discovery walk:** global (`~/.codex/AGENTS.md`) → repo root → current directory. Files closer to the working directory appear later in the assembled prompt and "override earlier guidance" by virtue of recency.
- **`AGENTS.override.md`** at any level *replaces* the AGENTS.md at that level instead of merging — explicit override channel for personal/machine-specific tweaks not committed to git.
- **Hard size cap: `project_doc_max_bytes` = 32 KiB by default.** Once the combined size hits the cap, **Codex stops adding files and silently truncates without warning.**

That last point is exactly the anti-pattern `spec_driven` should avoid. The Codex behavior is unsafe because:
1. The user has no idea their later AGENTS.md files were dropped.
2. The model has no idea it's missing context.
3. The drop boundary is byte-counted, so it can land mid-sentence.

This single design failure is the strongest argument for `spec_driven`'s warn-don't-truncate policy: when the assembled regen blob exceeds a soft threshold, surface it to the user before they paste, because nobody — model or user — can detect silent truncation after the fact.

### 1.6 Continue.dev — `.continue/rules/`

Continue uses a folder of Markdown files (YAML still supported for back-compat) loaded into the system message of Agent / Chat / Edit modes [[Continue.dev rules deep-dive](https://docs.continue.dev/customize/deep-dives/rules)]. Frontmatter:

- `globs` — file-pattern gating
- `regex` — content-pattern gating
- `description` — read by the agent only when `alwaysApply: false`, to decide if the rule should be pulled in
- `alwaysApply: true | false`

Loading order is lexicographic, "joined with newlines" into the system message. There's no header-switches-behavior pattern; mode is implicit in the editor (Agent vs Chat vs Edit), and the rules merely hint at fit.

**Takeaway:** Continue's "hub → referenced → workspace → global" precedence ladder is a richer version of Codex's discovery walk. For a single-project tool like `spec_driven`, this is overkill, but the lexicographic-prefix-numbering trick (`001-foo.md`, `002-bar.md`) is exactly how `user_input/follow_ups/NNN-...md` should be ordered (and is).

### 1.7 GitHub Spec Kit — slash commands

Spec Kit ships three slash commands [[Spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md), [Spec Kit slash commands](https://deepwiki.com/github/spec-kit/5-slash-commands-reference)]:

- `/speckit.specify` → writes `specs/[branch]/spec.md`
- `/speckit.plan` → writes `plan.md`, `research.md`, `data-model.md`, `contracts/`
- `/speckit.tasks` → writes `tasks.md`

These run *inside* the agent (Copilot, Claude, etc.) — the agent recognizes the slash command and executes the bundled prompt template. They're not copy-paste blobs. The artifact tree (`specs/[branch]/`) is essentially identical in shape to `spec_driven`'s `specs/{type}/{name}/`.

**Takeaway:** Spec Kit is the closest peer in workflow shape, but it diverges in execution model. Spec Kit lives inside the agent harness and uses slash-command invocation; `spec_driven` lives outside and uses copy-paste. The next section discusses why that split is intentional.

---

## 2. Copy-paste vs API-driven regeneration patterns

The trade space:

| Dimension | Copy-paste blob (`spec_driven`) | API-driven (Spec Kit, Cursor, Cline) |
|---|---|---|
| Auth surface | None — user owns the model session | Tool needs API key / OAuth |
| Visibility | User reads the prompt before pasting | Hidden in tool internals |
| Drift risk | Low — model session has fresh state every paste | High — long-running session can drift |
| Cost model | User's existing subscription | Per-call API charges or tool subscription |
| Replayability | High — prompt persists in chat history | Low without explicit logging |
| Multi-stage parallelism | Hard — user serializes pastes | Easy — tool fans out calls |

Copy-paste is the right pattern when (a) the user already has a CLI-grade model session running, (b) auditability and "I read what I sent" are values, and (c) the regeneration cadence is human-paced (a few times a day) rather than agent-paced (hundreds per minute). All three apply to `spec_driven`. The pattern of "copying context out of your editor, pasting it into a chat window, and copying the response back" is widely critiqued for *interactive coding*, but `spec_driven`'s use case is *occasional regeneration of a known spec stage*, where the round-trip cost is amortized over a multi-hour writing task [[Cline overview](https://www.deployhq.com/guides/cline)].

The transparency win matters: with copy-paste, the user sees the full regen blob — `revised_prompt.md` plus every follow-up file inlined — before they hand it to the model. That's a property no API-driven tool offers. It's the single feature that makes `# EXECUTION MODE: AUTONOMOUS` safe to ship: the user has the chance to read what autonomous mode was asked to do before authorizing it.

The cost: parallelism is poor (one paste at a time) and the user must manage the model session themselves (no automatic retries, no streaming validation across stages). For `spec_driven`'s six-stage pipeline these are acceptable; the alternative (running an autonomous agent against the user's Claude Code session via API) would require API credentials, a long-running daemon, and a much heavier audit story.

---

## 3. Server-side prompt assembly patterns

The webapp's `POST /api/regen-prompt` is a server-side template renderer. Two patterns dominate:

**Jinja2** is the de-facto standard for LLM prompt templating in Python ecosystems [[Microsoft Semantic Kernel Jinja2 docs](https://learn.microsoft.com/en-us/semantic-kernel/concepts/prompts/jinja2-prompt-templates), [Instructor Jinja docs](https://python.useinstructor.com/concepts/templating/), [Haystack PromptBuilder](https://docs.haystack.deepset.ai/docs/promptbuilder)]. It supports variable insertion, conditionals, loops, and filters. Production deployments use `jinja2.sandbox.SandboxedEnvironment` to prevent template-injection attacks when any template content is user-influenced [[Gretel docs](https://docs.gretel.ai/create-synthetic-data/gretel-data-designer/using-jinja-templates)].

**Handlebars / Mustache** is the lightweight alternative — fewer features, simpler escape semantics, easier to reason about. Used by some platforms (Inya, parts of Semantic Kernel) [[Inya Jinja docs](https://docs.inya.ai/C03_Jinja)].

For `spec_driven`'s narrow use case (inline a fixed list of files, no logic), the templating need is closer to "string formatting" than "templating engine." Python f-strings or `.format()` are sufficient; reaching for Jinja would introduce a dependency for one variable substitution. The risk surface is also small: the user authored the source files (`revised_prompt.md`, `follow_ups/*.md`), so injection is self-injection. The only substitution is the mode header (autonomous vs interactive) plus a separator/heading per follow-up.

The architectural point is **assembly-time variable inlining, not runtime fetching.** The model never reaches out to read files; the harness serializes the entire intent into one blob the user pastes. This is what makes the prompt self-contained and replayable.

---

## Recommendations for `spec_driven`

1. **Keep `# EXECUTION MODE: AUTONOMOUS` as the single load-bearing header line.** Place it on line 1 of the assembled prompt with no preamble. Pattern-match the brevity of Claude Code's plan-mode reminder: a short imperative is more reliable than a paragraph.

2. **Adopt a verbatim imperative line directly under the header**, in the style of plan mode. Suggested wording: `You MUST NOT call AskUserQuestion in this run. For ambiguous decisions use best judgment and record the choice inline in the artifact you produce. Produce every requested artifact in this turn before stopping.` Mirror the uppercase-MUST-NOT convention. The current CLAUDE.md autonomous-mode block already says all of this; collapsing it into a single quotable line lets the regen blob enforce itself without depending on the reader having internalized CLAUDE.md.

3. **Keep CLAUDE.md as the back-reference.** The pasted blob does not need to restate the full autonomous-mode rules — it just needs to say "honor `CLAUDE.md` § Regeneration prompts & autonomous mode." The Model Spec authority pattern (level + override scope) applies: the header asserts what it suppresses (questions, pausing) and explicitly defers everything else to CLAUDE.md.

4. **Adopt warn-don't-truncate as the size policy, with a soft threshold visible in the UI.** Codex's silent 32 KiB truncation is an explicit anti-pattern: the model can't tell context was dropped, and the user can't tell either. Pick a soft warning threshold (e.g., 24 KiB or ~6,000 tokens — well under any model context limit but high enough that a typical project won't trip it) and surface it before the Copy button: "This prompt is 28 KiB. The model can still handle it, but if regeneration quality degrades, consider archiving older follow-ups." Never truncate silently. Never auto-summarize.

5. **Section-breakdown UI before the Copy button.** Render the assembled prompt as a tree the user can fold open: `[Header] [Stage instructions] [revised_prompt.md (X bytes)] [follow_ups/001-...md] [follow_ups/002-...md] ...`. This is the transparency win that justifies the copy-paste model in the first place — the user can verify what they're about to authorize. Copy still copies the full assembled blob; the breakdown is read-only.

6. **Mark each inlined source file with a delimiter the model can rely on.** Use a single shape across the whole prompt — e.g., a heading like `## file: specs/.../user_input/revised_prompt.md` directly above each inlined block, then the file content unchanged. Continue.dev's "join rules with newlines" plus Aider's read-only file marker are both versions of this. The model reads the path-headed block as "this is the canonical revised prompt," not "this is part of the user's instruction."

7. **Default the autonomous toggle to off, and persist the setting per browser only.** This matches CLAUDE.md's existing rule and Cursor's per-project rules pattern: a destructive-by-omission flag should never be a session-global default. `localStorage["spec_driven.autonomous_mode.v1"]` is the right scope — explicit, per-user, per-browser, no server-side state. Match the toggle to a clear visual diff in the assembled prompt header (the user should be able to *see* whether they're about to paste an autonomous run).

8. **Log every assembled prompt to `.audit/adhoc_agents/.../prompt.md`** even when the user generated it from the webapp. The auditability story is the second-strongest argument for the copy-paste model; surrendering it because the prompt was assembled in a browser tab would forfeit the property. The webapp can write the assembled blob to the audit folder at the same moment it offers it to the user for copying — same content, two destinations.

---

## Open questions / not researched

- **Exact silent-truncation behavior of Claude Code itself when CLAUDE.md exceeds some internal limit.** I know Codex's cap is 32 KiB; Claude Code's CLAUDE.md handling under heavy load was not surveyed. If `spec_driven`'s assembled prompt grows large enough to bump against a host-side cap, that interacts with the warn-don't-truncate recommendation in ways I did not measure.
- **Token-count vs byte-count for the soft threshold.** I recommended 24 KiB as a byte threshold, but token count is the more accurate signal. A tokenizer call in the webapp would be more honest; whether that's worth the dependency was not researched.
- **Whether `# EXECUTION MODE: AUTONOMOUS` survives a re-paste into a fresh Claude Code session vs into an existing session with a long history.** Plan mode's reminder is re-prepended to *every* user message; a copy-paste header is single-shot. I did not test whether long-running sessions cause the header to drift out of attention scope mid-run.
- **Cross-tool portability.** The spec_driven blob is currently optimized for Claude Code. Whether the same header convention reads cleanly in Cursor, Cline, or Codex (all of which have their own mode systems) is an unanswered question.
- **Adversarial prompt injection from `follow_ups/*.md`.** Since users author follow-ups, the risk is self-injection; but if a follow-up file is later edited by another tool (a teammate, an automated bot), the header could be neutralized by content placed lower in the blob. A simple defense — re-stating the imperative line at the bottom of the blob — was not surveyed and would benefit from a small experiment.

---

## Sources

- [Plan mode reverse-engineering — Armin Ronacher](https://lucumr.pocoo.org/2025/12/17/what-is-plan-mode/)
- [Sergey Karayev tweet — verbatim plan-mode reminder](https://x.com/sergeykarayev/status/1965575615941411071)
- [Sondera — Claude Code's plan mode isn't read-only](https://blog.sondera.ai/p/claude-codes-plan-mode-isnt-read)
- [Piebald-AI — claude-code-system-prompts repo](https://github.com/Piebald-AI/claude-code-system-prompts)
- [OpenAI Model Spec 2025-12-18](https://model-spec.openai.com/2025-12-18.html)
- [Cursor MDC reference](https://github.com/sanjeed5/awesome-cursor-rules-mdc/blob/main/cursor-rules-reference.md)
- [Cursor forum — Optimal MDC structure](https://forum.cursor.com/t/optimal-structure-for-mdc-rules-files/52260)
- [Aider — Specifying coding conventions](https://aider.chat/docs/usage/conventions.html)
- [Aider — YAML config](https://aider.chat/docs/config/aider_conf.html)
- [OpenAI Codex — AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md)
- [openai/codex docs/agents_md.md](https://github.com/openai/codex/blob/main/docs/agents_md.md)
- [Continue.dev — Rules deep-dive](https://docs.continue.dev/customize/deep-dives/rules)
- [GitHub Spec Kit — spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- [Spec Kit slash command reference (DeepWiki)](https://deepwiki.com/github/spec-kit/5-slash-commands-reference)
- [Microsoft Semantic Kernel — Jinja2 prompt templates](https://learn.microsoft.com/en-us/semantic-kernel/concepts/prompts/jinja2-prompt-templates)
- [Instructor — Prompt templating with Jinja](https://python.useinstructor.com/concepts/templating/)
- [Haystack PromptBuilder](https://docs.haystack.deepset.ai/docs/promptbuilder)
- [Gretel — Using Jinja templates](https://docs.gretel.ai/create-synthetic-data/gretel-data-designer/using-jinja-templates)
- [Inya — Jinja for dynamic system prompts](https://docs.inya.ai/C03_Jinja)
- [Cline overview — DeployHQ](https://www.deployhq.com/guides/cline)
