"""CLI entry: download every canonical novel into novels/{slug}/.

Resumable — re-running picks up where it left off via novels/{slug}/_meta.json.
Repo root is detected by walking parents until 'novels/' or the repo marker is found,
or overridden via NOVELS_ROOT env var.

Usage:
    python -m apps.cli.novel_download              # download all
    python -m apps.cli.novel_download <slug>       # one novel
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
        if (ancestor / "novels").is_dir():
            return (ancestor / "novels").resolve()
        if (ancestor / ".git").exists():
            return (ancestor / "novels").resolve()
    return (Path.cwd() / "novels").resolve()


def _on_progress(slug: str, idx: int, total: int) -> None:
    print(f"  [{slug}] {idx}/{total}", flush=True)


def main(argv: list[str]) -> int:
    novels_root = _resolve_novels_root()
    novels_root.mkdir(parents=True, exist_ok=True)
    print(f"novels_root: {novels_root}", flush=True)

    with NovelDownloader(novels_root=novels_root) as downloader:
        command = NovelCommand(downloader)
        if len(argv) >= 2:
            slug = argv[1]
            print(f"downloading single novel: {slug}", flush=True)
            result = downloader.download(slug, on_progress=_on_progress)
            print(
                f"DONE {result.slug}: {result.chapters_done}/{result.chapters_total} "
                f"complete={result.complete} errors={len(result.errors)}",
                flush=True,
            )
            return 0 if result.complete else 1
        print("downloading all canonical novels", flush=True)
        results = downloader.download_all(on_progress=_on_progress)
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
