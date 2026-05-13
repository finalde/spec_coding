"""Stdlib KEY=VALUE loader for backend/.env (follow-up 025).

Reads simple `KEY=VALUE` lines and `os.environ.setdefault`s them so an
already-set shell / CI env wins. No PyDotEnv dependency. Comments (`#`)
and blank lines are skipped. Quoted values are unquoted only if the
whole value is wrapped in matching single or double quotes.

Missing file → return 0 (dev-friendly; absent credentials surface later
at KlingProvider.from_env() time with a clear RuntimeError).
"""
from __future__ import annotations

import os
from pathlib import Path


def load_env_file(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return 0
    except OSError:
        return 0
    loaded = 0
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if os.environ.setdefault(key, value) is value:
            loaded += 1
    return loaded
