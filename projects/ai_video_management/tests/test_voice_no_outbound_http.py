"""LOAD-BEARING CARVE-OUT TEST — follow-up 115.

Voice generation is local-only by design. Any outbound-HTTP machinery
(httpx / requests / urllib / literal https URLs / dedicated voice client
files) drifting into the voice modules recreates the actor-side provider
surface that this follow-up was explicitly built to avoid (no Kling, no
JWT, no 429 retry, no SSRF, no provider env vars).

This test AST-walks each voice implementation file and grep-fails on any
import / Name / Attribute reference to a forbidden module, plus any
literal http(s) URL string. Docstrings and comments are intentionally
excluded so the *contract documentation* in module docstrings can mention
the forbidden names without tripping the test.

Severity: critical (per validation/strategy.md cross-cutting concern #7
and validation/backend_tests.md U8 row).
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]

_VOICE_FILES: tuple[Path, ...] = (
    _REPO_ROOT / "libs" / "infrastructure" / "writers" / "voice__writer.py",
    _REPO_ROOT / "libs" / "infrastructure" / "writers" / "voice__chinese_prompt.py",
    _REPO_ROOT / "libs" / "application" / "commands" / "voice__command.py",
    _REPO_ROOT / "libs" / "application" / "queries" / "voice__query.py",
    _REPO_ROOT / "libs" / "application" / "dtos" / "voice__dto.py",
    _REPO_ROOT / "libs" / "application" / "mappers" / "voice__mapper.py",
    _REPO_ROOT / "libs" / "domain" / "value_objects" / "voice__valueobject.py",
    _REPO_ROOT / "libs" / "domain" / "errors" / "voice__error.py",
    _REPO_ROOT / "libs" / "domain" / "repositories" / "voice__repository.py",
)

# Module / attribute names that, if used in real code, indicate the voice
# pool reached for outbound HTTP. Docstring mentions are fine — only Name
# and Attribute AST nodes trigger.
_FORBIDDEN_NAMES: frozenset[str] = frozenset({
    "httpx",
    "requests",
    "aiohttp",
    "urllib",
    "urlopen",
    "Request",  # urllib.request.Request — Attribute access trips on "Request"
})

# String literals that look like a real outbound URL. Allow loopback only.
_URL_RE = re.compile(r"^https?://(?!127\.0\.0\.1|localhost)[^\s]+")


class _ForbiddenVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.hits: list[tuple[int, str]] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root in _FORBIDDEN_NAMES:
                self.hits.append((node.lineno, f"import {alias.name}"))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module is not None:
            root = node.module.split(".")[0]
            if root in _FORBIDDEN_NAMES:
                self.hits.append((node.lineno, f"from {node.module} import ..."))
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        # Catch `httpx.get(...)` / `requests.post(...)` etc. (the receiver name).
        if isinstance(node.value, ast.Name) and node.value.id in _FORBIDDEN_NAMES:
            self.hits.append((node.lineno, f"{node.value.id}.{node.attr}"))
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        # Catch bare-name uses smuggled in via `from foo import requests`-style.
        if node.id in _FORBIDDEN_NAMES and isinstance(node.ctx, ast.Load):
            self.hits.append((node.lineno, f"name use: {node.id}"))
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str) and _URL_RE.match(node.value):
            self.hits.append((node.lineno, f"literal URL: {node.value[:60]}"))
        self.generic_visit(node)


def _scan(file_path: Path) -> list[tuple[int, str]]:
    text = file_path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(file_path))
    visitor = _ForbiddenVisitor()
    visitor.visit(tree)
    # Drop the implicit-docstring Constant nodes — the visitor already
    # picked them up as ast.Constant, but our URL regex only matches real
    # URL-shaped strings so docstrings ABOUT the forbidden names never
    # appear in `hits`. (Mention this here for future readers; no code
    # needed beyond `visit_Constant` already discriminating by `_URL_RE`.)
    return visitor.hits


@pytest.mark.parametrize("voice_file", _VOICE_FILES, ids=lambda p: p.name)
def test_voice_module_has_no_outbound_http(voice_file: Path) -> None:
    """Each voice module must contain ZERO references to outbound-HTTP libs."""
    assert voice_file.exists(), f"expected voice file missing: {voice_file}"
    hits = _scan(voice_file)
    if hits:
        report = "\n".join(f"  line {line_no}: {what}" for line_no, what in hits)
        pytest.fail(
            f"\n\nLOAD-BEARING CARVE-OUT VIOLATION in {voice_file.relative_to(_REPO_ROOT)}:\n"
            f"voice modules must NOT contain outbound-HTTP machinery.\n"
            f"{report}\n\n"
            f"If you genuinely need to add a voice-side network call, write a spec\n"
            f"follow-up first — this test is the contract enforcement (see\n"
            f"validation/strategy.md cross-cutting concern #7).\n"
        )


def test_voice_client_directory_does_not_exist() -> None:
    """A `libs/infrastructure/clients/voice_*.py` file would be a smoking-gun
    indicator that someone wired in a voice provider client. The clients
    subtree is where the actor-side `kling_*` would have lived; voice must
    never have a peer."""
    clients_dir = _REPO_ROOT / "libs" / "infrastructure" / "clients"
    if not clients_dir.is_dir():
        return  # No clients dir at all — nothing to assert.
    voice_clients = (
        list(clients_dir.glob("voice_*.py"))
        + list(clients_dir.glob("voice__*.py"))
    )
    assert not voice_clients, (
        f"voice client files detected — violates the no-HTTP carve-out: "
        f"{[str(p.relative_to(_REPO_ROOT)) for p in voice_clients]}"
    )
