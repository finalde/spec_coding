"""Export every subtitled episode master into a per-language production folder.

`export(rel)` resolves the drama root from any path under it, walks all
`episodes/ep{NN}` dirs (legacy root layout AND staged `…/5_6_…/episodes/`), and
for each finds the burned subtitle masters `ep{NN}_{zh|en|zhen}.mp4`, copying
each into `ai_videos/{drama}/production/{中文|英文|中英}/ep{NN}.mp4` — the language
is implied by the sub-folder, so the suffix is stripped. `shutil.copy2`,
overwrites, never a symlink; existing production files are left in place and only
overwritten when re-exported. Nothing-to-export is a valid EMPTY result (not an
error) — the user simply hasn't burned any episode subtitles yet.

The drama-root resolution + episode tree-walk mirror
`subtitle_batch__writer.SubtitleBatchBurner` (defined once there, copied here to
keep this aggregate self-contained); the `production/` folder it creates carries
no `episodes/` dir so it is never re-walked.
"""
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.subtitle__error import InvalidBatchScopeError

_EP_DIR_RE = re.compile(r"^ep\d+$", re.IGNORECASE)
_EPISODES_DIR_NAME = "episodes"
_PRODUCTION_DIR_NAME = "production"
# burned-subtitle suffix -> production sub-folder (language implied by folder).
_LANG_FOLDERS: dict[str, str] = {"zh": "中文", "en": "英文", "zhen": "中英"}


@dataclass(frozen=True)
class ExportedEpisode:
    lang: str       # zh | en | zhen
    folder: str     # 中文 | 英文 | 中英
    episode: str    # ep01
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
class ExportProductionResult:
    drama_rel: str
    production_rel: str
    exported: tuple[ExportedEpisode, ...]

    def by_lang(self) -> dict[str, int]:
        counts: dict[str, int] = {folder: 0 for folder in _LANG_FOLDERS.values()}
        for e in self.exported:
            counts[e.folder] = counts.get(e.folder, 0) + 1
        return counts

    def to_payload(self) -> dict[str, Any]:
        return {
            "drama": self.drama_rel,
            "production": self.production_rel,
            "exported": [e.to_payload() for e in self.exported],
            "by_lang": self.by_lang(),
        }


class ProductionExporter:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def export(self, rel: str) -> ExportProductionResult:
        drama_root = self._drama_root(rel)
        production_root = drama_root / _PRODUCTION_DIR_NAME
        exported: list[ExportedEpisode] = []
        for ep_dir in self._episode_dirs(drama_root):
            slug = ep_dir.name.lower()
            for suffix, folder in _LANG_FOLDERS.items():
                src = ep_dir / f"{slug}_{suffix}.mp4"
                if not src.is_file() or src.is_symlink():
                    continue
                dst_dir = production_root / folder
                dst_dir.mkdir(parents=True, exist_ok=True)
                dst = dst_dir / f"{slug}.mp4"
                shutil.copy2(src, dst)
                exported.append(
                    ExportedEpisode(suffix, folder, slug, self._rel(src), self._rel(dst))
                )
        return ExportProductionResult(
            self._rel(drama_root), self._rel(production_root), tuple(exported)
        )

    def _drama_root(self, rel: str) -> Path:
        if not isinstance(rel, str) or rel == "":
            raise InvalidBatchScopeError("path is empty")
        if not self._exposed.is_inside(rel):
            raise InvalidBatchScopeError("path outside sandbox")
        parts = rel.split("/")
        if len(parts) < 2 or parts[0] != "ai_videos" or parts[1].startswith("_"):
            raise InvalidBatchScopeError("path is not under ai_videos/{drama}/")
        resolved = self._resolver.resolve("/".join(parts[:2]))
        if resolved is None:
            raise InvalidBatchScopeError("path failed sandbox resolution")
        if resolved.is_symlink():
            raise InvalidBatchScopeError("symlink is not allowed")
        if not resolved.is_dir():
            raise InvalidBatchScopeError("drama folder does not exist")
        return resolved

    def _episode_dirs(self, drama_root: Path) -> list[Path]:
        found: list[Path] = []
        try:
            episodes_dirs = [
                d for d in drama_root.rglob(_EPISODES_DIR_NAME)
                if d.is_dir() and not d.is_symlink()
            ]
        except OSError:
            return []
        for episodes_dir in episodes_dirs:
            for ep in self._sorted_children(episodes_dir):
                if _EP_DIR_RE.match(ep.name):
                    found.append(ep)
        return sorted(found, key=lambda p: (p.name.lower(), p.as_posix()))

    @staticmethod
    def _sorted_children(parent: Path) -> list[Path]:
        try:
            entries = sorted(parent.iterdir(), key=lambda p: p.name)
        except OSError:
            return []
        return [e for e in entries if e.is_dir() and not e.is_symlink()]

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()
