"""Production-aggregate command: export every subtitled episode master into a
per-language production folder. Thin application seam over ProductionExporter."""
from __future__ import annotations

from libs.application.dtos.production__dto import ExportProductionResultCdto
from libs.application.mappers.production__mapper import ProductionMapper
from libs.infrastructure.writers.production__writer import ProductionExporter


class ProductionCommand:
    def __init__(self, exporter: ProductionExporter) -> None:
        self._exporter = exporter

    def export(self, rel_path: str) -> ExportProductionResultCdto:
        return ProductionMapper.to_cdto(self._exporter.export(rel_path))
