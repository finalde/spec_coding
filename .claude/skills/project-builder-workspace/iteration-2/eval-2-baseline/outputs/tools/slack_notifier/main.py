"""Entry point: parse CLI arguments and send a CI pipeline Slack notification."""

import argparse
import os
import sys

from libs import SlackNotifier, CIPipelineEvent


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a Slack notification for a CI pipeline result.")
    parser.add_argument("--pipeline", required=True, help="Pipeline name")
    parser.add_argument("--status", required=True, choices=["success", "failure", "cancelled"])
    parser.add_argument("--branch", required=True, help="Git branch name")
    parser.add_argument("--commit", required=True, help="Git commit SHA")
    parser.add_argument("--url", required=True, help="Build URL")
    parser.add_argument("--duration", type=int, default=None, help="Build duration in seconds")
    parser.add_argument("--triggered-by", default=None, help="Who or what triggered the build")
    args = parser.parse_args()

    token: str = os.environ.get("SLACK_BOT_TOKEN", "")
    channel: str = os.environ.get("SLACK_CHANNEL", "")
    if not token or not channel:
        sys.exit("Error: SLACK_BOT_TOKEN and SLACK_CHANNEL environment variables must be set.")

    event = CIPipelineEvent(
        pipeline_name=args.pipeline,
        status=args.status,
        branch=args.branch,
        commit_sha=args.commit,
        build_url=args.url,
        duration_seconds=args.duration,
        triggered_by=args.triggered_by,
    )
    notifier = SlackNotifier(token=token, channel=channel)
    ts = notifier.notify(event)
    print(f"Notification sent (ts={ts})")


if __name__ == "__main__":
    main()
