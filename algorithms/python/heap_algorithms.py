"""
heap_algorithms.py

Demonstrates three classic heap-based algorithms using Python's heapq module:
  1. Finding the K largest elements in a collection.
  2. Merging K sorted lists into a single sorted sequence.
  3. Maintaining the running median of a stream of numbers.
"""

import heapq
from typing import Iterable, Iterator, List


def k_largest(nums: Iterable[int], k: int) -> List[int]:
    """Return the k largest elements from nums, in descending order."""
    if k <= 0:
        return []
    # heapq.nlargest uses a heap of size k internally for efficiency.
    return heapq.nlargest(k, nums)


def merge_k_sorted_lists(lists: List[List[int]]) -> List[int]:
    """Merge k sorted lists into one sorted list using a min-heap."""
    result: List[int] = []
    heap = []
    # Seed the heap with the first element of each non-empty list.
    for list_idx, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], list_idx, 0))

    while heap:
        value, list_idx, elem_idx = heapq.heappop(heap)
        result.append(value)
        next_idx = elem_idx + 1
        if next_idx < len(lists[list_idx]):
            heapq.heappush(heap, (lists[list_idx][next_idx], list_idx, next_idx))

    return result


class MedianFinder:
    """Maintains the running median of a stream of numbers using two heaps.

    `low` is a max-heap (negated values) holding the smaller half.
    `high` is a min-heap holding the larger half.
    Invariant: len(low) == len(high) or len(low) == len(high) + 1.
    """

    def __init__(self) -> None:
        self.low: List[int] = []   # max-heap, values stored negated
        self.high: List[int] = []  # min-heap

    def add_num(self, num: int) -> None:
        heapq.heappush(self.low, -num)
        # Ensure every element in low <= every element in high.
        heapq.heappush(self.high, -heapq.heappop(self.low))
        # Rebalance so low has equal or one more element than high.
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def find_median(self) -> float:
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2.0


def _demo() -> None:
    print("K largest elements:", k_largest([5, 1, 9, 3, 7, 2], 3))

    sorted_lists = [[1, 4, 7], [2, 5, 8], [0, 3, 6, 9]]
    print("Merged sorted lists:", merge_k_sorted_lists(sorted_lists))

    finder = MedianFinder()
    stream = [5, 15, 1, 3, 8]
    for n in stream:
        finder.add_num(n)
        print(f"After adding {n}, median = {finder.find_median()}")


if __name__ == "__main__":
    _demo()
