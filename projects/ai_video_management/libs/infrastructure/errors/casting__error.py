"""Infrastructure-side exceptions raised by the casting writer/reader.

Per follow-up 067 (Single Responsibility Principle): exception classes
do not belong in the writer/reader file. They live here, one file per
aggregate, mirroring the `libs/domain/errors/casting__error.py` layout
on the domain side. Commands catch these infra exceptions and re-raise
as named domain errors.
"""
from __future__ import annotations


class InvalidActorId(Exception):
    pass

class InvalidRole(Exception):
    pass
