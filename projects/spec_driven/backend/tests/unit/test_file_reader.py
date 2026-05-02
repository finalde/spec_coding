from __future__ import annotations

from pathlib import Path

import pytest

from libs.file_reader import FileReadError, read_file


def test_read_existing_md(fake_repo: Path) -> None:
    content = read_file("CLAUDE.md", fake_repo)
    assert content.path == "CLAUDE.md"
    assert content.extension == ".md"
    assert "fake claude" in content.text


def test_read_traversal_blocked(fake_repo: Path) -> None:
    with pytest.raises(FileReadError) as ei:
        read_file("../../../etc/hosts", fake_repo)
    assert ei.value.status == 400
    assert ei.value.error == "outside_sandbox"


def test_read_outside_exposed_tree(fake_repo: Path) -> None:
    (fake_repo / "pyproject.toml").write_text("[project]", encoding="utf-8")
    with pytest.raises(FileReadError) as ei:
        read_file("pyproject.toml", fake_repo)
    assert ei.value.status == 404
    assert ei.value.kind == "outside_exposed_tree"


def test_read_unsupported_extension(fake_repo: Path) -> None:
    (fake_repo / "specs" / "development" / "spec_driven" / "final_specs" / "diagram.png").write_bytes(b"\x89PNG")
    with pytest.raises(FileReadError) as ei:
        read_file("specs/development/spec_driven/final_specs/diagram.png", fake_repo)
    assert ei.value.status in (404, 415)


def test_read_too_large(fake_repo: Path) -> None:
    big = fake_repo / "specs" / "development" / "spec_driven" / "final_specs" / "huge.md"
    big.write_text("x" * (2 * 1024 * 1024 + 1), encoding="utf-8")
    with pytest.raises(FileReadError) as ei:
        read_file("specs/development/spec_driven/final_specs/huge.md", fake_repo)
    assert ei.value.status == 413


def test_read_binary_content(fake_repo: Path) -> None:
    bad = fake_repo / "specs" / "development" / "spec_driven" / "final_specs" / "bin.md"
    bad.write_bytes(b"hello\x00world")
    with pytest.raises(FileReadError) as ei:
        read_file("specs/development/spec_driven/final_specs/bin.md", fake_repo)
    assert ei.value.status == 415
    assert ei.value.error == "binary_content"


def test_read_missing_file(fake_repo: Path) -> None:
    with pytest.raises(FileReadError) as ei:
        read_file("specs/development/spec_driven/final_specs/missing.md", fake_repo)
    assert ei.value.status == 404
    assert ei.value.kind in ("file_removed", "outside_exposed_tree")
