"""
benchmark.py -- time, memory and comparison-count experiments

MSCS 532 Algorithms and Data Structures -- Assignment 2
Author: Jatin Jaiswal

Runs merge_sort, quick_sort (deterministic, last-element pivot),
randomized_quick_sort and -- as a reference point -- Python's built-in
sorted() (Timsort, implemented in C) on three families of input:

    sorted   : 0, 1, 2, ..., n-1
    reverse  : n-1, ..., 2, 1, 0
    random   : n integers drawn uniformly from [0, 10^9) with a fixed seed

For every (algorithm, dataset, n) the script records
    * wall-clock time   -- min and median of several trials (time.perf_counter)
    * auxiliary memory  -- peak bytes allocated DURING the call (tracemalloc)
    * key comparisons   -- one instrumented run with a Counter
and writes everything to results/benchmark_results.csv.  Deterministic
quicksort is Theta(n^2) on sorted and reverse-sorted input, so those two
series are capped at QUADRATIC_MAX_N to keep the run time reasonable.

Usage:
    python benchmark.py            # full run (about 5-10 minutes on a laptop)
    python benchmark.py --quick    # small sizes only, for a smoke test
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import os
import platform
import random
import statistics
import sys
import time
import tracemalloc
from typing import Callable, Dict, List

from merge_sort import Counter, merge_sort
from quick_sort import quick_sort, randomized_quick_sort

# Deterministic quicksort recurses n deep on sorted input; Python's default
# limit is 1,000 frames.  (Since Python 3.12 pure-Python recursion no longer
# consumes C stack, so raising the limit is safe.)
sys.setrecursionlimit(1_100_000)

SIZES = [1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 100_000]
QUADRATIC_MAX_N = 20_000          # cap for quick_sort on sorted / reverse input
# tracemalloc hooks every allocation (each loop-counter int above 256 is one),
# so the memory probe itself becomes Theta(n^2) on those inputs: ~7 us per
# traced allocation => 13 s at n = 2,000 and ~85 s at n = 5,000.  Memory is
# therefore only measured up to this size for the quadratic cases.
QUADRATIC_MEM_MAX_N = 2_000
DATASETS = ["sorted", "reverse", "random"]
SEED = 2026
RESULTS_DIR = "results"


def make_data(kind: str, n: int) -> List[int]:
    """Build one input of the requested kind (same seed => same random data)."""
    if kind == "sorted":
        return list(range(n))
    if kind == "reverse":
        return list(range(n - 1, -1, -1))
    if kind == "random":
        rng = random.Random(SEED + n)
        return [rng.randrange(1_000_000_000) for _ in range(n)]
    raise ValueError(kind)


def builtin_sorted(A: List, counter=None) -> List:
    """Reference: CPython's sorted() (Timsort in C).  Not divide-and-conquer
    in the textbook sense, included only to calibrate the Python results."""
    A[:] = sorted(A)
    return A


def rqs_seeded(A: List, counter=None) -> List:
    """randomized_quick_sort with a fixed RNG so runs are reproducible."""
    return randomized_quick_sort(A, counter=counter, rng=random.Random(SEED))


ALGORITHMS: Dict[str, Callable] = {
    "merge_sort": merge_sort,
    "quick_sort": quick_sort,
    "randomized_quick_sort": rqs_seeded,
    "builtin_sorted": builtin_sorted,
}


def time_one(fn: Callable, data: List) -> float:
    """Wall-clock seconds for one call on a fresh copy of `data`."""
    A = list(data)
    gc.collect()
    gc.disable()                          # keep the collector out of the timing
    t0 = time.perf_counter()
    fn(A)
    t1 = time.perf_counter()
    gc.enable()
    assert A == sorted(data), "sort produced wrong output"
    return t1 - t0


def memory_one(fn: Callable, data: List) -> int:
    """Peak bytes allocated by Python during the call, over and above what
    was already allocated when the call started (tracemalloc)."""
    A = list(data)                        # input copy exists BEFORE measuring
    gc.collect()
    tracemalloc.start()
    base, _ = tracemalloc.get_traced_memory()
    tracemalloc.reset_peak()
    fn(A)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak - base


def comparisons_one(fn: Callable, data: List) -> int:
    """Key comparisons for one instrumented run ('' for builtin_sorted)."""
    if fn is builtin_sorted:
        return -1
    c = Counter()
    fn(list(data), counter=c)
    return c.comparisons


def run(sizes: List[int], out_csv: str) -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    rows = []
    for n in sizes:
        for kind in DATASETS:
            data = make_data(kind, n)
            for name, fn in ALGORITHMS.items():
                if name == "quick_sort" and kind != "random" and n > QUADRATIC_MAX_N:
                    rows.append(dict(algorithm=name, dataset=kind, n=n, trials=0,
                                     time_min_s="", time_median_s="", aux_peak_bytes="",
                                     comparisons="", status="skipped (Theta(n^2))"))
                    print(f"{name:22s} {kind:8s} n={n:>7,}  skipped (quadratic)")
                    continue
                trials = 5 if n <= 20_000 else 3
                times = [time_one(fn, data) for _ in range(trials)]
                quadratic = name == "quick_sort" and kind != "random"
                mem = memory_one(fn, data) if not (quadratic and n > QUADRATIC_MEM_MAX_N) else -1
                comps = comparisons_one(fn, data)
                row = dict(algorithm=name, dataset=kind, n=n, trials=trials,
                           time_min_s=f"{min(times):.6f}",
                           time_median_s=f"{statistics.median(times):.6f}",
                           aux_peak_bytes=mem if mem >= 0 else "",
                           comparisons=comps if comps >= 0 else "",
                           status="ok" if mem >= 0 else "ok (memory not probed: tracemalloc cost)")
                rows.append(row)
                print(f"{name:22s} {kind:8s} n={n:>7,}  median {statistics.median(times):8.4f} s"
                      f"  aux {(f'{mem/1024:9.1f}' if mem >= 0 else '        -')} KiB"
                      f"  comps {comps if comps >= 0 else '-':>12}")
                sys.stdout.flush()

    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    env = dict(python=sys.version.split()[0], implementation=platform.python_implementation(),
               platform=platform.platform(), machine=platform.machine(),
               cpu_count=os.cpu_count(), seed=SEED, sizes=sizes,
               quadratic_cap=QUADRATIC_MAX_N, timestamp=time.strftime("%Y-%m-%d %H:%M:%S"))
    with open(os.path.join(RESULTS_DIR, "environment.json"), "w") as f:
        json.dump(env, f, indent=2)
    print(f"\nwrote {out_csv} ({len(rows)} rows) and results/environment.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true", help="smoke test with small sizes")
    ap.add_argument("--out", default=os.path.join(RESULTS_DIR, "benchmark_results.csv"))
    args = ap.parse_args()
    run([1_000, 2_000, 5_000] if args.quick else SIZES, args.out)
