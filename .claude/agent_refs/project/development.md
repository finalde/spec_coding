# Project refs — `task_type=development`

Cross-cutting rules about the outputs of every development-task project (`projects/{name}/`). Loaded when the current task has `task_type=development`. Per `CLAUDE.md` § Stage playbooks and reference docs: this file overrides `project/general.md`; the per-project spec under `specs/development/{name}/` overrides this file for that one project (with a divergence note).

## Rules

### 1. UI theme: light only on app chrome

All webapps under `projects/` ship a **light theme** for app chrome — every surface the user navigates and clicks: `body`, sidebars / navigators, toolbars, panels, buttons, form controls, table chrome, breadcrumbs.

**Implementation:**
- `:root { color-scheme: light; }` exclusively. Do NOT include `dark`.
- NO `@media (prefers-color-scheme: dark) { ... }` block targeting app-chrome surfaces. The rule forbids OS-driven dark-mode toggling of chrome, NOT dark color anywhere on the page.

**Carve-outs (allowed dark surfaces):**
Intentional dark surfaces *inside* an otherwise-light UI are permitted when:
- The spec calls for them (e.g., a syntax-highlighted `<pre>`, a code-view panel, a regen-prompt assembled-output panel).
- Contrast meets WCAG AA against foreground colors.
- They are NOT triggered by `prefers-color-scheme: dark` — the dark palette is the unconditional default for that element, not an OS-toggled override.

Concrete `spec_driven` example: `<pre>` blocks inside `.regen-prompt-block`, `.markdown-view pre`, `.code-view pre` ship with a fixed dark palette regardless of OS theme — fine. NOT fine: wrapping `body { background: #fff; }` in `@media (prefers-color-scheme: light)` with a dark counterpart.

**Severity:** generated frontend with `prefers-color-scheme: dark` overrides on `body` / sidebar / toolbar / panels / buttons = `blocker` at stage 5. Fix: delete the dark `@media` block, not add a user toggle.

**v1 out of scope:** user-toggleable theme picker. If a future follow-up adds one, this rule will be revised here, not bypassed.

*(Originated from follow-up 004 of run `spec_driven`; relocated from `CLAUDE.md` to this file by follow-up 005.)*

## Update protocol

Surgical: one new rule per lesson, citing the source run / follow-up. When a class of cross-project regression surfaces (analogous to API-shape-drift in `validation/development.md`), promote the prevention rule here rather than embedding in any single project's spec.
