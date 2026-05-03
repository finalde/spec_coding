"""
Group 2 — file_reader (FR-3, FR-5, AC-2, AC-7, AC-8).
"""

from __future__ import annotations

import pytest

from libs.file_reader import (
    FileReader,
    NotFoundError,
    TooLargeError,
    UnsupportedExtensionError,
)


def test_reads_known_markdown(resolver):
    reader = FileReader(resolver=resolver)
    r = reader.read("CLAUDE.md")
    assert r.path == "CLAUDE.md"
    assert "# CLAUDE.md" in r.content
    assert r.bytes > 0


@pytest.mark.parametrize("ext", [".md", ".json", ".yaml", ".yml", ".jsonl", ".txt"])
def test_extension_whitelist_allows_text(resolver, scratch_dir, ext):
    f = scratch_dir / f"sample{ext}"
    f.write_bytes(b"ok\n")
    try:
        reader = FileReader(resolver=resolver)
        r = reader.read(f"specs/development/spec_driven/__scratch__/sample{ext}")
        assert r.bytes == 3
    finally:
        f.unlink()


@pytest.mark.parametrize("ext", [".exe", ".bat", ".cmd", ".ps1", ".sh", ".html", ".svg", ".dll"])
def test_extension_whitelist_rejects_executables(resolver, scratch_dir, ext):
    f = scratch_dir / f"sample{ext}"
    f.write_text("nope\n", encoding="utf-8")
    try:
        reader = FileReader(resolver=resolver)
        with pytest.raises(UnsupportedExtensionError):
            reader.read(f"specs/development/spec_driven/__scratch__/sample{ext}")
    finally:
        f.unlink()


def test_rejects_no_extension(resolver, scratch_dir):
    f = scratch_dir / "noext"
    f.write_text("x", encoding="utf-8")
    try:
        with pytest.raises(UnsupportedExtensionError):
            FileReader(resolver=resolver).read("specs/development/spec_driven/__scratch__/noext")
    finally:
        f.unlink()


def test_size_cap_at_1mb(resolver, scratch_dir):
    f = scratch_dir / "big.md"
    f.write_bytes(b"a" * (1024 * 1024 + 1))
    try:
        with pytest.raises(TooLargeError):
            FileReader(resolver=resolver).read("specs/development/spec_driven/__scratch__/big.md")
    finally:
        f.unlink()


def test_zero_byte_file_returns_empty_content(resolver, scratch_dir):
    f = scratch_dir / "empty.md"
    f.write_bytes(b"")
    try:
        r = FileReader(resolver=resolver).read("specs/development/spec_driven/__scratch__/empty.md")
        assert r.content == ""
        assert r.bytes == 0
    finally:
        f.unlink()


def test_single_404_for_missing_file(resolver, scratch_dir):
    with pytest.raises(NotFoundError):
        FileReader(resolver=resolver).read("specs/development/spec_driven/__scratch__/nope.md")


def test_single_404_for_outside_tree(resolver):
    with pytest.raises(NotFoundError):
        FileReader(resolver=resolver).read("../etc/passwd")


def test_returns_mtime_and_bytes(resolver):
    r = FileReader(resolver=resolver).read("CLAUDE.md")
    assert r.mtime
    assert r.bytes > 0
    assert "T" in r.mtime
