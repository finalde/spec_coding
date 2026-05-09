# Follow-up draft 011 — 2026-05-06

Two coupled fixes for follow-up 010's parent-level delete:

1. **Bug — 405 in prod mode, validation gap.** User reports `DELETE /api/project` returns 405 in prod mode (`make run-prod`). Root cause: the static-files mount at `/` (with `html=True`) catches DELETE requests for any path that doesn't match a route, and `StaticFiles` returns 405 because it only supports `GET` / `HEAD`. This manifests when the backend is running old code (without the `/api/project` route registered) — but the unit tests in 010 use `serve_static=False`, so they never exercise the route-vs-static-mount interaction. The 405 was never going to be caught by my added tests.
2. **Scope expansion — generic delete.** User wants delete to work for `task_type=development` too, not just `ai_video`. Output-path mapping per task type: `ai_video` → `ai_videos/{name}/`; `development` → `projects/{name}/`.

## Original wording

> when I click delete, it gives me "Delete failed (405): Method Not Allowed", help me find out why this is not captured by validatoin, also make this delete feature a generic feature which means also applies to development project and all projects under spec_driven

## Concrete deltas

**Backend `libs/project_deleter.py`:**

- `ALLOWED_TASK_TYPES_FOR_DELETE`: `{"ai_video", "development"}` (was `{"ai_video"}`).
- New `_TASK_TYPE_TO_OUTPUT_DIR: dict[str, str]` mapping: `{"ai_video": "ai_videos", "development": "projects"}`. `delete()` reads this to compute the output path instead of hardcoding `ai_videos/`.
- Defense-in-depth path-resolution check broadened to admit `specs/` plus all output dirs in the mapping (`{"ai_videos", "projects"}`). Anything not in those two top-level dirs is rejected as `InvalidProjectName`.
- The dangerous-self-delete carve-out: `task_type=development` + `project_name=spec_driven` is **rejected** with a new `SelfDeleteRefused` exception → HTTP 400 — this is the running webapp; deleting it from the UI would self-immolate the process while it's serving the deletion response.

**Backend `libs/api.py`:**

- Add `pd.SelfDeleteRefused` to the exception handler chain → `400 {"detail": {"kind": "self_delete_refused"}}`.
- No other changes (endpoint already takes arbitrary `project_type` and delegates).

**Frontend `components/ProjectPage.tsx`:**

- Remove the `projectType === "ai_video"` gate; the danger zone now renders for any `task_type`.
- Output-path label in the confirm dialog must reflect the actual target dir per task type (`projects/{name}/` for development, `ai_videos/{name}/` for ai_video). Resolved client-side via the same task-type → output-dir mapping.
- Add a special-case warning when the user is on `/project/development/spec_driven` — the delete button is **disabled** and a help text explains "this is the running webapp; deletion not allowed via UI".

**Frontend `types.ts` + `api.ts`:**

- Relax `ProjectDeleteRequest.project_type` from `"ai_video"` literal to `"ai_video" | "development"`.

**Backend test — close the validation gap:**

- New test `test_delete_endpoint_routed_correctly_in_prod_mode` with `serve_static=True` (production-mode client). Verifies `DELETE /api/project` reaches the FastAPI handler (returns 200/400/404 depending on body) and is NOT captured by the static-files mount returning 405. **This test fails if someone removes or shadows the `/api/project` route in the future.** Same shape required for any new state-changing endpoint going forward.
- New parametrized tests for `task_type=development`: synthetic-project full delete (specs/development/{name}/ + projects/{name}/), partial delete (only specs side present), self-delete refused (development/spec_driven → 400 with `self_delete_refused` kind).

**Validation patch — close the rule gap:**

- `agent_refs/validation/development.md` move #1 (multi-mode parity): add a clarifying sub-clause that "any new state-changing endpoint MUST have at least one integration test with `serve_static=True` (or the project's prod-mode equivalent), not just `serve_static=False`. Otherwise the static-files mount can shadow the endpoint in prod and the test suite won't catch it." This is a class-of-failure rule, not a project-specific patch — applies to every development-task project that ships a prod-mode + dev-mode runtime split.
- This is exactly the class of rule promotion that move #1 already exists for (originated from spec_driven-006 and -20260502-clean); appending a sub-clause is surgical, not a rewrite.

## Why the unit tests didn't catch it

`backend/tests/conftest.py::app` fixture: `create_app(serve_static=False)`. Every test using the `client` fixture goes through this — the static mount is never active. So:

- A correctly-registered route → handler runs → 200/400/404. (Tests pass.)
- A route that's accidentally missing or shadowed in prod → no static mount in test mode → FastAPI returns 404 (route not found). (Tests would also pass on the wrong outcome — 404 is the same status the test asserts.)

In production with `serve_static=True`:

- Correctly-registered route → handler runs → 200/400/404. (Works.)
- Route missing or shadowed → static mount catches → 405 for non-GET methods. (Bug surfaces only here.)

The fix is a single regression test that asserts the route is reachable when the static mount is active. It's a 5-line test; the principle should be canonized in `agent_refs/validation/development.md` so future endpoints don't fall into the same gap.

## Scope-discipline note

User's phrase "all projects under spec_driven" is interpreted as "all `task_type`s that the spec_driven webapp manages" → `ai_video` + `development`. NOT as "any path under `projects/spec_driven/`" (which would be the webapp's own source — different beast).

## Out of scope

- Bulk delete (multi-project select).
- Trash/undo.
- Deleting non-canonical task types (anything other than `ai_video` and `development` continues to 400 with `unsupported_task_type`).
- Deleting the running spec_driven webapp itself (refused with `self_delete_refused`).
