"""SlackNotifier: sends Slack messages when CI pipelines finish."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


@dataclass(frozen=True)
class PipelineResult:
    """Immutable container representing a CI pipeline result."""

    pipeline_name: str
    status: str  # e.g. "success", "failure", "cancelled"
    branch: str
    commit_sha: str
    duration_seconds: int
    url: str | None = None

    def __post_init__(self) -> None:
        if not self.pipeline_name:
            raise ValueError("pipeline_name must not be empty")
        if self.status not in ("success", "failure", "cancelled"):
            raise ValueError(
                f"status must be one of success/failure/cancelled, got {self.status!r}"
            )
        if self.duration_seconds < 0:
            raise ValueError("duration_seconds must be non-negative")


class SlackNotifier:
    """Sends CI pipeline completion notifications to a Slack channel.

    Parameters
    ----------
    token:
        A Slack Bot OAuth token (starts with ``xoxb-``).
    channel:
        The Slack channel ID or name to post messages to (e.g. ``#ci-alerts``).
    username:
        Display name shown for the bot message (default ``CI Bot``).
    icon_emoji:
        Emoji used as the bot's avatar (default ``:robot_face:``).
    """

    STATUS_EMOJI: dict[str, str] = {
        "success": ":white_check_mark:",
        "failure": ":x:",
        "cancelled": ":warning:",
    }

    def __init__(
        self,
        token: str,
        channel: str,
        username: str = "CI Bot",
        icon_emoji: str = ":robot_face:",
    ) -> None:
        if not token:
            raise ValueError("Slack token must not be empty")
        if not channel:
            raise ValueError("channel must not be empty")

        self._client: WebClient = WebClient(token=token)
        self._channel: str = channel
        self._username: str = username
        self._icon_emoji: str = icon_emoji

    def notify(self, result: PipelineResult) -> dict[str, Any]:
        """Post a pipeline completion message to Slack.

        Parameters
        ----------
        result:
            A :class:`PipelineResult` describing the finished pipeline.

        Returns
        -------
        dict[str, Any]
            The raw Slack API response payload.

        Raises
        ------
        SlackApiError
            If the Slack API returns a non-OK response.
        """
        blocks = self._build_blocks(result)
        fallback_text = self._build_fallback_text(result)

        try:
            response = self._client.chat_postMessage(
                channel=self._channel,
                text=fallback_text,
                blocks=blocks,
                username=self._username,
                icon_emoji=self._icon_emoji,
            )
        except SlackApiError as exc:
            raise SlackApiError(
                f"Failed to post Slack notification for pipeline "
                f"{result.pipeline_name!r}: {exc.response['error']}",
                exc.response,
            ) from exc

        return dict(response.data)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_fallback_text(self, result: PipelineResult) -> str:
        emoji: str = self.STATUS_EMOJI.get(result.status, ":question:")
        return (
            f"{emoji} Pipeline *{result.pipeline_name}* finished with "
            f"*{result.status.upper()}* on branch `{result.branch}`"
        )

    def _build_blocks(self, result: PipelineResult) -> list[dict[str, Any]]:
        emoji: str = self.STATUS_EMOJI.get(result.status, ":question:")
        minutes, seconds = divmod(result.duration_seconds, 60)
        duration_str: str = f"{minutes}m {seconds}s" if minutes else f"{seconds}s"

        header_block: dict[str, Any] = {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{emoji} CI Pipeline: {result.pipeline_name}",
                "emoji": True,
            },
        }

        fields: list[dict[str, str]] = [
            {"type": "mrkdwn", "text": f"*Status*\n{result.status.upper()}"},
            {"type": "mrkdwn", "text": f"*Branch*\n`{result.branch}`"},
            {
                "type": "mrkdwn",
                "text": f"*Commit*\n`{result.commit_sha[:8]}`",
            },
            {"type": "mrkdwn", "text": f"*Duration*\n{duration_str}"},
        ]

        section_block: dict[str, Any] = {
            "type": "section",
            "fields": fields,
        }

        blocks: list[dict[str, Any]] = [header_block, section_block]

        if result.url:
            actions_block: dict[str, Any] = {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Pipeline"},
                        "url": result.url,
                        "action_id": "view_pipeline",
                    }
                ],
            }
            blocks.append(actions_block)

        return blocks
