"""BGM prompt composition for ElevenLabs Music.

Each of the 12 emotion categories maps to a rich English description (genre +
instrumentation + mood + dynamics). The user's per-track attrs (mood override,
bpm, intensity, instruments) fill the remaining slots, and a shared structural
scaffold (arrangement, dynamics, production, use-case, constraints) expands the
result into a long, highly-detailed prompt — at least ~1000 characters — that
ElevenLabs Music can act on precisely. The prompt is English (ElevenLabs is
English-trained); the user generates the track there, downloads it, and imports
it via the global Downloads importer.

`build_bgm_prompt` returns the music prompt. `build_bgm_prompt_keyed` prepends
the track id as a leading KEY line so the downloaded file carries the id for
one-click import routing; the local-generation read-back strips that line.

Deterministic: same (attrs, seed) → same prompt.
"""
from __future__ import annotations

import random
from typing import Any

# Core genre + instrumentation + mood + dynamics per category.
_CATEGORY_TEMPLATE: dict[str, str] = {
    "tension": "a tense cinematic confrontation underscore, built on sustained low string friction, muffled timpani hits and a staccato pulsing ostinato that swells from soft to loud over a dark, suspended minor harmony, with brittle tremolo strings and a distant brass rumble creating a coiled, about-to-snap pressure",
    "combat": "a high-energy action combat score, driven by dense propulsive percussion and snare rolls, aggressive short brass bursts, fast taiko and orchestral hits trading off, rapid sixteenth-note string runs and a hard syncopated groove that pushes adrenaline-surging urgency",
    "climax_hype": "an epic, uplifting climax cue, with soaring unison strings and bright triumphant brass, a choir-like swell and layered percussion building relentlessly toward an explosive peak, grand, blood-pumping and unstoppable in its sense of victory",
    "faceslap": "a smug, victorious turnaround sting, with punchy brass accents over a thick synth bass, a cocky on-the-beat strut, playful pizzicato string jabs and a crisp, clean payoff hit that lands with deeply satisfying comeuppance swagger",
    "tragic": "a mournful, sorrowful theme, carried by a solo cello murmur and single sustained piano notes, aching legato strings that unfold slowly over sparse space and long fading tails, desolate, heavy and quietly tear-jerking",
    "warm": "a warm, tender, heartfelt theme, with gentle piano arpeggios and fingerpicked acoustic guitar over a soft string bed and delicate woodwind touches, intimate, healing and comforting like a spring breeze",
    "romance_pain": "a bittersweet, tragic-love theme, with a yearning solo violin and piano in intimate dialogue, delicate aching melodic swells over a string bed that carries a faint sob, lingering, unfulfilled and melancholically romantic",
    "suspense": "an eerie suspenseful underscore, with sparse pizzicato strings, ticking clock percussion, unsettling held tones and dissonant overtones punctuated by an occasional low heartbeat pulse, cold, mysterious and full of breath-holding dread",
    "daily": "a light, casual slice-of-life background cue, with softly strummed acoustic guitar and mellow electric piano over a relaxed mid-tempo groove, playful marimba or whistle touches, bright, cozy and pressure-free",
    "flashback": "a nostalgic, dreamy flashback cue, with hazy reverb-soaked piano and an ethereal synth pad under a wistful music-box or glockenspiel motif, soft-focus in texture, distant, sentimental and gently time-rewinding",
    "theme_open": "a bold, memorable opening-title theme, with a full cinematic orchestra tutti stating a strong, vivid signature melody as brass and strings call and answer, confident, grand and instantly gripping",
    "system_cue": "a short, clean UI notification cue, with bright synth bells and a crisp chime over light electronic timbre accents, a neutral, unobtrusive game-system feedback sound that stays tidy and highly recognizable",
}

# A scene type per category, used in the use-case sentence.
_CATEGORY_SCENE: dict[str, str] = {
    "tension": "a tense standoff or interrogation",
    "combat": "an action fight sequence",
    "climax_hype": "a triumphant turning-point climax",
    "faceslap": "a satisfying comeback / face-slap beat",
    "tragic": "a grief or loss scene",
    "warm": "a tender, heart-warming moment",
    "romance_pain": "a bittersweet romantic scene",
    "suspense": "a suspenseful, mysterious scene",
    "daily": "an everyday slice-of-life scene",
    "flashback": "a memory or flashback montage",
    "theme_open": "an opening title / intro sequence",
    "system_cue": "a system / UI notification moment",
}

_INTENSITY_ADJ: dict[int, tuple[str, ...]] = {
    1: ("very soft and minimal", "sparse and understated", "gentle and restrained"),
    2: ("soft and subtle", "light and laid-back", "calm and measured"),
    3: ("balanced and moderate", "steady mid-energy", "even and controlled"),
    4: ("strong and driving", "bold and energetic", "intense and forward"),
    5: ("explosive and maximal", "overwhelming and powerful", "full-throttle and huge"),
}

_INTENSITY_DYNAMICS: dict[int, str] = {
    1: "keep the dynamics very restrained throughout, barely rising, leaving plenty of quiet space",
    2: "keep the dynamics gentle, with small tasteful swells that never overpower a scene",
    3: "use moderate dynamic contrast, with a clear but controlled rise and fall",
    4: "use strong dynamic contrast, with bold builds and powerful hits",
    5: "use extreme dynamic range, from tense quiet to a massive, overwhelming peak",
}

