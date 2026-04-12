"""Validate multi-view input images for consistency before 3D generation."""

from dataclasses import dataclass
from pathlib import Path

import open_clip
import torch
from PIL import Image


@dataclass(frozen=True)
class ValidationResult:
    """Result of multi-view image validation."""

    is_valid: bool
    similarity_scores: dict[str, float]
    warnings: list[str]
    errors: list[str]

    def summary(self) -> str:
        lines = []
        if self.is_valid:
            lines.append("[PASS] Images are consistent enough for 3D generation.")
        else:
            lines.append("[FAIL] Images have consistency issues.")
        for pair, score in self.similarity_scores.items():
            lines.append(f"  {pair}: {score:.3f}")
        for w in self.warnings:
            lines.append(f"  WARNING: {w}")
        for e in self.errors:
            lines.append(f"  ERROR: {e}")
        return "\n".join(lines)


class ImageValidator:
    """Validates that front/side/back reference images depict the same character."""

    SIMILARITY_THRESHOLD: float = 0.65
    MIN_RESOLUTION: int = 512

    def __init__(self, device: str = "cuda") -> None:
        self._device = device
        self._model, _, self._preprocess = open_clip.create_model_and_transforms(
            "ViT-B-32", pretrained="laion2b_s34b_b79k", device=device
        )
        self._model.eval()

    def _encode_image(self, image: Image.Image) -> torch.Tensor:
        tensor = self._preprocess(image).unsqueeze(0).to(self._device)
        with torch.no_grad():
            features = self._model.encode_image(tensor)
            features = features / features.norm(dim=-1, keepdim=True)
        return features

    def _check_resolution(self, path: Path, image: Image.Image) -> list[str]:
        warnings: list[str] = []
        w, h = image.size
        if w < self.MIN_RESOLUTION or h < self.MIN_RESOLUTION:
            warnings.append(
                f"{path.name}: resolution {w}x{h} is below recommended "
                f"{self.MIN_RESOLUTION}x{self.MIN_RESOLUTION}. "
                "Quality may suffer."
            )
        return warnings

    def validate(
        self,
        front_path: Path,
        side_path: Path,
        back_path: Path,
    ) -> ValidationResult:
        """Validate three reference images for cross-view consistency.

        Args:
            front_path: Path to front view image.
            side_path: Path to side view image.
            back_path: Path to back view image.

        Returns:
            ValidationResult with similarity scores and any issues found.
        """
        warnings: list[str] = []
        errors: list[str] = []

        views: dict[str, Path] = {
            "front": front_path,
            "side": side_path,
            "back": back_path,
        }

        images: dict[str, Image.Image] = {}
        for name, path in views.items():
            if not path.exists():
                errors.append(f"{name} image not found: {path}")
                continue
            img = Image.open(path).convert("RGB")
            images[name] = img
            warnings.extend(self._check_resolution(path, img))

        if errors:
            return ValidationResult(
                is_valid=False,
                similarity_scores={},
                warnings=warnings,
                errors=errors,
            )

        embeddings: dict[str, torch.Tensor] = {
            name: self._encode_image(img) for name, img in images.items()
        }

        pairs = [("front-side", "front", "side"),
                 ("front-back", "front", "back"),
                 ("side-back", "side", "back")]
        scores: dict[str, float] = {}
        for pair_name, a, b in pairs:
            sim = (embeddings[a] @ embeddings[b].T).item()
            scores[pair_name] = sim
            if sim < self.SIMILARITY_THRESHOLD:
                warnings.append(
                    f"{pair_name} similarity {sim:.3f} is below threshold "
                    f"{self.SIMILARITY_THRESHOLD}. Characters may not match."
                )

        is_valid = all(s >= self.SIMILARITY_THRESHOLD for s in scores.values())

        return ValidationResult(
            is_valid=is_valid,
            similarity_scores=scores,
            warnings=warnings,
            errors=errors,
        )
