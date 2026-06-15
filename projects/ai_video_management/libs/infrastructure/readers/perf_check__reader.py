"""Assemble a copy-paste "让 Claude 检查已下载 MP4 并打分" prompt for a
performance-library entry (`perf_NNNN.md`).

The user downloads a render into the entry's `renders/` folder, then clicks
「🎬 让 Claude 检查 MP4 并打分」on the perf-score panel. This locates the MP4
directly under `renders/`:

- 0 个 → `kind=no_mp4`（未发现已下载的 MP4）。
- >1 个 → `kind=multiple_mp4`（发现多个，需指明是哪一个）。
- 恰好 1 个 → 组装一段 prompt，用户粘到 Claude Code CLI：抽帧检查该 MP4，
  对照本 entry 的目标情绪 / 锁定文本块在三轴（表演达意 / 情绪可识别 / 是否过火）
  上打分，并 `POST /api/perf-score`（`who=Claude`）写回。

只扫描 `renders/` 的直接子文件（`.mp4`，大小写不敏感），不递归 `archive/` 等子目录
——与 episode-concat / downloads 的「每镜最新 renders mp4」约定一致。
"""
from __future__ import annotations

import re
from pathlib import Path

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.casting__error import InvalidDramaPathError

_PERF_ENTRY = re.compile(r"_performances/[^/]+/(perf_\d{4})/\1\.md$")
_BACKEND = "http://127.0.0.1:8766"


class PerfCheckPathError(InvalidDramaPathError):
    pass


class PerfCheckPromptReader:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def build(self, rel_path: str) -> dict[str, object]:
        norm = (rel_path or "").replace("\\", "/")
        m = _PERF_ENTRY.search(norm)
        if not norm or not self._exposed.is_inside(norm) or m is None:
            raise PerfCheckPathError("not a performance-library entry path")
        entry = self._resolver.resolve(norm)
        if entry is None or not entry.is_file():
            raise PerfCheckPathError("perf entry file does not exist")
        perf_id = m.group(1)
        renders = entry.parent / "renders"
        mp4s = (
            sorted(p for p in renders.iterdir() if p.is_file() and p.suffix.lower() == ".mp4")
            if renders.is_dir()
            else []
        )
        if not mp4s:
            return {
                "ok": False,
                "kind": "no_mp4",
                "message": f"未发现已下载的 MP4 — 先把渲染好的视频放进 `{perf_id}/renders/`（或用「从下载导入」），再点评分。",
                "prompt": "",
                "mp4": "",
                "candidates": [],
            }
        if len(mp4s) > 1:
            names = [p.name for p in mp4s]
            return {
                "ok": False,
                "kind": "multiple_mp4",
                "message": f"`{perf_id}/renders/` 下发现 {len(names)} 个 MP4，无法确定评哪一个：{', '.join(names)}。请只保留要评的那个（其余移到 archive/ 或删除）。",
                "prompt": "",
                "mp4": "",
                "candidates": names,
            }
        mp4 = mp4s[0]
        mp4_rel = mp4.relative_to(self._resolver.root).as_posix()
        return {
            "ok": True,
            "kind": "ok",
            "message": f"已锁定 1 个 MP4：{mp4.name} — 复制下面的 prompt 到 Claude Code CLI 执行。",
            "prompt": self._assemble(norm, perf_id, mp4_rel),
            "mp4": mp4_rel,
            "candidates": [mp4.name],
        }

    @staticmethod
    def _assemble(entry_rel: str, perf_id: str, mp4_rel: str) -> str:
        parts: list[str] = []
        parts.append(f"# 任务：检查已下载的检验视频并给出 Claude 表演评分（{perf_id}）")
        parts.append("")
        parts.append(f"- 表演库条目：`{entry_rel}`")
        parts.append(f"- 待评 MP4：`{mp4_rel}`")
        parts.append("")
        parts.append("## 步骤")
        parts.append(f"1. 先读条目 `{entry_rel}`：拿到**目标情绪**、`## 锁定文本块` 里的物理动作要点、以及达标线（表演达意≥4 且 情绪可识别≥4 且 是否过火≤2）。")
        parts.append(f"2. 抽帧检查 `{mp4_rel}`：用 ffmpeg 均匀抽 6–10 帧（外加几张关键动作帧），再逐帧看图——")
        parts.append("   ```bash")
        parts.append(f"   ffmpeg -i \"{mp4_rel}\" -vf fps=2 -y /tmp/{perf_id}_%02d.png   # 按视频时长调 fps")
        parts.append("   ```")
        parts.append("   然后用 Read 工具逐张读出 `/tmp/` 下的帧。")
        parts.append("3. 按三轴各打 1–5 分（**盲看**判断，不要被 prompt 的文字暗示）：")
        parts.append("   - **表演达意 da_yi**：锁定块里的物理动作是否真的被渲出（1 几乎被忽略 → 5 全部 land）。")
        parts.append("   - **情绪可识别 qing_xu**：盲看能否认出目标情绪（1 认不出 → 5 一眼即中）。")
        parts.append("   - **是否过火 guo_huo**：1 自然克制 → 5 严重过火（**越低越好**）。")
        parts.append("4. 把 Claude 这一行评分写回（后端默认跑在 " + _BACKEND + "，按你的实际端口改）：")
        parts.append("   ```bash")
        parts.append(f"   curl -s -X POST {_BACKEND}/api/perf-score \\")
        parts.append("     -H 'Content-Type: application/json' \\")
        parts.append(f"     -d '{{\"path\":\"{entry_rel}\",\"who\":\"Claude\",\"da_yi\":<1-5>,\"qing_xu\":<1-5>,\"guo_huo\":<1-5>,\"note\":\"<哪些词 land/被忽略/过火点，一句话>\"}}'")
        parts.append("   ```")
        parts.append("   该接口会重算 你+Claude 的合议（accept / revise / pending）并写回条目的 `## 实测与验证` 表。")
        parts.append("")
        parts.append("评分要克制、对照达标线给理由；过火轴记住越低越好。完成后回我一句最终合议结果。")
        return "\n".join(parts)
