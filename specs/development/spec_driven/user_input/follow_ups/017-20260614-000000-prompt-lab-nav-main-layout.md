---
target_stage: 6
target_artifacts:
  - final_specs/spec.md
  - projects/spec_driven/apps/ui/src/components/PromptLabPage.tsx
severity: low
---

# Follow-up draft 017 — 2026-06-14

Restructure the Prompt Lab page (FR-43) from a full-width tile/card grid into the app's standard **left-nav + main-section** layout, matching the `ai_video_management` webapp's `Sidebar` + `main-pane` pattern.

## Abstracted instruction

The Prompt Lab overview at `/prompt-lab` currently renders categories as a grid of cards. Replace that with a two-column `app-root` layout:

- **Left nav (`.sidebar`).** A "← Home" back link, a "Prompt Lab" title with a "+ New" button, then the library as a navigable list: each category is a header, each task is a clickable item. The selected item is highlighted.
- **Main section (`.main-pane`).** Shows the selected task's detail: title, the `Stack / Est / Output` meta, the Source + Expected-result links, and the copy-paste prompt rendered in the highlighted, click-to-edit block (clicking opens the file in the reader for editing), plus Copy / Open-in-reader / Delete actions. The New-prompt form renders here when "+ New" is active. Empty state prompts the user to pick a task.

Selection is page-local state (no per-item route needed); "Open / edit" and clicking the prompt block still navigate to `/file/{path}` so the existing reader (with prompt highlight + click-to-edit) handles editing.
