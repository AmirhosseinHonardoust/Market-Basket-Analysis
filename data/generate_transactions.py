#!/usr/bin/env python3
"""Generate a synthetic retail transactions dataset for market basket analysis.

The generator creates realistic co-purchase behavior (e.g., laptops → mouse/keyboard/bag),
optionally across multiple stores and days. Output is a tidy CSV with one row per line item.

Columns: order_id, customer_id, date, store, item, category, price, quantity
"""
from __future__ import annotations
import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
import numpy as np
import pandas as pd

RANDOM_CATEGORIES = {
    # anchor : (co-purchase items, base price)
    "Laptop": (["Mouse", "Keyboard", "Laptop Bag", "USB-C Hub", "External SSD"], 1100),
    "Monitor": (["HDMI Cable", "Monitor Arm", "Mouse"], 220),
    "Smartphone": (["Case", "Screen Protector", "Wireless Charger"], 800),
    "Printer": (["Printer Paper", "Ink Cartridge"], 140),
    "Desk": (["Chair", "Desk Lamp"], 200),
}

EXTRA_ITEMS = {
    "Mouse": 25,
    "Keyboard": 45,
    "Laptop Bag": 60,
    "USB-C Hub": 35,
    "External SSD": 120,
    "HDMI Cable": 12,
    "Monitor Arm": 55,
    "Case": 20,
    "Screen Protector": 15,
    "Wireless Charger": 30,
    "Printer Paper": 8,
    "Ink Cartridge": 28,
    "Chair": 160,
    "Desk Lamp": 30,
}

ALL_ITEMS = {**{k: v for k, (_, v) in RANDOM_CATEGORIES.items()}, **EXTRA_ITEMS}

STORES = ["Downtown", "Mall", "Airport", "Online"]


def sample_basket(rng: random.Random) -> List[str]:
    """Sample a basket with anchor products + probabilistic accessories."""
    anchor = rng.choice(list(RANDOM_CATEGORIES.keys()))
    co_items, _ = RANDOM_CATEGORIES[anchor]
    basket = {anchor}

    # Anchor attachment probabilities
    for item in co_items:
        p = 0.65 if anchor == "Laptop" and item in {"Mouse", "Keyboard", "Laptop Bag"} else 0.35
        if rng.random() < p:
            basket.add(item)

    # Random extras with small probability
    for item in EXTRA_ITEMS:
        if rng.random() < 0.05:
            basket.add(item)

    return sorted(basket)


def generate(start: str, end: str, n_customers: int, avg_orders_per_day: float, seed: int) -> pd.DataFrame:
    rng = random.Random(seed)
    np.random.seed(seed)

    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)
    days = (end_dt - start_dt).days + 1

    rows = []
    order_id = 1
    for d in range(days):
        date = (start_dt + timedelta(days=d)).date().isoformat()
        # Poisson-like orders per day
        n_orders = max(1, int(np.random.poisson(avg_orders_per_day)))
        for _ in range(n_orders):
            customer_id = rng.randint(1, n_customers)
            store = rng.choice(STORES)
            basket = sample_basket(rng)
            for item in basket:
                price = ALL_ITEMS[item] * np.random.uniform(0.9, 1.1)
                qty = 1 if item not in {"Printer Paper", "Ink Cartridge"} else rng.choice([1, 2, 3])
                rows.append({
                    "order_id": order_id,
                    "customer_id": customer_id,
                    "date": date,
                    "store": store,
                    "item": item,
                    "category": "Electronics" if item in ALL_ITEMS else "Misc",
                    "price": round(float(price), 2),
                    "quantity": int(qty),
                })
            order_id += 1

    return pd.DataFrame(rows)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate synthetic transactions CSV")
    p.add_argument("--start", default="2024-01-01", help="start date YYYY-MM-DD")
    p.add_argument("--end", default="2024-12-31", help="end date YYYY-MM-DD")
    p.add_argument("--customers", type=int, default=800)
    p.add_argument("--avg_per_day", type=float, default=120.0, help="avg orders per day")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="data/transactions.csv")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    df = generate(args.start, args.end, args.customers, args.avg_per_day, args.seed)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df):,} rows → {out_path}")


if __name__ == "__main__":
    main()
