# log_analyzer

Reads server log files and produces a structured summary report.

## Usage

```bash
python main.py <log_file>
python main.py server.log --top-errors 10
```

## Output

```
=== Log Analysis Report ===
Total lines    : 1532
Parsed lines   : 1489
Unparsed lines : 43

Level breakdown:
  DEBUG     : 412
  ERROR     : 87
  INFO      : 904
  WARNING   : 86

Top ERROR messages:
  1. Connection refused: db:5432
  2. Timeout waiting for upstream
  ...
```

## Supported log formats

Lines matching any of these timestamp patterns are parsed:

| Format            | Example                          |
|-------------------|----------------------------------|
| ISO-like          | `2024-01-15 12:34:56 ERROR ...`  |
| ISO T-separator   | `2024-01-15T12:34:56 WARNING ...`|
| Syslog-like       | `Jan 15 12:34:56 INFO ...`       |

Recognized levels: `DEBUG`, `INFO`, `NOTICE`, `WARNING`, `WARN`, `ERROR`, `CRITICAL`, `FATAL`.

Lines that do not match are counted as **unparsed** and excluded from level breakdown.

## Project layout

```
log_analyzer/
├── main.py               # CLI entry point (~15 lines)
├── requirements.txt      # no third-party deps
├── README.md
└── libs/
    ├── __init__.py
    └── analyzer.py       # Analyzer class, LogEntry, SummaryReport
```

## Classes

### `Analyzer`

| Method | Description |
|--------|-------------|
| `__init__(log_path: Path)` | Validates the path; raises `FileNotFoundError` / `ValueError` on bad input. |
| `parse() -> list[LogEntry]` | Reads and parses the file; returns matched entries. |
| `summarize() -> SummaryReport` | Returns a `SummaryReport`; calls `parse()` automatically if needed. |

### `LogEntry` _(frozen dataclass)_

Fields: `raw`, `level`, `timestamp`, `message`.

### `SummaryReport` _(frozen dataclass)_

Fields: `total_lines`, `parsed_lines`, `unparsed_lines`, `level_counts`, `top_errors`.
`str()` renders the human-readable report shown above.

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | Success |
| 1    | File not found or invalid path |
| 2    | Argument parsing error (argparse default) |
