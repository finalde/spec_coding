# Follow-up draft 002 — 2026-05-05

ai_video_management must be unaware of `CLAUDE.md`, `.claude/`, and `specs/` even at internal-anchor level. Backend code should not read or reference those files for any purpose.

## Original wording

> backend should not read those files either, the whole ai_video_management system should not aware the existence of specs and claude settings, it is none of its business

## Abstracted intent

Follow-up 001 hid `specs/`, `CLAUDE.md`, `.claude/` from the user-facing tree but left `backend/libs/repo_root.py` walking up the directory tree looking for `CLAUDE.md + .claude/` as anchor markers. The user wants that internal coupling removed too. **Zero references to those paths anywhere in `projects/ai_video_management/` source code.**

Concrete deltas:

1. **Anchor strategy switches to `ai_videos/` directory presence.** `RepoRoot.find()` walks up looking for a directory containing `ai_videos/` as a child. The parent of that match is the workspace root. If no `ai_videos/` is found anywhere up the tree, raise a clear error.
2. **All inline comments referencing `CLAUDE.md`, `.claude/`, or `specs/`** in source are rewritten to talk about `ai_videos/` (or removed where they were just historical notes about follow-up 001).
3. **README and docstrings** in code drop all mentions of `CLAUDE.md`, `.claude/`, `specs/` and `spec_driven`. The webapp's documentation is self-contained.
4. **Tests' `conftest.repo_root()` helper** stops walking up looking for `CLAUDE.md + .claude/`; switches to the same `ai_videos/`-based anchor.

The webapp must be a true black box: drop it under any folder that contains `ai_videos/` as a sibling, run it, and it works. Any other directory layout choices are not its concern.

## Why

Hard separation of concern. `ai_video_management` manages `ai_videos/` artifacts; that is its full surface area. Knowing about `CLAUDE.md`, `.claude/`, or `specs/` — even just as anchor markers — is leakage. After this follow-up, grep-ing the codebase for those literal strings should return nothing.

## Out of scope

- The `specs/development/ai_video_management/` directory under the workspace's spec-pipeline tree continues to exist (this is the agent_team workflow's audit trail, written by Claude Code, not by the webapp itself). The webapp simply does not read it.
- The CLAUDE.md / .claude/ files in the workspace continue to exist (they govern Claude Code behavior, not the webapp). The webapp simply does not read them.
- spec_driven (port 8765) keeps its own anchor strategy unchanged; only ai_video_management is affected.
