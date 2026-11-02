# MSCS 532 – Assignment 2: Analyzing and Implementing Divide-and-Conquer Algorithms

**Jatin Jaiswal** · MSCS 532 Algorithms and Data Structures · University of the Cumberlands

Merge sort and quicksort (deterministic last-element pivot and randomized), implemented in
Python from the CLRS 4th-edition pseudocode, analyzed with the substitution, recursion-tree
and master methods, and benchmarked on sorted, reverse-sorted and random inputs.

The written analysis is **`Assignment2_Divide_and_Conquer_Analysis.pdf`** (APA 7).

## Repository layout

| Path | What it is |
|---|---|
| `merge_sort.py` | `merge_sort(A)` – CLRS MERGE-SORT / MERGE; stable, Θ(n) extra space; optional comparison `Counter` |
| `quick_sort.py` | `quick_sort(A)` (PARTITION with pivot `A[r]`) and `randomized_quick_sort(A)`; in place |
| `test_sorts.py` | 7 `unittest` cases: textbook examples, edge cases, duplicates, stability, 200 random checks vs `sorted()`, recursion-depth behaviour |
| `benchmark.py` | Timing (`time.perf_counter`), peak auxiliary memory (`tracemalloc`) and comparison counts → `results/benchmark_results.csv` |
| `charts.py` | Builds `figures/fig1_time.png`, `fig2_comparisons.png`, `fig3_memory.png` from the CSV |
| `recursion_demo.py` | Shows deterministic quicksort hitting Python's default recursion limit on 1,000 sorted integers |
| `results/` | Raw CSV, full benchmark log, `environment.json`, recursion-demo output |
| `figures/` | The three figures used in the report |
| `docs/` | `report_template.html` + `build_report.py` (fills every number from the CSV) + `render.py` (HTML → PDF via headless Chromium) |

## Running it

```bash
python -m unittest -v test_sorts.py        # all tests pass on Python 3.13
python merge_sort.py 12 3 7 9 14 6 11 2    # tiny CLI demos
python quick_sort.py 2 8 7 1 3 5 6 4
python recursion_demo.py

python benchmark.py                        # ~5 min; writes results/benchmark_results.csv
python charts.py                           # needs matplotlib
python docs/build_report.py && python docs/render.py docs/report.html report.pdf   # needs playwright
```

## Headline results (Python 3.13, median of 3–5 trials)

| Algorithm | Input | n = 10,000 | n = 20,000 | n = 100,000 |
|---|---|---:|---:|---:|
| Merge sort | sorted / reverse / random | 0.014 / 0.014 / 0.017 s | 0.029 / 0.029 / 0.036 s | 0.165 / 0.167 / 0.219 s |
| Quicksort (last-element pivot) | sorted / reverse / random | 3.52 / 2.51 / 0.012 s | 14.7 / 10.6 / 0.024 s | — / — / 0.168 s |
| Randomized quicksort | sorted / reverse / random | 0.013 / 0.013 / 0.015 s | 0.028 / 0.028 / 0.034 s | 0.163 / 0.164 / 0.176 s |
| Python `sorted()` (reference) | sorted / reverse / random | 0.0001 / 0.0001 / 0.0015 s | 0.0002 / 0.0002 / 0.0036 s | 0.0011 / 0.0013 / 0.019 s |

* Merge sort and randomized quicksort scale as Θ(n lg n) on every input (×1.96 and ×2.01 from
  50k → 100k elements on random data; n lg n predicts ×2.13).
* Deterministic quicksort on sorted / reverse-sorted input is Θ(n²): ×4.2 when n doubles, exactly
  n(n−1)/2 comparisons, and a recursion depth of n – it raises `RecursionError` on 1,000 sorted
  integers under Python's default limit.
* Comparison counts at n = 20,000 ÷ n lg n: merge sort 0.49 (reverse) – 0.91 (random);
  randomized quicksort 1.16–1.21 (theory ≈ 1.39 asymptotically).
* Peak auxiliary memory: merge sort ≈ 8 bytes/element (782 KiB at n = 100,000);
  quicksort on random input 2.8 KiB (Θ(lg n) stack); deterministic quicksort on sorted input
  47 KiB → 109 KiB from n = 1,000 → 2,000 (Θ(n) stack).

## Reference

Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to algorithms* (4th ed.). MIT Press.
