import argparse

from libs.slack_notifier import SlackNotifier


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a Slack message when a CI pipeline finishes")
    parser.add_argument("--webhook-url", required=True, help="Slack incoming webhook URL")
    parser.add_argument("--pipeline", required=True, help="Name of the CI pipeline")
    parser.add_argument("--status", required=True, help="Final status of the pipeline (e.g. success, failure)")
    parser.add_argument("--channel", default=None, help="Slack channel to post to (optional)")
    parser.add_argument("--details", default=None, help="Extra details or URL to include in the message")
    args = parser.parse_args()

    notifier = SlackNotifier(args.webhook_url, args.channel)
    notifier.notify(args.pipeline, args.status, args.details)


if __name__ == "__main__":
    main()
