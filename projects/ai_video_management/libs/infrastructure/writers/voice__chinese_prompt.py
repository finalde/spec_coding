"""Local Chinese-prompt composition for the voice pool.

Follow-up 115: voice generation is purely local text composition. This
module assembles a natural-language Chinese 配音 prompt from the user's
chosen attrs + seed + variance pools. The prompt is what the user pastes
into an external AI voice model (ElevenLabs / MiniMax / CosyVoice / OpenAI
TTS / etc.) — this module never speaks to the network.

Mirrors the actor pool's `actor__chinese_prompt.py` archetype-bias overlay
pattern (`_LOOK_FEATURE_BIAS_ZH`) — voice archetypes weight specific
descriptor pools so 陰柔太監音 vs 雄壯將軍音 produce systematically
different prompts even when other fields match.

Hard invariant: no `httpx`, no `requests`, no `urllib`, no literal `https://`
URL anywhere in this file. Enforced by `tests/test_voice_no_outbound_http.py`
at critical severity.
"""
from __future__ import annotations

import random
from typing import Any

from libs.domain.value_objects.voice__valueobject import ARCHETYPE_LABELS_ZH

# ---------------------------------------------------------------------------
# Variance pools — every entry is a Chinese descriptor fragment.
# ---------------------------------------------------------------------------

_TIMBRE_POOL: tuple[str, ...] = (
    "音色清亮通透", "音色低沉浑厚", "音色绵柔温润", "音色尖细高亢", "音色沙哑略带磁性",
    "音色干净清爽", "音色苍老粗粝", "音色嗓音偏宽", "音色嗓音偏窄", "音色金属质感",
    "音色丝绸般顺滑", "音色木质温暖", "音色玉石般清越", "音色钟磬般共鸣",
    "音色略带气音", "音色厚实如鼓",
)

_BREATH_QUALITY_POOL: tuple[str, ...] = (
    "气息绵长平稳", "气息短促有力", "气息深沉如井", "气息轻柔若羽",
    "气息浑厚自胸腔涌出", "气息从丹田发力", "气息浮于喉间",
    "换气几不可闻", "换气短促分明", "气息浸润每一字",
)

_RESONANCE_POOL: tuple[str, ...] = (
    "胸腔共鸣饱满", "头腔共鸣明亮", "鼻腔共鸣偏重", "口腔共鸣清晰",
    "咽喉共鸣松弛", "腹腔共鸣低沉", "共鸣点偏前",
    "共鸣点偏后", "共鸣点居中", "共鸣层次丰富",
)

_PITCH_DESCRIPTOR_POOL: tuple[str, ...] = (
    "音调起伏自然", "音调平稳如线", "音调婉转似溪", "音调骤升骤降",
    "音调悠扬婉转", "音调直白平铺", "音调跌宕起伏",
    "句末上扬带询问意", "句末下沉显笃定", "句首蓄势后徐徐展开",
)

_SPEED_DESCRIPTOR_POOL: tuple[str, ...] = (
    "语速从容不迫", "语速急促紧凑", "语速忽快忽慢", "语速字字分明",
    "语速绵密连贯", "语速沉稳如老成",
)

_ACCENT_DIALECT_POOL: tuple[str, ...] = (
    "标准普通话", "略带京腔尾音", "略带江南吴侬软语韵味", "略带北方儿化音",
    "古韵腔调", "戏曲念白韵味", "舞台朗诵腔",
    "市井口语腔", "书生雅言腔", "庙堂正音",
)

_EMOTION_TINT_POOL: tuple[str, ...] = (
    "字里行间带笑意", "字里行间含怒意", "字里行间藏哀伤", "字里行间露怯意",
    "字里行间显威严", "字里行间露媚态", "字里行间藏杀机",
    "情绪克制内敛", "情绪外放奔涌", "情绪起伏分明", "情绪压抑暗涌",
)

_SIGNATURE_INFLECTION_POOL: tuple[str, ...] = (
    "尾音微颤", "尾音骤断", "尾音拖长", "尾音上挑",
    "字头清晰", "字头含糊", "重音落在词首", "重音落在词尾",
    "停顿恰到好处", "语气词偏多", "断句锐利", "断句温柔",
    "卷舌偏重", "齿音清脆",
)

