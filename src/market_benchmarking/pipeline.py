from __future__ import annotations

from pathlib import Path

from market_benchmarking.analysis import (
    build_brand_benchmark,
    build_category_summary,
    build_products_frame,
)
from market_benchmarking.config import load_config
from market_benchmarking.data_sources import fetch_all_products
from market_benchmarking.reporting import build_report, write_outputs


def run(project_root: Path) -> None:
    config = load_config(project_root / "config" / "benchmark_targets.yaml")
    raw_products = fetch_all_products(
        base_url=config.data_source.base_url,
        page_size=config.data_source.page_size,
    )
    products_frame = build_products_frame(raw_products, config.benchmark.categories)
    brand_benchmark = build_brand_benchmark(products_frame, config)
    category_summary = build_category_summary(products_frame)
    report_text = build_report(brand_benchmark, category_summary, config)

    write_outputs(
        raw_products=raw_products,
        brand_benchmark=brand_benchmark,
        category_summary=category_summary,
        report_text=report_text,
        project_root=project_root,
    )
