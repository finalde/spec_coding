"""Inject / refresh the `角色造型` block in every character prompt.

Per agent_refs/project/ai_video.md rule 12.5-A v3 (2026-05-25): EVERY
character `c{N}_{中文名}/c{N}_{中文名}.md` must carry a `角色造型` block in
its first turntable prompt code block, with the `- 发型 ...` row bearing an
explicit inline annotation forbidding the model from copying the actor
reference photo's hairstyle.

This script:
  - Walks `ai_videos/{drama}/characters/c*/c*.md`.
  - Parses 锁定描述符 rows by label (发型, 服装, 道具, 气质) — robust to drama
    variations in row numbering and surrounding markdown bold/italic.
  - Finds the first `text` code block; inside it, locates the FIRST line
    starting with `主体:` or `角色:` and inserts the 5-line `角色造型` block
    right after.
  - Idempotent: if a `角色造型` block is already present (anywhere in the
    code block), it is replaced rather than duplicated.

Usage:
    python tools/inject_character_styling_block.py <drama_slug>
    python tools/inject_character_styling_block.py --all
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AI_VIDEOS = REPO_ROOT / "ai_videos"

# Match a `| ... | 发型 ... | <value> |` row, robust to bold/italic on the
# label cell and to trailing parens like "（6 子项）".
_DESC_ROW_RE = re.compile(
    r"^\|\s*(?:[*\d]+)\s*\|\s*\**\s*([^|]+?)\s*\**\s*\|\s*([^|]+?)\s*\|\s*$",
    re.MULTILINE,
)

_CODE_BLOCK_RE = re.compile(r"```text\n([\s\S]*?)```", re.MULTILINE)
_BODY_ANCHOR_RE = re.compile(r"^(主体|角色)\s*:\s*.+$", re.MULTILINE)
_EXISTING_STYLING_BLOCK_RE = re.compile(
    r"^角色造型 \(覆盖演员照片[\s\S]*?(?=^\S|\Z)",
    re.MULTILINE,
)

# v1 boilerplate — if found, removed before reinjection.
_V1_BOILERPLATE_RE = re.compile(r"^演员参考照片解读契约:[^\n]*\n?", re.MULTILINE)

# v2 styling block without the v3 发型 annotation — removed before reinjection.
_LEGACY_V2_STYLING_RE = re.compile(
    r"^角色造型 \(覆盖演员照片[^\n]*\n(?:- [^\n]+\n)+",
    re.MULTILINE,
)


def parse_lock_rows(content: str) -> dict[str, str]:
    """Return {normalized_label: value} from the 锁定描述符 table.

    Looks at all `| ... | <label> | <value> |` rows. The first match for a
    label wins (so multi-state files like 裴知秋 use the first state's values
    for injection — author can manually adjust afterwards if state B should
    differ).
    """
    out: dict[str, str] = {}
    for m in _DESC_ROW_RE.finditer(content):
        label_raw = m.group(1).strip().strip("*").strip()
        value = m.group(2).strip()
        for key in ("发型", "服装", "道具", "气质"):
            if key in label_raw and key not in out:
                out[key] = value
                break
    return out


_STYLING_HEADER = "角色造型 (覆盖演员照片日常素颜 + 现成短假发 — 模型禁止 carry T-shirt / 现代发型 / 演员素颜 入画):"
_FAXING_ANNOTATION = "(**以本 prompt 为准, 严禁照抄演员参考照片的实际发型 / 假发 / 现代发型**)"


def build_styling_block(rows: dict[str, str]) -> str:
    faxing = rows.get("发型", "(未在锁定描述符中找到 发型 / 发色 字段 — 请人工填写)")
    fuzhuang = rows.get("服装", "(未在锁定描述符中找到 服装 / 主色 字段 — 请人工填写)")
    daoju = rows.get("道具", "无标志道具")
    qizhi = rows.get("气质", "(未在锁定描述符中找到 气质 字段 — 请人工填写)")
    return (
        f"{_STYLING_HEADER}\n"
        f"- 发型 {_FAXING_ANNOTATION}: {faxing}\n"
        f"- 服装: {fuzhuang}\n"
        f"- 道具: {daoju}\n"
        f"- 神情 / 气质: {qizhi}"
    )


def transform_character_file(path: Path) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    rows = parse_lock_rows(text)
    if "发型" not in rows:
        return False, "skip — no 发型 row found in 锁定描述符 table"

    cb_match = _CODE_BLOCK_RE.search(text)
    if cb_match is None:
        return False, "skip — no ```text code block"
    body = cb_match.group(1)
    body_start = cb_match.start(1)
    body_end = cb_match.end(1)

    anchor = _BODY_ANCHOR_RE.search(body)
    if anchor is None:
        return False, "skip — no `主体:` or `角色:` anchor line inside code block"
    anchor_end = body_start + anchor.end()
    anchor_label = anchor.group(1)  # 主体 or 角色

    # Strip any pre-existing v1 boilerplate / v2 styling block from inside
    # the code block before injection.
    new_body = body
    new_body = _V1_BOILERPLATE_RE.sub("", new_body)
    new_body = _LEGACY_V2_STYLING_RE.sub("", new_body)
    # Recompute anchor end against the cleaned body.
    cleaned_anchor = _BODY_ANCHOR_RE.search(new_body)
    if cleaned_anchor is None:
        return False, "skip — anchor disappeared after cleanup (unexpected)"
    cleaned_anchor_end = cleaned_anchor.end()

    styling = build_styling_block(rows)
    # Ensure a blank line separates anchor and styling, and styling and rest.
    injection = "\n\n" + styling + "\n"
    # Drop any leading blank lines after the anchor so the spacing is exactly
    # `<anchor>\n\n<styling>\n\n<rest>`.
    rest = new_body[cleaned_anchor_end:].lstrip("\n")
    composed_body = new_body[:cleaned_anchor_end] + injection + "\n" + rest

    new_text = text[:body_start] + composed_body + text[body_end:]
    if new_text == text:
        return False, "no change (already canonical)"
    path.write_text(new_text, encoding="utf-8", newline="\n")
    return True, f"injected/refreshed 角色造型 block (anchor `{anchor_label}:`)"


def run_drama(drama_dir: Path) -> tuple[int, int, int]:
    files = sorted(drama_dir.glob("characters/c*/c*.md"))
    if not files:
        return 0, 0, 0
    print(f"\n=== {drama_dir.name} ({len(files)} files) ===")
    changed = 0
    skipped = 0
    for f in files:
        rel = f.relative_to(drama_dir).as_posix()
        try:
            did, msg = transform_character_file(f)
        except Exception as exc:
            print(f"  ! {rel}  ERROR: {exc}")
            skipped += 1
            continue
        marker = "*" if did else " "
        print(f"  {marker} {rel}  — {msg}")
        if did:
            changed += 1
        else:
            skipped += 1
    return len(files), changed, skipped


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        return 2
    targets: list[Path] = []
    if argv[0] == "--all":
        targets = [
            p for p in sorted(AI_VIDEOS.iterdir())
            if p.is_dir() and not p.name.startswith("_")
            and (p / "characters").is_dir()
        ]
    else:
        d = AI_VIDEOS / argv[0]
        if not d.is_dir():
            print(f"ERROR: drama folder not found: {d}", file=sys.stderr)
            return 1
        targets = [d]

    total = total_changed = total_skipped = 0
    for d in targets:
        n, c, s = run_drama(d)
        total += n
        total_changed += c
        total_skipped += s

    print(f"\nTotal: {total_changed} changed / {total_skipped} skipped / {total} files")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
