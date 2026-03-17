# slack_notifier

Sends Slack messages when CI pipelines finish, using an incoming webhook or the Slack SDK.

## Usage

```bash
make run PROJECT=tools/slack_notifier
```

Or directly:

```bash
.venv/bin/python tools/slack_notifier/main.py --help
```

Example — notify on a successful pipeline run:

```bash
.venv/bin/python tools/slack_notifier/main.py \
  --webhook-url https://hooks.slack.com/services/... \
  --pipeline "my-ci-pipeline" \
  --status success \
  --details "https://ci.example.com/builds/42"
```

## Arguments

| Flag | Required | Description |
|------|----------|-------------|
| `--webhook-url` | yes | Slack incoming webhook URL |
| `--pipeline` | yes | Name of the CI pipeline |
| `--status` | yes | Final status (e.g. `success`, `failure`) |
| `--channel` | no | Slack channel to post to |
| `--details` | no | Extra details or build URL to include |

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Message sent successfully |
| 1 | Failed to send message (network error, invalid webhook, etc.) |

## Project structure

```
tools/slack_notifier/
├── main.py           # CLI entry point
├── requirements.txt  # project dependencies
└── libs/
    ├── __init__.py
    └── slack_notifier.py   # SlackNotifier: builds and sends CI status messages to Slack
```

## Development

Install dependencies:

```bash
make sync-project PROJECT=tools/slack_notifier
```
