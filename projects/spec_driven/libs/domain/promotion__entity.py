from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Promotion:
    item_id: str
    source_file: str
    item_text: str
