"""Named domain errors for the Casting aggregate."""
from __future__ import annotations


class CastingDomainError(Exception):
    """Base for all Casting-aggregate domain errors."""


class InvalidRoleError(CastingDomainError):
    """role is empty, too long, contains control chars, or contains markdown table separator."""


class InvalidDramaPathError(CastingDomainError):
    """rel_drama_path is not of the form 'ai_videos/{drama}' or drama folder missing."""


class DramaNotFoundError(CastingDomainError):
    """The drama folder (or its casting.md) is not on disk."""


class RoleNotFoundError(CastingDomainError):
    """The named role is not in this drama's casting.md."""


class ActorNotInPoolError(CastingDomainError):
    """The actor_id does not correspond to any folder under _actors/."""
