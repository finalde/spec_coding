"""File-aggregate commands: atomically write a text file under the sandbox,
guarded by If-Unmodified-Since mtime concurrency (RFC 7232)."""
from __future__ import annotations

from libs.application.dtos.file__dto import FileWriteResultCdto, WriteFileInputCdto
from libs.application.mappers.file__mapper import FileMapper
from libs.domain.errors.file__error import (
    FileNotInSandboxError,
    FileTooLargeError,
    InvalidBodyEncodingError,
    MissingIfUnmodifiedSinceError,
    StaleWriteError,
    UnsupportedFileExtensionError,
)
from libs.infrastructure.writers.file__writer import (
    FileTooLarge,
    FileWriter,
    InvalidBodyEncoding,
    MissingIfUnmodifiedSince,
    OutsideSandbox,
    StaleWrite,
    UnsupportedExtension,
)


class FileCommand:
    def __init__(self, writer: FileWriter) -> None:
        self._writer = writer

    def write(self, input_cdto: WriteFileInputCdto) -> FileWriteResultCdto:
        try:
            result = self._writer.write(
                input_cdto.rel_path,
                input_cdto.content,
                input_cdto.if_unmodified_since,
            )
        except MissingIfUnmodifiedSince as exc:
            raise MissingIfUnmodifiedSinceError(str(exc)) from exc
        except UnsupportedExtension as exc:
            raise UnsupportedFileExtensionError(str(exc)) from exc
        except FileTooLarge as exc:
            raise FileTooLargeError(str(exc)) from exc
        except InvalidBodyEncoding as exc:
            raise InvalidBodyEncodingError(str(exc)) from exc
        except StaleWrite as exc:
            raise StaleWriteError(current_mtime=exc.current_mtime) from exc
        except OutsideSandbox as exc:
            raise FileNotInSandboxError(str(exc)) from exc
        return FileMapper.write_to_cdto(result)
