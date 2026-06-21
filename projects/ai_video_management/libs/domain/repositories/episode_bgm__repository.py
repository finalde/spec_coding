"""Repository Protocol for the episode-BGM aggregate. Concrete implementation
in `libs/infrastructure/writers/episode_bgm__writer.py`; the application layer
only sees this interface (dependency-inversion seam per development.md §2)."""
from __future__ import annotations

from typing import Protocol


class EpisodeBgmRepository(Protocol):
    """Read / assign / burn surface for an episode's sparse BGM cue timeline."""

    def read(self, rel: str) -> object: ...

    def assign(self, rel: str, start: float, end: float, bgm_id: str) -> object: ...

    def unassign(self, rel: str, start: float, end: float) -> object: ...

    def burn(self, rel: str) -> object: ...
