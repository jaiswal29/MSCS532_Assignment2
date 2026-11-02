"""
quick_sort.py -- Quicksort (CLRS 4th ed., Chapter 7)

MSCS 532 Algorithms and Data Structures -- Assignment 2
Author: Jatin Jaiswal

Quicksort is a divide-and-conquer algorithm whose work is done in the
DIVIDE step rather than in the COMBINE step:

    Divide   : PARTITION A[p..r] around a pivot x so that every element of
               A[p..q-1] is <= x = A[q] and every element of A[q+1..r] is > x
    Conquer  : sort A[p..q-1] and A[q+1..r] recursively
    Combine  : nothing -- the sub-arrays are sorted in place

Two variants are provided, exactly as in the textbook:

    quick_sort            PARTITION always picks the LAST element A[r] as the
                          pivot.  Worst case Theta(n^2) on already-sorted or
                          reverse-sorted input (one sub-array is always empty).
    randomized_quick_sort RANDOMIZED-PARTITION swaps a uniformly random
                          element into A[r] first, so the expected running
                          time is Theta(n lg n) for EVERY input.

Recurrences:
    best / balanced : T(n) = 2 T(n/2) + Theta(n)        = Theta(n lg n)
    worst           : T(n) = T(n-1) + T(0) + Theta(n)   = Theta(n^2)
    expected        : E[T(n)] = (2/n) * sum_{q} E[T(q)] + Theta(n) = Theta(n lg n)

Both variants sort in place (O(1) extra space per call) but the
deterministic variant can recurse n deep, which matters in Python -- see
the report and benchmark.py.
"""

from __future__ import annotations

import random
import sys
from typing import List, Optional

from merge_sort import Counter  # re-use the same comparison tally


def partition(A: List, p: int, r: int, counter: Optional[Counter] = None) -> int:
    """PARTITION(A, p, r) -- Lomuto partition around the pivot x = A[r].

    Maintains the loop invariant (CLRS Figure 7.2):
        A[p..i]     <= x   (the "low side")
        A[i+1..j-1] >  x   (the "high side")
        A[r]        =  x   (the pivot)
    Each of the r - p iterations does exactly one key comparison, so
    PARTITION runs in Theta(n) time where n = r - p + 1.
    Returns the final index q of the pivot.
    """
    x = A[r]                    # the pivot
    i = p - 1                   # highest index into the low side
    for j in range(p, r):       # process each element other than the pivot
        if counter is not None:
            counter.comparisons += 1
        if A[j] <= x:           # does this element belong on the low side?
            i += 1              # index of a new slot in the low side
            A[i], A[j] = A[j], A[i]   # put this element there
    A[i + 1], A[r] = A[r], A[i + 1]   # pivot goes just right of the low side
    return i + 1                # new index of the pivot


def quick_sort(A: List, p: int = 0, r: Optional[int] = None,
               counter: Optional[Counter] = None) -> List:
    """QUICKSORT(A, p, r) -- deterministic (last-element pivot). Sorts in place."""
    if r is None:
        r = len(A) - 1
    if p < r:
        q = partition(A, p, r, counter)       # DIVIDE: pivot ends up at A[q]
        quick_sort(A, p, q - 1, counter)      # CONQUER: low side
        quick_sort(A, q + 1, r, counter)      #          high side
    return A                                  # COMBINE: nothing to do


def randomized_partition(A: List, p: int, r: int,
                         counter: Optional[Counter] = None,
                         rng: random.Random = random) -> int:
    """RANDOMIZED-PARTITION(A, p, r) -- pick a random pivot, then PARTITION."""
    i = rng.randint(p, r)               # uniform over A[p..r]
    A[i], A[r] = A[r], A[i]             # move the chosen pivot into A[r]
    return partition(A, p, r, counter)


def randomized_quick_sort(A: List, p: int = 0, r: Optional[int] = None,
                          counter: Optional[Counter] = None,
                          rng: random.Random = random) -> List:
    """RANDOMIZED-QUICKSORT(A, p, r) -- expected Theta(n lg n) on any input."""
    if r is None:
        r = len(A) - 1
    if p < r:
        q = randomized_partition(A, p, r, counter, rng)
        randomized_quick_sort(A, p, q - 1, counter, rng)
        randomized_quick_sort(A, q + 1, r, counter, rng)
    return A


def _main(argv: List[str]) -> None:
    """Tiny command-line demo: python quick_sort.py 2 8 7 1 3 5 6 4"""
    values = [float(x) if "." in x else int(x) for x in argv] or [2, 8, 7, 1, 3, 5, 6, 4]
    print("input                :", values)
    c1, c2 = Counter(), Counter()
    print("quick_sort           :", quick_sort(list(values), counter=c1),
          f"({c1.comparisons} comparisons)")
    print("randomized_quick_sort:", randomized_quick_sort(list(values), counter=c2),
          f"({c2.comparisons} comparisons)")


if __name__ == "__main__":
    _main(sys.argv[1:])
