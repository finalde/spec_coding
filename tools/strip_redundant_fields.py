"""Strip redundant `场景视角锚:` and `角色:` fields from shot prompt code blocks.

Per follow-up 2026-05-27: both fields duplicate information already carried
by the reference-line header at the top of every shot prompt code block
(added 2026-05-24 per rule 12.4-F — `<char>請參考: <drama>_<char>` and
`<scene>:<drama>_<scene>` lines). The body-level `角色:` / `场景视角锚:`
entries are now废话 — strip them.

A stripped block is:
  - Head line matching `^场景视角锚` or `^角色\b` (followed by `:`/`：` or
    a parenthetical like `(2 一句话锁定 ...): ` — both shapes accepted), AND
  - Any consecutive continuation lines that:
      - start with indentation (≥ 2 spaces — the multi-line form's child rows), OR
      - start with `不要` / `严禁` continuation markers, OR
      - lack a field-label `:` early in the line.

Terminator:
  - Blank line
  - Closing ``` fence
  - A new field-label line (e.g. `镜头:`, `场景:`, `动作:`, `光线/色调:`,
    `节奏:`, `渲染样式:`, `比例:`, `时长:`, `台词 / 字幕:`, `音频:`,
    `运镜:`)

Idempotent: re-running is a no-op if no such field is present.

Usage:
    python tools/strip_redundant_fields.py --all
    python tools/strip_redundant_fields.py <drama_slug>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AI_VIDEOS = REPO_ROOT / "ai_videos"

# Match the start of a strippable field. Accepts:
#   `场景视角锚:` / `场景视角锚 (...):`
#   `角色:` / `角色 (N 一句话锁定 ...):`
_HEAD_RE = re.compile(
    r"^(场景视角锚|角色)(?:\s*[(（][^)）]*[)）])?\s*[:：]",
)

# A real field-label line that should TERMINATE the strip. Short label
# (≤ 20 chars) followed by `:` or `：` and not itself starting with one
# of the stripped heads.
_FIELD_LABEL_RE = re.compile(
    r"^([一-鿿A-Za-z_/ ]{1,20})\s*[:：]",
)
_STRIPPED_HEADS = {"场景视角锚", "角色"}

_CODE_BLOCK_RE = re.compile(r"(```text\n)([\s\S]*?)(```)")


def _is_continuation(line: str) -> bool:
    """Continuation lines in a multi-line 角色 block typically start with
    indent (2+ spaces). 场景视角锚 bodies are usually single-line, so
    continuation handling is mostly for 角色 (...) form."""
    if not line:
        return False
    if line.startswith("  ") or line.startswith("\t"):
        return True
    # `不要 ...` / `严禁 ...` are negative-list continuations that should
    # also be swallowed.
    stripped = line.lstrip()
    if stripped.startswith("不要") or stripped.startswith("严禁"):
        return True
    return False


def strip_fields_from_code_body(body: str) -> tuple[str, int]:
    lines = body.split("\n")
    out: list[str] = []
    removed = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        m = _HEAD_RE.match(line)
        if m and m.group(1) in _STRIPPED_HEADS:
            # Pop trailing blank line so we don't leave a double blank.
            while out and out[-1].strip() == "":
                out.pop()
            removed += 1
            i += 1
            # Consume continuations.
            while i < len(lines):
                cont = lines[i]
                stripped = cont.strip()
                if not stripped:
                    break
                # Terminator: a NEW field-label line whose label is not one
                # of the stripped heads.
                fl = _FIELD_LABEL_RE.match(cont.lstrip())
                if fl and fl.group(1) not in _STRIPPED_HEADS and not cont.startswith("  ") and not cont.startswith("\t"):
                    break
                # Otherwise treat as continuation.
                if _is_continuation(cont) or fl is None:
                    removed += 1
                    i += 1
                    continue
                break
            continue
        out.append(line)
        i += 1
    return "\n".join(out), removed


def transform_file(path: Path) -> tuple[bool, str]:
    original = path.read_text(encoding="utf-8")
    total_removed = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal total_removed
        body = m.group(2)
        new_body, removed = strip_fields_from_code_body(body)
        total_removed += removed
        return m.group(1) + new_body + m.group(3)

    new_text = _CODE_BLOCK_RE.sub(repl, original)
    if total_removed == 0 or new_text == original:
        return False, "no strippable fields"
    path.write_text(new_text, encoding="utf-8", newline="\n")
    return True, f"removed {total_removed} line(s) across 场景视角锚 / 角色 blocks"


def run_drama(drama_dir: Path) -> tuple[int, int]:
    files = sorted(drama_dir.glob("episodes/*/shots/*/*.md"))
    if not files:
        return 0, 0
    print(f"\n=== {drama_dir.name} ({len(files)} shot files) ===")
    changed = 0
    for f in files:
        rel = f.relative_to(drama_dir).as_posix()
        try:
            did, msg = transform_file(f)
        except Exception as exc:
            print(f"  ! {rel}  ERROR: {exc}")
            continue
        if did:
            print(f"  * {rel}  — {msg}")
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
    total = changed = 0
    for d in targets:
        n, c = run_drama(d)
        total += n
        changed += c
    print(f"\nTotal: {changed} files changed / {total} files scanned")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
