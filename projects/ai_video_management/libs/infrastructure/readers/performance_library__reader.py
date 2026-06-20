"""Read the performance library at `ai_videos/_performances/{emotion}/perf_NNNN/perf_NNNN.md`.

Each entry has a YAML head (`perf_id / emotion / intensity / style / carrier /
au_ref / lma_tag / status`), an H1 title, a `## 锁定文本块` code fence (the
embeddable performance text), and a `## 检验视频` section carrying a duration
(e.g. 「时长 4 秒」). Renders may live under `renders/*.mp4`.

This reader does the IO + parsing only; ranking lives in the query layer.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_PERF_ID = re.compile(r"^perf_\d{4}$")
_DURATION = re.compile(r"时长\s*([0-9]+(?:\.[0-9]+)?)\s*秒")
_VIDEO_EXTS: tuple[str, ...] = (".mp4",)


@dataclass(frozen=True)
class PerformanceEntry:
    perf_id: str
    emotion: str
    intensity: int | None
    style: str
    carrier: str
    duration_s: float | None
    title: str
    preview: str
    locked: str
    mp4_rel_path: str | None


class PerformanceLibraryReader:
    def __init__(self, root: Path) -> None:
        self._root = root

    def _perf_root(self) -> Path:
        return self._root / "ai_videos" / "_performances"

    def list_entries(self) -> list[PerformanceEntry]:
        root = self._perf_root()
        if not root.is_dir():
            return []
        out: list[PerformanceEntry] = []
        for emotion_dir in sorted(root.iterdir(), key=lambda p: p.name):
            if not emotion_dir.is_dir() or emotion_dir.is_symlink():
                continue
            if emotion_dir.name.startswith("_"):
                continue
            for perf_dir in sorted(emotion_dir.iterdir(), key=lambda p: p.name):
                if not perf_dir.is_dir() or perf_dir.is_symlink():
                    continue
                if not _PERF_ID.match(perf_dir.name):
                    continue
                md = perf_dir / f"{perf_dir.name}.md"
                if not md.is_file():
                    continue
                entry = self._parse_entry(perf_dir, md)
                if entry is not None:
                    out.append(entry)
        return out

    def by_id(self, perf_id: str) -> PerformanceEntry | None:
        if not _PERF_ID.match(perf_id):
            return None
        root = self._perf_root()
        if not root.is_dir():
            return None
        for emotion_dir in root.iterdir():
            if not emotion_dir.is_dir() or emotion_dir.is_symlink():
                continue
            if emotion_dir.name.startswith("_"):
                continue
            md = emotion_dir / perf_id / f"{perf_id}.md"
            if md.is_file():
                return self._parse_entry(md.parent, md)
        return None

    def _parse_entry(self, perf_dir: Path, md: Path) -> PerformanceEntry | None:
        try:
            text = md.read_text(encoding="utf-8")
        except OSError:
            return None
        front = self._parse_front_matter(text)
        title = self._first_h1(text)
        locked = self._locked_block(text)
        preview = locked.strip().replace("\n", " ")[:80]
        duration = self._duration(text)
        mp4 = self._first_render(perf_dir)
        intensity = self._as_int(front.get("intensity"))
        return PerformanceEntry(
            perf_id=front.get("perf_id") or perf_dir.name,
            emotion=front.get("emotion", ""),
            intensity=intensity,
            style=front.get("style", ""),
            carrier=front.get("carrier", ""),
            duration_s=duration,
            title=title,
            preview=preview,
            locked=locked,
            mp4_rel_path=mp4,
        )

    @staticmethod
    def _parse_front_matter(text: str) -> dict[str, str]:
        if not text.startswith("---"):
            return {}
        end = text.find("\n---", 3)
        if end == -1:
            return {}
        block = text[3:end]
        out: dict[str, str] = {}
        for line in block.splitlines():
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            out[key.strip()] = value.strip()
        return out

    @staticmethod
    def _as_int(value: str | None) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _first_h1(text: str) -> str:
        for line in text.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return ""

    @staticmethod
    def _locked_block(text: str) -> str:
        idx = text.find("## 锁定文本块")
        if idx == -1:
            return ""
        after = text[idx:]
        fences = [m.start() for m in re.finditer(r"```", after)]
        if len(fences) >= 2:
            return after[fences[0] + 3:fences[1]].strip()
        return ""

    @staticmethod
    def _duration(text: str) -> float | None:
        idx = text.find("## 检验视频")
        scope = text[idx:] if idx != -1 else text
        m = _DURATION.search(scope)
        if m is None:
            return None
        try:
            return float(m.group(1))
        except ValueError:
            return None

    def _first_render(self, perf_dir: Path) -> str | None:
        renders = perf_dir / "renders"
        if not renders.is_dir() or renders.is_symlink():
            return None
        candidates: list[Path] = []
        for child in renders.iterdir():
            if child.is_file() and child.suffix.lower() in _VIDEO_EXTS:
                candidates.append(child)
        if not candidates:
            return None
        chosen = sorted(candidates, key=lambda p: p.name)[0]
        try:
            return chosen.resolve().relative_to(self._root).as_posix()
        except (OSError, ValueError):
            return None
