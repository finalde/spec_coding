#!/usr/bin/env python3
"""ralph_loop — feed a structured spec to `claude --continue` until a <promise> tag appears."""
import argparse
import logging
import sys

from libs.loop import DEFAULT_MAX_ITERATIONS, RalphLoop
from libs.spec import Spec


def main() -> None:
    ap = argparse.ArgumentParser(description="Run claude loop until <promise> tag.")
    ap.add_argument("spec_file", nargs="?", default="SPEC.yaml")
    ap.add_argument("--max-iterations", "-n", type=int, default=None)
    ap.add_argument("--verbose", "-v", action="store_true", help="Enable DEBUG logging")
    args = ap.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    try:
        spec: Spec = Spec.from_file(args.spec_file)
    except (FileNotFoundError, ValueError) as exc:
        logging.error("%s", exc)
        sys.exit(1)
    max_iterations: int = (
        args.max_iterations
        if args.max_iterations is not None
        else (spec.max_iterations if spec.max_iterations is not None else DEFAULT_MAX_ITERATIONS)
    )
    sys.exit(RalphLoop(spec, max_iterations).run())


if __name__ == "__main__":
    main()
