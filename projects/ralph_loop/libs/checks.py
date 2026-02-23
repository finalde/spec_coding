from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScriptCheck:
    run: str  # shell command; passes when exit code is 0


@dataclass(frozen=True)
class NaturalCheck:
    description: str  # Claude interprets and executes this


Check = ScriptCheck | NaturalCheck
