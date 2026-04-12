"""char3d_gen — Generate 3D character models from multi-view reference images."""

import argparse
import sys
from pathlib import Path

from libs.generator import CACHE_DIR, GenerationConfig, ModelGenerator
from libs.validator import ImageValidator


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a 3D .glb model from front/side/back character images."
    )
    parser.add_argument("--front", type=Path, required=True, help="Front view image")
    parser.add_argument("--side", type=Path, required=True, help="Side view image")
    parser.add_argument("--back", type=Path, required=True, help="Back view image")
    parser.add_argument("--output", type=Path, required=True, help="Output .glb path")
    parser.add_argument("--prompt", type=str, default="", help="Character description")
    parser.add_argument("--skip-validation", action="store_true", help="Skip image consistency check")
    parser.add_argument("--device", type=str, default="cuda", help="Device (cuda/cpu)")
    parser.add_argument("--faces", type=int, default=10000, help="Target face count")
    parser.add_argument(
        "--shape",
        choices=("mini", "full"),
        default="mini",
        help="Shape model: mini (less VRAM) or full Hunyuan3D-2 DiT (better quality, ~hunyuan3d-dit-v2-0).",
    )
    args = parser.parse_args()

    if not args.skip_validation:
        print("=== Validating input images ===")
        validator = ImageValidator(device=args.device)
        result = validator.validate(args.front, args.side, args.back)
        print(result.summary())
        if not result.is_valid:
            print("\nValidation failed. Use --skip-validation to force generation.")
            sys.exit(1)
        print()

    print("=== Generating 3D model ===")
    if args.shape == "full":
        gen_cfg = GenerationConfig(
            device=args.device,
            target_face_count=args.faces,
            shape_model_path=str(CACHE_DIR / "Hunyuan3D-2"),
            shape_dit_subfolder="hunyuan3d-dit-v2-0",
        )
    else:
        gen_cfg = GenerationConfig(
            device=args.device,
            target_face_count=args.faces,
        )
    generator = ModelGenerator(gen_cfg)
    output = generator.generate(
        front_path=args.front,
        side_path=args.side,
        back_path=args.back,
        output_path=args.output,
        prompt=args.prompt,
    )
    print(f"\nDone! Model saved to: {output}")


if __name__ == "__main__":
    main()
