# src/utils.py
from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt

def _json_default(o):
    if isinstance(o, (set, frozenset)):
        return sorted(list(o))
    return str(o)  # last-resort fallback for other exotic types

def ensure_outdir(path: str | Path) -> Path:
    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    return out

def save_table(df: pd.DataFrame, path: str | Path, index: bool = False) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)
    return path

def save_json(data: dict, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=_json_default)
    return path

def plot_top_items(item_support: pd.DataFrame, top_n: int, outdir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5))
    top = item_support.head(top_n)
    ax.bar(top["item"], top["support"])
    ax.set_title(f"Top {top_n} Items by Support")
    ax.set_xlabel("Item")
    ax.set_ylabel("Support")
    plt.xticks(rotation=30, ha="right")
    out_path = outdir / "fig_top_items.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path
