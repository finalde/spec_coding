# Follow-up draft 066 — 2026-05-17

Bugfix to follow-up 065's routes-split: `apps/api/main.py` and `apps/api/asgi.py` still imported `create_app` from the legacy `apps.api.routes` location, which now resolves to the per-aggregate routes **package** rather than the module that used to export `create_app`.

## Symptom

```
$ make run-backend
python -m apps.api.main
Traceback (most recent call last):
  ...
  File "C:\workspace\spec_coding\projects\ai_video_management\apps\api\main.py", line 13, in <module>
    from apps.api.routes import create_app
ImportError: cannot import name 'create_app' from 'apps.api.routes' (.../apps/api/routes/__init__.py)
```

## Root cause

Follow-up 051 introduced `apps/api/app_factory.py` as the new home for `create_app`. Follow-up 065's route-split pre-turn recovery updated `tests/conftest.py` + `tests/test_*.py` to import from the new location but missed the same import sites in `apps/api/main.py` + `apps/api/asgi.py`. Pytest passed (it uses `tests/conftest.py:make_app` which already pointed at the right place), so the regression slipped through.

## Fix

Both files: `from apps.api.routes import create_app` → `from apps.api.app_factory import create_app`. Single-line edit per file; no other changes.

## Out of scope

- Adding a smoke test for `python -m apps.api.main --no-reload` (would catch this class of regression at pytest time, but stays a follow-up of its own).
- HTTP route paths + JSON shapes (byte-identical).

## Acceptance trigger

- `python -m apps.api.main --no-reload` boots without ImportError (or, equivalently, `import apps.api.main` + `import apps.api.asgi` cold-import cleanly).
- Pytest baseline unchanged: 18 pass / 5 pre-existing wukong fixture failures.
