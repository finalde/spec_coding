from __future__ import annotations

from libs.application.promotion__cdto import AddPromotionCdto
from libs.domain.promotion__entity import Promotion


class PromotionMapper:
    @staticmethod
    def cdto_to_entity(cdto: AddPromotionCdto) -> Promotion:
        return Promotion(
            item_id=cdto.item_id,
            source_file=cdto.source_file,
            item_text=cdto.item_text,
        )
