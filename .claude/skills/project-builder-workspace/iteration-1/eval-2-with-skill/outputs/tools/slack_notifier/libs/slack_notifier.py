class SlackNotifier:
    def __init__(self, webhook_url: str, channel: str | None = None) -> None:
        self.webhook_url: str = webhook_url
        self.channel: str | None = channel

    def notify(self, pipeline_name: str, status: str, details: str | None = None) -> bool:
        """Send a Slack notification when a CI pipeline finishes.

        Args:
            pipeline_name: Name of the CI pipeline that finished.
            status: Final status of the pipeline (e.g. 'success', 'failure').
            details: Optional extra details or URL to include in the message.

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        pass

    def build_message(self, pipeline_name: str, status: str, details: str | None = None) -> dict[str, object]:
        """Build the Slack message payload for a pipeline completion event.

        Args:
            pipeline_name: Name of the CI pipeline.
            status: Final status of the pipeline.
            details: Optional extra context to include.

        Returns:
            A dict representing the Slack message payload.
        """
        pass
