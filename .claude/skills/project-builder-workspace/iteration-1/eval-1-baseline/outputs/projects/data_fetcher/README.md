# data_fetcher

A command-line tool that fetches data from a REST API endpoint and saves the response as a JSON file.

## Usage

```bash
python main.py <base_url> <endpoint> [--output-dir DIR] [--filename FILE]
```

### Arguments

| Argument       | Required | Default          | Description                                      |
|----------------|----------|------------------|--------------------------------------------------|
| `base_url`     | yes      | —                | Base URL of the REST API (e.g. `https://api.example.com`) |
| `endpoint`     | yes      | —                | API endpoint path (e.g. `/users/1`)              |
| `--output-dir` | no       | `output`         | Directory where the JSON file will be written    |
| `--filename`   | no       | `response.json`  | Name of the output file                          |

### Example

```bash
python main.py https://jsonplaceholder.typicode.com /todos/1 --output-dir data --filename todo.json
# Saved response to data/todo.json
```

## Project layout

```
data_fetcher/
├── main.py              # CLI entry point (~15 lines)
├── requirements.txt     # Project dependencies (none yet)
├── README.md            # This file
└── libs/
    ├── __init__.py      # Re-exports Fetcher
    └── fetcher.py       # Fetcher class + FetcherConfig dataclass
```

## Classes

### `FetcherConfig` (`libs/fetcher.py`)

Immutable (`@dataclass(frozen=True)`) configuration object.

| Attribute         | Type              | Description                              |
|-------------------|-------------------|------------------------------------------|
| `base_url`        | `str`             | API base URL; must start with http/https |
| `output_path`     | `Path`            | Directory where JSON files are saved     |
| `timeout_seconds` | `int`             | HTTP timeout in seconds (default: 30)    |
| `headers`         | `dict[str, str]`  | Optional request headers (default: `{}`) |

Raises `ValueError` in `__post_init__` for invalid inputs.

### `Fetcher` (`libs/fetcher.py`)

Main class that orchestrates HTTP requests and file persistence.

| Method            | Returns  | Description                                              |
|-------------------|----------|----------------------------------------------------------|
| `fetch(endpoint, params)` | `dict` | GET the endpoint and return parsed JSON          |
| `fetch_and_save(endpoint, filename, params)` | `Path` | Fetch and write JSON to disk |

## Dependencies

No external dependencies. Uses Python standard library only (`urllib`, `json`, `pathlib`).

## Exit codes

| Code | Meaning                              |
|------|--------------------------------------|
| 0    | Success                              |
| 1    | Unhandled exception (network error, invalid JSON, bad arguments) |

## Error conditions

- `ValueError`: raised by `FetcherConfig` if `base_url` is invalid or `timeout_seconds <= 0`.
- `ValueError`: raised by `Fetcher.fetch` if the API response is not valid JSON.
- `urllib.error.URLError`: propagated on network-level failures (DNS, connection refused, timeout).
