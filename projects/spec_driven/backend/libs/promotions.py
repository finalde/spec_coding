"""
promotions — POST /api/promote, DELETE /api/promote (FR-13, FR-14).

Block format inside `<stage>/promoted.md`:

    <!-- promoted-item: ${item_id} -->
    {item_text verbatim}
    <!-- /promoted-item: ${item_id} -->

The delimiter strong-fences the body so an item_text can contain `##` or other
markdown without prematurely starting a new block (Group 5.5 in unit_tests.md).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ALLOWED_STAGE_FOLDERS = frozenset({"interview", "findings", "final_specs", "validation"})
PROMOTED_HEADER = "# Promoted items\n\n_INPUT to regeneration. See CLAUDE.md → Pinned items survive regeneration._\n\n"


def _open_marker(item_id: str) -> str:
    return f"<!-- promoted-item: {item_id} -->"


def _close_marker(item_id: str) -> str:
    return f"<!-- /promoted-item: {item_id} -->"


@dataclass(frozen=True)
class PromotedItem:
    item_id: str
    body: str


class PromotionError(Exception):
    pass


@dataclass(frozen=True)
class Promotions:
    repo_root: Path

    def _stage_path(self, project_type: str, project_name: str, stage_folder: str) -> Path:
        if stage_folder not in ALLOWED_STAGE_FOLDERS:
            raise PromotionError(f"stage_folder not in allowlist: {stage_folder!r}")
        if "/" in project_type or "\\" in project_type or ".." in project_type:
            raise PromotionError("invalid project_type")
        if "/" in project_name or "\\" in project_name or ".." in project_name:
            raise PromotionError("invalid project_name")
        path = self.repo_root / "specs" / project_type / project_name / stage_folder / "promoted.md"
        try:
            path.relative_to(self.repo_root)
        except ValueError as e:
            raise PromotionError("path escape") from e
        return path

    def post(
        self,
        project_type: str,
        project_name: str,
        stage_folder: str,
        source_file: str,
        item_id: str,
        item_text: str,
    ) -> dict:
        if not item_id or not item_id.strip():
            raise PromotionError("item_id required")
        if not item_text or not item_text.strip():
            raise PromotionError("item_text required")

        path = self._stage_path(project_type, project_name, stage_folder)
        path.parent.mkdir(parents=True, exist_ok=True)

        existing = path.read_text(encoding="utf-8") if path.is_file() else PROMOTED_HEADER
        items = parse_promoted_text(existing)

        block = (
            f"{_open_marker(item_id)}\n"
            f"<!-- source: {source_file} -->\n"
            f"{item_text.rstrip()}\n"
            f"{_close_marker(item_id)}\n"
        )

        replaced = False
        for i, it in enumerate(items):
            if it.item_id == item_id:
                items[i] = PromotedItem(item_id=item_id, body=block)
                replaced = True
                break
        if not replaced:
            items.append(PromotedItem(item_id=item_id, body=block))

        out = [PROMOTED_HEADER]
        for it in items:
            out.append(it.body if it.body.startswith("<!-- promoted-item:") else self._wrap(it))
            out.append("\n")
        path.write_text("".join(out), encoding="utf-8")

        return {"status": "pinned" if not replaced else "replaced", "item_id": item_id}

    @staticmethod
    def _wrap(it: PromotedItem) -> str:
        return f"{_open_marker(it.item_id)}\n{it.body.rstrip()}\n{_close_marker(it.item_id)}\n"

    def delete(
        self,
        project_type: str,
        project_name: str,
        stage_folder: str,
        item_id: str,
    ) -> dict:
        path = self._stage_path(project_type, project_name, stage_folder)
        if not path.is_file():
            raise PromotionError("promoted.md does not exist")

        text = path.read_text(encoding="utf-8")
        items = parse_promoted_text(text)
        kept = [it for it in items if it.item_id != item_id]
        if len(kept) == len(items):
            raise PromotionError(f"item_id not found: {item_id!r}")

        out = [PROMOTED_HEADER]
        for it in kept:
            out.append(it.body if it.body.startswith("<!-- promoted-item:") else self._wrap(it))
            out.append("\n")
        path.write_text("".join(out), encoding="utf-8")
        return {"status": "unpinned", "item_id": item_id}


_BLOCK_RE = re.compile(
    r"<!-- promoted-item: (?P<id>[^ ]+) -->\n(?P<body>.*?)\n<!-- /promoted-item: (?P=id) -->\n?",
    re.DOTALL,
)


def parse_promoted_text(text: str) -> list[PromotedItem]:
    items: list[PromotedItem] = []
    for m in _BLOCK_RE.finditer(text):
        full = m.group(0)
        items.append(PromotedItem(item_id=m.group("id"), body=full))
    return items


def promoted_body_only(text: str) -> str:
    """Return the union of all pin bodies (text between markers), one per pin."""
    out: list[str] = []
    for m in _BLOCK_RE.finditer(text):
        body = m.group("body")
        body = re.sub(r"^<!-- source: [^>]+ -->\n", "", body)
        out.append(body)
    return "\n\n".join(out)
