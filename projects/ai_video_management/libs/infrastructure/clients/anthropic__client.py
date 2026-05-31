"""Thin Anthropic Messages-API client for prompt-refinement suggestions
(follow-up 117).

Mirrors the `KlingProvider.from_env()` shape used by the actor pipeline:
credentials are read from the process env (loaded by `libs.common.env_loader`
from `apps/api/.env`), and a missing key yields `None` rather than raising,
so the container can build at startup whether or not the key is configured.

The official `anthropic` SDK is imported lazily on first call so that
neither module import nor container construction fails when the SDK is
absent — the failure surfaces as a named infra error at call time, which
the application layer maps to a clean transport error.

Prompt caching: the system block (the static director-assistant guide) is
marked `cache_control: ephemeral`, so repeated suggestion calls within the
5-minute cache window reuse it and only pay for the per-shot user text.
"""
from __future__ import annotations

import os
from typing import Any

from libs.infrastructure.errors.anthropic__error import (
    AnthropicRequestError,
    AnthropicSdkMissingError,
)

API_KEY_ENV = "ANTHROPIC_API_KEY"
MODEL_ENV = "ANTHROPIC_SUGGEST_MODEL"
DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TIMEOUT_SECONDS = 30.0


class AnthropicClient:
    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._max_tokens = max_tokens
        self._timeout = timeout
        self._impl: Any = None

    @classmethod
    def from_env(cls) -> "AnthropicClient | None":
        key = os.environ.get(API_KEY_ENV, "").strip()
        if not key:
            return None
        model = os.environ.get(MODEL_ENV, "").strip() or DEFAULT_MODEL
        return cls(api_key=key, model=model)

    def _ensure_impl(self) -> Any:
        if self._impl is None:
            try:
                from anthropic import Anthropic
            except ImportError as exc:
                raise AnthropicSdkMissingError(
                    "anthropic SDK 未安装；请运行 `uv sync` 或 `pip install anthropic`"
                ) from exc
            self._impl = Anthropic(api_key=self._api_key, timeout=self._timeout)
        return self._impl

    def complete(self, system_blocks: list[dict[str, Any]], user_text: str) -> str:
        """Run one non-streaming Messages call; return concatenated text blocks."""
        client = self._ensure_impl()
        try:
            response = client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=system_blocks,
                messages=[{"role": "user", "content": user_text}],
            )
        except Exception as exc:  # SDK raises APIError / APIConnectionError / etc.
            raise AnthropicRequestError(f"Messages API 调用失败: {exc}") from exc
        parts = [
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text"
        ]
        return "".join(parts)
