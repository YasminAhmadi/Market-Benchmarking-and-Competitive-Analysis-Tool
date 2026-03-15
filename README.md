# Market Benchmarking & Competitive Analysis Tool

Python project for automated competitor pricing and service benchmarking using structured online product data. The pipeline downloads data from a public API, scores competitor brands across pricing and service metrics, and exports a leadership-ready markdown report plus processed CSV outputs.

## Why this project exists

This project mirrors a finance and shared-services style benchmarking workflow:

- collect competitor data from structured external sources
- compare pricing and service indicators consistently
- summarize findings into decision-ready outputs for product and finance teams

## Data source

The default source is the public DummyJSON products API:

- `https://dummyjson.com/products`

The dataset is downloaded directly in code at runtime. No local source files are required.

## Repository structure

```text
.
├── .github/
│   └── workflows/
├── config/
│   └── benchmark_targets.yaml
├── data/
│   ├── processed/
│   └── raw/
├── reports/
├── src/
│   └── market_benchmarking/
├── tests/
├── pyproject.toml
├── README.md
├── requirements.txt
└── run_pipeline.py
```

## What the pipeline does

1. Downloads all available products from the configured public API.
2. Filters the dataset to benchmark-relevant categories.
3. Parses service signals such as shipping time, return window, and warranty coverage.
4. Scores brands using weighted benchmark metrics.
5. Exports processed tables and a markdown summary report.

## Quick start

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the pipeline

```bash
python run_pipeline.py
```

## Generated outputs

After execution, the project writes:

- `data/raw/competitor_products.json`
- `data/processed/brand_benchmark.csv`
- `data/processed/category_summary.csv`
- `reports/benchmark_report.md`

## Configuration

Update `config/benchmark_targets.yaml` to adjust:

- categories to benchmark
- scoring weights
- competitor sample thresholds
- source endpoint

## Suggested GitHub repo description

Automated benchmarking pipeline for competitor pricing and service analysis using structured online product data.
