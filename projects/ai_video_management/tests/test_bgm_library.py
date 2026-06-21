"""BGM library slice — contract tests.

Covers the stage-5 acceptance anchors that are pure-local (no torch / GPU):
global cross-category id allocation, sidecar build↔parse round-trip, the
`bgm.md` reference reverse-lookup, the assignment-guarded delete, soft-delete
layout, and generation-failure leaving no orphan folder. Generation is
stubbed with a tiny script that writes a fake mp3, so these run on any host;
the real Stable Audio path is exercised by `tools/stableaudio_gen.py` itself.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from libs.application.commands.bgm__command import BgmCommand
from libs.application.dtos.bgm__dto import GenerateBgmsInputCdto
from libs.application.queries.bgm__query import BgmQuery
from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.bgm__error import BgmAlreadyAssignedError, InvalidBgmAttributeError
from libs.domain.value_objects.bgm__valueobject import BgmAttrs, validate_bgm_id
from libs.domain.errors.bgm__error import InvalidBgmIdError
from libs.infrastructure.readers.bgm_reference__reader import BgmReferenceReader
from libs.infrastructure.writers.bgm__writer import BgmPool

_STUB = (
    "import argparse,sys\n"
    "p=argparse.ArgumentParser()\n"
    "[p.add_argument(f) for f in ('--prompt','--seed','--duration','--model','--out')]\n"
    "a=p.parse_args()\n"
    "open(a.out,'wb').write(b'ID3fakeaudio')\n"
    "sys.exit(0)\n"
)
_FAIL_STUB = "import sys; sys.exit(1)\n"


def _make(root: Path, stub_body: str = _STUB) -> tuple[BgmCommand, BgmQuery, BgmPool, BgmReferenceReader]:
    (root / "ai_videos").mkdir(parents=True, exist_ok=True)
    (root / "tools").mkdir(exist_ok=True)
    (root / "tools" / "stableaudio_gen.py").write_text(stub_body, encoding="utf-8")
    os.environ["BGM_PYTHON"] = sys.executable
    exposed = ExposedTree(root)
    resolver = SafeResolver(root)
    pool = BgmPool(exposed, resolver)
    refs = BgmReferenceReader(exposed, resolver)
    return BgmCommand(pool, refs), BgmQuery(pool, refs), pool, refs


def _gen(cmd: BgmCommand, category: str, **kw) -> str:
    cdto = cmd.generate(GenerateBgmsInputCdto(count=1, category=category, duration=3, **kw))
    assert cdto.errors == [], cdto.errors
    return cdto.generated[0]["id"]


def test_id_is_globally_unique_across_categories(tmp_path: Path) -> None:
    cmd, _q, _p, _r = _make(tmp_path)
    a = _gen(cmd, "tension")
    b = _gen(cmd, "combat")
    c = _gen(cmd, "tension")
    assert (a, b, c) == ("bgm_0001", "bgm_0002", "bgm_0003")  # +1 across categories, not per-category


def test_disk_layout_and_sidecar_roundtrip(tmp_path: Path) -> None:
    cmd, qry, _p, _r = _make(tmp_path)
    bid = _gen(cmd, "warm", bpm=72, intensity=2, loopable=True, mood="gentle piano", instruments="piano")
    folder = tmp_path / "ai_videos" / "_bgm" / "warm" / bid
    assert (folder / f"{bid}.mp3").is_file()
    assert (folder / f"{bid}.md").is_file()
    row = {b["id"]: b for b in qry.list().to_payload()["bgms"]}[bid]
    assert row["category"] == "warm" and row["bpm"] == 72 and row["intensity"] == 2
    assert row["loopable"] is True and row["mood"] == "gentle piano"
    assert row["category_label"] == "温情"


def test_references_and_referenced_flag(tmp_path: Path) -> None:
    cmd, qry, _p, refs = _make(tmp_path)
    bid = _gen(cmd, "tension")
    ep = tmp_path / "ai_videos" / "drama_a" / "episodes" / "ep01"
    ep.mkdir(parents=True)
    (ep / "bgm.md").write_text(f"0-5 {bid} | vol=0.6 | duck=on | fade=in\n", encoding="utf-8")
    assert bid in refs.referenced_bgm_ids()
    rows = qry.get_references(bid).to_payload()["references"]
    assert rows and rows[0]["drama"] == "drama_a" and rows[0]["location"] == "episodes/ep01"
    flags = {b["id"]: b["is_referenced"] for b in qry.list().to_payload()["bgms"]}
    assert flags[bid] is True


def test_short_root_bgm_md_is_scanned(tmp_path: Path) -> None:
    cmd, qry, _p, refs = _make(tmp_path)
    bid = _gen(cmd, "daily")
    drama = tmp_path / "ai_videos" / "short_b"
    drama.mkdir(parents=True, exist_ok=True)
    (drama / "bgm.md").write_text(f"0-8 {bid} | vol=0.5\n", encoding="utf-8")
    rows = qry.get_references(bid).to_payload()["references"]
    assert rows[0]["location"] == "(root)"


def test_delete_refused_when_referenced(tmp_path: Path) -> None:
    cmd, _q, _p, _r = _make(tmp_path)
    bid = _gen(cmd, "tension")
    ep = tmp_path / "ai_videos" / "drama_a" / "episodes" / "ep01"
    ep.mkdir(parents=True)
    (ep / "bgm.md").write_text(f"0-5 {bid} | vol=0.6\n", encoding="utf-8")
    with pytest.raises(BgmAlreadyAssignedError):
        cmd.delete(bid)


def test_unreferenced_delete_is_soft_delete(tmp_path: Path) -> None:
    cmd, _q, _p, _r = _make(tmp_path)
    bid = _gen(cmd, "combat")
    res = cmd.delete(bid).to_payload()
    assert f"_deleted/_bgm/combat/{bid}" in res["to"]
    assert (tmp_path / "ai_videos" / "_deleted" / "_bgm" / "combat" / bid).is_dir()
    assert not (tmp_path / "ai_videos" / "_bgm" / "combat" / bid).exists()


def test_deleted_id_is_not_reused(tmp_path: Path) -> None:
    """A soft-deleted track's number must never be handed to a new track — else
    any drama's bgm.md cue still referencing the retired id silently rebinds to
    the new (different) track. Allocation counts the `_deleted` recycle bin too."""
    cmd, _q, _p, _r = _make(tmp_path)
    a = _gen(cmd, "tension")  # bgm_0001
    b = _gen(cmd, "tragic")   # bgm_0002
    assert (a, b) == ("bgm_0001", "bgm_0002")
    cmd.delete(b)  # soft-delete bgm_0002 → _deleted/_bgm/tragic/bgm_0002
    c = _gen(cmd, "tragic")
    assert c == "bgm_0003"  # NOT bgm_0002 again, even though it's gone from the live lib


def test_generation_failure_leaves_no_orphan(tmp_path: Path) -> None:
    cmd, _q, _p, _r = _make(tmp_path, stub_body=_FAIL_STUB)
    cdto = cmd.generate(GenerateBgmsInputCdto(count=1, category="daily", duration=3))
    assert cdto.generated == [] and cdto.errors
    daily = tmp_path / "ai_videos" / "_bgm" / "daily"
    assert not daily.exists() or not any(daily.iterdir())


def test_invalid_category_and_id_rejected() -> None:
    with pytest.raises(InvalidBgmAttributeError):
        BgmAttrs(category="not_a_category")
    with pytest.raises(InvalidBgmIdError):
        validate_bgm_id("bgm_12")  # too few digits
    validate_bgm_id("bgm_0001")  # ok


def test_create_prompts_is_prompt_only(tmp_path: Path) -> None:
    """Step 1: create_prompts allocates folders + sidecars, NO mp3, and the
    result entries are flagged pending_audio with the resolved prompt."""
    cmd, qry, _p, _r = _make(tmp_path)
    cdto = cmd.create_prompts(GenerateBgmsInputCdto(count=2, category="daily", duration=3))
    assert cdto.errors == [] and len(cdto.generated) == 2
    for e in cdto.generated:
        assert e["pending_audio"] is True and e["audio_path"] is None and e["prompt"]
        folder = tmp_path / "ai_videos" / "_bgm" / "daily" / e["id"]
        assert (folder / f"{e['id']}.md").is_file()
        assert not list(folder.glob("*.mp3"))
    rows = {b["id"]: b for b in qry.list().to_payload()["bgms"]}
    assert all(rows[e["id"]]["audio_path"] is None for e in cdto.generated)


def test_generate_audio_renders_from_sidecar(tmp_path: Path) -> None:
    """Step 2a: generate_audio reads the prompt-only sidecar and renders the
    track's mp3 (stubbed)."""
    cmd, _q, _p, _r = _make(tmp_path)
    bid = cmd.create_prompts(GenerateBgmsInputCdto(count=1, category="warm", duration=3)).generated[0]["id"]
    res = cmd.generate_audio(bid).to_payload()
    assert res["id"] == bid
    assert (tmp_path / "ai_videos" / "_bgm" / "warm" / bid / f"{bid}.mp3").is_file()


