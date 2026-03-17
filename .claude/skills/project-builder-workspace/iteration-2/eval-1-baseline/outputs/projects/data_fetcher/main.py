"""Entry point for data_fetcher: fetch REST API data and save as JSON."""

import argparse

from libs.fetcher import Fetcher


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch data from a REST API and save as JSON.")
    parser.add_argument("base_url", help="Base URL of the REST API")
    parser.add_argument("endpoint", help="Endpoint path to fetch (e.g. /users/1)")
    parser.add_argument("filename", help="Output filename (e.g. output.json)")
    parser.add_argument("--output-dir", default=".", help="Directory to write output (default: .)")
    args = parser.parse_args()

    fetcher = Fetcher(base_url=args.base_url, output_dir=args.output_dir)
    result = fetcher.fetch_and_save(endpoint=args.endpoint, filename=args.filename)
    print(f"Saved {result.url} -> {result.output_path}")


if __name__ == "__main__":
    main()
