from __future__ import annotations

from pathlib import Path

import pytest

from libs.repo_root import RepoRootNotFound, discover_repo_root


def test_discover_repo_root_at_root(fake_repo: Path) -> None:
    assert discover_repo_root(fake_repo / "specs" / "development" / "spec_driven" / "final_specs" / "spec.md") == fake_repo.resolve()


def test_discover_repo_root_from_starting_dir(fake_repo: Path) -> None:
    nested = fake_repo / ".claude" / "agents"
    assert discover_repo_root(nested) == fake_repo.resolve()


def test_discover_repo_root_not_found(tmp_path: Path) -> None:
    with pytest.raises(RepoRootNotFound):
        discover_repo_root(tmp_path)
