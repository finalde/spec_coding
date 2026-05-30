"""Simplify verbose `· 念法 (...)` voice-direction sub-bullets in shot prompts.

Per follow-up 2026-05-25: "盡量要簡短" — the original 念法 lines contained
per-字 micro-direction (e.g. `"奉天"二字起势重音 + 略拖音`) that bloats the
prompt without giving the AI model genuinely actionable signal. Kling /
Seedance / Sora derive the voice modulation from the scene context + key
voice descriptors; they ignore per-字 timing direction.

New format: each `· 念法 (...)` line is replaced with a 3-bullet block:

    · 念法:
      - 不要照抄 reference sample 的语气, 按本行重渲染
      - 场景: <one-line scene/beat description from the shot's H1 title>
      - 关键声音: <bolded voice descriptors from the original 念法 line>

Idempotent: re-running is a no-op if the line already matches the new format.

Usage:
    python tools/simplify_voice_direction.py --all
    python tools/simplify_voice_direction.py <drama_slug>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AI_VIDEOS = REPO_ROOT / "ai_videos"

# Match the legacy 念法 line (single line, may have leading indent of any size).
# Group 1: leading whitespace (preserved for indent).
# Group 2: the rest of the line after `· 念法 (...): `.
_LEGACY_LINE_RE = re.compile(
    r"^(\s+)·\s+念法\s*\([^)]*\)\s*[:：]\s*(.+)$",
    re.MULTILINE,
)

# Match the new (post-transform) head line so the script is idempotent.
_NEW_HEAD_RE = re.compile(r"^\s+·\s+念法\s*[:：]\s*$", re.MULTILINE)

# Pull bolded spans (`**...**`) out of the original content — these are the
# canonical voice-quality descriptors we want to keep.
_BOLD_RE = re.compile(r"\*\*([^*]+?)\*\*")

# H1 title pattern: `# ep01 / shotNN · <scene/beat description>`.
_H1_RE = re.compile(r"^#\s+ep\d+\s*/\s*shot\d+\s*·\s*(.+?)\s*$", re.MULTILINE)


def extract_scene_context(text: str) -> str:
    m = _H1_RE.search(text)
    return m.group(1).strip() if m else "见上方 Shot context 描述"


def extract_voice_descriptor(legacy_content: str) -> str:
    """Pull bolded spans out, join with ` / `; fall back to first 60 chars
    when no bold spans exist (rare)."""
    spans = _BOLD_RE.findall(legacy_content)
    if spans:
        # De-duplicate while preserving order.
        seen: list[str] = []
        for s in spans:
            s = s.strip()
            if s and s not in seen:
                seen.append(s)
        return " / ".join(seen)
    # No bold spans — use up to the first `;` so we drop most micro-direction.
    snippet = legacy_content.split(";")[0].strip()
    return snippet[:120] if snippet else "(未指定关键声音特征 — 请人工填写)"


def build_new_block(indent: str, scene: str, descriptor: str) -> str:
    sub_indent = indent + "  "
    return (
        f"{indent}· 念法:\n"
        f"{sub_indent}- 不要照抄 reference sample 的语气, 按本行重渲染\n"
        f"{sub_indent}- 场景: {scene}\n"
        f"{sub_indent}- 关键声音: {descriptor}"
    )


def transform_file(path: Path) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    if not _LEGACY_LINE_RE.search(text):
        return False, "no 念法 lines"
    scene = extract_scene_context(text)
    transformed_count = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal transformed_count
        indent = m.group(1)
        legacy_content = m.group(2)
        descriptor = extract_voice_descriptor(legacy_content)
        transformed_count += 1
        return build_new_block(indent, scene, descriptor)

    new_text = _LEGACY_LINE_RE.sub(repl, text)
    if new_text == text:
        return False, "no change (no legacy lines matched)"
    path.write_text(new_text, encoding="utf-8", newline="\n")
    return True, f"transformed {transformed_count} 念法 line(s)"


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
