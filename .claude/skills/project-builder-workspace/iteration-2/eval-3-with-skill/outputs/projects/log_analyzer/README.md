# log_analyzer

Reads server logs and produces a summary report.

## Usage

```bash
make run PROJECT=projects/log_analyzer
```

Or directly:

```bash
.venv/bin/python projects/log_analyzer/main.py --help
```

## Project structure

```
projects/log_analyzer/
├── main.py           # CLI entry point
├── requirements.txt  # project dependencies
└── libs/
    ├── __init__.py
    └── analyzer.py   # Analyzer: parses server log files and generates summary reports
```

## Development

Install dependencies:

```bash
make sync-project PROJECT=projects/log_analyzer
```
