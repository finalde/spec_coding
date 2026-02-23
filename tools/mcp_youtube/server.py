#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Any, Optional

from fastmcp import FastMCP


mcp = FastMCP("youtube")


@dataclass(frozen=True)
class YtDlpResult:
    stdout: str
    stderr: str
    returncode: int


def _run_yt_dlp(args: list[str]) -> YtDlpResult:
    proc = subprocess.run(
        args,
        text=True,
        capture_output=True,
        check=False,
    )
    return YtDlpResult(stdout=proc.stdout, stderr=proc.stderr, returncode=proc.returncode)


def _ensure_http_url(maybe_id_or_url: Optional[str]) -> Optional[str]:
    if not maybe_id_or_url:
        return None
    if maybe_id_or_url.startswith("http://") or maybe_id_or_url.startswith("https://"):
        return maybe_id_or_url
    # yt-dlp flat playlist entries often store "url" as the video id.
    return f"https://www.youtube.com/watch?v={maybe_id_or_url}"


@mcp.tool
def list_channel_videos(channel_url: str, limit: int = 30) -> list[dict[str, Any]]:
    """
    List recent videos from a YouTube channel or playlist URL using public metadata.

    Returns flat entries (best-effort): id, title, url, uploader, channel, duration, view_count, upload_date.
    Some fields may be missing depending on YouTube/yt-dlp availability.
    """
    capped = max(1, min(int(limit), 100))
    result = _run_yt_dlp(
        [
            "yt-dlp",
            "--flat-playlist",
            "-J",
            "--playlist-end",
            str(capped),
            channel_url,
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed (exit {result.returncode}): {result.stderr.strip()}")

    payload = json.loads(result.stdout)
    entries = payload.get("entries") or []

    out: list[dict[str, Any]] = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        out.append(
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "url": _ensure_http_url(e.get("url") or e.get("id")),
                "uploader": e.get("uploader"),
                "channel": e.get("channel") or e.get("uploader"),
                "duration": e.get("duration"),
                "view_count": e.get("view_count"),
                "upload_date": e.get("upload_date"),
            }
        )
    return out


@mcp.tool
def get_video_details(video_url: str) -> dict[str, Any]:
    """
    Fetch richer metadata for a single YouTube video URL via yt-dlp -J.

    Returns a trimmed dict with commonly useful fields for analysis.
    """
    result = _run_yt_dlp(["yt-dlp", "-J", video_url])
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed (exit {result.returncode}): {result.stderr.strip()}")

    data = json.loads(result.stdout)
    return {
        "id": data.get("id"),
        "title": data.get("title"),
        "webpage_url": data.get("webpage_url") or video_url,
        "channel": data.get("channel") or data.get("uploader"),
        "uploader": data.get("uploader"),
        "upload_date": data.get("upload_date"),
        "duration": data.get("duration"),
        "view_count": data.get("view_count"),
        "like_count": data.get("like_count"),
        "tags": data.get("tags"),
        "categories": data.get("categories"),
        "description": data.get("description"),
    }


if __name__ == "__main__":
    mcp.run()

