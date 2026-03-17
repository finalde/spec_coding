# data_fetcher

Fetches data from a REST API endpoint and saves the response as a JSON file.

## Usage

```bash
make run PROJECT=projects/data_fetcher
```

Or directly:

```bash
.venv/bin/python projects/data_fetcher/main.py --help
```

## Project structure

```
projects/data_fetcher/
├── main.py           # CLI entry point
├── requirements.txt  # project dependencies
└── libs/
    ├── __init__.py
    └── fetcher.py    # Fetcher: fetches data from a REST API and saves it as JSON
```

## Development

Install dependencies:

```bash
make sync-project PROJECT=projects/data_fetcher
```
