# char3d_gen — 3D Character Model Generator

Generate production-quality 3D `.glb` character models from three reference images (front, side, back views) using **Hunyuan3D 2.0**.

## Pipeline

```
┌─────────────────────────────────────────────────┐
│  Input: front.png + side.png + back.png + prompt │
└──────────────────────┬──────────────────────────┘
                       ▼
              ┌─────────────────┐
              │  CLIP Validator  │  checks cross-view consistency
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │ Background Rem. │  rembg strips backgrounds
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │  Hunyuan3D 2.0  │  multi-view → textured 3D mesh
              │     (mini)      │  ~12-16 GB VRAM
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │ Mesh Decimation │  trimesh simplify to target faces
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │  Export .glb     │  trimesh → glTF binary
              └─────────────────┘
```

## Requirements

- **OS**: Linux (WSL2 recommended on Windows)
- **GPU**: NVIDIA with 16 GB+ VRAM
- **CUDA**: 11.8+ with `nvcc` available
- **Python**: 3.10+
- **Mesh decimation**: `fast-simplification` (pulled in by `requirements.txt`; needed for `trimesh.simplify_quadric_decimation`)

## Setup

```bash
# 1. Create venv and install base deps
make setup

# 2. Install Hunyuan3D-2 + custom_rasterizer (downloads weights ~5GB; extension needs nvcc)
export PATH="/usr/local/cuda-12.6/bin:$PATH"   # must match your PyTorch CUDA (e.g. cu126)
make setup-hunyuan
```

### CUDA mismatch when building `custom_rasterizer`

If you see:

`RuntimeError: ... The detected CUDA version (%s) mismatches the version that was used to compile PyTorch (%s) ... '12.6', '13.0'`

then **`nvcc` on your PATH is 12.6** but **PyTorch was installed as a CUDA 13.0 wheel**. Extensions compile with `nvcc` and must align with `torch.version.cuda`.

**Fix (recommended):** reinstall PyTorch from the CUDA 12.6 wheel index, then rebuild the extension:

```bash
cd projects/char3d_gen
source .venv/bin/activate
export PATH="/usr/local/cuda-12.6/bin:$PATH"
uv pip uninstall torch torchvision torchaudio
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
python -c "import torch; print('torch', torch.__version__, 'cuda', torch.version.cuda)"
uv pip install --no-build-isolation "git+https://github.com/Tencent/Hunyuan3D-2.git#subdirectory=hy3dgen/texgen/custom_rasterizer"
```

**Alternative:** install CUDA **13.x** toolkit and put that `nvcc` first on `PATH` to match a cu130 PyTorch build (heavier).

This project’s `pyproject.toml` pins `torch` / `torchvision` to the `pytorch-cu126` index so `uv sync` stays on CUDA 12.x wheels.

### pytorch3d (if needed)

If Hunyuan3D-2 requires pytorch3d and pip install fails:

```bash
# Option A: conda
conda install pytorch3d -c pytorch3d

# Option B: build from source
pip install "git+https://github.com/facebookresearch/pytorch3d.git"
```

### WSL2-specific setup

```bash
# Ensure NVIDIA driver 535+ is installed on Windows side
nvidia-smi  # should work inside WSL2

# Install CUDA toolkit if nvcc is missing
sudo apt install nvidia-cuda-toolkit

# OpenGL stubs (needed for some trimesh operations)
sudo apt install libegl1-mesa-dev
```

## Usage

### One-shot script (`run_man.sh`)

From anywhere (uses paths under this monorepo’s `ai_videos/...`):

```bash
bash /path/to/projects/char3d_gen/run_man.sh          # mini shape
bash /path/to/projects/char3d_gen/run_man.sh full       # full Hunyuan3D-2 DiT
```

### Generate a 3D model

```bash
make run \
  FRONT=path/to/front.png \
  SIDE=path/to/side.png \
  BACK=path/to/back.png \
  OUTPUT=output/character.glb \
  PROMPT="young female warrior, silver armor, long dark hair"
```

