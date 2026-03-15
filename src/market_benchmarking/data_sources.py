from __future__ import annotations

from datetime import datetime, timezone

import requests


def fetch_all_products(base_url: str, page_size: int = 100, timeout: int = 30) -> list[dict]:
    products: list[dict] = []
    skip = 0
    total = None

    while total is None or skip < total:
        response = requests.get(
            base_url,
            params={"limit": page_size, "skip": skip},
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()

        batch = payload.get("products", [])
        products.extend(batch)

        total = payload.get("total", len(products))
        if not batch:
            break
        skip += page_size

    fetched_at = datetime.now(timezone.utc).isoformat()
    for product in products:
        product["fetched_at"] = fetched_at

    return products
