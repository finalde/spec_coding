"""Frame-aggregate DTOs: ExtractFramesCommand's row/failure/result Cdtos.
Renamed from the former `frame__cdto.py` (no Qdtos for this aggregate)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FrameRowCdto:
    timestamp: float
    role: str
    shot_size: str
    rank: int
    rel_path: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "role": self.role,
            "shot_size": self.shot_size,
            "rank": self.rank,
            "path": self.rel_path,
        }


@dataclass(frozen=True)
class FrameFailureCdto:
    timestamp: float
    role: str
    error: str

    def to_payload(self) -> dict[str, Any]:
        return {"timestamp": self.timestamp, "role": self.role, "error": self.error}


@dataclass(frozen=True)
class ExtractFramesResultCdto:
    src_rel: str
    frames: tuple[FrameRowCdto, ...]
    failures: tuple[FrameFailureCdto, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "src": self.src_rel,
            "frames": [f.to_payload() for f in self.frames],
            "failures": [f.to_payload() for f in self.failures],
        }
