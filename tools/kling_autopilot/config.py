from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Selectors:
    prompt_input: str
    mention_dropdown: str
    mention_option: str
    aspect_control: str
    duration_control: str
    generate_button: str
    result_ready: str
    download_button: str


@dataclass(frozen=True)
class ElementSpec:
    name: str
    search: str
    label: str


@dataclass(frozen=True)
class Timing:
    type_delay_ms: int = 25
    dropdown_timeout_ms: int = 8000
    result_timeout_ms: int = 300000
    between_actions_ms: int = 400


@dataclass(frozen=True)
class KlingConfig:
    create_url: str
    user_data_dir: str
    aspect_ratio: str
    duration: str
    selectors: Selectors
    elements: dict[str, ElementSpec]
    timing: Timing

    @staticmethod
    def load(path: Path) -> "KlingConfig":
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        elements = {entry["name"]: ElementSpec(**entry) for entry in raw["elements"]}
        return KlingConfig(
            create_url=raw["create_url"],
            user_data_dir=raw["user_data_dir"],
            aspect_ratio=raw["aspect_ratio"],
            duration=raw["duration"],
            selectors=Selectors(**raw["selectors"]),
            elements=elements,
            timing=Timing(**raw.get("timing", {})),
        )
