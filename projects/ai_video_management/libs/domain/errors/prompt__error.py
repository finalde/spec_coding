"""Named domain errors for the Prompt (suggestion) aggregate — follow-up 117.

The application layer (`PromptQuery`) raises these; `apps/api/app_factory.py`
maps each to a transport-layer error shape. Infra-layer Anthropic errors
(`libs/infrastructure/errors/anthropic__error.py`) are caught in the query
and translated into these named classes — the route layer never sees the
infra errors.
"""
from __future__ import annotations


class PromptSuggestionDomainError(Exception):
    """Base for all Prompt-suggestion domain errors."""


class InvalidSuggestionRequestError(PromptSuggestionDomainError):
    """The suggestion request is malformed (e.g. empty dimension)."""


class SuggestionProviderUnavailableError(PromptSuggestionDomainError):
    """No LLM provider is configured (missing ANTHROPIC_API_KEY) or its SDK is absent."""


class SuggestionGenerationFailedError(PromptSuggestionDomainError):
    """The LLM call ran but the response could not be obtained or parsed."""
