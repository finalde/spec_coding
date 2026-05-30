"""Prepend character/scene reference lines to every shot prompt code block.

Per user follow-up 2026-05-24: each shot's video-prompt code block must open
with reference lines that point the AI model at the per-character / per-scene
visual reference handles (drama_chinese_name + character_name).

Format:
    <character_zh>請參考：<drama_chinese_name>_<character_zh>
    <scene_zh>:<drama_chinese_name>_<scene_zh>

Also strips any legacy `{ref_xxx}` placeholder lines from the same code block.

Usage:
    python tools/add_shot_reference_lines.py <drama_pinyin_folder>

Example:
    python tools/add_shot_reference_lines.py nvdi_tuihun_houhuile

The script:
  - Walks `ai_videos/<drama>/episodes/*/shots/*/<shotNN>.md`.
  - Parses `- Characters: cN_<name> (...) [+ cN_<name> (...)]` for character list.
  - Parses `- Scene: sN_<name> (...)` for scene.
  - Reads the drama's Chinese name from `ai_videos/<drama>/README.md` H1.
  - Prepends reference lines as the first content inside the ```text ... ```
    code block (after the opening fence, before the existing title line).
  - Strips lines containing `{ref_xxx}` placeholders from the same code block.
  - Idempotent: skips a shot whose code block already starts with the
    canonical reference lines for its characters/scene.

Reports per-shot status; exits non-zero on parse failure.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parents[1]

_CHAR_TOKEN_RE = re.compile(r"c\d+_([^\s()（）+,，]+)")
_SCENE_TOKEN_RE = re.compile(r"s\d+_([^\s()（）+,，]+)")
_CODE_BLOCK_RE = re.compile(r"^```text\s*$", re.MULTILINE)
_CODE_BLOCK_CLOSE_RE = re.compile(r"^```\s*$", re.MULTILINE)
_REF_PLACEHOLDER_RE = re.compile(r"\{ref_[^}]+\}")
_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)

# Pattern that detects "voice-only / off-screen" markers in the parenthetical
# that follows a `cN_<name>` token in the Characters: line. Any of these
# markers (case-insensitive for ASCII) flips the emitted reference line into
# the "(画外 OS, 仅声线无入画)" form.
_OS_MARKER_RE = re.compile(r"画外|OS|V\.?O\.?|voice[\s-]?over", re.IGNORECASE)
_OS_SUFFIX = "(画外 OS, 仅声线无入画)"


class CharRef(NamedTuple):
    name: str          # bare Chinese name (no cN_ prefix)
    is_voice_only: bool


class ShotMeta(NamedTuple):
    characters: list[CharRef]  # bare names + on-screen vs voice-only flag
    scene: str | None          # bare Chinese name, no sN_ prefix


def parse_drama_chinese_name(drama_dir: Path) -> str:
    readme = drama_dir / "README.md"
    if not readme.is_file():
        raise SystemExit(f"missing README.md at {readme}")
    text = readme.read_text(encoding="utf-8")
    m = _H1_RE.search(text)
    if not m:
        raise SystemExit(f"no H1 found in {readme}")
    name = m.group(1).strip()
    # Drop surrounding 《》 if present.
    name = name.strip("《》").strip()
    # Drop the trailing "— ..." suffix some READMEs add.
    if "—" in name:
        name = name.split("—")[0].strip()
    if " " in name:
        name = name.split()[0]
    return name


def _voice_only_for_token(chars_line: str, token_end: int) -> bool:
    """Look at the parenthetical immediately following a `cN_<name>` token
    and return True if it contains an OS / 画外 / V.O. marker."""
    # Find the next parenthetical opening AFTER the token but BEFORE the
    # next `+` (separator between characters in the Characters: line).
    next_plus = chars_line.find("+", token_end)
    region_end = next_plus if next_plus != -1 else len(chars_line)
    region = chars_line[token_end:region_end]
    paren_open = re.search(r"[(（]", region)
    if not paren_open:
        return False
    paren_close = re.search(r"[)）]", region[paren_open.end():])
    if not paren_close:
        return False
    paren_body = region[paren_open.end() : paren_open.end() + paren_close.start()]
    return bool(_OS_MARKER_RE.search(paren_body))


def parse_shot(shot_path: Path) -> ShotMeta:
    text = shot_path.read_text(encoding="utf-8")
    chars_match = re.search(r"^-\s+Characters:\s*(.+)$", text, re.MULTILINE)
    scene_match = re.search(r"^-\s+Scene:\s*(.+)$", text, re.MULTILINE)
    characters: list[CharRef] = []
    seen: set[str] = set()
    if chars_match:
        chars_line = chars_match.group(1)
        for m in _CHAR_TOKEN_RE.finditer(chars_line):
            name = m.group(1)
            if name in seen:
                continue
            seen.add(name)
            voice_only = _voice_only_for_token(chars_line, m.end())
            characters.append(CharRef(name=name, is_voice_only=voice_only))
    scene: str | None = None
    if scene_match:
        m = _SCENE_TOKEN_RE.search(scene_match.group(1))
        if m:
            scene = m.group(1)
    return ShotMeta(characters=characters, scene=scene)


def build_reference_lines(drama_zh: str, meta: ShotMeta) -> list[str]:
    lines: list[str] = []
    for ch in meta.characters:
        if ch.is_voice_only:
            lines.append(f"{ch.name}請參考 {_OS_SUFFIX}：{drama_zh}_{ch.name}")
        else:
            lines.append(f"{ch.name}請參考：{drama_zh}_{ch.name}")
    if meta.scene:
        lines.append(f"{meta.scene}:{drama_zh}_{meta.scene}")
    return lines


def transform_shot_file(
    shot_path: Path, drama_zh: str, meta: ShotMeta
) -> tuple[bool, str]:
    """Return (changed?, status_message).

    Raises SystemExit on malformed shot file (no text code block at all).
    """
    text = shot_path.read_text(encoding="utf-8")
    open_match = _CODE_BLOCK_RE.search(text)
    if not open_match:
        return False, "skip (no ```text code block)"
    open_end = open_match.end()
    close_match = _CODE_BLOCK_CLOSE_RE.search(text, pos=open_end + 1)
    if not close_match:
        raise SystemExit(f"unterminated code block in {shot_path}")
    close_start = close_match.start()

    before = text[: open_end]
    code_body = text[open_end:close_start]
    after = text[close_start:]

    new_ref_lines = build_reference_lines(drama_zh, meta)
    if not new_ref_lines:
        return False, "skip (no characters AND no scene)"
    new_ref_block = "\n".join(new_ref_lines)

    # Strip lines that contain a {ref_xxx} placeholder AND any pre-existing
    # `<name>請參考...` reference lines + the scene reference line (so we can
    # re-insert with potentially updated OS-suffix annotations).
    existing_scene_line = f"{meta.scene}:{drama_zh}_{meta.scene}" if meta.scene else None
    code_lines = code_body.split("\n")
    stripped_lines: list[str] = []
    refs_removed = 0
    for line in code_lines:
        if _REF_PLACEHOLDER_RE.search(line):
            refs_removed += 1
            continue
        if "請參考" in line:
            continue
        if existing_scene_line is not None and line.strip() == existing_scene_line:
            continue
        stripped_lines.append(line)
    stripped_code = "\n".join(stripped_lines)

    # Idempotency: if the code block already starts with these exact ref
    # lines (modulo leading blank lines), no-op.
    canonical_prefix = "\n" + new_ref_block + "\n"
    if stripped_code.startswith(canonical_prefix):
        return False, f"already has refs (stripped {refs_removed} placeholders)" if refs_removed > 0 else "already has refs (no-op)"

    # Prepend the ref block. The code body starts with a leading "\n" after
    # the ```text fence; we want:
    #     ```text
    #     <ref lines>
    #     <blank>
    #     <original content>
    #     ```
    # `stripped_code` already begins with "\n" (the newline after ```text).
    new_code_body = "\n" + new_ref_block + "\n" + stripped_code.lstrip("\n")
    # Ensure exactly one blank line between ref block and the rest:
    new_code_body = re.sub(
        r"^\n" + re.escape(new_ref_block) + r"\n+",
        "\n" + new_ref_block + "\n\n",
        new_code_body,
        count=1,
    )

    new_text = before + new_code_body + after
    shot_path.write_text(new_text, encoding="utf-8", newline="\n")
    parts = [f"prepended {len(new_ref_lines)} ref lines"]
    if refs_removed > 0:
        parts.append(f"stripped {refs_removed} ref_xxx placeholders")
    return True, "; ".join(parts)


def main(drama_slug: str) -> int:
    drama_dir = REPO_ROOT / "ai_videos" / drama_slug
    if not drama_dir.is_dir():
        print(f"ERROR: drama folder not found: {drama_dir}", file=sys.stderr)
        return 1
    drama_zh = parse_drama_chinese_name(drama_dir)
    print(f"Drama: {drama_slug}  ZH: {drama_zh}\n")

    shot_files = sorted(drama_dir.glob("episodes/*/shots/*/*.md"))
    if not shot_files:
        print("No shot files found.")
        return 0

    changed = 0
    skipped = 0
    for sf in shot_files:
        rel = sf.relative_to(drama_dir).as_posix()
        meta = parse_shot(sf)
        if not meta.characters and not meta.scene:
            print(f"  {rel}  SKIP — no characters / scene parsed")
            skipped += 1
            continue
        did_change, status = transform_shot_file(sf, drama_zh, meta)
        marker = "*" if did_change else " "
        print(
            f"{marker} {rel}  chars={meta.characters} scene={meta.scene} — {status}"
        )
        if did_change:
            changed += 1
        else:
            skipped += 1

    print(f"\nChanged: {changed} / Skipped: {skipped} / Total: {len(shot_files)}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
