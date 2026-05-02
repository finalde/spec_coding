from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from libs.exposed_tree import ExposedTree
from libs.file_reader import FileReadError
from libs.file_writer import write_file
from libs.safe_resolve import OutsideSandbox, SymlinkRefused, safe_resolve

PROMOTED_FILENAME: str = "promoted.md"

_VALID_STAGES: frozenset[str] = frozenset({"interview", "findings", "final_specs", "validation"})

_PIN_HEADING_RE = re.compile(r"^##\s+(pin-\d+)\s+—\s+(.+?)\s*$")


@dataclass(frozen=True)
class Pin:
    pin_id: str
    location: str  # "<source_file> / <id_or_path>"
    body: str  # verbatim markdown of the pinned item


@dataclass(frozen=True)
class PromotedFile:
    stage_path: str  # e.g., "specs/development/spec_driven/interview"
    pins: tuple[Pin, ...]


def parse_promoted_text(text: str) -> tuple[Pin, ...]:
    if not text.strip():
        return ()
    lines = text.split("\n")
    pins: list[Pin] = []
    cur_id: str | None = None
    cur_loc: str | None = None
    cur_body: list[str] = []
    in_pin = False
    for line in lines:
        m = _PIN_HEADING_RE.match(line)
        if m is not None:
            if in_pin and cur_id is not None and cur_loc is not None:
                pins.append(_finalize_pin(cur_id, cur_loc, cur_body))
            cur_id = m.group(1)
            cur_loc = m.group(2).strip()
            cur_body = []
            in_pin = True
            continue
        if in_pin:
            cur_body.append(line)
    if in_pin and cur_id is not None and cur_loc is not None:
        pins.append(_finalize_pin(cur_id, cur_loc, cur_body))
    return tuple(pins)


def _finalize_pin(pin_id: str, location: str, body_lines: list[str]) -> Pin:
    while body_lines and body_lines[0].strip() == "":
        body_lines.pop(0)
    while body_lines and body_lines[-1].strip() == "":
        body_lines.pop()
    return Pin(pin_id=pin_id, location=location, body="\n".join(body_lines))


def render_promoted_text(stage: str, pins: tuple[Pin, ...]) -> str:
    parts: list[str] = []
    parts.append(f"# Promoted items — {stage}")
    parts.append("")
    parts.append(
        "INPUT to regeneration. Items here MUST appear verbatim in the regenerated "
        "artifact. Managed via the 📌 toggle in the spec_driven webapp; remove only "
        "by manual delete or unpin."
    )
    parts.append("")
    parts.append(
        "See `CLAUDE.md → ## Regeneration prompts & autonomous mode → "
        "### Regeneration semantics → ### Pinned items survive regeneration` for the contract."
    )
    parts.append("")
    for pin in pins:
        parts.append(f"## {pin.pin_id} — {pin.location}")
        parts.append("")
        parts.append(pin.body)
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def _next_pin_id(existing: tuple[Pin, ...]) -> str:
    max_n = 0
    for p in existing:
        m = re.match(r"^pin-(\d+)$", p.pin_id)
        if m is not None:
            n = int(m.group(1))
            if n > max_n:
                max_n = n
    return f"pin-{max_n + 1:03d}"


def _resolve_stage_dir(stage_path: str, repo_root: Path) -> tuple[Path, str]:
    """Resolves a stage_path string like 'specs/development/spec_driven/interview'
    to its absolute directory and returns (absolute_dir, stage_name).
    Raises FileReadError on bad input."""
    try:
        rel = safe_resolve(stage_path, repo_root)
    except (OutsideSandbox, SymlinkRefused):
        raise FileReadError(400, "outside_sandbox", kind="outside_sandbox")
    abs_dir = (repo_root / rel).resolve(strict=False)
    if not abs_dir.is_dir():
        raise FileReadError(404, "not_found", kind="stage_dir_missing")
    parts = rel.parts
    if len(parts) != 4 or parts[0] != "specs":
        raise FileReadError(400, "outside_sandbox", kind="not_a_stage_dir")
    stage = parts[3]
    if stage not in _VALID_STAGES:
        raise FileReadError(400, "outside_sandbox", kind="not_a_stage_dir")
    return abs_dir, stage


def list_promotions(stage_path: str, repo_root: Path) -> PromotedFile:
    abs_dir, _ = _resolve_stage_dir(stage_path, repo_root)
    target = abs_dir / PROMOTED_FILENAME
    if not target.is_file():
        return PromotedFile(stage_path=stage_path, pins=())
    try:
        text = target.read_text(encoding="utf-8", errors="replace")
    except OSError as err:
        raise FileReadError(500, "read_failed") from err
    return PromotedFile(stage_path=stage_path, pins=parse_promoted_text(text))


def add_promotion(
    stage_path: str,
    location: str,
    body: str,
    repo_root: Path,
) -> Pin:
    if not location.strip():
        raise FileReadError(400, "invalid_request", kind="empty_location")
    if not body.strip():
        raise FileReadError(400, "invalid_request", kind="empty_body")
    abs_dir, stage = _resolve_stage_dir(stage_path, repo_root)
    target = abs_dir / PROMOTED_FILENAME
    existing = parse_promoted_text(target.read_text(encoding="utf-8", errors="replace")) if target.is_file() else ()
    pin_id = _next_pin_id(existing)
    new_pin = Pin(pin_id=pin_id, location=location.strip(), body=body.rstrip())
    new_text = render_promoted_text(stage, existing + (new_pin,))

    rel_target = f"{stage_path.rstrip('/')}/" + PROMOTED_FILENAME
    tree = ExposedTree(repo_root)
    if not tree.is_inside(target):
        raise FileReadError(404, "not_found", kind="outside_exposed_tree")
    write_file(rel_target, new_text, repo_root)
    return new_pin


def remove_promotion(stage_path: str, pin_id: str, repo_root: Path) -> None:
    abs_dir, stage = _resolve_stage_dir(stage_path, repo_root)
    target = abs_dir / PROMOTED_FILENAME
    if not target.is_file():
        raise FileReadError(404, "not_found", kind="pin_not_found")
    existing = parse_promoted_text(target.read_text(encoding="utf-8", errors="replace"))
    remaining = tuple(p for p in existing if p.pin_id != pin_id)
    if len(remaining) == len(existing):
        raise FileReadError(404, "not_found", kind="pin_not_found")

    rel_target = f"{stage_path.rstrip('/')}/" + PROMOTED_FILENAME
    if remaining:
        new_text = render_promoted_text(stage, remaining)
        write_file(rel_target, new_text, repo_root)
    else:
        try:
            target.unlink()
        except FileNotFoundError:
            pass
