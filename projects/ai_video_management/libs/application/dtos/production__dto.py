"""Production-aggregate DTO: result of exporting subtitled episode masters into
per-language production sub-folders. Cdto only — no Qdto."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExportedEpisodeCdto:
    lang: str
    folder: str
    episode: str
    src_rel: str
    out_rel: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "lang": self.lang,
            "folder": self.folder,
            "episode": self.episode,
            "src": self.src_rel,
            "out": self.out_rel,
        }


@dataclass(frozen=True)
class ExportProductionResultCdto:
    drama_rel: str
    production_rel: str
    exported: tuple[ExportedEpisodeCdto, ...]
    by_lang: dict[str, int]

    def to_payload(self) -> dict[str, Any]:
        return {
            "drama": self.drama_rel,
            "production": self.production_rel,
            "exported": [e.to_payload() for e in self.exported],
            "by_lang": self.by_lang,
        }
