"""log_analyzer — entry point.

Usage:
    python main.py <log_file> [--top-errors N]
"""

import argparse
from pathlib import Path

from libs.analyzer import Analyzer


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a server log file.")
    parser.add_argument("log_file", type=Path, help="Path to the log file.")
    parser.add_argument(
        "--top-errors", type=int, default=5,
        metavar="N", help="Number of top error messages to show (default: 5).",
    )
    args = parser.parse_args()

    analyzer = Analyzer(args.log_file)
    report = analyzer.summarize()
    print(report)


if __name__ == "__main__":
    main()
