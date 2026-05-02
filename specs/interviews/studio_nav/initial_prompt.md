# Initial prompt — studio_nav

> the spec studio should have a left nav which shows the specs for all tasks currrent just spec_studio, and under spec studio we should have a input module which shows claude.md, system prompt, user initial prompt bascially all input factor could impact the gneration of downstream intreview quesitons and specs. Another module is interivew quesitons, when user click, the right main pannel should how interview questions and answers in a beautified manner, and those are editable. Another modules would be specs, and another module is findings and then execution plan

**Captured:** 2026-04-29

**Scope (initial read):**
- Restructure `projects/spec_studio/frontend` to use a tree-style left nav listing all tasks (only `spec_studio` itself for now).
- Per task, expand into modules: **Input**, **Interview Questions**, **Specs**, **Findings**, **Execution Plan**.
- The right main panel renders the selected module.
- **New module — Input:** shows CLAUDE.md, system prompt, and the task's initial prompt (every input factor that influences generation downstream).
- **Interview module:** Q&A rendered beautifully, editable.
- **Specs / Findings / Execution Plan:** existing artifacts, also presumably editable or at minimum read-only viewers.
- Existing tabs in `TaskDetail.tsx` (Interview / Spec / Research / Adjustments / Plan / ExecuteValidate) need to be reconciled with the new module list.

**Open from prompt (for interview to resolve):**
- Should Adjustments remain its own module, fold into Input, or be dropped?
- Should Execute & Validate remain (it's a runtime view, not an artifact)?
- For "editable" — does saving an edited interview Q&A trigger spec recompilation, or does it only persist?
- Should "Input" surface a system prompt that Claude actually uses, or is "system prompt" a placeholder in the UI for whatever instruction is sent to the SDK?
- Should the left nav scroll independently from the main panel? Persist the selected module across reloads?
- Where does the "currently just spec_studio" task entry come from — is the platform itself a task in `specs/index.json`, or do we synthesize it for display?
