import json


class Fetcher:
    def __init__(self, url: str, output_path: str) -> None:
        self.url: str = url
        self.output_path: str = output_path

    def fetch(self) -> dict:
        """Fetch data from the REST API and return as a dict."""
        pass

    def save(self, data: dict) -> None:
        """Save the fetched data as JSON to output_path."""
        pass

    def run(self) -> None:
        """Fetch data from the API and save it as JSON."""
        data = self.fetch()
        self.save(data)
