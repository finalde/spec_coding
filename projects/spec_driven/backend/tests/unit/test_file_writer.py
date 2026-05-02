from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest import mock

import pytest

from libs.file_reader import FileReadError, read_file
from libs.file_writer import write_file


def test_put_happy_path_round_trip(fake_repo: Path) -> None:
    rel = "specs/development/spec_driven/final_specs/spec.md"
    result = write_file(rel, "# replaced\n", fake_repo)
    assert result.path == rel
    out = read_file(rel, fake_repo)
    assert "replaced" in out.text


def test_outside_sandbox_400(fake_repo: Path) -> None:
    with pytest.raises(FileReadError) as ei:
        write_file("../../etc/hosts", "x", fake_repo)
    assert ei.value.status == 400
    assert ei.value.kind == "outside_sandbox"


def test_binary_content_415(fake_repo: Path) -> None:
    rel = "specs/development/spec_driven/final_specs/spec.md"
    with pytest.raises(FileReadError) as ei:
        write_file(rel, "head\x00tail", fake_repo)
    assert ei.value.status == 415
    assert ei.value.kind == "binary_content"


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="permission semantics differ on Windows",
)
def test_atomic_temp_file_cleaned_up_on_permission_error(fake_repo: Path) -> None:
    rel = "specs/development/spec_driven/final_specs/spec.md"
    parent = fake_repo / "specs" / "development" / "spec_driven" / "final_specs"

    def boom(*args, **kwargs):
        raise PermissionError("nope")

    with mock.patch("libs.file_writer.os.replace", side_effect=boom):
        with pytest.raises(FileReadError) as ei:
            write_file(rel, "# replaced\n", fake_repo)
        assert ei.value.status == 403

    leftover = [p for p in parent.iterdir() if p.name.startswith(".tmp-")]
    assert leftover == []


def test_unsupported_extension_415(fake_repo: Path) -> None:
    findings = fake_repo / "specs" / "development" / "spec_driven" / "findings"
    rel = "specs/development/spec_driven/findings/diagram.png"
    with pytest.raises(FileReadError) as ei:
        write_file(rel, "x", fake_repo)
    assert ei.value.status in (404, 415)
