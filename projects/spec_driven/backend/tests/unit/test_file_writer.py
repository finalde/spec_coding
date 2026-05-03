"""
Group 3 — file_writer (FR-6, FR-7, FR-8, NFR-10).
"""

from __future__ import annotations

import pytest

from libs.file_reader import TooLargeError, UnsupportedExtensionError
from libs.file_writer import FileWriter, NotTextError


def test_atomic_write_temp_then_rename(resolver, scratch_dir):
    writer = FileWriter(resolver=resolver)
    rel = "specs/development/spec_driven/__scratch__/atomic.md"
    r = writer.write(rel, "hello")
    assert r.bytes == 5
    assert (scratch_dir / "atomic.md").read_text(encoding="utf-8") == "hello"
    leftovers = list(scratch_dir.glob(".tmp-*"))
    assert leftovers == []


def test_body_cap_at_1mb(resolver, scratch_dir):
    writer = FileWriter(resolver=resolver)
    rel = "specs/development/spec_driven/__scratch__/cap.md"
    with pytest.raises(TooLargeError):
        writer.write(rel, "a" * (1024 * 1024 + 1))


def test_extension_validation_md_allowed(resolver, scratch_dir):
    writer = FileWriter(resolver=resolver)
    r = writer.write("specs/development/spec_driven/__scratch__/ok.md", "hi")
    assert r.bytes == 2


@pytest.mark.parametrize("ext", [".png", ".jpg", ".svg", ".exe", ".html"])
def test_extension_validation_rejects(resolver, scratch_dir, ext):
    writer = FileWriter(resolver=resolver)
    rel = f"specs/development/spec_driven/__scratch__/x{ext}"
    with pytest.raises(UnsupportedExtensionError):
        writer.write(rel, "data")


def test_first_16_bytes_must_be_valid_utf8_no_nul(resolver, scratch_dir):
    writer = FileWriter(resolver=resolver)
    rel = "specs/development/spec_driven/__scratch__/binary.md"
    with pytest.raises(NotTextError):
        writer.write(rel, "\x00abcdefghij")


def test_returns_path_bytes_mtime(resolver, scratch_dir):
    writer = FileWriter(resolver=resolver)
    r = writer.write("specs/development/spec_driven/__scratch__/r.md", "abc\n")
    assert r.path == "specs/development/spec_driven/__scratch__/r.md"
    assert r.bytes == 4
    assert "T" in r.mtime


def test_overwrite_advances_mtime(resolver, scratch_dir):
    import time

    writer = FileWriter(resolver=resolver)
    rel = "specs/development/spec_driven/__scratch__/owr.md"
    r1 = writer.write(rel, "v1")
    time.sleep(1.05)
    r2 = writer.write(rel, "v2")
    assert r2.mtime > r1.mtime


def test_zero_byte_md_allowed(resolver, scratch_dir):
    writer = FileWriter(resolver=resolver)
    r = writer.write("specs/development/spec_driven/__scratch__/empty.md", "")
    assert r.bytes == 0
