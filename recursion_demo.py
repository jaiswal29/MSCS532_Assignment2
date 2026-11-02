"""
recursion_demo.py -- a practical failure the asymptotic analysis does not predict.

Deterministic quicksort (last-element pivot) recurses n deep on already-sorted
input, so with Python's default limit of 1,000 frames it cannot even sort
1,000 sorted integers.  Randomized quicksort on the same input has expected
depth Theta(lg n) and is fine.

Usage:  python recursion_demo.py
"""

import sys

from quick_sort import quick_sort, randomized_quick_sort

print("default recursion limit:", sys.getrecursionlimit())
data = list(range(1000))
try:
    quick_sort(list(data))
    print("quick_sort(sorted 1000)             : ok")
except RecursionError as e:
    print("quick_sort(sorted 1000)             : RecursionError --", e)
print("randomized_quick_sort(sorted 1000)  : ok" if randomized_quick_sort(list(data)) == data else "wrong")
sys.setrecursionlimit(5000)
print("after sys.setrecursionlimit(5000)   : quick_sort(sorted 1000) ok" if quick_sort(list(data)) == data else "wrong")
