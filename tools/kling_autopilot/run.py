from __future__ import annotations

import argparse
from pathlib import Path

from config import KlingConfig
from segments import PromptSegment, element_count, parse_segments


def _print_plan(segments: list[PromptSegment]) -> None:
    for segment in segments:
        if segment.kind == "element":
            print(f"@ELEM  | {segment.value}")
        else:
            preview = segment.value.replace("\n", "\\n")
            print(f"TEXT   | {preview[:72]}")
    print(f"\n{element_count(segments)} 次 @ 下拉; 共 {len(segments)} 段")


def main() -> None:
    parser = argparse.ArgumentParser(description="Drive the Kling web editor to submit @-element prompts")
    parser.add_argument("prompt", type=Path, help="prompt .txt with inline @element markers")
    parser.add_argument("--config", type=Path, default=Path(__file__).parent / "config.yaml")
    parser.add_argument("--dry-run", action="store_true", help="parse and print the plan, no browser")
    parser.add_argument("--no-generate", action="store_true", help="fill prompt + @ only, do not click 生成")
    parser.add_argument("--download-to", type=Path, default=None, help="save the finished clip here")
    parser.add_argument("--elements", default=None, help="comma-separated element names for --dry-run without a config")
    args = parser.parse_args()

    prompt = args.prompt.read_text(encoding="utf-8")

    if args.dry_run and args.elements is not None:
        names = [name.strip() for name in args.elements.split(",") if name.strip()]
        _print_plan(parse_segments(prompt, names))
        return

    config = KlingConfig.load(args.config)
    segments = parse_segments(prompt, list(config.elements.keys()))

    if args.dry_run:
        _print_plan(segments)
        return

    from kling_session import KlingSession

    with KlingSession(config) as session:
        session.open_create()
        session.fill_prompt(segments)
        session.set_params()
        if args.no_generate:
            return
        session.generate_and_wait()
        if args.download_to is not None:
            session.download_to(args.download_to)


if __name__ == "__main__":
    main()
