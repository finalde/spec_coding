from __future__ import annotations

from pathlib import Path

ALLOWED_EXTENSIONS: frozenset[str] = frozenset(
    {".md", ".json", ".yaml", ".yml", ".jsonl", ".txt", ".png", ".jpg"}
)
MAX_FILE_BYTES: int = 1_048_576

_EXCLUDED_DIRS: frozenset[str] = frozenset(
    {"node_modules", ".git", ".audit", "__pycache__", ".pytest_cache", "dist", "build", ".vite"}
)


_ALLOWED_TOP_LEVEL: frozenset[str] = frozenset({"ai_videos", "research"})


class ExposedTree:
    """The webapp's read/write tree exposes two roots: ai_videos/** and research/**.

    `research/` was added by follow-up 003 for free-form reference dumps. It
    reuses every existing security control (extension allowlist, _EXCLUDED_DIRS
    filter, traversal hardening) — only the admitted-first-segment set is
    widened.
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

    def research_dirs(self) -> list[Path]:
        research_root = self._root / "research"
        if not research_root.is_dir():
            return []
        return sorted(p for p in research_root.iterdir() if p.is_dir())

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
        if first in _ALLOWED_TOP_LEVEL:
            for seg in parts:
                if seg in _EXCLUDED_DIRS:
                    return False
            return True
        return False

    def excluded_dirs(self) -> frozenset[str]:
        return _EXCLUDED_DIRS
