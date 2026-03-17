"""Entry point for the log analyzer."""

import argparse
import sys

from libs.analyzer import Analyzer


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyse a server log file and print a summary report.")
    parser.add_argument("log_file", help="Path to the log file to analyse.")
    parser.add_argument("--output", "-o", help="Write the report to this file instead of stdout.")
    args = parser.parse_args()

    analyzer = Analyzer(args.log_file)
    report = analyzer.summarize()
    text = report.as_text()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"Report written to {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
