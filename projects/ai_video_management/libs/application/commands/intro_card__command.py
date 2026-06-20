"""Intro-card-aggregate command: burn character intro cards (freeze-frame
nameplate) into a shot render. ffmpeg + file I/O live in infrastructure
(IntroCardBurner); card parsing + ASS rendering are domain knowledge.
"""
from __future__ import annotations

from libs.application.dtos.intro_card__dto import BurnIntroCardsResultCdto
from libs.application.mappers.intro_card__mapper import IntroCardMapper
from libs.infrastructure.writers.intro_card__writer import IntroCardBurner


class IntroCardCommand:
    def __init__(self, burner: IntroCardBurner) -> None:
        self._burner = burner

    def burn(self, rel_path: str) -> BurnIntroCardsResultCdto:
        return IntroCardMapper.to_burn_cdto(self._burner.burn(rel_path))
