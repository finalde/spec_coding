# Angle — copypaste-prompt-ux

## 1. What this angle covers

How production tools that emit copy-paste LLM prompts signal **execution mode** (autonomous vs interactive) and present the assembled prompt for human copy. Specifically:

- (a) header conventions — literal first-line directive vs frontmatter vs metadata field
- (b) prompt-assembly rules — what gets inlined vs referenced
- (c) "Build prompt → Copy" UX flow — visible inline vs collapsed `<details>`; soft-wrap toggle; size warnings
- (d) section breakdown of the assembled prompt for the user's preview
- (e) size-budget signals — warn-don't-truncate vs hard-413
- (f) how the receiving model is told to honor the mode contract

The angle informs FR-14c (regen-prompt assembly) and FR-42 (Build prompt → Copy UI) for `spec_driven`.

## 2. Key findings

### Header conventions: there is no industry-standard literal `# EXECUTION MODE` directive — `spec_driven` is inventing one

- **Cursor / `.cursor/rules/*.mdc`** uses **YAML frontmatter** with three fields: `description`, `globs`, `alwaysApply`. The "mode" of a rule (always-on, file-pattern-scoped, agent-decided, manual) is signaled by the *combination* of those fields, not a literal mode header. `alwaysApply: true` is the closest equivalent to "this rule must be honored." [cursor.com/docs/context/rules](https://cursor.com/docs/context/rules)
- **GitHub Spec Kit** prompts use frontmatter with a `mode:` field (e.g. `mode: speckit.command-name`) for routing inside Copilot Chat skills, but it is a *routing* signal, not an autonomy signal. [github.com/github/spec-kit/blob/main/AGENTS.md](https://github.com/github/spec-kit/blob/main/AGENTS.md)
- **AGENTS.md (the cross-tool standard, stewarded under the Linux Foundation Agentic AI Foundation)** is *just standard Markdown* — "use any headings you like; the agent simply parses the text you provide." There is no mode header at all. Mode is inferred from prose. [agents.md](https://agents.md/), [developers.openai.com/codex/guides/agents-md](https://developers.openai.com/codex/guides/agents-md)
- **Claude Code plan mode** injects a *literal system-message preamble* `Plan mode is active` plus the contract `you MUST NOT make any edits…`. This is a system-level injection, not a header the user sees in a copy-paste artifact. [lucumr.pocoo.org/2025/12/17/what-is-plan-mode/](https://lucumr.pocoo.org/2025/12/17/what-is-plan-mode/), [claudelog.com/mechanics/plan-mode/](https://claudelog.com/mechanics/plan-mode/)
- **JetBrains Junie** signals autonomy via a UI checkbox ("Brave Mode") that maps to an internal flag — there is no user-visible prompt header. [jetbrains.com/help/junie/modes.html](https://www.jetbrains.com/help/junie/modes.html), [junie.jetbrains.com/docs/junie-cli.html](https://junie.jetbrains.com/docs/junie-cli.html)
- **OpenAI Model Spec** uses a structural hierarchy (system / developer / user) baked into the API, not a literal mode header; commentary blocks are visually distinguished from instruction blocks but do not gate execution autonomy. [model-spec.openai.com/2025-12-18.html](https://model-spec.openai.com/2025-12-18.html)
- **Codex CLI** also recommends "turning up the autonomy or prompting for a 'non-interactive' mode" for evals — phrased as prose, not a header. [developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide)

**Implication:** the literal `# EXECUTION MODE: AUTONOMOUS` / `# EXECUTION MODE: INTERACTIVE` header that follow-up 001 specifies is a *novel convention for this repo*. It is justified — copy-paste prompts have no system/developer message channel, so the contract has to ride in the prose — but the spec should call it out explicitly and document why frontmatter was rejected.

### Prompt-assembly rules: inlined > referenced for copy-paste workflows

- **Codex CLI** concatenates `AGENTS.md` files top-down ("Codex concatenates files from the root down, joining them with blank lines. Files closer to your current directory override earlier guidance because they appear later in the combined prompt"). Inline assembly, not reference. [developers.openai.com/codex/guides/agents-md](https://developers.openai.com/codex/guides/agents-md)
- **Continue.dev `.prompt` files** use a YAML preamble above a `---` separator and inline the body verbatim into the chat; context-provider variables (`{{file}}`, `{{input}}`) expand at send time, not reference time. [docs.continue.dev/customize/deep-dives/prompts](https://docs.continue.dev/customize/deep-dives/prompts), [docs.continue.dev/features/prompt-files](https://docs.continue.dev/features/prompt-files)
- **Cursor** rule files, when activated, are inlined into the system prompt — never referenced as paths the model has to fetch. The user never sees the assembled bundle in their chat input. [cursor.com/docs/context/rules](https://cursor.com/docs/context/rules)
- **Spec Kit slash commands** install command files into `.claude/`, `.github/prompts/`, `.pi/prompts/`, etc., and the agent reads those command files directly when the slash command fires — but the *user-visible* artifact is the spec/plan/tasks markdown, which is itself self-contained. [github.com/github/spec-kit](https://github.com/github/spec-kit)

**Established convention:** for copy-paste prompts where the receiving session has no shared filesystem context, **inline the content of every dependency**. Listing filenames is acceptable as an *audit trail*, but the prompt body must be self-contained. This matches the qa.md decision for FR-14c (inline `revised_prompt.md`, list every `follow_ups/*.md` filename, inline non-empty `<stage>/promoted.md`).

### Build-prompt → Copy UX: the inline-visible-block pattern is the converged norm for long content

- **PatternFly Clipboard Copy** — the canonical design-system reference — distinguishes inline (single-line, scroll-fade-right for overflow) vs **block (recommended for very long content), with an expand caret and a copy icon in the header bar**. [patternfly.org/components/clipboard-copy](https://www.patternfly.org/components/clipboard-copy/), [patternfly.org/v3/pattern-library/forms-and-controls/copy-to-clipboard](https://www.patternfly.org/v3/pattern-library/forms-and-controls/copy-to-clipboard/index.html)
- **Cloudscape (AWS) `<copy-to-clipboard>`** confirms the same model: "Copy" button with a transient success state ("Copied!" for 2–3 seconds). [cloudscape.design/components/copy-to-clipboard](https://cloudscape.design/components/copy-to-clipboard/)
- **Flowbite (Tailwind)** ships the same pattern: bordered code/textarea block, copy button anchored to the header bar. [flowbite.com/docs/components/clipboard](https://flowbite.com/docs/components/clipboard/)
- **Soft-wrap toggle**: HTML's native `wrap` attribute supports `soft` / `hard` / `off`; CSS `text-wrap` extends it. Wrapping is universally the *default* for textarea, and toggling it off (so users can see indentation / line structure) is the established power-user affordance. [developer.mozilla.org/en-US/docs/Web/API/HTMLTextAreaElement/wrap](https://developer.mozilla.org/en-US/docs/Web/API/HTMLTextAreaElement/wrap), [developer.mozilla.org/en-US/docs/Web/CSS/text-wrap](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/text-wrap)
- **Collapsing behind `<details>`** is *not* the converged norm for content the user is going to copy in one click — design systems specifically recommend visible-block when the content is long, with internal scroll, not collapse-then-expand. Follow-up 002's "no inner `<details>`, inline visible block with header bar Copy + Wrap toggle" matches PatternFly/Cloudscape/Flowbite guidance.

### Size-budget signals: warn, don't truncate

- No mainstream tool **hard-truncates** an assembled prompt for the user. They warn:
  - **Codex CLI** caps merged `AGENTS.md` content with a "size cap" but is explicit about it; truncation is logged. [developers.openai.com/codex/guides/agents-md](https://developers.openai.com/codex/guides/agents-md)
  - **Cursor** does not truncate rule bundles; long rules degrade rule-following quality, which is surfaced in community guidance ("keep rules short / under ~500 lines"), not in a hard cap. [forum.cursor.com/t/my-best-practices-for-mdc-rules-and-troubleshooting/50526](https://forum.cursor.com/t/my-best-practices-for-mdc-rules-and-troubleshooting/50526)
  - **Claude API XML-tagged prompts** documentation explicitly warns "avoid over-tagging" and "be consistent" but does not cap length. [docs.claude.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags)
- **For a copy-paste UI**, the established UX is: show byte/char count, soft-warn at a threshold (e.g. ">100 KB"), never truncate the copy payload. The user is the one who knows their target model's context window.

### Section breakdown of the assembled prompt

Across Codex/Cursor/Continue/Spec Kit, the consensus structure is:

1. **Mode / role preamble** (system-level intent — "you are a coding agent", autonomy contract)
2. **Project / repo context** (inlined `AGENTS.md` / `CLAUDE.md` / cursor rules)
3. **Task statement** (the user's revised prompt + any follow-ups)
4. **Constraints / guardrails** (non-negotiables, file scope, tools)
5. **Pinned must-survive content** (Spec Kit's "constitution.md" plays this role; for `spec_driven` it's `<stage>/promoted.md`)
6. **Output contract** (what artifacts to produce, where to write them)

`spec_driven`'s FR-14c assembly should mirror this ordering.

### How the receiving model is told to honor the mode contract

- **Plan mode (Claude Code)** uses an imperative "you MUST NOT make any edits" — restrictive, single-axis. [lucumr.pocoo.org/2025/12/17/what-is-plan-mode/](https://lucumr.pocoo.org/2025/12/17/what-is-plan-mode/)
- **Codex preamble guidance** says "acknowledge then plan before any tool calls; 1-sentence acknowledgement, 1–2 sentence plan; updates every 1–3 execution steps; hard floor every 6 steps or 10 tool calls" — prescriptive cadence rules, not a single mode-flag. [developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide)
- **Spec Kit constitution.md** sets "non-negotiable principles" as a separate file the agent must consult — establishes a contract layer above task instructions. [github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)

For copy-paste prompts that drop into a fresh CLI session with no system-message channel, the established move is to **make the contract the first paragraph of the user message and phrase it imperatively**. `spec_driven`'s `# EXECUTION MODE: AUTONOMOUS` followed by "Do NOT call AskUserQuestion. For anything ambiguous, use best judgment, and record the choice inline" is exactly this pattern.

## 3. Implications for the spec (concrete, actionable)

**FR-14c — regen-prompt assembly:**
- Top-of-prompt mode header MUST be a literal first-line H1 (`# EXECUTION MODE: AUTONOMOUS` or `# EXECUTION MODE: INTERACTIVE`). Inventing this is justified — frontmatter (Cursor / Spec Kit) and structural hierarchy (Model Spec) both rely on tool-side parsers that copy-paste flows do not have. The spec should call out the rejected alternatives so the convention is not re-litigated.
- Body sections, in this order: (1) mode header, (2) one-sentence "you are running a regen of stages X, Y, Z for project P" intent line, (3) inlined `revised_prompt.md` verbatim, (4) follow-ups list — filenames + body inlined, (5) per-stage section with module checklist + invocation hint + inlined non-empty `<stage>/promoted.md` (under "Pinned items (MUST survive regeneration)"), (6) the regeneration contract from `CLAUDE.md § Regeneration semantics: read-zero from prior outputs` quoted verbatim, (7) output contract (paths, events to emit).
- No truncation. Surface a byte/line count under the prompt block. Soft-warn (yellow chip) above 100 KB; never block the copy.
- Contract phrasing for autonomous mode: imperative, addressed to "you" — matches plan-mode style. Reuse the wording from `CLAUDE.md § Regeneration prompts & autonomous mode`.

**FR-42 — Build prompt → Copy UI:**
- Inline visible block (no inner `<details>`). Bordered container; header bar with title, Wrap toggle (default ON), and Copy button. Match PatternFly / Cloudscape / Flowbite design-system conventions. (Already locked by follow-up 002.)
- Copy button visual feedback: label flips to "Copied!" for ~1.5–2 s. (Cloudscape / PatternFly converge on 2–3 s; 1.5 s in qa.md is on the short side but defensible.)
- Wrap toggle drives the textarea/`<pre>` element's CSS `white-space` (or HTML `wrap` attribute on `<textarea>`).
- Display a metadata chip near the header showing line count + byte count. If the count exceeds a configurable threshold (default 100 KB), show a yellow "Large prompt — verify your model's context window" hint. Do NOT truncate the payload; do NOT block Copy.
- Keyboard: Ctrl/⌘-C while focused inside the block should copy the entire block, not just the selection. (Aligns with PatternFly clipboard pattern.)

**Documentation:**
- The spec should include a one-paragraph rationale for the literal mode-header convention with citations to AGENTS.md, Cursor rules, and Spec Kit constitution.md, so a future contributor doesn't migrate it to frontmatter.

## 4. Open questions surfaced

1. Should the autonomous-mode header carry a *machine-readable* secondary signal (e.g. `<!-- mode: autonomous -->`) for tooling that wants to detect mode programmatically without parsing the H1? AGENTS.md ecosystem has no precedent; Cursor frontmatter would be the closest analogue. Deferred.
2. The 100 KB warn threshold is conventional but unvalidated for `spec_driven`. A real run with a large `<stage>/promoted.md` would tell us where the actual ceiling is. Defer to runtime data.
3. PatternFly recommends scroll-fade-right for inline copy; for our block variant with Wrap=ON the issue doesn't arise, but with Wrap=OFF horizontal overflow is back. Should the block also fade-right at the gutter, or rely on a plain horizontal scrollbar? Defer to FR-42 implementation review.
4. Cursor, JetBrains Junie, and Claude Code all expose autonomy via UI toggle + tool-side enforcement. `spec_driven`'s prose-only enforcement depends entirely on Claude honoring the contract when reading the H1. Worth a one-line note in the spec that this is a *trust-based* contract, not a sandbox.
