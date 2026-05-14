from __future__ import annotations

from libs.application.read_file__qdto import ReadFileQdto
from libs.application.write_file__cdto import WriteFileResultCdto
from libs.infrastructure.file__reader import ReadResult
from libs.infrastructure.file__writer import WriteResult


class FileMapper:
    @staticmethod
    def read_to_qdto(r: ReadResult) -> ReadFileQdto:
        return ReadFileQdto(
            path=r.rel_path,
            content=r.content,
            encoding=r.encoding,
            size_bytes=r.size_bytes,
            mtime_unix=r.mtime_unix,
            mtime_http=r.mtime_http,
        )

    @staticmethod
    def write_to_cdto(w: WriteResult) -> WriteFileResultCdto:
        return WriteFileResultCdto(
            path=w.rel_path,
            size_bytes=w.size_bytes,
            mtime_unix=w.mtime_unix,
            mtime_http=w.mtime_http,
        )
