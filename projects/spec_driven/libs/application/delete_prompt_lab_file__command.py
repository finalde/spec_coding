from __future__ import annotations

from libs.application.prompt_lab__cdto import (
    DeletePromptLabFileCdto,
    DeletePromptLabResultCdto,
)
from libs.infrastructure.prompt_lab__writer import PromptLabWriter


class DeletePromptLabFileCommand:
    def __init__(self, writer: PromptLabWriter) -> None:
        self._writer = writer

    def execute(self, cdto: DeletePromptLabFileCdto) -> DeletePromptLabResultCdto:
        r = self._writer.delete(cdto.path)
        return DeletePromptLabResultCdto(path=r["path"])
