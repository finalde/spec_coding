"""CLI entry: download every canonical novel into downloaded_novels/{category}/{slug}/.

Resumable — re-running picks up where it left off via
downloaded_novels/{category}/{slug}/_meta.json.
Repo root is detected by walking parents until `downloaded_novels/` or the repo
marker is found, or overridden via NOVELS_ROOT env var (kept under the old name
for backwards-compatibility; the value points at downloaded_novels/).

Per follow-up 113 the surface formerly known as `novels/` was renamed to
`downloaded_novels/`, sibling to the new `my_novel/` surface for original
manuscripts.

Usage:
    python -m apps.cli.novel_download                       # download all, 1 worker (serial, polite)
    python -m apps.cli.novel_download --workers 3           # opt into parallel (higher rate-limit risk)
    python -m apps.cli.novel_download <slug>                # one novel (single-threaded)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from libs.application.commands.novel__command import NovelCommand
from libs.infrastructure.writers.novel__writer import NovelDownloader


def _resolve_novels_root() -> Path:
    override = os.environ.get("NOVELS_ROOT", "").strip()
    if override:
        return Path(override).resolve()
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        if (ancestor / "downloaded_novels").is_dir():
            return (ancestor / "downloaded_novels").resolve()
        if (ancestor / ".git").exists():
            return (ancestor / "downloaded_novels").resolve()
    return (Path.cwd() / "downloaded_novels").resolve()


def _on_progress(slug: str, idx: int, total: int) -> None:
    print(f"  [{slug}] {idx}/{total}", flush=True)


def main(argv: list[str]) -> int:
    novels_root = _resolve_novels_root()
    novels_root.mkdir(parents=True, exist_ok=True)
    print(f"downloaded_novels_root: {novels_root}", flush=True)

    # Default reverted to 1 (serial) per follow-up 106: 5 workers tripped sudugu.org's
    # anti-bot in follow-up 105 and got the IP 302-redirected to google.com. Use
    # --workers N to opt back into parallel once the block clears.
    workers = 1
    positional: list[str] = []
    it = iter(argv[1:])
    for tok in it:
        if tok == "--workers":
            workers = int(next(it, "5"))
        elif tok.startswith("--workers="):
            workers = int(tok.split("=", 1)[1])
        else:
            positional.append(tok)

    with NovelDownloader(novels_root=novels_root) as downloader:
        command = NovelCommand(downloader)
        if positional:
            slug = positional[0]
            print(f"downloading single novel: {slug}", flush=True)
            result = downloader.download(slug, on_progress=_on_progress)
            print(
                f"DONE {result.slug}: {result.chapters_done}/{result.chapters_total} "
                f"complete={result.complete} errors={len(result.errors)}",
                flush=True,
            )
            return 0 if result.complete else 1
        print(f"downloading all canonical novels (parallel, workers={workers})", flush=True)
        results = downloader.download_all(on_progress=_on_progress, max_workers=workers)
        print()
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        any_incomplete = False
        for r in results:
            tag = "COMPLETE" if r.complete else "PARTIAL "
            print(f"{tag} {r.slug:30s} {r.chapters_done:4d}/{r.chapters_total:4d}  ({r.title_zh})")
            if not r.complete:
                any_incomplete = True
                for err in r.errors[:3]:
                    print(f"    err: {err}")
                if len(r.errors) > 3:
                    print(f"    ... +{len(r.errors) - 3} more")
        return 1 if any_incomplete else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
