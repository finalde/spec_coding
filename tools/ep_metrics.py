"""Per-episode fact & metrics generator for AI 短剧 shots.

Scans an episode's shotNN.md files, extracts per-line 台词 + 时长目标 + shot 时长,
computes 字/秒 by voice type, flags over-speed lines, and writes a derived
metrics.md fact sheet (recomputable cache, not a canonical authoring surface).

Usage:
    python tools/ep_metrics.py wushen_juexing ep02
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

CJK = re.compile(r"[一-鿿]")
NUM = re.compile(r"\d+(?:\.\d+)?")

# 字/秒 上限（与 ai_videos__时长节奏 PA1/PA2 对齐）
CAP_OS = 3.5        # 内心独白 / OS / 情绪慢镜
CAP_SLOW = 3.5      # 慢嗓角色（老者/气虚/虚弱/低声/偏慢）
CAP_NORMAL = 5.0    # 普通对白上限（目标 ≤4）
SLOW_HINTS = ("偏慢", "苍老", "气虚", "虚弱", "低声", "老者", "孩童", "垂死", "重伤")


def cjk_len(s: str) -> int:
    return len(CJK.findall(s))


def first_num(s: str) -> float | None:
    m = NUM.search(s)
    return float(m.group()) if m else None


@dataclass
class Line:
    role: str
    kind: str
    pace: str
    text: str
    target: float | None

    @property
    def chars(self) -> int:
        return cjk_len(self.text)

    @property
    def cps(self) -> float | None:
        if not self.target:
            return None
        return round(self.chars / self.target, 2)

    @property
    def cap(self) -> float:
        if "内心独白" in self.kind or "OS" in self.kind:
            return CAP_OS
        blob = self.pace + self.role
        if any(h in blob for h in SLOW_HINTS):
            return CAP_SLOW
        return CAP_NORMAL

    @property
    def over(self) -> bool:
        return self.cps is not None and self.cps > self.cap


@dataclass
class Shot:
    sid: str
    duration: float | None
    lines: list[Line] = field(default_factory=list)

    @property
    def total_chars(self) -> int:
        return sum(l.chars for l in self.lines)

    @property
    def target_sum(self) -> float:
        return round(sum(l.target or 0 for l in self.lines), 1)


def parse_blocks(section: str) -> list[Line]:
    lines: list[Line] = []
    for blk in re.findall(r"```text(.*?)```", section, re.S):
        kv = {}
        for raw in blk.splitlines():
            parts = re.split(r"[:：]", raw.strip(), maxsplit=1)
            if len(parts) == 2:
                kv[parts[0].strip()] = parts[1].strip()
        if "台词" not in kv:
            continue
        lines.append(Line(
            role=kv.get("角色", "?"),
            kind=kv.get("类型", ""),
            pace=kv.get("语速", ""),
            text=kv.get("台词", ""),
            target=first_num(kv.get("时长目标", "")),
        ))
    return lines


def parse_shot(md: Path) -> Shot:
    txt = md.read_text(encoding="utf-8")
    sid = md.stem
    dur = None
    mdur = re.search(r"时长[:：]\s*([\d.]+)\s*秒", txt)
    if mdur:
        dur = float(mdur.group(1))
    # 台词配音 prompt 段（到下一个 ## 或文件尾）
    voice = re.split(r"##\s*台词配音\s*prompt", txt, maxsplit=1)
    lines = parse_blocks(voice[1]) if len(voice) > 1 else []
    return Shot(sid=sid, duration=dur, lines=lines)


def render(name: str, ep: str, shots: list[Shot]) -> str:
    out: list[str] = []
    out.append(f"# {name} / {ep} — Fact & Metrics（自动生成·派生缓存）\n")
    out.append("> 由 `tools/ep_metrics.py` 从各 shotNN.md 重算；勿手改。字/秒上限："
               f"OS/慢嗓 {CAP_OS}、普通对白 {CAP_NORMAL}（目标 ≤4）。⚠=超速。\n")

    tot_dur = sum(s.duration or 0 for s in shots)
    tot_chars = sum(s.total_chars for s in shots)
    n_lines = sum(len(s.lines) for s in shots)
    over = [(s, l) for s in shots for l in s.lines if l.over]

    out.append("## 集级汇总\n")
    out.append(f"- 镜数：{len(shots)}")
    out.append(f"- 总时长：{round(tot_dur,1)} 秒（{round(tot_dur/60,2)} 分）")
    out.append(f"- 台词总字数：{tot_chars}（{n_lines} 句）")
    if tot_dur:
        out.append(f"- 全集平均：{round(tot_chars/tot_dur,2)} 字/秒")
    out.append(f"- ⚠ 超速句数：{len(over)}" + (
        "（达标）" if not over else "（需修：见下方标 ⚠ 行）"))
    out.append("")

    out.append("## 逐镜逐句\n")
    out.append("| 镜 | 时长s | 角色 | 类型 | 字数 | 时长目标s | 字/秒 | 上限 | 判定 |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for s in shots:
        if not s.lines:
            out.append(f"| {s.sid} | {s.duration or '?'} | — | (无台词) | 0 | — | — | — | ok |")
            continue
        sum_warn = "" if s.duration is None or s.target_sum <= s.duration else " ⚠时长目标和超镜长"
        for i, l in enumerate(s.lines):
            head = s.sid if i == 0 else ""
            dur = (s.duration if i == 0 else "")
            verdict = "⚠ 超速" if l.over else "ok"
            kind = l.kind.replace("正常台词", "对白").replace("内心独白", "OS")
            out.append(
                f"| {head} | {dur} | {l.role} | {kind} | {l.chars} | "
                f"{l.target or '?'} | {l.cps if l.cps is not None else '?'} | "
                f"{l.cap} | {verdict} |")
        if sum_warn:
            out.append(f"| {s.sid} 合计 | {s.duration} | | | {s.total_chars} | "
                       f"{s.target_sum} | | |{sum_warn} |")
    out.append("")

    if over:
        out.append("## ⚠ 超速明细（需 时长节奏/台词大师 处理）\n")
        for s, l in over:
            out.append(f"- **{s.sid}** {l.role}（{l.kind}）：{l.chars}字÷{l.target}s="
                       f"**{l.cps}字/秒** > 上限{l.cap}。建议：加时长或精简——「{l.text}」")
        out.append("")
    return "\n".join(out)


def main() -> int:
    if len(sys.argv) < 3:
        sys.stderr.write("usage: ep_metrics.py <drama_name> <epNN>\n")
        return 2
    name, ep = sys.argv[1], sys.argv[2]
    root = Path(__file__).resolve().parents[1]
    ep_dir = root / "ai_videos" / name / "5_6_分镜与prompt" / "episodes" / ep
    shot_files = sorted(ep_dir.glob("shots/shot*/shot*.md"))
    if not shot_files:
        sys.stderr.write(f"no shots under {ep_dir}\n")
        return 1
    shots = [parse_shot(f) for f in shot_files]
    out_md = ep_dir / "metrics.md"
    out_md.write_text(render(name, ep, shots), encoding="utf-8")
    n_over = sum(1 for s in shots for l in s.lines if l.over)
    msg = (f"wrote {out_md.relative_to(root)} | shots={len(shots)} "
           f"over_speed_lines={n_over}\n")
    sys.stdout.write(msg.encode("ascii", "backslashreplace").decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
