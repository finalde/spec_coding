#!/usr/bin/env python3
"""ralph_loop — feed a prompt to `claude --continue` until a <promise> tag appears."""
import argparse
import logging
import sys

from libs.loop import DEFAULT_MAX_ITERATIONS, RalphLoop
from libs.state import Prompt


def main() -> None:
    ap = argparse.ArgumentParser(description="Run claude loop until <promise> tag.")
    ap.add_argument("prompt_file", nargs="?", default="PROMPT.md")
    ap.add_argument("--max-iterations", "-n", type=int, default=DEFAULT_MAX_ITERATIONS)
    ap.add_argument("--verbose", "-v", action="store_true", help="Enable DEBUG logging")
    args = ap.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    try:
        prompt: Prompt = Prompt(args.prompt_file)
    except (FileNotFoundError, ValueError) as exc:
        logging.error("%s", exc)
        sys.exit(1)
    sys.exit(RalphLoop(prompt, args.max_iterations).run())


if __name__ == "__main__":
    main()
