"""Apply a performance-library review score to a `perf_NNNN.md` entry and
recompute the combined (你 + Claude) verdict.

The library uses ONE generic, model-agnostic prompt per entry, so scoring is on
the PROMPT itself — not per render model. The `## 实测与验证` block holds exactly
two rows (你 / Claude), each on three 1–5 axes (表演达意 / 情绪可识别 / 是否过火;
过火 lower-is-better). A row passes when 表演达意≥4 ∧ 情绪可识别≥4 ∧ 是否过火≤2.

合议:
- **accept** (→ validation_status=validated): 你 AND Claude both pass.
- **revise** (→ needs_revision): both rated but not both passing.
- **pending** (→ pending_review): a side hasn't rated yet.

The whole `## 实测与验证` section (the file's last section) is rebuilt from the
parsed row state — no fragile in-place table surgery.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.casting__error import InvalidDramaPathError

SECTION = "## 实测与验证"
_NOTE = (
    "> 评分：你 + Claude 对这条 prompt 各评一次，每轴 1–5（表演达意 / 情绪可识别 / 是否过火；"
    "过火越低越好）。达标 = 表演达意≥4 且 情绪可识别≥4 且 是否过火≤2。合议：双方均达标 ⇒ accept；"
    "双方都评过但未同时达标 ⇒ revise（按失败轴改 prompt）；尚有一方未评 ⇒ pending。"
)
_HEADER = "| 评分者 | 表演达意 | 情绪可识别 | 是否过火 | 笔记 |"
_SEP = "|--------|----------|-----------|----------|------|"
SCORERS = ("你", "Claude")


class PerfScorePathError(InvalidDramaPathError):
    pass


@dataclass
class _Row:
    scorer: str
    da_yi: int | None
    qing_xu: int | None
    guo_huo: int | None
    note: str

    def _c(self, v: int | None) -> str:
        return "-" if v is None else str(v)

    def render(self) -> str:
        note = self.note.strip() or "-"
        return f"| {self.scorer} | {self._c(self.da_yi)} | {self._c(self.qing_xu)} | {self._c(self.guo_huo)} | {note} |"


def _to_int(cell: str) -> int | None:
    cell = cell.strip()
    if cell in ("", "-"):
        return None
    try:
        n = int(cell)
    except ValueError:
        return None
    return n if 1 <= n <= 5 else None


def _parse_rows(block: str) -> list[_Row]:
    rows: list[_Row] = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|--") or "评分者" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        rows.append(
            _Row(
                scorer=cells[0],
                da_yi=_to_int(cells[1]),
                qing_xu=_to_int(cells[2]),
                guo_huo=_to_int(cells[3]),
                note="" if cells[4] in ("", "-") else cells[4],
            )
        )
    return rows


def _passes(r: _Row | None) -> bool:
    return bool(
        r and r.da_yi is not None and r.qing_xu is not None and r.guo_huo is not None
        and r.da_yi >= 4 and r.qing_xu >= 4 and r.guo_huo <= 2
    )


def _scored(r: _Row | None) -> bool:
    return bool(r and (r.da_yi is not None or r.qing_xu is not None or r.guo_huo is not None))


def _decide(rows: list[_Row]) -> tuple[str, str, str]:
    by = {r.scorer: r for r in rows}
    you, claude = by.get("你"), by.get("Claude")
    if _scored(you) and _scored(claude):
        if _passes(you) and _passes(claude):
            return "validated", "accept", "你与 Claude 均达标 ⇒ accept"
        return "needs_revision", "revise", "双方已评但未同时达标 ⇒ revise（按失败轴改 prompt）"
    if _scored(you) or _scored(claude):
        return "pending_review", "pending", "待另一方评分"
    return "pending_review", "pending", "待评分"


def _seed_rows() -> list[_Row]:
    return [_Row(s, None, None, None, "") for s in SCORERS]


def _merge(rows: list[_Row], scorer: str, da: int | None, qing: int | None,
           guo: int | None, note: str) -> list[_Row]:
    have = {r.scorer for r in rows}
    for s in SCORERS:
        if s not in have:
            rows.append(_Row(s, None, None, None, ""))
    target = next((r for r in rows if r.scorer == scorer), None)
    if target is None:
        target = _Row(scorer, None, None, None, "")
        rows.append(target)
    target.da_yi, target.qing_xu, target.guo_huo = da, qing, guo
    if note:
        target.note = note
    return rows


def render_block(rows: list[_Row]) -> tuple[str, str, str]:
    status, decision, verdict = _decide(rows)
    ordered = [r for s in SCORERS for r in rows if r.scorer == s] + \
              [r for r in rows if r.scorer not in SCORERS]
    body = "\n".join(r.render() for r in ordered)
    block = (
        f"{SECTION}\n\nvalidation_status: {status}\ndecision: {decision}\n\n"
        f"{_NOTE}\n\n{_HEADER}\n{_SEP}\n{body}\n\n合议: {verdict}\n"
    )
    return block, status, decision


def update_scores_text(md: str, scorer: str, da: int | None, qing: int | None,
                       guo: int | None, note: str) -> tuple[str, dict[str, str]]:
    if scorer not in SCORERS:
        raise PerfScorePathError(f"unknown scorer {scorer!r}")
    idx = md.find(SECTION)
    rows = _parse_rows(md[idx:]) if idx != -1 else _seed_rows()
    rows = _merge(rows, scorer, da, qing, guo, note.strip())
    block, status, decision = render_block(rows)
    head = (md[:idx].rstrip() + "\n\n") if idx != -1 else (md.rstrip() + "\n\n")
    _, _, verdict = _decide(rows)
    return head + block, {"validation_status": status, "decision": decision, "verdict": verdict}


class PerfScorer:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def apply(self, rel_path: str, scorer: str, da_yi: int | None, qing_xu: int | None,
              guo_huo: int | None, note: str = "") -> dict[str, str]:
        norm = (rel_path or "").replace("\\", "/")
        if not norm or "_performances/" not in norm:
            raise PerfScorePathError("path must be a _performances entry")
        if not self._exposed.is_inside(norm):
            raise PerfScorePathError("path outside sandbox")
        target = self._resolver.resolve(norm)
        if target is None or not target.is_file():
            raise PerfScorePathError("entry file does not exist")
        md = target.read_text(encoding="utf-8")
        new_md, result = update_scores_text(md, scorer, da_yi, qing_xu, guo_huo, note)
        target.write_text(new_md.rstrip("\n") + "\n", encoding="utf-8")
        result["path"] = norm
        return result
