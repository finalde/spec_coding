# slack_notifier

Sends a formatted Slack message to a channel when a CI pipeline finishes.

## Features

- Posts a rich Block Kit message showing pipeline name, status, branch, commit, and duration.
- Includes an optional "View Pipeline" button when a URL is supplied.
- Raises a descriptive `SlackApiError` on API failures.

## Dependencies

- `requests` — HTTP utilities (available for future webhook fallback)
- `slack-sdk` — Official Slack SDK for Python

## Usage

```bash
python main.py \
  --token  xoxb-your-bot-token \
  --channel "#ci-alerts" \
  --pipeline "build-and-test" \
  --status success \
  --branch main \
  --commit abc1234def5678 \
  --duration 183 \
  --url "https://ci.example.com/pipelines/42"
```

### Arguments

| Argument     | Required | Description                                      |
|-------------|----------|--------------------------------------------------|
| `--token`   | Yes      | Slack Bot OAuth token (`xoxb-...`)               |
| `--channel` | Yes      | Slack channel ID or name (e.g. `#ci-alerts`)     |
| `--pipeline`| Yes      | Human-readable pipeline name                     |
| `--status`  | Yes      | One of `success`, `failure`, `cancelled`         |
| `--branch`  | Yes      | Git branch name                                  |
| `--commit`  | Yes      | Full or short Git commit SHA                     |
| `--duration`| No       | Pipeline duration in seconds (default `0`)       |
| `--url`     | No       | Link to the pipeline run (adds a button)         |

## Exit codes

| Code | Meaning                               |
|------|---------------------------------------|
| `0`  | Message posted successfully           |
| `1`  | Invalid arguments or Slack API error  |

## Library API

### `PipelineResult` (frozen dataclass)

```python
PipelineResult(
    pipeline_name: str,
    status: str,          # "success" | "failure" | "cancelled"
    branch: str,
    commit_sha: str,
    duration_seconds: int,
    url: str | None = None,
)
```

Raises `ValueError` on invalid inputs.

### `SlackNotifier`

```python
notifier = SlackNotifier(token="xoxb-...", channel="#ci-alerts")
response: dict = notifier.notify(result)
```

## Project structure

```
slack_notifier/
├── main.py              # CLI entry point (~25 lines)
├── requirements.txt     # project-local deps
├── README.md
└── libs/
    ├── __init__.py
    └── notifier.py      # SlackNotifier + PipelineResult
```
