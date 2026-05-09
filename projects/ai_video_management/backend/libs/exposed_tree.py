from __future__ import annotations

from pathlib import Path

ALLOWED_EXTENSIONS: frozenset[str] = frozenset(
    {".md", ".json", ".yaml", ".yml", ".jsonl", ".txt", ".png", ".jpg"}
)
MAX_FILE_BYTES: int = 1_048_576

_EXCLUDED_DIRS: frozenset[str] = frozenset(
    {"node_modules", ".git", ".audit", "__pycache__", ".pytest_cache", "dist", "build", ".vite"}
)


class ExposedTree:
    """The webapp's read/write tree exposes a single root: ai_videos/**.

    No other workspace directory is reachable through this sandbox.
    """

    def __init__(self, repo_root: Path) -> None:
        self._root = repo_root.resolve()

    @property
    def root(self) -> Path:
        return self._root

    def ai_video_dirs(self) -> list[Path]:
        ai_videos_root = self._root / "ai_videos"
        if not ai_videos_root.is_dir():
            return []
        return sorted(p for p in ai_videos_root.iterdir() if p.is_dir())

    def is_inside(self, rel: str) -> bool:
        if not rel or rel.startswith("/") or "\\" in rel or "\x00" in rel:
            return False
        candidate = (self._root / rel).resolve(strict=False)
        if not (candidate == self._root or self._root in candidate.parents):
            return False
        try:
            relative = candidate.relative_to(self._root)
        except ValueError:
            return False
        parts = relative.parts
        if not parts:
            return False
        first = parts[0]
        if first == "ai_videos":
            for seg in parts:
                if seg in _EXCLUDED_DIRS:
                    return False
            return True
        return False

    def excluded_dirs(self) -> frozenset[str]:
        return _EXCLUDED_DIRS
