from __future__ import annotations

import re
from typing import Iterable

import pandas as pd

from market_benchmarking.config import AppConfig


def parse_duration_to_days(text: str | None) -> float | None:
    if not text:
        return None

    normalized = text.strip().lower()
    match = re.search(r"(\d+)\s+(day|days|week|weeks|month|months)", normalized)
    if not match:
        if "same day" in normalized:
            return 0.0
        return None

    quantity = int(match.group(1))
    unit = match.group(2)

    if unit.startswith("day"):
        return float(quantity)
    if unit.startswith("week"):
        return float(quantity * 7)
    if unit.startswith("month"):
        return float(quantity * 30)
    return None


def parse_warranty_to_months(text: str | None) -> float | None:
    if not text:
        return None

    normalized = text.strip().lower()
    if normalized in {"no warranty", "none"}:
        return 0.0

    match = re.search(r"(\d+)\s+(month|months|year|years)", normalized)
    if not match:
        return None

    quantity = int(match.group(1))
    unit = match.group(2)
    if unit.startswith("month"):
        return float(quantity)
    if unit.startswith("year"):
        return float(quantity * 12)
    return None


def normalize_score(series: pd.Series, higher_is_better: bool) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    min_value = numeric.min()
    max_value = numeric.max()

    if pd.isna(min_value) or pd.isna(max_value) or min_value == max_value:
        return pd.Series([50.0] * len(series), index=series.index)

    if higher_is_better:
        scaled = (numeric - min_value) / (max_value - min_value)
    else:
        scaled = (max_value - numeric) / (max_value - min_value)

    return (scaled.fillna(0.5) * 100).round(2)


def build_products_frame(products: Iterable[dict], categories: list[str]) -> pd.DataFrame:
    frame = pd.DataFrame(products)
    if frame.empty:
        raise ValueError("No product data was retrieved from the source.")

    frame = frame.copy()
    frame["brand"] = frame["brand"].fillna("Unknown")
    frame["category"] = frame["category"].fillna("Unknown")
    frame = frame[frame["category"].isin(categories)].copy()

    if frame.empty:
        raise ValueError("No products matched the configured benchmark categories.")

    frame["shipping_days"] = frame["shippingInformation"].apply(parse_duration_to_days)
    frame["return_days"] = frame["returnPolicy"].apply(parse_duration_to_days)
    frame["warranty_months"] = frame["warrantyInformation"].apply(parse_warranty_to_months)
    frame["in_stock"] = frame["stock"].fillna(0).gt(0).astype(int)

    category_median_price = frame.groupby("category")["price"].transform("median")
    frame["price_index"] = frame["price"] / category_median_price

    return frame


def build_brand_benchmark(products_frame: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    products_frame = products_frame[products_frame["brand"].ne("Unknown")].copy()

    brand_summary = (
        products_frame.groupby("brand", dropna=False)
        .agg(
            product_count=("id", "count"),
            category_count=("category", "nunique"),
            avg_price=("price", "mean"),
            median_price=("price", "median"),
            avg_discount_percentage=("discountPercentage", "mean"),
            avg_rating=("rating", "mean"),
            avg_price_index=("price_index", "mean"),
            stock_availability_rate=("in_stock", "mean"),
            median_shipping_days=("shipping_days", "median"),
            median_return_days=("return_days", "median"),
            median_warranty_months=("warranty_months", "median"),
        )
        .reset_index()
    )

    brand_summary = brand_summary[
        brand_summary["product_count"] >= config.benchmark.minimum_products_per_brand
    ].copy()

    if brand_summary.empty:
        raise ValueError("No brands met the minimum product threshold for benchmarking.")

    weights = config.weights.as_dict()
    brand_summary["price_score"] = normalize_score(
        brand_summary["avg_price_index"], higher_is_better=False
    )
    brand_summary["rating_score"] = normalize_score(
        brand_summary["avg_rating"], higher_is_better=True
    )
    brand_summary["shipping_score"] = normalize_score(
        brand_summary["median_shipping_days"], higher_is_better=False
    )
    brand_summary["warranty_score"] = normalize_score(
        brand_summary["median_warranty_months"], higher_is_better=True
    )
    brand_summary["return_score"] = normalize_score(
        brand_summary["median_return_days"], higher_is_better=True
    )
    brand_summary["stock_score"] = normalize_score(
        brand_summary["stock_availability_rate"], higher_is_better=True
    )

    brand_summary["overall_benchmark_score"] = (
        brand_summary["price_score"] * weights["price_competitiveness"]
        + brand_summary["rating_score"] * weights["customer_rating"]
        + brand_summary["shipping_score"] * weights["shipping_speed"]
        + brand_summary["warranty_score"] * weights["warranty_coverage"]
        + brand_summary["return_score"] * weights["return_window"]
        + brand_summary["stock_score"] * weights["stock_availability"]
    ).round(2)

    brand_summary = brand_summary.sort_values(
        by=["overall_benchmark_score", "avg_rating"], ascending=[False, False]
    ).reset_index(drop=True)

    return brand_summary.head(config.benchmark.top_n_competitors)


def build_category_summary(products_frame: pd.DataFrame) -> pd.DataFrame:
    category_summary = (
        products_frame.groupby("category")
        .agg(
            brand_count=("brand", "nunique"),
            product_count=("id", "count"),
            avg_price=("price", "mean"),
            median_price=("price", "median"),
            avg_rating=("rating", "mean"),
        )
        .reset_index()
        .sort_values(by="avg_price", ascending=False)
    )
    return category_summary
