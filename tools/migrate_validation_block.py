"""Migrate each entry's `## 实测与验证` section to the dual-scorer format
(follow-up 004): 你 + Claude each rate on three axes, a combined 合议 decides
accept / revise. Replaces the old per-model render table (all rows were empty /
pending_review anyway — no scores lost). Idempotent.
"""
from __future__ import annotations

import sys
from pathlib import Path

PERF_ROOT = Path(__file__).resolve().parent.parent / "ai_videos" / "_performances"

NEW_BLOCK = """## 实测与验证

validation_status: pending_review
decision: pending

> 评分：你 + Claude 对这条 prompt 各评一次，每轴 1–5（表演达意 / 情绪可识别 / 是否过火；过火越低越好）。达标 = 表演达意≥4 且 情绪可识别≥4 且 是否过火≤2。合议：双方均达标 ⇒ accept；双方都评过但未同时达标 ⇒ revise（按失败轴改 prompt）；尚有一方未评 ⇒ pending。

| 评分者 | 表演达意 | 情绪可识别 | 是否过火 | 笔记 |
|--------|----------|-----------|----------|------|
| 你 | - | - | - | - |
| Claude | - | - | - | - |

合议: 待评分
"""


def migrate(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    idx = text.find("## 实测与验证")
    if idx == -1:
        return False
    # re-migrate if still on the per-model schema (has 模型 column) or unmigrated
    block = text[idx:]
    if "评分者" in block and "合议:" in block and "模型" not in block:
        return False  # already on the model-free schema
    new_text = text[:idx].rstrip() + "\n\n" + NEW_BLOCK
    path.write_text(new_text.rstrip("\n") + "\n", encoding="utf-8")
    return True


def main() -> None:
    n = 0
    for f in sorted(PERF_ROOT.glob("*/perf_*/perf_*.md")):
        if migrate(f):
            n += 1
    sys.stdout.write(f"migrated {n} validation blocks\n")


if __name__ == "__main__":
    main()
