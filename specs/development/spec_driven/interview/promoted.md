# Promoted items — interview

INPUT to regeneration. Items here MUST appear verbatim in the regenerated artifact. Managed via the 📌 toggle in the spec_driven webapp; remove only by manual delete or unpin.

See `CLAUDE.md → ## Regeneration prompts & autonomous mode → ### Regeneration semantics → ### Pinned items survive regeneration` for the contract.

## pin-001 — interview/qa.md / Round 1 (interactive, AskUserQuestion) / functional-scope

**Q:** Section 2 ("Projects") — which projects appear in the tree?
- A: All discovered (Recommended) — backend walks `specs/{type}/{name}/` for every type+name pair on disk; show all. `spec_driven` is just the first; `ai_video` etc. appear automatically when present.
