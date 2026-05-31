"""Infra-layer errors for the Anthropic LLM client (follow-up 117).

The application layer catches these and translates them into named
domain errors (`libs/domain/errors/prompt__error.py`); the route layer
never sees infra errors directly.
"""
from __future__ import annotations


class AnthropicClientError(Exception):
    """Base for all Anthropic-client infra errors."""


class AnthropicSdkMissingError(AnthropicClientError):
    """The `anthropic` SDK is not installed (run `uv sync` / `pip install anthropic`)."""


class AnthropicRequestError(AnthropicClientError):
    """The Messages API call failed (network / auth / rate-limit / bad response)."""
