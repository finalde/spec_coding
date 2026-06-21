"""Intro-card parse (pure) + IntroCardBurner image-overlay burn.

The intro card is a per-character PNG from the global library
`ai_videos/_intro_cards/`; the burn composites it onto a shot's top corner with
a fade. The burn test does a real (tiny) ffmpeg overlay and asserts the carded
output exists with the same duration (smooth overlay, no freeze).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import imageio_ffmpeg
import pytest

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.intro_card__error import (
    IntroCardImageMissingError,
    IntroCardsFileMissingError,
    NoCardForShotError,
)
from libs.domain.value_objects.intro_card__valueobject import (
    cards_for_shot,
    parse_intro_cards,
)
from libs.infrastructure.writers.intro_card__writer import IntroCardBurner

_CARDS = (
    "```text\n"
    "裴知秋 | shot01 | 0.3 | 裴知秋 | 右上 | 3.5 | 0.3\n"
    "裴霆   | shot02 | 0.2 | 2_世界观人设/intro_cards/裴霆.png | 左上 | 3.5\n"
    "# comment line, skipped\n"
    "坏行字段不够 | shot03 | 1.0\n"
    "```\n"
)


def test_parse_image_card_keeps_raw_ref() -> None:
    cards = parse_intro_cards(_CARDS)
    assert len(cards) == 2
    s1 = cards_for_shot(cards, "shot01")[0]
    # raw ref kept as-is; the writer resolves it per drama
    assert s1.image_ref == "裴知秋"
    assert s1.corner == "tr" and s1.at == 0.3 and s1.width_frac == 0.3
    s2 = cards_for_shot(cards, "shot02")[0]
    assert s2.image_ref == "2_世界观人设/intro_cards/裴霆.png"
    assert s2.corner == "tl" and s2.width_frac == 0.28
    assert cards_for_shot(cards, "shot03") == ()


def _shot_render(root: Path, shot: str = "shot01") -> tuple[Path, str]:
    renders = root / "ai_videos" / "td" / "episodes" / "ep01" / "shots" / shot / "renders"
    renders.mkdir(parents=True, exist_ok=True)
    mp4 = renders / "take.mp4"
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ffmpeg, "-y", "-f", "lavfi", "-i",
         "testsrc=duration=1:size=540x960:rate=15",
         "-pix_fmt", "yuv420p", "-loglevel", "error", str(mp4)],
        check=True, capture_output=True, timeout=60,
    )
    return mp4, f"ai_videos/td/episodes/ep01/shots/{shot}/renders/take.mp4"


def _make_card_png(root: Path, name: str) -> None:
    # intro card lives INSIDE the character folder as `intro_card.png`
    char = root / "ai_videos" / "td" / "2_世界观人设" / "characters" / name
    char.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    # a small RGBA png (semi-transparent) standing in for a Kling nameplate
    subprocess.run(
        [ffmpeg, "-y", "-f", "lavfi", "-i",
         "color=c=red@0.6:size=200x300:d=1,format=rgba",
         "-frames:v", "1", "-loglevel", "error", str(char / "intro_card.png")],
        check=True, capture_output=True, timeout=60,
    )


def _burner(root: Path) -> IntroCardBurner:
    return IntroCardBurner(ExposedTree(root), SafeResolver(root))


def _probe_duration(path: Path) -> float:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    out = subprocess.run([ffmpeg, "-i", str(path), "-hide_banner"],
                         capture_output=True, timeout=20, check=False)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)",
                  out.stderr.decode("utf-8", "replace"))
    h, mn, s = m.groups()
    return int(h) * 3600 + int(mn) * 60 + float(s)


def _cards_md(root: Path, body: str) -> None:
    (root / "ai_videos/td/episodes/ep01/intro_cards.md").write_text(
        f"```text\n{body}\n```\n", encoding="utf-8"
    )


def test_burn_missing_intro_cards_raises(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _shot_render(root)
    with pytest.raises(IntroCardsFileMissingError):
        _burner(root).burn("ai_videos/td/episodes/ep01/shots/shot01/renders/take.mp4")


def test_burn_no_card_for_shot_raises(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    mp4, rel = _shot_render(root, "shot09")
    _cards_md(root, "裴知秋 | shot01 | 0.3 | 裴知秋 | 右上 | 3.5")
    with pytest.raises(NoCardForShotError):
        _burner(root).burn(rel)


def test_burn_missing_card_image_raises(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    mp4, rel = _shot_render(root, "shot01")
    _cards_md(root, "裴知秋 | shot01 | 0.3 | 裴知秋 | 右上 | 3.5")  # png not in lib
    with pytest.raises(IntroCardImageMissingError):
        _burner(root).burn(rel)


def test_burn_composites_card_keeps_duration(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    mp4, rel = _shot_render(root, "shot01")
    shot_folder = mp4.parent.parent
    _make_card_png(root, "裴知秋")
    _cards_md(root, "裴知秋 | shot01 | 0.2 | 裴知秋 | 右上 | 0.6 | 0.3")
    result = _burner(root).burn(rel)
    assert result.card_count == 1 and result.names == ("裴知秋",)
    out = shot_folder / "shot01.mp4"
    assert out.is_file() and out.stat().st_size > 0
    assert result.out_rel.endswith("shots/shot01/shot01.mp4")
    assert (shot_folder / "renders" / "take.mp4").is_file()  # original untouched
    # smooth overlay — duration unchanged (~1s source)
    assert 0.9 <= _probe_duration(out) <= 1.1


def test_burn_two_cards_one_shot(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    mp4, rel = _shot_render(root, "shot03")
    _make_card_png(root, "裴昭")
    _make_card_png(root, "沈婉")
    _cards_md(
        root,
        "裴昭 | shot03 | 0.1 | 裴昭 | 右上 | 0.5\n"
        "沈婉 | shot03 | 0.6 | 沈婉 | 左上 | 0.4",
    )
    result = _burner(root).burn(rel)
    assert result.card_count == 2 and result.names == ("裴昭", "沈婉")
    assert (mp4.parent.parent / "shot03.mp4").is_file()
