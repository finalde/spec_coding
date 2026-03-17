"""Core Fetcher class for retrieving data from a REST API and saving as JSON."""

import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class FetchResult:
    """Immutable container for a successful fetch result."""

    url: str
    data: dict | list
    output_path: str


class Fetcher:
    """Fetches data from a REST API endpoint and saves it as a JSON file."""

    def __init__(self, base_url: str, output_dir: str = ".") -> None:
        """
        Initialise the Fetcher.

        Args:
            base_url: Root URL of the REST API (e.g. "https://api.example.com").
            output_dir: Directory where JSON output files will be written.

        Raises:
            ValueError: If base_url is empty.
        """
        if not base_url:
            raise ValueError("base_url must not be empty")
        self.base_url: str = base_url.rstrip("/")
        self.output_dir: Path = Path(output_dir)

    def fetch(self, endpoint: str) -> dict | list:
        """
        Perform a GET request against the given endpoint and return parsed JSON.

        Args:
            endpoint: Path relative to base_url (e.g. "/users/1").

        Returns:
            Parsed JSON payload as a dict or list.

        Raises:
            urllib.error.URLError: On network or HTTP errors.
            ValueError: If the response body is not valid JSON.
        """
        url: str = self.base_url + "/" + endpoint.lstrip("/")
        with urllib.request.urlopen(url) as response:  # noqa: S310
            raw: bytes = response.read()
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Response from {url} is not valid JSON") from exc

    def fetch_and_save(self, endpoint: str, filename: str) -> FetchResult:
        """
        Fetch data from an endpoint and save it as a JSON file.

        Args:
            endpoint: Path relative to base_url.
            filename: Name of the output file (e.g. "users.json").

        Returns:
            A FetchResult describing what was fetched and where it was saved.
        """
        data: dict | list = self.fetch(endpoint)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path: Path = self.output_dir / filename
        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return FetchResult(
            url=self.base_url + "/" + endpoint.lstrip("/"),
            data=data,
            output_path=str(output_path),
        )
