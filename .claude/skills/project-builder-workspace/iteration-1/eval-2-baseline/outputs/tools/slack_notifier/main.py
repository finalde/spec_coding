"""Entry point for slack_notifier — sends a Slack message when a CI pipeline finishes."""

import argparse
import sys

from libs.notifier import PipelineResult, SlackNotifier


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Notify a Slack channel when a CI pipeline finishes."
    )
    parser.add_argument("--token", required=True, help="Slack Bot OAuth token (xoxb-...)")
    parser.add_argument("--channel", required=True, help="Slack channel ID or name")
    parser.add_argument("--pipeline", required=True, help="Pipeline name")
    parser.add_argument(
        "--status",
        required=True,
        choices=["success", "failure", "cancelled"],
        help="Pipeline result status",
    )
    parser.add_argument("--branch", required=True, help="Git branch name")
    parser.add_argument("--commit", required=True, help="Git commit SHA")
    parser.add_argument("--duration", type=int, default=0, help="Duration in seconds")
    parser.add_argument("--url", default=None, help="Pipeline URL (optional)")
    args = parser.parse_args()

    result = PipelineResult(
        pipeline_name=args.pipeline,
        status=args.status,
        branch=args.branch,
        commit_sha=args.commit,
        duration_seconds=args.duration,
        url=args.url,
    )
    notifier = SlackNotifier(token=args.token, channel=args.channel)
    notifier.notify(result)


if __name__ == "__main__":
    main()
