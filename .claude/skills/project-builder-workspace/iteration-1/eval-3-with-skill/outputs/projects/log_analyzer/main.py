import argparse

from libs.analyzer import Analyzer


def main() -> None:
    parser = argparse.ArgumentParser(description="Read server logs and produce a summary report")
    parser.add_argument("--input", required=True, help="Path to the server log file to analyze")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    analyzer = Analyzer(args.input, verbose=args.verbose)
    print(analyzer.summarize())


if __name__ == "__main__":
    main()
