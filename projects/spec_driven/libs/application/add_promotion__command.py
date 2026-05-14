from __future__ import annotations

from libs.application.promotion__cdto import AddPromotionCdto, PromotionResultCdto
from libs.application.promotion__mapper import PromotionMapper
from libs.infrastructure.promotion__writer import PromotionWriter


class AddPromotionCommand:
    def __init__(self, writer: PromotionWriter) -> None:
        self._writer = writer

    def execute(self, cdto: AddPromotionCdto) -> PromotionResultCdto:
        promotion = PromotionMapper.cdto_to_entity(cdto)
        self._writer.upsert(
            project_type=cdto.project_type,
            project_name=cdto.project_name,
            stage_folder=cdto.stage_folder,
            promotion=promotion,
        )
        return PromotionResultCdto(status="ok", item_id=cdto.item_id)
