"""
Segment tree supporting range sum queries and point updates in O(log n).

Backed by a flat array of size 2 * n (iterative implementation), where
leaves occupy indices [n, 2n) and each internal node stores the sum of
its two children.
"""

from typing import List, Sequence


class SegmentTree:
    def __init__(self, data: Sequence[int]):
        self.n = len(data)
        self.tree: List[int] = [0] * (2 * self.n)
        # Place leaves and build internal nodes bottom-up.
        self.tree[self.n:] = list(data)
        for i in range(self.n - 1, 0, -1):
            self.tree[i] = self.tree[2 * i] + self.tree[2 * i + 1]

    def update(self, index: int, value: int) -> None:
        """Set element at `index` to `value` in O(log n)."""
        if not 0 <= index < self.n:
            raise IndexError("index out of range")
        i = index + self.n
        self.tree[i] = value
        # Propagate the change upward, recomputing each ancestor's sum.
        i //= 2
        while i >= 1:
            self.tree[i] = self.tree[2 * i] + self.tree[2 * i + 1]
            i //= 2

    def query(self, left: int, right: int) -> int:
        """Return sum of elements in the half-open range [left, right)."""
        if not (0 <= left <= right <= self.n):
            raise IndexError("range out of bounds")
        result = 0
        l, r = left + self.n, right + self.n
        while l < r:
            if l & 1:
                result += self.tree[l]
                l += 1
            if r & 1:
                r -= 1
                result += self.tree[r]
            l //= 2
            r //= 2
        return result


if __name__ == "__main__":
    arr = [1, 3, 5, 7, 9, 11]
    st = SegmentTree(arr)
    print(st.query(1, 4))   # 3 + 5 + 7 = 15
    st.update(2, 10)        # arr becomes [1, 3, 10, 7, 9, 11]
    print(st.query(1, 4))   # 3 + 10 + 7 = 20
    print(st.query(0, 6))   # sum of all elements = 41
