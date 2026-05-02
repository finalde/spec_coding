from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator


@dataclass(frozen=True)
class RunnerEvent:
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    ts: str = ""

    @classmethod
    def now(cls, type_: str, payload: dict[str, Any] | None = None) -> "RunnerEvent":
        return cls(
            type=type_,
            payload=payload or {},
            ts=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )


class ClaudeRunner:
    """Wraps claude_agent_sdk.query into an async event iterator.

    The SDK is imported lazily so the backend can boot (and tests can run)
    without the package being installed. If the SDK is missing, ClaudeRunner
    falls back to a stub that emits a single error event — enough to verify
    the API surface end-to-end before SDK provisioning.
    """

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root.resolve()

    async def stream(
        self,
        prompt: str,
        *,
        allowed_tools: list[str] | None = None,
        system_prompt: str | None = None,
    ) -> AsyncIterator[RunnerEvent]:
        try:
            sdk = self._load_sdk()
        except ModuleNotFoundError as e:
            yield RunnerEvent.now(
                "runner.sdk_unavailable",
                {"detail": str(e), "hint": "pip install claude-agent-sdk"},
            )
            return

        options = sdk.ClaudeAgentOptions(
            cwd=str(self._repo_root),
            allowed_tools=allowed_tools,
            system_prompt=system_prompt,
        )

        yield RunnerEvent.now("runner.started", {"cwd": str(self._repo_root)})

        try:
            async for message in sdk.query(prompt=prompt, options=options):
                yield self._serialize(message)
        except Exception as e:
            yield RunnerEvent.now("runner.error", {"error": repr(e)})
            return

        yield RunnerEvent.now("runner.completed", {})

    def _load_sdk(self) -> Any:
        import claude_agent_sdk as sdk
        return sdk

    def _serialize(self, message: Any) -> RunnerEvent:
        type_name = type(message).__name__
        payload: dict[str, Any] = {}
        for attr in ("content", "text", "name", "input", "tool_use_id", "stop_reason"):
            if hasattr(message, attr):
                value = getattr(message, attr)
                payload[attr] = self._jsonable(value)
        return RunnerEvent.now(f"sdk.{type_name}", payload)

    def _jsonable(self, value: Any) -> Any:
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, (list, tuple)):
            return [self._jsonable(v) for v in value]
        if isinstance(value, dict):
            return {str(k): self._jsonable(v) for k, v in value.items()}
        return repr(value)
