"""Generate 3D mesh from multi-view character images using Hunyuan3D 2.0."""

from dataclasses import dataclass
from pathlib import Path

import trimesh
from PIL import Image

CACHE_DIR = Path.home() / ".cache" / "hy3dgen" / "tencent"


def _unwrap_shape_mesh(output: object) -> trimesh.Trimesh:
    """Normalize hy3dgen `export_to_trimesh` output: one Trimesh or list / nested list."""
    if isinstance(output, trimesh.Trimesh):
        return output
    if isinstance(output, (list, tuple)):
        if not output:
            raise ValueError("Shape pipeline returned an empty mesh list")
        first = output[0]
        if isinstance(first, trimesh.Trimesh):
            return first
        if isinstance(first, (list, tuple)) and first:
            inner = first[0]
            if isinstance(inner, trimesh.Trimesh):
                return inner
    raise TypeError(f"Unexpected shape pipeline output: {type(output)!r}")


@dataclass(frozen=True)
class GenerationConfig:
    """Configuration for 3D model generation."""

    # Root folder with Hunyuan shape weights (local cache path or HF repo id).
    shape_model_path: str = str(CACHE_DIR / "Hunyuan3D-2mini")
    # DiT subfolder: mini hunyuan3d-dit-v2-mini, full hunyuan3d-dit-v2-0.
    shape_dit_subfolder: str = "hunyuan3d-dit-v2-mini"
    texture_model_path: str = str(CACHE_DIR / "Hunyuan3D-2")
    device: str = "cuda"
    num_inference_steps: int = 50
    guidance_scale: float = 5.0
    octree_resolution: int = 384
    target_face_count: int = 10000
    remove_background: bool = True


class ModelGenerator:
    """Generates a 3D .glb model from front/side/back reference images."""

    def __init__(self, config: GenerationConfig | None = None) -> None:
        self._config = config or GenerationConfig()
        self._shape_pipeline: object | None = None
        self._texture_pipeline: object | None = None

    def _load_pipelines(self) -> None:
        if self._shape_pipeline is not None:
            return

        try:
            from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
            from hy3dgen.texgen import Hunyuan3DPaintPipeline
        except ImportError as e:
            raise ImportError(
                "Hunyuan3D-2 is not installed. "
                "Run: pip install git+https://github.com/Tencent/Hunyuan3D-2.git"
            ) from e

        print(f"Loading shape pipeline from {self._config.shape_model_path}...")
        self._shape_pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
            self._config.shape_model_path,
            subfolder=self._config.shape_dit_subfolder,
            device=self._config.device,
        )

        try:
            import custom_rasterizer  # noqa: F401 — Hunyuan3D texture paint CUDA extension
        except ModuleNotFoundError as e:
            raise RuntimeError(
                "缺少纹理管线依赖：Python 包 custom_rasterizer（需本地 CUDA 编译）。"
                "请先保证 PyTorch 的 CUDA 版本与 nvcc 一致（见 README），再在项目 venv 中执行：\n"
                "  export PATH=\"/usr/local/cuda-12.6/bin:$PATH\"   # 按本机 CUDA 路径调整\n"
                "  uv pip install --no-build-isolation "
                '"git+https://github.com/Tencent/Hunyuan3D-2.git#'
                'subdirectory=hy3dgen/texgen/custom_rasterizer"\n'
                "或：make setup-hunyuan"
            ) from e

        print(f"Loading texture pipeline from {self._config.texture_model_path}...")
        self._texture_pipeline = Hunyuan3DPaintPipeline.from_pretrained(
            self._config.texture_model_path,
            subfolder="hunyuan3d-paint-v2-0",
        )

    def _remove_bg(self, image: Image.Image) -> Image.Image:
        if not self._config.remove_background:
            return image
        from rembg import remove
        return remove(image)

    def _prepare_images(
        self,
        front_path: Path,
        side_path: Path,
        back_path: Path,
    ) -> dict[str, Image.Image]:
        views: dict[str, Path] = {
            "front": front_path,
            "left": side_path,
            "back": back_path,
        }
        prepared: dict[str, Image.Image] = {}
        for view_name, path in views.items():
            img = Image.open(path).convert("RGBA")
            img = self._remove_bg(img)
            img = img.resize((512, 512), Image.LANCZOS)
            prepared[view_name] = img
            print(f"  Prepared {view_name} view: {path.name}")
        return prepared

    def generate(
        self,
        front_path: Path,
        side_path: Path,
        back_path: Path,
        output_path: Path,
        prompt: str = "",
    ) -> Path:
        """Generate a 3D model from three reference views.

        Args:
            front_path: Path to front view image.
            side_path: Path to side view image.
            back_path: Path to back view image.
            output_path: Where to save the .glb file.
            prompt: Optional text description of the character.

        Returns:
            Path to the generated .glb file.
        """
        self._load_pipelines()

        print("Preparing input images...")
        images = self._prepare_images(front_path, side_path, back_path)

        # Official mini and full DiT configs both use SingleImageEncoder + ImageProcessorV2:
        # pass one PIL (front). A dict iterates string keys in prepare_image → cv2 error.
        print("Generating 3D shape...")
        mesh_results = self._shape_pipeline(
            image=images["front"],
            num_inference_steps=self._config.num_inference_steps,
            guidance_scale=self._config.guidance_scale,
            octree_resolution=self._config.octree_resolution,
        )
        mesh = _unwrap_shape_mesh(mesh_results)

        print("Generating textures...")
        textured_mesh = self._texture_pipeline(
            mesh=mesh,
            image=images["front"],
        )

        if isinstance(textured_mesh, trimesh.Trimesh):
            face_count = len(textured_mesh.faces)
            if face_count > self._config.target_face_count:
                print(
                    f"Decimating mesh from {face_count} to "
                    f"{self._config.target_face_count} faces..."
                )
                try:
                    # First positional arg is `percent` (0..1), not face count.
                    textured_mesh = textured_mesh.simplify_quadric_decimation(
                        face_count=self._config.target_face_count
                    )
                except ModuleNotFoundError as e:
                    if getattr(e, "name", "") == "fast_simplification":
                        print(
                            "Warning: fast_simplification is not installed; "
                            "skipping decimation. Run: uv pip install fast-simplification"
                        )
                    else:
                        raise

        output_path.parent.mkdir(parents=True, exist_ok=True)
        textured_mesh.export(str(output_path))
        print(f"Saved 3D model to {output_path}")

        return output_path
