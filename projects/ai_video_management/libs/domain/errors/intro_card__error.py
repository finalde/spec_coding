"""Named domain errors for character intro-card burn-in (ai_video.md 11d).

Video-path validation reuses the frame aggregate's errors
(InvalidVideoPathError / NotVideoError / VideoNotFoundError /
FfmpegMissingError) — the validation shape is identical.
"""
from __future__ import annotations


class IntroCardDomainError(Exception):
    """Base for intro-card domain errors."""


class IntroCardsFileMissingError(IntroCardDomainError):
    """No `intro_cards.md` found in the shot's episode folder."""


class NoCardForShotError(IntroCardDomainError):
    """`intro_cards.md` exists but has no card for this shot."""


class IntroCardImageMissingError(IntroCardDomainError):
    """A shot's card references a PNG that is not in the library / sandbox."""


class IntroCardBurnFailedError(IntroCardDomainError):
    """ffmpeg ran but failed to produce the carded mp4."""
