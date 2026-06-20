"""Media-aggregate DTOs: ServeMediaQuery's Qdto + archive/unarchive/delete/
hard_delete/rename command results. Consolidates `media__qdto.py` +
`media__cdto.py`."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MediaFileQdto:
    """For serve-media: returns the resolved on-disk Path + the content-type
    so the route handler can build a FileResponse. The Path lives in this
    DTO (not domain) because it's a transport artefact — the route handler
    needs it to construct FastAPI's FileResponse."""

    resolved_path: Path
    media_type: str
    filename: str


@dataclass(frozen=True)
class MediaMoveCdto:
    src_rel: str
    dst_rel: str

    def to_payload(self) -> dict[str, str]:
        return {"from": self.src_rel, "to": self.dst_rel}


@dataclass(frozen=True)
class MediaHardDeleteCdto:
    deleted_rel: str

    def to_payload(self) -> dict[str, Any]:
        return {"deleted": self.deleted_rel}


@dataclass(frozen=True)
class MediaPurgeDeletedCdto:
    count: int

    def to_payload(self) -> dict[str, Any]:
        return {"purged": self.count}


@dataclass(frozen=True)
class RenameMediaResultCdto:
    renamed: list[dict[str, str]]
    skipped: list[str]
    errors: list[dict[str, str]]

    def to_payload(self) -> dict[str, Any]:
        return {
            "renamed": list(self.renamed),
            "skipped": list(self.skipped),
            "errors": list(self.errors),
        }
