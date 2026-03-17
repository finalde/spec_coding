# data_fetcher

Fetches data from a REST API endpoint and saves it as a JSON file.

## Usage

```bash
python main.py <base_url> <endpoint> <filename> [--output-dir DIR]
```

### Arguments

| Argument | Description |
|---|---|
| `base_url` | Root URL of the REST API, e.g. `https://jsonplaceholder.typicode.com` |
| `endpoint` | Endpoint path to fetch, e.g. `/todos/1` |
| `filename` | Name of the output JSON file, e.g. `todo.json` |
| `--output-dir` | Directory to write the file (default: current directory) |

### Example

```bash
python main.py https://jsonplaceholder.typicode.com /todos/1 todo.json --output-dir ./output
```

Produces `./output/todo.json` containing the API response.

## Structure

```
data_fetcher/
├── main.py          # Argument parsing; delegates to libs.Fetcher
├── requirements.txt # Project dependencies (none yet)
├── README.md        # This file
└── libs/
    ├── __init__.py
    └── fetcher.py   # Fetcher class + FetchResult dataclass
```

## Classes

### `Fetcher`

Main class. Owns the base URL and output directory.

- `__init__(base_url, output_dir)` — raises `ValueError` if `base_url` is empty.
- `fetch(endpoint) -> dict | list` — performs GET request, returns parsed JSON.
- `fetch_and_save(endpoint, filename) -> FetchResult` — fetches and writes JSON file.

### `FetchResult`

Frozen dataclass returned by `fetch_and_save`.

| Field | Type | Description |
|---|---|---|
| `url` | `str` | Full URL that was fetched |
| `data` | `dict \| list` | Parsed JSON payload |
| `output_path` | `str` | Absolute or relative path of the saved file |

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Network/HTTP error or invalid JSON response |
| 2 | Bad CLI arguments |
