"""Core Fetcher class for retrieving data from a REST API and saving it as JSON."""

import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class FetcherConfig:
    """Immutable configuration for a Fetcher instance."""

    base_url: str
    output_path: Path
    timeout_seconds: int = 30
    headers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError(f"base_url must start with http:// or https://, got: {self.base_url!r}")
        if self.timeout_seconds <= 0:
            raise ValueError(f"timeout_seconds must be positive, got: {self.timeout_seconds}")


class Fetcher:
    """Fetches data from a REST API endpoint and persists responses as JSON files."""

    def __init__(self, config: FetcherConfig) -> None:
        self._config: FetcherConfig = config
        self._config.output_path.mkdir(parents=True, exist_ok=True)

    @property
    def config(self) -> FetcherConfig:
        return self._config

    def fetch(self, endpoint: str, params: dict[str, str] | None = None) -> dict:
        """
        Perform a GET request to base_url + endpoint and return the parsed JSON body.

        Args:
            endpoint: Path appended to base_url (e.g. "/users/1").
            params:   Optional query-string parameters.

        Returns:
            Parsed JSON response as a dict.

        Raises:
            urllib.error.URLError: On network-level failures.
            ValueError: If the response body is not valid JSON.
        """
        url: str = self._build_url(endpoint, params)
        request = urllib.request.Request(url, headers=self._config.headers)

        with urllib.request.urlopen(request, timeout=self._config.timeout_seconds) as response:
            raw_bytes: bytes = response.read()

        try:
            data: dict = json.loads(raw_bytes.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Response from {url!r} is not valid JSON: {exc}") from exc

        return data

    def fetch_and_save(self, endpoint: str, filename: str, params: dict[str, str] | None = None) -> Path:
        """
        Fetch data from endpoint and write it to <output_path>/<filename>.

        Args:
            endpoint: Path appended to base_url.
            filename: Name of the output file (e.g. "users.json").
            params:   Optional query-string parameters.

        Returns:
            Path to the saved JSON file.
        """
        data: dict = self.fetch(endpoint, params)
        output_file: Path = self._config.output_path / filename
        output_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return output_file

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_url(self, endpoint: str, params: dict[str, str] | None) -> str:
        """Combine base_url and endpoint, appending query params if provided."""
        base: str = self._config.base_url.rstrip("/")
        path: str = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        url: str = base + path

        if params:
            query: str = "&".join(
                f"{urllib.parse.quote_plus(k)}={urllib.parse.quote_plus(v)}"
                for k, v in params.items()
            )
            url = f"{url}?{query}"

        return url
