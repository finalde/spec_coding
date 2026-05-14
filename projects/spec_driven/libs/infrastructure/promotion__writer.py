from __future__ import annotations

from pathlib import Path

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.promotion__entity import Promotion
from libs.infrastructure.promotion__reader import PromotionReader

_PROMOTED_HEADER: str = (
    "<!-- spec_driven promoted.md — INPUT to regeneration; pinned items survive read-zero regen. -->\n"
)


class PromotionWriter:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._reader = PromotionReader(exposed, resolver)

    def upsert(
        self,
        project_type: str,
        project_name: str,
        stage_folder: str,
        promotion: Promotion,
    ) -> None:
        path = self._reader.promoted_path(project_type, project_name, stage_folder)
        pins = self._reader.read(project_type, project_name, stage_folder)
        replaced = False
        new_pins: list[Promotion] = []
        for p in pins:
            if p.item_id == promotion.item_id:
                new_pins.append(promotion)
                replaced = True
            else:
                new_pins.append(p)
        if not replaced:
            new_pins.append(promotion)
        self._write(path, new_pins)

    def remove(
        self,
        project_type: str,
        project_name: str,
        stage_folder: str,
        item_id: str,
    ) -> None:
        path = self._reader.promoted_path(project_type, project_name, stage_folder)
        pins = self._reader.read(project_type, project_name, stage_folder)
        kept = [p for p in pins if p.item_id != item_id]
        if kept != pins:
            self._write(path, kept)

    @staticmethod
    def _write(path: Path, pins: list[Promotion]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not pins:
            path.write_text(_PROMOTED_HEADER, encoding="utf-8")
            return
        parts = [_PROMOTED_HEADER]
        for p in pins:
            parts.append(
                f"\n<!-- pin source={p.source_file} id={p.item_id} -->\n{p.item_text.rstrip()}\n"
            )
        path.write_text("".join(parts), encoding="utf-8")
