"""BgmAttrs value object — immutable attributes that identify a generated
background-music track. Pure domain: validation invariants + the closed
enums of acceptable values. No I/O, no framework imports.

The shared BGM library mirrors the actor / voice library pattern: each
track gets a globally-unique `bgm_NNNN` id (unique ACROSS categories, so a
drama can reference a track by bare id like an actor) and lives on disk at
`ai_videos/_bgm/{category}/bgm_NNNN/`. `category` is both a folder layer
and a metadata field so the UI can filter by it.

The on-disk representation (the `{category}/` folder layer, the `.md`
sidecar table, the `.mp3` audio) is the infrastructure's job to
materialise; this object is the canonical in-memory shape of what the user
picked.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from libs.domain.errors.bgm__error import (
    InvalidBgmAttributeError,
    InvalidBgmIdError,
)

# Closed emotion-category enum. The slug is English (filesystem + API
# stability); it is BOTH the `{category}/` folder layer and a metadata
# field. Chinese display labels live in `CATEGORY_LABELS_ZH` so the UI
# renders the 中文 name without a frontend lookup table. Sourced from
# short-drama beat-scoring practice (findings: bgm-metadata-cue).
CATEGORY_OPTIONS: frozenset[str] = frozenset(
    {
        "tension",
        "combat",
        "climax_hype",
        "faceslap",
        "tragic",
        "warm",
        "romance_pain",
        "suspense",
        "daily",
        "flashback",
        "theme_open",
        "system_cue",
    }
)

CATEGORY_LABELS_ZH: dict[str, str] = {
    "tension": "紧张对峙",
    "combat": "打斗",
    "climax_hype": "高燃爽点",
    "faceslap": "打脸爽感",
    "tragic": "悲情",
    "warm": "温情",
    "romance_pain": "虐恋",
    "suspense": "悬疑",
    "daily": "日常",
    "flashback": "回忆",
    "theme_open": "片头主题",
    "system_cue": "系统提示音",
}

# bpm / intensity / duration bounds. Per stage-5 sign-off the user accepts
# NO hard upper bound on duration (self-hosted, single-user, no concurrency
# — the GPU-time risk is observe-only), so `duration` only needs a positive
# floor. bpm + intensity stay bounded to keep the prompt sensible.
MIN_BPM: int = 40
MAX_BPM: int = 220
MIN_INTENSITY: int = 1
MAX_INTENSITY: int = 5
MIN_DURATION_SECONDS: int = 1
MOOD_MAX_LEN: int = 200
INSTRUMENTS_MAX_LEN: int = 200
NOTES_MAX_LEN: int = 500

MIN_BATCH_COUNT: int = 1
MAX_BATCH_COUNT: int = 50

# Recorded into every sidecar; constant for the Stable Audio backend chosen
# at stage 5 (open weights, Stability AI Community License — commercial-safe
# under the $1M-revenue ceiling).
DEFAULT_GENERATOR: str = "stable_audio"
DEFAULT_MODEL: str = "stable-audio-open-1.0"
DEFAULT_LICENSE: str = "Stability AI Community License"

_BGM_ID_RE = re.compile(r"^bgm_\d{4,}$")


@dataclass(frozen=True)
class BgmAttrs:
    category: str
    mood: str = ""
    bpm: int = 90
    duration: int = 30
    loopable: bool = False
    intensity: int = 3
    instruments: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.category not in CATEGORY_OPTIONS:
            raise InvalidBgmAttributeError(
                f"category={self.category!r} not in {sorted(CATEGORY_OPTIONS)}"
            )
        if not isinstance(self.bpm, int) or isinstance(self.bpm, bool):
            raise InvalidBgmAttributeError(f"bpm must be int, got {self.bpm!r}")
        if not MIN_BPM <= self.bpm <= MAX_BPM:
            raise InvalidBgmAttributeError(
                f"bpm must be between {MIN_BPM} and {MAX_BPM}, got {self.bpm}"
            )
        if not isinstance(self.duration, int) or isinstance(self.duration, bool):
            raise InvalidBgmAttributeError(f"duration must be int, got {self.duration!r}")
        if self.duration < MIN_DURATION_SECONDS:
            raise InvalidBgmAttributeError(
                f"duration must be ≥ {MIN_DURATION_SECONDS}s, got {self.duration}"
            )
        if not isinstance(self.loopable, bool):
            raise InvalidBgmAttributeError(f"loopable must be bool, got {self.loopable!r}")
        if not isinstance(self.intensity, int) or isinstance(self.intensity, bool):
            raise InvalidBgmAttributeError(f"intensity must be int, got {self.intensity!r}")
        if not MIN_INTENSITY <= self.intensity <= MAX_INTENSITY:
            raise InvalidBgmAttributeError(
                f"intensity must be between {MIN_INTENSITY} and {MAX_INTENSITY}, got {self.intensity}"
            )
        if len(self.mood) > MOOD_MAX_LEN:
            raise InvalidBgmAttributeError(f"mood must be ≤ {MOOD_MAX_LEN} characters")
        if len(self.instruments) > INSTRUMENTS_MAX_LEN:
            raise InvalidBgmAttributeError(
                f"instruments must be ≤ {INSTRUMENTS_MAX_LEN} characters"
            )
        if len(self.notes) > NOTES_MAX_LEN:
            raise InvalidBgmAttributeError(f"notes must be ≤ {NOTES_MAX_LEN} characters")


def validate_bgm_id(bgm_id: str) -> None:
    if not _BGM_ID_RE.match(bgm_id):
        raise InvalidBgmIdError(f"bgm_id={bgm_id!r} does not match shape bgm_NNNN")


def validate_category(category: str) -> None:
    if category not in CATEGORY_OPTIONS:
        raise InvalidBgmAttributeError(
            f"category={category!r} not in {sorted(CATEGORY_OPTIONS)}"
        )


def validate_batch_count(count: int) -> None:
    if not MIN_BATCH_COUNT <= count <= MAX_BATCH_COUNT:
        raise InvalidBgmAttributeError(
            f"count must be between {MIN_BATCH_COUNT} and {MAX_BATCH_COUNT}, got {count}"
        )


def validate_seeds(seeds: list[int] | None, count: int) -> None:
    if seeds is None:
        return
    if not isinstance(seeds, list) or len(seeds) != count:
        raise InvalidBgmAttributeError(f"seeds must be a list of length {count}, got {seeds!r}")
    for s in seeds:
        if not isinstance(s, int) or isinstance(s, bool):
            raise InvalidBgmAttributeError(f"seeds must be all int, got {seeds!r}")
