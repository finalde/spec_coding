"""Named domain errors for the Actor aggregate. Application layer catches
these and maps to transport-layer error shapes; infrastructure never sees
them. Generic exceptions (ValueError, OSError) are NOT used for domain
violations — every invariant breach is a named class."""
from __future__ import annotations


class ActorDomainError(Exception):
    """Base for all Actor-aggregate domain errors."""


class InvalidActorAttributeError(ActorDomainError):
    """An attribute (ethnicity/gender/age_range/look/style/notes/count/resolution/seeds) is out of schema."""


class InvalidActorIdError(ActorDomainError):
    """actor_id does not match the actor_NNNN shape."""


class ActorNotFoundError(ActorDomainError):
    """No actor folder under _actors/ for the given id."""


class ActorAlreadyAssignedError(ActorDomainError):
    """The actor is currently assigned to at least one character role — cannot delete or archive."""

    def __init__(self, actor_id: str, assignments: list[dict[str, object]]) -> None:
        super().__init__(f"actor {actor_id} has {len(assignments)} assignment(s)")
        self.actor_id: str = actor_id
        self.assignments: list[dict[str, object]] = assignments


class ActorAlreadyDeletedError(ActorDomainError):
    """The actor folder is already under _deleted/."""


class ActorDeleteTargetExistsError(ActorDomainError):
    """The target path under _deleted/_actors/ already exists."""


class ActorDeleteFailedError(ActorDomainError):
    """OS-level failure during the rename / mkdir step of delete_actor."""


class ActorGenerationDirMissingError(ActorDomainError):
    """The _actors directory cannot be created (filesystem error at generation time)."""


class AssignmentsScanFailedError(ActorDomainError):
    """OS-level failure while scanning casting.md files for actor assignments."""
