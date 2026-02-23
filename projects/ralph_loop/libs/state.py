from pathlib import Path


class Prompt:
    def __init__(self, path: str) -> None:
        p: Path = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Prompt file not found: {p}")
        text: str = p.read_text(encoding="utf-8").strip()
        if not text:
            raise ValueError(f"Prompt file is empty: {p}")
        self.path: str = path
        self.text: str = text
