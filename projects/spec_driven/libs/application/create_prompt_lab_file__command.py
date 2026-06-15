from __future__ import annotations

from libs.application.prompt_lab__cdto import (
    CreatePromptLabFileCdto,
    PromptLabFileResultCdto,
)
from libs.infrastructure.prompt_lab__writer import PromptLabWriter


class CreatePromptLabFileCommand:
    def __init__(self, writer: PromptLabWriter) -> None:
        self._writer = writer

    def execute(self, cdto: CreatePromptLabFileCdto) -> PromptLabFileResultCdto:
        r = self._writer.create(cdto.category, cdto.filename, cdto.content)
        return PromptLabFileResultCdto(
            path=r["path"],
            bytes=r["bytes"],
            mtime=r["mtime"],
            mtime_http=r["mtime_http"],
        )
