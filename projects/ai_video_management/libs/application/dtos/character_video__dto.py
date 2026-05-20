"""Character-video aggregate DTOs: TruncateCharacterVideoCommand result +
ConcatShotCharactersCommand result + per-character used/skipped rows.
Renamed from the former `character_video__cdto.py`."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TruncateCharacterVideoResultCdto:
    src_rel: str
    out_rel: str
    duration_seconds: float

    def to_payload(self) -> dict[str, Any]:
        return {
            "src": self.src_rel,
            "out": self.out_rel,
            "duration_seconds": self.duration_seconds,
        }


@dataclass(frozen=True)
class ShotConcatUsedCdto:
    role: str
    character_folder: str
    rel_path: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "character_folder": self.character_folder,
            "rel_path": self.rel_path,
        }


@dataclass(frozen=True)
class ShotConcatSkippedCdto:
    role: str
    character_folder: str
    reason: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "character_folder": self.character_folder,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ConcatShotCharactersResultCdto:
    shot_rel: str
    out_rel: str | None
    used: tuple[ShotConcatUsedCdto, ...]
    skipped: tuple[ShotConcatSkippedCdto, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "shot_path": self.shot_rel,
            "out": self.out_rel,
            "used": [u.to_payload() for u in self.used],
            "skipped": [s.to_payload() for s in self.skipped],
        }


@dataclass(frozen=True)
class CharacterViewCdto:
    timestamp: float
    role: str
    path: str

    def to_payload(self) -> dict[str, Any]:
        return {"timestamp": self.timestamp, "role": self.role, "path": self.path}


@dataclass(frozen=True)
class CharacterAudioCdto:
    path: str

    def to_payload(self) -> dict[str, Any]:
        return {"path": self.path}


@dataclass(frozen=True)
class CharacterViewFailureCdto:
    target: str
    error: str

    def to_payload(self) -> dict[str, Any]:
        return {"target": self.target, "error": self.error}


@dataclass(frozen=True)
class ExtractCharacterViewsResultCdto:
    src_rel: str
    views: tuple[CharacterViewCdto, ...]
    audio: CharacterAudioCdto | None
    failures: tuple[CharacterViewFailureCdto, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "src": self.src_rel,
            "views": [v.to_payload() for v in self.views],
            "audio": self.audio.to_payload() if self.audio is not None else None,
            "failures": [f.to_payload() for f in self.failures],
        }