**Shape: mini vs full:** Pass `--shape full` to use **`Hunyuan3D-2`** / `hunyuan3d-dit-v2-0` (larger DiT + VAE latents, more VRAM/time). Default `--shape mini` uses **Hunyuan3D-2mini**. Download the full DiT + VAE folders from [tencent/Hunyuan3D-2](https://huggingface.co/tencent/Hunyuan3D-2) into `~/.cache/hy3dgen/tencent/Hunyuan3D-2/` if missing.

**Single image for shape (mini and full):** The published `config.yaml` for both **mini** and **full** DiT uses **`SingleImageEncoder` + `ImageProcessorV2`**. Only the **front** view is passed into the shape pipeline; side/back are still validated/prepared but not fused into DiT unless you switch to a multi-view config (e.g. `MVImageProcessorV2`), which is not the default HF layout.

### Validate images only (no generation)

```bash
make validate \
  FRONT=path/to/front.png \
  SIDE=path/to/side.png \
  BACK=path/to/back.png
```

### Skip validation

```bash
make run-skip-val \
  FRONT=path/to/front.png \
  SIDE=path/to/side.png \
  BACK=path/to/back.png \
  OUTPUT=output/character.glb \
  PROMPT="description"
```

### Direct Python

```bash
python main.py \
  --front front.png \
  --side side.png \
  --back back.png \
  --output character.glb \
  --prompt "young female warrior, silver armor" \
  --faces 10000 \
  --device cuda
```

## Input Image Guidelines

For best results, your three reference images should:

1. **Same character**: identical outfit, proportions, and features across all views
2. **Clean background**: solid color or transparent (rembg will strip it, but clean input helps)
3. **Resolution**: 512x512 minimum, higher is better
4. **Consistent lighting**: similar light direction and intensity
5. **Full body**: head to toe visible in all views, no cropping
6. **T-pose or neutral stance**: arms slightly away from body for cleaner geometry

## Validation

The validator uses CLIP (ViT-B-32) to compare image embeddings across view pairs:

| Pair | What it catches |
|------|----------------|
| front-side | Outfit/color mismatch between views |
| front-back | Different character entirely |
| side-back | Inconsistent proportions |

**Threshold**: 0.65 cosine similarity. Below this, images are flagged as inconsistent.

## Output

- **Format**: `.glb` (glTF binary) — opens in Blender, Unity, Three.js, Windows 3D Viewer
- **Mesh**: textured, decimated to target face count (default 10k)
- **Textures**: PBR materials baked by Hunyuan3D

## Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--front` | required | Front view image path |
| `--side` | required | Side view image path |
| `--back` | required | Back view image path |
| `--output` | required | Output .glb path |
| `--prompt` | `""` | Text description of the character |
| `--device` | `cuda` | `cuda` or `cpu` |
| `--faces` | `10000` | Target face count after decimation |
| `--skip-validation` | `false` | Skip CLIP consistency check |

## Project Structure

```
projects/char3d_gen/
├── main.py              # CLI entry point (~15 lines)
├── requirements.txt     # project dependencies
├── Makefile             # setup, run, validate targets
├── README.md            # this file
└── libs/
    ├── __init__.py
    ├── validator.py     # CLIP-based multi-view consistency check
    └── generator.py     # Hunyuan3D-2 inference + mesh export
```

## Limitations

- **Identity drift**: AI 3D generation is not perfect. Fingers, facial details, and thin accessories may have artifacts.
- **VRAM**: the mini model uses ~12-16 GB. Close other GPU-heavy apps before running.
- **First run**: model weights download automatically from HuggingFace (~5 GB). Subsequent runs use cache.
- **No rigging**: output is a static mesh. For animation, import into Blender and use Mixamo or AccuRIG for auto-rigging.

## Integration with AI Video Workflow

This tool fits into the video production pipeline as:

```
topic-scout → storyboard → character prompts → image generation (3 views)
                                                        ↓
                                                  char3d_gen ← YOU ARE HERE
                                                        ↓
                                              3D model (.glb) for reference
```

The 3D model can be used to:
- Render additional reference angles for Seedance prompts
- Verify character consistency before committing to video generation
- Provide a turntable preview for the visual bible