# The mood / instruments dropdown presets are Chinese (UI vocabulary). Translate
# the known ones to English so the prompt stays single-language; any custom
# free-text the user types that isn't a preset passes through unchanged.
_MOOD_EN: dict[str, str] = {
    "阴森压抑": "grim and oppressive",
    "紧张悬疑": "tense and suspenseful",
    "热血激昂": "hot-blooded and rousing",
    "悲伤凄凉": "sad and desolate",
    "温暖治愈": "warm and healing",
    "甜蜜浪漫": "sweet and romantic",
    "诡异不安": "eerie and uneasy",
    "轻松愉快": "light and cheerful",
    "怀旧感伤": "nostalgic and wistful",
    "史诗恢弘": "epic and grand",
    "空灵神秘": "ethereal and mysterious",
}

_INSTRUMENTS_EN: dict[str, str] = {
    "弦乐 + 低音鼓": "strings and bass drum",
    "钢琴独奏": "solo piano",
    "古筝 + 笛": "guzheng and bamboo flute",
    "电子合成器": "electronic synthesizer",
    "管弦乐团": "full orchestra",
    "大提琴独奏": "solo cello",
    "二胡": "erhu",
    "鼓点打击乐": "rhythmic percussion",
    "氛围 pad + 长音": "ambient pad and sustained tones",
    "钢琴 + 弦乐": "piano and strings",
}


def build_bgm_prompt(attrs: dict[str, Any], seed: int) -> str:
    """Compose a long, detailed (~1000+ char) English ElevenLabs Music prompt
    for one track. `attrs` is `asdict(BgmAttrs)`."""
    category = str(attrs.get("category", ""))
    core = _CATEGORY_TEMPLATE.get(category, "a cinematic instrumental background music cue")
    scene = _CATEGORY_SCENE.get(category, "a dramatic scene")
    intensity = int(attrs.get("intensity", 3) or 3)
    choices = _INTENSITY_ADJ.get(intensity, _INTENSITY_ADJ[3])
    rng = random.Random(seed)
    energy = choices[rng.randrange(len(choices))]
    dynamics = _INTENSITY_DYNAMICS.get(intensity, _INTENSITY_DYNAMICS[3])
    bpm = int(attrs.get("bpm", 90) or 90)
    duration = int(attrs.get("duration", 30) or 30)
    loopable = bool(attrs.get("loopable"))

    mood_raw = str(attrs.get("mood", "") or "").strip()
    mood = _MOOD_EN.get(mood_raw, mood_raw)
    instruments_raw = str(attrs.get("instruments", "") or "").strip()
    instruments = _INSTRUMENTS_EN.get(instruments_raw, instruments_raw)

    mood_clause = f" The overall emotional tone should feel {mood}." if mood else ""
    instr_clause = (
        f" Feature {instruments} prominently in the arrangement, blended naturally with the "
        f"instrumentation above." if instruments else ""
    )
    loop_clause = (
        " Compose it as a seamless loop with a smooth, click-free transition from end back to "
        "start, and avoid any hard final cadence that would prevent looping."
        if loopable else
        " Give it a clear beginning and a clean, settled ending."
    )

    sentences = [
        f"A fully instrumental cinematic background-music cue for a Chinese vertical short drama, "
        f"in the style of {core}.",
        f"{mood_clause.strip()}" if mood_clause else "",
        f"Energy level: {energy} (about {intensity} out of 5), at a tempo of roughly {bpm} BPM.",
        f"Arrangement and structure: open with a sparse, atmospheric introduction that establishes "
        f"the mood within the first few seconds; gradually layer in instruments and build through a "
        f"development section; reach a clear emotional focal point near the middle; then ease back "
        f"and resolve gracefully.",
        f"Dynamics: {dynamics}.{instr_clause}",
        f"Production and mix: clean, modern, professional cinematic production with a wide stereo "
        f"image, tasteful reverb for depth and space, a balanced and controlled low end, and a "
        f"polished, high-fidelity master with no clipping or harshness.",
        f"Use case: this is background score for {scene} in a vertical short drama, so it must sit "
        f"comfortably underneath dialogue without overwhelming it, stay emotionally consistent from "
        f"start to finish, and transition cleanly.{loop_clause}",
        f"Strictly instrumental: absolutely no vocals, no lyrics, no singing, no spoken word, no "
        f"choir words and no sound-effects or foley. Target length about {duration} seconds.",
    ]
    return " ".join(s for s in sentences if s)


def build_bgm_prompt_keyed(attrs: dict[str, Any], seed: int, bgm_id: str = "") -> str:
    """The music prompt with the `bgm_id` KEY on its own leading line (when
    given) — what the user copies into ElevenLabs. The download then carries the
    id in its filename, so the global Downloads import routes the right file
    back. The local read-back strips this key line before feeding the model."""
    body = build_bgm_prompt(attrs, seed)
    return f"{bgm_id}\n{body}" if bgm_id else body
