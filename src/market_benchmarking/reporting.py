from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import pandas as pd

from market_benchmarking.config import AppConfig


def _format_markdown_table(frame: pd.DataFrame) -> str:
    columns = list(frame.columns)
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    rows = []

    for _, row in frame.iterrows():
        rows.append("| " + " | ".join(str(row[column]) for column in columns) + " |")

    return "\n".join([header, separator, *rows])


def build_report(
    brand_benchmark: pd.DataFrame,
    category_summary: pd.DataFrame,
    config: AppConfig,
) -> str:
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    top_brand = brand_benchmark.iloc[0]
    cheapest_brand = brand_benchmark.sort_values("avg_price_index", ascending=True).iloc[0]
    best_rated_brand = brand_benchmark.sort_values("avg_rating", ascending=False).iloc[0]

    report_lines = [
        "# Market Benchmarking Report",
        "",
        f"Generated: {generated_at}",
        "",
        "## Executive Summary",
        "",
        f"- Top overall benchmark performer: **{top_brand['brand']}** with a score of **{top_brand['overall_benchmark_score']}**.",
        f"- Strongest price competitiveness: **{cheapest_brand['brand']}** with an average category-relative price index of **{cheapest_brand['avg_price_index']:.2f}**.",
        f"- Highest customer rating: **{best_rated_brand['brand']}** with an average rating of **{best_rated_brand['avg_rating']:.2f}**.",
        f"- Benchmark categories reviewed: **{', '.join(config.benchmark.categories)}**.",
        "",
        "## Brand Benchmark Table",
        "",
        _format_markdown_table(
            brand_benchmark[
                [
                    "brand",
                    "product_count",
                    "avg_price",
                    "avg_rating",
                    "avg_price_index",
                    "median_shipping_days",
                    "median_return_days",
                    "median_warranty_months",
                    "overall_benchmark_score",
                ]
            ].round(2)
        ),
        "",
        "## Category Summary",
        "",
        _format_markdown_table(category_summary.round(2)),
        "",
        "## Scoring Logic",
        "",
        "Weighted score components:",
        f"- Price competitiveness: {config.weights.price_competitiveness:.0%}",
        f"- Customer rating: {config.weights.customer_rating:.0%}",
        f"- Shipping speed: {config.weights.shipping_speed:.0%}",
        f"- Warranty coverage: {config.weights.warranty_coverage:.0%}",
        f"- Return window: {config.weights.return_window:.0%}",
        f"- Stock availability: {config.weights.stock_availability:.0%}",
        "",
        "## Interpretation Notes",
        "",
        "- Lower price index means a brand is priced below the category median on average.",
        "- Shipping days, return policy, and warranty data are parsed from source text fields when available.",
        "- This project is intended as a repeatable benchmarking template and can be repointed to other structured sources.",
    ]

    return "\n".join(report_lines)


def write_outputs(
    raw_products: list[dict],
    brand_benchmark: pd.DataFrame,
    category_summary: pd.DataFrame,
    report_text: str,
    project_root: Path,
) -> None:
    raw_path = project_root / "data" / "raw" / "competitor_products.json"
    processed_dir = project_root / "data" / "processed"
    report_path = project_root / "reports" / "benchmark_report.md"

    raw_path.write_text(json.dumps(raw_products, indent=2), encoding="utf-8")
    brand_benchmark.to_csv(processed_dir / "brand_benchmark.csv", index=False)
    category_summary.to_csv(processed_dir / "category_summary.csv", index=False)
    report_path.write_text(report_text, encoding="utf-8")
