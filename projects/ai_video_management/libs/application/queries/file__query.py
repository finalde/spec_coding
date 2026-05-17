"""File-aggregate queries: read a text or image file from the sandbox.

Per development.md §3 read-side simplification: bypasses domain layer.
"""
from __future__ import annotations

from libs.application.dtos.file__dto import FileReadQdto
from libs.application.mappers.file__mapper import FileMapper
from libs.domain.errors.file__error import (
    FileNotInSandboxError,
    FileTooLargeError,
    UnsupportedFileExtensionError,
)
from libs.infrastructure.readers.file__reader import (
    FileReader,
    FileTooLarge,
    OutsideSandbox,
    UnsupportedExtension,
)


class FileQuery:
    def __init__(self, reader: FileReader) -> None:
        self._reader = reader

    def read(self, rel_path: str) -> FileReadQdto:
        try:
            result = self._reader.read(rel_path)
        except UnsupportedExtension as exc:
            raise UnsupportedFileExtensionError(str(exc)) from exc
        except FileTooLarge as exc:
            raise FileTooLargeError(str(exc)) from exc
        except OutsideSandbox as exc:
            raise FileNotInSandboxError(str(exc)) from exc
        return FileMapper.read_to_qdto(result)
