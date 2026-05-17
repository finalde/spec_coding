"""ActorAttrs value object — immutable attributes that identify the look
of an AI-generated actor face. Pure domain: validation invariants + the
closed enums of acceptable values. No I/O, no framework imports.

The on-disk representation (jpg filename, sidecar md format, folder name)
is the infrastructure's job to materialise; this object is the canonical
in-memory shape of what the user picked.
"""
from __future__ import annotations

from dataclasses import dataclass

from libs.domain.errors.actor__error import InvalidActorAttributeError

ETHNICITY_OPTIONS: frozenset[str] = frozenset(
    {"asian", "east-asian", "south-asian", "caucasian", "african", "latino", "middle-eastern", "mixed"}
)
GENDER_OPTIONS: frozenset[str] = frozenset({"male", "female"})
AGE_RANGE_OPTIONS: frozenset[str] = frozenset({"18-25", "26-35", "36-50", "51-65", "65+"})
LOOK_OPTIONS: frozenset[str] = frozenset(
    {
        # Original 8 physical-appearance values.
        "handsome", "beautiful", "cute", "mature", "rugged", "soft", "aristocratic", "fierce",
        # Per follow-up 064: 5 character-archetype-flavored values.
        # MUST stay in sync with `libs/infrastructure/writers/actor__writer.py::LOOK_OPTIONS`
        # — both enums are checked at different layers (domain validate() +
        # infra _validate_attrs); a mismatch produces a confusing
        # 400 invalid_attribute on the new values.
        "righteous", "sinister", "seductive", "cunning", "innocent",
    }
)
STYLE_OPTIONS: frozenset[str] = frozenset(
    {"modern-casual", "period-ancient-china", "period-western", "business", "streetwear", "sci-fi", "fantasy"}
)
RESOLUTION_OPTIONS: frozenset[str] = frozenset({"normal", "2k", "4k"})
DEFAULT_RESOLUTION: str = "normal"
NOTES_MAX_LEN: int = 500
MIN_BATCH_COUNT: int = 1
MAX_BATCH_COUNT: int = 50


@dataclass(frozen=True)
class ActorAttrs:
    ethnicity: str
    gender: str
    age_range: str
    look: str
    style: str
    notes: str = ""

    def validate(self) -> None:
        if self.ethnicity not in ETHNICITY_OPTIONS:
            raise InvalidActorAttributeError(f"ethnicity={self.ethnicity!r} not in schema")
        if self.gender not in GENDER_OPTIONS:
            raise InvalidActorAttributeError(f"gender={self.gender!r} not in schema")
        if self.age_range not in AGE_RANGE_OPTIONS:
            raise InvalidActorAttributeError(f"age_range={self.age_range!r} not in schema")
        if self.look not in LOOK_OPTIONS:
            raise InvalidActorAttributeError(f"look={self.look!r} not in schema")
        if self.style not in STYLE_OPTIONS:
            raise InvalidActorAttributeError(f"style={self.style!r} not in schema")
        if len(self.notes) > NOTES_MAX_LEN:
            raise InvalidActorAttributeError(f"notes must be ≤ {NOTES_MAX_LEN} characters")

    def to_dict(self) -> dict[str, str]:
        return {
            "ethnicity": self.ethnicity,
            "gender": self.gender,
            "age_range": self.age_range,
            "look": self.look,
            "style": self.style,
            "notes": self.notes,
        }


def validate_batch_count(count: int) -> None:
    if not MIN_BATCH_COUNT <= count <= MAX_BATCH_COUNT:
        raise InvalidActorAttributeError(
            f"count must be between {MIN_BATCH_COUNT} and {MAX_BATCH_COUNT}, got {count}"
        )


def validate_resolution(resolution: str) -> None:
    if resolution not in RESOLUTION_OPTIONS:
        raise InvalidActorAttributeError(
            f"resolution={resolution!r} not in {sorted(RESOLUTION_OPTIONS)}"
        )


def validate_seeds(seeds: list[int] | None, count: int) -> None:
    if seeds is None:
        return
    if not isinstance(seeds, list) or len(seeds) != count:
        raise InvalidActorAttributeError(f"seeds must be a list of length {count}, got {seeds!r}")
    for s in seeds:
        if not isinstance(s, int):
            raise InvalidActorAttributeError(f"seeds must be all int, got {seeds!r}")
