import json


class Fetcher:
    def __init__(self, url: str, output_path: str) -> None:
        self.url: str = url
        self.output_path: str = output_path

    def fetch(self) -> dict:
        pass

    def save(self, data: dict) -> None:
        pass

    def run(self) -> None:
        pass
