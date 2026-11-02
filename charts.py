"""
charts.py -- figures for the report, generated from results/benchmark_results.csv

MSCS 532 Algorithms and Data Structures -- Assignment 2
Author: Jatin Jaiswal

    figures/fig1_time.png         median running time vs n (log-log), one panel per dataset
    figures/fig2_comparisons.png  key comparisons divided by n lg n   (random vs sorted input)
    figures/fig3_memory.png       peak auxiliary memory vs n (log-log)

Usage:  python charts.py
"""

from __future__ import annotations

import csv
import math
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402

CSV = os.path.join("results", "benchmark_results.csv")
OUT = "figures"

COLOR = {                    # one colour per algorithm, used in every figure
    "merge_sort": "#2a78d6",             # blue
    "quick_sort": "#eb6834",             # orange
    "randomized_quick_sort": "#1baf7a",  # aqua
    "builtin_sorted": "#4a3aa7",         # violet
}
LABEL = {
    "merge_sort": "Merge sort",
    "quick_sort": "Quicksort (last-element pivot)",
    "randomized_quick_sort": "Randomized quicksort",
    "builtin_sorted": "Python sorted() [reference]",
}
MARKER = {"merge_sort": "o", "quick_sort": "s", "randomized_quick_sort": "^", "builtin_sorted": "d"}
DATASET_TITLE = {"sorted": "Sorted input", "reverse": "Reverse-sorted input", "random": "Random input"}

plt.rcParams.update({
    "font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8, "legend.fontsize": 7,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": "#e3e3e3", "grid.linewidth": 0.6, "lines.linewidth": 1.4, "lines.markersize": 3.5,
})


def load():
    """rows[(algorithm, dataset)] -> list of dict sorted by n (only status 'ok*')."""
    rows = defaultdict(list)
    with open(CSV, newline="") as f:
        for r in csv.DictReader(f):
            if not r["status"].startswith("ok"):
                continue
            r["n"] = int(r["n"])
            r["time_median_s"] = float(r["time_median_s"])
            r["aux_peak_bytes"] = int(r["aux_peak_bytes"]) if r["aux_peak_bytes"] else None
            r["comparisons"] = int(r["comparisons"]) if r["comparisons"] else None
            rows[(r["algorithm"], r["dataset"])].append(r)
    for k in rows:
        rows[k].sort(key=lambda r: r["n"])
    return rows


def fig1_time(rows):
    fig, axes = plt.subplots(1, 3, figsize=(6.5, 2.3), sharey=True)
    for ax, ds in zip(axes, ["sorted", "reverse", "random"]):
        for alg in COLOR:
            pts = rows.get((alg, ds), [])
            ax.plot([r["n"] for r in pts], [r["time_median_s"] for r in pts],
                    marker=MARKER[alg], color=COLOR[alg], label=LABEL[alg])
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_title(DATASET_TITLE[ds]); ax.set_xlabel("n (elements)")
    axes[0].set_ylabel("median time (s)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(os.path.join(OUT, "fig1_time.png"), dpi=220)
    plt.close(fig)


def fig2_comparisons(rows):
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.05))
    for ax, ds in zip(axes, ["random", "sorted"]):
        for alg in ["merge_sort", "quick_sort", "randomized_quick_sort"]:
            pts = [r for r in rows.get((alg, ds), []) if r["comparisons"]]
            ax.plot([r["n"] for r in pts],
                    [r["comparisons"] / (r["n"] * math.log2(r["n"])) for r in pts],
                    marker=MARKER[alg], color=COLOR[alg], label=LABEL[alg])
        ax.set_xscale("log"); ax.set_xlabel("n (elements)")
        ax.set_title(DATASET_TITLE[ds])
    axes[0].set_ylabel("comparisons / (n lg n)")
    axes[0].set_ylim(0, 1.6)
    axes[1].set_yscale("log")
    axes[1].legend(loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig2_comparisons.png"), dpi=220)
    plt.close(fig)


def fig3_memory(rows):
    fig, ax = plt.subplots(figsize=(6.5, 2.6))
    for alg in COLOR:
        pts = [r for r in rows.get((alg, "random"), []) if r["aux_peak_bytes"]]
        ax.plot([r["n"] for r in pts], [r["aux_peak_bytes"] / 1024 for r in pts],
                marker=MARKER[alg], color=COLOR[alg], label=LABEL[alg] + ", random input")
    pts = [r for r in rows.get(("quick_sort", "sorted"), []) if r["aux_peak_bytes"]]
    ax.plot([r["n"] for r in pts], [r["aux_peak_bytes"] / 1024 for r in pts],
            marker="s", linestyle="--", color="#eda100",
            label="Quicksort (last-element pivot), sorted input")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("n (elements)"); ax.set_ylabel("peak auxiliary memory (KiB)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.28), frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig3_memory.png"), dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    data = load()
    fig1_time(data)
    fig2_comparisons(data)
    fig3_memory(data)
    print("wrote", ", ".join(sorted(os.listdir(OUT))))
