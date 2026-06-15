"""Perf-library dual-scorer engine: 你 + Claude score the (one generic) prompt;
their scores combine into a 合议 (accept / revise / pending). Model-free."""
from __future__ import annotations

from pathlib import Path

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.infrastructure.writers.perf_score__writer import (
    PerfScorer,
    update_scores_text,
)

SEED = """# perf_0003 · 压抑隐忍·强度3·内敛·眼神

## 锁定文本块

```
眼眶下缘极淡泛红…
```

## 实测与验证

validation_status: pending_review
decision: pending

> 评分：你 + Claude…

| 评分者 | 表演达意 | 情绪可识别 | 是否过火 | 笔记 |
|--------|----------|-----------|----------|------|
| 你 | - | - | - | - |
| Claude | - | - | - | - |

合议: 待评分
"""


def test_one_side_scored_is_pending() -> None:
    out, res = update_scores_text(SEED, "你", 5, 4, 1, "干净")
    assert res["decision"] == "pending"
    assert res["validation_status"] == "pending_review"
    assert "| 你 | 5 | 4 | 1 | 干净 |" in out
    assert "待另一方评分" in out


def test_both_pass_accepts() -> None:
    out, _ = update_scores_text(SEED, "你", 5, 4, 1, "好")
    out, res = update_scores_text(out, "Claude", 4, 4, 2, "认同")
    assert res["decision"] == "accept"
    assert res["validation_status"] == "validated"
    assert "均达标" in res["verdict"]


def test_both_scored_but_one_fails_revises() -> None:
    out, _ = update_scores_text(SEED, "你", 5, 5, 1, "达意")
    out, res = update_scores_text(out, "Claude", 3, 4, 4, "过火且不达意")
    assert res["decision"] == "revise"
    assert res["validation_status"] == "needs_revision"


def test_rescoring_overwrites_row() -> None:
    out, _ = update_scores_text(SEED, "你", 2, 2, 4, "僵")
    out, _ = update_scores_text(out, "Claude", 4, 4, 2, "ok")
    # 你 re-scores higher → now both pass → accept
    out, res = update_scores_text(out, "你", 5, 4, 2, "改后好多了")
    assert res["decision"] == "accept"
    assert "| 你 | 5 | 4 | 2 | 改后好多了 |" in out


def test_route_wired_rejects_non_perf_path() -> None:
    from fastapi.testclient import TestClient

    from libs.common.origin import BoundOrigin
    from libs.common.repo_root import RepoRoot
    from tests.conftest import make_app, repo_root

    client = TestClient(make_app(RepoRoot(path=repo_root()), BoundOrigin(host="127.0.0.1", port=8766), serve_static=False))
    resp = client.post("/api/perf-score", json={
        "path": "ai_videos/feng_shou_lu/README.md", "who": "你",
        "da_yi": 5, "qing_xu": 4, "guo_huo": 1, "note": "x",
    })
    assert resp.status_code == 400, resp.text


def test_writer_end_to_end(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    entry = root / "ai_videos" / "_performances" / "yayi_yinren" / "perf_0003" / "perf_0003.md"
    entry.parent.mkdir(parents=True, exist_ok=True)
    entry.write_text(SEED, encoding="utf-8")
    scorer = PerfScorer(ExposedTree(root), SafeResolver(root))
    rel = "ai_videos/_performances/yayi_yinren/perf_0003/perf_0003.md"
    scorer.apply(rel, "你", 5, 4, 1, "干净")
    res = scorer.apply(rel, "Claude", 4, 4, 2, "认同")
    assert res["decision"] == "accept"
    text = entry.read_text(encoding="utf-8")
    assert "validation_status: validated" in text
    assert "| 你 | 5 | 4 | 1 | 干净 |" in text
    assert "| Claude | 4 | 4 | 2 | 认同 |" in text
    assert "## 锁定文本块" in text
    assert "模型" not in text[text.find("## 实测与验证"):]
