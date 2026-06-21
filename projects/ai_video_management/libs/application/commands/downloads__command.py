"""Downloads-aggregate commands: drama-scoped one-click "import + rename" flow."""
from __future__ import annotations

from libs.application.dtos.downloads__dto import ImportFromDownloadsResultCdto
from libs.application.mappers.downloads__mapper import DownloadsMapper
from libs.domain.value_objects.drama__valueobject import DramaPath
from libs.infrastructure.writers.downloads__writer import DownloadsImporter


class DownloadsCommand:
    def __init__(self, importer: DownloadsImporter) -> None:
        self._importer = importer

    def import_drama(self, rel_drama_path: str) -> ImportFromDownloadsResultCdto:
        path = DramaPath(rel=rel_drama_path)
        if path.drama_name == "_performances":
            return DownloadsMapper.to_cdto(self._importer.import_performances(rel_drama_path))
        if path.drama_name == "_actors":
            return DownloadsMapper.to_cdto(self._importer.import_actors(rel_drama_path))
        if path.drama_name == "_bgm":
            return DownloadsMapper.to_cdto(self._importer.import_bgms(rel_drama_path))
        return DownloadsMapper.to_cdto(self._importer.import_drama(rel_drama_path))