_VIBE_POOL: tuple[str, ...] = (
    "整体气质清冷孤傲", "整体气质温润如玉", "整体气质阴鸷狠厉",
    "整体气质雍容华贵", "整体气质质朴憨厚", "整体气质狡黠机敏",
    "整体气质沉稳如山", "整体气质潇洒不羁", "整体气质媚意天成",
    "整体气质悲悯慈祥",
)

_GENRE_HINT_POOL: tuple[str, ...] = (
    "适合古风仙侠 / 玄幻题材", "适合宫廷权谋 / 历史正剧",
    "适合武侠江湖 / 快意恩仇", "适合悬疑探案 / 冷峻独白",
    "适合甜宠浪漫 / 轻喜剧", "适合修真问道 / 散仙独白",
    "适合朝堂奏对 / 庄重场景", "适合江湖夜话 / 闲谈闲叙",
    "适合家国情仇 / 庙堂之上", "适合儿女情长 / 闺阁之内",
)

# ---------------------------------------------------------------------------
# Archetype-bias overlay — parallel to `_LOOK_FEATURE_BIAS_ZH` in
# actor__chinese_prompt.py. Each archetype weights specific pool indices so
# the generated prompt sits squarely inside its archetype vibe.
# Archetypes not listed get uniform random over the full pool (no overlay).
# ---------------------------------------------------------------------------

_VOICE_ARCHETYPE_BIAS_ZH: dict[str, dict[str, tuple[int, ...]]] = {
    "effeminate_eunuch": {
        # 阴柔 / 尖细 / 鼻音重 / 略带气音
        "timbre":      (3, 4, 10, 14),
        "breath":      (3, 7, 9),
        "resonance":   (1, 2, 6),
        "pitch":       (2, 4, 7),
        "speed":       (2, 4),
        "accent":      (3, 5, 6),
        "emotion":     (5, 6, 7),
        "inflection":  (0, 2, 3, 10, 12, 13),
        "vibe":        (2, 5, 8),
    },
    "mighty_general": {
        # 浑厚 / 鼓声 / 胸腔共鸣 / 重音落字首
        "timbre":      (1, 5, 11, 15),
        "breath":      (2, 4, 5),
        "resonance":   (0, 5, 8),
        "pitch":       (1, 5, 8),
        "speed":       (0, 3, 5),
        "accent":      (9, 6),
        "emotion":     (4, 7, 8),
        "inflection":  (4, 6, 10),
        "vibe":        (6, 5),
    },
    "gentle_palace_mistress": {
        # 绵柔 / 婉转 / 江南软语 / 媚意
        "timbre":      (2, 6, 10, 11),
        "breath":      (3, 6, 9),
        "resonance":   (3, 6, 9),
        "pitch":       (2, 3, 4),
        "speed":       (0, 1),
        "accent":      (2, 7),
        "emotion":     (5, 7, 9),
        "inflection":  (2, 3, 11, 13),
        "vibe":        (3, 8),
    },
    "aged_master": {
        # 苍老 / 沙哑 / 缓慢 / 古韵
        "timbre":      (4, 6, 7),
        "breath":      (2, 7, 8, 9),
        "resonance":   (4, 7),
        "pitch":       (1, 5, 8),
        "speed":       (0, 5),
        "accent":      (4, 8, 9),
        "emotion":     (7, 9),
        "inflection":  (2, 8, 11),
        "vibe":        (6, 7, 9),
    },
    "young_jianghu_swordsman": {
        # 清亮 / 爽利 / 潇洒不羁
        "timbre":      (0, 5, 8),
        "breath":      (1, 4, 5),
        "resonance":   (0, 1, 3),
        "pitch":       (0, 3, 6),
        "speed":       (1, 3, 4),
        "accent":      (0, 4, 7),
        "emotion":     (0, 8, 10),
        "inflection":  (3, 4, 7, 11),
        "vibe":        (7, 5),
    },
    "noble_emperor": {
        # 沉稳 / 雍容 / 庙堂正音 / 字字千钧
        "timbre":      (1, 5, 11, 13, 15),
        "breath":      (0, 2, 5),
        "resonance":   (0, 5, 8),
        "pitch":       (1, 8),
        "speed":       (0, 3, 5),
        "accent":      (9, 4),
        "emotion":     (4, 7, 8, 10),
        "inflection":  (4, 6, 8, 10),
        "vibe":        (3, 6),
    },
    "cold_assassin": {
        # 冷峻 / 干净清爽 / 杀机内敛 / 字头锐利
        "timbre":      (0, 5, 9, 14),
        "breath":      (1, 4, 7),
        "resonance":   (3, 5, 8),
        "pitch":       (1, 5, 8),
        "speed":       (1, 3, 5),
        "accent":      (0, 5),
        "emotion":     (6, 7, 10),
        "inflection":  (1, 4, 10, 11),
        "vibe":        (0, 2),
    },
    "coquettish_concubine": {
        # 嬌媚 / 气音偏重 / 媚态 / 尾音上挑
        "timbre":      (10, 11, 14),
        "breath":      (3, 6, 9),
        "resonance":   (2, 3, 6),
        "pitch":       (2, 3, 7),
        "speed":       (0, 1),
        "accent":      (1, 2, 7),
        "emotion":     (5, 9),
        "inflection":  (2, 3, 6, 11, 13),
        "vibe":        (8, 3),
    },
    "wise_elder_monk": {
        # 慈悲 / 平稳 / 钟磬般共鸣 / 沉缓
        "timbre":      (2, 11, 13),
        "breath":      (0, 2, 5, 9),
        "resonance":   (0, 1, 4, 5),
        "pitch":       (1, 5, 9),
        "speed":       (0, 5),
        "accent":      (4, 9),
        "emotion":     (7, 9, 10),
        "inflection":  (2, 6, 8, 11),
        "vibe":        (9, 1),
    },
    "cunning_advisor": {
        # 狡黠 / 略带笑意 / 重音落词尾 / 城府深
        "timbre":      (5, 8, 10),
        "breath":      (1, 4, 7),
        "resonance":   (2, 3, 6),
        "pitch":       (4, 6, 9),
        "speed":       (1, 2, 4),
        "accent":      (5, 6, 7),
        "emotion":     (0, 6, 10),
        "inflection":  (5, 7, 9, 11),
        "vibe":        (5, 2, 6),
    },
}

