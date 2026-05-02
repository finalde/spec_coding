from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from libs.safe_resolve import OutsideSandbox, SymlinkRefused, safe_resolve


def test_clean_relative_path_returns_relative(fake_repo: Path) -> None:
    rel = "specs/development/spec_driven/final_specs/spec.md"
    out = safe_resolve(rel, fake_repo)
    assert out == Path("specs/development/spec_driven/final_specs/spec.md")


def test_dotdot_traversal_rejected(fake_repo: Path) -> None:
    with pytest.raises(OutsideSandbox):
        safe_resolve("../../etc/hosts", fake_repo)


def test_posix_absolute_path_rejected(fake_repo: Path) -> None:
    with pytest.raises(OutsideSandbox):
        safe_resolve("/etc/passwd", fake_repo)


def test_double_encoded_dotdot_does_not_bypass(fake_repo: Path) -> None:
    out = safe_resolve("%252e%252e/secret", fake_repo)
    assert ".." not in out.parts


def test_empty_path_rejected(fake_repo: Path) -> None:
    with pytest.raises(OutsideSandbox):
        safe_resolve("", fake_repo)


def test_leading_slash_rejected(fake_repo: Path) -> None:
    with pytest.raises(OutsideSandbox):
        safe_resolve("/specs/development/spec_driven/final_specs/spec.md", fake_repo)


def test_embedded_nul_rejected(fake_repo: Path) -> None:
    with pytest.raises(OutsideSandbox):
        safe_resolve("specs/development/spec_driven/final_specs/spec.md\x00.png", fake_repo)


def test_dotfile_inside_exposed_tree_resolves(fake_repo: Path) -> None:
    out = safe_resolve(".claude/agents/agent_team__interview_manager.md", fake_repo)
    assert out == Path(".claude/agents/agent_team__interview_manager.md")


def test_drive_letter_rejected(fake_repo: Path) -> None:
    with pytest.raises(OutsideSandbox):
        safe_resolve("C:/Windows/System32/config", fake_repo)


def _can_create_symlink(tmp_path: Path) -> bool:
    src = tmp_path / "_probe_src"
    dst = tmp_path / "_probe_dst"
    src.write_text("x", encoding="utf-8")
    try:
        os.symlink(str(src), str(dst))
    except (OSError, NotImplementedError):
        return False
    return True


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="symlinks require admin/dev mode on Windows",
)
def test_symlink_rejected_even_inside_tree(fake_repo: Path) -> None:
    if not _can_create_symlink(fake_repo):
        pytest.skip("cannot create symlinks in this environment")
    target = fake_repo / "specs" / "development" / "spec_driven" / "final_specs" / "spec.md"
    link = (
        fake_repo
        / "specs"
        / "development"
        / "spec_driven"
        / "final_specs"
        / "linked.md"
    )
    os.symlink(str(target), str(link))
    with pytest.raises(SymlinkRefused):
        safe_resolve("specs/development/spec_driven/final_specs/linked.md", fake_repo)
