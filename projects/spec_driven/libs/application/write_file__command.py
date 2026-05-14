from __future__ import annotations

from libs.application.file__mapper import FileMapper
from libs.application.write_file__cdto import WriteFileCdto, WriteFileResultCdto
from libs.infrastructure.file__writer import FileWriter


class WriteFileCommand:
    def __init__(self, writer: FileWriter) -> None:
        self._writer = writer

    def execute(self, cdto: WriteFileCdto) -> WriteFileResultCdto:
        result = self._writer.write(cdto.path, cdto.content, cdto.if_unmodified_since)
        return FileMapper.write_to_cdto(result)
