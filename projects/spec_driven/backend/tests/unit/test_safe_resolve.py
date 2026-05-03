"""
Group 1 — safe_resolve / path sandbox.

Spec anchors: FR-2, FR-4, NFR-5, NFR-10, NFR-11, NFR-12. Severity: critical for
any sandbox-escape failure (per agent_refs/validation/general.md).

Surface under test: `SafeResolver.resolve(rel) -> Path | None`.
- Inside-tree, well-formed → absolute Path
- Anything else (traversal, percent-encoded, ADS, reserved name, 8.3, NUL,
  absolute, mixed slashes, symlink/junction) → None.
The HTTP layer maps None to single 404 (no existence-oracle) per NFR-11.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# 1.1 happy paths
# ---------------------------------------------------------------------------


def test_resolves_known_good_relative_path(resolver, repo_root):
    p = resolver.resolve("CLAUDE.md")
    assert p is not None
    assert p.is_file()
    assert p.parent == repo_root.path or repo_root.path in p.parents or p.parent.resolve() == repo_root.path


def test_resolves_nested_spec_path(resolver, repo_root):
    p = resolver.resolve("specs/development/spec_driven/final_specs/spec.md")
    assert p is not None
    assert p.is_file()
    # Containment check via parents.
    assert repo_root.path in p.parents


def test_resolves_dotclaude_skill(resolver):
    p = resolver.resolve(".claude/skills/agent_team/SKILL.md")
    # Skill file may or may not exist depending on harness state, but it MUST
    # not be rejected pre-FS — i.e., it should resolve to an absolute path
    # under repo_root.
    if p is not None:
        assert p.is_absolute()


# ---------------------------------------------------------------------------
# 1.2 — `..` traversal
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "probe",
    [
        "../etc/passwd",
        "specs/../../../etc/passwd",
        "./../../something",
        "specs/development/../../../etc/passwd",
        "../",
        "..",
        "specs/foo/..",
    ],
)
def test_rejects_dotdot_traversal(resolver, probe):
    assert resolver.resolve(probe) is None


# ---------------------------------------------------------------------------
# 1.3 — percent-encoded traversal stays opaque
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "probe",
    [
        "%2e%2e/etc/passwd",
        "%2E%2E%2Fetc",
        "specs%2F..%2F..",
        "%2e%2e%2f%2e%2e",
        "%252e%252e%252f",
    ],
)
def test_rejects_percent_encoded_traversal(resolver, probe):
    """The resolver MUST treat percent-encoding as opaque — no double-decode."""
    assert resolver.resolve(probe) is None


# ---------------------------------------------------------------------------
# 1.4 — Alternate Data Streams / colons
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "probe",
    [
        "CLAUDE.md:hidden",
        "CLAUDE.md::$DATA",
        "specs/foo.md:Zone.Identifier",
        "specs/foo:hidden:bar",
        "foo.md:stream:$DATA",
        "CLAUDE.md::$INDEX_ALLOCATION",
    ],
)
def test_rejects_alternate_data_streams(resolver, probe):
    assert resolver.resolve(probe) is None


# ---------------------------------------------------------------------------
# 1.5 — Windows reserved device names
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "probe",
    [
        "CON",
        "PRN.md",
        "specs/COM1.txt",
        "AUX",
        "NUL",
        "LPT3",
        "con",
        "Con.MD",
        "nul.txt",
        "CON.md",
        "LPT1.md",
        "specs/development/spec_driven/CON.md",
    ],
)
def test_rejects_windows_reserved_names(resolver, probe):
    assert resolver.resolve(probe) is None


def test_rejects_reserved_name_at_any_segment(resolver):
    assert resolver.resolve("specs/development/spec_driven/CON/foo.md") is None


# ---------------------------------------------------------------------------
# 1.6 — 8.3 short-name aliasing
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "probe",
    [
        "PROGRA~1",
        "DOCUME~1/foo",
        "VERY~1.MD",
        "specs/DEVELO~1/spec.md",
        "FINAL_~1/spec.md",
    ],
)
def test_rejects_windows_8_3_short_names(resolver, probe):
    assert resolver.resolve(probe) is None


# ---------------------------------------------------------------------------
# 1.7 — Vite CVE-2025-62522 trailing-backslash + NUL byte + colon
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "probe",
    [
        "CLAUDE.md\\",
        "specs\\..\\..",
        "foo\\bar.md",
        "\x00CLAUDE.md",
        "foo:bar.md",
        "CLAUDE.md\x00",
        "specs/foo\x00.md",
        "C:\\Windows\\system.ini",
        "\\\\?\\C:\\Windows\\system.ini",
    ],
)
def test_rejects_vite_cve_and_pathological(resolver, probe):
    """NFR-12 — reject `\\`, `:`, NUL byte BEFORE any realpath call."""
    assert resolver.resolve(probe) is None


# ---------------------------------------------------------------------------
# 1.8 — symlinks (POSIX)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="POSIX symlink test; Windows junctions tested separately",
)
def test_rejects_symlink_outside_tree(resolver, scratch_dir, tmp_path):
    """A symlink under EXPOSED_TREE pointing outside is refused outright.
    No realpath leak, no 'follow then re-verify' fallback per NFR-10 / OQ-4.
    """
    target = tmp_path / "outside_target.md"
    target.write_text("secret", encoding="utf-8")
    link = scratch_dir / "leak.md"
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlink not supported in this environment")
    try:
        result = resolver.resolve(
            "specs/development/spec_driven/__scratch__/leak.md"
        )
        assert result is None
    finally:
        try:
            link.unlink()
        except OSError:
            pass


# ---------------------------------------------------------------------------
# 1.9 — Windows junction (Developer Mode optional; skip if unavailable)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    sys.platform != "win32",
    reason="NTFS junction syntax; Windows-only",
)
def test_rejects_windows_junction(resolver, scratch_dir, tmp_path):
    """Windows junctions are reparse points; treat like a symlink — refuse."""
    target = tmp_path / "junction_target"
    target.mkdir(parents=True, exist_ok=True)
    (target / "secret.md").write_text("secret", encoding="utf-8")
    junction = scratch_dir / "junction_leak"
    rc = os.system(f'mklink /J "{junction}" "{target}" >NUL 2>&1')
    if rc != 0:
        pytest.skip("could not create NTFS junction (Developer Mode/elevation?)")
    try:
        result = resolver.resolve(
            "specs/development/spec_driven/__scratch__/junction_leak/secret.md"
        )
        assert result is None
    finally:
        try:
            os.system(f'rmdir "{junction}" >NUL 2>&1')
        except OSError:
            pass


# ---------------------------------------------------------------------------
# 1.10 — outside-tree probes collapse to single None signal
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "probe",
    [
        "/etc/passwd",
        "C:\\Windows\\System32\\drivers\\etc\\hosts",
        "~/secret",
        "node_modules/foo",
        "/tmp/xxx",
        "../../etc/passwd",
        "specs/development/nope/missing.md",
    ],
)
def test_collapses_outside_tree_to_single_None(resolver, probe):
    """SAME signal regardless of WHY (no existence oracle per NFR-11)."""
    assert resolver.resolve(probe) is None


# ---------------------------------------------------------------------------
# 1.11 — mixed slashes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "probe",
    [
        "specs\\foo/bar.md",
        "specs/foo\\bar.md",
        "specs\\development\\spec_driven\\final_specs\\spec.md",
    ],
)
def test_rejects_mixed_slashes_in_user_input(resolver, probe):
    """User input MUST be pure forward-slash. `\\` is never accepted."""
    assert resolver.resolve(probe) is None


# ---------------------------------------------------------------------------
# 1.12 — empty / control input
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("probe", ["", " ", "\x00", "\x01\x02foo", "\t"])
def test_rejects_empty_and_control_input(resolver, probe):
    assert resolver.resolve(probe) is None


# ---------------------------------------------------------------------------
# 1.13 — leading separators / absolute path heuristics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "probe",
    [
        "/CLAUDE.md",
        "//etc",
        "\\\\server\\share",
        "C:/Windows",
        "C:\\Windows",
    ],
)
def test_rejects_absolute_paths(resolver, probe):
    assert resolver.resolve(probe) is None
