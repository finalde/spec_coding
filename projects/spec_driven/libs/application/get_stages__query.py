from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from libs.common.stages import Stages


@dataclass(frozen=True)
class StagesQdto:
    stages: list[dict[str, Any]]

    def to_payload(self) -> dict[str, Any]:
        return {"stages": self.stages}


class GetStagesQuery:
    def execute(self) -> StagesQdto:
        return StagesQdto(stages=Stages.to_payload())
