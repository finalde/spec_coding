# slack_notifier

Sends Slack messages when CI pipelines finish, reporting the pipeline status to a configured channel.

## Usage

```bash
make run PROJECT=tools/slack_notifier
```

Or directly:

```bash
.venv/bin/python tools/slack_notifier/main.py --help
```

### Example

```bash
.venv/bin/python tools/slack_notifier/main.py \
  --token xoxb-your-slack-bot-token \
  --channel "#ci-notifications" \
  --status success \
  --pipeline my-build-pipeline
```

## Arguments

| Argument | Required | Description |
|---|---|---|
| `--token` | Yes | Slack bot token (xoxb-...) |
| `--channel` | Yes | Slack channel to post to (e.g. `#ci-notifications`) |
| `--status` | Yes | CI pipeline status (e.g. `success`, `failure`) |
| `--pipeline` | No | Name of the CI pipeline |

## Project structure

```
tools/slack_notifier/
├── main.py           # CLI entry point
├── requirements.txt  # project dependencies
└── libs/
    ├── __init__.py
    └── slack_notifier.py   # SlackNotifier: sends Slack notifications for CI pipeline events
```

## Development

Install dependencies:

```bash
make sync-project PROJECT=tools/slack_notifier
```
