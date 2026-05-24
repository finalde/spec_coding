"""Errors raised by the Legado book-source reader."""
from __future__ import annotations


class LegadoRuleError(Exception):
    """Failed to apply a Legado rule against a document."""


class LegadoUnsupportedSyntaxError(LegadoRuleError):
    """Encountered a Legado rule construct we don't implement (e.g. @js:)."""


class LegadoFetchError(LegadoRuleError):
    """HTTP error while fetching a URL referenced by a Legado source."""
