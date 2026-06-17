"""Stable Audio prompt composition for BGM tracks.

Each of the 12 emotion categories maps to a default English prompt template
(genre + instrumentation + mood register). The user's per-track attrs (mood
override, bpm, intensity, instruments) fill the remaining slots. Stable
Audio is text-conditioned and instrumental by default, which fits BGM (no
vocals). Output is a single English prompt string the generation subprocess
passes to `tools/stableaudio_gen.py`.

Deterministic: same (attrs, seed) → same prompt. The seed only varies the
intensity-adjective draw so two tracks in the same category aren't byte
identical; the audio-side seed reproduction is best-effort (stage-5 note).
"""
from __future__ import annotations

import random
from typing import Any

# Base genre + instrumentation + mood per category. The trailing
# ", instrumental, no vocals" is appended once at assembly time.
_CATEGORY_TEMPLATE: dict[str, str] = {
    "tension": "tense cinematic confrontation, low strings and timpani, staccato pulsing ostinato, dark suspended harmony",
    "combat": "high-energy action combat score, driving percussion, aggressive brass stabs, fast taiko and orchestral hits",
    "climax_hype": "epic uplifting climax, soaring strings and brass, triumphant choir-like swell, powerful cinematic build",
    "faceslap": "smug victorious turnaround sting, punchy brass and synth bass, cocky strutting groove, satisfying payoff accent",
    "tragic": "mournful sorrowful theme, solo cello and piano, aching legato strings, slow grieving lament",
    "warm": "warm tender heartfelt theme, soft piano and acoustic guitar, gentle strings, intimate comforting mood",
    "romance_pain": "bittersweet tragic-love theme, yearning solo violin and piano, delicate aching melody, melancholic romance",
    "suspense": "eerie suspenseful underscore, sparse pizzicato strings, ticking clock percussion, unsettling held tones",
    "daily": "light casual slice-of-life background, mellow acoustic guitar and soft keys, relaxed easygoing groove",
    "flashback": "nostalgic dreamy flashback, hazy reverb piano and pad, wistful music-box motif, distant reflective mood",
    "theme_open": "bold memorable opening theme, full cinematic orchestra, strong signature melody, confident main-title energy",
    "system_cue": "short clean UI notification cue, bright synth bells and soft chime, neutral game-system stinger",
}

_INTENSITY_ADJ: dict[int, tuple[str, ...]] = {
    1: ("very soft and minimal", "sparse and understated", "gentle and restrained"),
    2: ("soft and subtle", "light and laid-back", "calm and measured"),
    3: ("balanced and moderate", "steady mid-energy", "even and controlled"),
    4: ("strong and driving", "bold and energetic", "intense and forward"),
    5: ("explosive and maximal", "overwhelming and powerful", "full-throttle and huge"),
}


def build_bgm_prompt(attrs: dict[str, Any], seed: int) -> str:
    """Compose the English Stable Audio prompt for one track.

    `attrs` is `asdict(BgmAttrs)`. Category drives the base template; the
    user's free-text `mood` / `instruments` override or extend it; `bpm`
    and an intensity adjective (seed-picked) tune the energy.
    """
    category = str(attrs.get("category", ""))
    base = _CATEGORY_TEMPLATE.get(category, "cinematic instrumental background music")
    rng = random.Random(seed)
    intensity = int(attrs.get("intensity", 3) or 3)
    intensity_adj = rng.choice(_INTENSITY_ADJ.get(intensity, _INTENSITY_ADJ[3]))
    parts: list[str] = [base, intensity_adj]
    mood = str(attrs.get("mood", "") or "").strip()
    if mood:
        parts.append(mood)
    instruments = str(attrs.get("instruments", "") or "").strip()
    if instruments:
        parts.append(instruments)
    bpm = int(attrs.get("bpm", 90) or 90)
    parts.append(f"{bpm} bpm")
    if attrs.get("loopable"):
        parts.append("seamless loop")
    parts.append("instrumental, no vocals")
    return ", ".join(parts)
