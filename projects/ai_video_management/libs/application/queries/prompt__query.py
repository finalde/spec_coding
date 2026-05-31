"""Prompt-aggregate query: per-dimension shot-prompt refinement suggestions
(follow-up 117).

Read-only — no state change, so it skips the domain layer per CLAUDE.md §3
carve-out. It orchestrates: build payload (mapper) → call LLM (infra client)
→ parse reply (mapper), translating infra errors into named domain errors.
"""
from __future__ import annotations

from libs.application.dtos.prompt__dto import (
    SuggestRefinementsInputQdto,
    SuggestRefinementsQdto,
)
from libs.application.mappers.prompt__mapper import PromptMapper
from libs.domain.errors.prompt__error import (
    SuggestionGenerationFailedError,
    SuggestionProviderUnavailableError,
)
from libs.infrastructure.clients.anthropic__client import AnthropicClient
from libs.infrastructure.errors.anthropic__error import (
    AnthropicClientError,
    AnthropicSdkMissingError,
)


class PromptQuery:
    def __init__(self, client: AnthropicClient | None) -> None:
        self._client = client

    def suggest_refinements(
        self, input_qdto: SuggestRefinementsInputQdto
    ) -> SuggestRefinementsQdto:
        if self._client is None:
            raise SuggestionProviderUnavailableError(
                "未配置 ANTHROPIC_API_KEY — 无法生成细化建议"
            )
        system_blocks = PromptMapper.build_system_blocks()
        user_text = PromptMapper.build_user_text(input_qdto)
        try:
            raw = self._client.complete(system_blocks, user_text)
        except AnthropicSdkMissingError as exc:
            raise SuggestionProviderUnavailableError(str(exc)) from exc
        except AnthropicClientError as exc:
            raise SuggestionGenerationFailedError(str(exc)) from exc
        try:
            return PromptMapper.parse_response(
                raw, input_qdto.dimension, input_qdto.count
            )
        except ValueError as exc:
            raise SuggestionGenerationFailedError(f"解析建议失败: {exc}") from exc