# Fallthrough chance: even with a biased pool, leave room for a wild-card
# pick so two consecutive same-archetype slots are not identical text.
_WILDCARD_PROBABILITY: float = 0.25


def _pick_biased(
    rng: random.Random, pool: tuple[str, ...], bias_indices: tuple[int, ...] | None
) -> str:
    """Pick from the biased subset most of the time; occasionally fall through
    to the full pool. Mirrors the actor side's `_pick_biased` (follow-up 077)."""
    if bias_indices and rng.random() > _WILDCARD_PROBABILITY:
        # Bias indices may overflow the actual pool length if a pool changes
        # later — guard with modulo so the prompt builder never IndexErrors.
        safe = tuple(pool[i % len(pool)] for i in bias_indices if 0 <= i < len(pool))
        if safe:
            return rng.choice(safe)
    return rng.choice(pool)


def _pick_n_biased(
    rng: random.Random,
    pool: tuple[str, ...],
    bias_indices: tuple[int, ...] | None,
    n: int,
) -> list[str]:
    """Pick `n` distinct values, biased when an overlay is present."""
    seen: list[str] = []
    attempts = 0
    n = min(n, len(pool))
    while len(seen) < n and attempts < n * 6:
        candidate = _pick_biased(rng, pool, bias_indices)
        if candidate not in seen:
            seen.append(candidate)
        attempts += 1
    return seen


