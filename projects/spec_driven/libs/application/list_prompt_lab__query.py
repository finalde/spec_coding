from __future__ import annotations

from libs.application.prompt_lab__qdto import PromptLabQdto
from libs.infrastructure.prompt_lab__reader import PromptLabReader


class ListPromptLabQuery:
    def __init__(self, reader: PromptLabReader) -> None:
        self._reader = reader

    def execute(self) -> PromptLabQdto:
        return PromptLabQdto(categories=self._reader.overview())
