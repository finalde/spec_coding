from __future__ import annotations

from libs.application.tree__qdto import TreeQdto
from libs.infrastructure.tree__reader import TreeReader


class GetTreeQuery:
    def __init__(self, reader: TreeReader) -> None:
        self._reader = reader

    def execute(self) -> TreeQdto:
        return TreeQdto(tree=self._reader.build())
