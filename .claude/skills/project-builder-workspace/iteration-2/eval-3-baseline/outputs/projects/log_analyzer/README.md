# log_analyzer

A command-line tool that reads server log files and produces a structured summary report.

## Usage

```bash
python main.py path/to/server.log
python main.py path/to/server.log --output report.txt
```

## Log format

The analyzer expects log lines matching this pattern:

```
YYYY-MM-DD HH:MM:SS LEVEL [module] message
```

or ISO 8601 with a `T` separator:

```
YYYY-MM-DDTHH:MM:SS LEVEL [module] message
```

Level values accepted: `DEBUG`, `INFO`, `WARNING` / `WARN`, `ERROR`, `CRITICAL` / `FATAL`
The `[module]` field is optional.

Lines that do not match the pattern are counted as unparsed/skipped.

## Report contents

- Total / parsed / skipped line counts
- Time range of the log
- Per-level line counts
- Top 10 modules by line count
- Top 5 most frequent ERROR/CRITICAL messages

## Flags

| Flag | Description |
|------|-------------|
| `log_file` | Path to the log file (required positional) |
| `--output / -o` | Write report to a file instead of stdout |

## Architecture

```
log_analyzer/
├── main.py          # argument parsing only (~15 lines)
├── requirements.txt # no external deps (stdlib only)
└── libs/
    ├── __init__.py
    └── analyzer.py  # Analyzer, LogEntry, SummaryReport classes
```

### Classes

| Class | Role |
|-------|------|
| `LogEntry` | Frozen dataclass; parses a single raw log line via `from_line()` |
| `SummaryReport` | Aggregated statistics; renders itself via `as_text()` |
| `Analyzer` | Owns the file path; exposes `parse()` and `summarize()` |

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | File not found or invalid path (unhandled exception message printed) |
| `2` | Argument parsing error (argparse default) |
