"""Self-hosted Stable Audio background-music generator.

Generates ONE instrumental music clip from a text prompt and writes it as an
mp3. Invoked as a subprocess by the BGM library webapp slice
(`libs/infrastructure/writers/bgm__writer.py`) so the heavy torch / GPU
dependency stays out of the webapp process.

Backend: the `stabilityai/stable-audio-open-1.0` open weights (Stability AI
Community License — commercial-safe under the $1M-revenue ceiling) loaded via
`diffusers.StableAudioPipeline`. diffusers is used instead of the original
`stable-audio-tools` because the latter hard-pins 2023-era deps (pandas==2.0.2,
…) that have no Python 3.12/3.13 wheels; diffusers loads the same weights and
installs cleanly on modern Python. torch / diffusers are imported lazily inside
generation so `--dry-run` works in any environment.

The weights are GATED on Hugging Face: accept the license at
https://huggingface.co/stabilityai/stable-audio-open-1.0 and authenticate the
generation venv (`huggingface-cli login`, or set the HF_TOKEN env var) once.

Usage:
  python tools/stableaudio_gen.py --prompt "<text>" --seed 42 --duration 30 \
      --model stabilityai/stable-audio-open-1.0 --out path/to/bgm_0001.mp3
  python tools/stableaudio_gen.py --prompt "<text>" --seed 42 --duration 30 \
      --out x.mp3 --dry-run

`--dry-run` prints the resolved generation parameters and exits 0 WITHOUT
importing torch or writing any file — the CI / no-GPU path.

seed reproduction is best-effort (Stable Audio's diffusion sampler is not
bit-exact across torch / hardware versions).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SAMPLE_RATE_FALLBACK: int = 44100


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate a BGM mp3 with self-hosted Stable Audio.")
    p.add_argument("--prompt", required=True, help="English instrumental music prompt.")
    p.add_argument("--seed", type=int, required=True, help="Generation seed (best-effort repro).")
    p.add_argument("--duration", type=int, required=True, help="Clip length in seconds (>0).")
    p.add_argument("--model", default="stable-audio-open-1.0", help="HF model id / checkpoint.")
    p.add_argument("--out", required=True, help="Destination mp3 path.")
    p.add_argument("--dry-run", action="store_true", help="Print params and exit; no torch, no write.")
    return p.parse_args(argv)


def _ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def _encode_wav_to_mp3(wav_path: Path, mp3_path: Path) -> None:
    cmd = [
        _ffmpeg_exe(), "-y",
        "-i", str(wav_path),
        "-c:a", "libmp3lame", "-q:a", "2",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-loglevel", "error",
        str(mp3_path),
    ]
    subprocess.run(cmd, check=True)


def _generate(args: argparse.Namespace) -> int:
    # Lazy heavy imports — only on the real generation path.
    import torch
    import torchaudio
    from diffusers import StableAudioPipeline

    # bgm__writer passes the bare checkpoint name (`stable-audio-open-1.0`);
    # diffusers wants the full HF repo id.
    model_id = args.model if "/" in args.model else f"stabilityai/{args.model}"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    pipe = StableAudioPipeline.from_pretrained(model_id, torch_dtype=dtype)
    pipe = pipe.to(device)

    generator = torch.Generator(device).manual_seed(args.seed)
    result = pipe(
        args.prompt,
        negative_prompt="Low quality.",
        num_inference_steps=200,
        audio_end_in_s=float(args.duration),
        num_waveforms_per_prompt=1,
        generator=generator,
        output_type="pt",
    )
    audio = result.audios[0].to(torch.float32).cpu()  # (channels, samples)
    sample_rate = int(getattr(pipe.vae, "sampling_rate", SAMPLE_RATE_FALLBACK))
    audio = audio / audio.abs().max().clamp(min=1e-8)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav_path = Path(tmp) / "raw.wav"
        torchaudio.save(str(wav_path), audio, sample_rate)
        _encode_wav_to_mp3(wav_path, out_path)
    sys.stdout.write(f"wrote {out_path}\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.duration < 1:
        sys.stderr.write("duration must be >= 1\n")
        return 2
    if args.dry_run:
        sys.stdout.write(json.dumps({
            "dry_run": True,
            "prompt": args.prompt,
            "seed": args.seed,
            "duration": args.duration,
            "model": args.model,
            "out": args.out,
        }, ensure_ascii=False) + "\n")
        return 0
    return _generate(args)


if __name__ == "__main__":
    raise SystemExit(main())
