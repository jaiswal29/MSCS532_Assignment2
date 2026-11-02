"""
build_report.py -- fill docs/report_template.html from the measured data.

Every number quoted in the report is computed here from
results/benchmark_results.csv, results/environment.json and
results/recursion_demo.txt, so the text cannot drift from the data.

Usage:  python docs/build_report.py            # writes docs/report.html
        python docs/render.py docs/report.html Assignment2_Divide_and_Conquer_Analysis.pdf
"""

from __future__ import annotations

import csv
import html
import json
import math
import re
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "results" / "benchmark_results.csv"
ENV = ROOT / "results" / "environment.json"
DEMO = ROOT / "results" / "recursion_demo.txt"
TEMPLATE = ROOT / "docs" / "report_template.html"
OUT = ROOT / "docs" / "report.html"

ALG_LABEL = {
    "merge_sort": "Merge sort",
    "quick_sort": "Quicksort (last-element pivot)",
    "randomized_quick_sort": "Randomized quicksort",
    "builtin_sorted": "Python sorted()",
}
DS_LABEL = {"sorted": "Sorted", "reverse": "Reverse", "random": "Random"}


def load():
    R = {}
    with open(CSV, newline="") as f:
        for r in csv.DictReader(f):
            R[(r["algorithm"], r["dataset"], int(r["n"]))] = r
    return R


def t(R, alg, ds, n):
    r = R.get((alg, ds, n))
    return float(r["time_median_s"]) if r and r["time_median_s"] else None


def comps(R, alg, ds, n):
    r = R.get((alg, ds, n))
    return int(r["comparisons"]) if r and r["comparisons"] else None


def mem_kib(R, alg, ds, n):
    r = R.get((alg, ds, n))
    return int(r["aux_peak_bytes"]) / 1024 if r and r["aux_peak_bytes"] else None


def fmt_t(x):
    if x is None:
        return "—"
    return f"{x:.4f}" if x >= 0.001 else f"{x:.5f}"


def table1(R, sizes):
    cols = [10_000, 20_000, 100_000]
    head = "<tr><th class='l'>Algorithm</th><th class='l'>Input</th>" + \
           "".join(f"<th><var>n</var> = {c:,}</th>" for c in cols) + "</tr>"
    body = ""
    for alg in ["merge_sort", "quick_sort", "randomized_quick_sort", "builtin_sorted"]:
        for i, ds in enumerate(["sorted", "reverse", "random"]):
            body += "<tr><td class='l'>" + (ALG_LABEL[alg] if i == 0 else "") + "</td>" + \
                    f"<td class='l'>{DS_LABEL[ds]}</td>" + \
                    "".join(f"<td>{fmt_t(t(R, alg, ds, c))}</td>" for c in cols) + "</tr>"
    return f"<table>{head}{body}</table>"


def table2(R):
    n = 20_000
    nlgn = n * math.log2(n)
    head = "<tr><th class='l'>Algorithm</th><th class='l'>Input</th><th>Comparisons</th><th>Comparisons / <var>n</var> lg <var>n</var></th></tr>"
    body = ""
    for alg in ["merge_sort", "quick_sort", "randomized_quick_sort"]:
        for i, ds in enumerate(["sorted", "reverse", "random"]):
            c = comps(R, alg, ds, n)
            body += "<tr><td class='l'>" + (ALG_LABEL[alg] if i == 0 else "") + "</td>" + \
                    f"<td class='l'>{DS_LABEL[ds]}</td><td>{c:,}</td><td>{c / nlgn:.2f}</td></tr>"
    return f"<table>{head}{body}</table>"


def snippet(path: Path, start_pat: str, end_pat: str) -> str:
    """Lines of `path` from the first line matching start_pat up to (not incl.) end_pat."""
    lines = path.read_text().splitlines()
    s = next(i for i, l in enumerate(lines) if re.search(start_pat, l))
    e = next(i for i, l in enumerate(lines) if i > s and re.search(end_pat, l))
    block = lines[s:e]
    indent = min(len(l) - len(l.lstrip()) for l in block if l.strip())
    return html.escape("\n".join(l[indent:] for l in block).rstrip())


