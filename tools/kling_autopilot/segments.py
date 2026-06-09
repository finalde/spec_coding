from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SegmentKind = Literal["text", "element"]


@dataclass(frozen=True)
class PromptSegment:
    kind: SegmentKind
    value: str


def parse_segments(prompt: str, element_names: list[str]) -> list[PromptSegment]:
    names = sorted(element_names, key=len, reverse=True)
    segments: list[PromptSegment] = []
    buffer = ""
    index = 0
    length = len(prompt)
    while index < length:
        if prompt[index] == "@":
            matched = next((n for n in names if prompt.startswith(n, index + 1)), None)
            if matched is not None:
                if buffer:
                    segments.append(PromptSegment("text", buffer))
                    buffer = ""
                segments.append(PromptSegment("element", matched))
                index += 1 + len(matched)
                continue
        buffer += prompt[index]
        index += 1
    if buffer:
        segments.append(PromptSegment("text", buffer))
    return segments


def element_count(segments: list[PromptSegment]) -> int:
    return sum(1 for segment in segments if segment.kind == "element")
