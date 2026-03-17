import argparse

from libs.fetcher import Fetcher


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch data from a REST API and save it as JSON")
    parser.add_argument("--url", required=True, help="REST API endpoint URL to fetch data from")
    parser.add_argument("--output", required=True, help="Path to save the resulting JSON file")
    args = parser.parse_args()

    runner = Fetcher(args.url, args.output)
    runner.run()


if __name__ == "__main__":
    main()
