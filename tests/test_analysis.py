from market_benchmarking.analysis import (
    parse_duration_to_days,
    parse_warranty_to_months,
)


def test_parse_duration_to_days_for_weeks() -> None:
    assert parse_duration_to_days("Ships in 2 weeks") == 14.0


def test_parse_duration_to_days_for_same_day() -> None:
    assert parse_duration_to_days("Same day delivery") == 0.0


def test_parse_warranty_to_months_for_years() -> None:
    assert parse_warranty_to_months("2 years warranty") == 24.0


def test_parse_warranty_to_months_for_none() -> None:
    assert parse_warranty_to_months("No warranty") == 0.0