def test_prompt_is_long_and_detailed(tmp_path: Path) -> None:
    """The generated prompt must be a long, detailed brief (≥ 1000 chars)."""
    _c, qry, _p, _r = _make(tmp_path)
    out = qry.preview_prompts(GenerateBgmsInputCdto(count=1, category="suspense", duration=30))
    prompt = out.to_payload()["prompts"][0]["prompt"]
    assert len(prompt) >= 1000
    assert "instrumental" in prompt and "no vocals" in prompt


def test_prompt_carries_key_line_and_readback_strips_it(tmp_path: Path) -> None:
    """The sidecar prompt starts with the `bgm_NNNN` KEY line (for download
    routing); the local read-back strips it before feeding the model."""
    cmd, _q, pool, _r = _make(tmp_path)
    bid = cmd.create_prompts(GenerateBgmsInputCdto(count=1, category="suspense", duration=3)).generated[0]["id"]
    md = tmp_path / "ai_videos" / "_bgm" / "suspense" / bid / f"{bid}.md"
    text = md.read_text(encoding="utf-8")
    assert f"```\n{bid}\n" in text  # key is the first line inside the fence
    model_prompt, _seed, _dur = BgmPool._read_sidecar_generation(md)
    assert not model_prompt.startswith(bid)  # key line stripped for the model
    assert "instrumental" in model_prompt


