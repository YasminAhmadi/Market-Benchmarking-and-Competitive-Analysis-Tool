from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class DataSourceConfig:
    name: str
    base_url: str
    page_size: int = 100


@dataclass(frozen=True)
class BenchmarkSettings:
    categories: list[str]
    minimum_products_per_brand: int
    top_n_competitors: int


@dataclass(frozen=True)
class BenchmarkWeights:
    price_competitiveness: float
    customer_rating: float
    shipping_speed: float
    warranty_coverage: float
    return_window: float
    stock_availability: float

    def as_dict(self) -> dict[str, float]:
        return {
            "price_competitiveness": self.price_competitiveness,
            "customer_rating": self.customer_rating,
            "shipping_speed": self.shipping_speed,
            "warranty_coverage": self.warranty_coverage,
            "return_window": self.return_window,
            "stock_availability": self.stock_availability,
        }


@dataclass(frozen=True)
class AppConfig:
    data_source: DataSourceConfig
    benchmark: BenchmarkSettings
    weights: BenchmarkWeights


def load_config(config_path: Path) -> AppConfig:
    with config_path.open("r", encoding="utf-8") as handle:
        raw_config = yaml.safe_load(handle)

    return AppConfig(
        data_source=DataSourceConfig(**raw_config["data_source"]),
        benchmark=BenchmarkSettings(**raw_config["benchmark"]),
        weights=BenchmarkWeights(**raw_config["weights"]),
    )
