from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable


class QAParseError(ValueError):
    pass


@dataclass
class InterviewOptionData:
    key: str
    text: str
    picked: bool = False
    freeform_value: str | None = None


@dataclass
class InterviewQuestionData:
    qid: str
    perspective: str
    text: str
    kind: str = "single"
    options: list[InterviewOptionData] = field(default_factory=list)
    notes: str | None = None


@dataclass
class InterviewRoundData:
    number: int
    questions: list[InterviewQuestionData] = field(default_factory=list)


@dataclass
class InterviewQAData:
    task_id: str
    initial_prompt_ref: str
    rounds: list[InterviewRoundData] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    raw_header_extras: list[str] = field(default_factory=list)


_PICKED_MARKERS = ("← user picked", "<- user picked", "← picked", "user picked")
_OPTION_LINE = re.compile(r"^\s*-\s*(?:\[[ xX]\]\s*)?\*{0,2}([a-z])\)\*{0,2}\s+(.+?)\s*$")
_QUESTION_LINE = re.compile(r"^####\s+(Q\d+):\s+(.+?)\s*$")
_PERSPECTIVE_LINE = re.compile(r"^###\s+(.+?)\s*$")
_ROUND_LINE = re.compile(r"^##\s+Round\s+(\d+).*$")
_NOTES_LINE = re.compile(r"^\*\*Notes:\*\*\s*(.*)$")
_PROMPT_REF_LINE = re.compile(
    r"^\*\*Initial prompt:\*\*\s*see\s+`([^`]+)`",
    re.IGNORECASE,
)


def _strip_marker(text: str) -> tuple[str, bool]:
    cleaned = text
    picked = False
    for marker in _PICKED_MARKERS:
        if marker in cleaned:
            picked = True
            cleaned = cleaned.replace(marker, "").strip()
    cleaned = cleaned.rstrip(" *")
    return cleaned.strip(), picked


def _strip_emphasis(text: str) -> str:
    if text.startswith("**") and text.endswith("**"):
        return text[2:-2].strip()
    return text


def parse_qa(source: str) -> InterviewQAData:
    lines = source.splitlines()
    task_id = ""
    prompt_ref = ""
    header_extras: list[str] = []
    rounds: list[InterviewRoundData] = []
    open_questions: list[str] = []

    current_round: InterviewRoundData | None = None
    current_perspective = ""
    current_question: InterviewQuestionData | None = None
    in_open_block = False

    def commit_question() -> None:
        nonlocal current_question
        if current_question is not None and current_round is not None:
            current_round.questions.append(current_question)
        current_question = None

    for raw in lines:
        line = raw.rstrip()
        if not task_id and line.startswith("# Interview"):
            parts = line.split("—", 1)
            if len(parts) == 2:
                task_id = parts[1].strip()
            continue
        m = _PROMPT_REF_LINE.match(line)
        if m:
            prompt_ref = m.group(1).strip()
            continue
        if line.lower().startswith("**initial prompt:**"):
            continue
        if line.startswith("**Rounds:**"):
            header_extras.append(line)
            continue
        m = _ROUND_LINE.match(line)
        if m:
            commit_question()
            current_round = InterviewRoundData(number=int(m.group(1)))
            rounds.append(current_round)
            in_open_block = False
            continue
        if line.startswith("## Open Questions"):
            commit_question()
            current_round = None
            in_open_block = True
            continue
        if in_open_block:
            stripped = line.lstrip("- ").strip()
            if stripped:
                open_questions.append(stripped)
            continue
        m = _PERSPECTIVE_LINE.match(line)
        if m and current_round is not None:
            commit_question()
            current_perspective = m.group(1).strip()
            continue
        m = _QUESTION_LINE.match(line)
        if m and current_round is not None:
            commit_question()
            current_question = InterviewQuestionData(
                qid=m.group(1),
                perspective=current_perspective,
                text=m.group(2).strip(),
            )
            continue
        m = _OPTION_LINE.match(line)
        if m and current_question is not None:
            key = m.group(1)
            text_with_markers = m.group(2)
            text, picked = _strip_marker(text_with_markers)
            text = _strip_emphasis(text)
            current_question.options.append(
                InterviewOptionData(key=key, text=text, picked=picked)
            )
            continue
        m = _NOTES_LINE.match(line)
        if m and current_question is not None:
            current_question.notes = m.group(1).strip() or None
            continue

    commit_question()

    if not task_id:
        raise QAParseError("missing '# Interview — {task_id}' header")

    return InterviewQAData(
        task_id=task_id,
        initial_prompt_ref=prompt_ref or "initial_prompt.md",
        rounds=rounds,
        open_questions=open_questions,
        raw_header_extras=header_extras,
    )


def render_qa(data: InterviewQAData) -> str:
    out: list[str] = []
    out.append(f"# Interview — {data.task_id}")
    out.append("")
    out.append(f"**Initial prompt:** see `{data.initial_prompt_ref}`.")
    out.append("")
    for extra in data.raw_header_extras:
        out.append(extra)
    if data.raw_header_extras:
        out.append("")
    for rnd in data.rounds:
        out.append(f"## Round {rnd.number}")
        out.append("")
        last_perspective = ""
        for q in rnd.questions:
            if q.perspective and q.perspective != last_perspective:
                out.append(f"### {q.perspective}")
                out.append("")
                last_perspective = q.perspective
            out.append(f"#### {q.qid}: {q.text}")
            for opt in q.options:
                marker = "  ← user picked" if opt.picked else ""
                bold_open = "**" if opt.picked else ""
                bold_close = "**" if opt.picked else ""
                out.append(f"- {bold_open}{opt.key}) {opt.text}{bold_close}{marker}")
            if q.notes:
                out.append(f"**Notes:** {q.notes}")
            out.append("")
    if data.open_questions:
        out.append("## Open Questions")
        out.append("")
        for item in data.open_questions:
            out.append(f"- {item}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def serialize_questions(rounds: Iterable[InterviewRoundData]) -> list[dict]:
    out: list[dict] = []
    for rnd in rounds:
        for q in rnd.questions:
            out.append({
                "round": rnd.number,
                "qid": q.qid,
                "perspective": q.perspective,
                "text": q.text,
                "kind": q.kind,
                "options": [
                    {
                        "key": opt.key,
                        "text": opt.text,
                        "picked": opt.picked,
                        "freeform_value": opt.freeform_value,
                    }
                    for opt in q.options
                ],
                "notes": q.notes,
            })
    return out
