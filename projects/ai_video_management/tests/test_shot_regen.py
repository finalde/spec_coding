"""Shot-regen reader assembles a copy-paste prompt from a shot's
`表演库参考:` annotations + the referenced perf entries' current locked blocks."""
from __future__ import annotations

from pathlib import Path

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.infrastructure.readers.shot_regen__reader import ShotRegenPromptReader


def _reader(root: Path) -> ShotRegenPromptReader:
    return ShotRegenPromptReader(ExposedTree(root), SafeResolver(root))


def _perf(root: Path, emotion: str, pid: str, locked: str) -> None:
    p = root / "ai_videos" / "_performances" / emotion / pid / f"{pid}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"# {pid} · 压抑隐忍·强度3\n\n## 锁定文本块\n\n```\n{locked}\n```\n", encoding="utf-8")


def _shot(root: Path, refs: str) -> str:
    rel = "ai_videos/td/episodes/ep01/shots/shot07/shot07.md"
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        "---\nstage: 6\n---\n\n## Shot context\n\n- Summary: 苏晚当众受辱\n"
        f"{refs}\n- Duration: 5s\n\n## 视频 prompt\n\n```text\n动作: 旧的占位\n```\n",
        encoding="utf-8",
    )
    return rel


def test_assembles_prompt_with_locked_block(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _perf(root, "yayi_yinren", "perf_0003", "泪膜成形不落；眨眼抑制；喉头吞咽；上下脸冲突")
    rel = _shot(root, "- 表演库参考: perf_0003 (压抑隐忍·强度3·内敛·眼神) — 用于 苏晚 当众受辱强忍")
    out = _reader(root).build(rel)
    assert out["refs"] == ["perf_0003"]
    prompt = out["prompt"]
    assert "泪膜成形不落" in prompt          # latest locked block inlined
    assert "苏晚 当众受辱强忍" in prompt       # the 用于 annotation carried
    assert "融入" in prompt and "不照抄" in prompt
    assert "苏晚当众受辱" in prompt            # shot context included


def test_no_annotation_returns_message(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    rel = _shot(root, "- Characters: 苏晚")
    out = _reader(root).build(rel)
    assert out["refs"] == []
    assert "未标注" in out["message"]
    assert out["prompt"] == ""


def test_missing_perf_flagged(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    rel = _shot(root, "- 表演库参考: perf_9999 (不存在) — 用于 苏晚")
    out = _reader(root).build(rel)
    assert out["refs"] == ["perf_9999"]
    assert "未找到" in out["prompt"]
