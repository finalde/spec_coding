"""File-aggregate queries: read a text or image file from the sandbox.

Per development.md §3 read-side simplification: bypasses domain layer.
"""
from __future__ import annotations

from libs.application.dtos.file__dto import FileReadQdto
from libs.application.mappers.file__mapper import FileMapper
from libs.infrastructure.readers.file__reader import FileReader


class FileQuery:
    def __init__(self, reader: FileReader) -> None:
        self._reader = reader

    def read(self, rel_path: str) -> FileReadQdto:
        return FileMapper.read_to_qdto(self._reader.read(rel_path))
