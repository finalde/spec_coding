# Follow-up draft 152 — 2026-06-27
Downloads import: unmatched files are not imported at all (no `not_matched/` dumping ground).

---
target_stage: 6
target_artifacts:
  - libs/infrastructure/writers/downloads__writer.py
severity: medium
---

The Downloads importer previously moved any file it could not route to a
`not_matched/` (drama) or `_not_matched/` (performances / actors / bgm)
sub-folder for manual triage. Change the behavior across ALL importer entry
points (`import_drama`, `import_performances`, `import_actors`, `import_bgms`):

- An unmatched download is **NOT imported at all** — it is left untouched in the
  user's Downloads folder.
- It is still **reported** in the result's `unmatched` list (kind `"unmatched"`,
  carrying only `from`, no `to`) so the UI count is unchanged.
- No `not_matched/` / `_not_matched/` folder is ever created.

Also delete the existing `ai_videos/wushen_juexing/not_matched/` folder and its
contents (stale triage leftovers).
