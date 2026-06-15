---
target_stage: 6
target_artifacts:
  - final_specs/spec.md
  - projects/spec_driven/apps/ui/src/components/PromptLabPage.tsx
severity: medium
---

# Follow-up draft 019 — 2026-06-14

Bug fix (FR-43): opening/editing a Prompt Lab task must stay **inside** the Prompt Lab page (its own category nav + main pane), not navigate to the global `/file/{path}` route — which renders the spec project's sidebar and a mismatched layout.

## Symptom

From `/prompt-lab`, clicking the prompt block ("click to edit") or "Open / edit" called `navigate('/file/prompt_lab/...')`. That route is served by the app's main layout (spec `Sidebar` + `Reader`), so the left nav and main pane switched to the unrelated Specs file-tree context — "totally wrong" nav + main.

## Fix

The Prompt Lab page now views and edits the selected task **inline** in its own `.main-pane`, keeping the category nav fixed:

- Selecting a task fetches its full content (`GET /api/file`) and renders it with the existing `Renderer` (so the highlighted prompt block + Copy button + click-to-edit are preserved).
- A small detail toolbar offers ✎ Edit and Delete. ✎ Edit (and clicking the prompt block) swaps the rendered view for the existing `Editor` component, saving via `PUT /api/file` with the same `If-Unmodified-Since` concurrency guard and 409 conflict handling as the reader.
- Creating a new prompt selects it and opens the inline editor — no navigation.

No navigation to `/file/...` happens from the Prompt Lab page anymore. (The global `/file/prompt_lab/...` route still works for direct deep-links and keeps its "← Prompt Lab" back button.)