def test_reaper_preserves_prompt_only_but_reaps_empty(tmp_path: Path) -> None:
    """The reaper must keep an aged prompt-only track (sidecar, no mp3) but
    still drop a truly-empty aged folder (crash leftover)."""
    cmd, _q, pool, _r = _make(tmp_path)
    bid = cmd.create_prompts(GenerateBgmsInputCdto(count=1, category="suspense", duration=3)).generated[0]["id"]
    cat_dir = tmp_path / "ai_videos" / "_bgm" / "suspense"
    prompt_only = cat_dir / bid
    empty = cat_dir / "bgm_9999"
    empty.mkdir()
    old = 1.0  # epoch — far older than the 1800s reap threshold
    for f in (prompt_only, empty):
        os.utime(f, (old, old))
    pool._reap_incomplete_folders(tmp_path / "ai_videos" / "_bgm")
    assert (prompt_only / f"{bid}.md").is_file()  # prompt-only survives
    assert not empty.exists()  # empty leftover reaped


def test_preview_does_not_write(tmp_path: Path) -> None:
    _c, qry, _p, _r = _make(tmp_path)
    out = qry.preview_prompts(GenerateBgmsInputCdto(count=2, category="suspense", duration=10))
    payload = out.to_payload()
    assert len(payload["prompts"]) == 2
    assert "instrumental" in payload["prompts"][0]["prompt"]
    assert not (tmp_path / "ai_videos" / "_bgm").exists()
