"""Downloads-aggregate commands: drama-scoped one-click "import + rename" flow."""
from __future__ import annotations

from libs.application.dtos.downloads__dto import ImportFromDownloadsResultCdto
from libs.application.mappers.downloads__mapper import DownloadsMapper
from libs.domain.errors.casting__error import DramaNotFoundError, InvalidDramaPathError
from libs.domain.errors.downloads__error import DownloadsDirMissingError
from libs.domain.value_objects.drama__valueobject import DramaPath
from libs.infrastructure.writers.downloads__writer import (
    DownloadsDirMissing,
    DownloadsImporter,
)
from libs.infrastructure.writers.media__writer import DramaNotFound, InvalidDramaPath


class DownloadsCommand:
    def __init__(self, importer: DownloadsImporter) -> None:
        self._importer = importer

    def import_drama(self, rel_drama_path: str) -> ImportFromDownloadsResultCdto:
        DramaPath(rel=rel_drama_path)
        try:
            result = self._importer.import_drama(rel_drama_path)
        except InvalidDramaPath as exc:
            raise InvalidDramaPathError(str(exc)) from exc
        except DramaNotFound as exc:
            raise DramaNotFoundError(str(exc)) from exc
        except DownloadsDirMissing as exc:
            raise DownloadsDirMissingError(str(exc)) from exc
        return DownloadsMapper.to_cdto(result)
