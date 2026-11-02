"""
test_sorts.py -- unit tests for merge_sort.py and quick_sort.py

Run with:  python -m unittest -v test_sorts.py
"""

import random
import sys
import unittest

from merge_sort import Counter, merge_sort
from quick_sort import quick_sort, randomized_quick_sort

SORTS = {
    "merge_sort": merge_sort,
    "quick_sort": quick_sort,
    "randomized_quick_sort": randomized_quick_sort,
}


class Rec:
    """Record compared by key only -- used to test stability."""

    def __init__(self, key, tag):
        self.key, self.tag = key, tag

    def __lt__(self, other):
        return self.key < other.key

    def __le__(self, other):
        return self.key <= other.key

    def __repr__(self):
        return f"{self.key}{self.tag}"


class SortTests(unittest.TestCase):

    def check_all(self, data):
        expected = sorted(data)
        for name, fn in SORTS.items():
            with self.subTest(sort=name, n=len(data)):
                A = list(data)
                out = fn(A)
                self.assertIs(out, A, "sort must work in place and return A")
                self.assertEqual(A, expected)

    def test_textbook_examples(self):
        self.check_all([12, 3, 7, 9, 14, 6, 11, 2])   # CLRS Figure 2.4 (merge sort)
        self.check_all([2, 8, 7, 1, 3, 5, 6, 4])      # CLRS Figure 7.1 (quicksort)

    def test_edge_cases(self):
        self.check_all([])
        self.check_all([42])
        self.check_all([2, 1])
        self.check_all([1, 2])
        self.check_all([5, 5, 5, 5])
        self.check_all([3, -1, 0, -7, 2.5, 2])

    def test_sorted_reverse_and_random(self):
        for n in (10, 100, 1000):
            self.check_all(list(range(n)))
            self.check_all(list(range(n, 0, -1)))
            rng = random.Random(n)
            self.check_all([rng.randint(0, 50) for _ in range(n)])   # many duplicates
            self.check_all([rng.random() for _ in range(n)])

    def test_randomized_against_builtin(self):
        rng = random.Random(2026)
        for _ in range(200):
            n = rng.randint(0, 60)
            data = [rng.randint(-1000, 1000) for _ in range(n)]
            self.check_all(data)

    def test_merge_sort_is_stable(self):
        data = [Rec(2, "a"), Rec(1, "b"), Rec(2, "c"), Rec(1, "d"), Rec(0, "e"), Rec(2, "f")]
        out = merge_sort(list(data))
        self.assertEqual([r.tag for r in out], ["e", "b", "d", "a", "c", "f"])

    def test_comparison_counts(self):
        # Merge sort on 8 already-sorted elements: every MERGE stops as soon as
        # the left run is exhausted, so the count is (n/2) lg n = 12.
        c = Counter()
        merge_sort(list(range(8)), counter=c)
        self.assertEqual(c.comparisons, 12)       # best case: 4*1 + 2*2 + 1*4
        c = Counter()
        quick_sort(list(range(8)), counter=c)     # worst case: n(n-1)/2
        self.assertEqual(c.comparisons, 28)

    def test_partition_sorted_input_recursion_depth(self):
        """Deterministic quicksort on sorted input recurses n deep."""
        n = 2000
        sys.setrecursionlimit(1000)
        with self.assertRaises(RecursionError):
            quick_sort(list(range(n)))
        sys.setrecursionlimit(10_000)
        self.assertEqual(quick_sort(list(range(n))), list(range(n)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
