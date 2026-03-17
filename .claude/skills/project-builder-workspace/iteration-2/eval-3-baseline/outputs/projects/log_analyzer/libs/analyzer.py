"""Core log analysis logic."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


# Common log line pattern:
# 2024-01-15 12:34:56 ERROR [module] message text
_LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})"
    r"(?:\.\d+)?"
    r"\s+(?P<level>DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL|FATAL)"
    r"(?:\s+\[(?P<module>[^\]]+)\])?"
    r"\s+(?P<message>.+)$",
    re.IGNORECASE,
)

_TIMESTAMP_FORMATS: list[str] = [
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
]


@dataclass(frozen=True)
class LogEntry:
    """Represents a single parsed log line."""

    timestamp: datetime | None
    level: str
    module: str | None
    message: str
    raw: str

    @classmethod
    def from_line(cls, line: str) -> "LogEntry | None":
        """Parse a raw log line.  Returns None if the line does not match."""
        stripped = line.strip()
        if not stripped:
            return None
        match = _LOG_PATTERN.match(stripped)
        if match is None:
            return None
        ts: datetime | None = None
        for fmt in _TIMESTAMP_FORMATS:
            try:
                ts = datetime.strptime(match.group("timestamp"), fmt)
                break
            except ValueError:
                continue
        level = match.group("level").upper()
        if level == "WARN":
            level = "WARNING"
        if level == "FATAL":
            level = "CRITICAL"
        return cls(
            timestamp=ts,
            level=level,
            module=match.group("module"),
            message=match.group("message").strip(),
            raw=stripped,
        )


@dataclass
class SummaryReport:
    """Aggregated statistics produced by Analyzer.summarize()."""

    total_lines: int
    parsed_lines: int
    unparsed_lines: int
    level_counts: dict[str, int]
    module_counts: dict[str, int]
    first_timestamp: datetime | None
    last_timestamp: datetime | None
    top_errors: list[str]

    def as_text(self) -> str:
        """Render the report as a human-readable string."""
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("LOG ANALYSIS SUMMARY REPORT")
        lines.append("=" * 60)
        lines.append(f"Total lines      : {self.total_lines}")
        lines.append(f"Parsed           : {self.parsed_lines}")
        lines.append(f"Unparsed/skipped : {self.unparsed_lines}")
        if self.first_timestamp and self.last_timestamp:
            lines.append(f"Time range       : {self.first_timestamp}  ->  {self.last_timestamp}")
        else:
            lines.append("Time range       : Unknown")
        lines.append("")
        lines.append("Log levels:")
        for lvl, count in sorted(self.level_counts.items()):
            lines.append(f"  {lvl:<10} {count}")
        if self.module_counts:
            lines.append("")
            lines.append("Top modules (by line count):")
            for mod, count in sorted(self.module_counts.items(), key=lambda x: -x[1])[:10]:
                lines.append(f"  {mod:<30} {count}")
        if self.top_errors:
            lines.append("")
            lines.append("Most frequent ERROR/CRITICAL messages (top 5):")
            for i, msg in enumerate(self.top_errors, 1):
                lines.append(f"  {i}. {msg}")
        lines.append("=" * 60)
        return "\n".join(lines)


class Analyzer:
    """Reads a server log file and produces a SummaryReport.

    Args:
        log_path: Path to the log file to analyse.

    Raises:
        FileNotFoundError: if log_path does not exist.
        ValueError: if log_path is not a file.
    """

    def __init__(self, log_path: str | Path) -> None:
        self._path: Path = Path(log_path)
        if not self._path.exists():
            raise FileNotFoundError(f"Log file not found: {self._path}")
        if not self._path.is_file():
            raise ValueError(f"Expected a file, got: {self._path}")
        self._entries: list[LogEntry] = []
        self._total_lines: int = 0
        self._parsed: bool = False

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def parse(self) -> list[LogEntry]:
        """Parse the log file into a list of LogEntry objects.

        Subsequent calls are idempotent — the file is only read once.

        Returns:
            The list of successfully parsed LogEntry objects.
        """
        if self._parsed:
            return self._entries

        entries: list[LogEntry] = []
        total: int = 0
        with self._path.open(encoding="utf-8", errors="replace") as fh:
            for raw_line in fh:
                total += 1
                entry = LogEntry.from_line(raw_line)
                if entry is not None:
                    entries.append(entry)

        self._total_lines = total
        self._entries = entries
        self._parsed = True
        return self._entries

    def summarize(self) -> SummaryReport:
        """Produce a SummaryReport from the parsed entries.

        Calls parse() automatically if it has not been called yet.

        Returns:
            A populated SummaryReport instance.
        """
        entries = self.parse()

        level_counts: Counter[str] = Counter(e.level for e in entries)
        module_counts: Counter[str] = Counter(
            e.module for e in entries if e.module is not None
        )

        timestamps = [e.timestamp for e in entries if e.timestamp is not None]
        first_ts: datetime | None = min(timestamps) if timestamps else None
        last_ts: datetime | None = max(timestamps) if timestamps else None

        error_messages = [
            e.message for e in entries if e.level in {"ERROR", "CRITICAL"}
        ]
        top_errors: list[str] = [
            msg for msg, _ in Counter(error_messages).most_common(5)
        ]

        return SummaryReport(
            total_lines=self._total_lines,
            parsed_lines=len(entries),
            unparsed_lines=self._total_lines - len(entries),
            level_counts=dict(level_counts),
            module_counts=dict(module_counts),
            first_timestamp=first_ts,
            last_timestamp=last_ts,
            top_errors=top_errors,
        )
