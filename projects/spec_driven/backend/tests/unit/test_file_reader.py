from __future__ import annotations

import os
from pathlib import Path

import pytest

from libs.file_reader import FileReadError, read_file


def test_happy_path_md(fake_repo: Path) -> None:
    out = read_file("specs/development/spec_driven/final_specs/spec.md", fake_repo)
    assert out.path == "specs/development/spec_driven/final_specs/spec.md"
    assert out.extension == ".md"
    assert "spec content" in out.text


def test_outside_sandbox_traversal(fake_repo: Path) -> None:
    with pytest.raises(FileReadError) as ei:
        read_file("../../etc/hosts", fake_repo)
    assert ei.value.status == 400
    assert ei.value.kind == "outside_sandbox"


def test_unsupported_extension(fake_repo: Path) -> None:
    findings = fake_repo / "specs" / "development" / "spec_driven" / "findings"
    p = findings / "diagram.png"
    p.write_text("x", encoding="utf-8")
    with pytest.raises(FileReadError) as ei:
        read_file("specs/development/spec_driven/findings/diagram.png", fake_repo)
    assert ei.value.status == 415
    assert ei.value.kind == "unsupported_extension"


def test_too_large(fake_repo: Path) -> None:
    findings = fake_repo / "specs" / "development" / "spec_driven" / "findings"
    big = findings / "big.md"
    big.write_bytes(b"a" * (2 * 1024 * 1024 + 100))
    with pytest.raises(FileReadError) as ei:
        read_file("specs/development/spec_driven/findings/big.md", fake_repo)
    assert ei.value.status == 413
    assert ei.value.kind == "too_large"


def test_binary_content_nul(fake_repo: Path) -> None:
    findings = fake_repo / "specs" / "development" / "spec_driven" / "findings"
    bin_md = findings / "binary.md"
    bin_md.write_bytes(b"# header\x00more")
    with pytest.raises(FileReadError) as ei:
        read_file("specs/development/spec_driven/findings/binary.md", fake_repo)
    assert ei.value.status == 415
    assert ei.value.kind == "binary_content"


def test_outside_exposed_tree(fake_repo: Path) -> None:
    other = fake_repo / "pyproject.toml"
    other.write_text("[project]\n", encoding="utf-8")
    with pytest.raises(FileReadError) as ei:
        read_file("pyproject.toml", fake_repo)
    assert ei.value.status == 404
    assert ei.value.kind == "outside_exposed_tree"


def test_file_removed_after_stat(fake_repo: Path) -> None:
    findings = fake_repo / "specs" / "development" / "spec_driven" / "findings"
    p = findings / "transient.md"
    p.write_text("hi", encoding="utf-8")
    os.unlink(p)
    with pytest.raises(FileReadError) as ei:
        read_file("specs/development/spec_driven/findings/transient.md", fake_repo)
    assert ei.value.status == 404
    assert ei.value.kind == "file_removed"
