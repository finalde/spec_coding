"""Core logic for sending Slack notifications when CI pipelines finish."""

from dataclasses import dataclass
from typing import Literal

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


PipelineStatus = Literal["success", "failure", "cancelled"]


@dataclass(frozen=True)
class CIPipelineEvent:
    """Immutable data container representing a completed CI pipeline event."""

    pipeline_name: str
    status: PipelineStatus
    branch: str
    commit_sha: str
    build_url: str
    duration_seconds: int | None = None
    triggered_by: str | None = None

    def __post_init__(self) -> None:
        if not self.pipeline_name:
            raise ValueError("pipeline_name must not be empty")
        if self.status not in ("success", "failure", "cancelled"):
            raise ValueError(f"Invalid status: {self.status!r}")
        if not self.branch:
            raise ValueError("branch must not be empty")
        if not self.commit_sha:
            raise ValueError("commit_sha must not be empty")
        if not self.build_url:
            raise ValueError("build_url must not be empty")
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise ValueError("duration_seconds must be non-negative")


class SlackNotifier:
    """Sends CI pipeline completion notifications to a Slack channel."""

    STATUS_EMOJI: dict[PipelineStatus, str] = {
        "success": ":white_check_mark:",
        "failure": ":x:",
        "cancelled": ":warning:",
    }

    STATUS_COLOR: dict[PipelineStatus, str] = {
        "success": "#36a64f",
        "failure": "#e01e5a",
        "cancelled": "#daa038",
    }

    def __init__(self, token: str, channel: str) -> None:
        """Initialize the notifier.

        Args:
            token: Slack Bot OAuth token (starts with xoxb-).
            channel: Slack channel ID or name (e.g. "#ci-notifications").

        Raises:
            ValueError: If token or channel is empty.
        """
        if not token:
            raise ValueError("token must not be empty")
        if not channel:
            raise ValueError("channel must not be empty")

        self._client: WebClient = WebClient(token=token)
        self._channel: str = channel

    def notify(self, event: CIPipelineEvent) -> str:
        """Send a Slack notification for the given pipeline event.

        Args:
            event: The CI pipeline event to report.

        Returns:
            The Slack message timestamp (ts) of the posted message.

        Raises:
            SlackApiError: If the Slack API call fails.
        """
        emoji: str = self.STATUS_EMOJI[event.status]
        color: str = self.STATUS_COLOR[event.status]
        short_sha: str = event.commit_sha[:8]

        title: str = f"{emoji} CI Pipeline *{event.pipeline_name}* — {event.status.upper()}"
        fields: list[dict[str, str]] = [
            {"title": "Branch", "value": event.branch, "short": True},
            {"title": "Commit", "value": short_sha, "short": True},
        ]

        if event.triggered_by:
            fields.append({"title": "Triggered by", "value": event.triggered_by, "short": True})

        if event.duration_seconds is not None:
            duration_str: str = self._format_duration(event.duration_seconds)
            fields.append({"title": "Duration", "value": duration_str, "short": True})

        attachment: dict = {
            "color": color,
            "title": title,
            "title_link": event.build_url,
            "fields": fields,
            "footer": "CI Slack Notifier",
            "mrkdwn_in": ["title"],
        }

        response = self._client.chat_postMessage(
            channel=self._channel,
            attachments=[attachment],
        )

        ts: str = response["ts"]
        return ts

    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Format a duration in seconds as a human-readable string."""
        if seconds < 60:
            return f"{seconds}s"
        minutes: int = seconds // 60
        remaining_seconds: int = seconds % 60
        if remaining_seconds == 0:
            return f"{minutes}m"
        return f"{minutes}m {remaining_seconds}s"
