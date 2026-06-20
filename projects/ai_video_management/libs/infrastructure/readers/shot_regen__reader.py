"""Assemble a copy-paste regeneration prompt for a drama shot that references
the performance library (per ai_video.md rule 9b / performance_library FR-10 v2
+ FR-17).

A shot.md annotates `表演库参考: perf_NNNN (...) — 用于 <角色> <beat>`. When the
user updates the library and clicks 「🎭 按表演库重生成」, this reads each
referenced entry's CURRENT `## 锁定文本块` and emits a prompt the user pastes
into Claude Code: re-weave the latest performance content into THIS shot's
`动作:`/`表情:` per its plot (adapt, don't copy verbatim).
"""
from __future__ import annotations

import re
from pathlib import Path

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.casting__error import InvalidDramaPathError

_REF_LINE = re.compile(r"表演库参考[:：]\s*(perf_\d{4})\s*(.*)")
_PERF_ID = re.compile(r"^perf_\d{4}$")


class ShotRegenPathError(InvalidDramaPathError):
    pass


class ShotRegenPromptReader:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def build(
        self,
        rel_shot_path: str,
        selected_perf_ids: list[str] | None = None,
    ) -> dict[str, object]:
        norm = (rel_shot_path or "").replace("\\", "/")
        if not norm or not self._exposed.is_inside(norm):
            raise ShotRegenPathError("shot path outside sandbox")
        shot = self._resolver.resolve(norm)
        if shot is None or not shot.is_file():
            raise ShotRegenPathError("shot file does not exist")
        shot_md = shot.read_text(encoding="utf-8")
        # When the caller passes an explicit selection, assemble the prompt from
        # those perf_ids (deduped, order preserved) instead of scanning the
        # shot's already-annotated `表演库参考:` lines.
        if selected_perf_ids:
            seen: set[str] = set()
            refs = []
            for pid in selected_perf_ids:
                if pid in seen:
                    continue
                seen.add(pid)
                refs.append((pid, ""))
        else:
            refs = _REF_LINE.findall(shot_md)
        if not refs:
            return {
                "prompt": "",
                "refs": [],
                "message": "本 shot 未标注 `表演库参考:`，无法按表演库重生成。先在 ## Shot context 加 `表演库参考: perf_NNNN (...) — 用于 <角色> <beat>`。",
            }
        blocks: list[dict[str, str]] = []
        for perf_id, tail in refs:
            entry = self._find_perf(perf_id)
            if entry is None:
                blocks.append({"perf_id": perf_id, "tail": tail.strip(), "locked": "", "missing": "true"})
                continue
            locked, title = self._locked_block(entry)
            blocks.append({"perf_id": perf_id, "tail": tail.strip(), "title": title, "locked": locked})
        prompt = self._assemble(norm, shot_md, blocks)
        return {"prompt": prompt, "refs": [b["perf_id"] for b in blocks], "message": ""}

    def _find_perf(self, perf_id: str) -> Path | None:
        if not _PERF_ID.match(perf_id):
            return None
        root = self._resolver.root / "ai_videos" / "_performances"
        if not root.is_dir():
            return None
        for emotion in root.iterdir():
            if not emotion.is_dir() or emotion.name.startswith("_"):
                continue
            cand = emotion / perf_id / f"{perf_id}.md"
            if cand.is_file():
                return cand
        return None

    @staticmethod
    def _locked_block(entry: Path) -> tuple[str, str]:
        md = entry.read_text(encoding="utf-8")
        title = ""
        for line in md.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        locked = ""
        idx = md.find("## 锁定文本块")
        if idx != -1:
            after = md[idx:]
            fences = [m.start() for m in re.finditer(r"```", after)]
            if len(fences) >= 2:
                locked = after[fences[0] + 3:fences[1]].strip()
        return locked, title

    @staticmethod
    def _shot_context(shot_md: str) -> str:
        idx = shot_md.find("## Shot context")
        if idx == -1:
            return ""
        end = shot_md.find("\n## ", idx + 1)
        return shot_md[idx:end if end != -1 else len(shot_md)].strip()

    def _assemble(self, shot_path: str, shot_md: str, blocks: list[dict[str, str]]) -> str:
        ctx = self._shot_context(shot_md)
        parts: list[str] = []
        parts.append("# 任务：按表演演技库重新生成本 shot 的表演（动作/表情）")
        parts.append("")
        parts.append(f"目标 shot：`{shot_path}`")
        parts.append("")
        parts.append("## 怎么做（融入，不照抄 — 契约 ai_video.md 9b / FR-10 v2）")
        parts.append("- 重读下面每条被引表演库 entry 的**最新锁定文本块**，把其**物理动作要点**改写进本 shot 的 `动作:` / `表情:` 字段。")
        parts.append("- 保留「写物理动作不写情绪名」的内核与关键肌肉动作；但按**本 shot 的角色 / 机位 / 时长 / 剧情语境**重新措辞、按本镜时长拆 timed beats、并入本镜既有走位与台词。")
        parts.append("- **不要**把 entry 的检验视频 prompt 整段粘进来。其它字段（镜头/场景/光线/台词等）保持不变，只更新表演相关字段。")
        parts.append("- 保留 shot 的 `表演库参考:` 标注行。")
        parts.append("- **重生范围：本 shot**；若本次表演改动影响开场/结尾的情绪走向，连带相邻 shot / 本集 episode 一并 review（见 ai_video.md 2026-06-16 / 2026-06-17 连贯性契约 — 改动剧本/台词/表演后默认做相邻+全剧序列连贯性 check）。")
        parts.append("")
        parts.append("## 本 shot 当前 Shot context")
        parts.append("")
        parts.append("```")
        parts.append(ctx or "(无 ## Shot context)")
        parts.append("```")
        parts.append("")
        parts.append("## 被引用的表演库 entry（最新锁定块）")
        for b in blocks:
            parts.append("")
            if b.get("missing"):
                parts.append(f"### {b['perf_id']} — ⚠ 未找到该 entry（库里不存在），请核对编号。{(' ' + b['tail']) if b['tail'] else ''}")
                continue
            head = f"### {b['perf_id']}"
            if b.get("title"):
                head += f" · {b['title']}"
            parts.append(head)
            if b["tail"]:
                parts.append(f"> 引用说明: {b['tail']}")
            parts.append("")
            parts.append("```")
            parts.append(b["locked"] or "(该 entry 无锁定文本块)")
            parts.append("```")
        parts.append("")
        parts.append("完成后把更新写回该 shot.md 的 `## 视频 prompt` 代码块。")
        return "\n".join(parts)
