#!/usr/bin/env python3
"""Market Basket Analysis: frequent itemsets & association rules.

Steps
-----
1) Load transactions CSV (one row per line-item)
2) Transform to transaction x item one-hot matrix (binary incidence)
3) Mine frequent itemsets via Apriori or FP-Growth (mlxtend)
4) Derive association rules (confidence, lift, leverage)
5) Save CSV artifacts and simple figures

Example
-------
python src/market_basket.py \
  --input data/transactions.csv --outdir outputs \
  --min_support 0.02 --metric lift --min_threshold 1.1 --algo apriori
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules
from utils import ensure_outdir, save_table, save_json, plot_top_items


def load_and_prepare(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Build a basket-level indicator matrix (order_id x item)
    basket = (
        df.assign(qty=lambda d: (d["quantity"] > 0).astype(int))
          .pivot_table(index="order_id", columns="item", values="qty", aggfunc="max", fill_value=0)
          .astype(bool)
    )
    return basket


def mine_frequent_itemsets(basket: pd.DataFrame, algo: str, min_support: float) -> pd.DataFrame:
    if algo == "apriori":
        fi = apriori(basket, min_support=min_support, use_colnames=True)
    elif algo == "fpgrowth":
        fi = fpgrowth(basket, min_support=min_support, use_colnames=True)
    else:
        raise ValueError("algo must be 'apriori' or 'fpgrowth'")
    fi.sort_values(["support", "itemsets"], ascending=[False, True], inplace=True)
    return fi


def derive_rules(fi: pd.DataFrame, metric: str, min_threshold: float) -> pd.DataFrame:
    rules = association_rules(fi, metric=metric, min_threshold=min_threshold)
    # Sort for readability
    rules = rules.sort_values(["lift", "confidence", "support"], ascending=False)
    # Add human-readable columns
    rules["antecedents_str"] = rules["antecedents"].apply(lambda s: ", ".join(sorted(list(s))))
    rules["consequents_str"] = rules["consequents"].apply(lambda s: ", ".join(sorted(list(s))))
    cols = [
        "antecedents_str", "consequents_str", "support", "confidence", "lift", "leverage", "conviction",
    ]
    return rules[[*cols, "antecedents", "consequents"]]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Market Basket Analysis")
    p.add_argument("--input", default="data/transactions.csv")
    p.add_argument("--outdir", default="outputs")
    p.add_argument("--algo", choices=["apriori", "fpgrowth"], default="apriori")
    p.add_argument("--min_support", type=float, default=0.02)
    p.add_argument("--metric", choices=["support", "confidence", "lift", "leverage", "conviction"], default="lift")
    p.add_argument("--min_threshold", type=float, default=1.1, help="threshold for association_rules metric")
    p.add_argument("--top_n", type=int, default=12, help="plot top-N single items by support")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    outdir = ensure_outdir(args.outdir)

    basket = load_and_prepare(args.input)

    # Single-item supports for plotting
    item_support = (
        basket.mean(axis=0)
        .rename("support")
        .reset_index()
        .rename(columns={"index": "item"})
        .sort_values("support", ascending=False)
    )

    fi = mine_frequent_itemsets(basket, args.algo, args.min_support)
    rules = derive_rules(fi, metric=args.metric, min_threshold=args.min_threshold)

    # Save artifacts
    save_table(item_support, outdir / "item_support.csv")
    save_table(fi, outdir / f"frequent_itemsets_{args.algo}.csv")
    save_table(rules, outdir / f"association_rules_{args.algo}.csv")

    # Simple figure
    plot_top_items(item_support, args.top_n, outdir)

    # Summary JSON for quick inspection
    summary = {
        "n_orders": int(basket.shape[0]),
        "n_items": int(basket.shape[1]),
        "algo": args.algo,
        "min_support": args.min_support,
        "metric": args.metric,
        "min_threshold": args.min_threshold,
        "top_rule": rules.head(1).to_dict(orient="records") if not rules.empty else [],
    }
    save_json(summary, outdir / "summary.json")

    print("Artifacts saved to:", str(outdir.resolve()))


if __name__ == "__main__":
    main()
