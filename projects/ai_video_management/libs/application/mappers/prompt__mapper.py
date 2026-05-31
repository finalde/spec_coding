"""Prompt-suggestion mapper — follow-up 117.

Pure functions that (a) build the Anthropic system + user payload from a
`SuggestRefinementsInputQdto` and (b) parse the model's JSON reply into a
`SuggestRefinementsQdto`. Keeping prompt construction + parsing here leaves
`PromptQuery` as a thin orchestrator and the client as a thin transport.
"""
from __future__ import annotations

import json
import re
from typing import Any

from libs.application.dtos.prompt__dto import (
    RefinementSuggestionQdto,
    SuggestRefinementsInputQdto,
    SuggestRefinementsQdto,
)

_SYSTEM_GUIDE = (
    "你是一位资深仙侠 / 古装短剧分镜导演，兼任 AI 视频生成模型（Kling / Seedance / Sora / Veo）"
    "的 prompt master。用户正在逐字段细化一个 shot（镜头）的视频 prompt：他点击某个维度（栏目），"
    "你要根据该 shot 当前的剧情场景与已填写的其他维度，为这个维度给出若干条精炼、可直接落入该字段的中文细化选项。\n\n"
    "硬性要求：\n"
    "1. 只针对用户指定的那一个维度作答，不要改写或建议其他维度。\n"
    "2. 每条选项是【可直接粘贴进该字段的中文正文】，不带字段名前缀（不要写「镜头:」之类），不带引号包裹。\n"
    "3. 选项之间走不同的导演思路（不同景别 / 不同情绪走向 / 不同节奏），不要互相重复。\n"
    "4. 贴合该 shot 的剧情、场景基调与已有维度；仙侠真人写实风格，禁止动漫 / 卡通措辞。\n"
    "5. 措辞精炼，符合 prompt 字数克制原则（单条尽量 ≤ 80 字，多拍动作可稍长）。\n"
    "6. 严格只输出一个 JSON 数组，不要任何解释、不要 markdown 代码围栏。"
    '数组每个元素形如 {"value": "<可粘贴的中文正文>", "rationale": "<一句中文，说明为何贴合本镜>"}。'
)

# Per-dimension nudges appended to the user message. Keyed by whitespace-
# stripped label so `光线 / 色调` and `光线/色调` both match.
_DIMENSION_HINTS: dict[str, str] = {
    "镜头": "给出「景别 + 运动」组合（如 大全景仰拍 / 中近景特写 + 急推），可含一句运动节奏描述。",
    "运镜": "聚焦摄影机运动（推/拉/摇/移/升降/环绕/手持），与镜头景别配合。",
    "动作": "按 timed beats 写（如 0–2s … / 2–4s …），各拍之和应等于时长；最后一拍是落点静态。",
    "台词": "三选一：内嵌硬字幕 / 后期软字幕 / 无台词默剧；给出贴合本镜情绪的台词原文与字体调性。",
    "台词/字幕": "三选一：内嵌硬字幕 / 后期软字幕 / 无台词默剧；给出贴合本镜情绪的台词原文与字体调性。",
    "光线/色调": "描述光源方向、明暗对比与主色调 hex 倾向，呼应场景基调。",
    "节奏": "用 visual-only 的节奏词（慢 / 中等 / 快 / 顿挫 / 急促），贴合戏剧张力。",
    "渲染样式": "影视级真人写实关键词组合（cinematic / 4K HDR / 真实毛孔 / 东方面孔 等），≤ 9 个核心词。",
    "场景": "给出该地点的一句话锁定式描述（含变体状态，如 雷劫态 / 黄昏），与场景档一致。",
    "人物": "给出本镜出场角色的组合方式（主体 + 配角 / 光影剪影），不展开外貌细节。",
    "比例": "竖屏短剧默认 9:16；按平台需要给候选比例。",
    "时长": "3–15s，按本镜剧情节拍给出贴合的秒数（黄金钩 / 铺垫可偏长，反应快切偏短）。",
}


def _norm(label: str) -> str:
    return re.sub(r"\s+", "", label)


class PromptMapper:
    @staticmethod
    def build_system_blocks() -> list[dict[str, Any]]:
        return [
            {
                "type": "text",
                "text": _SYSTEM_GUIDE,
                "cache_control": {"type": "ephemeral"},
            }
        ]

    @staticmethod
    def build_user_text(inp: SuggestRefinementsInputQdto) -> str:
        hint = _DIMENSION_HINTS.get(_norm(inp.dimension), "")
        lines: list[str] = []
        if inp.drama:
            lines.append(f"剧目: {inp.drama}")
        if inp.scene:
            lines.append(f"场景档: {inp.scene}")
        lines.append(f"要细化的维度（栏目）: 「{inp.dimension}」")
        if hint:
            lines.append(f"该维度写法提示: {hint}")
        lines.append(f"请给出 {inp.count} 条不同思路的细化选项。")
        lines.append("")
        lines.append("【该维度当前内容】")
        lines.append(inp.current_value.strip() or "（空）")
        lines.append("")
        lines.append("【本镜完整 prompt 当前内容（供保持一致，勿改其他字段）】")
        lines.append(inp.prompt_body.strip() or "（空）")
        if inp.shot_context.strip():
            lines.append("")
            lines.append("【本镜剧情 / 场景上下文】")
            lines.append(inp.shot_context.strip())
        return "\n".join(lines)

    @staticmethod
    def parse_response(text: str, dimension: str, count: int) -> SuggestRefinementsQdto:
        raw = _strip_code_fence(text).strip()
        start = raw.find("[")
        end = raw.rfind("]")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("响应中未找到 JSON 数组")
        try:
            parsed = json.loads(raw[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSON 解析失败: {exc}") from exc
        if not isinstance(parsed, list):
            raise ValueError("响应顶层不是数组")
        suggestions: list[RefinementSuggestionQdto] = []
        for item in parsed:
            if not isinstance(item, dict):
                continue
            value = str(item.get("value", "")).strip()
            if not value:
                continue
            rationale = str(item.get("rationale", "")).strip()
            suggestions.append(RefinementSuggestionQdto(value=value, rationale=rationale))
        if not suggestions:
            raise ValueError("响应中没有可用的建议项")
        return SuggestRefinementsQdto(
            dimension=dimension,
            suggestions=tuple(suggestions[:count]),
        )


def _strip_code_fence(text: str) -> str:
    fence = re.match(r"^\s*```[a-zA-Z]*\n(.*)\n```\s*$", text, re.DOTALL)
    return fence.group(1) if fence else text