def main():
    R = load()
    env = json.loads(ENV.read_text())
    sizes = env["sizes"]
    V = {}
    V["DATE"] = time.strftime("%B %-d, %Y")
    V["PYVER"] = env["python"]
    V["SIZES"] = ", ".join(f"{s:,}" for s in sizes[:-1]) + f", and {sizes[-1]:,}"
    V["TRIALS"] = "five (three for n ≥ 50,000)"
    V["QCAP"] = f"{env['quadratic_cap']:,}"
    V["PLATFORM"] = f"Linux ({env['machine']})"
    V["CPUS"] = str(env["cpu_count"])
    V["SNIPPET_MERGE"] = snippet(ROOT / "merge_sort.py", r"# As long as each of the arrays", r"^def merge_sort")
    V["SNIPPET_PARTITION"] = snippet(ROOT / "quick_sort.py", r"^def partition", r"^def quick_sort")
    V["RECURSION_DEMO"] = html.escape("$ python recursion_demo.py\n" + DEMO.read_text().rstrip())
    V["TABLE1"] = table1(R, sizes)
    V["TABLE2"] = table2(R)

    r2 = lambda a, b: f"{a / b:.2f}"
    V["MS_RAND_RATIO"] = r2(t(R, "merge_sort", "random", 100_000), t(R, "merge_sort", "random", 50_000))
    V["RQS_RAND_RATIO"] = r2(t(R, "randomized_quick_sort", "random", 100_000), t(R, "randomized_quick_sort", "random", 50_000))
    V["NLGN_RATIO"] = r2(100_000 * math.log2(100_000), 50_000 * math.log2(50_000))
    V["QS_SORTED_RATIO"] = r2(t(R, "quick_sort", "sorted", 20_000), t(R, "quick_sort", "sorted", 10_000))
    V["QS_REV_RATIO"] = r2(t(R, "quick_sort", "reverse", 20_000), t(R, "quick_sort", "reverse", 10_000))
    V["QS_SORTED_20K"] = f"{t(R, 'quick_sort', 'sorted', 20_000):.1f}"
    V["RQS_SORTED_20K"] =f"{t(R, 'randomized_quick_sort', 'sorted', 20_000):.3f}"
    V["MS_SORTED_20K"] = f"{t(R, 'merge_sort', 'sorted', 20_000):.3f}"
    V["QS_VS_RQS_20K"] = f"{t(R, 'quick_sort', 'sorted', 20_000) / t(R, 'randomized_quick_sort', 'sorted', 20_000):,.0f}"

    nlgn20 = 20_000 * math.log2(20_000)
    V["NLGN_20K"] = f"{nlgn20:,.0f}"
    V["MS_RAND_RATIO_C"] = f"{comps(R, 'merge_sort', 'random', 20_000) / nlgn20:.2f}"
    V["MS_SORTED_RATIO_C"] = f"{comps(R, 'merge_sort', 'sorted', 20_000) / nlgn20:.2f}"
    V["RQS_RAND_RATIO_C"] = f"{comps(R, 'randomized_quick_sort', 'random', 20_000) / nlgn20:.2f}"
    V["QS_SORTED_COMPS_20K"] = f"{comps(R, 'quick_sort', 'sorted', 20_000):,}"
    assert comps(R, "quick_sort", "sorted", 20_000) == 20_000 * 19_999 // 2

    V["MS_MEM_100K"] = f"{mem_kib(R, 'merge_sort', 'random', 100_000):,.0f}"
    V["QS_MEM_RAND_100K"] = f"{mem_kib(R, 'quick_sort', 'random', 100_000):.1f}"
    V["QS_MEM_SORTED_1K"] = f"{mem_kib(R, 'quick_sort', 'sorted', 1_000):.0f}"
    V["QS_MEM_SORTED_2K"] = f"{mem_kib(R, 'quick_sort', 'sorted', 2_000):.0f}"

    V["QS_RAND_100K"] = f"{t(R, 'quick_sort', 'random', 100_000):.3f}"
    V["MS_RAND_100K"] = f"{t(R, 'merge_sort', 'random', 100_000):.3f}"
    V["MS_SORTED_100K"] = f"{t(R, 'merge_sort', 'sorted', 100_000):.3f}"
    V["QS_OVER_MS_COMPS"] = f"{comps(R, 'quick_sort', 'random', 100_000) / comps(R, 'merge_sort', 'random', 100_000):.1f}"
    V["RQS_SLOWER_PCT"] = f"{(t(R, 'randomized_quick_sort', 'random', 100_000) / t(R, 'quick_sort', 'random', 100_000) - 1) * 100:.0f}"
    V["BUILTIN_SPEEDUP_RAND"] = f"{t(R, 'merge_sort', 'random', 100_000) / t(R, 'builtin_sorted', 'random', 100_000):.0f}"

    out = TEMPLATE.read_text()
    for k, v in V.items():
        out = out.replace("{{" + k + "}}", str(v))
    missing = re.findall(r"\{\{[A-Z0-9_]+\}\}", out)
    if missing:
        raise SystemExit(f"unfilled placeholders: {missing}")
    OUT.write_text(out)
    print("wrote", OUT)
    for k in ["MS_RAND_RATIO", "RQS_RAND_RATIO", "QS_SORTED_RATIO", "QS_REV_RATIO", "QS_VS_RQS_20K",
              "MS_RAND_RATIO_C", "MS_SORTED_RATIO_C", "RQS_RAND_RATIO_C", "QS_OVER_MS_COMPS",
              "RQS_SLOWER_PCT", "BUILTIN_SPEEDUP_RAND", "MS_MEM_100K", "QS_MEM_RAND_100K"]:
        print(f"  {k:22s} {V[k]}")


if __name__ == "__main__":
    main()
