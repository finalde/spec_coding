"""
Group 1 — safe_resolve probes (FR-3, FR-4, AC-3..AC-6).
"""

from __future__ import annotations

import sys

import pytest

from libs.safe_resolve import OutsideTreeError


def test_happy_path(resolver):
    p = resolver.resolve("specs/development/spec_driven/final_specs/spec.md")
    assert p.exists()


def test_happy_path_claude_md(resolver):
    p = resolver.resolve("CLAUDE.md")
    assert p.exists()


def test_happy_path_dotslash_prefix(resolver):
    p = resolver.resolve("./CLAUDE.md")
    assert p.exists()


def test_happy_path_mixed_separators(resolver):
    p = resolver.resolve("specs\\development/spec_driven/final_specs/spec.md")
    assert p.exists()


@pytest.mark.parametrize(
    "probe",
    [
        "../etc/passwd",
        "specs/../../etc/passwd",
        "specs/development/../../../etc/passwd",
        "specs/./../../etc/passwd",
        "..\\etc\\passwd",
        "specs\\..\\..\\etc\\passwd",
    ],
)
def test_rejects_traversal(resolver, probe):
    with pytest.raises(OutsideTreeError):
        resolver.resolve(probe)


@pytest.mark.parametrize(
    "probe",
    [
        "/etc/passwd",
        "C:\\Windows\\System32\\drivers\\etc\\hosts",
        "C:/Windows/system.ini",
        "\\\\?\\C:\\Windows\\system.ini",
        "//?/C:/Windows/system.ini",
        "\\\\server\\share\\file",
    ],
)
def test_rejects_absolute_paths(resolver, probe):
    with pytest.raises(OutsideTreeError):
        resolver.resolve(probe)


@pytest.mark.parametrize(
    "probe",
    [
        "specs/development/spec_driven/final_specs/spec.md::$DATA",
        "specs/development/spec_driven/final_specs/spec.md:hidden",
        "specs/development/spec_driven/final_specs/spec.md:hidden:$DATA",
        "specs/foo::$DATA/bar",
    ],
)
def test_rejects_alternate_data_streams(resolver, probe):
    with pytest.raises(OutsideTreeError):
        resolver.resolve(probe)


@pytest.mark.parametrize(
    "name",
    [
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM9",
        "LPT1",
        "LPT9",
        "CON.md",
        "Con.MD",
        "nul.txt",
        "lpt5.json",
    ],
)
def test_rejects_windows_reserved_names(resolver, name):
    with pytest.raises(OutsideTreeError):
        resolver.resolve(f"specs/development/spec_driven/{name}")


def test_rejects_reserved_names_at_any_depth(resolver):
    with pytest.raises(OutsideTreeError):
        resolver.resolve("specs/development/spec_driven/CON/foo.md")


@pytest.mark.parametrize(
    "probe",
    [
        "PROGRA~1/foo.md",
        "specs/DEVELO~1/spec.md",
        "FINAL_~1/spec.md",
    ],
)
def test_rejects_8_3_short_names(resolver, probe):
    with pytest.raises(OutsideTreeError):
        resolver.resolve(probe)


def test_allows_legitimate_tilde_names(resolver, scratch_dir):
    """Filenames containing ~ but not in 8.3 form must be allowed."""
    fixture = scratch_dir / "notes~v2.md"
    fixture.write_text("ok", encoding="utf-8")
    try:
        p = resolver.resolve("specs/development/spec_driven/__scratch__/notes~v2.md")
        assert p.exists()
    finally:
        fixture.unlink()


@pytest.mark.parametrize(
    "probe",
    [
        "specs/development/\x00etc/passwd",
        "specs/\x01\x02foo",
        "\x00",
    ],
)
def test_rejects_control_chars(resolver, probe):
    with pytest.raises(OutsideTreeError):
        resolver.resolve(probe)


def test_rejects_empty_path(resolver):
    with pytest.raises(OutsideTreeError):
        resolver.resolve("")


def test_canonicalizes_first_then_asserts_containment(resolver):
    """`..` that cancels and lands inside the tree is allowed."""
    p = resolver.resolve("specs/development/../development/spec_driven/final_specs/spec.md")
    assert p.exists()


@pytest.mark.skipif(sys.platform != "win32", reason="POSIX FS is case-sensitive; case-folding is Windows-specific")
def test_case_folding_on_ntfs(resolver):
    p = resolver.resolve("Specs/Development/Spec_Driven/Final_Specs/Spec.md")
    assert p.exists()
