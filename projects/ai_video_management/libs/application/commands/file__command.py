"""File-aggregate commands: atomically write a text file under the sandbox,
guarded by If-Unmodified-Since mtime concurrency (RFC 7232)."""
from __future__ import annotations

from libs.application.dtos.file__dto import FileWriteResultCdto, WriteFileInputCdto
from libs.application.mappers.file__mapper import FileMapper
from libs.infrastructure.writers.file__writer import FileWriter


class FileCommand:
    def __init__(self, writer: FileWriter) -> None:
        self._writer = writer

    def write(self, input_cdto: WriteFileInputCdto) -> FileWriteResultCdto:
        result = self._writer.write(
            input_cdto.rel_path,
            input_cdto.content,
            input_cdto.if_unmodified_since,
        )
        return FileMapper.write_to_cdto(result)
