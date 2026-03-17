from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LogEntry:
    """A single parsed log line."""
    raw: str
    level: str        # e.g. INFO, WARNING, ERROR, DEBUG
    timestamp: str    # raw timestamp string as found in the line
    message: str


@dataclass(frozen=True)
class SummaryReport:
    """Immutable summary produced by Analyzer.summarize()."""
    total_lines: int
    parsed_lines: int
    unparsed_lines: int
    level_counts: dict[str, int]
    top_errors: list[str]   # up to 5 most-common ERROR messages

    def __str__(self) -> str:
        lines: list[str] = [
            "=== Log Analysis Report ===",
            f"Total lines    : {self.total_lines}",
            f"Parsed lines   : {self.parsed_lines}",
            f"Unparsed lines : {self.unparsed_lines}",
            "",
            "Level breakdown:",
        ]
        for level, count in sorted(self.level_counts.items()):
            lines.append(f"  {level:<10}: {count}")

        if self.top_errors:
            lines.append("")
            lines.append("Top ERROR messages:")
            for i, msg in enumerate(self.top_errors, 1):
                lines.append(f"  {i}. {msg}")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

# Common log formats:
#   [2024-01-15 12:34:56] ERROR   Some message
#   2024-01-15T12:34:56 WARNING  Another message
#   Jan 15 12:34:56 INFO  A third message
_LOG_PATTERN = re.compile(
    r"(?P<timestamp>"
    r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}"          # ISO-like
    r"|[A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}"       # syslog-like
    r")"
    r"\]?\s+"
    r"(?P<level>DEBUG|INFO|NOTICE|WARNING|WARN|ERROR|CRITICAL|FATAL)"
    r"\s+(?P<message>.+)",
    re.IGNORECASE,
)


class Analyzer:
    """Reads server log files and produces a structured summary report.

    Usage::

        analyzer = Analyzer(Path("server.log"))
        entries = analyzer.parse()
        report  = analyzer.summarize()
        print(report)
    """

    def __init__(self, log_path: Path) -> None:
        if not isinstance(log_path, Path):
            raise TypeError(f"log_path must be a Path, got {type(log_path)!r}")
        if not log_path.exists():
            raise FileNotFoundError(f"Log file not found: {log_path}")
        if not log_path.is_file():
            raise ValueError(f"log_path must point to a file: {log_path}")

        self._log_path: Path = log_path
        self._entries: list[LogEntry] | None = None  # populated on first parse()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def parse(self) -> list[LogEntry]:
        """Parse the log file and return a list of LogEntry objects.

        Lines that do not match the expected format are stored internally
        as unparsed and excluded from the returned list.
        """
        entries: list[LogEntry] = []
        unparsed: list[str] = []

        with self._log_path.open("r", encoding="utf-8", errors="replace") as fh:
            for raw_line in fh:
                line = raw_line.rstrip("\n")
                match = _LOG_PATTERN.search(line)
                if match:
                    entries.append(
                        LogEntry(
                            raw=line,
                            level=match.group("level").upper(),
                            timestamp=match.group("timestamp"),
                            message=match.group("message").strip(),
                        )
                    )
                else:
                    unparsed.append(line)

        self._entries = entries
        self._unparsed: list[str] = unparsed
        return entries

    def summarize(self) -> SummaryReport:
        """Return a SummaryReport for the parsed log data.

        Calls parse() automatically if it has not been called yet.
        """
        if self._entries is None:
            self.parse()

        entries: list[LogEntry] = self._entries  # type: ignore[assignment]
        unparsed: list[str] = getattr(self, "_unparsed", [])

        level_counts: dict[str, int] = dict(Counter(e.level for e in entries))

        error_messages: list[str] = [
            e.message for e in entries if e.level in ("ERROR", "CRITICAL", "FATAL")
        ]
        top_errors: list[str] = [
            msg for msg, _ in Counter(error_messages).most_common(5)
        ]

        return SummaryReport(
            total_lines=len(entries) + len(unparsed),
            parsed_lines=len(entries),
            unparsed_lines=len(unparsed),
            level_counts=level_counts,
            top_errors=top_errors,
        )
