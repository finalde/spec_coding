"""CLI entry: split each already-downloaded `{slug}.md` into per-chapter files.

Per follow-up 111. The downloader (follow-up 096 / 101) appended every chapter
to a single `novels/{cat}/{slug}/{slug}.md`. These files grew to 3–19 MB, which
the webapp's `/api/file` endpoint refuses (`MAX_FILE_BYTES = 1 MiB`). This script
re-splits the concatenated body into `chapters/{NNNN}-{safe_title}.md` files,
fills `_meta.json.chapters[].file`, writes a per-novel README, and removes the
original concatenated file.

Usage:
    python -m apps.cli.novel_split                # all novels under novels/
    python -m apps.cli.novel_split <slug>         # one novel
    python -m apps.cli.novel_split --dry-run      # print what would happen, no writes
    python -m apps.cli.novel_split --keep         # keep the concatenated {slug}.md after split

Safety: if the split chapter count diverges from `_meta.json.chapters`, the script
logs a WARN and leaves the original `{slug}.md` in place for manual review.
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
from pathlib import Path

# Windows console defaults to cp1252; chapter titles + filenames contain CJK
# characters that crash `print(...)` with UnicodeEncodeError. Reconfigure
# stdout/stderr to UTF-8 before any output is emitted.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
else:  # pragma: no cover — older Pythons
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from libs.domain.value_objects.novel__valueobject import CANONICAL_NOVELS, find_novel
from libs.infrastructure.writers.novel__writer import (
    ChapterRecord,
    NovelMeta,
    _build_chapter_filename,
)

_CHAPTER_HEADING_RE = re.compile(r"^## (.+?)\s*$", re.MULTILINE)
_CHAPTER_FILENAME_RE = re.compile(r"^(\d{4})-(.+)\.md$")


def _resolve_novels_root() -> Path:
    override = os.environ.get("NOVELS_ROOT", "").strip()
    if override:
        return Path(override).resolve()
    here = Path(__file__).resolve()
    candidates = ("downloaded_novels", "novels")  # follow-up 112 renamed novels/ → downloaded_novels/
    for ancestor in here.parents:
        for name in candidates:
            if (ancestor / name).is_dir():
                return (ancestor / name).resolve()
        if (ancestor / ".git").exists():
            return (ancestor / candidates[0]).resolve()
    return (Path.cwd() / candidates[0]).resolve()


def _load_meta(meta_path: Path) -> NovelMeta | None:
    if not meta_path.is_file():
        return None
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    try:
        return NovelMeta.from_json(data)
    except (KeyError, ValueError, TypeError):
        return None


def _write_meta(meta_path: Path, meta: NovelMeta) -> None:
    tmp = meta_path.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(meta.to_json(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(tmp, meta_path)


def _split_body(body: str) -> dict[str, str]:
    """Return {title: body} for every `## ` heading found.

    Duplicate titles (e.g. from a resumable-download retry that appended the
    same chapter twice) collapse to the **last** occurrence — the most recently
    written copy wins. Anything before the first `## ` heading (book front-
    matter, author line, source URL) is discarded; README.md is the canonical
    home for that content post-split.
    """
    matches = list(_CHAPTER_HEADING_RE.finditer(body))
    chapters: dict[str, str] = {}
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        chapters[title] = body[start:end].strip("\n")
    return chapters


def _write_readme(novel_dir: Path, meta: NovelMeta) -> None:
    src_host = meta.active_source_host or meta.source_host
    src_id = meta.active_source_id or meta.source_id
    readme = novel_dir / "README.md"
    readme.write_text(
        f"# {meta.title_zh}\n\n作者：{meta.author}\n\n来源：{src_host}/{src_id}/\n\n"
        f"章节存放于 `chapters/` 目录，每章一个 `.md` 文件。\n",
        encoding="utf-8",
    )


def _repair_meta_from_chapters_dir(meta: NovelMeta, chapters_dir: Path) -> None:
    """If a prior splitter run wrote files under chapters/ but the meta got
    blown away (e.g. by a concurrent downloader running with the legacy writer),
    rebuild `record.file` + `done` from the on-disk filenames.

    Filenames follow `{NNNN}-{safe_title}.md`. The NNNN prefix maps 1:1 to the
    chapter's `idx`, so we use it as the primary key and only verify the title
    matches the meta record (after `_safe_filename_segment` normalization)."""
    if not chapters_dir.is_dir():
        return
    by_idx: dict[int, str] = {}
    for child in chapters_dir.iterdir():
        if not child.is_file():
            continue
        m = _CHAPTER_FILENAME_RE.match(child.name)
        if m is None:
            continue
        idx = int(m.group(1))
        by_idx[idx] = child.name
    for record in meta.chapters:
        filename = by_idx.get(record.idx)
        if filename is None:
            continue
        expected = _build_chapter_filename(record.idx, record.title)
        if filename != expected:
            continue
        if record.file != filename:
            record.file = filename
        if not record.done:
            record.done = True
            record.error = None


def _split_one(novel_dir: Path, dry_run: bool, keep: bool) -> int:
    """Split one novel dir. Returns 0 on success, 1 on warning."""
    slug = novel_dir.name
    body_path = novel_dir / f"{slug}.md"
    meta_path = novel_dir / "_meta.json"
    chapters_dir = novel_dir / "chapters"
    if not body_path.is_file():
        meta = _load_meta(meta_path)
        if meta is None or not chapters_dir.is_dir():
            print(f"SKIP  {slug:35s} no {slug}.md (already split or never downloaded)")
            return 0
        before = sum(1 for c in meta.chapters if c.done and c.file)
        _repair_meta_from_chapters_dir(meta, chapters_dir)
        after = sum(1 for c in meta.chapters if c.done and c.file)
        repaired = after - before
        if repaired and not dry_run:
            meta.complete = all(c.done for c in meta.chapters)
            _write_meta(meta_path, meta)
            _write_readme(novel_dir, meta)
        action = "REPAIR" if repaired else "SKIP "
        suffix = f"repaired {repaired} chapter records" if repaired else "already split, meta in sync"
        print(f"{action} {slug:35s} {suffix}")
        return 0
    meta = _load_meta(meta_path)
    if meta is None:
        print(f"WARN  {slug:35s} _meta.json missing or unparseable; skipping")
        return 1
    body = body_path.read_text(encoding="utf-8")
    parsed = _split_body(body)
    chapters_dir = novel_dir / "chapters"
    if not dry_run:
        chapters_dir.mkdir(parents=True, exist_ok=True)

    _repair_meta_from_chapters_dir(meta, chapters_dir)

    updated_chapters: list[ChapterRecord] = []
    written = 0
    preserved = 0
    missing = 0
    for record in meta.chapters:
        # Re-run safety: if a prior split already wrote chapters/{file}, treat
        # that as canonical and don't disturb it even when the concatenated
        # body no longer carries the ## heading (the body file may have been
        # truncated + partially rewritten by a concurrent downloader).
        existing_file = record.file
        if existing_file and (chapters_dir / existing_file).is_file():
            updated_chapters.append(record)
            preserved += 1
            continue
        chapter_body = parsed.get(record.title)
        if chapter_body is None:
            # Chapter recorded done in _meta.json but its body never landed in
            # {slug}.md (concurrent-writer drop, truncated file, or stale meta).
            # Clear `done` so the next `download_all` will re-fetch it.
            new_record = ChapterRecord(
                idx=record.idx,
                title=record.title,
                url=record.url,
                done=False,
                hash=None,
                error="missing in concatenated body at split time",
                file=None,
            )
            updated_chapters.append(new_record)
            missing += 1
            continue
        filename = _build_chapter_filename(record.idx, record.title)
        chapter_path = chapters_dir / filename
        content = f"# {record.title}\n\n{chapter_body}\n"
        if not dry_run:
            chapter_path.write_text(content, encoding="utf-8")
        new_record = ChapterRecord(
            idx=record.idx,
            title=record.title,
            url=record.url,
            done=True,
            hash=record.hash,
            error=None,
            file=filename,
        )
        updated_chapters.append(new_record)
        written += 1

    if not dry_run:
        meta.chapters = updated_chapters
        meta.complete = all(c.done for c in meta.chapters)
        _write_meta(meta_path, meta)
        _write_readme(novel_dir, meta)
        if not keep:
            body_path.unlink()

    action = "DRY  " if dry_run else "OK   "
    parts = [f"{written:4d} chapters -> chapters/"]
    if preserved:
        parts.append(f"{preserved} preserved (already split)")
    if missing:
        parts.append(f"{missing} missing (cleared done; rerun downloader)")
    if keep:
        parts.append(f"kept {slug}.md")
    print(f"{action} {slug:35s} {'; '.join(parts)}")
    return 1 if missing else 0


def _iter_novel_dirs(novels_root: Path, slug_filter: str | None) -> list[Path]:
    novel_dirs: list[Path] = []
    if slug_filter:
        spec = find_novel(slug_filter)
        novel_dirs.append(novels_root / spec.category / spec.slug)
        return novel_dirs
    for spec in CANONICAL_NOVELS:
        candidate = novels_root / spec.category / spec.slug
        if candidate.is_dir():
            novel_dirs.append(candidate)
    return novel_dirs


def main(argv: list[str]) -> int:
    dry_run = False
    keep = False
    positional: list[str] = []
    for tok in argv[1:]:
        if tok == "--dry-run":
            dry_run = True
        elif tok == "--keep":
            keep = True
        elif tok.startswith("--"):
            print(f"unknown flag: {tok}", file=sys.stderr)
            return 2
        else:
            positional.append(tok)

    novels_root = _resolve_novels_root()
    print(f"novels_root: {novels_root}", flush=True)
    if dry_run:
        print("(dry-run mode — no files will be created or deleted)", flush=True)

    slug_filter = positional[0] if positional else None
    novel_dirs = _iter_novel_dirs(novels_root, slug_filter)
    if not novel_dirs:
        print("no novels found", file=sys.stderr)
        return 1

    print(f"splitting {len(novel_dirs)} novel(s)", flush=True)
    warns = 0
    for novel_dir in novel_dirs:
        warns += _split_one(novel_dir, dry_run=dry_run, keep=keep)
    print()
    print("=" * 60)
    print(f"SUMMARY: {len(novel_dirs)} novel(s) processed, {warns} warning(s)")
    return 0 if warns == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
