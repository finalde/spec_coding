---
target_stage: 6
target_artifacts:
  - final_specs/spec.md
  - projects/spec_driven/apps/ui/src/markdown/renderer.tsx
  - projects/spec_driven/apps/ui/src/components/PromptLabPage.tsx
severity: low
---

# Follow-up draft 018 — 2026-06-14

Two Prompt Lab refinements (FR-43): a one-click **Copy** button on the highlighted prompt block, and a fixed **3-section** authoring structure for task files (reflected in the new-file template).

## Abstracted instruction

1. **One-click copy.** The highlighted copy-paste prompt block (reader view + Prompt Lab detail) gets a **Copy** button that copies the prompt text to the clipboard. It must `stopPropagation` so copying does not also trigger the block's click-to-edit. (The Prompt Lab detail pane already had a "Copy prompt" button; the reader's prompt block now gets one too.)

2. **Fixed 3-section task structure.** Every `prompt_lab/` task `.md` follows a consistent order after the title + `Stack/Est/Output` meta line:
   - **✨ 1. Expectation — what you'll get** — after running the prompt, what happens, the impressive result, and the wow / innovation angle.
   - **▶️ 2. How to run** — how to run it (copy-paste-and-walk-away) + prerequisites.
   - **🔗 3. Source & references** — the `**Source:**` and `**Expected result:**` links.
   Then the `## 📋 COPY-PASTE PROMPT` block. The webapp's new-prompt template (`PromptLabPage.fileTemplate`) seeds new files with this structure. The overview parser is unchanged (it still keys on the `**Stack:**` / `**Source:**` / `**Expected result:**` lines and the first fenced block).

## Notes

- The 21 existing library files were restructured into the 3-section format (content-only edits under `prompt_lab/`; the prompt blocks + metadata were preserved verbatim so the parser output is unchanged).
