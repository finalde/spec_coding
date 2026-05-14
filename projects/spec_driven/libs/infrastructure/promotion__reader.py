from __future__ import annotations

import re
from pathlib import Path

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.promotion__entity import Promotion
from libs.domain.promotion__error import PromotionPathRejected, StageFolderRejected

ALLOWED_STAGE_FOLDERS: frozenset[str] = frozenset(
    {"interview", "findings", "final_specs", "validation"}
)

_PIN_HEADER = re.compile(r"<!--\s*[Pp][Ii][Nn]\s+(?P<attrs>[^>]+?)\s*-->")
_ATTR = re.compile(r"(?P<key>id|source)=(?P<val>[^\s>]+)")


class PromotionReader:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def read(
        self,
        project_type: str,
        project_name: str,
        stage_folder: str,
    ) -> list[Promotion]:
        path = self.promoted_path(project_type, project_name, stage_folder)
        if not path.is_file():
            return []
        return parse_promoted_text(path.read_text(encoding="utf-8"))

    def promoted_path(
        self,
        project_type: str,
        project_name: str,
        stage_folder: str,
    ) -> Path:
        if stage_folder not in ALLOWED_STAGE_FOLDERS:
            raise StageFolderRejected(stage_folder)
        rel = f"specs/{project_type}/{project_name}/{stage_folder}/promoted.md"
        resolved = self._resolver.resolve(rel)
        if resolved is None or not self._exposed.is_inside(rel):
            raise PromotionPathRejected(rel)
        return resolved


def parse_promoted_text(s: str) -> list[Promotion]:
    if not s:
        return []
    headers = list(_PIN_HEADER.finditer(s))
    if not headers:
        return []
    pins: list[Promotion] = []
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
        pins.append(Promotion(item_id=item_id, source_file=source, item_text=body))
    return pins
