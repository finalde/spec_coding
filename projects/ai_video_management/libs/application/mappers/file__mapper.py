"""FileMapper — owns the DAO↔Qdto/Cdto translation for file-resource ops."""
from __future__ import annotations

from libs.application.dtos.file__dto import FileWriteResultCdto
from libs.application.dtos.file__dto import FileReadQdto
from libs.infrastructure.readers.file__reader import ReadResult
from libs.infrastructure.writers.file__writer import WriteResult


class FileMapper:
    @staticmethod
    def read_to_qdto(r: ReadResult) -> FileReadQdto:
        return FileReadQdto(
            rel_path=r.rel_path,
            content=r.content,
            encoding=r.encoding,
            size_bytes=r.size_bytes,
            mtime_unix=r.mtime_unix,
            mtime_http=r.mtime_http,
        )

    @staticmethod
    def write_to_cdto(w: WriteResult) -> FileWriteResultCdto:
        return FileWriteResultCdto(
            rel_path=w.rel_path,
            size_bytes=w.size_bytes,
            mtime_unix=w.mtime_unix,
            mtime_http=w.mtime_http,
        )
