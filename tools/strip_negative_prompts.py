"""Strip the `负向:` field (single- or multi-line) from every prompt code block.

Per follow-up 2026-05-25: "所有的提示詞，都不需要加負向".

Scope: removes the `负向:` block from inside ```text``` fenced code blocks in:
  - ai_videos/*/characters/c*/c*.md       (character turntable prompts)
  - ai_videos/*/episodes/*/shots/*/*.md   (shot prompts)
  - ai_videos/*/scenes/s*/s*.md           (scene立绘 prompts)

A 负向 block is:
  - One line matching `^负向\s*[:：]` (the head line), AND
  - Any consecutive continuation lines that don't start a new field
    (continuation lines typically open with `不要 ` or end with `/`).

The block terminates at:
  - A blank line, OR
  - A line matching a field-label pattern `^<short_label>\s*[:：]` (where
    label is ≤ 20 chars and not starting with `不要`), OR
  - The closing ``` fence.

Idempotent: re-running is a no-op if no 负向 line is present.

Usage:
    python tools/strip_negative_prompts.py --all
    python tools/strip_negative_prompts.py <drama_slug>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AI_VIDEOS = REPO_ROOT / "ai_videos"

_NEG_HEAD_RE = re.compile(r"^负向\s*[:：]")
_FIELD_LABEL_RE = re.compile(r"^[一-鿿A-Za-z_][一-鿿A-Za-z_ /]{0,18}\s*[:：]")
_CODE_BLOCK_RE = re.compile(r"(```text\n)([\s\S]*?)(```)")


def _is_continuation(line: str) -> bool:
    """A continuation line of a 负向 block.

    These lines typically open with `不要 ` or look like a fragment list
    `X / Y / Z` (often ending with `/`). They never start a new field
    label, but they may contain a `:` somewhere (e.g. `不要 hex 偏色: ...`).
    The discriminator: line is non-empty, does NOT match the field-label
    pattern at line head, and starts with `不要` OR previous line ended
    with `/` (long-wrapped list).
    """
    stripped = line.strip()
    if not stripped:
        return False
    if _FIELD_LABEL_RE.match(stripped) and not stripped.startswith("不要"):
        return False
    return True


def strip_negative_from_code_body(body: str) -> tuple[str, int]:
    """Remove the 负向 block from a code-block body. Return (new_body, lines_removed)."""
    lines = body.split("\n")
    out: list[str] = []
    removed = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if _NEG_HEAD_RE.match(line):
            # Pop trailing blank line we just appended, so we don't leave
            # a double blank when 负向 is removed.
            while out and out[-1].strip() == "":
                out.pop()
            removed += 1
            i += 1
            # Consume continuation lines.
            while i < len(lines):
                cont = lines[i]
                stripped = cont.strip()
                # Empty line terminates.
                if not stripped:
                    break
                # New field-label terminates (unless it starts with 不要).
                if (
                    _FIELD_LABEL_RE.match(stripped)
                    and not stripped.startswith("不要")
                ):
                    break
                # Otherwise this is a continuation.
                removed += 1
                i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out), removed


def transform_file(path: Path) -> tuple[bool, str]:
    original = path.read_text(encoding="utf-8")
    new_text = original
    total_removed = 0
    # Walk every ```text code block (some scene files have a立绘 block + a
    # walk-through block — both may carry 负向).
    def repl(m: re.Match[str]) -> str:
        nonlocal total_removed
        body = m.group(2)
        new_body, removed = strip_negative_from_code_body(body)
        total_removed += removed
        return m.group(1) + new_body + m.group(3)

    new_text = _CODE_BLOCK_RE.sub(repl, original)
    if total_removed == 0 or new_text == original:
        return False, "no 负向 found"
    path.write_text(new_text, encoding="utf-8", newline="\n")
    return True, f"removed {total_removed} 负向 line(s)"


def run_drama(drama_dir: Path) -> tuple[int, int]:
    files: list[Path] = []
    files.extend(sorted(drama_dir.glob("characters/c*/c*.md")))
    files.extend(sorted(drama_dir.glob("episodes/*/shots/*/*.md")))
    files.extend(sorted(drama_dir.glob("scenes/s*/s*.md")))
    if not files:
        return 0, 0
    print(f"\n=== {drama_dir.name} ({len(files)} candidate files) ===")
    changed = 0
    for f in files:
        rel = f.relative_to(drama_dir).as_posix()
        try:
            did, msg = transform_file(f)
        except Exception as exc:
            print(f"  ! {rel}  ERROR: {exc}")
            continue
        marker = "*" if did else " "
        print(f"  {marker} {rel}  — {msg}")
        if did:
            changed += 1
    return len(files), changed


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        return 2
    if argv[0] == "--all":
        targets = [
            p for p in sorted(AI_VIDEOS.iterdir())
            if p.is_dir() and not p.name.startswith("_")
        ]
    else:
        d = AI_VIDEOS / argv[0]
        if not d.is_dir():
            print(f"ERROR: drama folder not found: {d}", file=sys.stderr)
            return 1
        targets = [d]

    total = 0
    changed = 0
    for d in targets:
        n, c = run_drama(d)
        total += n
        changed += c
    print(f"\nTotal: {changed} changed / {total} files")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
