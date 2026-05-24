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
RESOLUTION_OPTIONS: frozenset[str] = frozenset({"normal", "2k", "4k"})
DEFAULT_RESOLUTION: str = "normal"
NOTES_MAX_LEN: int = 500
MIN_BATCH_COUNT: int = 1
MAX_BATCH_COUNT: int = 50

# Per follow-up 100: optional dropdown locks for the 3 feature lines users
# care about most. Each accepts either RANDOM_SENTINEL_VALUES (= use pool) or
# one of the curated Chinese descriptors below. The prompt builder
# (`actor__chinese_prompt.py`) substitutes the locked value verbatim and
# falls back to deterministic pool sampling otherwise.
RANDOM_SENTINEL_VALUES: frozenset[str] = frozenset({"", "__random__", "random", "随机"})
EYES_OPTIONS: frozenset[str] = frozenset(
    {
        "大眼", "细长眼", "圆眼", "杏眼", "桃花眼", "凤眼", "鹿眼",
        "小眼", "丹凤眼", "狐眼", "单眼皮", "双眼皮", "内双", "深邃眼",
    }
)
NOSE_OPTIONS: frozenset[str] = frozenset(
    {
        "高挺", "挺直", "小巧", "翘鼻", "鹰钩", "蒜头", "塌鼻",
        "驼峰鼻", "朝天鼻", "宽鼻", "窄鼻", "圆鼻头", "尖鼻",
    }
)
LIPS_OPTIONS: frozenset[str] = frozenset(
    {
        "樱桃小嘴", "丰唇", "薄唇", "厚唇", "嘟嘟嘴", "上翘嘴角",
        "大嘴", "小嘴", "性感唇", "苹果唇", "嘴角下垂", "棱角分明唇",
    }
)
FACE_OPTIONS: frozenset[str] = frozenset(
    {
        "鹅蛋脸", "瓜子脸", "圆脸", "方脸", "长脸",
        "心形脸", "国字脸", "菱形脸", "倒三角脸",
    }
)
QI_ZHI_OPTIONS: frozenset[str] = frozenset(
    {
        "阳光", "温柔", "清纯", "邻家", "楚楚动人",
        "优雅", "高冷", "冷艳", "神秘", "知性",
        "忧郁", "颓废", "沧桑", "阴鸷", "邪魅",
        "霸气", "不羁", "萌系", "俏皮", "妩媚",
    }
)
SKIN_OPTIONS: frozenset[str] = frozenset(
    {
        "白皙", "小麦色", "古铜色", "瓷白", "象牙白", "蜜糖色",
        "黝黑", "苍白", "红润", "雪白", "焦糖色", "深棕色", "橄榄色", "麦色",
    }
)
BODY_OPTIONS: frozenset[str] = frozenset(
    {
        "高挑修长", "中等匀称", "娇小玲珑", "纤瘦", "丰满", "健硕",
        "高大", "矮小", "魁梧",
        "骨感", "偏瘦", "微胖", "胖", "肥胖", "过度肥胖",
    }
)


def _validate_optional_feature(value: str, options: frozenset[str], name: str) -> None:
    if value in RANDOM_SENTINEL_VALUES:
        return
    if value not in options:
        raise InvalidActorAttributeError(
            f"{name}={value!r} not in {sorted(options)} (or one of {sorted(RANDOM_SENTINEL_VALUES)})"
        )


@dataclass(frozen=True)
class ActorAttrs:
    ethnicity: str
    gender: str
    age_range: str
    look: str
    notes: str = ""
    # Per follow-up 100: optional user-locked feature descriptors. Each
    # defaults to "" (treated as random pool sample by the prompt builder).
    eyes: str = ""
    nose: str = ""
    lips: str = ""
    face: str = ""
    skin: str = ""
    body: str = ""
    qi_zhi: str = ""

    def validate(self) -> None:
        if self.ethnicity not in ETHNICITY_OPTIONS:
            raise InvalidActorAttributeError(f"ethnicity={self.ethnicity!r} not in schema")
        if self.gender not in GENDER_OPTIONS:
            raise InvalidActorAttributeError(f"gender={self.gender!r} not in schema")
        if self.age_range not in AGE_RANGE_OPTIONS:
            raise InvalidActorAttributeError(f"age_range={self.age_range!r} not in schema")
        if self.look not in LOOK_OPTIONS:
            raise InvalidActorAttributeError(f"look={self.look!r} not in schema")
        if len(self.notes) > NOTES_MAX_LEN:
            raise InvalidActorAttributeError(f"notes must be ≤ {NOTES_MAX_LEN} characters")
        _validate_optional_feature(self.eyes, EYES_OPTIONS, "eyes")
        _validate_optional_feature(self.nose, NOSE_OPTIONS, "nose")
        _validate_optional_feature(self.lips, LIPS_OPTIONS, "lips")
        _validate_optional_feature(self.face, FACE_OPTIONS, "face")
        _validate_optional_feature(self.skin, SKIN_OPTIONS, "skin")
        _validate_optional_feature(self.body, BODY_OPTIONS, "body")
        _validate_optional_feature(self.qi_zhi, QI_ZHI_OPTIONS, "qi_zhi")

    def to_dict(self) -> dict[str, str]:
        return {
            "ethnicity": self.ethnicity,
            "gender": self.gender,
            "age_range": self.age_range,
            "look": self.look,
            "notes": self.notes,
            "eyes": self.eyes,
            "nose": self.nose,
            "lips": self.lips,
            "face": self.face,
            "skin": self.skin,
            "body": self.body,
            "qi_zhi": self.qi_zhi,
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
