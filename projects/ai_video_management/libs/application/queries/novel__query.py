"""Novel-aggregate queries: list status of every downloaded novel on disk.

Reads `downloaded_novels/{cat}/{slug}/_meta.json` directly (no domain enforcement
— pure projection). Returns one NovelStatusQdto per novel; novels with no
`_meta.json` yet are excluded. The `novels_root` constructor parameter is
named after the abstract "novels root" concept; per follow-up 113 the container
wires it to `downloaded_novels/` rather than the retired top-level `novels/`.
"""
from __future__ import annotations

import json
from pathlib import Path

from libs.application.dtos.novel__dto import NovelStatusQdto
from libs.application.mappers.novel__mapper import NovelMapper
from libs.domain.value_objects.novel__valueobject import CANONICAL_NOVELS
from libs.infrastructure.writers.novel__writer import NovelMeta


class NovelQuery:
    def __init__(self, novels_root: Path) -> None:
        self._root = novels_root

    def list(self) -> list[NovelStatusQdto]:
        order = {spec.slug: idx for idx, spec in enumerate(CANONICAL_NOVELS)}
        items: list[NovelStatusQdto] = []
        if not self._root.is_dir():
            return items
        for cat_dir in self._root.iterdir():
            if not cat_dir.is_dir():
                continue
            for novel_dir in cat_dir.iterdir():
                if not novel_dir.is_dir():
                    continue
                meta_path = novel_dir / "_meta.json"
                if not meta_path.is_file():
                    continue
                try:
                    data = json.loads(meta_path.read_text(encoding="utf-8"))
                    meta = NovelMeta.from_json(data)
                except (json.JSONDecodeError, KeyError, OSError):
                    continue
                items.append(NovelMapper.meta_to_qdto(meta))
        items.sort(key=lambda q: order.get(q.slug, 9999))
        return items
