from __future__ import annotations

from pathlib import Path

import pytest

from libs.repo_root import RepoRootNotFound, discover_repo_root


def test_discover_from_child_path(fake_repo: Path) -> None:
    discover_repo_root.cache_clear()
    nested = fake_repo / "specs" / "development" / "spec_driven" / "final_specs"
    found = discover_repo_root(nested)
    assert found.resolve() == fake_repo.resolve()


def test_discover_from_unrelated_path_raises(tmp_path: Path) -> None:
    discover_repo_root.cache_clear()
    elsewhere = tmp_path / "no_repo_here"
    elsewhere.mkdir()
    with pytest.raises(RepoRootNotFound):
        discover_repo_root(elsewhere)


def test_cache_reused(fake_repo: Path) -> None:
    discover_repo_root.cache_clear()
    a = discover_repo_root(fake_repo)
    b = discover_repo_root(fake_repo)
    assert a is b
