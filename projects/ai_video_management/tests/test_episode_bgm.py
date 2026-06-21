"""EpisodeBgmManager: parse / assign / burn a sparse episode BGM cue timeline.

The real ffmpeg mux is stubbed — these assert the orchestration (cue parsing,
slot rewrite, source/track resolution, skip of unassigned cues, filtergraph
shape), not the encode itself.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.episode_bgm__error import (
    BgmCueNotFoundError,
    BgmTrackAudioMissingError,
    NoAssignedBgmCuesError,
    NotEpisodeBgmPathError,
    SubtitledEpisodeMissingError,
)
from libs.domain.value_objects.episode_bgm__valueobject import (
    BgmCue,
    parse_bgm_cues,
    serialize_cue,
)
from libs.infrastructure.writers.episode_bgm__writer import EpisodeBgmManager

_CUE_FILE = """# ep01 BGM 编排

> 稀疏配乐时间线。
```text
12-27   bgm_0003 | cat=combat | vol=0.7 | duck=on | fade=in/out  # 武打：反杀
40-55   -        | cat=tragic | vol=0.5 | duck=off | fade=in     # 悲伤：遗言
```
"""


class _FakeBgmPool:
    def __init__(self, audio: dict[str, Path]) -> None:
        self._audio = audio

    def bgm_exists(self, bgm_id: str) -> bool:
        return bgm_id in self._audio

    def audio_path_for(self, bgm_id: str) -> Path | None:
        return self._audio.get(bgm_id)


def _ep(root: Path) -> Path:
    return root / "ai_videos" / "td" / "episodes" / "ep01"


def _manager(root: Path, audio: dict[str, Path] | None = None) -> EpisodeBgmManager:
    return EpisodeBgmManager(
        ExposedTree(root), SafeResolver(root), _FakeBgmPool(audio or {})  # type: ignore[arg-type]
    )


def test_parse_serialize_roundtrip() -> None:
    cues = parse_bgm_cues(_CUE_FILE)
    assert len(cues) == 2
    a, b = cues
    assert (a.start, a.end, a.bgm_id, a.category) == (12.0, 27.0, "bgm_0003", "combat")
    assert a.vol == 0.7 and a.duck is True and a.fade_in and a.fade_out
    assert b.bgm_id is None and b.category == "tragic" and b.duck is False
    # serialize is stable / re-parseable
    again = parse_bgm_cues(serialize_cue(a) + "\n" + serialize_cue(b))
    assert again == cues


def test_read_reports_status(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    ep = _ep(root)
    (ep / "bgm").mkdir(parents=True)
    (ep / "bgm" / "bgm.md").write_text(_CUE_FILE, encoding="utf-8")
    (ep / "ep01_zh.mp4").write_bytes(b"video")

    res = _manager(root).read("ai_videos/td/episodes/ep01/bgm/bgm.md")
    assert res.cue_file_exists and res.source_exists and not res.output_exists
    assert len(res.cues) == 2


def test_assign_rewrites_slot_and_unassign_restores(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    ep = _ep(root)
    (ep / "bgm").mkdir(parents=True)
    cue_md = ep / "bgm" / "bgm.md"
    cue_md.write_text(_CUE_FILE, encoding="utf-8")
    mgr = _manager(root, {"bgm_0009": ep / "x.mp3"})

    res = mgr.assign("ai_videos/td/episodes/ep01/bgm/bgm.md", 40.0, 55.0, "bgm_0009")
    tragic = [c for c in res.cues if c.category == "tragic"][0]
    assert tragic.bgm_id == "bgm_0009"
    # the other cue + its comment survive untouched
    assert "武打：反杀" in cue_md.read_text(encoding="utf-8")

    res2 = mgr.unassign("ai_videos/td/episodes/ep01/bgm/bgm.md", 40.0, 55.0)
    assert [c for c in res2.cues if c.category == "tragic"][0].bgm_id is None


def test_assign_unknown_bgm_rejected(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    ep = _ep(root)
    (ep / "bgm").mkdir(parents=True)
    (ep / "bgm" / "bgm.md").write_text(_CUE_FILE, encoding="utf-8")
    with pytest.raises(BgmTrackAudioMissingError):
        _manager(root).assign("ai_videos/td/episodes/ep01/bgm/bgm.md", 12.0, 27.0, "bgm_9999")


def test_assign_window_not_found(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    ep = _ep(root)
    (ep / "bgm").mkdir(parents=True)
    (ep / "bgm" / "bgm.md").write_text(_CUE_FILE, encoding="utf-8")
    mgr = _manager(root, {"bgm_0009": ep / "x.mp3"})
    with pytest.raises(BgmCueNotFoundError):
        mgr.assign("ai_videos/td/episodes/ep01/bgm/bgm.md", 1.0, 2.0, "bgm_0009")


def test_burn_resolves_assigned_skips_unassigned(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    ep = _ep(root)
    (ep / "bgm").mkdir(parents=True)
    (ep / "bgm" / "bgm.md").write_text(_CUE_FILE, encoding="utf-8")
    (ep / "ep01_zh.mp4").write_bytes(b"video")
    mp3 = ep / "bgm_0003.mp3"
    mp3.write_bytes(b"audio")
    mgr = _manager(root, {"bgm_0003": mp3})

    captured: dict[str, object] = {}

    def fake_mux(source: Path, cues, out_path: Path) -> None:  # type: ignore[no-untyped-def]
        captured["n"] = len(cues)
        out_path.write_bytes(b"final")

    mgr._mux = fake_mux  # type: ignore[method-assign]
    res = mgr.burn("ai_videos/td/episodes/ep01/bgm/bgm.md")

    assert captured["n"] == 1  # only the assigned cue
    assert res.out_rel == "ai_videos/td/episodes/ep01/ep01_zh_bgm.mp4"
    assert (ep / "ep01_zh_bgm.mp4").is_file()
    assert [s["reason"] for s in res.skipped] == ["unassigned"]


def test_burn_no_assigned_raises(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    ep = _ep(root)
    (ep / "bgm").mkdir(parents=True)
    (ep / "bgm" / "bgm.md").write_text(
        "```text\n10-20   -  | cat=warm | vol=0.4 | duck=on | fade=none\n```\n",
        encoding="utf-8",
    )
    (ep / "ep01_zh.mp4").write_bytes(b"video")
    with pytest.raises(NoAssignedBgmCuesError):
        _manager(root).burn("ai_videos/td/episodes/ep01/bgm/bgm.md")


def test_burn_missing_subtitled_source_raises(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    ep = _ep(root)
    (ep / "bgm").mkdir(parents=True)
    (ep / "bgm" / "bgm.md").write_text(_CUE_FILE, encoding="utf-8")
    mgr = _manager(root, {"bgm_0003": ep / "x.mp3"})
    with pytest.raises(SubtitledEpisodeMissingError):
        mgr.burn("ai_videos/td/episodes/ep01/bgm/bgm.md")


def test_filtergraph_shape() -> None:
    cues = [
        (BgmCue(12, 27, "combat", bgm_id="bgm_0003", vol=0.7, duck=True, fade_in=True, fade_out=True), Path("a.mp3")),
        (BgmCue(40, 55, "tragic", bgm_id="bgm_0009", vol=0.5, duck=False, fade_in=True), Path("b.mp3")),
    ]
    graph, pads = EpisodeBgmManager._build_filtergraph(cues)
    assert pads == "[aout]"
    assert "asplit=2[base]" in graph  # 1 ducked cue → base + 1 key
    assert "sidechaincompress" in graph
    assert "amix=inputs=3:normalize=0" in graph  # base + 2 bgm
    assert "adelay=12000:all=1" in graph and "adelay=40000:all=1" in graph


def test_non_episode_path_rejected(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos" / "td" / "characters").mkdir(parents=True)
    with pytest.raises(NotEpisodeBgmPathError):
        _manager(root).read("ai_videos/td/characters/c1/c1.md")
