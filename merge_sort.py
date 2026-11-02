"""
merge_sort.py -- Merge Sort (CLRS 4th ed., Section 2.3.1)

MSCS 532 Algorithms and Data Structures -- Assignment 2
Author: Jatin Jaiswal

Merge Sort is a divide-and-conquer algorithm:

    Divide   : split A[p..r] at the midpoint q = floor((p + r) / 2)
    Conquer  : sort A[p..q] and A[q+1..r] recursively
    Combine  : MERGE the two sorted halves into one sorted run

Recurrence:  T(n) = 2 T(n/2) + Theta(n)   =>   T(n) = Theta(n lg n)
for every input (best, average and worst case are all Theta(n lg n)).
The algorithm is stable but NOT in place: MERGE uses Theta(n) auxiliary
storage for the two temporary arrays L and R.

The implementation follows the textbook pseudocode closely so that the
recurrence written in the report can be read directly from the code.
An optional `Counter` lets the caller count key comparisons, which is
how the experiments connect the measured running time to the theory.
"""

from __future__ import annotations

import sys
from typing import List, Optional


class Counter:
    """Mutable tally of key comparisons performed by a sort."""

    __slots__ = ("comparisons",)

    def __init__(self) -> None:
        self.comparisons = 0


def merge(A: List, p: int, q: int, r: int, counter: Optional[Counter] = None) -> None:
    """MERGE(A, p, q, r) -- combine the sorted runs A[p..q] and A[q+1..r].

    Both runs are copied into temporary arrays L and R (Theta(n) extra
    space, n = r - p + 1) and then merged back into A[p..r] with a
    single left-to-right pass.  Every iteration of the main while-loop
    performs exactly one key comparison, so MERGE costs Theta(n) time.
    Taking L[i] when L[i] <= R[j] (ties go to the LEFT run) is what
    makes the sort stable.
    """
    n_L = q - p + 1          # length of A[p..q]
    n_R = r - q              # length of A[q+1..r]
    L = A[p:q + 1]           # copy the left run   (Python slice == CLRS loop)
    R = A[q + 1:r + 1]       # copy the right run

    i = j = 0                # i indexes L, j indexes R
    k = p                    # k indexes the location in A to fill

    # As long as each of the arrays L and R contains an unmerged element,
    # copy the smallest unmerged element back into A[p..r].
    while i < n_L and j < n_R:
        if counter is not None:
            counter.comparisons += 1
        if L[i] <= R[j]:
            A[k] = L[i]
            i += 1
        else:
            A[k] = R[j]
            j += 1
        k += 1

    # One of L or R is exhausted; copy the remainder of the other
    # (no further comparisons are needed).
    while i < n_L:
        A[k] = L[i]
        i += 1
        k += 1
    while j < n_R:
        A[k] = R[j]
        j += 1
        k += 1


def merge_sort(A: List, p: int = 0, r: Optional[int] = None,
               counter: Optional[Counter] = None) -> List:
    """MERGE-SORT(A, p, r) -- sort A[p..r] in place and return A.

    The default arguments let the caller simply write merge_sort(A).
    Recursion depth is only ceil(lg n) + 1, so Python's default
    recursion limit (1000) is never a concern.
    """
    if r is None:
        r = len(A) - 1
    if p >= r:                      # zero or one element: already sorted
        return A
    q = (p + r) // 2                # DIVIDE: midpoint, floor((p + r) / 2)
    merge_sort(A, p, q, counter)    # CONQUER: sort A[p..q]
    merge_sort(A, q + 1, r, counter)  #          sort A[q+1..r]
    merge(A, p, q, r, counter)      # COMBINE: merge the two sorted halves
    return A


def _main(argv: List[str]) -> None:
    """Tiny command-line demo: python merge_sort.py 12 3 7 9 14 6 11 2"""
    values = [float(x) if "." in x else int(x) for x in argv] or [12, 3, 7, 9, 14, 6, 11, 2]
    print("input :", values)
    counter = Counter()
    print("sorted:", merge_sort(list(values), counter=counter))
    print("key comparisons:", counter.comparisons)


if __name__ == "__main__":
    _main(sys.argv[1:])
