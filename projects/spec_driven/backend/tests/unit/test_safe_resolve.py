from __future__ import annotations

from pathlib import Path

import pytest

from libs.safe_resolve import OutsideSandbox, SymlinkRefused, safe_resolve


def test_safe_resolve_inside_sandbox(fake_repo: Path) -> None:
    result = safe_resolve("CLAUDE.md", fake_repo)
    assert result == (fake_repo / "CLAUDE.md").resolve()


def test_safe_resolve_dot_dot_traversal(fake_repo: Path) -> None:
    with pytest.raises(OutsideSandbox):
        safe_resolve("../../../etc/hosts", fake_repo)


def test_safe_resolve_absolute_path_in_sandbox(fake_repo: Path) -> None:
    target = fake_repo / "CLAUDE.md"
    with pytest.raises(OutsideSandbox):
        safe_resolve(str(target.resolve()), fake_repo)


def test_safe_resolve_empty(fake_repo: Path) -> None:
    with pytest.raises(OutsideSandbox):
        safe_resolve("", fake_repo)


def test_safe_resolve_null_byte(fake_repo: Path) -> None:
    with pytest.raises(OutsideSandbox):
        safe_resolve("CLAUDE.md\x00../../etc/hosts", fake_repo)


def test_safe_resolve_dot_is_root(fake_repo: Path) -> None:
    assert safe_resolve(".", fake_repo) == fake_repo.resolve()


def test_safe_resolve_unc_path(fake_repo: Path) -> None:
    with pytest.raises(OutsideSandbox):
        safe_resolve("\\\\server\\share\\hosts", fake_repo)


def test_safe_resolve_mixed_slashes(fake_repo: Path) -> None:
    rel = "specs/development/spec_driven/final_specs/spec.md"
    expected = (fake_repo / "specs" / "development" / "spec_driven" / "final_specs" / "spec.md").resolve()
    assert safe_resolve(rel, fake_repo) == expected


def test_safe_resolve_symlink(fake_repo: Path, tmp_path: Path) -> None:
    target = fake_repo / "CLAUDE.md"
    link = fake_repo / "specs" / "development" / "spec_driven" / "final_specs" / "claude_link.md"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not permitted on this platform")
    rel = "specs/development/spec_driven/final_specs/claude_link.md"
    with pytest.raises(SymlinkRefused):
        safe_resolve(rel, fake_repo)
