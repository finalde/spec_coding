# slack_notifier

Sends Slack messages when CI pipelines finish. Posts a rich attachment with pipeline status, branch, commit SHA, duration, and a link to the build.

## Setup

```bash
make sync-project PROJECT=tools/slack_notifier
```

Set required environment variables:

| Variable         | Description                              |
|------------------|------------------------------------------|
| `SLACK_BOT_TOKEN`| Bot OAuth token (starts with `xoxb-`)   |
| `SLACK_CHANNEL`  | Channel ID or name (e.g. `#ci-alerts`)  |

## Usage

```bash
export SLACK_BOT_TOKEN=xoxb-...
export SLACK_CHANNEL="#ci-notifications"

python tools/slack_notifier/main.py \
  --pipeline "build-and-test" \
  --status success \
  --branch main \
  --commit abc1234def567890 \
  --url "https://ci.example.com/builds/42" \
  --duration 183 \
  --triggered-by "github-actions"
```

## CLI flags

| Flag            | Required | Description                           |
|-----------------|----------|---------------------------------------|
| `--pipeline`    | Yes      | Pipeline name                         |
| `--status`      | Yes      | `success`, `failure`, or `cancelled`  |
| `--branch`      | Yes      | Git branch name                       |
| `--commit`      | Yes      | Git commit SHA (full or short)        |
| `--url`         | Yes      | URL to the build/job page             |
| `--duration`    | No       | Build duration in seconds             |
| `--triggered-by`| No       | Who or what triggered the build       |

## Exit codes

| Code | Meaning                                           |
|------|---------------------------------------------------|
| 0    | Notification sent successfully                    |
| 1    | Missing environment variables or Slack API error  |

## Architecture

```
tools/slack_notifier/
├── main.py              # CLI argument parsing, delegates to libs/
├── requirements.txt     # requests, slack-sdk
└── libs/
    ├── __init__.py      # re-exports SlackNotifier, CIPipelineEvent
    └── notifier.py      # SlackNotifier class + CIPipelineEvent dataclass
```

### Key classes

**`CIPipelineEvent`** (`libs/notifier.py`)
Frozen dataclass representing a completed pipeline event. Validates all fields in `__post_init__`.

**`SlackNotifier`** (`libs/notifier.py`)
Owns the `slack_sdk.WebClient` instance and channel config. Call `notify(event)` to post a message; returns the Slack message timestamp (`ts`).
