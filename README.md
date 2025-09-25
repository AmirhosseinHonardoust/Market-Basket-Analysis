# Market Basket Analysis

Market basket analysis with Python. Generate synthetic retail transactions, mine frequent itemsets using **Apriori** or **FP‑Growth**, derive association rules, and produce clean outputs and charts.

* * *
## Features

- Synthetic transactions generator with realistic co‑purchases (e.g., **Laptop → Mouse/Keyboard/Bag**)
- Frequent itemsets via **Apriori** or **FP‑Growth** (mlxtend)
- Association rules with **support, confidence, lift, leverage, conviction**
- Reproducible artifacts: CSVs for item supports, frequent itemsets, association rules
- Visual: Top‑N items by support (Matplotlib)
- All outputs saved under `outputs/`

* * *
## Project Structure

```
market-basket-analysis/
├─ README.md
├─ LICENSE
├─ requirements.txt
├─ data/
│  └─ generate_transactions.py
├─ src/
│  ├─ market_basket.py
│  └─ utils.py
└─ outputs/
   └─ figures & reports (auto-created)
```

* * *
## Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

* * *
## Generate Synthetic Data

```bash
python data/generate_transactions.py   --start 2024-01-01 --end 2024-12-31   --customers 800 --avg_per_day 120 --seed 42   --out data/transactions.csv
```

* * *
## Run Market Basket Analysis

Apriori:
```bash
python src/market_basket.py   --input data/transactions.csv --outdir outputs   --algo apriori --min_support 0.02 --metric lift --min_threshold 1.1 --top_n 12
```

FP‑Growth:
```bash
python src/market_basket.py   --input data/transactions.csv --outdir outputs   --algo fpgrowth --min_support 0.02 --metric lift --min_threshold 1.1 --top_n 12
```

**Outputs**
- `outputs/item_support.csv`
- `outputs/frequent_itemsets_<algo>.csv`
- `outputs/association_rules_<algo>.csv`
- `outputs/fig_top_items.png`
- `outputs/summary.json`

* * *

* * *
## Example Results (from a real run)

**Top rule (by lift)**

| Antecedents                   | Consequents   | Support | Confidence | Lift | Conviction |
|--------------------------------|---------------|---------|------------|------|------------|
| Keyboard, Laptop Bag, USB-C Hub | Laptop, Mouse | 0.024   | 0.684      | 5.095 | 2.743 |

> Interpretation: baskets containing **Keyboard + Laptop Bag + USB‑C Hub** are **~5× more likely** than random to also include **Laptop + Mouse**.

**Top‑N item supports**

<img width="1200" height="750" alt="fig_top_items" src="https://github.com/user-attachments/assets/6c2e4a9c-2fbb-4e13-aa39-0bf54df2e676" />


**Top rule (by lift)**

| Antecedents        | Consequent   | Support | Confidence | Lift |
|--------------------|--------------|---------|------------|------|
| Laptop, Mouse      | Keyboard     | 0.036   | 0.58       | 2.41 |

> Interpretation: if a basket contains **Laptop + Mouse**, it’s ~2.4× more likely to also contain **Keyboard** than at random.

**Top‑N item supports** (chart saved to `outputs/fig_top_items.png`).

* * *
## Methods

- **Frequent Itemset Mining**: Identify groups of products that co‑occur in transactions. Two algorithms are provided:
  - **Apriori**: generates candidate itemsets level‑wise using the downward‑closure property, pruning infrequent candidates early.
  - **FP‑Growth**: compresses the dataset into an FP‑tree to mine itemsets without explicit candidate generation. Efficient on dense data.
- **Association Rules**: For each frequent itemset, derive rules `X → Y` (with `X ∩ Y = ∅`) and compute:
  - **Support**: `P(X ∪ Y)`
  - **Confidence**: `P(Y|X)`
  - **Lift**: `P(Y|X) / P(Y)` ( >1 indicates positive association )
  - **Leverage** and **Conviction** for additional signal.

* * *
## Notes

- The synthetic generator biases realistic attachments (e.g., Laptop → Mouse/Keyboard/Bag) so mined rules are interpretable.
- Tune `--min_support` and `--min_threshold` for sparser vs. denser rule sets.
- For large datasets, **FP‑Growth** is typically faster than Apriori.

* * *
## About

Market basket analysis with Python. Generate synthetic retail transactions, mine frequent itemsets using Apriori/FP‑Growth, derive association rules, and export figures and CSVs for quick portfolio demos.
