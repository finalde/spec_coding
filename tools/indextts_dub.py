"""Generate locked-voice 台词配音 for AI-video shots via a local IndexTTS-2.

For each shot, parse its `## 台词配音 prompt` block (voice_id / 情绪 / 语速 / 台词
/ 时长目标), synthesize with IndexTTS-2 using the voice_id's locked reference
sample (timbre) + an emotion text description, then time-fit (pitch-preserving)
so the clip lands inside the shot's target seconds. Optionally mux the result
onto the shot's silent video.

MUST be run with the IndexTTS-2 venv python (it imports the `indextts` package):
  C:/workspace/spec_coding/index-tts/.venv/Scripts/python.exe tools/indextts_dub.py ...

Voice consistency: each voice_id maps to ONE locked reference sample reused for
every line of that character — `<voices-dir>/<voice_id>/ref.{wav,mp3,flac}`.

Usage:
  python tools/indextts_dub.py \
    --repo C:/workspace/spec_coding/index-tts \
    --voices-dir ".../2_世界观人设/voices" \
    --shot ".../episodes/ep01/shots/shot01/shot01.md" \
    [--ref path.wav]            # override voice_id lookup for a single shot
    [--emo-alpha 0.8] [--mux ".../shot01_silent.mp4"] [--out ".../shot01_voice.mp3"]
    [--no-timefit]

Multiple --shot may be passed; the model loads once and processes all.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

_VOICE_ID = re.compile(r"\b([A-Z]{2,4}-[a-z]+-\d{2})\b")
_DUR = re.compile(r"(\d+(?:\.\d+)?)\s*秒")


def _ffmpeg() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def _field(block: str, label: str) -> str | None:
    m = re.search(rf"^{label}\s*[:：]\s*(.+)$", block, re.MULTILINE)
    return m.group(1).strip() if m else None


def _dub_block(md: str) -> str:
    """Return the fenced text of the `## 台词配音 prompt` section."""
    i = md.find("## 台词配音")
    if i < 0:
        raise ValueError("no '## 台词配音' section")
    m = re.search(r"```text\s*(.*?)```", md[i:], re.DOTALL)
    if not m:
        raise ValueError("no ```text block under 台词配音")
    return m.group(1)


def _parse_shot(md_path: Path) -> dict:
    block = _dub_block(md_path.read_text(encoding="utf-8"))
    text = _field(block, "台词")
    if not text:
        raise ValueError(f"{md_path.name}: no 台词")
    dur_raw = _field(block, "时长目标") or ""
    dm = _DUR.search(dur_raw)
    target = float(dm.group(1)) if dm else None
    vm = _VOICE_ID.search(block)
    emo = _field(block, "情绪") or ""
    rate = _field(block, "语速") or ""
    emo_text = "；".join(p for p in (emo, f"语速{rate}" if rate else "") if p)
    return {
        "voice_id": vm.group(1) if vm else None,
        "text": text,
        "emo_text": emo_text,
        "target": target,
    }


def _find_ref(voices_dir: Path, voice_id: str) -> Path:
    d = voices_dir / voice_id
    for ext in ("wav", "mp3", "flac", "m4a"):
        hits = sorted(d.glob(f"*.{ext}"))
        if hits:
            return hits[0]
    raise FileNotFoundError(f"no reference sample in {d} (expected ref.wav/mp3)")


def _probe_dur(ffmpeg: str, path: Path) -> float | None:
    out = subprocess.run([ffmpeg, "-i", str(path)], capture_output=True).stderr.decode(
        "utf-8", errors="replace"
    )
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", out)
    if not m:
        return None
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def _atempo_chain(factor: float) -> str:
    """ffmpeg atempo accepts 0.5-2.0; chain for larger factors."""
    steps: list[float] = []
    f = factor
    while f > 2.0:
        steps.append(2.0)
        f /= 2.0
    while f < 0.5:
        steps.append(0.5)
        f /= 0.5
    steps.append(f)
    return ",".join(f"atempo={s:.6f}" for s in steps)


def _timefit_to_mp3(ffmpeg: str, src: Path, dst: Path, target: float | None) -> None:
    """Encode src→mp3; if it overruns target seconds, compress (pitch-preserving)."""
    dur = _probe_dur(ffmpeg, src) if target else None
    filt: list[str] = []
    if target and dur and dur > target + 0.05:
        filt = ["-filter:a", _atempo_chain(dur / target)]
    cmd = [ffmpeg, "-y", "-i", str(src), *filt, "-c:a", "libmp3lame", "-q:a", "2", str(dst)]
    if subprocess.run(cmd, capture_output=True).returncode != 0:
        raise RuntimeError(f"timefit failed for {src}")


def _mux(ffmpeg: str, video: Path, audio: Path, out: Path) -> None:
    cmd = [
        ffmpeg, "-y", "-i", str(video), "-i", str(audio),
        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        str(out),
    ]
    if subprocess.run(cmd, capture_output=True).returncode != 0:
        raise RuntimeError(f"mux failed for {video}")


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    p = argparse.ArgumentParser(description="IndexTTS-2 台词配音 generator + time-fit + mux.")
    p.add_argument("--repo", required=True, help="index-tts repo dir (holds checkpoints/).")
    p.add_argument("--shot", action="append", required=True, help="shotNN.md path (repeatable).")
    p.add_argument("--voices-dir", default=None, help="dir of <voice_id>/ref.* samples.")
    p.add_argument("--ref", default=None, help="explicit reference sample (single shot).")
    p.add_argument("--emo-alpha", type=float, default=0.8)
    p.add_argument("--no-emo", action="store_true", help="Pure timbre clone, ignore 情绪 (A/B).")
    p.add_argument("--emo-audio", default=None, help="Emotion reference audio: timbre=ref, emotion follows this clip.")
    p.add_argument("--emo-vec", default=None, help="8 comma floats [喜,怒,哀,惧,厌,忧,惊,静]; timbre stays on ref.")
    p.add_argument("--mux", default=None, help="silent video to mux (single shot).")
    p.add_argument("--out", default=None, help="output mp3 (single shot; else <shotdir>/<stem>_voice.mp3).")
    p.add_argument("--no-timefit", action="store_true")
    args = p.parse_args(argv)

    ffmpeg = _ffmpeg()
    repo = Path(args.repo)
    ckpt = repo / "checkpoints"

    from indextts.infer_v2 import IndexTTS2

    tts = IndexTTS2(cfg_path=str(ckpt / "config.yaml"), model_dir=str(ckpt), use_fp16=True)

    for shot_path_s in args.shot:
        shot = Path(shot_path_s)
        info = _parse_shot(shot)
        if args.ref:
            ref = Path(args.ref)
        elif args.voices_dir and info["voice_id"]:
            ref = _find_ref(Path(args.voices_dir), info["voice_id"])
        else:
            raise ValueError(f"{shot.name}: no --ref and could not resolve voice_id/{info['voice_id']}")

        out_mp3 = Path(args.out) if args.out else shot.parent / f"{shot.stem}_voice.mp3"
        raw_wav = shot.parent / f"{shot.stem}_voice.raw.wav"

        print(f"[{shot.stem}] voice={info['voice_id']} ref={ref.name} target={info['target']}s")
        print(f"  emo='{info['emo_text']}'  text='{info['text'][:30]}...'")
        if args.emo_vec:
            vec = [float(x) for x in args.emo_vec.split(",")]
            tts.infer(
                spk_audio_prompt=str(ref),
                text=info["text"],
                output_path=str(raw_wav),
                emo_vector=vec,
                emo_alpha=args.emo_alpha,
                verbose=False,
            )
        elif args.emo_audio:
            tts.infer(
                spk_audio_prompt=str(ref),
                text=info["text"],
                output_path=str(raw_wav),
                emo_audio_prompt=args.emo_audio,
                emo_alpha=args.emo_alpha,
                verbose=False,
            )
        elif args.no_emo:
            tts.infer(
                spk_audio_prompt=str(ref),
                text=info["text"],
                output_path=str(raw_wav),
                verbose=False,
            )
        else:
            tts.infer(
                spk_audio_prompt=str(ref),
                text=info["text"],
                output_path=str(raw_wav),
                use_emo_text=True,
                emo_text=info["emo_text"],
                emo_alpha=args.emo_alpha,
                verbose=False,
            )
        if args.no_timefit:
            _timefit_to_mp3(ffmpeg, raw_wav, out_mp3, None)
        else:
            _timefit_to_mp3(ffmpeg, raw_wav, out_mp3, info["target"])
        raw_wav.unlink(missing_ok=True)
        final_dur = _probe_dur(ffmpeg, out_mp3)
        print(f"  -> {out_mp3.name}  ({final_dur:.2f}s)")

        if args.mux:
            voiced = shot.parent / f"{shot.stem}_voiced.mp4"
            _mux(ffmpeg, Path(args.mux), out_mp3, voiced)
            print(f"  -> {voiced.name} (muxed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
