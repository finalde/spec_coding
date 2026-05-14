from __future__ import annotations

from libs.application.promotion__cdto import PromotionResultCdto, RemovePromotionCdto
from libs.infrastructure.promotion__writer import PromotionWriter


class RemovePromotionCommand:
    def __init__(self, writer: PromotionWriter) -> None:
        self._writer = writer

    def execute(self, cdto: RemovePromotionCdto) -> PromotionResultCdto:
        self._writer.remove(
            project_type=cdto.project_type,
            project_name=cdto.project_name,
            stage_folder=cdto.stage_folder,
            item_id=cdto.item_id,
        )
        return PromotionResultCdto(status="ok", item_id=cdto.item_id)
