# Project-level refs — `task_type=development`

This file is **required pre-reading** at the start of every coordinated stage (2, 3, 5) and at every stage-6 work unit when the current task has `task_type=development`. It captures cross-cutting rules that apply to the *outputs* of every development-task project (everything under `projects/{name}/`), regardless of which specific project is being worked on.

The parent (Claude in the `agent_team` skill) MUST consult this file when generating spec language, validation strategy, or implementation code for a development-task project. The parent records the absolute path it read in the `pre_reading_consulted` array on the run's stage-start event in `events.jsonl`, alongside `general.md` and the stage's own refs.

When a rule in this file conflicts with `general.md`, this file wins. When a rule conflicts with a project-specific spec under `specs/development/{name}/`, the spec wins for that project — but the spec author should question whether the divergence is intentional, and if so, document why.

## Rules

### 1. UI theme: light only on app chrome

All webapps under `projects/` default to a **light theme** for app chrome — every surface the user navigates and clicks: `body`, sidebars / navigators (`aside.sidebar`, `nav`, ...), toolbars (`.toolbar`, header bars), panels (`.regen-panel`, dialogs, drawers), buttons, form controls (inputs, selects, checkboxes, textareas), table chrome, breadcrumbs.

**Specific implementation requirements:**

- The `:root` `color-scheme` property MUST be `light;` exclusively. Do NOT include `dark` (i.e., do NOT set `color-scheme: light dark;`).
- The stylesheet MUST NOT include any `@media (prefers-color-scheme: dark) { ... }` block that targets app-chrome surfaces. The rule is "no OS-driven dark-mode toggling of the surrounding chrome," not "no dark color anywhere on the page."

**Carve-outs (allowed dark surfaces):**

Intentional dark surfaces *inside* an otherwise-light UI are permitted when:

- The spec calls for them (e.g., a syntax-highlighted `<pre>` code block, a code-view panel, a regen-prompt assembled-output panel).
- Their contrast meets WCAG AA against the foreground colors used inside them.
- They are **not** triggered by `prefers-color-scheme: dark`. The dark palette is the unconditional default for that specific element, not an OS-toggled override.

Concrete example from `spec_driven`: `<pre>` blocks inside `.regen-prompt-block`, `.markdown-view pre`, and `.code-view pre` ship with a fixed dark palette (`#0d1117` / `#c9d1d9` / `#161b22`) regardless of OS theme. This is fine. What is NOT fine is wrapping `body { background: #fff; }` in `@media (prefers-color-scheme: light)` and providing a dark counterpart in `@media (prefers-color-scheme: dark)` — that pattern is forbidden on chrome.

**Why this rule exists:** cross-project user preference. The user works on light-themed dev environments and finds OS-driven dark-mode flips on app chrome jarring. By making the rule a project-level ref rather than a per-spec FR/NFR, every webapp the spec-driven workflow produces inherits it without each spec having to re-derive the constraint. (Originated from follow-up 004 of run `spec_driven`; relocated to this file by follow-up 005 of run `spec_driven`.)

**Severity for stage-5 strategy:** if a project's spec or generated frontend includes `prefers-color-scheme: dark` overrides on `body` / sidebar / toolbar / panels / buttons, that's a `blocker` issue at validation. The fix is to delete the dark `@media` block, not to add a user-facing toggle.

**v1 explicitly out of scope:** a user-toggleable theme picker. Webapps stay light-only at the chrome level. If a future follow-up adds a theme picker, this rule will be revised here, not bypassed.

## Update protocol

- Surgical updates only — one new rule, one new clarification, one new severity row at a time.
- Cite the source: which follow-up of which run introduced or refined the rule.
- When a development-task validation run discovers a class of cross-project regression (analogous to the API-shape-drift class in `validation/development.md`), promote the prevention rule into this file rather than embedding it in any single project's spec.
- This file is NOT a replacement for the per-project spec — project-specific FRs / NFRs / ACs still live under `specs/development/{name}/`. This file is for rules that span ALL development-task projects.
