"""Infrastructure-side exceptions raised by the actor writer/reader.

Per follow-up 067 (Single Responsibility Principle): exception classes
do not belong in the writer/reader file. They live here, one file per
aggregate, mirroring the `libs/domain/errors/actor__error.py` layout
on the domain side. Commands catch these infra exceptions and re-raise
as named domain errors.
"""
from __future__ import annotations


class InvalidAttribute(Exception):
    """Raised when an enum field doesn't match the closed schema or count is out of range."""

class GenerationDirMissing(Exception):
    """Raised when the _actors directory cannot be created (filesystem error)."""

class ActorNotFound(Exception):
    """Raised when delete_actor cannot locate the actor folder."""

class ActorAlreadyDeleted(Exception):
    """Raised when the actor folder is already under _deleted/."""

class ActorDeleteTargetExists(Exception):
    """Raised when the target path under _deleted/_actors/ already exists."""

class ActorDeleteFailed(Exception):
    """Raised on OS-level failure during the rename / mkdir step of delete_actor."""
