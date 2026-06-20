"""Intro-card parse/ASS (pure) + IntroCardBurner freeze-frame nameplate burn.

The burn test does a real (tiny) ffmpeg freeze+overlay+concat on a 1s clip and
asserts the carded output is longer than the source (the freeze added time).
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
    IntroCardsFileMissingError,
    NoCardForShotError,
)
from libs.domain.value_objects.intro_card__valueobject import (
    cards_for_shot,
    cards_to_ass,
    parse_intro_cards,
)
from libs.infrastructure.writers.intro_card__writer import IntroCardBurner

_CARDS = (
    "```text\n"
    "裴知秋 | shot01 | 0.3 | 裴知秋 | 镇北王府庶长子 · 废少 | 描金框 | 右上 | 3.5\n"
    "裴霆   | shot02 | 0.2 | 裴霆   | 镇北王                 | 描金框 | 左上 | 3.5\n"
    "# comment line, skipped\n"
    "坏行没有足够字段 | shot03 | 1.0\n"
    "```\n"
)


def test_parse_and_filter_by_shot() -> None:
    cards = parse_intro_cards(_CARDS)
    assert len(cards) == 2
    s1 = cards_for_shot(cards, "shot01")
    assert len(s1) == 1 and s1[0].main == "裴知秋" and s1[0].at == 0.3
    assert s1[0].sub == "镇北王府庶长子 · 废少" and s1[0].corner == "tr"
    assert cards_for_shot(cards, "shot02")[0].corner == "tl"
    assert cards_for_shot(cards, "shot03") == ()


def test_cards_to_ass_has_main_sub_and_corner() -> None:
    cards = parse_intro_cards(_CARDS)
    ass = cards_to_ass(cards)
    assert "[Script Info]" in ass and "BorderStyle" in ass  # framed plate style
    dlg = [ln for ln in ass.splitlines() if ln.startswith("Dialogue:")]
    assert len(dlg) == 2
    assert "裴知秋" in dlg[0] and "镇北王府庶长子" in dlg[0]
    assert "\\fad(" in dlg[0]
    assert "\\an9" in dlg[0] and "\\an7" in dlg[1]  # top-right / top-left


def _shot_render(root: Path, shot: str = "shot01") -> tuple[Path, str]:
    renders = root / "ai_videos" / "td" / "episodes" / "ep01" / "shots" / shot / "renders"
    renders.mkdir(parents=True, exist_ok=True)
    mp4 = renders / "take.mp4"
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ffmpeg, "-y", "-f", "lavfi", "-i",
         "testsrc=duration=1:size=320x240:rate=15",
         "-pix_fmt", "yuv420p", "-loglevel", "error", str(mp4)],
        check=True, capture_output=True, timeout=60,
    )
    return mp4, f"ai_videos/td/episodes/ep01/shots/{shot}/renders/take.mp4"


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


def test_burn_missing_intro_cards_raises(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _shot_render(root)
    with pytest.raises(IntroCardsFileMissingError):
        _burner(root).burn("ai_videos/td/episodes/ep01/shots/shot01/renders/take.mp4")


def test_burn_no_card_for_shot_raises(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    mp4, rel = _shot_render(root, "shot09")
    (root / "ai_videos/td/episodes/ep01/intro_cards.md").write_text(_CARDS, encoding="utf-8")
    with pytest.raises(NoCardForShotError):
        _burner(root).burn(rel)


def test_burn_produces_longer_carded_mp4(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    mp4, rel = _shot_render(root, "shot01")
    shot_folder = mp4.parent.parent
    (root / "ai_videos/td/episodes/ep01/intro_cards.md").write_text(_CARDS, encoding="utf-8")
    result = _burner(root).burn(rel)
    assert result.card_count == 1 and result.names == ("裴知秋",)
    out = shot_folder / "shot01.mp4"
    assert out.is_file() and out.stat().st_size > 0
    assert result.out_rel.endswith("shots/shot01/shot01.mp4")
    # original take under renders/ is untouched
    assert (shot_folder / "renders" / "take.mp4").is_file()
    # smooth overlay — NO freeze, so duration is unchanged (~1s source)
    assert 0.9 <= _probe_duration(out) <= 1.1
