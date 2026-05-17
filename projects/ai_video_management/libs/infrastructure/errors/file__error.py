"""Infrastructure-side exceptions raised by the file writer/reader.

Per follow-up 067 (Single Responsibility Principle): exception classes
do not belong in the writer/reader file. They live here, one file per
aggregate, mirroring the `libs/domain/errors/file__error.py` layout
on the domain side. Commands catch these infra exceptions and re-raise
as named domain errors.
"""
from __future__ import annotations


class UnsupportedExtension(Exception):
    pass

class FileTooLarge(Exception):
    pass

class InvalidBodyEncoding(Exception):
    pass

class OutsideSandbox(Exception):
    pass

class MissingIfUnmodifiedSince(Exception):
    """If-Unmodified-Since header is REQUIRED on PUT for existing files."""
    pass

class StaleWrite(Exception):
    def __init__(self, current_mtime: float) -> None:
        super().__init__(f"stale_write: current_mtime={current_mtime}")
        self.current_mtime: float = current_mtime

class UnsupportedExtension(Exception):
    pass

class FileTooLarge(Exception):
    pass

class OutsideSandbox(Exception):
    pass