def build_voice_prompt(attrs_dict: dict[str, Any], seed: int) -> str:
    """Build the user-facing Chinese 配音 prompt for one voice profile.

    The prompt is structured Chinese — labeled lines a voice-model UI can
    parse visually and a human can paste verbatim. NO model-specific JSON
    or instruct sigils; this string targets any AI voice model.
    """
    archetype = str(attrs_dict.get("archetype", ""))
    gender = str(attrs_dict.get("gender", ""))
    age_impression = str(attrs_dict.get("age_impression", ""))
    pace = str(attrs_dict.get("pace", "medium"))
    pitch_register = str(attrs_dict.get("pitch_register", "mid"))
    emotion_default = str(attrs_dict.get("emotion_default", "calm"))
    tone = str(attrs_dict.get("tone", ""))
    signature_inflection = str(attrs_dict.get("signature_inflection", ""))
    notes = str(attrs_dict.get("notes", ""))

    label = ARCHETYPE_LABELS_ZH.get(archetype, archetype)
    bias = _VOICE_ARCHETYPE_BIAS_ZH.get(archetype, {})
    rng = random.Random(seed)

    timbre_picks = _pick_n_biased(rng, _TIMBRE_POOL, bias.get("timbre"), 2)
    breath_picks = _pick_n_biased(rng, _BREATH_QUALITY_POOL, bias.get("breath"), 2)
    resonance_picks = _pick_n_biased(rng, _RESONANCE_POOL, bias.get("resonance"), 2)
    pitch_picks = _pick_n_biased(rng, _PITCH_DESCRIPTOR_POOL, bias.get("pitch"), 2)
    speed_picks = _pick_n_biased(rng, _SPEED_DESCRIPTOR_POOL, bias.get("speed"), 1)
    accent_picks = _pick_n_biased(rng, _ACCENT_DIALECT_POOL, bias.get("accent"), 1)
    emotion_picks = _pick_n_biased(rng, _EMOTION_TINT_POOL, bias.get("emotion"), 2)
    inflection_picks = _pick_n_biased(rng, _SIGNATURE_INFLECTION_POOL, bias.get("inflection"), 3)
    vibe_pick = _pick_biased(rng, _VIBE_POOL, bias.get("vibe"))
    genre_hint = rng.choice(_GENRE_HINT_POOL)

    age_label = _AGE_LABEL_ZH.get(age_impression, age_impression)
    gender_label = _GENDER_LABEL_ZH.get(gender, gender)
    pace_label = _PACE_LABEL_ZH.get(pace, pace)
    pitch_label = _PITCH_LABEL_ZH.get(pitch_register, pitch_register)
    emotion_label = _EMOTION_LABEL_ZH.get(emotion_default, emotion_default)

    tone_line = f"音色描述：{tone}" if tone else ""
    sig_line = f"标志性发声：{signature_inflection}" if signature_inflection else ""
    notes_line = f"附加备注：{notes}" if notes else ""

    sections = [
        f"角色定位：{label}（{gender_label} / {age_label}）",
        f"音色：{'，'.join(timbre_picks)}",
        f"气息：{'，'.join(breath_picks)}",
        f"共鸣：{'，'.join(resonance_picks)}",
        f"音调：{'，'.join(pitch_picks)}（基础音区 {pitch_label}）",
        f"语速：{'，'.join(speed_picks)}（基础语速 {pace_label}）",
        f"腔调：{'，'.join(accent_picks)}",
        f"情绪：{'，'.join(emotion_picks)}（默认情绪 {emotion_label}）",
        f"发声细节：{'，'.join(inflection_picks)}",
        f"整体气质：{vibe_pick}",
        f"题材建议：{genre_hint}",
    ]
    if tone_line:
        sections.append(tone_line)
    if sig_line:
        sections.append(sig_line)
    if notes_line:
        sections.append(notes_line)

    sections.append(
        "使用提示：将本段提示词粘贴入任意 AI 配音模型（ElevenLabs / MiniMax / "
        "CosyVoice / OpenAI TTS 等），让模型据此塑造声线后再朗读你的台词。"
    )
    return "\n".join(sections)


# Display-label helpers used when assembling the prompt text.
_AGE_LABEL_ZH: dict[str, str] = {
    "child": "儿童",
    "teen": "少年",
    "young_adult": "青年",
    "middle_aged": "中年",
    "elderly": "老年",
}

_GENDER_LABEL_ZH: dict[str, str] = {
    "male": "男声",
    "female": "女声",
    "neutral": "中性嗓音",
}

_PACE_LABEL_ZH: dict[str, str] = {"slow": "缓慢", "medium": "中速", "fast": "急快"}

_PITCH_LABEL_ZH: dict[str, str] = {"low": "低音区", "mid": "中音区", "high": "高音区"}

_EMOTION_LABEL_ZH: dict[str, str] = {
    "calm": "平静",
    "authoritative": "威严",
    "playful": "俏皮",
    "menacing": "阴狠",
    "mournful": "哀婉",
    "flirtatious": "撩拨",
    "solemn": "庄重",
    "whimsical": "随性",
}
