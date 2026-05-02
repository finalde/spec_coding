from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WriteResult:
    path: Path
    sha256: str
    bytes_written: int
    backed_up: bool


class AtomicWriter:
    """Write text atomically: temp file in the same directory + os.replace.

    Same-directory placement of the temp file guarantees os.replace() is a
    rename rather than a cross-device copy. os.replace() is atomic on both
    POSIX and Windows when target is on the same filesystem.
    """

    def __init__(self, encoding: str = "utf-8") -> None:
        self._encoding = encoding

    def write(self, path: Path, content: str) -> WriteResult:
        path = path.resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        encoded = content.encode(self._encoding)
        sha = hashlib.sha256(encoded).hexdigest()
        fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(encoded)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_name, path)
        except Exception:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise
        return WriteResult(path=path, sha256=sha, bytes_written=len(encoded), backed_up=False)


class BackupWriter:
    """Decorate AtomicWriter with a single-slot .bak snapshot of the prior content."""

    def __init__(self, atomic: AtomicWriter | None = None) -> None:
        self._atomic = atomic or AtomicWriter()

    def write(self, path: Path, content: str) -> WriteResult:
        path = path.resolve()
        backed_up = False
        if path.exists():
            bak = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, bak)
            backed_up = True
        result = self._atomic.write(path, content)
        return WriteResult(
            path=result.path,
            sha256=result.sha256,
            bytes_written=result.bytes_written,
            backed_up=backed_up,
        )


def hash_text(content: str, encoding: str = "utf-8") -> str:
    return hashlib.sha256(content.encode(encoding)).hexdigest()
