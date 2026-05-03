# Angle: Prior-art spec-driven tools

## 1. What this angle covers

How established tools that pair AI agents with spec/intent files structure the spec-to-execution loop, and what affordances they expose to users for inspecting, editing, or regenerating intent. The goal is to surface patterns `spec_driven` (the FastAPI + React webapp surfacing `specs/{type}/{name}/` artifacts and assembling copy-paste regeneration prompts) should copy, and anti-patterns to avoid. Tools surveyed: GitHub Spec Kit, AGENTS.md (open standard), Aider, Cursor rules, Continue.dev, JetBrains Junie, OpenAI Codex CLI.

## 2. Key findings

### 2.1 The dominant pipeline shape is "intent → plan → tasks → implement," with explicit human gates between stages

- **GitHub Spec Kit** decomposes the agent loop into `/constitution` (project principles), `/specify` (PRD), `/plan` (technical design), `/tasks` (verifiable units), `/implement`, plus optional `/clarify` and `/analyze` quality-gate commands. Each stage produces a separate, inspectable artifact and the pipeline "pauses at human review gates" between stages. ([github/spec-kit](https://github.com/github/spec-kit), [Spec Kit workflows](https://github.github.io/spec-kit/reference/workflows.html), [spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md))
- **JetBrains Junie** explicitly advertises a three-phase spec workflow: `requirements.md` → `plan.md` → `tasks.md`, and recommends "don't ask Junie to 'do everything in tasks.md' in one go… start with a subset" — i.e., bound the per-unit work and let the user re-enter between units. A "Think More" toggle forces the agent to refine plans before execution. ([JetBrains Junie spec-driven blog](https://blog.jetbrains.com/junie/2025/10/how-to-use-a-spec-driven-approach-for-coding-with-ai/))
- **Spec Kit** persists run state at `.specify/workflows/runs/<run_id>/{state.json, inputs.json, log.jsonl}` so a paused run is resumable: `specify workflow resume <run_id>`. Step outputs are addressable as `steps.specify.output.file` for downstream reference. ([Spec Kit workflows](https://github.github.io/spec-kit/reference/workflows.html))

`spec_driven`'s six-stage layout (intake → interview → research → spec → validation → execution) is a strict superset of the Spec Kit / Junie shape, with two original additions: an explicit interview stage with multi-choice prompts and a research/findings stage that synthesizes a dossier. Both are well-aligned with the stated rationale that PRDs are produced "through iterative dialogue with AI" that "asks clarifying questions, identifies edge cases, and helps define precise acceptance criteria." ([Microsoft blog on Spec Kit](https://developer.microsoft.com/blog/spec-driven-development-spec-kit))

### 2.2 Spec/rule files are plain markdown checked into the repo, with directory-tree precedence

- **AGENTS.md** is now stewarded by the Agentic AI Foundation (Linux Foundation) as a portable open standard adopted by Codex, Cursor, Aider, Jules, RooCode, Zed, etc. It is "just standard Markdown… agents automatically read the nearest file in the directory tree, so the closest one takes precedence." Recommended sections: commands, testing, project structure, code style, git workflow, boundaries. ([agents.md](https://agents.md/), [GitHub Blog on AGENTS.md](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/), [InfoQ](https://www.infoq.com/news/2025/08/agents-md/))
- **Codex** builds an "instruction chain" by walking from the project root to the cwd, checking `AGENTS.override.md` then `AGENTS.md` at each level, plus a home-directory variant. ([OpenAI Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md))
- **Cursor** has migrated from a single `.cursorrules` to `.cursor/rules/` containing one rule file per concern, each version-controlled, scoped via path globs, "invoked manually, or included based on relevance." ([Cursor docs — Rules](https://cursor.com/docs/context/rules))
- **Continue.dev** stores rules in `.continue/rules/` as numbered Markdown files (`01-general.md`, `02-stack.md`, `03-code-style.md`, …) auto-loaded for that workspace, with optional `globs` so a rule only applies to matching files. ([Continue rules deep-dive](https://docs.continue.dev/customize/deep-dives/rules))
- **Aider** uses a `CONVENTIONS.md` loaded via `aider --read CONVENTIONS.md` or `.aider.conf.yml`, with a hierarchy (home → repo root → cwd, last-loaded wins). ([Aider conventions](https://aider.chat/docs/usage/conventions.html))

`spec_driven`'s `CLAUDE.md` + per-stage playbooks + `agent_refs/{stage}/{general.md, <task_type>.md}` mirrors this pattern (plain markdown, version-controlled, layered general → task-type-specific). The split between "what the parent does" (playbooks) and "what the parent has learned" (refs) goes beyond what the surveyed tools offer.

### 2.3 The drift problem is universally acknowledged; the answer is regenerate, not edit

- "Specifications are living artifacts that generate implementations. Change the spec, regenerate the code… Modify a user story, and corresponding API endpoints regenerate." ([Microsoft blog on Spec Kit](https://developer.microsoft.com/blog/spec-driven-development-spec-kit))
- "Manual code editing is either prohibited or confined to well-defined extension points. In return, drift is eliminated by design: since code is regenerated rather than manually edited, spec and code are always aligned by construction." ([Augment — What is SDD](https://www.augmentcode.com/guides/what-is-spec-driven-development))
- "Divergence is no longer an edge case; it is the natural state that must be continuously governed… By Sprint 3, the HLD is outdated. By release 2, the SRS no longer matches the product. Preventing drift from accumulating is more practical than periodically reconciling diverged specifications." ([InfoQ — Spec-driven development](https://www.infoq.com/articles/spec-driven-development/))
- ThoughtWorks Tech Radar antipattern: "a bias toward heavy up-front specification and big-bang releases." ([Augment — What is SDD](https://www.augmentcode.com/guides/what-is-spec-driven-development))

`spec_driven`'s "read-zero from prior outputs" rule (delete the stage's files before regenerating, regen depends only on inputs + `CLAUDE.md` + promoted pins) is the most disciplined version of this principle I found in the survey — Spec Kit's documented regeneration semantics stop at "regenerate the code" without an explicit delete-first contract. The promoted-pins sidecar is also stronger than anything in the surveyed prior art.

### 2.4 Inspect/edit affordances split into three camps

| Tool | Inspect | Edit | Regenerate |
|------|---------|------|------------|
| Spec Kit | `state.json`, `log.jsonl`, per-stage `.md` files in repo | Edit `.md` directly in IDE; `/speckit.clarify` and `/speckit.analyze` are ad-hoc gate prompts | `specify workflow resume <run_id>`; chain of slash commands re-run downstream |
| AGENTS.md | Plain MD in repo | Plain MD in repo | n/a — the file is input to every agent run |
| Junie | Plan/tasks files in repo, "Code mode" vs "Ask mode" | Edit MD between phases; "do tasks 1–2 only" pattern | Re-prompt with same files |
| Cursor / Continue | Rules in `.cursor/rules/` or `.continue/rules/`, globs | Edit MD per rule | Auto-applied next message |
| Codex CLI | Audit logs of TUI session | Edit AGENTS.md, AGENTS.override.md | Re-run command; Symphony orchestrator (Linear → Codex) for batch ([OpenTools — Symphony](https://opentools.ai/news/openai-symphony-turns-linear-boards-into-autonomous-coding-agent-orchestration)) |

None of the surveyed tools ship a dedicated **GUI for editing intermediate spec artifacts**. They all rely on the user opening the file in their IDE. Spec Kit ships templates but no viewer. The closest thing is a community VS Code extension ("I Built a Visual Spec-Driven Development Extension for VS Code That Works With Any LLM" — [DEV community](https://dev.to/fabian_silva_/i-built-a-visual-spec-driven-development-extension-for-vs-code-that-works-with-any-llm-36ok)), which is a third-party effort. `spec_driven`'s webapp is therefore in a genuinely thin slice of the design space.

### 2.5 Autonomous mode is contracted via headers/flags, not configuration

- **Codex** has documented `--full-auto`, `--ask-for-approval`, and a sandbox mode hierarchy; AGENTS.md is the *durable* guidance, command-line flags switch the *per-run* autonomy level. ([Codex best practices](https://developers.openai.com/codex/learn/best-practices))
- **Junie** distinguishes "Code mode" (acts) vs "Ask mode" (read-only). ([Junie docs](https://junie.jetbrains.com/docs/))
- **Aider** has `--message` headless mode (one instruction, exit). ([Aider docs](https://aider.chat/docs/))

`spec_driven`'s `# EXECUTION MODE: AUTONOMOUS` header in pasted regen prompts is the same idea, expressed as a per-prompt contract. The webapp toggle defaulting to off ("interactive") matches Codex's default-low-autonomy posture.

### 2.6 Anti-patterns called out by the prior art

- **Heavy up-front spec, big-bang release.** ThoughtWorks Tech Radar antipattern.
- **Drift via surgical edit.** Augment, InfoQ, and Spec Kit all converge on regenerate-don't-edit.
- **Skipping planning.** Augment lists this as an antipattern; Junie's whole pitch is "ask the AI to *think first*, not code first." ([Junie blog](https://blog.jetbrains.com/junie/2025/10/how-to-use-a-spec-driven-approach-for-coding-with-ai/))
- **Unbounded execution sweeps.** Junie: "AI agents work best when they focus on a bounded unit of work, rather than trying to do everything simultaneously."
- **Reinventing waterfall.** Scott Logic's empirical writeup ("Putting Spec Kit Through Its Paces: Radical Idea or Reinvented Waterfall?" [Scott Logic blog](https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html)) is a direct warning that aggressive up-front specification can stall delivery.

## 3. Implications for the spec (concrete, actionable)

1. **Keep the per-stage Regenerate panel and master Regenerate panel in the project page.** This is the affordance the prior art is missing — Spec Kit users edit MD in their IDE and remember to re-run slash commands. A GUI that surfaces `regen-prompt` per stage and per project is a real differentiator. (Already in the spec; reinforced.)
2. **Make the regen prompt self-contained.** The webapp already inlines `revised_prompt.md` + every `follow_ups/*.md`. This matches Codex's "instruction chain" mental model and Spec Kit's `inputs.json` pattern — the regen prompt should be a complete restatement of intent so a fresh CLI session can act on it.
3. **Default the autonomous-mode toggle to off; persist per-prompt only.** Mirror Codex's default-low-autonomy posture. (Already in the spec.) Document the contract on the toggle itself, not just in `CLAUDE.md`.
4. **Surface the read-zero contract in the regen prompt body itself.** The current spec already requires this. Reinforce: emit `regen.delete.planned` / `regen.delete.completed` events visible in the events viewer, so the user sees the stage was actually deleted before the new generation wrote.
5. **Render `events.jsonl` as a first-class view.** Spec Kit has `log.jsonl` with no viewer; Codex audit logs are TUI-only. A webapp `EventsViewer` that filters by event type (`validation.issue.raised`, `regen.write.completed`, `pipeline.halted`) gives users something the prior art doesn't.
6. **Keep `<stage>/promoted.md` distinct from the regenerated artifact.** The pinned-items pattern has no direct analog in the surveyed prior art. Reasoning: Cursor rules / Continue rules are *applied at every run* (always-on), while `promoted.md` is *carried forward at every regen* (regen-input). Make sure the UI labels the distinction clearly: "this pin will appear in the next regen of this stage" — not "this pin is currently active on the next message."
7. **Mark the interview and research stages as `spec_driven`'s extensions.** Prior art jumps from raw idea straight to PRD. The interview multi-choice loop and the research dossier are real value-add and should be advertised as such in `README.md` (vs Spec Kit / Junie comparison table).
8. **Bound execution to one work unit at a time, with revision rounds capped.** Already in the spec (3 rounds, 30-min wall clock). Junie's "do tasks 1–2 only" pattern is the same shape.
9. **Avoid re-creating the waterfall failure mode.** Make sure the webapp doesn't make it *easier* to over-spec at stage 4 by showing huge spec.md surfaces with no quick path to "just go to stage 6 with a thin spec." Maybe surface a "spec wordcount / FR count" indicator with a soft warning when it crosses a threshold.

## 4. Open questions surfaced

- **Should `spec_driven` adopt AGENTS.md as a co-equal alongside `CLAUDE.md`?** The Agentic AI Foundation steward gives it portability across Codex, Cursor, Aider, Junie, etc. If the user ever wants to drive the same `specs/` tree from a non-Claude agent, an `AGENTS.md` symlink/copy of `CLAUDE.md`'s repo-rules section would unlock that without forking.
- **Drift detection for the artifacts themselves.** Spec Kit's `/speckit.analyze` "catches inconsistencies between your spec, plan, and tasks before implementation begins." Should `spec_driven` ship a `/analyze` equivalent that scans `qa.md` ↔ `spec.md` ↔ `validation/strategy.md` for unreferenced FR/AC IDs? Out of scope for v1, but worth a future stage 4.5.
- **Multi-run comparison.** None of the prior art lets you diff two runs of the same stage side-by-side. Given the read-zero contract, a stash-then-regen-then-diff workflow would be a clear win for users debugging "why did the spec change."
- **Workflow YAML vs ad-hoc regen prompts.** Spec Kit's `workflows/` are YAML pipelines that orchestrate slash commands with `if`/`switch` and gate steps. `spec_driven` currently emits ad-hoc copy-paste prompts — should it also emit a YAML workflow file the user can replay deterministically? This bridges the "GUI for inspect/edit" with the "CLI for execute" worlds, but adds substantial scope.
- **Should `promoted.md` support globs/scopes the way Cursor rules do?** A pinned FR that should "always survive a stage 4 regen, even after the FR id changes" might need a fuzzier match than the current verbatim-id-then-orphaned-section fallback. Worth deferring until the orphaned-section behavior is observed in real use.

## Sources

- [github/spec-kit](https://github.com/github/spec-kit)
- [Spec Kit workflows reference](https://github.github.io/spec-kit/reference/workflows.html)
- [spec-driven.md (Spec Kit)](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- [Microsoft blog — Diving Into SDD With GitHub Spec Kit](https://developer.microsoft.com/blog/spec-driven-development-spec-kit)
- [GitHub Blog — spec-driven development with AI](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)
- [agents.md](https://agents.md/)
- [GitHub Blog — How to write a great agents.md](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/)
- [InfoQ — AGENTS.md as open standard](https://www.infoq.com/news/2025/08/agents-md/)
- [OpenAI Codex — AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md)
- [OpenAI Codex — best practices](https://developers.openai.com/codex/learn/best-practices)
- [OpenTools — OpenAI Symphony](https://opentools.ai/news/openai-symphony-turns-linear-boards-into-autonomous-coding-agent-orchestration)
- [Aider — coding conventions](https://aider.chat/docs/usage/conventions.html)
- [Cursor docs — Rules](https://cursor.com/docs/context/rules)
- [Continue.dev — Rules deep-dive](https://docs.continue.dev/customize/deep-dives/rules)
- [JetBrains Junie — How to use a spec-driven approach](https://blog.jetbrains.com/junie/2025/10/how-to-use-a-spec-driven-approach-for-coding-with-ai/)
- [JetBrains Junie docs](https://junie.jetbrains.com/docs/)
- [Augment Code — What is SDD](https://www.augmentcode.com/guides/what-is-spec-driven-development)
- [InfoQ — Spec-Driven Development](https://www.infoq.com/articles/spec-driven-development/)
- [Scott Logic — Spec Kit through its paces](https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html)
- [DEV — Visual SDD VS Code extension](https://dev.to/fabian_silva_/i-built-a-visual-spec-driven-development-extension-for-vs-code-that-works-with-any-llm-36ok)
