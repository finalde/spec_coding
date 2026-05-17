"""ActorEntity — has identity (actor_id) + holds an ActorAttrs value object.

Per development.md §2: entities use mutable @dataclass with invariant-guarded
methods. ActorEntity is currently a thin holder — most actor business logic
lives on ActorAttrs (validation) and the prompt/sidecar value objects.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from libs.domain.errors.actor__error import InvalidActorIdError
from libs.domain.value_objects.actor__valueobject import ActorAttrs

_ACTOR_ID_RE = re.compile(r"^actor_\d{4,}$")


def validate_actor_id(actor_id: str) -> None:
    if not _ACTOR_ID_RE.match(actor_id):
        raise InvalidActorIdError(f"actor_id={actor_id!r} does not match shape actor_NNNN")


@dataclass
class ActorEntity:
    actor_id: str
    attrs: ActorAttrs
    image_path: str
    mtime: float

    def __post_init__(self) -> None:
        validate_actor_id(self.actor_id)
