from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libs.exposed_tree import ExposedTree
from libs.safe_resolve import SafeResolver

ALLOWED_STAGE_FOLDERS: frozenset[str] = frozenset(
    {"interview", "findings", "final_specs", "validation"}
)

_PIN_HEADER = re.compile(
    r"<!--\s*[Pp][Ii][Nn]\s+(?P<attrs>[^>]+?)\s*-->",
)
_ATTR = re.compile(r"(?P<key>id|source)=(?P<val>[^\s>]+)")

_PROMOTED_HEADER: str = (
    "<!-- spec_driven promoted.md — INPUT to regeneration; pinned items survive read-zero regen. -->\n"
)


class StageFolderRejected(Exception):
    pass


class PromotionPathRejected(Exception):
    pass


@dataclass(frozen=True)
class Pin:
    item_id: str
    source_file: str
    item_text: str


class Promotions:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver
        self._root = exposed.root

    def add(
        self,
        project_type: str,
        project_name: str,
        stage_folder: str,
        source_file: str,
        item_id: str,
        item_text: str,
    ) -> dict[str, Any]:
        promoted_path = self._promoted_path(project_type, project_name, stage_folder)
        existing = self._read_text(promoted_path)
        pins = parse_promoted_text(existing)
        replaced = False
        new_pins: list[Pin] = []
        for p in pins:
            if p.item_id == item_id:
                new_pins.append(Pin(item_id=item_id, source_file=source_file, item_text=item_text))
                replaced = True
            else:
                new_pins.append(p)
        if not replaced:
            new_pins.append(Pin(item_id=item_id, source_file=source_file, item_text=item_text))
        self._write_text(promoted_path, _serialize(new_pins))
        return {"status": "ok", "item_id": item_id}

    def remove(
        self,
        project_type: str,
        project_name: str,
        stage_folder: str,
        item_id: str,
    ) -> dict[str, Any]:
        promoted_path = self._promoted_path(project_type, project_name, stage_folder)
        existing = self._read_text(promoted_path)
        pins = parse_promoted_text(existing)
        kept = [p for p in pins if p.item_id != item_id]
        if kept != pins:
            self._write_text(promoted_path, _serialize(kept))
        return {"status": "ok", "item_id": item_id}

    def _promoted_path(self, project_type: str, project_name: str, stage_folder: str) -> Path:
        if stage_folder not in ALLOWED_STAGE_FOLDERS:
            raise StageFolderRejected(stage_folder)
        rel = f"specs/{project_type}/{project_name}/{stage_folder}/promoted.md"
        resolved = self._resolver.resolve(rel)
        if resolved is None or not self._exposed.is_inside(rel):
            raise PromotionPathRejected(rel)
        return resolved

    @staticmethod
    def _read_text(p: Path) -> str:
        if not p.is_file():
            return ""
        return p.read_text(encoding="utf-8")

    @staticmethod
    def _write_text(p: Path, text: str) -> None:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")


def parse_promoted_text(s: str) -> list[Pin]:
    if not s:
        return []
    headers = list(_PIN_HEADER.finditer(s))
    if not headers:
        return []
    pins: list[Pin] = []
    for i, h in enumerate(headers):
        attrs_text = h.group("attrs")
        attrs: dict[str, str] = {}
        for a in _ATTR.finditer(attrs_text):
            attrs[a.group("key")] = a.group("val")
        item_id = attrs.get("id", "").strip()
        source = attrs.get("source", "").strip()
        body_start = h.end()
        body_end = headers[i + 1].start() if i + 1 < len(headers) else len(s)
        body = s[body_start:body_end].strip("\n").rstrip()
        if not item_id and not source and not body:
            continue
        pins.append(Pin(item_id=item_id, source_file=source, item_text=body))
    return pins


def _serialize(pins: list[Pin]) -> str:
    if not pins:
        return _PROMOTED_HEADER
    parts = [_PROMOTED_HEADER]
    for p in pins:
        parts.append(
            f"\n<!-- pin source={p.source_file} id={p.item_id} -->\n{p.item_text.rstrip()}\n"
        )
    return "".join(parts)
