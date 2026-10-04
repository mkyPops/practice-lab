"""
Heap-based algorithms using Python's heapq module.

Implements three classic patterns:
1. Finding the K largest elements in a collection.
2. Merging K sorted lists into a single sorted list.
3. Maintaining the running median of a stream of numbers.
"""

import heapq


def k_largest(nums, k):
    """Return the k largest elements from nums, in descending order."""
    if k <= 0:
        return []
    # heapq.nlargest uses a bounded min-heap internally for O(n log k) performance.
    return heapq.nlargest(k, nums)


def merge_k_sorted_lists(lists):
    """Merge k sorted iterables into a single sorted list."""
    result = []
    # heapq.merge lazily merges sorted inputs using a heap of size k.
    for value in heapq.merge(*lists):
        result.append(value)
    return result


class MedianFinder:
    """Maintains the median of a stream of numbers using two heaps.

    `low` is a max-heap (negated values) holding the smaller half,
    `high` is a min-heap holding the larger half. The heaps are kept
    balanced so their sizes differ by at most one.
    """

    def __init__(self):
        self.low = []   # max-heap (store negatives)
        self.high = []  # min-heap

    def add_num(self, num):
        heapq.heappush(self.low, -num)
        # Ensure every element in low is <= every element in high.
        heapq.heappush(self.high, -heapq.heappop(self.low))

        # Rebalance so low has equal or one more element than high.
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def find_median(self):
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2.0


if __name__ == "__main__":
    # Demo: k largest elements
    data = [5, 1, 9, 3, 7, 8, 2]
    print("K largest (k=3):", k_largest(data, 3))

    # Demo: merge k sorted lists
    sorted_lists = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
    print("Merged sorted lists:", merge_k_sorted_lists(sorted_lists))

    # Demo: running median
    mf = MedianFinder()
    stream = [5, 15, 1, 3, 8]
    for n in stream:
        mf.add_num(n)
        print(f"After adding {n}, median = {mf.find_median()}")
