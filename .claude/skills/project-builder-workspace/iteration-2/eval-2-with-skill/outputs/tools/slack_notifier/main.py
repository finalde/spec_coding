import argparse

from libs.slack_notifier import SlackNotifier


def main() -> None:
    parser = argparse.ArgumentParser(description="Send Slack messages when CI pipelines finish")
    parser.add_argument("--token", required=True, help="Slack bot token")
    parser.add_argument("--channel", required=True, help="Slack channel to post to")
    parser.add_argument("--status", required=True, help="CI pipeline status (e.g. success, failure)")
    parser.add_argument("--pipeline", default=None, help="Name of the CI pipeline")
    args = parser.parse_args()

    notifier = SlackNotifier(args.token, args.channel, args.pipeline)
    notifier.notify(args.status)


if __name__ == "__main__":
    main()
