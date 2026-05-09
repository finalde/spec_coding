# Follow-up draft 010 — 2026-05-06

Add parent-level project delete to `spec_driven`, scoped to `task_type=ai_video` only.

## Original wording

> lets add a new functionality to spec_driven, ai_video type only, which is a parent level delete, for example, I could delete a entire project under ai_video on UI, and then it will help me remove all the sub folders, files and content for me

## Abstracted intent

When the user navigates to an ai_video project in the spec_driven sidebar (e.g., `specs/ai_video/wukong_juexing/`), expose a "Delete project" affordance on the ProjectPage that removes the project end-to-end:

1. `specs/ai_video/{project_name}/` — the spec-pipeline trail (intake, interview, findings, final_specs, validation, follow_ups, changelog).
2. `ai_videos/{project_name}/` — the generated output artifacts (character bibles, prompts, publish, etc.).

Both deletions are recursive (`rm -rf`-equivalent). Any sub-folders, files, and content are wiped.

**Scope-limit: ai_video task_type only.** A `task_type=development` project deletion would also wipe `projects/{name}/` (a much larger blast radius — code, tests, build output) and isn't in scope of this follow-up. The endpoint must reject `project_type != "ai_video"` with 400.

## Concrete deltas

**Backend:**

- New `backend/libs/project_deleter.py` module with strict slug validation (regex `^[a-zA-Z0-9_][a-zA-Z0-9_-]*$`), task-type guard, dual-path target computation, and `shutil.rmtree`-equivalent deletion. Refuses if the project doesn't exist (404) or path traversal slips through (404).
- New `DELETE /api/project` endpoint: body `{project_type: "ai_video", project_name: str}`. Returns 200 with `{deleted_paths: [...]}` on success.
- Add `("DELETE", "/api/project")` to `api_security.py` `GUARDED_ROUTES` — confirmation must come from the same Origin/Host as the rest of the webapp.
- Audit event: emit a `project.deleted` line to `events.jsonl` with the project name + paths removed + timestamp.

**Frontend:**

- New `deleteProject` call in `api.ts`.
- "Delete project" button on `ProjectPage.tsx`, gated on `projectType === "ai_video"`. Two-step confirmation:
  1. Click "Delete project" → confirmation dialog showing both paths that will be removed + a "Type the project name to confirm" input.
  2. On confirm: call `DELETE /api/project`, on success navigate to `/` + refresh tree.
- Disable the button on non-ai_video pages (or hide entirely) so a `task_type=development` project page has no surprise destructive option.
- Toast / banner confirming deletion + listing what was removed.

**Security:**

- Slug regex MUST reject `..`, `/`, `\`, leading `.`, drive letters, percent-encoding.
- Origin/Host gate active (added to `GUARDED_ROUTES`).
- Endpoint refuses `project_type != "ai_video"` with 400 — destructive operation must NOT be reachable for development task type until that scope is explicitly added.
- Workspace-relative path computation (no absolute paths in body) — server resolves `specs/ai_video/{slug}/` and `ai_videos/{slug}/` itself.

**Tests:**

- Slug validation unit tests (path traversal, special chars, empty, uppercase, …).
- Origin/Host 403 when delete is sent from foreign origin.
- 400 when `project_type != "ai_video"`.
- 404 when project doesn't exist.
- 200 + confirmed deletion when project exists (use a temp-fixture project).

## Out of scope

- Trash / undo. Deletion is permanent.
- Soft-delete with a `__trash__/` folder.
- Bulk delete (multi-select of projects).
- Development-task delete (different blast radius — would need a separate follow-up).
- Editing the spec_driven sidebar to surface a delete button per node directly (clutters the tree; ProjectPage button is enough).

## Why now

The user has been iterating on `wukong_juexing` as the v1 ai_video project; they'll want to clean it up and start fresh on a different IP without manually `rm -rf`-ing two directories. A UI affordance with confirmation prevents accidental command-line typos and gives a consistent audit trail via `events.jsonl`.
