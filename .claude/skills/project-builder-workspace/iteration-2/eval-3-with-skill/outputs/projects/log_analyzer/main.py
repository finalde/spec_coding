import argparse

from libs.analyzer import Analyzer


def main() -> None:
    parser = argparse.ArgumentParser(description="Reads server logs and produces a summary report.")
    parser.add_argument("--input", required=True, help="Path to the server log file to analyze")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    runner = Analyzer(args.input, verbose=args.verbose)
    runner.summarize()


if __name__ == "__main__":
    main()
