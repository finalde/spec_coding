#!/usr/bin/env python3
"""ralph_loop — feed a structured spec to `claude --continue` until a <promise> tag appears."""
import argparse
import logging
import sys
from pathlib import Path

from libs.config import Config
from libs.loop import DEFAULT_MAX_ITERATIONS, RalphLoop
from libs.spec import Spec

_SPECS_ROOT: Path = Path(__file__).parent / "specs"


def main() -> None:
    ap = argparse.ArgumentParser(description="Run claude loop for a project spec.")
    ap.add_argument("project_name", help="Name of the project folder under specs/")
    args = ap.parse_args()

    project_dir: Path = _SPECS_ROOT / args.project_name
    config_file: Path = project_dir / "config.yml"
    spec_file: Path = project_dir / "spec.yml"

    try:
        config: Config = Config.from_file(config_file) if config_file.exists() else Config.default(args.project_name)
        spec: Spec = Spec.from_file(str(spec_file))
    except (FileNotFoundError, ValueError) as exc:
        logging.error("%s", exc)
        sys.exit(1)

    logging.basicConfig(level=logging.DEBUG if config.verbose else logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    logging.info("Output dir: %s", config.output_dir)
    max_iter: int = config.max_iterations or spec.max_iterations or DEFAULT_MAX_ITERATIONS
    sys.exit(RalphLoop(spec, max_iter, stream=config.stream).run())


if __name__ == "__main__":
    main()
