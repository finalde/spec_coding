from __future__ import annotations

from libs.application.file__mapper import FileMapper
from libs.application.read_file__qdto import ReadFileQdto
from libs.infrastructure.file__reader import FileReader


class ReadFileQuery:
    def __init__(self, reader: FileReader) -> None:
        self._reader = reader

    def execute(self, rel: str) -> ReadFileQdto:
        return FileMapper.read_to_qdto(self._reader.read(rel))
