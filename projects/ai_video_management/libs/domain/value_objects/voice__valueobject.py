"""VoiceAttrs value object — immutable attributes that identify a generated
voice profile. Pure domain: validation invariants + the closed enums of
acceptable values. No I/O, no framework imports.

Voice pool ships prompt-only (follow-up 115). The on-disk representation
(voice_NNNN.md sidecar + optional voice_NNNN.{mp3,wav,m4a} user-supplied
sample) is the infrastructure's job to materialize; this object is the
canonical in-memory shape of what the user picked.

The archetype enum is intentionally extensible — the 10 starter values
cover xianxia / palace / wuxia genres the project actively produces; new
archetypes land here, no infra change required (variance overlay falls
back to uniform when no `_VOICE_ARCHETYPE_BIAS_ZH` entry exists for an
archetype).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from libs.domain.errors.voice__error import (
    InvalidVoiceAttributeError,
    InvalidVoiceIdError,
)

# Closed enums — the archetype slugs are English (for filesystem + API
# stability); the Chinese display labels live in `ARCHETYPE_LABELS_ZH`
# below so the UI can render the user-facing 中文 name without a lookup
# table sitting on the frontend.
ARCHETYPE_OPTIONS: frozenset[str] = frozenset(
    {
        "effeminate_eunuch",
        "mighty_general",
        "gentle_palace_mistress",
        "aged_master",
        "young_jianghu_swordsman",
        "noble_emperor",
        "cold_assassin",
        "coquettish_concubine",
        "wise_elder_monk",
        "cunning_advisor",
    }
)

ARCHETYPE_LABELS_ZH: dict[str, str] = {
    "effeminate_eunuch": "陰柔太監音",
    "mighty_general": "雄壯將軍音",
    "gentle_palace_mistress": "柔美宮主音",
    "aged_master": "蒼老掌門音",
    "young_jianghu_swordsman": "年輕江湖俠音",
    "noble_emperor": "威嚴帝王音",
    "cold_assassin": "冷峻刺客音",
    "coquettish_concubine": "嬌媚妃嬪音",
    "wise_elder_monk": "慈悲高僧音",
    "cunning_advisor": "陰險謀士音",
}

GENDER_OPTIONS: frozenset[str] = frozenset({"male", "female", "neutral"})

AGE_IMPRESSION_OPTIONS: frozenset[str] = frozenset(
    {"child", "teen", "young_adult", "middle_aged", "elderly"}
)

PACE_OPTIONS: frozenset[str] = frozenset({"slow", "medium", "fast"})

PITCH_REGISTER_OPTIONS: frozenset[str] = frozenset({"low", "mid", "high"})

EMOTION_OPTIONS: frozenset[str] = frozenset(
    {"calm", "authoritative", "playful", "menacing", "mournful",
     "flirtatious", "solemn", "whimsical"}
)

# Free-form Chinese fields are length-bounded; no value-enum.
TONE_MAX_LEN: int = 200
SIGNATURE_INFLECTION_MAX_LEN: int = 200
NOTES_MAX_LEN: int = 500

MIN_BATCH_COUNT: int = 1
MAX_BATCH_COUNT: int = 50

DEFAULT_PACE: str = "medium"
DEFAULT_PITCH_REGISTER: str = "mid"
DEFAULT_EMOTION: str = "calm"

# Audio sample handling (voice writes flow through FR-9v5 multipart upload,
# not through PUT /api/file). The 10 MiB cap is intentionally larger than
# PUT /api/file's 1 MiB cap because audio is naturally bigger than markdown.
AUDIO_EXTENSIONS: frozenset[str] = frozenset({".mp3", ".wav", ".m4a"})
AUDIO_MAX_BYTES: int = 10 * 1024 * 1024

_VOICE_ID_RE = re.compile(r"^voice_\d{4,}$")


@dataclass(frozen=True)
class VoiceAttrs:
    archetype: str
    gender: str
    age_impression: str
    pace: str = DEFAULT_PACE
    pitch_register: str = DEFAULT_PITCH_REGISTER
    emotion_default: str = DEFAULT_EMOTION
    tone: str = ""
    signature_inflection: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.archetype not in ARCHETYPE_OPTIONS:
            raise InvalidVoiceAttributeError(
                f"archetype={self.archetype!r} not in {sorted(ARCHETYPE_OPTIONS)}"
            )
        if self.gender not in GENDER_OPTIONS:
            raise InvalidVoiceAttributeError(f"gender={self.gender!r} not in schema")
        if self.age_impression not in AGE_IMPRESSION_OPTIONS:
            raise InvalidVoiceAttributeError(
                f"age_impression={self.age_impression!r} not in schema"
            )
        if self.pace not in PACE_OPTIONS:
            raise InvalidVoiceAttributeError(f"pace={self.pace!r} not in schema")
        if self.pitch_register not in PITCH_REGISTER_OPTIONS:
            raise InvalidVoiceAttributeError(
                f"pitch_register={self.pitch_register!r} not in schema"
            )
        if self.emotion_default not in EMOTION_OPTIONS:
            raise InvalidVoiceAttributeError(
                f"emotion_default={self.emotion_default!r} not in schema"
            )
        if len(self.tone) > TONE_MAX_LEN:
            raise InvalidVoiceAttributeError(f"tone must be ≤ {TONE_MAX_LEN} characters")
        if len(self.signature_inflection) > SIGNATURE_INFLECTION_MAX_LEN:
            raise InvalidVoiceAttributeError(
                f"signature_inflection must be ≤ {SIGNATURE_INFLECTION_MAX_LEN} characters"
            )
        if len(self.notes) > NOTES_MAX_LEN:
            raise InvalidVoiceAttributeError(f"notes must be ≤ {NOTES_MAX_LEN} characters")


def validate_voice_id(voice_id: str) -> None:
    if not _VOICE_ID_RE.match(voice_id):
        raise InvalidVoiceIdError(f"voice_id={voice_id!r} does not match shape voice_NNNN")


def validate_batch_count(count: int) -> None:
    if not MIN_BATCH_COUNT <= count <= MAX_BATCH_COUNT:
        raise InvalidVoiceAttributeError(
            f"count must be between {MIN_BATCH_COUNT} and {MAX_BATCH_COUNT}, got {count}"
        )


def validate_seeds(seeds: list[int] | None, count: int) -> None:
    if seeds is None:
        return
    if not isinstance(seeds, list) or len(seeds) != count:
        raise InvalidVoiceAttributeError(f"seeds must be a list of length {count}, got {seeds!r}")
    for s in seeds:
        if not isinstance(s, int):
            raise InvalidVoiceAttributeError(f"seeds must be all int, got {seeds!r}")


def validate_audio_extension(filename: str) -> str:
    """Return the normalized extension (lowercased, including dot) or raise."""
    if not isinstance(filename, str) or "." not in filename:
        raise InvalidVoiceAttributeError("audio filename has no extension")
    ext = "." + filename.rsplit(".", 1)[-1].lower()
    if ext not in AUDIO_EXTENSIONS:
        raise InvalidVoiceAttributeError(
            f"audio extension {ext!r} not in {sorted(AUDIO_EXTENSIONS)}"
        )
    return ext
