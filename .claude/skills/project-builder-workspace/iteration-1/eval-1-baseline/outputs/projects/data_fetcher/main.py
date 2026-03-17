"""Entry point for data_fetcher: parses CLI arguments and delegates to Fetcher."""

import argparse
from pathlib import Path

from libs.fetcher import Fetcher, FetcherConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch data from a REST API and save as JSON.")
    parser.add_argument("base_url", help="Base URL of the REST API (e.g. https://api.example.com)")
    parser.add_argument("endpoint", help="API endpoint path (e.g. /users)")
    parser.add_argument("--output-dir", default="output", help="Directory to save JSON files (default: output)")
    parser.add_argument("--filename", default="response.json", help="Output filename (default: response.json)")
    args = parser.parse_args()

    config = FetcherConfig(base_url=args.base_url, output_path=Path(args.output_dir))
    fetcher = Fetcher(config)
    saved_path = fetcher.fetch_and_save(args.endpoint, args.filename)
    print(f"Saved response to {saved_path}")


if __name__ == "__main__":
    main()
