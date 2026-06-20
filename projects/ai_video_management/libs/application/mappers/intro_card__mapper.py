"""IntroCardMapper — writer-result↔Cdto translation for the card burn."""
from __future__ import annotations

from libs.application.dtos.intro_card__dto import BurnIntroCardsResultCdto
from libs.infrastructure.writers.intro_card__writer import IntroCardBurnResult


class IntroCardMapper:
    @staticmethod
    def to_burn_cdto(r: IntroCardBurnResult) -> BurnIntroCardsResultCdto:
        return BurnIntroCardsResultCdto(
            src_rel=r.src_rel, out_rel=r.out_rel,
            card_count=r.card_count, names=r.names,
        )
